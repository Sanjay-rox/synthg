/**
 * LayerBreakdown Component
 * Shows detailed breakdown of each layer's contribution to final score
 */

import React, { useState } from 'react';
import { FileText, Network, Activity, Link, ChevronDown, ChevronUp } from 'lucide-react';

const LayerBreakdown = ({ layerContributions, processingTime }) => {
  const [expandedLayer, setExpandedLayer] = useState(null);

  if (!layerContributions || layerContributions.length === 0) {
    return null;
  }

  const layerIcons = {
    'layer_1': FileText,
    'layer_2_3': Network,
    'layer_4': Activity,
    'layer_5': Link
  };

  const layerColors = {
    'layer_1': '#a855f7',
    'layer_2_3': '#00d9ff',
    'layer_4': '#ec4899',
    'layer_5': '#10b981'
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'var(--color-verified)';
    if (score >= 60) return 'var(--color-suspicious)';
    return 'var(--color-reject)';
  };

  const toggleLayer = (layerId) => {
    setExpandedLayer(expandedLayer === layerId ? null : layerId);
  };

  const formatTime = (ms) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Layer Breakdown</h2>
        <p className="card-description">
          Detailed analysis from each verification layer
        </p>
      </div>

      {/* Processing Time */}
      {processingTime && (
        <div style={{
          padding: '0.75rem 1rem',
          background: 'rgba(0, 217, 255, 0.05)',
          border: '1px solid rgba(0, 217, 255, 0.2)',
          borderRadius: 'var(--radius-md)',
          marginBottom: '1.5rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            Total Processing Time
          </span>
          <span style={{ 
            fontSize: '0.875rem', 
            fontWeight: 600, 
            color: 'var(--accent-cyan)',
            fontFamily: 'JetBrains Mono, monospace'
          }}>
            {formatTime(processingTime)}
          </span>
        </div>
      )}

      {/* Layer Cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {layerContributions.map((layer) => {
          const Icon = layerIcons[layer.layer_id] || FileText;
          const color = layerColors[layer.layer_id] || '#00d9ff';
          const isExpanded = expandedLayer === layer.layer_id;

          return (
            <div
              key={layer.layer_id}
              style={{
                border: `1px solid rgba(255, 255, 255, 0.1)`,
                borderRadius: 'var(--radius-lg)',
                overflow: 'hidden',
                background: 'rgba(255, 255, 255, 0.02)',
                transition: 'all 0.2s ease'
              }}
            >
              {/* Layer Header */}
              <div
                onClick={() => toggleLayer(layer.layer_id)}
                style={{
                  padding: '1rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '1rem',
                  background: isExpanded ? 'rgba(255, 255, 255, 0.05)' : 'transparent',
                  transition: 'background 0.2s ease'
                }}
              >
                {/* Icon */}
                <div
                  style={{
                    width: '48px',
                    height: '48px',
                    borderRadius: 'var(--radius-md)',
                    background: `${color}20`,
                    border: `2px solid ${color}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0
                  }}
                >
                  <Icon size={24} style={{ color }} />
                </div>

                {/* Layer Info */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <h3 style={{ 
                    fontSize: '1rem', 
                    fontWeight: 600,
                    color: 'var(--text-primary)',
                    marginBottom: '0.25rem'
                  }}>
                    {layer.layer_name}
                  </h3>
                  
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
                    {/* Status Badge */}
                    <span style={{
                      fontSize: '0.75rem',
                      padding: '0.125rem 0.5rem',
                      background: layer.status === 'SUCCESS' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                      color: layer.status === 'SUCCESS' ? 'var(--color-verified)' : 'var(--color-reject)',
                      borderRadius: 'var(--radius-sm)',
                      fontWeight: 600,
                      textTransform: 'uppercase'
                    }}>
                      {layer.status}
                    </span>

                    {/* Weight */}
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      Weight: <strong style={{ color: 'var(--text-secondary)' }}>{(layer.weight * 100).toFixed(0)}%</strong>
                    </span>
                  </div>
                </div>

                {/* Score Display */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexShrink: 0 }}>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ 
                      fontSize: '1.75rem', 
                      fontWeight: 700,
                      color: getScoreColor(layer.score),
                      lineHeight: 1
                    }}>
                      {Math.round(layer.score)}
                    </div>
                    <div style={{ 
                      fontSize: '0.75rem', 
                      color: 'var(--text-muted)',
                      marginTop: '0.125rem'
                    }}>
                      / 100
                    </div>
                  </div>

                  {/* Contribution */}
                  <div style={{
                    padding: '0.5rem 0.75rem',
                    background: 'rgba(0, 217, 255, 0.1)',
                    borderRadius: 'var(--radius-sm)',
                    textAlign: 'center'
                  }}>
                    <div style={{ 
                      fontSize: '0.75rem', 
                      color: 'var(--text-muted)',
                      marginBottom: '0.125rem'
                    }}>
                      Contribution
                    </div>
                    <div style={{ 
                      fontSize: '1rem', 
                      fontWeight: 600,
                      color: 'var(--accent-cyan)'
                    }}>
                      +{layer.contribution.toFixed(1)}
                    </div>
                  </div>

                  {/* Expand Icon */}
                  {isExpanded ? (
                    <ChevronUp size={20} style={{ color: 'var(--text-muted)' }} />
                  ) : (
                    <ChevronDown size={20} style={{ color: 'var(--text-muted)' }} />
                  )}
                </div>
              </div>

              {/* Expanded Details */}
              {isExpanded && (
                <div style={{
                  padding: '1rem',
                  background: 'rgba(0, 0, 0, 0.2)',
                  borderTop: '1px solid rgba(255, 255, 255, 0.1)'
                }}>
                  {/* Progress Bar */}
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      marginBottom: '0.5rem',
                      fontSize: '0.75rem',
                      color: 'var(--text-muted)'
                    }}>
                      <span>Score Contribution</span>
                      <span>{((layer.contribution / layer.score) * 100).toFixed(0)}% of layer score</span>
                    </div>
                    <div style={{
                      width: '100%',
                      height: '6px',
                      background: 'rgba(255, 255, 255, 0.1)',
                      borderRadius: '3px',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        height: '100%',
                        width: `${layer.score}%`,
                        background: `linear-gradient(90deg, ${color}, ${getScoreColor(layer.score)})`,
                        transition: 'width 0.5s ease'
                      }} />
                    </div>
                  </div>

                  {/* Key Findings */}
                  {layer.key_findings && layer.key_findings.length > 0 && (
                    <div>
                      <h4 style={{ 
                        fontSize: '0.875rem', 
                        fontWeight: 600,
                        color: 'var(--text-secondary)',
                        marginBottom: '0.75rem'
                      }}>
                        Key Findings
                      </h4>
                      <ul style={{
                        listStyle: 'none',
                        padding: 0,
                        margin: 0,
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '0.5rem'
                      }}>
                        {layer.key_findings.map((finding, index) => (
                          <li
                            key={index}
                            style={{
                              fontSize: '0.875rem',
                              color: 'var(--text-primary)',
                              padding: '0.5rem 0.75rem',
                              background: 'rgba(255, 255, 255, 0.05)',
                              borderLeft: `3px solid ${color}`,
                              borderRadius: '0 var(--radius-sm) var(--radius-sm) 0'
                            }}
                          >
                            {finding}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* No findings message */}
                  {(!layer.key_findings || layer.key_findings.length === 0) && (
                    <p style={{ 
                      fontSize: '0.875rem', 
                      color: 'var(--text-muted)',
                      textAlign: 'center',
                      padding: '1rem'
                    }}>
                      No additional findings to display
                    </p>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Summary Stats */}
      <div style={{
        marginTop: '1.5rem',
        padding: '1rem',
        background: 'rgba(255, 255, 255, 0.02)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: 'var(--radius-md)',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '1rem'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
            Layers Analyzed
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>
            {layerContributions.length}
          </div>
        </div>

        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
            Average Score
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-purple)' }}>
            {Math.round(layerContributions.reduce((sum, l) => sum + l.score, 0) / layerContributions.length)}
          </div>
        </div>

        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
            Highest Score
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-verified)' }}>
            {Math.round(Math.max(...layerContributions.map(l => l.score)))}
          </div>
        </div>

        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
            Lowest Score
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-reject)' }}>
            {Math.round(Math.min(...layerContributions.map(l => l.score)))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LayerBreakdown;