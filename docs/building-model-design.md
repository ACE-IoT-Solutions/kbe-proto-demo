# Building Model Design for KBE PoC Demo

## Executive Summary

This document defines a simplified building model designed for the Knowledge-Based Engineering (KBE) Proof of Concept demonstration. The model focuses on actionability - enabling users to execute building control actions through the KBE system with proper validation and side-effect management.

**Building Type**: Small commercial office building
**Complexity Level**: Simplified for demo (PoC scope)
**Primary Goal**: Demonstrate KBE action execution with scheduling and demand management scenarios

---

## 1. Building Topology

### 1.1 Building Overview

```
┌─────────────────────────────────────────┐
│         Demo Building (DemoB-001)       │
│  Small Commercial Office (5-Story)      │
│  Total Area: 10,000 m²                  │
│  Total Occupants: ~150                  │
└─────────────────────────────────────────┘
         │
    ┌────┴────────────────────────┬───────────┐
    │                             │           │
┌───▼──────────┐  ┌──────────────▼──┐  ┌─────▼────────┐
│  Floor 1-4   │  │   Server Room   │  │  Building    │
│  (4 zones)   │  │   (1 zone)      │  │  Systems     │
└──────────────┘  └─────────────────┘  └──────────────┘
```

### 1.2 Zone Structure

The building is divided into **5 thermal zones**, each with independent control:

| Zone ID | Zone Name | Type | Area | Occupants | Priority | Description |
|---------|-----------|------|------|-----------|----------|-------------|
| Z001 | Office Zone | OFFICE | 4,000 m² | 80 | MEDIUM | Open office workspace, 4 floors |
| Z002 | Conference Zone | CONFERENCE | 2,000 m² | 40 | MEDIUM | Meeting rooms, training areas |
| Z003 | Common Zone | COMMON | 2,500 m² | 20 | LOW | Hallways, restrooms, break rooms |
| Z004 | Server Room | MECHANICAL | 800 m² | 0 | CRITICAL | IT equipment, requires stable conditions |
| Z005 | Lobby & Entry | COMMON | 700 m² | 10 | LOW | Building entry, reception |

---

## 2. Equipment Configuration

### 2.1 HVAC Systems

Each zone has dedicated HVAC equipment:

```typescript
interface HVACUnit {
  id: string;                  // Unique equipment ID
  zoneId: string;              // Associated zone
  type: 'VAV' | 'CAV' | 'FCU'; // Unit type
  capacity: number;            // BTU/h capacity
  powerConsumption: {
    heating: number;           // Watts (heating mode)
    cooling: number;           // Watts (cooling mode)
    ventilation: number;       // Watts (ventilation only)
  };
}
```

**HVAC Unit Specifications**:

| Zone | Equipment ID | Type | Capacity | Heating Power | Cooling Power | Ventilation |
|------|--------------|------|----------|---------------|---------------|-------------|
| Z001 | HVAC-Z001 | VAV | 150,000 BTU/h | 18,000W | 22,000W | 8,000W |
| Z002 | HVAC-Z002 | VAV | 80,000 BTU/h | 10,000W | 12,000W | 4,000W |
| Z003 | HVAC-Z003 | CAV | 60,000 BTU/h | 7,500W | 9,000W | 3,500W |
| Z004 | HVAC-Z004 | FCU | 40,000 BTU/h | 5,000W | 6,000W | 2,000W |
| Z005 | HVAC-Z005 | CAV | 30,000 BTU/h | 3,500W | 4,500W | 2,000W |

### 2.2 Thermostat & Sensor Equipment

```typescript
interface Thermostat {
  id: string;                  // Device ID
  zoneId: string;              // Associated zone
  type: 'Smart' | 'Basic';     // Thermostat type
  capabilities: {
    occupancySensor: boolean;  // Motion detection
    humidity: boolean;         // Humidity sensing
    co2: boolean;              // CO2 monitoring
  };
  communicationProtocol: 'Modbus' | 'BACnet' | 'MQTT';
}
```

**Thermostat Inventory**:

| Zone | Thermostat ID | Type | Occupancy | Humidity | CO2 | Protocol |
|------|---------------|------|-----------|----------|-----|----------|
| Z001 | STAT-Z001 | Smart | Yes | Yes | Yes | BACnet |
| Z002 | STAT-Z002 | Smart | Yes | No | No | BACnet |
| Z003 | STAT-Z003 | Basic | Yes | No | No | Modbus |
| Z004 | STAT-Z004 | Smart | No | Yes | Yes | BACnet |
| Z005 | STAT-Z005 | Basic | Yes | No | No | Modbus |

