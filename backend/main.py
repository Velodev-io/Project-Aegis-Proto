from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import uvicorn
import sqlite3
import os
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from sentinel import analyze_call_transcript, analyze_document_mock, check_for_scams
from advocate import check_bills
from database import init_db, DB_PATH

# Models
class Transcript(BaseModel):
    text: str

class BillRequest(BaseModel):
    service_name: str = "utility_portal"

class ApprovalAction(BaseModel):
    item_id: int
    decision: str # "APPROVE" or "REJECT"

# Database Helpers
def add_pending_bill(service, amount, reasoning):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO pending_bills (service_name, amount, reasoning, status) VALUES (?, ?, ?, 'PENDING')",
              (service, amount, reasoning))
    conn.commit()
    conn.close()

def get_pending_items():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM pending_bills WHERE status='PENDING'")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_item_status(item_id, status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE pending_bills SET status=? WHERE id=?", (status, item_id))
    conn.commit()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for demo purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Aegis Backend Online"}

@app.post("/sentinel/analyze")
def sentinel_analyze(transcript: Transcript):
    """
    Analyzes call text. If suspicious, returns warning.
    """
    result = analyze_call_transcript(transcript.text)
    # If suspicious, one might log it for Steward, but for now just return to App for Alert
    return result

@app.post("/sentinel/scan")
async def sentinel_scan(file: UploadFile = File(...)):
    """
    Analyzes an uploaded document/image.
    """
    # In a real app, we would read file.file and pass to OCR/Vision model.
    # For prototype, we mock the analysis based on filename or random logic.
    return analyze_document_mock(file.filename)

@app.post("/analyze-voice")
def analyze_voice(transcript: Transcript):
    """
    Real-time voice analysis for the Sentinel module.
    """
    return check_for_scams(transcript.text)

@app.post("/advocate/check_bills")
async def advocate_check(request: BillRequest):
    """
    Triggers Playwright to check bills.
    """
    try:
        result = await check_bills(request.service_name)
        
        if result.get("action_required"):
            # Add to Steward Queue
            add_pending_bill(result["service"], result["bill_amount"], result["reasoning"])
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/steward/pending")
def steward_pending():
    """
    Returns pending approvals for Dashboard.
    """
    return get_pending_items()

@app.post("/steward/review")
def steward_review(action: ApprovalAction):
    """
    Approve or Reject a bill.
    """
    update_item_status(action.item_id, action.decision)
    return {"status": "success", "decision": action.decision}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
