import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { orderService } from '../../services/orderService'
import type { CreateOrderData, Order, OrderStatusResponse } from '../../types'
import type { ApiError } from '../../services/api'

export const createOrder = createAsyncThunk<
  Order,
  CreateOrderData,
  { rejectValue: ApiError }
>(
  'orders/createOrder',
  async (orderData, { rejectWithValue }) => {
    try {
      const response = await orderService.createOrder(orderData)
      return response
    } catch (error) {
      return rejectWithValue(error as ApiError)
    }
  }
)

export const fetchOrders = createAsyncThunk<
  Order[],
  void,
  { rejectValue: ApiError }
>(
  'orders/fetchOrders',
  async (_, { rejectWithValue }) => {
    try {
      const response = await orderService.getOrders()
      return response
    } catch (error) {
      return rejectWithValue(error as ApiError)
    }
  }
)

export const fetchOrder = createAsyncThunk<
  Order,
  number,
  { rejectValue: ApiError }
>(
  'orders/fetchOrder',
  async (orderId, { rejectWithValue }) => {
    try {
      const response = await orderService.getOrder(orderId)
      return response
    } catch (error) {
      return rejectWithValue(error as ApiError)
    }
  }
)

export const fetchOrderStatus = createAsyncThunk<
  OrderStatusResponse,
  number,
  { rejectValue: ApiError }
>(
  'orders/fetchOrderStatus',
  async (orderId, { rejectWithValue }) => {
    try {
      const response = await orderService.getOrderStatus(orderId)
      return response
    } catch (error) {
      return rejectWithValue(error as ApiError)
    }
  }
)

interface OrdersState {
  items: Order[]
  currentOrder: Order | null
  checkoutTimer: number
  isCheckingOut: boolean
  loading: boolean
  error: string | null
}

const initialState: OrdersState = {
  items: [],
  currentOrder: null,
  checkoutTimer: 0,
  isCheckingOut: false,
  loading: false,
  error: null,
}

const ordersSlice = createSlice({
  name: 'orders',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
    setCheckoutTimer: (state, action: PayloadAction<number>) => {
      state.checkoutTimer = action.payload
    },
    setIsCheckingOut: (state, action: PayloadAction<boolean>) => {
      state.isCheckingOut = action.payload
    },
    clearCurrentOrder: (state) => {
      state.currentOrder = null
    },
    updateOrderStatus: (state, action: PayloadAction<OrderStatusResponse>) => {
      // Real-time status update
      if (state.currentOrder && state.currentOrder.id === action.payload.id) {
        state.currentOrder.status = action.payload.status
        if (action.payload.processing_duration_ms !== undefined) {
          state.currentOrder.processing_duration_ms = action.payload.processing_duration_ms
        }
      }
      // Update in orders list
      const orderIndex = state.items.findIndex(o => o.id === action.payload.id)
      if (orderIndex !== -1) {
        state.items[orderIndex].status = action.payload.status
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Create order
      .addCase(createOrder.pending, (state) => {
        state.loading = true
        state.error = null
        state.isCheckingOut = true
      })
      .addCase(createOrder.fulfilled, (state, action) => {
        state.loading = false
        state.currentOrder = action.payload
        state.isCheckingOut = false
      })
      .addCase(createOrder.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload?.message || 'Failed to create order'
        state.isCheckingOut = false
      })
      // Fetch orders
      .addCase(fetchOrders.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchOrders.fulfilled, (state, action) => {
        state.loading = false
        state.items = action.payload
      })
      .addCase(fetchOrders.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload?.message || 'Failed to fetch orders'
      })
      // Fetch single order
      .addCase(fetchOrder.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchOrder.fulfilled, (state, action) => {
        state.loading = false
        state.currentOrder = action.payload
      })
      .addCase(fetchOrder.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload?.message || 'Failed to fetch order'
      })
      // Fetch order status (real-time polling)
      .addCase(fetchOrderStatus.fulfilled, (state, action) => {
        if (state.currentOrder && state.currentOrder.id === action.payload.id) {
          state.currentOrder.status = action.payload.status
          if (action.payload.processing_duration_ms !== undefined) {
            state.currentOrder.processing_duration_ms = action.payload.processing_duration_ms
          }
        }
      })
  },
})

export const {
  clearError,
  setCheckoutTimer,
  setIsCheckingOut,
  clearCurrentOrder,
  updateOrderStatus
} = ordersSlice.actions

export default ordersSlice.reducer
