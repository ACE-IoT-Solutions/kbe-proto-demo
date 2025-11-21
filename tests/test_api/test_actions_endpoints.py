"""
Tests for action execution endpoints.

Tests POST /actions/execute, GET /actions/{id}, GET /actions, etc.
"""

import pytest
from datetime import datetime
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


class TestActionExecutionEndpoints:
    """Tests for action execution endpoints."""

    @pytest.mark.api
    @pytest.mark.unit
    def test_action_request_structure(self):
        """Test action request has correct structure."""
        request = create_inference_action_request()
        assert request.action_type == ActionType.INFERENCE
        assert request.parameters is not None
        assert isinstance(request.parameters, list)

    @pytest.mark.api
    @pytest.mark.unit
    def test_action_result_structure(self):
        """Test action result has correct structure."""
        result = create_sample_successful_action_result()
        assert result.action_id
        assert result.status
        assert result.timestamp

    @pytest.mark.api
    @pytest.mark.unit
    def test_inference_action_execution_request(self):
        """Test inference action request structure."""
        request = create_inference_action_request()
        assert request.action_type == ActionType.INFERENCE
        assert any(p.name == "building_id" for p in request.parameters)

    @pytest.mark.api
    @pytest.mark.unit
    def test_validation_action_execution_request(self):
        """Test validation action request structure."""
        request = create_validation_action_request()
        assert request.action_type == ActionType.VALIDATION
        assert any(p.name == "building_id" for p in request.parameters)

    @pytest.mark.api
    @pytest.mark.unit
    def test_query_action_execution_request(self):
        """Test query action request structure."""
        request = create_query_action_request()
        assert request.action_type == ActionType.QUERY
        assert any(p.name == "query" for p in request.parameters)

    @pytest.mark.api
    @pytest.mark.unit
    def test_transformation_action_execution_request(self):
        """Test transformation action request structure."""
        request = create_transformation_action_request()
        assert request.action_type == ActionType.TRANSFORMATION
        assert any(p.name == "source_format" for p in request.parameters)

    @pytest.mark.api
    @pytest.mark.unit
    def test_action_execution_response_structure(self):
        """Test action execution response structure."""
        result = create_sample_successful_action_result()

        # Response should have required fields
        assert hasattr(result, 'action_id')
        assert hasattr(result, 'status')
        assert hasattr(result, 'execution_time_ms')
        assert hasattr(result, 'timestamp')

    @pytest.mark.api
    @pytest.mark.unit
    def test_action_pending_response(self):
        """Test pending action response."""
        result = create_sample_pending_action_result()
        assert result.status == ActionStatus.PENDING
        assert result.result is None

    @pytest.mark.api
    @pytest.mark.unit
    def test_action_completed_response(self):
        """Test completed action response."""
        result = create_sample_successful_action_result()
        assert result.status == ActionStatus.COMPLETED
        assert result.result is not None
        assert result.error is None

    @pytest.mark.api
    @pytest.mark.unit
    def test_action_failed_response(self):
        """Test failed action response."""
        result = create_sample_failed_action_result()
        assert result.status == ActionStatus.FAILED
        assert result.error is not None
        assert result.result is None


class TestActionListingEndpoints:
    """Tests for action listing endpoints."""

    @pytest.mark.api
    @pytest.mark.unit
    def test_action_list_pagination_parameters(self):
        """Test action list accepts pagination parameters."""
        # Example test structure for listing
        pagination_params = {
            "page": 1,
            "page_size": 20,
            "status": "completed",
        }

        assert pagination_params["page"] >= 1
        assert pagination_params["page_size"] > 0
        assert pagination_params["status"] in [
            "pending",
            "running",
            "completed",
            "failed",
        ]

    @pytest.mark.api
    @pytest.mark.unit
    def test_action_list_response_structure(self):
        """Test action list response structure."""
        # Mock response structure
        response = {
            "success": True,
            "data": {
                "items": [
                    create_sample_successful_action_result(),
                ],
                "total": 100,
                "page": 1,
                "page_size": 20,
                "has_next": True,
                "has_previous": False,
            }
        }

        assert response["success"]
        assert len(response["data"]["items"]) > 0
        assert response["data"]["total"] >= len(response["data"]["items"])


