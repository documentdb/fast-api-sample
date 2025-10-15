import { useState, useEffect } from 'react'
import { Package, ShoppingBag, Users, DollarSign } from 'lucide-react'
import { getProducts, getOrders, getCustomers } from '../../services/api'

export default function AdminDashboard() {
  const [stats, setStats] = useState({
    products: 0,
    orders: 0,
    customers: 0,
    revenue: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const [productsData, ordersData, customersData] = await Promise.all([
        getProducts(1, 1),
        getOrders(1, 100),
        getCustomers(1, 1),
      ])

      const revenue = ordersData.items.reduce((sum, order) => sum + order.total_amount, 0)

      setStats({
        products: productsData.total,
        orders: ordersData.total,
        customers: customersData.total,
        revenue,
      })
    } catch (error) {
      console.error('Failed to load stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const cards = [
    { title: 'Total Products', value: stats.products, icon: Package, color: 'bg-blue-500' },
    { title: 'Total Orders', value: stats.orders, icon: ShoppingBag, color: 'bg-green-500' },
    { title: 'Total Customers', value: stats.customers, icon: Users, color: 'bg-purple-500' },
    { title: 'Total Revenue', value: `$${stats.revenue.toFixed(2)}`, icon: DollarSign, color: 'bg-yellow-500' },
  ]

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading dashboard...</p>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-8">Dashboard Overview</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card) => (
          <div key={card.title} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">{card.title}</p>
                <p className="text-2xl font-bold text-gray-900">{card.value}</p>
              </div>
              <div className={`${card.color} p-3 rounded-lg`}>
                <card.icon className="h-6 w-6 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a
            href="/admin/products"
            className="block p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center"
          >
            <Package className="h-8 w-8 text-primary-600 mx-auto mb-2" />
            <span className="font-medium text-gray-900">Manage Products</span>
          </a>
          <a
            href="/admin/orders"
            className="block p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center"
          >
            <ShoppingBag className="h-8 w-8 text-primary-600 mx-auto mb-2" />
            <span className="font-medium text-gray-900">View Orders</span>
          </a>
          <a
            href="/admin/customers"
            className="block p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center"
          >
            <Users className="h-8 w-8 text-primary-600 mx-auto mb-2" />
            <span className="font-medium text-gray-900">View Customers</span>
          </a>
        </div>
      </div>
    </div>
  )
}
