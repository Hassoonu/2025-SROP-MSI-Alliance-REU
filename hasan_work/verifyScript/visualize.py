import rasterio
from rasterio.enums import Resampling
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for safe plotting
import matplotlib.pyplot as plt
import os
from flask import Flask, send_file, jsonify
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import io

SCOPES = ['https://www.googleapis.com/auth/drive'] # the scope with which the google drive api can access data
app = Flask(__name__)
index_file = "index.txt"
drive_api = None
parent_drive = "1vIc1NqmQGPlP6ILXoY61fp0OWdcdGfbP"
dataset_len = 0
output_file_path = "temp/currData_dem.tif"
indexByFolder = []
currFolder = 0

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
            orderBy="name",
        ).execute()
    else:
        results = api.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType)",
            pageSize=1000,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            orderBy="name",
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
    print("Downloading data...", flush=True)
    file_handler = io.FileIO(output_file_path, 'wb')
    downloader_obj = MediaIoBaseDownload(file_handler, request)
    done = False
    try: 
        while done == False:
            status, done = downloader_obj.next_chunk()
            print(status.progress(), flush=True) # Optional to see status of download.
    
    except HttpError as error:
        print(f"An error occurred: {error}")
        file_handler = None
    print("Finished downloading.", flush=True)
    
# needs to be simplified to only use the folder index it was provided or the global folder index
# from there just access the element
# keep a running count of total index or maybe local file index, some way to make sure
# we're using the right index within the folder but also know what's the next folder to go to.
def prepData():
    # find way to access data from dataIndex
    suffix = "dem.tif"
    # MAKE IT SO THAT THIS FUNCTION ACCESSES THE FOLDER AT CURRFOLDER
    index = get_current_index()
    q = f"'{parent_drive}' in parents and mimeType = 'application/vnd.google-apps.folder'"
    files = accessFolder(drive_api, parent_drive, q) # goes to parent directory with multiple folders per point
    file = files[currFolder] # gets the folder we want

    print("Looking at: ", files[currFolder]['name'], flush=True)

    if(file['mimeType'] == 'application/vnd.google-apps.folder'):
        files = accessFolder(drive_api, file['id'])
    print("Entered Folder...", flush=True)
    wantedFile = files[index] # CHECK IF ITS A DEM FILE AND CORRECT INDEX
    
    if(wantedFile['name'].endswith(suffix)):
        print("found dem file!")
        print("file name:", wantedFile['name'], flush=True)
    else:
        wantedFile = None
    
    # for item in files:
    #     if item['name'].endswith(suffix):
    #         fileID = item['id']
    #         print("Found dem file.\n")
    #         break
    #     else:
    #         continue
            
    
    if wantedFile is None:
        raise ValueError(f"No file found ending with {suffix}")
    
    request = drive_api.files().get_media(
        fileId=wantedFile['id'],
        supportsAllDrives=True
    )

    metadata = drive_api.files().get(
        fileId=wantedFile['id'],
        fields="name",
        supportsAllDrives=True
    ).execute()

    filename = metadata["name"]
    print("Original filename from Drive:", filename, flush=True)

    download_data(request)

    if not os.path.exists(output_file_path):
        raise ValueError("File not downloaded correctly.")
    return 0

def next():
    index = get_current_index()
    curr_folder_len = indexByFolder[currFolder]
    if(index + 1 >= curr_folder_len): # if we reached the end of the current folder
        nextFolder() # get the next folder
        index = 0 # reset index
    else:
        index += 1 # stay in same folder, iterate to next file
    save_current_index(index)
    return 0

def prev():
    index = get_current_index()
    if(index - 1 < 0):
        prevFolder() # go to the last folder
        index = indexByFolder[currFolder] - 1 # so we don't go past the length
    else:
        index -= 1
    save_current_index(index)
    return 0

@app.route("/health")
def health():
    return "OK", 200

