# Module C: The Proxy - README

## 🔐 Digital POA Vault with Break-Glass Protocol

**Module C** implements a revolutionary **Smart Power of Attorney** system that replaces traditional "all-or-nothing" legal documents with granular, time-limited, scope-restricted digital credentials.

---

## 🎯 Core Innovation

### Traditional POA Problem
```
"You can do EVERYTHING for me, FOREVER"
❌ Too broad
❌ No limits
❌ No oversight
❌ High risk of abuse
```

### Aegis Smart POA Solution
```
"You can negotiate my AT&T bill, max $100, expires in 30 days"
✅ Specific scope
✅ Spend limits
✅ Time-limited
✅ Automatic monitoring
✅ Break-glass protocol for violations
```

---

## 🏗️ Architecture

### 1. Digital POA Vault
**Granular Permission Management**

- **Scope-based**: utilities, banking, healthcare, subscriptions
- **Service-specific**: Optional restriction to specific services (e.g., only "AT&T" and "Water Bill")
- **Spend limits**: Maximum transaction amount per POA
- **Time-limited**: Automatic expiration
- **Instant revocation**: Can be revoked at any time

### 2. Token Gatekeeper
**OAuth Token Management & Validation**

- **Fernet Encryption**: Symmetric encryption for stored tokens
- **Scope Validation**: Blocks requests outside POA scope
- **Spend Limit Enforcement**: Triggers break-glass for violations
- **Audit Trail**: Every request logged with cryptographic signature

### 3. Break-Glass Protocol
**Emergency Override with Multi-Factor Verification**

**Triggers:**
- Transaction exceeds spend limit
- Request outside POA scope
- Unusual activity patterns

**Workflow:**
1. Violation detected → Create break-glass event
2. Send push notification to Trusted Advocate
3. Generate 2FA code (TOTP, 5-minute window)
4. Optional: Require liveness detection (face/voice)
5. Advocate approves/denies
6. All actions logged with signatures

### 4. Fiduciary Proof
**Legal-Grade Audit Trail**

- **HMAC-SHA256 Signatures**: Cryptographically signed logs
- **Immutable Records**: Cannot be altered after creation
- **PDF Export**: Legal documentation for authorities
- **Signature Verification**: Independent verification of authenticity

---

## 📡 API Endpoints

### Vault Management

```bash
# Create Smart POA
POST /proxy/vault/poa
{
  "senior_id": "senior_001",
  "agent_id": "ai_agent_001",
  "scope": "utilities",
  "spend_limit": 100.00,
  "expiry_days": 30,
  "specific_services": ["AT&T", "Water Bill"]
}

# Get POA
GET /proxy/vault/poa/{poa_id}

# Revoke POA
DELETE /proxy/vault/poa/{poa_id}?reason=No%20longer%20needed&revoked_by=senior_001

# List all POAs for senior
GET /proxy/vault/poa/senior/{senior_id}
```

### Token Management

```bash
# Store encrypted OAuth token
POST /proxy/tokens/store
{
  "poa_id": 1,
  "service_name": "plaid",
  "token": "access_token_here",
  "token_type": "access",
  "expires_in_seconds": 3600
}

# Validate request (TOKEN GATEKEEPER)
POST /proxy/tokens/validate
{
  "poa_id": 1,
  "service_name": "AT&T",
  "amount": 75.50,
  "action": "payment"
}
# Returns: ALLOWED, BLOCKED, or BREAK_GLASS

# Decrypt token for authorized use
GET /proxy/tokens/decrypt/{token_id}
```

### Break-Glass Protocol

```bash
# Verify 2FA code
POST /proxy/break-glass/verify-2fa
{
  "event_id": 1,
  "code": "123456"
}

# Verify liveness (face/voice)
POST /proxy/break-glass/verify-liveness
{
  "event_id": 1,
  "method": "face",
  "verification_data": {}
}

# Deny break-glass request
POST /proxy/break-glass/deny
{
  "event_id": 1,
  "denied_by": "advocate_001",
  "reason": "Suspicious activity"
}

# Get pending break-glass events
GET /proxy/break-glass/pending?advocate_id=advocate_001
```

### Audit Trail

```bash
# Get audit logs
GET /proxy/audit/logs/{poa_id}?action_type=TRANSACTION&decision=ALLOWED&limit=100

# Export audit trail (JSON or PDF)
GET /proxy/audit/export/{poa_id}?format=pdf

# Verify audit log signature
POST /proxy/audit/verify/{log_id}
```

### Credentials

