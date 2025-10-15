# 🏗️ Architecture Overview

Visual guide to the FastAPI + DocumentDB E-Commerce Demo architecture.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Development Machine                          │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                         VS Code Editor                          │ │
│  │                                                                  │ │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │ │
│  │  │ Python Code      │  │ MongoDB          │  │ DocumentDB   │ │ │
│  │  │ Editor           │  │ Playground       │  │ Extension    │ │ │
│  │  │                  │  │ (.mongodb files) │  │ (GUI)        │ │ │
│  │  └──────────────────┘  └──────────────────┘  └──────────────┘ │ │
│  │                                                                  │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                      Docker Desktop                             │ │
│  │                                                                  │ │
│  │  ┌──────────────────────────────┐  ┌───────────────────────┐  │ │
│  │  │   FastAPI Backend Container  │  │  DocumentDB Container │  │ │
│  │  │   (Port 8000)                │  │  (Port 10260)         │  │ │
│  │  │                              │  │                       │  │ │
│  │  │  ┌────────────────────────┐  │  │  ┌────────────────┐  │  │ │
│  │  │  │  FastAPI App           │  │  │  │  DocumentDB    │  │  │ │
│  │  │  │  - REST API            │  │  │  │  - MongoDB     │  │  │ │
│  │  │  │  - Pydantic Schemas    │  │  │  │    Protocol    │  │  │ │
│  │  │  │  - Beanie ODM          │◄─┼──┼─►│  - PostgreSQL  │  │  │ │
│  │  │  │  - Motor Driver        │  │  │  │    Backend     │  │  │ │
│  │  │  └────────────────────────┘  │  │  │  - TLS/SCRAM   │  │  │ │
│  │  │                              │  │  └────────────────┘  │  │ │
│  │  └──────────────────────────────┘  └───────────────────────┘  │ │
│  │              ▲                                  ▲               │ │
│  │              │                                  │               │ │
│  │              └──────────── app-network ────────┘               │ │
│  │                                                                  │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                          ▲                    ▲                      │
│                          │                    │                      │
│                    Port 8000            Port 10260                   │
│                          │                    │                      │
└──────────────────────────┼────────────────────┼──────────────────────┘
                           │                    │
                           ▼                    ▼
                    ┌────────────┐      ┌─────────────┐
                    │  Browser   │      │  mongosh    │
                    │  (Swagger) │      │  (CLI)      │
                    └────────────┘      └─────────────┘
```

---

## Component Details

### 1. **VS Code Editor**
Your main development interface with three key tools:

#### Python Code Editor
- Edit FastAPI routes, models, schemas
- Syntax highlighting, IntelliSense
- Integrated debugging

#### MongoDB Playground
- `.mongodb` files with syntax highlighting
- Run queries with `Ctrl+Shift+R`
- Auto-complete for MongoDB commands
- Results displayed inline

#### DocumentDB Extension
- Visual database browser (Tree/Table/JSON views)
- Query editor with IntelliSense
- Import/Export functionality
- Live data updates

---

### 2. **FastAPI Backend Container**

```
┌─────────────────────────────────────────┐
│         FastAPI Backend                 │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  app/main.py                      │ │
│  │  - FastAPI application            │ │
│  │  - CORS middleware                │ │
│  │  - Exception handlers             │ │
│  │  - Health checks                  │ │
│  └───────────────────────────────────┘ │
│                 │                       │
│  ┌───────────────────────────────────┐ │
│  │  app/routers/                     │ │
│  │  ├── products.py  (7 endpoints)   │ │
│  │  ├── customers.py (5 endpoints)   │ │
│  │  └── orders.py    (7 endpoints)   │ │
│  └───────────────────────────────────┘ │
│                 │                       │
│  ┌───────────────────────────────────┐ │
│  │  app/models/                      │ │
│  │  ├── Product  (Beanie Document)   │ │
│  │  ├── Customer (Beanie Document)   │ │
│  │  └── Order    (Beanie Document)   │ │
│  └───────────────────────────────────┘ │
│                 │                       │
│  ┌───────────────────────────────────┐ │
│  │  app/schemas/                     │ │
│  │  - Request/Response models        │ │
│  │  - Pydantic validation            │ │
│  └───────────────────────────────────┘ │
│                 │                       │
│  ┌───────────────────────────────────┐ │
│  │  Libraries                        │ │
│  │  ├── Beanie (ODM)                 │ │
│  │  ├── Motor (Async Driver)         │ │
│  │  ├── Pydantic (Validation)        │ │
│  │  └── Uvicorn (ASGI Server)        │ │
│  └───────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
         │
         ▼ (MongoDB Wire Protocol)
