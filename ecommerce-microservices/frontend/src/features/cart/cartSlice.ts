import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { cartService } from '../../services/cartService'
import type { Cart, CartItem } from '../../types'
import type { ApiError } from '../../services/api'

export const fetchCart = createAsyncThunk<
  Cart,
  void,
  { rejectValue: ApiError }
>(
  'cart/fetchCart',
  async (_, { rejectWithValue }) => {
    try {
      const response = await cartService.getCart()
      return response
    } catch (error) {
      return rejectWithValue(error as ApiError)
    }
  }
)

export const addToCart = createAsyncThunk<
  Cart,
  { productId: number; quantity: number },
  { rejectValue: ApiError }
>(
  'cart/addToCart',
  async ({ productId, quantity }, { rejectWithValue }) => {
    try {
      const response = await cartService.addToCart(productId, quantity)
      return response
    } catch (error) {
      return rejectWithValue(error as ApiError)
    }
  }
)

export const updateCartItem = createAsyncThunk<
  Cart,
  { itemId: number; quantity: number },
  { rejectValue: ApiError }
>(
  'cart/updateCartItem',
  async ({ itemId, quantity }, { rejectWithValue }) => {
    try {
      const response = await cartService.updateCartItem(itemId, quantity)
      return response
    } catch (error) {
      return rejectWithValue(error as ApiError)
    }
  }
)

export const removeFromCart = createAsyncThunk<
  Cart,
  number,
  { rejectValue: ApiError }
>(
  'cart/removeFromCart',
  async (itemId, { rejectWithValue }) => {
    try {
      const response = await cartService.removeFromCart(itemId)
      return response
    } catch (error) {
      return rejectWithValue(error as ApiError)
    }
  }
)

export const clearCart = createAsyncThunk<
  Cart,
  void,
  { rejectValue: ApiError }
>(
  'cart/clearCart',
  async (_, { rejectWithValue }) => {
    try {
      const response = await cartService.clearCart()
      return response
    } catch (error) {
      return rejectWithValue(error as ApiError)
    }
  }
)

interface CartState {
  items: CartItem[]
  total: number
  loading: boolean
  error: string | null
}

const initialState: CartState = {
  items: [],
  total: 0,
  loading: false,
  error: null,
}

const cartSlice = createSlice({
  name: 'cart',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch cart
      .addCase(fetchCart.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchCart.fulfilled, (state, action) => {
        state.loading = false
        state.items = action.payload.items || []
        state.total = action.payload.total || 0
      })
      .addCase(fetchCart.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload?.message || 'Failed to fetch cart'
      })
      // Add to cart
      .addCase(addToCart.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(addToCart.fulfilled, (state, action) => {
        state.loading = false
        state.items = action.payload.items || []
        state.total = action.payload.total || 0
      })
      .addCase(addToCart.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload?.message || 'Failed to add to cart'
      })
      // Update cart item
      .addCase(updateCartItem.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(updateCartItem.fulfilled, (state, action) => {
        state.loading = false
        state.items = action.payload.items || []
        state.total = action.payload.total || 0
      })
      .addCase(updateCartItem.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload?.message || 'Failed to update cart'
      })
      // Remove from cart
      .addCase(removeFromCart.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(removeFromCart.fulfilled, (state, action) => {
        state.loading = false
        state.items = action.payload.items || []
        state.total = action.payload.total || 0
      })
      .addCase(removeFromCart.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload?.message || 'Failed to remove from cart'
      })
      // Clear cart
      .addCase(clearCart.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(clearCart.fulfilled, (state) => {
        state.loading = false
        state.items = []
        state.total = 0
      })
      .addCase(clearCart.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload?.message || 'Failed to clear cart'
      })
  },
})

export const { clearError } = cartSlice.actions
export default cartSlice.reducer
