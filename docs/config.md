# Configuration Management

## Schema Validation

All configurations are validated against JSON schemas (`config/schemas/config_schema.yaml`) ensuring:
- Type safety and value ranges
- Required parameter checking  
- Clear error reporting for configuration issues

## Default YAML Configuration

**Base Configuration** (`config/default.yaml`):
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

## Scenario Overrides

Test scenarios override base configuration (`config/scenarios/*.yaml`):

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

## CLI Overrides

Runtime parameter changes without editing files:

```bash
# Config validation
python main.py validate --config config/custom.yaml

# Single parameter override
python main.py run --config config/default.yaml --set room.it_load_kw=80.0

# Multiple overrides
python main.py run --config config/default.yaml \
    --set room.it_load_kw=60.0 \
    --set pid_controller.kp=4.0 \
    --set simulation.duration_minutes=30

# Performance testing
python main.py benchmark --config config/default.yaml --duration 30
```

## System Scaling

**System Scaling**: Architecture supports scaling from 3 to 10+ CRAC units through configuration changes:

**Multi-Unit Scaling Example**:
```yaml
# Scale to 8 CRAC units with mixed capacities
crac_units:
  - unit_id: "CRAC-01"     # Auto LEAD
    q_rated_kw: 50.0
  - unit_id: "CRAC-02"     # Auto LAG-1  
    q_rated_kw: 50.0
  - unit_id: "CRAC-03"     # Auto LAG-2
    q_rated_kw: 50.0
  - unit_id: "CRAC-04"     # Auto STANDBY-1
    q_rated_kw: 75.0       # Larger backup unit
  - unit_id: "CRAC-05"     # Auto STANDBY-2
    q_rated_kw: 50.0
```

**Equipment Type Extension**: Modular structure allows new equipment types:
- **Humidifiers**: `sim/humidifier.py` with PID humidity control
- **AHU Units**: `sim/ahu.py` with VAV and economizer integration  
- **Lighting Systems**: `control/lighting.py` with occupancy scheduling
- **UPS Monitoring**: `sim/ups.py` with battery management and load transfer

**Zone Expansion**: Multi-zone support through configuration:
```yaml
zones:
  - zone_id: "DC-Floor-1"
    crac_assignments: ["CRAC-01", "CRAC-02", "CRAC-03"]
  - zone_id: "DC-Floor-2" 
    crac_assignments: ["CRAC-04", "CRAC-05", "CRAC-06"]
```