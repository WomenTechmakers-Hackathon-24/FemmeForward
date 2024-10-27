import axios from 'axios';

// Create an axios instance with default config
const api = axios.create({
  baseURL: '/api', // Update this to your API base URL
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json'
  }
});

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