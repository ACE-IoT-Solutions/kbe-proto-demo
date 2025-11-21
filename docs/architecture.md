# FastAPI Architecture for KBE Actions PoC Demo

## 1. Project Structure

```
kbe-proto-demo/
├── src/
│   ├── kbe_api/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application entry point
│   │   ├── config.py                  # Configuration management
│   │   ├── dependencies.py            # Dependency injection
│   │   │
│   │   ├── api/                       # API layer
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py          # Main API router
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── actions.py     # Action endpoints
│   │   │   │   │   ├── knowledge.py   # Knowledge base endpoints
│   │   │   │   │   ├── reasoning.py   # Reasoning endpoints
│   │   │   │   │   └── health.py      # Health check endpoints
│   │   │   │
│   │   ├── models/                    # Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── action.py              # Action models
│   │   │   ├── knowledge.py           # Knowledge models
│   │   │   ├── reasoning.py           # Reasoning models
│   │   │   ├── response.py            # Response wrappers
│   │   │   └── common.py              # Common/shared models
│   │   │
│   │   ├── services/                  # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── action_service.py      # Action execution service
│   │   │   ├── knowledge_service.py   # Knowledge base service
│   │   │   ├── reasoning_service.py   # Reasoning engine service
│   │   │   └── validation_service.py  # Validation service
│   │   │
│   │   ├── repositories/              # Data access layer
│   │   │   ├── __init__.py
│   │   │   ├── rdf_repository.py      # RDF graph operations
│   │   │   ├── cache_repository.py    # Caching layer
│   │   │   └── base.py                # Base repository
│   │   │
│   │   ├── core/                      # Core KBE logic
│   │   │   ├── __init__.py
│   │   │   ├── action_engine.py       # Action execution engine
│   │   │   ├── inference.py           # Inference engine
│   │   │   ├── ontology.py            # Ontology management
│   │   │   └── rules.py               # Rule engine
│   │   │
│   │   ├── schemas/                   # RDF schemas & ontologies
│   │   │   ├── __init__.py
│   │   │   ├── kbe_ontology.ttl       # Main KBE ontology
│   │   │   └── actions_schema.ttl     # Actions schema
│   │   │
│   │   └── utils/                     # Utilities
│   │       ├── __init__.py
│   │       ├── logging.py             # Logging configuration
│   │       ├── exceptions.py          # Custom exceptions
│   │       └── validators.py          # Custom validators
│   │
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Pytest configuration
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_core.py
│   ├── integration/
│   │   ├── test_api.py
│   │   └── test_workflows.py
│   └── fixtures/
│       └── sample_data.py
│
├── docs/
│   ├── architecture.md                # This file
│   ├── api_design.md                  # API specification
│   └── development.md                 # Development guide
│
├── scripts/
│   ├── setup_dev.sh                   # Development setup
│   └── run_tests.sh                   # Test runner
│
├── pyproject.toml
├── README.md
├── .env.example
└── .gitignore
```

## 2. Pydantic Models

### 2.1 Action Models (`models/action.py`)

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ActionType(str, Enum):
    """Types of KBE actions"""
    QUERY = "query"
    INFERENCE = "inference"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"

class ActionStatus(str, Enum):
    """Action execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ActionParameter(BaseModel):
    """Individual action parameter"""
    name: str = Field(..., description="Parameter name")
    value: Any = Field(..., description="Parameter value")
    type: str = Field(..., description="Parameter type")
    required: bool = Field(default=True)

class ActionRequest(BaseModel):
    """Request to execute an action"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "action_type": "inference",
            "parameters": [
                {"name": "entity", "value": "Building", "type": "string", "required": True}
            ],
            "context": {"building_id": "B123"}
        }
    })

    action_type: ActionType
    parameters: List[ActionParameter]
    context: Optional[Dict[str, Any]] = Field(default=None)
    metadata: Optional[Dict[str, str]] = Field(default=None)

class ActionResult(BaseModel):
    """Result of action execution"""
    action_id: str
    status: ActionStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

### 2.2 Knowledge Models (`models/knowledge.py`)

