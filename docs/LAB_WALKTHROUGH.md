# E-commerce Demo Lab Walkthrough

This guide walks you through setting up DocumentDB, loading sample data using the VS Code extension, and running the FastAPI application.

## Prerequisites

- [x] Docker Desktop installed and running
- [x] VS Code with DocumentDB extension installed
- [x] Python 3.11+ (for local development)
- [x] Git (to clone this repository)

## Lab Overview

**Duration**: 30-45 minutes

**What You'll Learn**:
1. Launch DocumentDB using Docker (following official quickstart)
2. Use DocumentDB for VS Code extension to load and explore data
3. Connect FastAPI to DocumentDB
4. Test the e-commerce API endpoints

---

## Step 1: Launch DocumentDB Container

Following the [official DocumentDB quickstart](https://seesharprun-documentdb-prototype.github.io/docs/quickstart/mongodb-shell), we'll use Docker to run DocumentDB.

### Option A: Using Docker Compose (Recommended)

This starts both DocumentDB and the FastAPI backend together:

```powershell
# From the project root
docker-compose up -d documentdb
```

**What this does**:
- Pulls `ghcr.io/documentdb/documentdb/documentdb-local:latest` image
- Creates container named `documentdb-local`
- Exposes port **10260** (DocumentDB default)
- Sets up admin credentials: `admin` / `password123`
- Configures health checks

**Verify it's running**:
```powershell
docker ps
```

You should see:
```
CONTAINER ID   IMAGE                                                  STATUS         PORTS                     NAMES
xxxxx          ghcr.io/documentdb/documentdb/documentdb-local:latest  Up 2 minutes   0.0.0.0:10260->10260/tcp  documentdb-local
```

### Option B: Standalone Docker Command

If you prefer to follow the quickstart guide exactly:

```powershell
docker run -d `
  --name documentdb-container `
  -p 10260:10260 `
  -e USERNAME=admin `
  -e PASSWORD=password123 `
  ghcr.io/documentdb/documentdb/documentdb-local:latest
```

### Verify Connection with mongosh

```powershell
# Test the connection
mongosh "mongodb://admin:password123@localhost:10260/?authMechanism=SCRAM-SHA-256&tls=true&tlsAllowInvalidCertificates=true"
```

You should see:
```
Current Mongosh Log ID: ...
Connecting to: mongodb://localhost:10260/...
Using MongoDB: 8.0.0 (compatible)
Using Mongosh: 2.x.x

test>
```

Type `exit` to disconnect.

---

## Step 2: Load E-commerce Data Using VS Code Extension

Now we'll use the **DocumentDB for VS Code extension** to load our sample data visually.

### 2.1 Install the Extension (if not already installed)

1. Open VS Code
2. Press `Ctrl+Shift+X` (Extensions)
3. Search for `DocumentDB`
4. Install **"DocumentDB for VS Code"** by Microsoft (`ms-azuretools.vscode-documentdb`)

**Alternative**: Open the workspace file which will prompt you to install:
```powershell
code fastapi-documentdb.code-workspace
```

### 2.2 Connect to DocumentDB

1. **Open DocumentDB Extension Panel**:
   - Click the DocumentDB icon in the Activity Bar (left sidebar)
   - OR press `Ctrl+Shift+P` → type "DocumentDB: Focus on Databases View"

2. **Add Connection**:
   - Click the **"+"** button (or right-click → "Add Connection")
   - Choose **"Connection String"**
   - Paste this connection string:
     ```
     mongodb://admin:password123@localhost:10260/?authMechanism=SCRAM-SHA-256&tls=true&tlsAllowInvalidCertificates=true
     ```
   - Press Enter

3. **Verify Connection**:
   - You should see `localhost:10260` in the tree
   - Expand it to see system databases (`admin`, `config`, `local`)

### 2.3 Create the E-commerce Database

1. Right-click on `localhost:10260`
2. Select **"Create Database"**
3. Database name: `ecommerce`
4. Collection name: `products` (we'll create this first)
5. Click "Create"

### 2.4 Load Sample Data

We'll load data into three collections: `products`, `customers`, and `orders`.

#### Method 1: Import JSON Files (Recommended)

First, let's create the sample data files:

**File 1: `scripts/sample_products.json`**
```json
[
  {
    "name": "Wireless Bluetooth Headphones",
    "description": "High-quality over-ear headphones with active noise cancellation",
    "price": 149.99,
    "category": "Electronics",
    "sku": "ELEC-HEAD-001",
    "stock_quantity": 50,
    "tags": ["audio", "bluetooth", "noise-cancelling"]
  },
  {
    "name": "Smart Fitness Watch",
    "description": "Track your workouts, heart rate, and sleep patterns",
    "price": 199.99,
    "category": "Electronics",
    "sku": "ELEC-WATCH-001",
    "stock_quantity": 75,
    "tags": ["fitness", "smartwatch", "health"]
  },
  {
    "name": "Ergonomic Office Chair",
    "description": "Adjustable lumbar support and breathable mesh back",
    "price": 299.99,
    "category": "Furniture",
    "sku": "FURN-CHAIR-001",
    "stock_quantity": 25,
    "tags": ["office", "ergonomic", "chair"]
  },
  {
    "name": "Portable External SSD 1TB",
    "description": "Fast USB-C external storage drive",
    "price": 119.99,
    "category": "Electronics",
    "sku": "ELEC-SSD-001",
    "stock_quantity": 100,
    "tags": ["storage", "usb-c", "portable"]
  },
  {
    "name": "Organic Cotton T-Shirt",
    "description": "Soft and sustainable everyday wear",
    "price": 29.99,
    "category": "Clothing",
    "sku": "CLTH-SHIRT-001",
    "stock_quantity": 200,
    "tags": ["organic", "cotton", "casual"]
  }
]
```

**To import**:
1. Expand `ecommerce` → `products` in the extension
2. Right-click on `products` collection
3. Select **"Import Documents"**
4. Choose `scripts/sample_products.json`
5. Click "Import"

You should see a success message with the number of documents imported.

#### Method 2: Using the Extension's Document Editor

1. Right-click on `products` collection
2. Select **"New Document"**
3. Paste one of the JSON objects from above
4. Click "Save" (✓ icon)
5. Repeat for more documents

#### Method 3: Run the Python Script

```powershell
# Make sure you have the correct connection string in .env
python scripts/load_sample_data.py
```

### 2.5 Verify Data Was Loaded

1. **View in Table Mode**:
   - Right-click on `products` → **"View as Table"**
   - You'll see a spreadsheet-like view of all products
   - Great for quick browsing!

2. **View in Tree Mode**:
   - Click the tree icon at the top
   - Better for seeing nested document structure

3. **View in JSON Mode**:
   - Click the JSON icon `{}`
   - Raw MongoDB documents

4. **Run a Query**:
   - Right-click on `products` → **"New Query"**
   - Try: `{ "category": "Electronics" }`
   - Press "Run" or `Ctrl+Enter`

### 2.6 Explore with MongoDB Playground

Open the sample playground file we created:

1. Open `examples/ecommerce-analytics.mongodb`
2. You'll see 30+ ready-to-run queries
3. Click the **"Run"** button above any query (or `Ctrl+Shift+R`)
4. Results appear in the output panel

**Try these queries**:
```javascript
// See all products
use('ecommerce');
db.products.find({});

// Find low stock items
db.products.find({ stock_quantity: { $lt: 50 } });

// Count products by category
db.products.aggregate([
  {
    $group: {
      _id: "$category",
      count: { $sum: 1 },
      avgPrice: { $avg: "$price" }
    }
  }
]);
```

---

## Step 3: Connect FastAPI to DocumentDB

Now we'll start the FastAPI backend and connect it to our DocumentDB instance.

### 3.1 Configure Environment Variables

Create a `.env` file in the project root (or verify it exists):

```bash
# .env
DOCUMENTDB_USERNAME=admin
DOCUMENTDB_PASSWORD=password123
DOCUMENTDB_URL=mongodb://admin:password123@localhost:10260/?authMechanism=SCRAM-SHA-256&tls=true&tlsAllowInvalidCertificates=true
DOCUMENTDB_DB_NAME=ecommerce
DEBUG=true
RELOAD=true
```

**Important**: Notice we're using **port 10260** (DocumentDB default), not 27017.

### 3.2 Start the FastAPI Backend

#### Option A: Using Docker Compose (Full Stack)

```powershell
# Start everything
docker-compose up --build
```

This starts:
- DocumentDB (if not already running)
- FastAPI backend on http://localhost:8000

**Watch the logs**:
```
documentdb-local  | DocumentDB started successfully
fastapi-backend   | INFO:     Will watch for changes in these directories: ['/app']
fastapi-backend   | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
fastapi-backend   | INFO:     Started reloader process [1]
fastapi-backend   | INFO:     Started server process [7]
fastapi-backend   | INFO:     Waiting for application startup.
fastapi-backend   | INFO:     Connected to DocumentDB successfully!
fastapi-backend   | INFO:     Application startup complete.
```

#### Option B: Local Python Development

If you prefer to run FastAPI locally (outside Docker):

```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the app
cd backend
uvicorn app.main:app --reload
```

### 3.3 Verify the Connection

**Test the health endpoint**:
```powershell
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-10-09T12:34:56.789Z"
}
```

**Open the API docs**:
1. Navigate to: http://localhost:8000/docs
2. You should see the Swagger UI with all endpoints

### 3.4 Test API Endpoints

**Create a product**:
```powershell
curl -X POST http://localhost:8000/api/v1/products `
  -H "Content-Type: application/json" `
  -d '{
    "name": "USB-C Cable 2m",
    "description": "Durable braided charging cable",
    "price": 19.99,
    "category": "Electronics",
    "sku": "ELEC-CABLE-001",
    "stock_quantity": 150,
    "tags": ["usb-c", "charging", "cable"]
  }'
```

