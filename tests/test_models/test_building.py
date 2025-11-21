"""
Tests for building, zone, and equipment models.

Tests validation, creation, and manipulation of building configurations.
"""

import pytest
from datetime import time, datetime
from tests.fixtures.sample_building import (
    Location,
    Schedule,
    ZoneConfiguration,
    EquipmentConfiguration,
    BuildingConfiguration,
    create_sample_building,
    create_small_single_zone_building,
    create_multi_floor_building,
)


class TestLocation:
    """Tests for Location model."""

    @pytest.mark.models
    @pytest.mark.unit
    def test_location_creation_valid(self):
        """Test creating a valid location."""
        location = Location(
            latitude=40.7128,
            longitude=-74.0060,
            elevation_m=10.0,
            timezone="America/New_York",
        )
        assert location.latitude == 40.7128
        assert location.longitude == -74.0060
        assert location.elevation_m == 10.0
        assert location.timezone == "America/New_York"

    @pytest.mark.models
    @pytest.mark.unit
    def test_location_invalid_latitude_too_high(self):
        """Test that invalid latitude is rejected."""
        with pytest.raises(AssertionError):
            Location(latitude=91, longitude=0)

    @pytest.mark.models
    @pytest.mark.unit
    def test_location_invalid_latitude_too_low(self):
        """Test that invalid latitude is rejected."""
        with pytest.raises(AssertionError):
            Location(latitude=-91, longitude=0)

    @pytest.mark.models
    @pytest.mark.unit
    def test_location_invalid_longitude_too_high(self):
        """Test that invalid longitude is rejected."""
        with pytest.raises(AssertionError):
            Location(latitude=0, longitude=181)

    @pytest.mark.models
    @pytest.mark.unit
    def test_location_invalid_longitude_too_low(self):
        """Test that invalid longitude is rejected."""
        with pytest.raises(AssertionError):
            Location(latitude=0, longitude=-181)

    @pytest.mark.models
    @pytest.mark.unit
    def test_location_edge_case_poles(self):
        """Test location at poles."""
        north_pole = Location(latitude=90, longitude=0)
        assert north_pole.latitude == 90

        south_pole = Location(latitude=-90, longitude=0)
        assert south_pole.latitude == -90

    @pytest.mark.models
    @pytest.mark.unit
    def test_location_edge_case_date_line(self):
        """Test location at international date line."""
        location = Location(latitude=0, longitude=180)
        assert location.longitude == 180

        location = Location(latitude=0, longitude=-180)
        assert location.longitude == -180

    @pytest.mark.models
    @pytest.mark.unit
    def test_location_default_elevation(self):
        """Test location with default elevation."""
        location = Location(latitude=0, longitude=0)
        assert location.elevation_m == 0.0

    @pytest.mark.models
    @pytest.mark.unit
    def test_location_negative_elevation(self):
        """Test location below sea level."""
        location = Location(latitude=0, longitude=0, elevation_m=-300)
        assert location.elevation_m == -300


