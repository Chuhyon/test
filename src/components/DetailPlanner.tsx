import React, { useState, useRef } from 'react';
import { ProductInput, DetailImageSegment, PageLength } from '../types';
import { planDetailPage, generateSectionImage } from '../services/geminiService';
import {
    Upload,
    Sparkles,
    ChevronRight,
    Save,
    Download,
    Loader2,
    AlertCircle,
    FileImage,
    RefreshCw,
    Image as ImageIcon
} from 'lucide-react';

type Step = 'input' | 'planning' | 'generating';

const DetailPlanner: React.FC = () => {
    const [step, setStep] = useState<Step>('input');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Form State
    const [input, setInput] = useState<ProductInput>({
        name: '',
        category: '',
        price: '',
        promotion: '',
        features: '',
        targetGender: [],
        targetAge: [],
        pageLength: 'auto',
        referenceImage: undefined
    });

    const [segments, setSegments] = useState<DetailImageSegment[]>([]);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setInput(prev => ({ ...prev, [name]: value }));
    };

    const handleCheckboxChange = (group: 'targetGender' | 'targetAge', value: string) => {
        setInput(prev => {
            const current = prev[group];
            if (current.includes(value)) {
                return { ...prev, [group]: current.filter(i => i !== value) };
            }
            return { ...prev, [group]: [...current, value] };
        });
    };

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setInput(prev => ({ ...prev, referenceImage: reader.result as string }));
            };
            reader.readAsDataURL(file);
        }
    };

    const handleStartPlanning = async () => {
        if (!input.name || !input.referenceImage) {
            setError('상품명과 제품 사진은 필수입니다.');
            return;
        }
        setError(null);
        setLoading(true);
        try {
            const plan = await planDetailPage(input);
            setSegments(plan);
            setStep('planning');
        } catch (err: any) {
            setError(err.message || '기획 중 오류가 발생했습니다.');
        } finally {
            setLoading(false);
        }
    };

    const handleGenerateImages = async () => {
        setStep('generating');
        // Initially all marked as generating
        setSegments(prev => prev.map(s => ({ ...s, isGenerating: true })));

        for (let i = 0; i < segments.length; i++) {
            try {
                const imageUrl = await generateSectionImage(segments[i], input.referenceImage);
                setSegments(prev => prev.map((s, idx) =>
                    idx === i ? { ...s, imageUrl, isGenerating: false } : s
                ));
            } catch (err) {
                console.error(`Error generating image ${i}`, err);
                setSegments(prev => prev.map((s, idx) =>
                    idx === i ? { ...s, isGenerating: false } : s
                ));
            }
        }
    };

    const downloadAll = () => {
        segments.forEach((seg, i) => {
            if (seg.imageUrl) {
                const link = document.createElement('a');
                link.href = seg.imageUrl;
                link.download = `detail_page_${i + 1}.jpg`;
                link.click();
            }
        });
    };

    return (
        <div className="max-w-4xl mx-auto px-4 py-12">
            {/* Progress Stepper */}
            <div className="flex items-center justify-center mb-12">
                <div className={`flex items-center ${step === 'input' ? 'text-brand-600' : 'text-slate-400'}`}>
                    <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center font-bold mr-2 ${step === 'input' ? 'border-brand-600' : 'border-slate-300'}`}>1</div>
                    <span className="font-medium mr-4">정보 입력</span>
                </div>
                <div className="w-12 h-px bg-slate-200 mx-4" />
                <div className={`flex items-center ${step === 'planning' ? 'text-brand-600' : 'text-slate-400'}`}>
                    <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center font-bold mr-2 ${step === 'planning' ? 'border-brand-600' : 'border-slate-300'}`}>2</div>
                    <span className="font-medium mr-4">전략 기획</span>
                </div>
                <div className="w-12 h-px bg-slate-200 mx-4" />
                <div className={`flex items-center ${step === 'generating' ? 'text-brand-600' : 'text-slate-400'}`}>
                    <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center font-bold mr-2 ${step === 'generating' ? 'border-brand-600' : 'border-slate-300'}`}>3</div>
                    <span className="font-medium">이미지 생성</span>
                </div>
            </div>

            {step === 'input' && (
                <section className="bg-white rounded-3xl shadow-xl shadow-slate-200/50 p-8 border border-slate-100">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="space-y-6">
                            <div>
                                <label className="block text-sm font-bold text-slate-700 mb-2">상품명 <span className="text-red-500">*</span></label>
                                <input
                                    type="text"
                                    name="name"
                                    value={input.name}
                                    onChange={handleInputChange}
                                    placeholder="예: 프리미엄 무선 소음 차단 헤드폰"
                                    className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-brand-500 focus:border-transparent outline-none transition-all"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-bold text-slate-700 mb-2">카테고리</label>
                                <select
                                    name="category"
                                    value={input.category}
                                    onChange={handleInputChange}
                                    className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-brand-500 outline-none transition-all"
                                >
                                    <option value="">카테고리 선택</option>
                                    <option value="fashion">패션/의류</option>
                                    <option value="beauty">뷰티/화장품</option>
                                    <option value="food">식품</option>
                                    <option value="electronic">전자기기</option>
                                    <option value="home">가공/리빙</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-bold text-slate-700 mb-2">상품 특징 (USP)</label>
                                <textarea
                                    name="features"
                                    value={input.features}
                                    onChange={handleInputChange}
                                    rows={4}
                                    placeholder="상품의 핵심 장점을 적어주세요. AI가 판매 문구로 변환합니다."
                                    className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-brand-500 outline-none transition-all"
                                ></textarea>
                            </div>
                        </div>

                        <div className="space-y-6">
                            <div>
                                <label className="block text-sm font-bold text-slate-700 mb-2">상세페이지 길이</label>
                                <div className="grid grid-cols-2 gap-2">
                                    {['auto', '5', '7', '9'].map(val => (
                                        <button
                                            key={val}
                                            onClick={() => setInput(p => ({ ...p, pageLength: val as PageLength }))}
                                            className={`px-4 py-2 rounded-xl border text-sm font-medium transition-all ${input.pageLength === val
                                                    ? 'bg-brand-50 border-brand-500 text-brand-700 shadow-sm'
                                                    : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'
                                                }`}
                                        >
                                            {val === 'auto' ? 'AI 추천' : `${val}장 (${val === '5' ? 'Short' : val === '7' ? 'Standard' : 'Long'})`}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-bold text-slate-700 mb-2">제품 원본 이미지 <span className="text-red-500">*</span></label>
                                <div
                                    onClick={() => fileInputRef.current?.click()}
                                    className="aspect-square rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50 flex flex-col items-center justify-center cursor-pointer hover:bg-slate-100 hover:border-brand-300 transition-all overflow-hidden"
                                >
                                    {input.referenceImage ? (
                                        <img src={input.referenceImage} alt="Preview" className="w-full h-full object-cover" />
                                    ) : (
                                        <>
                                            <Upload className="w-10 h-10 text-slate-300 mb-2" />
                                            <span className="text-sm text-slate-500">이미지 업로드</span>
                                        </>
                                    )}
                                </div>
                                <input
                                    type="file"
                                    ref={fileInputRef}
                                    onChange={handleFileUpload}
                                    accept="image/*"
                                    className="hidden"
                                />
                            </div>
                        </div>
                    </div>

                    <div className="mt-8 flex flex-col gap-4">
                        {error && (
                            <div className="bg-red-50 text-red-600 p-4 rounded-xl flex items-center gap-3 text-sm">
                                <AlertCircle size={18} />
                                {error}
                            </div>
                        )}
                        <button
                            onClick={handleStartPlanning}
                            disabled={loading}
                            className="w-full py-4 bg-brand-600 hover:bg-brand-700 text-white rounded-2xl font-bold flex items-center justify-center gap-2 shadow-lg shadow-brand-200 transition-all disabled:opacity-50"
                        >
                            {loading ? <Loader2 className="animate-spin" /> : <Sparkles />}
                            AI로 상세페이지 기획 시작하기
                        </button>
                    </div>
                </section>
            )}

            {step === 'planning' && (
                <section className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <div className="flex items-center justify-between">
                        <h2 className="text-2xl font-bold text-slate-800">AI 전략 기획안</h2>
                        <button
                            onClick={handleGenerateImages}
                            className="px-6 py-3 bg-brand-600 hover:bg-brand-700 text-white rounded-xl font-bold flex items-center gap-2 shadow-lg shadow-brand-100 transition-all"
                        >
                            <FileImage size={20} />
                            이미지 일괄 생성하기
                        </button>
                    </div>

                    <div className="space-y-4">
                        {segments.map((seg, idx) => (
                            <div key={seg.id} className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                                <div className="flex flex-wrap gap-2 mb-3">
                                    {seg.logicalSections.map(tag => (
                                        <span key={tag} className="px-3 py-1 bg-slate-100 text-slate-600 text-[10px] font-bold rounded-full uppercase tracking-wider">{tag}</span>
                                    ))}
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                    <div className="md:col-span-1">
                                        <p className="text-xs font-bold text-brand-600 mb-1 uppercase tracking-tighter">Image {idx + 1}</p>
                                        <h3 className="text-lg font-bold text-slate-800 mb-2">{seg.title}</h3>
                                    </div>
                                    <div className="md:col-span-2 space-y-4">
                                        <div>
                                            <label className="block text-[10px] font-bold text-slate-400 mb-1">한글 카피 (Key Message)</label>
                                            <input
                                                type="text"
                                                value={seg.keyMessage}
                                                onChange={(e) => {
                                                    const newSegs = [...segments];
                                                    newSegs[idx].keyMessage = e.target.value;
                                                    setSegments(newSegs);
                                                }}
                                                className="w-full px-4 py-2 bg-slate-50 border-none rounded-lg text-slate-700 font-medium"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-[10px] font-bold text-slate-400 mb-1">비주얼 프롬프트 (Visual Prompt)</label>
                                            <textarea
                                                value={seg.visualPrompt}
                                                onChange={(e) => {
                                                    const newSegs = [...segments];
                                                    newSegs[idx].visualPrompt = e.target.value;
                                                    setSegments(newSegs);
                                                }}
                                                rows={2}
                                                className="w-full px-4 py-2 bg-slate-50 border-none rounded-lg text-slate-700 text-sm"
                                            ></textarea>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            )}

            {step === 'generating' && (
                <section className="space-y-8 animate-in fade-in duration-700">
                    <div className="flex items-center justify-between">
                        <div>
                            <h2 className="text-2xl font-bold text-slate-800">생성된 상세페이지</h2>
                            <p className="text-slate-500">이미지가 순차적으로 생성되고 있습니다. 완료되면 저장하세요.</p>
                        </div>
                        <div className="flex gap-2">
                            <button
                                onClick={() => setStep('input')}
                                className="px-6 py-3 bg-white border border-slate-200 text-slate-600 rounded-xl font-bold hover:bg-slate-50 transition-all"
                            >
                                처음으로
                            </button>
                            <button
                                onClick={downloadAll}
                                className="px-6 py-3 bg-brand-600 hover:bg-brand-700 text-white rounded-xl font-bold flex items-center gap-2 transition-all shadow-lg shadow-brand-100"
                            >
                                <Download size={20} />
                                전체 저장하기
                            </button>
                        </div>
                    </div>

                    <div className="detail-page-container space-y-px">
                        {segments.map((seg, idx) => (
                            <div key={seg.id} className="relative group">
                                <div className="image-preview-aspect bg-slate-200 overflow-hidden">
                                    {seg.isGenerating ? (
                                        <div className="w-full h-full flex flex-col items-center justify-center gap-4 bg-slate-100">
                                            <div className="relative">
                                                <Loader2 className="w-12 h-12 text-brand-500 animate-spin" />
                                                <Sparkles className="absolute -top-1 -right-1 w-5 h-5 text-brand-300 animate-pulse" />
                                            </div>
                                            <span className="text-sm font-bold text-slate-400">AI가 이미지를 그리고 있습니다...</span>
                                        </div>
                                    ) : seg.imageUrl ? (
                                        <div className="relative w-full h-full">
                                            <img src={seg.imageUrl} alt={seg.title} className="w-full h-full object-cover" />
                                            {/* Overlay text simulation */}
                                            <div className="absolute inset-x-8 top-12 text-center">
                                                <h3 className="text-2xl md:text-4xl font-black text-white drop-shadow-[0_2px_10px_rgba(0,0,0,0.8)] leading-tight whitespace-pre-line">
                                                    {seg.keyMessage}
                                                </h3>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="w-full h-full flex items-center justify-center bg-slate-100 text-slate-400">
                                            대기 중
                                        </div>
                                    )}
                                </div>
                                <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button className="p-2 bg-white/90 backdrop-blur rounded-full shadow-lg text-slate-700 hover:text-brand-600">
                                        <RefreshCw size={20} />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            )}
        </div>
    );
};

export default DetailPlanner;
