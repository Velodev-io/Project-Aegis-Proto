"""
Virtual Card Authorization Webhook
===================================

This FastAPI endpoint receives real-time authorization requests from the
card network (Lithic/Stripe) when a senior taps their phone to pay.

Flow:
1. Senior taps phone at register
2. Visa/Mastercard sends POST to /webhook/card-auth
3. We analyze with Sentinel AI (<100ms)
4. We respond APPROVED or DECLINED
5. Transaction completes or fails

This is the CORE of the virtual card approach.
"""

from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
import hmac
import hashlib
from datetime import datetime

from virtual_card_manager import VirtualCardManager, AuthDecision
from transaction_governor import ContextAwareGovernor
from models import Base, SecurityLog, PendingApproval
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Initialize components
card_manager = VirtualCardManager(provider="lithic")
sentinel_governor = ContextAwareGovernor()

# Database setup
SENTINEL_DB_URL = "sqlite:///./data/aegis_trust_vault.db"
engine = create_engine(
    SENTINEL_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=None
)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="Aegis Virtual Card Authorization Service")


# ============================================================================
# WEBHOOK ENDPOINTS
# ============================================================================

@app.post("/webhook/card-auth")
async def card_authorization_webhook(
    request: Request,
    x_lithic_signature: Optional[str] = Header(None)
):
    """
    Real-time card authorization webhook
    
    Called by Lithic/Stripe when senior attempts a purchase.
    We have ~100ms to respond with APPROVED or DECLINED.
    
    Request Format (Lithic):
    {
        "token": "auth_abc123",
        "card_token": "card_xyz789",
        "amount": 129999,  // cents
        "merchant": {
            "descriptor": "BEST BUY",
            "mcc": "5732",
            "city": "San Francisco",
            "state": "CA"
        },
        "created": "2024-01-15T14:30:00Z"
    }
    
    Response Format:
    {
        "result": "APPROVED" | "DECLINED",
        "amount": 129999
    }
    """
    
    # Get raw body for signature verification
    body = await request.body()
    
    # Verify webhook signature (security)
    webhook_secret = "your_webhook_secret_here"  # From Lithic dashboard
    if x_lithic_signature:
        is_valid = card_manager.verify_webhook_signature(
            body, 
            x_lithic_signature, 
            webhook_secret
        )
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse request
    auth_request = await request.json()
    
    # Log the authorization attempt
    print(f"\n{'='*60}")
    print(f"🔔 CARD AUTHORIZATION REQUEST")
    print(f"{'='*60}")
    print(f"Card: {auth_request.get('card_token', 'unknown')}")
    print(f"Amount: ${auth_request.get('amount', 0) / 100:.2f}")
    print(f"Merchant: {auth_request.get('merchant', {}).get('descriptor', 'Unknown')}")
    
    # Process with Sentinel AI
    decision = card_manager.authorize_transaction(auth_request, sentinel_governor)
    
    # Log to database
    db = SessionLocal()
    try:
        amount = auth_request.get("amount", 0) / 100
        merchant = auth_request.get("merchant", {})
        
        security_log = SecurityLog(
            event_type="CARD_AUTHORIZATION",
            transaction_amount=amount,
            transaction_time=datetime.utcnow(),
            transaction_category=card_manager._mcc_to_category(merchant.get("mcc", "0000")),
            merchant=merchant.get("descriptor", "Unknown"),
            risk_level=decision.get("metadata", {}).get("risk_score", 0),
            approval_status=decision["result"],
            reasoning=decision.get("metadata", {}).get("decline_reason", "Approved by Sentinel"),
            user_id=card_manager._get_senior_from_card(auth_request.get("card_token")),
            event_metadata={
                "auth_token": auth_request.get("token"),
                "card_token": auth_request.get("card_token"),
                "merchant_mcc": merchant.get("mcc"),
                "merchant_city": merchant.get("city"),
                "merchant_state": merchant.get("state")
            }
        )
        
        db.add(security_log)
        db.commit()
        
        print(f"\n✅ Logged to database (ID: {security_log.id})")
        
    except Exception as e:
        print(f"Error logging to database: {e}")
    finally:
        db.close()
    
    # Return decision to card network
    print(f"\n⚖️  RESPONSE: {decision['result']}")
    print(f"{'='*60}\n")
    
    return decision


