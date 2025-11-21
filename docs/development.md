# Development Guide

## Quick Start

### Prerequisites

- Python 3.13+
- uv (package manager)
- Git

### Setup

```bash
# Clone repository
git clone <repository-url>
cd kbe-proto-demo

# Create virtual environment with uv
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e ".[dev]"

# Set up environment
cp .env.example .env

# Run development server
uvicorn src.kbe_api.main:app --reload
```

## Project Structure

```
kbe-proto-demo/
├── src/kbe_api/         # Main application code
├── tests/               # Test suites
├── docs/                # Documentation
├── scripts/             # Utility scripts
└── pyproject.toml       # Project configuration
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Write Tests First (TDD)

```python
# tests/unit/test_action_service.py
import pytest
from kbe_api.services.action_service import ActionService

@pytest.mark.asyncio
async def test_execute_inference_action():
    service = ActionService()
    result = await service.execute_action(
        action_type="inference",
        parameters=[{"name": "entity", "value": "Building"}]
    )
    assert result.status == "completed"
    assert result.result is not None
```

### 3. Implement Feature

```python
# src/kbe_api/services/action_service.py
class ActionService:
    async def execute_action(
        self,
        action_type: str,
        parameters: List[ActionParameter]
    ) -> ActionResult:
        # Implementation
        pass
```

### 4. Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_action_service.py

# Run with coverage
pytest --cov=src/kbe_api --cov-report=html

# Run and watch for changes
pytest-watch
```

### 5. Code Quality Checks

```bash
# Format code
ruff format .

# Lint
ruff check .

# Type check
mypy src/

# Run all checks
./scripts/quality_check.sh
```

### 6. Commit Changes

```bash
git add .
git commit -m "feat: add inference action support"
git push origin feature/your-feature-name
```

## Code Style

### Type Hints

Always use type hints:

```python
from typing import List, Optional, Dict, Any

def process_entities(
    entities: List[str],
    config: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Process entities with optional configuration."""
    pass
```

### Async/Await

Use async for I/O operations:

```python
async def fetch_entity(uri: str) -> KnowledgeEntity:
    """Fetch entity from knowledge base."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/entities/{uri}")
        return KnowledgeEntity(**response.json())
```

### Error Handling

Use custom exceptions:

```python
# utils/exceptions.py
class KBEException(Exception):
    """Base exception for KBE API."""
    pass

class EntityNotFoundError(KBEException):
    """Entity not found in knowledge base."""
    pass

# Usage
@app.get("/entities/{uri}")
async def get_entity(uri: str):
    try:
        entity = await entity_service.get(uri)
        return APIResponse(success=True, data=entity)
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Entity not found")
```

### Logging

Use structured logging:

```python
import structlog

logger = structlog.get_logger()

async def process_action(action_id: str):
    logger.info("processing_action", action_id=action_id)
    try:
        result = await execute_action(action_id)
        logger.info("action_completed", action_id=action_id, duration_ms=result.execution_time_ms)
    except Exception as e:
        logger.error("action_failed", action_id=action_id, error=str(e))
        raise
```

## Testing Strategy

### Unit Tests

Test individual components in isolation:

```python
# tests/unit/test_models.py
def test_action_request_validation():
    request = ActionRequest(
        action_type="inference",
        parameters=[
            ActionParameter(name="entity", value="Building", type="string")
        ]
    )
    assert request.action_type == ActionType.INFERENCE
    assert len(request.parameters) == 1
```

### Integration Tests

Test API endpoints end-to-end:

```python
# tests/integration/test_api.py
from fastapi.testclient import TestClient

def test_execute_action_endpoint(client: TestClient):
    response = client.post(
        "/api/v1/actions/execute",
        json={
            "action_type": "inference",
            "parameters": [
                {"name": "entity", "value": "Building", "type": "string"}
            ]
        }
    )
    assert response.status_code == 202
    assert "action_id" in response.json()["data"]
```

### Test Fixtures

