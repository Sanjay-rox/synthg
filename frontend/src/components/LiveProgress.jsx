/**
 * LiveProgress Component
 * Shows real-time progress as layers are being verified
 */

import React from 'react';
import { FileText, Network, Activity, Link, CheckCircle, Loader, XCircle } from 'lucide-react';

const LiveProgress = ({ isVerifying, layerStatuses }) => {
  if (!isVerifying && !layerStatuses) {
    return null;
  }

  const layers = [
    {
      id: 'layer_1',
      name: 'Document Forensics',
      description: 'Analyzing document authenticity',
      icon: FileText,
      color: '#a855f7'
    },
    {
      id: 'layer_2_3',
      name: 'OSINT + Graph Analysis',
      description: 'Checking digital footprint and relationships',
      icon: Network,
      color: '#00d9ff'
    },
    {
      id: 'layer_4',
      name: 'Behavioral Patterns',
      description: 'Analyzing human behavior patterns',
      icon: Activity,
      color: '#ec4899'
    },
    {
      id: 'layer_5',
      name: 'Blockchain Verification',
      description: 'Checking consortium records',
      icon: Link,
      color: '#10b981'
    }
  ];

  const getLayerStatus = (layerId) => {
    if (!layerStatuses || !layerStatuses[layerId]) {
      return 'pending';
    }
    return layerStatuses[layerId];
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <div className="spinner" style={{ width: '20px', height: '20px' }} />;
      case 'processing':
        return <Loader size={20} className="icon-spin" />;
      case 'success':
        return <CheckCircle size={20} style={{ color: 'var(--color-verified)' }} />;
      case 'error':
        return <XCircle size={20} style={{ color: 'var(--color-reject)' }} />;
      default:
        return <div className="spinner" style={{ width: '20px', height: '20px' }} />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
        return 'var(--color-verified)';
      case 'error':
        return 'var(--color-reject)';
      case 'processing':
        return 'var(--accent-cyan)';
      default:
        return 'var(--text-muted)';
    }
  };

  return (
    <div className="card" style={{ marginBottom: '2rem' }}>
      <div className="card-header">
        <h2 className="card-title">Verification Progress</h2>
        <p className="card-description">
          {isVerifying ? 'Analyzing identity across multiple layers...' : 'Verification complete'}
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {layers.map((layer, index) => {
          const status = getLayerStatus(layer.id);
          const Icon = layer.icon;
          const isActive = status === 'processing' || status === 'success';
          const isComplete = status === 'success';

          return (
            <div
              key={layer.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '1rem',
                padding: '1rem',
                background: isActive ? 'rgba(0, 217, 255, 0.05)' : 'rgba(255, 255, 255, 0.02)',
                border: `1px solid ${isActive ? 'rgba(0, 217, 255, 0.3)' : 'rgba(255, 255, 255, 0.1)'}`,
                borderRadius: 'var(--radius-md)',
                transition: 'all 0.3s ease',
                position: 'relative',
                overflow: 'hidden'
              }}
            >
              {/* Progress bar background */}
              {status === 'processing' && (
                <div
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    height: '100%',
                    width: '100%',
                    background: `linear-gradient(90deg, transparent 0%, ${layer.color}20 50%, transparent 100%)`,
                    animation: 'slideProgress 2s ease-in-out infinite'
                  }}
                />
              )}

              {/* Layer Icon */}
              <div
                style={{
                  width: '48px',
                  height: '48px',
                  borderRadius: 'var(--radius-md)',
                  background: `${layer.color}20`,
                  border: `2px solid ${layer.color}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  position: 'relative',
                  zIndex: 1
                }}
              >
                <Icon size={24} style={{ color: layer.color }} />
              </div>

              {/* Layer Info */}
              <div style={{ flex: 1, position: 'relative', zIndex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                  <h3 style={{ 
                    fontSize: '1rem', 
                    fontWeight: 600,
                    color: isActive ? 'var(--text-primary)' : 'var(--text-muted)'
                  }}>
                    {layer.name}
                  </h3>
                  
                  {/* Layer number badge */}
                  <span style={{
                    fontSize: '0.75rem',
                    padding: '0.125rem 0.5rem',
                    background: 'rgba(255, 255, 255, 0.1)',
                    borderRadius: 'var(--radius-sm)',
                    color: 'var(--text-muted)'
                  }}>
                    Layer {index + 1}
                  </span>
                </div>

                <p style={{ 
                  fontSize: '0.875rem', 
                  color: getStatusColor(status),
                  marginBottom: 0
                }}>
                  {status === 'pending' && 'Waiting...'}
                  {status === 'processing' && layer.description}
                  {status === 'success' && 'Analysis complete'}
                  {status === 'error' && 'Analysis failed'}
                </p>
              </div>

              {/* Status Icon */}
              <div style={{ position: 'relative', zIndex: 1 }}>
                {getStatusIcon(status)}
              </div>
            </div>
          );
        })}
      </div>

      {/* Overall Progress */}
      <div style={{ marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
          <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            Overall Progress
          </span>
          <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--accent-cyan)' }}>
            {layerStatuses ? 
              `${Object.values(layerStatuses).filter(s => s === 'success').length} / ${Object.keys(layerStatuses).length}` 
              : '0 / 4'
            }
          </span>
        </div>
        
        {/* Progress Bar */}
        <div style={{
          width: '100%',
          height: '8px',
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '4px',
          overflow: 'hidden'
        }}>
          <div style={{
            height: '100%',
            background: 'linear-gradient(90deg, var(--accent-cyan), var(--accent-purple))',
            width: layerStatuses ? 
              `${(Object.values(layerStatuses).filter(s => s === 'success').length / Object.keys(layerStatuses).length) * 100}%`
              : '0%',
            transition: 'width 0.3s ease',
            boxShadow: '0 0 10px rgba(0, 217, 255, 0.5)'
          }} />
        </div>
      </div>

      <style>{`
        @keyframes slideProgress {
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }

        .icon-spin {
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </div>
  );
};

export default LiveProgress;