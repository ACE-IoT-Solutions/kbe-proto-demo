"""
Tests for KBE action models.

Tests ActionDefinition, ActionExecution, ActionParameter, and related classes.
"""

import pytest
from datetime import datetime
from tests.fixtures.sample_actions import (
    ActionType,
    ActionStatus,
    ActionParameter,
    ActionRequest,
    ActionResult,
    InferenceRule,
    InferenceResult,
    ReasoningType,
    create_inference_action_request,
    create_validation_action_request,
    create_query_action_request,
    create_transformation_action_request,
    create_sample_inference_result,
    create_sample_validation_result,
    create_sample_inference_rules,
    create_sample_successful_action_result,
    create_sample_failed_action_result,
    create_sample_pending_action_result,
)


class TestActionParameter:
    """Tests for ActionParameter model."""

    @pytest.mark.models
    @pytest.mark.unit
    def test_parameter_creation_valid(self):
        """Test creating a valid parameter."""
        param = ActionParameter(
            name="entity",
            value="Building",
            param_type="string",
            required=True,
            description="Entity to process",
        )
        assert param.name == "entity"
        assert param.value == "Building"
        assert param.param_type == "string"
        assert param.required

    @pytest.mark.models
    @pytest.mark.unit
    def test_parameter_invalid_empty_name(self):
        """Test that empty parameter name is rejected."""
        with pytest.raises(AssertionError):
            ActionParameter(
                name="",
                value="test",
                param_type="string",
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_parameter_invalid_type(self):
        """Test that invalid parameter type is rejected."""
        with pytest.raises(AssertionError):
            ActionParameter(
                name="test",
                value="value",
                param_type="invalid_type",
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_parameter_valid_types(self):
        """Test all valid parameter types."""
        valid_types = ["string", "integer", "float", "boolean", "array", "object"]

        for ptype in valid_types:
            param = ActionParameter(
                name="test",
                value=f"value_{ptype}",
                param_type=ptype,
            )
            assert param.param_type == ptype

    @pytest.mark.models
    @pytest.mark.unit
    def test_parameter_various_values(self):
        """Test parameters with different value types."""
        string_param = ActionParameter(
            name="text",
            value="hello",
            param_type="string",
        )
        assert string_param.value == "hello"

        int_param = ActionParameter(
            name="count",
            value=42,
            param_type="integer",
        )
        assert int_param.value == 42

        bool_param = ActionParameter(
            name="flag",
            value=True,
            param_type="boolean",
        )
        assert bool_param.value

        array_param = ActionParameter(
            name="items",
            value=["a", "b", "c"],
            param_type="array",
        )
        assert len(array_param.value) == 3

        obj_param = ActionParameter(
            name="config",
            value={"key": "value"},
            param_type="object",
        )
        assert obj_param.value["key"] == "value"


class TestActionRequest:
    """Tests for ActionRequest model."""

    @pytest.mark.models
    @pytest.mark.unit
    def test_action_request_creation_valid(self):
        """Test creating a valid action request."""
        request = ActionRequest(
            action_type=ActionType.INFERENCE,
            parameters=[
                ActionParameter(
                    name="entity",
                    value="Building",
                    param_type="string",
                )
            ],
            timeout_seconds=30,
        )
        assert request.action_type == ActionType.INFERENCE
        assert len(request.parameters) == 1

    @pytest.mark.models
    @pytest.mark.unit
    def test_action_request_invalid_timeout_zero(self):
        """Test that zero timeout is rejected."""
        with pytest.raises(AssertionError):
            ActionRequest(
                action_type=ActionType.QUERY,
                timeout_seconds=0,
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_action_request_invalid_timeout_negative(self):
        """Test that negative timeout is rejected."""
        with pytest.raises(AssertionError):
            ActionRequest(
                action_type=ActionType.QUERY,
                timeout_seconds=-10,
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_action_request_various_types(self):
        """Test action requests with different action types."""
        for action_type in ActionType:
            request = ActionRequest(action_type=action_type)
            assert request.action_type == action_type

    @pytest.mark.models
    @pytest.mark.unit
    def test_action_request_with_context(self):
        """Test action request with context."""
        context = {"building_id": "BLDG-001", "user": "admin"}
        request = ActionRequest(
            action_type=ActionType.INFERENCE,
            context=context,
        )
        assert request.context["building_id"] == "BLDG-001"

    @pytest.mark.models
    @pytest.mark.unit
    def test_action_request_with_metadata(self):
        """Test action request with metadata."""
        metadata = {"source": "api", "priority": "high"}
        request = ActionRequest(
            action_type=ActionType.VALIDATION,
            metadata=metadata,
        )
        assert request.metadata["priority"] == "high"

    @pytest.mark.models
    @pytest.mark.integration
    def test_inference_action_request(self):
        """Test creating inference action request."""
        request = create_inference_action_request()
        assert request.action_type == ActionType.INFERENCE
        assert len(request.parameters) > 0

    @pytest.mark.models
    @pytest.mark.integration
    def test_validation_action_request(self):
        """Test creating validation action request."""
        request = create_validation_action_request()
        assert request.action_type == ActionType.VALIDATION

    @pytest.mark.models
    @pytest.mark.integration
    def test_query_action_request(self):
        """Test creating query action request."""
        request = create_query_action_request()
        assert request.action_type == ActionType.QUERY

    @pytest.mark.models
    @pytest.mark.integration
    def test_transformation_action_request(self):
        """Test creating transformation action request."""
        request = create_transformation_action_request()
        assert request.action_type == ActionType.TRANSFORMATION


class TestActionResult:
    """Tests for ActionResult model."""

    @pytest.mark.models
    @pytest.mark.unit
    def test_action_result_creation_successful(self):
        """Test creating a successful action result."""
        result = ActionResult(
            action_id="act-001",
            status=ActionStatus.COMPLETED,
            result={"key": "value"},
            execution_time_ms=100.0,
        )
        assert result.action_id == "act-001"
        assert result.status == ActionStatus.COMPLETED
        assert result.result["key"] == "value"

    @pytest.mark.models
    @pytest.mark.unit
    def test_action_result_invalid_empty_id(self):
        """Test that empty action ID is rejected."""
        with pytest.raises(AssertionError):
            ActionResult(
                action_id="",
                status=ActionStatus.COMPLETED,
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_action_result_invalid_negative_execution_time(self):
        """Test that negative execution time is rejected."""
        with pytest.raises(AssertionError):
            ActionResult(
                action_id="act-001",
                status=ActionStatus.COMPLETED,
                execution_time_ms=-100.0,
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_action_result_failed_requires_error(self):
        """Test that failed status requires error details."""
        with pytest.raises(AssertionError):
            ActionResult(
                action_id="act-001",
                status=ActionStatus.FAILED,
                error=None,  # Must have error
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_action_result_failed_with_error(self):
        """Test failed action result with error details."""
        result = ActionResult(
            action_id="act-001",
            status=ActionStatus.FAILED,
            error={"code": "INVALID", "message": "Invalid input"},
        )
        assert result.status == ActionStatus.FAILED
        assert result.error["code"] == "INVALID"

    @pytest.mark.models
    @pytest.mark.unit
    def test_action_result_timestamp_creation(self):
        """Test action result has timestamp."""
        result = ActionResult(
            action_id="act-001",
            status=ActionStatus.COMPLETED,
        )
        assert result.timestamp is not None
        assert isinstance(result.timestamp, datetime)

    @pytest.mark.models
    @pytest.mark.integration
    def test_successful_action_result(self):
        """Test successful action result."""
        result = create_sample_successful_action_result()
        assert result.status == ActionStatus.COMPLETED
        assert result.error is None

    @pytest.mark.models
    @pytest.mark.integration
    def test_failed_action_result(self):
        """Test failed action result."""
        result = create_sample_failed_action_result()
        assert result.status == ActionStatus.FAILED
        assert result.error is not None

    @pytest.mark.models
    @pytest.mark.integration
    def test_pending_action_result(self):
        """Test pending action result."""
        result = create_sample_pending_action_result()
        assert result.status == ActionStatus.PENDING
        assert result.execution_time_ms == 0.0


class TestInferenceRule:
    """Tests for InferenceRule model."""

    @pytest.mark.models
    @pytest.mark.unit
    def test_inference_rule_creation_valid(self):
        """Test creating a valid inference rule."""
        rule = InferenceRule(
            rule_id="rule-001",
            name="Building Age Check",
            description="Check building age",
            premise="Building.year > 2000",
            conclusion="Building.old = false",
            confidence=0.95,
            reasoning_type=ReasoningType.DEDUCTIVE,
        )
        assert rule.rule_id == "rule-001"
        assert rule.confidence == 0.95

    @pytest.mark.models
    @pytest.mark.unit
    def test_inference_rule_invalid_empty_id(self):
        """Test that empty rule ID is rejected."""
        with pytest.raises(AssertionError):
            InferenceRule(
                rule_id="",
                name="Test",
                description="Test",
                premise="premise",
                conclusion="conclusion",
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_inference_rule_invalid_confidence_too_high(self):
        """Test that confidence > 1 is rejected."""
        with pytest.raises(AssertionError):
            InferenceRule(
                rule_id="rule-001",
                name="Test",
                description="Test",
                premise="premise",
                conclusion="conclusion",
                confidence=1.5,
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_inference_rule_invalid_confidence_negative(self):
        """Test that negative confidence is rejected."""
        with pytest.raises(AssertionError):
            InferenceRule(
                rule_id="rule-001",
                name="Test",
                description="Test",
                premise="premise",
                conclusion="conclusion",
                confidence=-0.5,
            )

    @pytest.mark.models
    @pytest.mark.unit
    def test_inference_rule_confidence_edge_cases(self):
        """Test confidence edge cases."""
        rule_zero = InferenceRule(
            rule_id="rule-zero",
            name="Test",
            description="Test",
            premise="premise",
            conclusion="conclusion",
            confidence=0.0,
        )
        assert rule_zero.confidence == 0.0

        rule_one = InferenceRule(
            rule_id="rule-one",
            name="Test",
            description="Test",
            premise="premise",
            conclusion="conclusion",
            confidence=1.0,
        )
        assert rule_one.confidence == 1.0

    @pytest.mark.models
    @pytest.mark.unit
    def test_inference_rule_reasoning_types(self):
        """Test different reasoning types."""
        for reasoning_type in ReasoningType:
            rule = InferenceRule(
                rule_id=f"rule-{reasoning_type}",
                name="Test",
                description="Test",
                premise="premise",
                conclusion="conclusion",
                reasoning_type=reasoning_type,
            )
            assert rule.reasoning_type == reasoning_type

    @pytest.mark.models
    @pytest.mark.integration
    def test_sample_inference_rules(self):
        """Test creating sample inference rules."""
        rules = create_sample_inference_rules()
        assert len(rules) == 5
        assert all(isinstance(r, InferenceRule) for r in rules)
        assert rules[0].rule_id == "rule-001"


class TestInferenceResult:
    """Tests for InferenceResult model."""

    @pytest.mark.models
    @pytest.mark.unit
    def test_inference_result_creation(self):
        """Test creating inference result."""
        result = InferenceResult(
            inferred_facts=[{"fact": "value"}],
            applied_rules=["rule-001"],
            confidence_scores={"fact": 0.95},
            reasoning_path=["step1", "step2"],
        )
        assert len(result.inferred_facts) == 1
        assert len(result.applied_rules) == 1

    @pytest.mark.models
    @pytest.mark.unit
    def test_inference_result_empty(self):
        """Test creating empty inference result."""
        result = InferenceResult()
        assert len(result.inferred_facts) == 0
        assert len(result.applied_rules) == 0
        assert len(result.reasoning_path) == 0

    @pytest.mark.models
    @pytest.mark.integration
    def test_sample_inference_result(self):
        """Test creating sample inference result."""
        result = create_sample_inference_result()
        assert len(result.inferred_facts) > 0
        assert len(result.applied_rules) > 0
        assert result.confidence_scores["BLDG-001/requiresMaintenance"] == 0.95


class TestValidationResult:
    """Tests for ValidationResult from fixtures."""

    @pytest.mark.models
    @pytest.mark.unit
    def test_valid_result_properties(self):
        """Test valid result properties."""
        result = create_sample_validation_result(valid=True)
        assert result.valid
        assert not result.has_issues
        assert not result.has_warnings

    @pytest.mark.models
    @pytest.mark.unit
    def test_invalid_result_properties(self):
        """Test invalid result properties."""
        result = create_sample_validation_result(valid=False)
        assert not result.valid
        assert result.has_issues
        assert result.has_warnings

    @pytest.mark.models
    @pytest.mark.unit
    def test_validation_result_details(self):
        """Test validation result contains details."""
        result = create_sample_validation_result(valid=False)
        assert len(result.issues) == 2
        assert result.issues[0]["type"] == "missing_equipment"
        assert len(result.warnings) == 1
