import React, { useState, useEffect } from "react";


export default function Shield({ onScan, status }) {
    const [pulse, setPulse] = useState(false);

    useEffect(() => {
        const interval = setInterval(() => setPulse((p) => !p), 1500);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="shield-container">
            <div className={`shield ${status === "Scanning..." ? "pulse" : ""}`}>
                🛡️
            </div>
            <h2>{status}</h2>

            <div className="controls">
                <button onClick={() => onScan("bill")} disabled={status !== "Ready"}>
                    Check Bills
                </button>
                <button onClick={() => onScan("call")} disabled={status !== "Ready"}>
                    Analyze Call
                </button>

                <label className="scan-btn">
                    Scan Document
                    <input
                        type="file"
                        style={{ display: 'none' }}
                        onChange={(e) => {
                            if (e.target.files && e.target.files[0]) {
                                onScan("doc", e.target.files[0]);
                            }
                        }}
                        disabled={status !== "Ready"}
                    />
                </label>
            </div>
        </div>
    );
}
