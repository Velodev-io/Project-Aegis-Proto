"""
Advocate Module: Medical Bill Forensics Agent
==============================================

This agent analyzes medical bills for:
- Upcoding (billing higher-level codes than warranted)
- Duplicate charges
- Out-of-network pricing
- Insurance policy violations
"""

import re
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class LineItem:
    """Represents a single line item from a medical bill"""
    code: str  # CPT/HCPCS code
    description: str
    quantity: int
    unit_price: float
    total: float
    date_of_service: Optional[datetime] = None


@dataclass
class BillAnalysis:
    """Results of bill forensics analysis"""
    total_billed: float
    total_allowed: float
    potential_savings: float
    errors: List[Dict]
    recommendations: List[str]
    risk_score: int  # 0-100


class CPTCodeDatabase:
    """
    Mock CPT (Current Procedural Terminology) code database
    In production, this would be a real medical coding database
    """
    
    CODES = {
        # Office Visits
        "99211": {
            "description": "Office visit - minimal",
            "typical_range": (50, 100),
            "level": 1
        },
        "99212": {
            "description": "Office visit - low complexity",
            "typical_range": (75, 150),
            "level": 2
        },
        "99213": {
            "description": "Office visit - moderate complexity",
            "typical_range": (100, 200),
            "level": 3
        },
        "99214": {
            "description": "Office visit - moderate to high complexity",
            "typical_range": (150, 300),
            "level": 4
        },
        "99215": {
            "description": "Office visit - high complexity",
            "typical_range": (200, 400),
            "level": 5
        },
        
        # Common Procedures
        "80053": {
            "description": "Comprehensive metabolic panel",
            "typical_range": (30, 80),
            "level": 1
        },
        "85025": {
            "description": "Complete blood count (CBC)",
            "typical_range": (20, 50),
            "level": 1
        },
        "93000": {
            "description": "Electrocardiogram (EKG)",
            "typical_range": (50, 150),
            "level": 2
        },
        "70450": {
            "description": "CT scan head/brain without contrast",
            "typical_range": (400, 1200),
            "level": 4
        },
        "99283": {
            "description": "Emergency department visit - moderate complexity",
            "typical_range": (300, 600),
            "level": 3
        }
    }
    
    @classmethod
    def get_code_info(cls, code: str) -> Optional[Dict]:
        """Get information about a CPT code"""
        return cls.CODES.get(code)
    
    @classmethod
    def is_valid_code(cls, code: str) -> bool:
        """Check if a CPT code exists"""
        return code in cls.CODES


class InsurancePolicy:
    """
    Mock insurance policy with allowed amounts
    In production, this would integrate with real insurance APIs
    """
    
    def __init__(self, policy_type: str = "PPO"):
        self.policy_type = policy_type
        self.network_discount = 0.30  # 30% discount for in-network
        
        # Allowed amounts for common codes (in-network)
        self.allowed_amounts = {
            "99211": 75,
            "99212": 110,
            "99213": 145,
            "99214": 210,
            "99215": 290,
            "80053": 45,
            "85025": 30,
            "93000": 85,
            "70450": 650,
            "99283": 425
        }
    
    def get_allowed_amount(self, code: str, is_in_network: bool = True) -> Optional[float]:
        """Get the allowed amount for a CPT code"""
        base_amount = self.allowed_amounts.get(code)
        
        if base_amount is None:
            return None
        
        if not is_in_network:
            # Out-of-network typically pays less
            return base_amount * 0.70
        
        return base_amount


