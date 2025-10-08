# sim/actuator_faults.py
"""
Professional Actuator Fault Simulation Module for BAS Data Center Systems

Comprehensive actuator fault modeling for building automation troubleshooting:
- Stuck valve/damper (position doesn't respond to commands)
- Valve backlash (hysteresis in positioning)
- Actuator degradation (reduced response speed, accuracy loss)
- Partial failure (limited range of motion)
- Oscillation (unstable actuator hunting behavior)

Engineering Implementation:
- Realistic actuator dynamics with fault injection
- Configurable fault parameters for various scenarios
- Professional actuator modeling for HVAC systems
- Integration with CRAC unit control systems
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Tuple
from enum import Enum
import random
import math
from abc import ABC, abstractmethod


class ActuatorFaultType(Enum):
    """Types of actuator faults that can be simulated."""
    STUCK = "stuck"                        # Actuator stuck at position
    BACKLASH = "backlash"                  # Hysteresis in positioning
    DEGRADATION = "degradation"            # Reduced response/accuracy
    PARTIAL_FAILURE = "partial_failure"    # Limited range of motion
    OSCILLATION = "oscillation"            # Unstable hunting behavior
    SLOW_RESPONSE = "slow_response"        # Increased response time
    POSITION_ERROR = "position_error"      # Systematic position errors
    STICTION = "stiction"                  # Static friction at startup


@dataclass
class ActuatorFaultConfig:
    """Configuration for individual actuator fault parameters."""
    fault_type: ActuatorFaultType
    severity: float = 1.0                  # Fault severity multiplier (0-1)
    progression_rate: float = 1.0          # Rate of fault development
    
    # Stuck actuator parameters
    stuck_position: Optional[float] = None  # Position to stick at (None = current)
    stick_probability: float = 0.001       # Probability per timestep
    
    # Backlash parameters
    backlash_deadband: float = 2.0         # Deadband percentage
    hysteresis_factor: float = 0.5         # Hysteresis strength
    
    # Degradation parameters
    response_degradation: float = 0.5      # Response time multiplier
    accuracy_loss: float = 1.0             # Accuracy degradation (%)
    
    # Partial failure parameters
    min_position: float = 0.0              # Minimum achievable position
    max_position: float = 100.0            # Maximum achievable position
    failure_rate: float = 0.1              # Range reduction rate (%/hour)
    
    # Oscillation parameters
    oscillation_amplitude: float = 5.0     # Oscillation amplitude (%)
    oscillation_frequency: float = 0.1     # Oscillation frequency (Hz)
    hunt_threshold: float = 1.0            # Threshold for hunting behavior
    
    # Slow response parameters
    response_multiplier: float = 2.0       # Response time multiplier
    
    # Position error parameters
    position_bias: float = 0.0             # Systematic position bias (%)
    
    # Stiction parameters
    breakaway_threshold: float = 5.0       # Minimum command change to move (%)
    static_friction: float = 2.0           # Static friction force (%)


class ActuatorFault(ABC):
    """Abstract base class for actuator fault implementations."""
    
    def __init__(self, config: ActuatorFaultConfig, seed: Optional[int] = None):
        self.config = config
        self.active = False
        self.start_time: Optional[float] = None
        self.random = random.Random(seed)
        self.fault_state: Dict[str, Any] = {}
        
    @abstractmethod
    def apply_fault(self, command: float, current_position: float, 
                   dt: float, sim_time: float) -> Tuple[float, Dict[str, Any]]:
        """
        Apply fault to actuator response.
        
        Args:
            command: Commanded position (0-100%)
            current_position: Current actuator position (0-100%)
            dt: Time step (seconds)
            sim_time: Current simulation time (seconds)
            
        Returns:
            Tuple of (actual_position, fault_diagnostics)
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