```

---

### 3. **DocumentDB Container**

```
┌─────────────────────────────────────────┐
│         DocumentDB Server               │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  MongoDB Wire Protocol (v4.2-8.0) │ │
│  │  - Listens on port 10260          │ │
│  │  - TLS encryption                 │ │
│  │  - SCRAM-SHA-256 auth             │ │
│  └───────────────────────────────────┘ │
│                 │                       │
│  ┌───────────────────────────────────┐ │
│  │  PostgreSQL Backend               │ │
│  │  - Stores MongoDB documents       │ │
│  │  - JSONB data type                │ │
│  │  - Full ACID transactions         │ │
│  └───────────────────────────────────┘ │
│                 │                       │
│  ┌───────────────────────────────────┐ │
│  │  Collections                      │ │
│  │  ├── products (15 docs)           │ │
│  │  ├── customers (10 docs)          │ │
│  │  └── orders (variable)            │ │
│  └───────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### Create Product Flow

```
┌─────────┐                 ┌─────────────┐                 ┌─────────────┐
│ Browser │                 │   FastAPI   │                 │ DocumentDB  │
│ Client  │                 │   Backend   │                 │   Server    │
└────┬────┘                 └──────┬──────┘                 └──────┬──────┘
     │                             │                                │
     │ POST /api/v1/products       │                                │
     │ {name, price, category...}  │                                │
     ├────────────────────────────►│                                │
     │                             │                                │
     │                             │ 1. Validate with Pydantic      │
     │                             │    schema                      │
     │                             │                                │
     │                             │ 2. Create Beanie model         │
     │                             │    instance                    │
     │                             │                                │
     │                             │ 3. Insert document             │
     │                             ├───────────────────────────────►│
     │                             │                                │
     │                             │                                │ 4. Store in
     │                             │                                │    PostgreSQL
     │                             │                                │    as JSONB
     │                             │                                │
     │                             │ 5. Return inserted document    │
     │                             │◄───────────────────────────────┤
     │                             │    with _id                    │
     │                             │                                │
     │ 6. HTTP 201 Created         │                                │
     │    {_id, name, price...}    │                                │
     │◄────────────────────────────┤                                │
     │                             │                                │
```

### Query Products Flow

```
┌──────────┐              ┌─────────────┐              ┌─────────────┐
│ VS Code  │              │ DocumentDB  │              │ DocumentDB  │
│Extension │              │  Extension  │              │   Server    │
└────┬─────┘              └──────┬──────┘              └──────┬──────┘
     │                           │                             │
     │ 1. User enters query:     │                             │
     │    {category: "Electronics"}                            │
     │                           │                             │
     │ 2. Execute query          │                             │
     ├──────────────────────────►│                             │
     │                           │                             │
     │                           │ 3. Send to DocumentDB       │
     │                           ├────────────────────────────►│
     │                           │                             │
     │                           │                             │ 4. Query
     │                           │                             │    PostgreSQL
     │                           │                             │    JSONB
     │                           │                             │
     │                           │ 5. Return matching docs     │
     │                           │◄────────────────────────────┤
     │                           │                             │
     │ 6. Display in Table/Tree  │                             │
     │    /JSON view             │                             │
     │◄──────────────────────────┤                             │
     │                           │                             │
```

