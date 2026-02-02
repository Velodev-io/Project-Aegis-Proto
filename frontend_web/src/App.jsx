import React, { useState, useEffect } from "react";
import SeniorDashboard from "./components/SeniorDashboard";
import AdvocatePage from "./components/AdvocatePage";
import FamilyPage from "./components/FamilyPage";
import HelpPage from "./components/HelpPage";
import CaregiverDashboard from "./components/CaregiverDashboard";
import Shield from "./components/Shield";
import Steward from "./components/Steward";
import { analyzeCall, checkBills, scanDocument } from "./api";
import "./App.css";

function App() {
  // 'dashboard' = Senior app home, 'advocate' = Senior app bills page, 'caregiver' = Separate caregiver app
  const [view, setView] = useState("dashboard");
  const [status, setStatus] = useState("Ready");
  const [alert, setAlert] = useState(null);
  const [darkMode, setDarkMode] = useState(false);

  // Initialize dark mode from system preference
  useEffect(() => {
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setDarkMode(true);
      document.documentElement.classList.add('dark');
    }
  }, []);

  // Toggle dark mode
  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark');
  };

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

  // Show new dashboard by default
  if (view === "dashboard") {
    return <SeniorDashboard onToggleDarkMode={toggleDarkMode} darkMode={darkMode} onNavigateToAdvocate={() => setView("advocate")} onNavigateToFamily={() => setView("family")} onNavigateToHelp={() => setView("help")} />;
  }

  // Show advocate page
  if (view === "advocate") {
    return <AdvocatePage onBack={() => setView("dashboard")} darkMode={darkMode} />;
  }

  // Show family page
  if (view === "family") {
    return <FamilyPage onBack={() => setView("dashboard")} darkMode={darkMode} />;
  }

  // Show help page
  if (view === "help") {
    return <HelpPage onBack={() => setView("dashboard")} darkMode={darkMode} />;
  }

  // Show caregiver dashboard
  if (view === "caregiver") {
    return <CaregiverDashboard darkMode={darkMode} onToggleDarkMode={toggleDarkMode} />;
  }

  return (
    <div className="app-container">
      <nav>
        <span onClick={() => setView("dashboard")} className={view === "dashboard" ? "active" : ""}>Dashboard</span>
        <span onClick={() => setView("caregiver")} className={view === "caregiver" ? "active" : ""}>Caregiver</span>
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