class StuckActuatorFault(ActuatorFault):
    """Stuck actuator fault - actuator frozen at specific position."""
    
    def __init__(self, config: ActuatorFaultConfig, seed: Optional[int] = None):
        super().__init__(config, seed)
        self.stuck_at_position: Optional[float] = None
        self.is_stuck = False
        
    def apply_fault(self, command: float, current_position: float, 
                   dt: float, sim_time: float) -> Tuple[float, Dict[str, Any]]:
        if not self.active:
            return current_position, {}
            
        # Check for sticking event
        if not self.is_stuck:
            stick_prob = (self.config.stick_probability * 
                         self.config.severity * dt)
            
            if self.random.random() < stick_prob:
                self.is_stuck = True
                self.stuck_at_position = (self.config.stuck_position 
                                        if self.config.stuck_position is not None 
                                        else current_position)
                
        if self.is_stuck and self.stuck_at_position is not None:
            self.fault_state = {
                'stuck_position': self.stuck_at_position,
                'command_error': abs(command - self.stuck_at_position)
            }
            return self.stuck_at_position, self.fault_state
            
        return current_position, {}


class BacklashFault(ActuatorFault):
    """Backlash fault - hysteresis in actuator positioning."""
    
    def __init__(self, config: ActuatorFaultConfig, seed: Optional[int] = None):
        super().__init__(config, seed)
        self.last_command = 0.0
        self.command_direction = 0
        self.deadband_offset = 0.0
        
    def apply_fault(self, command: float, current_position: float, 
                   dt: float, sim_time: float) -> Tuple[float, Dict[str, Any]]:
        if not self.active:
            return current_position, {}
            
        # Determine command direction
        command_change = command - self.last_command
        if abs(command_change) > 0.1:  # Minimum change threshold
            new_direction = 1 if command_change > 0 else -1
            
            # Check for direction reversal
            if new_direction != self.command_direction:
                self.command_direction = new_direction
                # Apply deadband offset based on direction
                deadband = (self.config.backlash_deadband * 
                          self.config.severity)
                self.deadband_offset = deadband * new_direction
        
        self.last_command = command
        
        # Apply hysteresis effect
        effective_command = command - self.deadband_offset
        effective_command = max(0.0, min(100.0, effective_command))
        
        # Apply hysteresis factor to position response
        hysteresis = self.config.hysteresis_factor * self.config.severity
        position_response = (current_position * hysteresis + 
                           effective_command * (1 - hysteresis))
        
        self.fault_state = {
            'deadband_offset': self.deadband_offset,
            'effective_command': effective_command,
            'position_error': abs(command - current_position)
        }
        
        return position_response, self.fault_state


class DegradationFault(ActuatorFault):
    """Actuator degradation fault - reduced response speed and accuracy."""
    
    def apply_fault(self, command: float, current_position: float, 
                   dt: float, sim_time: float) -> Tuple[float, Dict[str, Any]]:
        if not self.active or self.start_time is None:
            return current_position, {}
            
        # Calculate degradation based on fault progression
        elapsed_hours = (sim_time - self.start_time) / 3600.0
        
        # Progressive degradation over time
        degradation_factor = min(1.0, elapsed_hours * 
                               self.config.progression_rate * 0.1)
        
        # Apply response degradation (slower response)
        response_reduction = (self.config.response_degradation * 
                            degradation_factor * self.config.severity)
        
        # Effective response is slower
        position_change = command - current_position
        reduced_response = position_change * (1.0 - response_reduction)
        new_position = current_position + reduced_response
        
        # Apply accuracy loss (position error)
        accuracy_error = (self.config.accuracy_loss * 
                         degradation_factor * self.config.severity)
        
        if accuracy_error > 0:
            error_amplitude = accuracy_error * 0.5
            position_noise = self.random.uniform(-error_amplitude, error_amplitude)
            new_position += position_noise
        
        new_position = max(0.0, min(100.0, new_position))
        
        self.fault_state = {
            'degradation_factor': degradation_factor,
            'response_reduction': response_reduction,
            'accuracy_error': accuracy_error,
            'position_error': abs(command - new_position)
        }
        
        return new_position, self.fault_state