### 2.3 Lighting Systems

```typescript
interface LightingSystem {
  id: string;                  // Fixture group ID
  zoneId: string;              // Associated zone
  type: 'LED' | 'Fluorescent';
  controlType: 'Dimmable' | 'OnOff';
  powerConsumption: number;    // Watts at full brightness
  quantity: number;            // Number of fixtures
}
```

**Lighting Inventory**:

| Zone | Light System ID | Type | Control | Power @ 100% | Quantity | Installed Power |
|------|-----------------|------|---------|--------------|----------|-----------------|
| Z001 | LIGHT-Z001 | LED | Dimmable | 200W | 40 | 8,000W |
| Z002 | LIGHT-Z002 | LED | Dimmable | 150W | 20 | 3,000W |
| Z003 | LIGHT-Z003 | Fluorescent | OnOff | 100W | 30 | 3,000W |
| Z004 | LIGHT-Z004 | LED | Dimmable | 300W | 50 | 15,000W |
| Z005 | LIGHT-Z005 | LED | Dimmable | 120W | 15 | 1,800W |

---

## 3. Zone Thermal Characteristics

### 3.1 Temperature Control Ranges

```typescript
interface ZoneThermalProfile {
  zoneId: string;
  currentTemp: number;         // Current temperature (°C)
  targetTemp: number;          // Target setpoint (°C)

  // Temperature limits
  minAllowedTemp: number;      // Absolute minimum
  maxAllowedTemp: number;      // Absolute maximum

  // Comfort ranges
  comfortMin: number;          // Comfort range minimum
  comfortMax: number;          // Comfort range maximum

  // Thermal dynamics
  maxRampRate: number;         // Max °C per hour
  thermalMass: 'High' | 'Medium' | 'Low';
}
```

**Zone Thermal Specifications**:

| Zone | Min Allowed | Max Allowed | Comfort Min | Comfort Max | Max Ramp | Thermal Mass |
|------|-------------|-------------|-------------|-------------|----------|--------------|
| Z001 (Office) | 15°C | 30°C | 20°C | 24°C | 3°C/hr | Medium |
| Z002 (Conference) | 16°C | 29°C | 19°C | 24°C | 2.5°C/hr | Medium |
| Z003 (Common) | 14°C | 28°C | 18°C | 25°C | 4°C/hr | Low |
| Z004 (Server) | 10°C | 26°C | 15°C | 25°C | 1°C/hr | High |
| Z005 (Lobby) | 16°C | 28°C | 19°C | 24°C | 3°C/hr | Medium |

### 3.2 Occupancy Schedules

```typescript
interface OccupancySchedule {
  zoneId: string;
  weekday: {
    morningStart: string;      // "06:00" format
    morningEnd: string;
    eveningStart: string;
    eveningEnd: string;
  };
  weekend: {
    occupied: boolean;
    hours?: string[];          // If partially occupied
  };
  holidays: string[];          // ISO date strings
}
```

**Standard Operating Schedules**:

| Zone | Mon-Fri | Saturday | Sunday | Notes |
|------|---------|----------|--------|-------|
| Z001 (Office) | 06:00-22:00 | 08:00-18:00 | Closed | Pre-cool 1hr before |
| Z002 (Conference) | 07:00-20:00 | 09:00-17:00 | Closed | On-demand override |
| Z003 (Common) | 06:00-22:00 | 08:00-18:00 | Closed | Limited occupancy |
| Z004 (Server) | 24/7 | 24/7 | 24/7 | Critical - no setback |
| Z005 (Lobby) | 06:00-22:00 | 08:00-18:00 | Closed | Follows main schedule |

---

## 4. Key KBE Actions for Demo

### 4.1 Action 1: Adjust Zone Setpoint (Scheduling Action)

**Purpose**: Modify target temperature for a zone with validation

**Action Identifier**: `kbe:ZoneSetpointAdjustment`

```typescript
interface AdjustZoneSetpointAction {
  // Action metadata
  actionId: string;                    // Unique action instance ID
  actionType: 'SCHEDULING';
  name: 'Adjust Zone Setpoint';
  description: 'Modify target temperature for comfort or energy savings';

  // Input parameters
  inputs: {
    zoneId: string;                    // Target zone (Z001-Z005)
    newSetpoint: number;               // New temperature in °C
    duration: 'IMMEDIATE' | 'TIMED';   // Apply until next schedule or for duration
    durationMinutes?: number;          // If TIMED, duration in minutes
    reason: string;                    // 'comfort_adjustment' | 'demand_response' | 'pre_cooling'
  };

  // Validation rules
  validationRules: ValidationRule[];

  // Side effects
  sideEffects: SideEffect[];

  // Execution timestamp
  executedAt?: Date;
  status: 'PENDING' | 'EXECUTING' | 'COMPLETED' | 'FAILED';
}
```

