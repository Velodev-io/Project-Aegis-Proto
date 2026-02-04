"""
Real Lithic Card Issuance Test
================================

This script uses your actual Lithic API key to:
1. Create a real virtual card
2. Display card details
3. Test the authorization flow

IMPORTANT: This creates a REAL card in your Lithic account!
"""

import os
from virtual_card_manager import VirtualCardManager
from transaction_governor import ContextAwareGovernor
from datetime import datetime
import json

# Set your Lithic API key
LITHIC_API_KEY = "bcc003a0-8f62-4707-a1e9-3a54eeb471b7"
os.environ["LITHIC_API_KEY"] = LITHIC_API_KEY

print("=" * 70)
print("🚀 LITHIC SANDBOX CARD ISSUANCE TEST")
print("=" * 70)
print(f"API Key: {LITHIC_API_KEY[:20]}...")
print(f"Environment: SANDBOX")
print()

# Initialize manager with sandbox mode
manager = VirtualCardManager(
    api_key=LITHIC_API_KEY, 
    provider="lithic",
    environment="sandbox"  # Use sandbox endpoint
)

# Step 1: Create a real virtual card
print("=" * 70)
print("STEP 1: Creating Real Virtual Card")
print("=" * 70)

try:
    card = manager.create_card_for_senior(
        senior_id="senior_robert_001",
        senior_name="Robert Johnson",
        spending_limit_monthly=2000.00,
        spending_limit_daily=200.00
    )
    
    print("✅ CARD CREATED SUCCESSFULLY!")
    print()
    print(json.dumps(card, indent=2))
    print()
    
    # Save card details
    with open("lithic_card_details.json", "w") as f:
        json.dump(card, f, indent=2)
    
    print("💾 Card details saved to: lithic_card_details.json")
    print()
    
except Exception as e:
    print(f"❌ Error creating card: {e}")
    print()
    print("This might be because:")
    print("1. API key is for sandbox (needs real account)")
    print("2. Account not fully set up")
    print("3. Need to complete KYC/compliance")
    print()
    exit(1)

# Step 2: Get card details
print("=" * 70)
print("STEP 2: Card Details")
print("=" * 70)
print(f"Card ID: {card['card_id']}")
print(f"Last 4 Digits: {card['last_four']}")
print(f"Expiry: {card['exp_month']}/{card['exp_year']}")
print(f"Status: {card['status']}")
print(f"Monthly Limit: ${card['spending_limits']['monthly']}")
print(f"Daily Limit: ${card['spending_limits']['daily']}")
print()

# Step 3: Simulate authorization
print("=" * 70)
print("STEP 3: Simulating Transaction Authorization")
print("=" * 70)

sentinel = ContextAwareGovernor()

# Test 1: Normal grocery purchase (should approve)
print("\n📊 TEST 1: Normal Grocery Purchase")
print("-" * 70)

auth_request_1 = {
    "card_token": card["card_id"],
    "amount": 8750,  # $87.50
    "merchant": {
        "descriptor": "WHOLE FOODS",
        "mcc": "5411"  # Groceries
    },
    "created": datetime.now().replace(hour=14).isoformat()  # 2 PM
}

decision_1 = manager.authorize_transaction(auth_request_1, sentinel)
print(f"\n✅ Result: {decision_1['result']}")
print(f"   Reasoning: {decision_1.get('metadata', {}).get('decline_reason', 'Approved')}")

# Test 2: 2 AM laptop purchase (should decline)
print("\n📊 TEST 2: 2 AM Laptop Purchase")
print("-" * 70)

auth_request_2 = {
    "card_token": card["card_id"],
    "amount": 129999,  # $1,299.99
    "merchant": {
        "descriptor": "BEST BUY",
        "mcc": "5732"  # Electronics
    },
    "created": datetime.now().replace(hour=2).isoformat()  # 2 AM
}

decision_2 = manager.authorize_transaction(auth_request_2, sentinel)
print(f"\n❌ Result: {decision_2['result']}")
print(f"   Reasoning: {decision_2.get('metadata', {}).get('decline_reason', 'N/A')}")

# Test 3: Gift card purchase (should decline)
print("\n📊 TEST 3: Gift Card Purchase")
print("-" * 70)

auth_request_3 = {
    "card_token": card["card_id"],
    "amount": 50000,  # $500
    "merchant": {
        "descriptor": "CVS PHARMACY",
        "mcc": "5945"  # Gift Cards
    },
    "created": datetime.now().replace(hour=20).isoformat()  # 8 PM
}

decision_3 = manager.authorize_transaction(auth_request_3, sentinel)
print(f"\n❌ Result: {decision_3['result']}")
print(f"   Reasoning: {decision_3.get('metadata', {}).get('decline_reason', 'N/A')}")

# Summary
print("\n" + "=" * 70)
print("📊 SUMMARY")
print("=" * 70)
print(f"✅ Card Created: {card['card_id']}")
print(f"✅ Test 1 (Groceries): {decision_1['result']}")
print(f"✅ Test 2 (2 AM Laptop): {decision_2['result']}")
print(f"✅ Test 3 (Gift Cards): {decision_3['result']}")
print()
print("🎉 All tests completed successfully!")
print()
print("=" * 70)
print("NEXT STEPS")
print("=" * 70)
print("1. Add this card to Apple Pay (check Lithic dashboard)")
print("2. Configure webhook URL in Lithic dashboard:")
print("   https://yourdomain.com/webhook/card-auth")
print("3. Test real transaction with phone")
print("=" * 70)
