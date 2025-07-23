from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
from app.helpers.by_keyword import find_data_by_keyword

SERVICE_ACCOUNT_FILE = os.path.join(os.getcwd(), "service_account.json")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1EOEqg2eGsCvUk1DAAmRRpjhS1k3q65o_nh56LBlAdQE"  # ← Replace this

def get_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
    )
    return build("sheets", "v4", credentials=creds)

def read_sheet(range_: str):
    service = get_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=range_
    ).execute()
    return result.get("values", [])

def write_sheet(range_: str, values: list):
    service = get_service()
    body = {"values": values}
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_,
        valueInputOption="RAW",
        body=body
    ).execute()
