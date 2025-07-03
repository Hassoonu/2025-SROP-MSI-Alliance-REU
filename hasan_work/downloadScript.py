from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import requests
import os

# thank you chatGPT, most this script was due to chatGPT

# If modifying these scopes, delete the token.json file
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate_drive():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def upload_to_drive(service, file_path, parent_folder_id=None):
    file_metadata = {'name': os.path.basename(file_path)}
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]

    media = MediaFileUpload(file_path, mimetype='image/tiff')
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    print(f'Uploaded: {file_path} → Drive file ID: {file.get("id")}')

from googleapiclient.http import MediaFileUpload

# Replace with your actual .tif download URLs (this is where your STAC filter comes in)
tif_urls = [
    "https://data.pgc.umn.edu/elev/dem/setsm/ArcticDEM/strips/s2s041/2m/n65w155/SETSM_s2s041_WV01_20240920_..._2m_dem.tif",
    # add more URLs here
]

# Local temp directory to save before uploading
local_dir = "./downloaded_tifs"
os.makedirs(local_dir, exist_ok=True)

# Authenticate
service = authenticate_drive()

# Loop through and download/upload
for url in tif_urls:
    filename = url.split("/")[-1]
    filepath = os.path.join(local_dir, filename)
    
    print(f"Downloading {url}")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    upload_to_drive(service, filepath)
