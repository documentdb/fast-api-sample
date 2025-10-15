import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import StorefrontLayout from './layouts/StorefrontLayout'
import AdminLayout from './layouts/AdminLayout'
import HomePage from './pages/storefront/HomePage'
import ProductsPage from './pages/storefront/ProductsPage'
import CartPage from './pages/storefront/CartPage'
import CheckoutPage from './pages/storefront/CheckoutPage'
import AdminDashboard from './pages/admin/AdminDashboard'
import AdminProducts from './pages/admin/AdminProducts'
import AdminOrders from './pages/admin/AdminOrders'
import AdminCustomers from './pages/admin/AdminCustomers'
import { CartProvider } from './context/CartContext'

function App() {
  return (
    <Router>
      <CartProvider>
        <Toaster position="top-right" />
        <Routes>
          {/* Storefront Routes */}
          <Route path="/" element={<StorefrontLayout />}>
            <Route index element={<HomePage />} />
            <Route path="products" element={<ProductsPage />} />
            <Route path="cart" element={<CartPage />} />
            <Route path="checkout" element={<CheckoutPage />} />
          </Route>

          {/* Admin Routes */}
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<Navigate to="/admin/dashboard" replace />} />
            <Route path="dashboard" element={<AdminDashboard />} />
            <Route path="products" element={<AdminProducts />} />
            <Route path="orders" element={<AdminOrders />} />
            <Route path="customers" element={<AdminCustomers />} />
          </Route>
        </Routes>
      </CartProvider>
    </Router>
  )
}

export default App
