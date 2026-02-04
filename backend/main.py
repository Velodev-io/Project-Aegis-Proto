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

# Import Sentinel Module components
try:
    from sentinel_analyzer import AgenticScamAnalyzer
    from transaction_governor import ContextAwareGovernor
    from advocate_notifier import TrustedAdvocateNotifier
    from models import Base, SecurityLog, PendingApproval
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    SENTINEL_MODULE_AVAILABLE = True
except ImportError:
    SENTINEL_MODULE_AVAILABLE = False
    print("⚠️  Sentinel Module not available - using legacy endpoints only")

# Import Advocate Module components
try:
    from advocate_bill_auditor import AgenticAuditor, InsurancePolicy, LineItem
    from advocate_subscription_detector import SubscriptionDetector, Transaction
    from advocate_cancellation_agent import CancellationAgent
    from advocate_negotiation_agent import NegotiationScriptGenerator
    from datetime import datetime
    from typing import List, Dict, Optional
    ADVOCATE_MODULE_AVAILABLE = True
except ImportError:
    ADVOCATE_MODULE_AVAILABLE = False
    print("⚠️  Advocate Module not available - using legacy endpoints only")

# Import Proxy Module (Module C) components
try:
    from proxy_api import router as proxy_router
    PROXY_MODULE_AVAILABLE = True
except ImportError:
    PROXY_MODULE_AVAILABLE = False
    print("⚠️  Proxy Module (Module C) not available")

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

# Register Module C Router
if PROXY_MODULE_AVAILABLE:
    app.include_router(proxy_router)
    print("✅ Module C (The Proxy) endpoints registered")

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

# ============================================================================
# ADVOCATE MODULE ENDPOINTS
# ============================================================================

