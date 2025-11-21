"""
Building Infrastructure Models

Pydantic models representing building entities including buildings, zones, and equipment.
These models provide validation and structure for the building management system.
"""

from typing import Literal
from pydantic import BaseModel, Field, field_validator


class Equipment(BaseModel):
    """
    Equipment model representing HVAC or other building equipment.

    Attributes:
        id: Unique identifier for the equipment
        type: Type of equipment (e.g., 'hvac', 'lighting', 'fan')
        status: Current operational status
        power_usage: Current power consumption in watts
    """

    id: str = Field(..., description="Unique equipment identifier")
    type: Literal["hvac", "lighting", "fan", "pump", "chiller", "boiler"] = Field(
        ...,
        description="Equipment type"
    )
    status: Literal["on", "off", "standby", "fault"] = Field(
        ...,
        description="Current equipment status"
    )
    power_usage: float = Field(
        ...,
        ge=0.0,
        description="Current power usage in watts"
    )

    @field_validator("power_usage")
    @classmethod
    def validate_power_usage(cls, v: float) -> float:
        """
        Validate that power usage is a reasonable value.

        Args:
            v: Power usage value in watts

        Returns:
            Validated power usage value

        Raises:
            ValueError: If power usage exceeds 100kW (100000W)
        """
        if v > 100000:
            raise ValueError("Power usage exceeds reasonable maximum (100kW)")
        return v


class Zone(BaseModel):
    """
    Zone model representing a climate-controlled area within a building.

    Attributes:
        id: Unique identifier for the zone
        name: Human-readable zone name
        current_temp: Current temperature in Fahrenheit
        setpoint: Target temperature setpoint in Fahrenheit
        occupancy_mode: Current occupancy status
        equipment: List of equipment serving this zone
    """

    id: str = Field(..., description="Unique zone identifier")
    name: str = Field(..., min_length=1, description="Zone name")
    current_temp: float = Field(
        ...,
        ge=-50.0,
        le=150.0,
        description="Current temperature in Fahrenheit"
    )
    setpoint: float = Field(
        ...,
        ge=50.0,
        le=90.0,
        description="Target temperature setpoint in Fahrenheit"
    )
    occupancy_mode: Literal["occupied", "unoccupied", "scheduled"] = Field(
        ...,
        description="Current occupancy mode"
    )
    equipment: list[Equipment] = Field(
        default_factory=list,
        description="Equipment serving this zone"
    )

    @field_validator("setpoint")
    @classmethod
    def validate_setpoint_range(cls, v: float) -> float:
        """
        Validate that setpoint is within comfortable range.

        Args:
            v: Setpoint temperature in Fahrenheit

        Returns:
            Validated setpoint value

        Raises:
            ValueError: If setpoint is outside comfort range (60-80°F)
        """
        if v < 60.0 or v > 80.0:
            raise ValueError(
                f"Setpoint {v}°F is outside typical comfort range (60-80°F)"
            )
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        Validate and clean zone name.

        Args:
            v: Zone name string

        Returns:
            Cleaned zone name

        Raises:
            ValueError: If name is empty after stripping whitespace
        """
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Zone name cannot be empty or whitespace only")
        return cleaned


class Building(BaseModel):
    """
    Building model representing a complete building with multiple zones.

    Attributes:
        id: Unique identifier for the building
        name: Human-readable building name
        zones: List of zones within the building
    """

    id: str = Field(..., description="Unique building identifier")
    name: str = Field(..., min_length=1, description="Building name")
    zones: list[Zone] = Field(
        default_factory=list,
        description="Zones within the building"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        Validate and clean building name.

        Args:
            v: Building name string

        Returns:
            Cleaned building name

        Raises:
            ValueError: If name is empty after stripping whitespace
        """
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Building name cannot be empty or whitespace only")
        return cleaned

    @field_validator("zones")
    @classmethod
    def validate_zones(cls, v: list[Zone]) -> list[Zone]:
        """
        Validate zone list has unique IDs.

        Args:
            v: List of Zone objects

        Returns:
            Validated zone list

        Raises:
            ValueError: If duplicate zone IDs are found
        """
        zone_ids = [zone.id for zone in v]
        if len(zone_ids) != len(set(zone_ids)):
            raise ValueError("Duplicate zone IDs found in building")
        return v
