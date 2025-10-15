import axios from 'axios'
import { Product, Customer, Order, PaginatedResponse } from '../types'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Products
export const getProducts = async (page = 1, size = 20, category?: string) => {
  const params: any = { page, size }
  if (category) params.category = category
  const response = await api.get<PaginatedResponse<Product>>('/products', { params })
  return response.data
}

export const getProduct = async (id: string) => {
  const response = await api.get<Product>(`/products/${id}`)
  return response.data
}

export const createProduct = async (product: Partial<Product>) => {
  const response = await api.post<Product>('/products', product)
  return response.data
}

export const updateProduct = async (id: string, product: Partial<Product>) => {
  const response = await api.put<Product>(`/products/${id}`, product)
  return response.data
}

export const deleteProduct = async (id: string) => {
  await api.delete(`/products/${id}`)
}

// Customers
export const getCustomers = async (page = 1, size = 20) => {
  const response = await api.get<PaginatedResponse<Customer>>('/customers', {
    params: { page, size },
  })
  return response.data
}

export const getCustomer = async (id: string) => {
  const response = await api.get<Customer>(`/customers/${id}`)
  return response.data
}

export const createCustomer = async (customer: Partial<Customer>) => {
  const response = await api.post<Customer>('/customers', customer)
  return response.data
}

export const updateCustomer = async (id: string, customer: Partial<Customer>) => {
  const response = await api.put<Customer>(`/customers/${id}`, customer)
  return response.data
}

// Orders
export const getOrders = async (page = 1, size = 20, status?: string) => {
  const params: any = { page, size }
  if (status) params.status = status
  const response = await api.get<PaginatedResponse<Order>>('/orders', { params })
  return response.data
}

export const getOrder = async (id: string) => {
  const response = await api.get<Order>(`/orders/${id}`)
  return response.data
}

export const createOrder = async (order: {
  customer_id: string
  items: Array<{ product_id: string; quantity: number }>
}) => {
  const response = await api.post<Order>('/orders', order)
  return response.data
}

export const updateOrderStatus = async (id: string, status: string) => {
  const response = await api.patch<Order>(`/orders/${id}/status`, { status })
  return response.data
}

export default api
