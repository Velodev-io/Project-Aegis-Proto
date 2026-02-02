import React from 'react';

const BattleCard = ({ status, statusColor, title, description, actionText, actionIcon, icon, iconBg, iconColor, isPrimary = false }) => {
    const statusColors = {
        'In Progress': { dot: 'bg-amber-500', text: 'text-amber-600 dark:text-amber-400' },
        'Resolved': { dot: 'bg-green-500', text: 'text-green-600 dark:text-green-400' },
        'Review Required': { dot: 'bg-blue-500', text: 'text-blue-600 dark:text-blue-400' }
    };

    const colors = statusColors[status] || statusColors['In Progress'];

    return (
        <div className="px-4 py-2">
            <div className="flex items-stretch justify-between gap-4 rounded-xl bg-white dark:bg-gray-800 p-4 shadow-sm border border-gray-100 dark:border-gray-700">
                <div className="flex flex-[2_2_0px] flex-col justify-between gap-4">
                    <div className="flex flex-col gap-1">
                        <div className="flex items-center gap-2 mb-1">
                            <span className={`flex h-2 w-2 rounded-full ${colors.dot}`}></span>
                            <p className={`${colors.text} text-xs font-bold uppercase tracking-wider`}>{status}</p>
                        </div>
                        <p className="text-[#0d131b] dark:text-white text-base font-bold leading-tight">{title}</p>
                        <p className="text-gray-600 dark:text-gray-400 text-sm font-normal leading-relaxed">
                            {description}
                        </p>
                    </div>
                    <button className={`flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-9 px-4 flex-row-reverse ${isPrimary ? 'bg-primary text-white' : 'bg-primary/10 text-primary'} gap-1 text-sm font-bold leading-normal w-fit`}>
                        <span className="material-symbols-outlined text-[18px]">{actionIcon}</span>
                        <span className="truncate">{actionText}</span>
                    </button>
                </div>
                <div className={`w-24 h-24 ${iconBg} rounded-lg flex items-center justify-center border ${iconColor}`}>
                    <span className={`material-symbols-outlined ${iconColor.replace('border-', 'text-')} text-4xl`}>{icon}</span>
                </div>
            </div>
        </div>
    );
};

const AdvocatePage = ({ onBack, darkMode }) => {
    const battles = [
        {
            status: 'In Progress',
            title: 'Comcast Bill',
            description: (
                <>
                    Disputed. Found <span className="font-bold text-[#0d131b] dark:text-white">$20 overcharge</span>. Refund pending.
                </>
            ),
            actionText: 'View Details',
            actionIcon: 'chevron_right',
            icon: 'wifi',
            iconBg: 'bg-primary/5',
            iconColor: 'border-gray-100 dark:border-gray-700 text-primary',
            isPrimary: false
        },
        {
            status: 'Resolved',
            title: 'Medicare Claim',
            description: 'Approved. Full benefits applied to your provider account.',
            actionText: 'View Results',
            actionIcon: 'chevron_right',
            icon: 'medical_services',
            iconBg: 'bg-green-50 dark:bg-green-900/10',
            iconColor: 'border-green-100 dark:border-green-900/30 text-green-600',
            isPrimary: false
        },
        {
            status: 'Review Required',
            title: 'Property Tax Review',
            description: 'AI analysis complete. Potential savings found in regional assessment.',
            actionText: 'Approve Action',
            actionIcon: 'gavel',
            icon: 'home_work',
            iconBg: 'bg-blue-50 dark:bg-blue-900/10',
            iconColor: 'border-blue-100 dark:border-blue-900/30 text-blue-600',
            isPrimary: true
        }
    ];

    return (
        <div className="relative flex h-auto min-h-screen w-full max-w-[430px] mx-auto flex-col bg-background-light dark:bg-background-dark shadow-xl overflow-x-hidden">
            {/* TopAppBar */}
            <div className="flex items-center bg-background-light dark:bg-background-dark p-4 pb-2 justify-between sticky top-0 z-10 border-b border-gray-200 dark:border-gray-800">
                <div
                    onClick={onBack}
                    className="text-[#0d131b] dark:text-white flex size-12 shrink-0 items-center justify-start cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                >
                    <span className="material-symbols-outlined">arrow_back</span>
                </div>
                <h2 className="text-[#0d131b] dark:text-white text-lg font-bold leading-tight tracking-[-0.015em] flex-1 text-center">
                    Advocate
                </h2>
                <div className="flex w-12 items-center justify-end">
                    <button className="flex max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-12 bg-transparent text-[#0d131b] dark:text-white gap-2 text-base font-bold leading-normal tracking-[0.015em] min-w-0 p-0 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                        <span className="material-symbols-outlined">help</span>
                    </button>
                </div>
            </div>

            {/* Header Section */}
            <div className="px-4 py-4">
                <p className="text-sm font-medium text-primary uppercase tracking-wider mb-1">Aegis Fiduciary</p>
                <h1 className="text-2xl font-bold text-[#0d131b] dark:text-white">Bill Protection</h1>
            </div>

            {/* Stats Section */}
            <div className="flex flex-wrap gap-4 p-4 pt-0">
                <div className="flex min-w-[158px] flex-1 flex-col gap-2 rounded-xl p-6 bg-white dark:bg-gray-800 shadow-sm border border-gray-100 dark:border-gray-700">
                    <div className="flex items-center justify-between">
                        <p className="text-gray-500 dark:text-gray-400 text-sm font-medium leading-normal">
                            Total Saved This Year
                        </p>
                        <span className="material-symbols-outlined text-green-600">trending_up</span>
                    </div>
                    <p className="text-[#0d131b] dark:text-white tracking-tight text-4xl font-bold leading-tight">
                        $1,240.00
                    </p>
                    <div className="flex items-center gap-1">
                        <span className="text-[#07883b] text-sm font-bold leading-normal">+15%</span>
                        <span className="text-gray-400 text-xs font-normal leading-normal">vs last period</span>
                    </div>
                </div>
            </div>

            {/* Section Header */}
            <div className="flex items-center justify-between px-4 pb-2 pt-4">
                <h3 className="text-[#0d131b] dark:text-white text-lg font-bold leading-tight tracking-[-0.015em]">
                    Recent Battles
                </h3>
                <button className="text-primary text-sm font-semibold hover:underline">Filter</button>
            </div>

            {/* Battle Cards */}
            {battles.map((battle, index) => (
                <BattleCard key={index} {...battle} />
            ))}

            {/* Floating Action Button Space */}
            <div className="h-24 bg-transparent"></div>

            {/* Bottom Action Button */}
            <div className="fixed bottom-6 left-1/2 -translate-x-1/2 w-full max-w-[390px] px-4">
                <button className="w-full flex items-center justify-center gap-2 bg-primary text-white rounded-xl h-14 font-bold text-lg shadow-lg shadow-primary/30 hover:bg-primary/90 active:scale-95 transition-all">
                    <span className="material-symbols-outlined">add_circle</span>
                    <span>Upload New Bill or Claim</span>
                </button>
            </div>

            {/* Spacer for footer */}
            <div className="h-8 bg-background-light dark:bg-background-dark"></div>
        </div>
    );
};

export default AdvocatePage;
