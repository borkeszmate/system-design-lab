import api, { handleApiError } from './api'
import type { CreateOrderData, Order, OrderStatusResponse } from '../types'

export const orderService = {
  async createOrder(orderData: CreateOrderData): Promise<Order> {
    try {
      const response = await api.post<Order>('/checkout', orderData)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async getOrders(): Promise<Order[]> {
    try {
      const response = await api.get<Order[]>('/orders')
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async getOrder(orderId: number): Promise<Order> {
    try {
      const response = await api.get<Order>(`/orders/${orderId}`)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async getOrderStatus(orderId: number): Promise<OrderStatusResponse> {
    try {
      const response = await api.get<OrderStatusResponse>(`/orders/${orderId}/status`)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },
}