#### Input Validation Rules

```yaml
Validation Rules for Zone Setpoint Adjustment:

V1_ZoneExists:
  Rule: "Zone ID must exist in building model"
  Check: "zoneId in [Z001, Z002, Z003, Z004, Z005]"
  Impact: "CRITICAL - Reject if zone not found"

V2_SetpointInRange:
  Rule: "New setpoint must be within zone's allowed range"
  Check: "minAllowedTemp ≤ newSetpoint ≤ maxAllowedTemp"
  Example: "Z001 allows 15°C-30°C, cannot set 32°C"
  Impact: "CRITICAL - Reject if out of range"
  ErrorMessage: "Setpoint {value}°C outside zone range {min}-{max}°C"

V3_OccupancyConstraint:
  Rule: "Occupied zones must maintain comfort ranges"
  Check: "If zone.isOccupied AND newSetpoint outside comfortMin-comfortMax"
  Example: "Z001 occupied, cannot set below 20°C (comfort min)"
  Impact: "WARNING - Allow with confirmation"
  ErrorMessage: "Zone is occupied. Setting {value}°C outside comfort range."

V4_RampRateCompliance:
  Rule: "Temperature change must respect thermal dynamics"
  Check: "|newSetpoint - currentTemp| ≤ (maxRampRate × timeAvailable)"
  Example: "Z001 max 3°C/hr. If current=22°C, in 1 hour max reach 25°C"
  Impact: "WARNING - Suggest staged adjustment"
  ErrorMessage: "Cannot reach {setpoint}°C in {time}min (max ramp: {rate}°C/hr)"

V5_ServerRoomProtection:
  Rule: "Server room (Z004) has strict constraints"
  Check: "If zoneId == Z004: setpoint must be 15-25°C (critical range)"
  Impact: "CRITICAL - Reject if outside critical range"
  ErrorMessage: "Server room requires 15-25°C. Requested: {value}°C"

V6_MultipleAdjustmentsConflict:
  Rule: "Cannot have conflicting simultaneous adjustments"
  Check: "No other pending adjustment for same zone"
  Impact: "WARNING - Queue adjustment or cancel previous"
  ErrorMessage: "Zone already has pending adjustment. Current: {pending}"
```

#### Side Effects

```yaml
Side Effects of Zone Setpoint Adjustment:

SE1_HVACModeChange:
  Description: "HVAC unit mode may change based on setpoint"
  Examples:
    - "If newSetpoint > currentTemp: Switch to HEATING"
    - "If newSetpoint < currentTemp: Switch to COOLING"
    - "If newSetpoint == currentTemp: IDLE or VENTILATION_ONLY"
  MeasurableImpact: "Power consumption changes (see HVAC specs)"

SE2_LightingStateConsideration:
  Description: "Lower setpoint may affect occupancy inference"
  Examples:
    - "Reduced setpoint might indicate vacancy prep"
    - "System may auto-reduce lighting if occupancy drops"
  MeasurableImpact: "Minor - lighting reduction if occupancy changes"

SE3_DemandImpact:
  Description: "Building total demand may increase/decrease"
  ZoneZ001Example:
    - "Z001 heating mode +18kW"
    - "Building demand impact: +18kW"
  Monitoring: "Track total building demand vs 500kW limit"

SE4_ScheduleInteraction:
  Description: "TIMED adjustments override schedule for duration"
  Example: "60-minute setpoint override, then revert to schedule"
  Recovery: "Automatic return to schedule when timer expires"
```

#### Action Execution Example

```json
{
  "actionId": "act-adjust-z001-20241120-0930",
  "actionType": "SCHEDULING",
  "name": "Adjust Zone Setpoint",
  "inputs": {
    "zoneId": "Z001",
    "newSetpoint": 21.5,
    "duration": "TIMED",
    "durationMinutes": 120,
    "reason": "comfort_adjustment"
  },
  "validation": {
    "passed": true,
    "checks": [
      {"rule": "V1_ZoneExists", "status": "PASS", "message": "Zone Z001 found"},
      {"rule": "V2_SetpointInRange", "status": "PASS", "message": "21.5°C in range [15, 30]"},
      {"rule": "V3_OccupancyConstraint", "status": "PASS", "message": "Within comfort range [20, 24]"},
      {"rule": "V4_RampRateCompliance", "status": "PASS", "message": "Can reach target in time"},
      {"rule": "V5_ServerRoomProtection", "status": "SKIPPED", "message": "Not a server room"},
      {"rule": "V6_MultipleAdjustmentsConflict", "status": "PASS", "message": "No conflicts"}
    ]
  },
  "executedAt": "2024-11-20T09:30:00Z",
  "status": "COMPLETED",
  "result": {
    "previousSetpoint": 22.0,
    "newSetpoint": 21.5,
    "affectedZone": "Z001",
    "expectedHVACMode": "COOLING",
    "estimatedPowerChange": "+5000W",
    "durationMinutes": 120,
    "scheduledRevertTime": "2024-11-20T11:30:00Z"
  }
}
```

