export const API_BASE = "http://localhost:8000";

// Legacy Sentinel functions
export async function analyzeCall(transcript) {
    try {
        const res = await fetch(`${API_BASE}/sentinel/analyze`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: transcript }),
        });
        return await res.json();
    } catch (e) {
        return { classification: "Error", reasoning: "Backend offline" };
    }
}

// New Sentinel Module API Functions
export async function interceptVoiceCall(transcript, userId = "senior_001") {
    try {
        const res = await fetch(`${API_BASE}/sentinel/voice/intercept`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                transcript,
                user_id: userId,
                call_metadata: { source: "web_dashboard" }
            }),
        });
        return await res.json();
    } catch (e) {
        return {
            fraud_score: 0,
            action: "ERROR",
            reasoning: "Backend offline",
            indicators: [],
            advocate_notified: false
        };
    }
}

export async function monitorTransaction(amount, category, merchant, userId = "senior_001") {
    try {
        const res = await fetch(`${API_BASE}/sentinel/transactions/monitor`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                amount,
                transaction_time: new Date().toISOString(),
                category,
                merchant,
                user_id: userId
            }),
        });
        return await res.json();
    } catch (e) {
        return {
            risk_level: "ERROR",
            status: "ERROR",
            reasoning: "Backend offline",
            flags: [],
            advocate_notified: false
        };
    }
}

export async function getSecurityLogs(limit = 20, eventType = null) {
    try {
        const params = new URLSearchParams({ limit: limit.toString() });
        if (eventType) params.append('event_type', eventType);

        const res = await fetch(`${API_BASE}/sentinel/logs?${params}`);
        return await res.json();
    } catch (e) {
        return { count: 0, logs: [] };
    }
}

export async function getPendingApprovals() {
    try {
        const res = await fetch(`${API_BASE}/sentinel/approvals/pending`);
        return await res.json();
    } catch (e) {
        return { count: 0, approvals: [] };
    }
}

export async function checkBills() {
    try {
        const res = await fetch(`${API_BASE}/advocate/check_bills`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ service_name: "utility_portal" }),
        });
        return await res.json();
    } catch (e) {
        return { action_required: false, reasoning: "Backend offline" };
    }
}

export async function getPendingMethod() {
    try {
        const res = await fetch(`${API_BASE}/steward/pending`);
        return await res.json();
    } catch (e) {
        return [];
    }
}

export async function reviewItem(id, decision) {
    await fetch(`${API_BASE}/steward/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ item_id: id, decision }),
    });
}

export async function scanDocument(file) {
    try {
        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch(`${API_BASE}/sentinel/scan`, {
            method: "POST",
            body: formData,
        });
        return await res.json();
    } catch (e) {
        return { classification: "Error", reasoning: "Backend offline" };
    }
}

// ============================================================================
// ADVOCATE MODULE API FUNCTIONS
// ============================================================================

export async function analyzeBill(lineItems, isInNetwork = true, previousBills = null) {
    try {
        const res = await fetch(`${API_BASE}/advocate/analyze-bill`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                line_items: lineItems,
                is_in_network: isInNetwork,
                previous_bills: previousBills
            }),
        });
        return await res.json();
    } catch (e) {
        return {
            total_billed: 0,
            total_allowed: 0,
            potential_savings: 0,
            errors: [],
            recommendations: [],
            risk_score: 0,
            action_required: false,
            error: "Backend offline"
        };
    }
}

export async function auditSubscriptions(transactions, usageData = null) {
    try {
        const res = await fetch(`${API_BASE}/advocate/subscriptions/audit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                transactions,
                usage_data: usageData
            }),
        });
        return await res.json();
    } catch (e) {
        return {
            subscriptions: [],
            total_monthly_cost: 0,
            potential_monthly_savings: 0,
            potential_annual_savings: 0,
            action_required: false,
            error: "Backend offline"
        };
    }
}

export async function generateNegotiationScript(scriptType, merchant, details = {}) {
    try {
        const res = await fetch(`${API_BASE}/advocate/generate-script`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                script_type: scriptType,
                merchant,
                ...details
            }),
        });
        return await res.json();
    } catch (e) {
        return {
            formatted_script: "Backend offline",
            error: "Backend offline"
        };
    }
}

export async function getAdvocateSummary() {
    try {
        const res = await fetch(`${API_BASE}/advocate/summary`);
        return await res.json();
    } catch (e) {
        return {
            module: "Advocate",
            status: "offline",
            capabilities: {},
            error: "Backend offline"
        };
    }
}

export async function uploadBillImage(file) {
    try {
        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch(`${API_BASE}/advocate/analyze-bill-image`, {
            method: "POST",
            body: formData,
        });
        return await res.json();
    } catch (e) {
        return {
            extracted_text: "",
            line_items: [],
            analysis: null,
            error: "Backend offline"
        };
    }
}

