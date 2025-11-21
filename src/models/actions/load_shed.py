"""
Load Shed Action

Action model for demand management through strategic load shedding.
Enables temporary reduction of building energy consumption during peak demand.
"""

from typing import Literal
from pydantic import Field, field_validator, model_validator
from ..kbe_actions import ActionInput


class LoadShedInput(ActionInput):
    """
    Input model for load shedding demand management actions.

    Attributes:
        zone_ids: List of zone identifiers to shed load from
        shed_level: Intensity of load shedding (1-5, 5 being most aggressive)
        duration_minutes: Duration to maintain load shed in minutes
        equipment_types: Types of equipment to shed (empty = all)
        reason: Reason for load shedding
        min_comfort_temp: Minimum acceptable temperature during shed
        max_comfort_temp: Maximum acceptable temperature during shed
        priority_zones: Zones to protect from shedding (critical spaces)
    """

    zone_ids: list[str] = Field(
        ...,
        min_length=1,
        description="Target zone identifiers for load shedding"
    )
    shed_level: Literal[1, 2, 3, 4, 5] = Field(
        ...,
        description="Load shed intensity (1=minimal, 5=maximum)"
    )
    duration_minutes: int = Field(
        ...,
        gt=0,
        le=240,
        description="Duration to maintain load shed (max 4 hours)"
    )
    equipment_types: list[Literal["hvac", "lighting", "fan", "pump", "chiller", "boiler"]] = Field(
        default_factory=list,
        description="Equipment types to shed (empty = all)"
    )
    reason: str = Field(
        ...,
        min_length=1,
        description="Reason for load shedding"
    )
    min_comfort_temp: float = Field(
        default=68.0,
        ge=60.0,
        le=75.0,
        description="Minimum acceptable temperature in Fahrenheit"
    )
    max_comfort_temp: float = Field(
        default=78.0,
        ge=70.0,
        le=85.0,
        description="Maximum acceptable temperature in Fahrenheit"
    )
    priority_zones: list[str] = Field(
        default_factory=list,
        description="Zones to protect from shedding"
    )
    expected_savings_kw: float | None = Field(
        default=None,
        ge=0.0,
        description="Expected energy savings in kilowatts"
    )

    @field_validator("zone_ids")
    @classmethod
    def validate_zone_ids(cls, v: list[str]) -> list[str]:
        """
        Validate zone IDs are non-empty and unique.

        Args:
            v: List of zone IDs

        Returns:
            Validated zone ID list

        Raises:
            ValueError: If duplicate zone IDs or empty strings found
        """
        if len(v) != len(set(v)):
            raise ValueError("Duplicate zone IDs not allowed")

        for zone_id in v:
            if not zone_id.strip():
                raise ValueError("Zone IDs cannot be empty or whitespace")

        return v

    @model_validator(mode="after")
    def validate_comfort_range(self) -> "LoadShedInput":
        """
        Validate that min_comfort_temp is less than max_comfort_temp.

        Returns:
            Validated model instance

        Raises:
            ValueError: If comfort range is invalid
        """
        if self.min_comfort_temp >= self.max_comfort_temp:
            raise ValueError(
                f"min_comfort_temp ({self.min_comfort_temp}°F) must be less than "
                f"max_comfort_temp ({self.max_comfort_temp}°F)"
            )

        temp_range = self.max_comfort_temp - self.min_comfort_temp
        if temp_range < 5.0:
            raise ValueError(
                f"Comfort temperature range ({temp_range}°F) is too narrow. "
                "Minimum range is 5°F."
            )

        return self

    @model_validator(mode="after")
    def validate_priority_zones(self) -> "LoadShedInput":
        """
        Validate that priority zones are not in the shed zone list.

        Returns:
            Validated model instance

        Raises:
            ValueError: If priority zones overlap with shed zones
        """
        if self.priority_zones:
            overlap = set(self.zone_ids) & set(self.priority_zones)
            if overlap:
                raise ValueError(
                    f"Priority zones cannot be in shed zone list: {overlap}"
                )

        return self

    @field_validator("duration_minutes")
    @classmethod
    def validate_duration(cls, v: int, info) -> int:
        """
        Validate duration based on shed level.

        Args:
            v: Duration in minutes
            info: Validation context

        Returns:
            Validated duration

        Raises:
            ValueError: If duration is too long for high shed levels
        """
        shed_level = info.data.get("shed_level")

        # Higher shed levels should have shorter durations
        if shed_level and shed_level >= 4 and v > 120:
            raise ValueError(
                f"Shed level {shed_level} should not exceed 120 minutes duration "
                "due to occupant comfort concerns"
            )

        return v


