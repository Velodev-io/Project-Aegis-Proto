"""
Trusted Advocate Notification System
Sends alerts to caregivers/advocates for pending approvals
"""
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TrustedAdvocateNotifier:
    """
    Notification system for alerting Trusted Advocates
    Supports multiple notification channels (webhook, email, SMS, push)
    """
    
    def __init__(self, webhook_url: Optional[str] = None):
        """
        Initialize the notifier
        
        Args:
            webhook_url: Optional webhook URL for notifications
        """
        self.webhook_url = webhook_url
    
    async def notify_scam_detected(
        self,
        user_id: str,
        fraud_score: float,
        action: str,
        reasoning: str,
        transcript: str
    ) -> Dict:
        """
        Notify advocate of detected scam call
        
        Args:
            user_id: Protected user ID
            fraud_score: Fraud score (0-100)
            action: Action taken
            reasoning: Analysis reasoning
            transcript: Call transcript
            
        Returns:
            Notification result
        """
        notification = {
            "type": "SCAM_DETECTED",
            "severity": "CRITICAL" if fraud_score > 80 else "HIGH",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "details": {
                "fraud_score": fraud_score,
                "action_taken": action,
                "reasoning": reasoning,
                "transcript_preview": transcript[:200] + "..." if len(transcript) > 200 else transcript
            }
        }
        
        return await self._send_notification(notification)
    
    async def notify_transaction_pending(
        self,
        user_id: str,
        amount: float,
        merchant: str,
        category: str,
        risk_level: str,
        reasoning: str,
        approval_id: int
    ) -> Dict:
        """
        Notify advocate of pending transaction approval
        
        Args:
            user_id: Protected user ID
            amount: Transaction amount
            merchant: Merchant name
            category: Transaction category
            risk_level: Risk assessment
            reasoning: Analysis reasoning
            approval_id: Pending approval ID
            
        Returns:
            Notification result
        """
        notification = {
            "type": "TRANSACTION_APPROVAL_REQUIRED",
            "severity": "CRITICAL" if risk_level == "CRITICAL" else "MEDIUM",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "approval_id": approval_id,
            "details": {
                "amount": amount,
                "merchant": merchant,
                "category": category,
                "risk_level": risk_level,
                "reasoning": reasoning
            },
            "actions": {
                "approve_url": f"/api/approvals/{approval_id}/approve",
                "reject_url": f"/api/approvals/{approval_id}/reject"
            }
        }
        
        return await self._send_notification(notification)
    
    async def _send_notification(self, notification: Dict) -> Dict:
        """
        Send notification through configured channels
        
        Args:
            notification: Notification payload
            
        Returns:
            Delivery result
        """
        # Mock implementation - logs to console
        # In production, this would send to webhook, email, SMS, push notification
        
        logger.info("=" * 80)
        logger.info("🚨 TRUSTED ADVOCATE NOTIFICATION")
        logger.info("=" * 80)
        logger.info(f"Type: {notification['type']}")
        logger.info(f"Severity: {notification['severity']}")
        logger.info(f"Timestamp: {notification['timestamp']}")
        logger.info(f"User: {notification.get('user_id', 'N/A')}")
        logger.info("-" * 80)
        logger.info("Details:")
        for key, value in notification.get('details', {}).items():
            logger.info(f"  {key}: {value}")
        logger.info("=" * 80)
        
        # Simulate webhook call
        if self.webhook_url:
            logger.info(f"📡 Webhook notification sent to: {self.webhook_url}")
            # TODO: Implement actual HTTP POST to webhook
        
        return {
            "success": True,
            "notification_id": f"notif_{int(datetime.utcnow().timestamp())}",
            "channels": ["LOG", "WEBHOOK"] if self.webhook_url else ["LOG"],
            "timestamp": datetime.utcnow().isoformat()
        }
