# Module 00 - Prerequisites and Setup

[< Home](Home.md) - [Foundation - Your First API Endpoint >](Module-01.md)

---

## Introduction

In this module, you'll set up your local development environment and deploy the DocumentDB container needed to run this workshop. You will also learn about the structure of this workshop and get an overview of modern API development with FastAPI.

This workshop covers the complete journey from basic API endpoints to advanced production patterns with async database operations and comprehensive testing.

---

## Learning Objectives and Activities

- Set up your local development environment
- Deploy and configure DocumentDB container
- Learn the structure and overview of this workshop
- Explore the core principles of FastAPI and async Python
- Install dependencies and verify the setup
- Run the starter solution locally

---

## Module Exercises

1. Activity 1: Configure Workshop Environment
2. Activity 2: Set Up DocumentDB Container
3. Activity 3: Load Sample Data into DocumentDB
4. Activity 4: Workshop Structure and Overview
5. Activity 5: Verify Dependencies
6. Activity 6: Run and Test the Application

---

## Activity 1: Configure Workshop Environment

This workshop is designed to run entirely in **GitHub Codespaces**, providing a consistent, pre-configured development environment for all participants.

> 💡 **Why Codespaces?** No local setup required, consistent environment for everyone, and automatic dependency installation.

### Prerequisites

