import React, { useState } from 'react';
import type { HarmAssessment } from '../types';
import './ExplanationPanel.css';

interface ExplanationPanelProps {
    assessment: HarmAssessment;
}

const ExplanationPanel: React.FC<ExplanationPanelProps> = ({ assessment }) => {
    const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview', 'cnn']));

    const toggleSection = (section: string) => {
        const newExpanded = new Set(expandedSections);
        if (newExpanded.has(section)) {
            newExpanded.delete(section);
        } else {
            newExpanded.add(section);
        }
        setExpandedSections(newExpanded);
    };

    return (
        <div className="explanation-panel glass-strong fade-in">
            <div className="explanation-header">
                <h3>⚠️ Risk Assessment Summary</h3>
                <p className="text-muted text-small">
                    This is an advisory assessment, not a censorship decision.
                </p>
            </div>

            {/* Overview */}
            <div className="explanation-section">
                <button
                    className={`section-toggle ${expandedSections.has('overview') ? 'active' : ''}`}
                    onClick={() => toggleSection('overview')}
                >
                    <span className="section-icon">📊</span>
                    <span className="section-title">Overview</span>
                    <span className="toggle-icon">{expandedSections.has('overview') ? '−' : '+'}</span>
                </button>

                {expandedSections.has('overview') && (
                    <div className="section-content">
                        <p>{assessment.explanation}</p>
                    </div>
                )}
            </div>

            {/* CNN Analysis */}
            <div className="explanation-section">
                <button
                    className={`section-toggle ${expandedSections.has('cnn') ? 'active' : ''}`}
                    onClick={() => toggleSection('cnn')}
                >
                    <span className="section-icon">🤖</span>
                    <span className="section-title">CNN Model Analysis</span>
                    <span className="toggle-icon">{expandedSections.has('cnn') ? '−' : '+'}</span>
                </button>

                {expandedSections.has('cnn') && (
                    <div className="section-content">
                        <p>
                            <strong>Model Confidence Score:</strong> {assessment.cnnHarmScore ? (assessment.cnnHarmScore * 100).toFixed(1) + '%' : 'N/A'}
                        </p>
                        <p className="text-small text-muted">
                            {assessment.cnnHarmScore && assessment.cnnHarmScore > 0.7
                                ? 'The CNN model has flagged this content as highly likely to be harmful based on training data.'
                                : assessment.cnnHarmScore && assessment.cnnHarmScore > 0.3
                                    ? 'The CNN model shows moderate concern regarding this content.'
                                    : 'The CNN model has a low confidence for harm in this statement.'}
                        </p>
                    </div>
                )}
            </div>

            {/* Intent Analysis */}
            <div className="explanation-section">
                <button
                    className={`section-toggle ${expandedSections.has('intent') ? 'active' : ''}`}
                    onClick={() => toggleSection('intent')}
                >
                    <span className="section-icon">🎯</span>
                    <span className="section-title">Intent & Call-to-Action</span>
                    <span className="toggle-icon">{expandedSections.has('intent') ? '−' : '+'}</span>
                </button>

                {expandedSections.has('intent') && (
                    <div className="section-content">
                        <ul className="info-list">
                            <li>
                                <strong>Intent Type:</strong> {assessment.intentAnalysis.type}
                            </li>
                            <li>
                                <strong>Explicit Call-to-Action:</strong>{' '}
                                {assessment.intentAnalysis.hasExplicitCTA ? 'Yes' : 'No'}
                            </li>
                            <li>
                                <strong>Implicit Call-to-Action:</strong>{' '}
                                {assessment.intentAnalysis.hasImplicitCTA ? 'Yes' : 'No'}
                            </li>
                            <li>
                                <strong>Dog-Whistle Probability:</strong>{' '}
                                {Math.round(assessment.intentAnalysis.dogWhistleProbability * 100)}%
                            </li>
                        </ul>
                    </div>
                )}
            </div>

            {/* Truth Verification */}
            <div className="explanation-section">
                <button
                    className={`section-toggle ${expandedSections.has('truth') ? 'active' : ''}`}
                    onClick={() => toggleSection('truth')}
                >
                    <span className="section-icon">🔍</span>
                    <span className="section-title">Truth Verification</span>
                    <span className="toggle-icon">{expandedSections.has('truth') ? '−' : '+'}</span>
                </button>

                {expandedSections.has('truth') && (
                    <div className="section-content">
                        <ul className="info-list">
                            <li>
                                <strong>Similarity to Known False Narratives:</strong>{' '}
                                {Math.round(assessment.truthVerification.similarityToFalseNarratives * 100)}%
                            </li>
                            <li>
                                <strong>Evidence Confidence:</strong> {assessment.truthVerification.evidenceConfidence}
                            </li>
                            <li>
                                <strong>Contradictory Sources Found:</strong>{' '}
                                {assessment.truthVerification.contradictorySources ? 'Yes' : 'No'}
                            </li>
                        </ul>

                        {assessment.truthVerification.similarClaims.length > 0 && (
                            <div className="similar-claims">
                                <strong>Similar Historical Claims:</strong>
                                <ul>
                                    {assessment.truthVerification.similarClaims.map((claim, idx) => (
                                        <li key={idx} className="text-small">{claim}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Historical Context */}
            <div className="explanation-section">
                <button
                    className={`section-toggle ${expandedSections.has('historical') ? 'active' : ''}`}
                    onClick={() => toggleSection('historical')}
                >
                    <span className="section-icon">📚</span>
                    <span className="section-title">Potential Consequences</span>
                    <span className="toggle-icon">{expandedSections.has('historical') ? '−' : '+'}</span>
                </button>

                {expandedSections.has('historical') && (
                    <div className="section-content">
                        <p className="text-small text-muted mb-sm">
                            Based on historical patterns, if acted upon, potential outcomes include:
                        </p>
                        <ul className="outcome-list">
                            {assessment.historicalContext.pastOutcomes.map((outcome, idx) => (
                                <li key={idx} className={`outcome-item outcome-${outcome.probability.toLowerCase()}`}>
                                    <span className="outcome-badge">{outcome.probability}</span>
                                    <span>{outcome.outcome}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>

            <div className="explanation-footer">
                <p className="text-small text-muted">
                    💡 <em>This assessment uses AI-powered analysis and may not be 100% accurate.
                        Please verify information from trusted sources before taking action.</em>
                </p>
            </div>
        </div>
    );
};

export default ExplanationPanel;
