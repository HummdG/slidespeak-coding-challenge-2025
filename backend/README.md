# SlideSpeak Backend - PowerPoint to PDF Converter API

A robust, scalable backend service for converting PowerPoint files to PDF format. Built with FastAPI, Celery, and LibreOffice, featuring asynchronous processing, AWS S3 integration, and comprehensive error handling.

## 🚀 Features

- **RESTful API**: FastAPI-based REST API with automatic OpenAPI documentation
- **Asynchronous Processing**: Celery-based background task processing with Redis
- **File Conversion**: LibreOffice Unoserver integration for reliable PPTX to PDF conversion
- **Cloud Storage**: AWS S3 integration with presigned URLs for secure file access
- **Auto-cleanup**: Scheduled cleanup of old files to manage storage costs
- **Comprehensive Testing**: Full test suite with pytest and mocking
- **Production Ready**: Docker containerization with proper logging and error handling
- **Type Safety**: Full type hints with mypy static analysis
- **Code Quality**: Linting with flake8, formatting with black, security scanning with bandit

## 🏗️ Architecture

### System Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │────│  FastAPI    │────│   Celery    │────│ Unoserver   │
│             │    │   Server    │    │   Worker    │    │(LibreOffice)│
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                           │                  │
                           │                  │
                   ┌─────────────┐    ┌─────────────┐
                   │    Redis    │    │   AWS S3    │
                   │   Broker    │    │   Storage   │
                   └─────────────┘    └─────────────┘
```

### Tech Stack

- **API Framework**: [FastAPI 0.104+](https://fastapi.tiangolo.com/) - Modern, fast web framework
- **Task Queue**: [Celery 5.3+](https://docs.celeryq.dev/) - Distributed task queue
- **Message Broker**: [Redis 7](https://redis.io/) - In-memory data structure store
- **File Conversion**: [LibreOffice Unoserver](https://github.com/unoconv/unoserver) - Headless office suite
- **Cloud Storage**: [AWS S3](https://aws.amazon.com/s3/) - Object storage service
- **Containerization**: [Docker](https://www.docker.com/) + Docker Compose
- **Testing**: [pytest](https://pytest.org/) - Python testing framework
- **Code Quality**: black, flake8, mypy, bandit, isort

## 📁 Project Structure

```
backend/
├── app/                      # Application source code
│   ├── main.py              # FastAPI application and routes
│   ├── tasks.py             # Celery background tasks
│   ├── celery_app.py        # Celery configuration
│   └── tests/               # Test suite
│       ├── __init__.py
│       ├── conftest.py      # Test configuration and fixtures
│       ├── factories.py     # Test data factories
│       ├── test_main.py     # API endpoint tests
│       ├── test_tasks.py    # Celery task tests
│       └── test_celery_app.py # Celery configuration tests
├── docker-compose.yml       # Multi-service container orchestration
├── Dockerfile              # Container build instructions
├── requirements.txt        # Python dependencies
├── requirements-test.txt   # Testing dependencies
├── pyproject.toml         # Python project configuration
├── pytest.ini            # pytest configuration
├── .flake8               # Flake8 linting configuration
├── .gitignore            # Git ignore patterns
├── format.ps1            # Windows formatting script
├── lint.ps1              # Windows linting script
└── run_tests.py          # Test runner script
```

## 🔧 Installation & Setup

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- [AWS CLI](https://aws.amazon.com/cli/) configured with appropriate credentials
- Python 3.10+ (for local development)

### Quick Start with Docker

```bash
# Clone the repository
git clone <repository-url>
cd backend

# Set up environment variables
cp .env.example .env
# Edit .env with your AWS credentials and configuration

# Build and start all services
docker compose up --build

# The API will be available at http://localhost:8000
# API documentation at http://localhost:8000/docs
```

### Environment Configuration

Create a `.env` file in the backend directory:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_S3_BUCKET=your-bucket-name
AWS_REGION=eu-west-1

# Redis Configuration
REDIS_URL=redis://redis:6379/0
REDIS_RESULT_BACKEND=redis://redis:6379/1

# Unoserver Configuration
UNOSERVER_HOST=unoserver
UNOSERVER_PORT=2004

# Task Configuration
TASK_SOFT_TIME_LIMIT=300
TASK_TIME_LIMIT=360
```

### AWS Setup

#### 1. IAM User Setup

Create an IAM user with the following configuration:

```json
{
  "UserName": "ppt-to-pdf-bot",
  "AttachedPolicies": ["AmazonS3FullAccess"],
  "ARN": "arn:aws:iam::ACCOUNT_ID:user/ppt-to-pdf-bot"
}
```

#### 2. S3 Bucket Configuration

```bash
# Create S3 bucket
aws s3 mb s3://your-bucket-name --region eu-west-1

# Configure bucket policy for secure access
aws s3api put-bucket-policy --bucket your-bucket-name --policy file://bucket-policy.json
```

#### 3. AWS CLI Configuration

