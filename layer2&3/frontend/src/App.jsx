import React, { useState, useEffect } from 'react';
import IdentityForm from './components/IdentityForm';
import ScoreDisplay from './components/ScoreDisplay';
import GraphVisualizer from './components/GraphVisualizer';
import RedFlagsPanel from './components/RedFlagsPanel';
import { analyzeIdentity, checkHealth } from './api';

function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState(null);

  useEffect(() => {
    checkHealth()
      .then(status => setApiStatus(status))
      .catch(() => setApiStatus({ status: 'offline' }));
  }, []);

  const handleSubmit = async (formData) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await analyzeIdentity(formData);
      setResult(response);
    } catch (err) {
      setError(err.message || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="container">
          <div className="header-content">
            <div className="header-left">
              <div className="logo-container">🔐</div>
              <div className="header-title">
                <h1>Identity Verification</h1>
                <span>OSINT • Graph Analysis • AI</span>
              </div>
            </div>
            <div className="header-badges">
              {apiStatus?.api_status?.claude && (
                <span className="badge badge-success">Claude AI</span>
              )}
              {apiStatus?.api_status?.tavily && (
                <span className="badge badge-success">OSINT Active</span>
              )}
              {apiStatus?.api_status?.hibp && (
                <span className="badge badge-info">Breach Check</span>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="main">
        <div className="container">
          <IdentityForm onSubmit={handleSubmit} loading={loading} />

          {loading && (
            <div className="card loading-container fade-in" style={{ marginTop: '32px' }}>
              <div className="loading-spinner"></div>
              <p className="loading-text">Analyzing identity across multiple sources...</p>
              <p className="loading-subtext">OSINT • Graph • AI Verdict</p>
            </div>
          )}

          {error && (
            <div className="card fade-in" style={{ marginTop: '32px', borderColor: 'var(--accent-danger)' }}>
              <div className="card-header">
                <div className="card-icon">⚠️</div>
                <h3 className="card-title" style={{ color: 'var(--accent-danger)' }}>Analysis Error</h3>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>{error}</p>
            </div>
          )}

          {result && !loading && (
            <div className="results-section fade-in">
              {/* Score Section */}
              <ScoreDisplay result={result} />

              {/* Two Column Grid */}
              <div className="results-grid">
                {/* Graph */}
                <div className="card">
                  <div className="card-header">
                    <div className="card-icon">🕸️</div>
                    <h3 className="card-title">Identity Graph</h3>
                  </div>
                  <GraphVisualizer result={result} />
                </div>

                {/* Red Flags & Trust */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                  <RedFlagsPanel result={result} />
                </div>
              </div>

              {/* OSINT Stats */}
              {result.osint_analysis && (
                <div className="card" style={{ marginTop: '24px' }}>
                  <div className="card-header">
                    <div className="card-icon">🔎</div>
                    <h3 className="card-title">OSINT Intelligence</h3>
                  </div>
                  
                  <div className="stats-grid">
                    <div className="stat-item">
                      <div className="stat-value primary">{result.osint_analysis.total_hits}</div>
                      <div className="stat-label">Search Hits</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-value secondary">{result.osint_analysis.unique_domains}</div>
                      <div className="stat-label">Unique Domains</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-value primary">{result.osint_analysis.high_trust_domains?.length || 0}</div>
                      <div className="stat-label">High-Trust Sources</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-value purple">{result.queries_executed || 0}</div>
                      <div className="stat-label">Dork Queries</div>
                    </div>
                  </div>
                  
                  {result.domains_seen?.length > 0 && (
                    <div style={{ marginTop: '20px' }}>
                      <div className="section-title">Domains Discovered</div>
                      <div className="domain-tags">
                        {result.domains_seen.slice(0, 15).map((domain, i) => (
                          <span key={i} className="domain-tag">{domain}</span>
                        ))}
                        {result.domains_seen.length > 15 && (
                          <span className="domain-tag domain-tag-more">
                            +{result.domains_seen.length - 15} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Analysis Metadata */}
              <div className="card" style={{ marginTop: '24px' }}>
                <div className="card-header">
                  <div className="card-icon">📊</div>
                  <h3 className="card-title">Analysis Metadata</h3>
                </div>
                <div className="metadata-grid">
                  <div className="metadata-item">
                    <span className="metadata-label">Timestamp</span>
                    <span className="metadata-value">{new Date(result.analysis_timestamp).toLocaleString()}</span>
                  </div>
                  <div className="metadata-item">
                    <span className="metadata-label">Duration</span>
                    <span className="metadata-value">{(result.analysis_duration_ms / 1000).toFixed(1)}s</span>
                  </div>
                  <div className="metadata-item">
                    <span className="metadata-label">Context</span>
                    <span className="metadata-value" style={{ textTransform: 'capitalize' }}>{result.context}</span>
                  </div>
                  <div className="metadata-item">
                    <span className="metadata-label">Connections</span>
                    <span className="metadata-value">{result.total_connections}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      <footer className="footer">
        <p className="footer-text">
          Identity Verification System • OSINT + Graph + AI • <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">API Docs</a>
        </p>
      </footer>
    </div>
  );
}

export default App;