```bash
# Generate PDF certificate
GET /proxy/credentials/pdf/{poa_id}

# Record credential presentation
POST /proxy/credentials/present
{
  "poa_id": 1,
  "presented_to": "AT&T Customer Service",
  "method": "PDF"
}
```

---

## 🔒 Security Features

### Encryption
- **Fernet**: Symmetric encryption for OAuth tokens
- **HMAC-SHA256**: Cryptographic signatures for audit logs
- **Environment Variables**: Encryption keys stored securely

### Authentication
- **2FA**: Time-based OTP (TOTP) with 5-minute window
- **Liveness Detection**: Face/voice verification for high-value transactions
- **Multi-Channel Notifications**: Push, SMS, Email

### Audit Trail
- **Immutable Logs**: Cannot be altered after creation
- **Cryptographic Signatures**: HMAC-SHA256 for legal verification
- **PDF Export**: Legal-grade documentation

---

## 🚀 Quick Start

### 1. Set Environment Variables

```bash
# Required
export VAULT_ENCRYPTION_KEY="<fernet_key>"
export SECRET_KEY="<hmac_secret>"

# Optional (for notifications)
export TRUSTED_ADVOCATE_EMAIL="advocate@example.com"
export TRUSTED_ADVOCATE_PHONE="+1234567890"
export TWILIO_ACCOUNT_SID="<twilio_sid>"
export TWILIO_AUTH_TOKEN="<twilio_token>"
export SENDGRID_API_KEY="<sendgrid_key>"
```

### 2. Run Database Migration

```bash
# Create Module C tables
alembic revision --autogenerate -m "Add Module C tables"
alembic upgrade head
```

### 3. Start Backend

```bash
python main.py
# Module C endpoints available at http://localhost:8000/proxy/*
```

### 4. Test the Flow

```bash
# 1. Create Smart POA
curl -X POST http://localhost:8000/proxy/vault/poa \
  -H "Content-Type: application/json" \
  -d '{
    "senior_id": "senior_001",
    "agent_id": "ai_agent",
    "scope": "utilities",
    "spend_limit": 100.00,
    "expiry_days": 30
  }'

# 2. Validate request (within limits)
curl -X POST http://localhost:8000/proxy/tokens/validate \
  -H "Content-Type: application/json" \
  -d '{
    "poa_id": 1,
    "service_name": "Water Bill",
    "amount": 75.00
  }'
# Response: {"authorized": true, "decision": "ALLOWED"}

# 3. Trigger break-glass (exceed limit)
curl -X POST http://localhost:8000/proxy/tokens/validate \
  -H "Content-Type: application/json" \
  -d '{
    "poa_id": 1,
    "service_name": "Water Bill",
    "amount": 150.00
  }'
# Response: {"decision": "BREAK_GLASS", "break_glass_event_id": 1}

# 4. Verify 2FA code (check console for code)
curl -X POST http://localhost:8000/proxy/break-glass/verify-2fa \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": 1,
    "code": "123456"
  }'
```

---

## 📊 Database Schema

### SmartPOA
- Granular permissions with scope and limits
- Time-limited credentials
- Revocation support

### EncryptedToken
- Fernet-encrypted OAuth tokens
- Service-specific storage
- Expiration tracking

### AuditLog
- Cryptographically signed records
- Complete action history
- Legal-grade evidence

### BreakGlassEvent
- Violation tracking
- 2FA verification
- Liveness detection
- Approval workflow

### CredentialPresentation
- Track credential usage
- QR code verification
- Document hashing

---

## 🎓 Use Cases

### 1. Utility Bill Negotiation
```python
# POA: "Can negotiate utility bills, max $100"
# Agent tries to pay $75 water bill → ALLOWED
# Agent tries to pay $150 electric bill → BREAK_GLASS
```

### 2. Subscription Management
```python
# POA: "Can cancel subscriptions, max $50"
# Agent cancels $10 Netflix → ALLOWED
# Agent tries to access banking → BLOCKED (scope violation)
```

### 3. Healthcare Coordination
```python
# POA: "Can schedule appointments, no payments"
# Agent books doctor appointment → ALLOWED
# Agent tries to pay $200 bill → BREAK_GLASS
```

---

## 🔮 Future Enhancements

- [ ] Blockchain integration for immutable audit trail
- [ ] Real liveness detection (AWS Rekognition, Azure Face API)
- [ ] Multi-signature approvals
- [ ] Smart contract automation
- [ ] Machine learning for anomaly detection
- [ ] Integration with real Open Banking APIs (Plaid, Salt Edge)

---

## 📄 License

Part of Project Aegis - Cognitive Fiduciary System

---

## 🆘 Support

For questions or issues, refer to the main Project Aegis documentation.
