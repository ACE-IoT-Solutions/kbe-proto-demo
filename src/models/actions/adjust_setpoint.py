"""
Adjust Setpoint Action

Action model for adjusting temperature setpoints in building zones.
Includes validation for safe and efficient setpoint changes.
"""

from typing import Literal
from pydantic import Field, field_validator, model_validator
from ..kbe_actions import ActionInput


class AdjustSetpointInput(ActionInput):
    """
    Input model for adjusting zone temperature setpoints.

    Attributes:
        zone_id: Target zone identifier
        new_setpoint: Desired temperature setpoint in Fahrenheit
        reason: Reason for setpoint adjustment
        priority: Adjustment priority level
        max_change: Maximum allowed temperature change from current setpoint
    """

    zone_id: str = Field(
        ...,
        min_length=1,
        description="Target zone identifier"
    )
    new_setpoint: float = Field(
        ...,
        ge=50.0,
        le=90.0,
        description="New temperature setpoint in Fahrenheit"
    )
    reason: str = Field(
        ...,
        min_length=1,
        description="Reason for setpoint adjustment"
    )
    priority: Literal["low", "medium", "high", "emergency"] = Field(
        default="medium",
        description="Adjustment priority"
    )
    max_change: float = Field(
        default=5.0,
        gt=0.0,
        le=15.0,
        description="Maximum allowed temperature change in degrees F"
    )
    current_setpoint: float | None = Field(
        default=None,
        ge=50.0,
        le=90.0,
        description="Current setpoint for validation (optional)"
    )

    @field_validator("new_setpoint")
    @classmethod
    def validate_comfort_range(cls, v: float) -> float:
        """
        Validate setpoint is within comfort range.

        Args:
            v: New setpoint temperature

        Returns:
            Validated setpoint

        Raises:
            ValueError: If setpoint is outside typical comfort range
        """
        if v < 60.0 or v > 80.0:
            raise ValueError(
                f"Setpoint {v}°F is outside typical comfort range (60-80°F). "
                "Use high/emergency priority if intentional."
            )
        return v

    @model_validator(mode="after")
    def validate_setpoint_change(self) -> "AdjustSetpointInput":
        """
        Validate that setpoint change doesn't exceed max_change.

        Returns:
            Validated model instance

        Raises:
            ValueError: If change exceeds max_change limit
        """
        if self.current_setpoint is not None:
            change = abs(self.new_setpoint - self.current_setpoint)
            if change > self.max_change:
                raise ValueError(
                    f"Setpoint change of {change}°F exceeds max_change limit of {self.max_change}°F"
                )
        return self


class AdjustSetpointAction:
    """
    Action implementation for adjusting zone temperature setpoints.

    This class provides factory methods and utilities for creating
    ActionDefinition instances for setpoint adjustments.
    """

    ACTION_TYPE = "control"
    ACTION_NAME = "Adjust Zone Setpoint"

    @staticmethod
    def get_input_schema() -> dict:
        """
        Get JSON Schema for AdjustSetpointInput.

        Returns:
            JSON Schema dictionary for action inputs
        """
        return {
            "type": "object",
            "properties": {
                "zone_id": {
                    "type": "string",
                    "minLength": 1,
                    "description": "Target zone identifier"
                },
                "new_setpoint": {
                    "type": "number",
                    "minimum": 50.0,
                    "maximum": 90.0,
                    "description": "New temperature setpoint in Fahrenheit"
                },
                "reason": {
                    "type": "string",
                    "minLength": 1,
                    "description": "Reason for setpoint adjustment"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "emergency"],
                    "default": "medium",
                    "description": "Adjustment priority"
                },
                "max_change": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 15.0,
                    "default": 5.0,
                    "description": "Maximum allowed temperature change"
                },
                "current_setpoint": {
                    "type": "number",
                    "minimum": 50.0,
                    "maximum": 90.0,
                    "description": "Current setpoint for validation"
                }
            },
            "required": ["zone_id", "new_setpoint", "reason"],
            "additionalProperties": False
        }

    @staticmethod
    def get_preconditions() -> list[str]:
        """
        Get preconditions that must be true before executing this action.

        Returns:
            List of precondition expression strings
        """
        return [
            "zone_exists(zone_id)",
            "zone_is_online(zone_id)",
            "setpoint_within_limits(new_setpoint, zone_id)",
            "no_override_active(zone_id)"
        ]

    @staticmethod
    def get_postconditions() -> list[str]:
        """
        Get expected postconditions after successful execution.

        Returns:
            List of postcondition expression strings
        """
        return [
            "zone_setpoint_equals(zone_id, new_setpoint)",
            "zone_responding(zone_id)",
            "audit_log_created(action_id)"
        ]

    @staticmethod
    def validate_input(input_data: dict) -> AdjustSetpointInput:
        """
        Validate raw input data against AdjustSetpointInput model.

        Args:
            input_data: Raw input dictionary

        Returns:
            Validated AdjustSetpointInput instance

        Raises:
            ValidationError: If input data is invalid
        """
        return AdjustSetpointInput(**input_data)