---

### 4.2 Action 2: Load Shed - Reduce Lighting (Demand Management Action)

**Purpose**: Reduce lighting load during peak demand periods

**Action Identifier**: `kbe:DemandResponseLoadShed`

```typescript
interface LoadShedAction {
  // Action metadata
  actionId: string;
  actionType: 'DEMAND_MANAGEMENT';
  name: 'Load Shed - Reduce Lighting';
  description: 'Reduce lighting brightness to cut peak demand';

  // Input parameters
  inputs: {
    targetZones: string[];             // Zones to affect (can be multiple)
    reductionPercentage: number;       // 0-100% reduction
    durationMinutes: number;           // How long to maintain reduction
    priority: 'LOW' | 'MEDIUM' | 'HIGH';
    reason: string;                    // 'peak_demand' | 'utility_event' | 'cost_optimization'
  };

  // Validation rules
  validationRules: ValidationRule[];

  // Side effects
  sideEffects: SideEffect[];
}
```

#### Input Validation Rules

```yaml
Validation Rules for Load Shed - Reduce Lighting:

V1_ZoneValidity:
  Rule: "All specified zones must exist"
  Check: "Every zoneId in targetZones exists in [Z001-Z005]"
  Impact: "CRITICAL - Reject if any zone invalid"
  ErrorMessage: "Zone {zoneId} not found"

V2_OccupancyCheck:
  Rule: "Cannot reduce lighting below safety threshold if occupied"
  Check: "If zone.isOccupied AND reductionPercentage > 50: Warning"
  Example: "Z001 occupied, 70% reduction may cause comfort issues"
  Impact: "WARNING - Allow with confirmation"
  ErrorMessage: "Zone is occupied. 70% lighting reduction may affect comfort."
  SafetyMinimum: "20% illuminance (minimum for safety code compliance)"

V3_ReductionPercentageValid:
  Rule: "Reduction must be within sensible range"
  Check: "0 ≤ reductionPercentage ≤ 100"
  Constraints:
    - "0% = No change (no-op)"
    - "100% = Complete blackout (rarely recommended)"
    - "30-50% = Recommended range for demand response"
  Impact: "WARNING - Clamp to sensible range"

V4_DurationReasonable:
  Rule: "Shedding duration must be practical"
  Check: "0 < durationMinutes ≤ 480 (8 hours max)"
  Rationale: "Temporary demand response, not permanent changes"
  Impact: "WARNING - Cap at 480 minutes"
  ErrorMessage: "Duration {value} exceeds maximum of 480 minutes"

V5_ControllableZonesOnly:
  Rule: "Cannot shed lighting from zones without dimmable controls"
  Check: "For each zone: lighting.controlType must be 'Dimmable'"
  ZoneZ003_Issue: "Z003 has non-dimmable fluorescent (OnOff only)"
  Impact: "WARNING - Z003 cannot be dimmed (all-or-nothing)"
  Workaround: "Z003 can only be turned OFF (100% shed)"

V6_DemandImpactValidation:
  Rule: "Load reduction must actually help building demand"
  Check: "buildingDemand > warningThreshold (400kW)"
  Example: "If demand is only 200kW, shedding unnecessary"
  Impact: "INFO - Action allowed but may not be needed"
  Message: "Building demand currently {demand}kW (warning: 400kW)"

V7_ServerRoomExemption:
  Rule: "Server room (Z004) typically excluded from aggressive shedding"
  Check: "If 'Z004' in targetZones AND reductionPercentage > 50: Warning"
  Impact: "WARNING - Server room lighting critical for safety"
  Recommendation: "Reduce Z004 by max 30% if included"
```

#### Side Effects

