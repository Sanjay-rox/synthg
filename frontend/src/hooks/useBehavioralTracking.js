/**
 * useBehavioralTracking Hook - FIXED VERSION
 * Tracks user behavioral patterns during form interaction
 * 
 * FIX: Ensures data format matches backend Pydantic models exactly
 */

import { useState, useEffect, useRef, useCallback } from 'react';

const useBehavioralTracking = () => {
  // State
  const [isTracking, setIsTracking] = useState(false);
  const [sessionId] = useState(() => `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  
  // Refs to store tracking data
  const trackingData = useRef({
    startTime: null,
    mouseMovements: [],
    keystrokeData: [],
    navigationPatterns: [],
    lastMouseTime: null,
    lastKeyTime: null
  });

  // Start tracking
  const startTracking = useCallback(() => {
    console.log('🎯 Starting behavioral tracking...');
    trackingData.current.startTime = Date.now();
    setIsTracking(true);
  }, []);

  // Stop tracking and return data
  const stopTracking = useCallback(() => {
    console.log('🛑 Stopping behavioral tracking...');
    setIsTracking(false);
    return getBehavioralData();
  }, []);

  // Get current behavioral data - FIXED FORMAT
  const getBehavioralData = useCallback(() => {
    const data = trackingData.current;
    
    // Calculate completion time as INTEGER (required by backend)
    const completionTime = data.startTime 
      ? Math.round((Date.now() - data.startTime) / 1000) 
      : 0;

    // FIXED: Format navigation_patterns as array of strings (not objects)
    const navigationPatterns = data.navigationPatterns.map(item => {
      // If it's already a string, return it
      if (typeof item === 'string') return item;
      // If it's an object with field property, extract field name
      if (item && typeof item === 'object' && item.field) return item.field;
      // Otherwise, return empty string (will be filtered out)
      return '';
    }).filter(Boolean); // Remove any empty strings

    const formattedData = {
      session_id: sessionId,
      mouse_movements: data.mouseMovements || [],
      keystroke_data: data.keystrokeData || [],
      form_completion_time: completionTime, // INTEGER
      navigation_patterns: navigationPatterns // ARRAY OF STRINGS
    };

    console.log('📊 Formatted behavioral data:', {
      session_id: formattedData.session_id,
      mouse_movements_count: formattedData.mouse_movements.length,
      keystroke_data_count: formattedData.keystroke_data.length,
      form_completion_time: formattedData.form_completion_time,
      form_completion_time_type: typeof formattedData.form_completion_time,
      navigation_patterns: formattedData.navigation_patterns,
      navigation_patterns_type: typeof formattedData.navigation_patterns[0]
    });

    return formattedData;
  }, [sessionId]);

  // Track mouse movement
  const trackMouseMovement = useCallback((event) => {
    if (!isTracking) return;

    const now = Date.now();
    const lastTime = trackingData.current.lastMouseTime || now;
    const timeDelta = now - lastTime;

    // Only track if movement is significant (not too frequent)
    if (timeDelta > 50) { // 50ms threshold
      trackingData.current.mouseMovements.push({
        x: event.clientX,
        y: event.clientY,
        timestamp: now,
        timeDelta: timeDelta
      });

      trackingData.current.lastMouseTime = now;

      // Limit buffer size to prevent memory issues
      if (trackingData.current.mouseMovements.length > 500) {
        trackingData.current.mouseMovements.shift();
      }
    }
  }, [isTracking]);

  // Track mouse click
  const trackMouseClick = useCallback((event) => {
    if (!isTracking) return;

    const now = Date.now();
    trackingData.current.mouseMovements.push({
      x: event.clientX,
      y: event.clientY,
      timestamp: now,
      type: 'click',
      button: event.button // 0=left, 1=middle, 2=right
    });
  }, [isTracking]);

  // Track keystroke
  const trackKeystroke = useCallback((event) => {
    if (!isTracking) return;

    const now = Date.now();
    const lastTime = trackingData.current.lastKeyTime || now;
    const timeDelta = now - lastTime;

    // Anonymize the key (privacy-first)
    let keyCategory = '[OTHER]';
    if (/^[a-zA-Z]$/.test(event.key)) {
      keyCategory = '[LETTER]';
    } else if (/^[0-9]$/.test(event.key)) {
      keyCategory = '[DIGIT]';
    } else if (event.key === 'Backspace') {
      keyCategory = '[BACKSPACE]';
    } else if (event.key === 'Enter') {
      keyCategory = '[ENTER]';
    } else if (event.key === 'Tab') {
      keyCategory = '[TAB]';
    } else if (event.key === ' ') {
      keyCategory = '[SPACE]';
    } else if (/^[!@#$%^&*()_+=\-[\]{}|;:'",.<>?/\\]$/.test(event.key)) {
      keyCategory = '[SPECIAL]';
    }

    trackingData.current.keystrokeData.push({
      key: keyCategory,  // PRIVACY: Only category, not actual key
      timestamp: now,
      timeDelta: timeDelta,
      type: event.type // 'keydown' or 'keyup'
    });

    trackingData.current.lastKeyTime = now;

    // Limit buffer size
    if (trackingData.current.keystrokeData.length > 500) {
      trackingData.current.keystrokeData.shift();
    }
  }, [isTracking]);

  // Track field navigation - FIXED to store only field names
  const trackFieldFocus = useCallback((fieldName) => {
    if (!isTracking) return;

    // FIXED: Store only the field name (string), not an object
    trackingData.current.navigationPatterns.push(fieldName);

    console.log(`🎯 Field navigation tracked: "${fieldName}"`);

    // Limit buffer size
    if (trackingData.current.navigationPatterns.length > 50) {
      trackingData.current.navigationPatterns.shift();
    }
  }, [isTracking]);

  // Set up global event listeners
  useEffect(() => {
    if (!isTracking) return;

    // Mouse movement listener
    const handleMouseMove = (e) => trackMouseMovement(e);
    const handleMouseClick = (e) => trackMouseClick(e);

    // Keyboard listeners
    const handleKeyDown = (e) => trackKeystroke(e);

    // Add listeners
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('click', handleMouseClick);
    document.addEventListener('keydown', handleKeyDown);

    // Cleanup
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('click', handleMouseClick);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isTracking, trackMouseMovement, trackMouseClick, trackKeystroke]);

  // Get tracking statistics (for debugging/display)
  const getTrackingStats = useCallback(() => {
    const data = trackingData.current;
    const elapsedTime = data.startTime 
      ? Math.round((Date.now() - data.startTime) / 1000) 
      : 0;

    return {
      isTracking,
      sessionId,
      elapsedTime,
      mouseMovementCount: data.mouseMovements.length,
      keystrokeCount: data.keystrokeData.length,
      fieldNavigations: data.navigationPatterns.length
    };
  }, [isTracking, sessionId]);

  // Reset tracking data
  const resetTracking = useCallback(() => {
    trackingData.current = {
      startTime: null,
      mouseMovements: [],
      keystrokeData: [],
      navigationPatterns: [],
      lastMouseTime: null,
      lastKeyTime: null
    };
    setIsTracking(false);
  }, []);

  return {
    // Control functions
    startTracking,
    stopTracking,
    resetTracking,
    
    // Data functions
    getBehavioralData,
    getTrackingStats,
    trackFieldFocus,
    
    // State
    isTracking,
    sessionId
  };
};

export default useBehavioralTracking;