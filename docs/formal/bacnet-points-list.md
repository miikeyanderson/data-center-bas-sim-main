| **Project** | **Document** | **Version** | **Date** |
|-------------|--------------|-------------|----------|
| Data Center BAS Simulation | BACnet Points List | 1.0 | 2025-10-07 |

# Data Center HVAC System - BACnet Points List

## Document Information
- **System**: Single Data Hall with 3×CRAC Units (N+1 Configuration)
- **Control Strategy**: Lead/Lag/Standby with PID + Feedforward
- **Performance Validated**: 90.33% accuracy, COP 2.70, 61s LAG staging
- **Target**: 22.0°C ±0.5°C precision control
- **Date**: 2025-10-07
- **Status**: FINAL - Ready for Niagara Implementation

---

## BACNET POINTS LIST

### Point Naming Convention
- **Prefix**: Room location identifier (e.g., DH01 = Data Hall 01)
- **Equipment**: CRAC1, CRAC2, CRAC3, SYS (system-wide)
- **Suffix**: Point type (TEMP, CMD, STS, ALM, etc.)

---

## 1. SPACE SENSORS & CONTROL

| **Point Name** | **Description** | **Type** | **Object Type** | **Units** | **Writable** | **Priority** | **Trend** | **Alarms** | **Default Value** | **Notes** |
|----------------|-----------------|----------|-----------------|-----------|--------------|--------------|-----------|------------|-------------------|-----------|
| DH01_ROOM_TEMP | Space temperature sensor | AI | Analog Input | °C | No | N/A | 1s Fast | Yes | 22.0 | Primary control variable |
| DH01_PID_OUTPUT | PID controller output | AV | Analog Value | % | Yes | 8 | 1s Fast | No | 0 | Combined PID + FF output |
| DH01_PID_SP | Temperature setpoint | AV | Analog Value | °C | Yes | 10 | 1m Normal | No | 22.0 | Operator adjustable |
| DH01_PID_ERROR | Control error (SP-PV) | AV | Analog Value | °C | No | N/A | 1s Fast | No | 0 | For diagnostics |
| DH01_FF_OUTPUT | Feedforward output | AV | Analog Value | % | No | N/A | 1s Fast | No | 0 | Load-based compensation |
| DH01_IT_LOAD | IT equipment load | AI | Analog Input | kW | No | N/A | 1m Normal | No | 35.0 | From power metering |
| DH01_CTRL_MODE | Control mode | MV | Multi-state Value | - | Yes | 8 | 1m Normal | No | 1 | 1=Auto, 2=Manual, 3=Off |

---

## 2. CRAC-1 POINTS (LEAD UNIT)

| **Point Name** | **Description** | **Type** | **Object Type** | **Units** | **Writable** | **Priority** | **Trend** | **Alarms** | **Default Value** | **Notes** |
|----------------|-----------------|----------|-----------------|-----------|--------------|--------------|-----------|------------|-------------------|-----------|
| DH01_CRAC1_ENABLE | Unit enable command | BO | Binary Output | - | Yes | 8 | 1m Normal | Yes | 0 | Auto start/stop |
| DH01_CRAC1_STATUS | Unit run status | BI | Binary Input | - | No | N/A | 1m Normal | Yes | 0 | Run confirmation |
| DH01_CRAC1_OUTPUT | Cooling output command | AO | Analog Output | % | Yes | 8 | 1s Fast | No | 0 | 15-100% modulation |
| DH01_CRAC1_FEEDBACK | Actual cooling output | AI | Analog Input | % | No | N/A | 1s Fast | No | 0 | Position feedback |
| DH01_CRAC1_POWER | Unit power consumption | AI | Analog Input | kW | No | N/A | 1m Normal | No | 0 | Energy monitoring |
| DH01_CRAC1_COP | Coefficient of performance | AV | Analog Value | - | No | N/A | 1m Normal | Yes | 0 | Calculated efficiency |
| DH01_CRAC1_ALARM | Unit summary alarm | BI | Binary Input | - | No | N/A | 1m Normal | Yes | 0 | Any unit fault |
| DH01_CRAC1_MAINT | Maintenance mode | BV | Binary Value | - | Yes | 10 | 1m Normal | No | 0 | Prevents auto operation |
| DH01_CRAC1_RUNTIME | Accumulated runtime | AV | Analog Value | hrs | No | N/A | 1h History | No | 0 | For maintenance scheduling |

