import React from 'react';

const ActivityTimelineItem = ({ icon, iconBg, iconColor, title, time, description, isLast }) => {
    return (
        <div className={`relative pl-8 pb-6 ${!isLast ? 'border-l-2 border-slate-100 dark:border-slate-800' : ''} ml-3`}>
            <div className={`absolute -left-[17px] top-0 ${iconBg} ${iconColor} p-1 rounded-full border-4 border-background-light dark:border-background-dark`}>
                <span className="material-symbols-outlined text-[20px] block">{icon}</span>
            </div>
            <div className="flex flex-col gap-1">
                <div className="flex justify-between items-center">
                    <p className="text-sm font-bold text-[#0d131b] dark:text-white">{title}</p>
                    <span className="text-xs text-slate-400">{time}</span>
                </div>
                <p className="text-sm text-slate-500 dark:text-slate-400">{description}</p>
            </div>
        </div>
    );
};

const CaregiverDashboard = ({ darkMode, onToggleDarkMode }) => {
    const activities = [
        {
            icon: 'block',
            iconBg: 'bg-red-100 dark:bg-red-900/20',
            iconColor: 'text-red-600',
            title: 'Aegis blocked a scam call',
            time: '2:00 PM',
            description: "Identified as: 'Social Security Administration Phishing'. Phone line remains secure."
        },
        {
            icon: 'shopping_cart',
            iconBg: 'bg-blue-100 dark:bg-blue-900/20',
            iconColor: 'text-blue-600',
            title: 'Grocery Purchase',
            time: '11:30 AM',
            description: 'Spend: $64.20 at Whole Foods Market. Within normal budget limits.'
        },
        {
            icon: 'description',
            iconBg: 'bg-green-100 dark:bg-green-900/20',
            iconColor: 'text-green-600',
            title: 'Document Verified',
            time: 'Yesterday',
            description: 'Medicare 2024 Benefits statement successfully uploaded and analyzed for changes.'
        }
    ];

    return (
        <div className="min-h-screen bg-background-light dark:bg-background-dark text-[#0d131b] dark:text-slate-100">
            {/* Top Navigation Bar */}
            <div className="sticky top-0 z-50 bg-background-light/80 dark:bg-background-dark/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800">
                <div className="flex items-center p-4 justify-between">
                    <div className="flex items-center gap-3">
                        <div className="bg-primary/10 p-1 rounded-full border border-primary/20">
                            <div
                                className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10"
                                style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuAfDbhFVVEB0_ViVv086yGNw-oqoyyljS0tUEktPcEpGU4x5xH0GP2sa3hV4e7rVag5m-f6W6ODZR8TKm_nQqOR2aZemyC39oMApuTOTYhZ4nt45ZG5lGWEXHgpygFGEDNC-wMhw7ywcL4P03MJbXsVVswQZ2goFak0wdMNvbu20lLZOCRgjINbU5gVXhpoXdeK5uJXzhXPg4iK7dYiJya0dPHHVPKwzHeGdmpj9WUQz6VddA_itVwl-PZ6I2AwB2WIohlYDhQZadqD")' }}
                                aria-label="Senior user profile picture"
                            />
                        </div>
                        <div className="flex flex-col">
                            <h2 className="text-[#0d131b] dark:text-white text-lg font-bold leading-tight tracking-[-0.015em]">
                                Robert's Account
                            </h2>
                            <div className="flex items-center gap-1.5">
                                <span className="size-2 rounded-full bg-green-500"></span>
                                <p className="text-xs font-medium text-[#4c6c9a] dark:text-slate-400">
                                    Security: Active &amp; Protected
                                </p>
                            </div>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <button className="flex size-10 items-center justify-center rounded-full bg-white dark:bg-slate-800 shadow-sm text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                            <span className="material-symbols-outlined">shield_with_heart</span>
                        </button>
                        <button className="relative flex size-10 items-center justify-center rounded-full bg-white dark:bg-slate-800 shadow-sm text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                            <span className="material-symbols-outlined">notifications</span>
                            <span className="absolute top-2 right-2 size-2 bg-red-500 rounded-full border-2 border-white dark:border-slate-800"></span>
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Content Scroll Area */}
            <main className="max-w-md mx-auto pb-24">
                {/* Stats Section */}
                <div className="p-4 flex flex-col gap-4">
                    <div className="flex min-w-[158px] flex-col gap-3 rounded-xl p-6 bg-white dark:bg-slate-800 shadow-sm border border-slate-200 dark:border-slate-700">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-slate-500 dark:text-slate-400 text-sm font-medium uppercase tracking-wider">
                                    Peace of Mind Score
                                </p>
                                <p className="text-[#0d131b] dark:text-white tracking-tight text-4xl font-bold mt-1 leading-tight">
                                    94<span className="text-xl text-slate-400">/100</span>
                                </p>
                            </div>
                            <div className="size-14 rounded-full border-4 border-primary/20 flex items-center justify-center relative">
                                <div className="absolute inset-0 rounded-full border-4 border-primary border-t-transparent -rotate-45"></div>
                                <span className="material-symbols-outlined text-primary">verified_user</span>
                            </div>
                        </div>
                        <div className="flex items-center gap-2 pt-2 border-t border-slate-100 dark:border-slate-700">
                            <span className="text-green-600 dark:text-green-400 material-symbols-outlined text-sm">trending_up</span>
                            <p className="text-green-600 dark:text-green-400 text-sm font-semibold leading-normal">
                                +2% from last week
                            </p>
                            <p className="text-slate-400 dark:text-slate-500 text-sm ml-auto font-normal">Highly Secure</p>
                        </div>
                    </div>
                </div>

                {/* Section Header: Actions */}
                <div className="flex items-center justify-between px-4 pt-4">
                    <h2 className="text-[#0d131b] dark:text-white text-xl font-bold leading-tight tracking-[-0.015em]">
                        Needs Approval
                    </h2>
                    <span className="px-2 py-0.5 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 text-xs font-bold rounded">
                        1 URGENT
                    </span>
                </div>

                {/* Approval Card */}
                <div className="p-4">
                    <div className="flex flex-col gap-4 rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-200 dark:border-slate-700">
                        <div className="flex gap-4">
                            <div className="flex-1 flex flex-col gap-1">
                                <div className="flex items-center gap-2 text-primary font-bold text-sm uppercase">
                                    <span className="material-symbols-outlined text-sm">account_balance_wallet</span>
                                    Financial Guard
                                </div>
                                <p className="text-[#0d131b] dark:text-white text-lg font-bold leading-tight">
                                    $500.00 Transfer Request
                                </p>
                                <p className="text-[#4c6c9a] dark:text-slate-400 text-sm font-normal">
                                    To: External Account • Chase ****4321
                                </p>
                            </div>
                            <div className="size-16 bg-slate-100 dark:bg-slate-700 rounded-lg flex items-center justify-center">
                                <span className="material-symbols-outlined text-slate-400 text-3xl">payments</span>
                            </div>
                        </div>
                        <div className="flex gap-3 pt-2">
                            <button className="flex-1 h-10 px-4 rounded-lg bg-primary text-white text-sm font-bold shadow-sm shadow-primary/20 hover:bg-primary/90 transition-colors">
                                Approve
                            </button>
                            <button className="flex-1 h-10 px-4 rounded-lg bg-slate-100 dark:bg-slate-700 text-[#0d131b] dark:text-white text-sm font-bold hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors">
                                Decline
                            </button>
                            <button className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                                <span className="material-symbols-outlined text-slate-500">more_horiz</span>
                            </button>
                        </div>
                    </div>
                </div>

                {/* Recent Activity Header */}
                <div className="flex items-center justify-between px-4 pt-6 pb-2">
                    <h2 className="text-[#0d131b] dark:text-white text-xl font-bold leading-tight tracking-[-0.015em]">
                        Recent Activity
                    </h2>
                    <button className="text-primary text-sm font-bold hover:underline">See All</button>
                </div>

                {/* Activity Timeline */}
                <div className="px-4 flex flex-col">
                    {activities.map((activity, index) => (
                        <ActivityTimelineItem
                            key={index}
                            {...activity}
                            isLast={index === activities.length - 1}
                        />
                    ))}
                </div>

                {/* Quick Access Banner */}
                <div className="p-4">
                    <div className="bg-gradient-to-r from-primary to-blue-700 rounded-xl p-5 text-white shadow-lg flex items-center gap-4">
                        <div className="flex-1">
                            <h3 className="font-bold text-lg mb-1">Administrative Help</h3>
                            <p className="text-blue-100 text-sm">
                                Robert has 2 upcoming bills due this Friday. Would you like to schedule them?
                            </p>
                        </div>
                        <button className="bg-white text-primary rounded-lg px-4 py-2 text-sm font-bold whitespace-nowrap hover:bg-blue-50 transition-colors">
                            View Bills
                        </button>
                    </div>
                </div>
            </main>

            {/* Bottom Navigation Bar (iOS Style) */}
            <nav className="fixed bottom-0 left-0 right-0 bg-white/90 dark:bg-slate-900/90 backdrop-blur-lg border-t border-slate-200 dark:border-slate-800 pb-8 pt-3 px-6">
                <div className="max-w-md mx-auto flex justify-between items-center">
                    <div className="flex flex-col items-center gap-1 text-primary">
                        <span className="material-symbols-outlined">dashboard</span>
                        <span className="text-[10px] font-bold">Dashboard</span>
                    </div>
                    <div className="flex flex-col items-center gap-1 text-slate-400 hover:text-primary transition-colors cursor-pointer">
                        <span className="material-symbols-outlined">account_balance</span>
                        <span className="text-[10px] font-bold">Fiduciary</span>
                    </div>
                    <div className="flex flex-col items-center gap-1 text-slate-400 hover:text-primary transition-colors cursor-pointer">
                        <span className="material-symbols-outlined">history</span>
                        <span className="text-[10px] font-bold">Activity</span>
                    </div>
                    <div className="flex flex-col items-center gap-1 text-slate-400 hover:text-primary transition-colors cursor-pointer">
                        <span className="material-symbols-outlined">settings</span>
                        <span className="text-[10px] font-bold">Settings</span>
                    </div>
                </div>
            </nav>
        </div>
    );
};

export default CaregiverDashboard;
