export const API_BASE = "http://192.168.1.4:8000";

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
