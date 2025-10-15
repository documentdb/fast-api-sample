# 📋 Lab Cheat Sheet

Quick reference for the FastAPI + DocumentDB E-Commerce Lab.

---

## 🔌 Connection Info

```
DocumentDB:    localhost:10260
Username:      admin
Password:      password123
Database:      ecommerce

Connection String:
mongodb://admin:password123@localhost:10260/?authMechanism=SCRAM-SHA-256&tls=true&tlsAllowInvalidCertificates=true

FastAPI:       http://localhost:8000
API Docs:      http://localhost:8000/docs
```

---

## 🚀 Essential Commands

### Docker
```powershell
# Start everything
docker-compose up --build

# Start DocumentDB only
docker-compose up -d documentdb

# Stop everything
docker-compose down

# Remove all data (fresh start)
docker-compose down -v

# View logs
docker-compose logs -f documentdb

# Check status
docker ps
```

### Setup
```powershell
# Automated setup
.\scripts\setup-lab.ps1

# Load sample data
python scripts/load_sample_data.py
```

### FastAPI
```powershell
# Start locally
cd backend
uvicorn app.main:app --reload

# Run tests
pytest backend/tests/ -v

# Format code
black backend/app
```

### mongosh
```powershell
# Connect
mongosh "mongodb://admin:password123@localhost:10260/?authMechanism=SCRAM-SHA-256&tls=true&tlsAllowInvalidCertificates=true"

# Inside mongosh
use ecommerce
db.products.find({})
db.products.countDocuments({})
exit
```

---

## 🎨 VS Code Extension

### Installation
```
Ctrl+Shift+X → Search "DocumentDB" → Install
```

### Quick Actions
```
Ctrl+Shift+P → "DocumentDB: Focus on Databases View"
Ctrl+Shift+R → Run Playground Query
Ctrl+Enter   → Execute Selected Query
Right-click  → Context menu (Refresh, Import, Export, etc.)
```

### View Modes
- **Table** 📊 - Spreadsheet view (best for browsing)
- **Tree** 🌳 - Nested structure (best for relationships)  
- **JSON** 📝 - Raw documents (best for copying)

---

## 📝 Common Queries

### Simple Queries
```javascript
use('ecommerce');

// Find all
db.products.find({});

// Filter by category
db.products.find({ category: "Electronics" });

// Filter by price range
db.products.find({ price: { $gte: 50, $lte: 200 } });

// Find low stock
db.products.find({ stock_quantity: { $lt: 10 } });

// Search by name (case-insensitive)
db.products.find({ name: { $regex: "wireless", $options: "i" } });

// Count documents
db.products.countDocuments({});
```

### Aggregations
```javascript
// Count by category
db.products.aggregate([
  { $group: { _id: "$category", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
]);

// Best sellers
db.orders.aggregate([
  { $unwind: "$items" },
  {
    $group: {
      _id: "$items.product_name",
      totalSold: { $sum: "$items.quantity" },
      revenue: { $sum: "$items.subtotal" }
    }
  },
  { $sort: { totalSold: -1 } },
  { $limit: 10 }
]);

// Customer spending
db.orders.aggregate([
  {
    $group: {
      _id: "$customer_email",
      totalSpent: { $sum: "$total_amount" },
      orderCount: { $sum: 1 }
    }
  },
  { $sort: { totalSpent: -1 } }
]);
```

---

## 🌐 API Endpoints

### Products
```
GET    /api/v1/products              - List all products
GET    /api/v1/products?category=Electronics&skip=0&limit=10
POST   /api/v1/products              - Create product
GET    /api/v1/products/{id}         - Get product
PUT    /api/v1/products/{id}         - Update product
DELETE /api/v1/products/{id}         - Delete product
GET    /api/v1/products/search?name=wireless
```

