import apiClient from './client';

export const createSession = async (alertId) => {
  return apiClient.post(`/explanations/alerts/${alertId}/chat/init/`);
};

export const sendMessage = async (sessionToken, message) => {
  return apiClient.post(`/explanations/sessions/${sessionToken}/`, {
    message
  });
};

export const getSessionMessages = async (sessionToken) => {
  return apiClient.get(`/explanations/sessions/${sessionToken}/`);
};

export const chatApi = {
  createSession,
  sendMessage,
  getSessionMessages
};

export default chatApi;

