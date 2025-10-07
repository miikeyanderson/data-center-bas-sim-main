# Fault Simulation & Diagnostics

## Fault Simulation

### Fault Types
- **Sensor Faults**: Drift, bias, noise, stuck sensors, calibration errors
- **Actuator Faults**: Stiction, backlash, oscillation, partial failure
- **Control Faults**: Short-cycling, instability, communication dropouts
- **Equipment Faults**: Performance degradation, efficiency loss, component wear

### Diagnostic Engine
- **Real-time Fault Detection**: Statistical analysis with confidence levels
- **Root Cause Analysis**: Expert system with symptom-cause mapping
- **Performance Impact**: Quantified effect on system operations
- **Predictive Maintenance**: Early warning indicators and recommendations

### Execution Commands

```bash
# Run fault simulation (15 minutes)
python demo_fault_simulation.py --duration 15

# Run fault scenario testing
python demo_fault_simulation.py --config config/scenarios/fault_demo.yaml

# Diagnostic reports created automatically
# View results in: reports/fault_demo/
```

## Fault Simulation Features

| Fault Type | Examples | Detection Method | Response |
|------------|----------|------------------|----------|
| **Sensor** | Drift, Bias, Stuck | Statistical deviation analysis | Calibration recommendations |
| **Actuator** | Stiction, Backlash | Position error tracking | Mechanical maintenance alerts |
| **Control** | Short-cycling, Instability | Pattern recognition | Tuning parameter adjustments |
| **Equipment** | Degradation, Leaks | Performance trending | Preventive maintenance scheduling |

## Diagnostic Reports

**Created automatically during fault events:**
- **Summary**: High-level system health status
- **Technical Analysis**: Fault isolation and root cause
- **Maintenance Recommendations**: Specific actions with priorities
- **Performance Impact**: Quantified effects on efficiency and reliability

```
reports/fault_demo/
├── fault_demo_fault_report_20241207_143022.md     ← Fault analysis
├── fault_demo_health_report_20241207_143045.md    ← System health assessment  
├── fault_demo_maintenance_report_20241207_143055.md ← Maintenance planning
├── telemetry_data.json                            ← System data
└── fault_events.json                              ← Fault injection timeline
```

## Engineering Applications

**BAS diagnostic capabilities:**
- **Troubleshooting**: Fault isolation using statistical analysis and pattern recognition
- **Diagnostics**: Real-time fault detection with root cause analysis
- **Predictive Maintenance**: Cost-effective maintenance scheduling with performance trending
- **Documentation**: Management-ready reports with impact analysis

## System Resilience & Error Handling

**System Resilience**: Fault detection and recovery handle critical failure scenarios:

**No CRAC Available**: System activates emergency protocols with high-priority alarms, maintains cooling through available units, and provides operator guidance for manual intervention.

**Sensor Fault Handling**: Drift detection through statistical analysis, bias correction, stuck sensor identification, and sensor validation with confidence intervals.

**Actuator Fault Management**: Stiction detection through position feedback analysis, backlash compensation, oscillation damping, and partial failure handling with reduced capacity.

**Communication Dropout Recovery**: Timeout handling with retry logic, fallback to local control modes, alarm escalation for extended outages, and manual override.

**Sample Operator Log**:
```
2024-12-07 14:32:15 [WARN] CRAC-01: Temperature sensor drift detected (0.8°C bias)
2024-12-07 14:32:45 [INFO] SENSOR_DRIFT: Bias correction applied automatically
2024-12-07 14:35:22 [CRIT] CRAC-01: Unit failure - no cooling output after 60s command
2024-12-07 14:35:23 [INFO] STAGING: STANDBY unit promoted to LAG role
2024-12-07 14:35:45 [INFO] RECOVERY: Temperature stabilized at 22.3°C
```