---

## Network Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Docker Network: app-network            │
│                                                            │
│  ┌─────────────────────┐         ┌──────────────────────┐│
│  │   backend:8000      │         │  documentdb:10260    ││
│  │   (Container Name)  │────────►│  (Container Name)    ││
│  └─────────────────────┘         └──────────────────────┘│
│           ▲                                  ▲            │
│           │                                  │            │
└───────────┼──────────────────────────────────┼────────────┘
            │                                  │
    ┌───────┴──────────┐           ┌──────────┴────────┐
    │ localhost:8000   │           │ localhost:10260   │
    │ (Host Port)      │           │ (Host Port)       │
    └──────────────────┘           └───────────────────┘
```

**Key Points**:
- Containers communicate via service names (`documentdb:10260`)
- Host access via localhost and mapped ports
- Network isolation for security
- Bridge driver for container-to-container communication

---

## Storage Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Volume: documentdb-data            │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │               PostgreSQL Data Directory                 │ │
│  │                                                          │ │
│  │  ┌────────────┐  ┌─────────────┐  ┌─────────────────┐ │ │
│  │  │ System DBs │  │ DocumentDB  │  │ WAL & Temp      │ │ │
│  │  │ (postgres, │  │ Collections │  │ Files           │ │ │
│  │  │  template) │  │ (JSONB)     │  │                 │ │ │
│  │  └────────────┘  └─────────────┘  └─────────────────┘ │ │
│  │                                                          │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Persisted on host
                            ▼
              /var/lib/docker/volumes/documentdb-data/...
```

**Persistence**:
- Data survives container restarts
- Can be backed up/restored
- Removed only with `docker-compose down -v`

---

## API Structure

```
http://localhost:8000
│
├── /health                        GET  - Health check
│
├── /docs                          GET  - Swagger UI
├── /redoc                         GET  - ReDoc UI
├── /openapi.json                  GET  - OpenAPI schema
│
└── /api/v1/
    │
    ├── /products
    │   ├── GET     /              - List all products
    │   ├── POST    /              - Create product
    │   ├── GET     /{id}          - Get product by ID
    │   ├── PUT     /{id}          - Update product
    │   ├── DELETE  /{id}          - Delete product
    │   └── GET     /search        - Search products
    │       └── ?name=query&category=Electronics
    │
    ├── /customers
    │   ├── GET     /              - List all customers
    │   ├── POST    /              - Create customer
    │   ├── GET     /{email}       - Get customer by email
    │   ├── PUT     /{email}       - Update customer
    │   └── DELETE  /{email}       - Delete customer
    │
    └── /orders
        ├── GET     /              - List all orders
        ├── POST    /              - Create order
        ├── GET     /{id}          - Get order by ID
        ├── PUT     /{id}/status   - Update order status
        └── GET     /customer/{email} - Get customer orders
```

---

## Database Schema

```
ecommerce (Database)
│
├── products (Collection)
│   └── Document Schema:
│       {
│         "_id": ObjectId,
│         "name": String,
│         "description": String,
│         "price": Decimal,
│         "category": String,
│         "sku": String (unique),
│         "stock_quantity": Integer,
│         "tags": [String],
│         "created_at": DateTime,
│         "updated_at": DateTime
│       }
│       Indexes:
│       - category (ascending)
│       - sku (unique)
│
├── customers (Collection)
│   └── Document Schema:
│       {
│         "_id": ObjectId,
│         "email": String (unique),
│         "first_name": String,
│         "last_name": String,
│         "phone": String,
│         "address": {
│           "street": String,
│           "city": String,
│           "state": String,
│           "postal_code": String,
│           "country": String
│         },
│         "is_active": Boolean,
│         "created_at": DateTime,
│         "updated_at": DateTime
│       }
│       Indexes:
│       - email (unique)
│
└── orders (Collection)
    └── Document Schema:
        {
          "_id": ObjectId,
          "customer_email": String,
          "items": [
            {
              "product_id": ObjectId,
              "product_name": String,
              "quantity": Integer,
              "price": Decimal,
              "subtotal": Decimal
            }
          ],
          "total_amount": Decimal,
          "status": Enum["pending","processing","shipped","delivered","cancelled"],
          "shipping_address": {
            "street": String,
            "city": String,
            "state": String,
            "postal_code": String,
            "country": String
          },
          "created_at": DateTime,
          "updated_at": DateTime,
          "shipped_at": DateTime?,
          "delivered_at": DateTime?
        }
        Indexes:
        - customer_email (ascending)
        - status (ascending)
```

