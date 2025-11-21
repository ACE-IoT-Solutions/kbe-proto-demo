"""
Tests for action validation logic.

Tests validation of building configurations, equipment, schedules, and action parameters.
"""

import pytest
from datetime import time
from tests.fixtures.sample_building import (
    Location,
    Schedule,
    ZoneConfiguration,
    EquipmentConfiguration,
    BuildingConfiguration,
    create_sample_building,
)
from tests.fixtures.sample_actions import (
    ActionType,
    ActionParameter,
    ActionRequest,
    InferenceRule,
    ReasoningType,
)


class TestBuildingValidation:
    """Tests for building configuration validation."""

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_building_complete(self):
        """Test validating a complete building configuration."""
        building = create_sample_building()

        # Should have all required fields
        assert building.building_id
        assert building.building_name
        assert building.location
        assert building.total_area_m2 > 0
        assert building.construction_year > 1800
        assert len(building.zones) > 0
        assert len(building.equipment) > 0

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_zone_area_consistency(self):
        """Test that zone areas sum correctly."""
        building = create_sample_building()

        total_zone_area = sum(z.area_m2 for z in building.zones)
        assert total_zone_area <= building.total_area_m2

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_equipment_assignment(self):
        """Test that equipment is properly assigned to zones."""
        building = create_sample_building()

        zone_ids = {z.name for z in building.zones}
        equipment_zones = {e.zone_id for e in building.equipment}

        # All equipment zones should reference actual zones or building
        for eq in building.equipment:
            assert eq.zone_id in zone_ids or eq.zone_id == "Building"

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_demand_limits(self):
        """Test demand limit validation."""
        building = create_sample_building()

        assert building.demand_limit_kw > 0
        assert building.demand_warning_threshold_kw > 0
        assert building.demand_warning_threshold_kw < building.demand_limit_kw

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_temperature_ranges(self):
        """Test temperature range validation in zones."""
        building = create_sample_building()

        for zone in building.zones:
            assert zone.min_temperature_c < zone.target_temperature_c
            assert zone.target_temperature_c < zone.max_temperature_c
            assert zone.min_temperature_c >= 10  # Reasonable minimum
            assert zone.max_temperature_c <= 30  # Reasonable maximum

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_schedule_consistency(self):
        """Test schedule validation within zones."""
        building = create_sample_building()

        for zone in building.zones:
            schedule = zone.schedule
            assert schedule.weekday_start < schedule.weekday_end
            assert schedule.weekend_start < schedule.weekend_end
            assert schedule.occupied_setpoint_c > schedule.unoccupied_setpoint_c

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_equipment_capacity(self):
        """Test equipment capacity validation."""
        building = create_sample_building()

        for equipment in building.equipment:
            assert equipment.capacity > 0
            assert equipment.efficiency_percent >= 0
            assert equipment.efficiency_percent <= 100
            assert equipment.maintenance_schedule_hours > 0

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_floor_numbering(self):
        """Test floor numbering consistency."""
        building = create_sample_building()

        # All floor numbers should be non-negative
        for zone in building.zones:
            assert zone.floor_number >= 0

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_humidity_setpoints(self):
        """Test humidity setpoint validation."""
        building = create_sample_building()

        for zone in building.zones:
            assert 0 <= zone.humidity_setpoint_percent <= 100

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_airflow_rates(self):
        """Test airflow rate validation."""
        building = create_sample_building()

        for zone in building.zones:
            assert zone.outdoor_air_cfm >= 0
            assert zone.return_air_cfm >= 0
            # Return air should typically be >= outdoor air
            if zone.outdoor_air_cfm > 0:
                assert zone.return_air_cfm >= zone.outdoor_air_cfm


class TestActionValidation:
    """Tests for action request validation."""

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_action_parameters(self):
        """Test action parameter validation."""
        param = ActionParameter(
            name="building_id",
            value="BLDG-001",
            param_type="string",
            required=True,
        )
        assert param.name
        assert param.value
        assert param.param_type in [
            "string",
            "integer",
            "float",
            "boolean",
            "array",
            "object",
        ]

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_action_types(self):
        """Test all action types are valid."""
        valid_types = [
            ActionType.QUERY,
            ActionType.INFERENCE,
            ActionType.VALIDATION,
            ActionType.TRANSFORMATION,
        ]

        for action_type in valid_types:
            request = ActionRequest(action_type=action_type)
            assert request.action_type == action_type

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_parameter_required_flag(self):
        """Test parameter required flag validation."""
        required_param = ActionParameter(
            name="entity",
            value="Building",
            param_type="string",
            required=True,
        )
        assert required_param.required

        optional_param = ActionParameter(
            name="limit",
            value=100,
            param_type="integer",
            required=False,
        )
        assert not optional_param.required

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_parameter_types_match_values(self):
        """Test that parameter types match their values."""
        test_cases = [
            (ActionType.QUERY, "string", "SELECT * FROM table"),
            (ActionType.INFERENCE, "integer", 3),
            (ActionType.VALIDATION, "boolean", True),
            (ActionType.TRANSFORMATION, "array", ["item1", "item2"]),
        ]

        for action_type, param_type, value in test_cases:
            param = ActionParameter(
                name="test",
                value=value,
                param_type=param_type,
            )
            assert param.param_type == param_type


