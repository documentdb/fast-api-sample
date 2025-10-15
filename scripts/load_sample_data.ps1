# Load Sample Data Script for Windows
# Run this script with: .\scripts\load_sample_data.ps1

Write-Host "Loading sample data into DocumentDB..." -ForegroundColor Yellow
Write-Host ""

# Check if services are running
$backend_status = docker-compose ps -q backend
if (-not $backend_status) {
    Write-Host "✗ Backend service is not running. Please start services first with: docker-compose up -d" -ForegroundColor Red
    exit 1
}

# Run the Python script inside the backend container
docker-compose exec backend python /app/scripts/load_sample_data.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Sample data loaded successfully!" -ForegroundColor Green
    Write-Host "Visit http://localhost:8000/docs to explore the API" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "✗ Failed to load sample data" -ForegroundColor Red
}
