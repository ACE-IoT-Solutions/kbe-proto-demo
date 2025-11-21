# KBE PoC Demo Portal

**Knowledge-Based Engineering (KBE) Proof-of-Concept** - Demonstrating how to transform passive building ontologies (Brick/REC) into active operational systems with Palantir-style kinetic capabilities.

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-E92063.svg)](https://docs.pydantic.dev)
[![Tests: 232 Passing](https://img.shields.io/badge/tests-232%20passing-success)](./tests/TEST_SUMMARY.md)
[![Coverage: >85%](https://img.shields.io/badge/coverage-%3E85%25-success)](./tests/TEST_SUMMARY.md)

## Overview

This demo portal showcases a complete Knowledge-Based Engineering system for building automation, featuring:

- **ActionDefinition Templates** - Reusable operation specifications with SHACL-style validation
- **ActionExecution Instances** - Reified transactions with complete audit trails
- **ODRL Governance** - Role-based access control and permission policies
- **Interactive Knowledge Graph** - D3.js visualization of ontology relationships
- **Real-time Validation** - Client-side constraint enforcement with violation reporting

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Using Make (easiest)
make quick-start

# Or using Docker Compose
docker compose up -d

# Or using Docker CLI
docker build -t kbe-demo-portal .
docker run -d -p 8008:8008 kbe-demo-portal
```

**Access at**: http://localhost:8008

### Option 2: Local Development

**Prerequisites**: Python 3.13, [uv](https://github.com/astral-sh/uv)

```bash
# Install dependencies
uv sync

# Run development server
uv run python src/main.py

# Or using uvicorn directly
uv run uvicorn src.main:app --reload --port 8008
```

## Key Features

### 1. Building Automation System

- **5-Zone Building Model** (Z001-Z005)
  - HVAC zones with temperature control
  - Occupancy tracking
  - Power usage monitoring
- **FastAPI REST API** - 16 endpoints
- **Thread-safe State Management** - Async/await throughout
- **Pydantic v2 Validation** - Type-safe models

### 2. KBE Actions Framework

**Available Actions:**
- **Adjust Temperature Setpoint** - Modify zone setpoints with validation
- **Load Shed** - Demand management through lighting reduction
- **Pre-Cooling** - Optimize peak demand costs through strategic pre-cooling

**Action Properties:**
- SHACL-style validation rules (60-80F range, max 15F delta)
- ODRL governance policies
- Side effects tracking (HVAC mode changes, power consumption, audit logs)
- Complete audit trail with violation logging

### 3. Validation & Security

**SHACL Constraints:**
- **Adjust Setpoint**: 60-80F range, max 15F delta, operator 5F limit
- **Load Shed**: Levels 1-5, max 240 min duration, level 4-5 max 120 min
- **Pre-Cooling**: 60-75F target, 30 min - 8 hour window, max 10F/hr cooling rate

**ODRL Policies:**
- **Operator**: Basic setpoint controls (5F limit), no load shed or pre-cooling
- **Facility Manager**: Full setpoint access, shed levels 1-3, pre-cooling (3 zones max, $50 cost limit)
- **Energy Manager**: Full access to all actions including high shed levels (4-5) and unrestricted pre-cooling
- **Contractor**: Limited setpoint access, no emergency actions, no optimization features

**Security Features:**
- Failed action logging for security monitoring
- Comprehensive violation collection and reporting
- Role-based access control enforcement
- Audit trail with full KBE ontology exposure

### 4. Interactive Knowledge Graph

Visualize the complete semantic structure:

- **31 Nodes**: Brick classes, KBE actions, properties, constraints, policies, roles
- **43 Relationships**: Composition, validation, permissions, enforcement
- **3 Layout Modes**: Force-Directed, Hierarchical, Radial
- **Filtering**: View by node type (all/classes/actions/properties)
- **Interactive**: Click to select, drag to reposition, zoom/pan
- **Export**: Download as SVG

Access at: http://localhost:8008/static/graph.html

## Documentation

- **[Architecture Summary](./docs/ARCHITECTURE_SUMMARY.md)** - System design and components
- **[API Design](./docs/api-design.md)** - REST endpoint specifications
- **[Building Model](./docs/building-model-design.md)** - Zone and equipment details
- **[Test Summary](./tests/TEST_SUMMARY.md)** - Test coverage report (232 tests)
- **[Graph Visualization](./docs/GRAPH_VISUALIZATION.md)** - Knowledge graph guide
- **[Docker Guide](./DOCKER.md)** - Container deployment instructions

## Development

### Run Tests

```bash
# All tests (232 tests)
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=html

# Specific test file
uv run pytest tests/test_api/test_actions_endpoints.py -v
```

### Code Quality

```bash
# Lint
uv run ruff check src/

# Format
uv run ruff format src/

# Type checking
uv run mypy src/
```

### Make Commands

```bash
make help           # Show all available commands
make build          # Build Docker image
make run            # Run container
make test           # Run tests in container
make logs           # View container logs
make shell          # Access container shell
make clean          # Remove container and image
```

## Architecture

```
src/
 api/              # REST API endpoints
    actions.py    # Action execution endpoints (5)
    building.py   # Building state endpoints (6)
    audit.py      # Audit trail endpoints (5)
 models/           # Pydantic models
    building.py   # Building, Zone, Equipment
    kbe_actions.py # ActionDefinition, ActionExecution
    actions/      # Specific action types
 services/         # Business logic
    action_executor.py  # Core execution engine
    validator.py        # SHACL validation
    state_manager.py    # State management
 static/           # Web UI
    index.html    # Demo portal
    graph.html    # Knowledge graph
 main.py          # FastAPI application
```

## API Endpoints

### System
- `GET /` - Demo portal web UI
- `GET /health` - Health check
- `GET /docs` - OpenAPI documentation
- `GET /redoc` - ReDoc documentation

### Actions
- `POST /actions/execute` - Execute an action
- `POST /actions/validate` - Validate action parameters
- `GET /actions/active` - List active actions
- `POST /actions/{action_id}/cancel` - Cancel an action
- `GET /actions/types` - List available action types

### Building
- `GET /building/state` - Get all zone states
- `GET /building/zones/{zone_id}/state` - Get zone state
- `POST /building/zones/{zone_id}/initialize` - Initialize zone
- `GET /building/zones/{zone_id}/history` - Get state history
- `GET /building/statistics` - Get system statistics
- `GET /building/zones` - List all zones

### Audit
- `GET /audit/history` - Get action history
- `GET /audit/{action_id}` - Get action details
- `GET /audit/zone/{zone_id}` - Get zone audit trail
- `GET /audit/summary` - Get audit summary
- `GET /audit/recent` - Get recent actions

## Testing

**Test Coverage**: 232 tests, >85% coverage

```
tests/
 test_models/           # Model validation tests (141)
    test_building.py
    test_kbe_actions.py
    test_action_validation.py
 test_api/             # API endpoint tests (76)
    test_actions_endpoints.py
    test_building_endpoints.py
    test_audit_endpoints.py
 test_services/        # Service logic tests (15)
     test_action_executor.py
     test_validator.py
```

## Demo Scenarios

### Scenario 1: Adjust Temperature Setpoint

1. Select zone (Z001-Z005)
2. Choose user role (Operator/Facility Manager/Energy Manager/Contractor)
3. Set new temperature setpoint
4. Select priority level
5. Execute action
6. View validation results and audit trail

**Try these violations:**
- Operator trying to change >5F (denied)
- Contractor trying emergency priority (denied)
- Anyone trying to set outside 60-80F range (denied)

### Scenario 2: Load Shed Event

1. Switch to "Load Shed" action
2. Select shed level (1-5)
3. Set duration (max 240 min)
4. Energy Manager can execute level 4-5
5. Other roles limited to level 1-3

### Scenario 3: Pre-Cooling Optimization

1. Switch to "Pre-Cooling" action
2. Set target temperature (60-75F)
3. Configure start time (e.g., 05:00) and occupancy time (e.g., 08:00)
4. Adjust max cooling rate (1-10F/hr)
5. Energy Manager has full access
6. Facility Manager limited to 3 zones and $50 cost
7. Operators and Contractors denied access

**Try these violations:**
- Operator trying to execute (denied - requires optimization expertise)
- Facility Manager with 4+ zones (denied - 3 zone limit)
- Target temp below 62F (denied - too aggressive for economics)
- Time window less than 30 min (denied - insufficient pre-cooling time)

## Docker Details

**Base Image**: `ghcr.io/astral-sh/uv:python3.13-bookworm-slim`

**Features**:
- Multi-stage build for optimal size (~150-200MB final image)
- UV for 150x faster dependency installation
- Non-root user for security
- Built-in health checks
- Bytecode compilation for faster startup

See [DOCKER.md](./DOCKER.md) for complete deployment guide.

## Configuration

### Environment Variables

```bash
ENV=production              # Environment (development/production)
LOG_LEVEL=info             # Logging level (debug/info/warning/error)
PORT=8008                  # Application port
```

### Port Configuration

The application runs on port **8008** by default (configurable in `src/main.py`).

## Technology Stack

- **Backend**: Python 3.13, FastAPI, Pydantic v2
- **Package Manager**: Astral UV
- **Frontend**: Vanilla JavaScript, D3.js v7, responsive CSS
- **Testing**: pytest, pytest-asyncio
- **Container**: Docker with multi-stage builds

## Contributing

This is a proof-of-concept demo built with the Hive Mind Collective Intelligence System.

### Development Process

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run test suite (`make test`)
5. Submit pull request

### Code Style

- Python 3.13+ type hints
- Pydantic v2 models
- FastAPI async/await patterns
- Maximum line length: 100 characters
- Docstrings for all public functions

## License

[Add your license here]

## Acknowledgments

- **Brick Schema** - Building ontology foundation
- **SHACL** - Validation constraint language
- **ODRL** - Open Digital Rights Language for policies
- **Astral UV** - Fast Python package management
- **FastAPI** - Modern web framework
- **D3.js** - Interactive graph visualization

## Built With Hive Mind

This project was built using the Hive Mind Collective Intelligence System, coordinating 4 specialized agents in parallel:

- **Researcher Agent** - Domain analysis and specifications
- **Coder Agent #1** - Pydantic model layer
- **Coder Agent #2** - FastAPI application layer
- **Tester Agent** - Comprehensive test suite

See [HIVE_SUMMARY.md](./HIVE_SUMMARY.md) for complete development details.

---

**Questions?** Check the [documentation](./docs/) or explore the [interactive graph](http://localhost:8008/static/graph.html) to understand the KBE framework.

## **Ready to explore?** Start the demo at http://localhost:8008

