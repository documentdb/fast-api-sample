# FastAPI + DocumentDB E-Commerce Workshop

**Build a Modern E-Commerce API with FastAPI and DocumentDB**

Welcome to this hands-on workshop where you'll learn to build a production-ready e-commerce API using FastAPI and DocumentDB. Through progressive modules, you'll master async Python development, database operations, and production deployment patterns.

---

## Learning Path

The workshop follows a progressive learning path with the following modules:

- [Module 0: Prerequisites and Setup](Module-00.md)
- [Module 1: Foundation - Your First API Endpoint](Module-01.md)
- [Module 2: Database Integration with Beanie ODM](Module-02.md)
- [Module 3: Advanced Querying and Filtering](Module-03.md)
- [Module 4: Production Ready - Testing and Deployment](Module-04.md)

---

## What You'll Build

By the end of this workshop, you'll have created:

- **Complete E-Commerce API** with Products, Customers, and Orders
- **Async Database Operations** using Beanie ODM
- **Advanced Query Patterns** with filtering, pagination, and search
- **Production-Ready Application** with tests, Docker, and deployment configs
- **Modern Frontend** integrated with your API

---

## Technologies Covered

- **FastAPI** - Modern, high-performance Python web framework
- **DocumentDB** - MongoDB-compatible document database
- **Beanie ODM** - Async MongoDB ODM built on Pydantic
- **Docker** - Containerization and orchestration
- **React** - Frontend integration
- **Pytest** - Testing framework

---

## Prerequisites

- Basic Python knowledge
- Understanding of REST APIs
- Docker installed
- VS Code (recommended)

---

## Clean Up

If you're done with the workshop or sample application, you can deprovision the containers:

```powershell
# Stop and remove containers
docker-compose down

# Remove DocumentDB container
docker stop documentdb-container
docker rm documentdb-container

# Remove images (optional)
docker rmi documentdb
```

---

**Ready to begin?** Start with [Module 0: Prerequisites and Setup](Module-00.md)