class TestSchedule:
    """Tests for Schedule model."""

    @pytest.mark.models
    @pytest.mark.unit
    def test_schedule_creation_valid(self):
        """Test creating a valid schedule."""
        schedule = Schedule(
            weekday_start=time(8, 0),
            weekday_end=time(17, 0),
            occupied_setpoint_c=22.0,
            unoccupied_setpoint_c=18.0,
        )
        assert schedule.weekday_start == time(8, 0)
        assert schedule.weekday_end == time(17, 0)
        assert schedule.occupied_setpoint_c == 22.0

    @pytest.mark.models
    @pytest.mark.unit
    def test_schedule_invalid_start_after_end(self):
        """Test that end time before start time is rejected."""
        with pytest.raises(AssertionError):
            Schedule(
                weekday_start=time(17, 0),
                weekday_end=time(8, 0),
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_schedule_invalid_occupied_setpoint_too_cold(self):
        """Test that occupied setpoint too cold is rejected."""
        with pytest.raises(AssertionError):
            Schedule(occupied_setpoint_c=14)

    @pytest.mark.models
    @pytest.mark.unit
    def test_schedule_invalid_occupied_setpoint_too_hot(self):
        """Test that occupied setpoint too hot is rejected."""
        with pytest.raises(AssertionError):
            Schedule(occupied_setpoint_c=30)

    @pytest.mark.models
    @pytest.mark.unit
    def test_schedule_holidays_list(self):
        """Test schedule with holidays."""
        schedule = Schedule(
            holidays=["2024-01-01", "2024-07-04", "2024-12-25"]
        )
        assert len(schedule.holidays) == 3
        assert "2024-01-01" in schedule.holidays

    @pytest.mark.models
    @pytest.mark.unit
    def test_schedule_default_values(self):
        """Test schedule default values."""
        schedule = Schedule()
        assert schedule.weekday_start == time(8, 0)
        assert schedule.weekday_end == time(17, 0)
        assert schedule.occupied_setpoint_c == 22.0


class TestZoneConfiguration:
    """Tests for ZoneConfiguration model."""

    @pytest.mark.models
    @pytest.mark.unit
    def test_zone_creation_valid(self):
        """Test creating a valid zone."""
        schedule = Schedule()
        zone = ZoneConfiguration(
            name="Office A",
            area_m2=100.0,
            zone_type="office",
            schedule=schedule,
            target_temperature_c=22.0,
        )
        assert zone.name == "Office A"
        assert zone.area_m2 == 100.0
        assert zone.zone_type == "office"

    @pytest.mark.models
    @pytest.mark.unit
    def test_zone_invalid_area_zero(self):
        """Test that zero area is rejected."""
        schedule = Schedule()
        with pytest.raises(AssertionError):
            ZoneConfiguration(
                name="Zone",
                area_m2=0,
                zone_type="office",
                schedule=schedule,
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_zone_invalid_area_negative(self):
        """Test that negative area is rejected."""
        schedule = Schedule()
        with pytest.raises(AssertionError):
            ZoneConfiguration(
                name="Zone",
                area_m2=-100,
                zone_type="office",
                schedule=schedule,
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_zone_invalid_temperature_ordering(self):
        """Test that invalid temperature ordering is rejected."""
        schedule = Schedule()
        with pytest.raises(AssertionError):
            ZoneConfiguration(
                name="Zone",
                area_m2=100,
                zone_type="office",
                schedule=schedule,
                min_temperature_c=25,
                target_temperature_c=22,
                max_temperature_c=26,
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_zone_invalid_humidity_too_high(self):
        """Test that humidity > 100% is rejected."""
        schedule = Schedule()
        with pytest.raises(AssertionError):
            ZoneConfiguration(
                name="Zone",
                area_m2=100,
                zone_type="office",
                schedule=schedule,
                humidity_setpoint_percent=101,
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_zone_equipment_list(self):
        """Test zone with equipment list."""
        schedule = Schedule()
        zone = ZoneConfiguration(
            name="Office A",
            area_m2=100.0,
            zone_type="office",
            schedule=schedule,
            equipment_ids=["VAV-001", "FAN-001"],
        )
        assert len(zone.equipment_ids) == 2
        assert "VAV-001" in zone.equipment_ids

    @pytest.mark.models
    @pytest.mark.unit
    def test_zone_floor_numbering(self):
        """Test zone floor numbering."""
        schedule = Schedule()
        zone = ZoneConfiguration(
            name="Zone",
            area_m2=100,
            zone_type="office",
            schedule=schedule,
            floor_number=3,
        )
        assert zone.floor_number == 3

    @pytest.mark.models
    @pytest.mark.unit
    def test_zone_various_types(self):
        """Test zones with different types."""
        schedule = Schedule()
        zone_types = ["office", "conference", "lobby", "stairwell", "restroom"]

        for zone_type in zone_types:
            zone = ZoneConfiguration(
                name=f"Zone {zone_type}",
                area_m2=100,
                zone_type=zone_type,
                schedule=schedule,
            )
            assert zone.zone_type == zone_type


class TestEquipmentConfiguration:
    """Tests for EquipmentConfiguration model."""

    @pytest.mark.models
    @pytest.mark.unit
    def test_equipment_creation_valid(self):
        """Test creating valid equipment."""
        equipment = EquipmentConfiguration(
            equipment_id="VAV-001",
            equipment_type="vav",
            zone_id="Zone A",
            capacity=2.5,
            capacity_unit="kW",
            efficiency_percent=92.0,
        )
        assert equipment.equipment_id == "VAV-001"
        assert equipment.capacity == 2.5
        assert equipment.efficiency_percent == 92.0

    @pytest.mark.models
    @pytest.mark.unit
    def test_equipment_invalid_empty_id(self):
        """Test that empty equipment ID is rejected."""
        with pytest.raises(AssertionError):
            EquipmentConfiguration(
                equipment_id="",
                equipment_type="vav",
                zone_id="Zone A",
                capacity=2.5,
                capacity_unit="kW",
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_equipment_invalid_zero_capacity(self):
        """Test that zero capacity is rejected."""
        with pytest.raises(AssertionError):
            EquipmentConfiguration(
                equipment_id="VAV-001",
                equipment_type="vav",
                zone_id="Zone A",
                capacity=0,
                capacity_unit="kW",
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_equipment_invalid_negative_capacity(self):
        """Test that negative capacity is rejected."""
        with pytest.raises(AssertionError):
            EquipmentConfiguration(
                equipment_id="VAV-001",
                equipment_type="vav",
                zone_id="Zone A",
                capacity=-5,
                capacity_unit="kW",
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_equipment_invalid_efficiency_too_high(self):
        """Test that efficiency > 100% is rejected."""
        with pytest.raises(AssertionError):
            EquipmentConfiguration(
                equipment_id="VAV-001",
                equipment_type="vav",
                zone_id="Zone A",
                capacity=2.5,
                capacity_unit="kW",
                efficiency_percent=101,
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_equipment_various_types(self):
        """Test equipment with different types."""
        equipment_types = ["vav", "fan", "chiller", "boiler", "pump", "damper"]

        for eq_type in equipment_types:
            equipment = EquipmentConfiguration(
                equipment_id=f"EQ-{eq_type}",
                equipment_type=eq_type,
                zone_id="Zone",
                capacity=10.0,
                capacity_unit="kW",
            )
            assert equipment.equipment_type == eq_type

    @pytest.mark.models
    @pytest.mark.unit
    def test_equipment_operational_status(self):
        """Test equipment operational status."""
        equipment_on = EquipmentConfiguration(
            equipment_id="VAV-001",
            equipment_type="vav",
            zone_id="Zone",
            capacity=2.5,
            capacity_unit="kW",
            operational=True,
        )
        assert equipment_on.operational

        equipment_off = EquipmentConfiguration(
            equipment_id="VAV-002",
            equipment_type="vav",
            zone_id="Zone",
            capacity=2.5,
            capacity_unit="kW",
            operational=False,
        )
        assert not equipment_off.operational


class TestBuildingConfiguration:
    """Tests for BuildingConfiguration model."""

    @pytest.mark.models
    @pytest.mark.unit
    def test_building_creation_valid(self):
        """Test creating a valid building."""
        location = Location(latitude=40.7128, longitude=-74.0060)
        building = BuildingConfiguration(
            building_id="BLDG-001",
            building_name="Test Building",
            location=location,
            total_area_m2=1000.0,
            construction_year=2020,
        )
        assert building.building_id == "BLDG-001"
        assert building.total_area_m2 == 1000.0

    @pytest.mark.models
    @pytest.mark.unit
    def test_building_invalid_empty_id(self):
        """Test that empty building ID is rejected."""
        location = Location(latitude=0, longitude=0)
        with pytest.raises(AssertionError):
            BuildingConfiguration(
                building_id="",
                building_name="Test",
                location=location,
                total_area_m2=1000,
                construction_year=2020,
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_building_invalid_zero_area(self):
        """Test that zero area is rejected."""
        location = Location(latitude=0, longitude=0)
        with pytest.raises(AssertionError):
            BuildingConfiguration(
                building_id="BLDG-001",
                building_name="Test",
                location=location,
                total_area_m2=0,
                construction_year=2020,
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_building_invalid_construction_year_too_old(self):
        """Test that very old construction year is rejected."""
        location = Location(latitude=0, longitude=0)
        with pytest.raises(AssertionError):
            BuildingConfiguration(
                building_id="BLDG-001",
                building_name="Test",
                location=location,
                total_area_m2=1000,
                construction_year=1700,
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_building_invalid_construction_year_future(self):
        """Test that future construction year is rejected."""
        location = Location(latitude=0, longitude=0)
        with pytest.raises(AssertionError):
            BuildingConfiguration(
                building_id="BLDG-001",
                building_name="Test",
                location=location,
                total_area_m2=1000,
                construction_year=2200,
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_building_demand_limit_validation(self):
        """Test demand limit must be above warning threshold."""
        location = Location(latitude=0, longitude=0)
        with pytest.raises(AssertionError):
            BuildingConfiguration(
                building_id="BLDG-001",
                building_name="Test",
                location=location,
                total_area_m2=1000,
                construction_year=2020,
                demand_limit_kw=100,
                demand_warning_threshold_kw=200,
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_building_zone_area_validation(self):
        """Test that total zone area cannot exceed building area."""
        location = Location(latitude=0, longitude=0)
        schedule = Schedule()

        zone = ZoneConfiguration(
            name="Zone",
            area_m2=1500,  # Larger than building
            zone_type="office",
            schedule=schedule,
        )

        with pytest.raises(AssertionError):
            BuildingConfiguration(
                building_id="BLDG-001",
                building_name="Test",
                location=location,
                total_area_m2=1000,
                construction_year=2020,
                zones=[zone],
            )

    @pytest.mark.models
    @pytest.mark.integration
    def test_sample_building_creation(self):
        """Test creating sample building."""
        building = create_sample_building()
        assert building.building_id == "BLDG-001"
        assert len(building.zones) == 4
        assert len(building.equipment) == 10

    @pytest.mark.models
    @pytest.mark.integration
    def test_small_single_zone_building(self):
        """Test creating small single-zone building."""
        building = create_small_single_zone_building()
        assert len(building.zones) == 1
        assert building.zones[0].name == "Single Zone"

    @pytest.mark.models
    @pytest.mark.integration
    def test_multi_floor_building(self):
        """Test creating multi-floor building."""
        building = create_multi_floor_building()
        assert len(building.zones) == 6  # 3 floors x 2 zones

        # Verify floor numbers
        floor_numbers = {zone.floor_number for zone in building.zones}
        assert floor_numbers == {1, 2, 3}

    @pytest.mark.models
    @pytest.mark.unit
    def test_building_timestamp_creation(self):
        """Test building timestamp is set."""
        location = Location(latitude=0, longitude=0)
        building = BuildingConfiguration(
            building_id="BLDG-001",
            building_name="Test",
            location=location,
            total_area_m2=1000,
            construction_year=2020,
        )
        assert building.created_at is not None
        assert isinstance(building.created_at, datetime)
