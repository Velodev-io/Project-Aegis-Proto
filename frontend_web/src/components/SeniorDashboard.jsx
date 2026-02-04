import React from 'react';

const SeniorDashboard = ({ onToggleDarkMode, darkMode, onNavigateToAdvocate, onNavigateToFamily, onNavigateToHelp, onNavigateToSentinel }) => {
    return (
        <div className="relative flex h-auto min-h-screen w-full flex-col group/design-root overflow-x-hidden max-w-[480px] mx-auto bg-white dark:bg-background-dark shadow-xl">
            {/* TopAppBar */}
            <div className="flex items-center p-4 pb-2 justify-between sticky top-0 bg-white/80 dark:bg-background-dark/80 backdrop-blur-md z-10">
                <div className="flex size-14 shrink-0 items-center">
                    <div
                        className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10 border-2 border-primary/20"
                        style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuC8YG5fjA5Is6XwAzQmUEJrbLU8-zrdCzZc82nyaGMVV8onfaVeCGazDV_J4fcp5wd8UGFMTmknODxP5kl_ZPL4ODRKfM-mXcSCgYflDDEAkH41o2-ptI8paRzEgVeAX0_CM3boPikr320IfNjFbdX2Lc47MbSSfzbb_KFXKhHYu7ChYS370l44pg3O5Bc_eYtnr6UjMlyoN0WUu0-8zc6_MMHrUSyVoHVRW7bwXRWZxQlUnwjfcVUCFBWUq103q8uDrd5VYJacDh33")' }}
                        aria-label="A smiling senior man profile picture"
                    />
                </div>
                <h2 className="text-[#0d131b] dark:text-slate-50 text-xl font-bold leading-tight tracking-tight flex-1 ml-3">
                    Hello, Robert
                </h2>
                <div className="flex w-12 items-center justify-end">
                    <button
                        onClick={onToggleDarkMode}
                        className="flex cursor-pointer items-center justify-center rounded-lg h-10 w-10 bg-transparent text-[#0d131b] dark:text-slate-50 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                        aria-label="Toggle dark mode"
                    >
                        <span className="material-symbols-outlined">
                            {darkMode ? 'light_mode' : 'dark_mode'}
                        </span>
                    </button>
                </div>
            </div>

            {/* Shield Hero Section */}
            <div className="flex flex-col items-center justify-center py-10 px-4">
                <div className="relative flex items-center justify-center">
                    {/* Glowing Circle Background */}
                    <div className="absolute w-48 h-48 bg-primary/10 dark:bg-primary/20 rounded-full glow-effect"></div>
                    {/* Shield Icon */}
                    <div className="relative z-0 bg-white dark:bg-slate-800 p-8 rounded-full shadow-lg border-4 border-primary">
                        <span className="material-symbols-outlined big-icon text-primary">verified_user</span>
                    </div>
                </div>
                <h1 className="text-[#0d131b] dark:text-white tracking-tight text-[36px] font-bold leading-tight px-4 text-center pt-8">
                    Your Shield is Active
                </h1>
                <p className="text-primary font-semibold text-lg mt-1">Protection is running</p>
            </div>

            {/* SingleButton: Main Action */}
            <div className="px-6 py-6">
                <button className="flex w-full cursor-pointer items-center justify-center overflow-hidden rounded-xl h-20 px-8 bg-primary text-white gap-4 shadow-lg active:scale-95 transition-transform">
                    <span className="material-symbols-outlined !text-[40px]">mic</span>
                    <span className="text-2xl font-bold">Talk to Aegis</span>
                </button>
                <p className="text-center text-slate-500 dark:text-slate-400 mt-4 text-lg">
                    Tap to ask a question or check a call
                </p>
            </div>

            {/* Section Header */}
            <div className="px-6 pt-6">
                <h3 className="text-[#0d131b] dark:text-white text-2xl font-bold leading-tight tracking-tight">
                    Daily Status
                </h3>
            </div>

            {/* Status Cards */}
            <div className="px-6 py-4 space-y-4">
                {/* Card 1: Scams Blocked - Now Clickable */}
                <div
                    onClick={onNavigateToSentinel}
                    className="bg-white dark:bg-slate-800 border-2 border-slate-100 dark:border-slate-700 rounded-xl p-5 flex items-center justify-between shadow-sm cursor-pointer hover:border-green-500/30 hover:shadow-md transition-all active:scale-[0.98]"
                >
                    <div className="flex items-center gap-4">
                        <div className="bg-green-100 dark:bg-green-900/30 p-3 rounded-lg">
                            <span className="material-symbols-outlined text-green-600 dark:text-green-400">shield</span>
                        </div>
                        <div>
                            <p className="text-slate-500 dark:text-slate-400 text-base font-medium">
                                Sentinel Security
                            </p>
                            <p className="text-2xl font-bold text-slate-900 dark:text-white">Active Protection</p>
                        </div>
                    </div>
                    <span className="material-symbols-outlined text-slate-300">chevron_right</span>
                </div>

                {/* Card 2: Next Bill - Now Clickable */}
                <div
                    onClick={onNavigateToAdvocate}
                    className="bg-white dark:bg-slate-800 border-2 border-slate-100 dark:border-slate-700 rounded-xl p-5 flex items-center justify-between shadow-sm cursor-pointer hover:border-primary/30 hover:shadow-md transition-all active:scale-[0.98]"
                >
                    <div className="flex items-center gap-4">
                        <div className="bg-blue-100 dark:bg-blue-900/30 p-3 rounded-lg">
                            <span className="material-symbols-outlined text-primary">receipt_long</span>
                        </div>
                        <div>
                            <p className="text-slate-500 dark:text-slate-400 text-base font-medium">
                                Next Bill: Electric
                            </p>
                            <div className="flex items-center gap-2">
                                <p className="text-2xl font-bold text-slate-900 dark:text-white">$85.00</p>
                                <span className="bg-primary/10 text-primary text-xs font-bold px-2 py-0.5 rounded-full flex items-center gap-1 border border-primary/20">
                                    <span className="material-symbols-outlined !text-sm">check_circle</span>
                                    VERIFIED
                                </span>
                            </div>
                        </div>
                    </div>
                    <span className="material-symbols-outlined text-slate-300">chevron_right</span>
                </div>
            </div>

            {/* Spacer for Bottom Nav */}
            <div className="h-24"></div>

            {/* Navigation Bar */}
            <div className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-[480px] bg-white dark:bg-background-dark border-t border-slate-100 dark:border-slate-800 flex justify-around items-center py-4 px-2 shadow-[0_-4px_20px_rgba(0,0,0,0.05)]">
                <button className="flex flex-col items-center gap-1 text-primary">
                    <span className="material-symbols-outlined">home</span>
                    <span className="text-sm font-bold">Home</span>
                </button>
                <button
                    onClick={onNavigateToFamily}
                    className="flex flex-col items-center gap-1 text-slate-400 dark:text-slate-500 hover:text-primary dark:hover:text-primary transition-colors cursor-pointer"
                >
                    <span className="material-symbols-outlined">family_restroom</span>
                    <span className="text-sm font-bold">Family</span>
                </button>
                <button
                    onClick={onNavigateToHelp}
                    className="flex flex-col items-center gap-1 text-red-500 hover:text-red-600 transition-colors cursor-pointer"
                >
                    <span className="material-symbols-outlined !fill-1">emergency</span>
                    <span className="text-sm font-bold">Help</span>
                </button>
            </div>
        </div>
    );
};

export default SeniorDashboard;
