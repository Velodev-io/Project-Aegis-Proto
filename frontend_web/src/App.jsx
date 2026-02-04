import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import LoginPage from "./components/LoginPage";
import SeniorDashboard from "./components/SeniorDashboard";
import AdvocatePage from "./components/AdvocatePage";
import FamilyPage from "./components/FamilyPage";
import HelpPage from "./components/HelpPage";
import CaregiverDashboard from "./components/CaregiverDashboard";
import Shield from "./components/Shield";
import Steward from "./components/Steward";
import SentinelDashboard from "./components/SentinelDashboard";
import TrustVaultPermissions from "./components/TrustVaultPermissions";
import AdvocateSavingsDashboard from "./components/AdvocateSavingsDashboard";
import UrgentApprovalModal from "./components/UrgentApprovalModal"; // Import for global usage if needed
import UIShowcase from "./components/UIShowcase";
import MainApp from "./components/MainApp";
import { analyzeCall, checkBills, scanDocument } from "./api";
import "./App.css";

// Main App Component with Router
function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

// App Content with routing logic
function AppContent() {
  const navigate = useNavigate();
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

  // Scam Alert Overlay
  if (alert) {
    return (
      <div className="scam-overlay">
        <h1>⚠️ SCAM DETECTED ⚠️</h1>
        <p>{alert}</p>
        <button onClick={() => setAlert(null)}>I UNDERSTAND</button>
      </div>
    );
  }

  // Demo state for Urgent Approval Modal - typically would be triggered by WebSocket or API polling
  const [showUrgentModal, setShowUrgentModal] = useState(false);

  // Expose a way to toggle it for demo purposes (e.g. window object or just a hotkey if we wanted)
  useEffect(() => {
    window.triggerUrgentModal = () => setShowUrgentModal(true);
  }, []);

  return (
    <>
      <UrgentApprovalModal
        isOpen={showUrgentModal}
        onClose={() => setShowUrgentModal(false)}
        details={{
          amount: "$1,200.00",
          recipient: "External Account • Chase ****4321",
          timestamp: "Today, 3:45 PM"
        }}
        onApprove={() => {
          alertUser("Transaction Approved Verified by Face ID", "success");
          setShowUrgentModal(false);
        }}
        onDecline={() => {
          alertUser("Transaction Declined and Blocked");
          setShowUrgentModal(false);
        }}
      />
      <Routes>

        {/* Main App with Bottom Navigation */}
        <Route
          path="/"
          element={<MainApp />}
        />

        {/* UI Showcase / Navigation Page */}
        <Route
          path="/showcase"
          element={<UIShowcase />}
        />

        {/* Login/Role Selection Page */}
        <Route
          path="/login"
          element={<LoginPage darkMode={darkMode} onToggleDarkMode={toggleDarkMode} />}
        />

        {/* Senior Dashboard Routes */}
        <Route
          path="/senior-dashboard"
          element={
            <SeniorDashboard
              onToggleDarkMode={toggleDarkMode}
              darkMode={darkMode}
              onNavigateToAdvocate={() => navigate("/advocate")}
              onNavigateToFamily={() => navigate("/family")}
              onNavigateToHelp={() => navigate("/help")}
              onNavigateToSentinel={() => navigate("/sentinel")}
            />
          }
        />
        <Route
          path="/advocate"
          element={<AdvocatePage onBack={() => navigate("/senior-dashboard")} darkMode={darkMode} />}
        />
        <Route
          path="/family"
          element={<FamilyPage onBack={() => navigate("/senior-dashboard")} darkMode={darkMode} />}
        />
        <Route
          path="/help"
          element={<HelpPage onBack={() => navigate("/senior-dashboard")} darkMode={darkMode} />}
        />

        {/* Caregiver Dashboard */}
        <Route
          path="/caregiver"
          element={<CaregiverDashboard darkMode={darkMode} onToggleDarkMode={toggleDarkMode} />}
        />

        {/* Steward/HITL Dashboard */}
        <Route
          path="/steward"
          element={<Steward />}
        />

        {/* Sentinel Security Dashboard */}
        <Route
          path="/sentinel"
          element={<SentinelDashboard darkMode={darkMode} onBack={() => navigate("/senior-dashboard")} />}
        />

        {/* New UI Modules */}
        <Route
          path="/trust-vault"
          element={<TrustVaultPermissions />}
        />
        <Route
          path="/advocate-savings"
          element={<AdvocateSavingsDashboard />}
        />

        {/* Legacy Shield Component */}
        <Route
          path="/senior"
          element={<Shield onScan={handleScan} status={status} />}
        />

        {/* Catch all - redirect to login */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}

export default App;
