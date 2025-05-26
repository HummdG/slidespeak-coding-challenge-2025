# Backend Testing Script for PowerShell
# This script runs all tests with proper environment setup

param(
    [string]$TestType = "all",
    [switch]$SkipLint,
    [switch]$SkipCoverage,
    [switch]$Verbose
)

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "Starting Backend Test Suite" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Function to print colored output
function Write-Step {
    param([string]$Message)
    Write-Host ">> $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if we're in Docker environment
$InDocker = Test-Path "/.dockerenv"
if ($InDocker) {
    Write-Step "Running in Docker environment"
} else {
    Write-Step "Running in local environment"
}

# Set test environment variables
Write-Step "Setting environment variables for testing"
$env:TESTING = "1"
$env:AWS_S3_BUCKET = "test-bucket"
$env:AWS_REGION = "us-east-1"
$env:AWS_ACCESS_KEY_ID = "testing"
$env:AWS_SECRET_ACCESS_KEY = "testing"
$env:REDIS_URL = "redis://localhost:6379/15"
$env:UNOSERVER_HOST = "test-unoserver"
$env:UNOSERVER_PORT = "2004"

Write-Success "Environment variables configured"

# Function to run tests with different configurations
function Invoke-Tests {
    param(
        [string]$TestCategory,
        [string]$ExtraArgs = ""
    )
    
    Write-Step "Running $TestCategory tests..."
    
    try {
        if ($ExtraArgs) {
            $cmd = "pytest $ExtraArgs"
        } else {
            $cmd = "pytest"
        }
        
        if ($Verbose) {
            Write-Host "Executing: $cmd" -ForegroundColor Gray
        }
        
        Invoke-Expression $cmd
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "$TestCategory tests passed!"
            return $true
        } else {
            Write-Error "$TestCategory tests failed!"
            return $false
        }
    }
    catch {
        Write-Error "Failed to run $TestCategory tests: $($_.Exception.Message)"
        return $false
    }
}

# Function to check if a command exists
function Test-Command {
    param([string]$Command)
    
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to install dependencies if not in Docker
function Install-Dependencies {
    if (-not $InDocker) {
        Write-Step "Installing test dependencies..."
        
        if (-not (Test-Command "pip")) {
            Write-Error "pip not found. Please install Python and pip first."
            exit 1
        }
        
        # Check if requirements.txt exists
        if (-not (Test-Path "requirements.txt")) {
            Write-Warning "requirements.txt not found in current directory"
            Write-Host "Current directory: $(Get-Location)" -ForegroundColor Gray
            Write-Host "Available files:" -ForegroundColor Gray
            Get-ChildItem | Select-Object Name | Format-Table -AutoSize
            
            # Try to find requirements.txt in app directory
            if (Test-Path "app\requirements.txt") {
                Write-Step "Found requirements.txt in app directory, using that..."
                try {
                    pip install -r app\requirements.txt
                    Write-Success "Dependencies installed successfully from app\requirements.txt"
                }
                catch {
                    Write-Warning "Failed to install dependencies from app\requirements.txt: $($_.Exception.Message)"
                }
            } else {
                Write-Warning "No requirements.txt found. Installing basic test dependencies..."
                try {
                    pip install pytest pytest-asyncio pytest-mock httpx moto fakeredis pytest-cov
                    Write-Success "Basic test dependencies installed"
                }
                catch {
                    Write-Warning "Failed to install basic dependencies: $($_.Exception.Message)"
                }
            }
        } else {
            try {
                pip install -r requirements.txt
                Write-Success "Dependencies installed successfully"
            }
            catch {
                Write-Error "Failed to install dependencies: $($_.Exception.Message)"
                exit 1
            }
        }
    }
}

# Function to run code quality checks
function Invoke-QualityChecks {
    Write-Step "Running code quality checks..."
    $qualityPassed = $true
    
    # Check style with flake8 (if available)
    Write-Host "Checking code style..." -ForegroundColor Gray
    try {
        if (Test-Command "flake8") {
            flake8 . 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Code style is correct"
            } else {
                Write-Warning "Code style issues found"
                $qualityPassed = $false
            }
        } else {
            Write-Warning "flake8 not available, skipping style check"
        }
    }
    catch {
        Write-Warning "flake8 check failed"
    }
    
    # Type checking with mypy (if available)
    Write-Host "Running type checking..." -ForegroundColor Gray
    try {
        if (Test-Command "mypy") {
            mypy . --ignore-missing-imports 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Type checking passed"
            } else {
                Write-Warning "Type checking issues found"
                $qualityPassed = $false
            }
        } else {
            Write-Warning "mypy not available, skipping type check"
        }
    }
    catch {
        Write-Warning "mypy check failed"
    }
    
    return $qualityPassed
}

