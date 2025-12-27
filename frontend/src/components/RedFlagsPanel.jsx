/**
 * RedFlagsPanel Component
 * Displays red flags (warnings) and trust indicators from verification
 */

import React, { useState } from 'react';
import { AlertTriangle, CheckCircle, Shield, XCircle, Info } from 'lucide-react';

const RedFlagsPanel = ({ redFlags, trustIndicators }) => {
  const [activeTab, setActiveTab] = useState('flags'); // 'flags' or 'trust'

  if ((!redFlags || redFlags.length === 0) && (!trustIndicators || trustIndicators.length === 0)) {
    return null;
  }

  const getSeverityConfig = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL':
        return {
          icon: XCircle,
          color: '#ef4444',
          bgColor: 'rgba(239, 68, 68, 0.1)',
          label: 'Critical'
        };
      case 'HIGH':
        return {
          icon: AlertTriangle,
          color: '#f59e0b',
          bgColor: 'rgba(245, 158, 11, 0.1)',
          label: 'High'
        };
      case 'MEDIUM':
        return {
          icon: Info,
          color: '#3b82f6',
          bgColor: 'rgba(59, 130, 246, 0.1)',
          label: 'Medium'
        };
      case 'LOW':
        return {
          icon: Info,
          color: '#6b7280',
          bgColor: 'rgba(107, 114, 128, 0.1)',
          label: 'Low'
        };
      default:
        return {
          icon: Info,
          color: '#6b7280',
          bgColor: 'rgba(107, 114, 128, 0.1)',
          label: 'Info'
        };
    }
  };

  const sortedFlags = redFlags ? [...redFlags].sort((a, b) => {
    const severityOrder = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
    return severityOrder[a.severity?.toUpperCase()] - severityOrder[b.severity?.toUpperCase()];
  }) : [];

  const flagCount = redFlags?.length || 0;
  const trustCount = trustIndicators?.length || 0;

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Security Analysis</h2>
        <p className="card-description">
          Warning indicators and trust signals identified during verification
        </p>
      </div>

      {/* Tabs */}
      <div style={{
        display: 'flex',
        gap: '0.5rem',
        marginBottom: '1.5rem',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        paddingBottom: '0.5rem'
      }}>
        <button
          onClick={() => setActiveTab('flags')}
          style={{
            padding: '0.5rem 1rem',
            background: activeTab === 'flags' ? 'rgba(239, 68, 68, 0.2)' : 'transparent',
            border: 'none',
            borderBottom: activeTab === 'flags' ? '2px solid var(--color-reject)' : '2px solid transparent',
            color: activeTab === 'flags' ? 'var(--color-reject)' : 'var(--text-muted)',
            cursor: 'pointer',
            fontSize: '0.875rem',
            fontWeight: 600,
            transition: 'all 0.2s ease',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}
        >
          <AlertTriangle size={16} />
          Red Flags
          {flagCount > 0 && (
            <span style={{
              background: 'var(--color-reject)',
              color: 'white',
              padding: '0.125rem 0.5rem',
              borderRadius: '12px',
              fontSize: '0.75rem',
              fontWeight: 700
            }}>
              {flagCount}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab('trust')}
          style={{
            padding: '0.5rem 1rem',
            background: activeTab === 'trust' ? 'rgba(16, 185, 129, 0.2)' : 'transparent',
            border: 'none',
            borderBottom: activeTab === 'trust' ? '2px solid var(--color-verified)' : '2px solid transparent',
            color: activeTab === 'trust' ? 'var(--color-verified)' : 'var(--text-muted)',
            cursor: 'pointer',
            fontSize: '0.875rem',
            fontWeight: 600,
            transition: 'all 0.2s ease',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}
        >
          <CheckCircle size={16} />
          Trust Indicators
          {trustCount > 0 && (
            <span style={{
              background: 'var(--color-verified)',
              color: 'white',
              padding: '0.125rem 0.5rem',
              borderRadius: '12px',
              fontSize: '0.75rem',
              fontWeight: 700
            }}>
              {trustCount}
            </span>
          )}
        </button>
      </div>

      {/* Content */}
      {activeTab === 'flags' && (
        <div>
          {sortedFlags.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {sortedFlags.map((flag, index) => {
                const config = getSeverityConfig(flag.severity);
                const Icon = config.icon;

                return (
                  <div
                    key={index}
                    style={{
                      padding: '1rem',
                      background: config.bgColor,
                      border: `1px solid ${config.color}40`,
                      borderLeft: `4px solid ${config.color}`,
                      borderRadius: 'var(--radius-md)',
                      display: 'flex',
                      gap: '1rem',
                      alignItems: 'flex-start'
                    }}
                  >
                    {/* Icon */}
                    <div style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: '50%',
                      background: `${config.color}20`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0
                    }}>
                      <Icon size={18} style={{ color: config.color }} />
                    </div>

                    {/* Content */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem', flexWrap: 'wrap' }}>
                        {/* Severity Badge */}
                        <span style={{
                          fontSize: '0.75rem',
                          fontWeight: 700,
                          color: config.color,
                          textTransform: 'uppercase',
                          letterSpacing: '0.5px'
                        }}>
                          {config.label}
                        </span>

                        {/* Layer Badge */}
                        {flag.layer && (
                          <span style={{
                            fontSize: '0.7rem',
                            padding: '0.125rem 0.5rem',
                            background: 'rgba(255, 255, 255, 0.1)',
                            borderRadius: 'var(--radius-sm)',
                            color: 'var(--text-muted)'
                          }}>
                            {flag.layer.replace('_', ' ').replace('layer', 'Layer')}
                          </span>
                        )}
                      </div>

                      {/* Message */}
                      <p style={{
                        fontSize: '0.875rem',
                        color: 'var(--text-primary)',
                        marginBottom: flag.details ? '0.5rem' : 0,
                        lineHeight: 1.5
                      }}>
                        {flag.message}
                      </p>

                      {/* Details */}
                      {flag.details && (
                        <p style={{
                          fontSize: '0.75rem',
                          color: 'var(--text-muted)',
                          lineHeight: 1.4,
                          fontStyle: 'italic'
                        }}>
                          {flag.details}
                        </p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div style={{
              padding: '2rem',
              textAlign: 'center',
              background: 'rgba(16, 185, 129, 0.05)',
              border: '1px solid rgba(16, 185, 129, 0.2)',
              borderRadius: 'var(--radius-md)'
            }}>
              <CheckCircle size={48} style={{ color: 'var(--color-verified)', marginBottom: '1rem' }} />
              <p style={{ fontSize: '1rem', color: 'var(--color-verified)', fontWeight: 600, marginBottom: '0.5rem' }}>
                No Red Flags Detected
              </p>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                All verification checks passed without any warning indicators
              </p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'trust' && (
        <div>
          {trustIndicators && trustIndicators.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {trustIndicators.map((indicator, index) => (
                <div
                  key={index}
                  style={{
                    padding: '1rem',
                    background: 'rgba(16, 185, 129, 0.05)',
                    border: '1px solid rgba(16, 185, 129, 0.2)',
                    borderLeft: '4px solid var(--color-verified)',
                    borderRadius: 'var(--radius-md)',
                    display: 'flex',
                    gap: '1rem',
                    alignItems: 'flex-start'
                  }}
                >
                  {/* Icon */}
                  <div style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '50%',
                    background: 'rgba(16, 185, 129, 0.2)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0
                  }}>
                    <CheckCircle size={18} style={{ color: 'var(--color-verified)' }} />
                  </div>

                  {/* Content */}
                  <p style={{
                    fontSize: '0.875rem',
                    color: 'var(--text-primary)',
                    margin: 0,
                    lineHeight: 1.5,
                    flex: 1
                  }}>
                    {indicator}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div style={{
              padding: '2rem',
              textAlign: 'center',
              background: 'rgba(107, 114, 128, 0.1)',
              border: '1px solid rgba(107, 114, 128, 0.2)',
              borderRadius: 'var(--radius-md)'
            }}>
              <Shield size={48} style={{ color: 'var(--text-muted)', marginBottom: '1rem' }} />
              <p style={{ fontSize: '1rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '0.5rem' }}>
                No Trust Indicators Found
              </p>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                Limited positive signals were identified during verification
              </p>
            </div>
          )}
        </div>
      )}

      {/* Summary Stats */}
      <div style={{
        marginTop: '1.5rem',
        padding: '1rem',
        background: 'rgba(255, 255, 255, 0.02)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: 'var(--radius-md)',
        display: 'flex',
        justifyContent: 'space-around',
        gap: '1rem'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
            Total Flags
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-reject)' }}>
            {flagCount}
          </div>
        </div>

        <div style={{ width: '1px', background: 'rgba(255, 255, 255, 0.1)' }} />

        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
            Trust Signals
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-verified)' }}>
            {trustCount}
          </div>
        </div>

        <div style={{ width: '1px', background: 'rgba(255, 255, 255, 0.1)' }} />

        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
            Risk Ratio
          </div>
          <div style={{ 
            fontSize: '1.5rem', 
            fontWeight: 700, 
            color: flagCount > trustCount ? 'var(--color-reject)' : 'var(--color-verified)'
          }}>
            {trustCount > 0 ? (flagCount / trustCount).toFixed(1) : flagCount > 0 ? '∞' : '0'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RedFlagsPanel;