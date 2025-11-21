"""
Pre-Cooling Action Descriptor

Self-describing metadata for peak demand optimization through pre-cooling.
"""

from src.models.action_descriptor import (
    ActionDescriptor,
    UIFieldDescriptor,
    GraphNodeDescriptor,
    AuditLogDescriptor,
    action_registry
)


pre_cooling_descriptor = ActionDescriptor(
    action_id="pre-cooling",
    action_name="Pre-Cooling - Optimize Peak Demand",
    action_type="optimization",
    description="Strategic pre-cooling during off-peak hours to reduce peak demand costs",
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
                {"value": "operator:Operator", "label": "Operator (No Access)"},
                {"value": "facility_manager:Facility Manager", "label": "Facility Manager (3 zones, $50 limit)"},
                {"value": "energy_manager:Energy Manager", "label": "Energy Manager (Full Access)"},
                {"value": "contractor:Contractor", "label": "Contractor (No Access)"}
            ],
            help_text="Pre-cooling requires optimization expertise"
        ),
        UIFieldDescriptor(
            field_name="zone_ids",
            field_type="multi-select",
            label="Select Zones for Pre-Cooling",
            required=True,
            options=[{"value": "dynamic", "label": "Populated from available zones"}],  # Populated dynamically
            help_text="Facility Mgr: max 3 zones"
        ),
        UIFieldDescriptor(
            field_name="target_temp",
            field_type="number",
            label="Target Temperature (°F)",
            required=True,
            default_value=65.0,
            min_value=60.0,
            max_value=75.0,
            step=0.5,
            help_text="Range: 60-75°F for pre-cooling comfort"
        ),
        UIFieldDescriptor(
            field_name="start_time",
            field_type="time",
            label="Start Time (HH:MM, 24-hour)",
            required=True,
            default_value="05:00",
            pattern=r"^([01]\d|2[0-3]):([0-5]\d)$",
            placeholder="05:00",
            help_text="When to begin pre-cooling"
        ),
        UIFieldDescriptor(
            field_name="occupancy_start",
            field_type="time",
            label="Occupancy Start (HH:MM, 24-hour)",
            required=True,
            default_value="08:00",
            pattern=r"^([01]\d|2[0-3]):([0-5]\d)$",
            placeholder="08:00",
            help_text="When occupants arrive"
        ),
        UIFieldDescriptor(
            field_name="max_rate_delta",
            field_type="number",
            label="Max Cooling Rate (°F/hr)",
            required=True,
            default_value=5.0,
            min_value=1.0,
            max_value=10.0,
            step=0.5,
            help_text="1-10°F/hr cooling rate limit"
        ),
        UIFieldDescriptor(
            field_name="electricity_rate",
            field_type="number",
            label="Electricity Rate ($/kWh)",
            required=True,
            default_value=0.12,
            min_value=0.01,
            max_value=1.0,
            step=0.01,
            help_text="Cost per kilowatt-hour for cost estimation"
        ),
        UIFieldDescriptor(
            field_name="enable_adaptive",
            field_type="checkbox",
            label="Enable Adaptive Learning",
            required=False,
            default_value=True,
            help_text="Learn from historical patterns to optimize"
        ),
        UIFieldDescriptor(
            field_name="reason",
            field_type="text",
            label="Reason",
            required=True,
            placeholder="e.g., Peak demand reduction",
            help_text="Explanation for pre-cooling action"
        )
    ],

    ui_layout="single-column",

    # Graph Representation
    graph_nodes=[
        GraphNodeDescriptor(
            node_id="action:pre-cooling",
            node_type="action",
            label="Pre-Cooling Optimization",
            description="Peak demand reduction through strategic cooling",
            relationships=[
                {"target": "constraint:target-temp-range", "type": "has_constraint"},
                {"target": "constraint:time-window", "type": "has_constraint"},
                {"target": "constraint:cooling-rate", "type": "has_constraint"},
                {"target": "constraint:economics-validation", "type": "has_constraint"},
                {"target": "policy:operator-denied", "type": "governed_by"},
                {"target": "policy:fm-zone-limit", "type": "governed_by"},
                {"target": "policy:fm-cost-limit", "type": "governed_by"},
                {"target": "policy:contractor-denied", "type": "governed_by"},
                {"target": "brick:HVAC_System", "type": "targets"}
            ]
        ),
        GraphNodeDescriptor(
            node_id="constraint:target-temp-range",
            node_type="constraint",
            label="Target Temp: 60-75°F (≥62°F for economics)",
            description="SHACL: Temperature limits with economic validation"
        ),
        GraphNodeDescriptor(
            node_id="constraint:time-window",
            node_type="constraint",
            label="Time Window: 30 min - 8 hours",
            description="SHACL: Pre-cooling window constraints"
        ),
        GraphNodeDescriptor(
            node_id="constraint:cooling-rate",
            node_type="constraint",
            label="Cooling Rate: 1-10°F/hr",
            description="SHACL: Maximum cooling rate for equipment protection"
        ),
        GraphNodeDescriptor(
            node_id="constraint:economics-validation",
            node_type="constraint",
            label="Economics: Target ≥62°F",
            description="SHACL: Prevent excessive energy waste"
        ),
        GraphNodeDescriptor(
            node_id="policy:operator-denied",
            node_type="policy",
            label="Operator: No Access",
            description="ODRL: Requires optimization expertise"
        ),
        GraphNodeDescriptor(
            node_id="policy:fm-zone-limit",
            node_type="policy",
            label="Facility Manager: Max 3 Zones",
            description="ODRL: Zone count limitation"
        ),
        GraphNodeDescriptor(
            node_id="policy:fm-cost-limit",
            node_type="policy",
            label="Facility Manager: $50 Cost Limit",
            description="ODRL: Budget constraint"
        ),
        GraphNodeDescriptor(
            node_id="policy:contractor-denied",
            node_type="policy",
            label="Contractor: No Access",
            description="ODRL: Requires building system knowledge"
        )
    ],

    # Audit Log Formatting
    audit_descriptor=AuditLogDescriptor(
        summary_template="{zone_count} zones pre-cooled to {target_temp}°F (Cost: ${estimated_cost})",
        icon="❄️",
        detail_fields=[
            {"param": "target_temp", "label": "Target Temperature", "format": "temperature"},
            {"param": "start_time", "label": "Start Time", "format": "time"},
            {"param": "occupancy_start", "label": "Occupancy Start", "format": "time"},
            {"param": "max_rate_delta", "label": "Max Cooling Rate", "format": "cooling_rate"},
            {"param": "electricity_rate", "label": "Electricity Rate", "format": "currency_rate"},
            {"param": "estimated_cost", "label": "Estimated Cost", "format": "currency"},
            {"param": "enable_adaptive", "label": "Adaptive Learning", "format": "boolean"},
            {"param": "zones", "label": "Zones", "format": "zone_list"},
            {"param": "reason", "label": "Reason", "format": "text"}
        ],
        formatters={
            "target_temp": "temperature",
            "start_time": "time",
            "occupancy_start": "time",
            "max_rate_delta": "cooling_rate",
            "electricity_rate": "currency_rate",
            "estimated_cost": "currency",
            "enable_adaptive": "boolean_enabled",
            "zones": "zone_list"
        }
    ),

    # SHACL Constraints
    shacl_constraints=[
        "Target temperature: 60-75°F (≥62°F for economics)",
        "Time window: 30 minutes to 8 hours",
        "Max cooling rate: 1-10°F/hr",
        "No duplicate zones, no empty zone IDs",
        "Time format: HH:MM (24-hour)",
        "Overnight windows supported"
    ],

    # ODRL Governance
    odrl_policies={
        "operator": {
            "permitted": False,
            "reason": "Pre-cooling requires optimization expertise"
        },
        "facility_manager": {
            "permitted": True,
            "constraints": [
                "max_zones: 3",
                "max_cost: $50",
                "priority: low/medium only"
            ]
        },
        "energy_manager": {
            "permitted": True,
            "constraints": [
                "max_zones: unlimited",
                "max_cost: $500",
                "priority: low/medium/high",
                "optimization_authority: true"
            ]
        },
        "contractor": {
            "permitted": False,
            "reason": "Pre-cooling requires building system knowledge"
        }
    },

    # Target & Execution
    target_type="brick:HVAC_System",
    required_permissions=["zone:write", "hvac:control", "demand:optimize", "pre-cooling:execute"],
    side_effects=["power:consumption_increase", "peak:demand_reduction", "cost:savings", "comfort:optimization"],
    handler_function="_handle_pre_cooling",
    validation_class="PreCoolingInput",
    cost_calculator="calculate_pre_cooling_cost"
)

# Register with global registry
action_registry.register(pre_cooling_descriptor)
