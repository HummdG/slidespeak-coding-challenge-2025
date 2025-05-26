# Backend linting script for Windows
Write-Host "Running Python linting tools..." -ForegroundColor Green

# Format imports
Write-Host "Sorting imports with isort..." -ForegroundColor Yellow
docker-compose exec web isort . --check-only --diff

# Format code
Write-Host "Checking code formatting with black..." -ForegroundColor Yellow
docker-compose exec web black . --check --diff

# Check code style
Write-Host "Checking code style with flake8..." -ForegroundColor Yellow
docker-compose exec web flake8 .

# Type checking (with relaxed rules for missing stubs)
Write-Host "Type checking with mypy..." -ForegroundColor Yellow
docker-compose exec web mypy . --ignore-missing-imports --disable-error-code=import-untyped

# Security check
Write-Host "Security check with bandit..." -ForegroundColor Yellow
docker-compose exec web bandit -r . -f json

Write-Host "Linting complete!" -ForegroundColor Green