"""
Advocate Module: Autonomous Negotiation Agent
==============================================

This agent generates professional dispute scripts and can use
voice synthesis to negotiate with billing departments.

Features:
- Generates firm but professional scripts
- Cites specific billing errors
- Requests specific remedies
- Can be used with Deepgram/Twilio for voice calls
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DisputeScript:
    """Generated negotiation script"""
    merchant: str
    script_type: str  # "MEDICAL_BILL", "SUBSCRIPTION", "GENERAL"
    opening: str
    body: List[str]  # Main points to make
    closing: str
    expected_outcome: str
    fallback_options: List[str]
    estimated_duration: int  # seconds
    tone: str  # "FIRM", "PROFESSIONAL", "FRIENDLY"


class NegotiationScriptGenerator:
    """
    Generates professional negotiation scripts for various scenarios
    
    Scripts are:
    - Firm but respectful
    - Cite specific errors/issues
    - Request specific remedies
    - Provide fallback options
    """
    
    def generate_medical_bill_dispute(
        self,
        provider_name: str,
        errors: List[Dict],
        total_disputed: float,
        policy_holder_name: str
    ) -> DisputeScript:
        """
        Generate script for medical bill dispute
        
        Args:
            provider_name: Name of medical provider
            errors: List of billing errors from AgenticAuditor
            total_disputed: Total amount being disputed
            policy_holder_name: Patient's name
        """
        
        # Opening
        opening = (
            f"Hello, my name is calling on behalf of {policy_holder_name}. "
            f"I'm calling regarding a recent bill from {provider_name} that contains "
            f"several billing errors totaling ${total_disputed:.2f}. "
            f"I have the bill in front of me and would like to review these discrepancies."
        )
        
        # Body - cite each error
        body = []
        
        for i, error in enumerate(errors, 1):
            if error["type"] == "UPCODING":
                body.append(
                    f"First, regarding CPT code {error['code']}: "
                    f"The bill shows a charge of ${error['billed']:.2f}, "
                    f"however, the insurance allowed amount for this code is ${error['allowed']:.2f}. "
                    f"This represents an overcharge of ${error['potential_savings']:.2f}."
                )
            
            elif error["type"] == "DUPLICATE_BILLING":
                body.append(
                    f"Second, I see duplicate billing for code {error['code']}. "
                    f"This service was billed on {error['current_date']} and again on {error['previous_date']}, "
                    f"which appears to be the same service charged twice. "
                    f"This duplicate charge is ${error['potential_savings']:.2f}."
                )
            
            elif error["type"] == "UNBUNDLING":
                body.append(
                    f"Additionally, code {error['code']} is being billed separately, "
                    f"but this service is included in the comprehensive panel already billed. "
                    f"This unbundled charge of ${error['potential_savings']:.2f} should be removed."
                )
            
            elif error["type"] == "INVALID_CODE":
                body.append(
                    f"I also notice code {error['code']} which is not a recognized CPT code. "
                    f"I need clarification on what this ${error['potential_savings']:.2f} charge represents."
                )
        
        # Add summary
        body.append(
            f"In total, these errors amount to ${total_disputed:.2f} in incorrect charges. "
            f"I'm requesting that these charges be removed and a corrected bill be issued."
        )
        
        # Closing
        closing = (
            f"I have documented all of these discrepancies and am prepared to escalate "
            f"this to the insurance company and state medical board if necessary. "
            f"However, I'm confident we can resolve this directly. "
            f"Can you confirm you'll review these errors and issue a corrected bill?"
        )
        
        # Expected outcome
        expected_outcome = (
            f"Billing department agrees to review errors and issue corrected bill "
            f"with ${total_disputed:.2f} in charges removed."
        )
        
        # Fallback options
        fallback_options = [
            "Request to speak with billing supervisor",
            "Ask for itemized bill and explanation of benefits (EOB)",
            "Request formal dispute process documentation",
            "Mention filing complaint with state medical board",
            "Request payment plan for any legitimate remaining balance"
        ]
        
        return DisputeScript(
            merchant=provider_name,
            script_type="MEDICAL_BILL",
            opening=opening,
            body=body,
            closing=closing,
            expected_outcome=expected_outcome,
            fallback_options=fallback_options,
            estimated_duration=180,  # 3 minutes
            tone="FIRM"
        )
    
    def generate_subscription_cancellation_dispute(
        self,
        merchant: str,
        subscription_amount: float,
        months_unused: int,
        reason: str
    ) -> DisputeScript:
        """
        Generate script for subscription cancellation/refund
        
        Args:
            merchant: Subscription merchant
            subscription_amount: Monthly amount
            months_unused: Number of months with no usage
            reason: Reason for cancellation
        """
        
        total_wasted = subscription_amount * months_unused
        
        # Opening
        opening = (
            f"Hello, I'm calling to cancel my subscription with {merchant}. "
            f"I've been a customer for {months_unused} months but have not used the service. "
            f"I'd like to discuss cancellation and a possible refund."
        )
        
        # Body
        body = [
            f"Looking at my account, I see I've been charged ${subscription_amount:.2f} per month "
            f"for the past {months_unused} months, totaling ${total_wasted:.2f}.",
            
            f"However, my usage data shows {reason}. "
            f"I was not aware the subscription was still active.",
            
            f"I'd like to cancel the subscription immediately and request a refund "
            f"for at least the last {min(months_unused, 3)} months, which would be ${subscription_amount * min(months_unused, 3):.2f}."
        ]
        
        # Closing
        closing = (
            f"I understand you have policies, but given the zero usage and the fact that "
            f"I'm requesting cancellation now, I believe a partial refund is fair. "
            f"Can you process the cancellation and refund today?"
        )
        
        # Expected outcome
        expected_outcome = (
            f"Subscription canceled immediately with partial refund of "
            f"${subscription_amount * min(months_unused, 3):.2f} (last 3 months)."
        )
        
        # Fallback options
        fallback_options = [
            "Accept cancellation without refund if necessary",
            "Request to speak with retention team",
            "Ask for account credit instead of refund",
            "Request confirmation email of cancellation",
            "Mention filing complaint with credit card company"
        ]
        
        return DisputeScript(
            merchant=merchant,
            script_type="SUBSCRIPTION",
            opening=opening,
            body=body,
            closing=closing,
            expected_outcome=expected_outcome,
            fallback_options=fallback_options,
            estimated_duration=120,  # 2 minutes
            tone="PROFESSIONAL"
        )
    
    def generate_price_negotiation_script(
        self,
        merchant: str,
        service: str,
        quoted_price: float,
        market_price: float,
        competitor: str
    ) -> DisputeScript:
        """
        Generate script for price negotiation
        
        Args:
            merchant: Service provider
            service: Service being negotiated
            quoted_price: Their quoted price
            market_price: Average market price
            competitor: Competitor with better price
        """
        
        savings = quoted_price - market_price
        
        # Opening
        opening = (
            f"Hello, I'm calling about the quote I received for {service}. "
            f"I'm very interested in working with {merchant}, but I'd like to discuss the pricing."
        )
        
        # Body
        body = [
            f"Your quote shows ${quoted_price:.2f} for {service}.",
            
            f"I've done some research and found that the average market price "
            f"for this service is around ${market_price:.2f}.",
            
            f"Specifically, {competitor} quoted me ${market_price:.2f} for the same service.",
            
            f"I prefer to work with {merchant} based on your reputation, "
            f"but I need the pricing to be competitive. "
            f"Can you match or beat the ${market_price:.2f} price point?"
        ]
        
        # Closing
        closing = (
            f"I'm ready to commit today if we can agree on pricing around ${market_price:.2f}. "
            f"What can you do for me?"
        )
        
        # Expected outcome
        expected_outcome = (
            f"{merchant} agrees to match market price of ${market_price:.2f}, "
            f"saving ${savings:.2f}."
        )
        
        # Fallback options
        fallback_options = [
            f"Accept ${market_price + (savings * 0.5):.2f} (split the difference)",
            "Ask for additional services at quoted price",
            "Request payment plan to reduce immediate cost",
            "Ask to speak with sales manager",
            "Politely decline and go with competitor"
        ]
        
        return DisputeScript(
            merchant=merchant,
            script_type="PRICE_NEGOTIATION",
            opening=opening,
            body=body,
            closing=closing,
            expected_outcome=expected_outcome,
            fallback_options=fallback_options,
            estimated_duration=90,  # 1.5 minutes
            tone="FRIENDLY"
        )
    
    def format_script_for_voice(self, script: DisputeScript) -> str:
        """
        Format script for text-to-speech
        
        Adds pauses, emphasis, and natural speech patterns
        """
        
        # Add pauses between sections
        formatted = script.opening + "\n\n[PAUSE 2 seconds]\n\n"
        
        for point in script.body:
            formatted += point + "\n\n[PAUSE 1 second]\n\n"
        
        formatted += script.closing + "\n\n[PAUSE 2 seconds]\n\n"
        formatted += "Thank you for your time."
        
        return formatted
    
    def format_script_for_human(self, script: DisputeScript) -> str:
        """
        Format script for human advocate to read
        
        Includes stage directions and fallback options
        """
        
        formatted = f"""
