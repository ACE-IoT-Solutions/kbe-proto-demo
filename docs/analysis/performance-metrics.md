# Performance Metrics and Monitoring

## Key Performance Indicators (KPIs)

### 1. Energy Efficiency Metrics

#### Zone-Level Metrics
- **Energy Use Intensity (EUI)**: kWh/m²/year
- **HVAC Efficiency**: COP (Coefficient of Performance)
- **Lighting Efficiency**: W/m² per lux level
- **Demand Factor**: Peak load / Total connected load
- **Load Factor**: Average load / Peak load

#### Building-Level Metrics
- **Total Energy Consumption**: kWh
- **Peak Demand**: kW
- **Demand Reduction**: % reduction during DR events
- **Energy Cost**: $ per kWh
- **Carbon Intensity**: kg CO₂ per kWh

### 2. Comfort Metrics

#### Temperature Performance
- **Setpoint Accuracy**: Actual temp vs target temp
- **Comfort Hours**: % of time within comfort range
- **Overshoot/Undershoot**: Max deviation from setpoint
- **Ramp Rate**: °C per hour
- **Recovery Time**: Minutes to return to comfort

#### Air Quality
- **CO₂ Levels**: ppm
- **Humidity**: Relative humidity %
- **Air Changes per Hour (ACH)**: Ventilation rate
- **Particulate Matter**: PM2.5, PM10 levels

### 3. Operational Metrics

#### Schedule Adherence
- **Schedule Compliance**: % of time following schedule
- **Override Frequency**: Number of manual overrides
- **Pre-Conditioning Success**: % of times zone ready before occupancy
- **Setback Achievement**: % of unoccupied periods in setback mode

#### System Reliability
- **Uptime**: % of time systems operational
- **Response Time**: Seconds from command to action
- **Sensor Accuracy**: % deviation from calibration
- **Communication Errors**: Failed messages per day

### 4. Demand Response Metrics

#### DR Performance
- **Event Participation**: % of DR events participated
- **Load Reduction**: kW reduced during events
- **Recovery Duration**: Minutes to restore normal operation
- **Comfort Impact**: % deviation from normal comfort during DR
- **Financial Benefit**: $ saved through DR participation

#### Load Flexibility
- **Sheddable Capacity**: kW available for shedding
- **Shiftable Load**: kWh that can be time-shifted
- **Flexibility Duration**: Maximum curtailment time (minutes)
- **Rebound Peak**: kW spike after DR event

### 5. Cost Metrics

#### Financial Performance
- **Energy Cost**: Total $ spent on energy
- **Demand Charges**: $ from peak demand
- **Time-of-Use Savings**: $ saved through load shifting
- **DR Incentives**: $ earned from DR programs
- **Cost Avoidance**: $ saved vs baseline

#### Return on Investment
- **Payback Period**: Years to recover investment
- **Annual Savings**: $ saved per year
- **ROI**: % return on investment
- **Cost per Comfort Hour**: $ per hour of comfortable conditions

## Monitoring Framework

### Real-Time Monitoring
```typescript
interface RealTimeMetrics {
  timestamp: Date;

  // Instantaneous values
  current: {
    totalDemand: number;        // kW
    zoneLoads: Map<string, number>; // Per-zone consumption
    temperatures: Map<string, number>; // Per-zone temperature
    occupancy: Map<string, boolean>; // Per-zone occupancy
  };

  // Rolling averages
  averages: {
    last15min: number;
    lastHour: number;
    today: number;
  };

  // Status indicators
  status: {
    demandStatus: 'NORMAL' | 'WARNING' | 'CRITICAL';
    comfortStatus: 'COMFORTABLE' | 'MARGINAL' | 'UNCOMFORTABLE';
    systemHealth: 'HEALTHY' | 'DEGRADED' | 'FAULT';
  };

  // Alarms
  activeAlarms: Alarm[];
}
```

### Historical Analytics
```typescript
interface HistoricalAnalytics {
  period: {
    start: Date;
    end: Date;
  };

  // Aggregated metrics
  energy: {
    total: number;              // kWh
    byZone: Map<string, number>;
    byTimeOfDay: number[];      // Hourly array
    byDayOfWeek: number[];      // Daily array
  };

  // Statistical analysis
  statistics: {
    mean: number;
    median: number;
    stdDev: number;
    min: number;
    max: number;
    percentile95: number;
  };

  // Trends
  trends: {
    dailyProfile: number[];     // Typical daily pattern
    weeklyPattern: number[];    // Typical weekly pattern
    seasonalVariation: number[]; // Monthly variation
  };

  // Benchmarking
  benchmarks: {
    vsHistorical: number;       // % change vs historical average
    vsBudget: number;          // % vs energy budget
    vsPeers: number;           // % vs similar buildings
  };
}
```

### Alert Thresholds
```typescript
interface AlertConfiguration {
  // Energy alerts
  energyAlerts: {
    demandExceeded: number;     // kW threshold
    budgetExceeded: number;     // $ threshold
    anomalyDetection: boolean;  // Enable ML-based anomaly detection
  };

  // Comfort alerts
  comfortAlerts: {
    tempDeviation: number;      // °C from setpoint
    co2Level: number;          // ppm threshold
    humidityRange: [number, number]; // Min/max RH%
  };

  // System alerts
  systemAlerts: {
    sensorOffline: number;      // Minutes before alert
    communicationFailure: number; // Failed messages threshold
    scheduleDeviation: number;  // Minutes of non-compliance
  };

  // Notification settings
  notifications: {
    email: string[];
    sms: string[];
    webhook: string;
    severity: 'INFO' | 'WARNING' | 'CRITICAL';
  };
}
```

## Data Collection Strategy

### Sampling Rates
- **Real-time data**: Every 1-5 seconds (temperature, power, occupancy)
- **Trend data**: Every 15 minutes (aggregated metrics)
- **Historical data**: Hourly/daily summaries
- **Analytics**: Daily/weekly/monthly reports

### Data Retention
- **Raw data**: 7 days
- **15-minute intervals**: 90 days
- **Hourly data**: 2 years
- **Daily summaries**: 10 years

### Data Quality
- **Validation**: Range checking, rate-of-change limits
- **Cleaning**: Outlier detection and removal
- **Interpolation**: Filling gaps in time series
- **Calibration**: Regular sensor validation

## Dashboard Requirements

### Operator Dashboard
- Current demand vs limit (gauge)
- Zone temperature status (heat map)
- Active alarms and warnings
- Quick controls for DR events
- Schedule override interface

### Analytics Dashboard
- Energy consumption trends
- Cost analysis and projections
- Demand response performance
- Comfort metrics summary
- Benchmark comparisons

### Executive Dashboard
- Monthly energy costs
- Year-over-year comparisons
- Sustainability metrics
- DR revenue/savings
- ROI on efficiency investments
