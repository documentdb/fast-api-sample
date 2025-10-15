import { Outlet, Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, Package, ShoppingBag, Users, Home } from 'lucide-react'

export default function AdminLayout() {
  const location = useLocation()

  const isActive = (path: string) => location.pathname === path

  const navItems = [
    { path: '/admin/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/admin/products', icon: Package, label: 'Products' },
    { path: '/admin/orders', icon: ShoppingBag, label: 'Orders' },
    { path: '/admin/customers', icon: Users, label: 'Customers' },
  ]

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-gray-900">
        <div className="flex items-center justify-center h-16 bg-gray-800">
          <h1 className="text-white text-xl font-bold">Admin Panel</h1>
        </div>

        <nav className="mt-8">
          <Link
            to="/"
            className="flex items-center px-6 py-3 text-gray-400 hover:bg-gray-800 hover:text-white transition-colors"
          >
            <Home className="h-5 w-5 mr-3" />
            Back to Store
          </Link>

          <div className="mt-4">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center px-6 py-3 transition-colors ${
                  isActive(item.path)
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                }`}
              >
                <item.icon className="h-5 w-5 mr-3" />
                {item.label}
              </Link>
            ))}
          </div>
        </nav>
      </div>

      {/* Main Content */}
      <div className="ml-64">
        <header className="bg-white shadow-sm h-16 flex items-center px-8">
          <h2 className="text-xl font-semibold text-gray-800">
            {navItems.find((item) => isActive(item.path))?.label || 'Admin'}
          </h2>
        </header>

        <main className="p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