```yaml
Side Effects of Load Shed - Reduce Lighting:

SE1_OccupantComfort:
  Description: "Dimmed lighting affects occupant comfort and productivity"
  ImpactPerZone:
    Z001: "High impact - Large occupied office space"
    Z002: "High impact - Conference rooms require adequate lighting"
    Z003: "Low impact - Corridors tolerate lower light"
    Z004: "Medium impact - Server room for maintenance visibility"
    Z005: "Medium impact - Lobby/reception perception"
  RecoveryAction: "Restore to previous brightness when DR event ends"

SE2_AmbientIlluminance:
  Description: "Measured reduction in visible light levels"
  TypicalMetrics:
    "30% reduction": "300 lux → 210 lux (noticeable but acceptable)"
    "50% reduction": "300 lux → 150 lux (significant, may need adjustment)"
    "70% reduction": "300 lux → 90 lux (minimal, safety concern)"
  StandardCompliance: "ANSI/IESNA recommends 300-500 lux for offices"

SE3_PowerConsumptionReduction:
  Description: "Measurable reduction in electrical demand"
  CalculationExample:
    Zone: "Z001"
    Installed: "8,000W at full brightness"
    Reduction: "40%"
    PowerSaved: "3,200W (40% of 8,000W)"
  BuildingImpact:
    Z001: "-3,200W"
    Z002: "-1,200W (40% of 3,000W)"
    Z005: "-720W (40% of 1,800W)"
    Total: "-5,120W shed"

SE4_OccupancySensorInteraction:
  Description: "Dimmer lighting may affect occupancy detection"
  Risk: "Motion sensors may trigger false negatives"
  Mitigation: "Motion sensors use infrared, not affected by visible light"

SE5_ScheduleRecovery:
  Description: "Automatic recovery to normal levels after duration"
  Timeline: "At end of durationMinutes, restore original brightness"
  RecoveryRamp: "1% per 10 seconds (smooth, not jarring)"
  Example: "50% reduction for 60 minutes → restore gradually over 3 mins"
```

#### Action Execution Example

```json
{
  "actionId": "act-loadshed-20241120-1500",
  "actionType": "DEMAND_MANAGEMENT",
  "name": "Load Shed - Reduce Lighting",
  "inputs": {
    "targetZones": ["Z001", "Z002", "Z005"],
    "reductionPercentage": 40,
    "durationMinutes": 120,
    "priority": "HIGH",
    "reason": "peak_demand"
  },
  "validation": {
    "passed": true,
    "checks": [
      {"rule": "V1_ZoneValidity", "status": "PASS", "zones": 3},
      {"rule": "V2_OccupancyCheck", "status": "WARNING", "message": "Z001 occupied"},
      {"rule": "V3_ReductionPercentageValid", "status": "PASS", "value": 40},
      {"rule": "V4_DurationReasonable", "status": "PASS", "value": 120},
      {"rule": "V5_ControllableZonesOnly", "status": "PASS", "dimmable": 3},
      {"rule": "V6_DemandImpactValidation", "status": "PASS", "currentDemand": 450},
      {"rule": "V7_ServerRoomExemption", "status": "SKIPPED", "reason": "Z004 not included"}
    ]
  },
  "executedAt": "2024-11-20T15:00:00Z",
  "status": "COMPLETED",
  "result": {
    "affectedZones": ["Z001", "Z002", "Z005"],
    "reductionPerZone": {
      "Z001": {"from": "8,000W", "to": "4,800W", "saved": "3,200W"},
      "Z002": {"from": "3,000W", "to": "1,800W", "saved": "1,200W"},
      "Z005": {"from": "1,800W", "to": "1,080W", "saved": "720W"}
    },
    "totalPowerSaved": "5,120W",
    "buildingDemandBefore": "450kW",
    "buildingDemandAfter": "444.88kW",
    "scheduledRestoreTime": "2024-11-20T17:00:00Z"
  }
}
```

---

### 4.3 Action 3: Pre-Cooling Optimization (Scheduling + Optimization Action)

**Purpose**: Lower zone temperature during off-peak hours to reduce peak demand

**Action Identifier**: `kbe:PreCoolingOptimization`

```typescript
interface PreCoolingAction {
  // Action metadata
  actionId: string;
  actionType: 'SCHEDULING_AND_OPTIMIZATION';
  name: 'Pre-Cooling Optimization';
  description: 'Lower setpoint during off-peak to reduce peak demand later';

  // Input parameters
  inputs: {
    targetZones: string[];             // Zones to pre-cool
    offPeakStartTime: string;          // "HH:MM" format (e.g., "10:00")
    offPeakEndTime: string;            // When peak period starts
    peakSetpoint: number;              // Higher setpoint during peak (to save energy)
    offPeakSetpoint: number;           // Lower setpoint for pre-cooling
    expectedPeakDemand: number;        // Forecasted peak demand (kW)
    targetReduction: number;           // Target reduction (%)
  };

  validationRules: ValidationRule[];
  sideEffects: SideEffect[];
}
```

