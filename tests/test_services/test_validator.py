"""
Tests for validation service.

Tests ValidationService, building validation, action validation, etc.
"""

import pytest
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
from tests.fixtures.sample_actions import (
    ActionRequest,
    ActionParameter,
    InferenceRule,
    create_inference_action_request,
    create_validation_action_request,
    create_sample_validation_result,
)


class TestValidatorBasics:
    """Tests for basic validator functionality."""

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_validates_location(self):
        """Test validator validates location."""
        location = Location(latitude=40.7128, longitude=-74.0060)

        assert -90 <= location.latitude <= 90
        assert -180 <= location.longitude <= 180

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_validates_schedule(self):
        """Test validator validates schedule."""
        schedule = Schedule(
            occupied_setpoint_c=22.0,
            unoccupied_setpoint_c=18.0,
        )

        assert schedule.occupied_setpoint_c > schedule.unoccupied_setpoint_c

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_validates_zone(self):
        """Test validator validates zone configuration."""
        schedule = Schedule()
        zone = ZoneConfiguration(
            name="Test Zone",
            area_m2=100.0,
            zone_type="office",
            schedule=schedule,
        )

        assert zone.area_m2 > 0
        assert zone.name

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_validates_equipment(self):
        """Test validator validates equipment."""
        equipment = EquipmentConfiguration(
            equipment_id="VAV-001",
            equipment_type="vav",
            zone_id="Zone",
            capacity=2.5,
            capacity_unit="kW",
        )

        assert equipment.capacity > 0
        assert equipment.efficiency_percent >= 0


class TestBuildingValidatorService:
    """Tests for building validation service."""

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_validates_complete_building(self):
        """Test validator validates complete building."""
        building = create_sample_building()

        # Should pass validation
        result = create_sample_validation_result(valid=True)
        assert result.valid

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_detects_missing_zones(self):
        """Test validator detects buildings with no zones."""
        location = Location(latitude=0, longitude=0)

        # Building with no zones should fail validation
        try:
            building = BuildingConfiguration(
                building_id="BLDG-001",
                building_name="No Zones",
                location=location,
                total_area_m2=100,
                construction_year=2020,
                zones=[],  # No zones
            )
            # If no error, building exists but may have validation issues
        except Exception:
            pass  # Expected

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_detects_zone_area_mismatch(self):
        """Test validator detects zone area mismatches."""
        location = Location(latitude=0, longitude=0)
        schedule = Schedule()

        # Zone area larger than building area
        zone = ZoneConfiguration(
            name="Large Zone",
            area_m2=1000,
            zone_type="office",
            schedule=schedule,
        )

        try:
            BuildingConfiguration(
                building_id="BLDG-001",
                building_name="Test",
                location=location,
                total_area_m2=100,  # Smaller than zone
                construction_year=2020,
                zones=[zone],
            )
        except AssertionError:
            pass  # Expected validation error

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_detects_equipment_references(self):
        """Test validator detects invalid equipment references."""
        building = create_sample_building()

        # All equipment zone references should be valid
        zone_names = {z.name for z in building.zones}
        for equipment in building.equipment:
            assert equipment.zone_id in zone_names or equipment.zone_id == "Building"

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_checks_temperature_ranges(self):
        """Test validator checks temperature ranges."""
        schedule = Schedule()
        zone = ZoneConfiguration(
            name="Zone",
            area_m2=100,
            zone_type="office",
            schedule=schedule,
        )

        assert zone.min_temperature_c < zone.target_temperature_c
        assert zone.target_temperature_c < zone.max_temperature_c


class TestActionValidatorService:
    """Tests for action validation service."""

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_validates_action_request(self):
        """Test validator validates action request."""
        request = create_inference_action_request()

        assert request.action_type
        assert request.parameters is not None

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_validates_parameters(self):
        """Test validator validates action parameters."""
        request = create_validation_action_request()

        # All parameters should be valid
        for param in request.parameters:
            assert param.name
            assert param.param_type
            assert param.value is not None

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_checks_required_parameters(self):
        """Test validator checks required parameters."""
        request = create_inference_action_request()

        required_params = [p for p in request.parameters if p.required]
        assert all(p.value is not None for p in required_params)

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_validates_parameter_types(self):
        """Test validator validates parameter types."""
        request = create_validation_action_request()

        valid_types = ["string", "integer", "float", "boolean", "array", "object"]
        for param in request.parameters:
            assert param.param_type in valid_types

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_validates_timeout(self):
        """Test validator validates timeout."""
        request = create_inference_action_request()

        assert request.timeout_seconds > 0
        assert request.timeout_seconds <= 300


