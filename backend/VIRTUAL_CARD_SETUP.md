# Virtual Card Integration - Setup Guide

## 🎯 Overview

This implementation gives you **100% control** over senior spending at the payment network level. When a senior taps their phone to pay, the card network (Visa/Mastercard) asks YOUR AI: "Should I allow this?" in real-time.

## 🏗️ Architecture

```
Senior's Phone (Apple Pay)
         ↓
    Taps to Pay
         ↓
  Visa/Mastercard Network
         ↓
   YOUR WEBHOOK (/webhook/card-auth)
         ↓
   Sentinel AI Analysis (<100ms)
         ↓
   APPROVED or DECLINED
         ↓
  Transaction Completes/Fails
```

## 📋 Prerequisites

### 1. Choose a Card Issuing Provider

**Option A: Lithic (Recommended for Startups)**
- Website: https://lithic.com
- Cost: $0.50/card/month + interchange fees
- Setup time: 1-2 weeks (compliance review)
- Best for: MVP, startups, fast iteration

**Option B: Stripe Issuing**
- Website: https://stripe.com/issuing
- Cost: $0.50/card/month + interchange fees
- Setup time: 1-2 weeks
- Best for: If already using Stripe

**Option C: Marqeta**
- Website: https://marqeta.com
- Cost: Enterprise pricing
- Setup time: 4-6 weeks
- Best for: Large scale, enterprise

### 2. Sign Up and Get API Keys

For Lithic (example):
1. Go to https://lithic.com
2. Sign up for sandbox account
3. Get API key from dashboard
4. Set webhook URL to your server

## 🚀 Installation

### 1. Install Dependencies

```bash
cd backend
pip install lithic  # or stripe if using Stripe Issuing
pip install -r requirements_sentinel.txt
```

### 2. Set Environment Variables

```bash
# .env file
LITHIC_API_KEY=your_api_key_here
LITHIC_WEBHOOK_SECRET=your_webhook_secret_here
```

### 3. Start the Authorization Service

```bash
# Terminal 1: Main API
python main.py

# Terminal 2: Card Authorization Service
python card_auth_service.py
```

This starts the webhook server on port 8001.

## 🧪 Testing (Without Real Cards)

### Test 1: Simulate a Normal Purchase

```bash
curl -X POST http://localhost:8001/test/simulate-purchase \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50.00,
    "merchant_name": "Whole Foods",
    "merchant_category": "Groceries",
    "hour": 14
  }'
```

**Expected Result:** APPROVED (low risk)

### Test 2: Simulate a 2 AM Laptop Purchase

```bash
curl -X POST http://localhost:8001/test/simulate-purchase \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1299.99,
    "merchant_name": "Best Buy",
    "merchant_category": "Electronics",
    "hour": 2
  }'
```

**Expected Result:** DECLINED (critical risk)

### Test 3: Simulate a Gift Card Purchase

```bash
curl -X POST http://localhost:8001/test/simulate-purchase \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500.00,
    "merchant_name": "Target",
    "merchant_category": "Gift Cards",
    "hour": 20
  }'
```

**Expected Result:** DECLINED (scam indicator)

## 🎯 Production Deployment

### 1. Set Up Webhook URL

Your card issuing provider needs to send authorization requests to your server.

**For Lithic:**
1. Go to Lithic Dashboard → Webhooks
2. Add webhook URL: `https://yourdomain.com/webhook/card-auth`
3. Select events: `card_authorization`
4. Copy webhook secret

**Important:** Your server must:
- Be publicly accessible (use ngrok for testing)
- Use HTTPS (required by card networks)
- Respond in <100ms (card network timeout)

### 2. Deploy to Production

```bash
# Using Railway, Render, or any cloud provider
railway up

# Or Docker
docker build -t aegis-card-auth .
docker run -p 8001:8001 aegis-card-auth
```

### 3. Configure Webhook in Provider Dashboard

```
Webhook URL: https://your-domain.com/webhook/card-auth
Events: card_authorization, card_created, transaction_updated
```

## 📱 Senior Setup Flow

### 1. Issue Card

```python
from virtual_card_manager import VirtualCardManager

manager = VirtualCardManager(api_key="your_lithic_key")

card = manager.create_card_for_senior(
    senior_id="senior_001",
    senior_name="Robert Johnson",
    spending_limit_monthly=2000.00,
    spending_limit_daily=200.00
)

print(f"Card created: {card['card_id']}")
print(f"Last 4 digits: {card['last_four']}")
```

### 2. Add to Apple Pay