class PartialFailureFault(ActuatorFault):
    """Partial failure fault - limited range of motion."""
    
    def __init__(self, config: ActuatorFaultConfig, seed: Optional[int] = None):
        super().__init__(config, seed)
        self.current_min = 0.0
        self.current_max = 100.0
        
    def apply_fault(self, command: float, current_position: float, 
                   dt: float, sim_time: float) -> Tuple[float, Dict[str, Any]]:
        if not self.active or self.start_time is None:
            return current_position, {}
            
        # Calculate range reduction over time
        elapsed_hours = (sim_time - self.start_time) / 3600.0
        dt_hours = dt / 3600.0
        
        # Progressive range reduction
        range_reduction = (self.config.failure_rate * dt_hours * 
                          self.config.severity)
        
        # Reduce range symmetrically
        self.current_min += range_reduction / 2
        self.current_max -= range_reduction / 2
        
        # Ensure valid range
        self.current_min = max(self.config.min_position, self.current_min)
        self.current_max = min(self.config.max_position, self.current_max)
        
        if self.current_min >= self.current_max:
            self.current_max = self.current_min + 1.0
        
        # Constrain position to available range
        limited_position = max(self.current_min, 
                             min(self.current_max, current_position))
        
        # Constrain command to available range
        limited_command = max(self.current_min, 
                            min(self.current_max, command))
        
        self.fault_state = {
            'available_min': self.current_min,
            'available_max': self.current_max,
            'range_percentage': (self.current_max - self.current_min),
            'command_limited': command != limited_command
        }
        
        return limited_position, self.fault_state


class OscillationFault(ActuatorFault):
    """Oscillation fault - unstable actuator hunting behavior."""
    
    def __init__(self, config: ActuatorFaultConfig, seed: Optional[int] = None):
        super().__init__(config, seed)
        self.oscillation_phase = 0.0
        self.last_command = 0.0
        self.hunting_active = False
        
    def apply_fault(self, command: float, current_position: float, 
                   dt: float, sim_time: float) -> Tuple[float, Dict[str, Any]]:
        if not self.active:
            return current_position, {}
            
        # Check if hunting should be active
        command_change = abs(command - self.last_command)
        if command_change > self.config.hunt_threshold:
            self.hunting_active = True
        elif command_change < 0.1:  # Small threshold for settling
            # Gradually reduce hunting
            self.hunting_active = self.random.random() < 0.9
            
        self.last_command = command
        
        if self.hunting_active:
            # Generate oscillation
            self.oscillation_phase += (2 * math.pi * 
                                     self.config.oscillation_frequency * dt)
            
            oscillation = (self.config.oscillation_amplitude * 
                         self.config.severity * 
                         math.sin(self.oscillation_phase))
            
            oscillated_position = current_position + oscillation
            oscillated_position = max(0.0, min(100.0, oscillated_position))
            
            self.fault_state = {
                'hunting_active': self.hunting_active,
                'oscillation_amplitude': oscillation,
                'oscillation_phase': self.oscillation_phase,
                'position_deviation': abs(oscillation)
            }
            
            return oscillated_position, self.fault_state
        
        return current_position, {}


class SlowResponseFault(ActuatorFault):
    """Slow response fault - increased actuator response time."""
    
    def apply_fault(self, command: float, current_position: float, 
                   dt: float, sim_time: float) -> Tuple[float, Dict[str, Any]]:
        if not self.active:
            return current_position, {}
            
        # Apply response time multiplier
        response_factor = 1.0 / (self.config.response_multiplier * 
                               self.config.severity)
        
        # Reduce response speed
        position_change = command - current_position
        reduced_change = position_change * response_factor
        new_position = current_position + reduced_change
        
        new_position = max(0.0, min(100.0, new_position))
        
        self.fault_state = {
            'response_factor': response_factor,
            'response_multiplier': self.config.response_multiplier,
            'settling_time': abs(position_change) / max(abs(reduced_change), 0.001)
        }
        
        return new_position, self.fault_state


