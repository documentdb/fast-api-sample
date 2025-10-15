import { useState, useEffect } from 'react'
import { Users, Mail, Phone, MapPin } from 'lucide-react'
import toast from 'react-hot-toast'
import { getCustomers } from '../../services/api'
import { Customer } from '../../types'

export default function AdminCustomers() {
  const [customers, setCustomers] = useState<Customer[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadCustomers()
  }, [])

  const loadCustomers = async () => {
    try {
      setLoading(true)
      const data = await getCustomers(1, 100)
      setCustomers(data.items)
    } catch (error) {
      toast.error('Failed to load customers')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading customers...</div>
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Customers</h1>
        <div className="text-sm text-gray-600">
          Total: {customers.length} customers
        </div>
      </div>

      {customers.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow-md">
          <Users className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-600">No customers yet</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {customers.map((customer) => (
            <div
              key={customer.id}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-center mb-4">
                <div className="h-12 w-12 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center">
                  <Users className="h-6 w-6 text-white" />
                </div>
                <div className="ml-3">
                  <h3 className="font-semibold text-lg text-gray-900">
                    {customer.name}
                  </h3>
                  <p className="text-xs text-gray-500">
                    {new Date(customer.created_at || '').toLocaleDateString()}
                  </p>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-start text-sm">
                  <Mail className="h-4 w-4 text-gray-400 mt-0.5 mr-2 flex-shrink-0" />
                  <span className="text-gray-700 break-all">{customer.email}</span>
                </div>

                {customer.phone && (
                  <div className="flex items-center text-sm">
                    <Phone className="h-4 w-4 text-gray-400 mr-2 flex-shrink-0" />
                    <span className="text-gray-700">{customer.phone}</span>
                  </div>
                )}

                {customer.address && (
                  <div className="flex items-start text-sm">
                    <MapPin className="h-4 w-4 text-gray-400 mt-0.5 mr-2 flex-shrink-0" />
                    <span className="text-gray-700">
                      {customer.address.city}, {customer.address.state}{' '}
                      {customer.address.zip_code}
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
