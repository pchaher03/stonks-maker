import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Helper map converting tag strings to integer trading days
const HORIZON_MAP = {
  '1D': 1,
  '5D': 5,
  '1M': 21,
};

export const fetchPrediction = async (ticker, horizon = '1D') => {
  // Convert horizon to integer if string tag was passed, defaulting to 1
  const horizonDays = typeof horizon === 'string' ? (HORIZON_MAP[horizon] || 1) : horizon;

  const response = await apiClient.post('/predictions', { 
    ticker, 
    horizon: horizonDays 
  });
  return response.data;
};

export const fetchSentiment = async (ticker) => {
  const response = await apiClient.get(`/news/${ticker}`);
  return response.data;
};

export const fetchExplanation = async (ticker) => {
  const response = await apiClient.get(`/explain/${ticker}`);
  return response.data;
};