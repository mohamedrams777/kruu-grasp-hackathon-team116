import React from 'react';
import './RiskMeter.css';

interface RiskMeterProps {
    harmIndex: number;
    riskLevel: 'Low' | 'Medium' | 'High';
    uncertainty: number;
}

const RiskMeter: React.FC<RiskMeterProps> = ({ harmIndex, riskLevel, uncertainty }) => {
    const circumference = 2 * Math.PI * 90;
    const offset = circumference - (harmIndex / 100) * circumference;

    const getRiskColor = () => {
        if (harmIndex <= 30) return 'var(--color-success)';
        if (harmIndex <= 60) return 'var(--color-warning)';
        return 'var(--color-danger)';
    };

    const getRiskGradient = () => {
        if (harmIndex <= 30) return 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
        if (harmIndex <= 60) return 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)';
        return 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
    };

    return (
        <div className="risk-meter-container glass fade-in">
            <h3 className="risk-meter-title">Harm Risk Assessment</h3>

            <div className="risk-meter-visual">
                <svg width="240" height="240" viewBox="0 0 240 240">
                    {/* Background circle */}
                    <circle
                        cx="120"
                        cy="120"
                        r="90"
                        fill="none"
                        stroke="var(--color-border)"
                        strokeWidth="20"
                    />

                    {/* Progress circle */}
                    <circle
                        cx="120"
                        cy="120"
                        r="90"
                        fill="none"
                        stroke={getRiskColor()}
                        strokeWidth="20"
                        strokeDasharray={circumference}
                        strokeDashoffset={offset}
                        strokeLinecap="round"
                        className="risk-meter-progress"
                        style={{
                            filter: `drop-shadow(0 0 10px ${getRiskColor()})`,
                        }}
                    />

                    {/* Center text */}
                    <text
                        x="120"
                        y="110"
                        textAnchor="middle"
                        className="risk-meter-value"
                        fill={getRiskColor()}
                    >
                        {harmIndex}
                    </text>
                    <text
                        x="120"
                        y="135"
                        textAnchor="middle"
                        className="risk-meter-label"
                        fill="var(--color-text-muted)"
                    >
                        / 100
                    </text>
                </svg>
            </div>

            <div className="risk-level-badge" style={{ background: getRiskGradient() }}>
                <span className="risk-level-icon">
                    {riskLevel === 'Low' && '✓'}
                    {riskLevel === 'Medium' && '⚠'}
                    {riskLevel === 'High' && '⚠'}
                </span>
                <span className="risk-level-text">{riskLevel} Risk</span>
            </div>

            <div className="uncertainty-indicator">
                <span className="text-small text-muted">
                    Uncertainty: ±{uncertainty}%
                </span>
            </div>
        </div>
    );
};

export default RiskMeter;
