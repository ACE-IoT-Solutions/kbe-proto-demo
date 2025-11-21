"""
KBE Action Models

Pydantic models for Knowledge-Based Engine action definitions and execution.
Implements the core KBE specification for action lifecycle management.
"""

from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


class ActionInput(BaseModel):
    """
    Base model for action input validation.

    This base class should be extended by specific action input models
    to provide type-safe validation for action parameters.
    """

    class Config:
        extra = "forbid"  # Prevent unknown fields


class SideEffect(BaseModel):
    """
    Side effect model for webhooks, notifications, and other action triggers.

    Attributes:
        type: Type of side effect (webhook, notification, log, etc.)
        target: Target destination for the side effect
        payload: Optional payload data to send
        condition: Optional condition for triggering the side effect
    """

    type: Literal["webhook", "notification", "log", "email", "sms"] = Field(
        ...,
        description="Type of side effect"
    )
    target: str = Field(
        ...,
        min_length=1,
        description="Target destination (URL, email, phone, etc.)"
    )
    payload: dict[str, Any] | None = Field(
        default=None,
        description="Optional payload data"
    )
    condition: str | None = Field(
        default=None,
        description="Optional condition expression for triggering"
    )

    @field_validator("target")
    @classmethod
    def validate_target(cls, v: str, info) -> str:
        """
        Validate target based on side effect type.

        Args:
            v: Target string
            info: Validation context containing other field values

        Returns:
            Validated target string

        Raises:
            ValueError: If target format is invalid for the given type
        """
        effect_type = info.data.get("type")

        if effect_type == "webhook" and not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("Webhook target must be a valid HTTP/HTTPS URL")
        elif effect_type == "email" and "@" not in v:
            raise ValueError("Email target must contain @ symbol")

        return v.strip()


class ActionDefinition(BaseModel):
    """
    Action definition model matching KBE specification.

    Defines the structure and metadata for executable actions within the KBE system.

    Attributes:
        id: Unique action identifier
        name: Human-readable action name
        description: Detailed action description
        action_type: Category of action (control, optimization, diagnostic, etc.)
        input_schema: JSON Schema for validating action inputs
        preconditions: List of precondition expressions that must be true
        postconditions: List of expected postcondition expressions
        side_effects: List of side effects triggered by this action
        tags: Optional tags for categorization and search
        version: Action definition version string
        created_at: Timestamp of action creation
        updated_at: Timestamp of last update
    """

    id: str = Field(..., description="Unique action identifier")
    name: str = Field(..., min_length=1, description="Action name")
    description: str = Field(..., min_length=1, description="Action description")
    action_type: Literal[
        "control",
        "optimization",
        "diagnostic",
        "scheduling",
        "monitoring"
    ] = Field(..., description="Action category")
    input_schema: dict[str, Any] = Field(
        ...,
        description="JSON Schema for action inputs"
    )
    preconditions: list[str] = Field(
        default_factory=list,
        description="Precondition expressions"
    )
    postconditions: list[str] = Field(
        default_factory=list,
        description="Expected postcondition expressions"
    )
    side_effects: list[SideEffect] = Field(
        default_factory=list,
        description="Action side effects"
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Categorization tags"
    )
    version: str = Field(
        default="1.0.0",
        pattern=r"^\d+\.\d+\.\d+$",
        description="Semantic version string"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )

    @field_validator("input_schema")
    @classmethod
    def validate_input_schema(cls, v: dict[str, Any]) -> dict[str, Any]:
        """
        Validate that input_schema contains required JSON Schema fields.

        Args:
            v: Input schema dictionary

        Returns:
            Validated schema dictionary

        Raises:
            ValueError: If required schema fields are missing
        """
        if "type" not in v:
            raise ValueError("input_schema must contain 'type' field")
        if "properties" not in v and v.get("type") == "object":
            raise ValueError("Object type input_schema must contain 'properties' field")
        return v

    @model_validator(mode="after")
    def validate_timestamps(self) -> "ActionDefinition":
        """
        Validate that updated_at is not before created_at.

        Returns:
            Validated model instance

        Raises:
            ValueError: If updated_at precedes created_at
        """
        if self.updated_at < self.created_at:
            raise ValueError("updated_at cannot be before created_at")
        return self


class ActionExecution(BaseModel):
    """
    Action execution model tracking the lifecycle of action instances.

    Tracks the execution state, inputs, outputs, and metadata for action invocations.

    Attributes:
        id: Unique execution identifier
        action_id: Reference to the action definition
        status: Current execution status
        inputs: Validated input parameters
        outputs: Execution results (populated on completion)
        error_message: Error details if status is 'failed'
        started_at: Execution start timestamp
        completed_at: Execution completion timestamp (if finished)
        validation_errors: List of validation errors (if status is 'failed')
        retry_count: Number of retry attempts
        max_retries: Maximum allowed retries
    """

    id: str = Field(..., description="Unique execution identifier")
    action_id: str = Field(..., description="Reference to action definition")
    status: Literal[
        "pending",
        "validated",
        "executing",
        "completed",
        "failed"
    ] = Field(..., description="Execution status")
    inputs: dict[str, Any] = Field(
        default_factory=dict,
        description="Action input parameters"
    )
    outputs: dict[str, Any] | None = Field(
        default=None,
        description="Execution results"
    )
    error_message: str | None = Field(
        default=None,
        description="Error details if failed"
    )
    started_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Execution start time"
    )
    completed_at: datetime | None = Field(
        default=None,
        description="Execution completion time"
    )
    validation_errors: list[str] = Field(
        default_factory=list,
        description="Validation error messages"
    )
    retry_count: int = Field(
        default=0,
        ge=0,
        description="Number of retry attempts"
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts"
    )

    @model_validator(mode="after")
    def validate_execution_state(self) -> "ActionExecution":
        """
        Validate execution state consistency.

        Returns:
            Validated model instance

        Raises:
            ValueError: If state is inconsistent (e.g., completed without completion time)
        """
        if self.status in ["completed", "failed"]:
            if self.completed_at is None:
                raise ValueError(
                    f"completed_at must be set when status is '{self.status}'"
                )
            if self.completed_at < self.started_at:
                raise ValueError("completed_at cannot be before started_at")

        if self.status == "completed" and self.outputs is None:
            raise ValueError("outputs must be set when status is 'completed'")

        if self.status == "failed" and not self.error_message and not self.validation_errors:
            raise ValueError(
                "error_message or validation_errors must be set when status is 'failed'"
            )

        if self.retry_count > self.max_retries:
            raise ValueError(
                f"retry_count ({self.retry_count}) cannot exceed max_retries ({self.max_retries})"
            )

        return self

    @field_validator("status")
    @classmethod
    def validate_status_transition(cls, v: str) -> str:
        """
        Validate status value is one of the allowed states.

        Args:
            v: Status string

        Returns:
            Validated status string
        """
        return v
