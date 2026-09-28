import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

apiClient.interceptors.response.use(
  (response) => {
    const raw = response.data;
    // If DRF paginated response format: { count: N, next: ..., previous: ..., results: [...] }
    if (raw && typeof raw === 'object' && Array.isArray(raw.results)) {
      return {
        data: raw.results,
        count: raw.count,
        results: raw.results,
        next: raw.next,
        previous: raw.previous,
        raw
      };
    }
    // Standard response format
    return {
      data: raw,
      raw
    };
  },
  (error) => {
    console.error('API Request Error:', error.response?.data || error.message);
    return Promise.reject(error.response?.data || error);
  }
);

export default apiClient;
