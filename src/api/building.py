"""
API endpoints for building and zone state management.
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Query
from datetime import datetime

from src.models import BuildingState
from src.services import StateManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/building", tags=["building"])

# Service instance (will be injected via dependency injection in production)
_state_manager: Optional[StateManager] = None


def get_state_manager() -> StateManager:
    """Get or create state manager instance."""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager


@router.get(
    "/state",
    response_model=List[BuildingState],
    summary="Get building state",
    description="Get current state of all zones or entire building"
)
async def get_building_state() -> List[BuildingState]:
    """
    Get current state of all zones in the building.

    Returns:
        List of BuildingState objects for all zones
    """
    try:
        state_manager = get_state_manager()
        zones_state = await state_manager.get_all_zones_state()

        return zones_state

    except Exception as e:
        logger.error(f"Error retrieving building state: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving building state: {str(e)}"
        )


@router.get(
    "/zones/{zone_id}/state",
    response_model=BuildingState,
    summary="Get zone state",
    description="Get current state of a specific zone"
)
async def get_zone_state(zone_id: str) -> BuildingState:
    """
    Get current state of a specific zone.

    Args:
        zone_id: Zone identifier

    Returns:
        BuildingState for the specified zone

    Raises:
        HTTPException: If zone not found
    """
    try:
        state_manager = get_state_manager()
        zone_state = await state_manager.get_zone_state(zone_id)

        if zone_state is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Zone {zone_id} not found"
            )

        return zone_state

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving zone state: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving zone state: {str(e)}"
        )


@router.post(
    "/zones/{zone_id}/initialize",
    status_code=status.HTTP_201_CREATED,
    summary="Initialize zone",
    description="Initialize a zone with default or custom state"
)
async def initialize_zone(
    zone_id: str,
    initial_state: Optional[dict] = None
):
    """
    Initialize a zone with default or provided state.

    Args:
        zone_id: Zone identifier
        initial_state: Optional initial state dictionary

    Returns:
        Success message
    """
    try:
        state_manager = get_state_manager()
        await state_manager.initialize_zone(zone_id, initial_state)

        return {
            "message": f"Zone {zone_id} initialized successfully",
            "zone_id": zone_id
        }

    except Exception as e:
        logger.error(f"Error initializing zone: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initializing zone: {str(e)}"
        )


@router.get(
    "/zones/{zone_id}/history",
    summary="Get zone state history",
    description="Get historical state changes for a zone"
)
async def get_zone_history(
    zone_id: str,
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    offset: int = Query(0, ge=0, description="Number of records to skip")
):
    """
    Get state change history for a zone.

    Args:
        zone_id: Zone identifier
        limit: Maximum number of records to return
        offset: Number of records to skip

    Returns:
        List of state change records
    """
    try:
        state_manager = get_state_manager()
        history = await state_manager.get_state_history(
            zone_id=zone_id,
            limit=limit,
            offset=offset
        )

        return {
            "zone_id": zone_id,
            "total": len(history),
            "limit": limit,
            "offset": offset,
            "history": history
        }

    except Exception as e:
        logger.error(f"Error retrieving zone history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving zone history: {str(e)}"
        )


@router.get(
    "/statistics",
    summary="Get system statistics",
    description="Get statistics about the building management system"
)
async def get_statistics():
    """
    Get system statistics.

    Returns:
        Dictionary with system statistics
    """
    try:
        state_manager = get_state_manager()
        stats = await state_manager.get_statistics()

        return stats

    except Exception as e:
        logger.error(f"Error retrieving statistics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving statistics: {str(e)}"
        )


@router.delete(
    "/zones/{zone_id}/state",
    summary="Clear zone state",
    description="Clear state data for a zone (testing only)"
)
async def clear_zone_state(zone_id: str):
    """
    Clear state data for a zone (useful for testing).

    Args:
        zone_id: Zone identifier

    Returns:
        Success message
    """
    try:
        state_manager = get_state_manager()
        await state_manager.clear_state(zone_id)

        return {
            "message": f"State cleared for zone {zone_id}",
            "zone_id": zone_id
        }

    except Exception as e:
        logger.error(f"Error clearing zone state: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing zone state: {str(e)}"
        )


@router.get(
    "/zones",
    summary="List all zones",
    description="Get list of all zones in the system"
)
async def list_zones():
    """
    Get list of all zones.

    Returns:
        List of zone identifiers
    """
    try:
        state_manager = get_state_manager()
        stats = await state_manager.get_statistics()

        return {
            "total_zones": stats["total_zones"],
            "zones": stats["zones"]
        }

    except Exception as e:
        logger.error(f"Error listing zones: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing zones: {str(e)}"
        )
