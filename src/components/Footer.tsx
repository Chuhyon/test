import React from 'react';

const Footer: React.FC = () => {
    return (
        <footer className="bg-slate-900 text-slate-400 py-8 px-4 mt-auto">
            <div className="max-w-4xl mx-auto text-center">
                <p className="mb-4">이 앱은 AI싱크클럽의 지침으로 만들어졌습니다.</p>
                <p className="mb-6 font-semibold text-slate-200">유튜브와 쓰레드 팔로우 부탁드려요!</p>

                <div className="flex flex-wrap justify-center gap-6 mb-8">
                    <a
                        href="https://youtube.com/@aisyncclub"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="hover:text-brand-400 transition-colors"
                    >
                        유튜브 (6K 구독자)
                    </a>
                    <a
                        href="https://www.threads.com/@ai_sync_club"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="hover:text-brand-400 transition-colors"
                    >
                        쓰레드 (3.7K 구독자)
                    </a>
                    <a
                        href="https://litt.ly/aisyncclub"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="hover:text-brand-400 transition-colors"
                    >
                        리틀리
                    </a>
                </div>

                <div className="text-xs opacity-50">
                    &copy; {new Date().getFullYear()} AI Sync Club. All rights reserved.
                </div>
            </div>
        </footer>
    );
};

export default Footer;