**List all products**:
```powershell
curl http://localhost:8000/api/v1/products
```

**Filter by category**:
```powershell
curl "http://localhost:8000/api/v1/products?category=Electronics"
```

### 3.5 Watch Live Updates in VS Code

As you create/update/delete data via the API:

1. Keep the DocumentDB extension panel open
2. Right-click on `products` → **"Refresh"**
3. See your changes in real-time!

Or use **auto-refresh**:
- Settings → `documentdb.autoRefresh` → `true`

---

## Step 4: End-to-End Workflow Demo

Let's simulate a complete e-commerce flow:

### 4.1 Create a Customer

```powershell
curl -X POST http://localhost:8000/api/v1/customers `
  -H "Content-Type: application/json" `
  -d '{
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1-555-0123",
    "address": {
      "street": "123 Main St",
      "city": "San Francisco",
      "state": "CA",
      "postal_code": "94102",
      "country": "USA"
    }
  }'
```

### 4.2 Create an Order

First, get a product ID from the extension or API, then:

```powershell
curl -X POST http://localhost:8000/api/v1/orders `
  -H "Content-Type: application/json" `
  -d '{
    "customer_email": "john.doe@example.com",
    "items": [
      {
        "product_id": "YOUR_PRODUCT_ID_HERE",
        "quantity": 2
      }
    ],
    "shipping_address": {
      "street": "123 Main St",
      "city": "San Francisco",
      "state": "CA",
      "postal_code": "94102",
      "country": "USA"
    }
  }'
```

