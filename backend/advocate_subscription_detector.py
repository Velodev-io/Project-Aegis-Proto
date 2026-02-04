"""
Advocate Module: Subscription Purge Agent
==========================================

This agent:
1. Detects recurring subscriptions from bank transactions
2. Identifies unused/wasteful subscriptions
3. Autonomously cancels subscriptions (with HITL approval)
"""

import re
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dataclasses import dataclass


@dataclass
class Transaction:
    """Bank transaction"""
    date: datetime
    merchant: str
    amount: float
    category: str
    description: str


@dataclass
class Subscription:
    """Detected subscription"""
    merchant: str
    frequency: str  # "MONTHLY", "ANNUAL", "WEEKLY"
    average_amount: float
    last_charge: datetime
    total_charges: int
    total_spent: float
    confidence: float  # 0-1
    usage_score: float  # 0-1 (1 = high usage, 0 = no usage)
    recommendation: str  # "KEEP", "REVIEW", "CANCEL"
    reasoning: str


class SubscriptionDetector:
    """
    AI-powered subscription detector
    
    Uses pattern matching and ML-like heuristics to identify
    recurring charges from transaction data
    """
    
    # Known subscription merchants
    KNOWN_SUBSCRIPTIONS = {
        "netflix": {"category": "streaming", "typical_amount": 15.99},
        "spotify": {"category": "music", "typical_amount": 10.99},
        "amazon prime": {"category": "shopping", "typical_amount": 14.99},
        "planet fitness": {"category": "gym", "typical_amount": 10.00},
        "la fitness": {"category": "gym", "typical_amount": 29.99},
        "apple.com/bill": {"category": "tech", "typical_amount": 0.99},
        "google storage": {"category": "tech", "typical_amount": 1.99},
        "nyt": {"category": "news", "typical_amount": 17.00},
        "wsj": {"category": "news", "typical_amount": 39.99},
        "hulu": {"category": "streaming", "typical_amount": 7.99},
        "disney+": {"category": "streaming", "typical_amount": 7.99},
        "adobe": {"category": "software", "typical_amount": 52.99},
        "microsoft 365": {"category": "software", "typical_amount": 6.99},
        "dropbox": {"category": "storage", "typical_amount": 11.99},
        "linkedin premium": {"category": "professional", "typical_amount": 29.99}
    }
    
    def __init__(self):
        self.min_occurrences = 2  # Minimum charges to consider it a subscription
        self.recurrence_tolerance_days = 3  # Allow 3-day variance in billing
    
    def detect_subscriptions(
        self, 
        transactions: List[Transaction],
        usage_data: Optional[Dict[str, int]] = None
    ) -> List[Subscription]:
        """
        Detect subscriptions from transaction history
        
        Args:
            transactions: List of bank transactions
            usage_data: Optional dict of merchant -> usage count
            
        Returns:
            List of detected subscriptions
        """
        
        # Group transactions by merchant
        merchant_groups = self._group_by_merchant(transactions)
        
        subscriptions = []
        
        for merchant, txns in merchant_groups.items():
            # Need at least 2 transactions to detect pattern
            if len(txns) < self.min_occurrences:
                continue
            
            # Check if it's a recurring pattern
            is_recurring, frequency = self._check_recurrence(txns)
            
            if is_recurring:
                # Calculate statistics
                amounts = [t.amount for t in txns]
                avg_amount = sum(amounts) / len(amounts)
                total_spent = sum(amounts)
                last_charge = max(t.date for t in txns)
                
                # Calculate confidence (how sure are we it's a subscription?)
                confidence = self._calculate_confidence(merchant, txns, frequency)
                
                # Calculate usage score
                usage_score = self._calculate_usage_score(
                    merchant, 
                    txns, 
                    usage_data
                )
                
                # Generate recommendation
                recommendation, reasoning = self._generate_recommendation(
                    merchant,
                    frequency,
                    avg_amount,
                    usage_score,
                    last_charge
                )
                
                subscriptions.append(Subscription(
                    merchant=merchant,
                    frequency=frequency,
                    average_amount=avg_amount,
                    last_charge=last_charge,
                    total_charges=len(txns),
                    total_spent=total_spent,
                    confidence=confidence,
                    usage_score=usage_score,
                    recommendation=recommendation,
                    reasoning=reasoning
                ))
        
        # Sort by potential savings (unused + expensive first)
        subscriptions.sort(
            key=lambda s: (1 - s.usage_score) * s.average_amount,
            reverse=True
        )
        
        return subscriptions
    
    def _group_by_merchant(self, transactions: List[Transaction]) -> Dict[str, List[Transaction]]:
        """Group transactions by normalized merchant name"""
        groups = defaultdict(list)
        
        for txn in transactions:
            normalized = self._normalize_merchant(txn.merchant)
            groups[normalized].append(txn)
        
        return dict(groups)
    
    def _normalize_merchant(self, merchant: str) -> str:
        """Normalize merchant name for matching"""
        # Convert to lowercase
        normalized = merchant.lower()
        
        # Remove common suffixes
        normalized = re.sub(r'\s*(inc|llc|ltd|corp|co)\s*$', '', normalized)
        
        # Remove special characters
        normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        # Check if it matches a known subscription
        for known in self.KNOWN_SUBSCRIPTIONS:
            if known in normalized or normalized in known:
                return known
        
        return normalized
    
    def _check_recurrence(self, transactions: List[Transaction]) -> tuple[bool, str]:
        """
        Check if transactions follow a recurring pattern
        
        Returns:
            (is_recurring, frequency)
        """
        if len(transactions) < 2:
            return False, "UNKNOWN"
        
        # Sort by date
        sorted_txns = sorted(transactions, key=lambda t: t.date)
        
        # Calculate days between charges
        intervals = []
        for i in range(1, len(sorted_txns)):
            days = (sorted_txns[i].date - sorted_txns[i-1].date).days
            intervals.append(days)
        
        if not intervals:
            return False, "UNKNOWN"
        
        # Check for monthly pattern (28-32 days)
        monthly_intervals = [i for i in intervals if 28 <= i <= 32]
        if len(monthly_intervals) >= len(intervals) * 0.7:  # 70% match
            return True, "MONTHLY"
        
        # Check for annual pattern (360-370 days)
        annual_intervals = [i for i in intervals if 360 <= i <= 370]
        if len(annual_intervals) >= len(intervals) * 0.7:
            return True, "ANNUAL"
        
        # Check for weekly pattern (6-8 days)
        weekly_intervals = [i for i in intervals if 6 <= i <= 8]
        if len(weekly_intervals) >= len(intervals) * 0.7:
            return True, "WEEKLY"
        
        # Check for quarterly (88-92 days)
        quarterly_intervals = [i for i in intervals if 88 <= i <= 92]
        if len(quarterly_intervals) >= len(intervals) * 0.7:
            return True, "QUARTERLY"
        
        return False, "UNKNOWN"
    
    def _calculate_confidence(
        self, 
        merchant: str, 
        transactions: List[Transaction],
        frequency: str
    ) -> float:
        """
        Calculate confidence that this is a subscription
        
        Returns: 0-1 score
        """
        confidence = 0.0
        
        # Known subscription merchant
        if merchant in self.KNOWN_SUBSCRIPTIONS:
            confidence += 0.4
        
        # Consistent amounts
        amounts = [t.amount for t in transactions]
        if len(set(amounts)) == 1:  # All same amount
            confidence += 0.3
        elif max(amounts) - min(amounts) < 2.00:  # Within $2
            confidence += 0.2
        
        # Regular frequency
        if frequency in ["MONTHLY", "ANNUAL"]:
            confidence += 0.2
        
        # Number of occurrences
        if len(transactions) >= 6:
            confidence += 0.1
        elif len(transactions) >= 3:
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    def _calculate_usage_score(
        self,
        merchant: str,
        transactions: List[Transaction],
        usage_data: Optional[Dict[str, int]]
    ) -> float:
        """
        Calculate usage score (0 = never used, 1 = heavily used)
        
        Args:
            merchant: Merchant name
            transactions: Transaction history
            usage_data: Optional usage metrics (e.g., gym check-ins, streaming hours)
        """
        
        if not usage_data:
            # No usage data available - assume moderate usage
            return 0.5
        
        # Get usage count for this merchant
        usage_count = usage_data.get(merchant, 0)
        
        # Calculate expected usage based on subscription frequency
        months_active = len(transactions)
        
        # Heuristics for different categories
        merchant_info = self.KNOWN_SUBSCRIPTIONS.get(merchant, {})
        category = merchant_info.get("category", "unknown")
        
        if category == "gym":
            # Expect at least 8 visits per month for a gym
            expected_usage = months_active * 8
            usage_score = min(usage_count / expected_usage, 1.0) if expected_usage > 0 else 0
        
        elif category == "streaming":
            # Expect at least 10 hours per month
            expected_usage = months_active * 10
            usage_score = min(usage_count / expected_usage, 1.0) if expected_usage > 0 else 0
        
        elif category == "storage":
            # If they have storage subscription, assume they're using it
            usage_score = 0.8 if usage_count > 0 else 0.2
        
        else:
            # Generic: any usage is good
            usage_score = min(usage_count / (months_active * 4), 1.0)
        
        return usage_score
    
    def _generate_recommendation(
        self,
        merchant: str,
        frequency: str,
        amount: float,
        usage_score: float,
        last_charge: datetime
    ) -> tuple[str, str]:
        """
        Generate recommendation and reasoning
        
        Returns:
            (recommendation, reasoning)
        """
        
        # Calculate monthly cost
        if frequency == "ANNUAL":
            monthly_cost = amount / 12
        elif frequency == "WEEKLY":
            monthly_cost = amount * 4.33
        else:  # MONTHLY or QUARTERLY
            monthly_cost = amount
        
        # Decision logic
        if usage_score < 0.2:
            # Very low usage
            return "CANCEL", (
                f"Zero or minimal usage detected. "
                f"Wasting ${monthly_cost:.2f}/month on unused subscription."
            )
        
        elif usage_score < 0.5 and monthly_cost > 20:
            # Low usage + expensive
            return "CANCEL", (
                f"Low usage ({usage_score*100:.0f}%) for ${monthly_cost:.2f}/month. "
                f"Consider canceling or switching to pay-per-use."
            )
        
        elif usage_score < 0.5:
            # Low usage but cheap
            return "REVIEW", (
                f"Low usage ({usage_score*100:.0f}%) detected. "
                f"Review if ${monthly_cost:.2f}/month is worth keeping."
            )
        
        elif monthly_cost > 50 and usage_score < 0.7:
            # Expensive + moderate usage
            return "REVIEW", (
                f"Expensive subscription (${monthly_cost:.2f}/month) with moderate usage. "
                f"Consider if there are cheaper alternatives."
            )
        
        else:
            # Good usage
            return "KEEP", (
                f"Good usage ({usage_score*100:.0f}%) for ${monthly_cost:.2f}/month. "
                f"Subscription appears valuable."
            )


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("💳 SUBSCRIPTION DETECTOR - TEST")
    print("=" * 70)
    
    # Create sample transactions
    base_date = datetime(2025, 1, 15)
    
    transactions = [
        # Netflix - used regularly
        Transaction(base_date, "NETFLIX.COM", 15.99, "Entertainment", "Monthly subscription"),
        Transaction(base_date + timedelta(days=30), "NETFLIX.COM", 15.99, "Entertainment", "Monthly subscription"),
        Transaction(base_date + timedelta(days=60), "NETFLIX.COM", 15.99, "Entertainment", "Monthly subscription"),
        Transaction(base_date + timedelta(days=90), "NETFLIX.COM", 15.99, "Entertainment", "Monthly subscription"),
        
        # Planet Fitness - never used
        Transaction(base_date, "PLANET FITNESS", 10.00, "Health", "Gym membership"),
        Transaction(base_date + timedelta(days=30), "PLANET FITNESS", 10.00, "Health", "Gym membership"),
        Transaction(base_date + timedelta(days=60), "PLANET FITNESS", 10.00, "Health", "Gym membership"),
        
        # Adobe - expensive, moderate use
        Transaction(base_date, "ADOBE CREATIVE", 52.99, "Software", "Creative Cloud"),
        Transaction(base_date + timedelta(days=30), "ADOBE CREATIVE", 52.99, "Software", "Creative Cloud"),
        Transaction(base_date + timedelta(days=60), "ADOBE CREATIVE", 52.99, "Software", "Creative Cloud"),
        
        # Random one-time purchases (should not be detected)
        Transaction(base_date + timedelta(days=5), "WHOLE FOODS", 87.50, "Groceries", "Groceries"),
        Transaction(base_date + timedelta(days=15), "AMAZON.COM", 45.99, "Shopping", "Books"),
    ]
    
    # Mock usage data
    usage_data = {
        "netflix": 120,  # 120 hours watched over 3 months = high usage
        "planet fitness": 0,  # 0 gym visits = no usage
        "adobe": 15  # 15 times opened = moderate usage
    }
    
    # Detect subscriptions
    detector = SubscriptionDetector()
    subscriptions = detector.detect_subscriptions(transactions, usage_data)
    
    print(f"\n📊 Found {len(subscriptions)} subscriptions:\n")
    
    total_monthly_cost = 0
    potential_savings = 0
    
    for sub in subscriptions:
        monthly_cost = sub.average_amount if sub.frequency == "MONTHLY" else sub.average_amount / 12
        total_monthly_cost += monthly_cost
        
        print(f"{'='*70}")
        print(f"Merchant: {sub.merchant.upper()}")
        print(f"Frequency: {sub.frequency}")
        print(f"Amount: ${sub.average_amount:.2f}")
        print(f"Total Spent: ${sub.total_spent:.2f} ({sub.total_charges} charges)")
        print(f"Confidence: {sub.confidence*100:.0f}%")
        print(f"Usage Score: {sub.usage_score*100:.0f}%")
        print(f"Recommendation: {sub.recommendation}")
        print(f"Reasoning: {sub.reasoning}")
        
        if sub.recommendation == "CANCEL":
            potential_savings += monthly_cost
            print(f"💰 Potential Monthly Savings: ${monthly_cost:.2f}")
    
    print(f"\n{'='*70}")
    print(f"📈 SUMMARY")
    print(f"{'='*70}")
    print(f"Total Monthly Subscription Cost: ${total_monthly_cost:.2f}")
    print(f"Potential Monthly Savings: ${potential_savings:.2f}")
    print(f"Annual Savings if Canceled: ${potential_savings * 12:.2f}")
    
    print("\n✅ Subscription detector tests complete!")
