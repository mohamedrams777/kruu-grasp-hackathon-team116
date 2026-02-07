import { Router, Request, Response } from 'express';
import axios from 'axios';
import { computeHarmIndex } from '../services/harmIndex';

const router = Router();

const ML_SERVICES = {
    emotion: process.env.EMOTION_SERVICE_URL || 'http://localhost:8001',
    intent: process.env.INTENT_SERVICE_URL || 'http://localhost:8002',
    rag: process.env.RAG_SERVICE_URL || 'http://localhost:8003',
    cnnBert: process.env.CNN_BERT_SERVICE_URL || 'http://localhost:8004',
    llm: process.env.LLM_SERVICE_URL || 'http://localhost:8005',
    timeseries: process.env.TIMESERIES_SERVICE_URL || 'http://localhost:8006',
};

router.post('/analyze', async (req: Request, res: Response) => {
    try {
        const { text } = req.body;

        if (!text || typeof text !== 'string') {
            return res.status(400).json({
                success: false,
                error: 'Text is required and must be a string',
            });
        }

        console.log('📝 Analyzing text:', text.substring(0, 100) + '...');

        // Call ML services in parallel
        const [emotionResponse, intentResponse, ragResponse, cnnResponse, timeseriesResponse] = await Promise.all([
            axios.post(`${ML_SERVICES.emotion}/analyze`, { text }).catch(() => null),
            axios.post(`${ML_SERVICES.intent}/analyze`, { text }).catch(() => null),
            axios.post(`${ML_SERVICES.rag}/analyze`, { text }).catch(() => null),
            axios.post(`${ML_SERVICES.cnnBert}/predict`, { text }).catch(() => null),
            axios.post(`${ML_SERVICES.timeseries}/analyze`, { text }).catch(() => null),
        ]);


        // Extract data from responses
        const emotionScores = emotionResponse?.data || {
            anger: 0.1,
            fear: 0.1,
            joy: 0.2,
            sadness: 0.1,
            neutral: 0.5,
        };

        const intentAnalysis = intentResponse?.data || {
            type: 'Informational',
            hasExplicitCTA: false,
            hasImplicitCTA: false,
            dogWhistleProbability: 0.1,
        };

        const truthVerification = ragResponse?.data || {
            similarityToFalseNarratives: 0.2,
            evidenceConfidence: 'Medium',
            contradictorySources: false,
            similarClaims: [],
        };

        const cnnBertResult = cnnResponse?.data || {
            harm_score: 0.3,
            confidence: 0.5,
            bert_features: {},
            cnn_patterns: []
        };

        const timeseriesData = timeseriesResponse?.data || {
            detected_categories: [],
            trends: [],
            historical_context: 'No historical data available',
            risk_forecast: 'Unable to forecast',
            similar_incidents: []
        };

        // Compute harm index
        const cnnHarmScore = cnnBertResult.harm_score ?? 0;
        const harmAssessment = computeHarmIndex({
            text,
            emotionScores,
            intentAnalysis,
            truthVerification,
            cnnHarmScore,
        });

        // Generate LLM explanation
        let llmExplanation = null;
        try {
            const llmResponse = await axios.post(`${ML_SERVICES.llm}/explain`, {
                text,
                harmIndex: harmAssessment.harmIndex,
                riskLevel: harmAssessment.riskLevel,
                emotionScores,
                intentAnalysis,
                truthVerification
            });
            llmExplanation = llmResponse?.data || null;
        } catch (error) {
            console.log('⚠️ LLM service unavailable, continuing without explanation');
        }

        console.log('✅ Analysis complete. Harm Index:', harmAssessment.harmIndex);

        res.json({
            success: true,
            data: {
                ...harmAssessment,
                cnnBertResult,
                timeseriesData,
                llmExplanation
            },
        });
    } catch (error) {
        console.error('❌ Error in analyze endpoint:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error during analysis',
        });
    }
});

export default router;
