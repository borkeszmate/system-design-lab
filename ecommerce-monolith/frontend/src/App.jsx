import { useState, useEffect } from 'react'
import './App.css'

const API_BASE = 'http://localhost:8000/api'

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [user, setUser] = useState(null)
  const [products, setProducts] = useState([])
  const [cart, setCart] = useState([])
  const [loading, setLoading] = useState(false)
  const [checkoutTimer, setCheckoutTimer] = useState(0)
  const [isCheckingOut, setIsCheckingOut] = useState(false)
  const [lastOrder, setLastOrder] = useState(null)

  // Login (using existing test user)
  const login = async () => {
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'paintest@example.com', password: 'password123' })
      })
      const data = await res.json()
      if (data.access_token) {
        setToken(data.access_token)
        localStorage.setItem('token', data.access_token)
      }
    } catch (err) {
      console.error('Login failed:', err)
    }
  }

  // Fetch products
  const fetchProducts = async () => {
    try {
      const res = await fetch(`${API_BASE}/products`)
      const data = await res.json()
      setProducts(data)
    } catch (err) {
      console.error('Failed to fetch products:', err)
    }
  }

  // Fetch cart
  const fetchCart = async () => {
    if (!token) return
    try {
      const res = await fetch(`${API_BASE}/cart`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await res.json()
      setCart(data.items || [])
    } catch (err) {
      console.error('Failed to fetch cart:', err)
    }
  }

  // Add to cart
  const addToCart = async (productId) => {
    if (!token) return alert('Please login first')
    setLoading(true)
    try {
      await fetch(`${API_BASE}/cart/items`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ product_id: productId, quantity: 1 })
      })
      await fetchCart()
    } catch (err) {
      console.error('Failed to add to cart:', err)
    }
    setLoading(false)
  }

  // Checkout with timer
  const checkout = async () => {
    if (!token || cart.length === 0) return

    setIsCheckingOut(true)
    setCheckoutTimer(0)
    setLastOrder(null)

    // Start timer
    const startTime = Date.now()
    const timerInterval = setInterval(() => {
      setCheckoutTimer(Date.now() - startTime)
    }, 100)

    try {
      const res = await fetch(`${API_BASE}/orders/checkout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          shipping_address: '123 Main St, Test City, TC 12345',
          payment_method: 'credit_card'
        })
      })

      clearInterval(timerInterval)

      if (res.ok) {
        const order = await res.json()
        setLastOrder(order)
        await fetchCart() // Refresh cart (should be empty)
      } else {
        const error = await res.json()
        alert(`Checkout failed: ${error.detail || 'Unknown error'}`)
      }
    } catch (err) {
      clearInterval(timerInterval)
      console.error('Checkout failed:', err)
      alert('Checkout failed!')
    }

    setIsCheckingOut(false)
  }

  useEffect(() => {
    fetchProducts()
  }, [])

  useEffect(() => {
    if (token) {
      fetchCart()
    }
  }, [token])

  const cartTotal = cart.reduce((sum, item) => sum + parseFloat(item.price_snapshot) * item.quantity, 0)

  return (
    <div className="app">
      <header className="header">
        <h1>E-Commerce Monolith - Performance Test</h1>
        {!token ? (
          <button onClick={login} className="btn btn-primary">Login as Test User</button>
        ) : (
          <span className="user-info">Logged in as paintest@example.com</span>
        )}
      </header>

      <div className="container">
        {/* Products Section */}
        <section className="products-section">
          <h2>Products</h2>
          {products.length === 0 ? (
            <p className="empty-message">No products available. Create some via API!</p>
          ) : (
            <div className="products-grid">
              {products.map(product => (
                <div key={product.id} className="product-card">
                  <h3>{product.name}</h3>
                  <p className="product-description">{product.description}</p>
                  <p className="product-price">${parseFloat(product.price).toFixed(2)}</p>
                  <button
                    onClick={() => addToCart(product.id)}
                    disabled={loading || !token}
                    className="btn btn-secondary"
                  >
                    Add to Cart
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Cart Section */}
        <section className="cart-section">
          <h2>Shopping Cart</h2>
          {cart.length === 0 ? (
            <p className="empty-message">Cart is empty</p>
          ) : (
            <>
              <div className="cart-items">
                {cart.map(item => (
                  <div key={item.id} className="cart-item">
                    <span className="cart-item-name">Product #{item.product_id}</span>
                    <span className="cart-item-quantity">Qty: {item.quantity}</span>
                    <span className="cart-item-price">${parseFloat(item.price_snapshot).toFixed(2)}</span>
                  </div>
                ))}
              </div>
              <div className="cart-total">
                <strong>Total: ${cartTotal.toFixed(2)}</strong>
              </div>

              {/* Checkout Button with Timer */}
              <button
                onClick={checkout}
                disabled={isCheckingOut || !token}
                className="btn btn-checkout"
              >
                {isCheckingOut ? `Checking out... ${(checkoutTimer / 1000).toFixed(1)}s` : 'Checkout'}
              </button>

              {isCheckingOut && (
                <div className="checkout-alert">
                  <div className="spinner"></div>
                  <p>Processing your order...</p>
                  <p className="timer">Elapsed: {(checkoutTimer / 1000).toFixed(2)}s</p>
                  <p className="pain-message">This is the MONOLITH PAIN - you are waiting for EVERYTHING!</p>
                </div>
              )}
            </>
          )}
        </section>

        {/* Order Confirmation */}
        {lastOrder && (
          <section className="order-confirmation">
            <h2>Order Confirmed!</h2>
            <div className="order-details">
              <p><strong>Order ID:</strong> #{lastOrder.id}</p>
              <p><strong>Total Amount:</strong> ${parseFloat(lastOrder.total_amount).toFixed(2)}</p>
              <p><strong>Status:</strong> {lastOrder.status}</p>
              <div className="duration-highlight">
                <h3>Processing Duration</h3>
                <p className="duration-value">
                  {lastOrder.processing_duration_ms
                    ? `${lastOrder.processing_duration_ms}ms (${(lastOrder.processing_duration_ms / 1000).toFixed(2)}s)`
                    : 'Not recorded'}
                </p>
                <p className="pain-explanation">
                  You had to wait {(lastOrder.processing_duration_ms / 1000).toFixed(1)} seconds
                  for payment processing (1s) + email sending (2s) + database operations!
                </p>
              </div>
              <p className="microservices-promise">
                With microservices, this would take &lt;500ms and process async in the background
              </p>
            </div>
          </section>
        )}
      </div>
    </div>
  )
}

export default App
