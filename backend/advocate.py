from playwright.async_api import async_playwright
import os
import sqlite3
import asyncio

# Connect to DB to get credentials and limits
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "trust_vault.db")

def get_config(service_name):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM credentials WHERE service_name=?", (service_name,))
    creds = c.fetchone()
    c.execute("SELECT * FROM limits WHERE service_name=?", (service_name,))
    limit = c.fetchone()
    conn.close()
    return creds, limit

async def check_bills(service_name="utility_portal"):
    creds, limit_row = get_config(service_name)
    if not creds:
        return {"status": "ERROR", "reason": "No credentials found"}
    
    limit = limit_row['amount_limit'] if limit_row else 0.0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Load local mock file
        file_path = os.path.join(os.path.dirname(__file__), "mock_portal.html")
        await page.goto(f"file://{file_path}")
        
        # Login
        await page.fill("#username", creds['username'])
        await page.fill("#password", creds['password'])
        await page.click("text=Sign In")
        
        # Wait for dashboard
        await page.wait_for_selector("#dashboard-section")
        
        # Extract Amount
        amount_text = await page.inner_text(".amount")
        amount = float(amount_text.replace("$", ""))
        
        await browser.close()
        
        # Logic
        result = {
            "service": service_name,
            "bill_amount": amount,
            "limit": limit
        }
        
        if amount > limit:
            result["status"] = "Suspicious/Over Limit"
            result["action_required"] = True
            result["reasoning"] = f"Bill of ${amount} exceeds pre-approved limit of ${limit}."
        else:
            result["status"] = "Safe"
            result["action_required"] = False
            result["reasoning"] = "Within limits."
            
        return result

if __name__ == "__main__":
    print(asyncio.run(check_bills()))
