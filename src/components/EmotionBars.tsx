import React from 'react';
import type { EmotionScores } from '../types';
import './EmotionBars.css';

interface EmotionBarsProps {
    emotions: EmotionScores;
}

const EmotionBars: React.FC<EmotionBarsProps> = ({ emotions }) => {
    const emotionData = [
        { name: 'Anger', value: emotions.anger, color: 'var(--emotion-anger)', icon: '😠' },
        { name: 'Fear', value: emotions.fear, color: 'var(--emotion-fear)', icon: '😨' },
        { name: 'Joy', value: emotions.joy, color: 'var(--emotion-joy)', icon: '😊' },
        { name: 'Sadness', value: emotions.sadness, color: 'var(--emotion-sadness)', icon: '😢' },
        { name: 'Neutral', value: emotions.neutral, color: 'var(--emotion-neutral)', icon: '😐' },
    ];

    return (
        <div className="emotion-bars-container glass fade-in">
            <h3 className="emotion-bars-title">Emotional Analysis</h3>

            <div className="emotion-bars-list">
                {emotionData.map((emotion, index) => (
                    <div
                        key={emotion.name}
                        className="emotion-bar-item"
                        style={{ animationDelay: `${index * 0.1}s` }}
                    >
                        <div className="emotion-bar-header">
                            <span className="emotion-icon">{emotion.icon}</span>
                            <span className="emotion-name">{emotion.name}</span>
                            <span className="emotion-value">{Math.round(emotion.value * 100)}%</span>
                        </div>

                        <div className="emotion-bar-track">
                            <div
                                className="emotion-bar-fill"
                                style={{
                                    width: `${emotion.value * 100}%`,
                                    background: emotion.color,
                                    boxShadow: `0 0 10px ${emotion.color}`,
                                }}
                            />
                        </div>
                    </div>
                ))}
            </div>

            <div className="emotion-summary">
                <p className="text-small text-muted">
                    {emotions.anger > 0.6 || emotions.fear > 0.6 ? (
                        <span>⚠️ High emotional intensity detected</span>
                    ) : (
                        <span>✓ Moderate emotional tone</span>
                    )}
                </p>
            </div>
        </div>
    );
};

export default EmotionBars;
