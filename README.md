# Data Center BAS Control System

A professional Building Automation System (BAS) simulation platform for data center cooling systems. This project demonstrates real-world control strategies, alarm management, and commissioning workflows used in mission-critical facilities.

## Overview

This system simulates a typical data center cooling plant with multiple CRAC units, implementing industry-standard control sequences and monitoring capabilities. Built with Python, it provides a complete **config-driven simulation platform** for testing, validation, and operator training.

**Key Features:**
- **Professional CLI Interface**: Configuration-driven with scenarios and parameter overrides
- **YAML Configuration Management**: Schema-validated configs with deep-merge override system
- Multi-CRAC lead/lag/standby staging with automatic failover
- Professional PID temperature control with anti-windup protection  
- Comprehensive alarm management system with priority handling
- Real-time monitoring dashboard with Node-RED HMI
- Automated scenario testing for commissioning validation
- CSV data historian for trending and analysis

## Architecture

### System Overview

```mermaid
flowchart LR
  subgraph Room["Room Thermal Model"]
    IT[IT Load 35–70 kW] --> HeatBalance[Heat Balance]
    HeatBalance --> T[Space Temperature]
  end

  subgraph Control["Control System"]
    PID[PID Controller<br/>anti-windup]
    Seq[Sequencer<br/>lead/lag/standby]
    AM[Alarm Manager]
  end

  subgraph CRACs["CRAC Units (3×50 kW)"]
    L[CRAC-01: LEAD]
    G[CRAC-02: LAG] 
    S[CRAC-03: STANDBY]
  end

  subgraph Monitoring["Monitoring & Data"]
    NR[Node-RED HMI]
    CSV[CSV Historian]
    CFG[Config Platform]
  end

  T --> PID --> Seq --> L
  Seq --> G
  Seq --> S
  L -->|Cooling| T
  G -->|Cooling| T
  S -->|Failover| T
  PID --> AM
  AM --> NR
  T --> CSV
  L --> CSV
  G --> CSV
  S --> CSV
  CFG --> Control
```

*This architecture demonstrates modular design with clear separation of concerns, enabling independent testing of thermal dynamics, control algorithms, and monitoring systems.*

## Quick Start

**Requirements:** Python 3.8+, Node.js (for HMI)

```bash
# Clone and setup
git clone https://github.com/miikeyanderson/data-center-bas-sim-main.git
cd data-center-bas-sim-main
pip install -r requirements.txt

# Install config dependencies
pip install pyyaml jsonschema

# Validate configuration
python main.py validate --config config/default.yaml

# Run baseline simulation
python main.py run --config config/default.yaml --scenario baseline

# Run test scenarios
python main.py run --config config/default.yaml --scenario rising_load
python main.py run --config config/default.yaml --scenario crac_failure

# Override parameters
python main.py run --config config/default.yaml --set room.it_load_kw=60.0

# Launch HMI dashboard
node-red hmi/node-red-flows.json
```

## Configuration-Driven Architecture

### Professional CLI Interface

The simulation platform provides a professional command-line interface with multiple subcommands:

```bash
# Configuration validation
python main.py validate --config config/custom.yaml

# Simulation execution  
python main.py run --config config/default.yaml [options]

# Performance benchmarking
python main.py benchmark --config config/default.yaml --duration 30

# Configuration export
python main.py export --config config/default.yaml --format yaml
```

### YAML Configuration System

All system parameters are managed through professional YAML configuration files:

**Master Configuration** (`config/default.yaml`):
```yaml
system:
  name: "Data Center BAS Simulation"
  version: "1.0"

room:
  initial_temp_c: 22.0
  it_load_kw: 40.0
  thermal_mass_kj_per_c: 2500.0

pid_controller:
  kp: 3.0
  ki: 0.15
  kd: 0.08

crac_units:
  - unit_id: "CRAC-01"     # Auto-assigned LEAD role
    q_rated_kw: 50.0
    efficiency_cop: 3.5
  - unit_id: "CRAC-02"     # Auto-assigned LAG role  
    q_rated_kw: 50.0
  - unit_id: "CRAC-03"     # Auto-assigned STANDBY role
    q_rated_kw: 50.0

simulation:
  duration_minutes: 60.0
  timestep_s: 1.0
  setpoint_c: 22.0
```

### Scenario Override System