class AgenticAuditor:
    """
    AI-powered medical bill auditor
    
    Detects:
    - Upcoding (billing higher complexity than warranted)
    - Duplicate charges
    - Pricing above insurance allowed amounts
    - Unbundling (charging separately for bundled services)
    """
    
    def __init__(self, policy: InsurancePolicy):
        self.policy = policy
        self.cpt_db = CPTCodeDatabase()
    
    def analyze_bill(
        self, 
        line_items: List[LineItem],
        is_in_network: bool = True,
        previous_bills: List[List[LineItem]] = None
    ) -> BillAnalysis:
        """
        Comprehensive bill analysis
        
        Args:
            line_items: List of charges from the bill
            is_in_network: Whether provider is in insurance network
            previous_bills: Historical bills for duplicate detection
            
        Returns:
            BillAnalysis with findings and recommendations
        """
        
        errors = []
        total_billed = sum(item.total for item in line_items)
        total_allowed = 0
        
        # Check each line item
        for item in line_items:
            # 1. Check if code is valid
            if not self.cpt_db.is_valid_code(item.code):
                errors.append({
                    "type": "INVALID_CODE",
                    "severity": "HIGH",
                    "code": item.code,
                    "description": item.description,
                    "message": f"CPT code {item.code} is not recognized",
                    "potential_savings": item.total
                })
                continue
            
            # 2. Check for upcoding
            allowed = self.policy.get_allowed_amount(item.code, is_in_network)
            if allowed:
                total_allowed += allowed * item.quantity
                
                if item.unit_price > allowed * 1.2:  # 20% tolerance
                    code_info = self.cpt_db.get_code_info(item.code)
                    errors.append({
                        "type": "UPCODING",
                        "severity": "HIGH",
                        "code": item.code,
                        "description": item.description,
                        "billed": item.unit_price,
                        "allowed": allowed,
                        "message": f"Billed ${item.unit_price:.2f} but insurance allows ${allowed:.2f}",
                        "potential_savings": (item.unit_price - allowed) * item.quantity
                    })
            
            # 3. Check for excessive quantity
            if item.quantity > 1 and item.code.startswith("99"):  # Office visits
                errors.append({
                    "type": "DUPLICATE_SERVICE",
                    "severity": "MEDIUM",
                    "code": item.code,
                    "description": item.description,
                    "quantity": item.quantity,
                    "message": f"Multiple office visits ({item.quantity}) on same bill - verify if correct",
                    "potential_savings": item.unit_price * (item.quantity - 1)
                })
        
        # 4. Check for duplicates across bills
        if previous_bills:
            duplicates = self._find_duplicates(line_items, previous_bills)
            errors.extend(duplicates)
        
        # 5. Check for unbundling
        unbundling_errors = self._check_unbundling(line_items)
        errors.extend(unbundling_errors)
        
        # Calculate potential savings
        potential_savings = sum(error.get("potential_savings", 0) for error in errors)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(errors, is_in_network)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(errors, total_billed, potential_savings)
        
        return BillAnalysis(
            total_billed=total_billed,
            total_allowed=total_allowed,
            potential_savings=potential_savings,
            errors=errors,
            recommendations=recommendations,
            risk_score=risk_score
        )
    
    def _find_duplicates(
        self, 
        current_items: List[LineItem], 
        previous_bills: List[List[LineItem]]
    ) -> List[Dict]:
        """Find duplicate charges across bills"""
        duplicates = []
        
        for prev_bill in previous_bills:
            for current in current_items:
                for prev in prev_bill:
                    # Same code and similar date
                    if current.code == prev.code:
                        if current.date_of_service and prev.date_of_service:
                            days_apart = abs((current.date_of_service - prev.date_of_service).days)
                            
                            if days_apart <= 7:  # Within a week
                                duplicates.append({
                                    "type": "DUPLICATE_BILLING",
                                    "severity": "CRITICAL",
                                    "code": current.code,
                                    "description": current.description,
                                    "current_date": current.date_of_service.isoformat(),
                                    "previous_date": prev.date_of_service.isoformat(),
                                    "message": f"Same service billed {days_apart} days apart - possible duplicate",
                                    "potential_savings": current.total
                                })
        
        return duplicates
    
    def _check_unbundling(self, line_items: List[LineItem]) -> List[Dict]:
        """
        Check for unbundling (charging separately for bundled services)
        
        Example: Comprehensive metabolic panel (80053) includes multiple tests.
        If those tests are also billed separately, it's unbundling.
        """
        errors = []
        
        # Check if comprehensive panel is present
        has_comprehensive = any(item.code == "80053" for item in line_items)
        
        if has_comprehensive:
            # These should be included in 80053
            bundled_codes = ["82947", "82962", "84132"]  # Example bundled tests
            
            for item in line_items:
                if item.code in bundled_codes:
                    errors.append({
                        "type": "UNBUNDLING",
                        "severity": "HIGH",
                        "code": item.code,
                        "description": item.description,
                        "message": f"Code {item.code} is included in comprehensive panel (80053) - should not be billed separately",
                        "potential_savings": item.total
                    })
        
        return errors
    
    def _generate_recommendations(self, errors: List[Dict], is_in_network: bool) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if not errors:
            recommendations.append("✅ No billing errors detected. Bill appears accurate.")
            return recommendations
        
        # Group by severity
        critical = [e for e in errors if e["severity"] == "CRITICAL"]
        high = [e for e in errors if e["severity"] == "HIGH"]
        medium = [e for e in errors if e["severity"] == "MEDIUM"]
        
        if critical:
            recommendations.append(
                f"🚨 URGENT: {len(critical)} critical error(s) found. "
                "Contact billing department immediately to dispute charges."
            )
        
        if high:
            recommendations.append(
                f"⚠️  {len(high)} high-priority error(s) detected. "
                "Request itemized bill and explanation of benefits (EOB)."
            )
        
        if not is_in_network:
            recommendations.append(
                "💡 Provider is out-of-network. Consider requesting in-network referral "
                "for future visits to reduce costs."
            )
        
        # Specific recommendations by error type
        error_types = set(e["type"] for e in errors)
        
        if "UPCODING" in error_types:
            recommendations.append(
                "📋 Upcoding detected. Request medical records to verify complexity level "
                "of services provided matches billed codes."
            )
        
        if "DUPLICATE_BILLING" in error_types:
            recommendations.append(
                "🔄 Duplicate charges found. Provide dates of service to billing department "
                "and request removal of duplicate entries."
            )
        
        if "UNBUNDLING" in error_types:
            recommendations.append(
                "📦 Unbundling detected. Services should be billed as a package. "
                "Request rebilling with correct bundled codes."
            )
        
        return recommendations
    
    def _calculate_risk_score(
        self, 
        errors: List[Dict], 
        total_billed: float, 
        potential_savings: float
    ) -> int:
        """
        Calculate risk score (0-100)
        
        Higher score = more problematic bill
        """
        if not errors:
            return 0
        
        score = 0
        
        # Base score from error count
        score += min(len(errors) * 10, 40)
        
        # Severity weighting
        for error in errors:
            if error["severity"] == "CRITICAL":
                score += 15
            elif error["severity"] == "HIGH":
                score += 10
            elif error["severity"] == "MEDIUM":
                score += 5
        
        # Percentage of bill that's questionable
        if total_billed > 0:
            error_percentage = (potential_savings / total_billed) * 100
            score += min(int(error_percentage / 2), 30)
        
        return min(score, 100)


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("🏥 MEDICAL BILL FORENSICS AGENT - TEST")
    print("=" * 70)
    
    # Create insurance policy
    policy = InsurancePolicy("PPO")
    auditor = AgenticAuditor(policy)
    
    # Test 1: Upcoding scenario
    print("\n📋 TEST 1: Upcoding Detection")
    print("-" * 70)
    
    bill_items = [
        LineItem(
            code="99214",
            description="Office visit - moderate to high complexity",
            quantity=1,
            unit_price=350.00,  # Overcharged (allowed: $210)
            total=350.00,
            date_of_service=datetime(2026, 1, 15)
        ),
        LineItem(
            code="85025",
            description="Complete blood count",
            quantity=1,
            unit_price=30.00,
            total=30.00,
            date_of_service=datetime(2026, 1, 15)
        )
    ]
    
    analysis = auditor.analyze_bill(bill_items, is_in_network=True)
    
    print(f"Total Billed: ${analysis.total_billed:.2f}")
    print(f"Total Allowed: ${analysis.total_allowed:.2f}")
    print(f"Potential Savings: ${analysis.potential_savings:.2f}")
    print(f"Risk Score: {analysis.risk_score}/100")
    print(f"\nErrors Found: {len(analysis.errors)}")
    for error in analysis.errors:
        print(f"  - {error['type']}: {error['message']}")
    
    print(f"\nRecommendations:")
    for rec in analysis.recommendations:
        print(f"  {rec}")
    
    # Test 2: Duplicate billing
    print("\n\n📋 TEST 2: Duplicate Billing Detection")
    print("-" * 70)
    
    current_bill = [
        LineItem(
            code="99213",
            description="Office visit",
            quantity=1,
            unit_price=145.00,
            total=145.00,
            date_of_service=datetime(2026, 1, 20)
        )
    ]
    
    previous_bill = [
        LineItem(
            code="99213",
            description="Office visit",
            quantity=1,
            unit_price=145.00,
            total=145.00,
            date_of_service=datetime(2026, 1, 18)  # 2 days earlier
        )
    ]
    
    analysis2 = auditor.analyze_bill(current_bill, previous_bills=[previous_bill])
    
    print(f"Risk Score: {analysis2.risk_score}/100")
    print(f"Errors Found: {len(analysis2.errors)}")
    for error in analysis2.errors:
        print(f"  - {error['type']}: {error['message']}")
    
    print("\n✅ Medical Bill Forensics Agent tests complete!")
