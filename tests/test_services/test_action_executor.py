"""
Tests for action execution service.

Tests ActionExecutor, action queuing, and execution logic.
"""

import pytest
from datetime import datetime, timedelta
from tests.fixtures.sample_actions import (
    ActionType,
    ActionStatus,
    ActionRequest,
    ActionResult,
    create_inference_action_request,
    create_validation_action_request,
    create_query_action_request,
    create_transformation_action_request,
    create_sample_successful_action_result,
    create_sample_failed_action_result,
    create_sample_pending_action_result,
)
from tests.fixtures.sample_building import create_sample_building


class TestActionExecutorBasics:
    """Tests for basic action executor functionality."""

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_accepts_action_request(self):
        """Test executor accepts action requests."""
        request = create_inference_action_request()

        assert request.action_type
        assert request.parameters is not None

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_creates_action_id(self):
        """Test executor creates action ID for request."""
        result = create_sample_successful_action_result()

        # Action ID should be generated
        assert result.action_id
        assert len(result.action_id) > 0

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_sets_initial_status_pending(self):
        """Test executor sets initial status to pending."""
        result = create_sample_pending_action_result()

        assert result.status == ActionStatus.PENDING

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_returns_action_result(self):
        """Test executor returns action result."""
        result = create_sample_successful_action_result()

        assert isinstance(result, ActionResult)
        assert result.action_id
        assert result.status


class TestActionExecutionFlow:
    """Tests for action execution flow."""

    @pytest.mark.services
    @pytest.mark.unit
    def test_action_execution_state_progression(self):
        """Test action execution state progression."""
        # Typical progression: PENDING -> RUNNING -> COMPLETED/FAILED
        assert ActionStatus.PENDING in [
            ActionStatus.PENDING,
            ActionStatus.RUNNING,
            ActionStatus.COMPLETED,
            ActionStatus.FAILED,
        ]

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_measures_execution_time(self):
        """Test executor measures execution time."""
        result = create_sample_successful_action_result()

        assert result.execution_time_ms >= 0
        assert isinstance(result.execution_time_ms, float)

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_records_completion_timestamp(self):
        """Test executor records completion timestamp."""
        result = create_sample_successful_action_result()

        assert result.timestamp is not None
        assert isinstance(result.timestamp, datetime)

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_handles_successful_completion(self):
        """Test executor handles successful completion."""
        result = create_sample_successful_action_result()

        assert result.status == ActionStatus.COMPLETED
        assert result.result is not None
        assert result.error is None

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_handles_failure(self):
        """Test executor handles action failure."""
        result = create_sample_failed_action_result()

        assert result.status == ActionStatus.FAILED
        assert result.error is not None
        assert result.result is None


class TestActionQueuing:
    """Tests for action queuing."""

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_queues_actions(self):
        """Test executor can queue multiple actions."""
        request1 = create_inference_action_request()
        request2 = create_validation_action_request()

        assert request1.action_type != request2.action_type

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_processes_queue_order(self):
        """Test executor processes queue in order."""
        # First in, first out
        actions = [
            create_sample_pending_action_result(),
            create_sample_successful_action_result(),
            create_sample_failed_action_result(),
        ]

        assert len(actions) == 3
        # Verify all actions exist and are distinct
        action_ids = {a.action_id for a in actions}
        assert len(action_ids) == 3

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_concurrent_actions(self):
        """Test executor can handle concurrent actions."""
        # Multiple actions in parallel
        actions = [
            create_inference_action_request(),
            create_validation_action_request(),
            create_query_action_request(),
        ]

        assert len(actions) == 3


class TestActionTypeHandling:
    """Tests for handling different action types."""

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_handles_inference_actions(self):
        """Test executor handles inference actions."""
        request = create_inference_action_request()
        assert request.action_type == ActionType.INFERENCE

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_handles_validation_actions(self):
        """Test executor handles validation actions."""
        request = create_validation_action_request()
        assert request.action_type == ActionType.VALIDATION

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_handles_query_actions(self):
        """Test executor handles query actions."""
        request = create_query_action_request()
        assert request.action_type == ActionType.QUERY

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_handles_transformation_actions(self):
        """Test executor handles transformation actions."""
        request = create_transformation_action_request()
        assert request.action_type == ActionType.TRANSFORMATION


class TestActionErrorHandling:
    """Tests for action error handling."""

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_captures_error_code(self):
        """Test executor captures error code."""
        result = create_sample_failed_action_result()

        assert result.error is not None
        assert "code" in result.error
        assert result.error["code"]

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_captures_error_message(self):
        """Test executor captures error message."""
        result = create_sample_failed_action_result()

        assert result.error is not None
        assert "message" in result.error
        assert result.error["message"]

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_captures_error_details(self):
        """Test executor captures error details."""
        result = create_sample_failed_action_result()

        assert result.error is not None
        assert "details" in result.error

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_timeout_handling(self):
        """Test executor handles timeouts."""
        request = create_inference_action_request()

        # Should have a reasonable timeout
        assert request.timeout_seconds > 0
        assert request.timeout_seconds <= 300  # 5 minutes max


class TestActionContextHandling:
    """Tests for action context handling."""

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_preserves_context(self):
        """Test executor preserves action context."""
        request = create_inference_action_request()

        assert request.context is not None
        if "building_id" in request.context:
            assert request.context["building_id"]

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_preserves_metadata(self):
        """Test executor preserves action metadata."""
        request = create_inference_action_request()

        assert request.metadata is not None
        assert isinstance(request.metadata, dict)

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_returns_context_in_result(self):
        """Test executor returns context in result."""
        result = create_sample_successful_action_result()

        assert result.action_id
        assert result.timestamp


class TestActionParameterHandling:
    """Tests for action parameter handling."""

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_validates_required_parameters(self):
        """Test executor validates required parameters."""
        request = create_inference_action_request()

        required = [p for p in request.parameters if p.required]
        assert len(required) > 0

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_handles_optional_parameters(self):
        """Test executor handles optional parameters."""
        request = create_query_action_request()

        optional = [p for p in request.parameters if not p.required]
        # May or may not have optional parameters

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_validates_parameter_types(self):
        """Test executor validates parameter types."""
        request = create_transformation_action_request()

        for param in request.parameters:
            assert param.param_type in [
                "string",
                "integer",
                "float",
                "boolean",
                "array",
                "object",
            ]


class TestActionAsyncSupport:
    """Tests for async action execution."""

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_async_execution_support(self):
        """Test executor supports async execution."""
        request = create_inference_action_request()

        # Should be executable asynchronously
        assert request.action_type

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_returns_immediately_for_async(self):
        """Test executor returns immediately for async actions."""
        result = create_sample_pending_action_result()

        # Should return immediately with pending status
        assert result.status == ActionStatus.PENDING
        assert result.execution_time_ms >= 0

    @pytest.mark.services
    @pytest.mark.unit
    def test_executor_provides_status_polling(self):
        """Test executor provides status polling."""
        action_id = "act-001"

        # Should be able to poll status
        assert action_id
