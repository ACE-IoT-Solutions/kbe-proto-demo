# KBE Action Execution API Design

## Architecture Overview

The KBE Action Execution API is built using FastAPI and follows a layered architecture:

```
┌─────────────────────────────────────┐
│         API Layer (FastAPI)         │
│  - actions.py (action execution)    │
│  - building.py (state management)   │
│  - audit.py (history & audit)       │
└─────────────────────────────────────┘
                 │
┌─────────────────────────────────────┐
│         Service Layer               │
│  - ActionExecutor (execution)       │
│  - ActionValidator (SHACL)          │
│  - StateManager (state tracking)    │
└─────────────────────────────────────┘
                 │
┌─────────────────────────────────────┐
│         Models Layer                │
│  - Pydantic models                  │
│  - Request/Response schemas         │
└─────────────────────────────────────┘
```

## Key Design Decisions

### 1. Async/Await Throughout

All operations use async/await for:
- Non-blocking I/O operations
- Concurrent request handling
- Future integration with async databases

### 2. SHACL-Style Validation

The `ActionValidator` implements ontology-based validation:
- Parameter type checking
- Range validation
- Enum constraints
- Zone capability checks
- Temporal constraints

### 3. State Management

The `StateManager` maintains:
- Current zone states
- State change history
- Audit trail of all actions
- Thread-safe operations via asyncio locks

### 4. Error Handling

Comprehensive error handling:
- Validation errors (400)
- Not found errors (404)
- Execution errors (500)
- Detailed error messages for debugging

## API Endpoints

### Action Endpoints (`/actions`)

- `POST /actions/execute` - Execute an action
- `POST /actions/validate` - Validate without executing
- `GET /actions/active` - Get currently executing actions
- `DELETE /actions/{action_id}` - Cancel an action
- `GET /actions/types` - Get supported action types

### Building Endpoints (`/building`)

- `GET /building/state` - Get all zones state
- `GET /building/zones/{zone_id}/state` - Get zone state
- `POST /building/zones/{zone_id}/initialize` - Initialize zone
- `GET /building/zones/{zone_id}/history` - Get state history
- `GET /building/statistics` - Get system statistics
- `GET /building/zones` - List all zones

### Audit Endpoints (`/audit`)

- `GET /audit/history` - Get action history with filters
- `GET /audit/actions/{action_id}` - Get action details
- `GET /audit/zones/{zone_id}/history` - Get zone action history
- `GET /audit/summary` - Get audit statistics
- `GET /audit/recent` - Get recent actions

## Supported Action Types

### 1. setTemperature
```json
{
  "action_type": "setTemperature",
  "target_zone": "zone-001",
  "parameters": {
    "setpoint": 72.0,
    "mode": "auto"
  }
}
```

### 2. setOccupancyMode
```json
{
  "action_type": "setOccupancyMode",
  "target_zone": "zone-001",
  "parameters": {
    "mode": "occupied"
  }
}
```

### 3. adjustVentilation
```json
{
  "action_type": "adjustVentilation",
  "target_zone": "zone-001",
  "parameters": {
    "rate": 500,
    "mode": "demand-based"
  }
}
```

### 4. enableEconomizer
```json
{
  "action_type": "enableEconomizer",
  "target_zone": "zone-001",
  "parameters": {
    "enabled": true,
    "min_outdoor_temp": 55,
    "max_outdoor_temp": 75
  }
}
```

### 5. setLightingLevel
```json
{
  "action_type": "setLightingLevel",
  "target_zone": "zone-001",
  "parameters": {
    "level": 75,
    "duration": 3600
  }
}
```

## Validation Rules

Each action type has validation rules defined in `ActionValidator`:

- **Type checking**: Parameters must match expected types
- **Range validation**: Numeric values must be within min/max bounds
- **Enum validation**: String values must be from allowed list
- **Required parameters**: All required params must be present
- **Zone capabilities**: Zone must support the action (placeholder)
- **Temporal constraints**: Rate limits and schedules (placeholder)

## State Management

### Zone State Structure

```json
{
  "zone_id": "zone-001",
  "timestamp": "2025-11-20T00:00:00Z",
  "state": {
    "temperature_setpoint": 72.0,
    "hvac_mode": "auto",
    "occupancy_mode": "occupied",
    "ventilation_rate": 500,
    "lighting_level": 75,
    "economizer_enabled": true,
    "last_updated": "2025-11-20T00:00:00Z",
    "last_action_id": "abc123"
  }
}
```

### State History

Each state change is recorded with:
- Zone ID
- Timestamp
- Action ID that caused the change
- Previous state
- New state
- Action parameters

### Audit Trail

Complete audit trail includes:
- Action ID
- Timestamp
- Action type
- Target zone
- User (if provided)
- Status
- Details (parameters and state changes)

## Security Considerations

### Current Implementation (Development)
- CORS enabled for all origins
- No authentication/authorization
- Global services (singleton pattern)

### Production Recommendations
1. **Authentication**: Add JWT or OAuth2
2. **Authorization**: Role-based access control
3. **CORS**: Restrict to specific origins
4. **Rate Limiting**: Prevent abuse
5. **Input Sanitization**: Additional validation
6. **HTTPS**: Require TLS
7. **Audit Logging**: Enhanced logging with user context

## Performance Considerations

### Async Operations
- All database/state operations are async
- Non-blocking request handling
- Concurrent action execution

### Caching Opportunities
- Validation rules (cached on startup)
- Zone capabilities (future)
- Recent state queries (future)

### Scalability
- Stateless API design
- Horizontal scaling ready
- Database migration needed for production
- Consider Redis for state caching

## Future Enhancements

### 1. Database Integration
- Replace in-memory state with PostgreSQL/MongoDB
- Add proper migrations
- Implement connection pooling

### 2. Real-time Updates
- WebSocket support for live state updates
- Event streaming for audit trail
- Action execution progress

### 3. Advanced Validation
- Load SHACL shapes from RDF store
- Dynamic validation rules
- Custom rule definitions

### 4. Integration
- BACnet protocol support
- MQTT for IoT devices
- External system callbacks

### 5. Analytics
- Action success/failure rates
- Performance metrics
- Predictive maintenance alerts

## Dependencies

Current minimal dependencies:
- **FastAPI**: Web framework
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server (development)

Future additions:
- **SQLAlchemy**: Database ORM
- **Redis**: Caching
- **Celery**: Background tasks
- **RDFLib**: Ontology handling

## Testing Strategy

### Unit Tests
- Service layer logic
- Validation rules
- State transitions

### Integration Tests
- API endpoint behavior
- Service coordination
- Error handling

### End-to-End Tests
- Complete action workflows
- Multi-step scenarios
- Concurrent operations

## Deployment

### Development
```bash
python src/main.py
# or
uvicorn src.main:app --reload
```

### Production
```bash
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Monitoring & Logging

### Current Logging
- INFO level for normal operations
- ERROR level for failures
- Detailed exception tracing

### Production Monitoring
- Application logs (structured JSON)
- Performance metrics (Prometheus)
- Request tracing (OpenTelemetry)
- Health checks and alerts

## Coordination with Other Agents

This API implementation coordinates with:
- **Models Agent**: Uses Pydantic models (placeholder created)
- **Testing Agent**: API ready for comprehensive testing
- **Documentation Agent**: Auto-generated OpenAPI docs

## Notes

- All file paths are absolute per project requirements
- No files saved to root folder
- Comprehensive error handling throughout
- Production-ready structure with clear extension points
