# Quick Reference - KBE Actions API

## 🚀 Getting Started (5 minutes)

```bash
# 1. Setup environment
uv venv && source .venv/bin/activate

# 2. Install dependencies
uv pip install -e ".[dev]"

# 3. Configure
cp .env.example .env

# 4. Run server
uvicorn src.kbe_api.main:app --reload
```

**API Docs:** http://localhost:8000/api/docs

## 📁 Project Structure

```
src/kbe_api/
├── main.py              # FastAPI app entry
├── config.py            # Settings
├── api/v1/endpoints/    # API routes
├── models/              # Pydantic models
├── services/            # Business logic
├── repositories/        # Data access
└── core/                # KBE logic
```

## 📊 Key Models

```python
# Action Request
POST /api/v1/actions/execute
{
  "action_type": "inference",
  "parameters": [{"name": "entity", "value": "Building", "type": "string"}]
}

# Knowledge Query
POST /api/v1/knowledge/query
{
  "query": "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10"
}

# Reasoning Request
POST /api/v1/reasoning/infer
{
  "reasoning_type": "deductive",
  "input_entities": ["http://example.org/kbe#Building_B123"]
}
```

## 🔌 API Endpoints (19 total)

### Health (4)
- `GET /health` - Health check
- `GET /health/ready` - Readiness
- `GET /health/live` - Liveness
- `GET /version` - Version info

### Actions (4)
- `POST /actions/execute` - Execute action
- `GET /actions/{id}` - Get status
- `GET /actions` - List actions
- `DELETE /actions/{id}` - Cancel

### Knowledge (6)
- `POST /knowledge/query` - SPARQL query
- `GET /knowledge/entities` - List entities
- `GET /knowledge/entities/{uri}` - Get entity
- `POST /knowledge/entities` - Create
- `PUT /knowledge/entities/{uri}` - Update
- `DELETE /knowledge/entities/{uri}` - Delete

### Reasoning (5)
- `POST /reasoning/infer` - Execute inference
- `GET /reasoning/rules` - List rules
- `GET /reasoning/rules/{id}` - Get rule
- `POST /reasoning/rules` - Create rule
- `PUT /reasoning/rules/{id}` - Update rule

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src/kbe_api --cov-report=html

# Unit tests only
pytest tests/unit/

# Watch mode
pytest-watch
```

## 🎨 Code Quality

```bash
# Format
ruff format .

# Lint
ruff check .

# Type check
mypy src/

# All checks
ruff check . && ruff format --check . && mypy src/
```

## 📦 Dependencies

### Core
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **pydantic** - Data validation
- **rdflib** - RDF operations

### Dev
- **pytest** - Testing
- **ruff** - Linting
- **mypy** - Type checking

## 🏗️ Architecture Layers

```
API Layer (FastAPI endpoints)
    ↓
Service Layer (Business logic)
    ↓
Repository Layer (Data access)
    ↓
Core Layer (KBE logic)
```

## 💾 Pydantic Models (12+)

- **Action**: `ActionRequest`, `ActionResult`, `ActionParameter`
- **Knowledge**: `KnowledgeEntity`, `QueryRequest`, `QueryResponse`
- **Reasoning**: `ReasoningRequest`, `InferenceResult`, `InferenceRule`
- **Common**: `APIResponse[T]`, `PaginatedResponse[T]`, `HealthCheck`

## 🔐 Environment Variables

```env
API_TITLE="KBE Actions API"
API_PORT=8000
DEBUG=true
RDF_STORE_PATH="data/knowledge_base.ttl"
RDF_NAMESPACE="http://example.org/kbe#"
```

## 📖 Documentation

- **Architecture**: `docs/architecture.md` - Complete design
- **API Design**: `docs/api_design.md` - API specifications
- **Development**: `docs/development.md` - Development guide
- **Summary**: `docs/ARCHITECTURE_SUMMARY.md` - Overview

## 🎯 Implementation Order

1. Create directory structure
2. Implement Pydantic models
3. Build repository layer (RDF)
4. Implement services (business logic)
5. Create API endpoints
6. Add configuration
7. Write tests
8. Add documentation

## 🐛 Common Commands

```bash
# Create directories
mkdir -p src/kbe_api/{api/v1/endpoints,models,services,repositories,core,utils}

# Run with auto-reload
uvicorn src.kbe_api.main:app --reload --port 8000

# Install new dependency
uv pip install package-name

# Update dependencies
uv pip compile pyproject.toml

# Export requirements
uv pip freeze > requirements.txt
```

## 🧠 Coordination Memory Keys

- `hive/code/architecture` - Project structure and design
- `hive/code/dependencies` - Dependency list
- `hive/code/next_steps` - Implementation roadmap

Query with:
```bash
npx claude-flow@alpha memory query "architecture" --namespace coordination
```

## 📞 API Client Examples

### Python (httpx)
```python
import httpx

async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
    response = await client.post(
        "/api/v1/actions/execute",
        json={"action_type": "inference", "parameters": [...]}
    )
```

### cURL
```bash
curl -X POST http://localhost:8000/api/v1/actions/execute \
  -H "Content-Type: application/json" \
  -d '{"action_type": "inference", "parameters": [...]}'
```

## ⚡ Performance Targets

- Simple queries: **< 100ms**
- Complex inference: **< 5s**
- Batch operations: **< 30s**
- Test coverage: **> 80%**

## 🔗 Useful Links

- FastAPI Docs: https://fastapi.tiangolo.com/
- Pydantic Docs: https://docs.pydantic.dev/
- RDFLib Docs: https://rdflib.readthedocs.io/
- uv Docs: https://github.com/astral-sh/uv

## 🎓 Best Practices

✅ Use type hints everywhere
✅ Async for I/O operations
✅ Validate with Pydantic
✅ Write tests first (TDD)
✅ Keep functions small (<20 lines)
✅ Document with docstrings
✅ Handle errors gracefully
✅ Log structured data

## 📊 Status

- ✅ Architecture designed
- ✅ Models specified
- ✅ API endpoints defined
- ✅ Dependencies configured
- ✅ Documentation complete
- 🔄 Ready for implementation

---

**Next:** Start implementing Pydantic models in `src/kbe_api/models/`
