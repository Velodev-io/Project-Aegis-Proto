import React from 'react';
import { useNavigate } from 'react-router-dom';

const UIShowcase = () => {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white p-8">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-5xl font-bold mb-4 text-center bg-gradient-to-r from-yellow-400 to-yellow-600 bg-clip-text text-transparent">
                    Project Aegis UI Showcase
                </h1>
                <p className="text-center text-gray-300 mb-12 text-lg">
                    Navigate to the newly implemented UI screens
                </p>

                <div className="grid md:grid-cols-2 gap-6">
                    {/* Trust Vault Card */}
                    <div className="bg-slate-800/50 backdrop-blur-lg border border-yellow-500/30 rounded-2xl p-8 hover:border-yellow-500/60 transition-all hover:scale-105 cursor-pointer"
                        onClick={() => navigate('/trust-vault')}>
                        <div className="w-16 h-16 bg-gradient-to-br from-yellow-500 to-yellow-700 rounded-full flex items-center justify-center mb-4 mx-auto">
                            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                                <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
                                <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                            </svg>
                        </div>
                        <h2 className="text-2xl font-bold text-yellow-400 text-center mb-2">Trust Vault Permissions</h2>
                        <p className="text-gray-400 text-center text-sm mb-4">
                            Granular permission controls with toggle switches
                        </p>
                        <div className="flex items-center justify-center gap-2 text-yellow-500 text-sm font-semibold">
                            <span>View Screen</span>
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="m9 18 6-6-6-6" />
                            </svg>
                        </div>
                    </div>

                    {/* Advocate Savings Card */}
                    <div className="bg-slate-800/50 backdrop-blur-lg border border-green-500/30 rounded-2xl p-8 hover:border-green-500/60 transition-all hover:scale-105 cursor-pointer"
                        onClick={() => navigate('/advocate-savings')}>
                        <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-700 rounded-full flex items-center justify-center mb-4 mx-auto">
                            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                                <line x1="12" x2="12" y1="2" y2="22" />
                                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
                            </svg>
                        </div>
                        <h2 className="text-2xl font-bold text-green-400 text-center mb-2">Advocate Savings Dashboard</h2>
                        <p className="text-gray-400 text-center text-sm mb-4">
                            Savings trends and negotiation history
                        </p>
                        <div className="flex items-center justify-center gap-2 text-green-500 text-sm font-semibold">
                            <span>View Screen</span>
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="m9 18 6-6-6-6" />
                            </svg>
                        </div>
                    </div>

                    {/* Urgent Approval Demo */}
                    <div className="bg-slate-800/50 backdrop-blur-lg border border-red-500/30 rounded-2xl p-8 hover:border-red-500/60 transition-all hover:scale-105 cursor-pointer"
                        onClick={() => {
                            if (window.triggerUrgentModal) {
                                window.triggerUrgentModal();
                            } else {
                                alert('Navigate to any page first, then click this button to trigger the modal');
                            }
                        }}>
                        <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-red-700 rounded-full flex items-center justify-center mb-4 mx-auto">
                            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                                <path d="M12 9v4" />
                                <path d="M12 17h.01" />
                            </svg>
                        </div>
                        <h2 className="text-2xl font-bold text-red-400 text-center mb-2">Urgent Approval Modal</h2>
                        <p className="text-gray-400 text-center text-sm mb-4">
                            Critical transaction alert (Demo)
                        </p>
                        <div className="flex items-center justify-center gap-2 text-red-500 text-sm font-semibold">
                            <span>Trigger Modal</span>
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="m9 18 6-6-6-6" />
                            </svg>
                        </div>
                    </div>

                    {/* Senior Dashboard */}
                    <div className="bg-slate-800/50 backdrop-blur-lg border border-blue-500/30 rounded-2xl p-8 hover:border-blue-500/60 transition-all hover:scale-105 cursor-pointer"
                        onClick={() => navigate('/senior-dashboard')}>
                        <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-700 rounded-full flex items-center justify-center mb-4 mx-auto">
                            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                                <rect width="7" height="9" x="3" y="3" rx="1" />
                                <rect width="7" height="5" x="14" y="3" rx="1" />
                                <rect width="7" height="9" x="14" y="12" rx="1" />
                                <rect width="7" height="5" x="3" y="16" rx="1" />
                            </svg>
                        </div>
                        <h2 className="text-2xl font-bold text-blue-400 text-center mb-2">Senior Dashboard</h2>
                        <p className="text-gray-400 text-center text-sm mb-4">
                            Main dashboard (existing)
                        </p>
                        <div className="flex items-center justify-center gap-2 text-blue-500 text-sm font-semibold">
                            <span>View Screen</span>
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="m9 18 6-6-6-6" />
                            </svg>
                        </div>
                    </div>
                </div>

                <div className="mt-12 bg-slate-800/30 border border-gray-700 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-3 text-yellow-400">📍 Direct Links</h3>
                    <div className="space-y-2 text-sm">
                        <div className="flex items-center gap-2">
                            <span className="text-gray-400">Trust Vault:</span>
                            <code className="bg-slate-900 px-2 py-1 rounded text-yellow-300">http://localhost:5173/trust-vault</code>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-gray-400">Advocate Savings:</span>
                            <code className="bg-slate-900 px-2 py-1 rounded text-green-300">http://localhost:5173/advocate-savings</code>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UIShowcase;