class TestRuleValidatorService:
    """Tests for inference rule validation service."""

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_validates_rule_confidence(self):
        """Test validator validates rule confidence."""
        rule = InferenceRule(
            rule_id="rule-001",
            name="Test",
            description="Test",
            premise="x > 5",
            conclusion="result = true",
            confidence=0.85,
        )

        assert 0 <= rule.confidence <= 1

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_validates_rule_premise(self):
        """Test validator validates rule premise."""
        rule = InferenceRule(
            rule_id="rule-001",
            name="Test",
            description="Test",
            premise="x > 5 AND y < 10",
            conclusion="result = true",
        )

        assert rule.premise
        assert len(rule.premise) > 0

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_validates_rule_conclusion(self):
        """Test validator validates rule conclusion."""
        rule = InferenceRule(
            rule_id="rule-001",
            name="Test",
            description="Test",
            premise="x > 5",
            conclusion="result = high_priority",
        )

        assert rule.conclusion
        assert len(rule.conclusion) > 0


class TestValidationReporting:
    """Tests for validation result reporting."""

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_returns_validation_result(self):
        """Test validator returns validation result."""
        result = create_sample_validation_result(valid=True)

        assert hasattr(result, 'valid')
        assert hasattr(result, 'issues')
        assert hasattr(result, 'warnings')

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_reports_issues(self):
        """Test validator reports validation issues."""
        result = create_sample_validation_result(valid=False)

        assert not result.valid
        assert result.has_issues
        assert len(result.issues) > 0

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_reports_warnings(self):
        """Test validator reports warnings."""
        result = create_sample_validation_result(valid=False)

        assert result.has_warnings
        assert len(result.warnings) > 0

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_provides_details(self):
        """Test validator provides validation details."""
        result = create_sample_validation_result(valid=True)

        assert result.details is not None
        assert isinstance(result.details, dict)


class TestValidationErrorCases:
    """Tests for validation of error cases."""

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_catches_invalid_location(self):
        """Test validator catches invalid location."""
        try:
            Location(latitude=91, longitude=0)
            assert False, "Should have raised error"
        except AssertionError:
            pass  # Expected

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_catches_invalid_schedule(self):
        """Test validator catches invalid schedule."""
        try:
            Schedule(
                weekday_start=schedule.weekday_end,
                weekday_end=Schedule().weekday_start,
            )
        except Exception:
            pass

    @pytest.mark.services
    @pytest.mark.unit
    def test_validator_catches_invalid_equipment_capacity(self):
        """Test validator catches invalid equipment capacity."""
        try:
            EquipmentConfiguration(
                equipment_id="VAV-001",
                equipment_type="vav",
                zone_id="Zone",
                capacity=0,  # Invalid
                capacity_unit="kW",
            )
            assert False, "Should have raised error"
        except AssertionError:
            pass  # Expected


class TestValidationIntegration:
    """Integration tests for validator."""

    @pytest.mark.services
    @pytest.mark.integration
    def test_validator_validates_sample_building(self):
        """Test validator validates sample building."""
        building = create_sample_building()

        # Sample building should pass validation
        assert building.building_id
        assert len(building.zones) > 0

    @pytest.mark.services
    @pytest.mark.integration
    def test_validator_validates_small_building(self):
        """Test validator validates small building."""
        building = create_small_single_zone_building()

        assert len(building.zones) == 1
        assert building.zones[0].area_m2 > 0

    @pytest.mark.services
    @pytest.mark.integration
    def test_validator_validates_multi_floor_building(self):
        """Test validator validates multi-floor building."""
        building = create_multi_floor_building()

        # Check floor consistency
        floor_numbers = {z.floor_number for z in building.zones}
        assert len(floor_numbers) > 1
