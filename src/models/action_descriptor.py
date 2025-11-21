"""
Action Descriptor System

Self-describing action metadata that drives UI generation, graph representation,
audit logging, and validation. Each action is a fully modular, self-contained entity.
"""

from typing import Literal, Optional, Any
from pydantic import BaseModel, Field


class UIFieldDescriptor(BaseModel):
    """
    Describes a single UI input field with all rendering metadata.
    """
    field_name: str = Field(..., description="Parameter name in the model")
    field_type: Literal["text", "number", "select", "checkbox", "time", "multi-select", "zone-selector"] = Field(
        ..., description="HTML input type or custom component"
    )
    label: str = Field(..., description="Human-readable label")
    required: bool = Field(default=True, description="Whether field is required")
    default_value: Any | None = Field(default=None, description="Default value")
    placeholder: str | None = Field(default=None, description="Placeholder text")
    help_text: str | None = Field(default=None, description="Help text shown below field")

    # Validation constraints (for number/text inputs)
    min_value: float | None = Field(default=None, description="Minimum value (number)")
    max_value: float | None = Field(default=None, description="Maximum value (number)")
    step: float | None = Field(default=None, description="Step increment (number)")
    pattern: str | None = Field(default=None, description="Regex pattern (text)")
    min_length: int | None = Field(default=None, description="Minimum length (text)")
    max_length: int | None = Field(default=None, description="Maximum length (text)")

    # Select/multi-select options
    options: list[dict[str, str]] | None = Field(
        default=None,
        description="Options for select/multi-select [{'value': 'id', 'label': 'Display'}]"
    )

    # Conditional display
    depends_on: str | None = Field(default=None, description="Show only if this field has value")
    depends_value: Any | None = Field(default=None, description="Required value to show field")

    # UI styling
    grid_column: str | None = Field(default=None, description="CSS grid-column property")
    css_class: str | None = Field(default=None, description="Additional CSS classes")


class GraphNodeDescriptor(BaseModel):
    """
    Describes how action appears in the knowledge graph.
    """
    node_id: str = Field(..., description="Unique node identifier")
    node_type: Literal["action", "constraint", "policy", "property", "effect"] = Field(
        ..., description="Node type for styling"
    )
    label: str = Field(..., description="Display label")
    description: str | None = Field(default=None, description="Tooltip description")
    color: str | None = Field(default=None, description="Node color override")

    # Relationships
    relationships: list[dict[str, str]] = Field(
        default_factory=list,
        description="Edges to other nodes [{'target': 'node_id', 'type': 'has_constraint'}]"
    )


class AuditLogDescriptor(BaseModel):
    """
    Describes how to format action in audit log.
    """
    summary_template: str = Field(
        ...,
        description="Summary line template with {param} placeholders"
    )
    detail_fields: list[dict[str, str]] = Field(
        default_factory=list,
        description="Fields to show in details [{'param': 'field_name', 'label': 'Display', 'format': 'temperature'}]"
    )
    icon: str | None = Field(default=None, description="Emoji icon for action")

    # Field formatters
    formatters: dict[str, str] = Field(
        default_factory=dict,
        description="Custom formatters {'field': 'formatter_name'}"
    )


class ActionDescriptor(BaseModel):
    """
    Complete self-describing action metadata.

    This single descriptor provides everything needed to:
    - Generate UI forms dynamically
    - Render in knowledge graph
    - Format audit logs
    - Validate inputs
    - Execute with proper governance
    """

    # Basic metadata
    action_id: str = Field(..., description="Unique action identifier")
    action_name: str = Field(..., description="Human-readable name")
    action_type: str = Field(..., description="Action type category")
    description: str = Field(..., description="Detailed description")
    version: str = Field(default="1.0.0", description="Action schema version")

    # UI Generation
    ui_fields: list[UIFieldDescriptor] = Field(
        ...,
        description="UI form fields in display order"
    )
    ui_layout: Literal["single-column", "two-column", "grid"] = Field(
        default="single-column",
        description="Form layout style"
    )

    # Graph Representation
    graph_nodes: list[GraphNodeDescriptor] = Field(
        ...,
        description="Nodes and relationships for knowledge graph"
    )

    # Audit Logging
    audit_descriptor: AuditLogDescriptor = Field(
        ...,
        description="Audit log formatting"
    )

    # SHACL Constraints (semantic validation)
    shacl_constraints: list[str] = Field(
        default_factory=list,
        description="Human-readable constraint descriptions"
    )

    # ODRL Governance
    odrl_policies: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Role-based permissions and constraints"
    )

    # Target ontology
    target_type: str = Field(..., description="Brick schema target type")
    required_permissions: list[str] = Field(
        default_factory=list,
        description="Required permission strings"
    )
    side_effects: list[str] = Field(
        default_factory=list,
        description="Expected side effects"
    )

    # Execution
    handler_function: str = Field(..., description="Backend handler function name")
    validation_class: str = Field(..., description="Pydantic validation class name")

    # Cost estimation (optional)
    cost_calculator: str | None = Field(
        default=None,
        description="Function name for cost calculation"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "action_id": "adjust-setpoint",
                "action_name": "Adjust Temperature Setpoint",
                "action_type": "control",
                "description": "Modify zone temperature setpoint with validation",
                "ui_fields": [
                    {
                        "field_name": "zone_id",
                        "field_type": "zone-selector",
                        "label": "Target Zone",
                        "required": True
                    },
                    {
                        "field_name": "new_setpoint",
                        "field_type": "number",
                        "label": "New Setpoint (°F)",
                        "required": True,
                        "min_value": 60,
                        "max_value": 80,
                        "step": 0.5
                    }
                ]
            }
        }


class ActionRegistry:
    """
    Central registry of all available actions.
    Provides discovery, validation, and UI generation.
    """

    def __init__(self):
        self._actions: dict[str, ActionDescriptor] = {}

    def register(self, descriptor: ActionDescriptor) -> None:
        """Register a new action descriptor."""
        self._actions[descriptor.action_id] = descriptor

    def get(self, action_id: str) -> ActionDescriptor | None:
        """Get action descriptor by ID."""
        return self._actions.get(action_id)

    def list_all(self) -> list[ActionDescriptor]:
        """List all registered actions."""
        return list(self._actions.values())

    def to_json_schema(self) -> dict[str, Any]:
        """Export all actions as JSON schema for frontend."""
        return {
            action_id: descriptor.model_dump()
            for action_id, descriptor in self._actions.items()
        }

    def validate_completeness(self, action_id: str) -> tuple[bool, list[str]]:
        """
        Validate that action has all required elements.

        Returns:
            (is_valid, list_of_errors)
        """
        descriptor = self.get(action_id)
        if not descriptor:
            return False, [f"Action '{action_id}' not found in registry"]

        errors = []

        # Check UI fields
        if not descriptor.ui_fields:
            errors.append("No UI fields defined")

        # Check graph representation
        if not descriptor.graph_nodes:
            errors.append("No graph nodes defined")

        # Check audit descriptor
        if not descriptor.audit_descriptor.summary_template:
            errors.append("No audit summary template defined")

        # Check SHACL constraints
        if not descriptor.shacl_constraints:
            errors.append("No SHACL constraints defined")

        # Check ODRL policies
        if not descriptor.odrl_policies:
            errors.append("No ODRL policies defined")

        # Check handler exists
        if not descriptor.handler_function:
            errors.append("No handler function specified")

        # Check validation class
        if not descriptor.validation_class:
            errors.append("No validation class specified")

        return len(errors) == 0, errors


# Global registry instance
action_registry = ActionRegistry()
