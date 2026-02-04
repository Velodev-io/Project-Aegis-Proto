"""
Project Aegis: Sentinel Module API
Production-grade FastAPI backend for scam detection and transaction governance
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import logging

# Import custom modules
from models import Base, SecurityLog, PendingApproval
from sentinel_analyzer import AgenticScamAnalyzer
from transaction_governor import ContextAwareGovernor
from advocate_notifier import TrustedAdvocateNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Project Aegis - Sentinel Module",
    description="AI-powered scam detection and transaction governance",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "sqlite:///./data/aegis_trust_vault.db"
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=None  # Disable connection pooling for SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize services
scam_analyzer = AgenticScamAnalyzer(llm_enabled=False)
transaction_governor = ContextAwareGovernor()
advocate_notifier = TrustedAdvocateNotifier(webhook_url=None)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class VoiceInterceptRequest(BaseModel):
    """Request model for voice call interception"""
    transcript: str = Field(..., description="Real-time text transcript of the call")
    user_id: Optional[str] = Field(None, description="Protected user identifier")
    call_metadata: Optional[dict] = Field(None, description="Additional call metadata")


class VoiceInterceptResponse(BaseModel):
    """Response model for voice call analysis"""
    fraud_score: float = Field(..., description="Fraud score (0-100)")
    action: str = Field(..., description="Recommended action")
    reasoning: str = Field(..., description="Analysis reasoning")
    indicators: List[dict] = Field(..., description="Detected scam indicators")
    security_log_id: int = Field(..., description="Security log entry ID")
    advocate_notified: bool = Field(..., description="Whether advocate was notified")


class TransactionMonitorRequest(BaseModel):
    """Request model for transaction monitoring"""
    amount: float = Field(..., description="Transaction amount in dollars")
    transaction_time: datetime = Field(..., description="Transaction timestamp")
    category: str = Field(..., description="Transaction category")
    merchant: str = Field(..., description="Merchant name")
    user_id: Optional[str] = Field(None, description="User identifier")
    transaction_metadata: Optional[dict] = Field(None, description="Additional metadata")


class TransactionMonitorResponse(BaseModel):
    """Response model for transaction analysis"""
    risk_level: str = Field(..., description="Risk level assessment")
    risk_score: float = Field(..., description="Risk score (0-100)")
    status: str = Field(..., description="Approval status")
    reasoning: str = Field(..., description="Analysis reasoning")
    flags: List[str] = Field(..., description="Risk flags")
    security_log_id: int = Field(..., description="Security log entry ID")
    approval_id: Optional[int] = Field(None, description="Pending approval ID if applicable")
    advocate_notified: bool = Field(..., description="Whether advocate was notified")


# ============================================================================
# SENTINEL ENDPOINTS
# ============================================================================

@app.post("/sentinel/voice/intercept", response_model=VoiceInterceptResponse)
async def intercept_voice_call(
    request: VoiceInterceptRequest,
    db: Session = Depends(get_db)
):
    """
    Scam Interceptor Endpoint
    
    Analyzes real-time call transcripts for scam indicators and takes
    appropriate action (block, activate answer bot, or allow).
    """
    try:
        logger.info(f"Analyzing call transcript for user: {request.user_id}")
        
        # Analyze transcript
        analysis = scam_analyzer.analyze(request.transcript)
        
        # Create security log
        security_log = SecurityLog(
            event_type="SCAM_CALL",
            transcript=request.transcript,
            fraud_score=analysis["fraud_score"],
            scam_indicators=analysis["indicators"],
            action_taken=analysis["action"],
            reasoning=analysis["reasoning"],
            user_id=request.user_id,
            event_metadata=request.call_metadata
        )
        
        db.add(security_log)
        db.commit()
        db.refresh(security_log)
        
        # Notify advocate if high risk
        advocate_notified = False
        if analysis["fraud_score"] > 50:
            await advocate_notifier.notify_scam_detected(
                user_id=request.user_id or "unknown",
                fraud_score=analysis["fraud_score"],
                action=analysis["action"],
                reasoning=analysis["reasoning"],
                transcript=request.transcript
            )
            advocate_notified = True
            security_log.advocate_notified = True
            security_log.advocate_notification_time = datetime.utcnow()
            db.commit()
        
        logger.info(
            f"Call analysis complete: Score={analysis['fraud_score']}, "
            f"Action={analysis['action']}"
        )
        
        return VoiceInterceptResponse(
            fraud_score=analysis["fraud_score"],
            action=analysis["action"],
            reasoning=analysis["reasoning"],
            indicators=analysis["indicators"],
            security_log_id=security_log.id,
            advocate_notified=advocate_notified
        )
        
    except Exception as e:
        logger.error(f"Error analyzing call: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sentinel/transactions/monitor", response_model=TransactionMonitorResponse)
async def monitor_transaction(
    request: TransactionMonitorRequest,
    db: Session = Depends(get_db)
):
    """
    Spending Governance Endpoint
    
    Monitors transactions for suspicious patterns and flags high-risk
    spending for Trusted Advocate approval.
    """
    try:
        logger.info(
            f"Monitoring transaction: ${request.amount} at {request.merchant} "
            f"for user: {request.user_id}"
        )
        
        # Analyze transaction
        analysis = transaction_governor.analyze_transaction(
            amount=request.amount,
            transaction_time=request.transaction_time,
            category=request.category,
            merchant=request.merchant,
            user_id=request.user_id
        )
        
        # Create security log
        security_log = SecurityLog(
            event_type="TRANSACTION",
            transaction_amount=request.amount,
            transaction_time=request.transaction_time,
            transaction_category=request.category,
            merchant=request.merchant,
            risk_level=analysis["risk_level"],
            approval_status=analysis["status"],
            reasoning=analysis["reasoning"],
            user_id=request.user_id,
            event_metadata={
                "flags": analysis["flags"],
                "risk_score": analysis["risk_score"],
                **(request.transaction_metadata or {})
            }
        )
        
        db.add(security_log)
        db.commit()
        db.refresh(security_log)
        
        # Create pending approval if needed
        approval_id = None
        advocate_notified = False
        
        if analysis["status"] == "PENDING_APPROVAL":
            pending_approval = PendingApproval(
                security_log_id=security_log.id
            )
            db.add(pending_approval)
            db.commit()
            db.refresh(pending_approval)
            approval_id = pending_approval.id
            
            # Notify advocate
            await advocate_notifier.notify_transaction_pending(
                user_id=request.user_id or "unknown",
                amount=request.amount,
                merchant=request.merchant,
                category=request.category,
                risk_level=analysis["risk_level"],
                reasoning=analysis["reasoning"],
                approval_id=approval_id
            )
            advocate_notified = True
            security_log.advocate_notified = True
            security_log.advocate_notification_time = datetime.utcnow()
            db.commit()
        
        logger.info(
            f"Transaction analysis complete: Risk={analysis['risk_level']}, "
            f"Status={analysis['status']}"
        )
        
        return TransactionMonitorResponse(
            risk_level=analysis["risk_level"],
            risk_score=analysis["risk_score"],
            status=analysis["status"],
            reasoning=analysis["reasoning"],
            flags=analysis["flags"],
            security_log_id=security_log.id,
            approval_id=approval_id,
            advocate_notified=advocate_notified
        )
        
    except Exception as e:
        logger.error(f"Error monitoring transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Project Aegis - Sentinel Module",
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/sentinel/logs")
async def get_security_logs(
    limit: int = 50,
    event_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get security logs for audit trail"""
    query = db.query(SecurityLog)
    
    if event_type:
        query = query.filter(SecurityLog.event_type == event_type)
    
    logs = query.order_by(SecurityLog.timestamp.desc()).limit(limit).all()
    
    return {
        "count": len(logs),
        "logs": [
            {
                "id": log.id,
                "event_type": log.event_type,
                "timestamp": log.timestamp.isoformat(),
                "fraud_score": log.fraud_score,
                "risk_level": log.risk_level,
                "action_taken": log.action_taken,
                "approval_status": log.approval_status,
                "advocate_notified": log.advocate_notified
            }
            for log in logs
        ]
    }


@app.get("/sentinel/approvals/pending")
async def get_pending_approvals(db: Session = Depends(get_db)):
    """Get all pending approvals for Trusted Advocate review"""
    approvals = db.query(PendingApproval).filter(
        PendingApproval.decision == None
    ).all()
    
    result = []
    for approval in approvals:
        log = db.query(SecurityLog).filter(
            SecurityLog.id == approval.security_log_id
        ).first()
        
        if log:
            result.append({
                "approval_id": approval.id,
                "created_at": approval.created_at.isoformat(),
                "transaction": {
                    "amount": log.transaction_amount,
                    "merchant": log.merchant,
                    "category": log.transaction_category,
                    "time": log.transaction_time.isoformat() if log.transaction_time else None
                },
                "risk_level": log.risk_level,
                "reasoning": log.reasoning
            })
    
    return {"count": len(result), "approvals": result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
