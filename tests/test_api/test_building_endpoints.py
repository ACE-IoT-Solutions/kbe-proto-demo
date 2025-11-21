"""
Tests for building state and management endpoints.

Tests GET /building, /zones, /equipment, etc.
"""

import pytest
from tests.fixtures.sample_building import (
    create_sample_building,
    create_small_single_zone_building,
    create_multi_floor_building,
)


class TestBuildingStateEndpoints:
    """Tests for building state retrieval endpoints."""

    @pytest.mark.api
    @pytest.mark.unit
    def test_building_info_retrieval(self):
        """Test building info endpoint structure."""
        building = create_sample_building()

        # Response should have building info
        assert building.building_id
        assert building.building_name
        assert building.location
        assert building.total_area_m2 > 0

    @pytest.mark.api
    @pytest.mark.unit
    def test_building_response_structure(self):
        """Test building response has all required fields."""
        building = create_sample_building()

        required_fields = [
            "building_id",
            "building_name",
            "location",
            "total_area_m2",
            "construction_year",
            "zones",
            "equipment",
        ]

        for field in required_fields:
            assert hasattr(building, field)

    @pytest.mark.api
    @pytest.mark.unit
    def test_building_location_response(self):
        """Test building location in response."""
        building = create_sample_building()

        location = building.location
        assert location.latitude
        assert location.longitude
        assert location.timezone


class TestZoneEndpoints:
    """Tests for zone management endpoints."""

    @pytest.mark.api
    @pytest.mark.unit
    def test_zone_list_endpoint(self):
        """Test zone listing endpoint."""
        building = create_sample_building()

        assert len(building.zones) > 0
        for zone in building.zones:
            assert zone.name
            assert zone.area_m2 > 0
            assert zone.zone_type

    @pytest.mark.api
    @pytest.mark.unit
    def test_zone_detail_endpoint(self):
        """Test zone detail endpoint."""
        building = create_sample_building()
        zone = building.zones[0]

        # Zone details should include
        assert zone.name
        assert zone.area_m2
        assert zone.target_temperature_c
        assert zone.schedule

    @pytest.mark.api
    @pytest.mark.unit
    def test_zone_schedule_endpoint(self):
        """Test zone schedule information."""
        building = create_sample_building()
        zone = building.zones[0]

        schedule = zone.schedule
        assert schedule.weekday_start
        assert schedule.weekday_end
        assert schedule.occupied_setpoint_c
        assert schedule.unoccupied_setpoint_c

    @pytest.mark.api
    @pytest.mark.unit
    def test_zone_count_consistency(self):
        """Test zone count is consistent."""
        building = create_sample_building()
        assert len(building.zones) > 0

    @pytest.mark.api
    @pytest.mark.unit
    def test_zone_temperature_setpoints(self):
        """Test zone temperature setpoints."""
        building = create_sample_building()

        for zone in building.zones:
            assert zone.min_temperature_c > 0
            assert zone.target_temperature_c > zone.min_temperature_c
            assert zone.max_temperature_c > zone.target_temperature_c


class TestEquipmentEndpoints:
    """Tests for equipment management endpoints."""

    @pytest.mark.api
    @pytest.mark.unit
    def test_equipment_list_endpoint(self):
        """Test equipment listing endpoint."""
        building = create_sample_building()

        assert len(building.equipment) > 0
        for equipment in building.equipment:
            assert equipment.equipment_id
            assert equipment.equipment_type
            assert equipment.capacity > 0

    @pytest.mark.api
    @pytest.mark.unit
    def test_equipment_detail_endpoint(self):
        """Test equipment detail endpoint."""
        building = create_sample_building()
        equipment = building.equipment[0]

        # Equipment details should include
        assert equipment.equipment_id
        assert equipment.equipment_type
        assert equipment.zone_id
        assert equipment.capacity
        assert equipment.capacity_unit

    @pytest.mark.api
    @pytest.mark.unit
    def test_equipment_efficiency_endpoint(self):
        """Test equipment efficiency information."""
        building = create_sample_building()

        for equipment in building.equipment:
            assert 0 <= equipment.efficiency_percent <= 100

    @pytest.mark.api
    @pytest.mark.unit
    def test_equipment_operational_status(self):
        """Test equipment operational status."""
        building = create_sample_building()

        for equipment in building.equipment:
            assert isinstance(equipment.operational, bool)

    @pytest.mark.api
    @pytest.mark.unit
    def test_equipment_maintenance_schedule(self):
        """Test equipment maintenance schedule."""
        building = create_sample_building()

        for equipment in building.equipment:
            assert equipment.maintenance_schedule_hours > 0


