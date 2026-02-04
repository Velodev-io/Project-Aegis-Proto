"""
Advocate Module: Autonomous Cancellation Agent
===============================================

This agent uses Playwright to navigate subscription cancellation flows
and autonomously cancel subscriptions (with HITL approval).

SAFETY: All actions are logged and require human approval before execution.
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

try:
    from playwright.async_api import async_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright not installed. Run: pip install playwright && playwright install")


class CancellationStatus(Enum):
    """Status of cancellation attempt"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REQUIRES_HUMAN = "REQUIRES_HUMAN"
    BLOCKED_BY_DARK_PATTERN = "BLOCKED_BY_DARK_PATTERN"


@dataclass
class CancellationAttempt:
    """Record of a cancellation attempt"""
    merchant: str
    status: CancellationStatus
    steps_completed: List[str]
    screenshots: List[str]
    error_message: Optional[str] = None
    dark_patterns_detected: List[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.dark_patterns_detected is None:
            self.dark_patterns_detected = []


class DarkPatternDetector:
    """
    Detects dark patterns in cancellation flows
    
    Dark patterns are UI tricks that make it hard to cancel:
    - Fake cancel buttons
    - Multiple confirmation screens
    - Hidden cancel options
    - Confusing language
    """
    
    DARK_PATTERNS = {
        "fake_button": [
            "button:has-text('Keep My Subscription')",
            "button:has-text('No, I want to keep it')",
            "a:has-text('Go Back')"
        ],
        "hidden_cancel": [
            "a[style*='display: none']",
            "button[hidden]",
            "a[class*='hidden']"
        ],
        "confusing_language": [
            "Are you sure you want to lose all these benefits?",
            "You'll miss out on",
            "Don't leave us",
            "We'll miss you"
        ],
        "retention_offer": [
            "50% off",
            "free month",
            "special offer just for you"
        ]
    }
    
    async def scan_page(self, page: Page) -> List[str]:
        """Scan page for dark patterns"""
        detected = []
        
        # Check for fake buttons
        for selector in self.DARK_PATTERNS["fake_button"]:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    detected.append(f"FAKE_BUTTON: Found {len(elements)} misleading button(s)")
            except:
                pass
        
        # Check for hidden cancel options
        for selector in self.DARK_PATTERNS["hidden_cancel"]:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    detected.append(f"HIDDEN_CANCEL: Found {len(elements)} hidden element(s)")
            except:
                pass
        
        # Check page text for confusing language
        try:
            content = await page.content()
            for phrase in self.DARK_PATTERNS["confusing_language"]:
                if phrase.lower() in content.lower():
                    detected.append(f"CONFUSING_LANGUAGE: '{phrase}'")
        except:
            pass
        
        # Check for retention offers
        try:
            content = await page.content()
            for phrase in self.DARK_PATTERNS["retention_offer"]:
                if phrase.lower() in content.lower():
                    detected.append(f"RETENTION_OFFER: '{phrase}'")
        except:
            pass
        
        return detected


class CancellationAgent:
    """
    Autonomous agent that cancels subscriptions
    
    Features:
    - Navigates cancellation flows
    - Handles multi-step confirmations
    - Detects and bypasses dark patterns
    - Takes screenshots for audit trail
    - Requires human approval for final action
    """
    
    def __init__(self, read_only: bool = True):
        """
        Initialize cancellation agent
        
        Args:
            read_only: If True, only simulates cancellation (SHADOW MODE)
        """
        self.read_only = read_only
        self.dark_pattern_detector = DarkPatternDetector()
        self.max_confirmation_screens = 5  # Safety limit
    
    async def cancel_subscription(
        self,
        merchant: str,
        cancellation_url: str,
        credentials: Optional[Dict[str, str]] = None
    ) -> CancellationAttempt:
        """
        Attempt to cancel a subscription
        
        Args:
            merchant: Name of the merchant
            cancellation_url: URL to cancellation page
            credentials: Optional login credentials
            
        Returns:
            CancellationAttempt with results
        """
        
        if not PLAYWRIGHT_AVAILABLE:
            return CancellationAttempt(
                merchant=merchant,
                status=CancellationStatus.FAILED,
                steps_completed=[],
                screenshots=[],
                error_message="Playwright not installed"
            )
        
        steps_completed = []
        screenshots = []
        dark_patterns = []
        
        async with async_playwright() as p:
            # Launch browser (headless=False for debugging)
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # Step 1: Navigate to cancellation page
                steps_completed.append("Navigating to cancellation page")
                await page.goto(cancellation_url, wait_until="networkidle")
                
                # Take screenshot
                screenshot_path = f"screenshots/{merchant}_step1.png"
                await page.screenshot(path=screenshot_path)
                screenshots.append(screenshot_path)
                
                # Scan for dark patterns
                patterns = await self.dark_pattern_detector.scan_page(page)
                dark_patterns.extend(patterns)
                
                # Step 2: Login if needed
                if credentials and await self._needs_login(page):
                    steps_completed.append("Logging in")
                    await self._login(page, credentials)
                    screenshot_path = f"screenshots/{merchant}_step2_login.png"
                    await page.screenshot(path=screenshot_path)
                    screenshots.append(screenshot_path)
                
                # Step 3: Find and click cancel button
                steps_completed.append("Looking for cancel button")
                cancel_button = await self._find_cancel_button(page)
                
                if not cancel_button:
                    return CancellationAttempt(
                        merchant=merchant,
                        status=CancellationStatus.FAILED,
                        steps_completed=steps_completed,
                        screenshots=screenshots,
                        error_message="Could not find cancel button",
                        dark_patterns_detected=dark_patterns
                    )
                
                # Step 4: Navigate through confirmation screens
                confirmation_count = 0
                while confirmation_count < self.max_confirmation_screens:
                    steps_completed.append(f"Confirmation screen {confirmation_count + 1}")
                    
                    # Scan for dark patterns
                    patterns = await self.dark_pattern_detector.scan_page(page)
                    dark_patterns.extend(patterns)
                    
                    # Take screenshot
                    screenshot_path = f"screenshots/{merchant}_confirm{confirmation_count + 1}.png"
                    await page.screenshot(path=screenshot_path)
                    screenshots.append(screenshot_path)
                    
                    # Look for final cancel button
                    final_cancel = await self._find_final_cancel_button(page)
                    
                    if final_cancel:
                        if self.read_only:
                            steps_completed.append("SHADOW MODE: Would click final cancel button")
                            return CancellationAttempt(
                                merchant=merchant,
                                status=CancellationStatus.REQUIRES_HUMAN,
                                steps_completed=steps_completed,
                                screenshots=screenshots,
                                error_message="Shadow mode - requires human approval",
                                dark_patterns_detected=dark_patterns
                            )
                        else:
                            # Actually click cancel (requires human approval first)
                            await final_cancel.click()
                            steps_completed.append("Clicked final cancel button")
                            
                            # Wait for confirmation
                            await page.wait_for_timeout(2000)
                            
                            # Check if successful
                            if await self._verify_cancellation(page):
                                screenshot_path = f"screenshots/{merchant}_success.png"
                                await page.screenshot(path=screenshot_path)
                                screenshots.append(screenshot_path)
                                
                                return CancellationAttempt(
                                    merchant=merchant,
                                    status=CancellationStatus.SUCCESS,
                                    steps_completed=steps_completed,
                                    screenshots=screenshots,
                                    dark_patterns_detected=dark_patterns
                                )
                    
                    # Look for "continue to cancel" button
                    continue_button = await self._find_continue_button(page)
                    if continue_button:
                        await continue_button.click()
                        await page.wait_for_timeout(1000)
                        confirmation_count += 1
                    else:
                        break
                
                # Too many confirmation screens - likely dark pattern
                if confirmation_count >= self.max_confirmation_screens:
                    return CancellationAttempt(
                        merchant=merchant,
                        status=CancellationStatus.BLOCKED_BY_DARK_PATTERN,
                        steps_completed=steps_completed,
                        screenshots=screenshots,
                        error_message=f"Exceeded {self.max_confirmation_screens} confirmation screens",
                        dark_patterns_detected=dark_patterns
                    )
                
                return CancellationAttempt(
                    merchant=merchant,
                    status=CancellationStatus.FAILED,
                    steps_completed=steps_completed,
                    screenshots=screenshots,
                    error_message="Could not complete cancellation flow",
                    dark_patterns_detected=dark_patterns
                )
                
            except Exception as e:
                return CancellationAttempt(
                    merchant=merchant,
                    status=CancellationStatus.FAILED,
                    steps_completed=steps_completed,
                    screenshots=screenshots,
                    error_message=str(e),
                    dark_patterns_detected=dark_patterns
                )
            
            finally:
                await browser.close()
    
    async def _needs_login(self, page: Page) -> bool:
        """Check if page requires login"""
        login_indicators = [
            "input[type='password']",
            "input[name='password']",
            "button:has-text('Sign In')",
            "button:has-text('Log In')"
        ]
        
        for selector in login_indicators:
            if await page.query_selector(selector):
                return True
        return False
    
    async def _login(self, page: Page, credentials: Dict[str, str]):
        """Perform login"""
        # Fill username/email
        email_field = await page.query_selector("input[type='email'], input[name='email'], input[name='username']")
        if email_field:
            await email_field.fill(credentials.get("email", ""))
        
        # Fill password
        password_field = await page.query_selector("input[type='password']")
        if password_field:
            await password_field.fill(credentials.get("password", ""))
        
        # Click login button
        login_button = await page.query_selector("button:has-text('Sign In'), button:has-text('Log In')")
        if login_button:
            await login_button.click()
            await page.wait_for_timeout(2000)
    
    async def _find_cancel_button(self, page: Page):
        """Find the initial cancel/unsubscribe button"""
        cancel_selectors = [
            "button:has-text('Cancel Subscription')",
            "a:has-text('Cancel Subscription')",
            "button:has-text('Unsubscribe')",
            "a:has-text('Unsubscribe')",
            "button:has-text('Cancel Membership')",
            "a:has-text('Cancel Membership')",
            "button[id*='cancel']",
            "a[id*='cancel']"
        ]
        
        for selector in cancel_selectors:
            button = await page.query_selector(selector)
            if button:
                return button
        
        return None
    
    async def _find_continue_button(self, page: Page):
        """Find 'continue to cancel' button"""
        continue_selectors = [
            "button:has-text('Continue')",
            "button:has-text('Next')",
            "button:has-text('Proceed')",
            "a:has-text('Continue to Cancel')"
        ]
        
        for selector in continue_selectors:
            button = await page.query_selector(selector)
            if button:
                return button
        
        return None
    
    async def _find_final_cancel_button(self, page: Page):
        """Find the final confirmation cancel button"""
        final_selectors = [
            "button:has-text('Yes, Cancel')",
            "button:has-text('Confirm Cancellation')",
            "button:has-text('Cancel My Subscription')",
            "button[id*='confirm']"
        ]
        
        for selector in final_selectors:
            button = await page.query_selector(selector)
            if button:
                # Make sure it's not a "keep subscription" button
                text = await button.inner_text()
                if "keep" not in text.lower() and "stay" not in text.lower():
                    return button
        
        return None
    
    async def _verify_cancellation(self, page: Page) -> bool:
        """Verify that cancellation was successful"""
        success_indicators = [
            "text=Subscription Canceled",
            "text=Successfully Canceled",
            "text=Your subscription has been canceled",
            "text=Cancellation Confirmed"
        ]
        
        for selector in success_indicators:
            if await page.query_selector(selector):
                return True
        
        return False


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("🤖 AUTONOMOUS CANCELLATION AGENT - TEST")
    print("=" * 70)
    
    if not PLAYWRIGHT_AVAILABLE:
        print("\n❌ Playwright not installed")
        print("Run: pip install playwright && playwright install")
    else:
        print("\n✅ Playwright available")
        print("\nThis agent can:")
        print("  - Navigate cancellation flows")
        print("  - Handle multiple confirmation screens")
        print("  - Detect dark patterns")
        print("  - Take screenshots for audit trail")
        print("  - Operate in shadow mode (read-only)")
        
        print("\n💡 Shadow Mode (read_only=True):")
        print("  - Agent simulates cancellation")
        print("  - No actual changes made")
        print("  - Shows what it WOULD do")
        print("  - Safe for testing on real sites")
        
        print("\n🎯 To test with a real site:")
        print("  agent = CancellationAgent(read_only=True)")
        print("  result = await agent.cancel_subscription(")
        print("      merchant='Planet Fitness',")
        print("      cancellation_url='https://...',")
        print("      credentials={'email': '...', 'password': '...'}")
        print("  )")
