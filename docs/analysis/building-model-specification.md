# Building Model Specification
## Simple Building with Zones - Requirements Analysis

### 1. Zone Definition

A **zone** in this building model context represents a discrete, controllable space with:
- **Thermal characteristics**: Separate temperature control and monitoring
- **Occupancy patterns**: Distinct usage schedules and occupancy sensors
- **Energy consumption**: Independent HVAC and lighting loads
- **Spatial boundaries**: Physical separation allowing independent environmental control

### 2. Zone Data Structure Requirements

#### Core Zone Properties
```typescript
interface Zone {
  // Identity
  id: string;                    // Unique zone identifier
  name: string;                  // Human-readable name
  type: ZoneType;               // OFFICE | CONFERENCE | COMMON | MECHANICAL

  // Physical Properties
  area: number;                 // Square meters
  volume: number;               // Cubic meters
  floor: number;                // Floor level
  orientation: Compass;         // N, S, E, W, NE, NW, SE, SW

  // Thermal Properties
  currentTemp: number;          // Current temperature (Celsius)
  targetTemp: number;           // Setpoint temperature (Celsius)
  tempRange: {
    min: number;                // Minimum allowable temperature
    max: number;                // Maximum allowable temperature
    comfortMin: number;         // Comfort range minimum
    comfortMax: number;         // Comfort range maximum
  };

  // Occupancy
  occupancy: {
    current: number;            // Current occupant count
    capacity: number;           // Maximum capacity
    isOccupied: boolean;        // Occupancy status
    lastMotion: Date;           // Last motion detection
  };

  // Energy Systems
  hvac: {
    equipmentId: string;        // Reference to HVAC equipment
    mode: 'HEATING' | 'COOLING' | 'VENTILATION' | 'OFF';
    fanSpeed: number;           // 0-100%
    damperPosition: number;     // 0-100%
    powerConsumption: number;   // Watts
  };

  lighting: {
    isOn: boolean;
    brightness: number;         // 0-100%
    powerConsumption: number;   // Watts
  };

  // Scheduling
  schedule: ZoneSchedule;

  // Demand Management
  demandProfile: DemandProfile;

  // Sensors
  sensors: {
    temperature: SensorReading[];
    humidity: SensorReading[];
    co2: SensorReading[];
    motion: SensorReading[];
  };

  // Metadata
  metadata: {
    createdAt: Date;
    updatedAt: Date;
    tags: string[];
    notes: string;
  };
}
```

### 3. Scheduling Parameters and Constraints

#### Zone Schedule Structure
```typescript
interface ZoneSchedule {
  id: string;
  zoneId: string;
  scheduleType: 'OCCUPANCY' | 'TEMPERATURE' | 'DEMAND_RESPONSE';

  // Weekly Schedule
  weekly: {
    monday: DaySchedule;
    tuesday: DaySchedule;
    wednesday: DaySchedule;
    thursday: DaySchedule;
    friday: DaySchedule;
    saturday: DaySchedule;
    sunday: DaySchedule;
  };

  // Special Events/Overrides
  exceptions: ScheduleException[];

  // Holiday Calendar
  holidays: HolidaySchedule[];

  // Constraints
  constraints: {
    minOccupiedTemp: number;      // Minimum temp when occupied
    maxOccupiedTemp: number;      // Maximum temp when occupied
    unoccupiedSetback: number;    // Setback offset for unoccupied
    maxRampRate: number;          // Max temp change per hour
    preOccupancyTime: number;     // Minutes before occupancy to start conditioning
    postOccupancyTime: number;    // Minutes after occupancy to maintain comfort
  };
}

interface DaySchedule {
  periods: SchedulePeriod[];
}

interface SchedulePeriod {
  startTime: string;              // HH:MM format
  endTime: string;                // HH:MM format
  occupancyMode: 'OCCUPIED' | 'UNOCCUPIED' | 'STANDBY';
  targetTemp: number;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
}

interface ScheduleException {
  date: Date;
  reason: string;
  overrideSchedule: DaySchedule;
}
```

#### Scheduling Rules
1. **Occupancy-Based**:
   - Occupied periods: Full comfort conditions
   - Unoccupied periods: Setback temperature (±5°C typical)
   - Transition periods: Gradual ramping