```python
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from enum import Enum

class EntityType(str, Enum):
    """Types of knowledge entities"""
    CONCEPT = "concept"
    INSTANCE = "instance"
    PROPERTY = "property"
    RELATION = "relation"

class KnowledgeEntity(BaseModel):
    """Represents a knowledge base entity"""
    uri: str = Field(..., description="Entity URI")
    type: EntityType
    label: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    relations: List[Dict[str, str]] = Field(default_factory=list)

class QueryRequest(BaseModel):
    """SPARQL query request"""
    query: str = Field(..., description="SPARQL query string")
    limit: Optional[int] = Field(default=100, ge=1, le=1000)
    offset: Optional[int] = Field(default=0, ge=0)
    format: str = Field(default="json", pattern="^(json|xml|turtle)$")

class QueryResponse(BaseModel):
    """SPARQL query response"""
    results: List[Dict[str, Any]]
    count: int
    execution_time_ms: int
```

### 2.3 Reasoning Models (`models/reasoning.py`)

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class ReasoningType(str, Enum):
    """Types of reasoning operations"""
    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    ANALOGICAL = "analogical"

class InferenceRule(BaseModel):
    """Represents an inference rule"""
    rule_id: str
    name: str
    description: Optional[str] = None
    premise: str = Field(..., description="Rule premise (IF condition)")
    conclusion: str = Field(..., description="Rule conclusion (THEN action)")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

class ReasoningRequest(BaseModel):
    """Request for reasoning operation"""
    reasoning_type: ReasoningType
    input_entities: List[str] = Field(..., description="Entity URIs to reason about")
    rules: Optional[List[str]] = Field(default=None, description="Rule IDs to apply")
    depth: int = Field(default=3, ge=1, le=10, description="Reasoning depth")

class InferenceResult(BaseModel):
    """Result of inference operation"""
    inferred_facts: List[Dict[str, Any]]
    applied_rules: List[str]
    confidence_scores: Dict[str, float]
    reasoning_path: List[str]
```

### 2.4 Common Models (`models/common.py`)

```python
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, List
from datetime import datetime

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None

class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""
    items: List[T]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool

class HealthCheck(BaseModel):
    """Health check response"""
    status: str = Field(default="healthy")
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    dependencies: Dict[str, str] = Field(default_factory=dict)
```

## 3. API Endpoint Design

### 3.1 Base URL Structure
```
http://localhost:8000/api/v1/
```

### 3.2 Endpoint Specifications

#### Health & Status
```
GET  /health                    - Health check
GET  /health/ready               - Readiness probe
GET  /health/live                - Liveness probe
GET  /version                    - API version info
```

#### Actions
```
POST   /actions/execute          - Execute an action
GET    /actions/{action_id}      - Get action status
GET    /actions                  - List recent actions
DELETE /actions/{action_id}      - Cancel action
```

#### Knowledge Base
```
GET    /knowledge/entities       - List entities
GET    /knowledge/entities/{uri} - Get entity details
POST   /knowledge/query          - Execute SPARQL query
POST   /knowledge/entities       - Create entity
PUT    /knowledge/entities/{uri} - Update entity
DELETE /knowledge/entities/{uri} - Delete entity
```

#### Reasoning
```
POST   /reasoning/infer          - Execute inference
GET    /reasoning/rules          - List inference rules
POST   /reasoning/rules          - Create rule
GET    /reasoning/rules/{rule_id}- Get rule details
PUT    /reasoning/rules/{rule_id}- Update rule
```

## 4. Technology Stack

### 4.1 Core Dependencies
```toml
[project]
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic>=2.12.4",
    "pydantic-settings>=2.7.0",
    "rdflib>=7.4.0",
    "python-multipart>=0.0.20",
    "python-jose[cryptography]>=3.3.0",  # For JWT
    "passlib[bcrypt]>=1.7.4",             # For password hashing
    "httpx>=0.28.0",                      # For async HTTP
]

[dependency-groups]
dev = [
    "pytest>=9.0.1",
    "pytest-asyncio>=0.25.0",
    "pytest-cov>=6.0.0",
    "httpx>=0.28.0",                      # For testing
    "ruff>=0.14.5",
    "mypy>=1.14.0",
    "pre-commit>=4.0.1",
]
```

### 4.2 Key Technologies

- **FastAPI**: Modern, fast web framework with automatic API documentation
- **Pydantic**: Data validation using Python type annotations
- **RDFLib**: RDF graph manipulation and SPARQL queries
- **Uvicorn**: ASGI server for production deployment
- **uv**: Fast Python package installer and environment manager
- **pytest**: Testing framework
- **Ruff**: Fast Python linter and formatter

## 5. Development Setup Instructions

### 5.1 Initial Setup

```bash
# 1. Ensure Python 3.13+ is installed
python --version

