# DocumentDB Extension Quick Reference

## 🚀 Quick Start

### Installation
```bash
code --install-extension ms-azuretools.vscode-documentdb
```

### Connection String (Local Development)
```
## Connection String

**Local Development**:
```
mongodb://admin:password123@localhost:10260/?tls=true&tlsAllowInvalidCertificates=true&authMechanism=SCRAM-SHA-256
```

## 🎯 Common Tasks

### Connecting
1. Click DocumentDB icon in Activity Bar
2. Click "+" → "Connection String"
3. Paste connection string
4. Name connection → Connect

### Viewing Data
- **Table View**: Spreadsheet-like browsing
- **Tree View**: Hierarchical exploration
- **JSON View**: Raw document inspection

### Querying

#### Simple Queries
```javascript
// All documents
{}

// Filter by field
{ category: "Electronics" }

// Comparison operators
{ price: { $gt: 100 } }
{ stock_quantity: { $lte: 10 } }

// Text search
{ name: { $regex: "wireless", $options: "i" } }

// Multiple conditions
{ category: "Electronics", price: { $lt: 200 } }
```

#### Advanced Queries
```javascript
// OR condition
{ $or: [{ category: "Electronics" }, { category: "Furniture" }] }

// IN operator
{ status: { $in: ["pending", "processing"] } }

// Array operations
{ tags: { $in: ["wireless"] } }

// Nested field query
{ "address.city": "San Francisco" }

// Date range
{ created_at: { $gte: ISODate("2025-01-01"), $lt: ISODate("2025-12-31") } }
```

### Aggregation Pipelines (in .mongodb files)

```javascript
use('documentdb');

// Total revenue by order status
db.orders.aggregate([
  { $group: { 
      _id: "$status", 
      total: { $sum: "$total_amount" },
      count: { $count: {} }
  }},
  { $sort: { total: -1 } }
]);

// Top products
db.orders.aggregate([
  { $unwind: "$items" },
  { $group: { 
      _id: "$items.product_name",
      quantity: { $sum: "$items.quantity" }
  }},
  { $sort: { quantity: -1 } },
  { $limit: 10 }
]);

// Customer order summary
db.orders.aggregate([
  { $group: {
      _id: "$customer_email",
      totalOrders: { $count: {} },
      totalSpent: { $sum: "$total_amount" },
      avgOrderValue: { $avg: "$total_amount" }
  }},
  { $sort: { totalSpent: -1 } }
]);
```

## ⌨️ Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Open Extensions | `Ctrl+Shift+X` / `Cmd+Shift+X` |
| Run Query (in .mongodb file) | `Ctrl+Shift+R` |
| Save Document | `Ctrl+S` / `Cmd+S` |
| Refresh Connection | Right-click → Refresh |

## 🔧 Context Menu Actions

### On Connection
- ✏️ **Rename Connection**
- 🔄 **Refresh**
- 🗑️ **Remove Connection**
- 🔌 **Update Credentials**
- 🛠️ **Launch Shell** (if mongosh installed)

### On Database
- ➕ **Create Collection**
- 🗑️ **Drop Database** ⚠️
- 🔄 **Refresh**

### On Collection
- 📄 **New Document**
- 📥 **Import Documents**
- 📤 **Export Collection**
- 🔍 **Open Collection View**
- 🗑️ **Drop Collection** ⚠️

### On Document
- ✏️ **Edit Document**
- 📋 **Copy Document**
- 🗑️ **Delete Document** ⚠️

## 📊 View Modes

### Table View
- Quick data scanning
- Sortable columns
- Filter by column values
- Pagination controls

### Tree View
- Hierarchical data exploration
- Expand/collapse nested objects
- Array visualization
- Copy path or value

### JSON View
- Full document structure
- Syntax highlighting
- Edit and save
- Copy JSON

## 🔍 Query Editor Features

### Auto-complete Support
- MongoDB operators: `$gt`, `$lt`, `$in`, `$regex`, etc.
- Field names from your schema
- Collection names
- Database names

### Syntax Highlighting
- Operators in purple
- Strings in red
- Numbers in green
- Booleans in blue

## 📁 File Types

### .mongodb Files (MongoDB Playground)
Create reusable query scripts:

```javascript
// Connect to database
use('documentdb');

// Query 1
db.products.find({ category: "Electronics" });

// Query 2
db.orders.find({ status: "pending" });

// Aggregation
db.orders.aggregate([
  { $group: { _id: "$status", count: { $sum: 1 } } }
]);
```

Run individual queries with code lens buttons or `Ctrl+Shift+R`.

## 💾 Import/Export

### Export Formats
- **JSON Array**: `[{...}, {...}]`
- **NDJSON**: Newline-delimited JSON
- **Single Document**: `{...}`

### Export Options
- Entire collection
- Query results
- Single document

### Import Requirements
- Valid JSON format
- Array of documents or NDJSON
- Matching schema structure (Beanie will validate)

## 🔒 Connection Security

### Local Development
```
✅ tls=true
✅ tlsAllowInvalidCertificates=true
✅ authMechanism=SCRAM-SHA-256
```

### Production (when deploying)
```
✅ tls=true
❌ tlsAllowInvalidCertificates=false
✅ authMechanism=SCRAM-SHA-256 or X.509
✅ Use strong passwords
✅ Restrict by IP
```

## 🐛 Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Connection timeout | Check Docker: `docker-compose ps` |
| Authentication failed | Verify credentials in `.env` |
| SSL error | Add `tls=true&tlsAllowInvalidCertificates=true` |
| Collections not showing | Right-click connection → Refresh |
| Slow queries | Check indexes, add filters |

## ⚙️ Settings

```json
{
  "documentDB.mongoShell.path": "",
  "documentDB.mongoShell.timeout": 30000,
  "documentDB.mongoShell.batchSize": 50,
  "documentDB.confirmations.confirmationStyle": "Ask",
  "documentDB.userInterface.ShowOperationSummaries": true
}
```

## 🎨 Extension Features Checklist

- ✅ Multiple view modes (Table, Tree, JSON)
- ✅ IntelliSense query editor
- ✅ Import/Export documents
- ✅ Create/Edit/Delete operations
- ✅ Aggregation pipeline support
- ✅ MongoDB Playground (.mongodb files)
- ✅ Index visualization
- ✅ Connection management
- ✅ Service discovery (Azure, Local)
- ✅ Shell integration (mongosh)
- ✅ URL deep linking
- ✅ Pagination controls

## 📚 Resources

- **Documentation**: https://microsoft.github.io/vscode-documentdb/
- **GitHub**: https://github.com/microsoft/vscode-documentdb
- **Marketplace**: https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-documentdb
- **Local Guide**: [docs/DOCUMENTDB_EXTENSION_GUIDE.md](../docs/DOCUMENTDB_EXTENSION_GUIDE.md)

---

**Pro Tip**: Open this workspace file for recommended extensions and pre-configured settings:
```bash
code fastapi-documentdb.code-workspace
```
