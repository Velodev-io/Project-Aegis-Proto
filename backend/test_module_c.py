"""
Module C: The Proxy - Comprehensive Test Suite
Tests scope violations, limit violations, and expired POAs
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def print_test_header(test_name):
    print("\n" + "="*70)
    print(f"TEST: {test_name}")
    print("="*70)

def print_result(result, expected):
    status = "✅ PASS" if result == expected else "❌ FAIL"
    print(f"{status} - Expected: {expected}, Got: {result}")

def test_scope_violation():
    """
    Test 1: Scope Violation
    POA only allows 'medical' scope, but AI tries to pay Spotify bill
    Expected: BLOCKED decision
    """
    print_test_header("Scope Violation Test")
    
    # Step 1: Create POA with 'medical' scope only
    print("\n1️⃣  Creating POA with 'medical' scope only...")
    poa_data = {
        "senior_id": "senior_test_001",
        "agent_id": "ai_agent_test",
        "scope": "medical",
        "spend_limit": 500.00,
        "expiry_days": 30,
        "specific_services": ["Medical Bills", "Pharmacy"],
        "created_by": "test_suite"
    }
    
    response = requests.post(f"{BASE_URL}/proxy/vault/poa", json=poa_data)
    print(f"   Response: {response.status_code}")
    poa_result = response.json()
    print(f"   POA ID: {poa_result['poa_id']}")
    poa_id = poa_result['poa_id']
    
    # Step 2: Attempt to validate Spotify payment (scope violation)
    print("\n2️⃣  Attempting to pay $50 Spotify bill (SHOULD BE BLOCKED)...")
    validate_data = {
        "poa_id": poa_id,
        "service_name": "Spotify",
        "amount": 50.00,
        "action": "payment"
    }
    
    response = requests.post(f"{BASE_URL}/proxy/tokens/validate", json=validate_data)
    result = response.json()
    
    print(f"   Decision: {result['decision']}")
    print(f"   Reasoning: {result['reasoning']}")
    
    # Verify
    print("\n3️⃣  Verification:")
    print_result(result['decision'], "BLOCKED")
    print_result(result['authorized'], False)
    
    if 'violation_type' in result:
        print(f"   Violation Type: {result['violation_type']}")
    
    return result['decision'] == "BLOCKED"


def test_limit_violation():
    """
    Test 2: Limit Violation
    POA has $200 limit, AI tries $201 transaction
    Expected: BREAK_GLASS decision with event creation
    """
    print_test_header("Limit Violation Test (Break-Glass Protocol)")
    
    # Step 1: Create POA with $200 limit
    print("\n1️⃣  Creating POA with $200 spend limit...")
    poa_data = {
        "senior_id": "senior_test_002",
        "agent_id": "ai_agent_test",
        "scope": "utilities",
        "spend_limit": 200.00,
        "expiry_days": 30,
        "created_by": "test_suite"
    }
    
    response = requests.post(f"{BASE_URL}/proxy/vault/poa", json=poa_data)
    poa_result = response.json()
    print(f"   POA ID: {poa_result['poa_id']}")
    poa_id = poa_result['poa_id']
    
    # Step 2: Attempt $201 transaction (limit violation)
    print("\n2️⃣  Attempting $201 transaction (SHOULD TRIGGER BREAK-GLASS)...")
    validate_data = {
        "poa_id": poa_id,
        "service_name": "Electric Bill",
        "amount": 201.00,
        "action": "payment"
    }
    
    response = requests.post(f"{BASE_URL}/proxy/tokens/validate", json=validate_data)
    result = response.json()
    
    print(f"   Decision: {result['decision']}")
    print(f"   Reasoning: {result['reasoning']}")
    
    # Verify Break-Glass Event
    print("\n3️⃣  Verification:")
    print_result(result['decision'], "BREAK_GLASS")
    
    if 'break_glass_event_id' in result:
        print(f"   ✅ Break-Glass Event Created: ID {result['break_glass_event_id']}")
        print(f"   ✅ 2FA Required: {result.get('two_fa_required', False)}")
        
        # Check pending events
        print("\n4️⃣  Checking pending break-glass events...")
        response = requests.get(f"{BASE_URL}/proxy/break-glass/pending")
        pending = response.json()
        print(f"   Total Pending Events: {pending['total_pending']}")
        
        if pending['total_pending'] > 0:
            event = pending['events'][0]
            print(f"   Event Status: {event['status']}")
            print(f"   Trigger Reason: {event['trigger_reason']}")
    
    return result['decision'] == "BREAK_GLASS"


def test_expired_poa():
    """
    Test 3: Expired POA
    POA expired yesterday, AI tries to use it
    Expected: BLOCKED decision with "expired or revoked" reasoning
    """
    print_test_header("Expired POA Test")
    
    # Step 1: Create POA with expiry date in the past
    print("\n1️⃣  Creating POA with expiry date YESTERDAY...")
    poa_data = {
        "senior_id": "senior_test_003",
        "agent_id": "ai_agent_test",
        "scope": "banking",
        "spend_limit": 1000.00,
        "expiry_days": -1,  # Expired yesterday
        "created_by": "test_suite"
    }
    
    response = requests.post(f"{BASE_URL}/proxy/vault/poa", json=poa_data)
    poa_result = response.json()
    print(f"   POA ID: {poa_result['poa_id']}")
    poa_id = poa_result['poa_id']
    
    # Step 2: Attempt to use expired POA
    print("\n2️⃣  Attempting to use EXPIRED POA (SHOULD BE BLOCKED)...")
    validate_data = {
        "poa_id": poa_id,
        "service_name": "Bank Transfer",
        "amount": 100.00,
        "action": "transfer"
    }
    
    response = requests.post(f"{BASE_URL}/proxy/tokens/validate", json=validate_data)
    result = response.json()
    
    print(f"   Decision: {result['decision']}")
    print(f"   Reasoning: {result['reasoning']}")
    
    # Verify
    print("\n3️⃣  Verification:")
    print_result(result['decision'], "BLOCKED")
    
    # Check if reasoning mentions expiry
    is_expired_mentioned = "expired" in result['reasoning'].lower() or "revoked" in result['reasoning'].lower()
    print_result(is_expired_mentioned, True)
    
    return result['decision'] == "BLOCKED" and is_expired_mentioned


def run_all_tests():
    """Run all Module C tests"""
    print("\n" + "🚀 "*35)
    print("MODULE C: THE PROXY - COMPREHENSIVE TEST SUITE")
    print("🚀 "*35)
    
    results = {
        "Scope Violation": False,
        "Limit Violation": False,
        "Expired POA": False
    }
    
    try:
        # Test 1: Scope Violation
        results["Scope Violation"] = test_scope_violation()
        
        # Test 2: Limit Violation (Break-Glass)
        results["Limit Violation"] = test_limit_violation()
        
        # Test 3: Expired POA
        results["Expired POA"] = test_expired_poa()
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED! Module C is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")


if __name__ == "__main__":
    run_all_tests()