@app.post("/webhook/card-created")
async def card_created_webhook(request: Request):
    """
    Webhook called when a new card is created
    Used to track card lifecycle
    """
    data = await request.json()
    print(f"✅ New card created: {data.get('token')}")
    return {"status": "received"}


@app.post("/webhook/card-transaction-updated")
async def transaction_updated_webhook(request: Request):
    """
    Webhook called when transaction status changes
    (e.g., from PENDING to SETTLED)
    """
    data = await request.json()
    print(f"📊 Transaction updated: {data.get('token')} -> {data.get('status')}")
    return {"status": "received"}


# ============================================================================
# CARD MANAGEMENT ENDPOINTS (For your app)
# ============================================================================

class CreateCardRequest(BaseModel):
    senior_id: str
    senior_name: str
    monthly_limit: float = 2000.00
    daily_limit: float = 200.00


class UpdateLimitsRequest(BaseModel):
    card_id: str
    monthly_limit: Optional[float] = None
    daily_limit: Optional[float] = None


@app.post("/cards/create")
async def create_card(request: CreateCardRequest):
    """
    Create a new virtual card for a senior
    Called from your caregiver dashboard
    """
    card = card_manager.create_card_for_senior(
        senior_id=request.senior_id,
        senior_name=request.senior_name,
        spending_limit_monthly=request.monthly_limit,
        spending_limit_daily=request.daily_limit
    )
    return card


@app.post("/cards/freeze")
async def freeze_card(card_id: str, reason: str = "Security hold"):
    """
    Immediately freeze a card
    Called when scam is detected or caregiver requests
    """
    result = card_manager.freeze_card(card_id, reason)
    return result


@app.post("/cards/unfreeze")
async def unfreeze_card(card_id: str):
    """Unfreeze a card"""
    result = card_manager.unfreeze_card(card_id)
    return result


@app.post("/cards/update-limits")
async def update_limits(request: UpdateLimitsRequest):
    """Update spending limits on the fly"""
    result = card_manager.update_spending_limits(
        card_id=request.card_id,
        daily_limit=request.daily_limit,
        monthly_limit=request.monthly_limit
    )
    return result


@app.post("/cards/add-to-apple-pay")
async def add_to_apple_pay(card_id: str):
    """Generate Apple Pay provisioning data"""
    result = card_manager.add_to_apple_pay(card_id)
    return result


@app.get("/")
def health_check():
    return {
        "service": "Aegis Virtual Card Authorization",
        "status": "online",
        "provider": card_manager.provider,
        "sentinel_enabled": True
    }


# ============================================================================
# TESTING ENDPOINT (Remove in production)
# ============================================================================

@app.post("/test/simulate-purchase")
async def simulate_purchase(
    amount: float,
    merchant_name: str,
    merchant_category: str = "Electronics",
    hour: int = 14  # 2 PM by default
):
    """
    Simulate a card purchase for testing
    This mimics what the card network would send
    """
    
    # Map category to MCC
    category_to_mcc = {
        "Electronics": "5732",
        "Groceries": "5411",
        "Restaurants": "5812",
        "Wire Transfer": "4829",
        "Gift Cards": "5945"
    }
    
    mock_auth_request = {
        "token": f"auth_test_{datetime.now().timestamp()}",
        "card_token": "card_mock_senior_001_1234",
        "amount": int(amount * 100),  # Convert to cents
        "merchant": {
            "descriptor": merchant_name.upper(),
            "mcc": category_to_mcc.get(merchant_category, "5999"),
            "city": "San Francisco",
            "state": "CA"
        },
        "created": datetime.now().replace(hour=hour).isoformat()
    }
    
    # Process as if it came from card network
    decision = card_manager.authorize_transaction(mock_auth_request, sentinel_governor)
    
    return {
        "simulation": True,
        "request": mock_auth_request,
        "decision": decision,
        "explanation": "This simulates what would happen if the senior tapped their phone to pay"
    }


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Starting Aegis Virtual Card Authorization Service")
    print("="*60)
    print("Webhook URL: http://localhost:8001/webhook/card-auth")
    print("Test endpoint: http://localhost:8001/test/simulate-purchase")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
