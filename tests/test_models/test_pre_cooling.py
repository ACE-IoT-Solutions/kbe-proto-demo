"""
Tests for Pre-Cooling Action Model

Comprehensive tests for pre-cooling input validation, SHACL constraints,
and ODRL governance policies.
"""

import pytest
from pydantic import ValidationError
from src.models.actions.pre_cooling import PreCoolingInput, PreCoolingAction


class TestPreCoolingInputValidation:
    """Test basic input validation for pre-cooling actions."""

    def test_valid_pre_cooling_input(self):
        """Test that valid pre-cooling input passes validation."""
        input_data = {
            "zone_ids": ["Z001", "Z002"],
            "target_temp": 65.0,
            "start_time": "05:00",
            "occupancy_start": "08:00",
            "max_rate_delta": 5.0,
            "priority": "medium",
            "enable_adaptive": True,
            "reason": "Peak demand optimization"
        }

        result = PreCoolingInput(**input_data)

        assert result.zone_ids == ["Z001", "Z002"]
        assert result.target_temp == 65.0
        assert result.start_time == "05:00"
        assert result.occupancy_start == "08:00"
        assert result.max_rate_delta == 5.0
        assert result.enable_adaptive is True

    def test_target_temp_minimum_constraint(self):
        """Test SHACL constraint: Target temp must be >= 60°F."""
        input_data = {
            "zone_ids": ["Z001"],
            "target_temp": 59.0,  # Below minimum
            "start_time": "05:00",
            "occupancy_start": "08:00",
            "reason": "Test"
        }

        with pytest.raises(ValidationError) as exc_info:
            PreCoolingInput(**input_data)

        assert "greater than or equal to 60" in str(exc_info.value)

    def test_target_temp_maximum_constraint(self):
        """Test SHACL constraint: Target temp must be <= 75°F."""
        input_data = {
            "zone_ids": ["Z001"],
            "target_temp": 76.0,  # Above maximum
            "start_time": "05:00",
            "occupancy_start": "08:00",
            "reason": "Test"
        }

        with pytest.raises(ValidationError) as exc_info:
            PreCoolingInput(**input_data)

        assert "less than or equal to 75" in str(exc_info.value)

    def test_target_temp_economics_validation(self):
        """Test SHACL constraint: Target temp >= 62°F for economics."""
        input_data = {
            "zone_ids": ["Z001"],
            "target_temp": 61.0,  # Too aggressive
            "start_time": "05:00",
            "occupancy_start": "08:00",
            "reason": "Test"
        }

        with pytest.raises(ValidationError) as exc_info:
            PreCoolingInput(**input_data)

        assert "too aggressive" in str(exc_info.value).lower()
        assert "62" in str(exc_info.value)

    def test_time_format_validation(self):
        """Test SHACL constraint: Time must be HH:MM format."""
        input_data = {
            "zone_ids": ["Z001"],
            "target_temp": 65.0,
            "start_time": "25:00",  # Invalid hour
            "occupancy_start": "08:00",
            "reason": "Test"
        }

        with pytest.raises(ValidationError) as exc_info:
            PreCoolingInput(**input_data)

        assert "String should match pattern" in str(exc_info.value)

    def test_time_window_minimum_constraint(self):
        """Test SHACL constraint: Minimum 30 minute window."""
        input_data = {
            "zone_ids": ["Z001"],
            "target_temp": 65.0,
            "start_time": "07:45",
            "occupancy_start": "08:00",  # Only 15 minutes
            "reason": "Test"
        }

        with pytest.raises(ValidationError) as exc_info:
            PreCoolingInput(**input_data)

        assert "too short" in str(exc_info.value).lower()
        assert "30 minutes" in str(exc_info.value)

    def test_time_window_maximum_constraint(self):
        """Test SHACL constraint: Maximum 8 hour window."""
        input_data = {
            "zone_ids": ["Z001"],
            "target_temp": 65.0,
            "start_time": "05:00",
            "occupancy_start": "14:00",  # 9 hours
            "reason": "Test"
        }

        with pytest.raises(ValidationError) as exc_info:
            PreCoolingInput(**input_data)

        assert "too long" in str(exc_info.value).lower()
        assert "8 hours" in str(exc_info.value)

    def test_overnight_time_window(self):
        """Test that overnight pre-cooling windows work correctly."""
        input_data = {
            "zone_ids": ["Z001"],
            "target_temp": 65.0,
            "start_time": "23:00",
            "occupancy_start": "07:00",  # Next day
            "reason": "Overnight pre-cooling"
        }

        result = PreCoolingInput(**input_data)

        assert result.start_time == "23:00"
        assert result.occupancy_start == "07:00"

    def test_cooling_rate_minimum(self):
        """Test SHACL constraint: Min cooling rate 1°F/hr."""
        input_data = {
            "zone_ids": ["Z001"],
            "target_temp": 65.0,
            "start_time": "05:00",
            "occupancy_start": "08:00",
            "max_rate_delta": 0.5,  # Below minimum
            "reason": "Test"
        }

        with pytest.raises(ValidationError) as exc_info:
            PreCoolingInput(**input_data)

        assert "greater than or equal to 1" in str(exc_info.value)

    def test_cooling_rate_maximum(self):
        """Test SHACL constraint: Max cooling rate 10°F/hr."""
        input_data = {
            "zone_ids": ["Z001"],
            "target_temp": 65.0,
            "start_time": "05:00",
            "occupancy_start": "08:00",
            "max_rate_delta": 15.0,  # Above maximum
            "reason": "Test"
        }

        with pytest.raises(ValidationError) as exc_info:
            PreCoolingInput(**input_data)

        assert "less than or equal to 10" in str(exc_info.value)

    def test_priority_emergency_not_allowed(self):
        """Test ODRL policy: Emergency priority not allowed for pre-cooling."""
        input_data = {
            "zone_ids": ["Z001"],
            "target_temp": 65.0,
            "start_time": "05:00",
            "occupancy_start": "08:00",
            "priority": "emergency",  # Not allowed
            "reason": "Test"
        }

        with pytest.raises(ValidationError) as exc_info:
            PreCoolingInput(**input_data)

        # Should fail because emergency is not in allowed literals
        assert "Input should be" in str(exc_info.value)

    def test_duplicate_zone_ids(self):
        """Test SHACL constraint: No duplicate zone IDs."""
        input_data = {
            "zone_ids": ["Z001", "Z002", "Z001"],  # Duplicate
            "target_temp": 65.0,
            "start_time": "05:00",
            "occupancy_start": "08:00",
            "reason": "Test"
        }

        with pytest.raises(ValidationError) as exc_info:
            PreCoolingInput(**input_data)

        assert "Duplicate zone IDs" in str(exc_info.value)

    def test_empty_zone_id_string(self):
        """Test SHACL constraint: Zone IDs cannot be empty."""
        input_data = {
            "zone_ids": ["Z001", "   ", "Z002"],  # Empty string
            "target_temp": 65.0,
            "start_time": "05:00",
            "occupancy_start": "08:00",
            "reason": "Test"
        }

        with pytest.raises(ValidationError) as exc_info:
            PreCoolingInput(**input_data)

        assert "cannot be empty" in str(exc_info.value)

    def test_outdoor_temp_range_validation(self):
        """Test outdoor temperature constraint validation."""
        input_data = {
            "zone_ids": ["Z001"],
            "target_temp": 65.0,
            "start_time": "05:00",
            "occupancy_start": "08:00",
            "min_outdoor_temp": 80.0,
            "max_outdoor_temp": 70.0,  # Max < Min
            "reason": "Test"
        }

        with pytest.raises(ValidationError) as exc_info:
            PreCoolingInput(**input_data)

        assert "must be less than" in str(exc_info.value)

    def test_cost_limit_validation(self):
        """Test cost limit must be non-negative."""
        input_data = {
            "zone_ids": ["Z001"],
            "target_temp": 65.0,
            "start_time": "05:00",
            "occupancy_start": "08:00",
            "cost_limit_usd": -10.0,  # Negative
            "reason": "Test"
        }

        with pytest.raises(ValidationError) as exc_info:
            PreCoolingInput(**input_data)

        assert "greater than or equal to 0" in str(exc_info.value)


