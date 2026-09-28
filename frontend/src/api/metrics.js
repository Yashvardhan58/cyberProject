import apiClient from './client';

export const fetchSummaryMetrics = async () => {
  return apiClient.get('/metrics/summary/');
};

export const fetchExperimentResults = async () => {
  return apiClient.get('/metrics/experiments/');
};

export const metricsApi = {
  getSummaryMetrics: fetchSummaryMetrics,
  fetchSummaryMetrics,
  getExperimentResults: fetchExperimentResults,
  fetchExperimentResults
};

export default metricsApi;
