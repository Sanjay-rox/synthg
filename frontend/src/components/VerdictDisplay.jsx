/**
 * VerdictDisplay Component
 * Shows final verdict with detailed explanation and action buttons
 */

import React from 'react';
import { Shield, CheckCircle, AlertTriangle, XCircle, Download, FileText, Copy, Check } from 'lucide-react';
import { useState } from 'react';

const VerdictDisplay = ({ verificationData }) => {
  const [copied, setCopied] = useState(false);

  if (!verificationData) {
    return null;
  }

  const { verification_id, final_score, verdict, confidence, recommendation, timestamp } = verificationData;

  const getVerdictConfig = () => {
    switch (verdict) {
      case 'VERIFIED':
        return {
          icon: CheckCircle,
          color: 'var(--color-verified)',
          bgColor: 'rgba(16, 185, 129, 0.1)',
          borderColor: 'var(--color-verified)',
          title: 'Identity Verified',
          description: 'This identity has passed all verification checks and appears to be authentic.',
          action: 'Proceed with Confidence'
        };
      case 'SUSPICIOUS':
        return {
          icon: AlertTriangle,
          color: 'var(--color-suspicious)',
          bgColor: 'rgba(245, 158, 11, 0.1)',
          borderColor: 'var(--color-suspicious)',
          title: 'Identity Suspicious',
          description: 'Some concerns were identified during verification. Manual review is recommended before proceeding.',
          action: 'Review Required'
        };
      case 'REJECT':
        return {
          icon: XCircle,
          color: 'var(--color-reject)',
          bgColor: 'rgba(239, 68, 68, 0.1)',
          borderColor: 'var(--color-reject)',
          title: 'Identity Rejected',
          description: 'This identity has failed verification and shows signs of being synthetic or fraudulent.',
          action: 'Do Not Proceed'
        };
      default:
        return {
          icon: Shield,
          color: 'var(--text-muted)',
          bgColor: 'rgba(255, 255, 255, 0.05)',
          borderColor: 'rgba(255, 255, 255, 0.2)',
          title: 'Verification Pending',
          description: 'Verification is in progress.',
          action: 'Please Wait'
        };
    }
  };

  const config = getVerdictConfig();
  const Icon = config.icon;

  const handleCopyId = () => {
    navigator.clipboard.writeText(verification_id);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadReport = () => {
    const reportData = JSON.stringify(verificationData, null, 2);
    const blob = new Blob([reportData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `synthguard_report_${verification_id}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const formatTimestamp = (ts) => {
    return new Date(ts).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  return (
    <div className="card" style={{
      background: config.bgColor,
      border: `2px solid ${config.borderColor}`,
      boxShadow: `0 0 30px ${config.color}40`
    }}>
      {/* Header with Icon */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '1.5rem',
        marginBottom: '2rem',
        paddingBottom: '2rem',
        borderBottom: `1px solid ${config.borderColor}40`
      }}>
        {/* Large Icon */}
        <div style={{
          width: '80px',
          height: '80px',
          borderRadius: '50%',
          background: `${config.color}20`,
          border: `3px solid ${config.color}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: `0 0 30px ${config.color}60`,
          animation: 'pulse 2s ease-in-out infinite'
        }}>
          <Icon size={40} style={{ color: config.color }} />
        </div>

        {/* Title */}
        <div style={{ textAlign: 'center' }}>
          <h2 style={{
            fontSize: '2rem',
            fontWeight: 700,
            color: config.color,
            marginBottom: '0.5rem',
            textTransform: 'uppercase',
            letterSpacing: '1px'
          }}>
            {config.title}
          </h2>
          <p style={{
            fontSize: '1rem',
            color: 'var(--text-secondary)',
            maxWidth: '600px',
            lineHeight: 1.6
          }}>
            {config.description}
          </p>
        </div>

        {/* Action Badge */}
        <div style={{
          padding: '0.75rem 2rem',
          background: config.color,
          color: 'white',
          borderRadius: 'var(--radius-lg)',
          fontSize: '1rem',
          fontWeight: 700,
          textTransform: 'uppercase',
          letterSpacing: '0.5px',
          boxShadow: `0 4px 14px ${config.color}60`
        }}>
          {config.action}
        </div>
      </div>

      {/* Recommendation Section */}
      {recommendation && (
        <div style={{
          padding: '1.5rem',
          background: 'rgba(0, 217, 255, 0.05)',
          border: '1px solid rgba(0, 217, 255, 0.2)',
          borderRadius: 'var(--radius-lg)',
          marginBottom: '2rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
            <Shield size={24} style={{ color: 'var(--accent-cyan)', flexShrink: 0, marginTop: '0.125rem' }} />
            <div style={{ flex: 1 }}>
              <h3 style={{
                fontSize: '1rem',
                fontWeight: 600,
                color: 'var(--accent-cyan)',
                marginBottom: '0.5rem',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                Recommendation
              </h3>
              <p style={{
                fontSize: '1rem',
                color: 'var(--text-primary)',
                lineHeight: 1.6
              }}>
                {recommendation}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Verification Details */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '1rem',
        marginBottom: '2rem'
      }}>
        {/* Verification ID */}
        <div style={{
          padding: '1rem',
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
            Verification ID
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <code style={{
              fontSize: '0.875rem',
              fontFamily: 'JetBrains Mono, monospace',
              color: 'var(--accent-cyan)',
              flex: 1,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap'
            }}>
              {verification_id}
            </code>
            <button
              onClick={handleCopyId}
              style={{
                padding: '0.25rem',
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                color: 'var(--text-muted)',
                display: 'flex',
                alignItems: 'center'
              }}
              title="Copy ID"
            >
              {copied ? <Check size={16} style={{ color: 'var(--color-verified)' }} /> : <Copy size={16} />}
            </button>
          </div>
        </div>

        {/* Final Score */}
        <div style={{
          padding: '1rem',
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
            Final Score
          </div>
          <div style={{
            fontSize: '1.5rem',
            fontWeight: 700,
            color: config.color
          }}>
            {Math.round(final_score)} / 100
          </div>
        </div>

        {/* Confidence */}
        <div style={{
          padding: '1rem',
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
            Confidence Level
          </div>
          <div style={{
            fontSize: '1.5rem',
            fontWeight: 700,
            color: confidence === 'HIGH' ? 'var(--color-verified)' : confidence === 'MEDIUM' ? 'var(--color-suspicious)' : 'var(--color-reject)'
          }}>
            {confidence}
          </div>
        </div>

        {/* Timestamp */}
        <div style={{
          padding: '1rem',
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
            Verified At
          </div>
          <div style={{
            fontSize: '0.875rem',
            color: 'var(--text-primary)',
            fontFamily: 'JetBrains Mono, monospace'
          }}>
            {timestamp ? formatTimestamp(timestamp) : 'N/A'}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div style={{
        display: 'flex',
        gap: '1rem',
        flexWrap: 'wrap'
      }}>
        <button
          onClick={handleDownloadReport}
          className="btn btn-primary"
          style={{ flex: 1, minWidth: '200px' }}
        >
          <Download size={20} />
          Download Report
        </button>

        <button
          onClick={() => window.print()}
          className="btn btn-secondary"
          style={{ flex: 1, minWidth: '200px' }}
        >
          <FileText size={20} />
          Print Report
        </button>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% {
            transform: scale(1);
            opacity: 1;
          }
          50% {
            transform: scale(1.05);
            opacity: 0.9;
          }
        }
      `}</style>
    </div>
  );
};

export default VerdictDisplay;