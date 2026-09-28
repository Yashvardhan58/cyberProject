import apiClient from './client';

export const submitVerdict = async (alertId, verdictData) => {
  return apiClient.post(`/alerts/${alertId}/verdict/`, verdictData);
};

export const fetchVerdicts = async (params = {}) => {
  return apiClient.get('/verdicts/', { params });
};

export const verdictsApi = {
  submitVerdict,
  getVerdicts: fetchVerdicts,
  fetchVerdicts
};

export default verdictsApi;
