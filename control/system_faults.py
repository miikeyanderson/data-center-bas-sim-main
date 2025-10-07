# control/system_faults.py
"""
Professional Control System Fault Simulation Module for BAS Data Center Systems

Advanced control system fault modeling for building automation troubleshooting:
- Short-cycling detection and simulation
- Communication dropouts (network/protocol failures)
- Controller saturation beyond standard anti-windup
- Deadtime issues and control loop timing problems
- Cascade failures (multiple interconnected faults)

Engineering Implementation:
- Integration with existing PID controller architecture
- Realistic fault progression and interaction effects
- Professional control system diagnostic capabilities
- Advanced fault detection and isolation algorithms
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Tuple
from enum import Enum
import random
import time
from abc import ABC, abstractmethod


class ControlFaultType(Enum):
    """Types of control system faults that can be simulated."""
    SHORT_CYCLING = "short_cycling"        # Rapid on/off cycling
    COMM_DROPOUT = "comm_dropout"          # Communication failures
    CONTROLLER_SAT = "controller_sat"      # Controller saturation
    DEADTIME_ISSUE = "deadtime_issue"      # Control loop timing problems
    CASCADE_FAILURE = "cascade_failure"    # Multiple interconnected faults
    LOOP_INSTABILITY = "loop_instability"  # Control loop instability
    SETPOINT_DRIFT = "setpoint_drift"      # Setpoint corruption
    FEEDBACK_LOSS = "feedback_loss"        # Sensor feedback loss


@dataclass
class ControlFaultConfig:
    """Configuration for individual control system fault parameters."""
    fault_type: ControlFaultType
    severity: float = 1.0                  # Fault severity multiplier (0-1)
    progression_rate: float = 1.0          # Rate of fault development
    
    # Short-cycling parameters
    cycle_time_threshold_s: float = 300.0  # Minimum cycle time (seconds)
    short_cycle_ratio: float = 0.3         # Ratio of normal cycle time
    
    # Communication dropout parameters
    dropout_probability: float = 0.001     # Probability per timestep
    dropout_duration_s: float = 60.0       # Average dropout duration
    max_dropout_duration_s: float = 300.0  # Maximum dropout duration
    
    # Controller saturation parameters
    saturation_threshold: float = 95.0     # Saturation threshold (%)
    saturation_duration_s: float = 120.0   # Minimum saturation time
    
    # Deadtime parameters
    deadtime_multiplier: float = 2.0       # Deadtime increase factor
    timing_jitter_s: float = 5.0           # Timing jitter amplitude
    
    # Cascade failure parameters
    cascade_probability: float = 0.1       # Probability of cascading
    cascade_delay_s: float = 300.0         # Delay before cascade
    
    # Loop instability parameters
    instability_gain: float = 1.5          # Gain increase for instability
    oscillation_period_s: float = 600.0    # Oscillation period
    
    # Setpoint drift parameters
    drift_rate_per_hour: float = 0.1       # Setpoint drift rate (°C/hour)
    max_drift: float = 2.0                 # Maximum drift (°C)
    
    # Feedback loss parameters
    feedback_timeout_s: float = 180.0      # Timeout for feedback loss


class ControlSystemFault(ABC):
    """Abstract base class for control system fault implementations."""
    
    def __init__(self, config: ControlFaultConfig, seed: Optional[int] = None):
        self.config = config
        self.active = False
        self.start_time: Optional[float] = None
        self.random = random.Random(seed)
        self.fault_state: Dict[str, Any] = {}
        
    @abstractmethod
    def apply_fault(self, control_signal: float, process_value: float, 
                   setpoint: float, dt: float, sim_time: float) -> Tuple[float, float, Dict[str, Any]]:
        """
        Apply fault to control system.
        
        Args:
            control_signal: Current control output
            process_value: Current process variable
            setpoint: Current setpoint
            dt: Time step (seconds)
            sim_time: Current simulation time (seconds)
            
        Returns:
            Tuple of (modified_control_signal, modified_setpoint, fault_diagnostics)
        """
        pass
    
    def activate(self, sim_time: float) -> None:
        """Activate the fault at specified time."""
        self.active = True
        self.start_time = sim_time
        
    def deactivate(self) -> None:
        """Deactivate the fault (simulate repair)."""
        self.active = False
        self.start_time = None
        
    def get_fault_state(self) -> Dict[str, Any]:
        """Get current fault state for diagnostics."""
        return {
            'fault_type': self.config.fault_type.value,
            'active': self.active,
            'severity': self.config.severity,
            'start_time': self.start_time,
            **self.fault_state
        }


class ShortCyclingFault(ControlSystemFault):
    """Short-cycling fault - rapid on/off cycling of equipment."""
    
    def __init__(self, config: ControlFaultConfig, seed: Optional[int] = None):
        super().__init__(config, seed)
        self.last_state_change = 0.0
        self.current_state = "off"
        self.cycle_count = 0
        self.forced_cycle_time = 0.0
        
    def apply_fault(self, control_signal: float, process_value: float, 
                   setpoint: float, dt: float, sim_time: float) -> Tuple[float, float, Dict[str, Any]]:
        if not self.active:
            return control_signal, setpoint, {}
            
        # Determine if short cycling should occur
        normal_cycle_time = self.config.cycle_time_threshold_s
        short_cycle_time = normal_cycle_time * self.config.short_cycle_ratio
        
        # Force rapid cycling
        time_since_change = sim_time - self.last_state_change
        
        if time_since_change >= short_cycle_time * self.config.severity:
            # Force state change
            if self.current_state == "off" and control_signal > 10:
                self.current_state = "on"
                modified_signal = min(100.0, control_signal * 1.2)  # Aggressive startup
            else:
                self.current_state = "off"
                modified_signal = 0.0  # Force shutdown
                
            self.last_state_change = sim_time
            self.cycle_count += 1
        else:
            # Maintain current forced state
            if self.current_state == "off":
                modified_signal = 0.0
            else:
                modified_signal = control_signal
        
        self.fault_state = {
            'cycle_count': self.cycle_count,
            'current_state': self.current_state,
            'time_since_change': time_since_change,
            'short_cycle_time': short_cycle_time,
            'cycles_per_hour': self.cycle_count * 3600 / max(sim_time - (self.start_time or 0), 1)
        }
        
        return modified_signal, setpoint, self.fault_state


class CommDropoutFault(ControlSystemFault):
    """Communication dropout fault - network/protocol failures."""
    
    def __init__(self, config: ControlFaultConfig, seed: Optional[int] = None):
        super().__init__(config, seed)
        self.in_dropout = False
        self.dropout_end_time = 0.0
        self.last_valid_signal = 0.0
        self.dropout_count = 0
        
    def apply_fault(self, control_signal: float, process_value: float, 
                   setpoint: float, dt: float, sim_time: float) -> Tuple[float, float, Dict[str, Any]]:
        if not self.active:
            return control_signal, setpoint, {}
            
        # Check if currently in dropout
        if self.in_dropout:
            if sim_time >= self.dropout_end_time:
                self.in_dropout = False
                self.last_valid_signal = control_signal
            else:
                # During dropout, hold last value or go to safe state
                safe_signal = self.last_valid_signal * 0.5  # Conservative approach
                
                self.fault_state = {
                    'in_dropout': True,
                    'dropout_remaining': self.dropout_end_time - sim_time,
                    'safe_signal': safe_signal,
                    'dropout_count': self.dropout_count
                }
                
                return safe_signal, setpoint, self.fault_state
        
        # Check for new dropout event
        dropout_prob = (self.config.dropout_probability * 
                       self.config.severity * dt)
        
        if self.random.random() < dropout_prob:
            self.in_dropout = True
            self.dropout_count += 1
            
            # Random dropout duration
            duration_variation = self.random.uniform(0.5, 2.0)
            dropout_duration = min(
                self.config.dropout_duration_s * duration_variation,
                self.config.max_dropout_duration_s
            )
            self.dropout_end_time = sim_time + dropout_duration
            
            # Store last valid signal
            self.last_valid_signal = control_signal
            
            # Return safe signal immediately
            safe_signal = control_signal * 0.5
            
            self.fault_state = {
                'in_dropout': True,
                'dropout_duration': dropout_duration,
                'safe_signal': safe_signal,
                'dropout_count': self.dropout_count
            }
            
            return safe_signal, setpoint, self.fault_state
        
        # Normal operation
        self.last_valid_signal = control_signal
        self.fault_state = {
            'in_dropout': False,
            'dropout_count': self.dropout_count
        }
        
        return control_signal, setpoint, self.fault_state


class ControllerSaturationFault(ControlSystemFault):
    """Controller saturation fault - beyond standard anti-windup."""
    
    def __init__(self, config: ControlFaultConfig, seed: Optional[int] = None):
        super().__init__(config, seed)
        self.saturation_start_time = None
        self.is_saturated = False
        
    def apply_fault(self, control_signal: float, process_value: float, 
                   setpoint: float, dt: float, sim_time: float) -> Tuple[float, float, Dict[str, Any]]:
        if not self.active:
            return control_signal, setpoint, {}
            
        # Check for saturation condition
        if control_signal >= self.config.saturation_threshold:
            if not self.is_saturated:
                self.is_saturated = True
                self.saturation_start_time = sim_time
                
            # Force saturation for minimum duration
            saturation_duration = sim_time - (self.saturation_start_time or sim_time)
            if saturation_duration < self.config.saturation_duration_s:
                # Force maximum output regardless of actual need
                saturated_signal = 100.0
            else:
                # Allow normal operation but with degraded performance
                saturated_signal = min(100.0, control_signal * 1.1)
        else:
            if self.is_saturated:
                # Check if we should remain saturated due to fault
                saturation_duration = sim_time - (self.saturation_start_time or sim_time)
                if saturation_duration < self.config.saturation_duration_s:
                    saturated_signal = 100.0
                else:
                    self.is_saturated = False
                    saturated_signal = control_signal
            else:
                saturated_signal = control_signal
        
        self.fault_state = {
            'is_saturated': self.is_saturated,
            'saturation_duration': (sim_time - (self.saturation_start_time or sim_time)) if self.saturation_start_time else 0,
            'saturated_signal': saturated_signal if self.is_saturated else None,
            'saturation_threshold': self.config.saturation_threshold
        }
        
        return saturated_signal, setpoint, self.fault_state


class DeadtimeFault(ControlSystemFault):
    """Deadtime fault - control loop timing problems."""
    
    def __init__(self, config: ControlFaultConfig, seed: Optional[int] = None):
        super().__init__(config, seed)
        self.delayed_signals: List[Tuple[float, float]] = []  # (time, signal)
        self.base_delay = 30.0  # Base system delay (seconds)
        
    def apply_fault(self, control_signal: float, process_value: float, 
                   setpoint: float, dt: float, sim_time: float) -> Tuple[float, float, Dict[str, Any]]:
        if not self.active:
            return control_signal, setpoint, {}
            
        # Calculate increased deadtime
        fault_delay = self.base_delay * self.config.deadtime_multiplier
        
        # Add timing jitter
        jitter = self.random.uniform(-self.config.timing_jitter_s, 
                                   self.config.timing_jitter_s)
        total_delay = fault_delay + jitter
        
        # Store current signal with timestamp
        self.delayed_signals.append((sim_time + total_delay, control_signal))
        
        # Remove old signals and find output
        current_time = sim_time
        output_signal = 0.0
        
        # Remove expired signals and get the most recent valid one
        while self.delayed_signals:
            signal_time, signal_value = self.delayed_signals[0]
            if signal_time <= current_time:
                output_signal = signal_value
                self.delayed_signals.pop(0)
            else:
                break
        
        # Clean up very old signals (keep max 100)
        if len(self.delayed_signals) > 100:
            self.delayed_signals = self.delayed_signals[-50:]
        
        self.fault_state = {
            'fault_delay': fault_delay,
            'total_delay': total_delay,
            'delayed_signal': output_signal,
            'queue_length': len(self.delayed_signals),
            'timing_jitter': jitter
        }
        
        return output_signal, setpoint, self.fault_state


class CascadeFailureFault(ControlSystemFault):
    """Cascade failure fault - multiple interconnected faults."""
    
    def __init__(self, config: ControlFaultConfig, seed: Optional[int] = None):
        super().__init__(config, seed)
        self.cascade_triggered = False
        self.cascade_effects: List[str] = []
        self.effect_timers: Dict[str, float] = {}
        
    def apply_fault(self, control_signal: float, process_value: float, 
                   setpoint: float, dt: float, sim_time: float) -> Tuple[float, float, Dict[str, Any]]:
        if not self.active or self.start_time is None:
            return control_signal, setpoint, {}
            
        elapsed_time = sim_time - self.start_time
        
        # Check if cascade should trigger
        if not self.cascade_triggered and elapsed_time >= self.config.cascade_delay_s:
            if self.random.random() < self.config.cascade_probability:
                self.cascade_triggered = True
                
                # Define cascade effects
                possible_effects = [
                    "sensor_degradation",
                    "actuator_stiction", 
                    "communication_interference",
                    "power_fluctuation",
                    "thermal_instability"
                ]
                
                # Randomly select effects based on severity
                num_effects = int(self.config.severity * len(possible_effects))
                self.cascade_effects = self.random.sample(possible_effects, 
                                                        max(1, num_effects))
                
                # Initialize effect timers
                for effect in self.cascade_effects:
                    self.effect_timers[effect] = sim_time
        
        if self.cascade_triggered:
            modified_signal = control_signal
            modified_setpoint = setpoint
            
            # Apply cascade effects
            for effect in self.cascade_effects:
                effect_duration = sim_time - self.effect_timers[effect]
                
                if effect == "sensor_degradation":
                    # Simulate sensor noise affecting control
                    noise = self.random.uniform(-0.5, 0.5) * self.config.severity
                    modified_setpoint += noise
                    
                elif effect == "actuator_stiction":
                    # Simulate actuator sticking
                    if abs(control_signal - modified_signal) < 5.0:
                        modified_signal *= 0.8  # Reduce response
                        
                elif effect == "communication_interference":
                    # Simulate intermittent communication issues
                    if self.random.random() < 0.1 * self.config.severity:
                        modified_signal *= 0.5  # Reduce signal
                        
                elif effect == "power_fluctuation":
                    # Simulate power supply issues
                    power_factor = 1.0 - 0.2 * self.config.severity * \
                                 self.random.random()
                    modified_signal *= power_factor
                    
                elif effect == "thermal_instability":
                    # Simulate thermal effects on setpoint
                    thermal_drift = 0.1 * self.config.severity * \
                                  (effect_duration / 3600.0)  # Per hour
                    modified_setpoint += thermal_drift
            
            self.fault_state = {
                'cascade_triggered': True,
                'active_effects': self.cascade_effects,
                'effect_durations': {effect: sim_time - timer 
                                   for effect, timer in self.effect_timers.items()}
            }
            
            return modified_signal, modified_setpoint, self.fault_state
        
        return control_signal, setpoint, {}


class LoopInstabilityFault(ControlSystemFault):
    """Loop instability fault - control loop becomes unstable."""
    
    def __init__(self, config: ControlFaultConfig, seed: Optional[int] = None):
        super().__init__(config, seed)
        self.oscillation_phase = 0.0
        
    def apply_fault(self, control_signal: float, process_value: float, 
                   setpoint: float, dt: float, sim_time: float) -> Tuple[float, float, Dict[str, Any]]:
        if not self.active or self.start_time is None:
            return control_signal, setpoint, {}
            
        # Create oscillatory behavior
        self.oscillation_phase += 2 * 3.14159 * dt / self.config.oscillation_period_s
        
        # Apply instability gain
        gain_factor = 1.0 + (self.config.instability_gain - 1.0) * self.config.severity
        
        # Create oscillation in control signal
        import math
        oscillation = math.sin(self.oscillation_phase) * 10 * self.config.severity
        
        unstable_signal = control_signal * gain_factor + oscillation
        unstable_signal = max(0, min(100, unstable_signal))
        
        self.fault_state = {
            'gain_factor': gain_factor,
            'oscillation_amplitude': oscillation,
            'oscillation_phase': self.oscillation_phase,
            'period_s': self.config.oscillation_period_s
        }
        
        return unstable_signal, setpoint, self.fault_state


class SetpointDriftFault(ControlSystemFault):
    """Setpoint drift fault - setpoint corruption over time."""
    
    def apply_fault(self, control_signal: float, process_value: float, 
                   setpoint: float, dt: float, sim_time: float) -> Tuple[float, float, Dict[str, Any]]:
        if not self.active or self.start_time is None:
            return control_signal, setpoint, {}
            
        # Calculate drift over time
        elapsed_hours = (sim_time - self.start_time) / 3600.0
        
        drift_amount = (self.config.drift_rate_per_hour * elapsed_hours * 
                       self.config.severity)
        
        # Limit maximum drift
        drift_amount = min(drift_amount, self.config.max_drift)
        
        # Random direction for drift
        drift_direction = 1 if self.random.random() > 0.5 else -1
        
        drifted_setpoint = setpoint + (drift_amount * drift_direction)
        
        self.fault_state = {
            'drift_amount': drift_amount,
            'drift_direction': drift_direction,
            'original_setpoint': setpoint,
            'drifted_setpoint': drifted_setpoint,
            'elapsed_hours': elapsed_hours
        }
        
        return control_signal, drifted_setpoint, self.fault_state


class FeedbackLossFault(ControlSystemFault):
    """Feedback loss fault - sensor feedback timeout."""
    
    def __init__(self, config: ControlFaultConfig, seed: Optional[int] = None):
        super().__init__(config, seed)
        self.feedback_lost = False
        self.last_valid_feedback = 0.0
        self.feedback_loss_time = None
        
    def apply_fault(self, control_signal: float, process_value: float, 
                   setpoint: float, dt: float, sim_time: float) -> Tuple[float, float, Dict[str, Any]]:
        if not self.active:
            return control_signal, setpoint, {}
            
        if not self.feedback_lost:
            # Check for feedback loss condition
            if self.random.random() < 0.001 * self.config.severity:
                self.feedback_lost = True
                self.feedback_loss_time = sim_time
                self.last_valid_feedback = process_value
        
        if self.feedback_lost:
            # Check if feedback should return
            loss_duration = sim_time - (self.feedback_loss_time or sim_time)
            if loss_duration >= self.config.feedback_timeout_s:
                if self.random.random() < 0.1:  # 10% chance per timestep to recover
                    self.feedback_lost = False
                    self.feedback_loss_time = None
            
            # Use open-loop control with degraded performance
            if abs(control_signal - 50) > 20:  # If far from midpoint
                safe_signal = control_signal * 0.7  # Conservative approach
            else:
                safe_signal = control_signal
                
            self.fault_state = {
                'feedback_lost': True,
                'loss_duration': loss_duration,
                'last_valid_feedback': self.last_valid_feedback,
                'safe_signal': safe_signal
            }
            
            return safe_signal, setpoint, self.fault_state
        
        return control_signal, setpoint, {}


@dataclass
class ControlSystemConfig:
    """Configuration for control system with fault simulation capabilities."""
    system_id: str
    system_type: str = "pid_controller"    # Type of control system
    location: str = "primary_loop"         # Control loop location
    
    # Fault simulation parameters
    enable_faults: bool = True
    fault_configs: List[ControlFaultConfig] = field(default_factory=list)


class ControlSystemFaultManager:
    """
    Professional control system fault management and simulation.
    
    Features:
    - Multiple simultaneous fault types
    - Realistic fault progression and interaction
    - Professional fault injection capabilities
    - Comprehensive state tracking for diagnostics
    
    Integration:
    - Works with existing PID controller
    - Modifies control signals and setpoints
    - Provides detailed diagnostic information
    """
    
    def __init__(self, config: ControlSystemConfig, seed: Optional[int] = None):
        self.config = config
        self.system_id = config.system_id
        
        # Fault simulation
        self.faults: List[ControlSystemFault] = []
        self.fault_history: List[Dict] = []
        
        # Random seed for deterministic testing
        self._random = random.Random(seed)
        
        # Initialize fault objects
        self._initialize_faults(seed)
        
        # Diagnostics
        self.last_update_time = 0.0
        self.performance_metrics = {
            'cycle_count': 0,
            'saturation_time': 0.0,
            'dropout_count': 0,
            'instability_events': 0
        }
        
    def _initialize_faults(self, seed: Optional[int]) -> None:
        """Initialize fault objects from configuration."""
        fault_classes = {
            ControlFaultType.SHORT_CYCLING: ShortCyclingFault,
            ControlFaultType.COMM_DROPOUT: CommDropoutFault,
            ControlFaultType.CONTROLLER_SAT: ControllerSaturationFault,
            ControlFaultType.DEADTIME_ISSUE: DeadtimeFault,
            ControlFaultType.CASCADE_FAILURE: CascadeFailureFault,
            ControlFaultType.LOOP_INSTABILITY: LoopInstabilityFault,
            ControlFaultType.SETPOINT_DRIFT: SetpointDriftFault,
            ControlFaultType.FEEDBACK_LOSS: FeedbackLossFault
        }
        
        for fault_config in self.config.fault_configs:
            fault_class = fault_classes.get(fault_config.fault_type)
            if fault_class:
                fault_obj = fault_class(fault_config, seed)
                self.faults.append(fault_obj)
    
    def update(self, control_signal: float, process_value: float, 
              setpoint: float, dt: float, sim_time: float) -> Tuple[float, float]:
        """
        Update control system with fault injection.
        
        Args:
            control_signal: Current control output
            process_value: Current process variable
            setpoint: Current setpoint
            dt: Time step (seconds)
            sim_time: Current simulation time (seconds)
            
        Returns:
            Tuple of (modified_control_signal, modified_setpoint)
        """
        modified_signal = control_signal
        modified_setpoint = setpoint
        
        # Apply all active faults
        for fault in self.faults:
            if fault.active:
                modified_signal, modified_setpoint, diag = fault.apply_fault(
                    modified_signal, process_value, modified_setpoint, dt, sim_time)
        
        # Update performance metrics
        self._update_performance_metrics(modified_signal, sim_time)
        
        self.last_update_time = sim_time
        
        return modified_signal, modified_setpoint
    
    def _update_performance_metrics(self, control_signal: float, sim_time: float) -> None:
        """Update performance tracking metrics."""
        # Update metrics based on control behavior
        if control_signal >= 95.0:
            self.performance_metrics['saturation_time'] += 1
        
        # Additional metrics updated by individual faults
        for fault in self.faults:
            if fault.active and hasattr(fault, 'fault_state'):
                if fault.config.fault_type == ControlFaultType.SHORT_CYCLING:
                    if 'cycle_count' in fault.fault_state:
                        self.performance_metrics['cycle_count'] = fault.fault_state['cycle_count']
                
                elif fault.config.fault_type == ControlFaultType.COMM_DROPOUT:
                    if 'dropout_count' in fault.fault_state:
                        self.performance_metrics['dropout_count'] = fault.fault_state['dropout_count']
    
    def inject_fault(self, fault_type: ControlFaultType, 
                    config: Optional[ControlFaultConfig] = None,
                    sim_time: float = 0.0) -> bool:
        """
        Inject a fault for testing/scenario purposes.
        
        Args:
            fault_type: Type of fault to inject
            config: Optional fault configuration (uses default if None)
            sim_time: Current simulation time
            
        Returns:
            True if fault was successfully injected
        """
        # Find existing fault of this type
        for fault in self.faults:
            if fault.config.fault_type == fault_type:
                fault.activate(sim_time)
                self._log_fault_event("INJECTED", fault_type, sim_time)
                return True
        
        return False
    
    def clear_fault(self, fault_type: ControlFaultType, sim_time: float = 0.0) -> bool:
        """Clear a specific fault type."""
        for fault in self.faults:
            if fault.config.fault_type == fault_type and fault.active:
                fault.deactivate()
                self._log_fault_event("CLEARED", fault_type, sim_time)
                return True
        return False
    
    def clear_all_faults(self, sim_time: float = 0.0) -> None:
        """Clear all active faults."""
        for fault in self.faults:
            if fault.active:
                fault.deactivate()
                self._log_fault_event("CLEARED", fault.config.fault_type, sim_time)
    
    def get_active_faults(self) -> List[ControlFaultType]:
        """Get list of currently active fault types."""
        return [fault.config.fault_type for fault in self.faults if fault.active]
    
    def get_system_state(self) -> Dict[str, Any]:
        """Get comprehensive control system state for diagnostics."""
        return {
            'system_id': self.system_id,
            'system_type': self.config.system_type,
            'location': self.config.location,
            'active_faults': [f.value for f in self.get_active_faults()],
            'fault_states': [f.get_fault_state() for f in self.faults],
            'performance_metrics': self.performance_metrics,
            'last_update_time': self.last_update_time
        }
    
    def _log_fault_event(self, event: str, fault_type: ControlFaultType, 
                        sim_time: float) -> None:
        """Log fault events for analysis."""
        self.fault_history.append({
            'timestamp': sim_time,
            'system_id': self.system_id,
            'event': event,
            'fault_type': fault_type.value,
            'performance_metrics': self.performance_metrics.copy()
        })


def create_default_control_system_config() -> ControlSystemConfig:
    """Create default control system configuration."""
    return ControlSystemConfig(
        system_id="PRIMARY_CONTROL_LOOP",
        system_type="pid_controller",
        location="primary_loop",
        enable_faults=True,
        fault_configs=[
            ControlFaultConfig(
                fault_type=ControlFaultType.SHORT_CYCLING,
                cycle_time_threshold_s=300.0,
                short_cycle_ratio=0.3
            ),
            ControlFaultConfig(
                fault_type=ControlFaultType.COMM_DROPOUT,
                dropout_probability=0.0001,
                dropout_duration_s=30.0
            ),
            ControlFaultConfig(
                fault_type=ControlFaultType.CONTROLLER_SAT,
                saturation_threshold=95.0,
                saturation_duration_s=120.0
            )
        ]
    )


def create_test_scenario_config() -> ControlSystemConfig:
    """Create control system configuration for fault testing scenarios."""
    return ControlSystemConfig(
        system_id="TEST_CONTROL_LOOP",
        system_type="pid_controller",
        location="test_loop",
        enable_faults=True,
        fault_configs=[
            ControlFaultConfig(
                fault_type=ControlFaultType.SHORT_CYCLING,
                cycle_time_threshold_s=60.0,  # Shorter for demo
                short_cycle_ratio=0.2
            ),
            ControlFaultConfig(
                fault_type=ControlFaultType.LOOP_INSTABILITY,
                instability_gain=2.0,
                oscillation_period_s=300.0
            ),
            ControlFaultConfig(
                fault_type=ControlFaultType.CASCADE_FAILURE,
                cascade_probability=0.5,  # Higher for demo
                cascade_delay_s=180.0
            )
        ]
    )