interface EmotionScores {
    anger: number;
    fear: number;
    joy: number;
    sadness: number;
    neutral: number;
}

interface IntentAnalysis {
    type: 'Informational' | 'Persuasive' | 'Inciting' | 'Alarmist' | 'Action-oriented';
    hasExplicitCTA: boolean;
    hasImplicitCTA: boolean;
    dogWhistleProbability: number;
}

interface TruthVerification {
    similarityToFalseNarratives: number;
    evidenceConfidence: 'High' | 'Medium' | 'Low';
    contradictorySources: boolean;
    similarClaims: string[];
}

interface HarmIndexInput {
    text: string;
    emotionScores: EmotionScores;
    intentAnalysis: IntentAnalysis;
    truthVerification: TruthVerification;
    cnnHarmScore?: number;
}

interface HarmAssessment {
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
}

export function computeHarmIndex(input: HarmIndexInput): HarmAssessment {
    const { emotionScores, intentAnalysis, truthVerification, text } = input;

    // Calculate emotion volatility (0-1 scale)
    const emotionVolatility =
        (emotionScores.anger * 1.2 + emotionScores.fear * 1.1) / 2;

    // Calculate intent risk (0-1 scale)
    const intentRiskMap = {
        Informational: 0.1,
        Persuasive: 0.4,
        'Action-oriented': 0.6,
        Alarmist: 0.75,
        Inciting: 0.9,
    };
    const baseIntentRisk = intentRiskMap[intentAnalysis.type];
    const ctaBonus = intentAnalysis.hasExplicitCTA ? 0.15 : intentAnalysis.hasImplicitCTA ? 0.1 : 0;
    const dogWhistleBonus = intentAnalysis.dogWhistleProbability * 0.2;
    const intentRisk = Math.min(1, baseIntentRisk + ctaBonus + dogWhistleBonus);

    // Historical harm similarity (0-1 scale)
    const historicalHarm = truthVerification.similarityToFalseNarratives;

    // Truth uncertainty (0-1 scale)
    const evidenceConfidenceMap = { High: 0.1, Medium: 0.5, Low: 0.8 };
    const truthUncertainty = evidenceConfidenceMap[truthVerification.evidenceConfidence];
    const contradictionBonus = truthVerification.contradictorySources ? 0.15 : 0;
    const finalTruthUncertainty = Math.min(1, truthUncertainty + contradictionBonus);

    // Weighted formula for harm index (0-100 scale)
    const cnnScore = input.cnnHarmScore || 0;

    const harmIndex = Math.round(
        emotionVolatility * 20 +
        intentRisk * 25 +
        historicalHarm * 20 +
        finalTruthUncertainty * 15 +
        cnnScore * 20
    );

    // Determine risk level
    let riskLevel: 'Low' | 'Medium' | 'High';
    if (harmIndex <= 30) riskLevel = 'Low';
    else if (harmIndex <= 60) riskLevel = 'Medium';
    else riskLevel = 'High';

    // Calculate uncertainty
    const uncertainty = 10 + Math.round(emotionVolatility * 5 + finalTruthUncertainty * 5);

    // Generate historical context
    const pastOutcomes = generateHistoricalOutcomes(
        harmIndex,
        intentAnalysis.type,
        emotionScores
    );

    // Generate explanation
    const explanation = generateExplanation(
        harmIndex,
        emotionScores,
        intentAnalysis,
        truthVerification
    );

    return {
        harmIndex,
        riskLevel,
        uncertainty,
        emotionScores,
        intentAnalysis,
        truthVerification,
        historicalContext: { pastOutcomes },
        cnnHarmScore: input.cnnHarmScore,
        explanation,
    };
}

function generateHistoricalOutcomes(
    harmIndex: number,
    intentType: string,
    emotions: EmotionScores
): Array<{ outcome: string; probability: 'High' | 'Medium' | 'Low' }> {
    const outcomes: Array<{ outcome: string; probability: 'High' | 'Medium' | 'Low' }> = [];

    if (emotions.fear > 0.6) {
        outcomes.push({
            outcome: 'Panic behavior or anxiety',
            probability: harmIndex > 60 ? 'High' : 'Medium',
        });
    }

    if (emotions.anger > 0.6) {
        outcomes.push({
            outcome: 'Social unrest or confrontational behavior',
            probability: harmIndex > 70 ? 'High' : 'Medium',
        });
    }

    if (intentType === 'Alarmist' || intentType === 'Inciting') {
        outcomes.push({
            outcome: 'Rapid misinformation spread',
            probability: 'High',
        });
    }

    if (intentType === 'Action-oriented') {
        outcomes.push({
            outcome: 'Inappropriate action without verification',
            probability: 'Medium',
        });
    }

    if (outcomes.length === 0) {
        outcomes.push({
            outcome: 'Limited behavioral impact',
            probability: 'Low',
        });
    }

    return outcomes;
}

function generateExplanation(
    harmIndex: number,
    emotions: EmotionScores,
    intent: IntentAnalysis,
    truth: TruthVerification
): string {
    const parts: string[] = [];

    // Emotion part
    if (emotions.anger > 0.6 || emotions.fear > 0.6) {
        parts.push('The statement is conveyed with **high emotional intensity** (anger and/or fear)');
    } else if (emotions.anger > 0.3 || emotions.fear > 0.3) {
        parts.push('The statement shows **moderate emotional intensity**');
    } else {
        parts.push('The statement has **low emotional intensity**');
    }

    // Intent part
    if (intent.hasExplicitCTA) {
        parts.push('It includes **explicit calls to action**');
    } else if (intent.hasImplicitCTA) {
        parts.push('It includes **implicit calls to action**');
    }

    if (intent.dogWhistleProbability > 0.6) {
        parts.push('Potential **coded language or dog-whistles** detected');
    }

    // Truth part
    if (truth.similarityToFalseNarratives > 0.7) {
        parts.push('It shows **high similarity to known false narratives**');
    } else if (truth.similarityToFalseNarratives > 0.4) {
        parts.push('It shows **moderate similarity to debunked claims**');
    }

    if (truth.contradictorySources) {
        parts.push('Current verified sources **contradict or do not support** the claim');
    }

    return '• ' + parts.join('\n• ');
}