# 2. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 4. Install project dependencies
uv pip install -e ".[dev]"

# 5. Set up pre-commit hooks
pre-commit install

# 6. Copy environment template
cp .env.example .env
```

### 5.2 Configuration

Create `.env` file:
```env
# API Configuration
API_TITLE="KBE Actions API"
API_VERSION="0.1.0"
API_HOST="0.0.0.0"
API_PORT=8000
DEBUG=true

# Logging
LOG_LEVEL="INFO"
LOG_FORMAT="json"

# RDF Store
RDF_STORE_PATH="data/knowledge_base.ttl"
RDF_NAMESPACE="http://example.org/kbe#"

# Performance
MAX_WORKERS=4
CACHE_TTL=3600
```

### 5.3 Running the Application

```bash
# Development mode with auto-reload
uvicorn src.kbe_api.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn src.kbe_api.main:app --workers 4 --host 0.0.0.0 --port 8000

# Using the provided script
python -m src.kbe_api.main
```

### 5.4 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/kbe_api --cov-report=html

# Run specific test suite
pytest tests/unit/
pytest tests/integration/

# Run with verbose output
pytest -v
```

### 5.5 Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type checking
mypy src/

# Run all checks
ruff check . && ruff format --check . && mypy src/
```

## 6. FastAPI Application Structure

### 6.1 Main Application (`main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .api.v1.router import api_router
from .utils.logging import setup_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    setup_logging()
    # Initialize RDF store, load ontologies, etc.
    yield
    # Shutdown
    # Cleanup resources

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")
```

### 6.2 Configuration (`config.py`)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )

    # API Settings
    API_TITLE: str = "KBE Actions API"
    API_VERSION: str = "0.1.0"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = "change-me-in-production"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # RDF Settings
    RDF_STORE_PATH: str = "data/knowledge_base.ttl"
    RDF_NAMESPACE: str = "http://example.org/kbe#"

    # Performance
    MAX_WORKERS: int = 4
    CACHE_TTL: int = 3600

settings = Settings()
```

## 7. Best Practices

### 7.1 Code Organization
- **Separation of Concerns**: API, services, repositories, core logic
- **Dependency Injection**: Use FastAPI's dependency system
- **Type Safety**: Full type hints with Pydantic and mypy
- **Error Handling**: Custom exceptions with proper HTTP status codes

### 7.2 API Design
- **RESTful Principles**: Resource-based URLs, proper HTTP methods
- **Versioning**: URL-based versioning (/api/v1/)
- **Documentation**: Auto-generated with FastAPI + Pydantic
- **Validation**: Automatic with Pydantic models

### 7.3 Testing Strategy
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API endpoints end-to-end
- **Test Fixtures**: Reusable test data and mocks
- **Coverage**: Aim for >80% code coverage

### 7.4 Performance
- **Async/Await**: Use async for I/O operations
- **Caching**: Cache expensive operations (RDF queries)
- **Connection Pooling**: Reuse connections
- **Pagination**: Limit result sets

### 7.5 Security
- **Input Validation**: Automatic with Pydantic
- **CORS**: Properly configured
- **Rate Limiting**: Implement for production
- **Authentication**: JWT-based (if needed)

## 8. Next Steps

1. **Set up directory structure**: Create all necessary directories and `__init__.py` files
2. **Implement core models**: Start with Pydantic models
3. **Build repository layer**: RDF graph operations
4. **Implement services**: Business logic for actions and reasoning
5. **Create API endpoints**: RESTful endpoints with FastAPI
6. **Write tests**: Unit and integration tests
7. **Add documentation**: API docs and user guides
8. **Deploy**: Containerize with Docker

## 9. Architecture Decisions

### 9.1 Why FastAPI?
- Native async support
- Automatic API documentation (OpenAPI/Swagger)
- Built-in data validation with Pydantic
- High performance (on par with Node.js and Go)
- Modern Python features (type hints, async/await)

### 9.2 Why Layered Architecture?
- **API Layer**: HTTP handling, request/response transformation
- **Service Layer**: Business logic, orchestration
- **Repository Layer**: Data access, RDF operations
- **Core Layer**: KBE-specific logic (inference, rules)

### 9.3 Why RDFLib?
- Pure Python (no external dependencies)
- Supports multiple RDF formats
- Built-in SPARQL query support
- Active maintenance

### 9.4 Why uv?
- 10-100x faster than pip
- Drop-in replacement for pip
- Better dependency resolution
- Integrated virtual environment management
