import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { authService } from '../../services/authService'
import type { User, LoginCredentials, AuthResponse } from '../../types'
import type { ApiError } from '../../services/api'

// Async thunks
export const login = createAsyncThunk<
  AuthResponse,
  LoginCredentials,
  { rejectValue: ApiError }
>(
  'auth/login',
  async ({ email, password }, { rejectWithValue }) => {
    try {
      const response = await authService.login(email, password)
      return response
    } catch (error) {
      return rejectWithValue(error as ApiError)
    }
  }
)

export const getProfile = createAsyncThunk<
  User,
  void,
  { rejectValue: ApiError }
>(
  'auth/getProfile',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authService.getProfile()
      return response
    } catch (error) {
      return rejectWithValue(error as ApiError)
    }
  }
)

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
}

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  loading: false,
  error: null,
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      authService.logout()
      state.user = null
      state.token = null
      state.isAuthenticated = false
      state.error = null
    },
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false
        state.token = action.payload.access_token
        state.isAuthenticated = true
        state.error = null
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload?.message || 'Login failed'
      })
      // Get Profile
      .addCase(getProfile.pending, (state) => {
        state.loading = true
      })
      .addCase(getProfile.fulfilled, (state, action) => {
        state.loading = false
        state.user = action.payload
      })
      .addCase(getProfile.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload?.message || 'Failed to get profile'
        state.isAuthenticated = false
        state.token = null
      })
  },
})

export const { logout, clearError } = authSlice.actions
export default authSlice.reducer
