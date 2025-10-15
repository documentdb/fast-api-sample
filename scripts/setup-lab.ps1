# Quick Setup Script for E-commerce Demo Lab
# This script helps you set up the DocumentDB + FastAPI environment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  E-commerce Demo Lab - Quick Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Docker
Write-Host "[1/5] Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker not found. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if Docker is running
try {
    docker ps | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 2: Check if DocumentDB container is running
Write-Host "[2/5] Checking DocumentDB container..." -ForegroundColor Yellow
$existingContainer = docker ps -a --filter "name=documentdb" --format "{{.Names}}"

if ($existingContainer) {
    Write-Host "Found existing container: $existingContainer" -ForegroundColor Cyan
    $containerStatus = docker inspect -f '{{.State.Status}}' $existingContainer
    
    if ($containerStatus -eq "running") {
        Write-Host "✓ DocumentDB is already running on port 10260" -ForegroundColor Green
    } else {
        Write-Host "Container exists but is not running. Starting..." -ForegroundColor Yellow
        docker start $existingContainer
        Start-Sleep -Seconds 5
        Write-Host "✓ DocumentDB started" -ForegroundColor Green
    }
} else {
    Write-Host "No DocumentDB container found. Starting with docker-compose..." -ForegroundColor Yellow
    docker-compose up -d documentdb
    
    Write-Host "Waiting for DocumentDB to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # Check health
    $maxAttempts = 12
    $attempt = 0
    $healthy = $false
    
    while ($attempt -lt $maxAttempts -and -not $healthy) {
        $attempt++
        $health = docker inspect --format='{{.State.Health.Status}}' documentdb-local 2>$null
        
        if ($health -eq "healthy") {
            $healthy = $true
            Write-Host "✓ DocumentDB is healthy and ready" -ForegroundColor Green
        } else {
            Write-Host "  Attempt $attempt/$maxAttempts - Status: $health" -ForegroundColor Gray
            Start-Sleep -Seconds 5
        }
    }
    
    if (-not $healthy) {
        Write-Host "✗ DocumentDB did not become healthy. Check logs: docker-compose logs documentdb" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Step 3: Test connection with mongosh
Write-Host "[3/5] Testing DocumentDB connection..." -ForegroundColor Yellow
$connectionString = "mongodb://admin:password123@localhost:10260/?authMechanism=SCRAM-SHA-256&tls=true&tlsAllowInvalidCertificates=true"

try {
    $testResult = mongosh $connectionString --eval "db.adminCommand('ping')" --quiet 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ DocumentDB connection successful" -ForegroundColor Green
    } else {
        Write-Host "✗ Could not connect to DocumentDB" -ForegroundColor Red
        Write-Host "  Make sure mongosh is installed: https://www.mongodb.com/try/download/shell" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ mongosh not found (optional for this setup)" -ForegroundColor Yellow
    Write-Host "  You can still use the VS Code extension to connect" -ForegroundColor Gray
}

Write-Host ""

# Step 4: Check if VS Code extension is installed
Write-Host "[4/5] Checking VS Code extensions..." -ForegroundColor Yellow
try {
    $extensions = code --list-extensions 2>&1
    if ($extensions -match "ms-azuretools.vscode-documentdb") {
        Write-Host "✓ DocumentDB for VS Code extension is installed" -ForegroundColor Green
    } else {
        Write-Host "⚠ DocumentDB extension not found" -ForegroundColor Yellow
        Write-Host "  Install it with: code --install-extension ms-azuretools.vscode-documentdb" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠ Could not check VS Code extensions" -ForegroundColor Yellow
}

Write-Host ""

# Step 5: Check if sample data files exist
Write-Host "[5/5] Checking sample data files..." -ForegroundColor Yellow
$dataFiles = @(
    "scripts/sample_products.json",
    "scripts/sample_customers.json"
)

$allFilesExist = $true
foreach ($file in $dataFiles) {
    if (Test-Path $file) {
        Write-Host "✓ Found: $file" -ForegroundColor Green
    } else {
        Write-Host "✗ Missing: $file" -ForegroundColor Red
        $allFilesExist = $false
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "DocumentDB is running at:" -ForegroundColor White
Write-Host "  Host: localhost:10260" -ForegroundColor Cyan
Write-Host "  Username: admin" -ForegroundColor Cyan
Write-Host "  Password: password123" -ForegroundColor Cyan

Write-Host ""
Write-Host "Connection String for VS Code Extension:" -ForegroundColor White
Write-Host "  mongodb://admin:password123@localhost:10260/?authMechanism=SCRAM-SHA-256&tls=true&tlsAllowInvalidCertificates=true" -ForegroundColor Cyan

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Open VS Code: code ." -ForegroundColor White
Write-Host "  2. Open DocumentDB extension (Ctrl+Shift+P → 'DocumentDB: Focus on Databases View')" -ForegroundColor White
Write-Host "  3. Click '+' to add connection and paste the connection string above" -ForegroundColor White
Write-Host "  4. Create database 'ecommerce' with collection 'products'" -ForegroundColor White
Write-Host "  5. Import sample data from scripts/sample_products.json" -ForegroundColor White
Write-Host "  6. Start FastAPI: docker-compose up backend" -ForegroundColor White

Write-Host ""
Write-Host "Documentation:" -ForegroundColor Yellow
Write-Host "  - Full walkthrough: docs/LAB_WALKTHROUGH.md" -ForegroundColor White
Write-Host "  - Extension guide: docs/DOCUMENTDB_EXTENSION_GUIDE.md" -ForegroundColor White
Write-Host "  - Quick reference: docs/EXTENSION_QUICK_REFERENCE.md" -ForegroundColor White

Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor Yellow
Write-Host "  - View logs: docker-compose logs -f documentdb" -ForegroundColor White
Write-Host "  - Stop services: docker-compose down" -ForegroundColor White
Write-Host "  - Restart: docker-compose restart documentdb" -ForegroundColor White
Write-Host "  - Connect with mongosh: mongosh '$connectionString'" -ForegroundColor White

Write-Host ""
Write-Host "✓ Setup complete! Ready to start the lab." -ForegroundColor Green
Write-Host ""