Test scenarios are defined as YAML files that override base configuration:

**Rising Load Scenario** (`config/scenarios/rising_load.yaml`):
```yaml
simulation:
  duration_minutes: 15.0

room:
  it_load_kw: 35.0  # Starting load

load_profile:
  type: "ramp"
  start_load_kw: 35.0
  end_load_kw: 70.0
```

### Schema Validation

All configurations are validated against comprehensive JSON schemas ensuring:
- Type safety and value ranges
- Required parameter checking  
- Professional error reporting
- Configuration consistency

## Control System Features

### Temperature Control
- **PID Controller**: Tuned for data center thermal response with anti-windup protection
- **Setpoint**: 22°C ±0.5°C accuracy under normal operation
- **Response Time**: <5 minutes for load changes up to 100% of design capacity

#### PID Control Loop Design

```mermaid
flowchart LR
  subgraph PID["PID with Anti-Windup"]
    SP[Setpoint 22°C] --> E[Error e = SP - T]
    T[Measured Temp] --> E
    E --> P[Proportional<br/>Kp*e]
    E --> I[Integral<br/>Ki∫e dt]
    E --> D[Derivative<br/>Kd de/dt]
    P --> SUM
    I --> SUM
    D --> SUM
    SUM[Sum → Demand] --> Clamp{Clamp to limits}
    Clamp -->|u| Output[u → Sequencer]
    Clamp -->|back-calc| I
  end
```

*Professional PID implementation with derivative-on-measurement and conditional integration to prevent windup during saturation conditions.*

### CRAC Coordination
- **Lead Unit**: Primary cooling, runs continuously at minimum load
- **Lag Unit**: Stages when temperature error exceeds 0.8°C for >3 minutes  
- **Standby Unit**: Activates only during equipment failures
- **Role Rotation**: Automatic daily rotation for even equipment wear

#### Staging Sequence Logic

```mermaid
sequenceDiagram
  participant Room as Room Temp
  participant PID as PID Controller
  participant Seq as Sequencer
  participant Lead as CRAC-01 (LEAD)
  participant Lag as CRAC-02 (LAG)
  participant Standby as CRAC-03 (STANDBY)
  participant Alarm as Alarm Manager

  Room->>PID: Measured T
  PID->>Seq: Cooling demand (kW)
  activate Seq
  Seq->>Lead: Command min cooling (run continuous)
  Note over Seq: If error > 0.8°C for > 180s → stage LAG
  Seq->>Lag: Start & modulate
  Lead-->>Room: Sensible cooling
  Lag-->>Room: Additional cooling

  Note over Lead: Fault detected (no cooling output)
  Lead->>Alarm: CRAC_FAIL
  Seq->>Standby: Promote STANDBY → active
  Alarm-->>Monitoring: Critical alarm (priority & debounce)
  deactivate Seq
```

*Demonstrates automated staging thresholds, anti-short-cycle protection, and fault-tolerant role promotion for N+1 redundancy.*

### Redundancy & Failover
- **N+1 Configuration**: System maintains cooling with any single CRAC failure
- **Failover Time**: <15 seconds for equipment fault detection and response
- **Capacity**: 150kW total (3×50kW) for 70kW maximum IT load + envelope losses

## Alarm Management

**Standard BAS Alarms:**
- `HIGH_TEMP` - Space temperature >27°C for >2 minutes (Critical)
- `LOW_TEMP` - Space temperature <18°C for >2 minutes (Critical)
- `CRAC_FAIL` - Unit commanded but no cooling output (High)  
- `SENSOR_STUCK` - Temperature reading unchanged >10 minutes (Medium)

#### Alarm Lifecycle State Machine

```mermaid
stateDiagram-v2
  [*] --> Debounce
  Debounce --> Active: condition true for N seconds
  Debounce --> [*]: condition clears early
  Active --> Acknowledged: operator ack
  Active --> Cleared: condition clears
  Acknowledged --> Cleared: condition clears
  Cleared --> [*]
  
  note right of Active
    Priority classification:<br/>
    Critical / High / Medium / Low<br/>
    with proper escalation
  end note
```

*Professional alarm handling with debounce timers to prevent nuisance alarms and proper state management for operations teams.*

