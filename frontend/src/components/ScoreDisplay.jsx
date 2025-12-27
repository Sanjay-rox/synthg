/**
 * ScoreDisplay Component
 * Shows final verification score with circular progress indicator
 */

import React, { useEffect, useState } from 'react';
import { Shield, TrendingUp, TrendingDown, Minus } from 'lucide-react';

const ScoreDisplay = ({ score, verdict, confidence, recommendation }) => {
  const [animatedScore, setAnimatedScore] = useState(0);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    // Animate score counting up
    let start = 0;
    const end = score || 0;
    const duration = 2000; // 2 seconds
    const increment = end / (duration / 16); // 60fps

    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setAnimatedScore(end);
        clearInterval(timer);
      } else {
        setAnimatedScore(Math.floor(start));
      }
    }, 16);

    return () => clearInterval(timer);
  }, [score]);

  const getVerdictColor = () => {
    switch (verdict) {
      case 'VERIFIED':
        return 'var(--color-verified)';
      case 'SUSPICIOUS':
        return 'var(--color-suspicious)';
      case 'REJECT':
        return 'var(--color-reject)';
      default:
        return 'var(--text-muted)';
    }
  };

  const getVerdictIcon = () => {
    switch (verdict) {
      case 'VERIFIED':
        return <TrendingUp size={24} />;
      case 'SUSPICIOUS':
        return <Minus size={24} />;
      case 'REJECT':
        return <TrendingDown size={24} />;
      default:
        return <Shield size={24} />;
    }
  };

  const getConfidenceColor = () => {
    switch (confidence) {
      case 'HIGH':
        return 'var(--color-verified)';
      case 'MEDIUM':
        return 'var(--color-suspicious)';
      case 'LOW':
        return 'var(--color-reject)';
      default:
        return 'var(--text-muted)';
    }
  };

  // Calculate circle progress
  const radius = 100;
  const circumference = 2 * Math.PI * radius;
  const progress = ((animatedScore || 0) / 100) * circumference;
  const dashOffset = circumference - progress;

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Verification Score</h2>
        <p className="card-description">
          Overall authenticity assessment
        </p>
      </div>

      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        gap: '2rem' 
      }}>
        {/* Circular Score Display */}
        <div style={{ position: 'relative', display: 'inline-block' }}>
          <svg width="240" height="240" style={{ transform: 'rotate(-90deg)' }}>
            {/* Background circle */}
            <circle
              cx="120"
              cy="120"
              r={radius}
              stroke="rgba(255, 255, 255, 0.1)"
              strokeWidth="12"
              fill="none"
            />
            
            {/* Progress circle */}
            <circle
              cx="120"
              cy="120"
              r={radius}
              stroke={getVerdictColor()}
              strokeWidth="12"
              fill="none"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={dashOffset}
              style={{
                transition: 'stroke-dashoffset 2s ease',
                filter: 'drop-shadow(0 0 10px currentColor)'
              }}
            />
          </svg>

          {/* Score text in center */}
          <div style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            textAlign: 'center'
          }}>
            <div style={{ 
              fontSize: '3.5rem', 
              fontWeight: 700,
              color: getVerdictColor(),
              lineHeight: 1,
              marginBottom: '0.25rem'
            }}>
              {Math.round(animatedScore)}
            </div>
            <div style={{ 
              fontSize: '1rem', 
              color: 'var(--text-muted)',
              fontWeight: 500 
            }}>
              / 100
            </div>
          </div>
        </div>

        {/* Verdict Badge */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          padding: '1rem 2rem',
          background: `${getVerdictColor()}20`,
          border: `2px solid ${getVerdictColor()}`,
          borderRadius: 'var(--radius-lg)',
          boxShadow: `0 0 20px ${getVerdictColor()}40`
        }}>
          {getVerdictIcon()}
          <span style={{
            fontSize: '1.5rem',
            fontWeight: 700,
            color: getVerdictColor(),
            textTransform: 'uppercase',
            letterSpacing: '1px'
          }}>
            {verdict || 'PENDING'}
          </span>
        </div>

        {/* Confidence & Recommendation */}
        <div style={{
          width: '100%',
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem'
        }}>
          {/* Confidence Level */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '1rem',
            background: 'rgba(255, 255, 255, 0.05)',
            borderRadius: 'var(--radius-md)'
          }}>
            <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              Confidence Level
            </span>
            <span style={{
              fontSize: '0.875rem',
              fontWeight: 600,
              color: getConfidenceColor(),
              padding: '0.25rem 0.75rem',
              background: `${getConfidenceColor()}20`,
              borderRadius: 'var(--radius-sm)',
              border: `1px solid ${getConfidenceColor()}`
            }}>
              {confidence || 'N/A'}
            </span>
          </div>

          {/* Recommendation */}
          {recommendation && (
            <div style={{
              padding: '1rem',
              background: 'rgba(0, 217, 255, 0.05)',
              border: '1px solid rgba(0, 217, 255, 0.2)',
              borderRadius: 'var(--radius-md)',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '0.75rem'
            }}>
              <Shield size={20} style={{ color: 'var(--accent-cyan)', flexShrink: 0, marginTop: '0.125rem' }} />
              <div>
                <p style={{ 
                  fontSize: '0.75rem', 
                  color: 'var(--text-muted)', 
                  marginBottom: '0.25rem',
                  textTransform: 'uppercase',
                  fontWeight: 600,
                  letterSpacing: '0.5px'
                }}>
                  Recommendation
                </p>
                <p style={{ 
                  fontSize: '0.875rem', 
                  color: 'var(--text-primary)',
                  lineHeight: 1.5
                }}>
                  {recommendation}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Score Interpretation */}
        <div style={{
          width: '100%',
          padding: '1rem',
          background: 'rgba(255, 255, 255, 0.02)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <button
            onClick={() => setShowDetails(!showDetails)}
            style={{
              width: '100%',
              background: 'none',
              border: 'none',
              color: 'var(--text-secondary)',
              fontSize: '0.875rem',
              cursor: 'pointer',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: 0
            }}
          >
            <span style={{ fontWeight: 500 }}>Score Interpretation</span>
            <span style={{ 
              transform: showDetails ? 'rotate(180deg)' : 'rotate(0deg)',
              transition: 'transform 0.2s ease'
            }}>
              ▼
            </span>
          </button>

          {showDetails && (
            <div style={{ 
              marginTop: '1rem', 
              paddingTop: '1rem', 
              borderTop: '1px solid rgba(255, 255, 255, 0.1)',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.75rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{ 
                  width: '40px', 
                  height: '4px', 
                  background: 'var(--color-verified)',
                  borderRadius: '2px'
                }} />
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  90-100: <strong style={{ color: 'var(--color-verified)' }}>VERIFIED</strong> - High confidence authentic
                </span>
              </div>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{ 
                  width: '40px', 
                  height: '4px', 
                  background: 'var(--color-suspicious)',
                  borderRadius: '2px'
                }} />
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  50-89: <strong style={{ color: 'var(--color-suspicious)' }}>SUSPICIOUS</strong> - Manual review needed
                </span>
              </div>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{ 
                  width: '40px', 
                  height: '4px', 
                  background: 'var(--color-reject)',
                  borderRadius: '2px'
                }} />
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  0-49: <strong style={{ color: 'var(--color-reject)' }}>REJECT</strong> - Likely synthetic
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ScoreDisplay;