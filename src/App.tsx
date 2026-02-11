import React, { useState } from 'react';
import DetailPlanner from './components/DetailPlanner';
import ThumbnailGenerator from './components/ThumbnailGenerator';
import Footer from './components/Footer';
import ApiKeyModal from './components/ApiKeyModal';
import { Layout, Image as ImageIcon, FileText } from 'lucide-react';

const App: React.FC = () => {
    const [activeTab, setActiveTab] = useState<'detail' | 'thumbnail'>('detail');

    return (
        <div className="min-h-screen flex flex-col font-sans">
            {/* Header */}
            <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
                <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center text-white">
                            <Layout size={20} />
                        </div>
                        <h1 className="text-xl font-bold bg-gradient-to-r from-brand-600 to-sky-500 bg-clip-text text-transparent">
                            AI Sync Club Builder
                        </h1>
                    </div>

                    <nav className="flex gap-1 bg-slate-100 p-1 rounded-xl">
                        <button
                            onClick={() => setActiveTab('detail')}
                            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === 'detail'
                                ? 'bg-white text-brand-700 shadow-sm'
                                : 'text-slate-500 hover:text-slate-700'
                                }`}
                        >
                            <FileText size={16} />
                            상세페이지 제작
                        </button>
                        <button
                            onClick={() => setActiveTab('thumbnail')}
                            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === 'thumbnail'
                                ? 'bg-white text-brand-700 shadow-sm'
                                : 'text-slate-500 hover:text-slate-700'
                                }`}
                        >
                            <ImageIcon size={16} />
                            썸네일 제작
                        </button>
                    </nav>
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-grow">
                {activeTab === 'detail' ? (
                    <DetailPlanner />
                ) : (
                    <ThumbnailGenerator />
                )}
            </main>

            {/* Footer */}
            <Footer />
            <ApiKeyModal />
        </div>
    );
};

export default App;
