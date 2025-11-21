# KBE Actions API Design Specification

## API Overview

The KBE Actions API provides programmatic access to Knowledge-Based Engineering capabilities including action execution, knowledge base queries, and reasoning operations.

## Authentication

Currently designed for internal use. For production, consider JWT-based authentication:

```python
# Future implementation
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(credentials: HTTPCredentials = Depends(security)):
    # Validate JWT token
    pass
```

## Base URL

```
Development: http://localhost:8000/api/v1
Production:  https://api.example.com/api/v1
```

## Content Types

- Request: `application/json`
- Response: `application/json`

## Error Responses

All errors follow consistent format:

```json
{
  "success": false,
  "message": "Error description",
  "timestamp": "2024-11-20T19:00:00Z",
  "request_id": "req-123456",
  "error": {
    "code": "ERROR_CODE",
    "details": {}
  }
}
```

### HTTP Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created
- `400 Bad Request`: Invalid input
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

## Endpoints

### 1. Health & Status

#### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2024-11-20T19:00:00Z",
  "dependencies": {
    "rdf_store": "connected",
    "cache": "available"
  }
}
```

#### GET /version

API version information.

**Response:**
```json
{
  "api_version": "0.1.0",
  "python_version": "3.13.0",
  "fastapi_version": "0.115.0"
}
```

### 2. Actions

#### POST /actions/execute

Execute a KBE action.

**Request:**
```json
{
  "action_type": "inference",
  "parameters": [
    {
      "name": "entity",
      "value": "Building",
      "type": "string",
      "required": true
    }
  ],
  "context": {
    "building_id": "B123"
  },
  "metadata": {
    "source": "api",
    "user": "system"
  }
}
```

**Response (202 Accepted):**
```json
{
  "success": true,
  "data": {
    "action_id": "act-7a8b9c0d",
    "status": "pending",
    "result": null,
    "error": null,
    "execution_time_ms": 0,
    "timestamp": "2024-11-20T19:00:00Z"
  },
  "message": "Action queued for execution",
  "timestamp": "2024-11-20T19:00:00Z",
  "request_id": "req-123456"
}
```

#### GET /actions/{action_id}

Get action execution status and results.

**Response:**
```json
{
  "success": true,
  "data": {
    "action_id": "act-7a8b9c0d",
    "status": "completed",
    "result": {
      "inferred_facts": [
        {
          "subject": "http://example.org/kbe#Building_B123",
          "predicate": "http://example.org/kbe#hasType",
          "object": "http://example.org/kbe#CommercialBuilding"
        }
      ]
    },
    "error": null,
    "execution_time_ms": 345,
    "timestamp": "2024-11-20T19:00:01Z"
  }
}
```

#### GET /actions

List recent actions with pagination.

**Query Parameters:**
- `page` (int, default=1): Page number
- `page_size` (int, default=20): Items per page
- `status` (string, optional): Filter by status

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "action_id": "act-7a8b9c0d",
        "action_type": "inference",
        "status": "completed",
        "timestamp": "2024-11-20T19:00:00Z"
      }
    ],
    "total": 42,
    "page": 1,
    "page_size": 20,
    "has_next": true,
    "has_previous": false
  }
}
```

### 3. Knowledge Base

#### POST /knowledge/query

Execute SPARQL query against knowledge base.

**Request:**
```json
{
  "query": "SELECT ?subject ?predicate ?object WHERE { ?subject ?predicate ?object } LIMIT 10",
  "limit": 10,
  "offset": 0,
  "format": "json"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "subject": "http://example.org/kbe#Building_B123",
        "predicate": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
        "object": "http://example.org/kbe#Building"
      }
    ],
    "count": 10,
    "execution_time_ms": 23
  }
}
```

#### GET /knowledge/entities

List entities in knowledge base.

