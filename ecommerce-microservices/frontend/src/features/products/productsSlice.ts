import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { productService } from '../../services/productService'
import type { Product } from '../../types'
import type { ApiError } from '../../services/api'

export const fetchProducts = createAsyncThunk<
  Product[],
  void,
  { rejectValue: ApiError }
>(
  'products/fetchProducts',
  async (_, { rejectWithValue }) => {
    try {
      const response = await productService.getProducts()
      return response
    } catch (error) {
      return rejectWithValue(error as ApiError)
    }
  }
)

export const fetchProduct = createAsyncThunk<
  Product,
  number,
  { rejectValue: ApiError }
>(
  'products/fetchProduct',
  async (productId, { rejectWithValue }) => {
    try {
      const response = await productService.getProduct(productId)
      return response
    } catch (error) {
      return rejectWithValue(error as ApiError)
    }
  }
)

interface ProductsState {
  items: Product[]
  selectedProduct: Product | null
  loading: boolean
  error: string | null
}

const initialState: ProductsState = {
  items: [],
  selectedProduct: null,
  loading: false,
  error: null,
}

const productsSlice = createSlice({
  name: 'products',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch all products
      .addCase(fetchProducts.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.loading = false
        state.items = action.payload
      })
      .addCase(fetchProducts.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload?.message || 'Failed to fetch products'
      })
      // Fetch single product
      .addCase(fetchProduct.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchProduct.fulfilled, (state, action) => {
        state.loading = false
        state.selectedProduct = action.payload
      })
      .addCase(fetchProduct.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload?.message || 'Failed to fetch product'
      })
  },
})

export const { clearError } = productsSlice.actions
export default productsSlice.reducer
