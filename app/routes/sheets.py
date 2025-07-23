from fastapi import APIRouter
from app.services import sheets_api

router = APIRouter(prefix="/sheets", tags=["sheets"])

@router.get("/read")
def read_demo():
    values = sheets_api.read_sheet("BAJI!A1:ZZ")
    return {"values": values}

@router.post("/write")
def write_demo():
    values = [["Name", "Email", "Age"], ["Alice", "alice@example.com", "25"]]
    sheets_api.write_sheet("Sheet1!A1", values)
    return {"status": "ok"}