class TestPreCoolingActionMethods:
    """Test PreCoolingAction static methods."""

    def test_get_input_schema(self):
        """Test that input schema is properly defined."""
        schema = PreCoolingAction.get_input_schema()

        assert schema["type"] == "object"
        assert "zone_ids" in schema["properties"]
        assert "target_temp" in schema["properties"]
        assert "start_time" in schema["properties"]
        assert "occupancy_start" in schema["properties"]
        assert "reason" in schema["required"]

    def test_get_validation_rules(self):
        """Test that validation rules are properly defined."""
        rules = PreCoolingAction.get_validation_rules()

        assert len(rules) > 0
        assert any("60-75°F" in rule for rule in rules)
        assert any("30 min - 8 hours" in rule for rule in rules)
        assert any("Energy Manager" in rule for rule in rules)

    def test_get_odrl_policies(self):
        """Test ODRL governance policies."""
        policies = PreCoolingAction.get_odrl_policies()

        # Operators cannot execute
        assert policies["operator"]["permitted"] is False

        # Facility managers have constraints
        assert policies["facility_manager"]["permitted"] is True
        assert len(policies["facility_manager"]["constraints"]) > 0

        # Energy managers have full access
        assert policies["energy_manager"]["permitted"] is True

        # Contractors cannot execute
        assert policies["contractor"]["permitted"] is False

    def test_validate_input_success(self):
        """Test input validation wrapper method."""
        input_data = {
            "zone_ids": ["Z001"],
            "target_temp": 65.0,
            "start_time": "05:00",
            "occupancy_start": "08:00",
            "reason": "Test"
        }

        result = PreCoolingAction.validate_input(input_data)

        assert isinstance(result, PreCoolingInput)
        assert result.target_temp == 65.0

    def test_calculate_estimated_cost(self):
        """Test cost estimation calculation."""
        cost = PreCoolingAction.calculate_estimated_cost(
            zone_count=2,
            target_temp_delta=8.0,  # Cool by 8°F
            duration_hours=3.0,
            electricity_rate_per_kwh=0.12
        )

        # Expected: 2 zones * 8°F * 3 hours * 3 kW * $0.12
        expected = 2 * 8 * 3 * 3.0 * 0.12
        assert cost == pytest.approx(expected)

    def test_calculate_estimated_savings(self):
        """Test peak demand savings calculation."""
        savings = PreCoolingAction.calculate_estimated_savings(
            zone_count=3,
            peak_demand_rate_per_kw=15.0,
            estimated_peak_reduction_kw=5.0
        )

        # Expected: 3 zones * 5 kW * $15/kW
        expected = 3 * 5.0 * 15.0
        assert savings == pytest.approx(expected)

    def test_get_preconditions(self):
        """Test precondition specifications."""
        preconditions = PreCoolingAction.get_preconditions()

        assert len(preconditions) > 0
        assert any("zones_exist" in pc for pc in preconditions)
        assert any("weather" in pc.lower() for pc in preconditions)
        assert any("energy_prices" in pc for pc in preconditions)

    def test_get_postconditions(self):
        """Test postcondition specifications."""
        postconditions = PreCoolingAction.get_postconditions()

        assert len(postconditions) > 0
        assert any("target_temp" in pc for pc in postconditions)
        assert any("schedule_created" in pc for pc in postconditions)
        assert any("audit_log" in pc for pc in postconditions)


