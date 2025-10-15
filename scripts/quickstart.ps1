# FastAPI + DocumentDB Quick Start Script for Windows
# Run this script with: .\scripts\quickstart.ps1

Write-Host "FastAPI + DocumentDB E-commerce Demo - Quick Start" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env file created" -ForegroundColor Green
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# Build and start services
Write-Host ""
Write-Host "Building Docker containers..." -ForegroundColor Yellow
docker-compose build

Write-Host ""
Write-Host "Starting services..." -ForegroundColor Yellow
docker-compose up -d

# Wait for services to be healthy
Write-Host ""
Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if services are running
$backend_status = docker-compose ps -q backend
if ($backend_status) {
    Write-Host "✓ Backend service is running" -ForegroundColor Green
} else {
    Write-Host "✗ Backend service failed to start" -ForegroundColor Red
    docker-compose logs backend
    exit 1
}

$db_status = docker-compose ps -q documentdb
if ($db_status) {
    Write-Host "✓ DocumentDB service is running" -ForegroundColor Green
} else {
    Write-Host "✗ DocumentDB service failed to start" -ForegroundColor Red
    docker-compose logs documentdb
    exit 1
}

# Display success message
Write-Host ""
Write-Host "=================================================" -ForegroundColor Green
Write-Host "SUCCESS! Your e-commerce API is now running!" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green
Write-Host ""
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Alternative Docs:  http://localhost:8000/redoc" -ForegroundColor Cyan
Write-Host "Health Check:      http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  View logs:       docker-compose logs -f" -ForegroundColor White
Write-Host "  Stop services:   docker-compose down" -ForegroundColor White
Write-Host "  Run tests:       docker-compose exec backend pytest" -ForegroundColor White
Write-Host "  Load sample data: .\scripts\load_sample_data.ps1" -ForegroundColor White
Write-Host ""
