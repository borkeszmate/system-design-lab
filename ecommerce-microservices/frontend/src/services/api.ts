import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:9000/api'

// Axios instance with default configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Extended config type for retry logic
interface ExtendedAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
  _retryCount?: number
}

// Request interceptor to add auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as ExtendedAxiosRequestConfig

    // Handle 401 Unauthorized - clear token and redirect to login
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      localStorage.removeItem('token')
      window.location.href = '/'
      return Promise.reject(error)
    }

    // Handle network errors with retry logic
    if (!error.response && !originalRequest._retryCount) {
      originalRequest._retryCount = 0
    }

    if (!error.response && originalRequest._retryCount !== undefined && originalRequest._retryCount < 3) {
      originalRequest._retryCount++
      // Exponential backoff: 1s, 2s, 4s
      const delay = Math.pow(2, originalRequest._retryCount) * 1000
      await new Promise((resolve) => setTimeout(resolve, delay))
      return api(originalRequest)
    }

    return Promise.reject(error)
  }
)

// API Error type
export interface ApiError {
  message: string
  status: number
}

// Helper function to handle API errors
export const handleApiError = (error: unknown): ApiError => {
  if (axios.isAxiosError(error)) {
    if (error.response) {
      // Server responded with error status
      return {
        message: error.response.data?.detail || error.response.data?.message || 'An error occurred',
        status: error.response.status,
      }
    } else if (error.request) {
      // Request made but no response
      return {
        message: 'Network error. Please check your connection and try again.',
        status: 0,
      }
    }
  }

  // Something else happened
  return {
    message: error instanceof Error ? error.message : 'An unexpected error occurred',
    status: -1,
  }
}

export default api
