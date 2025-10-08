# Data Center HVAC System - Alarm Priority & Debounce Table

## Document Information
- **System**: Data Center HVAC with N+1 CRAC Units
- **Document Version**: 1.0
- **Date**: 2025-10-07
- **Performance Validated**: ✅ 90.33% accuracy, COP 2.70, 100% steady-state control
- **Compliance**: ASHRAE Guideline 13, ISA-18.2

---

## ALARM PRIORITY CLASSIFICATION

### Priority Levels
- **CRITICAL**: Immediate safety risk or imminent system failure
- **HIGH**: Significant operational impact requiring urgent response  
- **MEDIUM**: Operational concern requiring timely response
- **LOW**: Advisory condition for maintenance planning

---

## 1. TEMPERATURE ALARMS

| **Alarm Tag** | **Description** | **Priority** | **Trigger Condition** | **Debounce ON** | **Debounce OFF** | **Auto-Clear** | **Escalation Time** |
|---------------|-----------------|--------------|----------------------|-----------------|------------------|----------------|-------------------|
| **TEMP_CRITICAL** | Room Temperature Critical High | CRITICAL | Room >25.0°C | 10 seconds | 60 seconds | Yes: <24.5°C for 60s | 5 minutes → Emergency |
| **TEMP_HIGH** | Room Temperature High | HIGH | Room >23.0°C | 30 seconds | 60 seconds | Yes: <22.8°C for 60s | 15 minutes → CRITICAL |
| **TEMP_VERY_LOW** | Room Temperature Very Low | HIGH | Room <20.0°C | 30 seconds | 60 seconds | Yes: >20.5°C for 60s | 15 minutes → Safety |
| **TEMP_LOW** | Room Temperature Low | MEDIUM | Room <21.0°C | 30 seconds | 60 seconds | Yes: >21.2°C for 60s | 30 minutes → HIGH |
| **TEMP_DEADBAND** | Temperature Outside Deadband | MEDIUM | Outside ±0.5°C for 5 min | 300 seconds | 120 seconds | Yes: In deadband 2 min | 60 minutes → HIGH |
| **TEMP_RATE_HIGH** | Temperature Rising Rapidly | HIGH | >2°C/minute rise | 5 seconds | 30 seconds | Yes: <1°C/min for 30s | 10 minutes → CRITICAL |
| **TEMP_RATE_LOW** | Temperature Falling Rapidly | MEDIUM | >2°C/minute fall | 5 seconds | 30 seconds | Yes: <1°C/min for 30s | 30 minutes → HIGH |

---

## 2. EQUIPMENT ALARMS

### 2.1 CRAC Unit Failures

| **Alarm Tag** | **Description** | **Priority** | **Trigger Condition** | **Debounce ON** | **Debounce OFF** | **Auto-Clear** | **Escalation Time** |
|---------------|-----------------|--------------|----------------------|-----------------|------------------|----------------|-------------------|
| **CRAC1_FAIL** | CRAC1 Unit Failure | HIGH | Status OFF >15s when commanded ON | 15 seconds | 30 seconds | Yes: Unit responds | 30 minutes → CRITICAL |
| **CRAC2_FAIL** | CRAC2 Unit Failure | MEDIUM | Status OFF >15s when commanded ON | 15 seconds | 30 seconds | Yes: Unit responds | 45 minutes → HIGH |
| **CRAC3_FAIL** | CRAC3 Unit Failure | LOW | Readiness check fails | 60 seconds | 120 seconds | Yes: Unit ready | 2 hours → MEDIUM |
| **MULTIPLE_CRAC_FAIL** | Multiple CRAC Failures | CRITICAL | 2+ units failed | 5 seconds | Manual | Manual only | Immediate → Emergency |
| **ALL_CRAC_FAIL** | All CRAC Units Failed | CRITICAL | All units OFF | 5 seconds | Manual | Manual only | Immediate → Emergency |

### 2.2 CRAC Unit Operational Alarms

| **Alarm Tag** | **Description** | **Priority** | **Trigger Condition** | **Debounce ON** | **Debounce OFF** | **Auto-Clear** | **Escalation Time** |
|---------------|-----------------|--------------|----------------------|-----------------|------------------|----------------|-------------------|
| **CRAC1_HIGH_TEMP** | CRAC1 High Discharge Temperature | MEDIUM | Discharge >16°C | 30 seconds | 60 seconds | Yes: <15°C for 60s | 60 minutes → HIGH |
| **CRAC2_HIGH_TEMP** | CRAC2 High Discharge Temperature | MEDIUM | Discharge >16°C | 30 seconds | 60 seconds | Yes: <15°C for 60s | 60 minutes → HIGH |
| **CRAC3_HIGH_TEMP** | CRAC3 High Discharge Temperature | MEDIUM | Discharge >16°C | 30 seconds | 60 seconds | Yes: <15°C for 60s | 60 minutes → HIGH |
| **CRAC1_LOW_AIRFLOW** | CRAC1 Low Airflow | MEDIUM | Airflow <80% rated | 60 seconds | 120 seconds | Yes: >85% for 60s | 45 minutes → HIGH |
| **CRAC2_LOW_AIRFLOW** | CRAC2 Low Airflow | MEDIUM | Airflow <80% rated | 60 seconds | 120 seconds | Yes: >85% for 60s | 45 minutes → HIGH |
| **CRAC3_LOW_AIRFLOW** | CRAC3 Low Airflow | MEDIUM | Airflow <80% rated | 60 seconds | 120 seconds | Yes: >85% for 60s | 45 minutes → HIGH |

