# FastAPI + DocumentDB E-Commerce Demo

A modern, full-stack e-commerce application built with FastAPI and open-source DocumentDB (MongoDB-compatible), orchestrated with Docker containers.

## **🧪 New to this project?** [**Start here**](docs/WALKTHROUGH_PART1.md) for step-by-step instructions!

## 🎯 What You'll Learn

- Setting up a FastAPI backend and connecting it to DocumentDB using Docker Compose
- How open-source DocumentDB enables rapid iteration and seamless migration to cloud environments
- **Using the DocumentDB for VS Code extension** to explore, query, and manage your database visually

## 🏗️ Architecture

- **Backend**: FastAPI (Python 3.11+)
- **Database**: DocumentDB (MongoDB-compatible, PostgreSQL-based)
- **ODM**: Beanie (async MongoDB ODM built on Pydantic)
- **Containerization**: Docker & Docker Compose
- **Developer Tools**: DocumentDB for VS Code extension, MongoDB Playground

## 📋 Prerequisites

- Docker Desktop installed and running
- Python 3.11+ (for local development)
- Git
- VS Code with [DocumentDB extension](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-documentdb) (recommended)

## 🚀 Quick Start

#### 1. Clone the Repository

```bash
git clone https://github.com/documentdb/fast-api-sample.git
cd fast-api-sample
```

#### 2. Set up your DocumentDB instance
```bash
# Pull the latest DocumentDB Docker image
docker pull ghcr.io/documentdb/documentdb/documentdb-local:latest

# Tag the image for convenience
docker tag ghcr.io/documentdb/documentdb/documentdb-local:latest documentdb

# Run the container with your chosen username and password
docker run -dt -p 10260:10260 --name documentdb-container documentdb --username <YOUR_USERNAME> --password <YOUR_PASSWORD>
docker image rm -f ghcr.io/documentdb/documentdb/documentdb-local:latest
```
- Click the DocumentDB icon in the VS Code sidebar
- Click "Add New Connection"
- On the navigation bar, click on "Connection String"
- Paste your connection string
```bash
mongodb://<YOUR_USERNAME>:<YOUR_PASSWORD>@localhost:10260/?tls=true&tlsAllowInvalidCertificates=true&authMechanism=SCRAM-SHA-256
```
- Click on the drop-down next to your local connection and select "Create Database..."
- Enter database name and confirm (suggested: ecommerce)
- Click on the drop-down next to your created database and select "Create Collection..."
- Create your collections, `products` and `customers` and confirm.

#### 3. Import data to DocumentDB
- For each collection, click the `Import` button on the top-right corner. 
- Import the `/scripts/sample_customers.json` file in the `customers` collection and `/scripts/sample_products.json` file in the `products` collection.


#### 4. Set Up Environment Variables

```bash
cp .env.example .env
```

In the `.env` file, add your connection string, database name, and DocumentDB credentials.

Afterwards, install the requirements needed for the data to migrate to the frontend.

```bash
cd backend
pip install -r requirements.txt
```

#### 5. Start the Application

```bash
docker-compose up -d
```

This will:
- Build the FastAPI backend container
- Pull and start the DocumentDB container
- Set up networking between services
- Initialize the database connection

### 6. Access the Application

- **Final Product**: http://localhost
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📚 API Endpoints

### Products

- `GET /api/v1/products` - List all products (with pagination)
- `GET /api/v1/products/{id}` - Get a specific product
- `POST /api/v1/products` - Create a new product
- `PUT /api/v1/products/{id}` - Update a product
- `DELETE /api/v1/products/{id}` - Delete a product

### Orders

- `GET /api/v1/orders` - List all orders
- `GET /api/v1/orders/{id}` - Get a specific order
- `POST /api/v1/orders` - Create a new order
- `PUT /api/v1/orders/{id}/status` - Update order status

### Customers

- `GET /api/v1/customers` - List all customers
- `GET /api/v1/customers/{id}` - Get a specific customer
- `POST /api/v1/customers` - Create a new customer

## 🧪 Running Tests

```bash
# Run all tests
docker-compose exec backend pytest

# Run with coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Run specific test file
docker-compose exec backend pytest tests/test_products.py
```

## 🛠️ Development Workflow

### Using the DocumentDB for VS Code Extension (Recommended)

The **DocumentDB for VS Code extension** provides a powerful, integrated way to explore and manage your database directly within VS Code.

#### Quick Setup

