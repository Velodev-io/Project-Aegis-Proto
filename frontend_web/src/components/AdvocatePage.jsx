import React, { useState, useEffect } from 'react';
import { getAdvocateSummary, analyzeBill, uploadBillImage } from '../api';

const BattleCard = ({ status, statusColor, title, description, actionText, actionIcon, icon, iconBg, iconColor, isPrimary = false, onClick }) => {
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
                    <button
                        onClick={onClick}
                        className={`flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-9 px-4 flex-row-reverse ${isPrimary ? 'bg-primary text-white' : 'bg-primary/10 text-primary'} gap-1 text-sm font-bold leading-normal w-fit`}
                    >
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
    const [loading, setLoading] = useState(true);
    const [summary, setSummary] = useState(null);
    const [totalSaved, setTotalSaved] = useState(1240.00);
    const [battles, setBattles] = useState([]);
    const [uploading, setUploading] = useState(false);

    useEffect(() => {
        loadAdvocateData();
    }, []);

    const loadAdvocateData = async () => {
        setLoading(true);
        try {
            const summaryData = await getAdvocateSummary();
            setSummary(summaryData);

            // Load mock battles for now (in production, these would come from backend)
            setBattles([
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
            ]);
        } catch (error) {
            console.error('Error loading advocate data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleUploadBill = () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*,.pdf';
        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (file) {
                setUploading(true);
                try {
                    const result = await uploadBillImage(file);
                    if (result.analysis) {
                        alert(`Bill analyzed! Potential savings: $${result.analysis.potential_savings || 0}`);
                        loadAdvocateData(); // Reload data
                    } else if (result.error) {
                        alert('Backend is offline. Please try again later.');
                    }
                } catch (error) {
                    console.error('Error uploading bill:', error);
                    alert('Error uploading bill. Please try again.');
                } finally {
                    setUploading(false);
                }
            }
        };
        input.click();
    };

    const handleBattleClick = (battle) => {
        alert(`Viewing details for: ${battle.title}`);
    };

    if (loading) {
        return (
            <div className="relative flex h-screen w-full max-w-[430px] mx-auto flex-col bg-background-light dark:bg-background-dark items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                <p className="mt-4 text-gray-600 dark:text-gray-400">Loading Advocate...</p>
            </div>
        );
    }

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
                {summary && summary.status === 'operational' && (
                    <p className="text-xs text-green-600 dark:text-green-400 mt-1">● System Online</p>
                )}
                {summary && summary.status === 'offline' && (
                    <p className="text-xs text-red-600 dark:text-red-400 mt-1">● Backend Offline</p>
                )}
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
                        ${totalSaved.toFixed(2)}
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
                <BattleCard
                    key={index}
                    {...battle}
                    onClick={() => handleBattleClick(battle)}
                />
            ))}

            {/* Floating Action Button Space */}
            <div className="h-24 bg-transparent"></div>

            {/* Bottom Action Button */}
            <div className="fixed bottom-6 left-1/2 -translate-x-1/2 w-full max-w-[390px] px-4">
                <button
                    onClick={handleUploadBill}
                    disabled={uploading}
                    className="w-full flex items-center justify-center gap-2 bg-primary text-white rounded-xl h-14 font-bold text-lg shadow-lg shadow-primary/30 hover:bg-primary/90 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {uploading ? (
                        <>
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                            <span>Uploading...</span>
                        </>
                    ) : (
                        <>
                            <span className="material-symbols-outlined">add_circle</span>
                            <span>Upload New Bill or Claim</span>
                        </>
                    )}
                </button>
            </div>

            {/* Spacer for footer */}
            <div className="h-8 bg-background-light dark:bg-background-dark"></div>
        </div>
    );
};

export default AdvocatePage;
