import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const TrustVaultPermissions = () => {
    const navigate = useNavigate();
    // State for permissions
    const [permissions, setPermissions] = useState({
        medical: true,
        utility: true,
        financial: false,
    });

    const togglePermission = (key) => {
        setPermissions(prev => ({ ...prev, [key]: !prev[key] }));
    };

    return (
        <div className="min-h-screen bg-[#0f172a] text-white font-sans flex flex-col relative overflow-hidden">
            {/* Header */}
            <div className="flex justify-between items-center p-6 pt-12 z-10">
                <button onClick={() => navigate(-1)} className="text-yellow-500 hover:text-yellow-400 font-medium flex items-center gap-1">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6" /></svg>
                </button>
                <span className="text-xl font-semibold tracking-wide">Trust Vault Permissions</span>
                <button className="text-yellow-500 hover:text-yellow-400">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" /><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" /><path d="M12 17h.01" /></svg>
                </button>
            </div>

            {/* Hero Section */}
            <div className="px-6 pb-8 relative z-10">
                {/* Background Pattern Mockup */}
                <div className="absolute top-0 left-0 w-full h-full opacity-10 pointer-events-none"
                    style={{ backgroundImage: 'radial-gradient(circle at 50% 50%, #3b82f6 1px, transparent 1px)', backgroundSize: '20px 20px' }}>
                </div>

                <div className="bg-[#1e293b]/50 backdrop-blur-sm border border-yellow-500/20 rounded-2xl p-6 flex items-center gap-4">
                    <div className="w-16 h-16 bg-gradient-to-br from-yellow-600 to-yellow-800 rounded-full flex items-center justify-center shadow-lg shadow-yellow-900/50">
                        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" /></svg>
                    </div>
                    <div>
                        <h2 className="text-yellow-400 text-lg font-bold leading-tight">Secure Permissions for Robert's Account</h2>
                    </div>
                </div>
            </div>

            {/* Permissions List */}
            <div className="px-6 flex-1 space-y-4 z-10 overflow-y-auto pb-24">

                {/* Medical Records */}
                <PermissionCard
                    icon={<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="currentColor" className="text-green-900"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8z" /><path d="M12 7v10" /><path d="M7 12h10" /></svg>}
                    title="Medical Records"
                    description="View and manage health documents"
                    isActive={permissions.medical}
                    onToggle={() => togglePermission('medical')}
                    cardColor="border-green-500/30"
                    iconBg="bg-green-500/20"
                    iconColor="text-green-400"
                />

                {/* Utility Management */}
                <PermissionCard
                    icon={<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 10V5c0-1.7 1.3-3 3-3h1a3 3 0 0 1 3 3v5" /><path d="M16 3v5" /><path d="M12 12v9" /><path d="m19 5-7 7-7-7" /></svg>}
                    title="Utility Management"
                    description="Pay and track utility bills"
                    isActive={permissions.utility}
                    onToggle={() => togglePermission('utility')}
                    cardColor="border-blue-500/30"
                    iconBg="bg-blue-500/20"
                    iconColor="text-blue-400"
                />

                {/* Financial Transactions */}
                <PermissionCard
                    icon={<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" x2="12" y1="2" y2="22" /><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" /></svg>}
                    title="Financial Transactions"
                    description="Authorize bank and card payments"
                    isActive={permissions.financial}
                    onToggle={() => togglePermission('financial')}
                    cardColor="border-purple-500/30"
                    iconBg="bg-purple-500/20"
                    iconColor="text-purple-400"
                />

            </div>

            {/* Bottom Navigation */}
            <BottomNavigation active="fiduciary" />
        </div>
    );
};

const PermissionCard = ({ icon, title, description, isActive, onToggle, cardColor, iconBg, iconColor }) => {
    return (
        <div className={`bg-[#1e293b]/80 backdrop-blur-md rounded-xl p-5 border ${cardColor} flex items-center justify-between relative shadow-lg`}>
            <div className="absolute top-3 right-3 opacity-50">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-400"><circle cx="12" cy="12" r="10" /><path d="M12 16v-4" /><path d="M12 8h.01" /></svg>
            </div>

            <div className="flex items-center gap-4">
                <div className={`w-14 h-14 rounded-full ${iconBg} ${iconColor} flex items-center justify-center border border-white/10 shadow-inner`}>
                    {icon}
                </div>
                <div>
                    <h3 className="text-white font-semibold text-lg">{title}</h3>
                    <p className="text-gray-400 text-sm leading-tight max-w-[140px]">{description}</p>
                </div>
            </div>

            {/* Toggle Switch */}
            <button
                onClick={onToggle}
                className={`w-14 h-8 rounded-full flex items-center transition-colors duration-300 px-1 ${isActive ? 'bg-green-500' : 'bg-gray-600'}`}
            >
                <div
                    className={`w-6 h-6 bg-white rounded-full shadow-md transform transition-transform duration-300 ${isActive ? 'translate-x-6' : 'translate-x-0'}`}
                />
            </button>
        </div>
    );
};

const BottomNavigation = ({ active }) => {
    const navigate = useNavigate();

    // Helper for active styles
    const getStyle = (name) => active === name ? "text-yellow-400" : "text-gray-500 hover:text-gray-300";

    return (
        <div className="absolute bottom-0 left-0 w-full bg-[#0f172a] border-t border-gray-800 p-4 pb-8 flex justify-around items-center z-20">
            <button onClick={() => navigate('/senior-dashboard')} className={`flex flex-col items-center gap-1 ${getStyle('dashboard')}`}>
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="7" height="9" x="3" y="3" rx="1" /><rect width="7" height="5" x="14" y="3" rx="1" /><rect width="7" height="9" x="14" y="12" rx="1" /><rect width="7" height="5" x="3" y="16" rx="1" /></svg>
                <span className="text-xs font-medium">Dashboard</span>
            </button>
            <button onClick={() => navigate('/trust-vault')} className={`flex flex-col items-center gap-1 ${getStyle('fiduciary')}`}>
                <div className="relative">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></svg>
                    <div className="absolute -top-1 -right-1 w-3 h-3 bg-yellow-400 rounded-full border border-[#0f172a] flex items-center justify-center">
                        <svg width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="black" strokeWidth="3"><path d="M12 17h.01" /><path d="M12 11v2" /></svg>
                    </div>
                </div>
                <span className="text-xs font-medium">Fiduciary</span>
            </button>
            <button className={`flex flex-col items-center gap-1 ${getStyle('activity')}`}>
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2" /></svg>
                <span className="text-xs font-medium">Activity</span>
            </button>
            <button className={`flex flex-col items-center gap-1 ${getStyle('settings')}`}>
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.38a2 2 0 0 0-.73-2.73l-.15-.1a2 2 0 0 1-1-1.72v-.51a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" /><circle cx="12" cy="12" r="3" /></svg>
                <span className="text-xs font-medium">Settings</span>
            </button>
        </div>
    );
};

export default TrustVaultPermissions;
