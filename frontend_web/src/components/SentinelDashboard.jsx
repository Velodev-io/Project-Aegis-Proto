import React, { useState, useEffect } from 'react';
import { interceptVoiceCall, monitorTransaction, getSecurityLogs, getPendingApprovals } from '../api';

const SentinelDashboard = ({ darkMode, onBack }) => {
    const [activeTab, setActiveTab] = useState('monitor'); // monitor, logs, test
    const [securityLogs, setSecurityLogs] = useState([]);
    const [pendingApprovals, setPendingApprovals] = useState([]);
    const [loading, setLoading] = useState(false);

    // Test form states
    const [testTranscript, setTestTranscript] = useState('');
    const [testResult, setTestResult] = useState(null);
    const [transactionForm, setTransactionForm] = useState({
        amount: '',
        category: 'Electronics',
        merchant: ''
    });
    const [transactionResult, setTransactionResult] = useState(null);

    useEffect(() => {
        loadData();
    }, [activeTab]);

    const loadData = async () => {
        setLoading(true);
        try {
            const [logs, approvals] = await Promise.all([
                getSecurityLogs(20),
                getPendingApprovals()
            ]);
            setSecurityLogs(logs.logs || []);
            setPendingApprovals(approvals.approvals || []);
        } catch (error) {
            console.error('Error loading data:', error);
        }
        setLoading(false);
    };

    const handleTestCall = async () => {
        if (!testTranscript.trim()) return;

        setLoading(true);
        const result = await interceptVoiceCall(testTranscript);
        setTestResult(result);
        setLoading(false);

        // Reload logs
        setTimeout(loadData, 500);
    };

    const handleTestTransaction = async () => {
        if (!transactionForm.amount || !transactionForm.merchant) return;

        setLoading(true);
        const result = await monitorTransaction(
            parseFloat(transactionForm.amount),
            transactionForm.category,
            transactionForm.merchant
        );
        setTransactionResult(result);
        setLoading(false);

        // Reload logs
        setTimeout(loadData, 500);
    };

    const getRiskColor = (level) => {
        switch (level) {
            case 'CRITICAL': return 'text-red-600 dark:text-red-400';
            case 'HIGH': return 'text-orange-600 dark:text-orange-400';
            case 'MEDIUM': return 'text-yellow-600 dark:text-yellow-400';
            case 'LOW': return 'text-green-600 dark:text-green-400';
            default: return 'text-slate-600 dark:text-slate-400';
        }
    };

    const getActionColor = (action) => {
        switch (action) {
            case 'INTERVENE_AND_BLOCK': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
            case 'ACTIVATE_ANSWER_BOT': return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
            case 'ALLOW': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
            default: return 'bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-200';
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
            {/* Header */}
            <div className="sticky top-0 z-50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800">
                <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={onBack}
                            className="flex items-center justify-center h-10 w-10 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                        >
                            <span className="material-symbols-outlined text-slate-600 dark:text-slate-300">arrow_back</span>
                        </button>
                        <div>
                            <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                <span className="material-symbols-outlined text-primary">shield</span>
                                Sentinel Security
                            </h1>
                            <p className="text-sm text-slate-600 dark:text-slate-400">AI-Powered Protection System</p>
                        </div>
                    </div>
                    {pendingApprovals.length > 0 && (
                        <div className="bg-red-100 dark:bg-red-900 px-4 py-2 rounded-full">
                            <span className="text-red-800 dark:text-red-200 font-bold">
                                {pendingApprovals.length} Pending Approval{pendingApprovals.length !== 1 ? 's' : ''}
                            </span>
                        </div>
                    )}
                </div>
            </div>

            {/* Tabs */}
            <div className="max-w-7xl mx-auto px-4 py-6">
                <div className="flex gap-2 mb-6">
                    <button
                        onClick={() => setActiveTab('monitor')}
                        className={`px-6 py-3 rounded-xl font-bold transition-all ${activeTab === 'monitor'
                                ? 'bg-primary text-white shadow-lg'
                                : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700'
                            }`}
                    >
                        <span className="material-symbols-outlined inline-block mr-2">dashboard</span>
                        Monitor
                    </button>
                    <button
                        onClick={() => setActiveTab('logs')}
                        className={`px-6 py-3 rounded-xl font-bold transition-all ${activeTab === 'logs'
                                ? 'bg-primary text-white shadow-lg'
                                : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700'
                            }`}
                    >
                        <span className="material-symbols-outlined inline-block mr-2">history</span>
                        Security Logs
                    </button>
                    <button
                        onClick={() => setActiveTab('test')}
                        className={`px-6 py-3 rounded-xl font-bold transition-all ${activeTab === 'test'
                                ? 'bg-primary text-white shadow-lg'
                                : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700'
                            }`}
                    >
                        <span className="material-symbols-outlined inline-block mr-2">science</span>
                        Test System
                    </button>
                </div>

                {/* Monitor Tab */}
                {activeTab === 'monitor' && (
                    <div className="space-y-6">
                        {/* Pending Approvals */}
                        <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-xl">
                            <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                                <span className="material-symbols-outlined text-orange-600">pending_actions</span>
                                Pending Approvals ({pendingApprovals.length})
                            </h2>
                            {pendingApprovals.length === 0 ? (
                                <p className="text-slate-600 dark:text-slate-400">No pending approvals</p>
                            ) : (
                                <div className="space-y-4">
                                    {pendingApprovals.map((approval, idx) => (
                                        <div key={idx} className="border border-slate-200 dark:border-slate-700 rounded-xl p-4">
                                            <div className="flex justify-between items-start mb-2">
                                                <div>
                                                    <p className="font-bold text-slate-900 dark:text-white">
                                                        ${approval.transaction?.amount} - {approval.transaction?.merchant}
                                                    </p>
                                                    <p className="text-sm text-slate-600 dark:text-slate-400">
                                                        {approval.transaction?.category}
                                                    </p>
                                                </div>
                                                <span className={`px-3 py-1 rounded-full text-sm font-bold ${getRiskColor(approval.risk_level)}`}>
                                                    {approval.risk_level}
                                                </span>
                                            </div>
                                            <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">
                                                {approval.reasoning}
                                            </p>
                                            <div className="flex gap-2">
                                                <button className="px-4 py-2 bg-green-600 text-white rounded-lg font-bold hover:bg-green-700 transition-colors">
                                                    Approve
                                                </button>
                                                <button className="px-4 py-2 bg-red-600 text-white rounded-lg font-bold hover:bg-red-700 transition-colors">
                                                    Reject
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Recent Activity */}
                        <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-xl">
                            <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                                <span className="material-symbols-outlined text-blue-600">activity</span>
                                Recent Activity
                            </h2>
                            <div className="space-y-3">
                                {securityLogs.slice(0, 5).map((log, idx) => (
                                    <div key={idx} className="flex items-center gap-4 p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
                                        <span className={`material-symbols-outlined ${log.event_type === 'SCAM_CALL' ? 'text-red-600' : 'text-blue-600'
                                            }`}>
                                            {log.event_type === 'SCAM_CALL' ? 'phone' : 'credit_card'}
                                        </span>
                                        <div className="flex-1">
                                            <p className="font-bold text-slate-900 dark:text-white">
                                                {log.event_type === 'SCAM_CALL' ? 'Scam Call' : 'Transaction'}
                                            </p>
                                            <p className="text-sm text-slate-600 dark:text-slate-400">
                                                {new Date(log.timestamp).toLocaleString()}
                                            </p>
                                        </div>
                                        {log.fraud_score && (
                                            <span className="text-sm font-bold text-slate-600 dark:text-slate-400">
                                                Score: {log.fraud_score}/100
                                            </span>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {/* Logs Tab */}
                {activeTab === 'logs' && (
                    <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-xl">
                        <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4">
                            Security Audit Trail ({securityLogs.length} events)
                        </h2>
                        <div className="space-y-3">
                            {securityLogs.map((log, idx) => (
                                <div key={idx} className="border border-slate-200 dark:border-slate-700 rounded-xl p-4">
                                    <div className="flex justify-between items-start mb-2">
                                        <div className="flex items-center gap-3">
                                            <span className={`material-symbols-outlined ${log.event_type === 'SCAM_CALL' ? 'text-red-600' : 'text-blue-600'
                                                }`}>
                                                {log.event_type === 'SCAM_CALL' ? 'phone_in_talk' : 'account_balance_wallet'}
                                            </span>
                                            <div>
                                                <p className="font-bold text-slate-900 dark:text-white">
                                                    {log.event_type === 'SCAM_CALL' ? 'Scam Call Detected' : 'Transaction Monitored'}
                                                </p>
                                                <p className="text-sm text-slate-600 dark:text-slate-400">
                                                    {new Date(log.timestamp).toLocaleString()}
                                                </p>
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            {log.fraud_score !== null && (
                                                <p className="text-2xl font-bold text-primary">{log.fraud_score}/100</p>
                                            )}
                                            {log.risk_level && (
                                                <span className={`text-sm font-bold ${getRiskColor(log.risk_level)}`}>
                                                    {log.risk_level}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                    {log.action_taken && (
                                        <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold mb-2 ${getActionColor(log.action_taken)}`}>
                                            {log.action_taken.replace(/_/g, ' ')}
                                        </span>
                                    )}
                                    {log.approval_status && (
                                        <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold mb-2 ${log.approval_status === 'APPROVED' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                                                log.approval_status === 'PENDING_APPROVAL' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200' :
                                                    'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                                            }`}>
                                            {log.approval_status.replace(/_/g, ' ')}
                                        </span>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Test Tab */}
                {activeTab === 'test' && (
                    <div className="space-y-6">
                        {/* Test Scam Call */}
                        <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-xl">
                            <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                                <span className="material-symbols-outlined text-red-600">phone_in_talk</span>
                                Test Scam Detection
                            </h2>
                            <textarea
                                value={testTranscript}
                                onChange={(e) => setTestTranscript(e.target.value)}
                                placeholder="Enter a call transcript to test scam detection..."
                                className="w-full p-4 border border-slate-300 dark:border-slate-600 rounded-xl bg-white dark:bg-slate-700 text-slate-900 dark:text-white mb-4"
                                rows={4}
                            />
                            <button
                                onClick={handleTestCall}
                                disabled={loading || !testTranscript.trim()}
                                className="w-full py-3 bg-primary text-white rounded-xl font-bold hover:bg-primary/90 transition-all disabled:opacity-50"
                            >
                                {loading ? 'Analyzing...' : 'Analyze Call'}
                            </button>

                            {testResult && (
                                <div className="mt-4 p-4 bg-slate-50 dark:bg-slate-700 rounded-xl">
                                    <div className="flex justify-between items-center mb-3">
                                        <p className="text-3xl font-bold text-primary">{testResult.fraud_score}/100</p>
                                        <span className={`px-4 py-2 rounded-full font-bold ${getActionColor(testResult.action)}`}>
                                            {testResult.action.replace(/_/g, ' ')}
                                        </span>
                                    </div>
                                    <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">{testResult.reasoning}</p>
                                    {testResult.indicators && testResult.indicators.length > 0 && (
                                        <div>
                                            <p className="font-bold text-slate-900 dark:text-white mb-2">Detected Indicators:</p>
                                            <div className="flex flex-wrap gap-2">
                                                {testResult.indicators.map((ind, idx) => (
                                                    <span key={idx} className="px-3 py-1 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded-full text-xs font-bold">
                                                        {ind.category.replace(/_/g, ' ')} ({ind.weight})
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>

                        {/* Test Transaction */}
                        <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-xl">
                            <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                                <span className="material-symbols-outlined text-blue-600">credit_card</span>
                                Test Transaction Monitoring
                            </h2>
                            <div className="space-y-4">
                                <input
                                    type="number"
                                    value={transactionForm.amount}
                                    onChange={(e) => setTransactionForm({ ...transactionForm, amount: e.target.value })}
                                    placeholder="Amount ($)"
                                    className="w-full p-4 border border-slate-300 dark:border-slate-600 rounded-xl bg-white dark:bg-slate-700 text-slate-900 dark:text-white"
                                />
                                <select
                                    value={transactionForm.category}
                                    onChange={(e) => setTransactionForm({ ...transactionForm, category: e.target.value })}
                                    className="w-full p-4 border border-slate-300 dark:border-slate-600 rounded-xl bg-white dark:bg-slate-700 text-slate-900 dark:text-white"
                                >
                                    <option>Electronics</option>
                                    <option>Wire Transfer</option>
                                    <option>Groceries</option>
                                    <option>Gift Cards</option>
                                    <option>Cash Withdrawal</option>
                                </select>
                                <input
                                    type="text"
                                    value={transactionForm.merchant}
                                    onChange={(e) => setTransactionForm({ ...transactionForm, merchant: e.target.value })}
                                    placeholder="Merchant Name"
                                    className="w-full p-4 border border-slate-300 dark:border-slate-600 rounded-xl bg-white dark:bg-slate-700 text-slate-900 dark:text-white"
                                />
                                <button
                                    onClick={handleTestTransaction}
                                    disabled={loading || !transactionForm.amount || !transactionForm.merchant}
                                    className="w-full py-3 bg-primary text-white rounded-xl font-bold hover:bg-primary/90 transition-all disabled:opacity-50"
                                >
                                    {loading ? 'Analyzing...' : 'Monitor Transaction'}
                                </button>
                            </div>

                            {transactionResult && (
                                <div className="mt-4 p-4 bg-slate-50 dark:bg-slate-700 rounded-xl">
                                    <div className="flex justify-between items-center mb-3">
                                        <p className={`text-2xl font-bold ${getRiskColor(transactionResult.risk_level)}`}>
                                            {transactionResult.risk_level}
                                        </p>
                                        <span className="text-sm font-bold text-slate-600 dark:text-slate-400">
                                            Score: {transactionResult.risk_score}/100
                                        </span>
                                    </div>
                                    <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">{transactionResult.reasoning}</p>
                                    {transactionResult.flags && transactionResult.flags.length > 0 && (
                                        <div>
                                            <p className="font-bold text-slate-900 dark:text-white mb-2">Risk Flags:</p>
                                            <div className="flex flex-wrap gap-2">
                                                {transactionResult.flags.map((flag, idx) => (
                                                    <span key={idx} className="px-3 py-1 bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200 rounded-full text-xs font-bold">
                                                        {flag.replace(/_/g, ' ')}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default SentinelDashboard;
