import React, { useState } from "react";
import Shield from "./components/Shield";
import Steward from "./components/Steward";
import { analyzeCall, checkBills, scanDocument } from "./api";
import "./App.css";

function App() {
  const [view, setView] = useState("senior"); // 'senior' or 'steward'
  const [status, setStatus] = useState("Ready");
  const [alert, setAlert] = useState(null);

  const handleScan = async (type, payload) => {
    setStatus("Scanning...");

    if (type === "bill") {
      const res = await checkBills();
      setStatus("Ready");
      if (res.action_required) {
        alertUser("Alert: Steward notified of high bill!");
      } else {
        alertUser("Bill checked. All good!", "success");
      }
    } else if (type === "doc") {
      const res = await scanDocument(payload);
      setStatus("Ready");
      if (res.classification === "Confirmed Scam") {
        setAlert(res.reasoning);
      } else {
        alertUser(`Document Safe: ${res.reasoning}`, "success");
      }
    } else {
      // Call Analysis
      const transcript = "Hello I am from IRS give me gift card now";
      const res = await analyzeCall(transcript);
      setStatus("Ready");
      if (res.classification === "Confirmed Scam") {
        setAlert(res.reasoning); // Red Screen
      } else {
        alertUser("Call is Safe", "success");
      }
    }
  };

  const alertUser = (msg, type = "info") => {
    // simple toast simulation
    console.log(msg);
    if (type !== "success" && !msg.includes("Safe")) window.alert(msg);
  };

  if (alert) {
    return (
      <div className="scam-overlay">
        <h1>⚠️ SCAM DETECTED ⚠️</h1>
        <p>{alert}</p>
        <button onClick={() => setAlert(null)}>I UNDERSTAND</button>
      </div>
    );
  }

  return (
    <div className="app-container">
      <nav>
        <span onClick={() => setView("senior")} className={view === "senior" ? "active" : ""}>Senior Mode</span>
        <span onClick={() => setView("steward")} className={view === "steward" ? "active" : ""}>Steward Mode</span>
      </nav>

      <main>
        {view === "senior" ? <Shield onScan={handleScan} status={status} /> : <Steward />}
      </main>
    </div>
  );
}

export default App;
