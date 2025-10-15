import { Outlet, Link } from 'react-router-dom'
import { ShoppingCart, Store } from 'lucide-react'
import { useCart } from '../context/CartContext'

export default function StorefrontLayout() {
  const { totalItems } = useCart()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center space-x-2">
              <Store className="h-8 w-8 text-primary-600" />
              <span className="text-xl font-bold text-gray-900">E-Shop</span>
            </Link>

            <nav className="flex space-x-8">
              <Link
                to="/"
                className="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium"
              >
                Home
              </Link>
              <Link
                to="/products"
                className="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium"
              >
                Products
              </Link>
              <Link
                to="/admin"
                className="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium"
              >
                Admin
              </Link>
            </nav>

            <Link
              to="/cart"
              className="flex items-center space-x-2 text-gray-700 hover:text-primary-600"
            >
              <div className="relative">
                <ShoppingCart className="h-6 w-6" />
                {totalItems > 0 && (
                  <span className="absolute -top-2 -right-2 bg-primary-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                    {totalItems}
                  </span>
                )}
              </div>
              <span className="text-sm font-medium">Cart</span>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main>
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-center text-gray-400">
            © 2025 E-Shop. Built with FastAPI & DocumentDB
          </p>
        </div>
      </footer>
    </div>
  )
}
