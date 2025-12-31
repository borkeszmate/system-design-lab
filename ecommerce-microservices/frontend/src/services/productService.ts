import api, { handleApiError } from './api'
import type { Product } from '../types'

export const productService = {
  async getProducts(): Promise<Product[]> {
    try {
      const response = await api.get<Product[]>('/products')
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async getProduct(id: number): Promise<Product> {
    try {
      const response = await api.get<Product>(`/products/${id}`)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },
}
