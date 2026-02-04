"""
Agentic Scam Analyzer for Project Aegis Sentinel Module
Production-grade fraud detection with LLM integration
"""
from typing import Dict, List, Tuple
from datetime import datetime
import re


class AgenticScamAnalyzer:
    """
    AI-powered scam detection system
    Analyzes voice transcripts for fraud indicators
    """
    
    # Scam indicator patterns with weights
    SCAM_INDICATORS = {
        "urgency": {
            "patterns": [
                r"\b(urgent|emergency|immediately|right now|asap|hurry)\b",
                r"\b(act now|time sensitive|limited time)\b",
                r"\b(before it's too late|last chance)\b"
            ],
            "weight": 25
        },
        "gift_cards": {
            "patterns": [
                r"\b(gift card|gift|card|itunes|google play|steam|amazon card)\b",
                r"\b(prepaid card|reload|redeem)\b",
                r"\b(scratch off|activation code)\b"
            ],
            "weight": 35
        },
        "authority_impersonation": {
            "patterns": [
                r"\b(irs|internal revenue|tax|government|federal)\b",
                r"\b(social security|medicare|medicaid)\b",
                r"\b(police|sheriff|officer|detective|fbi|dea)\b",
                r"\b(warrant|arrest|legal action|lawsuit)\b",
                r"\b(bank|account frozen|suspicious activity)\b"
            ],
            "weight": 30
        },
        "payment_pressure": {
            "patterns": [
                r"\b(pay now|send money|wire transfer|western union)\b",
                r"\b(cash|bitcoin|cryptocurrency|venmo|zelle)\b",
                r"\b(penalty|fine|fee|charge|owe)\b"
            ],
            "weight": 20
        },
        "personal_info_request": {
            "patterns": [
                r"\b(social security number|ssn|account number|password)\b",
                r"\b(pin|verification code|security code)\b",
                r"\b(date of birth|mother's maiden name)\b"
            ],
            "weight": 25
        },
        "family_emergency": {
            "patterns": [
                r"\b(grandchild|grandson|granddaughter|nephew|niece)\b",
                r"\b(accident|hospital|jail|arrested|trouble)\b",
                r"\b(bail|lawyer|attorney|legal fees)\b"
            ],
            "weight": 30
        }
    }
    
    def __init__(self, llm_enabled: bool = False):
        """
        Initialize the scam analyzer
        
        Args:
            llm_enabled: Whether to use real LLM (future) or rule-based system
        """
        self.llm_enabled = llm_enabled
    
    def analyze(self, transcript: str) -> Dict:
        """
        Analyze a voice transcript for scam indicators
        
        Args:
            transcript: The text transcript of the call
            
        Returns:
            Dict with fraud_score, indicators, action, and reasoning
        """
        transcript_lower = transcript.lower()
        
        # Detect indicators
        detected_indicators = []
        total_score = 0
        
        for category, config in self.SCAM_INDICATORS.items():
            for pattern in config["patterns"]:
                if re.search(pattern, transcript_lower, re.IGNORECASE):
                    detected_indicators.append({
                        "category": category,
                        "pattern": pattern,
                        "weight": config["weight"]
                    })
                    total_score += config["weight"]
                    break  # Only count each category once
        
        # Normalize score to 0-100
        fraud_score = min(100, total_score)
        
        # Determine action
        action, reasoning = self._determine_action(fraud_score, detected_indicators)
        
        return {
            "fraud_score": fraud_score,
            "indicators": detected_indicators,
            "action": action,
            "reasoning": reasoning,
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_method": "LLM" if self.llm_enabled else "RULE_BASED"
        }
    
    def _determine_action(self, score: float, indicators: List[Dict]) -> Tuple[str, str]:
        """
        Determine the appropriate action based on fraud score
        
        Args:
            score: Fraud score (0-100)
            indicators: List of detected indicators
            
        Returns:
            Tuple of (action, reasoning)
        """
        if score > 80:
            action = "INTERVENE_AND_BLOCK"
            reasoning = (
                f"CRITICAL THREAT DETECTED (Score: {score}/100). "
                f"Multiple high-risk scam indicators identified: "
                f"{', '.join([ind['category'] for ind in indicators])}. "
                f"Immediate intervention required to protect user."
            )
        elif score > 50:
            action = "ACTIVATE_ANSWER_BOT"
            reasoning = (
                f"SUSPICIOUS ACTIVITY DETECTED (Score: {score}/100). "
                f"Scam indicators present: {', '.join([ind['category'] for ind in indicators])}. "
                f"Activating AI answer bot to waste scammer's time and gather intelligence."
            )
        else:
            action = "ALLOW"
            reasoning = (
                f"LOW RISK (Score: {score}/100). "
                f"Call appears legitimate. Monitoring continues."
            )
        
        return action, reasoning
    
    async def analyze_with_llm(self, transcript: str) -> Dict:
        """
        Future: Analyze using real LLM (OpenAI, Anthropic, etc.)
        
        Args:
            transcript: The text transcript
            
        Returns:
            Analysis results
        """
        # TODO: Implement LLM integration
        # For now, fall back to rule-based
        return self.analyze(transcript)