if ADVOCATE_MODULE_AVAILABLE:
    # Initialize Advocate components
    insurance_policy = InsurancePolicy("PPO")
    bill_auditor = AgenticAuditor(insurance_policy)
    subscription_detector = SubscriptionDetector()
    cancellation_agent = CancellationAgent(read_only=True)
    script_generator = NegotiationScriptGenerator()
    
    # Pydantic models for Advocate
    class BillAnalysisRequest(BaseModel):
        line_items: List[Dict]
        is_in_network: bool = True
        previous_bills: Optional[List[List[Dict]]] = None
    
    class SubscriptionAuditRequest(BaseModel):
        transactions: List[Dict]
        usage_data: Optional[Dict[str, int]] = None
    
    class NegotiationScriptRequest(BaseModel):
        script_type: str
        merchant: str
        errors: Optional[List[Dict]] = None
        total_disputed: Optional[float] = None
        policy_holder_name: Optional[str] = None
        subscription_amount: Optional[float] = None
        months_unused: Optional[int] = None
        reason: Optional[str] = None
    
    @app.post("/advocate/analyze-bill")
    async def analyze_bill(request: BillAnalysisRequest):
        """Analyze medical bill for errors"""
        # Convert dict line items to LineItem objects
        line_items = []
        for item in request.line_items:
            line_items.append(LineItem(
                code=item["code"],
                description=item["description"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                total=item["total"],
                date_of_service=datetime.fromisoformat(item["date_of_service"]) if item.get("date_of_service") else None
            ))
        
        # Convert previous bills if provided
        previous_bills = None
        if request.previous_bills:
            previous_bills = []
            for prev_bill in request.previous_bills:
                prev_items = []
                for item in prev_bill:
                    prev_items.append(LineItem(
                        code=item["code"],
                        description=item["description"],
                        quantity=item["quantity"],
                        unit_price=item["unit_price"],
                        total=item["total"],
                        date_of_service=datetime.fromisoformat(item["date_of_service"]) if item.get("date_of_service") else None
                    ))
                previous_bills.append(prev_items)
        
        # Analyze bill
        analysis = bill_auditor.analyze_bill(
            line_items=line_items,
            is_in_network=request.is_in_network,
            previous_bills=previous_bills
        )
        
        # Generate negotiation script if errors found
        negotiation_script = None
        if analysis.errors and analysis.potential_savings > 0:
            script = script_generator.generate_medical_bill_dispute(
                provider_name="Medical Provider",
                errors=analysis.errors,
                total_disputed=analysis.potential_savings,
                policy_holder_name="Patient"
            )
            negotiation_script = script_generator.format_script_for_human(script)
        
        return {
            "total_billed": analysis.total_billed,
            "total_allowed": analysis.total_allowed,
            "potential_savings": analysis.potential_savings,
            "errors": analysis.errors,
            "recommendations": analysis.recommendations,
            "risk_score": analysis.risk_score,
            "negotiation_script": negotiation_script,
            "action_required": analysis.risk_score > 50,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @app.post("/advocate/subscriptions/audit")
    async def audit_subscriptions(request: SubscriptionAuditRequest):
        """Detect and analyze subscriptions from transaction history"""
        # Convert dict transactions to Transaction objects
        transactions = []
        for txn in request.transactions:
            transactions.append(Transaction(
                date=datetime.fromisoformat(txn["date"]),
                merchant=txn["merchant"],
                amount=txn["amount"],
                category=txn["category"],
                description=txn["description"]
            ))
        
        # Detect subscriptions
        subscriptions = subscription_detector.detect_subscriptions(
            transactions=transactions,
            usage_data=request.usage_data
        )
        
        # Calculate totals
        total_monthly_cost = sum(
            sub.average_amount if sub.frequency == "MONTHLY" else sub.average_amount / 12
            for sub in subscriptions
        )
        
        potential_savings = sum(
            (sub.average_amount if sub.frequency == "MONTHLY" else sub.average_amount / 12)
            for sub in subscriptions
            if sub.recommendation == "CANCEL"
        )
        
        # Convert to dict
        subscriptions_dict = []
        for sub in subscriptions:
            subscriptions_dict.append({
                "merchant": sub.merchant,
                "frequency": sub.frequency,
                "average_amount": sub.average_amount,
                "last_charge": sub.last_charge.isoformat(),
                "total_charges": sub.total_charges,
                "total_spent": sub.total_spent,
                "confidence": sub.confidence,
                "usage_score": sub.usage_score,
                "recommendation": sub.recommendation,
                "reasoning": sub.reasoning
            })
        
        return {
            "subscriptions": subscriptions_dict,
            "total_monthly_cost": total_monthly_cost,
            "potential_monthly_savings": potential_savings,
            "potential_annual_savings": potential_savings * 12,
            "action_required": potential_savings > 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @app.post("/advocate/generate-script")
    async def generate_negotiation_script(request: NegotiationScriptRequest):
        """Generate professional negotiation script"""
        if request.script_type == "MEDICAL_BILL":
            if not request.errors or request.total_disputed is None:
                raise HTTPException(
                    status_code=400,
                    detail="Medical bill script requires 'errors' and 'total_disputed'"
                )
            
            script = script_generator.generate_medical_bill_dispute(
                provider_name=request.merchant,
                errors=request.errors,
                total_disputed=request.total_disputed,
                policy_holder_name=request.policy_holder_name or "Patient"
            )
        
        elif request.script_type == "SUBSCRIPTION":
            if request.subscription_amount is None or request.months_unused is None:
                raise HTTPException(
                    status_code=400,
                    detail="Subscription script requires 'subscription_amount' and 'months_unused'"
                )
            
            script = script_generator.generate_subscription_cancellation_dispute(
                merchant=request.merchant,
                subscription_amount=request.subscription_amount,
                months_unused=request.months_unused,
                reason=request.reason or "zero usage detected"
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown script type: {request.script_type}"
            )
        
        return {
            "merchant": script.merchant,
            "script_type": script.script_type,
            "tone": script.tone,
            "estimated_duration": script.estimated_duration,
            "formatted_script": script_generator.format_script_for_human(script),
            "voice_script": script_generator.format_script_for_voice(script),
            "expected_outcome": script.expected_outcome,
            "fallback_options": script.fallback_options
        }
    
    @app.get("/advocate/summary")
    async def get_advocate_summary():
        """Get summary of Advocate module capabilities"""
        return {
            "module": "Advocate",
            "status": "operational",
            "capabilities": {
                "medical_bill_forensics": {
                    "available": True,
                    "features": [
                        "Upcoding detection",
                        "Duplicate billing detection",
                        "Unbundling detection",
                        "Insurance policy verification",
                        "Negotiation script generation"
                    ]
                },
                "subscription_management": {
                    "available": True,
                    "features": [
                        "Subscription detection from transactions",
                        "Usage analysis",
                        "Cancellation recommendations",
                        "Autonomous cancellation (shadow mode)",
                        "Dark pattern detection"
                    ]
                },
                "negotiation": {
                    "available": True,
                    "features": [
                        "Professional script generation",
                        "Medical bill disputes",
                        "Subscription cancellations",
                        "Price negotiations"
                    ]
                }
            },
            "safety_features": {
                "shadow_mode": True,
                "human_approval_required": True,
                "audit_trail": True
            }
        }


# ============================================================================
# SENTINEL MODULE ENDPOINTS
# ============================================================================

if SENTINEL_MODULE_AVAILABLE:
    # Initialize Sentinel components
    scam_analyzer = AgenticScamAnalyzer(llm_enabled=False)
    transaction_governor = ContextAwareGovernor()
    advocate_notifier = TrustedAdvocateNotifier(webhook_url=None)
    
    # Database setup for Sentinel
    SENTINEL_DB_URL = "sqlite:///./data/aegis_trust_vault.db"
    sentinel_engine = create_engine(
        SENTINEL_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=None
    )
    Base.metadata.create_all(bind=sentinel_engine)
    SentinelSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sentinel_engine)
    
    # Pydantic models for Sentinel
    class VoiceInterceptRequest(BaseModel):
        transcript: str
        user_id: str = "senior_001"
        call_metadata: dict = None
    
    class TransactionMonitorRequest(BaseModel):
        amount: float
        transaction_time: str
        category: str
        merchant: str
        user_id: str = "senior_001"
        transaction_metadata: dict = None
    
    @app.post("/sentinel/voice/intercept")
    async def intercept_voice_call(request: VoiceInterceptRequest):
        """Scam Interceptor Endpoint"""
        from datetime import datetime
        
        db = SentinelSessionLocal()
        try:
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
                    user_id=request.user_id,
                    fraud_score=analysis["fraud_score"],
                    action=analysis["action"],
                    reasoning=analysis["reasoning"],
                    transcript=request.transcript
                )
                advocate_notified = True
                security_log.advocate_notified = True
                security_log.advocate_notification_time = datetime.utcnow()
                db.commit()
            
            return {
                "fraud_score": analysis["fraud_score"],
                "action": analysis["action"],
                "reasoning": analysis["reasoning"],
                "indicators": analysis["indicators"],
                "security_log_id": security_log.id,
                "advocate_notified": advocate_notified
            }
        finally:
            db.close()
    
    @app.post("/sentinel/transactions/monitor")
    async def monitor_transaction(request: TransactionMonitorRequest):
        """Spending Governance Endpoint"""
        from datetime import datetime
        
        db = SentinelSessionLocal()
        try:
            # Parse transaction time
            transaction_time = datetime.fromisoformat(request.transaction_time.replace('Z', '+00:00'))
            
            # Analyze transaction
            analysis = transaction_governor.analyze_transaction(
                amount=request.amount,
                transaction_time=transaction_time,
                category=request.category,
                merchant=request.merchant,
                user_id=request.user_id
            )
            
            # Create security log
            security_log = SecurityLog(
                event_type="TRANSACTION",
                transaction_amount=request.amount,
                transaction_time=transaction_time,
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
                    user_id=request.user_id,
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
            
            return {
                "risk_level": analysis["risk_level"],
                "risk_score": analysis["risk_score"],
                "status": analysis["status"],
                "reasoning": analysis["reasoning"],
                "flags": analysis["flags"],
                "security_log_id": security_log.id,
                "approval_id": approval_id,
                "advocate_notified": advocate_notified
            }
        finally:
            db.close()
    
    @app.get("/sentinel/logs")
    def get_security_logs(limit: int = 50, event_type: str = None):
        """Get security logs for audit trail"""
        db = SentinelSessionLocal()
        try:
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
        finally:
            db.close()
    
    @app.get("/sentinel/approvals/pending")
    def get_pending_approvals():
        """Get all pending approvals for Trusted Advocate review"""
        db = SentinelSessionLocal()
        try:
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
        finally:
            db.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
