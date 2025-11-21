"""
Core action execution engine for KBE system.
Handles the execution of building automation actions with proper validation and error handling.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
from uuid import uuid4

from src.models import ActionRequest, ActionResponse

logger = logging.getLogger(__name__)


class ActionExecutionError(Exception):
    """Raised when action execution fails."""
    pass


class ActionExecutor:
    """
    Core engine for executing building automation actions.

    Responsibilities:
    - Execute validated actions
    - Track action state transitions
    - Handle execution errors
    - Coordinate with state manager
    """

    def __init__(self, state_manager=None, validator=None):
        """
        Initialize the action executor.

        Args:
            state_manager: StateManager instance for managing building state
            validator: ActionValidator instance for pre-execution validation
        """
        self.state_manager = state_manager
        self.validator = validator
        self._execution_queue: asyncio.Queue = asyncio.Queue()
        self._active_actions: Dict[str, Dict[str, Any]] = {}
        logger.info("ActionExecutor initialized")

    async def execute_action(
        self,
        request: ActionRequest,
        user: Optional[str] = None
    ) -> ActionResponse:
        """
        Execute a building automation action.

        Args:
            request: The action request to execute
            user: Optional user identifier for audit trail

        Returns:
            ActionResponse with execution results

        Raises:
            ActionExecutionError: If execution fails
        """
        action_id = str(uuid4())
        timestamp = datetime.utcnow()

        logger.info(
            f"Executing action {action_id}: {request.action_type} "
            f"on zone {request.target_zone}"
        )

        try:
            # Pre-execution validation
            if self.validator:
                validation_result = await self.validator.validate_action(
                    request.action_type,
                    request.parameters,
                    request.target_zone
                )
                if not validation_result.is_valid:
                    return ActionResponse(
                        action_id=action_id,
                        status="validation_failed",
                        timestamp=timestamp,
                        errors=validation_result.errors
                    )

            # Track active action
            self._active_actions[action_id] = {
                "request": request,
                "status": "executing",
                "started_at": timestamp,
                "user": user
            }

            # Execute the action based on type
            result = await self._execute_action_logic(request, action_id)

            # Update state if execution successful
            if self.state_manager and result.get("success"):
                await self.state_manager.update_state(
                    request.target_zone,
                    request.action_type,
                    request.parameters,
                    action_id
                )

            # Remove from active actions
            del self._active_actions[action_id]

            return ActionResponse(
                action_id=action_id,
                status="completed" if result.get("success") else "failed",
                timestamp=timestamp,
                result=result,
                errors=result.get("errors")
            )

        except Exception as e:
            logger.error(f"Action execution failed for {action_id}: {str(e)}", exc_info=True)

            # Clean up active action
            if action_id in self._active_actions:
                del self._active_actions[action_id]

            return ActionResponse(
                action_id=action_id,
                status="error",
                timestamp=timestamp,
                errors=[f"Execution error: {str(e)}"]
            )

    async def _execute_action_logic(
        self,
        request: ActionRequest,
        action_id: str
    ) -> Dict[str, Any]:
        """
        Execute the actual action logic based on action type.

        Args:
            request: The action request
            action_id: Unique action identifier

        Returns:
            Dict containing execution results
        """
        # This is a placeholder implementation
        # Actual logic will depend on the specific action types defined in the ontology

        action_handlers = {
            "setTemperature": self._handle_set_temperature,
            "setOccupancyMode": self._handle_set_occupancy_mode,
            "adjustVentilation": self._handle_adjust_ventilation,
            "enableEconomizer": self._handle_enable_economizer,
            "setLightingLevel": self._handle_set_lighting_level,
        }

        handler = action_handlers.get(request.action_type)

        if not handler:
            logger.warning(f"No handler found for action type: {request.action_type}")
            return {
                "success": False,
                "errors": [f"Unsupported action type: {request.action_type}"]
            }

        try:
            result = await handler(request, action_id)
            return {"success": True, **result}
        except Exception as e:
            logger.error(f"Handler error for {request.action_type}: {str(e)}")
            return {
                "success": False,
                "errors": [f"Handler execution failed: {str(e)}"]
            }

    async def _handle_set_temperature(
        self,
        request: ActionRequest,
        action_id: str
    ) -> Dict[str, Any]:
        """Handle temperature setpoint changes."""
        setpoint = request.parameters.get("setpoint")
        mode = request.parameters.get("mode", "auto")

        logger.info(
            f"Setting temperature for zone {request.target_zone} "
            f"to {setpoint}°F in {mode} mode"
        )

        # Simulate async operation
        await asyncio.sleep(0.1)

        return {
            "action": "setTemperature",
            "zone": request.target_zone,
            "setpoint": setpoint,
            "mode": mode,
            "applied_at": datetime.utcnow().isoformat()
        }

    async def _handle_set_occupancy_mode(
        self,
        request: ActionRequest,
        action_id: str
    ) -> Dict[str, Any]:
        """Handle occupancy mode changes."""
        mode = request.parameters.get("mode")

        logger.info(f"Setting occupancy mode for zone {request.target_zone} to {mode}")

        await asyncio.sleep(0.1)

        return {
            "action": "setOccupancyMode",
            "zone": request.target_zone,
            "mode": mode,
            "applied_at": datetime.utcnow().isoformat()
        }

    async def _handle_adjust_ventilation(
        self,
        request: ActionRequest,
        action_id: str
    ) -> Dict[str, Any]:
        """Handle ventilation adjustments."""
        rate = request.parameters.get("rate")

        logger.info(f"Adjusting ventilation for zone {request.target_zone} to {rate} CFM")

        await asyncio.sleep(0.1)

        return {
            "action": "adjustVentilation",
            "zone": request.target_zone,
            "rate": rate,
            "applied_at": datetime.utcnow().isoformat()
        }

    async def _handle_enable_economizer(
        self,
        request: ActionRequest,
        action_id: str
    ) -> Dict[str, Any]:
        """Handle economizer enable/disable."""
        enabled = request.parameters.get("enabled", True)

        logger.info(
            f"{'Enabling' if enabled else 'Disabling'} economizer "
            f"for zone {request.target_zone}"
        )

        await asyncio.sleep(0.1)

        return {
            "action": "enableEconomizer",
            "zone": request.target_zone,
            "enabled": enabled,
            "applied_at": datetime.utcnow().isoformat()
        }

    async def _handle_set_lighting_level(
        self,
        request: ActionRequest,
        action_id: str
    ) -> Dict[str, Any]:
        """Handle lighting level changes."""
        level = request.parameters.get("level")

        logger.info(f"Setting lighting level for zone {request.target_zone} to {level}%")

        await asyncio.sleep(0.1)

        return {
            "action": "setLightingLevel",
            "zone": request.target_zone,
            "level": level,
            "applied_at": datetime.utcnow().isoformat()
        }

    async def get_active_actions(self) -> Dict[str, Dict[str, Any]]:
        """Get all currently executing actions."""
        return self._active_actions.copy()

    async def cancel_action(self, action_id: str) -> bool:
        """
        Cancel an active action.

        Args:
            action_id: ID of the action to cancel

        Returns:
            True if action was cancelled, False if not found
        """
        if action_id in self._active_actions:
            logger.info(f"Cancelling action {action_id}")
            del self._active_actions[action_id]
            return True
        return False
