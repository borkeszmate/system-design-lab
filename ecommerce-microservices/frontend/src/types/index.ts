// Auth types
export interface LoginCredentials {
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type?: string
}

export interface User {
  id: number
  email: string
  name?: string
  created_at?: string
}

export interface RegisterData {
  email: string
  password: string
  name?: string
}

// Product types
export interface Product {
  id: number
  name: string
  description: string
  price: number
  stock: number
  image_url?: string
  created_at?: string
}

// Cart types
export interface CartItem {
  id: number
  product_id: number
  quantity: number
  price: number
  name?: string
  image_url?: string
}

export interface Cart {
  items: CartItem[]
  total: number
}

// Order types
export interface OrderItem {
  product_id: number
  quantity: number
  price: number
}

export interface CreateOrderData {
  user_id?: number
  user_email?: string
  items: OrderItem[]
}

export interface Order {
  id: number
  user_id: number
  user_email: string
  status: 'pending' | 'paid' | 'failed' | 'processing'
  total_amount: number
  items: OrderItem[]
  created_at: string
  updated_at?: string
  processing_duration_ms?: number
}

export interface OrderStatusResponse {
  id: number
  status: 'pending' | 'paid' | 'failed' | 'processing'
  processing_duration_ms?: number
}