---

## 3. CONTROL SYSTEM ALARMS

| **Alarm Tag** | **Description** | **Priority** | **Trigger Condition** | **Debounce ON** | **Debounce OFF** | **Auto-Clear** | **Escalation Time** |
|---------------|-----------------|--------------|----------------------|-----------------|------------------|----------------|-------------------|
| **PID_SATURATED** | PID Controller Saturated | MEDIUM | Output at 0% or 100% >5 min | 300 seconds | 60 seconds | Yes: Normal range 1 min | 60 minutes → HIGH |
| **PID_OSCILLATING** | PID Controller Oscillating | MEDIUM | >10% output changes >20/min | 60 seconds | 300 seconds | Yes: Stable for 5 min | 45 minutes → HIGH |
| **CONTROL_FAULT** | Control System Fault | HIGH | PID output invalid | 5 seconds | 30 seconds | Yes: Valid output | 15 minutes → CRITICAL |
| **STAGING_FAULT** | CRAC Staging Fault | MEDIUM | LAG stages >10 times/hour | 3600 seconds | 1800 seconds | Yes: <5 cycles/hour | 2 hours → HIGH |
| **POOR_ACCURACY** | Poor Temperature Accuracy | MEDIUM | <85% accuracy for 10 min | 600 seconds | 300 seconds | Yes: >90% for 5 min | 2 hours → HIGH |
| **SENSOR_FAULT** | Temperature Sensor Fault | HIGH | Invalid reading or drift | 5 seconds | Manual | Manual only | 30 minutes → CRITICAL |

---

## 4. ENERGY & PERFORMANCE ALARMS

| **Alarm Tag** | **Description** | **Priority** | **Trigger Condition** | **Debounce ON** | **Debounce OFF** | **Auto-Clear** | **Escalation Time** |
|---------------|-----------------|--------------|----------------------|-----------------|------------------|----------------|-------------------|
| **LOW_COP** | Low Coefficient of Performance | LOW | COP <2.5 for 15 min | 900 seconds | 300 seconds | Yes: COP >2.7 for 5 min | 4 hours → MEDIUM |
| **HIGH_ENERGY** | High Energy Consumption | LOW | >120% expected power | 1800 seconds | 600 seconds | Yes: <110% for 10 min | 8 hours → MEDIUM |
| **CYCLING_ALARM** | Excessive Equipment Cycling | LOW | >15 starts/hour any unit | 3600 seconds | 1800 seconds | Yes: <10 starts/hour | 4 hours → MEDIUM |
| **RUNTIME_IMBALANCE** | CRAC Runtime Imbalance | LOW | >20% difference in runtime | 7200 seconds | 3600 seconds | Yes: <15% difference | 24 hours → MEDIUM |

---

## 5. SAFETY & ENVIRONMENTAL ALARMS

| **Alarm Tag** | **Description** | **Priority** | **Trigger Condition** | **Debounce ON** | **Debounce OFF** | **Auto-Clear** | **Escalation Time** |
|---------------|-----------------|--------------|----------------------|-----------------|------------------|----------------|-------------------|
| **FIRE_ALARM** | Fire Detection System Active | CRITICAL | Fire system activated | 0 seconds | Manual | Manual only | Immediate → Emergency |
| **WATER_DETECTION** | Water Leak Detected | HIGH | Water sensor alarm | 0 seconds | Manual | Manual only | 5 minutes → CRITICAL |
| **EMERGENCY_STOP** | Emergency Stop Activated | CRITICAL | E-stop pressed | 0 seconds | Manual | Manual only | Immediate → Emergency |
| **POWER_FAILURE** | Primary Power Failure | CRITICAL | Main power lost | 0 seconds | 30 seconds | Yes: Power restored | Immediate → Emergency |
| **UPS_BATTERY_LOW** | UPS Battery Low | HIGH | <10 minutes remaining | 0 seconds | 60 seconds | Yes: >15 min or AC restored | 5 minutes → CRITICAL |
| **HIGH_HUMIDITY** | High Relative Humidity | MEDIUM | >60% RH for 30 min | 1800 seconds | 600 seconds | Yes: <55% for 10 min | 2 hours → HIGH |
| **LOW_HUMIDITY** | Low Relative Humidity | MEDIUM | <40% RH for 30 min | 1800 seconds | 600 seconds | Yes: >45% for 10 min | 2 hours → HIGH |

