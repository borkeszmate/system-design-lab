import React from 'react'
import { useDispatch } from 'react-redux'
import { updateCartItem, removeFromCart } from '../features/cart/cartSlice'
import type { AppDispatch } from '../store/store'
import type { CartItem as CartItemType } from '../types'
import './CartItem.css'

interface CartItemProps {
  item: CartItemType & { product_name?: string }
}

const CartItem: React.FC<CartItemProps> = ({ item }) => {
  const dispatch = useDispatch<AppDispatch>()

  const handleQuantityChange = (newQuantity: number) => {
    if (newQuantity < 1) return
    dispatch(updateCartItem({ itemId: item.id, quantity: newQuantity }))
  }

  const handleRemove = () => {
    dispatch(removeFromCart(item.id))
  }

  return (
    <div className="cart-item">
      <div className="cart-item-info">
        <h4>{item.product_name || item.name || 'Product'}</h4>
        <p className="cart-item-price">${parseFloat(item.price.toString()).toFixed(2)}</p>
      </div>
      <div className="cart-item-actions">
        <div className="quantity-controls">
          <button onClick={() => handleQuantityChange(item.quantity - 1)}>-</button>
          <span>{item.quantity}</span>
          <button onClick={() => handleQuantityChange(item.quantity + 1)}>+</button>
        </div>
        <button className="remove-btn" onClick={handleRemove}>×</button>
      </div>
    </div>
  )
}

export default CartItem