**Features:**
- Priority-based classification with proper escalation
- Debounce timers prevent nuisance alarms
- Acknowledge/reset functionality for operator interface
- Complete alarm history and occurrence tracking

## Testing & Validation

### Automated Scenarios

**Baseline Scenario** (`baseline`):
- 60-minute steady-state validation
- Tight temperature control verification
- Single CRAC operation confirmation

**Rising Load Scenario** (`rising_load`):
- IT load ramp from 35kW to 70kW over 10 minutes
- Validates LAG staging response timing
- Ensures no high temperature alarms

**Equipment Failure Scenario** (`crac_failure`):
- LEAD CRAC failure at t=5 minutes
- Tests automatic role promotion
- Validates redundancy activation

## 📈 Professional Control Performance Analysis

The system includes a comprehensive **BAS analysis tool** that generates professional control performance plots and KPIs, demonstrating real Building Automation expertise.

### System Performance Dashboard

| Temperature Control | Equipment Runtime | Energy Performance | System Overview |
|-------|-------|-------|-------|
| ![PID](reports/pid_performance.png) | ![Runtime](reports/equipment_runtime.png) | ![Energy](reports/energy_performance.png) | ![Overview](reports/system_overview.png) |

### 🎯 Key Performance Indicators

#### Temperature Control Excellence
- **Setpoint**: 22.0°C (71.6°F)
- **Average Temperature**: 22.1°C (71.8°F)  
- **Control Accuracy**: 100.0% within ±0.5°C (exceeds ±1.0°C industry standard)
- **Standard Deviation**: 0.229°C
- **Maximum Error**: 0.500°C

#### Equipment Performance Optimization
- **CRAC-01 (Lead)**: 109.1% utilization — 0 switches
- **CRAC-02 (Lag)**: 18.2% utilization — 1 switches
- **CRAC-03 (Standby)**: 0.0% utilization — 0 switches

#### Energy Efficiency Metrics
- **Average Power**: 9.7 kW
- **Average Cooling**: 28.6 kW
- **System COP**: 2.94 (Energy Star compliant)
- **Total Energy**: 0.48 kWh per simulation

#### Professional BAS Features
- **Dual Temperature Units**: 22.0°C (71.6°F) displays
- **Airflow Tracking**: 8000 CFM (3776 L/s) rated capacity
- **Time Formatting**: HH:MM:SS professional timestamps
- **Controller Saturation**: 0.0% of time (optimal tuning)

### 🔍 Generate Your Own Analysis

```bash
# Install analysis dependencies
pip install pandas matplotlib seaborn

# Run simulation and analyze results
python main.py run --config config/default.yaml --duration 10
python analyze.py --csv logs/datacenter_telemetry_*.csv --name baseline

# Compare scenarios (before vs after optimization)  
python analyze.py --compare logs/before.csv logs/after.csv

# Automated analysis pipeline
./scripts/generate_analysis.sh baseline 15
```

### Analysis Output Structure
```
reports/
├── baseline_summary.md         ← README content
├── baseline_kpis.json         ← Structured KPIs
├── pid_performance.png        ← PID loop analysis
├── equipment_runtime.png      ← Runtime analysis  
├── energy_performance.png     ← Energy analysis
└── system_overview.png        ← Dashboard view
```

---
*Professional analysis generated by BAS Analysis Tool demonstrating control engineering expertise*

## Monitoring & HMI

### Node-RED Dashboard
- Real-time temperature display with alarm indicators
- CRAC status table showing role, capacity, and power consumption
- Manual controls for setpoint adjustment and equipment testing
- Historical trending with configurable data retention

#### Telemetry Data Flow

```mermaid
flowchart LR
  Sim[Simulation Outputs] -->|1–60s sampling| Hist[CSV Historian]
  Hist --> Ret[Rotation & Retention]
  Sim --> HMI[Node-RED Dashboard]
  HMI --> Ops[Operator Actions]
  Ops --> Sim
  
  subgraph Telemetry
    T[Temperature]
    Pwr[Power]
    Role[CRAC Role]
    Al[Alarms]
  end
  
  Sim --> T
  Sim --> Pwr  
  Sim --> Role
  Sim --> Al
  
  subgraph Interfaces
    HTTP[HTTP API]
    WS[WebSocket]
    MQTT[MQTT]
  end
  
  HMI --> HTTP
  HMI --> WS
  HMI --> MQTT
```

