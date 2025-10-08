# sim/sensor_faults.py
"""
Professional Sensor Fault Simulation Module for BAS Data Center Systems

Comprehensive sensor fault modeling for building automation troubleshooting:
- Sensor drift (gradual accuracy degradation)
- Sensor bias (systematic offset errors)
- Intermittent faults (dropouts, noise injection)
- Stuck sensor (frozen readings)
- Calibration drift (gain/offset changes)

Engineering Implementation:
- Realistic fault progression rates
- Configurable fault parameters
- Multiple fault types can occur simultaneously
- Professional fault injection for testing scenarios
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from enum import Enum
import random
import math
from abc import ABC, abstractmethod


class SensorFaultType(Enum):
    """Types of sensor faults that can be simulated."""
    DRIFT = "drift"                    # Gradual accuracy degradation
    BIAS = "bias"                      # Systematic offset error
    INTERMITTENT = "intermittent"      # Random dropouts/bad readings
    STUCK = "stuck"                    # Sensor frozen at value
    CALIBRATION_DRIFT = "cal_drift"    # Gain/offset changes over time
    NOISE = "noise"                    # Electronic noise injection
    SCALING_ERROR = "scaling"          # Incorrect engineering unit conversion


@dataclass
class SensorFaultConfig:
    """Configuration for individual sensor fault parameters."""
    fault_type: SensorFaultType
    severity: float = 1.0              # Fault severity multiplier (0-1)
    progression_rate: float = 1.0      # Rate of fault development
    
    # Drift-specific parameters
    drift_rate_per_hour: float = 0.01  # °C/hour drift rate
    max_drift: float = 2.0             # Maximum total drift (°C)
    
    # Bias-specific parameters
    bias_offset: float = 0.0           # Constant bias offset (°C)
    
    # Intermittent fault parameters
    dropout_probability: float = 0.01   # Probability per timestep
    dropout_duration_s: float = 30.0    # Average dropout duration
    bad_reading_range: tuple = (-10.0, 60.0)  # Range for bad readings
    
    # Stuck sensor parameters
    stuck_value: Optional[float] = None  # Value to stick at (None = current)
    
    # Calibration drift parameters
    gain_drift_rate: float = 0.001     # Gain drift per hour (fraction)
    offset_drift_rate: float = 0.01    # Offset drift per hour (°C)
    
    # Noise parameters
    noise_amplitude: float = 0.1       # RMS noise amplitude (°C)
    noise_frequency: float = 1.0       # Noise update frequency (Hz)
    
    # Scaling error parameters
    scale_factor_error: float = 0.0    # Multiplicative scaling error


class SensorFault(ABC):
    """Abstract base class for sensor fault implementations."""
    
    def __init__(self, config: SensorFaultConfig, seed: Optional[int] = None):
        self.config = config
        self.active = False
        self.start_time: Optional[float] = None
        self.accumulated_drift = 0.0
        self.random = random.Random(seed)
        
    @abstractmethod
    def apply_fault(self, true_value: float, sim_time: float) -> float:
        """Apply fault to sensor reading."""
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
            'accumulated_drift': self.accumulated_drift
        }


class DriftFault(SensorFault):
    """Sensor drift fault - gradual accuracy degradation over time."""
    
    def apply_fault(self, true_value: float, sim_time: float) -> float:
        if not self.active or self.start_time is None:
            return true_value
            
        # Calculate elapsed time in hours
        elapsed_hours = (sim_time - self.start_time) / 3600.0
        
        # Calculate cumulative drift
        drift_increment = (self.config.drift_rate_per_hour * 
                          self.config.progression_rate * 
                          self.config.severity)
        
        # Apply non-linear progression (square root for realistic drift)
        time_factor = math.sqrt(elapsed_hours) if elapsed_hours > 0 else 0
        total_drift = drift_increment * time_factor
        
        # Limit maximum drift
        total_drift = min(total_drift, self.config.max_drift)
        
        self.accumulated_drift = total_drift
        
        # Add random direction for drift
        drift_direction = 1 if self.random.random() > 0.5 else -1
        
        return true_value + (total_drift * drift_direction)


class BiasFault(SensorFault):
    """Sensor bias fault - systematic offset error."""
    
    def apply_fault(self, true_value: float, sim_time: float) -> float:
        if not self.active:
            return true_value
            
        bias = self.config.bias_offset * self.config.severity
        return true_value + bias


class IntermittentFault(SensorFault):
    """Intermittent sensor fault - random dropouts and bad readings."""
    
    def __init__(self, config: SensorFaultConfig, seed: Optional[int] = None):
        super().__init__(config, seed)
        self.in_dropout = False
        self.dropout_end_time = 0.0
        self.last_good_value = 0.0
        
    def apply_fault(self, true_value: float, sim_time: float) -> float:
        if not self.active:
            return true_value
            
        # Check if currently in dropout
        if self.in_dropout:
            if sim_time >= self.dropout_end_time:
                self.in_dropout = False
            else:
                # Return bad reading during dropout
                min_val, max_val = self.config.bad_reading_range
                return self.random.uniform(min_val, max_val)
        
        # Check for new dropout event
        dropout_prob = (self.config.dropout_probability * 
                       self.config.severity * 
                       self.config.progression_rate)
        
        if self.random.random() < dropout_prob:
            self.in_dropout = True
            duration_variation = self.random.uniform(0.5, 2.0)
            self.dropout_end_time = (sim_time + 
                                   self.config.dropout_duration_s * 
                                   duration_variation)
            
            # Return bad reading
            min_val, max_val = self.config.bad_reading_range
            return self.random.uniform(min_val, max_val)
        
        # Store good value for potential use
        self.last_good_value = true_value
        return true_value


class StuckFault(SensorFault):
    """Stuck sensor fault - sensor frozen at specific value."""
    
    def __init__(self, config: SensorFaultConfig, seed: Optional[int] = None):
        super().__init__(config, seed)
        self.stuck_at_value: Optional[float] = None
        
    def apply_fault(self, true_value: float, sim_time: float) -> float:
        if not self.active:
            return true_value
            
        # Set stuck value on first activation
        if self.stuck_at_value is None:
            self.stuck_at_value = (self.config.stuck_value 
                                 if self.config.stuck_value is not None 
                                 else true_value)
        
        return self.stuck_at_value


class CalibrationDriftFault(SensorFault):
    """Calibration drift fault - gain and offset changes over time."""
    
    def apply_fault(self, true_value: float, sim_time: float) -> float:
        if not self.active or self.start_time is None:
            return true_value
            
        # Calculate elapsed time in hours
        elapsed_hours = (sim_time - self.start_time) / 3600.0
        
        # Calculate gain drift (multiplicative error)
        gain_drift = (1.0 + self.config.gain_drift_rate * 
                     elapsed_hours * self.config.severity)
        
        # Calculate offset drift (additive error)
        offset_drift = (self.config.offset_drift_rate * 
                       elapsed_hours * self.config.severity)
        
        # Apply calibration errors
        return (true_value * gain_drift) + offset_drift


class NoiseFault(SensorFault):
    """Electronic noise injection fault."""
    
    def __init__(self, config: SensorFaultConfig, seed: Optional[int] = None):
        super().__init__(config, seed)
        self.last_noise_time = 0.0
        self.current_noise = 0.0
        
    def apply_fault(self, true_value: float, sim_time: float) -> float:
        if not self.active:
            return true_value
            
        # Update noise at specified frequency
        noise_interval = 1.0 / self.config.noise_frequency
        if sim_time - self.last_noise_time >= noise_interval:
            # Generate Gaussian noise
            self.current_noise = (self.random.gauss(0, self.config.noise_amplitude) * 
                                self.config.severity)
            self.last_noise_time = sim_time
            
        return true_value + self.current_noise


class ScalingErrorFault(SensorFault):
    """Scaling error fault - incorrect engineering unit conversion."""
    
    def apply_fault(self, true_value: float, sim_time: float) -> float:
        if not self.active:
            return true_value
            
        scale_factor = 1.0 + (self.config.scale_factor_error * self.config.severity)
        return true_value * scale_factor


@dataclass
class SensorConfig:
    """Configuration for a sensor with fault simulation capabilities."""
    sensor_id: str
    sensor_type: str = "temperature"    # temperature, humidity, pressure, etc.
    location: str = "zone"              # Physical location description
    normal_range: tuple = (18.0, 28.0)  # Normal operating range
    accuracy: float = 0.1               # Sensor accuracy (±°C)
    response_time_s: float = 30.0       # Sensor response time constant
    
    # Fault simulation parameters
    enable_faults: bool = True
    fault_configs: List[SensorFaultConfig] = field(default_factory=list)


class TemperatureSensor:
    """
    Professional temperature sensor model with comprehensive fault simulation.
    
    Features:
    - Multiple simultaneous fault types
    - Realistic sensor response dynamics
    - Professional fault injection capabilities
    - Comprehensive state tracking for diagnostics
    
    Engineering Model:
    - First-order lag response: tau * dy/dt + y = u
    - Fault injection after physical response
    - Multiple fault types can be active simultaneously
    """
    
    def __init__(self, config: SensorConfig, seed: Optional[int] = None):
        self.config = config
        self.sensor_id = config.sensor_id
        
        # Sensor state
        self.raw_value = 22.0               # Current sensor reading
        self.filtered_value = 22.0          # Filtered/processed reading
        self.true_value = 22.0              # Actual physical value
        
        # Response dynamics
        self.response_time_s = config.response_time_s
        
        # Fault simulation
        self.faults: List[SensorFault] = []
        self.fault_history: List[Dict] = []
        
        # Random seed for deterministic testing
        self._random = random.Random(seed)
        
        # Initialize fault objects
        self._initialize_faults(seed)
        
        # Diagnostics
        self.last_reading_time = 0.0
        self.reading_history: List[float] = []
        self.max_history = 100
        
    def _initialize_faults(self, seed: Optional[int]) -> None:
        """Initialize fault objects from configuration."""
        fault_classes = {
            SensorFaultType.DRIFT: DriftFault,
            SensorFaultType.BIAS: BiasFault,
            SensorFaultType.INTERMITTENT: IntermittentFault,
            SensorFaultType.STUCK: StuckFault,
            SensorFaultType.CALIBRATION_DRIFT: CalibrationDriftFault,
            SensorFaultType.NOISE: NoiseFault,
            SensorFaultType.SCALING_ERROR: ScalingErrorFault
        }
        
        for fault_config in self.config.fault_configs:
            fault_class = fault_classes.get(fault_config.fault_type)
            if fault_class:
                fault_obj = fault_class(fault_config, seed)
                self.faults.append(fault_obj)
    
    def update(self, true_temperature: float, dt: float, sim_time: float) -> None:
        """
        Update sensor reading with realistic response and fault injection.
        
        Args:
            true_temperature: Actual temperature value (°C)
            dt: Time step (seconds)
            sim_time: Current simulation time (seconds)
        """
        self.true_value = true_temperature
        
        # Apply first-order lag response (realistic sensor dynamics)
        if self.response_time_s > 0:
            alpha = dt / (self.response_time_s + dt)
            self.raw_value += alpha * (true_temperature - self.raw_value)
        else:
            self.raw_value = true_temperature
        
        # Apply all active faults
        faulted_value = self.raw_value
        for fault in self.faults:
            if fault.active:
                faulted_value = fault.apply_fault(faulted_value, sim_time)
        
        # Apply sensor accuracy limitations
        if self.config.accuracy > 0:
            quantization = self.config.accuracy / 2.0
            faulted_value = round(faulted_value / quantization) * quantization
        
        self.filtered_value = faulted_value
        
        # Update diagnostics
        self.last_reading_time = sim_time
        self.reading_history.append(self.filtered_value)
        if len(self.reading_history) > self.max_history:
            self.reading_history.pop(0)
    
    def inject_fault(self, fault_type: SensorFaultType, 
                    config: Optional[SensorFaultConfig] = None,
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
                SensorFaultType.DRIFT: DriftFault,
                SensorFaultType.BIAS: BiasFault,
                SensorFaultType.INTERMITTENT: IntermittentFault,
                SensorFaultType.STUCK: StuckFault,
                SensorFaultType.CALIBRATION_DRIFT: CalibrationDriftFault,
                SensorFaultType.NOISE: NoiseFault,
                SensorFaultType.SCALING_ERROR: ScalingErrorFault
            }
            
            fault_class = fault_classes.get(fault_type)
            if fault_class:
                fault = fault_class(config)
                fault.activate(sim_time)
                self.faults.append(fault)
                self._log_fault_event("INJECTED", fault_type, sim_time)
                return True
        
        return False
    
    def clear_fault(self, fault_type: SensorFaultType, sim_time: float = 0.0) -> bool:
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
    
    def get_active_faults(self) -> List[SensorFaultType]:
        """Get list of currently active fault types."""
        return [fault.config.fault_type for fault in self.faults if fault.active]
    
    def get_sensor_state(self) -> Dict[str, Any]:
        """Get comprehensive sensor state for diagnostics."""
        return {
            'sensor_id': self.sensor_id,
            'sensor_type': self.config.sensor_type,
            'location': self.config.location,
            'true_value': self.true_value,
            'raw_value': self.raw_value,
            'filtered_value': self.filtered_value,
            'active_faults': [f.value for f in self.get_active_faults()],
            'fault_states': [f.get_fault_state() for f in self.faults],
            'reading_history': self.reading_history[-10:],  # Last 10 readings
            'last_reading_time': self.last_reading_time,
            'response_time_s': self.response_time_s,
            'accuracy': self.config.accuracy
        }
    
    def _log_fault_event(self, event: str, fault_type: SensorFaultType, 
                        sim_time: float) -> None:
        """Log fault events for analysis."""
        self.fault_history.append({
            'timestamp': sim_time,
            'sensor_id': self.sensor_id,
            'event': event,
            'fault_type': fault_type.value,
            'current_reading': self.filtered_value,
            'true_value': self.true_value
        })


def create_default_sensor_configs() -> List[SensorConfig]:
    """Create default sensor configurations for data center zones."""
    configs = []
    
    # Zone temperature sensors
    for i in range(3):
        sensor_config = SensorConfig(
            sensor_id=f"TEMP_SENSOR_{i+1:02d}",
            sensor_type="temperature",
            location=f"Zone_{i+1}",
            normal_range=(20.0, 26.0),
            accuracy=0.1,
            response_time_s=30.0,
            enable_faults=True,
            fault_configs=[
                # Drift fault configuration
                SensorFaultConfig(
                    fault_type=SensorFaultType.DRIFT,
                    drift_rate_per_hour=0.02,
                    max_drift=1.0
                ),
                # Bias fault configuration  
                SensorFaultConfig(
                    fault_type=SensorFaultType.BIAS,
                    bias_offset=0.5
                ),
                # Intermittent fault configuration
                SensorFaultConfig(
                    fault_type=SensorFaultType.INTERMITTENT,
                    dropout_probability=0.001,
                    dropout_duration_s=15.0
                )
            ]
        )
        configs.append(sensor_config)
    
    return configs


def create_test_scenario_configs() -> List[SensorConfig]:
    """Create sensor configurations for fault testing scenarios."""
    # High-fault scenario for demonstration
    test_config = SensorConfig(
        sensor_id="TEST_TEMP_01",
        sensor_type="temperature",
        location="Test_Zone",
        normal_range=(20.0, 26.0),
        accuracy=0.1,
        response_time_s=10.0,
        enable_faults=True,
        fault_configs=[
            SensorFaultConfig(
                fault_type=SensorFaultType.DRIFT,
                drift_rate_per_hour=0.1,  # Aggressive drift for demo
                max_drift=2.0
            ),
            SensorFaultConfig(
                fault_type=SensorFaultType.NOISE,
                noise_amplitude=0.2,
                noise_frequency=2.0
            ),
            SensorFaultConfig(
                fault_type=SensorFaultType.INTERMITTENT,
                dropout_probability=0.01,  # Higher fault rate for demo
                dropout_duration_s=30.0
            )
        ]
    )
    
    return [test_config]