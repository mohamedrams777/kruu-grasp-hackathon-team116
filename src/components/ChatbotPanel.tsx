import React from 'react';
import type { LLMExplanation, TimeSeriesData, CNNBertResult } from '../types';
import './ChatbotPanel.css';

interface ChatbotPanelProps {
    llmExplanation: LLMExplanation | null;
    timeseriesData?: TimeSeriesData;
    cnnBertResult?: CNNBertResult;
}

const ChatbotPanel: React.FC<ChatbotPanelProps> = ({
    llmExplanation,
    timeseriesData,
    cnnBertResult
}) => {
    if (!llmExplanation) {
        return null;
    }

    return (
        <div className="chatbot-panel glass fade-in">
            <div className="chatbot-header">
                <div className="chatbot-avatar">🤖</div>
                <div className="chatbot-title">
                    <h3>AI Analysis Assistant</h3>
                    <p>Detailed explanation and insights</p>
                </div>
            </div>

            <div className="chatbot-content">
                {/* Main Explanation */}
                <div className="chatbot-message">
                    <div className="message-label">📊 Analysis Summary</div>
                    <div className="message-text">
                        {llmExplanation.explanation.split('\n').map((line, idx) => (
                            <p key={idx}>{line}</p>
                        ))}
                    </div>
                </div>

                {/* Key Insights */}
                {llmExplanation.insights && llmExplanation.insights.length > 0 && (
                    <div className="chatbot-message">
                        <div className="message-label">💡 Key Insights</div>
                        <ul className="insights-list">
                            {llmExplanation.insights.map((insight, idx) => (
                                <li key={idx}>{insight}</li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Recommendations */}
                {llmExplanation.recommendations && llmExplanation.recommendations.length > 0 && (
                    <div className="chatbot-message">
                        <div className="message-label">✅ Recommendations</div>
                        <ul className="recommendations-list">
                            {llmExplanation.recommendations.map((rec, idx) => (
                                <li key={idx}>{rec}</li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* CNN-BERT Patterns */}
                {cnnBertResult && cnnBertResult.cnn_patterns && cnnBertResult.cnn_patterns.length > 0 && (
                    <div className="chatbot-message">
                        <div className="message-label">🔍 Detected Patterns</div>
                        <div className="patterns-grid">
                            {cnnBertResult.cnn_patterns.map((pattern, idx) => (
                                <div key={idx} className="pattern-card">
                                    <div className="pattern-category">
                                        {pattern.category.replace(/_/g, ' ').toUpperCase()}
                                    </div>
                                    <div className="pattern-score">
                                        {Math.round(pattern.score * 100)}% match
                                    </div>
                                    <div className="pattern-matches">
                                        {pattern.matches.slice(0, 3).join(', ')}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Time-Series Context */}
                {timeseriesData && timeseriesData.historical_context && (
                    <div className="chatbot-message">
                        <div className="message-label">📈 Historical Context</div>
                        <div className="message-text">
                            {timeseriesData.historical_context.split('\n\n').map((para, idx) => (
                                <p key={idx} dangerouslySetInnerHTML={{ __html: para.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }} />
                            ))}
                        </div>
                    </div>
                )}

                {/* Risk Forecast */}
                {timeseriesData && timeseriesData.risk_forecast && (
                    <div className="chatbot-message">
                        <div className="message-label">🔮 Risk Forecast</div>
                        <div className="message-text forecast">
                            <p dangerouslySetInnerHTML={{ __html: timeseriesData.risk_forecast.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }} />
                        </div>
                    </div>
                )}

                {/* Similar Incidents */}
                {timeseriesData && timeseriesData.similar_incidents && timeseriesData.similar_incidents.length > 0 && (
                    <div className="chatbot-message">
                        <div className="message-label">📚 Similar Past Incidents</div>
                        <div className="incidents-list">
                            {timeseriesData.similar_incidents.map((incident, idx) => (
                                <div key={idx} className="incident-card">
                                    <div className="incident-date">{incident.date}</div>
                                    <div className="incident-description">{incident.description}</div>
                                    <div className="incident-outcome">
                                        <strong>Outcome:</strong> {incident.outcome}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            <div className="chatbot-footer">
                <div className="chatbot-disclaimer">
                    💡 This analysis is advisory only. Always verify critical information from trusted sources.
                </div>
            </div>
        </div>
    );
};

export default ChatbotPanel;
