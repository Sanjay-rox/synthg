/**
 * IdentityForm Component - FIXED VERSION
 * Main form for collecting identity data
 * 
 * FIX: Behavioral data is now passed directly to onSubmit instead of separate callback
 */

import React, { useState, useEffect } from 'react';
import { User, Mail, Phone, Calendar, CreditCard, MapPin, Building, UserCircle } from 'lucide-react';
import useBehavioralTracking from '../hooks/useBehavioralTracking';

const IdentityForm = ({ onSubmit, isLoading }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    dob: '',
    aadhaar: '',
    pan: '',
    address: '',
    location: '',
    username: '',
    company: '',
    context: 'professional'
  });

  const [errors, setErrors] = useState({});
  
  // Initialize behavioral tracking
  const {
    startTracking,
    stopTracking,
    getBehavioralData,
    trackFieldFocus,
    isTracking,
    getTrackingStats
  } = useBehavioralTracking();

  // Start tracking when form mounts
  useEffect(() => {
    startTracking();
    console.log('🎯 Behavioral tracking started for identity form');
    
    return () => {
      // Cleanup on unmount
      stopTracking();
    };
  }, [startTracking, stopTracking]);

  // Debug: Log tracking stats every 5 seconds
  useEffect(() => {
    if (!isTracking) return;

    const interval = setInterval(() => {
      const stats = getTrackingStats();
      console.log('📊 Tracking stats:', stats);
    }, 5000);

    return () => clearInterval(interval);
  }, [isTracking, getTrackingStats]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleFocus = (e) => {
    const { name } = e.target;
    // Track field navigation
    trackFieldFocus(name);
    console.log(`🎯 Field focused: ${name}`);
  };

  const validateForm = () => {
    const newErrors = {};

    // Required fields
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    if (!formData.phone.trim()) {
      newErrors.phone = 'Phone number is required';
    } else if (!formData.phone.startsWith('+')) {
      newErrors.phone = 'Phone must include country code (e.g., +91)';
    }

    // Optional but validated if provided
    if (formData.aadhaar && formData.aadhaar.replace(/\s/g, '').length !== 12) {
      newErrors.aadhaar = 'Aadhaar must be 12 digits';
    }

    if (formData.pan && formData.pan.length !== 10) {
      newErrors.pan = 'PAN must be 10 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      // Get behavioral data before submission
      const behavioralData = getBehavioralData();
      
      console.log('✅ Form validated - Collecting behavioral data...');
      console.log('📊 Behavioral data collected:', {
        session_id: behavioralData.session_id,
        form_completion_time: behavioralData.form_completion_time,
        mouse_movements: behavioralData.mouse_movements.length,
        keystrokes: behavioralData.keystroke_data.length,
        navigations: behavioralData.navigation_patterns.length,
        sample_mouse: behavioralData.mouse_movements.slice(0, 3),
        sample_keystrokes: behavioralData.keystroke_data.slice(0, 3),
        sample_navigation: behavioralData.navigation_patterns.slice(0, 3)
      });
      
      // FIXED: Pass behavioral data directly to onSubmit
      onSubmit(formData, behavioralData);
    } else {
      console.warn('⚠️ Form validation failed:', errors);
    }
  };

  const handleReset = () => {
    setFormData({
      name: '',
      email: '',
      phone: '',
      dob: '',
      aadhaar: '',
      pan: '',
      address: '',
      location: '',
      username: '',
      company: '',
      context: 'professional'
    });
    setErrors({});
  };

  // Get current tracking stats for display
  const trackingStats = getTrackingStats();

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Identity Information</h2>
        <p className="card-description">
          Enter the identity details to verify. Required fields are marked with *
        </p>
        
        {/* Debug: Show tracking status */}
        {isTracking && (
          <div style={{ 
            marginTop: '1rem',
            padding: '0.75rem 1rem',
            background: 'rgba(0, 217, 255, 0.05)',
            border: '1px solid rgba(0, 217, 255, 0.2)',
            borderRadius: 'var(--radius-md)',
            fontSize: '0.75rem',
            color: 'var(--accent-cyan)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span>🎯 Behavioral tracking active</span>
            <span style={{ fontFamily: 'JetBrains Mono, monospace' }}>
              {trackingStats.elapsedTime}s | 
              {trackingStats.mouseMovementCount} moves | 
              {trackingStats.keystrokeCount} keys
            </span>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit}>
        {/* Basic Information */}
        <div className="form-section">
          <h3 style={{ fontSize: '1rem', marginBottom: '1rem', color: 'var(--accent-cyan)' }}>
            Basic Information
          </h3>
          
          <div className="form-row">
            <div className="form-group">
              <label className="form-label form-label-required" htmlFor="name">
                <User size={16} style={{ display: 'inline', marginRight: '0.25rem' }} />
                Full Name
              </label>
              <input
                type="text"
                id="name"
                name="name"
                className="form-input"
                placeholder="John Doe"
                value={formData.name}
                onChange={handleChange}
                onFocus={handleFocus}
                disabled={isLoading}
              />
              {errors.name && <span style={{ color: 'var(--color-reject)', fontSize: '0.875rem' }}>{errors.name}</span>}
            </div>

            <div className="form-group">
              <label className="form-label form-label-required" htmlFor="email">
                <Mail size={16} style={{ display: 'inline', marginRight: '0.25rem' }} />
                Email Address
              </label>
              <input
                type="email"
                id="email"
                name="email"
                className="form-input"
                placeholder="john.doe@example.com"
                value={formData.email}
                onChange={handleChange}
                onFocus={handleFocus}
                disabled={isLoading}
              />
              {errors.email && <span style={{ color: 'var(--color-reject)', fontSize: '0.875rem' }}>{errors.email}</span>}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label form-label-required" htmlFor="phone">
                <Phone size={16} style={{ display: 'inline', marginRight: '0.25rem' }} />
                Phone Number
              </label>
              <input
                type="tel"
                id="phone"
                name="phone"
                className="form-input"
                placeholder="+91 98765 43210"
                value={formData.phone}
                onChange={handleChange}
                onFocus={handleFocus}
                disabled={isLoading}
              />
              {errors.phone && <span style={{ color: 'var(--color-reject)', fontSize: '0.875rem' }}>{errors.phone}</span>}
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="dob">
                <Calendar size={16} style={{ display: 'inline', marginRight: '0.25rem' }} />
                Date of Birth
              </label>
              <input
                type="date"
                id="dob"
                name="dob"
                className="form-input"
                value={formData.dob}
                onChange={handleChange}
                onFocus={handleFocus}
                disabled={isLoading}
              />
            </div>
          </div>
        </div>

        {/* Indian Documents */}
        <div className="form-section" style={{ marginTop: '2rem' }}>
          <h3 style={{ fontSize: '1rem', marginBottom: '1rem', color: 'var(--accent-cyan)' }}>
            Indian Identity Documents
          </h3>
          
          <div className="form-row">
            <div className="form-group">
              <label className="form-label" htmlFor="aadhaar">
                <CreditCard size={16} style={{ display: 'inline', marginRight: '0.25rem' }} />
                Aadhaar Number
              </label>
              <input
                type="text"
                id="aadhaar"
                name="aadhaar"
                className="form-input"
                placeholder="1234 5678 9012"
                value={formData.aadhaar}
                onChange={handleChange}
                onFocus={handleFocus}
                disabled={isLoading}
                maxLength="14"
              />
              {errors.aadhaar && <span style={{ color: 'var(--color-reject)', fontSize: '0.875rem' }}>{errors.aadhaar}</span>}
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="pan">
                <CreditCard size={16} style={{ display: 'inline', marginRight: '0.25rem' }} />
                PAN Number
              </label>
              <input
                type="text"
                id="pan"
                name="pan"
                className="form-input"
                placeholder="ABCDE1234F"
                value={formData.pan}
                onChange={handleChange}
                onFocus={handleFocus}
                disabled={isLoading}
                maxLength="10"
                style={{ textTransform: 'uppercase' }}
              />
              {errors.pan && <span style={{ color: 'var(--color-reject)', fontSize: '0.875rem' }}>{errors.pan}</span>}
            </div>
          </div>
        </div>

        {/* Address & Location */}
        <div className="form-section" style={{ marginTop: '2rem' }}>
          <h3 style={{ fontSize: '1rem', marginBottom: '1rem', color: 'var(--accent-cyan)' }}>
            Address & Location
          </h3>
          
          <div className="form-group">
            <label className="form-label" htmlFor="address">
              <MapPin size={16} style={{ display: 'inline', marginRight: '0.25rem' }} />
              Full Address
            </label>
            <input
              type="text"
              id="address"
              name="address"
              className="form-input"
              placeholder="123 MG Road, Koramangala"
              value={formData.address}
              onChange={handleChange}
              onFocus={handleFocus}
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="location">
              <MapPin size={16} style={{ display: 'inline', marginRight: '0.25rem' }} />
              City & PIN Code
            </label>
            <input
              type="text"
              id="location"
              name="location"
              className="form-input"
              placeholder="Bangalore 560001"
              value={formData.location}
              onChange={handleChange}
              onFocus={handleFocus}
              disabled={isLoading}
            />
          </div>
        </div>

        {/* Professional Information */}
        <div className="form-section" style={{ marginTop: '2rem' }}>
          <h3 style={{ fontSize: '1rem', marginBottom: '1rem', color: 'var(--accent-cyan)' }}>
            Professional Information (Optional)
          </h3>
          
          <div className="form-row">
            <div className="form-group">
              <label className="form-label" htmlFor="username">
                <UserCircle size={16} style={{ display: 'inline', marginRight: '0.25rem' }} />
                Username / Social Handle
              </label>
              <input
                type="text"
                id="username"
                name="username"
                className="form-input"
                placeholder="johndoe"
                value={formData.username}
                onChange={handleChange}
                onFocus={handleFocus}
                disabled={isLoading}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="company">
                <Building size={16} style={{ display: 'inline', marginRight: '0.25rem' }} />
                Company Name
              </label>
              <input
                type="text"
                id="company"
                name="company"
                className="form-input"
                placeholder="Acme Corp"
                value={formData.company}
                onChange={handleChange}
                onFocus={handleFocus}
                disabled={isLoading}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="context">
              Context
            </label>
            <select
              id="context"
              name="context"
              className="form-input"
              value={formData.context}
              onChange={handleChange}
              onFocus={handleFocus}
              disabled={isLoading}
            >
              <option value="professional">Professional</option>
              <option value="student">Student</option>
              <option value="personal">Personal</option>
            </select>
          </div>
        </div>

        {/* Form Actions */}
        <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem', justifyContent: 'flex-end' }}>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleReset}
            disabled={isLoading}
          >
            Reset
          </button>
          
          <button
            type="submit"
            className="btn btn-primary"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <div className="spinner" />
                Verifying...
              </>
            ) : (
              <>
                <User size={20} />
                Verify Identity
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default IdentityForm;