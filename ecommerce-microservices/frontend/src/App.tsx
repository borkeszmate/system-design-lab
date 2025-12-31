import { useState, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { login, logout, getProfile } from './features/auth/authSlice'
import { fetchProducts } from './features/products/productsSlice'
import { fetchCart } from './features/cart/cartSlice'
import { createOrder, setCheckoutTimer, clearCurrentOrder } from './features/orders/ordersSlice'
import { useOrderStatusPolling } from './hooks/useOrderStatusPolling'
import ProductCard from './components/ProductCard'
import CartItem from './components/CartItem'
import ErrorBoundary from './components/ErrorBoundary'
import type { RootState, AppDispatch } from './store/store'
import type { CreateOrderData } from './types'
import './App.css'

function App() {
  const dispatch = useDispatch<AppDispatch>()
  const [_timerInterval, setTimerInterval] = useState<NodeJS.Timeout | null>(null)

  const { user, isAuthenticated, loading: authLoading } = useSelector((state: RootState) => state.auth)
  const { items: products, loading: productsLoading, error: productsError } = useSelector((state: RootState) => state.products)
  const { items: cartItems, total: cartTotal, loading: cartLoading } = useSelector((state: RootState) => state.cart)
  const { currentOrder, checkoutTimer, isCheckingOut } = useSelector((state: RootState) => state.orders)

  // Real-time polling for order status
  useOrderStatusPolling(
    currentOrder?.id,
    !!currentOrder && currentOrder.status !== 'paid',
    2000 // Poll every 2 seconds
  )

  useEffect(() => {
    // Fetch products on mount (public endpoint)
    dispatch(fetchProducts())

    // If authenticated, fetch user profile and cart
    if (isAuthenticated) {
      dispatch(getProfile())
      dispatch(fetchCart())
    }
  }, [dispatch, isAuthenticated])

  const handleLogin = async () => {
    const result = await dispatch(login({
      email: 'paintest@example.com',
      password: 'password123'
    }))

    if (result.meta.requestStatus === 'fulfilled') {
      dispatch(getProfile())
      dispatch(fetchCart())
    }
  }

  const handleLogout = () => {
    dispatch(logout())
  }

  const handleCheckout = async () => {
    if (cartItems.length === 0) {
      alert('Cart is empty')
      return
    }

    // Start timer
    const startTime = Date.now()
    const interval = setInterval(() => {
      dispatch(setCheckoutTimer(Date.now() - startTime))
    }, 100)
    setTimerInterval(interval)

    // Prepare order data
    const orderData: CreateOrderData = {
      user_id: user?.id,
      user_email: user?.email,
      items: cartItems.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
        price: item.price
      }))
    }

    try {
      await dispatch(createOrder(orderData)).unwrap()
      // Stop timer
      clearInterval(interval)
      setTimerInterval(null)
      // Refresh cart after successful checkout
      dispatch(fetchCart())
    } catch (error) {
      clearInterval(interval)
      setTimerInterval(null)
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      alert('Checkout failed: ' + errorMessage)
    }
  }

  const handleDismissOrder = () => {
    dispatch(clearCurrentOrder())
    dispatch(setCheckoutTimer(0))
  }

  return (
    <ErrorBoundary>
      <div className="app">
        <div className="container">
          {/* Header */}
          <header className="header">
            <div>
              <h1>
                E-Commerce Store
                <span className="header-badge">Microservices</span>
              </h1>
            </div>
            <div className="header-actions">
              {isAuthenticated ? (
                <>
                  {user && <span className="user-info">Hi, {user.name || user.email}</span>}
                  <button className="btn btn-secondary" onClick={handleLogout}>
                    Logout
                  </button>
                </>
              ) : (
                <button
                  className="btn btn-primary"
                  onClick={handleLogin}
                  disabled={authLoading}
                >
                  {authLoading ? 'Logging in...' : 'Login as Test User'}
                </button>
              )}
            </div>
          </header>

          {/* Success Banner */}
          {currentOrder && !isCheckingOut && (
            <div className="success-banner">
              <h2>Order Placed Successfully!</h2>
              <div className="order-details">
                <div className="order-detail-row">
                  <span>Order ID:</span>
                  <span>#{currentOrder.id}</span>
                </div>
                <div className="order-detail-row">
                  <span>Status:</span>
                  <span className={`order-status ${currentOrder.status}`}>
                    {currentOrder.status?.toUpperCase()}
                  </span>
                </div>
                <div className="order-detail-row">
                  <span>Total:</span>
                  <span>${parseFloat(currentOrder.total_amount.toString()).toFixed(2)}</span>
                </div>
              </div>

              {currentOrder.processing_duration_ms !== undefined && (
                <div className="duration-highlight">
                  {currentOrder.processing_duration_ms}ms ({(currentOrder.processing_duration_ms / 1000).toFixed(2)}s)
                </div>
              )}

              {/* Real-time status updates */}
              {currentOrder.status !== 'paid' && (
                <div className="status-indicator">
                  <div className="status-dot"></div>
                  <span className="status-text">
                    Processing payment asynchronously...
                  </span>
                </div>
              )}

              {currentOrder.status === 'paid' && (
                <div className="microservices-badge">
                  Async processing complete! Email sent via message queue.
                </div>
              )}

              <button
                className="btn btn-primary"
                onClick={handleDismissOrder}
                style={{ marginTop: '20px', width: '100%' }}
              >
                Continue Shopping
              </button>
            </div>
          )}

          {/* Main Content */}
          <div className="main-content">
            {/* Products */}
            <section className="products-section">
              <h2 className="section-title">Products</h2>

              {productsError && (
                <div className="error-message">
                  Error loading products: {productsError}
                </div>
              )}

              {productsLoading ? (
                <div className="loading">Loading products...</div>
              ) : (
                <div className="products-grid">
                  {products.map((product) => (
                    <ProductCard key={product.id} product={product} />
                  ))}
                </div>
              )}
            </section>

            {/* Cart */}
            <aside className="cart-section">
              <h2 className="section-title">Shopping Cart</h2>

              {!isAuthenticated ? (
                <div className="empty-cart">
                  <p>Please login to view your cart</p>
                </div>
              ) : cartLoading ? (
                <div className="loading">Loading cart...</div>
              ) : cartItems.length === 0 ? (
                <div className="empty-cart">
                  <p>Your cart is empty</p>
                </div>
              ) : (
                <>
                  <div className="cart-items">
                    {cartItems.map((item) => (
                      <CartItem key={item.id} item={item} />
                    ))}
                  </div>

                  <div className="cart-total">
                    <div className="cart-total-row">
                      <span>Total:</span>
                      <span className="cart-total-amount">
                        ${parseFloat(cartTotal.toString()).toFixed(2)}
                      </span>
                    </div>
                  </div>

                  <button
                    className="checkout-btn"
                    onClick={handleCheckout}
                    disabled={isCheckingOut || cartItems.length === 0}
                  >
                    {isCheckingOut ? 'Processing...' : 'Checkout'}
                  </button>
                </>
              )}
            </aside>
          </div>

          {/* Checkout Modal */}
          {isCheckingOut && (
            <div className="checkout-modal">
              <div className="checkout-content">
                <div className="checkout-loader">
                  <div className="spinner"></div>
                  <h3>Processing your order...</h3>
                  <div className="checkout-timer">
                    Elapsed: {(checkoutTimer / 1000).toFixed(2)}s
                  </div>
                  <div className="microservices-badge">
                    Microservices in action! Order processing asynchronously.
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </ErrorBoundary>
  )
}

export default App