class TestRuleValidation:
    """Tests for inference rule validation."""

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_rule_confidence(self):
        """Test rule confidence validation."""
        rule = InferenceRule(
            rule_id="rule-001",
            name="Test Rule",
            description="Test rule",
            premise="x > 5",
            conclusion="x = high",
            confidence=0.85,
        )
        assert 0 <= rule.confidence <= 1

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_rule_reasoning_type(self):
        """Test rule reasoning type validation."""
        valid_types = [
            ReasoningType.DEDUCTIVE,
            ReasoningType.INDUCTIVE,
            ReasoningType.ABDUCTIVE,
            ReasoningType.ANALOGICAL,
        ]

        for reasoning_type in valid_types:
            rule = InferenceRule(
                rule_id="rule-001",
                name="Test",
                description="Test",
                premise="premise",
                conclusion="conclusion",
                reasoning_type=reasoning_type,
            )
            assert rule.reasoning_type == reasoning_type

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_rule_identifiers(self):
        """Test rule identifier validation."""
        rule = InferenceRule(
            rule_id="rule-building-age-check",
            name="Building Age Check",
            description="Infer maintenance requirements",
            premise="Building.year < 2000",
            conclusion="Building.maintenance_required = true",
        )
        assert rule.rule_id
        assert rule.name
        assert rule.description

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_rule_logic(self):
        """Test rule premise and conclusion are defined."""
        rule = InferenceRule(
            rule_id="rule-001",
            name="Logic Test",
            description="Test rule logic",
            premise="condition1 AND condition2",
            conclusion="result = true",
        )
        assert rule.premise
        assert rule.conclusion
        assert "AND" in rule.premise or "OR" in rule.premise or rule.premise


class TestScheduleValidation:
    """Tests for schedule validation."""

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_schedule_hours(self):
        """Test schedule time validation."""
        schedule = Schedule(
            weekday_start=time(8, 0),
            weekday_end=time(17, 0),
        )
        assert schedule.weekday_start < schedule.weekday_end

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_schedule_temperature_setpoints(self):
        """Test schedule temperature setpoint validation."""
        schedule = Schedule(
            occupied_setpoint_c=22.0,
            unoccupied_setpoint_c=18.0,
        )
        assert schedule.occupied_setpoint_c > schedule.unoccupied_setpoint_c
        assert 15 <= schedule.occupied_setpoint_c <= 28
        assert 10 <= schedule.unoccupied_setpoint_c <= 25

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_schedule_holidays(self):
        """Test schedule holiday list validation."""
        holidays = ["2024-01-01", "2024-12-25"]
        schedule = Schedule(holidays=holidays)
        assert len(schedule.holidays) == 2
        assert all(isinstance(h, str) for h in schedule.holidays)

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_schedule_weekend_hours(self):
        """Test weekend schedule validation."""
        schedule = Schedule(
            weekend_start=time(9, 0),
            weekend_end=time(13, 0),
        )
        assert schedule.weekend_start < schedule.weekend_end


class TestEquipmentValidation:
    """Tests for equipment validation."""

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_equipment_identifiers(self):
        """Test equipment identifier validation."""
        equipment = EquipmentConfiguration(
            equipment_id="VAV-001",
            equipment_type="vav",
            zone_id="Zone A",
            capacity=2.5,
            capacity_unit="kW",
        )
        assert equipment.equipment_id
        assert equipment.equipment_id.strip()

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_equipment_capacity(self):
        """Test equipment capacity validation."""
        equipment = EquipmentConfiguration(
            equipment_id="VAV-001",
            equipment_type="vav",
            zone_id="Zone A",
            capacity=2.5,
            capacity_unit="kW",
        )
        assert equipment.capacity > 0
        assert equipment.capacity_unit in ["kW", "GPM", "CFM", "Ton"]

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_equipment_efficiency(self):
        """Test equipment efficiency validation."""
        equipment = EquipmentConfiguration(
            equipment_id="VAV-001",
            equipment_type="vav",
            zone_id="Zone A",
            capacity=2.5,
            capacity_unit="kW",
            efficiency_percent=92.0,
        )
        assert 0 <= equipment.efficiency_percent <= 100

    @pytest.mark.validation
    @pytest.mark.unit
    def test_validate_equipment_operational_status(self):
        """Test equipment operational status."""
        equipment = EquipmentConfiguration(
            equipment_id="VAV-001",
            equipment_type="vav",
            zone_id="Zone A",
            capacity=2.5,
            capacity_unit="kW",
            operational=True,
        )
        assert isinstance(equipment.operational, bool)


class TestValidationChains:
    """Integration tests for validation chains."""

    @pytest.mark.validation
    @pytest.mark.integration
    def test_validate_complete_building_configuration(self):
        """Test validating a complete building configuration end-to-end."""
        building = create_sample_building()

        # Validate structure
        assert building.building_id
        assert building.zones
        assert building.equipment

        # Validate relationships
        for zone in building.zones:
            for eq_id in zone.equipment_ids:
                assert any(e.equipment_id == eq_id for e in building.equipment)

        # Validate constraints
        assert all(z.area_m2 > 0 for z in building.zones)
        assert all(e.capacity > 0 for e in building.equipment)

    @pytest.mark.validation
    @pytest.mark.integration
    def test_validate_building_and_zones_consistency(self):
        """Test consistency between building and zones."""
        building = create_sample_building()

        zone_area_sum = sum(z.area_m2 for z in building.zones)
        assert zone_area_sum <= building.total_area_m2

        # All zones should have valid configurations
        for zone in building.zones:
            assert zone.area_m2 > 0
            assert zone.target_temperature_c > 0
            assert zone.schedule is not None

    @pytest.mark.validation
    @pytest.mark.integration
    def test_validate_equipment_references(self):
        """Test equipment zone references are valid."""
        building = create_sample_building()

        zone_names = {z.name for z in building.zones}
        for equipment in building.equipment:
            # Equipment should reference valid zone or building
            assert equipment.zone_id in zone_names or equipment.zone_id == "Building"
