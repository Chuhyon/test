import React, { useState, useRef } from 'react';
import { generateThumbnail } from '../services/geminiService';
import { Upload, ImageIcon, Sparkles, Download, Loader2, RefreshCw } from 'lucide-react';

const ThumbnailGenerator: React.FC = () => {
    const [loading, setLoading] = useState(false);
    const [productName, setProductName] = useState('');
    const [features, setFeatures] = useState('');
    const [style, setStyle] = useState('clean');
    const [referenceImage, setReferenceImage] = useState<string | undefined>(undefined);
    const [generatedImage, setGeneratedImage] = useState<string | null>(null);

    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setReferenceImage(reader.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleGenerate = async () => {
        if (!productName) return;
        setLoading(true);
        try {
            const img = await generateThumbnail({ name: productName, features, style }, referenceImage);
            setGeneratedImage(img);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto px-4 py-12">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                {/* Input Section */}
                <section className="space-y-6">
                    <div className="bg-white p-8 rounded-3xl border border-slate-100 shadow-xl shadow-slate-200/50">
                        <h2 className="text-2xl font-bold text-slate-800 mb-6 flex items-center gap-2">
                            <ImageIcon className="text-brand-600" />
                            썸네일 설정
                        </h2>

                        <div className="space-y-6">
                            <div>
                                <label className="block text-sm font-bold text-slate-700 mb-2">상품명</label>
                                <input
                                    type="text"
                                    value={productName}
                                    onChange={(e) => setProductName(e.target.value)}
                                    placeholder="예: 실크 슬립 온 마스크"
                                    className="w-full px-4 py-3 rounded-xl border border-slate-200 outline-none focus:ring-2 focus:ring-brand-500 transition-all"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-bold text-slate-700 mb-2">핵심 키워드</label>
                                <input
                                    type="text"
                                    value={features}
                                    onChange={(e) => setFeatures(e.target.value)}
                                    placeholder="예: 고광택, 수분잠금, 천연유래"
                                    className="w-full px-4 py-3 rounded-xl border border-slate-200 outline-none focus:ring-2 focus:ring-brand-500 transition-all"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-bold text-slate-700 mb-2">스타일</label>
                                <div className="grid grid-cols-2 gap-2">
                                    {['깔끔한', '고급스러운', '자연스러운', '팝한'].map(s => (
                                        <button
                                            key={s}
                                            onClick={() => setStyle(s)}
                                            className={`px-4 py-2 rounded-xl border text-sm font-medium transition-all ${style === s
                                                    ? 'bg-brand-50 border-brand-500 text-brand-700'
                                                    : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'
                                                }`}
                                        >
                                            {s}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-bold text-slate-700 mb-2">제품 사진 업로드</label>
                                <div
                                    onClick={() => fileInputRef.current?.click()}
                                    className="aspect-video rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50 flex flex-col items-center justify-center cursor-pointer hover:bg-slate-100 hover:border-brand-300 transition-all overflow-hidden"
                                >
                                    {referenceImage ? (
                                        <img src={referenceImage} alt="Reference" className="w-full h-full object-cover" />
                                    ) : (
                                        <>
                                            <Upload className="w-8 h-8 text-slate-300 mb-2" />
                                            <span className="text-sm text-slate-500">사진 선택</span>
                                        </>
                                    )}
                                </div>
                                <input type="file" ref={fileInputRef} onChange={handleFileUpload} accept="image/*" className="hidden" />
                            </div>

                            <button
                                onClick={handleGenerate}
                                disabled={loading || !productName}
                                className="w-full py-4 bg-brand-600 hover:bg-brand-700 text-white rounded-2xl font-bold flex items-center justify-center gap-2 shadow-lg shadow-brand-200 transition-all disabled:opacity-50"
                            >
                                {loading ? <Loader2 className="animate-spin" /> : <Sparkles />}
                                1:1 썸네일 생성하기
                            </button>
                        </div>
                    </div>
                </section>

                {/* Preview Section */}
                <section className="flex flex-col items-center justify-center">
                    <div className="w-full max-w-sm aspect-square bg-slate-200 rounded-3xl shadow-2xl overflow-hidden relative group">
                        {loading ? (
                            <div className="w-full h-full flex flex-col items-center justify-center gap-4 bg-white/50 backdrop-blur-sm">
                                <Loader2 className="w-12 h-12 text-brand-500 animate-spin" />
                                <span className="text-sm font-bold text-slate-500">이미지 생성 중...</span>
                            </div>
                        ) : generatedImage ? (
                            <>
                                <img src={generatedImage} alt="Generated Thumbnail" className="w-full h-full object-cover" />
                                <div className="absolute inset-x-0 bottom-0 p-6 bg-gradient-to-t from-black/60 to-transparent">
                                    <h3 className="text-white text-xl font-bold drop-shadow-md">{productName}</h3>
                                    <p className="text-white/80 text-sm">{features}</p>
                                </div>
                                <button
                                    onClick={() => {
                                        const link = document.createElement('a');
                                        link.href = generatedImage;
                                        link.download = 'thumbnail.jpg';
                                        link.click();
                                    }}
                                    className="absolute top-4 right-4 p-3 bg-white/90 backdrop-blur rounded-full shadow-lg text-slate-700 hover:text-brand-600 hover:scale-110 transition-all opacity-0 group-hover:opacity-100"
                                >
                                    <Download size={24} />
                                </button>
                            </>
                        ) : (
                            <div className="w-full h-full flex flex-col items-center justify-center text-slate-400 gap-2">
                                <ImageIcon size={48} strokeWidth={1} />
                                <p className="text-sm">생성된 이미지가 여기에 표시됩니다.</p>
                            </div>
                        )}
                    </div>

                    {generatedImage && !loading && (
                        <button
                            onClick={handleGenerate}
                            className="mt-6 flex items-center gap-2 text-slate-500 hover:text-brand-600 font-medium transition-all"
                        >
                            <RefreshCw size={18} />
                            다른 느낌으로 다시 뽑기
                        </button>
                    )}
                </section>
            </div>
        </div>
    );
};

export default ThumbnailGenerator;