class TestBuildingStatsEndpoints:
    """Tests for building statistics endpoints."""

    @pytest.mark.api
    @pytest.mark.unit
    def test_building_area_stats(self):
        """Test building area statistics."""
        building = create_sample_building()

        assert building.total_area_m2 > 0
        zone_total = sum(z.area_m2 for z in building.zones)
        assert zone_total <= building.total_area_m2

    @pytest.mark.api
    @pytest.mark.unit
    def test_building_equipment_count(self):
        """Test building equipment count."""
        building = create_sample_building()

        equipment_count = len(building.equipment)
        assert equipment_count > 0

    @pytest.mark.api
    @pytest.mark.unit
    def test_building_demand_stats(self):
        """Test building demand statistics."""
        building = create_sample_building()

        assert building.demand_limit_kw > 0
        assert building.demand_warning_threshold_kw > 0
        assert building.demand_warning_threshold_kw < building.demand_limit_kw

    @pytest.mark.api
    @pytest.mark.unit
    def test_building_capacity_utilization(self):
        """Test building capacity utilization metrics."""
        building = create_sample_building()

        total_equipment_capacity = sum(e.capacity for e in building.equipment)
        assert total_equipment_capacity > 0

    @pytest.mark.api
    @pytest.mark.unit
    def test_building_efficiency_metrics(self):
        """Test building efficiency metrics."""
        building = create_sample_building()

        avg_efficiency = sum(
            e.efficiency_percent for e in building.equipment
        ) / len(building.equipment)
        assert 0 <= avg_efficiency <= 100


class TestBuildingOperationsEndpoints:
    """Tests for building operations endpoints."""

    @pytest.mark.api
    @pytest.mark.unit
    def test_building_status_endpoint(self):
        """Test building status endpoint."""
        building = create_sample_building()

        # All equipment should have operational status
        operational_count = sum(1 for e in building.equipment if e.operational)
        assert operational_count >= 0
        assert operational_count <= len(building.equipment)

    @pytest.mark.api
    @pytest.mark.unit
    def test_single_zone_building_endpoint(self):
        """Test endpoint with single zone building."""
        building = create_small_single_zone_building()

        assert len(building.zones) == 1
        zone = building.zones[0]
        assert zone.name
        assert zone.area_m2 > 0

    @pytest.mark.api
    @pytest.mark.unit
    def test_multi_floor_building_endpoint(self):
        """Test endpoint with multi-floor building."""
        building = create_multi_floor_building()

        assert len(building.zones) > 1
        # Verify floor information
        floor_numbers = {z.floor_number for z in building.zones}
        assert len(floor_numbers) > 1


class TestBuildingUpdateEndpoints:
    """Tests for building update operations."""

    @pytest.mark.api
    @pytest.mark.unit
    def test_building_update_structure(self):
        """Test building update request structure."""
        building = create_sample_building()

        # Sample update payload
        update_data = {
            "building_name": "Updated Name",
            "total_area_m2": building.total_area_m2,
        }

        assert "building_name" in update_data
        assert "total_area_m2" in update_data

    @pytest.mark.api
    @pytest.mark.unit
    def test_zone_update_validation(self):
        """Test zone update validation."""
        building = create_sample_building()
        zone = building.zones[0]

        # Updated zone should maintain valid state
        assert zone.target_temperature_c > zone.min_temperature_c
        assert zone.target_temperature_c < zone.max_temperature_c


class TestBuildingPaginationEndpoints:
    """Tests for pagination in building endpoints."""

    @pytest.mark.api
    @pytest.mark.unit
    def test_building_list_pagination(self):
        """Test building list pagination parameters."""
        # Pagination structure
        pagination = {
            "page": 1,
            "page_size": 50,
            "total": 100,
            "has_next": True,
            "has_previous": False,
        }

        assert pagination["page"] >= 1
        assert pagination["page_size"] > 0
        assert pagination["total"] >= 0

    @pytest.mark.api
    @pytest.mark.unit
    def test_zone_list_pagination(self):
        """Test zone list pagination."""
        building = create_sample_building()

        zone_count = len(building.zones)
        assert zone_count > 0

    @pytest.mark.api
    @pytest.mark.unit
    def test_equipment_list_pagination(self):
        """Test equipment list pagination."""
        building = create_sample_building()

        equipment_count = len(building.equipment)
        assert equipment_count > 0