#### Input Validation Rules

```yaml
Validation Rules for Pre-Cooling Optimization:

V1_TimeWindowLogic:
  Rule: "Off-peak period must precede peak period"
  Check: "offPeakEndTime < peakStartTime"
  Example: "Cannot pre-cool 14:00-18:00 if peak is 12:00-14:00"
  Impact: "CRITICAL - Reject invalid time logic"

V2_SetpointDifference:
  Rule: "Off-peak setpoint must be lower than peak setpoint"
  Check: "offPeakSetpoint < peakSetpoint"
  Minimum: "Difference ≥ 1°C (must have measurable cooling)"
  Maximum: "Difference ≤ 5°C (thermal comfort limits)"
  Impact: "CRITICAL - Reject if same or reversed"

V3_ThermalMassCapacity:
  Rule: "Zone must have sufficient thermal mass for strategy"
  ZonesThermalMass:
    Z001: "Medium - OK for pre-cooling"
    Z002: "Medium - OK for pre-cooling"
    Z003: "Low - Limited pre-cooling benefit"
    Z004: "High - Excellent for pre-cooling"
    Z005: "Medium - OK for pre-cooling"
  Impact: "WARNING - Low thermal mass zones less effective"

V4_DemandForecastValidity:
  Rule: "Forecast must be realistic"
  Check: "buildingCapacity ≥ expectedPeakDemand"
  BuildingCapacity: "500kW (from utility contract)"
  Impact: "WARNING - If forecast unrealistic"

V5_OccupancyOverlapCheck:
  Rule: "Should not aggressively pre-cool during occupancy"
  Check: "If offPeakWindow overlaps with occupancy AND newSetpoint < comfortMin"
  Impact: "WARNING - May affect occupant comfort"
  Example: "Pre-cool to 18°C from 2-4 PM when office occupied (comfort min 20°C)"
```

#### Side Effects

```yaml
Side Effects of Pre-Cooling Optimization:

SE1_ThermalShiftEnergy:
  Description: "Cooling cost shifted from peak to off-peak hours"
  Economics:
    OffPeakCooling: "$0.15/kWh (off-peak rate)"
    PeakAvoided: "$0.45/kWh (peak rate)"
    Example: "Use 10 kWh cooling at night (cost: $1.50)"
    "vs 10 kWh avoided at peak (cost avoided: $4.50)"
    NetSavings: "$3.00 for shifting 10 kWh"

SE2_ComfortRisk:
  Description: "Aggressive pre-cooling may overshoot comfort"
  Risk: "If zone drops to 18°C, occupants may find it too cold at 3 PM"
  Mitigation: "Gradual warming from 18°C → target by occupancy time"
  Recommendation: "Pre-cool only 1-2°C below comfort min"

SE3_PeakDemandReduction:
  Description: "Building demand reduced during critical peak window"
  Mechanism: "Thermal mass stores cold, HVAC ramps down during peak"
  Example:
    - "Pre-cool Z001 to 18°C from 2-4 PM (HVAC active, demand +5kW)"
    - "At 4 PM peak, zone temperature drifts 18°C → 21°C (HVAC idle)"
    - "Peak demand reduced by 5-10kW during 4-6 PM window"
  MeasurableKPI: "Peak demand reduction: 15-25% typical"

SE4_RecoveryPhase:
  Description: "Temperature recovery after peak period"
  Timeline: "As thermal mass warms, may need re-cooling after 6 PM"
  Risk: "Could shift demand to evening hours"
  Mitigation: "Careful orchestration with evening occupancy patterns"
```

---

## 5. Building Demand Profile

### 5.1 Total Building Demand Characteristics

```typescript
interface BuildingDemandProfile {
  buildingId: string;

  // Power capacity and limits
  utilityContract: {
    contractedCapacity: number;        // 500 kW
    peakDemandLimit: number;           // 500 kW
  };

  // Thresholds for alerts
  thresholds: {
    warningLevel: number;              // 80% = 400 kW
    criticalLevel: number;             // 95% = 475 kW
  };

  // Historical consumption patterns
  baselineLoad: {
    occupied: number;                  // Typical occupancy load
    unoccupied: number;                // Nighttime/weekend load
  };
}
```

### 5.2 Building Load Profile (Typical Weekday)

