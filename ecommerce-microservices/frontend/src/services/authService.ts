import api, { handleApiError } from './api'
import type { AuthResponse, User, RegisterData } from '../types'

export const authService = {
  async login(email: string, password: string): Promise<AuthResponse> {
    try {
      const response = await api.post<AuthResponse>('/auth/login', { email, password })
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token)
      }
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async register(userData: RegisterData): Promise<User> {
    try {
      const response = await api.post<User>('/auth/register', userData)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async getProfile(): Promise<User> {
    try {
      const response = await api.get<User>('/auth/me')
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  logout(): void {
    localStorage.removeItem('token')
  },
}
