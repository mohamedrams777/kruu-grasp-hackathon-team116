import React, { useState } from 'react';
import RiskMeter from './RiskMeter';
import EmotionBars from './EmotionBars';
import ExplanationPanel from './ExplanationPanel';
import ChatbotPanel from './ChatbotPanel';
import { analyzeText } from '../services/api';
import type { HarmAssessment } from '../types';
import './ChatInterface.css';

const ChatInterface: React.FC = () => {
    const [inputText, setInputText] = useState('');
    const [loading, setLoading] = useState(false);
    const [assessment, setAssessment] = useState<HarmAssessment | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!inputText.trim()) {
            return;
        }

        setLoading(true);
        setError(null);
        setAssessment(null);

        try {
            const response = await analyzeText(inputText);

            if (response.success && response.data) {
                setAssessment(response.data);
            } else {
                setError(response.error || 'Failed to analyze text');
            }
        } catch (err) {
            setError('An unexpected error occurred');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleClear = () => {
        setInputText('');
        setAssessment(null);
        setError(null);
    };

    return (
        <div className="chat-interface">
            <div className="chat-header">
                <h1 className="chat-title">🛡️ Harm Detection System</h1>
                <p className="chat-subtitle">
                    AI-powered misinformation risk assessment • Advisory, not authoritative
                </p>
            </div>

            <div className="chat-input-section glass">
                <form onSubmit={handleSubmit}>
                    <label htmlFor="statement-input" className="input-label">
                        Enter a statement to analyze:
                    </label>
                    <textarea
                        id="statement-input"
                        className="input textarea"
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        placeholder="Paste any claim, news headline, or social media post to assess potential harm..."
                        disabled={loading}
                        rows={6}
                    />

                    <div className="input-actions">
                        <button
                            type="submit"
                            className="btn btn-primary"
                            disabled={loading || !inputText.trim()}
                        >
                            {loading ? (
                                <>
                                    <span className="loading"></span>
                                    Analyzing...
                                </>
                            ) : (
                                <>
                                    <span>🔍</span>
                                    Analyze Statement
                                </>
                            )}
                        </button>

                        {(inputText || assessment) && !loading && (
                            <button
                                type="button"
                                className="btn btn-secondary"
                                onClick={handleClear}
                            >
                                Clear
                            </button>
                        )}
                    </div>
                </form>

                {error && (
                    <div className="error-message fade-in">
                        <span className="error-icon">⚠️</span>
                        <span>{error}</span>
                    </div>
                )}
            </div>

            {assessment && (
                <div className="chat-results">
                    <div className="results-grid">
                        <div className="results-col-left">
                            <RiskMeter
                                harmIndex={assessment.harmIndex}
                                riskLevel={assessment.riskLevel}
                                uncertainty={assessment.uncertainty}
                            />
                        </div>

                        <div className="results-col-right">
                            <EmotionBars emotions={assessment.emotionScores} />
                        </div>
                    </div>

                    <ExplanationPanel assessment={assessment} />

                    <ChatbotPanel
                        llmExplanation={assessment.llmExplanation || null}
                        timeseriesData={assessment.timeseriesData}
                        cnnBertResult={assessment.cnnBertResult}
                    />
                </div>
            )}

            {!assessment && !loading && !error && (
                <div className="chat-placeholder glass">
                    <div className="placeholder-content">
                        <div className="placeholder-icon">🎯</div>
                        <h3>How It Works</h3>
                        <div className="placeholder-steps">
                            <div className="placeholder-step">
                                <div className="step-number">1</div>
                                <div className="step-text">
                                    <strong>Enter Text</strong>
                                    <p>Paste any statement, claim, or social media post</p>
                                </div>
                            </div>
                            <div className="placeholder-step">
                                <div className="step-number">2</div>
                                <div className="step-text">
                                    <strong>AI Analysis</strong>
                                    <p>Emotion detection, intent classification, truth verification</p>
                                </div>
                            </div>
                            <div className="placeholder-step">
                                <div className="step-number">3</div>
                                <div className="step-text">
                                    <strong>Risk Assessment</strong>
                                    <p>Get harm index, explanations, and potential consequences</p>
                                </div>
                            </div>
                        </div>
                        <p className="placeholder-note">
                            💡 This tool provides <strong>advisory guidance</strong>, not absolute truth.
                            Always verify from trusted sources.
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ChatInterface;