### Customers
```
GET    /api/v1/customers             - List all customers
POST   /api/v1/customers             - Create customer
GET    /api/v1/customers/{email}     - Get customer
PUT    /api/v1/customers/{email}     - Update customer
DELETE /api/v1/customers/{email}     - Delete customer
```

### Orders
```
GET    /api/v1/orders                - List all orders
POST   /api/v1/orders                - Create order
GET    /api/v1/orders/{id}           - Get order
PUT    /api/v1/orders/{id}/status    - Update status
GET    /api/v1/orders/customer/{email} - Get customer orders
```

---

## 🧪 Test with curl

### Create Product
```powershell
curl -X POST http://localhost:8000/api/v1/products `
  -H "Content-Type: application/json" `
  -d '{
    "name": "Test Product",
    "description": "A test product",
    "price": 99.99,
    "category": "Electronics",
    "sku": "TEST-001",
    "stock_quantity": 10,
    "tags": ["test"]
  }'
```

### Get All Products
```powershell
curl http://localhost:8000/api/v1/products
```

### Filter Products
```powershell
curl "http://localhost:8000/api/v1/products?category=Electronics&limit=5"
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| Container won't start | `docker-compose down; docker-compose up -d documentdb` |
| Can't connect | Check port 10260 is exposed: `docker ps` |
| Extension timeout | Refresh connection, check container is running |
| Import fails | Validate JSON at jsonlint.com, ensure collection exists |
| API errors | Check logs: `docker-compose logs backend` |
| Script won't run | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |

---

## 📚 File Locations

```
docs/
├── LAB_WALKTHROUGH.md           ⭐ Complete lab guide
├── DOCUMENTDB_EXTENSION_GUIDE.md   Deep dive
├── EXTENSION_QUICK_REFERENCE.md    Quick lookup
└── LAB_RESOURCES.md                This file overview

scripts/
├── setup-lab.ps1                ⭐ Auto setup
├── load_sample_data.py             Load via Python
├── sample_products.json         ⭐ Import this
└── sample_customers.json        ⭐ Import this

examples/
└── ecommerce-analytics.mongodb  ⭐ 30+ queries
```

---

## ✅ Lab Checklist

Setup Phase:
- [ ] Docker Desktop running
- [ ] DocumentDB container started (port 10260)
- [ ] VS Code extension installed
- [ ] Connected to DocumentDB

Data Phase:
- [ ] Created `ecommerce` database
- [ ] Imported products (15 items)
- [ ] Imported customers (10 items)
- [ ] Explored in Table/Tree/JSON views

API Phase:
- [ ] FastAPI backend running (port 8000)
- [ ] Tested health endpoint
- [ ] Created test product via API
- [ ] Created test customer
- [ ] Created test order

Learning Phase:
- [ ] Ran queries in MongoDB Playground
- [ ] Tested aggregations
- [ ] Viewed live updates in extension
- [ ] Explored API docs (Swagger UI)

---

## 🎯 Next Steps

1. **Customize**: Add new fields to models
2. **Extend**: Build new API endpoints
3. **Test**: Run `pytest -v`
4. **Experiment**: Try advanced queries
5. **Deploy**: Explore cloud options

---

## 💡 Pro Tips

✨ Open `fastapi-documentdb.code-workspace` for auto-setup
✨ Use MongoDB Playground for reusable queries
✨ Export collections before experimenting
✨ Enable auto-refresh in extension settings
✨ Use Table view for quick data browsing

---

## 🆘 Quick Help

1. Lab stuck? → [LAB_WALKTHROUGH.md](LAB_WALKTHROUGH.md#troubleshooting)
2. Need syntax? → [EXTENSION_QUICK_REFERENCE.md](EXTENSION_QUICK_REFERENCE.md)
3. Want examples? → `examples/ecommerce-analytics.mongodb`
4. Docker issues? → `docker-compose logs -f`
5. API issues? → http://localhost:8000/docs

---

**Happy Building! 🚀**

Print this cheat sheet or keep it open in a separate tab for quick reference during the lab.
