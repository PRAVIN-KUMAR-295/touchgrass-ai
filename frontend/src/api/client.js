/**
 * Centralized API Client for TouchGrass AI Frontend
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        let errorDetail = `HTTP Error ${response.status}: ${response.statusText}`;
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            if (Array.isArray(errorData.detail)) {
              errorDetail = errorData.detail.map((d) => d.msg || JSON.stringify(d)).join(', ');
            } else {
              errorDetail = errorData.detail;
            }
          }
        } catch {
          // ignore non-JSON error bodies
        }
        throw new Error(errorDetail);
      }

      return await response.json();
    } catch (err) {
      console.error(`[API Error] ${endpoint}:`, err);
      throw err;
    }
  }

  /**
   * Health check endpoint
   */
  async getHealth() {
    return this.request('/api/health');
  }

  /**
   * AI provider configuration status
   */
  async getAiStatus() {
    return this.request('/api/ai-status');
  }

  /**
   * Create a new outdoor mission with validated preferences
   */
  async createMission(payload) {
    return this.request('/api/missions', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  /**
   * Generate AI mission plan for an existing mission record
   */
  async generateMission(missionId) {
    return this.request(`/api/missions/${missionId}/generate`, {
      method: 'POST',
    });
  }

  /**
   * Start an outdoor mission (transitions to in_progress)
   */
  async startMission(missionId) {
    return this.request(`/api/missions/${missionId}/start`, {
      method: 'POST',
    });
  }

  /**
   * Complete an in-progress outdoor mission (transitions to completed)
   */
  async completeMission(missionId) {
    return this.request(`/api/missions/${missionId}/complete`, {
      method: 'POST',
    });
  }

  /**
   * Fetch missions list, optionally filtered by status
   */
  async getMissions(status = null) {
    const query = status ? `?status=${encodeURIComponent(status)}` : '';
    return this.request(`/api/missions${query}`);
  }

  /**
   * Fetch outdoor activity stats
   */
  async getStats() {
    return this.request('/api/stats');
  }
}

export const api = new ApiClient(API_BASE_URL);
