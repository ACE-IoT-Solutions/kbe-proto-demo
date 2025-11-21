"""
Adjust Setpoint Action Descriptor

Self-describing metadata for temperature setpoint adjustment action.
"""

from src.models.action_descriptor import (
    ActionDescriptor,
    UIFieldDescriptor,
    GraphNodeDescriptor,
    AuditLogDescriptor,
    action_registry
)


adjust_setpoint_descriptor = ActionDescriptor(
    action_id="adjust-setpoint",
    action_name="Adjust Temperature Setpoint",
    action_type="control",
    description="Modify zone temperature setpoint with SHACL validation and ODRL governance",
    version="1.0.0",

    # UI Fields - drives form generation
    ui_fields=[
        UIFieldDescriptor(
            field_name="user_role",
            field_type="select",
            label="User / Role",
            required=True,
            default_value="facility_manager:Facility Manager",
            options=[
                {"value": "operator:Operator", "label": "Operator (Basic Controls)"},
                {"value": "facility_manager:Facility Manager", "label": "Facility Manager (All Controls)"},
                {"value": "energy_manager:Energy Manager", "label": "Energy Manager (Optimization)"},
                {"value": "contractor:Contractor", "label": "Contractor (Limited Access)"}
            ],
            help_text="Select your role for proper governance enforcement"
        ),
        UIFieldDescriptor(
            field_name="zone_id",
            field_type="zone-selector",
            label="Zone Selection (Click tile or select)",
            required=True,
            help_text="Select target zone for setpoint adjustment"
        ),
        UIFieldDescriptor(
            field_name="new_setpoint",
            field_type="number",
            label="New Setpoint (°F)",
            required=True,
            min_value=60.0,
            max_value=80.0,
            step=0.5,
            help_text="Range: 60-80°F for comfort and safety"
        ),
        UIFieldDescriptor(
            field_name="priority",
            field_type="select",
            label="Priority Level",
            required=True,
            default_value="medium",
            options=[
                {"value": "low", "label": "Low - Scheduled adjustment"},
                {"value": "medium", "label": "Medium - Normal operation"},
                {"value": "high", "label": "High - Comfort issue"},
                {"value": "emergency", "label": "Emergency - Critical response"}
            ],
            help_text="Emergency priority requires manager authorization"
        ),
        UIFieldDescriptor(
            field_name="reason",
            field_type="text",
            label="Reason",
            required=False,
            placeholder="e.g., Occupant complaint",
            help_text="Optional explanation for audit trail"
        )
    ],

    ui_layout="single-column",

    # Graph Representation
    graph_nodes=[
        GraphNodeDescriptor(
            node_id="action:adjust-setpoint",
            node_type="action",
            label="Adjust Temperature Setpoint",
            description="Modify zone temperature setpoint",
            relationships=[
                {"target": "constraint:setpoint-range", "type": "has_constraint"},
                {"target": "constraint:max-delta", "type": "has_constraint"},
                {"target": "constraint:operator-limit", "type": "has_constraint"},
                {"target": "policy:operator-restrictions", "type": "governed_by"},
                {"target": "policy:contractor-restrictions", "type": "governed_by"},
                {"target": "brick:Temperature_Setpoint", "type": "targets"}
            ]
        ),
        GraphNodeDescriptor(
            node_id="constraint:setpoint-range",
            node_type="constraint",
            label="Setpoint Range: 60-80°F",
            description="SHACL: Absolute temperature limits for comfort and safety"
        ),
        GraphNodeDescriptor(
            node_id="constraint:max-delta",
            node_type="constraint",
            label="Max Delta: 15°F",
            description="SHACL: Maximum temperature change in single adjustment"
        ),
        GraphNodeDescriptor(
            node_id="constraint:operator-limit",
            node_type="constraint",
            label="Operator Limit: 5°F",
            description="SHACL: Reduced limit for operator role"
        ),
        GraphNodeDescriptor(
            node_id="policy:operator-restrictions",
            node_type="policy",
            label="Operator: 5°F Max Change",
            description="ODRL: Operators limited to 5°F adjustments"
        ),
        GraphNodeDescriptor(
            node_id="policy:contractor-restrictions",
            node_type="policy",
            label="Contractor: No Emergency Priority",
            description="ODRL: Contractors cannot use emergency priority"
        )
    ],

    # Audit Log Formatting
    audit_descriptor=AuditLogDescriptor(
        summary_template="{zone_id} setpoint changed to {new_setpoint}°F (Priority: {priority})",
        icon="🌡️",
        detail_fields=[
            {"param": "zone_id", "label": "Target Zone", "format": "text"},
            {"param": "new_setpoint", "label": "New Setpoint", "format": "temperature"},
            {"param": "priority", "label": "Priority Level", "format": "text"},
            {"param": "reason", "label": "Reason", "format": "text"}
        ],
        formatters={
            "new_setpoint": "temperature",  # Adds °F suffix
            "priority": "capitalize"
        }
    ),

    # SHACL Constraints
    shacl_constraints=[
        "Setpoint range: 60-80°F (comfort)",
        "Max delta: 5°F for operators, 15°F for managers",
        "Server room protection: 15-25°C critical range",
        "Occupancy constraints enforced"
    ],

    # ODRL Governance
    odrl_policies={
        "operator": {
            "permitted": True,
            "constraints": [
                "max_delta: 5°F",
                "priority: low/medium only",
                "no_emergency_override: true"
            ]
        },
        "facility_manager": {
            "permitted": True,
            "constraints": [
                "max_delta: 15°F",
                "priority: all levels",
                "emergency_override: true"
            ]
        },
        "energy_manager": {
            "permitted": True,
            "constraints": [
                "max_delta: 15°F",
                "priority: all levels",
                "emergency_override: true",
                "optimization_access: true"
            ]
        },
        "contractor": {
            "permitted": True,
            "constraints": [
                "max_delta: 15°F",
                "priority: low/medium only",
                "no_emergency_override: true",
                "temporary_access: true"
            ]
        }
    },

    # Target & Execution
    target_type="brick:Temperature_Setpoint",
    required_permissions=["zone:write", "setpoint:modify"],
    side_effects=["hvac:mode_change", "power:consumption_change", "audit:log"],
    handler_function="_handle_set_temperature",
    validation_class="AdjustSetpointInput"
)

# Register with global registry
action_registry.register(adjust_setpoint_descriptor)
