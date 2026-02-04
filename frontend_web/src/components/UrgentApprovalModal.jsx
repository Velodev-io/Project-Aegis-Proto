import React, { useEffect } from 'react';

const UrgentApprovalModal = ({ isOpen, onClose, details, onApprove, onDecline }) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop with blur */}
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity" onClick={onClose}></div>

            {/* Modal Content */}
            <div className="bg-white rounded-3xl w-full max-w-sm shadow-2xl relative z-10 overflow-hidden animate-in fade-in zoom-in duration-300">

                <div className="p-6 text-center">
                    {/* Alert Icon */}
                    <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <div className="w-12 h-12 bg-red-600 rounded-full flex items-center justify-center shadow-red-500/50 shadow-lg">
                            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M12 9v4" /><path d="M12 17h.01" /></svg>
                        </div>
                    </div>

                    <h2 className="text-2xl font-bold text-red-600 mb-2 leading-tight">Urgent Approval Required</h2>

                    <p className="text-gray-600 text-[15px] mb-6 leading-relaxed">
                        A large or suspicious transaction needs your immediate attention.
                    </p>

                    <div className="bg-gray-50 rounded-xl p-4 mb-6 border border-gray-100">
                        <p className="text-gray-800 font-bold text-lg mb-1">Large Transfer Request: {details.amount}</p>
                        <p className="text-gray-500 text-sm">To: {details.recipient}</p>
                        <p className="text-gray-400 text-xs mt-1">{details.timestamp}</p>
                    </div>

                    <div className="space-y-3">
                        {/* Approve Button */}
                        <button
                            onClick={onApprove}
                            className="w-full bg-[#dc2626] hover:bg-red-700 text-white font-bold py-3.5 rounded-xl shadow-lg shadow-red-200 active:scale-[0.98] transition-all flex items-center justify-center gap-2"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 10a.5.5 0 0 0 1 0V9a.5.5 0 0 0-1 0v1Z" /><path d="M14 10a.5.5 0 0 0 1 0V9a.5.5 0 0 0-1 0v1Z" /><path d="M10 7a2 2 0 1 0 4 0" /><line x1="9" x2="9.01" y1="13" y2="13" /><line x1="15" x2="15.01" y1="13" y2="13" /><rect width="18" height="18" x="3" y="3" rx="2" ry="2" /><path d="M7 21v-3a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v3" /></svg>
                            Approve with Face ID
                        </button>

                        {/* Decline Button */}
                        <button
                            onClick={onDecline}
                            className="w-full bg-gray-600 hover:bg-gray-700 text-white font-bold py-3.5 rounded-xl shadow-lg active:scale-[0.98] transition-all flex items-center justify-center gap-2"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" /><line x1="4.93" x2="19.07" y1="4.93" y2="19.07" /></svg>
                            Decline & Block
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UrgentApprovalModal;
