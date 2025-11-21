# Test Scenarios for Building Model Validation

## 1. Zone Control Test Scenarios

### TC-01: Basic Zone Temperature Control
**Objective**: Verify zone maintains target temperature during occupied hours

**Setup**:
- Zone: Office (100 m²)
- Schedule: 8 AM - 5 PM occupied
- Target temperature: 22°C
- Outdoor temperature: 30°C

**Test Steps**:
1. Start simulation at 7:30 AM
2. Monitor pre-conditioning (should start by 7:30 AM)
3. Verify temperature reaches 22°C by 8:00 AM
4. Monitor temperature during occupied hours (8 AM - 5 PM)
5. Verify setback occurs after 5:00 PM

**Expected Results**:
- Temperature within ±1°C of setpoint during occupied hours
- Pre-conditioning completes before occupancy
- Energy consumption reduces during unoccupied period

**Pass Criteria**:
- 95% of time within comfort range during occupancy
- Pre-conditioning success rate: 100%
- Setback activation within 30 minutes of schedule

---

### TC-02: Multi-Zone Coordination
**Objective**: Verify multiple zones operate independently without interference

**Setup**:
- 4 zones: Office A, Office B, Conference Room, Common Area
- Different schedules and setpoints per zone
- Shared HVAC system

**Test Steps**:
1. Configure different schedules for each zone
2. Set different temperature setpoints
3. Run 24-hour simulation
4. Monitor each zone independently
5. Verify no cross-zone interference

**Expected Results**:
- Each zone maintains its own setpoint
- Schedule adherence per zone: >95%
- No thermal coupling between zones

**Pass Criteria**:
- Independent control verified for all zones
- No schedule conflicts
- Each zone within comfort range during occupied hours

---

## 2. Scheduling Test Scenarios

### TC-03: Schedule Override
**Objective**: Verify manual override functionality and automatic return to schedule

**Setup**:
- Zone: Conference Room
- Normal schedule: Unoccupied
- Manual override: Occupied mode, 21°C

**Test Steps**:
1. Start during unoccupied period (setback mode)
2. Activate manual override to occupied mode
3. Monitor temperature response
4. Wait for override timeout (2 hours)
5. Verify automatic return to schedule

**Expected Results**:
- Immediate response to override command
- Temperature reaches setpoint within 30 minutes
- Automatic return to scheduled mode after timeout

**Pass Criteria**:
- Override activation time: <1 minute
- Temperature target achieved: <30 minutes
- Schedule resumption: 100% success rate

---

### TC-04: Holiday Schedule
**Objective**: Verify holiday schedule overrides normal weekly schedule

**Setup**:
- All zones: Normal weekday schedule
- Exception: National holiday (unoccupied all day)

**Test Steps**:
1. Configure holiday exception
2. Run simulation on holiday date
3. Verify unoccupied mode all day
4. Verify normal schedule resumes next day

**Expected Results**:
- Holiday schedule takes precedence
- All zones in setback mode during holiday
- Normal operation resumes automatically

**Pass Criteria**:
- Exception activation: 100%
- Energy savings vs normal day: >40%
- Automatic schedule resumption: 100%

---

## 3. Demand Management Test Scenarios

### TC-05: Demand Limit Compliance
**Objective**: Verify building stays within demand limit

**Setup**:
- Building demand limit: 500 kW
- Warning threshold: 400 kW
- 4 zones at full load: 480 kW

**Test Steps**:
1. All zones operating normally
2. Simulate additional load bringing total to 520 kW
3. Monitor demand management response
4. Verify load shedding activates
5. Confirm demand stays below limit

**Expected Results**:
- Warning trigger at 400 kW
- Load shedding activates before 500 kW
- Demand maintained below limit
- Low-priority zones shed first

**Pass Criteria**:
- Demand limit never exceeded
- Response time: <2 minutes
- Load shedding sequence correct (priority-based)

---

### TC-06: Demand Response Event
**Objective**: Verify participation in utility demand response event

**Setup**:
- DR event: 2-6 PM, 20% reduction requested
- Baseline load: 450 kW
- Target: 360 kW

**Test Steps**:
1. Receive DR event notification (15 min advance)
2. Monitor system response
3. Verify load reduction strategies deployed
4. Monitor comfort impact
5. Verify recovery after event

**Expected Results**:
- Load reduction: ≥20% (90 kW)
- Comfort degradation: <10%
- Full recovery within 1 hour after event

**Pass Criteria**:
- Target load reduction achieved: ≥90%
- Temperature deviation during event: <2°C
- Recovery time: <60 minutes

---

## 4. Sensor and Data Quality Scenarios

### TC-07: Sensor Failure Handling
**Objective**: Verify graceful degradation when sensors fail

**Setup**:
- Zone with multiple temperature sensors
- Simulate sensor failure

**Test Steps**:
1. Normal operation with all sensors
2. Simulate temperature sensor failure
3. Monitor control system response
4. Verify fallback to remaining sensors
5. Test alarm generation

