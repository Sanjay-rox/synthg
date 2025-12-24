import React from 'react';

function RedFlagsPanel({ result }) {
  const { red_flags, trust_indicators } = result;

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical': return '🚨';
      case 'high': return '⚠️';
      case 'medium': return '⚡';
      case 'low': return 'ℹ️';
      default: return '❓';
    }
  };

  return (
    <>
      {/* Red Flags */}
      <div className="card">
        <div className="card-header">
          <div className="card-icon">🚩</div>
          <h3 className="card-title">Red Flags ({red_flags.length})</h3>
        </div>
        
        {red_flags.length === 0 ? (
          <div className="empty-state success">
            <div className="empty-state-icon">✨</div>
            <p className="empty-state-text">No red flags detected</p>
          </div>
        ) : (
          <div className="red-flags">
            {red_flags.map((flag, i) => (
              <div key={i} className={`red-flag ${flag.severity}`}>
                <span className="red-flag-icon">{getSeverityIcon(flag.severity)}</span>
                <div className="red-flag-content">
                  <div className="red-flag-code">{flag.code.replace(/_/g, ' ')}</div>
                  <div className="red-flag-text">{flag.description}</div>
                  <div className="red-flag-penalty">-{flag.penalty.toFixed(1)} points</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Trust Indicators */}
      <div className="card">
        <div className="card-header">
          <div className="card-icon">✓</div>
          <h3 className="card-title">Trust Signals ({trust_indicators.length})</h3>
        </div>
        
        {trust_indicators.length === 0 ? (
          <div className="empty-state">
            <p className="empty-state-text">No trust signals detected</p>
          </div>
        ) : (
          <div className="trust-indicators">
            {trust_indicators.map((indicator, i) => (
              <div key={i} className="trust-indicator">
                <span className="trust-indicator-icon">
                  {indicator.strength === 'strong' ? '●●' : indicator.strength === 'medium' ? '●○' : '○○'}
                </span>
                <span className="trust-indicator-text">{indicator.signal}</span>
                {indicator.source && (
                  <span className="trust-indicator-source">{indicator.source}</span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Enrichment Data */}
      {result.enrichment && (
        <div className="card">
          <div className="card-header">
            <div className="card-icon">📡</div>
            <h3 className="card-title">API Enrichment</h3>
          </div>
          
          <div className="enrichment-grid">
            {result.enrichment.email && (
              <div className="enrichment-item">
                <div className="enrichment-header">
                  <span className="enrichment-icon">✉️</span>
                  <span className="enrichment-title">Email</span>
                </div>
                <div className="enrichment-data">
                  <div className="enrichment-row">
                    <span className="enrichment-key">Domain</span>
                    <span className="enrichment-value">{result.enrichment.email.email?.split('@')[1]}</span>
                  </div>
                  <div className="enrichment-row">
                    <span className="enrichment-key">Breaches</span>
                    <span className="enrichment-value">{result.enrichment.email.breach_count || 0}</span>
                  </div>
                  <div className="enrichment-row">
                    <span className="enrichment-key">Disposable</span>
                    <span className="enrichment-value">{result.enrichment.email.is_disposable ? '⚠️ Yes' : '✓ No'}</span>
                  </div>
                  <div className="enrichment-row">
                    <span className="enrichment-key">Type</span>
                    <span className="enrichment-value">
                      {result.enrichment.email.is_educational ? 'Educational' : 
                       result.enrichment.email.is_corporate ? 'Corporate' : 'Personal'}
                    </span>
                  </div>
                </div>
              </div>
            )}
            
            {result.enrichment.phone && (
              <div className="enrichment-item">
                <div className="enrichment-header">
                  <span className="enrichment-icon">📱</span>
                  <span className="enrichment-title">Phone</span>
                </div>
                <div className="enrichment-data">
                  <div className="enrichment-row">
                    <span className="enrichment-key">Carrier</span>
                    <span className="enrichment-value">{result.enrichment.phone.carrier || 'Unknown'}</span>
                  </div>
                  <div className="enrichment-row">
                    <span className="enrichment-key">Valid</span>
                    <span className="enrichment-value">
                      {result.enrichment.phone.valid === true ? '✓ Yes' : 
                       result.enrichment.phone.valid === false ? '✗ No' : '—'}
                    </span>
                  </div>
                  <div className="enrichment-row">
                    <span className="enrichment-key">Type</span>
                    <span className="enrichment-value">{result.enrichment.phone.line_type || 'Mobile'}</span>
                  </div>
                  <div className="enrichment-row">
                    <span className="enrichment-key">Est. Age</span>
                    <span className="enrichment-value">~{result.enrichment.phone.registration_age_years || 0}y</span>
                  </div>
                </div>
              </div>
            )}
            
            {result.enrichment.aadhaar && (
              <div className="enrichment-item">
                <div className="enrichment-header">
                  <span className="enrichment-icon">🪪</span>
                  <span className="enrichment-title">Aadhaar</span>
                </div>
                <div className="enrichment-data">
                  <div className="enrichment-row">
                    <span className="enrichment-key">Active</span>
                    <span className="enrichment-value">{result.enrichment.aadhaar.years_active || 0} years</span>
                  </div>
                  <div className="enrichment-row">
                    <span className="enrichment-key">Enrolled</span>
                    <span className="enrichment-value">{result.enrichment.aadhaar.enrollment_year || '—'}</span>
                  </div>
                </div>
              </div>
            )}
            
            {result.enrichment.pan && (
              <div className="enrichment-item">
                <div className="enrichment-header">
                  <span className="enrichment-icon">💳</span>
                  <span className="enrichment-title">PAN</span>
                </div>
                <div className="enrichment-data">
                  <div className="enrichment-row">
                    <span className="enrichment-key">Active</span>
                    <span className="enrichment-value">{result.enrichment.pan.years_active || 0} years</span>
                  </div>
                  <div className="enrichment-row">
                    <span className="enrichment-key">Issued</span>
                    <span className="enrichment-value">{result.enrichment.pan.issue_year || '—'}</span>
                  </div>
                </div>
              </div>
            )}
            
            {result.enrichment.address && result.enrichment.address.city && (
              <div className="enrichment-item">
                <div className="enrichment-header">
                  <span className="enrichment-icon">📍</span>
                  <span className="enrichment-title">Address</span>
                </div>
                <div className="enrichment-data">
                  <div className="enrichment-row">
                    <span className="enrichment-key">City</span>
                    <span className="enrichment-value">{result.enrichment.address.city || '—'}</span>
                  </div>
                  <div className="enrichment-row">
                    <span className="enrichment-key">State</span>
                    <span className="enrichment-value">{result.enrichment.address.state || '—'}</span>
                  </div>
                  <div className="enrichment-row">
                    <span className="enrichment-key">PIN Valid</span>
                    <span className="enrichment-value">
                      {result.enrichment.address.valid === true ? '✓' : 
                       result.enrichment.address.valid === false ? '✗' : '—'}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Social Profiles */}
      {result.social_profiles && result.social_profiles.length > 0 && (
        <div className="card">
          <div className="card-header">
            <div className="card-icon">🌐</div>
            <h3 className="card-title">Social Profiles</h3>
          </div>
          
          <div className="social-profiles">
            {result.social_profiles.slice(0, 5).map((profile, i) => (
              <a 
                key={i}
                href={profile.url}
                target="_blank"
                rel="noopener noreferrer"
                className="social-profile-link"
              >
                <span className="social-profile-icon">{getPlatformIcon(profile.platform)}</span>
                <span className="social-profile-platform">{profile.platform}</span>
                <span className="social-profile-title">{profile.title}</span>
                <span className="social-profile-arrow">→</span>
              </a>
            ))}
          </div>
        </div>
      )}
    </>
  );
}

function getPlatformIcon(platform) {
  const icons = {
    'linkedin': '💼',
    'github': '💻',
    'twitter': '🐦',
    'facebook': '📘',
    'instagram': '📷',
    'stackoverflow': '📚',
    'medium': '📝',
  };
  
  const lower = platform.toLowerCase();
  for (const [key, icon] of Object.entries(icons)) {
    if (lower.includes(key)) return icon;
  }
  return '🌐';
}

export default RedFlagsPanel;