1. **Install the Extension**:
   - Open VS Code Extensions (`Ctrl+Shift+X` / `Cmd+Shift+X`)
   - Search for **"DocumentDB for VS Code"**
   - Install the extension by Microsoft (`ms-azuretools.vscode-documentdb`)

2. **Connect to Your Local Database**:
   - Click the DocumentDB icon in the Activity Bar
   - Click **"Add New Connection"** → **"Connection String"**
   - Paste: `mongodb://docdb_user:docdb_password@localhost:27017/?tls=true&tlsAllowInvalidCertificates=true&authMechanism=SCRAM-SHA-256`
   - Name it "E-commerce Local Dev" and connect

3. **Explore Your Data**:
   - Expand your connection to see databases and collections
   - View documents in Table, Tree, or JSON view
   - Run queries with IntelliSense support
   - Import/Export data as JSON

**📖 Detailed Guide**: See [DocumentDB Extension Guide](./docs/DOCUMENTDB_EXTENSION_GUIDE.md) for comprehensive documentation.

### Alternative: Command Line Access

Connect to DocumentDB using mongosh:

```bash
mongosh localhost:27017 -u docdb_user -p docdb_password \
  --authenticationMechanism SCRAM-SHA-256 \
  --tls --tlsAllowInvalidCertificates
```

### Local Development (without Docker)

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Start DocumentDB separately:
```bash
docker run -dt -p 27017:27017 \
  --name documentdb-local \
  ghcr.io/microsoft/documentdb/documentdb-local:latest \
  --username docdb_user --password docdb_password
```

3. Run the FastAPI app:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f documentdb
```

### Rebuild After Code Changes

```bash
docker-compose down
docker-compose up --build
```

## 📁 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── core/
│   │   │   ├── config.py        # Configuration settings
│   │   │   └── database.py      # Database connection setup
│   │   ├── models/              # Beanie document models
│   │   │   ├── product.py
│   │   │   ├── order.py
│   │   │   └── customer.py
│   │   ├── routers/             # API route handlers
│   │   │   ├── products.py
│   │   │   ├── orders.py
│   │   │   └── customers.py
│   │   └── schemas/             # Pydantic request/response schemas
│   │       ├── product.py
│   │       ├── order.py
│   │       └── customer.py
│   ├── tests/                   # Test files
│   │   ├── conftest.py
│   │   ├── test_products.py
│   │   ├── test_orders.py
│   │   └── test_customers.py
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🌟 Key Features Demonstrated

### DocumentDB Capabilities
- ✅ BSON document storage
- ✅ MongoDB wire protocol compatibility
- ✅ Complex aggregation pipelines
- ✅ Indexing strategies
- ✅ Full-text search (optional)
- ✅ Vector search for AI workloads (optional)

### FastAPI Best Practices
- ✅ Async/await patterns
- ✅ Pydantic validation
- ✅ Automatic OpenAPI documentation
- ✅ Dependency injection
- ✅ Error handling
- ✅ CORS configuration

### Docker Best Practices
- ✅ Multi-stage builds
- ✅ Environment variable management
- ✅ Volume mounting for development
- ✅ Health checks
- ✅ Network isolation

## 📄 License

This project is licensed under the MIT License.

## 🔗 Resources

### Official Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [DocumentDB GitHub](https://github.com/documentdb/documentdb)
- [DocumentDB Documentation](https://documentdb.io/)
- [Beanie ODM](https://beanie-odm.dev/)
- [Docker Documentation](https://docs.docker.com/)

### DocumentDB for VS Code Extension
- **Extension Marketplace**: [Install DocumentDB for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-documentdb)
- **GitHub Repository**: [microsoft/vscode-documentdb](https://github.com/microsoft/vscode-documentdb)
- **Extension Documentation**: [Official Docs](https://microsoft.github.io/vscode-documentdb/)
- **Quickstart Guide**: [VS Code Extension Quick Start](https://seesharprun-documentdb-prototype.github.io/docs/quickstart/extension)
- **Blog Post**: [Meet the DocumentDB Extension](https://devblogs.microsoft.com/cosmosdb/meet-the-documentdb-extension-for-vs-code/)
- **Local Guide**: [docs/DOCUMENTDB_EXTENSION_GUIDE.md](./docs/DOCUMENTDB_EXTENSION_GUIDE.md)

### Additional Resources
- [MongoDB Query Documentation](https://www.mongodb.com/docs/manual/tutorial/query-documents/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Python Async/Await](https://docs.python.org/3/library/asyncio.html)
