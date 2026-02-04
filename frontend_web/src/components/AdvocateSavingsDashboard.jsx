import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const AdvocateSavingsDashboard = () => {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-[#0f172a] text-white font-sans flex flex-col pb-24">
            {/* Header */}
            <div className="p-6 text-center">
                <h1 className="text-3xl font-bold tracking-tight">Advocate Savings<br />Dashboard</h1>
            </div>

            {/* Total Savings Card */}
            <div className="px-6 mb-8">
                <div className="bg-[#6ee7b7] text-[#0f172a] rounded-2xl p-8 text-center shadow-lg transform hover:scale-[1.02] transition-transform duration-300">
                    <h2 className="text-6xl font-bold tracking-tighter mb-2">$1240.00</h2>
                    <p className="text-lg font-medium opacity-80 mb-2">Total Saved This Year</p>
                    <div className="inline-flex items-center gap-1 bg-[#0f172a]/10 px-3 py-1 rounded-full text-sm font-semibold">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="m18 15-6-6-6 6" /></svg>
                        <span>+15% vs last year</span>
                    </div>
                </div>
            </div>

            {/* Monthly Trend Chart */}
            <div className="px-6 mb-8">
                <h3 className="text-xl font-bold mb-6">Monthly Savings Trend</h3>

                {/* Simple CSS Bar Chart */}
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
            <div className="px-6 flex-1">
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

            {/* We reuse the bottom nav layout but for Advocate specifically, usually the mockup didn't show it but good to have consistency */}
            <BottomNavigation active="dashboard" navigate={navigate} />

        </div>
    );
};

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

const BottomNavigation = ({ active, navigate }) => {
    // Helper for active styles
    const getStyle = (name) => active === name ? "text-[#6ee7b7]" : "text-gray-500 hover:text-gray-300";

    return (
        <div className="fixed bottom-0 left-0 w-full bg-[#0f172a] border-t border-gray-800 p-4 pb-8 flex justify-around items-center z-20 shadow-2xl shadow-black">
            <button onClick={() => navigate('/advocate-savings')} className={`flex flex-col items-center gap-1 ${getStyle('dashboard')}`}>
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="7" height="9" x="3" y="3" rx="1" /><rect width="7" height="5" x="14" y="3" rx="1" /><rect width="7" height="9" x="14" y="12" rx="1" /><rect width="7" height="5" x="3" y="16" rx="1" /></svg>
                <span className="text-xs font-medium">Dashboard</span>
            </button>
            <button onClick={() => navigate('/trust-vault')} className={`flex flex-col items-center gap-1 ${getStyle('fiduciary')}`}>
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></svg>
                <span className="text-xs font-medium">Fiduciary</span>
            </button>
            <button className={`flex flex-col items-center gap-1 ${getStyle('activity')}`}>
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2" /></svg>
                <span className="text-xs font-medium">Activity</span>
            </button>
            <button className={`flex flex-col items-center gap-1 ${getStyle('settings')}`}>
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.38a2 2 0 0 0-.73-2.73l-.15-.1a2 2 0 0 1-1-1.72v-.51a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" /><circle cx="12" cy="12" r="3" /></svg>
                <span className="text-xs font-medium">Settings</span>
            </button>
        </div>
    );
};

export default AdvocateSavingsDashboard;
