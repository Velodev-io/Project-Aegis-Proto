"""
Virtual Card Manager for Project Aegis
=======================================

This module integrates with card issuing APIs (Lithic/Stripe Issuing) to provide
real-time transaction authorization control. When a senior attempts a purchase,
the card network sends an authorization request to this system, which uses the
Sentinel AI to approve or decline in real-time.

Architecture:
1. Senior has a virtual card (Apple Pay/Google Pay)
2. When they tap to pay, Visa/Mastercard sends auth request to our webhook
3. Our AI analyzes the transaction in <100ms
4. We respond APPROVE or DECLINE
5. The transaction completes or fails at the register

This gives 100% control without needing phone permissions.
"""

import os
import hmac
import hashlib
import json
from datetime import datetime
from typing import Dict, Optional
from enum import Enum

# For production, use actual Lithic SDK
# pip install lithic
try:
    import lithic
    LITHIC_AVAILABLE = True
except ImportError:
    LITHIC_AVAILABLE = False
    print("⚠️  Lithic SDK not installed. Run: pip install lithic")


class AuthDecision(Enum):
    """Authorization decision for card transactions"""
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"
    PENDING_ADVOCATE = "PENDING_ADVOCATE"  # Hold for advocate approval


class VirtualCardManager:
    """
    Manages virtual card issuance and real-time transaction authorization.
    
    Integration Options:
    1. Lithic (lithic.com) - Best for startups, $0.50/card/month
    2. Stripe Issuing - Good if already using Stripe
    3. Marqeta - Enterprise-grade
    """
    
    def __init__(self, api_key: str = None, provider: str = "lithic", environment: str = "sandbox"):
        """
        Initialize the Virtual Card Manager
        
        Args:
            api_key: API key for the card issuing provider
            provider: "lithic", "stripe", or "marqeta"
            environment: "sandbox" or "production"
        """
        self.provider = provider
        self.environment = environment
        self.api_key = api_key or os.getenv("LITHIC_API_KEY")
        
        if provider == "lithic" and LITHIC_AVAILABLE and self.api_key:
            # Use sandbox base URL for sandbox keys
            if environment == "sandbox":
                self.client = lithic.Lithic(
                    api_key=self.api_key,
                    base_url="https://sandbox.lithic.com/v1"
                )
                print(f"✅ Lithic client initialized (SANDBOX mode)")
            else:
                self.client = lithic.Lithic(api_key=self.api_key)
                print(f"✅ Lithic client initialized (PRODUCTION mode)")
        else:
            self.client = None
            print(f"⚠️  Running in MOCK mode - {provider} client not initialized")
    
    # ========================================================================
    # CARD ISSUANCE
    # ========================================================================
    
    def create_card_for_senior(
        self, 
        senior_id: str, 
        senior_name: str,
        spending_limit_monthly: float = 2000.00,
        spending_limit_daily: float = 500.00
    ) -> Dict:
        """
        Issue a new virtual card for a senior
        
        Args:
            senior_id: Unique identifier for the senior
            senior_name: Senior's full name for the card
            spending_limit_monthly: Monthly spending cap
            spending_limit_daily: Daily spending cap
            
        Returns:
            Card details including card number, CVV, expiry (encrypted in production)
        """
        
        if self.client and self.provider == "lithic":
            # Real Lithic API call
            try:
                card = self.client.cards.create(
                    type="VIRTUAL",
                    memo=f"Aegis Protection Card - {senior_name}",
                    spend_limit=int(spending_limit_monthly * 100),  # Cents
                    spend_limit_duration="MONTHLY",
                    state="OPEN"
                )
                
                return {
                    "card_id": card.token,
                    "last_four": card.last_four,
                    "exp_month": card.exp_month,
                    "exp_year": card.exp_year,
                    "status": "ACTIVE",
                    "spending_limits": {
                        "monthly": spending_limit_monthly,
                        "daily": spending_limit_daily
                    },
                    "senior_id": senior_id,
                    "created_at": datetime.utcnow().isoformat()
                }
            except Exception as e:
                print(f"Error creating card: {e}")
                return self._create_mock_card(senior_id, senior_name, spending_limit_monthly)
        else:
            # Mock card for development
            return self._create_mock_card(senior_id, senior_name, spending_limit_monthly)
    
    def _create_mock_card(self, senior_id: str, senior_name: str, limit: float) -> Dict:
        """Create a mock card for development/testing"""
        import random
        
        return {
            "card_id": f"card_mock_{senior_id}_{random.randint(1000, 9999)}",
            "last_four": f"{random.randint(1000, 9999)}",
            "exp_month": "12",
            "exp_year": "2028",
            "status": "ACTIVE",
            "spending_limits": {
                "monthly": limit,
                "daily": limit / 30
            },
            "senior_id": senior_id,
            "created_at": datetime.utcnow().isoformat(),
            "mock": True
        }
    
    def add_to_apple_pay(self, card_id: str) -> Dict:
        """
        Generate provisioning data for Apple Pay
        
        In production, this returns encrypted card data that can be
        added to Apple Wallet via the Wallet API
        """
        if self.client and self.provider == "lithic":
            try:
                # Lithic provides Apple Pay provisioning
                provisioning = self.client.cards.provision(
                    card_token=card_id,
                    digital_wallet="APPLE_PAY"
                )
                return {
                    "status": "success",
                    "provisioning_data": provisioning.provisioning_payload
                }
            except Exception as e:
                print(f"Error provisioning Apple Pay: {e}")
        
        return {
            "status": "mock",
            "message": "In production, this would return Apple Pay provisioning data",
            "instructions": "Senior would scan QR code or receive push notification to add card to Apple Wallet"
        }
    
    # ========================================================================
    # REAL-TIME AUTHORIZATION (THE MAGIC HAPPENS HERE)
    # ========================================================================
    
    def authorize_transaction(
        self,
        auth_request: Dict,
        sentinel_analyzer  # Instance of ContextAwareGovernor
    ) -> Dict:
        """
        Real-time authorization decision for a card transaction.
        
        This is called by the card network (Visa/Mastercard) via webhook
        when the senior taps their phone to pay. We have ~100ms to respond.
        
        Args:
            auth_request: Authorization request from card network
            sentinel_analyzer: Instance of ContextAwareGovernor for AI analysis
            
        Returns:
            Authorization decision (APPROVED/DECLINED)
        """
        
        # Extract transaction details from auth request
        # Format varies by provider, this is Lithic's format
        amount = auth_request.get("amount", 0) / 100  # Convert cents to dollars
        merchant = auth_request.get("merchant", {})
        merchant_name = merchant.get("descriptor", "Unknown Merchant")
        merchant_category = merchant.get("mcc", "0000")  # MCC code
        transaction_time = datetime.fromisoformat(
            auth_request.get("created", datetime.utcnow().isoformat())
        )
        
        # Map MCC to category
        category = self._mcc_to_category(merchant_category)
        
        # Get senior ID from card
        card_token = auth_request.get("card_token")
        senior_id = self._get_senior_from_card(card_token)
        
        print(f"\n🔔 AUTHORIZATION REQUEST")
        print(f"   Amount: ${amount}")
        print(f"   Merchant: {merchant_name}")
        print(f"   Category: {category}")
        print(f"   Time: {transaction_time.strftime('%I:%M %p')}")
        print(f"   Senior: {senior_id}")
        
        # Run Sentinel AI analysis
        analysis = sentinel_analyzer.analyze_transaction(
            amount=amount,
            transaction_time=transaction_time,
            category=category,
            merchant=merchant_name,
            user_id=senior_id
        )
        
        risk_score = analysis["risk_score"]
        risk_level = analysis["risk_level"]
        flags = analysis["flags"]
        
        print(f"\n🤖 SENTINEL AI ANALYSIS")
        print(f"   Risk Score: {risk_score}/100")
        print(f"   Risk Level: {risk_level}")
        print(f"   Flags: {', '.join(flags) if flags else 'None'}")
        
        # Decision logic
        decision = self._make_decision(analysis)
        
        print(f"\n⚖️  DECISION: {decision.value}")
        
        # Format response for card network
        if decision == AuthDecision.APPROVED:
            return {
                "result": "APPROVED",
                "amount": int(amount * 100),  # Back to cents
                "metadata": {
                    "risk_score": risk_score,
                    "sentinel_approved": True
                }
            }
        elif decision == AuthDecision.DECLINED:
            return {
                "result": "DECLINED",
                "amount": int(amount * 100),
                "metadata": {
                    "risk_score": risk_score,
                    "decline_reason": analysis["reasoning"],
                    "sentinel_blocked": True
                }
            }
        else:  # PENDING_ADVOCATE
            # In production, you'd hold the auth and notify advocate
            # For now, we decline and create a pending approval
            return {
                "result": "DECLINED",
                "amount": int(amount * 100),
                "metadata": {
                    "risk_score": risk_score,
                    "pending_advocate_approval": True,
                    "reasoning": "High-risk transaction requires Trusted Advocate approval"
                }
            }
    
    def _make_decision(self, analysis: Dict) -> AuthDecision:
        """
        Convert Sentinel analysis to authorization decision
        
        Decision Matrix:
        - Risk Score 0-30: AUTO APPROVE
        - Risk Score 31-69: AUTO APPROVE (with monitoring)
        - Risk Score 70-89: PENDING ADVOCATE (decline, notify advocate)
        - Risk Score 90-100: AUTO DECLINE (critical risk)
        """
        risk_score = analysis["risk_score"]
        risk_level = analysis["risk_level"]
        
        if risk_score >= 90 or risk_level == "CRITICAL":
            # Immediate threat - auto decline
            return AuthDecision.DECLINED
        elif risk_score >= 70 or risk_level == "HIGH":
            # Needs advocate review - decline and notify
            return AuthDecision.PENDING_ADVOCATE
        else:
            # Low/Medium risk - approve
            return AuthDecision.APPROVED
    
    def _mcc_to_category(self, mcc: str) -> str:
        """
        Convert Merchant Category Code to human-readable category
        
        Common MCCs:
        - 5732: Electronics
        - 5411: Grocery Stores
        - 5812: Restaurants
        - 4829: Wire Transfer
        - 5999: Miscellaneous
        """
        mcc_map = {
            "5732": "Electronics",
            "5734": "Electronics",
            "5411": "Groceries",
            "5422": "Groceries",
            "5812": "Restaurants",
            "5814": "Restaurants",
            "4829": "Wire Transfer",
            "6051": "Cryptocurrency",
            "5945": "Gift Cards",
            "5999": "Miscellaneous"
        }
        return mcc_map.get(mcc, "Other")
    
    def _get_senior_from_card(self, card_token: str) -> str:
        """
        Map card token to senior ID
        In production, this would query your database
        """
        # Mock implementation
        return "senior_001"
    
    # ========================================================================
    # WEBHOOK SIGNATURE VERIFICATION
    # ========================================================================
    
    def verify_webhook_signature(
        self, 
        payload: bytes, 
        signature: str, 
        webhook_secret: str
    ) -> bool:
        """
        Verify that webhook request is actually from the card network
        
        This prevents attackers from sending fake authorization requests
        """
        expected_signature = hmac.new(
            webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    # ========================================================================
    # CARD MANAGEMENT
    # ========================================================================
    
    def freeze_card(self, card_id: str, reason: str = "Security hold") -> Dict:
        """Immediately freeze a card (e.g., if scam detected)"""
        if self.client and self.provider == "lithic":
            try:
                self.client.cards.update(card_id, state="PAUSED")
                return {"status": "frozen", "reason": reason}
            except Exception as e:
                print(f"Error freezing card: {e}")
        
        return {"status": "mock_frozen", "reason": reason}
    
    def unfreeze_card(self, card_id: str) -> Dict:
        """Unfreeze a card"""
        if self.client and self.provider == "lithic":
            try:
                self.client.cards.update(card_id, state="OPEN")
                return {"status": "active"}
            except Exception as e:
                print(f"Error unfreezing card: {e}")
        
        return {"status": "mock_active"}
    
    def update_spending_limits(
        self, 
        card_id: str, 
        daily_limit: float = None,
        monthly_limit: float = None
    ) -> Dict:
        """Update spending limits on the fly"""
        if self.client and self.provider == "lithic":
            try:
                if monthly_limit:
                    self.client.cards.update(
                        card_id,
                        spend_limit=int(monthly_limit * 100),
                        spend_limit_duration="MONTHLY"
                    )
                return {"status": "updated", "limits": {"daily": daily_limit, "monthly": monthly_limit}}
            except Exception as e:
                print(f"Error updating limits: {e}")
        
        return {"status": "mock_updated", "limits": {"daily": daily_limit, "monthly": monthly_limit}}


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Initialize manager
    manager = VirtualCardManager(provider="lithic")
    
    # 1. Issue a card for a senior
    print("=" * 60)
    print("STEP 1: Issue Virtual Card")
    print("=" * 60)
    
    card = manager.create_card_for_senior(
        senior_id="senior_001",
        senior_name="Robert Johnson",
        spending_limit_monthly=2000.00,
        spending_limit_daily=200.00
    )
    print(json.dumps(card, indent=2))
    
    # 2. Add to Apple Pay
    print("\n" + "=" * 60)
    print("STEP 2: Add to Apple Pay")
    print("=" * 60)
    
    apple_pay = manager.add_to_apple_pay(card["card_id"])
    print(json.dumps(apple_pay, indent=2))
    
    # 3. Simulate authorization request
    print("\n" + "=" * 60)
    print("STEP 3: Real-Time Authorization")
    print("=" * 60)
    
    # Import Sentinel analyzer
    from transaction_governor import ContextAwareGovernor
    sentinel = ContextAwareGovernor()
    
    # Mock authorization request (what card network sends)
    auth_request = {
        "card_token": card["card_id"],
        "amount": 129999,  # $1,299.99 in cents
        "merchant": {
            "descriptor": "BEST BUY",
            "mcc": "5732"  # Electronics
        },
        "created": datetime.now().replace(hour=2, minute=0).isoformat()  # 2 AM
    }
    
    # Process authorization
    decision = manager.authorize_transaction(auth_request, sentinel)
    print(f"\nFinal Response to Card Network:")
    print(json.dumps(decision, indent=2))
