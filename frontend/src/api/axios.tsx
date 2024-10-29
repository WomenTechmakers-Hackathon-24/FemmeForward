import axios from 'axios';
import { getAuth } from 'firebase/auth';

const apiUrl = import.meta.env.VITE_API_BASE_URL;

// Create an axios instance with default config
const api = axios.create({
  baseURL: apiUrl, // Update this to your API base URL
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Token refresh handling
let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

const subscribeTokenRefresh = (cb: (token: string) => void) => {
  refreshSubscribers.push(cb);
};

const onTokenRefreshed = (token: string) => {
  refreshSubscribers.forEach(cb => cb(token));
  refreshSubscribers = [];
};

// Add request interceptor to include Firebase token
api.interceptors.request.use(
  async config => {
    const auth = getAuth();
    const currentUser = auth.currentUser;

    if (currentUser) {
      const firebaseIdToken = await currentUser.getIdToken();
      config.headers['Authorization'] = `Bearer ${firebaseIdToken}`;
    }

    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling and token refresh
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (!isRefreshing) {
        isRefreshing = true;
        try {
          const auth = getAuth();
          const user = auth.currentUser;
          if (user) {
            const newToken = await user.getIdToken(true);
            onTokenRefreshed(newToken);
            originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
            return api(originalRequest);
          }
        } finally {
          isRefreshing = false;
        }
      }

      return new Promise(resolve => {
        subscribeTokenRefresh(token => {
          originalRequest.headers['Authorization'] = `Bearer ${token}`;
          resolve(api(originalRequest));
        });
      });
    }

    if (error.response) {
      console.error('Error response:', error.response.data);
    } else if (error.request) {
      console.error('No response received:', error.request);
    } else {
      console.error('Request error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export default api;