```
Building Total Demand (kW) - Typical Weekday

600 |
500 |      ╔═══════════════╗ Peak Period (High Rates)
400 |    ┌─╢                 ╟─┐
300 |  ┌─┘  │                 │  └─┐
200 |┌─┘    │                 │    └─┐
100 |│      │                 │      │
  0 |└──────┴─────────────────┴──────┘
    06:00  10:00    14:00    18:00  22:00

Key Times:
- 06:00-08:00: Morning startup (100→300 kW)
- 08:00-17:00: Business hours (300-450 kW, demand response window 14:00-18:00)
- 17:00-22:00: Evening wind-down (450→200 kW)
- 22:00-06:00: Minimal load (100-150 kW, server room only)

Demand Drivers:
- HVAC: 40-50% of load (200-250 kW)
- Lighting: 20-25% of load (100-125 kW)
- Office Equipment: 15-20% of load (75-100 kW)
- Server Room: 10-15% constant (50-75 kW)
- Other: 5-10% of load (25-50 kW)
```

---

## 6. Demo Scenario Examples

### 6.1 Scenario A: Standard Occupancy Day with Scheduling

**Goal**: Demonstrate zone scheduling and setpoint adjustment actions

**Timeline**:
```
06:00 - Building opens, pre-conditioning starts
  Action: Z001, Z002, Z005 setpoints drop to 18°C (pre-cool)
  Validation: Checks occupancy not starting yet, thermal mass suitable
  Duration: 2 hours

08:00 - Occupancy begins
  Automatic: Setpoints restore to comfort (22°C)
  Status: All zones in comfort range
  Building Demand: 300 kW

14:00 - Demand response window starts
  Action: Adjust Z003 setpoint 22°C → 23°C (reduce cooling)
  Validation: Zone occupied but allows +1°C in comfort range
  Expected: Reduce demand by 20 kW (6%)

18:00 - Occupancy ends
  Action: All zones setpoint shift to 20°C (unoccupied setback)
  Validation: Confirm no more occupancy before setback
  Recovery: Schedule-based, not timed

22:00 - Night mode
  Status: Building minimal load (server room only)
  All zones: Setback mode (20°C)
```

**Expected Outcomes**:
- Validation rules prevent unsafe setpoint changes
- HVAC side effects tracked (mode changes, power consumption)
- Demand management through scheduling demonstrated
- Comfortable occupancy hours maintained

### 6.2 Scenario B: Demand Response Event

**Goal**: Demonstrate aggressive demand management with multiple actions

**Timeline**:
```
14:00 - Utility issues demand response event
  Event: Peak demand alert (450 kW, warning 400 kW already exceeded)
  Target: Reduce to 380 kW (-15%)

14:10 - Action 1: Reduce Lighting (Load Shed)
  Target: Z001, Z002, Z005 (occupied zones)
  Reduction: 40% dimming
  Validation: Confirms zones dimmable, occupancy noted
  Power Saved: 5.1 kW (1% of building demand)

14:20 - Action 2: Adjust Z003 Setpoint
  Zone: Z003 (Common areas, lower priority)
  Change: 22°C → 24°C (2°C increase, reduces cooling)
  Validation: Allows +2°C for low-priority common area
  Power Saved: 8 kW (1.6% of building demand)
  Side Effect: Slightly warmer hallways (acceptable)

14:30 - Action 3: Reduce Server Room Cooling
  Zone: Z004 (Server room)
  Change: 20°C → 22°C (conservative, within range)
  Validation: Maintains 15-25°C critical range
  Power Saved: 3 kW (0.6% of building demand)
  Risk: Monitored closely, will revert if temp climbs

Result After 30 Minutes:
  Building Demand: 434 kW (before) → 418 kW (after)
  Reduction: 16 kW (3.7%) - Close to 15% target
  Comfort Impact: Minimal (noted but acceptable)
  Duration: Event runs 14:00-18:00 (4 hours)

18:00 - Event ends, all actions automatically reverse
  Recovery: All setpoints and lighting restored
  Timeline: Gradual recovery over 30 minutes (comfort)
```

**Expected Outcomes**:
- Multiple concurrent actions validated and coordinated
- Demand reduction achieved without critical zone overload
- Comfort monitoring and recovery demonstrated
- Side effects cascaded (e.g., lighting reduction + HVAC adjustment)

---

## 7. API Request Examples

### 7.1 Adjust Zone Setpoint - Request Format

```json
{
  "actionId": "act-123456",
  "actionType": "inference",
  "parameters": [
    {
      "name": "action_type",
      "value": "adjust_zone_setpoint",
      "type": "string"
    },
    {
      "name": "zone_id",
      "value": "Z001",
      "type": "string"
    },
    {
      "name": "new_setpoint",
      "value": 21.5,
      "type": "number"
    },
    {
      "name": "duration",
      "value": "TIMED",
      "type": "string"
    },
    {
      "name": "duration_minutes",
      "value": 120,
      "type": "integer"
    },
    {
      "name": "reason",
      "value": "comfort_adjustment",
      "type": "string"
    }
  ],
  "context": {
    "building_id": "DemoB-001",
    "initiated_by": "demo_user",
    "timestamp": "2024-11-20T09:30:00Z"
  }
}
```

