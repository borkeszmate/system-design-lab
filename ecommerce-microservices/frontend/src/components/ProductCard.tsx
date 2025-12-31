import React from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { addToCart } from '../features/cart/cartSlice'
import type { RootState, AppDispatch } from '../store/store'
import type { Product } from '../types'
import './ProductCard.css'

interface ProductCardProps {
  product: Product
}

const ProductCard: React.FC<ProductCardProps> = ({ product }) => {
  const dispatch = useDispatch<AppDispatch>()
  const { loading } = useSelector((state: RootState) => state.cart)
  const { isAuthenticated } = useSelector((state: RootState) => state.auth)

  const handleAddToCart = () => {
    if (!isAuthenticated) {
      alert('Please login to add items to cart')
      return
    }
    dispatch(addToCart({ productId: product.id, quantity: 1 }))
  }

  return (
    <div className="product-card">
      <div className="product-image">
        <div className="product-placeholder">
          {product.name.charAt(0)}
        </div>
      </div>
      <div className="product-info">
        <h3 className="product-name">{product.name}</h3>
        <p className="product-description">{product.description}</p>
        <div className="product-footer">
          <span className="product-price">${parseFloat(product.price.toString()).toFixed(2)}</span>
          <button
            className="add-to-cart-btn"
            onClick={handleAddToCart}
            disabled={loading || !isAuthenticated}
          >
            {loading ? 'Adding...' : 'Add to Cart'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ProductCard
