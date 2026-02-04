"""
Module C: The Proxy - Digital POA Vault
Encryption, Token Management, and Credential Presentation
"""
import os
import hashlib
import hmac
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from cryptography.fernet import Fernet
from sqlalchemy.orm import Session
import qrcode
from io import BytesIO
import base64

from proxy_models import SmartPOA, EncryptedToken, AuditLog, CredentialPresentation


class VaultEncryption:
    """
    Fernet symmetric encryption for OAuth tokens
    Uses environment variable for encryption key
    """
    
    def __init__(self):
        # Get encryption key from environment or generate new one
        key = os.getenv("VAULT_ENCRYPTION_KEY")
        if not key:
            # Generate new key for development
            key = Fernet.generate_key().decode()
            print(f"⚠️  Generated new encryption key. Set VAULT_ENCRYPTION_KEY={key}")
        else:
            key = key.encode() if isinstance(key, str) else key
        
        self.cipher = Fernet(key)
        self.secret_key = os.getenv("SECRET_KEY", "aegis-secret-key-change-in-production")
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt OAuth token using Fernet"""
        return self.cipher.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt OAuth token"""
        return self.cipher.decrypt(encrypted_token.encode()).decode()
    
    def sign_data(self, data: Dict[str, Any]) -> str:
        """Create HMAC-SHA256 signature for audit logs"""
        message = json.dumps(data, sort_keys=True).encode()
        signature = hmac.new(
            self.secret_key.encode(),
            message,
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def verify_signature(self, data: Dict[str, Any], signature: str) -> bool:
        """Verify HMAC signature"""
        expected_signature = self.sign_data(data)
        return hmac.compare_digest(expected_signature, signature)


class SmartPOAManager:
    """
    Manage Smart Power of Attorney creation, validation, and revocation
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.encryption = VaultEncryption()
    
    def create_poa(
        self,
        senior_id: str,
        agent_id: str,
        scope: str,
        spend_limit: float,
        expiry_days: int = 30,
        specific_services: Optional[List[str]] = None,
        created_by: Optional[str] = None
    ) -> SmartPOA:
        """
        Create a new Smart POA with granular permissions
        
        Args:
            senior_id: ID of the senior granting permission
            agent_id: ID of the agent (AI/family member)
            scope: Permission scope ('utilities', 'banking', 'healthcare', 'subscriptions')
            spend_limit: Maximum transaction amount
            expiry_days: Days until POA expires
            specific_services: Optional list of specific services (e.g., ['AT&T', 'Water Bill'])
            created_by: Who created this POA
        """
        poa = SmartPOA(
            senior_id=senior_id,
            agent_id=agent_id,
            scope=scope,
            spend_limit=spend_limit,
            expiry_date=datetime.utcnow() + timedelta(days=expiry_days),
            specific_services=specific_services,
            created_by=created_by,
            is_active=True
        )
        
        self.db.add(poa)
        self.db.commit()
        self.db.refresh(poa)
        
        # Create audit log
        self._create_audit_log(
            poa_id=poa.id,
            action_type="POA_CREATED",
            decision="ALLOWED",
            reasoning=f"Smart POA created for {scope} with ${spend_limit} limit",
            request_details={
                "senior_id": senior_id,
                "agent_id": agent_id,
                "scope": scope,
                "spend_limit": spend_limit,
                "expiry_days": expiry_days
            }
        )
        
        return poa
    
    def get_poa(self, poa_id: int) -> Optional[SmartPOA]:
        """Retrieve POA by ID"""
        return self.db.query(SmartPOA).filter(SmartPOA.id == poa_id).first()
    
    def get_poas_by_senior(self, senior_id: str, active_only: bool = True) -> List[SmartPOA]:
        """Get all POAs for a senior"""
        query = self.db.query(SmartPOA).filter(SmartPOA.senior_id == senior_id)
        if active_only:
            query = query.filter(
                SmartPOA.is_active == True,
                SmartPOA.revoked_at == None,
                SmartPOA.expiry_date > datetime.utcnow()
            )
        return query.all()
    
    def revoke_poa(self, poa_id: int, reason: str, revoked_by: str) -> bool:
        """Revoke a POA"""
        poa = self.get_poa(poa_id)
        if not poa:
            return False
        
        poa.is_active = False
        poa.revoked_at = datetime.utcnow()
        poa.revocation_reason = reason
        
        self.db.commit()
        
        # Create audit log
        self._create_audit_log(
            poa_id=poa.id,
            action_type="POA_REVOKED",
            decision="ALLOWED",
            reasoning=f"POA revoked: {reason}",
            request_details={
                "revoked_by": revoked_by,
                "reason": reason
            }
        )
        
        return True
    
    def store_oauth_token(
        self,
        poa_id: int,
        service_name: str,
        token: str,
        token_type: str = "access",
        expires_in_seconds: Optional[int] = None
    ) -> EncryptedToken:
        """Store encrypted OAuth token"""
        encrypted = self.encryption.encrypt_token(token)
        
        expires_at = None
        if expires_in_seconds:
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in_seconds)
        
        token_record = EncryptedToken(
            poa_id=poa_id,
            service_name=service_name,
            token_type=token_type,
            encrypted_token=encrypted,
            expires_at=expires_at
        )
        
        self.db.add(token_record)
        self.db.commit()
        self.db.refresh(token_record)
        
        return token_record
    
    def get_decrypted_token(self, token_id: int) -> Optional[str]:
        """Retrieve and decrypt OAuth token"""
        token_record = self.db.query(EncryptedToken).filter(
            EncryptedToken.id == token_id
        ).first()
        
        if not token_record:
            return None
        
        # Check if token is expired
        if token_record.expires_at and token_record.expires_at < datetime.utcnow():
            return None
        
        # Update last used
        token_record.last_used = datetime.utcnow()
        self.db.commit()
        
        return self.encryption.decrypt_token(token_record.encrypted_token)
    
    def _create_audit_log(
        self,
        poa_id: int,
        action_type: str,
        decision: str,
        reasoning: str,
        request_details: Dict[str, Any],
        service_name: Optional[str] = None,
        amount: Optional[float] = None
    ) -> AuditLog:
        """Create signed audit log entry"""
        # Create signature
        signature_data = {
            "poa_id": poa_id,
            "action_type": action_type,
            "timestamp": datetime.utcnow().isoformat(),
            "decision": decision,
            "request_details": request_details
        }
        signature = self.encryption.sign_data(signature_data)
        
        audit_log = AuditLog(
            poa_id=poa_id,
            action_type=action_type,
            decision=decision,
            reasoning=reasoning,
            request_details=request_details,
            service_name=service_name,
            amount=amount,
            signature=signature,
            signature_verified=True
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log


class TokenGatekeeper:
    """
    Validate requests against POA scope and limits
    Block unauthorized access
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.poa_manager = SmartPOAManager(db)
    
    def validate_request(
        self,
        poa_id: int,
        service_name: str,
        amount: Optional[float] = None,
        action: str = "access"
    ) -> Dict[str, Any]:
        """
        Validate if request is authorized by POA
        
        Returns:
            {
                "authorized": bool,
                "decision": "ALLOWED" | "BLOCKED" | "BREAK_GLASS",
                "reasoning": str,
                "poa": SmartPOA or None
            }
        """
        poa = self.poa_manager.get_poa(poa_id)
        
        if not poa:
            return {
                "authorized": False,
                "decision": "BLOCKED",
                "reasoning": "POA not found",
                "poa": None
            }
        
        # Check if POA is valid
        if not poa.is_valid():
            return {
                "authorized": False,
                "decision": "BLOCKED",
                "reasoning": "POA is expired or revoked",
                "poa": poa
            }
        
        # Check scope
        if not poa.is_within_scope(service_name):
            # Create audit log for blocked request
            self.poa_manager._create_audit_log(
                poa_id=poa.id,
                action_type="SCOPE_VIOLATION",
                decision="BLOCKED",
                reasoning=f"Service '{service_name}' not in POA scope '{poa.scope}'",
                request_details={
                    "service_name": service_name,
                    "action": action,
                    "allowed_services": poa.specific_services
                },
                service_name=service_name
            )
            
            return {
                "authorized": False,
                "decision": "BLOCKED",
                "reasoning": f"Service '{service_name}' not authorized. POA scope: {poa.scope}",
                "poa": poa,
                "violation_type": "SCOPE"
            }
        
        # Check spend limit if amount provided
        if amount is not None:
            if not poa.is_within_limit(amount):
                # Trigger break-glass protocol
                audit_log = self.poa_manager._create_audit_log(
                    poa_id=poa.id,
                    action_type="SPEND_LIMIT_EXCEEDED",
                    decision="BREAK_GLASS",
                    reasoning=f"Amount ${amount} exceeds limit ${poa.spend_limit}",
                    request_details={
                        "service_name": service_name,
                        "amount": amount,
                        "spend_limit": poa.spend_limit,
                        "action": action
                    },
                    service_name=service_name,
                    amount=amount
                )
                
                return {
                    "authorized": False,
                    "decision": "BREAK_GLASS",
                    "reasoning": f"Amount ${amount} exceeds POA limit ${poa.spend_limit}. Break-glass protocol triggered.",
                    "poa": poa,
                    "violation_type": "SPEND_LIMIT",
                    "audit_log_id": audit_log.id
                }
        
        # Request is authorized
        self.poa_manager._create_audit_log(
            poa_id=poa.id,
            action_type=f"REQUEST_{action.upper()}",
            decision="ALLOWED",
            reasoning=f"Request authorized for {service_name}",
            request_details={
                "service_name": service_name,
                "amount": amount,
                "action": action
            },
            service_name=service_name,
            amount=amount
        )
        
        return {
            "authorized": True,
            "decision": "ALLOWED",
            "reasoning": "Request within POA scope and limits",
            "poa": poa
        }


class CredentialPresenter:
    """
    Generate and present POA credentials
    Creates PDF certificates with QR codes for verification
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.encryption = VaultEncryption()
    
    def generate_qr_code(self, data: str) -> str:
        """Generate QR code as base64 image"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def generate_verification_code(self, poa_id: int) -> str:
        """Generate verification code for POA"""
        data = {
            "poa_id": poa_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        return self.encryption.sign_data(data)[:16]  # First 16 chars of signature
    
    def record_presentation(
        self,
        poa_id: int,
        presented_to: str,
        presentation_method: str = "PDF"
    ) -> CredentialPresentation:
        """Record when credentials were presented"""
        verification_code = self.generate_verification_code(poa_id)
        
        presentation = CredentialPresentation(
            poa_id=poa_id,
            presented_to=presented_to,
            presentation_method=presentation_method,
            verification_code=verification_code
        )
        
        self.db.add(presentation)
        self.db.commit()
        self.db.refresh(presentation)
        
        return presentation
