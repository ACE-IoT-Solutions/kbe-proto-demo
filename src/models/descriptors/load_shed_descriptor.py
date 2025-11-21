"""
Load Shed Action Descriptor

Self-describing metadata for demand response load shedding action.
"""

from src.models.action_descriptor import (
    ActionDescriptor,
    UIFieldDescriptor,
    GraphNodeDescriptor,
    AuditLogDescriptor,
    action_registry
)


load_shed_descriptor = ActionDescriptor(
    action_id="load-shed",
    action_name="Load Shed - Reduce Lighting",
    action_type="demand_response",
    description="Demand management through strategic lighting reduction with occupancy protection",
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
                {"value": "facility_manager:Facility Manager", "label": "Facility Manager (Levels 1-3)"},
                {"value": "energy_manager:Energy Manager", "label": "Energy Manager (All Levels)"},
                {"value": "contractor:Contractor", "label": "Contractor (Limited Access)"}
            ],
            help_text="Energy Manager required for shed levels 4-5"
        ),
        UIFieldDescriptor(
            field_name="shed_level",
            field_type="number",
            label="Shed Level (1-5)",
            required=True,
            default_value=2,
            min_value=1,
            max_value=5,
            step=1,
            help_text="1=20%, 2=40%, 3=50%, 4=60%, 5=80% reduction"
        ),
        UIFieldDescriptor(
            field_name="duration",
            field_type="number",
            label="Duration (minutes)",
            required=True,
            default_value=30,
            min_value=1,
            max_value=240,
            step=1,
            help_text="Max 240 min total, 120 min for levels 4-5"
        ),
        UIFieldDescriptor(
            field_name="reason",
            field_type="text",
            label="Reason",
            required=False,
            placeholder="e.g., Peak demand event",
            help_text="Optional explanation for audit trail"
        )
    ],

    ui_layout="single-column",

    # Graph Representation
    graph_nodes=[
        GraphNodeDescriptor(
            node_id="action:load-shed",
            node_type="action",
            label="Load Shed - Reduce Lighting",
            description="Demand response through lighting control",
            relationships=[
                {"target": "constraint:shed-level-range", "type": "has_constraint"},
                {"target": "constraint:duration-limits", "type": "has_constraint"},
                {"target": "constraint:occupancy-protection", "type": "has_constraint"},
                {"target": "policy:energy-manager-level-45", "type": "governed_by"},
                {"target": "brick:Lighting_System", "type": "targets"}
            ]
        ),
        GraphNodeDescriptor(
            node_id="constraint:shed-level-range",
            node_type="constraint",
            label="Shed Level: 1-5",
            description="SHACL: Five discrete reduction levels"
        ),
        GraphNodeDescriptor(
            node_id="constraint:duration-limits",
            node_type="constraint",
            label="Duration: Max 240 min (120 min for L4-5)",
            description="SHACL: Time limits prevent excessive comfort impact"
        ),
        GraphNodeDescriptor(
            node_id="constraint:occupancy-protection",
            node_type="constraint",
            label="Occupancy: Min 40% illumination",
            description="SHACL: Minimum lighting for occupied spaces"
        ),
        GraphNodeDescriptor(
            node_id="policy:energy-manager-level-45",
            node_type="policy",
            label="Energy Manager: Required for L4-5",
            description="ODRL: High shed levels require energy manager authorization"
        )
    ],

    # Audit Log Formatting
    audit_descriptor=AuditLogDescriptor(
        summary_template="Load shed level {shed_level} for {duration} minutes",
        icon="⚡",
        detail_fields=[
            {"param": "shed_level", "label": "Shed Level", "format": "number"},
            {"param": "duration", "label": "Duration", "format": "minutes"},
            {"param": "zones", "label": "Affected Zones", "format": "list"},
            {"param": "reason", "label": "Reason", "format": "text"}
        ],
        formatters={
            "shed_level": "shed_level",  # Custom: "Level 3 (50% reduction)"
            "duration": "minutes"  # Adds " minutes" suffix
        }
    ),

    # SHACL Constraints
    shacl_constraints=[
        "Shed level: 1-5 discrete levels",
        "Duration: Max 240 minutes, Level 4-5 max 120 minutes",
        "Occupancy-aware: Min 40% illumination when occupied",
        "Server room exemption enforced"
    ],

    # ODRL Governance
    odrl_policies={
        "operator": {
            "permitted": True,
            "constraints": [
                "max_shed_level: 3",
                "max_duration: 120",
                "requires_authorization: facility_manager"
            ]
        },
        "facility_manager": {
            "permitted": True,
            "constraints": [
                "max_shed_level: 3",
                "max_duration: 240",
                "emergency_override: true"
            ]
        },
        "energy_manager": {
            "permitted": True,
            "constraints": [
                "max_shed_level: 5",
                "max_duration: 240",
                "level_45_duration: 120",
                "demand_response_authority: true"
            ]
        },
        "contractor": {
            "permitted": False,
            "reason": "Load shedding requires operational authority"
        }
    },

    # Target & Execution
    target_type="brick:Lighting_System",
    required_permissions=["zone:write", "lighting:control", "demand:manage"],
    side_effects=["power:reduction", "comfort:degradation", "occupancy:notification"],
    handler_function="_handle_load_shed",
    validation_class="LoadShedInput"
)

# Register with global registry
action_registry.register(load_shed_descriptor)
