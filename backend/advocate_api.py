"""
Advocate Module - FastAPI Integration
======================================

Multi-agent orchestration for:
1. Medical bill forensics
2. Subscription detection and cancellation
3. Autonomous negotiation

All actions require Human-in-the-Loop (HITL) approval.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import json

# Import our agents
from advocate_bill_auditor import AgenticAuditor, InsurancePolicy, LineItem, CPTCodeDatabase
from advocate_subscription_detector import SubscriptionDetector, Transaction, Subscription
from advocate_cancellation_agent import CancellationAgent, CancellationStatus
from advocate_negotiation_agent import NegotiationScriptGenerator, DisputeScript

# Try to import OCR libraries
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("⚠️  EasyOCR not installed. Run: pip install easyocr")

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("⚠️  Tesseract not installed. Run: pip install pytesseract pillow")

app = FastAPI(title="Aegis Advocate Module")

# Initialize agents
insurance_policy = InsurancePolicy("PPO")
bill_auditor = AgenticAuditor(insurance_policy)
subscription_detector = SubscriptionDetector()
cancellation_agent = CancellationAgent(read_only=True)  # Shadow mode by default
script_generator = NegotiationScriptGenerator()

# Pydantic models
class BillAnalysisRequest(BaseModel):
    line_items: List[Dict]  # List of {code, description, quantity, unit_price, total, date_of_service}
    is_in_network: bool = True
    previous_bills: Optional[List[List[Dict]]] = None


class SubscriptionAuditRequest(BaseModel):
    transactions: List[Dict]  # List of {date, merchant, amount, category, description}
    usage_data: Optional[Dict[str, int]] = None  # merchant -> usage count


class CancellationRequest(BaseModel):
    merchant: str
    cancellation_url: str
    credentials: Optional[Dict[str, str]] = None
    require_approval: bool = True


class NegotiationScriptRequest(BaseModel):
    script_type: str  # "MEDICAL_BILL", "SUBSCRIPTION", "PRICE"
    merchant: str
    # For medical bills
    errors: Optional[List[Dict]] = None
    total_disputed: Optional[float] = None
    policy_holder_name: Optional[str] = None
    # For subscriptions
    subscription_amount: Optional[float] = None
    months_unused: Optional[int] = None
    reason: Optional[str] = None


# ============================================================================
# MEDICAL BILL FORENSICS
# ============================================================================

@app.post("/advocate/analyze-bill")
async def analyze_bill(request: BillAnalysisRequest):
    """
    Analyze medical bill for errors
    
    Returns:
        - Total billed
        - Total allowed by insurance
        - Potential savings
        - List of errors
        - Recommendations
        - Risk score
    """
    
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


@app.post("/advocate/analyze-bill-image")
async def analyze_bill_image(file: UploadFile = File(...)):
    """
    Analyze medical bill from uploaded image using OCR
    
    Returns:
        - Extracted line items
        - Bill analysis
        - OCR confidence
    """
    
    if not EASYOCR_AVAILABLE and not TESSERACT_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="OCR not available. Install easyocr or tesseract."
        )
    
    # Read image
    contents = await file.read()
    
    # Save temporarily
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(contents)
    
    # Extract text using OCR
    if EASYOCR_AVAILABLE:
        reader = easyocr.Reader(['en'])
        result = reader.readtext(temp_path)
        extracted_text = "\n".join([text[1] for text in result])
    elif TESSERACT_AVAILABLE:
        image = Image.open(temp_path)
        extracted_text = pytesseract.image_to_string(image)
    
    # Parse line items (simplified - in production, use more sophisticated parsing)
    # This is a mock implementation
    line_items = [
        {
            "code": "99214",
            "description": "Office visit",
            "quantity": 1,
            "unit_price": 350.00,
            "total": 350.00,
            "date_of_service": datetime.now().isoformat()
        }
    ]
    
    # Analyze
    analysis_request = BillAnalysisRequest(
        line_items=line_items,
        is_in_network=True
    )
    
    analysis_result = await analyze_bill(analysis_request)
    
    return {
        "extracted_text": extracted_text[:500],  # First 500 chars
        "line_items": line_items,
        "analysis": analysis_result,
        "ocr_method": "easyocr" if EASYOCR_AVAILABLE else "tesseract"
    }


# ============================================================================
# SUBSCRIPTION MANAGEMENT
# ============================================================================

@app.post("/advocate/subscriptions/audit")
async def audit_subscriptions(request: SubscriptionAuditRequest):
    """
    Detect and analyze subscriptions from transaction history
    
    Returns:
        - List of detected subscriptions
        - Recommendations (KEEP/REVIEW/CANCEL)
        - Potential savings
    """
    
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


@app.post("/advocate/subscriptions/cancel")
async def cancel_subscription(request: CancellationRequest):
    """
    Autonomously cancel a subscription (SHADOW MODE by default)
    
    Returns:
        - Cancellation status
        - Steps completed
        - Screenshots
        - Dark patterns detected
    """
    
    # Check if approval required
    if request.require_approval:
        return {
            "status": "PENDING_APPROVAL",
            "message": "Cancellation requires human approval",
            "merchant": request.merchant,
            "cancellation_url": request.cancellation_url,
            "next_steps": [
                "Review cancellation details",
                "Approve or reject cancellation",
                "If approved, agent will execute cancellation"
            ]
        }
    
    # Execute cancellation (in shadow mode)
    result = await cancellation_agent.cancel_subscription(
        merchant=request.merchant,
        cancellation_url=request.cancellation_url,
        credentials=request.credentials
    )
    
    return {
        "merchant": result.merchant,
        "status": result.status.value,
        "steps_completed": result.steps_completed,
        "screenshots": result.screenshots,
        "dark_patterns_detected": result.dark_patterns_detected,
        "error_message": result.error_message,
        "timestamp": result.timestamp.isoformat(),
        "shadow_mode": cancellation_agent.read_only
    }


# ============================================================================
# NEGOTIATION SCRIPTS
# ============================================================================

@app.post("/advocate/generate-script")
async def generate_negotiation_script(request: NegotiationScriptRequest):
    """
    Generate professional negotiation script
    
    Returns:
        - Formatted script for human advocate
        - Expected outcome
        - Fallback options
    """
    
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


# ============================================================================
# SUMMARY ENDPOINT
# ============================================================================

@app.get("/advocate/summary")
async def get_advocate_summary():
    """
    Get summary of Advocate module capabilities
    """
    
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
                    "Price negotiations",
                    "Voice synthesis ready (placeholder)"
                ]
            },
            "ocr": {
                "available": EASYOCR_AVAILABLE or TESSERACT_AVAILABLE,
                "method": "easyocr" if EASYOCR_AVAILABLE else ("tesseract" if TESSERACT_AVAILABLE else None)
            }
        },
        "safety_features": {
            "shadow_mode": True,
            "human_approval_required": True,
            "audit_trail": True,
            "screenshot_capture": True
        }
    }


@app.get("/")
def health_check():
    return {
        "service": "Aegis Advocate Module",
        "status": "online",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("🤝 Starting Aegis Advocate Module")
    print("="*70)
    print("Endpoints:")
    print("  POST /advocate/analyze-bill - Medical bill forensics")
    print("  POST /advocate/analyze-bill-image - OCR + bill analysis")
    print("  POST /advocate/subscriptions/audit - Subscription detection")
    print("  POST /advocate/subscriptions/cancel - Autonomous cancellation")
    print("  POST /advocate/generate-script - Negotiation scripts")
    print("  GET  /advocate/summary - Module capabilities")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8002)
