import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const MainApp = () => {
    const [activeTab, setActiveTab] = useState('dashboard');
    const navigate = useNavigate();

    const renderContent = () => {
        switch (activeTab) {
            case 'dashboard':
                return <DashboardView />;
            case 'advocate':
                return <AdvocateView />;
            case 'fiduciary':
                return <FiduciaryView />;
            case 'activity':
                return <ActivityView />;
            case 'settings':
                return <SettingsView />;
            default:
                return <DashboardView />;
        }
    };

    return (
        <div className="min-h-screen bg-[#0f172a] text-white flex flex-col">
            {/* Main Content Area */}
            <div className="flex-1 overflow-y-auto pb-24">
                {renderContent()}
            </div>

            {/* Fixed Bottom Navigation */}
            <BottomNav activeTab={activeTab} setActiveTab={setActiveTab} />
        </div>
    );
};

// Dashboard View (Home/Central Page)
const DashboardView = () => {
    return (
        <div className="p-6">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2">Project Aegis</h1>
                <p className="text-gray-400">Your Cognitive Fiduciary</p>
            </div>

            {/* Account Overview */}
            <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-2xl p-6 mb-6 shadow-xl">
                <div className="flex items-center gap-4 mb-4">
                    <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                            <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
                            <circle cx="12" cy="7" r="4" />
                        </svg>
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold">Robert's Account</h2>
                        <p className="text-blue-200 text-sm">Protected & Monitored</p>
                    </div>
                </div>
                <div className="grid grid-cols-2 gap-4 mt-6">
                    <div className="bg-white/10 rounded-lg p-3">
                        <p className="text-blue-200 text-xs mb-1">Total Saved</p>
                        <p className="text-2xl font-bold">$1,240</p>
                    </div>
                    <div className="bg-white/10 rounded-lg p-3">
                        <p className="text-blue-200 text-xs mb-1">Active POAs</p>
                        <p className="text-2xl font-bold">3</p>
                    </div>
                </div>
            </div>

            {/* Quick Actions */}
            <div className="mb-6">
                <h3 className="text-lg font-bold mb-4">Quick Actions</h3>
                <div className="grid grid-cols-2 gap-4">
                    <QuickActionCard
                        icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect width="18" height="11" x="3" y="11" rx="2" ry="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" /></svg>}
                        title="Permissions"
                        color="yellow"
                    />
                    <QuickActionCard
                        icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="12" x2="12" y1="2" y2="22" /><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" /></svg>}
                        title="Savings"
                        color="green"
                    />
                    <QuickActionCard
                        icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2z" /><path d="M12 7v10" /><path d="M7 12h10" /></svg>}
                        title="Medical"
                        color="red"
                    />
                    <QuickActionCard
                        icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2" /></svg>}
                        title="Activity"
                        color="purple"
                    />
                </div>
            </div>

            {/* Recent Activity */}
            <div>
                <h3 className="text-lg font-bold mb-4">Recent Activity</h3>
                <div className="space-y-3">
                    <ActivityItem
                        icon="✅"
                        title="Comcast Bill Negotiated"
                        time="2 hours ago"
                        amount="+$20"
                    />
                    <ActivityItem
                        icon="🔒"
                        title="POA Updated - Utilities"
                        time="1 day ago"
                    />
                    <ActivityItem
                        icon="💰"
                        title="Medical Claim Approved"
                        time="3 days ago"
                        amount="+$150"
                    />
                </div>
            </div>
        </div>
    );
};

