"""
Module C: The Proxy - FastAPI Endpoints
Digital POA Vault, Token Gatekeeper, Break-Glass Protocol, and Audit Trail
"""
from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from proxy_models import SmartPOA, EncryptedToken, AuditLog, BreakGlassEvent
from proxy_vault import SmartPOAManager, TokenGatekeeper, CredentialPresenter
from proxy_break_glass import BreakGlassMonitor
from proxy_audit import FiduciaryLogger, LegalExporter
from models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/aegis_trust_vault.db")
engine = create_engine(
    DATABASE_URL.replace("sqlite:///", "sqlite:///"),
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    poolclass=None
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Router
router = APIRouter(prefix="/proxy", tags=["Module C - The Proxy"])


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class CreatePOARequest(BaseModel):
    senior_id: str
    agent_id: str
    scope: str  # 'utilities', 'banking', 'healthcare', 'subscriptions'
    spend_limit: float
    expiry_days: int = 30
    specific_services: Optional[List[str]] = None
    created_by: Optional[str] = None


class StoreTokenRequest(BaseModel):
    poa_id: int
    service_name: str
    token: str
    token_type: str = "access"
    expires_in_seconds: Optional[int] = None


class ValidateRequestModel(BaseModel):
    poa_id: int
    service_name: str
    amount: Optional[float] = None
    action: str = "access"


class Verify2FARequest(BaseModel):
    event_id: int
    code: str


class VerifyLivenessRequest(BaseModel):
    event_id: int
    method: str = "face"  # 'face' or 'voice'
    verification_data: Dict[str, Any] = {}


class DenyBreakGlassRequest(BaseModel):
    event_id: int
    denied_by: str
    reason: str


# ============================================================================
# VAULT ENDPOINTS
# ============================================================================

@router.post("/vault/poa")
def create_smart_poa(request: CreatePOARequest, db: Session = Depends(get_db)):
    """
    Create a new Smart POA with granular permissions
    
    Example: "Agent can negotiate AT&T bill, max $100, expires in 30 days"
    """
    manager = SmartPOAManager(db)
    
    poa = manager.create_poa(
        senior_id=request.senior_id,
        agent_id=request.agent_id,
        scope=request.scope,
        spend_limit=request.spend_limit,
        expiry_days=request.expiry_days,
        specific_services=request.specific_services,
        created_by=request.created_by
    )
    
    return {
        "success": True,
        "poa_id": poa.id,
        "senior_id": poa.senior_id,
        "agent_id": poa.agent_id,
        "scope": poa.scope,
        "spend_limit": poa.spend_limit,
        "expiry_date": poa.expiry_date.isoformat(),
        "is_active": poa.is_active,
        "message": f"Smart POA created successfully. Valid until {poa.expiry_date.strftime('%Y-%m-%d')}"
    }


@router.get("/vault/poa/{poa_id}")
def get_poa(poa_id: int, db: Session = Depends(get_db)):
    """Retrieve POA by ID"""
    manager = SmartPOAManager(db)
    poa = manager.get_poa(poa_id)
    
    if not poa:
        raise HTTPException(status_code=404, detail="POA not found")
    
    return {
        "poa_id": poa.id,
        "senior_id": poa.senior_id,
        "agent_id": poa.agent_id,
        "scope": poa.scope,
        "spend_limit": poa.spend_limit,
        "specific_services": poa.specific_services,
        "expiry_date": poa.expiry_date.isoformat(),
        "created_at": poa.created_at.isoformat(),
        "is_active": poa.is_active,
        "is_valid": poa.is_valid(),
        "revoked_at": poa.revoked_at.isoformat() if poa.revoked_at else None,
        "revocation_reason": poa.revocation_reason
    }


@router.delete("/vault/poa/{poa_id}")
def revoke_poa(poa_id: int, reason: str, revoked_by: str, db: Session = Depends(get_db)):
    """Revoke a POA"""
    manager = SmartPOAManager(db)
    success = manager.revoke_poa(poa_id, reason, revoked_by)
    
    if not success:
        raise HTTPException(status_code=404, detail="POA not found")
    
    return {
        "success": True,
        "poa_id": poa_id,
        "message": f"POA revoked: {reason}"
    }


@router.get("/vault/poa/senior/{senior_id}")
def get_poas_by_senior(senior_id: str, active_only: bool = True, db: Session = Depends(get_db)):
    """Get all POAs for a senior"""
    manager = SmartPOAManager(db)
    poas = manager.get_poas_by_senior(senior_id, active_only)
    
    return {
        "senior_id": senior_id,
        "total_poas": len(poas),
        "poas": [
            {
                "poa_id": poa.id,
                "agent_id": poa.agent_id,
                "scope": poa.scope,
                "spend_limit": poa.spend_limit,
                "expiry_date": poa.expiry_date.isoformat(),
                "is_valid": poa.is_valid()
            }
            for poa in poas
        ]
    }


# ============================================================================
# TOKEN MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/tokens/store")
def store_oauth_token(request: StoreTokenRequest, db: Session = Depends(get_db)):
    """Store encrypted OAuth token"""
    manager = SmartPOAManager(db)
    
    token_record = manager.store_oauth_token(
        poa_id=request.poa_id,
        service_name=request.service_name,
        token=request.token,
        token_type=request.token_type,
        expires_in_seconds=request.expires_in_seconds
    )
    
    return {
        "success": True,
        "token_id": token_record.id,
        "poa_id": token_record.poa_id,
        "service_name": token_record.service_name,
        "expires_at": token_record.expires_at.isoformat() if token_record.expires_at else None,
        "message": "Token stored securely with Fernet encryption"
    }


@router.post("/tokens/validate")
def validate_request(request: ValidateRequestModel, db: Session = Depends(get_db)):
    """
    Validate request against POA scope and limits
    
    This is the TOKEN GATEKEEPER - blocks unauthorized access
    """
    gatekeeper = TokenGatekeeper(db)
    
    result = gatekeeper.validate_request(
        poa_id=request.poa_id,
        service_name=request.service_name,
        amount=request.amount,
        action=request.action
    )
    
    # If break-glass triggered, create event
    if result["decision"] == "BREAK_GLASS":
        monitor = BreakGlassMonitor(db)
        event = monitor.trigger_break_glass(
            audit_log_id=result["audit_log_id"],
            trigger_reason=result["violation_type"],
            trigger_details={
                "service_name": request.service_name,
                "amount": request.amount,
                "spend_limit": result["poa"].spend_limit
            },
            advocate_id=os.getenv("TRUSTED_ADVOCATE_EMAIL", "advocate@example.com"),
            require_liveness=request.amount and request.amount > 500  # Liveness for >$500
        )
        
        result["break_glass_event_id"] = event.id
        result["two_fa_required"] = True
        result["liveness_required"] = event.liveness_required
    
    return result


@router.get("/tokens/decrypt/{token_id}")
def decrypt_token(token_id: int, db: Session = Depends(get_db)):
    """Decrypt OAuth token for authorized use"""
    manager = SmartPOAManager(db)
    token = manager.get_decrypted_token(token_id)
    
    if not token:
        raise HTTPException(status_code=404, detail="Token not found or expired")
    
    return {
        "success": True,
        "token": token,
        "message": "Token decrypted successfully"
    }


# ============================================================================
# BREAK-GLASS ENDPOINTS
# ============================================================================

@router.post("/break-glass/verify-2fa")
def verify_2fa(request: Verify2FARequest, db: Session = Depends(get_db)):
    """Verify 2FA code for break-glass event"""
    monitor = BreakGlassMonitor(db)
    result = monitor.verify_2fa(request.event_id, request.code)
    
    if not result.get("verified"):
        raise HTTPException(status_code=400, detail=result.get("error", "Verification failed"))
    
    return result


@router.post("/break-glass/verify-liveness")
def verify_liveness(request: VerifyLivenessRequest, db: Session = Depends(get_db)):
    """Verify liveness (face/voice) for break-glass event"""
    monitor = BreakGlassMonitor(db)
    result = monitor.verify_liveness(
        event_id=request.event_id,
        verification_data=request.verification_data,
        method=request.method
    )
    
    if not result.get("verified"):
        raise HTTPException(status_code=400, detail=result.get("error", "Liveness verification failed"))
    
    return result


@router.post("/break-glass/deny")
def deny_break_glass(request: DenyBreakGlassRequest, db: Session = Depends(get_db)):
    """Deny break-glass request"""
    monitor = BreakGlassMonitor(db)
    result = monitor.deny_break_glass(
        event_id=request.event_id,
        denied_by=request.denied_by,
        reason=request.reason
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Denial failed"))
    
    return result


@router.get("/break-glass/pending")
def get_pending_break_glass(advocate_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Get all pending break-glass events"""
    monitor = BreakGlassMonitor(db)
    events = monitor.get_pending_events(advocate_id)
    
    return {
        "total_pending": len(events),
        "events": [
            {
                "event_id": event.id,
                "trigger_reason": event.trigger_reason,
                "status": event.status,
                "created_at": event.created_at.isoformat(),
                "expires_at": event.expires_at.isoformat(),
                "liveness_required": event.liveness_required,
                "two_fa_verified": event.two_fa_verified_at is not None
            }
            for event in events
        ]
    }


# ============================================================================
# AUDIT TRAIL ENDPOINTS
# ============================================================================

@router.get("/audit/logs/{poa_id}")
def get_audit_logs(
    poa_id: int,
    action_type: Optional[str] = None,
    decision: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get audit logs for a POA"""
    logger = FiduciaryLogger(db)
    logs = logger.get_logs_by_poa(poa_id, action_type, decision, limit)
    
    return {
        "poa_id": poa_id,
        "total_logs": len(logs),
        "logs": [
            {
                "log_id": log.id,
                "action_type": log.action_type,
                "timestamp": log.timestamp.isoformat(),
                "decision": log.decision,
                "reasoning": log.reasoning,
                "service_name": log.service_name,
                "amount": log.amount,
                "signature": log.signature[:32] + "...",  # Truncate for display
                "advocate_notified": log.advocate_notified
            }
            for log in logs
        ]
    }


@router.get("/audit/export/{poa_id}")
def export_audit_trail(poa_id: int, format: str = "json", db: Session = Depends(get_db)):
    """Export audit trail (JSON or PDF)"""
    if format == "json":
        logger = FiduciaryLogger(db)
        json_data = logger.export_logs_json(poa_id)
        return Response(content=json_data, media_type="application/json")
    
    elif format == "pdf":
        exporter = LegalExporter(db)
        pdf_data = exporter.generate_audit_trail_pdf(poa_id)
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=audit_trail_poa_{poa_id}.pdf"}
        )
    
    else:
        raise HTTPException(status_code=400, detail="Format must be 'json' or 'pdf'")


@router.post("/audit/verify/{log_id}")
def verify_audit_log(log_id: int, db: Session = Depends(get_db)):
    """Verify audit log signature"""
    logger = FiduciaryLogger(db)
    verified = logger.verify_log_signature(log_id)
    
    return {
        "log_id": log_id,
        "signature_verified": verified,
        "message": "Signature valid" if verified else "Signature invalid or log not found"
    }


# ============================================================================
# CREDENTIAL PRESENTATION ENDPOINTS
# ============================================================================

@router.get("/credentials/pdf/{poa_id}")
def generate_poa_certificate(poa_id: int, db: Session = Depends(get_db)):
    """Generate PDF certificate for POA"""
    exporter = LegalExporter(db)
    
    try:
        pdf_data = exporter.generate_poa_certificate_pdf(poa_id)
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=poa_certificate_{poa_id}.pdf"}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/credentials/present")
def present_credentials(poa_id: int, presented_to: str, method: str = "PDF", db: Session = Depends(get_db)):
    """Record credential presentation"""
    presenter = CredentialPresenter(db)
    presentation = presenter.record_presentation(poa_id, presented_to, method)
    
    return {
        "success": True,
        "presentation_id": presentation.id,
        "verification_code": presentation.verification_code,
        "presented_to": presented_to,
        "presented_at": presentation.presented_at.isoformat(),
        "message": f"Credentials presented to {presented_to}"
    }


# ============================================================================
# MODULE SUMMARY
# ============================================================================

@router.get("/summary")
def get_proxy_summary():
    """Get Module C summary and capabilities"""
    return {
        "module": "The Proxy (Module C)",
        "status": "operational",
        "description": "Digital POA Vault with granular permissions and break-glass protocol",
        "capabilities": {
            "smart_poa": {
                "available": True,
                "features": [
                    "Granular permission scopes (utilities, banking, healthcare, subscriptions)",
                    "Time-limited credentials",
                    "Spend limits per POA",
                    "Service-specific restrictions",
                    "Instant revocation"
                ]
            },
            "token_gatekeeper": {
                "available": True,
                "features": [
                    "Fernet encrypted token storage",
                    "Scope validation",
                    "Spend limit enforcement",
                    "Automatic blocking of unauthorized requests"
                ]
            },
            "break_glass_protocol": {
                "available": True,
                "features": [
                    "Automatic trigger on limit violations",
                    "2FA verification (TOTP)",
                    "Liveness detection (face/voice)",
                    "Multi-channel notifications (push, SMS, email)",
                    "Time-limited approval windows"
                ]
            },
            "audit_trail": {
                "available": True,
                "features": [
                    "Cryptographically signed logs (HMAC-SHA256)",
                    "Immutable fiduciary proof",
                    "PDF export for legal authorities",
                    "Signature verification",
                    "Complete action history"
                ]
            },
            "credentials": {
                "available": True,
                "features": [
                    "PDF certificate generation",
                    "QR code verification",
                    "Presentation tracking",
                    "Legal-grade documentation"
                ]
            }
        },
        "security_features": {
            "encryption": "Fernet (symmetric)",
            "signatures": "HMAC-SHA256",
            "2fa": "TOTP (Time-based OTP)",
            "liveness": "Face/Voice verification",
            "notifications": "Push, SMS, Email"
        }
    }
