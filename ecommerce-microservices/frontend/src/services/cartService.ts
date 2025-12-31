import api, { handleApiError } from './api'
import type { Cart } from '../types'

export const cartService = {
  async getCart(): Promise<Cart> {
    try {
      const response = await api.get<Cart>('/cart')
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async addToCart(productId: number, quantity: number = 1): Promise<Cart> {
    try {
      const response = await api.post<Cart>('/cart/items', {
        product_id: productId,
        quantity,
      })
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async updateCartItem(itemId: number, quantity: number): Promise<Cart> {
    try {
      const response = await api.put<Cart>(`/cart/items/${itemId}`, { quantity })
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async removeFromCart(itemId: number): Promise<Cart> {
    try {
      const response = await api.delete<Cart>(`/cart/items/${itemId}`)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async clearCart(): Promise<Cart> {
    try {
      const response = await api.delete<Cart>('/cart')
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },
}
