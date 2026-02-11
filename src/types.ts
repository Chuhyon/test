export interface DetailImageSegment {
    id: string;
    title: string;
    logicalSections: string[];
    keyMessage: string;
    visualPrompt: string;
    imageUrl?: string;
    isGenerating?: boolean;
}

export type PageLength = 5 | 7 | 9 | 'auto';

export interface ProductInput {
    name: string;
    category: string;
    price: string;
    promotion: string;
    features: string;
    targetGender: string[];
    targetAge: string[];
    pageLength: PageLength;
    referenceImage?: string; // Base64
}

export interface PlanResponse {
    sections: DetailImageSegment[];
}
