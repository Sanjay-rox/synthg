/**
 * Unified Identity Verification - API Client
 */

import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // 2 minutes for complex analysis
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Analyze an identity
 * @param {Object} identity - Identity data to analyze
 * @returns {Promise<Object>} Analysis result
 */
export async function analyzeIdentity(identity) {
  try {
    const response = await api.post('/analyze', identity);
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Analysis failed');
    }
    throw new Error('Network error - please check if backend is running');
  }
}

/**
 * Check API health and configuration
 * @returns {Promise<Object>} Health status
 */
export async function checkHealth() {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw new Error('Backend not available');
  }
}

/**
 * Get API configuration
 * @returns {Promise<Object>} Config status
 */
export async function getConfig() {
  try {
    const response = await api.get('/config');
    return response.data;
  } catch (error) {
    throw new Error('Could not fetch config');
  }
}

export default api;