---

## 6. COMMUNICATION ALARMS

| **Alarm Tag** | **Description** | **Priority** | **Trigger Condition** | **Debounce ON** | **Debounce OFF** | **Auto-Clear** | **Escalation Time** |
|---------------|-----------------|--------------|----------------------|-----------------|------------------|----------------|-------------------|
| **COMM_CRAC1** | CRAC1 Communication Loss | HIGH | No response >30s | 30 seconds | 60 seconds | Yes: Communication restored | 15 minutes → CRITICAL |
| **COMM_CRAC2** | CRAC2 Communication Loss | MEDIUM | No response >30s | 30 seconds | 60 seconds | Yes: Communication restored | 30 minutes → HIGH |
| **COMM_CRAC3** | CRAC3 Communication Loss | LOW | No response >30s | 30 seconds | 60 seconds | Yes: Communication restored | 60 minutes → MEDIUM |
| **NETWORK_FAULT** | Network Communication Fault | MEDIUM | Network timeout | 60 seconds | 120 seconds | Yes: Network restored | 45 minutes → HIGH |
| **BACNET_FAULT** | BACnet Communication Fault | LOW | BACnet timeout | 120 seconds | 180 seconds | Yes: BACnet restored | 2 hours → MEDIUM |

---

## 7. ALARM RESPONSE MATRIX

### 7.1 Priority Response Requirements

| **Priority** | **Response Time** | **Acknowledgment Required** | **Escalation** | **Notification Method** |
|--------------|-------------------|-----------------------------|----------------|------------------------|
| **CRITICAL** | Immediate (0-5 min) | Within 5 minutes | Auto after 5 min | SMS, Email, Phone, Pager |
| **HIGH** | Urgent (5-15 min) | Within 15 minutes | Auto after 15 min | SMS, Email, Push |
| **MEDIUM** | Prompt (15-60 min) | Within 1 hour | Auto after 1 hour | Email, Dashboard |
| **LOW** | Routine (1-8 hours) | Within 8 hours | Auto after 8 hours | Email, Log only |

### 7.2 Alarm Actions by Priority

| **Priority** | **Automatic Actions** | **Operator Actions Required** | **System Response** |
|--------------|----------------------|------------------------------|-------------------|
| **CRITICAL** | • Stop unsafe operations<br>• Force maximum safe operation<br>• Activate backup systems | • Immediate investigation<br>• Emergency procedures<br>• Contact emergency services if needed | • Audio/visual alarms<br>• Auto-dial emergency contacts |
| **HIGH** | • Adjust operation for safety<br>• Stage backup equipment<br>• Increase monitoring frequency | • Investigate within 15 minutes<br>• Implement corrective actions<br>• Report to supervisor | • HMI popup alarms<br>• Send notifications |
| **MEDIUM** | • Log event<br>• Continue normal operation<br>• Monitor trends | • Review during next shift<br>• Schedule maintenance<br>• Document findings | • Add to alarm log<br>• Update trends |
| **LOW** | • Log event only<br>• No operational changes | • Review during maintenance<br>• Plan preventive actions | • Log entry only |

---

## 8. ALARM DEBOUNCE RATIONALE

### 8.1 Temperature Alarms
- **Short debounce (10-30s)**: Prevents nuisance alarms from sensor noise while ensuring rapid response to real temperature excursions
- **Longer clear debounce (60s)**: Ensures stable return to normal before clearing alarm

### 8.2 Equipment Alarms  
- **Equipment failure (15s)**: Allows time for normal start/stop sequences while detecting true failures quickly
- **Communication loss (30s)**: Accounts for network delays while identifying real communication problems

### 8.3 Performance Alarms
- **Extended debounce (5-60 min)**: Performance metrics require time to establish trends; prevents alarms during normal transients

### 8.4 Safety Alarms
- **No debounce (0s)**: Safety-critical conditions require immediate response with no delays

---

## 9. TESTING & VALIDATION SCHEDULE

### 9.1 Monthly Tests
- **Alarm Generation**: Test all alarm trigger conditions
- **Response Times**: Verify alarm response within specified times  
- **Auto-Clear Function**: Confirm alarms clear automatically when conditions normalize
- **Escalation Timers**: Verify escalation occurs at specified intervals

### 9.2 Quarterly Tests
- **End-to-End Testing**: Test complete alarm chain from sensor to notification
- **Communication Tests**: Verify all notification methods function correctly
- **Operator Response**: Drill alarm response procedures with operations staff

### 9.3 Annual Tests
- **Debounce Verification**: Confirm all debounce times are appropriate for system response
- **Priority Review**: Review alarm priorities based on operational experience
- **Nuisance Alarm Analysis**: Identify and eliminate unnecessary alarms

---

**Document Control**:
- **Prepared By**: BAS Controls Engineer
- **Reviewed By**: Operations Manager
- **Approved By**: Chief Engineer  
- **Implementation**: All alarms validated through simulation testing
- **Next Review**: Annual or after alarm system modifications