@app.route('/image')
def get_image():
    try:
        if os.path.exists(output_file_path):
            os.remove(output_file_path)
        print("Starting image generation...", flush=True)
        prepData()
        
        print("Finished Prepping data.", flush=True)
        # Wait for the file to exist and have non-zero size
        tries = 0
        while (not os.path.exists("temp/currData_dem.tif") or os.path.getsize("temp/currData_dem.tif") < 1000) and tries < 10:
            time.sleep(0.5)
            tries += 1
            print(f"Waiting for file... attempt {tries}")

        if not os.path.exists("temp/currData_dem.tif") or os.path.getsize("temp/currData_dem.tif") < 1000:
            raise Exception("DEM file failed to download in time.")


        print("OPENING WITH RASTER...", flush=True)
        with rasterio.open("temp/currData_dem.tif") as dataset:
            print("bad values:", dataset.nodata, flush=True)
            band = dataset.read(1)
            band = np.ma.masked_equal(band, dataset.nodata)
        print("Finished...", flush=True)
        fig, ax = plt.subplots()
        cax = ax.imshow(band, cmap='gray', label='Elevation')
        fig.colorbar(cax)
        print("Saving Figure...", flush=True)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)

        print("Sending image buffer...", flush=True)
        return send_file(buf, mimetype='image/png')

    except Exception as e:
        print("ERROR:", e, flush=True)
        return jsonify({"error": str(e)}), 500


@app.route('/accept', methods=['POST'])
def accept():
    print("Recieved accept request!")
    next()
    return jsonify({'status': 'accepted'})

@app.route('/delete', methods=['POST'])
def delete_item():
    global dataset_len
    print("Recieved delete request!")
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
    print("Received next request!")
    try:
        next()
        return jsonify({'status': 'incremented'})  # HTTP 200 OK by default
    except Exception as e:
        print("Error in /next:", e)
        return jsonify({'error': str(e)}), 500  # If something goes wrong

@app.route("/prev", methods=['POST'])
def prev_item():
    print("Recieved previous request!")
    try:
        prev()
        return jsonify({'status': 'decremented'})
    except Exception as e:
        print("Error in /prev:", e, flush=True)
        return jsonify({'error': str(e)}), 500


@app.route("/")
def index():
    return "Flask server running and connected to Google Drive"


# functions to implement:
# iterates to the next folder within the data structure
def nextFolder():
    global currFolder
    if(currFolder + 1 < dataset_len):
        currFolder += 1
    # make it so that it doesnt go past dataset_len len

# similar but opposite effect of nextFolder()
def prevFolder():
    global currFolder
    if(currFolder - 1 >= 0):
        currFolder -= 1
    # for functionality, maybe add a round-about so if we go less than 0 we loop back to the last folder

# Creates a data structure that knows how many data points are in each folder
def prepIndex(api):
    global indexByFolder
    q = f"'{parent_drive}' in parents and mimeType = 'application/vnd.google-apps.folder'"
    foldersIterator = accessFolder(api, parent_drive, q)
    # totalItems = 0
    indexByFolder = [0] * dataset_len
    iterator = 0
    for folder in foldersIterator:
        filesList = accessFolder(api, folder['id'])
        sum = len(filesList)
        indexByFolder[iterator] = sum 
        iterator += 1
        # totalItems += sum
    print("Index by folder:")
    print(indexByFolder)
    return 0

def connectToDrive():
    global drive_api, dataset_len
    print("Initializing Server...")
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
    
    about = drive_api.about().get(fields="user(emailAddress)").execute()
    print("Authenticated as:", about["user"]["emailAddress"])
    # print(f"Loaded {dataset_len} folders")
    # print("All accessible folders:")
    # q = f"'{parent_drive}' in parents and mimeType = 'application/vnd.google-apps.folder'"
    # files = accessFolder(drive_api, parent_drive, q)
    # for f in files:
        # print(f['name'], f['id'])
    if os.path.exists(output_file_path):
        os.remove(output_file_path)
    print("Server open...")

def main():
    connectToDrive()
    prepIndex(drive_api)
    app.run(port=5000)
    # prepData()

if __name__ == '__main__':
    main()

'''
ERRORS:
After the "Finished Prepping data." print, the error is:
PYTHON: ERROR: Invalid shape (257,) for image data
AND:
PYTHON ERROR: 127.0.0.1 - - [16/Jul/2025 15:03:51] "GET /image HTTP/1.1" 500


PROGRAM CRASHES IF TOKEN IS NOT VALID

DOWNLODAING DATA IS OFF, Not sure why it's taking so many attempts
might look into a blocking io with the download function so excess attempts aren't made
also look into the function and see what's wrong and why it's not downloading properly
plt.show seems to be giving an error when trying to show the data.

CURRENT INDEX SYSTEM GOES FOR THE FIRST FILE PER FOLDER, CHANGE TO THIS 
NEW SYSTEM: https://excalidraw.com/#json=g5ySF974d5UF-uMCnRKHU,jddAsImGBUWlP33ItYj_Cw
'''
