/**
 * Main App Component - FIXED VERSION
 * Coordinates all components and manages verification workflow
 * 
 * FIX: Behavioral data is now passed directly instead of relying on state
 */

import React, { useState, useEffect } from 'react';
import { Shield, Activity } from 'lucide-react';
import apiService from './services/api';

// Import components
import IdentityForm from './components/IdentityForm';
import DocumentUpload from './components/DocumentUpload';
import LiveProgress from './components/LiveProgress';
import ScoreDisplay from './components/ScoreDisplay';
import LayerBreakdown from './components/LayerBreakdown';
import VerdictDisplay from './components/VerdictDisplay';
import RedFlagsPanel from './components/RedFlagsPanel';

function App() {
  // State management
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState(null);
  const [layerStatuses, setLayerStatuses] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [error, setError] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);

  // Check orchestrator health on mount
  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const health = await apiService.checkHealth();
      setHealthStatus(health);
    } catch (err) {
      console.error('Health check failed:', err);
      setHealthStatus({ status: 'unhealthy' });
    }
  };

  // FIXED: Accept behavioral data directly as parameter
  const handleVerification = async (identityData, behavioralData) => {
    setIsVerifying(true);
    setError(null);
    setVerificationResult(null);
    
    console.log('🎯 Starting verification with behavioral data:', {
      hasBehavioralData: !!behavioralData,
      sessionId: behavioralData?.session_id,
      formTime: behavioralData?.form_completion_time,
      mouseMovements: behavioralData?.mouse_movements?.length || 0,
      keystrokes: behavioralData?.keystroke_data?.length || 0
    });
    
    // Initialize layer statuses
    setLayerStatuses({
      layer_1: documents.length > 0 ? 'processing' : 'disabled',
      layer_2_3: 'processing',
      layer_4: behavioralData ? 'processing' : 'disabled',
      layer_5: 'processing'
    });

    try {
      // Format request with behavioral data
      const request = await apiService.formatVerificationRequest(
        identityData,
        documents,
        behavioralData // Now using the passed parameter directly
      );

      console.log('📤 Sending verification request:', {
        hasIdentityData: !!request.identity_data,
        documentCount: request.documents?.length || 0,
        hasBehavioralData: !!request.behavioral_data,
        behavioralDataDetails: request.behavioral_data ? {
          sessionId: request.behavioral_data.session_id,
          formTime: request.behavioral_data.form_completion_time,
          mouseCount: request.behavioral_data.mouse_movements?.length || 0,
          keystrokeCount: request.behavioral_data.keystroke_data?.length || 0
        } : null
      });

      // Simulate progressive updates
      const simulateProgress = () => {
        setTimeout(() => {
          setLayerStatuses(prev => ({
            ...prev,
            layer_1: documents.length > 0 ? 'success' : 'disabled'
          }));
        }, 1000);

        setTimeout(() => {
          setLayerStatuses(prev => ({
            ...prev,
            layer_4: behavioralData ? 'success' : 'disabled'
          }));
        }, 2000);

        setTimeout(() => {
          setLayerStatuses(prev => ({
            ...prev,
            layer_2_3: 'success'
          }));
        }, 3000);

        setTimeout(() => {
          setLayerStatuses(prev => ({
            ...prev,
            layer_5: 'success'
          }));
        }, 4000);
      };

      simulateProgress();

      // Make API call
      const result = await apiService.verifyIdentity(request);
      
      console.log('✅ Verification response received:', {
        verificationId: result.verification_id,
        finalScore: result.final_score,
        verdict: result.verdict,
        layersExecuted: result.layers_executed,
        hasLayer4: !!result.layer_results?.layer_4,
        layer4Score: result.layer_results?.layer_4?.score
      });
      
      // Update final statuses based on actual result
      const finalStatuses = {};
      if (result.layer_results) {
        Object.keys(result.layer_results).forEach(layerId => {
          const layerResult = result.layer_results[layerId];
          finalStatuses[layerId] = layerResult.status === 'SUCCESS' ? 'success' : 'error';
        });
      }
      setLayerStatuses(finalStatuses);

      // Store result
      setVerificationResult(result);
      
      // Scroll to results
      setTimeout(() => {
        document.getElementById('results-section')?.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        });
      }, 300);

    } catch (err) {
      console.error('❌ Verification failed:', err);
      setError(err.message || 'Verification failed. Please try again.');
      
      // Update statuses to show errors
      setLayerStatuses(prev => {
        const updated = {};
        Object.keys(prev).forEach(key => {
          updated[key] = prev[key] === 'processing' ? 'error' : prev[key];
        });
        return updated;
      });
    } finally {
      setIsVerifying(false);
    }
  };

  const handleDocumentsChange = (newDocuments) => {
    setDocuments(newDocuments);
  };

  const handleNewVerification = () => {
    setVerificationResult(null);
    setLayerStatuses(null);
    setError(null);
    setDocuments([]);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const isSystemHealthy = healthStatus?.status === 'healthy';

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <div className="logo-icon">
              <Shield size={24} style={{ color: 'white' }} />
            </div>
            <div className="logo-text">
              <h1>SynthGuard</h1>
              <p>AI-Powered Identity Verification</p>
            </div>
          </div>

          {/* Health Status */}
          {healthStatus && (
            <div className="health-status">
              <div className="health-dot" style={{
                background: isSystemHealthy ? 'var(--color-verified)' : 'var(--color-reject)'
              }} />
              <span>System {isSystemHealthy ? 'Healthy' : 'Degraded'}</span>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {/* System Health Warning */}
        {healthStatus && !isSystemHealthy && (
          <div className="alert alert-error" style={{ marginBottom: '2rem' }}>
            <Activity size={20} />
            <div>
              <p style={{ fontWeight: 600, marginBottom: '0.25rem' }}>
                System Health Issue
              </p>
              <p style={{ fontSize: '0.875rem', opacity: 0.9 }}>
                Some verification layers may be unavailable. Results may be incomplete.
              </p>
            </div>
          </div>
        )}

        {/* Input Section */}
        {!verificationResult && (
          <>
            <IdentityForm 
              onSubmit={handleVerification}  // FIXED: Now passes behavioral data as parameter
              isLoading={isVerifying}
            />

            <div style={{ marginTop: '2rem' }}>
              <DocumentUpload 
                onDocumentsChange={handleDocumentsChange}
                isLoading={isVerifying}
              />
            </div>
          </>
        )}

        {/* Progress Section */}
        {(isVerifying || verificationResult) && (
          <LiveProgress 
            isVerifying={isVerifying}
            layerStatuses={layerStatuses}
          />
        )}

        {/* Error Display */}
        {error && (
          <div className="alert alert-error" style={{ marginTop: '2rem' }}>
            <Activity size={20} />
            <div>
              <p style={{ fontWeight: 600, marginBottom: '0.25rem' }}>
                Verification Failed
              </p>
              <p style={{ fontSize: '0.875rem', opacity: 0.9 }}>
                {error}
              </p>
            </div>
          </div>
        )}

        {/* Results Section */}
        {verificationResult && (
          <div id="results-section" style={{ marginTop: '2rem' }}>
            {/* Main Verdict */}
            <VerdictDisplay verificationData={verificationResult} />

            {/* Score Display */}
            <div style={{ marginTop: '2rem' }}>
              <ScoreDisplay 
                score={verificationResult.final_score}
                verdict={verificationResult.verdict}
                confidence={verificationResult.confidence}
                recommendation={verificationResult.recommendation}
              />
            </div>

            {/* Layer Breakdown */}
            {verificationResult.score_breakdown?.layer_contributions && (
              <div style={{ marginTop: '2rem' }}>
                <LayerBreakdown 
                  layerContributions={verificationResult.score_breakdown.layer_contributions}
                  processingTime={verificationResult.total_processing_time_ms}
                />
              </div>
            )}

            {/* Red Flags & Trust Indicators */}
            {(verificationResult.score_breakdown?.red_flags || 
              verificationResult.score_breakdown?.trust_indicators) && (
              <div style={{ marginTop: '2rem' }}>
                <RedFlagsPanel 
                  redFlags={verificationResult.score_breakdown.red_flags}
                  trustIndicators={verificationResult.score_breakdown.trust_indicators}
                />
              </div>
            )}

            {/* Graph Visualization (if available from Layer 2&3) */}
            {verificationResult.visualization_data?.graph_nodes?.length > 0 && (
              <div className="card" style={{ marginTop: '2rem' }}>
                <div className="card-header">
                  <h2 className="card-title">Identity Graph</h2>
                  <p className="card-description">
                    Relationship network analysis from Layer 2&3
                  </p>
                </div>
                <div className="alert alert-info" style={{ marginBottom: 0 }}>
                  <Shield size={20} />
                  <p style={{ fontSize: '0.875rem' }}>
                    Graph visualization shows {verificationResult.visualization_data.graph_nodes.length} nodes 
                    and {verificationResult.visualization_data.graph_edges?.length || 0} connections. 
                    Dense networks indicate authentic identities.
                  </p>
                </div>
              </div>
            )}

            {/* New Verification Button */}
            <div style={{ 
              marginTop: '2rem', 
              padding: '2rem',
              textAlign: 'center',
              background: 'rgba(255, 255, 255, 0.02)',
              borderRadius: 'var(--radius-xl)',
              border: '1px solid rgba(255, 255, 255, 0.1)'
            }}>
              <p style={{ 
                fontSize: '1rem', 
                color: 'var(--text-secondary)', 
                marginBottom: '1rem' 
              }}>
                Need to verify another identity?
              </p>
              <button
                onClick={handleNewVerification}
                className="btn btn-primary"
              >
                <Shield size={20} />
                New Verification
              </button>
            </div>
          </div>
        )}

        {/* Footer Info */}
        {!verificationResult && !isVerifying && (
          <div style={{
            marginTop: '3rem',
            padding: '2rem',
            background: 'rgba(0, 217, 255, 0.05)',
            border: '1px solid rgba(0, 217, 255, 0.2)',
            borderRadius: 'var(--radius-xl)',
            textAlign: 'center'
          }}>
            <Shield size={48} style={{ color: 'var(--accent-cyan)', marginBottom: '1rem' }} />
            <h3 style={{ 
              fontSize: '1.25rem', 
              fontWeight: 600, 
              color: 'var(--text-primary)',
              marginBottom: '0.5rem'
            }}>
              Multi-Layer Verification System
            </h3>
            <p style={{ 
              fontSize: '0.875rem', 
              color: 'var(--text-muted)',
              maxWidth: '600px',
              margin: '0 auto',
              lineHeight: 1.6
            }}>
              SynthGuard uses 5 advanced layers including document forensics, OSINT intelligence, 
              graph analysis, behavioral patterns, and blockchain verification to detect synthetic identities 
              with up to 90% accuracy.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;