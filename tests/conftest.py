"""
Pytest configuration and shared fixtures for all tests.
"""

import pytest
from typing import Generator
from datetime import datetime, time
from enum import Enum


class ActionType(str, Enum):
    """Enum for action types."""

    QUERY = "query"
    INFERENCE = "inference"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"


class ActionStatus(str, Enum):
    """Enum for action execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EntityType(str, Enum):
    """Enum for knowledge entity types."""

    CONCEPT = "concept"
    INSTANCE = "instance"
    PROPERTY = "property"
    RELATION = "relation"


class ReasoningType(str, Enum):
    """Enum for reasoning types."""

    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    ANALOGICAL = "analogical"


# Markers for test categorization
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "models: Model tests")
    config.addinivalue_line("markers", "api: API endpoint tests")
    config.addinivalue_line("markers", "services: Service tests")
    config.addinivalue_line("markers", "validation: Validation tests")


@pytest.fixture
def sample_action_type() -> ActionType:
    """Fixture for sample action type."""
    return ActionType.INFERENCE


@pytest.fixture
def sample_action_status() -> ActionStatus:
    """Fixture for sample action status."""
    return ActionStatus.PENDING


@pytest.fixture
def sample_entity_type() -> EntityType:
    """Fixture for sample entity type."""
    return EntityType.INSTANCE


@pytest.fixture
def sample_reasoning_type() -> ReasoningType:
    """Fixture for sample reasoning type."""
    return ReasoningType.DEDUCTIVE


@pytest.fixture
def sample_timestamp() -> datetime:
    """Fixture for sample timestamp."""
    return datetime(2024, 11, 20, 10, 30, 45)


@pytest.fixture
def sample_time() -> time:
    """Fixture for sample time of day."""
    return time(10, 30, 45)
