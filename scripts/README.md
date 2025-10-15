# Scripts Directory

This folder contains helper scripts for setting up and managing the e-commerce demo lab.

## Available Scripts

### 1. `setup-lab.ps1` - Quick Lab Setup

**Purpose**: Automated setup script that checks Docker, starts DocumentDB, and provides next steps.

**Usage**:
```powershell
.\scripts\setup-lab.ps1
```

**What it does**:
- ✓ Verifies Docker is installed and running
- ✓ Starts DocumentDB container on port 10260
- ✓ Waits for DocumentDB to be healthy
- ✓ Tests connection with mongosh (if available)
- ✓ Checks if VS Code extension is installed
- ✓ Verifies sample data files exist
- ✓ Displays connection string and next steps

**Output Example**:
```
========================================
  E-commerce Demo Lab - Quick Setup
========================================

[1/5] Checking Docker...
✓ Docker found: Docker version 24.0.6
✓ Docker is running

[2/5] Checking DocumentDB container...
✓ DocumentDB is healthy and ready

...

DocumentDB is running at:
  Host: localhost:10260
  Username: admin
  Password: password123
```

---

### 2. `load_sample_data.py` - Load Sample E-commerce Data

**Purpose**: Python script to load products, customers, and orders into DocumentDB.

**Prerequisites**:
```powershell
pip install motor pymongo python-dotenv
```

**Usage**:
```powershell
# Make sure DocumentDB is running first
python scripts/load_sample_data.py
```

**What it does**:
- Creates `ecommerce` database
- Inserts 15 sample products
- Inserts 10 sample customers
- Inserts 8 sample orders with line items
- Creates indexes for performance
- Validates data integrity

**Sample Output**:
```
Connecting to DocumentDB...
✓ Connected successfully

Loading products...
✓ Inserted 15 products

Loading customers...
✓ Inserted 10 customers

Loading orders...
✓ Inserted 8 orders

Creating indexes...
✓ Created 6 indexes

Data loaded successfully!
```

