# KBE Ontology Knowledge Graph Visualization

## Overview

The KBE Ontology Knowledge Graph provides an interactive visualization of the semantic relationships powering the KBE demo application. This graph shows how classes, actions, properties, constraints, and governance policies interconnect to form a complete knowledge-based engineering system.

## Access

- **URL**: http://localhost:8008/static/graph.html
- **Link from main demo**: Click "🕸️ View Knowledge Graph" in the header

## Graph Components

### Node Types

The graph visualizes 7 different types of entities:

1. **Brick Classes** (Blue `#4e54c8`)
   - Building ontology classes from Brick Schema
   - Examples: `brick:Zone`, `brick:HVAC_Zone`, `brick:Temperature_Setpoint`
   - Foundation for semantic building modeling

2. **KBE Actions** (Green `#28a745`)
   - ActionDefinition templates for operations
   - Examples: `kbe:AdjustSetpoint`, `kbe:LoadShed`, `kbe:PreCooling`
   - Executable building automation actions

3. **Properties** (Yellow `#ffc107`)
   - Measurable/controllable attributes
   - Examples: `temperature_setpoint`, `occupancy_mode`, `power_usage`
   - State representation for zones and equipment

4. **Constraints** (Red `#dc3545`)
   - SHACL-style validation rules
   - Examples: `TempRange (60-80°F)`, `MaxDelta (15°F)`, `ShedLevel (1-5)`
   - Business logic enforcement

5. **Equipment** (Cyan `#17a2b8`)
   - Physical building systems
   - Examples: `brick:HVAC_System`, `brick:Lighting_System`
   - Controllable building infrastructure

6. **ODRL Policies** (Purple `#6f42c1`)
   - Governance and access control policies
   - Examples: `OperatorPolicy`, `EnergyManagerPolicy`, `ContractorPolicy`
   - Role-based permission management

7. **User Roles** (Orange `#fd7e14`)
   - Actor roles in the system
   - Examples: `Operator`, `Facility Manager`, `Energy Manager`, `Contractor`
   - Authorization principals

### Relationship Types

The graph shows 9 types of semantic relationships:

1. **composition** - Part-of relationships (Building → Zone)
2. **inheritance** - Subclass relationships (Zone → HVAC_Zone)
3. **association** - General associations (Zone → Equipment)
4. **property** - Property ownership (Zone → temperature_setpoint)
5. **action-target** - Action applies to class (AdjustSetpoint → Temperature_Setpoint)
6. **validation** - Action validates constraint (AdjustSetpoint → TempRange)
7. **permission** - Policy permits action (OperatorPolicy → AdjustSetpoint)
8. **enforcement** - Policy enforces constraint (OperatorPolicy → RoleDelta)
9. **role-policy** - Role has policy (Operator → OperatorPolicy)

## Features

### Interactive Controls

- **Layout Modes**:
  - **Force-Directed** (default): Natural physics-based layout
  - **Hierarchical**: Vertical layers by node type
  - **Radial**: Circular layout from Building center

- **Filtering**:
  - All Nodes (default)
  - Classes Only - Focus on Brick ontology
  - Actions Only - View executable operations
  - Properties Only - See state attributes

- **Navigation**:
  - Drag nodes to reposition
  - Scroll/pinch to zoom
  - Click "Reset View" to restore default zoom
  - Click node to select and view details

### Sidebar Information

- **Legend**: Color-coded node types
- **Statistics**: Real-time graph metrics
  - Total nodes and relationships
  - Counts by type (classes, actions, properties)
- **Node Details**: Click any node to see:
  - Full ID and type
  - Description
  - Incoming relationships
  - Outgoing relationships

### Export

- Click "Export SVG" to download the graph as a vector image
- Useful for documentation and presentations

## Graph Insights

### Key Patterns

1. **Brick Foundation**:
   - Building → Zone → HVAC_Zone hierarchy
   - Zones have points (sensors, setpoints)
   - Zones have equipment (HVAC, lighting)

2. **Action Structure**:
   - Actions target specific Brick classes
   - Actions validate multiple SHACL constraints
   - Actions are governed by ODRL policies

3. **Governance Flow**:
   - Roles → Policies → Actions → Constraints
   - Multi-layered access control
   - Role-specific constraint enforcement

4. **Validation Chain**:
   - Actions check SHACL constraints (comfort ranges, deltas)
   - Policies enforce role-based rules (operator 5°F limit)
   - Combined validation prevents invalid operations

## Implementation Details

### Technology Stack

- **D3.js v7**: Force-directed graph layout and visualization
- **SVG**: Scalable vector graphics rendering
- **Vanilla JavaScript**: No framework dependencies

### Graph Data Structure

The graph is defined in `graph.html` as a JSON structure:

```javascript
const graphData = {
    nodes: [
        { id: 'brick:Zone', label: 'Zone', type: 'class', description: '...', color: '#4e54c8' },
        { id: 'kbe:AdjustSetpoint', label: 'Adjust Setpoint', type: 'action', ... },
        // ... more nodes
    ],
    links: [
        { source: 'brick:Building', target: 'brick:Zone', label: 'hasPart', type: 'composition' },
        { source: 'kbe:AdjustSetpoint', target: 'brick:Temperature_Setpoint', label: 'targetType', type: 'action-target' },
        // ... more links
    ]
};
```

### Extending the Graph

To add new nodes or relationships:

1. Add node to `graphData.nodes` array
2. Add relationships to `graphData.links` array
3. Update legend if introducing new node type
4. Consider adding new arrow marker if new link type

## Use Cases

### 1. System Documentation

- Visual explanation of KBE architecture
- Onboarding new developers
- Architecture review presentations

### 2. Ontology Development

- Identify missing relationships
- Validate semantic consistency
- Explore class hierarchies

### 3. Debugging

- Trace action validation paths
- Understand permission flows
- Identify constraint conflicts

### 4. Education

- Teach KBE concepts visually
- Compare with Brick Schema
- Demonstrate ODRL governance

## Comparison with Traditional Ontology Tools

Unlike Protégé, WebVOWL, or other RDF/OWL visualizers:

- **Tailored to KBE**: Shows actions and governance, not just class hierarchies
- **Interactive**: Real-time layout, filtering, and exploration
- **Embedded**: Integrated with demo application
- **Lightweight**: No server-side reasoning engine required
- **Developer-friendly**: Simple JSON data structure

## Future Enhancements

Potential additions:

- [ ] Search/filter by node name
- [ ] Highlight paths between selected nodes
- [ ] Show ActionExecution instances from audit trail
- [ ] Timeline view of action executions
- [ ] Export to GraphML/GEXF for external analysis
- [ ] Load ontology from SHACL/RDF files
- [ ] Real-time updates from running system
- [ ] Diff view between ontology versions

## References

- **Brick Schema**: https://brickschema.org/
- **SHACL**: https://www.w3.org/TR/shacl/
- **ODRL**: https://www.w3.org/TR/odrl-model/
- **D3.js Force Layout**: https://d3js.org/d3-force

---

*Part of the KBE Proof-of-Concept Demo*
*Built with Hive Mind Collective Intelligence System*
