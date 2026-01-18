import React, { useEffect, useState } from "react";
import { getPendingMethod, reviewItem } from "../api";

export default function Steward() {
    const [items, setItems] = useState([]);

    useEffect(() => {
        loadItems();
    }, []);

    const loadItems = async () => {
        const data = await getPendingMethod();
        setItems(data);
    };

    const handleDecision = async (id, decision) => {
        await reviewItem(id, decision);
        loadItems();
    };

    return (
        <div className="steward-panel">
            <h2>Steward Dashboard (HITL)</h2>
            {items.length === 0 ? (
                <p>No pending approvals. Good job!</p>
            ) : (
                <div className="list">
                    {items.map((item) => (
                        <div key={item.id} className="card">
                            <h3>{item.service_name}</h3>
                            <p className="amount">${item.amount}</p>
                            <p className="reason">{item.reasoning}</p>
                            <div className="actions">
                                <button className="reject" onClick={() => handleDecision(item.id, "REJECT")}>Reject</button>
                                <button className="approve" onClick={() => handleDecision(item.id, "APPROVE")}>Approve</button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