// Advocate View (Savings Dashboard)
const AdvocateView = () => {
    return (
        <div className="p-6">
            <h1 className="text-3xl font-bold mb-6">Advocate Savings</h1>

            {/* Total Saved Card */}
            <div className="bg-[#6ee7b7] text-[#0f172a] rounded-2xl p-8 text-center shadow-lg mb-8">
                <h2 className="text-6xl font-bold tracking-tighter mb-2">$1240.00</h2>
                <p className="text-lg font-medium opacity-80 mb-2">Total Saved This Year</p>
                <div className="inline-flex items-center gap-1 bg-[#0f172a]/10 px-3 py-1 rounded-full text-sm font-semibold">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                        <path d="m18 15-6-6-6 6" />
                    </svg>
                    <span>+15% vs last year</span>
                </div>
            </div>

            {/* Monthly Trend Chart */}
            <div className="mb-8">
                <h3 className="text-xl font-bold mb-6">Monthly Savings Trend</h3>
                <div className="h-48 flex items-end justify-between px-2 gap-2">
                    <ChartBar label="Jan" height="40%" amount="$320" />
                    <ChartBar label="Feb" height="65%" amount="$630" />
                    <ChartBar label="Mar" height="50%" amount="$440" />
                    <ChartBar label="Apr" height="75%" amount="$820" />
                    <ChartBar label="May" height="85%" amount="$1000" />
                    <ChartBar label="Jun" height="100%" amount="$1240" isHighest />
                </div>
            </div>

            {/* Recent Negotiations */}
            <div>
                <h3 className="text-xl font-bold mb-4">Recent Negotiations</h3>
                <div className="space-y-4">
                    <NegotiationCard
                        status="Resolved"
                        title="Comcast Bill"
                        detail="Found $20 overcharge. Refund processed."
                        amount="$20 saved"
                        statusColor="bg-[#6ee7b7] text-[#064e3b]"
                    />
                    <NegotiationCard
                        status="In Progress"
                        title="Medical Claim"
                        detail="Disputed. Pending review."
                        amount="$150 potential save"
                        statusColor="bg-[#fcd34d] text-[#78350f]"
                    />
                    <NegotiationCard
                        status="Resolved"
                        title="Phone Plan"
                        detail="Lowered monthly rate."
                        amount="$40 saved"
                        statusColor="bg-[#6ee7b7] text-[#064e3b]"
                    />
                </div>
            </div>
        </div>
    );
};

