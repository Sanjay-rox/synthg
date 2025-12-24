import React, { useState } from 'react';

function IdentityForm({ onSubmit, loading }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    username: '',
    company: '',
    location: '',
    dob: '',
    aadhaar: '',
    pan: '',
    context: 'professional',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const cleanData = {};
    Object.entries(formData).forEach(([key, value]) => {
      if (value && value.trim()) {
        cleanData[key] = value.trim();
      }
    });
    
    cleanData.context = formData.context;
    onSubmit(cleanData);
  };

  const hasRequiredFields = formData.name || formData.email || formData.phone || formData.aadhaar;

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-icon">👤</div>
        <h3 className="card-title">Identity Information</h3>
      </div>
      
      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          {/* Core Identifiers */}
          <div className="form-group">
            <label htmlFor="name">Full Name</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="e.g. John Doe"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="e.g. john@company.com"
            />
          </div>

          <div className="form-group">
            <label htmlFor="phone">Phone Number</label>
            <input
              type="tel"
              id="phone"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              placeholder="e.g. +91 98765 43210"
            />
          </div>

          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="e.g. johndoe123"
            />
          </div>

          <div className="form-group">
            <label htmlFor="company">Company / Organization</label>
            <input
              type="text"
              id="company"
              name="company"
              value={formData.company}
              onChange={handleChange}
              placeholder="e.g. Acme Corporation"
            />
          </div>

          <div className="form-group">
            <label htmlFor="location">Location</label>
            <input
              type="text"
              id="location"
              name="location"
              value={formData.location}
              onChange={handleChange}
              placeholder="e.g. Bangalore, Karnataka 560001"
            />
          </div>

          {/* Indian Documents Section */}
          <div className="form-group full-width" style={{ marginTop: '8px' }}>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '8px',
              marginBottom: '4px',
              paddingBottom: '12px',
              borderBottom: '1px solid var(--border-subtle)'
            }}>
              <span style={{ fontSize: '0.875rem' }}>🇮🇳</span>
              <span style={{ 
                fontSize: '0.6875rem', 
                color: 'var(--text-muted)',
                textTransform: 'uppercase',
                letterSpacing: '0.04em',
                fontWeight: '500'
              }}>
                Indian Documents (Optional)
              </span>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="dob">Date of Birth</label>
            <input
              type="date"
              id="dob"
              name="dob"
              value={formData.dob}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label htmlFor="aadhaar">Aadhaar Number</label>
            <input
              type="text"
              id="aadhaar"
              name="aadhaar"
              value={formData.aadhaar}
              onChange={handleChange}
              placeholder="e.g. 1234 5678 9012"
              maxLength="14"
            />
          </div>

          <div className="form-group">
            <label htmlFor="pan">PAN Number</label>
            <input
              type="text"
              id="pan"
              name="pan"
              value={formData.pan}
              onChange={handleChange}
              placeholder="e.g. ABCDE1234F"
              maxLength="10"
              style={{ textTransform: 'uppercase' }}
            />
          </div>

          <div className="form-group">
            <label htmlFor="context">Verification Context</label>
            <select
              id="context"
              name="context"
              value={formData.context}
              onChange={handleChange}
            >
              <option value="student">Student — Relaxed thresholds</option>
              <option value="professional">Professional — Standard</option>
              <option value="executive">Executive — Strict verification</option>
            </select>
          </div>

          {/* Submit */}
          <div className="form-group full-width" style={{ marginTop: '8px' }}>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !hasRequiredFields}
              style={{ width: '100%', padding: '14px' }}
            >
              {loading ? (
                <>
                  <span className="loading-spinner" style={{ width: '18px', height: '18px', borderWidth: '2px' }}></span>
                  Analyzing...
                </>
              ) : (
                <>Verify Identity</>
              )}
            </button>
            
            {!hasRequiredFields && (
              <p style={{ 
                fontSize: '0.6875rem', 
                color: 'var(--text-dim)', 
                marginTop: '12px',
                textAlign: 'center',
                letterSpacing: '0.01em'
              }}>
                Enter at least one identifier — name, email, phone, or aadhaar
              </p>
            )}
          </div>
        </div>
      </form>
    </div>
  );
}

export default IdentityForm;
