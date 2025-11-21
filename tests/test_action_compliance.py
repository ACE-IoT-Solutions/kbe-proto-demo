"""
Abstract Action Compliance Test Suite

Validates that all actions meet modularity requirements:
- Complete UI field definitions
- Graph representation metadata
- Audit log formatting
- SHACL constraints
- ODRL governance policies
- Handler and validation class references
"""

import pytest
from src.models.action_descriptor import action_registry


# Import all descriptors to register them
from src.models.descriptors import adjust_setpoint_descriptor  # noqa: F401
from src.models.descriptors import load_shed_descriptor  # noqa: F401
from src.models.descriptors import pre_cooling_descriptor  # noqa: F401


class TestActionCompliance:
    """
    Abstract compliance tests that all actions must pass.
    Ensures modularity and self-containment.
    """

    @pytest.fixture
    def all_actions(self):
        """Get all registered actions."""
        return action_registry.list_all()

    def test_all_actions_registered(self, all_actions):
        """Test that actions are registered in the registry."""
        assert len(all_actions) >= 3, "Expected at least 3 actions registered"

        action_ids = [a.action_id for a in all_actions]
        assert "adjust-setpoint" in action_ids
        assert "load-shed" in action_ids
        assert "pre-cooling" in action_ids

    def test_action_has_complete_metadata(self, all_actions):
        """Test that every action has all required metadata fields."""
        for action in all_actions:
            # Basic metadata
            assert action.action_id, f"Action missing action_id"
            assert action.action_name, f"{action.action_id}: Missing action_name"
            assert action.action_type, f"{action.action_id}: Missing action_type"
            assert action.description, f"{action.action_id}: Missing description"
            assert action.version, f"{action.action_id}: Missing version"

    def test_action_has_ui_fields(self, all_actions):
        """Test that every action defines UI fields."""
        for action in all_actions:
            assert len(action.ui_fields) > 0, \
                f"{action.action_id}: No UI fields defined"

    def test_action_has_user_role_field(self, all_actions):
        """Test that every action has a user_role field for governance."""
        for action in all_actions:
            field_names = [f.field_name for f in action.ui_fields]
            assert "user_role" in field_names, \
                f"{action.action_id}: Missing required 'user_role' field for governance"

    def test_ui_fields_have_required_properties(self, all_actions):
        """Test that all UI fields have required properties."""
        for action in all_actions:
            for field in action.ui_fields:
                assert field.field_name, \
                    f"{action.action_id}: UI field missing field_name"
                assert field.field_type, \
                    f"{action.action_id}: Field {field.field_name} missing field_type"
                assert field.label, \
                    f"{action.action_id}: Field {field.field_name} missing label"

                # Validate field_type is recognized
                valid_types = ["text", "number", "select", "checkbox", "time",
                               "multi-select", "zone-selector"]
                assert field.field_type in valid_types, \
                    f"{action.action_id}: Field {field.field_name} has invalid type '{field.field_type}'"

                # Select fields must have options
                if field.field_type in ["select", "multi-select"]:
                    assert field.options is not None and len(field.options) > 0, \
                        f"{action.action_id}: Select field {field.field_name} missing options"

    def test_action_has_graph_nodes(self, all_actions):
        """Test that every action defines graph representation."""
        for action in all_actions:
            assert len(action.graph_nodes) > 0, \
                f"{action.action_id}: No graph nodes defined"

            # Should have at least one action node
            action_nodes = [n for n in action.graph_nodes if n.node_type == "action"]
            assert len(action_nodes) > 0, \
                f"{action.action_id}: No action node in graph"

    def test_graph_nodes_have_relationships(self, all_actions):
        """Test that graph nodes define relationships."""
        for action in all_actions:
            action_nodes = [n for n in action.graph_nodes if n.node_type == "action"]
            for node in action_nodes:
                assert len(node.relationships) > 0, \
                    f"{action.action_id}: Action node '{node.node_id}' has no relationships"

    def test_action_has_audit_descriptor(self, all_actions):
        """Test that every action has audit log formatting."""
        for action in all_actions:
            assert action.audit_descriptor, \
                f"{action.action_id}: No audit descriptor defined"
            assert action.audit_descriptor.summary_template, \
                f"{action.action_id}: No audit summary template"
            assert len(action.audit_descriptor.detail_fields) > 0, \
                f"{action.action_id}: No audit detail fields defined"

    def test_action_has_shacl_constraints(self, all_actions):
        """Test that every action defines SHACL constraints."""
        for action in all_actions:
            assert len(action.shacl_constraints) > 0, \
                f"{action.action_id}: No SHACL constraints defined"

    def test_action_has_odrl_policies(self, all_actions):
        """Test that every action defines ODRL governance policies."""
        for action in all_actions:
            assert len(action.odrl_policies) > 0, \
                f"{action.action_id}: No ODRL policies defined"

            # Should have policies for standard roles
            required_roles = ["operator", "facility_manager", "energy_manager", "contractor"]
            for role in required_roles:
                assert role in action.odrl_policies, \
                    f"{action.action_id}: Missing ODRL policy for role '{role}'"

                policy = action.odrl_policies[role]
                assert "permitted" in policy, \
                    f"{action.action_id}: Role '{role}' missing 'permitted' field"

                # If not permitted, must have reason
                if not policy["permitted"]:
                    assert "reason" in policy, \
                        f"{action.action_id}: Role '{role}' denied but no reason provided"

    def test_action_has_execution_metadata(self, all_actions):
        """Test that every action has execution configuration."""
        for action in all_actions:
            assert action.target_type, \
                f"{action.action_id}: No target_type defined"
            assert action.handler_function, \
                f"{action.action_id}: No handler_function defined"
            assert action.validation_class, \
                f"{action.action_id}: No validation_class defined"
            assert len(action.required_permissions) > 0, \
                f"{action.action_id}: No required_permissions defined"
            assert len(action.side_effects) > 0, \
                f"{action.action_id}: No side_effects defined"

    def test_registry_validate_completeness(self, all_actions):
        """Test using registry's built-in validation."""
        for action in all_actions:
            is_valid, errors = action_registry.validate_completeness(action.action_id)
            assert is_valid, \
                f"{action.action_id}: Completeness validation failed:\n" + "\n".join(errors)


