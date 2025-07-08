import rasterio
import matplotlib.pyplot as plt
import os
from flask import Flask, send_file, jsonify

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import io

SCOPES = ['https://www.googleapis.com/auth/drive.file'] # the scope with which the google drive api can access data
app = Flask(__name__)
index_file = "index.txt"
drive_api = None
parent_drive = "1nTQMbq0GZGfi1Xbdf27qrlb5aybo9vYc"
dataset_len = 0
output_file_path = "temp/currData_dem.tif"

def get_current_index():
    if os.path.exists(index_file):
        with open(index_file, 'r') as f:
            return int(f.read().strip())
    return 0

def save_current_index(i):
    with open(index_file, 'w') as f:
        f.write(str(i))

def accessFolder(api, id, query=None):
    if(query == None):
        results = api.files().list(
            q=f"'{id}' in parents",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            fields="files(id, name, mimeType)",
            orderBy="name"
        ).execute()
    else:
        results = api.files().list(
            q=query,
            fields="nextPageToken, files(id, name)",
            pageSize=1000,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            orderBy="name"
        ).execute()
    files = results.get('files', [])

    return files

def delete(api, id):
    api.files().delete(
        fileId=id,
        supportsAllDrives=True
    ).execute()

def deleteFolder(api, id):
    filesToDelete = accessFolder(api, id)
    for file in filesToDelete:
        if file['mimeType'] != 'application/vnd.google-apps.folder':
            delete(api, file['id'])
        else:
            deleteFolder(api, file['id'])
    delete(api, id)


def download_data(request):
    file_handler = io.FileIO(output_file_path, 'wb')
    downloader_obj = MediaIoBaseDownload(file_handler, request)
    done = False

    while done == False:
        status, done = downloader_obj.next_chunk()
        # print(status.progress()) # Optional to see status of download.

def visualizeData():
    # find way to access data from dataIndex
    suffix = "_dem.tif"
    index = get_current_index()
    file = files[index]
    if(file['mimeType'] == 'application/vnd.google-apps.folder'):
        files = accessFolder(drive_api, parent_drive)

    correct_file = None
    for item in files:
        if item.endswith(suffix):
            correct_file = item
        else:
            continue
    
    fileID = correct_file['id']

    request = drive_api.files().get_media(
        fileId=fileID,
        supportsAllDrives=True
    )

    download_data(request)

    with rasterio.open(output_file_path) as dataset:
        band = dataset.read(1)
        plt.imshow(band, cmap='gray')
        plt.colorbar(label='Elevation')
        plt.title('Elevation Data')
        plt.xlabel('X')
        plt.ylabel('Y')\
        
        notData = dataset.nodata

        validData = band != notData
        
        plt.figtext(0.5, 0.01, "Total area: {:.2f} m²".format(validData.sum() * 2), ha='center')

        plt.savefig('output/output.png', format='png', bbox_inches='tight', pad_inches=0)
        plt.close()

    return 0

def next():
    index = get_current_index()
    index += 1 % dataset_len
    save_current_index(index)
    return 0

def prev():
    index = get_current_index()
    index -= 1
    if(index < 0):
        index = dataset_len - 1
    save_current_index(index)
    return 0

@app.route('/image')
def get_image():
    return send_file('output/output.png')

@app.route('/accept', methods=['POST'])
def accept():
    next()
    return jsonify({'status': 'accepted'})

@app.route('/delete', methods=['POST'])
def delete_item():
    index = get_current_index()
    # find file from index
    q = f"'{parent_drive}' in parents and mimeType = 'application/vnd.google-apps.folder'"
    parent_files = accessFolder(drive_api, parent_drive, q)
    fileID = parent_files[index]['id']
    deleteFolder(drive_api, fileID)
    dataset_len -= 1
    return jsonify({'status': 'deleted'})

@app.route("/next", methods=['POST'])
def next_item():
    next()
    visualizeData()
    return jsonify({'status': 'incremented'})

@app.route("/prev", methods=['POST'])
def prev_item():
    prev()
    visualizeData()
    return jsonify({'status': 'decremented'})

@app.route("/")
def connectToDrive():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
      creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
                )
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    drive_api = build('drive', 'v3', credentials=creds)
    
    q = f"'{parent_drive}' in parents and mimeType = 'application/vnd.google-apps.folder'"

    folders = []
    folders.extend(accessFolder(drive_api, parent_drive, q))
    dataset_len = len(folders)

def main():
    app.run(port=5000)

if __name__ == '__main__':
    main()