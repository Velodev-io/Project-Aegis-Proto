"""
Module C: The Proxy - Database Models
Digital POA Vault, Token Storage, Audit Trail, and Break-Glass Events
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from models import Base


class SmartPOA(Base):
    """
    Smart Power of Attorney - Granular, time-limited permissions
    
    Example: "Agent can negotiate AT&T bill, max $100, expires in 30 days"
    vs traditional "Agent can do everything forever"
    """
    __tablename__ = "smart_poas"
    
    id = Column(Integer, primary_key=True, index=True)
    senior_id = Column(String(100), nullable=False, index=True)  # Who is granting permission
    agent_id = Column(String(100), nullable=False, index=True)    # Who can act (AI/Family)
    
    # Granular Permissions
    scope = Column(String(50), nullable=False)  # 'utilities', 'banking', 'healthcare', 'subscriptions'
    specific_services = Column(JSON, nullable=True)  # ['AT&T', 'Water Bill'] or None for all in scope
    spend_limit = Column(Float, nullable=False)  # Maximum transaction amount
    
    # Time Constraints
    expiry_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_by = Column(String(100), nullable=True)  # Who created this POA
    revocation_reason = Column(Text, nullable=True)
    
    # Relationships
    tokens = relationship("EncryptedToken", back_populates="poa", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="poa", cascade="all, delete-orphan")
    
    def is_valid(self) -> bool:
        """Check if POA is currently valid"""
        return (
            self.is_active and
            self.revoked_at is None and
            self.expiry_date > datetime.utcnow()
        )
    
    def is_within_scope(self, service_name: str) -> bool:
        """Check if service is within POA scope"""
        if not self.specific_services:
            return True  # All services in scope allowed
        return service_name in self.specific_services
    
    def is_within_limit(self, amount: float) -> bool:
        """Check if amount is within spend limit"""
        return amount <= self.spend_limit


class EncryptedToken(Base):
    """
    Encrypted OAuth tokens for delegated access
    Uses Fernet symmetric encryption
    """
    __tablename__ = "encrypted_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    poa_id = Column(Integer, ForeignKey("smart_poas.id"), nullable=False)
    
    service_name = Column(String(100), nullable=False)  # 'plaid', 'salt_edge', 'netflix', etc.
    token_type = Column(String(20), nullable=False)  # 'access', 'refresh'
    encrypted_token = Column(Text, nullable=False)  # Fernet encrypted
    
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    
    # Relationships
    poa = relationship("SmartPOA", back_populates="tokens")


class AuditLog(Base):
    """
    Fiduciary Proof - Immutable audit trail with cryptographic signatures
    Legal-grade evidence for authorities
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    poa_id = Column(Integer, ForeignKey("smart_poas.id"), nullable=False)
    
    # Action Details
    action_type = Column(String(50), nullable=False)  # 'TOKEN_USE', 'TRANSACTION', 'POA_CREATE', etc.
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Request Information
    request_details = Column(JSON, nullable=False)  # Full request context
    service_name = Column(String(100), nullable=True)
    amount = Column(Float, nullable=True)
    
    # Decision
    decision = Column(String(20), nullable=False)  # 'ALLOWED', 'BLOCKED', 'BREAK_GLASS'
    reasoning = Column(Text, nullable=False)
    
    # Cryptographic Proof
    signature = Column(String(256), nullable=False)  # HMAC-SHA256 signature
    signature_verified = Column(Boolean, default=False)
    
    # Advocate Notification
    advocate_notified = Column(Boolean, default=False)
    advocate_notification_time = Column(DateTime, nullable=True)
    override_code = Column(String(10), nullable=True)  # 2FA code if break-glass
    
    # Relationships
    poa = relationship("SmartPOA", back_populates="audit_logs")
    break_glass_event = relationship("BreakGlassEvent", back_populates="audit_log", uselist=False)


class BreakGlassEvent(Base):
    """
    Break-Glass Protocol Events
    Triggered when limits are exceeded or scope is violated
    """
    __tablename__ = "break_glass_events"
    
    id = Column(Integer, primary_key=True, index=True)
    audit_log_id = Column(Integer, ForeignKey("audit_logs.id"), nullable=False, unique=True)
    
    # Trigger Information
    trigger_reason = Column(String(100), nullable=False)  # 'SPEND_LIMIT_EXCEEDED', 'SCOPE_VIOLATION'
    trigger_details = Column(JSON, nullable=False)
    
    # Status
    status = Column(String(20), default='PENDING')  # 'PENDING', 'APPROVED', 'DENIED', 'EXPIRED'
    
    # Advocate Information
    advocate_id = Column(String(100), nullable=False)
    verification_method = Column(String(50), nullable=True)  # '2FA', 'LIVENESS', 'BOTH'
    
    # 2FA
    two_fa_code = Column(String(10), nullable=True)
    two_fa_sent_at = Column(DateTime, nullable=True)
    two_fa_verified_at = Column(DateTime, nullable=True)
    
    # Liveness Detection
    liveness_required = Column(Boolean, default=False)
    liveness_verified = Column(Boolean, default=False)
    liveness_verified_at = Column(DateTime, nullable=True)
    liveness_data = Column(JSON, nullable=True)  # Face/voice verification data
    
    # Resolution
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(String(100), nullable=True)
    denied_at = Column(DateTime, nullable=True)
    denied_by = Column(String(100), nullable=True)
    denial_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=1))
    
    # Relationships
    audit_log = relationship("AuditLog", back_populates="break_glass_event")
    
    def is_expired(self) -> bool:
        """Check if break-glass event has expired"""
        return datetime.utcnow() > self.expires_at
    
    def can_approve(self) -> bool:
        """Check if event can be approved"""
        return (
            self.status == 'PENDING' and
            not self.is_expired() and
            (not self.liveness_required or self.liveness_verified)
        )


class CredentialPresentation(Base):
    """
    Track when and where POA credentials were presented
    For audit trail of credential usage
    """
    __tablename__ = "credential_presentations"
    
    id = Column(Integer, primary_key=True, index=True)
    poa_id = Column(Integer, ForeignKey("smart_poas.id"), nullable=False)
    
    presented_to = Column(String(200), nullable=False)  # Company/service name
    presentation_method = Column(String(50), nullable=False)  # 'PDF', 'API', 'EMAIL'
    presented_at = Column(DateTime, default=datetime.utcnow)
    
    # Verification
    verification_code = Column(String(100), nullable=True)  # QR code or verification token
    verified_by_recipient = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    
    # Document
    document_hash = Column(String(256), nullable=True)  # SHA256 of presented document
    document_path = Column(String(500), nullable=True)  # Path to stored PDF
