#  backend/app/google_sheets_auth_setup.py
import os
import pickle
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import gspread

# Google API Scopes
SCOPES = list([
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://docs.google.com/spreadsheets/d/1GCtZ7pcFsqcIvbkhq9q-b3YmBZxEQ120UCIU_X5CuP8/edit?usp=sharing',
    'https://www.googleapis.com/auth/drive'
])

# Google Sheets API
client_config = {
    "installed": {
        "client_id": os.getenv('GOOGLE_CLIENT_ID'),
        "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
        "redirect_uris": ["http://localhost"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }
}

flow = InstalledAppFlow.from_client_config(
    client_config,
    SCOPES
)

creds = None
token_path = os.getenv('TOKEN_PATH', 'token.pickle')

# Load existing credentials if available
if os.path.exists(token_path):
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)

# If no valid credentials, authenticate
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        creds = flow.run_local_server(
            login_hint=os.getenv('ADMIN_EMAIL'),
            port=0
        )
    
    # Save credentials
    with open(token_path, 'wb') as token:
        pickle.dump(creds, token)

# Authorize client
client = gspread.authorize(creds)

try:
    sheet = client.open_by_key('1GCtZ7pcFsqcIvbkhq9q-b3YmBZxEQ120UCIU_X5CuP8').sheet1
    records = sheet.get_all_records()
except Exception as e:
    print(f"Failed to access Google Sheet: {str(e)}")

# google_sheets_auth_setup.py
import gspread

def setup_google_auth():
    print("Starting Google Sheets authentication setup...")
    print("A browser window will open - please login with sumitkumar@tagglabs.in")
    
    # This will create two files:
    # - credentials.json (client config)
    # - authorized_user.json (auth tokens)
    gc = gspread.oauth()
    
    print("\n✔ Authentication successful!")
    print("Two files were created:")
    print("- credentials.json")
    print("- authorized_user.json")
    print("\nYou can now use the main application")

if __name__ == "__main__":
    setup_google_auth()