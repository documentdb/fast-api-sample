# Lab Resources Overview

Quick reference guide for all lab-related files and documentation.

## 📚 Documentation Files

### Main Guides

| File | Purpose | When to Use |
|------|---------|-------------|
| [README.md](../README.md) | Project overview and quick start | First file to read, contains links to everything else |
| [LAB_WALKTHROUGH.md](LAB_WALKTHROUGH.md) | **Complete step-by-step lab guide** | Follow this for the full lab experience (30-45 min) |
| [DOCUMENTDB_EXTENSION_GUIDE.md](DOCUMENTDB_EXTENSION_GUIDE.md) | Comprehensive extension reference | Deep dive into all extension features |
| [EXTENSION_QUICK_REFERENCE.md](EXTENSION_QUICK_REFERENCE.md) | Quick reference card | Quick lookup for commands and queries |

### Supporting Docs

| File | Purpose |
|------|---------|
| [scripts/README.md](../scripts/README.md) | Scripts documentation and workflows |

---

## 🛠️ Setup Scripts

| Script | What It Does | Usage |
|--------|--------------|-------|
| `scripts/setup-lab.ps1` | Automated lab setup and verification | `.\scripts\setup-lab.ps1` |
| `scripts/quickstart.ps1` | Quick full-stack startup | `.\scripts\quickstart.ps1` |
| `scripts/load_sample_data.py` | Load sample data via Python | `python scripts/load_sample_data.py` |

---

## 📊 Sample Data Files

| File | What It Contains | How to Import |
|------|------------------|---------------|
| `scripts/sample_products.json` | 15 sample products | VS Code extension → Right-click collection → Import |
| `scripts/sample_customers.json` | 10 sample customers | VS Code extension → Right-click collection → Import |

---

## 💻 Code Examples

| File | What It Contains | Usage |
|------|------------------|-------|
| `examples/ecommerce-analytics.mongodb` | 30+ ready-to-run MongoDB queries | Open in VS Code → Press Ctrl+Shift+R |

---

## 🎯 Lab Steps - Quick Navigation