class PositionErrorFault(ActuatorFault):
    """Position error fault - systematic position errors."""
    
    def apply_fault(self, command: float, current_position: float, 
                   dt: float, sim_time: float) -> Tuple[float, Dict[str, Any]]:
        if not self.active:
            return current_position, {}
            
        # Apply systematic bias
        bias = self.config.position_bias * self.config.severity
        biased_position = current_position + bias
        
        biased_position = max(0.0, min(100.0, biased_position))
        
        self.fault_state = {
            'position_bias': bias,
            'true_position': current_position,
            'indicated_position': biased_position
        }
        
        return biased_position, self.fault_state


class StictionFault(ActuatorFault):
    """Stiction fault - static friction preventing small movements."""
    
    def __init__(self, config: ActuatorFaultConfig, seed: Optional[int] = None):
        super().__init__(config, seed)
        self.last_position = 0.0
        self.stuck_due_to_stiction = False
        self.accumulated_command_change = 0.0
        
    def apply_fault(self, command: float, current_position: float, 
                   dt: float, sim_time: float) -> Tuple[float, Dict[str, Any]]:
        if not self.active:
            return current_position, {}
            
        command_change = abs(command - self.last_position)
        self.accumulated_command_change += command_change
        
        # Check if static friction is overcome
        breakaway_force = (self.config.breakaway_threshold * 
                          self.config.severity)
        
        if self.accumulated_command_change >= breakaway_force:
            # Overcome stiction, allow movement
            self.stuck_due_to_stiction = False
            self.accumulated_command_change = 0.0
            
            # Apply some resistance to movement
            friction_resistance = (self.config.static_friction * 
                                 self.config.severity * 0.1)
            
            position_change = command - current_position
            if abs(position_change) > friction_resistance:
                if position_change > 0:
                    new_position = current_position + max(0, position_change - friction_resistance)
                else:
                    new_position = current_position + min(0, position_change + friction_resistance)
            else:
                new_position = current_position
                self.stuck_due_to_stiction = True
        else:
            # Stuck due to stiction
            self.stuck_due_to_stiction = True
            new_position = current_position
        
        new_position = max(0.0, min(100.0, new_position))
        self.last_position = new_position
        
        self.fault_state = {
            'stuck_due_to_stiction': self.stuck_due_to_stiction,
            'accumulated_command_change': self.accumulated_command_change,
            'breakaway_threshold': breakaway_force,
            'static_friction': self.config.static_friction
        }
        
        return new_position, self.fault_state


@dataclass
class ActuatorConfig:
    """Configuration for an actuator with fault simulation capabilities."""
    actuator_id: str
    actuator_type: str = "damper"          # damper, valve, fan_speed, etc.
    location: str = "crac_unit"            # Physical location description
    normal_range: tuple = (0.0, 100.0)    # Normal operating range (%)
    response_time_s: float = 60.0          # Actuator response time constant
    resolution: float = 1.0               # Position resolution (%)
    
    # Fault simulation parameters
    enable_faults: bool = True
    fault_configs: List[ActuatorFaultConfig] = field(default_factory=list)


