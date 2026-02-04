import React from 'react';
import { useNavigate } from 'react-router-dom';

const LoginPage = ({ darkMode, onToggleDarkMode }) => {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 flex items-center justify-center p-4">
            {/* Dark Mode Toggle */}
            <button
                onClick={onToggleDarkMode}
                className="fixed top-6 right-6 flex items-center justify-center h-12 w-12 rounded-full bg-white dark:bg-slate-800 shadow-lg hover:shadow-xl transition-all z-50"
                aria-label="Toggle dark mode"
            >
                <span className="material-symbols-outlined text-slate-700 dark:text-slate-200">
                    {darkMode ? 'light_mode' : 'dark_mode'}
                </span>
            </button>

            <div className="w-full max-w-md">
                {/* Header */}
                <div className="text-center mb-12">
                    <div className="flex items-center justify-center mb-6">
                        <div className="bg-primary/10 p-4 rounded-full border-4 border-primary/20">
                            <span className="material-symbols-outlined text-primary text-6xl">verified_user</span>
                        </div>
                    </div>
                    <h1 className="text-5xl font-bold text-slate-900 dark:text-white mb-3">
                        Project Aegis
                    </h1>
                    <p className="text-xl text-slate-600 dark:text-slate-400">
                        Your Cognitive Fiduciary
                    </p>
                </div>

                {/* Simple Buttons */}
                <div className="space-y-4">
                    <button
                        onClick={() => navigate('/senior-dashboard')}
                        className="w-full py-6 bg-primary text-white rounded-xl font-bold text-2xl shadow-lg shadow-primary/30 hover:bg-primary/90 transition-all active:scale-95"
                    >
                        Continue as Senior
                    </button>

                    <button
                        onClick={() => navigate('/caregiver')}
                        className="w-full py-6 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl font-bold text-2xl shadow-lg shadow-purple-600/30 hover:from-purple-700 hover:to-blue-700 transition-all active:scale-95"
                    >
                        Continue as Caregiver
                    </button>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