// Fiduciary View (Trust Vault Permissions)
const FiduciaryView = () => {
    const [permissions, setPermissions] = useState({
        medical: true,
        utility: true,
        financial: false,
    });

    const togglePermission = (key) => {
        setPermissions(prev => ({ ...prev, [key]: !prev[key] }));
    };

    return (
        <div className="p-6">
            <h1 className="text-3xl font-bold mb-6">Trust Vault Permissions</h1>

            {/* Hero Section */}
            <div className="bg-[#1e293b]/50 backdrop-blur-sm border border-yellow-500/20 rounded-2xl p-6 flex items-center gap-4 mb-8">
                <div className="w-16 h-16 bg-gradient-to-br from-yellow-600 to-yellow-800 rounded-full flex items-center justify-center shadow-lg shadow-yellow-900/50">
                    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                        <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
                        <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                    </svg>
                </div>
                <div>
                    <h2 className="text-yellow-400 text-lg font-bold leading-tight">Secure Permissions for Robert's Account</h2>
                </div>
            </div>

            {/* Permissions List */}
            <div className="space-y-4">
                <PermissionCard
                    icon={<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="currentColor" className="text-green-900"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8z" /><path d="M12 7v10" /><path d="M7 12h10" /></svg>}
                    title="Medical Records"
                    description="View and manage health documents"
                    isActive={permissions.medical}
                    onToggle={() => togglePermission('medical')}
                    cardColor="border-green-500/30"
                    iconBg="bg-green-500/20"
                    iconColor="text-green-400"
                />
                <PermissionCard
                    icon={<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 10V5c0-1.7 1.3-3 3-3h1a3 3 0 0 1 3 3v5" /><path d="M16 3v5" /><path d="M12 12v9" /><path d="m19 5-7 7-7-7" /></svg>}
                    title="Utility Management"
                    description="Pay and track utility bills"
                    isActive={permissions.utility}
                    onToggle={() => togglePermission('utility')}
                    cardColor="border-blue-500/30"
                    iconBg="bg-blue-500/20"
                    iconColor="text-blue-400"
                />
                <PermissionCard
                    icon={<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="12" x2="12" y1="2" y2="22" /><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" /></svg>}
                    title="Financial Transactions"
                    description="Authorize bank and card payments"
                    isActive={permissions.financial}
                    onToggle={() => togglePermission('financial')}
                    cardColor="border-purple-500/30"
                    iconBg="bg-purple-500/20"
                    iconColor="text-purple-400"
                />
            </div>
        </div>
    );
};

// Activity View
const ActivityView = () => {
    return (
        <div className="p-6">
            <h1 className="text-3xl font-bold mb-6">Activity</h1>

            <div className="space-y-4">
                <ActivityCard
                    type="success"
                    title="Bill Negotiation Successful"
                    description="Comcast bill reduced by $20/month"
                    time="2 hours ago"
                    amount="+$20"
                />
                <ActivityCard
                    type="info"
                    title="POA Permission Updated"
                    description="Utility management scope modified"
                    time="1 day ago"
                />
                <ActivityCard
                    type="warning"
                    title="Break-Glass Alert Resolved"
                    description="High-value transaction approved via 2FA"
                    time="2 days ago"
                />
                <ActivityCard
                    type="success"
                    title="Medical Claim Processed"
                    description="Insurance claim approved and paid"
                    time="3 days ago"
                    amount="+$150"
                />
            </div>
        </div>
    );
};

// Settings View
const SettingsView = () => {
    return (
        <div className="p-6">
            <h1 className="text-3xl font-bold mb-6">Settings</h1>

            <div className="space-y-6">
                <SettingsSection title="Account">
                    <SettingsItem label="Profile Information" />
                    <SettingsItem label="Security & Privacy" />
                    <SettingsItem label="Notifications" />
                </SettingsSection>

                <SettingsSection title="Preferences">
                    <SettingsItem label="Language" value="English" />
                    <SettingsItem label="Currency" value="USD ($)" />
                    <SettingsItem label="Dark Mode" value="Enabled" />
                </SettingsSection>

                <SettingsSection title="Support">
                    <SettingsItem label="Help Center" />
                    <SettingsItem label="Contact Support" />
                    <SettingsItem label="About Project Aegis" />
                </SettingsSection>
            </div>
        </div>
    );
};

// Reusable Components
const QuickActionCard = ({ icon, title, color }) => {
    const colors = {
        yellow: 'from-yellow-500 to-yellow-700',
        green: 'from-green-500 to-green-700',
        red: 'from-red-500 to-red-700',
        purple: 'from-purple-500 to-purple-700',
    };

    return (
        <div className={`bg-gradient-to-br ${colors[color]} rounded-xl p-4 flex flex-col items-center justify-center gap-2 cursor-pointer hover:scale-105 transition-transform`}>
            {icon}
            <span className="text-sm font-semibold">{title}</span>
        </div>
    );
};

const ActivityItem = ({ icon, title, time, amount }) => (
    <div className="bg-[#1e293b] rounded-lg p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
            <span className="text-2xl">{icon}</span>
            <div>
                <p className="font-semibold text-sm">{title}</p>
                <p className="text-gray-400 text-xs">{time}</p>
            </div>
        </div>
        {amount && <span className="text-green-400 font-bold">{amount}</span>}
    </div>
);

const ChartBar = ({ label, height, amount, isHighest }) => (
    <div className="flex flex-col items-center flex-1 h-full justify-end group cursor-pointer">
        <span className="text-xs text-gray-400 mb-1 opacity-0 group-hover:opacity-100 transition-opacity absolute -mt-6">{amount}</span>
        <div
            className={`w-full max-w-[40px] rounded-t-lg transition-all duration-500 hover:opacity-80 ${isHighest ? 'bg-[#6ee7b7]' : 'bg-[#99f6e4]'}`}
            style={{ height: height }}
        ></div>
        <span className="text-sm font-medium mt-2 text-gray-300">{label}</span>
    </div>
);

const NegotiationCard = ({ status, title, detail, amount, statusColor }) => (
    <div className="bg-[#1e293b] rounded-xl p-5 border border-gray-700/50 shadow-md">
        <div className="flex justify-between items-start mb-2">
            <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide ${statusColor}`}>
                {status}
            </span>
            <span className="text-gray-400 text-sm font-medium">{amount}</span>
        </div>
        <h4 className="text-white font-bold text-lg mb-1">{title}</h4>
        <p className="text-gray-400 text-sm">{detail}</p>
    </div>
);

const PermissionCard = ({ icon, title, description, isActive, onToggle, cardColor, iconBg, iconColor }) => (
    <div className={`bg-[#1e293b]/80 backdrop-blur-md rounded-xl p-5 border ${cardColor} flex items-center justify-between shadow-lg`}>
        <div className="flex items-center gap-4">
            <div className={`w-14 h-14 rounded-full ${iconBg} ${iconColor} flex items-center justify-center border border-white/10 shadow-inner`}>
                {icon}
            </div>
            <div>
                <h3 className="text-white font-semibold text-lg">{title}</h3>
                <p className="text-gray-400 text-sm leading-tight max-w-[140px]">{description}</p>
            </div>
        </div>
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

const ActivityCard = ({ type, title, description, time, amount }) => {
    const typeColors = {
        success: 'border-green-500/30 bg-green-500/5',
        info: 'border-blue-500/30 bg-blue-500/5',
        warning: 'border-yellow-500/30 bg-yellow-500/5',
    };

    return (
        <div className={`rounded-xl p-4 border ${typeColors[type]}`}>
            <div className="flex justify-between items-start mb-2">
                <h3 className="font-bold text-lg">{title}</h3>
                {amount && <span className="text-green-400 font-bold">{amount}</span>}
            </div>
            <p className="text-gray-400 text-sm mb-2">{description}</p>
            <p className="text-gray-500 text-xs">{time}</p>
        </div>
    );
};

const SettingsSection = ({ title, children }) => (
    <div>
        <h3 className="text-lg font-bold mb-3 text-gray-300">{title}</h3>
        <div className="bg-[#1e293b] rounded-xl overflow-hidden">
            {children}
        </div>
    </div>
);

const SettingsItem = ({ label, value }) => (
    <div className="p-4 border-b border-gray-700/50 last:border-b-0 flex justify-between items-center cursor-pointer hover:bg-white/5 transition-colors">
        <span className="font-medium">{label}</span>
        {value && <span className="text-gray-400 text-sm">{value}</span>}
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-gray-500">
            <path d="m9 18 6-6-6-6" />
        </svg>
    </div>
);

const BottomNav = ({ activeTab, setActiveTab }) => {
    const tabs = [
        { id: 'dashboard', label: 'Home', icon: <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect width="7" height="9" x="3" y="3" rx="1" /><rect width="7" height="5" x="14" y="3" rx="1" /><rect width="7" height="9" x="14" y="12" rx="1" /><rect width="7" height="5" x="3" y="16" rx="1" /></svg> },
        { id: 'advocate', label: 'Savings', icon: <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="12" x2="12" y1="2" y2="22" /><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" /></svg> },
        { id: 'fiduciary', label: 'Vault', icon: <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></svg> },
        { id: 'activity', label: 'Activity', icon: <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2" /></svg> },
        { id: 'settings', label: 'Settings', icon: <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="3" /><path d="M12 1v6m0 6v6" /></svg> },
    ];

    return (
        <nav className="fixed bottom-0 left-0 right-0 w-full bg-[#0f172a]/95 backdrop-blur-md border-t border-gray-800 z-50 shadow-2xl">
            <div className="flex justify-around items-center px-1 py-2 max-w-screen-xl mx-auto">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex flex-col items-center justify-center gap-1 rounded-lg transition-all touch-manipulation
                            px-2 py-2 min-w-[60px] flex-1 max-w-[100px]
                            ${activeTab === tab.id
                                ? 'text-yellow-400 bg-yellow-400/10'
                                : 'text-gray-500 active:text-gray-300'
                            }`}
                        aria-label={tab.label}
                    >
                        <div className="flex-shrink-0">
                            {tab.icon}
                        </div>
                        <span className="text-[9px] sm:text-[10px] font-medium leading-none truncate w-full text-center">
                            {tab.label}
                        </span>
                    </button>
                ))}
            </div>
        </nav>
    );
};

export default MainApp;
