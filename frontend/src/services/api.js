import axios from 'axios';

// Get API URL from environment or default to localhost
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance for authentication API
export const authAPI = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Create axios instance for general API
export const hospitalAPI = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
const addAuthInterceptor = (apiInstance) => {
  apiInstance.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('hospital_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );
};

// Response interceptor to handle auth errors
const addResponseInterceptor = (apiInstance) => {
  apiInstance.interceptors.response.use(
    (response) => {
      return response;
    },
    (error) => {
      // If we get a 401, the token is invalid
      if (error.response?.status === 401) {
        localStorage.removeItem('hospital_token');
        // Redirect to login if not already there
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      }
      return Promise.reject(error);
    }
  );
};

// Add interceptors to both API instances
addAuthInterceptor(authAPI);
addAuthInterceptor(hospitalAPI);
addResponseInterceptor(authAPI);
addResponseInterceptor(hospitalAPI);

// Auth API functions
export const authService = {
  // Login
  login: async (email, password) => {
    const response = await authAPI.post('/auth/login', { email, password });
    return response.data;
  },

  // Register
  register: async (userData) => {
    const response = await authAPI.post('/auth/register', userData);
    return response.data;
  },

  // Get current user
  getCurrentUser: async () => {
    const response = await authAPI.get('/auth/me');
    return response.data;
  },

  // Logout (client-side only)
  logout: () => {
    localStorage.removeItem('hospital_token');
  },

  // Check auth status
  checkAuthStatus: async () => {
    const response = await authAPI.get('/auth/status');
    return response.data;
  },

  // Change password
  changePassword: async (passwordData) => {
    const response = await authAPI.put('/auth/change-password', passwordData);
    return response.data;
  },

  // Request password reset
  requestPasswordReset: async (email) => {
    const response = await authAPI.post('/auth/password-reset', { email });
    return response.data;
  },

  // Confirm password reset
  confirmPasswordReset: async (token, newPassword) => {
    const response = await authAPI.post('/auth/password-reset/confirm', {
      token,
      new_password: newPassword,
      confirm_new_password: newPassword
    });
    return response.data;
  }
};

// Hospital API functions
export const hospitalService = {
  // Doctors
  getDoctors: async (skip = 0, limit = 100) => {
    const response = await hospitalAPI.get(`/medicos?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  getDoctor: async (id) => {
    const response = await hospitalAPI.get(`/medicos/${id}`);
    return response.data;
  },

  createDoctor: async (doctorData) => {
    const response = await hospitalAPI.post('/medicos', doctorData);
    return response.data;
  },

  updateDoctor: async (id, doctorData) => {
    const response = await hospitalAPI.put(`/medicos/${id}`, doctorData);
    return response.data;
  },

  deleteDoctor: async (id) => {
    const response = await hospitalAPI.delete(`/medicos/${id}`);
    return response.data;
  },

  // Users (admin functions)
  getUsers: async (skip = 0, limit = 100) => {
    const response = await hospitalAPI.get(`/auth/users?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  getUsersByRole: async (role, skip = 0, limit = 100) => {
    const response = await hospitalAPI.get(`/auth/users/role/${role}?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  activateUser: async (userId) => {
    const response = await hospitalAPI.put(`/auth/users/${userId}/activate`);
    return response.data;
  },

  deactivateUser: async (userId) => {
    const response = await hospitalAPI.put(`/auth/users/${userId}/deactivate`);
    return response.data;
  }
};

// Helper function to handle API errors
export const handleAPIError = (error) => {
  if (error.response) {
    // Server responded with error status
    return error.response.data?.detail || 'Erro no servidor';
  } else if (error.request) {
    // Request was made but no response received
    return 'Erro de conexão com o servidor';
  } else {
    // Something else happened
    return 'Erro inesperado';
  }
};

export default {
  authAPI,
  hospitalAPI,
  authService,
  hospitalService,
  handleAPIError
};
