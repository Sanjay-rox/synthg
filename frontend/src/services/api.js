/**
 * API Service for SynthGuard Orchestrator - FIXED VERSION
 * Handles all communication with the backend
 * 
 * FIX: Corrected behavioral_data format to match Pydantic model
 */

import axios from 'axios';

// Base URL for orchestrator API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:9000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 seconds (some layers might take time)
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log('🚀 API Request:', config.method.toUpperCase(), config.url);
    if (config.data) {
      console.log('📦 Request payload:', {
        hasIdentityData: !!config.data.identity_data,
        documentCount: config.data.documents?.length || 0,
        hasBehavioralData: !!config.data.behavioral_data,
        behavioralDataPreview: config.data.behavioral_data ? {
          session_id: config.data.behavioral_data.session_id,
          form_completion_time: config.data.behavioral_data.form_completion_time,
          mouse_movements_count: config.data.behavioral_data.mouse_movements?.length || 0,
          keystroke_data_count: config.data.behavioral_data.keystroke_data?.length || 0,
          navigation_patterns_count: config.data.behavioral_data.navigation_patterns?.length || 0
        } : null
      });
    }
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for logging and error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.status, error.message);
    
    // Log detailed error information
    if (error.response) {
      console.error('📋 Error details:', {
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data
      });
    }
    
    return Promise.reject(error);
  }
);

/**
 * API Service Object
 */
const apiService = {
  /**
   * Verify identity through all layers
   * @param {Object} data - Verification request data
   * @returns {Promise} Verification response
   */
  verifyIdentity: async (data) => {
    try {
      const response = await apiClient.post('/api/verify-identity', data);
      return response.data;
    } catch (error) {
      throw {
        message: error.response?.data?.detail || error.response?.data?.message || error.message || 'Verification failed',
        details: error.response?.data || null,
        status: error.response?.status || 500
      };
    }
  },

  /**
   * Simplified verification (minimal response)
   * @param {Object} data - Verification request data
   * @returns {Promise} Simplified verification response
   */
  verifyIdentitySimple: async (data) => {
    try {
      const response = await apiClient.post('/api/verify-identity-simple', data);
      return response.data;
    } catch (error) {
      throw {
        message: error.response?.data?.detail || error.response?.data?.message || error.message || 'Verification failed',
        details: error.response?.data || null,
        status: error.response?.status || 500
      };
    }
  },

  /**
   * Check orchestrator and layer health
   * @returns {Promise} Health status
   */
  checkHealth: async () => {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      throw {
        message: 'Health check failed',
        details: error.message,
        status: error.response?.status || 500
      };
    }
  },

  /**
   * Get detailed layer status
   * @returns {Promise} Layer status
   */
  getLayerStatus: async () => {
    try {
      const response = await apiClient.get('/api/layer-status');
      return response.data;
    } catch (error) {
      throw {
        message: 'Failed to fetch layer status',
        details: error.message,
        status: error.response?.status || 500
      };
    }
  },

  /**
   * Convert file to base64
   * @param {File} file - File object
   * @returns {Promise<string>} Base64 encoded string
   */
  fileToBase64: (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const base64 = reader.result;
        resolve(base64);
      };
      reader.onerror = (error) => reject(error);
      reader.readAsDataURL(file);
    });
  },

  /**
   * Format verification request - FIXED VERSION
   * @param {Object} identityData - Identity form data
   * @param {Array} documents - Document files
   * @param {Object} behavioralData - Behavioral tracking data
   * @returns {Object} Formatted request
   */
  formatVerificationRequest: async (identityData, documents = [], behavioralData = null) => {
    console.log('🔧 Formatting verification request...');
    console.log('  Identity data:', identityData);
    console.log('  Documents:', documents?.length || 0);
    console.log('  Behavioral data:', behavioralData);

    // Format documents
    const formattedDocuments = [];
    for (const doc of documents) {
      const base64 = await apiService.fileToBase64(doc.file);
      formattedDocuments.push({
        type: doc.type,
        file_base64: base64,
        filename: doc.file.name
      });
    }

    // Build base request
    const request = {
      identity_data: {
        name: identityData.name || '',
        email: identityData.email || '',
        phone: identityData.phone || '',
        dob: identityData.dob || null,
        aadhaar: identityData.aadhaar || null,
        pan: identityData.pan || null,
        address: identityData.address || null,
        location: identityData.location || null,
        username: identityData.username || null,
        company: identityData.company || null,
        context: identityData.context || 'professional'
      },
      documents: formattedDocuments
    };

    // FIXED: Add behavioral data only if it exists and has required fields
    if (behavioralData && behavioralData.session_id) {
      console.log('✅ Adding behavioral data to request');
      
      // Ensure all arrays exist (even if empty)
      request.behavioral_data = {
        session_id: behavioralData.session_id,
        mouse_movements: Array.isArray(behavioralData.mouse_movements) 
          ? behavioralData.mouse_movements 
          : [],
        keystroke_data: Array.isArray(behavioralData.keystroke_data) 
          ? behavioralData.keystroke_data 
          : [],
        form_completion_time: behavioralData.form_completion_time || 0,
        navigation_patterns: Array.isArray(behavioralData.navigation_patterns) 
          ? behavioralData.navigation_patterns.map(p => p.field || p) // Extract field name if object
          : []
      };

      console.log('📊 Formatted behavioral data:', {
        session_id: request.behavioral_data.session_id,
        mouse_movements_count: request.behavioral_data.mouse_movements.length,
        keystroke_data_count: request.behavioral_data.keystroke_data.length,
        form_completion_time: request.behavioral_data.form_completion_time,
        navigation_patterns_count: request.behavioral_data.navigation_patterns.length,
        navigation_sample: request.behavioral_data.navigation_patterns.slice(0, 3)
      });
    } else {
      console.log('⚠️ No behavioral data to add (missing or invalid)');
    }

    console.log('✅ Request formatted successfully');
    return request;
  }
};

export default apiService;