import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

from dotenv import load_dotenv
load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
ID_LISTS = ["1EOEqg2eGsCvUk1DAAmRRpjhS1k3q65o_nh56LBlAdQE","1HLsGWTxg3rBGb6RMu7aokM1OZgWuFJWkABkDBNg6PGI",
            "1tJeIynoBoCjORuWxCUyAy2MTYozaA9BWIC1gW0xzKO4","14b7GdGwAnHINf3NCTOkWVMKHFArCRAhY7qRizRXf_y4"]
SPREADSHEET_ID = "1EOEqg2eGsCvUk1DAAmRRpjhS1k3q65o_nh56LBlAdQE"

def get_service():
    private_key = os.getenv("GOOGLE_PRIVATE_KEY").replace("\\n", "\n")
    print("Private key (first 100 chars):", os.getenv("GOOGLE_PRIVATE_KEY")[:100])
    print("Private key (decoded preview):", private_key[:100])
    service_info = {
        "type": os.getenv("GOOGLE_TYPE"),
        "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
        "private_key": private_key,
        "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
        "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_CERT_URL"),
        "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_CERT_URL"),
        "universe_domain": os.getenv("GOOGLE_UNIVERSE_DOMAIN"),
    }

    creds = service_account.Credentials.from_service_account_info(service_info, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


def read_sheet(range_: str, type:str):
    sheet_id = ""
    if type == "fb":
        sheet_id = ID_LISTS[0]
    elif type == "ig":
        sheet_id = ID_LISTS[1]
    elif type == "yt":
        sheet_id = ID_LISTS[2]
    elif type == "x":
        sheet_id = ID_LISTS[3]
    service = get_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=range_
    ).execute()
    return result.get("values", [])

# def write_sheet(range_: str, values: list):
#     service = get_service()
#     body = {"values": values}
#     service.spreadsheets().values().update(
#         spreadsheetId=SPREADSHEET_ID,
#         range=range_,
#         valueInputOption="RAW",
#         body=body
#     ).execute()