class ActuatorModel:
    """
    Professional actuator model with comprehensive fault simulation.
    
    Features:
    - Multiple simultaneous fault types
    - Realistic actuator response dynamics
    - Professional fault injection capabilities
    - Comprehensive state tracking for diagnostics
    
    Engineering Model:
    - First-order lag response: tau * dy/dt + y = u
    - Fault injection modifies response characteristics
    - Position feedback with configurable resolution
    """
    
    def __init__(self, config: ActuatorConfig, seed: Optional[int] = None):
        self.config = config
        self.actuator_id = config.actuator_id
        
        # Actuator state
        self.command = 0.0                  # Commanded position (%)
        self.position = 0.0                 # Actual position (%)
        self.feedback = 0.0                 # Position feedback (%)
        
        # Response dynamics
        self.response_time_s = config.response_time_s
        
        # Fault simulation
        self.faults: List[ActuatorFault] = []
        self.fault_history: List[Dict] = []
        
        # Random seed for deterministic testing
        self._random = random.Random(seed)
        
        # Initialize fault objects
        self._initialize_faults(seed)
        
        # Diagnostics
        self.last_update_time = 0.0
        self.position_history: List[float] = []
        self.command_history: List[float] = []
        self.max_history = 100
        
    def _initialize_faults(self, seed: Optional[int]) -> None:
        """Initialize fault objects from configuration."""
        fault_classes = {
            ActuatorFaultType.STUCK: StuckActuatorFault,
            ActuatorFaultType.BACKLASH: BacklashFault,
            ActuatorFaultType.DEGRADATION: DegradationFault,
            ActuatorFaultType.PARTIAL_FAILURE: PartialFailureFault,
            ActuatorFaultType.OSCILLATION: OscillationFault,
            ActuatorFaultType.SLOW_RESPONSE: SlowResponseFault,
            ActuatorFaultType.POSITION_ERROR: PositionErrorFault,
            ActuatorFaultType.STICTION: StictionFault
        }
        
        for fault_config in self.config.fault_configs:
            fault_class = fault_classes.get(fault_config.fault_type)
            if fault_class:
                fault_obj = fault_class(fault_config, seed)
                self.faults.append(fault_obj)
    
    def update(self, command: float, dt: float, sim_time: float) -> None:
        """
        Update actuator position with realistic response and fault injection.
        
        Args:
            command: Commanded position (0-100%)
            dt: Time step (seconds)
            sim_time: Current simulation time (seconds)
        """
        self.command = max(0.0, min(100.0, command))
        
        # Apply first-order lag response (realistic actuator dynamics)
        if self.response_time_s > 0:
            alpha = dt / (self.response_time_s + dt)
            ideal_position = self.position + alpha * (self.command - self.position)
        else:
            ideal_position = self.command
        
        # Apply all active faults
        actual_position = ideal_position
        fault_diagnostics = {}
        
        for fault in self.faults:
            if fault.active:
                actual_position, diag = fault.apply_fault(
                    self.command, actual_position, dt, sim_time)
                fault_diagnostics[fault.config.fault_type.value] = diag
        
        # Apply position resolution limitations
        if self.config.resolution > 0:
            actual_position = round(actual_position / self.config.resolution) * self.config.resolution
        
        # Ensure position is within valid range
        actual_position = max(self.config.normal_range[0], 
                            min(self.config.normal_range[1], actual_position))
        
        self.position = actual_position
        self.feedback = actual_position  # Assume perfect feedback for now
        
        # Update diagnostics
        self.last_update_time = sim_time
        self.position_history.append(self.position)
        self.command_history.append(self.command)
        
        if len(self.position_history) > self.max_history:
            self.position_history.pop(0)
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)
    
    def inject_fault(self, fault_type: ActuatorFaultType, 
                    config: Optional[ActuatorFaultConfig] = None,
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
        
        # Create new fault if configuration provided
        if config is not None:
            fault_classes = {
                ActuatorFaultType.STUCK: StuckActuatorFault,
                ActuatorFaultType.BACKLASH: BacklashFault,
                ActuatorFaultType.DEGRADATION: DegradationFault,
                ActuatorFaultType.PARTIAL_FAILURE: PartialFailureFault,
                ActuatorFaultType.OSCILLATION: OscillationFault,
                ActuatorFaultType.SLOW_RESPONSE: SlowResponseFault,
                ActuatorFaultType.POSITION_ERROR: PositionErrorFault,
                ActuatorFaultType.STICTION: StictionFault
            }
            
            fault_class = fault_classes.get(fault_type)
            if fault_class:
                fault = fault_class(config)
                fault.activate(sim_time)
                self.faults.append(fault)
                self._log_fault_event("INJECTED", fault_type, sim_time)
                return True
        
        return False
    
    def clear_fault(self, fault_type: ActuatorFaultType, sim_time: float = 0.0) -> bool:
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
    
    def get_active_faults(self) -> List[ActuatorFaultType]:
        """Get list of currently active fault types."""
        return [fault.config.fault_type for fault in self.faults if fault.active]
    
    def get_actuator_state(self) -> Dict[str, Any]:
        """Get comprehensive actuator state for diagnostics."""
        return {
            'actuator_id': self.actuator_id,
            'actuator_type': self.config.actuator_type,
            'location': self.config.location,
            'command': self.command,
            'position': self.position,
            'feedback': self.feedback,
            'position_error': abs(self.command - self.position),
            'active_faults': [f.value for f in self.get_active_faults()],
            'fault_states': [f.get_fault_state() for f in self.faults],
            'position_history': self.position_history[-10:],  # Last 10 positions
            'command_history': self.command_history[-10:],    # Last 10 commands
            'last_update_time': self.last_update_time,
            'response_time_s': self.response_time_s,
            'resolution': self.config.resolution
        }
    
    def _log_fault_event(self, event: str, fault_type: ActuatorFaultType, 
                        sim_time: float) -> None:
        """Log fault events for analysis."""
        self.fault_history.append({
            'timestamp': sim_time,
            'actuator_id': self.actuator_id,
            'event': event,
            'fault_type': fault_type.value,
            'command': self.command,
            'position': self.position,
            'position_error': abs(self.command - self.position)
        })


def create_default_actuator_configs() -> List[ActuatorConfig]:
    """Create default actuator configurations for CRAC units."""
    configs = []
    
    # CRAC unit damper actuators
    for i in range(3):
        actuator_config = ActuatorConfig(
            actuator_id=f"CRAC_{i+1:02d}_DAMPER",
            actuator_type="damper",
            location=f"CRAC-{i+1:02d}",
            normal_range=(0.0, 100.0),
            response_time_s=90.0,  # Typical HVAC damper response
            resolution=1.0,
            enable_faults=True,
            fault_configs=[
                # Stiction fault (common in HVAC)
                ActuatorFaultConfig(
                    fault_type=ActuatorFaultType.STICTION,
                    breakaway_threshold=3.0,
                    static_friction=1.5
                ),
                # Backlash fault
                ActuatorFaultConfig(
                    fault_type=ActuatorFaultType.BACKLASH,
                    backlash_deadband=2.0,
                    hysteresis_factor=0.3
                ),
                # Degradation fault
                ActuatorFaultConfig(
                    fault_type=ActuatorFaultType.DEGRADATION,
                    response_degradation=0.3,
                    accuracy_loss=2.0
                )
            ]
        )
        configs.append(actuator_config)
    
    return configs


def create_test_scenario_configs() -> List[ActuatorConfig]:
    """Create actuator configurations for fault testing scenarios."""
    # High-fault scenario for demonstration
    test_config = ActuatorConfig(
        actuator_id="TEST_DAMPER_01",
        actuator_type="damper",
        location="Test_CRAC",
        normal_range=(0.0, 100.0),
        response_time_s=30.0,
        resolution=1.0,
        enable_faults=True,
        fault_configs=[
            ActuatorFaultConfig(
                fault_type=ActuatorFaultType.STUCK,
                stick_probability=0.01,  # Higher fault rate for demo
                stuck_position=50.0
            ),
            ActuatorFaultConfig(
                fault_type=ActuatorFaultType.OSCILLATION,
                oscillation_amplitude=8.0,  # Aggressive oscillation
                oscillation_frequency=0.2,
                hunt_threshold=2.0
            ),
            ActuatorFaultConfig(
                fault_type=ActuatorFaultType.PARTIAL_FAILURE,
                failure_rate=0.5,  # Faster degradation for demo
                min_position=10.0,
                max_position=90.0
            )
        ]
    )
    
    return [test_config]