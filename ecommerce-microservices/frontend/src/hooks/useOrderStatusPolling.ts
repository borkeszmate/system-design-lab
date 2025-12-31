import { useEffect, useRef } from 'react'
import { useDispatch } from 'react-redux'
import { fetchOrderStatus } from '../features/orders/ordersSlice'
import type { AppDispatch } from '../store/store'

/**
 * Custom hook for polling order status in real-time
 * Demonstrates microservices async processing benefits
 * @param orderId - The order ID to poll
 * @param enabled - Whether polling is enabled
 * @param interval - Polling interval in milliseconds (default: 2000)
 */
export const useOrderStatusPolling = (
  orderId: number | undefined,
  enabled: boolean = false,
  interval: number = 2000
): void => {
  const dispatch = useDispatch<AppDispatch>()
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (!enabled || !orderId) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
      return
    }

    // Start polling
    intervalRef.current = setInterval(() => {
      dispatch(fetchOrderStatus(orderId))
    }, interval)

    // Cleanup on unmount or when dependencies change
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [orderId, enabled, interval, dispatch])
}