### Step 1: Launch DocumentDB
→ See [LAB_WALKTHROUGH.md - Step 1](LAB_WALKTHROUGH.md#step-1-launch-documentdb-container)
- Use `setup-lab.ps1` OR
- Follow official quickstart manually

### Step 2: Load Data with VS Code Extension
→ See [LAB_WALKTHROUGH.md - Step 2](LAB_WALKTHROUGH.md#step-2-load-e-commerce-data-using-vs-code-extension)
- Install extension
- Connect to DocumentDB
- Import `sample_products.json` and `sample_customers.json`
- Explore with Table/Tree/JSON views

### Step 3: Connect FastAPI
→ See [LAB_WALKTHROUGH.md - Step 3](LAB_WALKTHROUGH.md#step-3-connect-fastapi-to-documentdb)
- Configure `.env`
- Start backend with Docker Compose
- Test API endpoints
- Watch live updates in extension

---

## 🔗 Important Connection Info

**DocumentDB Local Development**:
```
Host: localhost:10260
Username: admin
Password: password123

Connection String:
mongodb://admin:password123@localhost:10260/?authMechanism=SCRAM-SHA-256&tls=true&tlsAllowInvalidCertificates=true
```

**FastAPI**:
```
API: http://localhost:8000
Docs: http://localhost:8000/docs
Health: http://localhost:8000/health
```

---

## 🎓 Learning Path

Recommended order for going through the materials:

1. **Start Here**: [README.md](../README.md) - Get project overview
2. **Run Setup**: `.\scripts\setup-lab.ps1` - Automated environment setup
3. **Follow Lab**: [LAB_WALKTHROUGH.md](LAB_WALKTHROUGH.md) - Step-by-step guide (30-45 min)
4. **Deep Dive**: [DOCUMENTDB_EXTENSION_GUIDE.md](DOCUMENTDB_EXTENSION_GUIDE.md) - Learn all extension features
5. **Try Queries**: `examples/ecommerce-analytics.mongodb` - Run 30+ sample queries
6. **Reference**: [EXTENSION_QUICK_REFERENCE.md](EXTENSION_QUICK_REFERENCE.md) - Keep handy for quick lookups

---

## 🔍 Troubleshooting Quick Links

| Problem | Solution Location |
|---------|-------------------|
| Can't connect to DocumentDB | [LAB_WALKTHROUGH.md - Troubleshooting](LAB_WALKTHROUGH.md#documentdb-container-wont-start) |
| Extension won't connect | [LAB_WALKTHROUGH.md - Extension Can't Connect](LAB_WALKTHROUGH.md#extension-cant-connect) |
| Import fails | [scripts/README.md - Import Fails](../scripts/README.md#import-fails-in-vs-code-extension) |
| FastAPI connection issues | [LAB_WALKTHROUGH.md - FastAPI Can't Connect](LAB_WALKTHROUGH.md#fastapi-cant-connect-to-documentdb) |
| Script won't run | [scripts/README.md - Script Won't Run](../scripts/README.md#script-wont-run) |

---

## 📦 VS Code Extension Resources

### Installation
- **Marketplace**: https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-documentdb
- **Command**: `code --install-extension ms-azuretools.vscode-documentdb`
- **Workspace**: Open `fastapi-documentdb.code-workspace` (auto-prompts to install)

### Key Features
- 📊 Table View - Spreadsheet-like browsing
- 🌳 Tree View - Nested document structure
- 📝 JSON View - Raw MongoDB documents
- 🔍 Query Editor - IntelliSense and autocomplete
- 📁 Import/Export - Drag-and-drop JSON files
- 🎮 MongoDB Playground - Reusable `.mongodb` query files

### Quick Actions
| Action | Shortcut |
|--------|----------|
| Focus on Databases | `Ctrl+Shift+P` → "DocumentDB: Focus" |
| Run Playground Query | `Ctrl+Shift+R` |
| Execute Query | `Ctrl+Enter` |
| Refresh Collection | Right-click → Refresh |

---

## 🎯 Success Checklist

By the end of the lab, you should have:

- [x] DocumentDB running on localhost:10260
- [x] VS Code extension connected to DocumentDB
- [x] Sample data loaded (products, customers)
- [x] FastAPI backend running
- [x] Successfully tested CRUD operations
- [x] Explored data in Table/Tree/JSON views
- [x] Run queries in MongoDB Playground
- [x] Verified end-to-end workflow (create customer → create order)

---

## 📖 External References

### Official Documentation
- [DocumentDB Quickstart](https://seesharprun-documentdb-prototype.github.io/docs/quickstart/mongodb-shell)
- [DocumentDB GitHub Repo](https://github.com/microsoft/vscode-documentdb)
- [VS Code Extension Blog](https://techcommunity.microsoft.com/blog/DocumentDBBlog/announcing-documentdb-for-vs-code/4383994)

### Framework Docs
- [FastAPI](https://fastapi.tiangolo.com/)
- [Beanie ODM](https://beanie-odm.dev/)
- [Pydantic](https://docs.pydantic.dev/)
- [Docker Compose](https://docs.docker.com/compose/)

---

## 💡 Pro Tips

1. **Use the Workspace File**: Open `fastapi-documentdb.code-workspace` to get:
   - Extension recommendations auto-installed
   - Pre-configured settings
   - Launch configurations for debugging
   - Task definitions for common operations

2. **MongoDB Playground for Analytics**: Create `.mongodb` files for:
   - Reusable analytics queries
   - Team collaboration (check into Git)
   - Documentation of common queries

3. **Export Before Experimenting**: 
   - Right-click collection → Export
   - Experiment with queries/updates
   - Re-import if needed

4. **Watch Mode**: Enable auto-refresh in extension settings to see changes in real-time

5. **Use Table View for Data Entry**: When manually adding documents, Table view is fastest for seeing results

---

## 🤝 Getting Help

If you get stuck:

1. Check the [Troubleshooting section](LAB_WALKTHROUGH.md#troubleshooting)
2. Review [scripts/README.md](../scripts/README.md) for common workflows
3. Look at [EXTENSION_QUICK_REFERENCE.md](EXTENSION_QUICK_REFERENCE.md) for quick syntax
4. Check Docker logs: `docker-compose logs -f`
5. Verify connection with mongosh: `mongosh "mongodb://admin:password123@localhost:10260/..."`

---

## 📅 Lab Timeline

Estimated time breakdown:

- Setup (Step 1): **5-10 minutes**
  - Docker setup
  - Container verification

- Data Loading (Step 2): **10-15 minutes**
  - Extension installation
  - Connection setup
  - Data import
  - Exploration

- FastAPI Integration (Step 3): **10-15 minutes**
  - Environment config
  - Backend startup
  - API testing

- Exploration & Experiments: **5-10 minutes**
  - MongoDB Playground queries
  - End-to-end workflow
  - Analytics

**Total: 30-45 minutes**

---

## 🎉 What's Next?

After completing the lab:

1. **Customize the Data Model**: Add new fields, collections, or relationships
2. **Build New Endpoints**: Implement search, recommendations, or analytics
3. **Run the Test Suite**: `pytest backend/tests/ -v`
4. **Deploy to Production**: Explore deployment options (Azure, AWS, etc.)
5. **Add Advanced Features**: Vector search, change streams, aggregation pipelines

Happy coding! 🚀