class LoadShedAction:
    """
    Action implementation for demand management load shedding.

    This class provides factory methods and utilities for creating
    ActionDefinition instances for load shedding operations.
    """

    ACTION_TYPE = "optimization"
    ACTION_NAME = "Load Shed for Demand Management"

    @staticmethod
    def get_input_schema() -> dict:
        """
        Get JSON Schema for LoadShedInput.

        Returns:
            JSON Schema dictionary for action inputs
        """
        return {
            "type": "object",
            "properties": {
                "zone_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "description": "Target zone identifiers"
                },
                "shed_level": {
                    "type": "integer",
                    "enum": [1, 2, 3, 4, 5],
                    "description": "Load shed intensity"
                },
                "duration_minutes": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 240,
                    "description": "Duration in minutes"
                },
                "equipment_types": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["hvac", "lighting", "fan", "pump", "chiller", "boiler"]
                    },
                    "description": "Equipment types to shed"
                },
                "reason": {
                    "type": "string",
                    "minLength": 1,
                    "description": "Reason for load shedding"
                },
                "min_comfort_temp": {
                    "type": "number",
                    "minimum": 60.0,
                    "maximum": 75.0,
                    "default": 68.0,
                    "description": "Minimum comfort temperature"
                },
                "max_comfort_temp": {
                    "type": "number",
                    "minimum": 70.0,
                    "maximum": 85.0,
                    "default": 78.0,
                    "description": "Maximum comfort temperature"
                },
                "priority_zones": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Zones to protect from shedding"
                },
                "expected_savings_kw": {
                    "type": "number",
                    "minimum": 0.0,
                    "description": "Expected energy savings in kW"
                }
            },
            "required": ["zone_ids", "shed_level", "duration_minutes", "reason"],
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
            "all_zones_exist(zone_ids)",
            "all_zones_online(zone_ids)",
            "no_critical_operations_active(zone_ids)",
            "no_active_overrides(zone_ids)",
            "sufficient_shed_capacity(zone_ids, shed_level)",
            "weather_conditions_appropriate()",
            "occupancy_acceptable_for_shed(zone_ids)"
        ]

    @staticmethod
    def get_postconditions() -> list[str]:
        """
        Get expected postconditions after successful execution.

        Returns:
            List of postcondition expression strings
        """
        return [
            "load_reduced_by_target(zone_ids, shed_level)",
            "temperatures_within_comfort_range(zone_ids, min_comfort_temp, max_comfort_temp)",
            "equipment_shed_as_specified(zone_ids, equipment_types)",
            "shed_schedule_created(duration_minutes)",
            "audit_log_created(action_id)",
            "power_monitoring_active(zone_ids)"
        ]

    @staticmethod
    def validate_input(input_data: dict) -> LoadShedInput:
        """
        Validate raw input data against LoadShedInput model.

        Args:
            input_data: Raw input dictionary

        Returns:
            Validated LoadShedInput instance

        Raises:
            ValidationError: If input data is invalid
        """
        return LoadShedInput(**input_data)

    @staticmethod
    def calculate_estimated_savings(
        zone_count: int,
        shed_level: int,
        avg_zone_load_kw: float = 10.0
    ) -> float:
        """
        Calculate estimated energy savings from load shed.

        Args:
            zone_count: Number of zones in shed
            shed_level: Shed intensity (1-5)
            avg_zone_load_kw: Average load per zone in kW

        Returns:
            Estimated savings in kilowatts
        """
        # Shed percentage by level: 1=20%, 2=35%, 3=50%, 4=65%, 5=80%
        shed_percentages = {1: 0.20, 2: 0.35, 3: 0.50, 4: 0.65, 5: 0.80}

        total_load = zone_count * avg_zone_load_kw
        shed_percentage = shed_percentages.get(shed_level, 0.50)

        return total_load * shed_percentage
