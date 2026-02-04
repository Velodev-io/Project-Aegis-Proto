"""
SQLAlchemy Models for Project Aegis Trust Vault
Blockchain-ready audit trail for all security events
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class SecurityLog(Base):
    """
    Immutable security event log for blockchain audit trail
    Stores all intercepted calls and blocked transactions
    """
    __tablename__ = "security_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # 'SCAM_CALL', 'TRANSACTION'
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Scam Call Fields
    transcript = Column(Text, nullable=True)
    fraud_score = Column(Float, nullable=True)
    scam_indicators = Column(JSON, nullable=True)  # List of detected indicators
    action_taken = Column(String(50), nullable=True)  # 'INTERVENE_AND_BLOCK', 'ACTIVATE_ANSWER_BOT', 'ALLOW'
    
    # Transaction Fields
    transaction_amount = Column(Float, nullable=True)
    transaction_time = Column(DateTime, nullable=True)
    transaction_category = Column(String(100), nullable=True)
    merchant = Column(String(200), nullable=True)
    risk_level = Column(String(20), nullable=True)  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    approval_status = Column(String(50), nullable=True)  # 'APPROVED', 'PENDING', 'REJECTED'
    
    # Common Fields
    user_id = Column(String(100), nullable=True, index=True)
    reasoning = Column(Text, nullable=True)
    event_metadata = Column(JSON, nullable=True)  # Additional context (renamed from metadata)
    blockchain_hash = Column(String(256), nullable=True)  # Future: Hash for blockchain
    
    # Advocate Notification
    advocate_notified = Column(Boolean, default=False)
    advocate_notification_time = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<SecurityLog(id={self.id}, type={self.event_type}, timestamp={self.timestamp})>"


class PendingApproval(Base):
    """
    Pending approvals requiring Trusted Advocate review
    """
    __tablename__ = "pending_approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    security_log_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)
    reviewer_id = Column(String(100), nullable=True)
    decision = Column(String(20), nullable=True)  # 'APPROVED', 'REJECTED'
    reviewer_notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<PendingApproval(id={self.id}, log_id={self.security_log_id}, decision={self.decision})>"