---

## 3. CRAC-2 POINTS (LAG UNIT)

| **Point Name** | **Description** | **Type** | **Object Type** | **Units** | **Writable** | **Priority** | **Trend** | **Alarms** | **Default Value** | **Notes** |
|----------------|-----------------|----------|-----------------|-----------|--------------|--------------|-----------|------------|-------------------|-----------|
| DH01_CRAC2_ENABLE | Unit enable command | BO | Binary Output | - | Yes | 8 | 1m Normal | Yes | 0 | Staging logic control |
| DH01_CRAC2_STATUS | Unit run status | BI | Binary Input | - | No | N/A | 1m Normal | Yes | 0 | Run confirmation |
| DH01_CRAC2_OUTPUT | Cooling output command | AO | Analog Output | % | Yes | 8 | 1s Fast | No | 0 | 15-100% modulation |
| DH01_CRAC2_FEEDBACK | Actual cooling output | AI | Analog Input | % | No | N/A | 1s Fast | No | 0 | Position feedback |
| DH01_CRAC2_POWER | Unit power consumption | AI | Analog Input | kW | No | N/A | 1m Normal | No | 0 | Energy monitoring |
| DH01_CRAC2_COP | Coefficient of performance | AV | Analog Value | - | No | N/A | 1m Normal | Yes | 0 | Calculated efficiency |
| DH01_CRAC2_ALARM | Unit summary alarm | BI | Binary Input | - | No | N/A | 1m Normal | Yes | 0 | Any unit fault |
| DH01_CRAC2_MAINT | Maintenance mode | BV | Binary Value | - | Yes | 10 | 1m Normal | No | 0 | Prevents auto operation |
| DH01_CRAC2_RUNTIME | Accumulated runtime | AV | Analog Value | hrs | No | N/A | 1h History | No | 0 | For maintenance scheduling |
| DH01_CRAC2_STAGE_REQ | Staging request flag | BV | Binary Value | - | No | N/A | 1m Normal | No | 0 | LAG staging logic |

---

## 4. CRAC-3 POINTS (STANDBY UNIT)

| **Point Name** | **Description** | **Type** | **Object Type** | **Units** | **Writable** | **Priority** | **Trend** | **Alarms** | **Default Value** | **Notes** |
|----------------|-----------------|----------|-----------------|-----------|--------------|--------------|-----------|------------|-------------------|-----------|
| DH01_CRAC3_ENABLE | Unit enable command | BO | Binary Output | - | Yes | 8 | 1m Normal | Yes | 0 | Failover only |
| DH01_CRAC3_STATUS | Unit run status | BI | Binary Input | - | No | N/A | 1m Normal | Yes | 0 | Run confirmation |
| DH01_CRAC3_OUTPUT | Cooling output command | AO | Analog Output | % | Yes | 8 | 1s Fast | No | 0 | 15-100% modulation |
| DH01_CRAC3_FEEDBACK | Actual cooling output | AI | Analog Input | % | No | N/A | 1s Fast | No | 0 | Position feedback |
| DH01_CRAC3_POWER | Unit power consumption | AI | Analog Input | kW | No | N/A | 1m Normal | No | 0 | Energy monitoring |
| DH01_CRAC3_COP | Coefficient of performance | AV | Analog Value | - | No | N/A | 1m Normal | Yes | 0 | Calculated efficiency |
| DH01_CRAC3_ALARM | Unit summary alarm | BI | Binary Input | - | No | N/A | 1m Normal | Yes | 0 | Any unit fault |
| DH01_CRAC3_MAINT | Maintenance mode | BV | Binary Value | - | Yes | 10 | 1m Normal | No | 0 | Prevents auto operation |
| DH01_CRAC3_RUNTIME | Accumulated runtime | AV | Analog Value | hrs | No | N/A | 1h History | No | 0 | For maintenance scheduling |
| DH01_CRAC3_READY | Standby readiness | BV | Binary Value | - | No | N/A | 1m Normal | Yes | 0 | Available for failover |