### 7.2 Load Shed Request Format

```json
{
  "actionId": "act-loadshed-001",
  "actionType": "inference",
  "parameters": [
    {
      "name": "action_type",
      "value": "load_shed_reduce_lighting",
      "type": "string"
    },
    {
      "name": "target_zones",
      "value": ["Z001", "Z002", "Z005"],
      "type": "array"
    },
    {
      "name": "reduction_percentage",
      "value": 40,
      "type": "integer"
    },
    {
      "name": "duration_minutes",
      "value": 120,
      "type": "integer"
    },
    {
      "name": "priority",
      "value": "HIGH",
      "type": "string"
    },
    {
      "name": "reason",
      "value": "peak_demand",
      "type": "string"
    }
  ],
  "context": {
    "building_id": "DemoB-001",
    "demand_current": 450,
    "demand_limit": 500
  }
}
```

---

## 8. Validation Rule Framework

### 8.1 Validation Rule Structure

```typescript
interface ValidationRule {
  ruleId: string;                      // Unique ID (e.g., V1_ZoneExists)
  category: 'CRITICAL' | 'WARNING' | 'INFO';

  // Rule definition
  description: string;
  condition: string;                   // Logic expression

  // Execution
  check: (action: KBEAction, context: BuildingContext) => ValidationResult;

  // Response handling
  onFail: 'REJECT' | 'WARN' | 'LOG';
  errorMessage: string;
  suggestion?: string;                 // How to fix
}

interface ValidationResult {
  ruleId: string;
  passed: boolean;
  message: string;
  severity: 'CRITICAL' | 'WARNING' | 'INFO';
  details?: Record<string, any>;
}
```

### 8.2 Validation Execution Pipeline

```
User Request
    ↓
┌───────────────────────────────┐
│  Parse & Validate Syntax      │ (JSON schema, required fields)
└───────────────────────────────┘
    ↓
┌───────────────────────────────┐
│  Apply Business Rules         │ (Zone exists, setpoint in range, etc.)
│  CRITICAL rules → REJECT      │
│  WARNING rules → WARN         │
│  INFO rules → LOG             │
└───────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Run Side Effect Predictions        │ (Calculate expected power, etc.)
│  Estimate impact on demand          │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Return Validation Results          │
│  With predictions & side effects    │
└─────────────────────────────────────┘
    ↓
User Decision → Execute / Cancel
```

---

## 9. Summary of KBE Capabilities Demonstrated

| Capability | Action | Demo Aspect |
|------------|--------|-------------|
| **Constraint Checking** | All actions | Validation rules ensure safety |
| **Occupancy Awareness** | Setpoint Adjustment | Don't change temp below comfort if occupied |
| **Thermal Dynamics** | Pre-Cooling | Respect ramp rates, use thermal mass |
| **Demand Management** | Load Shed | Reduce lighting, shift HVAC load |
| **Scheduling** | Zone Setpoint | Time-based and occupancy-based control |
| **Side Effect Modeling** | All actions | Track HVAC mode changes, power impact |
| **Multi-zone Coordination** | Load Shed | Apply action to multiple zones safely |
| **Recovery & Reversibility** | All TIMED actions | Automatic return to schedule |
| **Real-time Monitoring** | All actions | Track execution, validate outcomes |

---

## 10. Glossary

| Term | Definition |
|------|-----------|
| **Zone** | A thermal space with independent control (e.g., office floor) |
| **Setpoint** | Target temperature for a zone (comfort goal) |
| **Thermal Mass** | Building capacity to store heat/cold (High = slow change) |
| **Ramp Rate** | Maximum temperature change per hour (°C/hr) |
| **HVAC** | Heating, Ventilation, and Air Conditioning system |
| **Demand Response** | Reducing power consumption during peak periods |
| **Load Shedding** | Intentional reduction of electrical load |
| **Pre-Cooling** | Lowering temperature during off-peak to reduce peak demand |
| **Side Effect** | Secondary impact of an action (e.g., power draw change) |
| **Validation Rule** | Constraint checking to ensure action safety |
| **KBE** | Knowledge-Based Engineering (reasoning with domain models) |

---

**Document Version**: 1.0
**Last Updated**: 2024-11-20
**Status**: PoC Design (Ready for Implementation)
