# Backend formatting script for Windows
Write-Host "Auto-formatting Python code..." -ForegroundColor Green

# Sort imports
Write-Host "Sorting imports with isort..." -ForegroundColor Yellow
docker-compose exec web isort .

# Format code
Write-Host "Formatting code with black..." -ForegroundColor Yellow
docker-compose exec web black .

Write-Host "Formatting complete!" -ForegroundColor Green