2. **Time-Based Constraints**:
   - Pre-occupancy conditioning (30-60 minutes before occupancy)
   - Post-occupancy setback delay (15-30 minutes after last occupancy)
   - Maximum temperature ramp rate (2-3°C per hour)

3. **Priority Levels**:
   - HIGH: Critical spaces (server rooms, laboratories)
   - MEDIUM: Normal occupied spaces (offices, conference rooms)
   - LOW: Intermittent spaces (storage, corridors)

### 4. Demand Management Criteria

#### Demand Profile
```typescript
interface DemandProfile {
  zoneId: string;

  // Load Characteristics
  baseLoad: number;              // Baseline power consumption (W)
  peakLoad: number;              // Maximum power consumption (W)
  averageLoad: number;           // Average power consumption (W)

  // Flexibility
  flexibility: {
    sheddable: boolean;          // Can reduce/shed load
    shiftable: boolean;          // Can shift load in time
    maxReduction: number;        // Maximum load reduction (%)
    duration: number;            // Maximum curtailment duration (minutes)
    recoveryTime: number;        // Time to return to normal (minutes)
  };

  // Demand Response Participation
  drParticipation: {
    enrolled: boolean;
    programs: string[];          // DR program IDs
    tier: 'CRITICAL' | 'STANDARD' | 'OPTIONAL';
  };

  // Thresholds
  thresholds: {
    demandLimit: number;         // Maximum demand (kW)
    warningLevel: number;        // Warning threshold (kW)
    criticalLevel: number;       // Critical threshold (kW)
  };

  // Historical Data
  consumption: {
    last15min: number;
    lastHour: number;
    lastDay: number;
    lastWeek: number;
  };
}
```

#### Demand Management Thresholds
1. **Building-Level Thresholds**:
   - Total building demand limit (e.g., 500 kW)
   - Warning level (80% of limit = 400 kW)
   - Critical level (95% of limit = 475 kW)

2. **Zone-Level Thresholds**:
   - Individual zone demand limits (based on zone size/type)
   - Proportional allocation of building capacity
   - Dynamic reallocation based on priority

3. **Time-Based Thresholds**:
   - Peak demand periods (utility rate-based)
   - Off-peak periods (reduced restrictions)
   - Real-time pricing triggers

#### Demand Response Strategies
1. **Load Shedding**:
   - Temperature setpoint adjustment (±2°C)
   - Lighting reduction (dimming to 70%)
   - Non-critical equipment shutdown

2. **Load Shifting**:
   - Pre-cooling before peak periods
   - Deferred conditioning in low-priority zones
   - Battery storage utilization (if available)

3. **Priority-Based Control**:
   - Critical zones: Maintain full comfort
   - Standard zones: Minor setpoint adjustments
   - Optional zones: Aggressive curtailment allowed

### 5. Data Flow Between Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Building Controller                      │
│  - Central coordination                                      │
│  - Demand aggregation                                        │
│  - Schedule management                                       │
└─────────────────┬───────────────────────────────────────────┘
                  │
      ┌───────────┴───────────┬──────────────┬─────────────┐
      │                       │              │             │
┌─────▼─────┐         ┌──────▼──────┐ ┌────▼─────┐ ┌────▼─────┐
│  Zone A   │         │   Zone B    │ │  Zone C  │ │  Zone D  │
│ (Office)  │         │ (Conference)│ │ (Common) │ │(Mechanical)│
└─────┬─────┘         └──────┬──────┘ └────┬─────┘ └────┬─────┘
      │                      │              │             │
      └──────────────────────┴──────────────┴─────────────┘
                             │
                    ┌────────▼────────┐
                    │  Sensor Network │
                    │  - Temperature  │
                    │  - Occupancy    │
                    │  - Power        │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Data Store    │
                    │  - Time series  │
                    │  - Events       │
                    │  - Analytics    │
                    └─────────────────┘
```

#### Component Communication
1. **Sensor → Zone**: Real-time sensor readings (temperature, occupancy, power)
2. **Zone → Controller**: Status updates, demand requests, alerts
3. **Controller → Zone**: Setpoint commands, mode changes, DR events
4. **Zone → Data Store**: Historical data logging, event recording
5. **External → Controller**: Utility signals, weather data, pricing