```bash
aws configure
AWS Access Key ID [None]: YOUR_ACCESS_KEY
AWS Secret Access Key [None]: YOUR_SECRET_KEY
Default region name [None]: eu-west-1
Default output format [None]: json
```

## 🌐 API Documentation

### Endpoints

#### POST /convert

Upload and convert a PowerPoint file to PDF.

**Request:**

```bash
curl -X POST "http://localhost:8000/convert" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@presentation.pptx"
```

**Response:**

```json
{
  "jobId": "task-uuid-here"
}
```

**Error Responses:**

- `400`: Invalid file format or missing filename
- `500`: Server error during upload or task creation

#### GET /status/{job_id}

Check the status of a conversion job.

**Request:**

```bash
curl "http://localhost:8000/status/task-uuid-here"
```

**Response (Processing):**

```json
{
  "status": "processing"
}
```

**Response (Success):**

```json
{
  "status": "done",
  "url": "https://s3.amazonaws.com/bucket/file.pdf?presigned-params"
}
```

**Response (Error):**

```json
{
  "status": "error",
  "error": "Conversion failed: detailed error message"
}
```

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🔄 Background Processing

### Celery Task Architecture

#### convert_task

Main conversion task that handles the complete workflow:

```python
@celery.task(bind=True)
def convert_task(self, pptx_key: str, base_filename: str):
    """
    1. Download PPTX from S3
    2. Send to Unoserver for conversion
    3. Upload PDF back to S3
    4. Generate presigned download URL
    5. Clean up temporary files
    """
```

#### cleanup_old_files

Scheduled task for automatic file cleanup:

```python
@celery.task
def cleanup_old_files():
    """
    Delete files from S3 older than 1 day
    Runs every 6 hours via Celery Beat
    """
```

### Task States

```
PENDING → SUCCESS/FAILURE/REVOKED
    ↓
processing → done/error
```

### Error Handling

- **S3 Errors**: Connection timeouts, permission issues
- **Conversion Errors**: LibreOffice processing failures
- **Network Errors**: Unoserver communication issues
- **File System Errors**: Temporary file handling issues

## 🐳 Docker Services

### Service Configuration

```yaml
services:
  web: # FastAPI application server
  celery: # Background task worker
  celery-beat: # Scheduled task scheduler
  redis: # Message broker and result backend
  unoserver: # LibreOffice conversion service
```

### Container Details

#### FastAPI Web Server

- **Port**: 8000
- **Image**: Custom Python 3.10-slim
- **Dependencies**: Redis, Unoserver
- **Health Check**: GET /docs endpoint

#### Celery Worker

- **Command**: `celery -A celery_app.celery worker --loglevel=info`
- **Concurrency**: Auto-detected based on CPU cores
- **Dependencies**: Redis, Unoserver

#### Celery Beat Scheduler

- **Command**: `celery -A celery_app.celery beat --loglevel=info`
- **Schedule**: Cleanup task every 6 hours
- **Persistence**: Schedule stored in Redis

#### Redis

- **Image**: redis:7-alpine
- **Port**: 6379
- **Persistence**: Optional volume mounting

#### Unoserver

- **Image**: libreofficedocker/libreoffice-unoserver:3.19-9c28c22
- **Port**: 2002
- **Purpose**: Headless LibreOffice for document conversion

## 🧪 Testing

### Test Structure

```
app/tests/
├── conftest.py           # Test configuration and fixtures
├── factories.py          # Test data generation utilities
├── test_main.py         # FastAPI endpoint tests
├── test_tasks.py        # Celery task tests
└── test_celery_app.py   # Celery configuration tests
```

### Test Categories

#### Unit Tests

- API endpoint functionality
- Task execution logic
- Error handling scenarios
- Configuration validation

#### Integration Tests

- End-to-end conversion workflow
- AWS S3 integration
- Unoserver communication
- Celery task execution

#### Mock Tests

- External service failures
- Network timeout scenarios
- File system errors
- AWS service unavailability

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app

# Run specific test file
python -m pytest app/tests/test_main.py -v

# Run with detailed output
python -m pytest -v --tb=short

# Run integration tests
python -m pytest -m integration -v
```

### Test Fixtures

```python
@pytest.fixture
def test_client():
    """FastAPI test client"""
    return TestClient(app)

@pytest.fixture
def sample_pptx_file():
    """Generate valid PPTX file for testing"""
    return FileFactory.create_pptx_file()

@pytest.fixture
def mock_s3():
    """Mock AWS S3 service"""
    return MockFactory.create_s3_client_mock()
```

## 🔍 Code Quality

### Linting and Formatting

#### Black (Code Formatting)

```bash
# Format all Python files
black .

# Check formatting without changes
black . --check --diff
```

#### Flake8 (Style Guide Enforcement)

```bash
# Run linting
flake8 .

# Configuration in .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503, E501
```

#### isort (Import Sorting)

```bash
# Sort imports
isort .

