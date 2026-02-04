"""
Direct Lithic API Test
======================

Testing different authentication methods with your API key
"""

import requests
import json

API_KEY = "bcc003a0-8f62-4707-a1e9-3a54eeb471b7"

print("=" * 70)
print("🔍 TESTING LITHIC API KEY")
print("=" * 70)
print(f"Key: {API_KEY}")
print()

# Test 1: Bearer token (standard)
print("Test 1: Bearer Authorization (Standard)")
print("-" * 70)
try:
    response = requests.get(
        "https://sandbox.lithic.com/v1/cards",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

print()

# Test 2: API-Key header
print("Test 2: API-Key Header")
print("-" * 70)
try:
    response = requests.get(
        "https://sandbox.lithic.com/v1/cards",
        headers={
            "API-Key": API_KEY,
            "Content-Type": "application/json"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

print()

# Test 3: X-API-Key header
print("Test 3: X-API-Key Header")
print("-" * 70)
try:
    response = requests.get(
        "https://sandbox.lithic.com/v1/cards",
        headers={
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

print()

# Test 4: Production endpoint
print("Test 4: Production Endpoint")
print("-" * 70)
try:
    response = requests.get(
        "https://api.lithic.com/v1/cards",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

print()

# Test 5: Account endpoint
print("Test 5: Account Info")
print("-" * 70)
try:
    response = requests.get(
        "https://sandbox.lithic.com/v1/account",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print()

# Test 6: Try to create a card
print("Test 6: Create Card Attempt")
print("-" * 70)
try:
    response = requests.post(
        "https://sandbox.lithic.com/v1/cards",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "type": "VIRTUAL",
            "memo": "Test Card for Aegis"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    if response.status_code == 201:
        print("\n🎉 SUCCESS! Card created!")
        card_data = response.json()
        print(json.dumps(card_data, indent=2))
except Exception as e:
    print(f"Error: {e}")

print()
print("=" * 70)
print("📊 SUMMARY")
print("=" * 70)
print("If all tests failed with 401/403, the key format might be incorrect.")
print("Please check the Lithic dashboard for the correct API key format.")
print("It should start with 'sk_sandbox_' or 'sk_live_'")
print("=" * 70)