**Expected Results**:
- Automatic failover to backup sensors
- Continued operation with degraded accuracy
- Alarm notification sent
- No loss of control

**Pass Criteria**:
- Failover time: <30 seconds
- Continued control: 100%
- Alarm generated: 100%
- Control accuracy with backup: ±2°C

---

### TC-08: Data Gap Handling
**Objective**: Verify system handles data communication interruptions

**Setup**:
- Normal operation
- Simulate 5-minute communication loss

**Test Steps**:
1. Normal data collection
2. Simulate network interruption
3. Monitor local control continuation
4. Restore communications
5. Verify data synchronization

**Expected Results**:
- Local control maintains operation
- No alarms during expected interruption
- Data backfill after restoration
- No control gaps

**Pass Criteria**:
- Continuous control during outage: 100%
- Data recovery: 100%
- Synchronization time: <2 minutes

---

## 5. Energy Optimization Scenarios

### TC-09: Pre-Cooling Strategy
**Objective**: Verify pre-cooling reduces peak demand

**Setup**:
- Summer day, peak rates 2-6 PM
- Pre-cool period: 10 AM - 2 PM
- Zone thermal mass: High

**Test Steps**:
1. Execute pre-cooling strategy
2. Reduce setpoint to 20°C during pre-cool
3. Increase setpoint to 24°C during peak period
4. Monitor temperature drift
5. Calculate demand reduction

**Expected Results**:
- Temperature maintained in comfort range
- Peak demand reduced by 15-25%
- Energy cost savings achieved

**Pass Criteria**:
- Comfort maintained: >90% of peak period
- Demand reduction: ≥15%
- Cost savings: >10% vs baseline

---

### TC-10: Optimal Start/Stop
**Objective**: Verify optimal start time minimizes energy while ensuring comfort

**Setup**:
- Office zone, occupancy at 8 AM
- Variable outdoor conditions
- Learning algorithm for start time

**Test Steps**:
1. Run multiple simulations with different outdoor temps
2. Monitor pre-conditioning start times
3. Verify comfort at occupancy time
4. Calculate energy consumption
5. Compare to fixed start time

**Expected Results**:
- Adaptive start time based on conditions
- Comfort achieved at occupancy: 100%
- Energy savings vs fixed start: 10-20%

**Pass Criteria**:
- Temperature at occupancy: 22°C ±0.5°C
- Start time variation: 15-60 minutes
- Energy savings: ≥10%

---

## 6. Integration Test Scenarios

### TC-11: Full Day Simulation
**Objective**: Verify complete system operation over 24-hour period

**Setup**:
- All 4 zones configured
- Realistic schedules and occupancy patterns
- Variable weather conditions
- DR event at 3 PM

**Test Steps**:
1. Run 24-hour simulation
2. Monitor all zones continuously
3. Execute scheduled changes
4. Respond to DR event
5. Collect performance metrics

**Expected Results**:
- All zones maintain comfort during occupancy
- Schedules followed accurately
- DR participation successful
- Energy consumption within budget

**Pass Criteria**:
- Schedule adherence: >95%
- Comfort hours: >95%
- DR load reduction: ≥20%
- Total energy: Within 10% of prediction

---

### TC-12: Week-Long Performance
**Objective**: Validate system performance over full week including weekend

**Setup**:
- Weekday and weekend schedules
- Varying occupancy patterns
- Multiple DR events
- Weather variation

**Test Steps**:
1. Run 7-day simulation
2. Monitor weekly patterns
3. Verify weekend setback
4. Calculate weekly metrics
5. Generate performance report

**Expected Results**:
- Consistent performance throughout week
- Appropriate weekend energy reduction
- All DR events successful
- Predictable energy patterns

**Pass Criteria**:
- Daily schedule compliance: >95%
- Weekend energy reduction: >50% vs weekday
- Weekly energy within budget: ±5%
- All DR events successful: 100%

---

## Test Execution Framework

### Automated Testing
```typescript
interface TestCase {
  id: string;
  name: string;
  category: 'ZONE_CONTROL' | 'SCHEDULING' | 'DEMAND_MGMT' | 'SENSORS' | 'OPTIMIZATION' | 'INTEGRATION';
  priority: 'P0' | 'P1' | 'P2';

  setup: {
    zones: ZoneConfiguration[];
    schedules: Schedule[];
    weather: WeatherProfile;
    duration: number;  // Simulation duration in hours
  };

  steps: TestStep[];
  assertions: Assertion[];
  metrics: MetricThreshold[];
}

interface Assertion {
  metric: string;
  condition: '>' | '<' | '==' | '>=' | '<=';
  threshold: number;
  tolerancePercent: number;
}
```

### Continuous Validation
- Run regression tests on every code change
- Performance benchmarking on weekly basis
- Long-term stability tests (monthly)
- Comparison against real building data (if available)

### Test Coverage Requirements
- Unit tests: >90% code coverage
- Integration tests: All component interfaces
- System tests: All critical user scenarios
- Performance tests: All optimization algorithms