```python
# Generate provisioning data
apple_pay_data = manager.add_to_apple_pay(card['card_id'])

# Senior scans QR code or receives push notification
# Card appears in Apple Wallet
```

### 3. Senior Can Now Pay!

When the senior taps their phone:
1. Visa sends request to your webhook
2. Your AI analyzes in <100ms
3. Transaction approved or declined
4. Senior sees result on phone

## 🎨 Frontend Integration

Add to your Caregiver Dashboard:

```javascript
// Create card for senior
async function createCardForSenior(seniorId, seniorName) {
  const response = await fetch('http://localhost:8001/cards/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      senior_id: seniorId,
      senior_name: seniorName,
      monthly_limit: 2000.00,
      daily_limit: 200.00
    })
  });
  return await response.json();
}

// Freeze card immediately
async function freezeCard(cardId, reason) {
  const response = await fetch(`http://localhost:8001/cards/freeze?card_id=${cardId}&reason=${reason}`, {
    method: 'POST'
  });
  return await response.json();
}

// Update spending limits
async function updateLimits(cardId, monthlyLimit) {
  const response = await fetch('http://localhost:8001/cards/update-limits', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      card_id: cardId,
      monthly_limit: monthlyLimit
    })
  });
  return await response.json();
}
```

## 🔒 Security Features

### 1. Webhook Signature Verification

```python
# Automatically verified in card_auth_service.py
is_valid = card_manager.verify_webhook_signature(
    payload=request_body,
    signature=x_lithic_signature,
    webhook_secret=WEBHOOK_SECRET
)
```

### 2. Real-Time Fraud Detection

- Sentinel AI analyzes every transaction
- Risk scoring: 0-100
- Auto-decline on critical risk
- Advocate notification on high risk

### 3. Instant Card Freeze

```python
# If scam detected during call
manager.freeze_card(card_id, reason="Scam call detected")
```

## 📊 Decision Matrix

| Risk Score | Risk Level | Action | Example |
|-----------|-----------|--------|---------|
| 0-30 | LOW | ✅ Auto Approve | $50 groceries at 2 PM |
| 31-69 | MEDIUM | ✅ Approve + Monitor | $200 electronics at 3 PM |
| 70-89 | HIGH | ⏸️ Decline + Notify Advocate | $500 at 11 PM |
| 90-100 | CRITICAL | ❌ Auto Decline | $1000 gift cards at 2 AM |

## 🎯 Real-World Example

**Scenario:** Senior receives scam call at 2 AM

1. **Scammer:** "Send $500 in gift cards now!"
2. **Senior:** Tries to buy gift cards at CVS
3. **Senior:** Taps phone to pay
4. **Visa:** Sends auth request to your webhook
5. **Your AI:** Detects: 2 AM + Gift Cards + $500 = CRITICAL
6. **Response:** DECLINED
7. **Senior's Phone:** "Card Declined"
8. **Caregiver:** Gets notification: "High-risk transaction blocked"

**Result:** Senior protected, scammer gets nothing! 🛡️

## 💡 Advanced Features

### 1. Time-Based Rules

```python
# Only allow purchases 8 AM - 8 PM
if transaction_time.hour < 8 or transaction_time.hour > 20:
    return "DECLINED"
```

### 2. Merchant Whitelist

```python
# Only allow specific merchants
ALLOWED_MERCHANTS = ["WHOLE FOODS", "WALGREENS", "CVS"]
if merchant_name not in ALLOWED_MERCHANTS:
    return "DECLINED"
```

### 3. Velocity Checks

```python
# Max 3 transactions per hour
recent_transactions = get_recent_transactions(card_id, hours=1)
if len(recent_transactions) >= 3:
    return "DECLINED"
```

## 📞 Support

For issues with:
- **Lithic API:** support@lithic.com
- **Stripe Issuing:** https://support.stripe.com
- **This Implementation:** Check logs in `card_auth_service.py`

## 🚀 Next Steps

1. ✅ Test with mock transactions
2. ✅ Sign up for Lithic/Stripe sandbox
3. ✅ Deploy webhook to production
4. ✅ Issue test card
5. ✅ Add to Apple Pay
6. ✅ Test real transaction
7. ✅ Launch! 🎉

---

**This is the most powerful approach because:**
- ✅ No phone permissions needed
- ✅ Works with any merchant
- ✅ Instant protection
- ✅ 100% control
- ✅ Senior has normal payment experience
- ✅ Caregiver has full visibility

You're building what True Link Financial charges $10/month for! 💪