Use pytest fixtures for common setup:

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from kbe_api.main import app

@pytest.fixture
def client():
    """Test client for API."""
    return TestClient(app)

@pytest.fixture
def sample_entity():
    """Sample entity for testing."""
    return KnowledgeEntity(
        uri="http://example.org/kbe#Test",
        type=EntityType.INSTANCE,
        label="Test Entity"
    )
```

## Database Migrations (RDF)

### Loading Ontologies

```python
# scripts/load_ontology.py
from rdflib import Graph

def load_ontology(file_path: str):
    """Load ontology into knowledge base."""
    g = Graph()
    g.parse(file_path, format="turtle")
    # Store in persistent store
    pass
```

### Exporting Data

```bash
# Export knowledge base
python scripts/export_kb.py --format turtle --output data/export.ttl
```

## Performance Optimization

### Caching

Use Redis for caching:

```python
from functools import lru_cache
import redis

# Simple in-memory cache
@lru_cache(maxsize=1000)
def get_entity_cached(uri: str) -> KnowledgeEntity:
    return get_entity(uri)

# Redis cache
redis_client = redis.Redis(host='localhost', port=6379, db=0)

async def get_entity_with_redis(uri: str) -> KnowledgeEntity:
    cached = redis_client.get(f"entity:{uri}")
    if cached:
        return KnowledgeEntity.model_validate_json(cached)

    entity = await get_entity(uri)
    redis_client.setex(
        f"entity:{uri}",
        3600,  # 1 hour TTL
        entity.model_dump_json()
    )
    return entity
```

### Database Optimization

```python
# Use connection pooling
from rdflib.plugins.stores.sparqlstore import SPARQLStore

store = SPARQLStore(
    query_endpoint="http://localhost:3030/kbe/query",
    update_endpoint="http://localhost:3030/kbe/update"
)
```

### Async Operations

```python
import asyncio

# Execute tasks concurrently
async def process_multiple_entities(uris: List[str]):
    tasks = [fetch_entity(uri) for uri in uris]
    return await asyncio.gather(*tasks)
```

## Debugging

### Local Development

```bash
# Run with debugger
python -m debugpy --listen 5678 -m uvicorn src.kbe_api.main:app --reload

# Or use IDE debugging (VS Code, PyCharm)
```

### Logging

```python
# Enable debug logging
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("kbe_api")
```

### FastAPI Debug Mode

```python
# main.py
app = FastAPI(debug=True)  # Enables auto-reload and detailed errors
```

## Deployment

### Docker

```dockerfile
# Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src/ ./src/

# Install dependencies
RUN uv pip install --system .

# Run application
CMD ["uvicorn", "src.kbe_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - RDF_STORE_PATH=/data/kb.ttl
    volumes:
      - ./data:/data

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

### Environment Variables

```bash
# Production .env
API_TITLE="KBE Actions API"
API_VERSION="0.1.0"
DEBUG=false
LOG_LEVEL="INFO"
SECRET_KEY="your-secret-key"
CORS_ORIGINS=["https://app.example.com"]
```

## Continuous Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - name: Install uv
        run: pip install uv
      - name: Install dependencies
        run: uv pip install -e ".[dev]"
      - name: Run tests
        run: pytest --cov
      - name: Lint
        run: ruff check .
      - name: Type check
        run: mypy src/
```

## Troubleshooting

### Common Issues

**Import errors:**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall package in editable mode
uv pip install -e .
```

**Port already in use:**
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn src.kbe_api.main:app --port 8001
```

**RDFLib errors:**
```bash
# Install additional RDF parsers if needed
uv pip install rdflib[sparql]
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [RDFLib Documentation](https://rdflib.readthedocs.io/)
- [uv Documentation](https://github.com/astral-sh/uv)
- [pytest Documentation](https://docs.pytest.org/)

## Getting Help

- Check documentation in `docs/`
- Review existing tests for examples
- Ask in team chat/discussions
- Create GitHub issue for bugs
