export interface EmotionScores {
    anger: number;
    fear: number;
    joy: number;
    sadness: number;
    neutral: number;
}

export interface IntentAnalysis {
    type: 'Informational' | 'Persuasive' | 'Inciting' | 'Alarmist' | 'Action-oriented';
    hasExplicitCTA: boolean;
    hasImplicitCTA: boolean;
    dogWhistleProbability: number;
}

export interface TruthVerification {
    similarityToFalseNarratives: number;
    evidenceConfidence: 'High' | 'Medium' | 'Low';
    contradictorySources: boolean;
    similarClaims: string[];
}

export interface CNNBertResult {
    harm_score: number;
    confidence: number;
    bert_features: Record<string, any>;
    cnn_patterns: Array<{
        category: string;
        matches: string[];
        score: number;
    }>;
}

export interface TrendData {
    category: string;
    current_level: number;
    trend_direction: 'increasing' | 'decreasing' | 'stable';
    volatility: number;
    recent_spike: boolean;
}

export interface TimeSeriesData {
    detected_categories: string[];
    trends: TrendData[];
    historical_context: string;
    risk_forecast: string;
    similar_incidents: Array<{
        category: string;
        date: string;
        description: string;
        outcome: string;
    }>;
}

export interface LLMExplanation {
    explanation: string;
    insights: string[];
    recommendations: string[];
}

export interface HistoricalContext {
    pastOutcomes: {
        outcome: string;
        probability: 'High' | 'Medium' | 'Low';
    }[];
}

export interface HarmAssessment {
    harmIndex: number;
    riskLevel: 'Low' | 'Medium' | 'High';
    uncertainty: number;
    emotionScores: EmotionScores;
    intentAnalysis: IntentAnalysis;
    truthVerification: TruthVerification;
    historicalContext: {
        pastOutcomes: Array<{
            outcome: string;
            probability: 'High' | 'Medium' | 'Low';
        }>;
    };
    cnnHarmScore?: number;
    explanation: string;
    cnnBertResult?: CNNBertResult;
    timeseriesData?: TimeSeriesData;
    llmExplanation?: LLMExplanation;
}

export interface AnalysisRequest {
    text: string;
}

export interface AnalysisResponse {
    success: boolean;
    data?: HarmAssessment;
    error?: string;
}
