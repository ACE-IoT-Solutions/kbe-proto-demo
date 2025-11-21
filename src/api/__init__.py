"""
FastAPI routers for KBE action execution system.
"""

from .actions import router as actions_router
from .building import router as building_router
from .audit import router as audit_router

__all__ = ["actions_router", "building_router", "audit_router"]
