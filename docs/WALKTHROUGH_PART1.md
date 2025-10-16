# FastAPI + DocumentDB: Building Modern, Intelligent APIs
## Part 1: Foundation

> **Prerequisites**: Basic Python knowledge, understanding of REST APIs, Docker installed

**Duration**: 1 hour  
**Difficulty**: Beginner to Intermediate

---

## 📚 Complete Walkthrough Navigation

- **Part 1: Foundation** ← You are here
- [Part 2: FastAPI Deep Dive](WALKTHROUGH_PART2.md)
- [Part 3: DocumentDB Superpowers](WALKTHROUGH_PART3.md)
- [Part 4: Production Ready](WALKTHROUGH_PART4.md)

---

## Step 0: Clone the Repository

```powershell
# Clone the repository
git clone https://github.com/documentdb/fast-api-sample.git
cd fast-api-sample

# Open in VS Code
code .
```

## Step 1: Launch DocumentDB Container

```powershell
# Pull and start DocumentDB
docker pull ghcr.io/documentdb/documentdb/documentdb-local:latest
docker tag ghcr.io/documentdb/documentdb/documentdb-local:latest documentdb

# Run DocumentDB container
docker run -dt -p 10260:10260 --name documentdb-container documentdb --username admin --password password123
```

**Verify it's running:**
```powershell
docker ps
# You should see documentdb-container running on port 10260
```

## Step 2: Load E-commerce Data

Use the DocumentDB VS Code extension using your connection string:
```powershell
mongosh "mongodb://USERNAME:PASSWORD@localhost:10260/?authMechanism=SCRAM-SHA-256&tls=true&tlsAllowInvalidCertificates=true"
```

- Click on the drop-down next to your local connection and select "Create Database..."
- Enter database name and confirm (suggested: ecommerce)
- Click on the drop-down next to your created database and select "Create Collection..."
- Create your collections, `products` and `customers` and confirm.

Import data to DocumentDB
- For each collection, click the `Import` button on the top-right corner. 
- Import the `/scripts/sample_customers.json` file in the `customers` collection and `/scripts/sample_products.json` file in the `products` collection.

## Step 3: Install Dependencies & Connect FastAPI to DocumentDB

```bash
cp .env.example .env
```

In the `.env` file, add your connection string, database name, and DocumentDB credentials.

Afterwards, install the requirements needed for the data to migrate to the frontend.

```bash
cd backend
pip install -r requirements.txt
```

## Step 4: Build and Run the Program!

```bash
cd ..
docker-compose up -d
```

**Test the API:**
- Open sample: http://localhost
- Open browser: http://localhost:8000/docs
- Test the health endpoint: http://localhost:8000/health

✅ **Checkpoint**: You should see the Swagger UI with all endpoints documented.

---

## 🎯 Part 1 Complete!

**What you've accomplished:**
- ✅ Set up DocumentDB container locally
- ✅ Loaded sample e-commerce data
- ✅ Configured FastAPI application
- ✅ Verified the API is running with Swagger UI

**What you've learned:**
- How to run DocumentDB in Docker
- How to connect FastAPI to DocumentDB
- How to use the DocumentDB VS Code extension
- Basic API testing with Swagger UI

**Next Steps:**
Continue to [Part 2: FastAPI Deep Dive](WALKTHROUGH_PART2.md) to learn about:
- Async/await patterns with database operations
- Request lifecycle and performance
- Pydantic + Beanie integration
- Building a complete Reviews feature from scratch
