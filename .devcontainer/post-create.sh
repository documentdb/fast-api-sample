#!/bin/bash
set -e

echo "🚀 Starting FastAPI + DocumentDB Workshop Setup..."

# Fix Docker permissions for vscode user
echo "🔧 Configuring Docker permissions..."
sudo usermod -aG docker vscode || true
sudo chown vscode:docker /var/run/docker.sock || true
sudo chmod 666 /var/run/docker.sock || true

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update

# Install additional utilities
echo "🔧 Installing additional utilities..."
sudo apt-get install -y \
    curl \
    wget \
    git \
    vim \
    jq \
    tree \
    htop

# Verify Docker installation
echo "🐳 Verifying Docker installation..."
docker --version
docker-compose --version

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install --user --upgrade pip
pip install --user -r backend/requirements.txt

# Verify Python packages
echo "✅ Verifying Python packages..."
python -c "import fastapi, uvicorn, beanie, motor, pytest; print('Python packages installed successfully!')"

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Verify Node.js installation
echo "✅ Verifying Node.js installation..."
node --version
npm --version

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ .env file created"
    else
        echo "⚠️  .env.example not found, creating default .env..."
        cat > .env << 'EOF'
DOCUMENTDB_URL=mongodb://admin:password123@host.docker.internal:10260/?tls=true&tlsAllowInvalidCertificates=true&authMechanism=SCRAM-SHA-256
DOCUMENTDB_DB_NAME=ecommerce
DEBUG=true
RELOAD=true
EOF
        echo "✅ Default .env file created"
    fi
else
    echo "✅ .env file already exists"
fi

# Pull DocumentDB Docker image (this takes time, so do it now)
echo "🗄️  Pulling DocumentDB Docker image (this may take a few minutes)..."
docker pull ghcr.io/documentdb/documentdb/documentdb-local:latest || echo "⚠️  DocumentDB image pull failed - you can pull it manually later"

# Tag the image for convenience
docker tag ghcr.io/documentdb/documentdb/documentdb-local:latest documentdb 2>/dev/null || echo "ℹ️  Image already tagged or not yet pulled"

# Set up git configuration helpers
echo "🔧 Setting up git configuration..."
git config --global --add safe.directory /workspaces/fast-api-sample || true

# Create helpful aliases
echo "📝 Creating helpful bash aliases..."
cat >> ~/.bashrc << 'EOF'

# Workshop aliases
alias workshop='cd /workspaces/fast-api-sample'
alias backend='cd /workspaces/fast-api-sample/backend'
alias frontend='cd /workspaces/fast-api-sample/frontend'
alias run-backend='cd /workspaces/fast-api-sample && docker-compose up -d backend'
alias run-frontend='cd /workspaces/fast-api-sample && docker-compose up -d frontend'
alias run-all='cd /workspaces/fast-api-sample && docker-compose up -d'
alias stop-all='cd /workspaces/fast-api-sample && docker-compose down'
alias logs-backend='cd /workspaces/fast-api-sample && docker-compose logs -f backend'
alias logs-frontend='cd /workspaces/fast-api-sample && docker-compose logs -f frontend'
alias test='cd /workspaces/fast-api-sample/backend && pytest -v'
alias test-cov='cd /workspaces/fast-api-sample/backend && pytest --cov=app --cov-report=html'
alias api-docs='echo "API docs available at: http://localhost:8000/docs"'

# Docker helpers
alias dps='docker ps'
alias dimg='docker images'
alias dprune='docker system prune -f'

EOF

# Display success message with next steps
echo ""
echo "✨ ============================================== ✨"
echo "   Workshop Environment Setup Complete! 🎉"
echo "✨ ============================================== ✨"
echo ""
echo "📚 Next Steps:"
echo ""
echo "1. Start the DocumentDB container:"
echo "   docker run -dt -p 10260:10260 --name documentdb-container documentdb --username admin --password password123"
echo ""
echo "2. Start the application:"
echo "   docker-compose up -d"
echo ""
echo "3. Access the application:"
echo "   - API docs: http://localhost:8000/docs"
echo "   - Frontend: http://localhost:80"
echo ""
echo "4. Helpful aliases available:"
echo "   - run-all        : Start all services"
echo "   - stop-all       : Stop all services"
echo "   - test           : Run tests"
echo "   - logs-backend   : View backend logs"
echo ""
echo "📖 Open workshop/Module-00.md to get started!"
echo ""
echo "💡 Tip: Run 'source ~/.bashrc' to load the new aliases"
echo ""
