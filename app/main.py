# app/main.py

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from app.utils import generate_report, save_upload_file, load_rules
from app.auth import get_api_key
from app.scheduler import start_scheduler
import os

app = FastAPI(title="Report Generator Microservice")

UPLOAD_DIR = "uploads"
REPORT_FILE = os.path.join(UPLOAD_DIR, "output.csv")
RULES_FILE = os.path.join(UPLOAD_DIR, "rules.yaml")

os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload/input", dependencies=[Depends(get_api_key)])
async def upload_input(file: UploadFile = File(...)):
    await save_upload_file(file, "input.csv")
    return {"message": "input.csv uploaded successfully"}

@app.post("/upload/reference", dependencies=[Depends(get_api_key)])
async def upload_reference(file: UploadFile = File(...)):
    await save_upload_file(file, "reference.csv")
    return {"message": "reference.csv uploaded successfully"}

@app.post("/configure_rules", dependencies=[Depends(get_api_key)])
async def configure_rules(file: UploadFile = File(...)):
    await save_upload_file(file, "rules.yaml")
    return {"message": "Rules updated successfully"}

@app.post("/trigger_report", dependencies=[Depends(get_api_key)])
def trigger_report():
    try:
        rules = load_rules(RULES_FILE)
        generate_report(rules)
        return {"message": "Report generated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download_report", dependencies=[Depends(get_api_key)])
def download_report():
    if not os.path.exists(REPORT_FILE):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(REPORT_FILE, media_type='text/csv', filename="output.csv")

# Start scheduler
def start():
    start_scheduler()

start()