- **GitHub account** - [Sign up for free](https://github.com/signup) if you don't have one
- **Web browser** - Chrome, Firefox, Safari, or Edge (latest version recommended)

That's it! Everything else is handled by Codespaces.

### Launch Your Codespace

### Launch Your Codespace

1. **Navigate to the repository**:
   - Go to: `https://github.com/documentdb/fast-api-sample`

2. **Open in GitHub Codespaces**:
   - Click the green **"Code"** button
   - Select the **"Codespaces"** tab
   - Click **"Create codespace on workshop"**
   
   Alternatively, click this badge:
   
   [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/documentdb/fast-api-sample/tree/workshop)

3. **Wait for the environment to build** (first launch takes 2-3 minutes):
   - Python 3.11 environment
   - Node.js 20
   - Docker-in-Docker
   - VS Code extensions (DocumentDB, Python, Docker)
   - All dependencies automatically installed

4. **Verify Codespace is ready**:
   - You should see VS Code in your browser
   - Extensions should be installed (check the sidebar)
   - Terminal should be available at the bottom

5. **Open a terminal** (Terminal → New Terminal) and proceed to Activity 2

---

## Activity 2: Set Up DocumentDB Container

Now that your environment is ready, let's deploy DocumentDB locally using Docker.

### Deploy DocumentDB Container

1. **Pull the DocumentDB Docker image**:
   ```bash
   docker pull ghcr.io/documentdb/documentdb/documentdb-local:latest
   ```

2. **Tag the image for convenience**:
   ```bash
   docker tag ghcr.io/documentdb/documentdb/documentdb-local:latest documentdb
   ```

3. **Run the DocumentDB container**:
   ```bash
   docker run -dt -p 10260:10260 --name documentdb-container documentdb --username admin --password password123
   ```

4. **Verify the container is running**:
   ```bash
   docker ps
   ```
   
   You should see `documentdb-container` running on port 10260.
   
   Expected output:
   ```
   CONTAINER ID   IMAGE        COMMAND                  CREATED         STATUS         PORTS                      NAMES
   abc123def456   documentdb   "./entrypoint.sh --u…"   10 seconds ago  Up 9 seconds   0.0.0.0:10260->10260/tcp   documentdb-container
   ```

### Connect to DocumentDB with VS Code Extension

Download the 'DocumentDB for VS Code' extension on your codespace using the VS Code Marketplace. Afterwards, follow these steps to connect your DocumentDB container to the extension:

1. **Open the DocumentDB extension**:
   - Click the DocumentDB icon in the left sidebar (database icon)
   - Or press `Ctrl+Shift+P` and type "DocumentDB"

2. **Add a new connection**:
   - Click the DocumentDB icon in the VS Code sidebar
   - Click "Add New Connection"
   - Select "Connection String"
   - Paste the connection string:
     ```
     mongodb://admin:password123@localhost:10260/?tls=true&tlsAllowInvalidCertificates=true&authMechanism=SCRAM-SHA-256
     ```

4. **Verify the connection** - You should see your connection in the DocumentDB explorer

---

## Activity 3: Load Sample Data into DocumentDB

Now that DocumentDB is running and connected, let's load sample data to work with throughout the workshop. You'll use the DocumentDB VS Code extension to import JSON files directly into your database.

### Understanding the Sample Data

The workshop includes three JSON files with sample data:

- `scripts/sample_customers.json` - Customer accounts with addresses
- `scripts/sample_products.json` - Product catalog with pricing and inventory
- `scripts/sample_orders.json` - Order history with various statuses

### Load Data Using DocumentDB Extension

1. **Open the DocumentDB extension**:
   - Click the DocumentDB icon in the left sidebar
   - Expand your connection to see databases

2. **Create the database and collections**:
   - Right-click on your connection
   - Select **"Create Database"**
   - Enter database name: `ecommerce`
   - Press Enter

3. **Create the customers collection**:
   - Expand the `ecommerce` database
   - Right-click on the database
   - Select **"Create Collection"**
   - Enter collection name: `customers`
   - Press Enter

4. **Import customer data**:
   - Right-click on the `customers` collection
   - Select **"Import Documents"**
   - Navigate to: `scripts/sample_customers.json`
   - Click **"Open"**
   - Wait for the import confirmation message

5. **Create and import products**:
   - Right-click on the `ecommerce` database
   - Select **"Create Collection"**
   - Enter collection name: `products`
   - Right-click on the `products` collection
   - Select **"Import Documents"**
   - Navigate to: `scripts/sample_products.json`
   - Click **"Open"**

6. **Create and import orders**:
   - Right-click on the `ecommerce` database
   - Select **"Create Collection"**
   - Enter collection name: `orders`
   - Right-click on the `orders` collection
   - Select **"Import Documents"**
   - Navigate to: `scripts/sample_orders.json`
   - Click **"Open"**

### Verify the Data

1. **View the imported data**:
   - Expand each collection (`customers`, `products`, `orders`)
   - Click on a collection to view documents
   - You should see the imported documents listed

2. **Explore a document**:
   - Click on any document to view its contents
   - Notice the structure matches the Beanie models
   - Each document has an automatically generated `_id` field

3. **Check document counts**:
   - Right-click on each collection
   - Select **"View Collection Statistics"** (if available)
   - Or simply count the visible documents

Expected counts:
- **customers**: ~10 documents
- **products**: ~15 documents
- **orders**: ~8 documents

### What You've Accomplished

You now have a fully populated DocumentDB instance with:

✅ **Customer data** - User accounts with contact information and addresses
✅ **Product catalog** - Items with pricing, categories, and inventory levels
✅ **Order history** - Orders in various states (pending, processing, shipped, delivered, cancelled)

This data will be used throughout the workshop as you build and test API endpoints.

> 💡 **Pro Tip**: You can also use the MongoDB query language in the DocumentDB extension to filter and search documents. Try clicking the **"New Query"** button and running: `db.products.find({ category: "Electronics" })`

---

## Activity 4: Workshop Structure and Overview

Now that you have data loaded, let's review the workshop structure and what you'll be building.

### Workshop Module Overview

This workshop consists of 5 progressive modules:

- **Module 0**: Prerequisites and Setup (this module)
- **Module 1**: Foundation - Your First API Endpoint
- **Module 2**: Database Integration with Beanie ODM
- **Module 3**: Advanced Querying and Filtering
- **Module 4**: Production Ready - Testing and Deployment

### Project Structure

This solution is organized in the following structure:

```
/fast-api-sample
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── main.py       # Application entry point
│   │   ├── core/         # Configuration and database setup
│   │   ├── models/       # Beanie document models
│   │   ├── schemas/      # Pydantic validation schemas
│   │   └── routers/      # API route handlers
│   ├── tests/            # Pytest test suite
│   └── Dockerfile        # Backend container definition
├── frontend/             # React application
├── scripts/              # Sample data and utilities
├── docs/                 # Documentation
├── workshop/             # Workshop modules (you are here!)
└── docker-compose.yml    # Multi-service orchestration
```

Here's how the structure appears in VS Code:

![Solution Structure](../docs/media/solution-structure.png)

### What You'll Build

Throughout this workshop, you'll build a complete e-commerce API with:

1. **Products API** - Catalog management with categories, pricing, inventory
2. **Customers API** - User account management with addresses
3. **Orders API** - Order processing with automatic stock management

---

## Activity 5: Verify Dependencies

All dependencies were automatically installed when your Codespace was created via the `postCreateCommand`. Let's verify everything is ready.

### Verify Python Dependencies

1. **Check installed Python packages**:
   ```bash
   pip list | grep -E "fastapi|uvicorn|beanie|motor"
   ```
   
   You should see:
   ```
   beanie           1.x.x
   fastapi          0.x.x
   motor            3.x.x
   uvicorn          0.x.x
   ```

2. **Verify key packages can be imported**:
   ```bash
   python -c "import fastapi, uvicorn, beanie, motor; print('✓ All packages installed successfully')"
   ```
   
   Expected output:
   ```
   ✓ All packages installed successfully!
   ```

### Verify Node.js Dependencies

1. **Check Node.js version**:
   ```bash
   node --version
   ```
   
   Should show: `v20.x.x`

2. **Verify npm packages** (in frontend directory):
   ```bash
   cd frontend && npm list --depth=0 | head -n 20
   ```

### Verify Docker

1. **Check Docker is available**:
   ```bash
   docker --version
   ```
   
   Should show: `Docker version 24.x.x` or later

2. **Verify Docker daemon is running**:
   ```bash
   docker ps
   ```
   
   Should list running containers (may be empty for now)

---

## Activity 6: Run and Test the Application

Let's verify everything is working by running the starter application.

### Create Environment Configuration

1. **Navigate to the project root**:
   ```bash
   cd /workspaces/fast-api-sample
   ```

2. **Create a `.env` file** from the example:
   ```bash
   cp .env.example .env
   ```

3. **Verify the settings** (should already be correct):
   ```bash
   cat .env
   ```
   
   Should contain:
   ```env
   DOCUMENTDB_URL=mongodb://admin:password123@host.docker.internal:10260/?tls=true&tlsAllowInvalidCertificates=true&authMechanism=SCRAM-SHA-256
   DOCUMENTDB_DB_NAME=ecommerce
   DEBUG=true
   RELOAD=true
   ```
   
   > 💡 **Note**: In Codespaces, `host.docker.internal` allows containers to communicate with services running on the Codespace host.

### Run the Application with Docker Compose

1. **Start all services**:
   ```bash
   docker-compose up -d
   ```

   This will:
   - Build the FastAPI backend container
   - Build the React frontend container
   - Set up networking between services
   
   > ⏱️ **First build**: This may take 2-3 minutes as Docker builds the images.

2. **Verify containers are running**:
   ```bash
   docker-compose ps
   ```

   You should see:
   ```
   NAME                IMAGE                    STATUS         PORTS
   fastapi-backend     fast-api-sample-backend  Up 30 seconds  0.0.0.0:8000->8000/tcp
   react-frontend      fast-api-sample-frontend Up 30 seconds  0.0.0.0:80->80/tcp
   ```

### Test the Application

Codespaces automatically forwards ports to make your application accessible.

1. **View forwarded ports**:
   - Click the **"PORTS"** tab in the bottom panel
   - You should see ports 8000 and 80 forwarded
   - Hover over the "Local Address" and click the globe icon 🌐 to open in browser

2. **Open the API documentation**:
   - In the PORTS tab, find port **8000**
   - Click the globe icon to open, then add `/docs` to the URL
   - You should see the Swagger UI with all endpoints

3. **Test the health endpoint**:
   - In the PORTS tab, find port **8000**
   - Right-click → "Open in Browser"
   - Add `/health` to the URL
   - You should see: `{"status": "healthy"}`

4. **Open the frontend** (optional):
   - In the PORTS tab, find port **80**
   - Click the globe icon to open
   - You should see the e-commerce storefront

### Exploring the Starter Code

Let's familiarize ourselves with key files:

1. **Open `backend/app/main.py`**:
   - This is the FastAPI application entry point
   - Notice the `lifespan` context manager for database connection
   - See how routers are included

2. **Open `backend/app/core/database.py`**:
   - This handles the DocumentDB connection
   - See how Beanie is initialized with document models

3. **Open `backend/app/models/product.py`**:
   - This is a Beanie document model
   - Notice the field types, validators, and indexes

4. **Explore the file structure** in VS Code to understand the organization

---

## Validation Checklist

Your setup is successful if:

- ✅ Codespace is running and accessible
- ✅ DocumentDB container is running on port 10260
- ✅ DocumentDB VS Code extension is connected
- ✅ All Python and Node.js dependencies are verified
- ✅ Docker Compose services are running
- ✅ Ports 8000 and 80 are forwarded in Codespaces
- ✅ API documentation is accessible via the forwarded port
- ✅ Health endpoint returns a successful response

---

## Common Issues and Troubleshooting

### Issue 1: Docker container won't start

**Error**: "Port 10260 is already in use"

**Solution**:
- Check if another instance is running: `docker ps`
- Stop the conflicting container: `docker stop documentdb-container`
- Remove it: `docker rm documentdb-container`
- Try again

### Issue 2: Dependencies not installed

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
- The postCreateCommand may have failed
- Manually install dependencies:
  ```bash
  pip install --user -r backend/requirements.txt
  cd frontend && npm install
  ```

### Issue 3: Docker Compose fails to start

**Error**: "Cannot connect to database"

**Solution**:
- Verify DocumentDB container is running: `docker ps`
- Check the connection string in `.env` uses `host.docker.internal` instead of `localhost`
- Restart containers: `docker-compose down && docker-compose up -d`

### Issue 4: VS Code DocumentDB extension won't connect

**Error**: "Connection failed"

**Solution**:
- Verify the connection string is exactly:
  ```
  mongodb://admin:password123@localhost:10260/?tls=true&tlsAllowInvalidCertificates=true&authMechanism=SCRAM-SHA-256
  ```
- Ensure DocumentDB container is running: `docker ps`
- Restart the extension
- Try reconnecting

### Issue 5: Cannot access forwarded ports

**Error**: Port URLs not working

**Solution**:
- Check the PORTS tab in VS Code
- Ensure ports are set to "Public" visibility (right-click → Port Visibility → Public)
- Try stopping and restarting the services:
  ```bash
  docker-compose down && docker-compose up -d
  ```
- Wait a few seconds for services to fully start

### Issue 6: Codespace is slow or unresponsive

**Error**: Performance issues

**Solution**:
- Stop unused services: `docker-compose down`
- Close unnecessary browser tabs
- Restart the Codespace (Codespaces menu → Restart Codespace)
- Consider upgrading to a larger Codespace machine type if available

---

## Success Criteria

To complete this module successfully, you should be able to:

- ✅ Launch and access your GitHub Codespace
- ✅ Have DocumentDB running in a Docker container
- ✅ Connect to DocumentDB using the VS Code extension
- ✅ Verify all dependencies are installed
- ✅ Run the application using Docker Compose
- ✅ Access the API documentation via forwarded ports
- ✅ Understand the project structure and key files

---

## Next Steps

Proceed to [Module 1: Foundation - Your First API Endpoint](Module-01.md) to begin building your FastAPI application. You'll learn:

1. FastAPI routing and request handling
2. Creating your first endpoint from scratch
3. Pydantic schemas for validation
4. Testing with Swagger UI
5. Understanding the request/response lifecycle

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Beanie Documentation](https://beanie-odm.dev/)
- [Docker Documentation](https://docs.docker.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [DocumentDB Documentation](https://learn.microsoft.com/azure/cosmos-db/mongodb/documentdb/)
