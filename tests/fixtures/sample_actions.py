"""
Sample action fixtures for testing.

Provides action definitions, requests, and expected results.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class ActionType(str, Enum):
    """Action types for KBE operations."""

    QUERY = "query"
    INFERENCE = "inference"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"


class ActionStatus(str, Enum):
    """Action execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ReasoningType(str, Enum):
    """Types of reasoning operations."""

    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    ANALOGICAL = "analogical"


@dataclass
class ActionParameter:
    """Represents a parameter for an action."""

    name: str
    value: Any
    param_type: str
    required: bool = True
    description: str = ""

    def __post_init__(self):
        """Validate parameter."""
        assert self.name.strip(), "Parameter name must not be empty"
        assert self.param_type in [
            "string",
            "integer",
            "float",
            "boolean",
            "array",
            "object",
        ], f"Invalid parameter type: {self.param_type}"


@dataclass
class ActionRequest:
    """Request to execute an action."""

    action_type: ActionType
    parameters: List[ActionParameter] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 30

    def __post_init__(self):
        """Validate action request."""
        assert self.timeout_seconds > 0, "Timeout must be positive"


@dataclass
class ActionResult:
    """Result of action execution."""

    action_id: str
    status: ActionStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    execution_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate action result."""
        assert self.action_id.strip(), "Action ID must not be empty"
        assert self.execution_time_ms >= 0, "Execution time must be non-negative"
        if self.status == ActionStatus.FAILED:
            assert self.error is not None, "Failed actions must have error details"


@dataclass
class InferenceRule:
    """Represents an inference rule."""

    rule_id: str
    name: str
    description: str
    premise: str
    conclusion: str
    confidence: float = 1.0
    reasoning_type: ReasoningType = ReasoningType.DEDUCTIVE

    def __post_init__(self):
        """Validate inference rule."""
        assert self.rule_id.strip(), "Rule ID must not be empty"
        assert self.name.strip(), "Rule name must not be empty"
        assert self.premise.strip(), "Premise must not be empty"
        assert self.conclusion.strip(), "Conclusion must not be empty"
        assert 0 <= self.confidence <= 1, "Confidence must be between 0 and 1"


@dataclass
class InferenceResult:
    """Result of an inference operation."""

    inferred_facts: List[Dict[str, Any]] = field(default_factory=list)
    applied_rules: List[str] = field(default_factory=list)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    reasoning_path: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    valid: bool
    issues: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    @property
    def has_issues(self) -> bool:
        """Check if validation has any issues."""
        return bool(self.issues)

    @property
    def has_warnings(self) -> bool:
        """Check if validation has warnings."""
        return bool(self.warnings)


def create_inference_action_request() -> ActionRequest:
    """Create a sample inference action request.

    Returns:
        ActionRequest: An inference action request for building maintenance check
    """
    return ActionRequest(
        action_type=ActionType.INFERENCE,
        parameters=[
            ActionParameter(
                name="building_id",
                value="BLDG-001",
                param_type="string",
                required=True,
                description="Building to analyze",
            ),
            ActionParameter(
                name="depth",
                value=3,
                param_type="integer",
                required=False,
                description="Inference depth",
            ),
        ],
        context={"source": "api", "user": "system"},
        metadata={"description": "Building maintenance requirement inference"},
        timeout_seconds=30,
    )


def create_validation_action_request() -> ActionRequest:
    """Create a sample validation action request.

    Returns:
        ActionRequest: A validation action request for building configuration
    """
    return ActionRequest(
        action_type=ActionType.VALIDATION,
        parameters=[
            ActionParameter(
                name="building_id",
                value="BLDG-001",
                param_type="string",
                required=True,
                description="Building to validate",
            ),
            ActionParameter(
                name="validation_rules",
                value=["zones", "equipment", "schedules"],
                param_type="array",
                required=False,
                description="Specific rules to validate",
            ),
        ],
        context={"validation_level": "strict"},
        timeout_seconds=30,
    )


def create_query_action_request() -> ActionRequest:
    """Create a sample SPARQL query action request.

    Returns:
        ActionRequest: A query action for knowledge base search
    """
    return ActionRequest(
        action_type=ActionType.QUERY,
        parameters=[
            ActionParameter(
                name="query",
                value="SELECT ?building ?zone WHERE { ?building hasZone ?zone }",
                param_type="string",
                required=True,
                description="SPARQL query",
            ),
            ActionParameter(
                name="limit",
                value=100,
                param_type="integer",
                required=False,
                description="Result limit",
            ),
        ],
        timeout_seconds=30,
    )


def create_transformation_action_request() -> ActionRequest:
    """Create a sample transformation action request.

    Returns:
        ActionRequest: A transformation action for data conversion
    """
    return ActionRequest(
        action_type=ActionType.TRANSFORMATION,
        parameters=[
            ActionParameter(
                name="source_format",
                value="json",
                param_type="string",
                required=True,
                description="Source data format",
            ),
            ActionParameter(
                name="target_format",
                value="rdf",
                param_type="string",
                required=True,
                description="Target data format",
            ),
            ActionParameter(
                name="data",
                value={"building_id": "BLDG-001", "name": "Sample Building"},
                param_type="object",
                required=True,
                description="Data to transform",
            ),
        ],
        timeout_seconds=60,
    )


def create_sample_inference_result() -> InferenceResult:
    """Create a sample inference result.

    Returns:
        InferenceResult: Results from building maintenance inference
    """
    return InferenceResult(
        inferred_facts=[
            {
                "subject": "BLDG-001",
                "predicate": "requiresMaintenance",
                "object": "true",
                "justification": "Building age > 3 years",
            },
            {
                "subject": "VAV-001",
                "predicate": "needsCalibration",
                "object": "true",
                "justification": "Last maintenance > 6 months ago",
            },
        ],
        applied_rules=["rule-001", "rule-003"],
        confidence_scores={
            "BLDG-001/requiresMaintenance": 0.95,
            "VAV-001/needsCalibration": 0.87,
        },
        reasoning_path=[
            "rule-001: Check building age",
            "rule-002: Check last maintenance date",
            "rule-003: Infer maintenance requirements",
        ],
    )


def create_sample_validation_result(valid: bool = True) -> ValidationResult:
    """Create a sample validation result.

    Args:
        valid: Whether validation passed

    Returns:
        ValidationResult: Validation results for building configuration
    """
    if valid:
        return ValidationResult(
            valid=True,
            issues=[],
            warnings=[],
            details={"zones_count": 4, "equipment_count": 10, "status": "All checks passed"},
        )
    else:
        return ValidationResult(
            valid=False,
            issues=[
                {
                    "type": "missing_equipment",
                    "message": "Zone 'Office A' missing VAV equipment",
                    "zone": "Office A",
                },
                {
                    "type": "invalid_schedule",
                    "message": "End time before start time in Conference Room schedule",
                    "zone": "Conference Room",
                },
            ],
            warnings=[
                {
                    "type": "low_efficiency",
                    "message": "Fan efficiency below 80%",
                    "equipment": "FAN-001",
                    "efficiency": 75,
                }
            ],
            details={"validation_level": "strict", "timestamp": datetime.utcnow().isoformat()},
        )


def create_sample_inference_rules() -> List[InferenceRule]:
    """Create a set of sample inference rules.

    Returns:
        List[InferenceRule]: Collection of building maintenance rules
    """
    return [
        InferenceRule(
            rule_id="rule-001",
            name="Building Age Check",
            description="Infer maintenance requirements based on building age",
            premise="Building.year_built < current_year - 3",
            conclusion="Building.requiresMaintenance = true",
            confidence=0.95,
            reasoning_type=ReasoningType.DEDUCTIVE,
        ),
        InferenceRule(
            rule_id="rule-002",
            name="Equipment Maintenance Schedule",
            description="Check if equipment maintenance is overdue",
            premise="Equipment.last_maintenance_date < current_date - 6months",
            conclusion="Equipment.needsMaintenance = true",
            confidence=0.99,
            reasoning_type=ReasoningType.DEDUCTIVE,
        ),
        InferenceRule(
            rule_id="rule-003",
            name="Energy Efficiency Classification",
            description="Classify building energy efficiency",
            premise="Building.annual_energy_per_area < 200 kWh/m²",
            conclusion="Building.energy_rating = 'A'",
            confidence=0.85,
            reasoning_type=ReasoningType.DEDUCTIVE,
        ),
        InferenceRule(
            rule_id="rule-004",
            name="Zone Occupancy Inference",
            description="Infer zone occupancy from sensor data",
            premise="Zone.motion_detected AND Zone.co2_level > 600",
            conclusion="Zone.occupied = true",
            confidence=0.90,
            reasoning_type=ReasoningType.INDUCTIVE,
        ),
        InferenceRule(
            rule_id="rule-005",
            name="Equipment Failure Prediction",
            description="Predict equipment failure from trend analysis",
            premise="Equipment.vibration_trend = increasing AND Equipment.temperature_trend = increasing",
            conclusion="Equipment.failure_risk = high",
            confidence=0.75,
            reasoning_type=ReasoningType.INDUCTIVE,
        ),
    ]


def create_sample_successful_action_result() -> ActionResult:
    """Create a sample successful action result.

    Returns:
        ActionResult: A completed action with results
    """
    return ActionResult(
        action_id="act-001",
        status=ActionStatus.COMPLETED,
        result={
            "inferred_facts": 3,
            "applied_rules": 2,
            "confidence": 0.92,
        },
        error=None,
        execution_time_ms=245.5,
        timestamp=datetime.utcnow(),
    )


def create_sample_failed_action_result() -> ActionResult:
    """Create a sample failed action result.

    Returns:
        ActionResult: A failed action with error details
    """
    return ActionResult(
        action_id="act-002",
        status=ActionStatus.FAILED,
        result=None,
        error={
            "code": "INVALID_PARAMETER",
            "message": "Building ID 'BLDG-999' not found",
            "details": {"building_id": "BLDG-999"},
        },
        execution_time_ms=123.0,
        timestamp=datetime.utcnow(),
    )


def create_sample_pending_action_result() -> ActionResult:
    """Create a sample pending action result.

    Returns:
        ActionResult: A pending action awaiting execution
    """
    return ActionResult(
        action_id="act-003",
        status=ActionStatus.PENDING,
        result=None,
        error=None,
        execution_time_ms=0.0,
        timestamp=datetime.utcnow(),
    )
