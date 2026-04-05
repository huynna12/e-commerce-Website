import axios from 'axios';
import { ACCESS_TOKEN, REFRESH_TOKEN, apiUrl } from './constants';

// Plain axios instance that bypasses the response interceptor — used only for token refresh.
const plainAxios = axios.create({ baseURL: apiUrl, withCredentials: true });

const api = axios.create({
  baseURL: apiUrl,
  // Needed for Django session cookies (recently viewed) when frontend/backends are on different origins.
  withCredentials: true,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(ACCESS_TOKEN);
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem(REFRESH_TOKEN);
      if (!refreshToken) {
        localStorage.removeItem(ACCESS_TOKEN);
        localStorage.removeItem(REFRESH_TOKEN);
        globalThis.location.href = '/login';
        throw error;
      }

      try {
        // Use plainAxios so this request does NOT re-enter the interceptor.
        const { data } = await plainAxios.post('/token/refresh/', { refresh: refreshToken });

        localStorage.setItem(ACCESS_TOKEN, data.access);
        originalRequest.headers.Authorization = `Bearer ${data.access}`;

        return api(originalRequest);
      } catch {
        localStorage.removeItem(ACCESS_TOKEN);
        localStorage.removeItem(REFRESH_TOKEN);
        globalThis.location.href = '/login';
        throw error;
      }
    }

    throw error;
  }
);

export default api;
