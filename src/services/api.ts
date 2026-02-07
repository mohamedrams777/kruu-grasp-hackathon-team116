import axios from 'axios';
import type { AnalysisRequest, AnalysisResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const analyzeText = async (text: string): Promise<AnalysisResponse> => {
    try {
        const response = await api.post<AnalysisResponse>('/api/analyze', {
            text,
        } as AnalysisRequest);
        return response.data;
    } catch (error) {
        console.error('Error analyzing text:', error);
        return {
            success: false,
            error: 'Failed to analyze text. Please try again.',
        };
    }
};

export default api;