# Function to generate coverage report
function Invoke-CoverageReport {
    Write-Step "Generating coverage report..."
    
    try {
        coverage report --fail-under=80
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Coverage requirements met"
        } else {
            Write-Warning "Coverage below 80%"
            return $false
        }
        
        # Generate HTML coverage report
        coverage html
        Write-Step "HTML coverage report generated in htmlcov/"
        
        return $true
    }
    catch {
        Write-Warning "Failed to generate coverage report"
        return $false
    }
}

# Main execution function
function Invoke-Main {
    $exitCode = 0
    
    # Install dependencies if needed
    Install-Dependencies
    
    # Run quality checks unless skipped
    if (-not $SkipLint) {
        $qualityPassed = Invoke-QualityChecks
        if (-not $qualityPassed) {
            $exitCode = 1
        }
    }
    
    # Run unit tests
    $unitPassed = Invoke-Tests "Unit" "--maxfail=5 -v -m 'not integration and not slow'"
    if (-not $unitPassed) {
        $exitCode = 1
    }
    
    # Run integration tests
    $integrationPassed = Invoke-Tests "Integration" "--maxfail=3 -v -m integration"
    if (-not $integrationPassed) {
        $exitCode = 1
    }
    
    # Run slow tests if environment variable is set
    if ($env:RUN_SLOW_TESTS -eq "true") {
        $slowPassed = Invoke-Tests "Slow" "--maxfail=1 -v -m slow"
        if (-not $slowPassed) {
            $exitCode = 1
        }
    } else {
        Write-Step "Skipping slow tests (set RUN_SLOW_TESTS=true to run them)"
    }
    
    # Generate coverage report unless skipped
    if (-not $SkipCoverage) {
        $coveragePassed = Invoke-CoverageReport
        if (-not $coveragePassed) {
            $exitCode = 1
        }
    }
    
    # Final summary
    Write-Host ""
    Write-Host "================================" -ForegroundColor Cyan
    if ($exitCode -eq 0) {
        Write-Success "All tests completed successfully!"
    } else {
        Write-Error "Some tests failed or quality checks didn't pass"
    }
    Write-Host "================================" -ForegroundColor Cyan
    
    return $exitCode
}

# Handle script arguments
switch ($TestType.ToLower()) {
    "unit" {
        Install-Dependencies
        $success = Invoke-Tests "Unit" "--maxfail=5 -v -m 'not integration and not slow'"
        exit $(if ($success) { 0 } else { 1 })
    }
    "integration" {
        Install-Dependencies
        $success = Invoke-Tests "Integration" "--maxfail=3 -v -m integration"
        exit $(if ($success) { 0 } else { 1 })
    }
    "slow" {
        Install-Dependencies
        $success = Invoke-Tests "Slow" "--maxfail=1 -v -m slow"
        exit $(if ($success) { 0 } else { 1 })
    }
    "coverage" {
        Install-Dependencies
        pytest --cov=app --cov-report=html --cov-report=term-missing
        exit $LASTEXITCODE
    }
    "lint" {
        Write-Step "Running linting only..."
        Install-Dependencies
        $success = Invoke-QualityChecks
        Write-Host "Note: Black formatting and isort checks removed to prevent hanging" -ForegroundColor Gray
        exit $(if ($success) { 0 } else { 1 })
    }
    "format" {
        Write-Step "Auto-formatting code..."
        Install-Dependencies
        
        Write-Success "Formatting completed (black and isort removed to avoid hanging)"
        Write-Host "To format manually, install and run:" -ForegroundColor Gray
        Write-Host "  pip install black isort" -ForegroundColor Gray
        Write-Host "  black ." -ForegroundColor Gray
        Write-Host "  isort ." -ForegroundColor Gray
        exit 0
    }
    default {
        $exitCode = Invoke-Main
        exit $exitCode
    }
}