**Environment Variables**:
Uses `.env` file or defaults:
- `MONGODB_URL` - Connection string (default: mongodb://admin:password123@localhost:10260/...)
- `MONGODB_DB_NAME` - Database name (default: ecommerce)

---

### 3. `sample_products.json` - Product Import File

**Purpose**: JSON file with 15 sample products for importing via VS Code extension.

**Usage with VS Code Extension**:
1. Open DocumentDB extension
2. Navigate to `ecommerce` → `products` collection
3. Right-click → "Import Documents"
4. Select `scripts/sample_products.json`
5. Click "Import"

**Sample Products Include**:
- Electronics (headphones, smartwatch, SSD, keyboard, mouse)
- Furniture (office chair, desk lamp)
- Clothing (organic t-shirt)
- Outdoor (water bottle, sunglasses, backpack)
- Fitness (yoga mat, running shoes, protein powder)
- Appliances (coffee maker)

**Format**:
```json
[
  {
    "name": "Wireless Bluetooth Headphones",
    "description": "High-quality over-ear headphones...",
    "price": 149.99,
    "category": "Electronics",
    "sku": "ELEC-HEAD-001",
    "stock_quantity": 50,
    "tags": ["audio", "bluetooth", "noise-cancelling"]
  },
  ...
]
```

---

### 4. `sample_customers.json` - Customer Import File

**Purpose**: JSON file with 10 sample customers for importing via VS Code extension.

**Usage with VS Code Extension**:
1. Open DocumentDB extension
2. Navigate to `ecommerce` → `customers` collection
3. Right-click → "Import Documents"
4. Select `scripts/sample_customers.json`
5. Click "Import"

**Sample Customers Include**:
- 10 customers from various US cities
- Complete address information
- Contact details (email, phone)
- Mix of active/inactive accounts

**Format**:
```json
[
  {
    "email": "alice.smith@example.com",
    "first_name": "Alice",
    "last_name": "Smith",
    "phone": "+1-555-0101",
    "is_active": true,
    "address": {
      "street": "123 Market Street",
      "city": "San Francisco",
      "state": "CA",
      "postal_code": "94102",
      "country": "USA"
    }
  },
  ...
]
```

---

### 5. `quickstart.ps1` - Original Quickstart Script

**Purpose**: Alternative quickstart script for Docker Compose setup.

**Usage**:
```powershell
.\scripts\quickstart.ps1
```

**What it does**:
- Builds and starts all services (DocumentDB + FastAPI)
- Loads sample data automatically
- Opens browser to API docs

---

## Common Workflows

### Workflow 1: Fresh Lab Setup (Recommended for Beginners)

```powershell
# 1. Run automated setup
.\scripts\setup-lab.ps1

# 2. Open VS Code
code .

# 3. Connect VS Code extension to DocumentDB
# (Use connection string from setup output)

# 4. Import sample data via extension UI
# - Import scripts/sample_products.json to products collection
# - Import scripts/sample_customers.json to customers collection

# 5. Start FastAPI
docker-compose up backend
```

### Workflow 2: Quick Full Stack (Fastest)

```powershell
# Start everything at once
docker-compose up --build

# In another terminal, load data
python scripts/load_sample_data.py

# Open browser
start http://localhost:8000/docs
```

### Workflow 3: Manual Step-by-Step (Most Control)

```powershell
# 1. Start DocumentDB only
docker-compose up -d documentdb

# 2. Wait for health check
docker-compose ps

# 3. Load data with Python script
python scripts/load_sample_data.py

# 4. Explore data with VS Code extension
# (Connect and browse collections)

# 5. Start FastAPI
docker-compose up backend
```

### Workflow 4: Reset Everything

```powershell
# Stop all containers
docker-compose down

# Remove volumes (deletes all data)
docker-compose down -v

# Start fresh
.\scripts\setup-lab.ps1
```

---

## Troubleshooting

### Script Won't Run

**Error**: "Cannot be loaded because running scripts is disabled"

**Fix**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Python Script Fails

**Error**: "ModuleNotFoundError: No module named 'motor'"

**Fix**:
```powershell
pip install -r requirements.txt
```

### Connection Refused

**Error**: "Connection refused to localhost:10260"

**Fix**:
```powershell
# Check if container is running
docker ps

# If not, start it
docker-compose up -d documentdb

# Check logs
docker-compose logs documentdb
```

### Import Fails in VS Code Extension

**Error**: "Failed to import documents"

**Fix**:
1. Verify JSON file is valid (use https://jsonlint.com)
2. Ensure collection exists (create it first)
3. Check connection is active (refresh extension)

---

## File Formats

All JSON files use MongoDB-compatible format:
- Arrays of objects: `[{...}, {...}]`
- Standard JSON types: string, number, boolean, null, object, array
- No `_id` field needed (MongoDB generates automatically)
- ISO 8601 dates as strings: `"2025-01-15T10:30:00Z"`

---

## Environment Variables

Scripts use these environment variables (from `.env` or defaults):

```bash
# DocumentDB Connection
DOCUMENTDB_USERNAME=admin
DOCUMENTDB_PASSWORD=password123
MONGODB_URL=mongodb://admin:password123@localhost:10260/?authMechanism=SCRAM-SHA-256&tls=true&tlsAllowInvalidCertificates=true
MONGODB_DB_NAME=ecommerce

# FastAPI Settings
DEBUG=true
RELOAD=true
API_V1_PREFIX=/api/v1
```

---

## Next Steps

After running the setup scripts:

1. **Explore Documentation**:
   - `docs/LAB_WALKTHROUGH.md` - Complete step-by-step lab guide
   - `docs/DOCUMENTDB_EXTENSION_GUIDE.md` - Extension features and usage
   - `docs/EXTENSION_QUICK_REFERENCE.md` - Quick reference card

2. **Try Sample Queries**:
   - Open `examples/ecommerce-analytics.mongodb`
   - Run queries with `Ctrl+Shift+R`

3. **Test the API**:
   - Navigate to http://localhost:8000/docs
   - Try creating products, customers, and orders

4. **Run Tests**:
   ```powershell
   pytest backend/tests/ -v
   ```

---

## Contributing

When adding new scripts:
1. Use descriptive names: `verb-noun.ps1` or `verb_noun.py`
2. Add usage documentation here
3. Include error handling
4. Provide clear output messages
5. Test on fresh environment

---

## References

- [DocumentDB Quickstart](https://seesharprun-documentdb-prototype.github.io/docs/quickstart/mongodb-shell)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MongoDB JSON Import Format](https://www.mongodb.com/docs/database-tools/mongoimport/)
- [PowerShell Scripting Guide](https://learn.microsoft.com/en-us/powershell/scripting/overview)
