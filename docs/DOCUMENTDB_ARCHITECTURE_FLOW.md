# DocumentDB Architecture Flow

## How DocumentDB Processes MongoDB Operations

Let's walk through how DocumentDB handles BSON data and translates MongoDB-style operations into actual PostgreSQL queries.

### Visual Architecture Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  USER / APPLICATION                                             │
│  Submits MongoDB-style operation (insert, update, query)       │
│  Using standard MongoDB driver                                  │
│                                                                  │
│  Example: db.products.insertMany([{...}])                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ MongoDB Wire Protocol (Port 10260)
                         │ BSON-formatted commands
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  GATEWAY COMPONENT                                              │
│  - Receives MongoDB operations                                  │
│  - Translates into PostgreSQL-compatible instructions          │
│  - Handles connection pooling and authentication               │
│  - Routes to appropriate DocumentDB API layer                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Translated operations
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  DOCUMENTDB API LAYER (PostgreSQL Extension)                   │
│  - Handles document-level CRUD operations                       │
│  - Processes MongoDB query operators ($match, $group, etc.)    │
│  - Manages collection operations                               │
│  - Implements MongoDB index commands                           │
│  - Coordinates with documentdb_core for BSON handling          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ BSON document operations
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  DOCUMENTDB_CORE LAYER (PostgreSQL Extension)                  │
│  - BSON parsing and serialization                              │
│  - Type mapping (BSON ↔ PostgreSQL types)                      │
│  - Document validation and schema enforcement                  │
│  - BSON-specific operators and functions                       │
│  - Converts BSON documents to JSONB storage format             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ SQL queries with JSONB data
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  POSTGRESQL 16 (Core Database Engine)                          │
│  - Executes query plans                                         │
│  - Handles transactions (ACID compliance)                       │
│  - Manages storage and indexing                                │
│  - Ensures durability and scale                                │
│  - Leverages extensions: pgvector, PostGIS                     │
│                                                                  │
│  Physical Storage:                                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Table: products                                          │  │
│  │ ┌──────────┬───────────────────────────────────────────┐│  │
│  │ │ _id      │ document (JSONB)                         ││  │
│  │ ├──────────┼───────────────────────────────────────────┤│  │
│  │ │ ObjectId │ {"name":"Mouse","price":29.99,...}       ││  │
│  │ │ ObjectId │ {"name":"Keyboard","price":79.99,...}    ││  │
│  │ └──────────┴───────────────────────────────────────────┘│  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Indexes: B-tree, GiST, HNSW (vector), 2dsphere (geospatial)  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Architectural Components

### 1. **Gateway Component**
- **Role**: Entry point for MongoDB operations
- **Responsibilities**:
  - Receives MongoDB wire protocol commands
  - Authenticates clients (SCRAM-SHA-256)
  - Translates MongoDB commands to PostgreSQL-compatible instructions
  - Routes operations to DocumentDB API layer

### 2. **DocumentDB API Layer**
- **Role**: MongoDB compatibility layer
- **Responsibilities**:
  - Implements MongoDB CRUD operations
  - Processes MongoDB query language ($match, $group, $project, etc.)
  - Handles aggregation pipelines
  - Manages collections (create, drop, list)
  - Implements MongoDB indexing commands (2dsphere, vector indexes)

### 3. **DocumentDB_Core Layer**
- **Role**: BSON and document model engine
- **Responsibilities**:
  - BSON parsing and serialization
  - Type mapping between BSON and PostgreSQL types
  - Document validation
  - BSON-specific operators
  - Converts BSON to JSONB for storage

### 4. **PostgreSQL 16**
- **Role**: Core database engine
- **Responsibilities**:
  - Query execution and optimization
  - Transaction management (ACID)
  - Storage management
  - Index management (B-tree, GiST, HNSW, etc.)
  - Extensions: pgvector (vector search), PostGIS (geospatial)

## Example: Insert Operation Flow

### User submits:
```javascript
db.products.insertOne({
  name: "Wireless Mouse",
  price: 29.99,
  category: "Electronics",
  tags: ["wireless", "bluetooth"]
})
```

### Gateway translates and routes to DocumentDB API Layer

### DocumentDB API Layer processes the insert command

### DocumentDB_Core Layer converts BSON to JSONB:
```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "name": "Wireless Mouse",
  "price": NumberDecimal("29.99"),
  "category": "Electronics",
  "tags": ["wireless", "bluetooth"]
}
```

### PostgreSQL executes:
```sql
INSERT INTO products (document)
VALUES ('{
  "_id": {"$oid": "507f1f77bcf86cd799439011"},
  "name": "Wireless Mouse",
  "price": {"$numberDecimal": "29.99"},
  "category": "Electronics",
  "tags": ["wireless", "bluetooth"]
}'::jsonb);
```

### Result flows back through layers to client

## The Advantage

**So even though the client sees MongoDB, under the hood, it's a clean stack that leverages PostgreSQL's battle-tested core — with full BSON and document model support layered on top.**

### Benefits of This Architecture:

✅ **Familiar MongoDB API**: Developers use MongoDB drivers and commands  
✅ **PostgreSQL Reliability**: ACID transactions, mature backup/recovery  
✅ **Advanced Features**: pgvector (AI embeddings), PostGIS (geospatial)  
✅ **Enterprise Scale**: PostgreSQL's proven performance and scaling  
✅ **Operational Excellence**: Standard PostgreSQL tooling and monitoring  

### Unique Capabilities:

- **Vector Search**: Native HNSW/IVF indexing via pgvector (up to 4000 dimensions)
- **Geospatial Queries**: Advanced PostGIS integration for location-based features
- **Full-Text Search**: PostgreSQL's mature text search capabilities
- **Complex Aggregations**: Leverage PostgreSQL's query optimizer for analytics
- **ACID Guarantees**: Built-in transactional support without replica sets

## For More Details

- See `FASTAPI_ADVANCED_WALKTHROUGH.md` for hands-on examples
- See `FASTAPI_ADVANCED_WALKTHROUGH_PART3.md` for DocumentDB superpowers (vector search, geospatial, aggregations)
