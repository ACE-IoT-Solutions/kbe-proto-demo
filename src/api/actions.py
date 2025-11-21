"""
API endpoints for action execution and validation.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Header
from fastapi.responses import JSONResponse

from src.models import (
    ActionRequest,
    ActionResponse,
    ValidationRequest,
    ValidationResponse
)
from src.services import ActionExecutor, ActionValidator, StateManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/actions", tags=["actions"])

# Service instances (will be injected via dependency injection in production)
_validator: Optional[ActionValidator] = None
_executor: Optional[ActionExecutor] = None
_state_manager: Optional[StateManager] = None


def get_validator() -> ActionValidator:
    """Get or create validator instance."""
    global _validator
    if _validator is None:
        _validator = ActionValidator()
    return _validator


def get_state_manager() -> StateManager:
    """Get or create state manager instance."""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager


def get_executor() -> ActionExecutor:
    """Get or create executor instance."""
    global _executor
    if _executor is None:
        _executor = ActionExecutor(
            state_manager=get_state_manager(),
            validator=get_validator()
        )
    return _executor


@router.post(
    "/execute",
    response_model=ActionResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute an action",
    description="Execute a building automation action after validation"
)
async def execute_action(
    request: ActionRequest,
    x_user_id: Optional[str] = Header(None, description="User identifier for audit trail")
) -> ActionResponse:
    """
    Execute a building automation action.

    Args:
        request: Action execution request
        x_user_id: Optional user identifier from header

    Returns:
        ActionResponse with execution results

    Raises:
        HTTPException: If execution fails
    """
    try:
        logger.info(
            f"Received action execution request: {request.action_type} "
            f"for zone {request.target_zone}"
        )

        executor = get_executor()
        response = await executor.execute_action(request, user=x_user_id)

        if response.status == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "Action execution failed",
                    "errors": response.errors
                }
            )

        if response.status == "validation_failed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Action validation failed",
                    "errors": response.errors
                }
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error executing action: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post(
    "/validate",
    response_model=ValidationResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate an action",
    description="Validate action parameters without executing"
)
async def validate_action(request: ValidationRequest) -> ValidationResponse:
    """
    Validate an action without executing it.

    Args:
        request: Validation request

    Returns:
        ValidationResponse with validation results
    """
    try:
        logger.info(
            f"Received validation request: {request.action_type} "
            f"for zone {request.target_zone}"
        )

        validator = get_validator()
        response = await validator.validate_request(request)

        return response

    except Exception as e:
        logger.error(f"Error during validation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation error: {str(e)}"
        )


@router.get(
    "/active",
    summary="Get active actions",
    description="Get all currently executing actions"
)
async def get_active_actions():
    """
    Get all currently executing actions.

    Returns:
        Dictionary of active actions
    """
    try:
        executor = get_executor()
        active_actions = await executor.get_active_actions()

        return {
            "count": len(active_actions),
            "actions": active_actions
        }

    except Exception as e:
        logger.error(f"Error retrieving active actions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving active actions: {str(e)}"
        )


@router.delete(
    "/{action_id}",
    summary="Cancel an action",
    description="Cancel a currently executing action"
)
async def cancel_action(action_id: str):
    """
    Cancel a currently executing action.

    Args:
        action_id: ID of the action to cancel

    Returns:
        Cancellation status
    """
    try:
        executor = get_executor()
        cancelled = await executor.cancel_action(action_id)

        if not cancelled:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Action {action_id} not found or already completed"
            )

        return {
            "action_id": action_id,
            "status": "cancelled"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling action: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelling action: {str(e)}"
        )


@router.get(
    "/types",
    summary="Get supported action types",
    description="Get list of all supported action types and their parameters"
)
async def get_action_types():
    """
    Get list of supported action types.

    Returns:
        Dictionary of action types and their specifications
    """
    try:
        validator = get_validator()

        # Get validation rules which define supported actions
        action_types = {}
        for action_type, rules in validator._validation_rules.items():
            action_types[action_type] = {
                "required_parameters": rules["required_params"],
                "optional_parameters": rules.get("optional_params", []),
                "parameter_specs": rules["validations"]
            }

        return {
            "supported_actions": action_types
        }

    except Exception as e:
        logger.error(f"Error retrieving action types: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving action types: {str(e)}"
        )
