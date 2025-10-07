# Testing & Validation

## Test Suite

**Test Suite**: Validates control algorithms, thermal modeling, and fault detection systems:

### Unit Tests
- **PID Controller**: Step response validation, anti-windup verification, tuning parameter analysis
- **CRAC Sequencer**: Lead/lag staging logic, role rotation, failure detection and recovery  
- **Alarm System**: Debounce timing validation, priority classification, acknowledgment
- **Thermal Model**: Heat balance accuracy, thermal mass response, steady-state

### Validation Against RC Model
Thermal simulation compared to RC circuit model with ±2.1% RMSE accuracy:
```
Thermal RC Model Validation Results:
- Step Response RMSE: 0.47°C (2.1% of range)  
- Settling Time Error: <5% vs prediction
- Steady-State Accuracy: ±0.1°C vs calculated values
- Thermal Mass Response: R² = 0.998 correlation
```

### Test Execution

```bash
# Run unit test suite
python test_fault_simulation.py

# Validate thermal model  
python validate_thermal_model.py --duration 30

# Control loop step testing
python validate_control_response.py --step-size 5.0
```

## Test Scenarios

**Baseline Scenario** (`baseline`):
- 60-minute steady-state test
- Temperature control verification
- Single CRAC operation test

**Rising Load Scenario** (`rising_load`):
- IT load ramp from 35kW to 70kW over 10 minutes
- Validates LAG staging response timing
- Ensures no high temperature alarms

**Equipment Failure Scenario** (`crac_failure`):
- LEAD CRAC failure at t=5 minutes
- Tests role promotion
- Tests redundancy activation

## Analysis Execution

```bash
# Install analysis dependencies
pip install pandas matplotlib seaborn

# Run analysis workflow
python main.py run --config config/default.yaml --duration 10
python analyze.py --csv logs/datacenter_telemetry_*.csv --name baseline

# Multi-scenario comparison analysis  
python analyze.py --compare logs/baseline.csv logs/rising_load.csv logs/crac_failure.csv

# Report generation
./scripts/generate_analysis.sh baseline 15
```

## Generated Analysis Outputs
```
reports/
├── baseline_summary.md         ← Summary with KPIs
├── baseline_kpis.json         ← Structured metrics for integration
├── pid_performance.png        ← Control loop stability analysis
├── equipment_runtime.png      ← Staging and redundancy testing  
├── energy_performance.png     ← Efficiency trends and COP analysis
└── system_overview.png        ← Dashboard view
```

## Development Approach

This project implements BAS engineering practices:

- **Config-Driven Architecture**: Separation of system parameters from implementation
- **Schema Validation**: Config management with error checking
- **CLI Interface**: Command-line tools for operation and integration
- **Modular Design**: Separate concerns for maintainability and testing
- **Industry Standards**: Follows established BAS control sequences and practices  
- **Testing Framework**: Validation ensures reliable commissioning
- **Documentation**: Technical documentation for operations handover
- **Version Control**: Git workflow with commit standards for change management