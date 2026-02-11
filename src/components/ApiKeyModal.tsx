import React, { useState, useEffect } from 'react';
import { Key, X, CheckCircle2 } from 'lucide-react';

const ApiKeyModal: React.FC = () => {
    const [apiKey, setApiKey] = useState('');
    const [isOpen, setIsOpen] = useState(false);
    const [isSaved, setIsSaved] = useState(false);

    useEffect(() => {
        const savedKey = localStorage.getItem('GEMINI_API_KEY');
        if (!savedKey) {
            setIsOpen(true);
        } else {
            // geminiService에서 사용할 수 있도록 window 객체에 할당
            (window as any).aistudio = savedKey;
        }
    }, []);

    const handleSave = () => {
        if (apiKey.trim()) {
            localStorage.setItem('GEMINI_API_KEY', apiKey.trim());
            (window as any).aistudio = apiKey.trim();
            setIsSaved(true);
            setTimeout(() => {
                setIsOpen(false);
                setIsSaved(false);
            }, 1000);
        }
    };

    if (!isOpen) return (
        <button
            onClick={() => setIsOpen(true)}
            className="fixed bottom-24 right-6 bg-slate-800 text-white p-3 rounded-full shadow-lg hover:bg-slate-700 transition-all z-40 group"
        >
            <Key size={20} />
            <span className="absolute right-full mr-3 bg-slate-800 text-white text-xs py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                API 키 설정
            </span>
        </button>
    );

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100] flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in duration-300">
                <div className="p-6">
                    <div className="flex justify-between items-center mb-6">
                        <div className="flex items-center gap-2">
                            <div className="w-10 h-10 bg-brand-100 text-brand-600 rounded-xl flex items-center justify-center">
                                <Key size={24} />
                            </div>
                            <h2 className="text-xl font-bold text-slate-800">API 키 설정</h2>
                        </div>
                        <button
                            onClick={() => setIsOpen(false)}
                            className="text-slate-400 hover:text-slate-600 transition-colors"
                        >
                            <X size={24} />
                        </button>
                    </div>

                    <div className="space-y-4">
                        <p className="text-sm text-slate-600 leading-relaxed">
                            Google AI Studio(Gemini) API 키를 입력해 주세요.
                            키는 브라우저의 로컬 스토리지에 안전하게 저장됩니다.
                        </p>

                        <div className="relative">
                            <input
                                type="password"
                                value={apiKey}
                                onChange={(e) => setApiKey(e.target.value)}
                                placeholder="AI Studio에서 발급받은 API 키 입력"
                                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all outline-none"
                            />
                        </div>

                        <a
                            href="https://aistudio.google.com/app/apikey"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-brand-600 hover:underline inline-block"
                        >
                            API 키가 없으신가요? 여기서 발급받기 →
                        </a>
                    </div>
                </div>

                <div className="p-6 bg-slate-50 border-t border-slate-100 flex gap-3">
                    <button
                        onClick={() => setIsOpen(false)}
                        className="flex-1 px-4 py-3 rounded-xl text-sm font-semibold text-slate-600 hover:bg-slate-200 transition-colors"
                    >
                        취소
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={isSaved}
                        className={`flex-1 px-4 py-3 rounded-xl text-sm font-semibold text-white transition-all flex items-center justify-center gap-2 ${isSaved ? 'bg-green-500' : 'bg-brand-600 hover:bg-brand-700'
                            }`}
                    >
                        {isSaved ? (
                            <>
                                <CheckCircle2 size={18} />
                                저장됨
                            </>
                        ) : (
                            '저장하기'
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ApiKeyModal;
