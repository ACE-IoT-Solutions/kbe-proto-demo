"""
KBE PoC Models Package

This package contains Pydantic models for the Knowledge-Based Engine Proof of Concept.
Includes building infrastructure models and action definition/execution models.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from .building import Building, Zone, Equipment
from .kbe_actions import (
    ActionDefinition,
    ActionExecution,
    ActionInput,
    SideEffect,
)


# API Request/Response Models for FastAPI endpoints
class ActionRequest(BaseModel):
    """Request model for action execution."""
    action_type: str = Field(..., description="Type of action to execute")
    target_zone: str = Field(..., description="Target zone ID")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ActionResponse(BaseModel):
    """Response model for action execution."""
    action_id: str = Field(..., description="Unique action identifier")
    status: str = Field(..., description="Execution status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    result: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None


class ValidationRequest(BaseModel):
    """Request model for action validation."""
    action_type: str
    parameters: Dict[str, Any]
    target_zone: str


class ValidationResponse(BaseModel):
    """Response model for validation."""
    is_valid: bool
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None


class BuildingState(BaseModel):
    """Model for building/zone state."""
    zone_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    state: Dict[str, Any] = Field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = None


class AuditEntry(BaseModel):
    """Model for audit trail entries."""
    action_id: str
    timestamp: datetime
    action_type: str
    target_zone: str
    user: Optional[str] = None
    status: str
    details: Optional[Dict[str, Any]] = None


__all__ = [
    # Building infrastructure models
    "Building",
    "Zone",
    "Equipment",
    # Action models
    "ActionDefinition",
    "ActionExecution",
    "ActionInput",
    "SideEffect",
    # API models
    "ActionRequest",
    "ActionResponse",
    "ValidationRequest",
    "ValidationResponse",
    "BuildingState",
    "AuditEntry",
]
