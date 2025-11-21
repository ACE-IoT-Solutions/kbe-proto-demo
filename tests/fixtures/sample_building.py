"""
Sample building model fixtures for testing.

Provides realistic building, zone, and equipment configurations.
"""

from datetime import time, datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Location:
    """Physical location specification."""

    latitude: float
    longitude: float
    elevation_m: float = 0.0
    timezone: str = "America/New_York"

    def __post_init__(self):
        """Validate location data."""
        assert -90 <= self.latitude <= 90, "Latitude must be between -90 and 90"
        assert -180 <= self.longitude <= 180, "Longitude must be between -180 and 180"
        assert self.elevation_m >= -500, "Elevation should not be below -500m"


@dataclass
class Schedule:
    """Operating schedule specification."""

    weekday_start: time = field(default_factory=lambda: time(8, 0))
    weekday_end: time = field(default_factory=lambda: time(17, 0))
    weekend_start: time = field(default_factory=lambda: time(9, 0))
    weekend_end: time = field(default_factory=lambda: time(13, 0))
    occupied_setpoint_c: float = 22.0
    unoccupied_setpoint_c: float = 18.0
    holidays: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate schedule data."""
        assert self.weekday_start < self.weekday_end, "Start time must be before end time"
        assert self.weekend_start < self.weekend_end, "Start time must be before end time"
        assert 15 <= self.occupied_setpoint_c <= 28, "Occupied setpoint should be between 15-28°C"
        assert 10 <= self.unoccupied_setpoint_c <= 25, "Unoccupied setpoint should be between 10-25°C"


@dataclass
class ZoneConfiguration:
    """Zone configuration specification."""

    name: str
    area_m2: float
    zone_type: str  # "office", "conference", "lobby", "stairwell", etc.
    schedule: Schedule
    target_temperature_c: float = 22.0
    min_temperature_c: float = 18.0
    max_temperature_c: float = 26.0
    outdoor_air_cfm: float = 500.0
    return_air_cfm: float = 1500.0
    humidity_setpoint_percent: float = 50.0
    floor_number: int = 1
    equipment_ids: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate zone configuration."""
        assert self.area_m2 > 0, "Zone area must be positive"
        assert self.min_temperature_c < self.target_temperature_c < self.max_temperature_c, (
            "Target must be between min and max temperature"
        )
        assert 0 <= self.humidity_setpoint_percent <= 100, "Humidity should be 0-100%"
        assert self.outdoor_air_cfm >= 0, "Outdoor air CFM must be non-negative"
        assert self.return_air_cfm >= 0, "Return air CFM must be non-negative"
        assert self.floor_number >= 0, "Floor number must be non-negative"


@dataclass
class EquipmentConfiguration:
    """Equipment configuration specification."""

    equipment_id: str
    equipment_type: str  # "vav", "fan", "chiller", "boiler", "pump", etc.
    zone_id: str
    capacity: float
    capacity_unit: str  # "kW", "GPM", "CFM", etc.
    efficiency_percent: float = 90.0
    maintenance_schedule_hours: int = 8760  # 1 year
    operational: bool = True

    def __post_init__(self):
        """Validate equipment configuration."""
        assert self.equipment_id.strip(), "Equipment ID must not be empty"
        assert self.capacity > 0, "Equipment capacity must be positive"
        assert 0 <= self.efficiency_percent <= 100, "Efficiency should be 0-100%"
        assert self.maintenance_schedule_hours > 0, "Maintenance schedule must be positive"


