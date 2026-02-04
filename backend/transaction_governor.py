"""
Context-Aware Transaction Governor for Project Aegis
Intelligent spending governance with risk assessment
"""
from typing import Dict
from datetime import datetime, time


class ContextAwareGovernor:
    """
    AI-powered transaction monitoring and governance
    Analyzes spending patterns and flags suspicious activity
    """
    
    # Risk thresholds
    HIGH_AMOUNT_THRESHOLD = 200.0
    ODD_HOURS_START = time(23, 0)  # 11 PM
    ODD_HOURS_END = time(5, 0)     # 5 AM
    
    # High-risk categories
    HIGH_RISK_CATEGORIES = {
        "electronics",
        "wire_transfer",
        "cryptocurrency",
        "gift_cards",
        "cash_advance",
        "gambling",
        "international_transfer"
    }
    
    # Medium-risk categories
    MEDIUM_RISK_CATEGORIES = {
        "jewelry",
        "luxury_goods",
        "travel",
        "online_shopping"
    }
    
    def __init__(self):
        """Initialize the transaction governor"""
        pass
    
    def analyze_transaction(
        self,
        amount: float,
        transaction_time: datetime,
        category: str,
        merchant: str,
        user_id: str = None
    ) -> Dict:
        """
        Analyze a transaction for suspicious patterns
        
        Args:
            amount: Transaction amount in dollars
            transaction_time: When the transaction occurred
            category: Transaction category
            merchant: Merchant name
            user_id: Optional user identifier
            
        Returns:
            Dict with risk_level, status, reasoning, and flags
        """
        flags = []
        risk_score = 0
        
        # Check amount
        is_high_amount = amount > self.HIGH_AMOUNT_THRESHOLD
        if is_high_amount:
            flags.append("HIGH_AMOUNT")
            risk_score += 30
        
        # Check time
        is_odd_time = self._is_odd_hours(transaction_time)
        if is_odd_time:
            flags.append("ODD_HOURS")
            risk_score += 25
        
        # Check category
        category_lower = category.lower().replace(" ", "_")
        is_high_risk_category = category_lower in self.HIGH_RISK_CATEGORIES
        is_medium_risk_category = category_lower in self.MEDIUM_RISK_CATEGORIES
        
        if is_high_risk_category:
            flags.append("HIGH_RISK_CATEGORY")
            risk_score += 35
        elif is_medium_risk_category:
            flags.append("MEDIUM_RISK_CATEGORY")
            risk_score += 15
        
        # Additional risk factors
        if amount > 1000:
            flags.append("VERY_HIGH_AMOUNT")
            risk_score += 20
        
        if "atm" in merchant.lower() and is_odd_time:
            flags.append("ODD_HOURS_ATM")
            risk_score += 15
        
        # Determine risk level and status
        risk_level, status, reasoning = self._determine_risk_and_status(
            risk_score, flags, amount, category, transaction_time
        )
        
        return {
            "risk_level": risk_level,
            "risk_score": min(100, risk_score),
            "status": status,
            "flags": flags,
            "reasoning": reasoning,
            "requires_approval": status == "PENDING_APPROVAL",
            "timestamp": datetime.utcnow().isoformat(),
            "transaction_details": {
                "amount": amount,
                "time": transaction_time.isoformat(),
                "category": category,
                "merchant": merchant
            }
        }
    
    def _is_odd_hours(self, transaction_time: datetime) -> bool:
        """
        Check if transaction occurred during odd hours (11 PM - 5 AM)
        
        Args:
            transaction_time: Transaction timestamp
            
        Returns:
            True if during odd hours
        """
        t = transaction_time.time()
        
        # Handle time range that crosses midnight
        if self.ODD_HOURS_START > self.ODD_HOURS_END:
            return t >= self.ODD_HOURS_START or t <= self.ODD_HOURS_END
        else:
            return self.ODD_HOURS_START <= t <= self.ODD_HOURS_END
    
    def _determine_risk_and_status(
        self,
        risk_score: int,
        flags: list,
        amount: float,
        category: str,
        transaction_time: datetime
    ) -> tuple:
        """
        Determine risk level and approval status
        
        Returns:
            Tuple of (risk_level, status, reasoning)
        """
        # Critical risk: High amount + Odd time + High risk category
        if (
            "HIGH_AMOUNT" in flags and
            "ODD_HOURS" in flags and
            "HIGH_RISK_CATEGORY" in flags
        ):
            risk_level = "CRITICAL"
            status = "PENDING_APPROVAL"
            reasoning = (
                f"CRITICAL RISK TRANSACTION: ${amount:.2f} {category} purchase at "
                f"{transaction_time.strftime('%I:%M %p')} (odd hours). "
                f"This combination of high amount, unusual time, and high-risk category "
                f"requires immediate Trusted Advocate approval."
            )
        elif risk_score >= 70:
            risk_level = "HIGH"
            status = "PENDING_APPROVAL"
            reasoning = (
                f"HIGH RISK TRANSACTION (Score: {risk_score}/100): "
                f"${amount:.2f} {category} purchase. "
                f"Flags: {', '.join(flags)}. Requires approval."
            )
        elif risk_score >= 40:
            risk_level = "MEDIUM"
            status = "PENDING_APPROVAL"
            reasoning = (
                f"MEDIUM RISK TRANSACTION (Score: {risk_score}/100): "
                f"${amount:.2f} {category} purchase. "
                f"Flags: {', '.join(flags)}. Recommended for review."
            )
        else:
            risk_level = "LOW"
            status = "APPROVED"
            reasoning = (
                f"LOW RISK TRANSACTION (Score: {risk_score}/100): "
                f"${amount:.2f} {category} purchase appears normal."
            )
        
        return risk_level, status, reasoning
