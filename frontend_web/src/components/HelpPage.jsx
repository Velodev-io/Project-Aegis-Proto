import React from 'react';

const HelpPage = ({ onBack, darkMode }) => {
    return (
        <div className="relative flex h-full min-h-screen w-full flex-col max-w-[480px] mx-auto overflow-x-hidden bg-background-light dark:bg-background-dark">
            {/* TopAppBar */}
            <header className="flex items-center bg-background-light dark:bg-background-dark p-4 pb-2 justify-between sticky top-0 z-50">
                <div
                    onClick={onBack}
                    className="text-[#0d131b] dark:text-white flex size-12 shrink-0 items-center justify-start cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                >
                    <span className="material-symbols-outlined text-3xl">arrow_back_ios_new</span>
                </div>
                <h2 className="text-[#0d131b] dark:text-white text-xl font-bold leading-tight tracking-[-0.015em] flex-1 text-center pr-12">
                    Help & Support
                </h2>
            </header>

            {/* Main Content Scroll Area */}
            <main className="flex-1 px-4">
                {/* Emergency Action Card */}
                <div className="mt-4 bg-white dark:bg-slate-800 rounded-xl p-5 shadow-md border-2 border-primary/20">
                    <div className="flex flex-col gap-4">
                        <button className="flex min-w-[84px] cursor-pointer items-center justify-center overflow-hidden rounded-xl h-16 px-5 w-full bg-primary text-white gap-3 text-lg font-bold shadow-lg active:scale-[0.98] transition-transform hover:bg-primary/90">
                            <span className="material-symbols-outlined text-3xl">support_agent</span>
                            <span className="truncate">Call a Human Steward</span>
                        </button>
                        <p className="text-[#0d131b] dark:text-slate-300 text-base font-medium leading-normal text-center">
                            Available 24/7 for immediate assistance.
                        </p>
                    </div>
                </div>

                {/* SearchBar (Voice Enabled) */}
                <div className="py-6">
                    <label className="flex flex-col min-w-40 h-14 w-full">
                        <div className="flex w-full flex-1 items-stretch rounded-xl h-full shadow-sm">
                            <div className="text-[#4c6c9a] dark:text-slate-400 flex border-none bg-white dark:bg-slate-800 items-center justify-center pl-4 rounded-l-xl">
                                <span className="material-symbols-outlined">search</span>
                            </div>
                            <input
                                className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden text-[#0d131b] dark:text-white focus:outline-0 focus:ring-0 border-none bg-white dark:bg-slate-800 focus:border-none h-full placeholder:text-[#4c6c9a] dark:placeholder:text-slate-500 px-4 pl-2 text-lg font-normal"
                                placeholder="How can I help you today?"
                            />
                            <div className="text-primary flex border-none bg-white dark:bg-slate-800 items-center justify-center pr-4 rounded-r-xl cursor-pointer hover:text-primary/80 transition-colors">
                                <span className="material-symbols-outlined text-2xl">mic</span>
                            </div>
                        </div>
                    </label>
                </div>

                {/* Support Categories Header */}
                <div className="pb-2">
                    <h3 className="text-[#0d131b] dark:text-white text-xl font-bold leading-tight tracking-[-0.015em]">
                        Support Categories
                    </h3>
                </div>

                {/* Categories Grid */}
                <div className="grid grid-cols-2 gap-4 pb-8">
                    {/* Category Card: Report a Scam */}
                    <div className="flex flex-col items-center justify-center p-6 bg-white dark:bg-slate-800 rounded-xl border-2 border-transparent active:border-red-500 transition-colors shadow-md text-center gap-3 cursor-pointer hover:shadow-lg">
                        <div className="w-14 h-14 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center text-red-600 dark:text-red-400">
                            <span className="material-symbols-outlined text-4xl">gpp_maybe</span>
                        </div>
                        <span className="text-[#0d131b] dark:text-white font-bold text-base">Report a Scam</span>
                    </div>

                    {/* Category Card: Bill Questions */}
                    <div className="flex flex-col items-center justify-center p-6 bg-white dark:bg-slate-800 rounded-xl border-2 border-transparent active:border-primary transition-colors shadow-md text-center gap-3 cursor-pointer hover:shadow-lg">
                        <div className="w-14 h-14 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                            <span className="material-symbols-outlined text-4xl">receipt_long</span>
                        </div>
                        <span className="text-[#0d131b] dark:text-white font-bold text-base">Bill Questions</span>
                    </div>

                    {/* Category Card: App Tutorial */}
                    <div className="flex flex-col items-center justify-center p-6 bg-white dark:bg-slate-800 rounded-xl border-2 border-transparent active:border-primary transition-colors shadow-md text-center gap-3 cursor-pointer hover:shadow-lg">
                        <div className="w-14 h-14 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                            <span className="material-symbols-outlined text-4xl">play_lesson</span>
                        </div>
                        <span className="text-[#0d131b] dark:text-white font-bold text-base">App Tutorial</span>
                    </div>

                    {/* Category Card: Legal Help */}
                    <div className="flex flex-col items-center justify-center p-6 bg-white dark:bg-slate-800 rounded-xl border-2 border-transparent active:border-primary transition-colors shadow-md text-center gap-3 cursor-pointer hover:shadow-lg">
                        <div className="w-14 h-14 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                            <span className="material-symbols-outlined text-4xl">gavel</span>
                        </div>
                        <span className="text-[#0d131b] dark:text-white font-bold text-base">Legal Help</span>
                    </div>
                </div>

                {/* Peace of Mind Section */}
                <div className="bg-primary/5 dark:bg-primary/10 rounded-xl p-4 mb-8 flex items-center justify-center gap-3 border border-primary/10">
                    <span className="relative flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                    </span>
                    <p className="text-[#4c6c9a] dark:text-slate-300 text-sm font-bold tracking-wide uppercase">
                        System Status: Active & Secure
                    </p>
                </div>
            </main>

            {/* Bottom Navigation Spacer (for iOS Home Indicator) */}
            <div className="h-8 bg-background-light dark:bg-background-dark"></div>
        </div>
    );
};

export default HelpPage;