### 4.3 View in DocumentDB Extension

1. Navigate to `ecommerce` → `orders`
2. Right-click → **"View as Table"**
3. See your order with calculated totals!

### 4.4 Run Analytics Queries

Open `examples/ecommerce-analytics.mongodb` and try:

```javascript
// Customer spending analysis
use('ecommerce');
db.orders.aggregate([
  {
    $group: {
      _id: "$customer_email",
      totalOrders: { $sum: 1 },
      totalSpent: { $sum: "$total_amount" },
      avgOrderValue: { $avg: "$total_amount" }
    }
  },
  { $sort: { totalSpent: -1 } }
]);
```

---

## Troubleshooting

### DocumentDB Container Won't Start

**Problem**: Port conflict or container already running

**Solution**:
```powershell
# Stop existing container
docker stop documentdb-local
docker rm documentdb-local

# Or stop all
docker-compose down

# Start fresh
docker-compose up -d documentdb
```

### Extension Can't Connect

**Problem**: "Failed to connect to localhost:10260"

**Checklist**:
- [ ] Container is running: `docker ps`
- [ ] Port 10260 is exposed: check `docker ps` output
- [ ] Connection string is correct (check port number!)
- [ ] Username/password match Docker env vars

**Test with mongosh**:
```powershell
mongosh "mongodb://admin:password123@localhost:10260/?authMechanism=SCRAM-SHA-256&tls=true&tlsAllowInvalidCertificates=true"
```