# Check import order
isort . --check-only --diff
```

#### mypy (Static Type Checking)

```bash
# Run type checking
mypy . --ignore-missing-imports
```

#### bandit (Security Analysis)

```bash
# Security scan
bandit -r . -f json
```

### Automated Scripts

#### Windows Scripts

```powershell
# Format code
.\format.ps1

# Run all linting tools
.\lint.ps1
```

#### Python Test Runner

```bash
# Comprehensive test execution
python run_tests.py
```

## 📊 Monitoring and Logging

### Application Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### Celery Monitoring

```bash
# Monitor Celery workers
celery -A celery_app.celery inspect active

# View task history
celery -A celery_app.celery events

# Worker statistics
celery -A celery_app.celery inspect stats
```

### Health Checks

- **API Health**: GET /docs endpoint availability
- **Redis Health**: Connection and response time monitoring
- **S3 Health**: Bucket access and upload capability
- **Unoserver Health**: Conversion service availability

## 🚀 Deployment

### Production Configuration

#### Environment Variables

```bash
# Production settings
FASTAPI_ENV=production
LOG_LEVEL=WARNING
WORKER_PROCESSES=4
REDIS_URL=redis://your-redis-host:6379/0
```

#### Docker Production Build

```dockerfile
FROM python:3.10-slim

# Security: Run as non-root user
RUN adduser --disabled-password --gecos '' appuser

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
CHOWN appuser:appuser /app

USER appuser

# Production command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Scaling Considerations

#### Horizontal Scaling

- Multiple FastAPI instances behind load balancer
- Increased Celery worker instances
- Redis clustering for high availability

#### Performance Optimization

- Connection pooling for S3 and Redis
- Task result expiration configuration
- File cleanup optimization
- Request rate limiting

## 🔐 Security

### File Upload Security

- File type validation (PPTX only)
- File size limitations
- Virus scanning (recommended for production)
- Temporary file cleanup

### AWS Security

- IAM roles with minimal permissions
- S3 bucket policies for restricted access
- Presigned URL expiration (1 hour default)
- VPC configuration for network isolation

### API Security

- CORS configuration for frontend domain
- Request rate limiting
- Input validation and sanitization
- Error message sanitization

## 📈 Performance Metrics

### Conversion Metrics

- **Average Conversion Time**: 15-30 seconds for typical presentations
- **File Size Limits**: 50MB maximum (configurable)
- **Concurrent Jobs**: Limited by Celery worker count
- **Storage Retention**: 24 hours (configurable)

### Resource Usage

- **Memory**: ~100MB per worker process
- **CPU**: Depends on document complexity
- **Storage**: Temporary files cleaned automatically
- **Network**: S3 transfer bandwidth

## 🔮 Future Enhancements

### Planned Features

- [ ] Multi-format conversion support (PNG, JPEG, DOCX)
- [ ] Batch file processing
- [ ] Webhook notifications for job completion
- [ ] File compression options
- [ ] Conversion quality settings
- [ ] User authentication and rate limiting

### Technical Improvements

- [ ] Prometheus metrics integration
- [ ] Advanced caching strategies
- [ ] Database integration for job persistence
- [ ] Kubernetes deployment manifests
- [ ] CI/CD pipeline configuration
- [ ] Load testing and performance benchmarks

## 🛠️ Troubleshooting

### Common Issues

#### "Connection refused to Redis"

```bash
# Check Redis container status
docker compose ps redis

# View Redis logs
docker compose logs redis

# Test Redis connectivity
docker compose exec web python -c "import redis; r=redis.Redis(host='redis'); print(r.ping())"
```

#### "S3 access denied"

```bash
# Verify AWS credentials
aws sts get-caller-identity

# Test S3 access
aws s3 ls s3://your-bucket-name

# Check IAM permissions
aws iam list-attached-user-policies --user-name ppt-to-pdf-bot
```

#### "Unoserver conversion failed"

```bash
# Check Unoserver container
docker compose ps unoserver

# View Unoserver logs
docker compose logs unoserver

# Test conversion endpoint
curl -X POST http://localhost:2002/request \
  -F "file=@test.pptx" \
  -F "convert-to=pdf"
```

### Debug Mode

```bash
# Run with debug logging
UVICORN_LOG_LEVEL=debug docker compose up

# Enable Celery debug
CELERY_LOG_LEVEL=debug docker compose up celery
```

## 🤝 Contributing

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt -r requirements-test.txt

# Set up pre-commit hooks
pre-commit install

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Code Contribution Guidelines

1. **Follow PEP 8**: Use black and flake8 for consistency
2. **Type Hints**: Add type annotations to all functions
3. **Documentation**: Update docstrings and README as needed
4. **Testing**: Write tests for new features and bug fixes
5. **Security**: Run bandit security scanner
6. **Conventional Commits**: Use semantic commit messages

### Commit Message Format

```
feat: add batch file processing support
fix: resolve S3 timeout handling
docs: update API documentation
test: add integration tests for conversion workflow
refactor: improve error handling structure
perf: optimize file upload performance
```