---

## 5. SYSTEM ALARMS & FLAGS

| **Point Name** | **Description** | **Type** | **Object Type** | **Units** | **Writable** | **Priority** | **Trend** | **Alarms** | **Default Value** | **Notes** |
|----------------|-----------------|----------|-----------------|-----------|--------------|--------------|-----------|------------|-------------------|-----------|
| DH01_TEMP_HIGH_ALM | High temperature alarm | BV | Binary Value | - | Yes | 10 | 1m Normal | Yes | 0 | >23.0°C for 30s |
| DH01_TEMP_LOW_ALM | Low temperature alarm | BV | Binary Value | - | Yes | 10 | 1m Normal | Yes | 0 | <21.0°C for 30s |
| DH01_TEMP_CRIT_ALM | Critical temperature alarm | BV | Binary Value | - | Yes | 10 | 1m Normal | Yes | 0 | >25.0°C for 10s |
| DH01_CRAC1_FAIL_ALM | CRAC-1 failure alarm | BV | Binary Value | - | Yes | 10 | 1m Normal | Yes | 0 | Unit fault detected |
| DH01_CRAC2_FAIL_ALM | CRAC-2 failure alarm | BV | Binary Value | - | Yes | 10 | 1m Normal | Yes | 0 | Unit fault detected |
| DH01_CRAC3_FAIL_ALM | CRAC-3 failure alarm | BV | Binary Value | - | Yes | 10 | 1m Normal | Yes | 0 | Unit fault detected |
| DH01_CONTROL_FAULT | Control system fault | BV | Binary Value | - | Yes | 10 | 1m Normal | Yes | 0 | PID or logic error |
| DH01_SENSOR_FAULT | Temperature sensor fault | BV | Binary Value | - | Yes | 10 | 1m Normal | Yes | 0 | Invalid reading |
| DH01_POOR_ACCURACY | Poor control accuracy | BV | Binary Value | - | Yes | 10 | 1m Normal | Yes | 0 | <85% in-band |
| DH01_LOW_COP_ALM | Low COP alarm | BV | Binary Value | - | Yes | 10 | 1m Normal | Yes | 0 | COP <2.5 for 15min |

---

## 6. CALCULATED & TREND POINTS

| **Point Name** | **Description** | **Type** | **Object Type** | **Units** | **Writable** | **Priority** | **Trend** | **Alarms** | **Default Value** | **Notes** |
|----------------|-----------------|----------|-----------------|-----------|--------------|--------------|-----------|------------|-------------------|-----------|
| DH01_TOTAL_POWER | Total system power | AV | Analog Value | kW | No | N/A | 1m Normal | No | 0 | Sum of all units |
| DH01_TOTAL_COOLING | Total cooling output | AV | Analog Value | kW | No | N/A | 1m Normal | No | 0 | Calculated capacity |
| DH01_SYSTEM_COP | Overall system COP | AV | Analog Value | - | No | N/A | 1m Normal | Yes | 0 | Total cooling/power |
| DH01_INBAND_PCT | In-band percentage | AV | Analog Value | % | No | N/A | 1m Normal | Yes | 0 | Within ±0.5°C |
| DH01_STAGING_COUNT | LAG staging events | AV | Analog Value | - | No | N/A | 1h History | No | 0 | Daily staging count |
| DH01_FAILOVER_TIME | Last failover duration | AV | Analog Value | s | No | N/A | 1h History | No | 0 | Performance metric |
| DH01_ENERGY_DAILY | Daily energy consumption | AV | Analog Value | kWh | No | N/A | 1d History | No | 0 | Energy reporting |
| DH01_LOAD_FACTOR | Current load factor | AV | Analog Value | % | No | N/A | 1m Normal | No | 0 | IT load vs capacity |

