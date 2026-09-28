import apiClient from './client';

export const fetchUsers = async (params = {}) => {
  return apiClient.get('/users/', { params });
};

export const fetchUserProfile = async (userId) => {
  return apiClient.get(`/users/${userId}/profile/`);
};

export const usersApi = {
  getAllUsers: fetchUsers,
  fetchUsers,
  getUserProfile: fetchUserProfile,
  getUserById: fetchUserProfile,
  fetchUserProfile
};

export default usersApi;