NEGOTIATION SCRIPT: {script.merchant}
Type: {script.script_type}
Tone: {script.tone}
Estimated Duration: {script.estimated_duration // 60} minutes

=== OPENING ===
{script.opening}

[Wait for acknowledgment]

=== MAIN POINTS ===
"""
        
        for i, point in enumerate(script.body, 1):
            formatted += f"\n{i}. {point}\n"
            formatted += "[Pause for response]\n"
        
        formatted += f"""
=== CLOSING ===
{script.closing}

[Wait for commitment]

=== EXPECTED OUTCOME ===
{script.expected_outcome}

=== IF THEY RESIST ===
Fallback options (in order of preference):
"""
        
        for i, option in enumerate(script.fallback_options, 1):
            formatted += f"{i}. {option}\n"
        
        formatted += """
=== NOTES ===
- Remain calm and professional throughout
- Take notes on their responses
- Get confirmation number for any agreements
- Request email confirmation
- If they refuse everything, escalate to supervisor
"""
        
        return formatted


class VoiceNegotiationAgent:
    """
    Agent that can make phone calls using voice synthesis
    
    Integration points:
    - Deepgram: Text-to-speech and speech-to-text
    - Twilio: Phone call handling
    - OpenAI Realtime API: Conversational AI
    """
    
    def __init__(self, provider: str = "deepgram"):
        """
        Initialize voice agent
        
        Args:
            provider: "deepgram", "twilio", or "openai"
        """
        self.provider = provider
        self.script_generator = NegotiationScriptGenerator()
    
    async def make_negotiation_call(
        self,
        phone_number: str,
        script: DisputeScript,
        record_call: bool = True
    ) -> Dict:
        """
        Make a phone call to negotiate
        
        Args:
            phone_number: Number to call
            script: Dispute script to follow
            record_call: Whether to record the call
            
        Returns:
            Call results
        """
        
        # This is a placeholder for actual voice integration
        # In production, this would use Deepgram/Twilio APIs
        
        return {
            "status": "PLACEHOLDER",
            "message": "Voice integration not yet implemented",
            "script_used": script.merchant,
            "recommendation": "Use human advocate for now",
            "formatted_script": self.script_generator.format_script_for_human(script)
        }


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("📞 NEGOTIATION SCRIPT GENERATOR - TEST")
    print("=" * 70)
    
    generator = NegotiationScriptGenerator()
    
    # Test 1: Medical bill dispute
    print("\n📋 TEST 1: Medical Bill Dispute Script")
    print("-" * 70)
    
    errors = [
        {
            "type": "UPCODING",
            "code": "99214",
            "billed": 350.00,
            "allowed": 210.00,
            "potential_savings": 140.00
        },
        {
            "type": "DUPLICATE_BILLING",
            "code": "85025",
            "current_date": "2026-01-20",
            "previous_date": "2026-01-18",
            "potential_savings": 30.00
        }
    ]
    
    script = generator.generate_medical_bill_dispute(
        provider_name="City Hospital",
        errors=errors,
        total_disputed=170.00,
        policy_holder_name="Robert Johnson"
    )
    
    print(generator.format_script_for_human(script))
    
    # Test 2: Subscription cancellation
    print("\n\n📋 TEST 2: Subscription Cancellation Script")
    print("-" * 70)
    
    script2 = generator.generate_subscription_cancellation_dispute(
        merchant="Planet Fitness",
        subscription_amount=10.00,
        months_unused=6,
        reason="zero gym check-ins in the past 6 months"
    )
    
    print(generator.format_script_for_human(script2))
    
    print("\n✅ Negotiation script generator tests complete!")