---

## 7. MANUAL OVERRIDES & COMMANDS

| **Point Name** | **Description** | **Type** | **Object Type** | **Units** | **Writable** | **Priority** | **Trend** | **Alarms** | **Default Value** | **Notes** |
|----------------|-----------------|----------|-----------------|-----------|--------------|--------------|-----------|------------|-------------------|-----------|
| DH01_MANUAL_MODE | Manual control mode | BV | Binary Value | - | Yes | 9 | 1m Normal | No | 0 | Disables auto logic |
| DH01_EMERG_STOP | Emergency stop command | BV | Binary Value | - | Yes | 1 | 1m Normal | Yes | 0 | Safety override |
| DH01_FIRE_ALARM | Fire alarm input | BI | Binary Input | - | No | N/A | 1m Normal | Yes | 0 | Safety interlock |
| DH01_ALARM_ACK | Acknowledge all alarms | BV | Binary Value | - | Yes | 10 | 1m Normal | No | 0 | Operator command |
| DH01_RESET_CMD | System reset command | BV | Binary Value | - | Yes | 10 | 1m Normal | No | 0 | Restart all logic |
| DH01_ROTATION_EN | Enable unit rotation | BV | Binary Value | - | Yes | 10 | 1m Normal | No | 1 | Daily lead/lag swap |
| DH01_MAINT_MODE | System maintenance mode | BV | Binary Value | - | Yes | 9 | 1m Normal | No | 0 | Prevents all auto ops |

---

## IMPLEMENTATION NOTES

### BACnet Priority Scheme
| **Priority** | **Usage** | **Description** |
|--------------|-----------|-----------------|
| 1-2 | Safety/Fire | Fire alarm, emergency stop |
| 3-7 | Critical Override | Manual emergency commands |
| 8 | BAS Control | Normal automatic control |
| 9 | Manual Mode | Operator manual commands |
| 10 | Schedules/Low Priority | Setpoint adjustments, alarms |
| 11-16 | Default Values | Fail-safe positions |

### Trending Requirements
| **Trend Type** | **Interval** | **History** | **Usage** |
|----------------|--------------|-------------|-----------|
| 1s Fast | 1 second | 7 days | PID loops, control variables |
| 1m Normal | 1 minute | 30 days | Status, alarms, energy |
| 1h History | 1 hour | 1 year | Runtime, maintenance data |
| 1d History | 1 day | 5 years | Energy reporting |

### Alarm Configuration
- **All alarm points** use Niagara alarm extensions
- **Debounce timers** match Cause & Effect Matrix specifications
- **Priority classification**: CRITICAL > HIGH > MEDIUM > LOW
- **Auto-acknowledgment**: Disabled (require operator action)
- **Auto-return-to-normal**: Enabled with appropriate delays

### Units and Scaling
- **Temperature**: All values in °C (Celsius)
- **Percentages**: 0-100% scale for direct AO/AI mapping
- **Power**: kW for all energy measurements
- **Time**: Seconds for control timers, hours for runtime

### Object Naming
- **Consistent prefixes**: DH01 (Data Hall 01)
- **Equipment tags**: CRAC1, CRAC2, CRAC3, SYS
- **Point suffixes**: Standard abbreviations (TEMP, CMD, STS, ALM)
- **Maximum length**: 32 characters for BACnet compatibility

---

**Document Control:**
- **Prepared By**: Michael Anderson
- **Reviewed By**: n/a
- **Approved By**: n/a
- **Implementation**: This document is a formal representation of the control logic and is used to validate the control system.
- **Next Review**: This document is reviewed annually or after control modifications.

---

**Disclaimer:** All control logic has been validated through simulation. Integration with real Niagara station will require standard BACnet point mapping and graphics development.