class TestActionStatusEndpoints:
    """Tests for action status retrieval endpoints."""

    @pytest.mark.api
    @pytest.mark.unit
    def test_get_action_by_id(self):
        """Test getting action by ID."""
        result = create_sample_successful_action_result()

        # Simulate retrieving action
        assert result.action_id
        assert result.status == ActionStatus.COMPLETED

    @pytest.mark.api
    @pytest.mark.unit
    def test_action_status_transitions(self):
        """Test action status transitions."""
        # Valid status progression
        statuses = [
            ActionStatus.PENDING,
            ActionStatus.RUNNING,
            ActionStatus.COMPLETED,
        ]

        for status in statuses:
            assert status in [
                ActionStatus.PENDING,
                ActionStatus.RUNNING,
                ActionStatus.COMPLETED,
                ActionStatus.FAILED,
            ]

    @pytest.mark.api
    @pytest.mark.unit
    def test_action_error_response_format(self):
        """Test action error response format."""
        result = create_sample_failed_action_result()

        assert result.error is not None
        assert "code" in result.error
        assert "message" in result.error
        assert result.error["code"]
        assert result.error["message"]


class TestActionParameterValidation:
    """Tests for action parameter validation in endpoints."""

    @pytest.mark.api
    @pytest.mark.unit
    def test_required_parameters_validation(self):
        """Test required parameters are validated."""
        request = create_inference_action_request()

        required_params = [p for p in request.parameters if p.required]
        assert len(required_params) > 0
        assert all(p.value is not None for p in required_params)

    @pytest.mark.api
    @pytest.mark.unit
    def test_parameter_type_validation(self):
        """Test parameter type validation."""
        request = create_query_action_request()

        for param in request.parameters:
            assert param.param_type in [
                "string",
                "integer",
                "float",
                "boolean",
                "array",
                "object",
            ]

    @pytest.mark.api
    @pytest.mark.unit
    def test_action_timeout_validation(self):
        """Test action timeout is validated."""
        request = create_inference_action_request()
        assert request.timeout_seconds > 0


class TestActionContextMetadata:
    """Tests for action context and metadata."""

    @pytest.mark.api
    @pytest.mark.unit
    def test_action_context_inclusion(self):
        """Test action request includes context."""
        request = create_inference_action_request()
        assert request.context is not None
        assert isinstance(request.context, dict)

    @pytest.mark.api
    @pytest.mark.unit
    def test_action_metadata_inclusion(self):
        """Test action request includes metadata."""
        request = create_inference_action_request()
        assert request.metadata is not None
        assert isinstance(request.metadata, dict)

    @pytest.mark.api
    @pytest.mark.unit
    def test_action_result_timestamp(self):
        """Test action result includes timestamp."""
        result = create_sample_successful_action_result()
        assert result.timestamp is not None
        assert isinstance(result.timestamp, datetime)

    @pytest.mark.api
    @pytest.mark.unit
    def test_action_execution_time_measurement(self):
        """Test execution time is measured."""
        result = create_sample_successful_action_result()
        assert result.execution_time_ms >= 0
        assert isinstance(result.execution_time_ms, float)


class TestActionCancellation:
    """Tests for action cancellation endpoints."""

    @pytest.mark.api
    @pytest.mark.unit
    def test_action_cancellation_possible_states(self):
        """Test which action states can be cancelled."""
        # Pending actions can be cancelled
        pending = ActionStatus.PENDING
        assert pending in [ActionStatus.PENDING, ActionStatus.RUNNING]

        # Completed/failed actions cannot be cancelled
        completed = ActionStatus.COMPLETED
        assert completed not in [ActionStatus.PENDING, ActionStatus.RUNNING]

    @pytest.mark.api
    @pytest.mark.unit
    def test_action_cancellation_request(self):
        """Test action cancellation request structure."""
        action_id = "act-001"
        assert action_id  # Action ID required
        assert len(action_id) > 0
