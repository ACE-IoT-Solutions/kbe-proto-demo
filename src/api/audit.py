"""
API endpoints for action history and audit trail.
"""

import logging
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Query

from src.models import AuditEntry
from src.services import StateManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audit", tags=["audit"])

# Service instance (will be injected via dependency injection in production)
_state_manager: Optional[StateManager] = None


def get_state_manager() -> StateManager:
    """Get or create state manager instance."""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager


@router.get(
    "/history",
    response_model=List[AuditEntry],
    summary="Get action history",
    description="Get audit trail of executed actions with optional filters"
)
async def get_action_history(
    zone_id: Optional[str] = Query(None, description="Filter by zone ID"),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    start_time: Optional[datetime] = Query(None, description="Filter by start time (ISO 8601)"),
    end_time: Optional[datetime] = Query(None, description="Filter by end time (ISO 8601)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    offset: int = Query(0, ge=0, description="Number of records to skip")
) -> List[AuditEntry]:
    """
    Get action audit trail with optional filters.

    Args:
        zone_id: Optional zone filter
        action_type: Optional action type filter
        start_time: Optional start time filter
        end_time: Optional end time filter
        limit: Maximum number of records
        offset: Number of records to skip

    Returns:
        List of audit entries
    """
    try:
        logger.info(
            f"Retrieving audit history with filters: zone={zone_id}, "
            f"action_type={action_type}, start={start_time}, end={end_time}"
        )

        state_manager = get_state_manager()
        audit_entries = await state_manager.get_audit_trail(
            zone_id=zone_id,
            action_type=action_type,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset
        )

        return audit_entries

    except Exception as e:
        logger.error(f"Error retrieving audit history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving audit history: {str(e)}"
        )


@router.get(
    "/actions/{action_id}",
    response_model=Optional[AuditEntry],
    summary="Get action details",
    description="Get detailed information about a specific action"
)
async def get_action_details(action_id: str) -> Optional[AuditEntry]:
    """
    Get details of a specific action from audit trail.

    Args:
        action_id: Action identifier

    Returns:
        AuditEntry if found, None otherwise

    Raises:
        HTTPException: If action not found
    """
    try:
        state_manager = get_state_manager()

        # Get all audit entries and find the one with matching action_id
        all_entries = await state_manager.get_audit_trail(limit=10000)

        for entry in all_entries:
            if entry.action_id == action_id:
                return entry

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action {action_id} not found in audit trail"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving action details: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving action details: {str(e)}"
        )


@router.get(
    "/zones/{zone_id}/history",
    response_model=List[AuditEntry],
    summary="Get zone action history",
    description="Get all actions executed on a specific zone"
)
async def get_zone_action_history(
    zone_id: str,
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    offset: int = Query(0, ge=0, description="Number of records to skip")
) -> List[AuditEntry]:
    """
    Get action history for a specific zone.

    Args:
        zone_id: Zone identifier
        limit: Maximum number of records
        offset: Number of records to skip

    Returns:
        List of audit entries for the zone
    """
    try:
        state_manager = get_state_manager()
        audit_entries = await state_manager.get_audit_trail(
            zone_id=zone_id,
            limit=limit,
            offset=offset
        )

        return audit_entries

    except Exception as e:
        logger.error(f"Error retrieving zone action history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving zone action history: {str(e)}"
        )


@router.get(
    "/summary",
    summary="Get audit summary",
    description="Get summary statistics of audit trail"
)
async def get_audit_summary(
    zone_id: Optional[str] = Query(None, description="Filter by zone ID"),
    start_time: Optional[datetime] = Query(None, description="Start time for summary"),
    end_time: Optional[datetime] = Query(None, description="End time for summary")
):
    """
    Get summary statistics of audit trail.

    Args:
        zone_id: Optional zone filter
        start_time: Optional start time
        end_time: Optional end time

    Returns:
        Dictionary with summary statistics
    """
    try:
        state_manager = get_state_manager()

        # Get filtered entries
        entries = await state_manager.get_audit_trail(
            zone_id=zone_id,
            start_time=start_time,
            end_time=end_time,
            limit=10000
        )

        # Compute summary statistics
        action_counts = {}
        zone_counts = {}
        user_counts = {}
        status_counts = {}

        for entry in entries:
            # Count by action type
            action_counts[entry.action_type] = action_counts.get(entry.action_type, 0) + 1

            # Count by zone
            zone_counts[entry.target_zone] = zone_counts.get(entry.target_zone, 0) + 1

            # Count by user
            if entry.user:
                user_counts[entry.user] = user_counts.get(entry.user, 0) + 1

            # Count by status
            status_counts[entry.status] = status_counts.get(entry.status, 0) + 1

        return {
            "total_actions": len(entries),
            "action_type_counts": action_counts,
            "zone_counts": zone_counts,
            "user_counts": user_counts,
            "status_counts": status_counts,
            "filters": {
                "zone_id": zone_id,
                "start_time": start_time.isoformat() if start_time else None,
                "end_time": end_time.isoformat() if end_time else None
            }
        }

    except Exception as e:
        logger.error(f"Error computing audit summary: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error computing audit summary: {str(e)}"
        )


@router.get(
    "/recent",
    response_model=List[AuditEntry],
    summary="Get recent actions",
    description="Get most recent actions across all zones"
)
async def get_recent_actions(
    limit: int = Query(50, ge=1, le=500, description="Number of recent actions to retrieve")
) -> List[AuditEntry]:
    """
    Get most recent actions.

    Args:
        limit: Number of recent actions to retrieve

    Returns:
        List of recent audit entries
    """
    try:
        state_manager = get_state_manager()
        recent_entries = await state_manager.get_audit_trail(limit=limit)

        return recent_entries

    except Exception as e:
        logger.error(f"Error retrieving recent actions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving recent actions: {str(e)}"
        )