*Complete data pipeline from simulation to visualization with multiple integration options for external systems and real-time operator control.*

### Data Logging
- CSV historian with configurable 1-60 second sampling
- Comprehensive telemetry: temperatures, equipment status, power consumption
- Automatic file rotation and cleanup for long-term operation
- Integration-ready format for external analytics tools

## Industry Compliance

**Standards Adherence:**
- ASHRAE Guideline 36: Multi-zone HVAC control sequences
- ANSI/TIA-942: Data center infrastructure standards  
- NETA Standards: Commissioning and acceptance testing procedures
- Energy Star: Equipment efficiency requirements

**Engineering Practices:**
- Professional configuration management with schema validation
- Automated testing for commissioning validation
- CLI-driven operation for integration and deployment
- Comprehensive documentation following industry standards

## Project Structure

```
data-center-bas-sim-main/
├── config/                    # Configuration management
│   ├── default.yaml          # Master system configuration
│   ├── config_loader.py      # Professional config system
│   ├── scenarios/            # Test scenario definitions
│   │   ├── baseline.yaml
│   │   ├── rising_load.yaml
│   │   └── crac_failure.yaml
│   └── schemas/              # Validation schemas
│       └── config_schema.yaml
├── control/                  # Control algorithms
│   ├── pid.py               # PID controller with anti-windup
│   ├── sequences.py         # Multi-CRAC staging logic
│   └── alarms.py            # Professional alarm management
├── sim/                     # Simulation models  
│   ├── environment.py       # Room thermal dynamics
│   └── crac.py              # CRAC unit modeling
├── telemetry/               # Data management
│   └── historian.py         # CSV data logging
├── tools/                   # Legacy utilities
│   └── run_scenario.py      # Original scenario runner
├── hmi/                     # Human-machine interface
│   └── node-red-flows.json  # Dashboard configuration
├── reports/                 # Documentation and results
└── main.py                  # Professional CLI interface
```

## Configuration Management

### File Organization

**Base Configuration** (`config/default.yaml`):
- Complete system definition with all required parameters
- Production-ready defaults for typical data center operation
- Schema-validated for consistency and correctness

**Scenario Overrides** (`config/scenarios/*.yaml`):
- Test-specific parameter modifications
- Clean separation of test conditions from base system
- Inheritance-based configuration for maintainability

**Schema Validation** (`config/schemas/config_schema.yaml`):
- Comprehensive validation rules for all parameters
- Type checking, range validation, and dependency verification
- Professional error reporting for configuration issues

### CLI Parameter Overrides

Runtime parameter modification without editing configuration files:

```bash
# Single parameter override
python main.py run --config config/default.yaml --set room.it_load_kw=80.0

# Multiple overrides
python main.py run --config config/default.yaml \
    --set room.it_load_kw=60.0 \
    --set pid_controller.kp=4.0 \
    --set simulation.duration_minutes=30
```

## Commissioning Documentation

Complete commissioning procedures and test results are documented in [`reports/commissioning.md`](reports/commissioning.md), including:

- Detailed test procedures for each scenario
- Performance validation with acceptance criteria
- CLI usage examples and configuration guidance
- Engineering recommendations and sign-off documentation

## Development Approach

This project demonstrates professional BAS engineering practices:

- **Configuration-Driven Architecture**: Complete separation of system parameters from implementation
- **Schema Validation**: Professional configuration management with error checking
- **CLI Interface**: Enterprise-grade command-line tools for operation and integration
- **Modular Design**: Separate concerns for maintainability and testing
- **Industry Standards**: Follows established BAS control sequences and practices  
- **Testing Framework**: Automated validation ensures reliable commissioning
- **Documentation**: Complete technical documentation for operations handover
- **Version Control**: Git workflow with proper commit standards for change management

## Future Enhancements

- Multi-zone modeling for hot/cold aisle configurations
- Integration with BACnet/IP for interoperability testing
- Machine learning optimization for predictive staging
- Digital twin integration with real facility data
- Web-based configuration interface for non-technical users
- Docker containerization for deployment flexibility

## License

MIT License - Created for portfolio demonstration and educational purposes.

---

*This project showcases professional Building Automation System engineering practices for data center applications, demonstrating competency in control systems, configuration management, CLI development, alarm management, HMI development, and commissioning procedures.*