export interface Product {
  id: string
  name: string
  description: string
  price: number
  category: string
  stock: number
  image_url?: string
  sku?: string
  created_at?: string
  updated_at?: string
}

export interface Customer {
  id: string
  email: string
  name: string
  phone?: string
  address?: {
    street: string
    city: string
    state: string
    zip_code: string
    country: string
  }
  created_at?: string
}

export interface OrderItem {
  product_id: string
  product_name: string
  quantity: number
  price: number
}

export interface Order {
  id: string
  customer_id: string
  customer_email?: string
  customer_name?: string
  items: OrderItem[]
  total_amount: number
  status: 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled'
  created_at: string
  updated_at?: string
}

export interface CartItem {
  product: Product
  quantity: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}