class TestPreCoolingODRLGovernance:
    """Test ODRL governance policies for pre-cooling."""

    def test_operator_cannot_execute(self):
        """Test ODRL: Operators cannot execute pre-cooling."""
        policies = PreCoolingAction.get_odrl_policies()

        operator_policy = policies["operator"]
        assert operator_policy["permitted"] is False
        assert "reason" in operator_policy

    def test_facility_manager_constraints(self):
        """Test ODRL: Facility manager has zone and cost limits."""
        policies = PreCoolingAction.get_odrl_policies()

        fm_policy = policies["facility_manager"]
        assert fm_policy["permitted"] is True

        constraints = fm_policy["constraints"]
        assert any("max_zones: 3" in c for c in constraints)
        assert any("$50" in c for c in constraints)

    def test_energy_manager_full_access(self):
        """Test ODRL: Energy manager has full access."""
        policies = PreCoolingAction.get_odrl_policies()

        em_policy = policies["energy_manager"]
        assert em_policy["permitted"] is True

        constraints = em_policy["constraints"]
        assert any("unlimited" in c for c in constraints)

    def test_contractor_cannot_execute(self):
        """Test ODRL: Contractors cannot execute pre-cooling."""
        policies = PreCoolingAction.get_odrl_policies()

        contractor_policy = policies["contractor"]
        assert contractor_policy["permitted"] is False
        assert "reason" in contractor_policy


class TestPreCoolingEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_exactly_30_minute_window(self):
        """Test exactly 30 minute window (minimum allowed)."""
        input_data = {
            "zone_ids": ["Z001"],
            "target_temp": 65.0,
            "start_time": "07:30",
            "occupancy_start": "08:00",
            "reason": "Minimum window test"
        }

        result = PreCoolingInput(**input_data)
        assert result.start_time == "07:30"

    def test_exactly_8_hour_window(self):
        """Test exactly 8 hour window (maximum allowed)."""
        input_data = {
            "zone_ids": ["Z001"],
            "target_temp": 65.0,
            "start_time": "00:00",
            "occupancy_start": "08:00",
            "reason": "Maximum window test"
        }

        result = PreCoolingInput(**input_data)
        assert result.occupancy_start == "08:00"

    def test_target_temp_at_62_degrees(self):
        """Test target temp at 62°F (minimum for economics)."""
        input_data = {
            "zone_ids": ["Z001"],
            "target_temp": 62.0,
            "start_time": "05:00",
            "occupancy_start": "08:00",
            "reason": "Boundary test"
        }

        result = PreCoolingInput(**input_data)
        assert result.target_temp == 62.0

    def test_multiple_zones(self):
        """Test with multiple zones."""
        input_data = {
            "zone_ids": ["Z001", "Z002", "Z003", "Z004", "Z005"],
            "target_temp": 65.0,
            "start_time": "05:00",
            "occupancy_start": "08:00",
            "reason": "Multi-zone test"
        }

        result = PreCoolingInput(**input_data)
        assert len(result.zone_ids) == 5

    def test_adaptive_learning_disabled(self):
        """Test with adaptive learning disabled."""
        input_data = {
            "zone_ids": ["Z001"],
            "target_temp": 65.0,
            "start_time": "05:00",
            "occupancy_start": "08:00",
            "enable_adaptive": False,
            "reason": "No adaptive learning"
        }

        result = PreCoolingInput(**input_data)
        assert result.enable_adaptive is False
