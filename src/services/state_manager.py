"""
State management for building zones and equipment.
Maintains current state and tracks state transitions.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import defaultdict
import asyncio

from src.models import BuildingState, AuditEntry

logger = logging.getLogger(__name__)


class StateManager:
    """
    Manages building and zone state.

    Responsibilities:
    - Track current state of zones
    - Record state transitions
    - Provide state history
    - Support audit trail
    """

    def __init__(self):
        """Initialize the state manager."""
        self._zone_states: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._state_history: List[Dict[str, Any]] = []
        self._audit_trail: List[AuditEntry] = []
        self._lock = asyncio.Lock()
        logger.info("StateManager initialized")

    async def get_zone_state(self, zone_id: str) -> Optional[BuildingState]:
        """
        Get current state of a zone.

        Args:
            zone_id: Zone identifier

        Returns:
            BuildingState if zone exists, None otherwise
        """
        async with self._lock:
            if zone_id not in self._zone_states:
                logger.warning(f"Zone {zone_id} not found in state manager")
                return None

            return BuildingState(
                zone_id=zone_id,
                state=self._zone_states[zone_id].copy(),
                timestamp=datetime.utcnow()
            )

    async def get_all_zones_state(self) -> List[BuildingState]:
        """
        Get current state of all zones.

        Returns:
            List of BuildingState objects
        """
        async with self._lock:
            return [
                BuildingState(
                    zone_id=zone_id,
                    state=state.copy(),
                    timestamp=datetime.utcnow()
                )
                for zone_id, state in self._zone_states.items()
            ]

    async def update_state(
        self,
        zone_id: str,
        action_type: str,
        parameters: Dict[str, Any],
        action_id: str,
        user: Optional[str] = None
    ) -> None:
        """
        Update zone state based on executed action.

        Args:
            zone_id: Zone identifier
            action_type: Type of action executed
            parameters: Action parameters
            action_id: Unique action identifier
            user: Optional user who executed the action
        """
        async with self._lock:
            timestamp = datetime.utcnow()

            # Get current state or initialize
            current_state = self._zone_states[zone_id]
            previous_state = current_state.copy()

            # Update state based on action type
            state_updates = self._compute_state_updates(
                action_type,
                parameters,
                current_state
            )

            # Apply updates
            current_state.update(state_updates)
            current_state["last_updated"] = timestamp.isoformat()
            current_state["last_action_id"] = action_id

            # Record state transition
            self._state_history.append({
                "zone_id": zone_id,
                "timestamp": timestamp,
                "action_id": action_id,
                "action_type": action_type,
                "previous_state": previous_state,
                "new_state": current_state.copy(),
                "parameters": parameters
            })

            # Add to audit trail
            self._audit_trail.append(AuditEntry(
                action_id=action_id,
                timestamp=timestamp,
                action_type=action_type,
                target_zone=zone_id,
                user=user,
                status="completed",
                details={
                    "parameters": parameters,
                    "state_changes": state_updates
                }
            ))

            logger.info(
                f"Updated state for zone {zone_id} from action {action_id} "
                f"({action_type})"
            )

    def _compute_state_updates(
        self,
        action_type: str,
        parameters: Dict[str, Any],
        current_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute state updates based on action.

        Args:
            action_type: Type of action
            parameters: Action parameters
            current_state: Current zone state

        Returns:
            Dictionary of state updates
        """
        updates = {}

        if action_type == "setTemperature":
            updates["temperature_setpoint"] = parameters.get("setpoint")
            updates["hvac_mode"] = parameters.get("mode", "auto")

        elif action_type == "setOccupancyMode":
            updates["occupancy_mode"] = parameters.get("mode")

        elif action_type == "adjustVentilation":
            updates["ventilation_rate"] = parameters.get("rate")
            if "mode" in parameters:
                updates["ventilation_mode"] = parameters["mode"]

        elif action_type == "enableEconomizer":
            updates["economizer_enabled"] = parameters.get("enabled", True)
            if "min_outdoor_temp" in parameters:
                updates["economizer_min_temp"] = parameters["min_outdoor_temp"]
            if "max_outdoor_temp" in parameters:
                updates["economizer_max_temp"] = parameters["max_outdoor_temp"]

        elif action_type == "setLightingLevel":
            updates["lighting_level"] = parameters.get("level")
            if "duration" in parameters:
                updates["lighting_duration"] = parameters["duration"]

        return updates

    async def get_state_history(
        self,
        zone_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get state change history.

        Args:
            zone_id: Optional zone filter
            limit: Maximum number of records
            offset: Number of records to skip

        Returns:
            List of state change records
        """
        async with self._lock:
            history = self._state_history

            if zone_id:
                history = [h for h in history if h["zone_id"] == zone_id]

            # Sort by timestamp descending
            history = sorted(
                history,
                key=lambda x: x["timestamp"],
                reverse=True
            )

            return history[offset:offset + limit]

    async def get_audit_trail(
        self,
        zone_id: Optional[str] = None,
        action_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditEntry]:
        """
        Get action audit trail with optional filters.

        Args:
            zone_id: Filter by zone
            action_type: Filter by action type
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum records
            offset: Skip records

        Returns:
            List of audit entries
        """
        async with self._lock:
            entries = self._audit_trail

            # Apply filters
            if zone_id:
                entries = [e for e in entries if e.target_zone == zone_id]

            if action_type:
                entries = [e for e in entries if e.action_type == action_type]

            if start_time:
                entries = [e for e in entries if e.timestamp >= start_time]

            if end_time:
                entries = [e for e in entries if e.timestamp <= end_time]

            # Sort by timestamp descending
            entries = sorted(
                entries,
                key=lambda x: x.timestamp,
                reverse=True
            )

            return entries[offset:offset + limit]

    async def initialize_zone(
        self,
        zone_id: str,
        initial_state: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize a zone with default or provided state.

        Args:
            zone_id: Zone identifier
            initial_state: Optional initial state dictionary
        """
        async with self._lock:
            if zone_id in self._zone_states:
                logger.warning(f"Zone {zone_id} already initialized, skipping")
                return

            default_state = {
                "temperature_setpoint": 72.0,
                "hvac_mode": "auto",
                "occupancy_mode": "unoccupied",
                "ventilation_rate": 0,
                "lighting_level": 0,
                "economizer_enabled": False,
                "last_updated": datetime.utcnow().isoformat()
            }

            if initial_state:
                default_state.update(initial_state)

            self._zone_states[zone_id] = default_state
            logger.info(f"Initialized zone {zone_id} with state: {default_state}")

    async def clear_state(self, zone_id: Optional[str] = None) -> None:
        """
        Clear state data (useful for testing).

        Args:
            zone_id: Optional zone to clear, or all if None
        """
        async with self._lock:
            if zone_id:
                if zone_id in self._zone_states:
                    del self._zone_states[zone_id]
                    logger.info(f"Cleared state for zone {zone_id}")
            else:
                self._zone_states.clear()
                self._state_history.clear()
                self._audit_trail.clear()
                logger.info("Cleared all state data")

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get state manager statistics.

        Returns:
            Dictionary with statistics
        """
        async with self._lock:
            return {
                "total_zones": len(self._zone_states),
                "total_state_changes": len(self._state_history),
                "total_audit_entries": len(self._audit_trail),
                "zones": list(self._zone_states.keys())
            }