---

## Technology Stack Details

| Layer | Technology | Purpose |
|-------|------------|---------|
| **API Framework** | FastAPI 0.115.0 | Modern async Python web framework |
| **ASGI Server** | Uvicorn | High-performance async server |
| **ODM** | Beanie 1.26.0 | Async MongoDB ODM with Pydantic |
| **Validation** | Pydantic 2.x | Data validation and settings |
| **Database Driver** | Motor 3.6.0 | Async MongoDB driver |
| **Database** | DocumentDB 0.103-0 | MongoDB-compatible on PostgreSQL |
| **Containerization** | Docker 24.0+ | Application containerization |
| **Orchestration** | Docker Compose 3.8 | Multi-container management |
| **Testing** | pytest 8.3+ | Testing framework |
| **Code Quality** | Black, isort | Code formatting |

---

## Development Workflow

```
┌──────────────────────────────────────────────────────────────┐
│                    Development Cycle                          │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │   1. Write Code     │
                   │   (VS Code)         │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ 2. Hot Reload       │
                   │ (Uvicorn --reload)  │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ 3. Test in Browser  │
                   │ (Swagger UI)        │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ 4. Query Data       │
                   │ (DocumentDB Ext)    │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ 5. Run Tests        │
                   │ (pytest)            │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ 6. Commit Changes   │
                   │ (Git)               │
                   └─────────────────────┘
```

---

## Deployment Architecture (Future)

```
┌────────────────────────────────────────────────────────┐
│                    Azure Cloud                          │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Azure Container Apps (FastAPI)           │  │
│  │         - Auto-scaling                           │  │
│  │         - HTTPS endpoints                        │  │
│  └─────────────────────┬────────────────────────────┘  │
│                        │                                │
│                        ▼                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │    Azure Cosmos DB for MongoDB (DocumentDB)      │  │
│  │    - Multi-region replication                    │  │
│  │    - Automatic backups                           │  │
│  │    - 99.99% SLA                                  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└────────────────────────────────────────────────────────┘
```

---

## Security Architecture

```
┌───────────────────────────────────────────────────────────┐
│                    Security Layers                         │
├───────────────────────────────────────────────────────────┤
│                                                            │
│  1. Network Security                                       │
│     ├── Docker network isolation                          │
│     ├── Port mapping controls                             │
│     └── CORS configuration                                │
│                                                            │
│  2. Authentication & Authorization                         │
│     ├── DocumentDB: SCRAM-SHA-256                         │
│     ├── TLS encryption                                    │
│     └── Environment variable secrets                      │
│                                                            │
│  3. Data Validation                                        │
│     ├── Pydantic schemas                                  │
│     ├── Type checking                                     │
│     └── Input sanitization                                │
│                                                            │
│  4. Application Security                                   │
│     ├── Exception handling                                │
│     ├── Request validation                                │
│     └── Error message sanitization                        │
│                                                            │
└───────────────────────────────────────────────────────────┘
```

---

This architecture is designed for:
- ✅ **Local Development** - Fast iteration with hot reload
- ✅ **Learning** - Clear separation of concerns
- ✅ **Testing** - Isolated containers for reliable tests
- ✅ **Scalability** - Ready to deploy to cloud platforms
- ✅ **Maintainability** - Standard patterns and conventions