### FastAPI Can't Connect to DocumentDB

**Problem**: Backend shows "Connection refused" or timeout

**Check**:
1. DocumentDB is healthy: `docker-compose ps`
2. Network exists: `docker network ls | Select-String app-network`
3. Environment variables in `.env` are correct
4. If running locally (not in Docker), use `localhost:10260`
5. If running in Docker, use `documentdb:10260` (service name)

### No Data Showing in Extension

**Problem**: Extension shows empty collections

**Solutions**:
1. Click refresh icon in extension panel
2. Check you're looking at the right database (`ecommerce`)
3. Verify data was actually inserted:
   ```javascript
   use('ecommerce');
   db.products.countDocuments({});
   ```

### Import Fails with "Invalid JSON"

**Problem**: Extension rejects your JSON file

**Fix**:
- Ensure JSON is valid (use https://jsonlint.com)
- For multiple documents, use array format: `[{...}, {...}]`
- Check for trailing commas
- Ensure proper UTF-8 encoding

---

## Next Steps

Once you have everything running:

1. **Explore the API** (http://localhost:8000/docs)
   - Try all CRUD operations
   - Test filtering and pagination
   - Check validation errors

2. **Run the Test Suite**:
   ```powershell
   pytest backend/tests/ -v
   ```

3. **Try Advanced Queries** in `examples/ecommerce-analytics.mongodb`
   - Revenue analytics
   - Best-selling products
   - Customer insights

4. **Modify the Code**:
   - Add new fields to models
   - Create custom endpoints
   - Implement business logic

5. **Monitor Performance**:
   - Use `.explain()` in MongoDB Playground
   - Check index usage
   - Optimize slow queries

---

## Useful Commands Reference

### Docker
```powershell
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart a service
docker-compose restart backend

# Rebuild and start
docker-compose up --build
```

### DocumentDB mongosh
```powershell
# Connect
mongosh "mongodb://admin:password123@localhost:10260/?authMechanism=SCRAM-SHA-256&tls=true&tlsAllowInvalidCertificates=true"

# Inside mongosh
use ecommerce
db.products.find({})
db.orders.countDocuments({})
exit
```

### FastAPI
```powershell
# Local development
uvicorn app.main:app --reload

# With specific host/port
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
pytest -v

# Format code
black backend/app
```

### VS Code Extension Shortcuts
- `Ctrl+Shift+P` → "DocumentDB: Focus on Databases View"
- `Ctrl+Shift+R` → Run query in MongoDB Playground
- `Ctrl+Enter` → Execute selected query
- Right-click collection → Refresh

---

## Additional Resources

- [DocumentDB Official Docs](https://seesharprun-documentdb-prototype.github.io/)
- [DocumentDB VS Code Extension Guide](./DOCUMENTDB_EXTENSION_GUIDE.md)
- [Extension Quick Reference](./EXTENSION_QUICK_REFERENCE.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Beanie ODM Docs](https://beanie-odm.dev/)

---

## Success Checklist

By the end of this lab, you should have:

- [x] DocumentDB running in Docker on port 10260
- [x] VS Code extension connected to DocumentDB
- [x] Sample e-commerce data loaded (products, customers, orders)
- [x] FastAPI backend running and connected
- [x] Successfully tested CRUD operations via API
- [x] Explored data using extension's Table/Tree/JSON views
- [x] Run queries in MongoDB Playground
- [x] Verified end-to-end workflow (create customer → create order)

🎉 **Congratulations!** You've built a full-stack e-commerce application with DocumentDB and FastAPI!
