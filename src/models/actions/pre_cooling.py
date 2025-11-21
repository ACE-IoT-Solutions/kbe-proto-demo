"""
Pre-Cooling Action

Action model for proactive cooling optimization to reduce peak demand costs.
Pre-cools building zones during off-peak hours before anticipated high occupancy/temperature periods.
"""

from typing import Literal
from datetime import datetime, time
from pydantic import Field, field_validator, model_validator
from ..kbe_actions import ActionInput


class PreCoolingInput(ActionInput):
    """
    Input model for pre-cooling optimization actions.

    Attributes:
        zone_ids: List of zone identifiers to pre-cool
        target_temp: Target temperature to achieve before occupancy period (°F)
        start_time: Time to begin pre-cooling (HH:MM format)
        occupancy_start: Expected occupancy/high-load start time (HH:MM format)
        max_rate_delta: Maximum cooling rate in °F per hour
        priority: Action priority level
        enable_adaptive: Enable adaptive learning from past performance
        cost_limit_usd: Maximum acceptable cost for pre-cooling operation
        reason: Reason for pre-cooling action
    """

    zone_ids: list[str] = Field(
        ...,
        min_length=1,
        description="Target zone identifiers for pre-cooling"
    )
    target_temp: float = Field(
        ...,
        ge=60.0,
        le=75.0,
        description="Target pre-cooling temperature in Fahrenheit (60-75°F)"
    )
    start_time: str = Field(
        ...,
        pattern=r'^([01]\d|2[0-3]):([0-5]\d)$',
        description="Pre-cooling start time in HH:MM format (24-hour)"
    )
    occupancy_start: str = Field(
        ...,
        pattern=r'^([01]\d|2[0-3]):([0-5]\d)$',
        description="Expected occupancy start time in HH:MM format (24-hour)"
    )
    max_rate_delta: float = Field(
        default=5.0,
        ge=1.0,
        le=10.0,
        description="Maximum cooling rate in °F per hour (1-10°F/hr)"
    )
    priority: Literal["low", "medium", "high"] = Field(
        default="medium",
        description="Action priority level (emergency not allowed for pre-cooling)"
    )
    enable_adaptive: bool = Field(
        default=True,
        description="Enable adaptive learning from historical performance"
    )
    cost_limit_usd: float | None = Field(
        default=None,
        ge=0.0,
        description="Maximum acceptable cost in USD"
    )
    reason: str = Field(
        ...,
        min_length=1,
        description="Reason for pre-cooling action"
    )
    min_outdoor_temp: float | None = Field(
        default=None,
        ge=-20.0,
        le=100.0,
        description="Minimum outdoor temperature to enable pre-cooling (°F)"
    )
    max_outdoor_temp: float | None = Field(
        default=None,
        ge=-20.0,
        le=120.0,
        description="Maximum outdoor temperature to enable pre-cooling (°F)"
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
    def validate_time_window(self) -> "PreCoolingInput":
        """
        Validate that start_time is before occupancy_start and allows sufficient time.

        Returns:
            Validated model instance

        Raises:
            ValueError: If time window is invalid
        """
        try:
            start = datetime.strptime(self.start_time, "%H:%M").time()
            occupancy = datetime.strptime(self.occupancy_start, "%H:%M").time()
        except ValueError as e:
            raise ValueError(f"Invalid time format: {e}")

        # Convert to minutes for comparison
        start_minutes = start.hour * 60 + start.minute
        occupancy_minutes = occupancy.hour * 60 + occupancy.minute

        # Handle overnight scenarios (e.g., pre-cool at 23:00 for 07:00 occupancy)
        if occupancy_minutes < start_minutes:
            occupancy_minutes += 24 * 60

        time_window = occupancy_minutes - start_minutes

        # Minimum 30 minutes pre-cooling window
        if time_window < 30:
            raise ValueError(
                f"Pre-cooling window too short ({time_window} minutes). "
                "Minimum 30 minutes required between start_time and occupancy_start."
            )

        # Maximum 8 hours pre-cooling window (reasonable for overnight pre-cooling)
        if time_window > 480:
            raise ValueError(
                f"Pre-cooling window too long ({time_window} minutes). "
                "Maximum 8 hours (480 minutes) allowed."
            )

        return self

    @model_validator(mode="after")
    def validate_outdoor_temps(self) -> "PreCoolingInput":
        """
        Validate outdoor temperature constraints if specified.

        Returns:
            Validated model instance

        Raises:
            ValueError: If outdoor temp range is invalid
        """
        if self.min_outdoor_temp is not None and self.max_outdoor_temp is not None:
            if self.min_outdoor_temp >= self.max_outdoor_temp:
                raise ValueError(
                    f"min_outdoor_temp ({self.min_outdoor_temp}°F) must be less than "
                    f"max_outdoor_temp ({self.max_outdoor_temp}°F)"
                )

        return self

    @field_validator("target_temp")
    @classmethod
    def validate_target_temp_economics(cls, v: float) -> float:
        """
        Validate target temperature is economically reasonable.

        Args:
            v: Target temperature

        Returns:
            Validated temperature

        Raises:
            ValueError: If temperature is too aggressive
        """
        if v < 62.0:
            raise ValueError(
                f"Target temperature {v}°F is too aggressive for pre-cooling. "
                "Minimum 62°F to avoid excessive energy waste."
            )

        return v


class PreCoolingAction:
    """
    Action implementation for pre-cooling optimization.

    This class provides factory methods and utilities for creating
    ActionDefinition instances for pre-cooling operations.
    """

    ACTION_TYPE = "optimization"
    ACTION_NAME = "Pre-Cooling for Demand Optimization"

    @staticmethod
    def get_input_schema() -> dict:
        """
        Get JSON Schema for PreCoolingInput.

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
                "target_temp": {
                    "type": "number",
                    "minimum": 60.0,
                    "maximum": 75.0,
                    "description": "Target pre-cooling temperature in °F"
                },
                "start_time": {
                    "type": "string",
                    "pattern": "^([01]\\d|2[0-3]):([0-5]\\d)$",
                    "description": "Start time (HH:MM, 24-hour)"
                },
                "occupancy_start": {
                    "type": "string",
                    "pattern": "^([01]\\d|2[0-3]):([0-5]\\d)$",
                    "description": "Occupancy start time (HH:MM, 24-hour)"
                },
                "max_rate_delta": {
                    "type": "number",
                    "minimum": 1.0,
                    "maximum": 10.0,
                    "default": 5.0,
                    "description": "Max cooling rate (°F/hr)"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "default": "medium",
                    "description": "Priority level"
                },
                "enable_adaptive": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable adaptive learning"
                },
                "cost_limit_usd": {
                    "type": "number",
                    "minimum": 0.0,
                    "description": "Maximum cost in USD"
                },
                "reason": {
                    "type": "string",
                    "minLength": 1,
                    "description": "Reason for pre-cooling"
                },
                "min_outdoor_temp": {
                    "type": "number",
                    "minimum": -20.0,
                    "maximum": 100.0,
                    "description": "Min outdoor temp (°F)"
                },
                "max_outdoor_temp": {
                    "type": "number",
                    "minimum": -20.0,
                    "maximum": 120.0,
                    "description": "Max outdoor temp (°F)"
                }
            },
            "required": ["zone_ids", "target_temp", "start_time", "occupancy_start", "reason"],
            "additionalProperties": False
        }

    @staticmethod
    def get_validation_rules() -> list[str]:
        """
        Get SHACL-style validation rules for pre-cooling actions.

        Returns:
            List of validation rule descriptions
        """
        return [
            "Target temp: 60-75°F (aggressive cooling avoided)",
            "Time window: 30 min - 8 hours before occupancy",
            "Cooling rate: Max 10°F/hr (equipment protection)",
            "Priority: Emergency not allowed (planned action only)",
            "Energy Manager: Required for cost > $100",
            "Facility Manager: Required for multi-zone (>3 zones)",
            "Adaptive learning: Historical data used when enabled",
            "Weather integration: Outdoor temp constraints enforced"
        ]

    @staticmethod
    def get_odrl_policies() -> dict[str, dict]:
        """
        Get ODRL governance policies for pre-cooling actions.

        Returns:
            Dictionary mapping roles to their permissions
        """
        return {
            "operator": {
                "permitted": False,
                "reason": "Pre-cooling requires optimization expertise"
            },
            "facility_manager": {
                "permitted": True,
                "constraints": [
                    "max_zones: 3",
                    "max_cost: $50",
                    "priority: low/medium only"
                ]
            },
            "energy_manager": {
                "permitted": True,
                "constraints": [
                    "max_zones: unlimited",
                    "max_cost: $500",
                    "priority: low/medium/high"
                ]
            },
            "contractor": {
                "permitted": False,
                "reason": "Pre-cooling requires building system knowledge"
            }
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
            "current_time_before_start_time(start_time)",
            "sufficient_precooling_window(start_time, occupancy_start)",
            "hvac_systems_operational(zone_ids)",
            "no_conflicting_schedules(zone_ids, start_time)",
            "weather_forecast_available()",
            "outdoor_temps_within_limits(min_outdoor_temp, max_outdoor_temp)",
            "energy_prices_within_budget(cost_limit_usd)"
        ]

    @staticmethod
    def get_postconditions() -> list[str]:
        """
        Get expected postconditions after successful execution.

        Returns:
            List of postcondition expression strings
        """
        return [
            "zones_at_target_temp(zone_ids, target_temp)",
            "cooling_rate_within_limits(max_rate_delta)",
            "pre_cooling_schedule_created(start_time, occupancy_start)",
            "energy_consumption_logged(zone_ids)",
            "cost_within_budget(cost_limit_usd)",
            "occupants_notified_if_needed(zone_ids)",
            "adaptive_data_recorded(enable_adaptive)",
            "audit_log_created(action_id)"
        ]

    @staticmethod
    def validate_input(input_data: dict) -> PreCoolingInput:
        """
        Validate raw input data against PreCoolingInput model.

        Args:
            input_data: Raw input dictionary

        Returns:
            Validated PreCoolingInput instance

        Raises:
            ValidationError: If input data is invalid
        """
        return PreCoolingInput(**input_data)

    @staticmethod
    def calculate_estimated_cost(
        zone_count: int,
        target_temp_delta: float,
        duration_hours: float,
        electricity_rate_per_kwh: float = 0.12
    ) -> float:
        """
        Calculate estimated cost for pre-cooling operation.

        Args:
            zone_count: Number of zones to pre-cool
            target_temp_delta: Temperature difference to achieve (°F)
            duration_hours: Expected duration in hours
            electricity_rate_per_kwh: Cost per kWh in USD

        Returns:
            Estimated cost in USD
        """
        # Rough estimation: 3 kW per zone per °F delta per hour
        estimated_kwh = zone_count * target_temp_delta * duration_hours * 3.0
        return estimated_kwh * electricity_rate_per_kwh

    @staticmethod
    def calculate_estimated_savings(
        zone_count: int,
        peak_demand_rate_per_kw: float = 15.0,
        estimated_peak_reduction_kw: float = 5.0
    ) -> float:
        """
        Calculate estimated peak demand cost savings.

        Args:
            zone_count: Number of zones benefiting from pre-cooling
            peak_demand_rate_per_kw: Peak demand charge ($/kW/month)
            estimated_peak_reduction_kw: Expected peak reduction per zone

        Returns:
            Estimated monthly savings in USD
        """
        total_peak_reduction = zone_count * estimated_peak_reduction_kw
        return total_peak_reduction * peak_demand_rate_per_kw
