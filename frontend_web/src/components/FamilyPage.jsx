import React from 'react';

const FamilyPage = ({ onBack, darkMode }) => {
    return (
        <div className="relative flex h-full min-h-screen w-full max-w-[480px] mx-auto flex-col bg-background-light dark:bg-background-dark overflow-x-hidden border-x border-gray-200 dark:border-gray-800">
            {/* TopAppBar */}
            <div className="flex items-center bg-background-light dark:bg-background-dark p-4 pb-2 justify-between sticky top-0 z-10">
                <div
                    onClick={onBack}
                    className="text-[#0d131b] dark:text-slate-100 flex size-12 shrink-0 items-center cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                >
                    <span className="material-symbols-outlined">arrow_back_ios</span>
                </div>
                <h2 className="text-[#0d131b] dark:text-white text-lg font-bold leading-tight tracking-[-0.015em] flex-1 text-center">
                    Family & Advocates
                </h2>
                <div className="flex w-12 items-center justify-end">
                    <button className="flex max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-12 bg-transparent text-[#0d131b] dark:text-white gap-2 text-base font-bold leading-normal tracking-[0.015em] min-w-0 p-0 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                        <span className="material-symbols-outlined">info</span>
                    </button>
                </div>
            </div>

            {/* HeadlineText */}
            <div className="px-4">
                <h2 className="text-[#0d131b] dark:text-white tracking-light text-[28px] font-bold leading-tight pb-2 pt-5">
                    Your Trusted Circle
                </h2>
            </div>

            {/* BodyText */}
            <div className="px-4">
                <p className="text-[#4c6c9a] dark:text-slate-400 text-lg font-normal leading-normal pb-6 pt-1">
                    These people help protect your finances and can assist in case of an emergency.
                </p>
            </div>

            {/* Advocates List */}
            <div className="flex flex-col gap-2 px-4 mb-6">
                {/* Sarah - Full Proxy */}
                <div className="flex items-center gap-4 bg-white dark:bg-slate-800/50 p-4 rounded-xl shadow-sm border border-gray-100 dark:border-slate-700 justify-between hover:border-primary/30 transition-colors cursor-pointer">
                    <div className="flex items-center gap-4">
                        <div
                            className="bg-center bg-no-repeat aspect-square bg-cover rounded-full h-16 w-16 border-2 border-primary/20"
                            style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuBG2yWeopmBoK6Xxkmhw7JkFytnyx53ZbWaEr2ID0GT4UtbFGDzeBFCQYJ6OdOeNasPRkmgMjoAXQjlbil8LdOuBVal0MrnmczLHqF3WytLOt0CouRSZMfsVW3yfVonE7ieNNPP6X1ZCq_U61e2wnuwcWXhFdLQAaWc4gQIRqozdPDcgKEz4OX4Z6y5bEAgxUl2ef5nVSNloeoZs664nZaFXFTIi-sY0NEow-l4AKZLipSUwf5wqfSxmqaCZd_0oetx6ATy0A38m-O7")' }}
                            aria-label="Portrait of a smiling woman with glasses"
                        />
                        <div className="flex flex-col justify-center">
                            <p className="text-[#0d131b] dark:text-white text-lg font-bold leading-tight">
                                Sarah (Daughter)
                            </p>
                            <div className="flex items-center gap-1 mt-1">
                                <span className="material-symbols-outlined text-primary text-sm">verified_user</span>
                                <p className="text-primary text-sm font-semibold leading-normal uppercase tracking-wider">
                                    Full Financial Proxy
                                </p>
                            </div>
                            <p className="text-[#4c6c9a] dark:text-slate-400 text-sm font-normal leading-normal mt-1">
                                Can manage bills and bank alerts
                            </p>
                        </div>
                    </div>
                    <div className="shrink-0">
                        <button className="p-2 text-slate-400">
                            <span className="material-symbols-outlined">chevron_right</span>
                        </button>
                    </div>
                </div>

                {/* Mark - Monitoring */}
                <div className="flex items-center gap-4 bg-white dark:bg-slate-800/50 p-4 rounded-xl shadow-sm border border-gray-100 dark:border-slate-700 justify-between mt-2 hover:border-primary/30 transition-colors cursor-pointer">
                    <div className="flex items-center gap-4">
                        <div
                            className="bg-center bg-no-repeat aspect-square bg-cover rounded-full h-16 w-16 border-2 border-primary/20"
                            style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuBnt9p9fFmrmW6-3VeFbj7VfZHfOCWUw4eHKuqwq1Bq9fISLBoni_92IJLUhtQX5bwc_NGo1NHgMGU8cI2egLRRfWVC-7x5-GKvCR5nnbdZUEUBbt23jJBOyqejmdM1vti3c3sy_6j4vOoRNB3FKC3Pxd8iBbVSC2KQZ1-Gtb8UvCJcic4nHn0MNEhKvj92wXb79WYx0Rdm0LbzLqhLM4t5jGvSPFGJ862DlRkk0WeYIU3cVX7BINV1IoTtUwNKCfYMudcIaTXLC7tT")' }}
                            aria-label="Portrait of a man in his 40s"
                        />
                        <div className="flex flex-col justify-center">
                            <p className="text-[#0d131b] dark:text-white text-lg font-bold leading-tight">
                                Mark (Son)
                            </p>
                            <div className="flex items-center gap-1 mt-1">
                                <span className="material-symbols-outlined text-slate-500 text-sm">visibility</span>
                                <p className="text-slate-500 text-sm font-semibold leading-normal uppercase tracking-wider">
                                    Can View Bills
                                </p>
                            </div>
                            <p className="text-[#4c6c9a] dark:text-slate-400 text-sm font-normal leading-normal mt-1">
                                Gets alerts for unusual activity
                            </p>
                        </div>
                    </div>
                    <div className="shrink-0">
                        <button className="p-2 text-slate-400">
                            <span className="material-symbols-outlined">chevron_right</span>
                        </button>
                    </div>
                </div>
            </div>

            {/* Action Button */}
            <div className="px-4 pb-8">
                <button className="w-full flex items-center justify-center gap-2 bg-primary text-white font-bold py-4 rounded-xl shadow-lg shadow-primary/20 active:scale-[0.98] transition-all hover:bg-primary/90">
                    <span className="material-symbols-outlined">person_add</span>
                    <span className="text-lg">Invite New Member</span>
                </button>
            </div>

            {/* Safety Net Section */}
            <div className="mx-4 mb-10 p-5 bg-blue-50 dark:bg-primary/10 rounded-xl border border-blue-100 dark:border-primary/20">
                <div className="flex items-center gap-3 mb-2">
                    <div className="bg-primary/20 p-2 rounded-lg">
                        <span className="material-symbols-outlined text-primary">security</span>
                    </div>
                    <h3 className="text-primary font-bold text-lg">Safety Net Active</h3>
                </div>
                <p className="text-[#0d131b] dark:text-slate-300 text-base leading-relaxed">
                    If Aegis detects a high-risk transaction or you trigger an SOS, <strong>Sarah</strong> and <strong>Mark</strong> will be notified instantly to help you verify the activity.
                </p>
                <div className="mt-4 flex -space-x-3">
                    <div
                        className="h-8 w-8 rounded-full border-2 border-white dark:border-slate-800 bg-cover"
                        style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuDOY7U_LUIiYR1y13cQkzxbpGIDxoWB9jRJ5xNO8U6gmD4b__lti6m1W6Y8mYyPJdNaoSXufpZiCQMw8Chqt5AzjbMbTlMzRk45TBj6CJGxGl4LD8lFca8vbaKhTTCz5la-eWSdSTdgO9Neh-QaA2G7tYK9WRLbAspFa-9l8VeZ68FfRmJDN0sOfx-HAB2jDddQDN1xn_d1esSUGMzrXNqg7BQhcXRoe3ae5FbuKL5Yp6kqTciV7YOnzRTUSFhHfoSeldFDraF7JIB_")' }}
                        aria-label="Small avatar of daughter"
                    />
                    <div
                        className="h-8 w-8 rounded-full border-2 border-white dark:border-slate-800 bg-cover"
                        style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuAKEQRVsSgA83uVXMWhxqpOuk-ZFnUnbTSc6UD7HTG5x5Y_yQRvKhA8Qjx5qryDLaQm6CQsBlj1ky9yeMae9YDRgeR9r7BOtDKxvNuHHf19X9WfMa4cUE-EZmIpVGh7tHEWD98RdCNw8wqpP1QeDPugt6k_s3rhgvVvKnymEqMf6dG-34NcwE7lFU5uLpuRfILuuQqBVCUGhJ6sj2622WD3yuXGtzoTjCfa4QN4keoyeu5LrlQsLSd9hPr2ag7pl7dcc-lDYufcNPll")' }}
                        aria-label="Small avatar of son"
                    />
                    <div className="h-8 flex items-center pl-5 text-xs font-semibold text-primary uppercase tracking-tighter">
                        Emergency Contacts Ready
                    </div>
                </div>
            </div>

            {/* Spacer */}
            <div className="h-10"></div>
        </div>
    );
};

export default FamilyPage;
