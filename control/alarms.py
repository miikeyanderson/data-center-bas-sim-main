# control/alarms.py
"""
BAS Alarm Manager for Data Center Controls

Professional alarm framework with:
- Debounce timers to prevent nuisance alarms
- Latching behavior for critical conditions
- Acknowledge/reset functionality
- Priority levels (Critical, High, Medium, Low)
- Alarm state tracking and history

Engineering alarms:
- HIGH_TEMP: Temperature exceeds setpoint + 2.0°C for >120s
- CRAC_FAIL: Command >0% but cooling output ≈0 for >60s
- SENSOR_STUCK: Sensor reading unchanged for >10 minutes
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from enum import Enum
from datetime import datetime


class AlarmPriority(Enum):
    """Alarm priority levels following BAS standards."""
    CRITICAL = "critical"    # Life safety, immediate action required
    HIGH = "high"           # Equipment protection, action within minutes
    MEDIUM = "medium"       # Performance degradation, action within hours
    LOW = "low"             # Information only, investigate when convenient


class AlarmState(Enum):
    """Alarm state machine."""
    NORMAL = "normal"           # No alarm condition
    ACTIVE = "active"           # Alarm condition present and debounced
    ACKNOWLEDGED = "acknowledged"  # Alarm acknowledged by operator
    CLEARED = "cleared"         # Condition cleared, waiting for reset


@dataclass
class AlarmConfig:
    """Configuration for individual alarm."""
    alarm_id: str
    description: str
    priority: AlarmPriority
    debounce_time_s: float = 60.0      # Time condition must persist
    auto_reset: bool = False           # Auto-reset when condition clears
    latch: bool = True                 # Latch until manually reset


@dataclass
class AlarmInstance:
    """Active alarm instance with state tracking."""
    config: AlarmConfig
    state: AlarmState = AlarmState.NORMAL
    
    # Timing
    condition_start_time: Optional[float] = None
    alarm_time: Optional[float] = None
    ack_time: Optional[float] = None
    clear_time: Optional[float] = None
    
    # Current values
    current_value: float = 0.0
    alarm_setpoint: float = 0.0
    
    # Counters
    occurrence_count: int = 0
    
    def is_alarmed(self) -> bool:
        """Return True if alarm is in active or acknowledged state."""
        return self.state in [AlarmState.ACTIVE, AlarmState.ACKNOWLEDGED]


class AlarmManager:
    """
    Professional BAS alarm management system.
    
    Features:
    - Multiple alarm types with configurable debounce
    - Latching and auto-reset behavior
    - Acknowledge/reset operations
    - Alarm history and statistics
    - Integration with BAS telemetry systems
    
    Usage:
        mgr = AlarmManager()
        mgr.register_alarm(AlarmConfig("HIGH_TEMP", ...))
        mgr.update(sim_time, {"avg_temp": 25.0, "setpoint": 22.0})
        active_alarms = mgr.get_active_alarms()
    """
    
    def __init__(self):
        self.alarms: Dict[str, AlarmInstance] = {}
        self.alarm_history: List[Dict] = []
        
        # Alarm evaluation functions
        self.evaluators: Dict[str, Callable] = {}
        
        # Register standard BAS alarms
        self._register_standard_alarms()
    
    def _register_standard_alarms(self) -> None:
        """Register standard data center BAS alarms."""
        
        # Critical temperature alarm
        high_temp_config = AlarmConfig(
            alarm_id="HIGH_TEMP",
            description="Space temperature exceeds setpoint + 2.0°C",
            priority=AlarmPriority.CRITICAL,
            debounce_time_s=120.0,     # 2 minutes
            auto_reset=False,
            latch=True
        )
        self.register_alarm(high_temp_config, self._evaluate_high_temp)
        
        # CRAC failure alarm
        crac_fail_config = AlarmConfig(
            alarm_id="CRAC_FAIL",
            description="CRAC unit commanded but no cooling output",
            priority=AlarmPriority.HIGH,
            debounce_time_s=60.0,      # 1 minute
            auto_reset=False,
            latch=True
        )
        self.register_alarm(crac_fail_config, self._evaluate_crac_fail)
        
        # Sensor stuck alarm
        sensor_stuck_config = AlarmConfig(
            alarm_id="SENSOR_STUCK",
            description="Temperature sensor reading unchanged >10 minutes",
            priority=AlarmPriority.MEDIUM,
            debounce_time_s=600.0,     # 10 minutes
            auto_reset=True,
            latch=False
        )
        self.register_alarm(sensor_stuck_config, self._evaluate_sensor_stuck)
    
    def register_alarm(self, config: AlarmConfig, 
                      evaluator: Callable[[float, Dict], bool]) -> None:
        """Register new alarm type with evaluation function."""
        self.alarms[config.alarm_id] = AlarmInstance(config)
        self.evaluators[config.alarm_id] = evaluator
    
    def update(self, sim_time: float, data: Dict) -> None:
        """
        Update all alarms based on current system data.
        
        Args:
            sim_time: Current simulation time (seconds)
            data: Dictionary of system values for alarm evaluation
        """
        for alarm_id, alarm in self.alarms.items():
            if alarm_id in self.evaluators:
                condition_present = self.evaluators[alarm_id](sim_time, data)
                self._update_alarm_state(alarm, condition_present, sim_time)
    
    def _update_alarm_state(self, alarm: AlarmInstance, 
                           condition_present: bool, sim_time: float) -> None:
        """Update individual alarm state machine."""
        
        if condition_present:
            # Condition is present
            if alarm.condition_start_time is None:
                alarm.condition_start_time = sim_time
            
            # Check if debounce time elapsed
            if (alarm.state == AlarmState.NORMAL and
                sim_time - alarm.condition_start_time >= 
                alarm.config.debounce_time_s):
                
                # Transition to ACTIVE
                alarm.state = AlarmState.ACTIVE
                alarm.alarm_time = sim_time
                alarm.occurrence_count += 1
                
                # Log alarm activation
                self._log_alarm_event(alarm, "ACTIVATED", sim_time)
        
        else:
            # Condition cleared
            if alarm.condition_start_time is not None:
                alarm.condition_start_time = None
            
            if alarm.state == AlarmState.ACTIVE:
                if alarm.config.auto_reset:
                    # Auto-reset to normal
                    alarm.state = AlarmState.NORMAL
                    alarm.clear_time = sim_time
                    self._log_alarm_event(alarm, "AUTO_RESET", sim_time)
                elif not alarm.config.latch:
                    # Non-latching, return to normal
                    alarm.state = AlarmState.NORMAL
                    alarm.clear_time = sim_time
                    self._log_alarm_event(alarm, "CLEARED", sim_time)
                else:
                    # Latching, go to cleared state
                    alarm.state = AlarmState.CLEARED
                    alarm.clear_time = sim_time
                    self._log_alarm_event(alarm, "CONDITION_CLEARED", sim_time)
            
            elif alarm.state == AlarmState.ACKNOWLEDGED:
                if alarm.config.auto_reset:
                    alarm.state = AlarmState.NORMAL
                    self._log_alarm_event(alarm, "AUTO_RESET", sim_time)
    
    def acknowledge_alarm(self, alarm_id: str, sim_time: float, 
                         operator: str = "AUTO") -> bool:
        """Acknowledge an active alarm."""
        if alarm_id not in self.alarms:
            return False
        
        alarm = self.alarms[alarm_id]
        if alarm.state == AlarmState.ACTIVE:
            alarm.state = AlarmState.ACKNOWLEDGED
            alarm.ack_time = sim_time
            self._log_alarm_event(alarm, f"ACKNOWLEDGED_BY_{operator}", sim_time)
            return True
        return False
    
    def reset_alarm(self, alarm_id: str, sim_time: float,
                   operator: str = "AUTO") -> bool:
        """Reset a cleared alarm back to normal."""
        if alarm_id not in self.alarms:
            return False
        
        alarm = self.alarms[alarm_id]
        if alarm.state in [AlarmState.CLEARED, AlarmState.ACKNOWLEDGED]:
            alarm.state = AlarmState.NORMAL
            self._log_alarm_event(alarm, f"RESET_BY_{operator}", sim_time)
            return True
        return False
    
    def get_active_alarms(self) -> List[AlarmInstance]:
        """Get list of all active (not normal) alarms."""
        return [alarm for alarm in self.alarms.values() 
                if alarm.state != AlarmState.NORMAL]
    
    def get_alarms_by_priority(self, priority: AlarmPriority) -> List[AlarmInstance]:
        """Get alarms filtered by priority level."""
        return [alarm for alarm in self.alarms.values()
                if alarm.config.priority == priority and alarm.is_alarmed()]
    
    def get_alarm_summary(self) -> Dict:
        """Get summary of alarm system status."""
        active_count = len(self.get_active_alarms())
        
        priority_counts = {}
        for priority in AlarmPriority:
            priority_counts[priority.value] = len(self.get_alarms_by_priority(priority))
        
        return {
            "total_alarms": len(self.alarms),
            "active_alarms": active_count,
            "priority_breakdown": priority_counts,
            "total_occurrences": sum(a.occurrence_count for a in self.alarms.values())
        }
    
    def _log_alarm_event(self, alarm: AlarmInstance, event: str, 
                        sim_time: float) -> None:
        """Log alarm state change to history."""
        self.alarm_history.append({
            "timestamp": sim_time,
            "alarm_id": alarm.config.alarm_id,
            "event": event,
            "priority": alarm.config.priority.value,
            "description": alarm.config.description,
            "current_value": alarm.current_value,
            "setpoint": alarm.alarm_setpoint
        })
    
    # Standard alarm evaluator functions
    def _evaluate_high_temp(self, sim_time: float, data: Dict) -> bool:
        """Evaluate HIGH_TEMP alarm condition."""
        avg_temp = data.get("avg_temp", 0.0)
        setpoint = data.get("setpoint", 22.0)
        
        alarm = self.alarms["HIGH_TEMP"]
        alarm.current_value = avg_temp
        alarm.alarm_setpoint = setpoint + 2.0
        
        return avg_temp > (setpoint + 2.0)
    
    def _evaluate_crac_fail(self, sim_time: float, data: Dict) -> bool:
        """Evaluate CRAC_FAIL alarm condition."""
        crac_states = data.get("crac_states", [])
        
        # Check each CRAC for failure condition
        for crac_state in crac_states:
            cmd_pct = crac_state.get("cmd_pct", 0.0)
            q_cool_kw = crac_state.get("q_cool_kw", 0.0)
            status = crac_state.get("status", "off")
            
            # Alarm if commanded >10% but cooling <5% of command
            if (cmd_pct > 10.0 and 
                status == "running" and
                q_cool_kw < (cmd_pct * 0.05)):
                
                alarm = self.alarms["CRAC_FAIL"]
                alarm.current_value = q_cool_kw
                alarm.alarm_setpoint = cmd_pct * 0.1  # Expected minimum
                return True
        
        return False
    
    def _evaluate_sensor_stuck(self, sim_time: float, data: Dict) -> bool:
        """Evaluate SENSOR_STUCK alarm condition."""
        sensors = data.get("sensor_temps", [])
        
        if not sensors or len(sensors) < 2:
            return False
        
        # Check if all sensors reading nearly identical (stuck)
        temp_range = max(sensors) - min(sensors)
        
        alarm = self.alarms["SENSOR_STUCK"]
        alarm.current_value = temp_range
        alarm.alarm_setpoint = 0.1  # Minimum expected range
        
        # Alarm if temperature range <0.1°C (sensors likely stuck)
        return temp_range < 0.1


def create_test_alarm_manager() -> AlarmManager:
    """Create alarm manager for testing with additional test alarms."""
    mgr = AlarmManager()
    
    # Add additional test alarm
    test_config = AlarmConfig(
        alarm_id="TEST_ALARM",
        description="Test alarm for validation",
        priority=AlarmPriority.LOW,
        debounce_time_s=5.0,
        auto_reset=True,
        latch=False
    )
    
    def test_evaluator(sim_time: float, data: Dict) -> bool:
        return data.get("test_condition", False)
    
    mgr.register_alarm(test_config, test_evaluator)
    return mgr