@dataclass
class BuildingConfiguration:
    """Complete building configuration."""

    building_id: str
    building_name: str
    location: Location
    total_area_m2: float
    construction_year: int
    zones: List[ZoneConfiguration] = field(default_factory=list)
    equipment: List[EquipmentConfiguration] = field(default_factory=list)
    demand_limit_kw: float = 500.0
    demand_warning_threshold_kw: float = 400.0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate building configuration."""
        assert self.building_id.strip(), "Building ID must not be empty"
        assert self.building_name.strip(), "Building name must not be empty"
        assert self.total_area_m2 > 0, "Building area must be positive"
        assert 1800 <= self.construction_year <= 2100, "Construction year should be reasonable"
        assert self.demand_limit_kw > 0, "Demand limit must be positive"
        assert (
            self.demand_warning_threshold_kw < self.demand_limit_kw
        ), "Warning threshold must be below demand limit"
        assert (
            sum(z.area_m2 for z in self.zones) <= self.total_area_m2
        ), "Total zone area cannot exceed building area"


def create_sample_building() -> BuildingConfiguration:
    """Create a sample building configuration for testing.

    Returns:
        BuildingConfiguration: A realistic office building configuration
    """
    location = Location(
        latitude=40.7128,
        longitude=-74.0060,
        elevation_m=10.0,
        timezone="America/New_York",
    )

    # Standard office schedule
    office_schedule = Schedule(
        weekday_start=time(8, 0),
        weekday_end=time(17, 0),
        weekend_start=time(9, 0),
        weekend_end=time(13, 0),
        occupied_setpoint_c=22.0,
        unoccupied_setpoint_c=18.0,
        holidays=[
            "2024-01-01",
            "2024-07-04",
            "2024-12-25",
        ],
    )

    # Create sample zones
    office_a = ZoneConfiguration(
        name="Office A",
        area_m2=100.0,
        zone_type="office",
        schedule=office_schedule,
        target_temperature_c=22.0,
        floor_number=1,
        equipment_ids=["VAV-001", "FAN-001"],
    )

    office_b = ZoneConfiguration(
        name="Office B",
        area_m2=100.0,
        zone_type="office",
        schedule=office_schedule,
        target_temperature_c=22.0,
        floor_number=1,
        equipment_ids=["VAV-002", "FAN-002"],
    )

    conference_room = ZoneConfiguration(
        name="Conference Room",
        area_m2=50.0,
        zone_type="conference",
        schedule=office_schedule,
        target_temperature_c=21.5,
        floor_number=1,
        equipment_ids=["VAV-003", "FAN-003"],
    )

    lobby = ZoneConfiguration(
        name="Lobby",
        area_m2=75.0,
        zone_type="lobby",
        schedule=office_schedule,
        target_temperature_c=20.0,
        floor_number=1,
        equipment_ids=["VAV-004", "FAN-004"],
    )

    # Create equipment
    equipment_list = [
        EquipmentConfiguration(
            equipment_id="VAV-001",
            equipment_type="vav",
            zone_id="Office A",
            capacity=2.5,
            capacity_unit="kW",
            efficiency_percent=92.0,
        ),
        EquipmentConfiguration(
            equipment_id="FAN-001",
            equipment_type="fan",
            zone_id="Office A",
            capacity=1.5,
            capacity_unit="kW",
            efficiency_percent=85.0,
        ),
        EquipmentConfiguration(
            equipment_id="VAV-002",
            equipment_type="vav",
            zone_id="Office B",
            capacity=2.5,
            capacity_unit="kW",
            efficiency_percent=92.0,
        ),
        EquipmentConfiguration(
            equipment_id="FAN-002",
            equipment_type="fan",
            zone_id="Office B",
            capacity=1.5,
            capacity_unit="kW",
            efficiency_percent=85.0,
        ),
        EquipmentConfiguration(
            equipment_id="VAV-003",
            equipment_type="vav",
            zone_id="Conference Room",
            capacity=2.0,
            capacity_unit="kW",
            efficiency_percent=92.0,
        ),
        EquipmentConfiguration(
            equipment_id="FAN-003",
            equipment_type="fan",
            zone_id="Conference Room",
            capacity=1.0,
            capacity_unit="kW",
            efficiency_percent=85.0,
        ),
        EquipmentConfiguration(
            equipment_id="VAV-004",
            equipment_type="vav",
            zone_id="Lobby",
            capacity=2.0,
            capacity_unit="kW",
            efficiency_percent=92.0,
        ),
        EquipmentConfiguration(
            equipment_id="FAN-004",
            equipment_type="fan",
            zone_id="Lobby",
            capacity=1.0,
            capacity_unit="kW",
            efficiency_percent=85.0,
        ),
        EquipmentConfiguration(
            equipment_id="CHILLER-001",
            equipment_type="chiller",
            zone_id="Building",
            capacity=50.0,
            capacity_unit="kW",
            efficiency_percent=85.0,
            maintenance_schedule_hours=4380,
        ),
        EquipmentConfiguration(
            equipment_id="BOILER-001",
            equipment_type="boiler",
            zone_id="Building",
            capacity=75.0,
            capacity_unit="kW",
            efficiency_percent=88.0,
            maintenance_schedule_hours=4380,
        ),
    ]

    building = BuildingConfiguration(
        building_id="BLDG-001",
        building_name="Sample Office Building",
        location=location,
        total_area_m2=325.0,
        construction_year=2020,
        zones=[office_a, office_b, conference_room, lobby],
        equipment=equipment_list,
        demand_limit_kw=500.0,
        demand_warning_threshold_kw=400.0,
    )

    return building


def create_small_single_zone_building() -> BuildingConfiguration:
    """Create a small single-zone building for basic testing.

    Returns:
        BuildingConfiguration: A minimal building with one zone
    """
    location = Location(latitude=40.7128, longitude=-74.0060)

    schedule = Schedule(
        weekday_start=time(9, 0),
        weekday_end=time(17, 0),
        occupied_setpoint_c=22.0,
        unoccupied_setpoint_c=18.0,
    )

    zone = ZoneConfiguration(
        name="Single Zone",
        area_m2=100.0,
        zone_type="office",
        schedule=schedule,
        equipment_ids=["VAV-001"],
    )

    equipment = [
        EquipmentConfiguration(
            equipment_id="VAV-001",
            equipment_type="vav",
            zone_id="Single Zone",
            capacity=2.5,
            capacity_unit="kW",
        )
    ]

    return BuildingConfiguration(
        building_id="BLDG-SMALL",
        building_name="Small Test Building",
        location=location,
        total_area_m2=100.0,
        construction_year=2020,
        zones=[zone],
        equipment=equipment,
        demand_limit_kw=100.0,
        demand_warning_threshold_kw=80.0,
    )


def create_multi_floor_building() -> BuildingConfiguration:
    """Create a multi-floor building for complex testing.

    Returns:
        BuildingConfiguration: A 3-floor office building
    """
    location = Location(latitude=40.7128, longitude=-74.0060)

    schedule = Schedule(occupied_setpoint_c=22.0, unoccupied_setpoint_c=18.0)

    zones = []
    equipment = []

    for floor in range(1, 4):
        for zone_num in range(1, 3):
            zone_name = f"Floor {floor} Zone {zone_num}"
            zone_id = f"ZONE-{floor}-{zone_num}"

            zone = ZoneConfiguration(
                name=zone_name,
                area_m2=150.0,
                zone_type="office",
                schedule=schedule,
                floor_number=floor,
                equipment_ids=[f"VAV-{floor}-{zone_num}", f"FAN-{floor}-{zone_num}"],
            )
            zones.append(zone)

            equipment.append(
                EquipmentConfiguration(
                    equipment_id=f"VAV-{floor}-{zone_num}",
                    equipment_type="vav",
                    zone_id=zone_name,
                    capacity=2.5,
                    capacity_unit="kW",
                )
            )
            equipment.append(
                EquipmentConfiguration(
                    equipment_id=f"FAN-{floor}-{zone_num}",
                    equipment_type="fan",
                    zone_id=zone_name,
                    capacity=1.5,
                    capacity_unit="kW",
                )
            )

    return BuildingConfiguration(
        building_id="BLDG-MULTI",
        building_name="Multi-Floor Office Building",
        location=location,
        total_area_m2=900.0,
        construction_year=2020,
        zones=zones,
        equipment=equipment,
        demand_limit_kw=800.0,
        demand_warning_threshold_kw=650.0,
    )
