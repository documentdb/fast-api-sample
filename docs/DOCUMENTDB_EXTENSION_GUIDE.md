# Using the DocumentDB for VS Code Extension

This guide will help you explore and manage your DocumentDB database using the powerful **DocumentDB for VS Code** extension - a dedicated tool that brings your MongoDB-compatible databases right into your editor.

## Table of Contents

- [Why Use the Extension?](#why-use-the-extension)
- [Installation](#installation)
- [Connecting to Your Local Database](#connecting-to-your-local-database)
- [Extension Features](#extension-features)
- [Working with Data](#working-with-data)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

## Why Use the Extension?

The DocumentDB for VS Code extension provides:

✨ **Seamless Integration**: Browse, query, and manage databases without leaving VS Code  
🔍 **Multiple View Modes**: Table, Tree, and JSON views for different data perspectives  
⚡ **Smart Query Editor**: Auto-complete, syntax highlighting, and field suggestions  
📊 **Import/Export**: Quick data migration with JSON file support  
🎯 **Service Discovery**: Auto-detect DocumentDB and MongoDB instances across environments  

## Installation

### Option 1: VS Code Marketplace (Recommended)

1. Open VS Code
2. Click the **Extensions** icon in the sidebar (or press `Ctrl+Shift+X` / `Cmd+Shift+X`)
3. Search for **"DocumentDB for VS Code"**
4. Click **Install** on the extension by Microsoft (`ms-azuretools.vscode-documentdb`)
5. Reload VS Code if prompted

### Option 2: Direct Install

Install from the marketplace link:
- [DocumentDB for VS Code Extension](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-documentdb)

### Option 3: Command Line

```bash
code --install-extension ms-azuretools.vscode-documentdb
```

## Connecting to Your Local Database

Once your e-commerce API is running via Docker Compose, you can connect the extension to your local DocumentDB instance.

### Step 1: Ensure Services Are Running

```powershell
# Start your services
docker-compose up -d

# Verify DocumentDB is running
docker-compose ps documentdb
```

### Step 2: Open the Extension

1. Look for the **DocumentDB** icon in the VS Code Activity Bar (left sidebar)
2. Click it to open the DocumentDB view
3. You'll see two main sections:
   - **Connections View**: Your saved database connections
   - **Service Discovery View**: Auto-detected databases

### Step 3: Add a Connection

#### Method 1: Using Connection String (Recommended for Local Development)

1. Click the **"+"** button or **"Add New Connection"**
2. Select **"Connection String"** from the navigation bar
3. Paste your local DocumentDB connection string:

   ```
   mongodb://admin:password123@localhost:10260/?tls=true&tlsAllowInvalidCertificates=true&authMechanism=SCRAM-SHA-256
   ```

4. **Important**: The connection string format is:
   - **Protocol**: `mongodb://`
   - **Username**: `admin` (default from docker-compose.yml)
   - **Password**: `password123` (default from docker-compose.yml)
   - **Host**: `localhost:10260` (DocumentDB default port)
   - **Required Parameters**:
     - `tls=true` - Enable TLS/SSL
     - `tlsAllowInvalidCertificates=true` - Accept self-signed certificates (local dev only)
     - `authMechanism=SCRAM-SHA-256` - Use SCRAM-SHA-256 authentication

5. Give your connection a friendly name (e.g., "E-commerce Local Dev")
6. Click **Connect**

#### Method 2: Using Service Discovery

The extension can automatically discover local DocumentDB instances:

1. Navigate to the **Service Discovery View**
2. Look for your local connection under detected services
3. Click the **"Save"** icon to add it to your Connections View

### Step 4: Explore Your Database

1. In the **Connections View**, expand your connection
2. You'll see databases created by your FastAPI application:
   - `documentdb` (default database name from `.env`)
3. Expand to see collections:
   - `products`
   - `customers`
   - `orders`

## Extension Features

### 🗂️ Database Explorer

**Tree View Navigation**:
- Connection → Databases → Collections → Documents hierarchy
- Right-click for context menus with actions
- Drag and drop support for organizing connections

**Multiple View Modes**:
- **Table View**: Spreadsheet-like view for quick data scanning
- **Tree View**: Hierarchical document structure exploration
- **JSON View**: Raw document inspection with syntax highlighting

### 🔍 Query Editor

The extension provides a powerful query interface with IntelliSense:

**Features**:
- Syntax highlighting for MongoDB queries
- Auto-complete for operators (`$gt`, `$regex`, `$in`, etc.)
- Field name suggestions based on your schema
- Query history for reusing previous queries

**Example Queries**:

```javascript
// Find all products in Electronics category
{ category: "Electronics" }

// Find products with price greater than $100
{ price: { $gt: 100 } }

// Find orders with "pending" status
{ status: "pending" }

// Text search in product names
{ name: { $regex: "wireless", $options: "i" } }

// Find products with low stock
{ stock_quantity: { $lt: 10 } }
```

### 📥 Import & Export

**Exporting Data**:
1. Right-click on a collection
2. Select **"Export"**
3. Choose what to export:
   - Entire collection
   - Current query results
   - Individual documents
4. Specify output JSON file location

**Importing Data**:
1. Right-click on a collection
2. Select **"Import"**
3. Choose your JSON file
4. Confirm import

**Supported Formats**:
- JSON array of documents
- NDJSON (newline-delimited JSON)
- Single document JSON

### 📊 Document Operations

**Create Documents**:
1. Right-click on a collection → **"New Document"**
2. Edit the template JSON
3. Save to insert

**Edit Documents**:
1. Click on a document to open it
2. Modify in JSON view
3. Press `Ctrl+S` (or `Cmd+S`) to save changes

**Delete Documents**:
1. Right-click on a document
2. Select **"Delete Document"**
3. Confirm deletion

### 🎯 Collection Management

**Create Collections**:
1. Right-click on a database → **"Create Collection"**
2. Enter collection name
3. Optionally configure options (validation, capped collection, etc.)

**Drop Collections**:
1. Right-click on a collection → **"Drop Collection"**
2. Confirm deletion ⚠️ This cannot be undone!

**View Indexes**:
1. Expand collection
2. See **Indexes** node showing all collection indexes
3. Review index definitions created by Beanie

## Working with Data

### Viewing Your E-commerce Data

After loading sample data or creating records via the API, you can explore them:

**Products Collection**:
```javascript
// View all products
{}

// Filter by category
{ category: "Electronics" }

// Find products on sale (assuming you add a sale field)
{ price: { $lt: 100 } }
```

**Orders Collection**:
```javascript
// View recent orders (sorted by created_at)
// Use the sort button in the query editor

// Find orders for a specific customer
{ customer_email: "alice.smith@example.com" }

// Find pending orders
{ status: "pending" }
```

**Customers Collection**:
```javascript
// Find customers by location
{ "address.city": "San Francisco" }

// Search by name
{ first_name: { $regex: "alice", $options: "i" } }
```

### Pagination

The extension automatically paginates results:
- Default: 20 documents per page
- Navigate with **Previous** / **Next** buttons
- Adjust page size in settings: `documentDB.mongoShell.batchSize`

### Aggregation Pipelines

For complex queries, use the **MongoDB Playground**:

1. Create a new `.mongodb` file in VS Code
2. Write aggregation queries:

```javascript
use('documentdb');

// Total revenue by order status
db.orders.aggregate([
  {
    $group: {
      _id: "$status",
      totalRevenue: { $sum: "$total_amount" },
      orderCount: { $count: {} }
    }
  },
  {
    $sort: { totalRevenue: -1 }
  }
]);

// Top-selling products
db.orders.aggregate([
  { $unwind: "$items" },
  {
    $group: {
      _id: "$items.product_name",
      totalQuantity: { $sum: "$items.quantity" },
      totalRevenue: { $sum: "$items.subtotal" }
    }
  },
  { $sort: { totalQuantity: -1 } },
  { $limit: 10 }
]);
```

3. Click **"Execute"** to run the pipeline

## Advanced Usage

### URL-Based Activation

You can create deep links that open specific connections:

```
vscode://ms-azuretools.vscode-documentdb?connectionString=<ENCODED_CONNECTION_STRING>&database=documentdb&collection=products
```

This feature enables:
- Quick bookmarks to frequently-used collections
- Team collaboration via shared links
- Integration with external tools

**How to construct URLs**: See the [extension documentation](https://microsoft.github.io/vscode-documentdb/manual/how-to-construct-url.html)

### MongoDB Shell Integration

The extension integrates with `mongosh`:

1. Install MongoDB Shell: https://www.mongodb.com/docs/mongodb-shell/install/
2. Configure path in VS Code settings:
   - `documentDB.mongoShell.path`: Path to `mongosh` executable
3. Right-click connection → **"Launch Shell"**
4. Run shell commands directly in VS Code terminal

### Scrapbook Feature

Create `.mongodb` files for reusable queries:

```javascript
// File: queries/product-queries.mongodb

// Connect to database
use('documentdb');

// Query 1: Out of stock products
db.products.find({ stock_quantity: { $lte: 0 } });

// Query 2: Premium products
db.products.find({ price: { $gte: 500 } });

// Query 3: Products by category with count
db.products.aggregate([
  { $group: { _id: "$category", count: { $sum: 1 } } }
]);
```

Execute queries by:
- Clicking the **"Run"** code lens above each query
- Selecting query text and pressing `Ctrl+Shift+R`

### Connection Management

**Multiple Connections**:
- Save multiple connections (local, staging, production)
- Color-code with custom names
- Organize with folders (coming soon)

**Credential Management**:
- Credentials stored securely in VS Code's secret storage
- Update credentials: Right-click → **"Update Credentials"**
- Different auth methods supported:
  - SCRAM-SHA-256 (username/password)
  - X.509 certificates
  - Connection string-based auth

### Service Discovery Providers

The extension includes built-in service discovery for:

1. **Azure Virtual Machines**: Auto-discover MongoDB on Azure VMs
2. **Azure Cosmos DB for MongoDB**: Detect vCore and RU-based accounts
3. **Local Instances**: Find DocumentDB Local and emulators

Configure in **Service Discovery View** → **Add Provider**

## Troubleshooting

### Connection Issues

**Problem**: "Connection timeout" or "Unable to connect"

**Solutions**:
1. Verify Docker container is running:
   ```powershell
   docker-compose ps documentdb
   ```

2. Check connection string parameters:
   ```
   mongodb://admin:password123@localhost:10260/?tls=true&tlsAllowInvalidCertificates=true&authMechanism=SCRAM-SHA-256
   ```

3. Ensure port 10260 is not blocked:
   ```powershell
   netstat -an | findstr "10260"
   ```

4. Check DocumentDB logs:
   ```powershell
   docker-compose logs documentdb
   ```

### Authentication Errors

**Problem**: "Authentication failed"

**Solutions**:
1. Verify credentials match `.env` file:
   - Username: `docdb_user`
   - Password: `docdb_password`

2. Ensure `authMechanism=SCRAM-SHA-256` is in connection string

3. Try recreating the connection with fresh credentials

### TLS/SSL Errors

**Problem**: "SSL handshake failed"

**Solution**: Ensure these parameters are in your connection string:
```
tls=true&tlsAllowInvalidCertificates=true
```

⚠️ Note: `tlsAllowInvalidCertificates=true` is acceptable for local development but **should never be used in production**.

### Data Not Appearing

**Problem**: Collections or documents don't show up

**Solutions**:
1. Refresh the connection:
   - Right-click connection → **"Refresh"**

2. Verify data exists via API:
   ```powershell
   # Test API endpoint
   curl http://localhost:8000/api/v1/products
   ```

3. Check database name in connection matches application:
   - Default: `documentdb` (from `MONGODB_DB_NAME` in `.env`)

### Performance Issues

**Problem**: Slow queries or timeouts

**Solutions**:
1. Check indexes in collections (expand collection → Indexes)
2. Limit result set size with filters
3. Adjust timeout in settings:
   - `documentDB.mongoShell.timeout`: Default 30000ms (30s)
4. Monitor Docker container resources:
   ```powershell
   docker stats documentdb
   ```

## Configuration Settings

Access via `File → Preferences → Settings` (or `Ctrl+,`):

```json
{
  // MongoDB Shell path (if using launch shell feature)
  "documentDB.mongoShell.path": "",
  
  // Shell execution timeout (milliseconds)
  "documentDB.mongoShell.timeout": 30000,
  
  // Documents per page in query results
  "documentDB.mongoShell.batchSize": 20,
  
  // Confirmation prompts
  "documentDB.confirmations.confirmationStyle": "Ask",
  
  // Show operation summaries
  "documentDB.userInterface.ShowOperationSummaries": true,
  
  // Show URL handling confirmations
  "documentDB.confirmations.showUrlHandlingConfirmations": true
}
```

## Resources

- **Extension Homepage**: https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-documentdb
- **GitHub Repository**: https://github.com/microsoft/vscode-documentdb
- **Documentation**: https://microsoft.github.io/vscode-documentdb/
- **Blog Post**: https://devblogs.microsoft.com/cosmosdb/meet-the-documentdb-extension-for-vs-code/
- **Issue Tracker**: https://github.com/microsoft/vscode-documentdb/issues

## Tips & Best Practices

### For Development

1. **Use Descriptive Connection Names**: "E-commerce Local" vs "localhost:10260"
2. **Leverage Query History**: Reuse common queries without retyping
3. **Create `.mongodb` Files**: Save frequently-used queries as scrapbooks
4. **Export Before Testing**: Backup data before running destructive operations
5. **Monitor Indexes**: Ensure Beanie-created indexes are present for performance

### For Team Collaboration

1. **Share Connection Patterns**: Document connection string format in README
2. **Use URL Deep Links**: Share direct links to specific collections
3. **Export Sample Data**: Provide team members with seed data as JSON
4. **Document Custom Queries**: Maintain a shared queries folder in the repo

### Security Reminders

- ✅ Use `tlsAllowInvalidCertificates=true` only for local development
- ✅ Never commit connection strings with production credentials
- ✅ Use environment variables for sensitive data
- ✅ Regularly rotate database passwords
- ✅ Restrict DocumentDB access by IP when deploying to cloud

---

**Next Steps**: Now that you understand the extension, try:
1. Connecting to your local DocumentDB instance
2. Exploring the sample data you created
3. Running queries to filter products by category
4. Exporting a collection to backup your data
5. Creating a MongoDB Playground file for analytics queries

Happy querying! 🚀
