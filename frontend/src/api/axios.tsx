import axios from 'axios';
import { getAuth } from 'firebase/auth';

// Create an axios instance with default config
const api = axios.create({
  baseURL: 'https://empowerwomen./', // Update this to your API base URL
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json'
  }
});

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

// Add response interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      // Server responded with error status
      console.error('Error response:', error.response.data);
    } else if (error.request) {
      // Request made but no response
      console.error('No response received:', error.request);
    } else {
      // Error in request config
      console.error('Request error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default api;