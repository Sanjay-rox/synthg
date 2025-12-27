import React from 'react';

function ScoreDisplay({ result }) {
  const { total_score, bucket, interpretation, score_breakdown } = result;
  
  const bucketClass = bucket.replace('_', '-');
  
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const progress = (total_score / 100) * circumference;
  const dashOffset = circumference - progress;

  const breakdownItems = [
    { label: 'Format', value: score_breakdown.format_legitimacy, weight: 10 },
    { label: 'Temporal', value: score_breakdown.temporal_analysis, weight: 15 },
    { label: 'Cross-Reference', value: score_breakdown.cross_reference, weight: 10 },
    { label: 'Platform', value: score_breakdown.platform_presence, weight: 10 },
    { label: 'Domain Trust', value: score_breakdown.domain_trust, weight: 8 },
    { label: 'Behavioral', value: score_breakdown.behavioral, weight: 7 },
    { label: 'Connections', value: score_breakdown.connection_count, weight: 8 },
    { label: 'Graph Depth', value: score_breakdown.temporal_depth, weight: 8 },
  ];

  const getColor = (value) => {
    if (value >= 70) return 'var(--accent-primary)';
    if (value >= 50) return 'var(--accent-secondary)';
    if (value >= 30) return 'var(--accent-warning)';
    return 'var(--accent-danger)';
  };

  const getBucketLabel = () => {
    switch (bucket) {
      case 'real': return 'Verified Authentic';
      case 'likely_real': return 'Likely Authentic';
      case 'suspicious': return 'Needs Review';
      case 'synthetic': return 'Likely Synthetic';
      default: return 'Unknown';
    }
  };

  return (
    <div className="card slide-in">
      <div className="card-header">
        <div className="card-icon">📊</div>
        <h3 className="card-title">Verification Score</h3>
      </div>

      <div className="score-container">
        {/* Circular Score */}
        <div className="score-circle-wrapper">
          <div className="score-circle">
            <svg className="score-ring" viewBox="0 0 160 160">
              <circle
                className="score-ring-bg"
                cx="80"
                cy="80"
                r={radius}
              />
              <circle
                className={`score-ring-progress ${bucketClass}`}
                cx="80"
                cy="80"
                r={radius}
                strokeDasharray={circumference}
                strokeDashoffset={dashOffset}
              />
            </svg>
            <div className="score-value">
              <div className="score-number" style={{ color: getColor(total_score) }}>
                {Math.round(total_score)}
              </div>
              <div className="score-label">of 100</div>
            </div>
          </div>
          
          <div className={`verdict-badge ${bucketClass}`}>
            {getBucketLabel()}
          </div>
        </div>

        {/* Score Details */}
        <div style={{ flex: 1 }}>
          {/* Claude AI Section */}
          {result.claude_verdict && result.claude_verdict !== 'INCONCLUSIVE' && (
            <div className="claude-section">
              <div className="claude-header">
                <span>🧠</span>
                <span className="claude-label">Claude AI Analysis</span>
              </div>
              <div className="claude-verdict" style={{ color: getColor(result.claude_confidence) }}>
                {result.claude_verdict} • {result.claude_confidence}% confidence
              </div>
              {result.claude_reasoning && (
                <div className="claude-reasoning">
                  {result.claude_reasoning}
                </div>
              )}
            </div>
          )}

          {/* Score Breakdown */}
          <div className="section-header">
            <div className="section-title">Signal Breakdown</div>
          </div>
          
          <div className="progress-list">
            {breakdownItems.map((item, i) => (
              <div key={i} className="progress-item">
                <span className="progress-label">{item.label}</span>
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ 
                      width: `${item.value}%`,
                      background: getColor(item.value)
                    }}
                  />
                </div>
                <span className="progress-value">{Math.round(item.value)}</span>
              </div>
            ))}
          </div>

          {/* Graph Analysis Metrics */}
          {(result.graph_density > 0 || result.oldest_relationship_years > 0) && (
            <div style={{ marginTop: '20px' }}>
              <div className="section-header">
                <div className="section-title">Graph Analysis</div>
              </div>
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(3, 1fr)', 
                gap: '12px',
                marginTop: '12px'
              }}>
                <div style={{ 
                  padding: '12px', 
                  background: 'var(--surface-secondary)',
                  borderRadius: 'var(--radius-md)',
                  textAlign: 'center'
                }}>
                  <div style={{ 
                    fontSize: '1.25rem', 
                    fontWeight: '600',
                    color: result.graph_density >= 1.5 ? 'var(--accent-primary)' : 'var(--accent-warning)',
                    fontFamily: 'var(--font-mono)'
                  }}>
                    {result.graph_density?.toFixed(2) || '0'}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Density</div>
                </div>
                <div style={{ 
                  padding: '12px', 
                  background: 'var(--surface-secondary)',
                  borderRadius: 'var(--radius-md)',
                  textAlign: 'center'
                }}>
                  <div style={{ 
                    fontSize: '1.25rem', 
                    fontWeight: '600',
                    color: result.oldest_relationship_years >= 5 ? 'var(--accent-primary)' : 'var(--accent-warning)',
                    fontFamily: 'var(--font-mono)'
                  }}>
                    {result.oldest_relationship_years?.toFixed(1) || '0'}y
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Oldest Link</div>
                </div>
                <div style={{ 
                  padding: '12px', 
                  background: 'var(--surface-secondary)',
                  borderRadius: 'var(--radius-md)',
                  textAlign: 'center'
                }}>
                  <div style={{ 
                    fontSize: '1.25rem', 
                    fontWeight: '600',
                    color: result.cross_reference_count > 0 ? 'var(--accent-primary)' : 'var(--text-muted)',
                    fontFamily: 'var(--font-mono)'
                  }}>
                    {result.cross_reference_count || 0}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Cross-Refs</div>
                </div>
              </div>
            </div>
          )}

          {/* Synthetic Indicators */}
          {result.synthetic_indicators && result.synthetic_indicators.length > 0 && (
            <div style={{ 
              marginTop: '16px', 
              padding: '12px 16px', 
              background: 'rgba(239, 68, 68, 0.08)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid rgba(239, 68, 68, 0.2)'
            }}>
              <div style={{ 
                fontSize: '0.7rem', 
                color: 'var(--accent-danger)', 
                fontWeight: '600',
                marginBottom: '8px',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                ⚠️ Synthetic Indicators Detected
              </div>
              {result.synthetic_indicators.map((indicator, i) => (
                <div key={i} style={{ 
                  fontSize: '0.75rem', 
                  color: 'var(--text-secondary)',
                  padding: '4px 0'
                }}>
                  • {indicator}
                </div>
              ))}
            </div>
          )}

          {/* Penalty Info */}
          {score_breakdown.red_flag_penalty > 0 && (
            <div style={{ 
              marginTop: '16px', 
              padding: '12px 16px', 
              background: 'var(--accent-danger-dim)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid rgba(239, 68, 68, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}>
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>
                Red Flag Penalty Applied
              </span>
              <span style={{ 
                color: 'var(--accent-danger)', 
                fontWeight: '600',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.875rem'
              }}>
                -{score_breakdown.red_flag_penalty.toFixed(1)} pts
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ScoreDisplay;
