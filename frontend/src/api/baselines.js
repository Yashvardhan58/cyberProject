import apiClient from './client';

export const fetchGovernanceLogs = async (params = {}) => {
  return apiClient.get('/baselines/governance/', { params });
};

export const fetchBaselineStats = async () => {
  return apiClient.get('/baselines/stats/');
};

export const overrideQuarantine = async (userId, data = {}) => {
  return apiClient.post(`/baselines/governance/`, { user_id: userId, ...data });
};

export const baselinesApi = {
  getGovernanceLogs: fetchGovernanceLogs,
  fetchGovernanceLogs,
  getBaselineStats: fetchBaselineStats,
  fetchBaselineStats,
  overrideQuarantine
};

export default baselinesApi;
