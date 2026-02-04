"""
Module C: The Proxy - Break-Glass Protocol
2FA, Liveness Detection, and Push Notifications
"""
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import pyotp
import hashlib

from proxy_models import BreakGlassEvent, AuditLog, SmartPOA


class TwoFactorAuth:
    """
    Generate and verify 2FA codes
    Uses TOTP (Time-based One-Time Password)
    """
    
    def __init__(self):
        # Use secret key from environment or generate
        self.secret = os.getenv("TOTP_SECRET", pyotp.random_base32())
    
    def generate_code(self) -> str:
        """Generate 6-digit 2FA code"""
        totp = pyotp.TOTP(self.secret, interval=300)  # 5-minute window
        return totp.now()
    
    def verify_code(self, code: str) -> bool:
        """Verify 2FA code (allows 5-minute window)"""
        totp = pyotp.TOTP(self.secret, interval=300)
        return totp.verify(code, valid_window=1)
    
    def generate_backup_code(self) -> str:
        """Generate one-time backup code"""
        return secrets.token_hex(4).upper()  # 8-character hex code


class LivenessVerification:
    """
    Mock liveness detection for face/voice verification
    In production, integrate with services like:
    - AWS Rekognition
    - Azure Face API
    - Onfido
    """
    
    def __init__(self):
        self.verification_threshold = 0.85  # 85% confidence required
    
    def verify_face(self, image_data: bytes, reference_image: bytes) -> Dict[str, Any]:
        """
        Mock face verification
        
        In production, this would:
        1. Extract face embeddings from both images
        2. Compare similarity
        3. Check for liveness (not a photo of photo)
        """
        # Mock implementation
        confidence = 0.92  # Simulated confidence score
        
        return {
            "verified": confidence >= self.verification_threshold,
            "confidence": confidence,
            "liveness_detected": True,
            "method": "face_recognition",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def verify_voice(self, audio_data: bytes, reference_audio: bytes) -> Dict[str, Any]:
        """
        Mock voice verification
        
        In production, this would:
        1. Extract voice biometrics
        2. Compare with reference
        3. Check for liveness (not a recording)
        """
        # Mock implementation
        confidence = 0.89
        
        return {
            "verified": confidence >= self.verification_threshold,
            "confidence": confidence,
            "liveness_detected": True,
            "method": "voice_recognition",
            "timestamp": datetime.utcnow().isoformat()
        }


class PushNotificationService:
    """
    Send push notifications to Trusted Advocate
    Mock implementation - in production use:
    - Firebase Cloud Messaging
    - Apple Push Notification Service
    - Twilio (SMS)
    - SendGrid (Email)
    """
    
    def __init__(self):
        self.firebase_credentials = os.getenv("FIREBASE_CREDENTIALS_PATH")
        self.twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.sendgrid_key = os.getenv("SENDGRID_API_KEY")
    
    def send_push(
        self,
        advocate_id: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send push notification
        
        In production, this would use Firebase/APNS
        """
        print(f"📱 PUSH NOTIFICATION to {advocate_id}")
        print(f"   Title: {title}")
        print(f"   Message: {message}")
        
        return {
            "sent": True,
            "method": "push",
            "advocate_id": advocate_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def send_sms(self, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Send SMS via Twilio
        
        In production, this would use Twilio API
        """
        print(f"📱 SMS to {phone_number}")
        print(f"   Message: {message}")
        
        return {
            "sent": True,
            "method": "sms",
            "phone": phone_number,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def send_email(
        self,
        email: str,
        subject: str,
        body: str,
        html: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send email via SendGrid
        
        In production, this would use SendGrid API
        """
        print(f"📧 EMAIL to {email}")
        print(f"   Subject: {subject}")
        print(f"   Body: {body[:100]}...")
        
        return {
            "sent": True,
            "method": "email",
            "email": email,
            "timestamp": datetime.utcnow().isoformat()
        }


class BreakGlassMonitor:
    """
    Monitor executor agent actions and trigger break-glass protocol
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.two_fa = TwoFactorAuth()
        self.liveness = LivenessVerification()
        self.notifications = PushNotificationService()
    
    def trigger_break_glass(
        self,
        audit_log_id: int,
        trigger_reason: str,
        trigger_details: Dict[str, Any],
        advocate_id: str,
        require_liveness: bool = False
    ) -> BreakGlassEvent:
        """
        Trigger break-glass protocol
        
        Workflow:
        1. Create break-glass event
        2. Generate 2FA code
        3. Send notifications to Trusted Advocate
        4. Wait for verification
        """
        # Generate 2FA code
        two_fa_code = self.two_fa.generate_code()
        
        # Create break-glass event
        event = BreakGlassEvent(
            audit_log_id=audit_log_id,
            trigger_reason=trigger_reason,
            trigger_details=trigger_details,
            advocate_id=advocate_id,
            verification_method="2FA" if not require_liveness else "BOTH",
            two_fa_code=two_fa_code,
            two_fa_sent_at=datetime.utcnow(),
            liveness_required=require_liveness,
            status="PENDING"
        )
        
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        
        # Send notifications
        self._send_break_glass_notifications(event, two_fa_code)
        
        return event
    
    def _send_break_glass_notifications(self, event: BreakGlassEvent, two_fa_code: str):
        """Send all notifications for break-glass event"""
        # Get POA details from audit log
        audit_log = self.db.query(AuditLog).filter(
            AuditLog.id == event.audit_log_id
        ).first()
        
        if not audit_log:
            return
        
        poa = self.db.query(SmartPOA).filter(SmartPOA.id == audit_log.poa_id).first()
        
        # Prepare message
        title = "🚨 Break-Glass Protocol Triggered"
        message = f"""
URGENT: Authorization required for {poa.senior_id}

Reason: {event.trigger_reason}
Amount: ${audit_log.amount if audit_log.amount else 'N/A'}
Service: {audit_log.service_name or 'N/A'}

Your 2FA code: {two_fa_code}
(Valid for 5 minutes)

Please review and approve/deny this request.
        """.strip()
        
        # Send push notification
        self.notifications.send_push(
            advocate_id=event.advocate_id,
            title=title,
            message=message,
            data={
                "event_id": event.id,
                "poa_id": audit_log.poa_id,
                "two_fa_code": two_fa_code
            }
        )
        
        # Send SMS if configured
        advocate_phone = os.getenv("TRUSTED_ADVOCATE_PHONE")
        if advocate_phone:
            self.notifications.send_sms(
                phone_number=advocate_phone,
                message=f"{title}\n\n{message}"
            )
        
        # Send email if configured
        advocate_email = os.getenv("TRUSTED_ADVOCATE_EMAIL")
        if advocate_email:
            self.notifications.send_email(
                email=advocate_email,
                subject=title,
                body=message
            )
    
    def verify_2fa(self, event_id: int, code: str) -> Dict[str, Any]:
        """Verify 2FA code for break-glass event"""
        event = self.db.query(BreakGlassEvent).filter(
            BreakGlassEvent.id == event_id
        ).first()
        
        if not event:
            return {"verified": False, "error": "Event not found"}
        
        if event.status != "PENDING":
            return {"verified": False, "error": f"Event status is {event.status}"}
        
        if event.is_expired():
            event.status = "EXPIRED"
            self.db.commit()
            return {"verified": False, "error": "Event expired"}
        
        # Verify code
        if code == event.two_fa_code or self.two_fa.verify_code(code):
            event.two_fa_verified_at = datetime.utcnow()
            
            # If liveness not required, approve immediately
            if not event.liveness_required:
                event.status = "APPROVED"
                event.approved_at = datetime.utcnow()
                event.approved_by = event.advocate_id
            
            self.db.commit()
            
            return {
                "verified": True,
                "liveness_required": event.liveness_required,
                "status": event.status
            }
        
        return {"verified": False, "error": "Invalid 2FA code"}
    
    def verify_liveness(
        self,
        event_id: int,
        verification_data: Dict[str, Any],
        method: str = "face"
    ) -> Dict[str, Any]:
        """Verify liveness for break-glass event"""
        event = self.db.query(BreakGlassEvent).filter(
            BreakGlassEvent.id == event_id
        ).first()
        
        if not event:
            return {"verified": False, "error": "Event not found"}
        
        if not event.liveness_required:
            return {"verified": False, "error": "Liveness not required"}
        
        if not event.two_fa_verified_at:
            return {"verified": False, "error": "2FA verification required first"}
        
        # Mock liveness verification
        if method == "face":
            result = self.liveness.verify_face(b"", b"")
        else:
            result = self.liveness.verify_voice(b"", b"")
        
        if result["verified"]:
            event.liveness_verified = True
            event.liveness_verified_at = datetime.utcnow()
            event.liveness_data = result
            event.status = "APPROVED"
            event.approved_at = datetime.utcnow()
            event.approved_by = event.advocate_id
            
            self.db.commit()
        
        return result
    
    def deny_break_glass(
        self,
        event_id: int,
        denied_by: str,
        reason: str
    ) -> Dict[str, Any]:
        """Deny break-glass request"""
        event = self.db.query(BreakGlassEvent).filter(
            BreakGlassEvent.id == event_id
        ).first()
        
        if not event:
            return {"success": False, "error": "Event not found"}
        
        event.status = "DENIED"
        event.denied_at = datetime.utcnow()
        event.denied_by = denied_by
        event.denial_reason = reason
        
        self.db.commit()
        
        return {"success": True, "status": "DENIED"}
    
    def get_pending_events(self, advocate_id: Optional[str] = None) -> list:
        """Get all pending break-glass events"""
        query = self.db.query(BreakGlassEvent).filter(
            BreakGlassEvent.status == "PENDING"
        )
        
        if advocate_id:
            query = query.filter(BreakGlassEvent.advocate_id == advocate_id)
        
        return query.all()
