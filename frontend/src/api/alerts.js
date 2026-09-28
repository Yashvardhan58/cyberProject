import apiClient from './client';

export const fetchAlerts = async (params = {}) => {
  return apiClient.get('/alerts/', { params });
};

export const fetchAlertDetail = async (alertId) => {
  return apiClient.get(`/alerts/${alertId}/`);
};

export const fetchUserAlerts = async (userId) => {
  return apiClient.get('/alerts/', { params: { user_id: userId } });
};

export const alertsApi = {
  getAllAlerts: fetchAlerts,
  fetchAlerts,
  getAlertById: fetchAlertDetail,
  fetchAlertDetail,
  getUserAlerts: fetchUserAlerts,
  fetchUserAlerts
};

export default alertsApi;