class TestSpecificActionConstraints:
    """
    Test specific constraint patterns that actions should follow.
    """

    def test_adjust_setpoint_constraints(self):
        """Test adjust setpoint has proper constraints."""
        action = action_registry.get("adjust-setpoint")
        assert action is not None

        # Should have temperature range constraint
        constraints = action.shacl_constraints
        assert any("60-80" in c for c in constraints), \
            "Missing temperature range constraint"

        # Should have delta constraint
        assert any("delta" in c.lower() for c in constraints), \
            "Missing delta constraint"

        # Should have operator specific constraint
        assert any("operator" in c.lower() for c in constraints), \
            "Missing operator-specific constraint"

    def test_load_shed_constraints(self):
        """Test load shed has proper constraints."""
        action = action_registry.get("load-shed")
        assert action is not None

        # Should have level constraint
        constraints = action.shacl_constraints
        assert any("level" in c.lower() and ("1-5" in c or "1" in c and "5" in c) for c in constraints), \
            "Missing shed level constraint"

        # Should have duration constraint
        assert any("240" in c or "duration" in c.lower() for c in constraints), \
            "Missing duration constraint"

        # Should have occupancy protection
        assert any("occupancy" in c.lower() or "40%" in c for c in constraints), \
            "Missing occupancy protection constraint"

    def test_pre_cooling_constraints(self):
        """Test pre-cooling has proper constraints."""
        action = action_registry.get("pre-cooling")
        assert action is not None

        # Should have temperature range
        constraints = action.shacl_constraints
        assert any("60-75" in c or ("60" in c and "75" in c) for c in constraints), \
            "Missing temperature range constraint"

        # Should have time window constraint
        assert any(("30" in c and "8" in c) or "time window" in c.lower() for c in constraints), \
            "Missing time window constraint"

        # Should have cooling rate constraint
        assert any("cooling rate" in c.lower() or ("1" in c and "10" in c and "hr" in c.lower()) for c in constraints), \
            "Missing cooling rate constraint"


class TestODRLPolicyConsistency:
    """
    Test that ODRL policies are consistent across actions.
    """

    def test_operator_permissions_are_limited(self):
        """Test that operators have limited permissions."""
        for action in action_registry.list_all():
            operator_policy = action.odrl_policies.get("operator")
            assert operator_policy is not None

            # If permitted, should have constraints
            if operator_policy["permitted"]:
                assert "constraints" in operator_policy, \
                    f"{action.action_id}: Operator permitted but no constraints"

    def test_energy_manager_has_highest_access(self):
        """Test that energy manager has highest access level."""
        for action in action_registry.list_all():
            em_policy = action.odrl_policies.get("energy_manager")
            assert em_policy is not None

            # Energy manager should be permitted for control/optimization actions
            if action.action_type in ["control", "demand_response", "optimization"]:
                assert em_policy["permitted"], \
                    f"{action.action_id}: Energy manager should be permitted"

    def test_contractor_limitations(self):
        """Test that contractors have appropriate limitations."""
        for action in action_registry.list_all():
            contractor_policy = action.odrl_policies.get("contractor")
            assert contractor_policy is not None

            # If permitted, should not have emergency/optimization access
            if contractor_policy["permitted"]:
                constraints = contractor_policy.get("constraints", [])
                # Should have some limitations
                assert len(constraints) > 0 or "temporary_access" in str(constraints), \
                    f"{action.action_id}: Contractor has unrestricted access"


class TestUIFieldConsistency:
    """
    Test that UI fields are consistent and complete.
    """

    def test_user_role_field_has_all_roles(self):
        """Test that user_role field includes all standard roles."""
        required_roles = {"operator", "facility_manager", "energy_manager", "contractor"}

        for action in action_registry.list_all():
            user_role_field = next(
                (f for f in action.ui_fields if f.field_name == "user_role"),
                None
            )
            assert user_role_field is not None, \
                f"{action.action_id}: No user_role field found"

            assert user_role_field.options is not None
            option_values = {opt["value"].split(":")[0] for opt in user_role_field.options}

            assert required_roles.issubset(option_values), \
                f"{action.action_id}: user_role field missing roles: {required_roles - option_values}"

    def test_required_fields_are_marked(self):
        """Test that critical fields are marked as required."""
        for action in action_registry.list_all():
            # user_role should always be required
            user_role_field = next(
                (f for f in action.ui_fields if f.field_name == "user_role"),
                None
            )
            assert user_role_field.required, \
                f"{action.action_id}: user_role field should be required"

    def test_number_fields_have_constraints(self):
        """Test that number fields have min/max constraints."""
        for action in action_registry.list_all():
            number_fields = [f for f in action.ui_fields if f.field_type == "number"]
            for field in number_fields:
                # Should have at least min or max
                assert field.min_value is not None or field.max_value is not None, \
                    f"{action.action_id}: Number field {field.field_name} has no constraints"
