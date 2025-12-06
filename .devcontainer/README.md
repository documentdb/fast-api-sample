# DevContainer Configuration

This directory contains the DevContainer configuration for the FastAPI + DocumentDB workshop. The DevContainer provides a fully configured development environment with all necessary tools and dependencies pre-installed.

## What's Included

### Base Environment
- **Python 3.11** - Latest Python runtime
- **Node.js 20** - For frontend development
- **Docker-in-Docker** - Run Docker commands inside the container
- **Git** - Version control

### VS Code Extensions
- **Python** - Python language support
- **Pylance** - Fast Python language server
- **Docker** - Docker container management
- **DocumentDB** - Azure Cosmos DB/DocumentDB extension
- **MongoDB** - MongoDB tools and query support
- **Prettier** - Code formatting for JSON, YAML, etc.
- **ESLint** - JavaScript linting
- **Black Formatter** - Python code formatting
- **isort** - Python import sorting
- **Ruff** - Fast Python linter

### Python Packages
All packages from `backend/requirements.txt`:
- FastAPI - Web framework
- Uvicorn - ASGI server
- Beanie - MongoDB ODM
- Motor - Async MongoDB driver
- Pydantic - Data validation
- Pytest - Testing framework
- httpx - Async HTTP client for testing
- Black, isort, mypy - Development tools

### Node.js Packages
All packages from `frontend/package.json`:
- React - UI library
- Vite - Build tool
- TypeScript - Type safety
- Tailwind CSS - Styling

## How It Works

### Automatic Setup
When you open this repository in GitHub Codespaces or VS Code with the Dev Containers extension:

1. **Container Creation**: DevContainer builds from the Python 3.11 base image
2. **Feature Installation**: Installs Docker, Node.js, and common utilities
3. **Post-Create Script**: Runs `.devcontainer/post-create.sh` which:
   - Updates system packages
   - Installs Python dependencies
   - Installs Node.js dependencies
   - Creates `.env` file if needed
   - Pulls DocumentDB Docker image
   - Sets up helpful bash aliases
   - Configures git

4. **Extension Installation**: All VS Code extensions are automatically installed
5. **Port Forwarding**: Ports 8000 (API), 80 (frontend), and 10260 (DocumentDB) are automatically forwarded

### Helpful Aliases

The post-create script adds these aliases to your shell:

#### Navigation
- `workshop` - Go to project root
- `backend` - Go to backend directory
- `frontend` - Go to frontend directory

#### Running Services
- `run-all` - Start all services with docker-compose
- `run-backend` - Start only backend service
- `run-frontend` - Start only frontend service
- `stop-all` - Stop all services

#### Logging
- `logs-backend` - View backend logs
- `logs-frontend` - View frontend logs

#### Testing
- `test` - Run pytest
- `test-cov` - Run pytest with coverage report

#### Docker
- `dps` - List running containers (docker ps)
- `dimg` - List images (docker images)
- `dprune` - Clean up unused Docker resources

## Manual Setup (if needed)

If the automatic setup doesn't complete, you can run these commands manually:

```bash
# Install Python dependencies
pip install --user -r backend/requirements.txt

# Install Node.js dependencies
cd frontend && npm install && cd ..

# Create .env file
cp .env.example .env

# Pull DocumentDB image
docker pull ghcr.io/documentdb/documentdb/documentdb-local:latest
docker tag ghcr.io/documentdb/documentdb/documentdb-local:latest documentdb

# Load aliases
source ~/.bashrc
```

## Port Configuration

The DevContainer automatically forwards these ports:

| Port  | Service           | Auto-Forward | Description                    |
|-------|-------------------|--------------|--------------------------------|
| 8000  | FastAPI Backend   | Notify       | API endpoints and Swagger UI   |
| 80    | React Frontend    | Notify       | Web application interface      |
| 10260 | DocumentDB        | Ignore       | Database connection (internal) |

## Environment Variables

The `.env` file is automatically created from `.env.example` with these defaults:

```env
DOCUMENTDB_URL=mongodb://admin:password123@host.docker.internal:10260/?tls=true&tlsAllowInvalidCertificates=true&authMechanism=SCRAM-SHA-256
DOCUMENTDB_DB_NAME=ecommerce
DEBUG=true
RELOAD=true
```

**Note**: `host.docker.internal` allows containers to communicate with services on the Codespace host.

## Customization

### Adding Python Packages

1. Add to `backend/requirements.txt`
2. Run: `pip install --user -r backend/requirements.txt`

### Adding Node.js Packages

1. Add to `frontend/package.json`
2. Run: `cd frontend && npm install`

### Adding VS Code Extensions

1. Edit `.devcontainer/devcontainer.json`
2. Add extension ID to `customizations.vscode.extensions` array
3. Rebuild container

### Modifying Post-Create Script

Edit `.devcontainer/post-create.sh` to add custom setup steps.

## Troubleshooting

### Docker not available
- Ensure Docker-in-Docker feature is enabled in `devcontainer.json`
- Restart the DevContainer

### Python packages not found
```bash
pip install --user -r backend/requirements.txt
```

### Node.js packages not found
```bash
cd frontend && npm install
```

### Aliases not available
```bash
source ~/.bashrc
```

### Ports not forwarded
- Check the PORTS tab in VS Code
- Manually forward ports if needed

## Rebuilding the DevContainer

If you make changes to the DevContainer configuration:

1. **In VS Code**: 
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Dev Containers: Rebuild Container"
   - Press Enter

2. **In GitHub Codespaces**:
   - Click the Codespaces menu (bottom left)
   - Select "Rebuild Container"

## Resources

- [DevContainer Specification](https://containers.dev/)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [GitHub Codespaces Docs](https://docs.github.com/en/codespaces)
