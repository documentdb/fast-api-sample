# E-Commerce Platform with FastAPI & DocumentDB

A full-stack e-commerce application built with **FastAPI**, **React**, and **Azure Cosmos DB for MongoDB (DocumentDB)**. Features both a customer-facing storefront and an admin dashboard.

## 🚀 Features

### Customer Storefront
- **Browse Products** - View all products with category filtering
- **Shopping Cart** - Add/remove items, update quantities
- **Checkout** - Create orders with customer information
- **Responsive Design** - Mobile-friendly interface

### Admin Dashboard
- **Dashboard Overview** - Real-time statistics and metrics
- **Product Management** - CRUD operations for products
- **Order Management** - View and update order statuses
- **Customer Management** - View customer information

## 🏗️ Architecture

```
┌─────────────────┐
│   React SPA     │  Port 80 (Frontend)
│   (Nginx)       │
└────────┬────────┘
         │
         │ /api/*
         ▼
┌─────────────────┐
│   FastAPI       │  Port 8000 (Backend)
│   (Python)      │
└────────┬────────┘
         │
         │ MongoDB Protocol
         ▼
┌─────────────────┐
│  DocumentDB     │  Port 10260 (Database)
│  (Host Machine) │
└─────────────────┘
```

## 📦 Tech Stack

### Backend
- **FastAPI** - Modern, fast Python web framework
- **Motor** - Async MongoDB driver
- **Beanie** - ODM for MongoDB
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **Axios** - HTTP client
- **Lucide Icons** - Icon library

### Database
- **Azure Cosmos DB for MongoDB (DocumentDB)** - NoSQL database

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- DocumentDB running on port 10260

### 1. Start the Application

```powershell
docker-compose up --build -d
```

### 2. Access the Application

- **Storefront**: http://localhost
- **Admin Dashboard**: http://localhost/admin
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

### 3. View Logs

```powershell
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

## 📚 API Endpoints

### Products
- `GET /api/v1/products` - List products
- `POST /api/v1/products` - Create product
- `GET /api/v1/products/{id}` - Get product
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product

### Customers
- `GET /api/v1/customers` - List customers
- `POST /api/v1/customers` - Create customer
- `GET /api/v1/customers/{id}` - Get customer
- `PUT /api/v1/customers/{id}` - Update customer

### Orders
- `GET /api/v1/orders` - List orders
- `POST /api/v1/orders` - Create order
- `GET /api/v1/orders/{id}` - Get order
- `PATCH /api/v1/orders/{id}/status` - Update order status

## 🗄️ Database Collections

### Products
```json
{
  "id": "string",
  "name": "Product Name",
  "description": "Product description",
  "price": 99.99,
  "category": "Electronics",
  "stock": 100,
  "sku": "PROD-001",
  "created_at": "2025-10-09T..."
}
```

### Customers
```json
{
  "id": "string",
  "name": "Customer Name",
  "email": "customer@example.com",
  "phone": "+1234567890",
  "address": {
    "street": "123 Main St",
    "city": "Seattle",
    "state": "WA",
    "zip_code": "98101",
    "country": "USA"
  },
  "created_at": "2025-10-09T..."
}
```

### Orders
```json
{
  "id": "string",
  "customer_id": "string",
  "items": [
    {
      "product_id": "string",
      "product_name": "Product Name",
      "quantity": 2,
      "price": 99.99
    }
  ],
  "total_amount": 199.98,
  "status": "pending",
  "created_at": "2025-10-09T..."
}
```

## 🛠️ Development

### Backend Development

```powershell
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```powershell
cd frontend
npm install
npm run dev
```

## 🔧 Configuration

### Environment Variables

Edit `.env` file:

```env
# Database
DOCUMENTDB_URL=mongodb://patty:chow@host.docker.internal:10260/?tls=true&tlsAllowInvalidCertificates=true&authMechanism=SCRAM-SHA-256
DOCUMENTDB_DB_NAME=shop

# API
API_V1_PREFIX=/api/v1
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000","http://localhost"]

# App Settings
DEBUG=true
RELOAD=true
```

## 📝 Usage Examples

### Creating an Order (Customer Flow)

1. Browse products at http://localhost/products
2. Click "Add to Cart" for desired products
3. View cart at http://localhost/cart
4. Click "Proceed to Checkout"
5. Fill in customer information
6. Submit order

This creates:
- A new **Customer** record
- A new **Order** record with order items
- Automatically decrements product stock

### Managing Orders (Admin Flow)

1. Navigate to http://localhost/admin/orders
2. View all orders with status filters
3. Update order status using dropdown
4. Track order progression: `pending → processing → shipped → delivered`

## 🐳 Docker Services

### Backend Service
- **Image**: `fastapi-vscode-backend`
- **Port**: 8000
- **Features**: Hot-reload enabled for development

### Frontend Service
- **Image**: `fastapi-vscode-frontend`
- **Port**: 80
- **Features**: Nginx serves React SPA, proxies /api/* to backend

## 🧹 Cleanup

```powershell
# Stop containers
docker-compose down

# Remove containers and volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

## 📊 Features Demonstration

### Order Creation Flow
1. Customer browses products and adds to cart
2. During checkout, system creates:
   - Customer record (if new)
   - Order record with items
   - Automatically updates product stock
3. Order appears in admin dashboard
4. Admin can track and update order status

### Admin Capabilities
- **Real-time Dashboard**: View total products, orders, customers, and revenue
- **Product Management**: Add, edit, delete products with stock tracking
- **Order Tracking**: Filter orders by status, update order workflow
- **Customer Insights**: View all customer information and order history

## 🚦 Status Workflow

Orders progress through these statuses:
- `pending` - Order created, awaiting processing
- `processing` - Order is being prepared
- `shipped` - Order has been shipped
- `delivered` - Order delivered to customer
- `cancelled` - Order cancelled

## 🎨 UI Features

- **Responsive Design** - Works on desktop, tablet, and mobile
- **Real-time Updates** - Cart updates instantly
- **Toast Notifications** - User-friendly feedback
- **Loading States** - Clear loading indicators
- **Error Handling** - Graceful error messages

## 📜 License

This project is part of the FastAPI + DocumentDB demonstration.

---

**Built with ❤️ using FastAPI, React, and Azure Cosmos DB for MongoDB**