**Query Parameters:**
- `type` (string, optional): Filter by entity type
- `page` (int, default=1): Page number
- `page_size` (int, default=50): Items per page

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "uri": "http://example.org/kbe#Building_B123",
        "type": "instance",
        "label": "Building B123",
        "properties": {
          "floor_count": 5,
          "year_built": 2020
        },
        "relations": [
          {
            "predicate": "locatedIn",
            "object": "http://example.org/kbe#City_NYC"
          }
        ]
      }
    ],
    "total": 156,
    "page": 1,
    "page_size": 50,
    "has_next": true,
    "has_previous": false
  }
}
```

#### GET /knowledge/entities/{uri}

Get detailed information about a specific entity.

**Response:**
```json
{
  "success": true,
  "data": {
    "uri": "http://example.org/kbe#Building_B123",
    "type": "instance",
    "label": "Building B123",
    "properties": {
      "floor_count": 5,
      "year_built": 2020,
      "square_footage": 50000
    },
    "relations": [
      {
        "predicate": "locatedIn",
        "object": "http://example.org/kbe#City_NYC",
        "label": "located in New York City"
      },
      {
        "predicate": "hasOwner",
        "object": "http://example.org/kbe#Company_XYZ",
        "label": "owned by XYZ Company"
      }
    ]
  }
}
```

#### POST /knowledge/entities

Create a new entity in the knowledge base.

**Request:**
```json
{
  "type": "instance",
  "label": "Building B456",
  "properties": {
    "floor_count": 3,
    "year_built": 2023
  },
  "relations": [
    {
      "predicate": "locatedIn",
      "object": "http://example.org/kbe#City_SF"
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "uri": "http://example.org/kbe#Building_B456",
    "type": "instance",
    "label": "Building B456",
    "properties": {
      "floor_count": 3,
      "year_built": 2023
    },
    "relations": [
      {
        "predicate": "locatedIn",
        "object": "http://example.org/kbe#City_SF"
      }
    ]
  },
  "message": "Entity created successfully"
}
```

### 4. Reasoning

#### POST /reasoning/infer

Execute inference operation.

**Request:**
```json
{
  "reasoning_type": "deductive",
  "input_entities": [
    "http://example.org/kbe#Building_B123"
  ],
  "rules": ["rule-001", "rule-002"],
  "depth": 3
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "inferred_facts": [
      {
        "subject": "http://example.org/kbe#Building_B123",
        "predicate": "http://example.org/kbe#requiresMaintenance",
        "object": "true",
        "justification": "Building age > 3 years"
      }
    ],
    "applied_rules": ["rule-001", "rule-003"],
    "confidence_scores": {
      "http://example.org/kbe#Building_B123/requiresMaintenance": 0.95
    },
    "reasoning_path": [
      "rule-001: Building age check",
      "rule-003: Maintenance schedule inference"
    ]
  }
}
```

#### GET /reasoning/rules

List available inference rules.

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "rule_id": "rule-001",
        "name": "Building Age Check",
        "description": "Infer maintenance requirements based on building age",
        "premise": "Building.year_built < current_year - 3",
        "conclusion": "Building.requiresMaintenance = true",
        "confidence": 0.95
      }
    ],
    "total": 25,
    "page": 1,
    "page_size": 50
  }
}
```

#### POST /reasoning/rules

Create new inference rule.

**Request:**
```json
{
  "name": "Energy Efficiency Check",
  "description": "Classify buildings by energy efficiency",
  "premise": "Building.energy_consumption < 50",
  "conclusion": "Building.energy_rating = 'A'",
  "confidence": 0.90
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "rule_id": "rule-026",
    "name": "Energy Efficiency Check",
    "description": "Classify buildings by energy efficiency",
    "premise": "Building.energy_consumption < 50",
    "conclusion": "Building.energy_rating = 'A'",
    "confidence": 0.90
  },
  "message": "Rule created successfully"
}
```

## Rate Limiting

For production deployment, implement rate limiting:

```python
from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/v1/actions")
@limiter.limit("100/minute")
async def list_actions(request: Request):
    pass
```

## WebSocket Support (Future)

For real-time updates on long-running actions:

```python
from fastapi import WebSocket

@app.websocket("/ws/actions/{action_id}")
async def action_status_ws(websocket: WebSocket, action_id: str):
    await websocket.accept()
    # Stream action progress updates
    pass
```

## API Versioning Strategy

- **URL-based versioning**: `/api/v1/`, `/api/v2/`
- **Deprecation policy**: Support N-1 versions for 6 months
- **Version header**: Optional `X-API-Version` header support

## OpenAPI Documentation

FastAPI automatically generates:
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Example Client Usage

### Python with httpx

```python
import httpx

async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
    # Execute action
    response = await client.post(
        "/api/v1/actions/execute",
        json={
            "action_type": "inference",
            "parameters": [
                {"name": "entity", "value": "Building", "type": "string"}
            ]
        }
    )
    action_result = response.json()
    action_id = action_result["data"]["action_id"]

    # Check status
    status = await client.get(f"/api/v1/actions/{action_id}")
    print(status.json())
```

### cURL

```bash
# Execute action
curl -X POST http://localhost:8000/api/v1/actions/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "inference",
    "parameters": [
      {"name": "entity", "value": "Building", "type": "string"}
    ]
  }'

# Query knowledge base
curl -X POST http://localhost:8000/api/v1/knowledge/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10"
  }'
```

## Performance Considerations

- **Response Time SLA**:
  - Simple queries: < 100ms
  - Complex inference: < 5s
  - Batch operations: < 30s

- **Caching Strategy**:
  - Cache SPARQL queries for 1 hour
  - Cache entity lookups for 30 minutes
  - Invalidate on updates

- **Async Operations**:
  - Long-running actions executed asynchronously
  - Status polling or WebSocket for updates
  - Background task queue (optional: Celery/Redis)

## Security Considerations

1. **Input Validation**: All inputs validated via Pydantic
2. **SPARQL Injection**: Parameterized queries only
3. **Rate Limiting**: Per-IP and per-user limits
4. **CORS**: Restricted to known origins
5. **HTTPS**: Required in production
6. **Authentication**: JWT tokens (future implementation)
