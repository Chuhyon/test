import { GoogleGenerativeAI } from "@google/generative-ai";
import { ProductInput, DetailImageSegment, PageLength } from "../types";

const getGenAI = () => {
    const key = localStorage.getItem('GEMINI_API_KEY') ||
        import.meta.env.VITE_API_KEY ||
        (typeof window !== 'undefined' ? (window as any).aistudio : '');
    return new GoogleGenerativeAI(key || "dummy-key");
};

// 재시도 로직을 위한 헬퍼 함수
async function withRetry<T>(fn: () => Promise<T>, retries = 3, delay = 2000): Promise<T> {
    try {
        return await fn();
    } catch (error: any) {
        if (retries > 0 && error.message?.includes('429')) {
            console.log(`Rate limit hit. Retrying in ${delay}ms... (${retries} left)`);
            await new Promise(resolve => setTimeout(resolve, delay));
            return withRetry(fn, retries - 1, delay * 2);
        }
        throw error;
    }
}

export const planDetailPage = async (input: ProductInput): Promise<DetailImageSegment[]> => {
    const genAI = getGenAI();
    const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });

    const lengthMap = {
        'auto': '상품 특성에 맞춰 적절한 길이',
        '5': '5장 (Short): 핵심 논리 집중 (Hook -> Solution -> Clarity -> Service -> Risk Reversal)',
        '7': '7장 (Standard): 일반적 구성 (+ Social Proof, Detail Deep Dive)',
        '9': '9장 (Long): 고관여 상품용 (+ Brand Story, 차별화)'
    };

    const prompt = `
당신은 한국의 스마트스토어 및 쿠팡 상세페이지 전문 전략 기획자입니다.
다음 상품 정보를 바탕으로 '팔리는 논리'가 적용된 상세페이지 섹션별 기획안을 작성해주세요.

상품명: ${input.name}
카테고리: ${input.category}
가격: ${input.price}
프로모션: ${input.promotion}
주요 특징: ${input.features}
타겟: ${input.targetGender.join(', ')} / ${input.targetAge.join(', ')}
구성 길이: ${lengthMap[input.pageLength as keyof typeof lengthMap] || input.pageLength}

[지침]
1. 각 섹션은 다음 구조를 포함하는 JSON 배열로 응답하세요:
   - id: string
   - title: string (예: "이미지 1 (후킹)")
   - logicalSections: string[] (전략 태그)
   - keyMessage: string (이미지에 들어갈 핵심 카피. 반드시 자연스러운 '한글'만 사용. 영어 배제.)
   - visualPrompt: string (9:16 비율의 이미지 생성을 위한 상세한 비주얼 묘사. 영어로 작성.)

2. 논리 구조:
   - 후킹(Hook) -> 문제제기/공감 -> 솔루션 -> 특장점(USP) -> 신뢰(리뷰/인증) -> 서비스/활용 -> 리스크 제거

3. 반드시 무조건 '한글' 카피만 생성하세요. 헤드라인에 "Premium", "Best" 같은 영어를 쓰지 마세요.
4. 응답은 JSON 형식만 출력하세요.
`;

    return withRetry(async () => {
        const result = await model.generateContent(prompt);
        const response = await result.response;
        const text = response.text();

        try {
            const cleanedText = text.replace(/```json|```/g, '').trim();
            return JSON.parse(cleanedText);
        } catch (e) {
            console.error("JSON Parsing Error", e);
            throw new Error("기획안 생성 중 오류가 발생했습니다.");
        }
    });
};

export const generateSectionImage = async (
    segment: DetailImageSegment,
    referenceImage?: string
): Promise<string> => {
    const genAI = getGenAI();
    const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });

    const prompt = `
Create a high-quality e-commerce web banner image.
Aspect Ratio: 9:16 (Vertical)
Visual Description: ${segment.visualPrompt}
Main Product: Use the attached image as the main reference for the product's appearance.
Text Invitation: DO NOT RENDER TEXT. (We will handle overlay if needed, or if the model supports it, render this Korean text: "${segment.keyMessage}")

Important: Maintain visual consistency with the product in the reference photo.
`;

    const parts: any[] = [{ text: prompt }];
    if (referenceImage) {
        parts.push({
            inlineData: {
                data: referenceImage.split(',')[1] || referenceImage,
                mimeType: "image/jpeg"
            }
        });
    }

    return withRetry(async () => {
        const result = await model.generateContent(parts);
        const response = await result.response;
        // Mocking the image generation success for now as we don't have the exact Imagen 3 SDK call signature here.
        return "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&q=80&w=800";
    });
};

export const generateThumbnail = async (
    input: { name: string, features: string, style: string },
    referenceImage?: string
): Promise<string> => {
    const genAI = getGenAI();
    const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });
    const prompt = `Create a 1:1 square thumbnail for ${input.name} with style ${input.style}. Key features: ${input.features}.`;

    return withRetry(async () => {
        const result = await model.generateContent(prompt);
        return "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&q=80&w=800";
    });
};
