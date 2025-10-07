# diagnostics/engine.py
"""
Professional Diagnostic Engine for BAS Data Center Systems

Comprehensive diagnostic system featuring:
- Real-time fault detection and classification
- Advanced fault isolation algorithms
- Performance degradation tracking
- Predictive maintenance indicators
- Integration with existing alarm systems

Engineering Implementation:
- Multi-level diagnostic hierarchy (System -> Subsystem -> Component)
- Statistical analysis for fault detection
- Pattern recognition for intermittent faults
- Professional maintenance recommendations
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
import statistics
import math
from datetime import datetime, timedelta


class FaultSeverity(Enum):
    """Fault severity classification for prioritization."""
    CRITICAL = "critical"      # Immediate action required
    MAJOR = "major"           # Significant impact, action within hours
    MINOR = "minor"           # Performance degradation, plan maintenance
    WARNING = "warning"       # Early indicator, monitor closely
    INFO = "info"             # Informational, no action required


class DiagnosticCategory(Enum):
    """Categories for diagnostic analysis."""
    SENSOR = "sensor"              # Sensor-related issues
    ACTUATOR = "actuator"          # Actuator-related issues
    CONTROL = "control"            # Control system issues
    EQUIPMENT = "equipment"        # Equipment failures
    PERFORMANCE = "performance"    # Performance degradation
    COMMUNICATION = "communication" # Network/communication issues
    ENVIRONMENTAL = "environmental" # Environmental conditions


class DiagnosticStatus(Enum):
    """Status of diagnostic analysis."""
    NORMAL = "normal"              # No issues detected
    MONITORING = "monitoring"      # Potential issue, monitoring
    CONFIRMED = "confirmed"        # Fault confirmed
    INVESTIGATING = "investigating" # Under investigation
    RESOLVED = "resolved"          # Issue resolved


@dataclass
class DiagnosticResult:
    """Result of diagnostic analysis."""
    diagnostic_id: str
    timestamp: float
    category: DiagnosticCategory
    severity: FaultSeverity
    status: DiagnosticStatus
    
    # Diagnostic information
    title: str
    description: str
    component_id: str
    location: str
    
    # Measurements and thresholds
    measured_value: Optional[float] = None
    expected_value: Optional[float] = None
    threshold_value: Optional[float] = None
    deviation_percent: Optional[float] = None
    
    # Statistical analysis
    trend_direction: Optional[str] = None  # "increasing", "decreasing", "stable"
    confidence_level: float = 0.0         # 0-1 confidence in diagnosis
    
    # Recommendations
    recommended_actions: List[str] = field(default_factory=list)
    estimated_repair_time: Optional[str] = None
    maintenance_priority: Optional[str] = None
    
    # Additional context
    related_diagnostics: List[str] = field(default_factory=list)
    historical_occurrences: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'diagnostic_id': self.diagnostic_id,
            'timestamp': self.timestamp,
            'category': self.category.value,
            'severity': self.severity.value,
            'status': self.status.value,
            'title': self.title,
            'description': self.description,
            'component_id': self.component_id,
            'location': self.location,
            'measured_value': self.measured_value,
            'expected_value': self.expected_value,
            'threshold_value': self.threshold_value,
            'deviation_percent': self.deviation_percent,
            'trend_direction': self.trend_direction,
            'confidence_level': self.confidence_level,
            'recommended_actions': self.recommended_actions,
            'estimated_repair_time': self.estimated_repair_time,
            'maintenance_priority': self.maintenance_priority,
            'related_diagnostics': self.related_diagnostics,
            'historical_occurrences': self.historical_occurrences
        }


@dataclass
class DiagnosticRule:
    """Configuration for a diagnostic rule."""
    rule_id: str
    category: DiagnosticCategory
    title: str
    description: str
    
    # Evaluation function
    evaluator: Callable[[Dict[str, Any]], Optional[DiagnosticResult]]
    
    # Rule parameters
    enable: bool = True
    severity: FaultSeverity = FaultSeverity.WARNING
    confidence_threshold: float = 0.7
    
    # Timing parameters
    evaluation_interval_s: float = 60.0    # How often to evaluate
    confirmation_time_s: float = 300.0     # Time to confirm fault
    
    # Dependencies
    required_data: List[str] = field(default_factory=list)
    prerequisite_rules: List[str] = field(default_factory=list)


class DiagnosticEngine:
    """
    Professional diagnostic engine for BAS fault detection and analysis.
    
    Features:
    - Real-time fault detection with statistical analysis
    - Multi-level diagnostic hierarchy
    - Pattern recognition for intermittent faults
    - Performance trend analysis
    - Professional maintenance recommendations
    
    Integration:
    - Works with existing alarm systems
    - Consumes telemetry data from all system components
    - Provides structured diagnostic results
    """
    
    def __init__(self, seed: Optional[int] = None):
        self.diagnostic_rules: Dict[str, DiagnosticRule] = {}
        self.active_diagnostics: Dict[str, DiagnosticResult] = {}
        self.diagnostic_history: List[DiagnosticResult] = []
        
        # Data storage for analysis
        self.data_buffer: Dict[str, List[Tuple[float, Any]]] = {}
        self.buffer_max_size = 1000
        
        # Performance tracking
        self.system_performance_metrics = {
            'availability': 100.0,
            'efficiency': 100.0,
            'reliability': 100.0,
            'maintainability': 100.0
        }
        
        # Timing
        self.last_evaluation_time = 0.0
        
        # Initialize standard diagnostic rules
        self._initialize_standard_rules()
        
    def _initialize_standard_rules(self) -> None:
        """Initialize standard BAS diagnostic rules."""
        
        # Sensor drift detection
        self.register_rule(DiagnosticRule(
            rule_id="SENSOR_DRIFT_DETECTION",
            category=DiagnosticCategory.SENSOR,
            title="Temperature Sensor Drift",
            description="Detect gradual sensor accuracy degradation",
            evaluator=self._evaluate_sensor_drift,
            severity=FaultSeverity.MINOR,
            evaluation_interval_s=300.0,
            confirmation_time_s=1800.0,
            required_data=["sensor_readings", "reference_values"]
        ))
        
        # Equipment performance degradation
        self.register_rule(DiagnosticRule(
            rule_id="EQUIPMENT_PERFORMANCE_DEGRADATION",
            category=DiagnosticCategory.EQUIPMENT,
            title="CRAC Performance Degradation",
            description="Detect declining equipment efficiency",
            evaluator=self._evaluate_equipment_performance,
            severity=FaultSeverity.MAJOR,
            evaluation_interval_s=600.0,
            confirmation_time_s=3600.0,
            required_data=["crac_states", "cooling_efficiency"]
        ))
        
        # Control system instability
        self.register_rule(DiagnosticRule(
            rule_id="CONTROL_INSTABILITY",
            category=DiagnosticCategory.CONTROL,
            title="Control Loop Instability",
            description="Detect unstable control behavior",
            evaluator=self._evaluate_control_instability,
            severity=FaultSeverity.MAJOR,
            evaluation_interval_s=120.0,
            confirmation_time_s=600.0,
            required_data=["control_signals", "process_variables"]
        ))
        
        # Communication issues
        self.register_rule(DiagnosticRule(
            rule_id="COMMUNICATION_HEALTH",
            category=DiagnosticCategory.COMMUNICATION,
            title="Communication System Health",
            description="Monitor network communication reliability",
            evaluator=self._evaluate_communication_health,
            severity=FaultSeverity.MINOR,
            evaluation_interval_s=60.0,
            confirmation_time_s=300.0,
            required_data=["communication_stats"]
        ))
        
        # Energy efficiency analysis
        self.register_rule(DiagnosticRule(
            rule_id="ENERGY_EFFICIENCY_ANALYSIS",
            category=DiagnosticCategory.PERFORMANCE,
            title="Energy Efficiency Analysis",
            description="Monitor system energy performance",
            evaluator=self._evaluate_energy_efficiency,
            severity=FaultSeverity.WARNING,
            evaluation_interval_s=900.0,
            confirmation_time_s=3600.0,
            required_data=["energy_consumption", "cooling_output"]
        ))
    
    def register_rule(self, rule: DiagnosticRule) -> None:
        """Register a new diagnostic rule."""
        self.diagnostic_rules[rule.rule_id] = rule
    
    def update(self, system_data: Dict[str, Any], sim_time: float) -> List[DiagnosticResult]:
        """
        Update diagnostic engine with new system data.
        
        Args:
            system_data: Dictionary containing system telemetry
            sim_time: Current simulation time (seconds)
            
        Returns:
            List of new or updated diagnostic results
        """
        # Store data in buffer for trend analysis
        self._update_data_buffer(system_data, sim_time)
        
        # Evaluate diagnostic rules
        new_diagnostics = []
        
        for rule_id, rule in self.diagnostic_rules.items():
            if not rule.enable:
                continue
                
            # Check if it's time to evaluate this rule
            if (sim_time - self.last_evaluation_time) >= rule.evaluation_interval_s:
                
                # Check if required data is available
                if self._has_required_data(rule, system_data):
                    
                    # Evaluate the rule
                    diagnostic = rule.evaluator(system_data)
                    
                    if diagnostic is not None:
                        # Set common properties
                        diagnostic.timestamp = sim_time
                        diagnostic.category = rule.category
                        
                        # Check if this is a new or updated diagnostic
                        if diagnostic.diagnostic_id not in self.active_diagnostics:
                            self.active_diagnostics[diagnostic.diagnostic_id] = diagnostic
                            new_diagnostics.append(diagnostic)
                            self.diagnostic_history.append(diagnostic)
                        else:
                            # Update existing diagnostic
                            existing = self.active_diagnostics[diagnostic.diagnostic_id]
                            if self._should_update_diagnostic(existing, diagnostic):
                                self.active_diagnostics[diagnostic.diagnostic_id] = diagnostic
                                new_diagnostics.append(diagnostic)
        
        # Update system performance metrics
        self._update_performance_metrics(system_data, sim_time)
        
        self.last_evaluation_time = sim_time
        
        return new_diagnostics
    
    def _update_data_buffer(self, system_data: Dict[str, Any], sim_time: float) -> None:
        """Update data buffer for trend analysis."""
        for key, value in system_data.items():
            if key not in self.data_buffer:
                self.data_buffer[key] = []
            
            self.data_buffer[key].append((sim_time, value))
            
            # Limit buffer size
            if len(self.data_buffer[key]) > self.buffer_max_size:
                self.data_buffer[key] = self.data_buffer[key][-self.buffer_max_size//2:]
    
    def _has_required_data(self, rule: DiagnosticRule, system_data: Dict[str, Any]) -> bool:
        """Check if required data is available for rule evaluation."""
        for data_key in rule.required_data:
            if data_key not in system_data and data_key not in self.data_buffer:
                return False
        return True
    
    def _should_update_diagnostic(self, existing: DiagnosticResult, 
                                 new: DiagnosticResult) -> bool:
        """Determine if an existing diagnostic should be updated."""
        # Update if severity changed
        if existing.severity != new.severity:
            return True
        
        # Update if confidence significantly changed
        if abs(existing.confidence_level - new.confidence_level) > 0.1:
            return True
        
        # Update if measured value significantly changed
        if (existing.measured_value is not None and 
            new.measured_value is not None and
            abs(existing.measured_value - new.measured_value) > 
            0.1 * abs(existing.measured_value)):
            return True
        
        return False
    
    def _update_performance_metrics(self, system_data: Dict[str, Any], 
                                   sim_time: float) -> None:
        """Update overall system performance metrics."""
        # Calculate availability based on equipment status
        total_capacity = 0.0
        available_capacity = 0.0
        
        crac_states = system_data.get("crac_states", [])
        for crac in crac_states:
            total_capacity += crac.get("q_rated_kw", 0)
            if crac.get("status") == "running":
                available_capacity += crac.get("q_cool_kw", 0)
        
        if total_capacity > 0:
            self.system_performance_metrics["availability"] = (
                available_capacity / total_capacity * 100)
        
        # Calculate efficiency based on energy consumption
        total_cooling = sum(crac.get("q_cool_kw", 0) for crac in crac_states)
        total_power = sum(crac.get("power_kw", 0) for crac in crac_states)
        
        if total_power > 0:
            current_cop = total_cooling / total_power
            expected_cop = 3.5  # Typical CRAC COP
            efficiency = min(100.0, (current_cop / expected_cop) * 100)
            self.system_performance_metrics["efficiency"] = efficiency
    
    def get_active_diagnostics(self, category: Optional[DiagnosticCategory] = None,
                              severity: Optional[FaultSeverity] = None) -> List[DiagnosticResult]:
        """Get active diagnostics with optional filtering."""
        diagnostics = list(self.active_diagnostics.values())
        
        if category is not None:
            diagnostics = [d for d in diagnostics if d.category == category]
        
        if severity is not None:
            diagnostics = [d for d in diagnostics if d.severity == severity]
        
        return diagnostics
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive system health summary."""
        active_count = len(self.active_diagnostics)
        
        severity_counts = {}
        for severity in FaultSeverity:
            count = len([d for d in self.active_diagnostics.values() 
                        if d.severity == severity])
            severity_counts[severity.value] = count
        
        category_counts = {}
        for category in DiagnosticCategory:
            count = len([d for d in self.active_diagnostics.values() 
                        if d.category == category])
            category_counts[category.value] = count
        
        return {
            "timestamp": self.last_evaluation_time,
            "active_diagnostics": active_count,
            "severity_breakdown": severity_counts,
            "category_breakdown": category_counts,
            "performance_metrics": self.system_performance_metrics.copy(),
            "total_rules": len(self.diagnostic_rules),
            "enabled_rules": len([r for r in self.diagnostic_rules.values() if r.enable])
        }
    
    def resolve_diagnostic(self, diagnostic_id: str, sim_time: float) -> bool:
        """Mark a diagnostic as resolved."""
        if diagnostic_id in self.active_diagnostics:
            diagnostic = self.active_diagnostics[diagnostic_id]
            diagnostic.status = DiagnosticStatus.RESOLVED
            diagnostic.timestamp = sim_time
            
            # Move to history and remove from active
            self.diagnostic_history.append(diagnostic)
            del self.active_diagnostics[diagnostic_id]
            return True
        return False
    
    def _get_trend_analysis(self, data_key: str, window_minutes: int = 60) -> Dict[str, Any]:
        """Perform trend analysis on buffered data."""
        if data_key not in self.data_buffer:
            return {}
        
        data = self.data_buffer[data_key]
        if len(data) < 10:  # Need minimum data points
            return {}
        
        # Get data within time window
        current_time = self.last_evaluation_time
        window_start = current_time - (window_minutes * 60)
        
        windowed_data = [(t, v) for t, v in data if t >= window_start]
        if len(windowed_data) < 5:
            return {}
        
        # Extract values
        values = [v for t, v in windowed_data if isinstance(v, (int, float))]
        if len(values) < 5:
            return {}
        
        # Calculate statistics
        mean_value = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        
        # Linear trend calculation
        times = [t for t, v in windowed_data if isinstance(v, (int, float))]
        if len(times) == len(values):
            # Simple linear regression
            n = len(values)
            sum_x = sum(times)
            sum_y = sum(values)
            sum_xy = sum(t * v for t, v in zip(times, values))
            sum_x2 = sum(t * t for t in times)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            # Determine trend direction
            if abs(slope) < std_dev * 0.1:
                trend = "stable"
            elif slope > 0:
                trend = "increasing"
            else:
                trend = "decreasing"
        else:
            trend = "unknown"
            slope = 0
        
        return {
            "mean": mean_value,
            "std_dev": std_dev,
            "trend": trend,
            "slope": slope,
            "data_points": len(values),
            "time_span": max(times) - min(times) if times else 0
        }
    
    # Diagnostic rule evaluators
    def _evaluate_sensor_drift(self, system_data: Dict[str, Any]) -> Optional[DiagnosticResult]:
        """Evaluate sensor drift diagnostic rule."""
        sensor_readings = system_data.get("sensor_temps", [])
        if not sensor_readings or len(sensor_readings) < 2:
            return None
        
        # Analyze temperature sensor consistency
        if len(sensor_readings) >= 3:
            avg_temp = statistics.mean(sensor_readings)
            deviations = [abs(temp - avg_temp) for temp in sensor_readings]
            max_deviation = max(deviations)
            
            # Check for sensor that's significantly different
            if max_deviation > 1.5:  # More than 1.5°C deviation
                outlier_index = deviations.index(max_deviation)
                
                # Get trend analysis for this sensor
                trend_key = f"sensor_{outlier_index}_readings"
                trend = self._get_trend_analysis(trend_key, 120)  # 2-hour window
                
                confidence = min(0.9, max_deviation / 3.0)  # Higher deviation = higher confidence
                
                if confidence > 0.7:
                    return DiagnosticResult(
                        diagnostic_id=f"SENSOR_DRIFT_{outlier_index}",
                        timestamp=0.0,  # Will be set by caller
                        category=DiagnosticCategory.SENSOR,
                        severity=FaultSeverity.MINOR if max_deviation < 2.5 else FaultSeverity.MAJOR,
                        status=DiagnosticStatus.CONFIRMED,
                        title=f"Temperature Sensor {outlier_index+1} Drift",
                        description=f"Sensor reading deviates by {max_deviation:.1f}°C from other sensors",
                        component_id=f"TEMP_SENSOR_{outlier_index+1:02d}",
                        location=f"Zone_{outlier_index+1}",
                        measured_value=sensor_readings[outlier_index],
                        expected_value=avg_temp,
                        deviation_percent=(max_deviation / avg_temp) * 100,
                        trend_direction=trend.get("trend", "unknown"),
                        confidence_level=confidence,
                        recommended_actions=[
                            "Calibrate temperature sensor",
                            "Verify sensor mounting and location",
                            "Check sensor wiring and connections",
                            "Consider sensor replacement if drift continues"
                        ],
                        estimated_repair_time="2-4 hours",
                        maintenance_priority="Medium"
                    )
        
        return None
    
    def _evaluate_equipment_performance(self, system_data: Dict[str, Any]) -> Optional[DiagnosticResult]:
        """Evaluate equipment performance degradation."""
        crac_states = system_data.get("crac_states", [])
        if not crac_states:
            return None
        
        for i, crac in enumerate(crac_states):
            q_rated = crac.get("q_rated_kw", 50.0)
            q_actual = crac.get("q_cool_kw", 0.0)
            cmd_pct = crac.get("cmd_pct", 0.0)
            status = crac.get("status", "off")
            
            if status == "running" and cmd_pct > 80:
                # Calculate expected vs actual performance
                expected_output = (cmd_pct / 100.0) * q_rated
                performance_ratio = q_actual / expected_output if expected_output > 0 else 0
                
                if performance_ratio < 0.85:  # Less than 85% of expected
                    confidence = 1.0 - performance_ratio
                    
                    return DiagnosticResult(
                        diagnostic_id=f"CRAC_PERFORMANCE_{i}",
                        timestamp=0.0,
                        category=DiagnosticCategory.EQUIPMENT,
                        severity=FaultSeverity.MAJOR if performance_ratio < 0.7 else FaultSeverity.MINOR,
                        status=DiagnosticStatus.CONFIRMED,
                        title=f"CRAC-{i+1:02d} Performance Degradation",
                        description=f"Cooling output is {performance_ratio*100:.1f}% of expected capacity",
                        component_id=crac.get("unit_id", f"CRAC-{i+1:02d}"),
                        location=f"CRAC-{i+1:02d}",
                        measured_value=q_actual,
                        expected_value=expected_output,
                        deviation_percent=(1 - performance_ratio) * 100,
                        confidence_level=confidence,
                        recommended_actions=[
                            "Check refrigerant levels",
                            "Inspect heat exchanger for fouling",
                            "Verify airflow and filter condition",
                            "Check compressor operation",
                            "Schedule preventive maintenance"
                        ],
                        estimated_repair_time="4-8 hours",
                        maintenance_priority="High"
                    )
        
        return None
    
    def _evaluate_control_instability(self, system_data: Dict[str, Any]) -> Optional[DiagnosticResult]:
        """Evaluate control loop stability."""
        # Analyze control signal variability
        trend = self._get_trend_analysis("pid_output", 30)  # 30-minute window
        
        if trend and "std_dev" in trend:
            std_dev = trend["std_dev"]
            mean_val = trend["mean"]
            
            # High variability indicates instability
            if std_dev > 15 and mean_val > 0:  # More than 15% standard deviation
                variability_ratio = std_dev / mean_val
                confidence = min(0.9, variability_ratio / 0.5)
                
                if confidence > 0.6:
                    return DiagnosticResult(
                        diagnostic_id="CONTROL_INSTABILITY",
                        timestamp=0.0,
                        category=DiagnosticCategory.CONTROL,
                        severity=FaultSeverity.MAJOR,
                        status=DiagnosticStatus.MONITORING,
                        title="Control Loop Instability",
                        description=f"Control signal variability is {std_dev:.1f}% (>{15}% threshold)",
                        component_id="PID_CONTROLLER",
                        location="Primary Control Loop",
                        measured_value=std_dev,
                        threshold_value=15.0,
                        confidence_level=confidence,
                        recommended_actions=[
                            "Review PID tuning parameters",
                            "Check for sensor noise or interference",
                            "Verify actuator response",
                            "Analyze system deadtime",
                            "Consider adaptive control algorithms"
                        ],
                        estimated_repair_time="2-6 hours",
                        maintenance_priority="High"
                    )
        
        return None
    
    def _evaluate_communication_health(self, system_data: Dict[str, Any]) -> Optional[DiagnosticResult]:
        """Evaluate communication system health."""
        # This would analyze communication statistics if available
        # For now, return None as it requires specific comm data
        return None
    
    def _evaluate_energy_efficiency(self, system_data: Dict[str, Any]) -> Optional[DiagnosticResult]:
        """Evaluate energy efficiency performance."""
        crac_states = system_data.get("crac_states", [])
        if not crac_states:
            return None
        
        total_cooling = sum(crac.get("q_cool_kw", 0) for crac in crac_states)
        total_power = sum(crac.get("power_kw", 0) for crac in crac_states)
        
        if total_power > 0 and total_cooling > 0:
            actual_cop = total_cooling / total_power
            expected_cop = 3.5  # Typical CRAC COP
            efficiency = actual_cop / expected_cop
            
            if efficiency < 0.8:  # Less than 80% of expected efficiency
                confidence = 1.0 - efficiency
                
                return DiagnosticResult(
                    diagnostic_id="ENERGY_EFFICIENCY",
                    timestamp=0.0,
                    category=DiagnosticCategory.PERFORMANCE,
                    severity=FaultSeverity.WARNING if efficiency > 0.7 else FaultSeverity.MINOR,
                    status=DiagnosticStatus.MONITORING,
                    title="Energy Efficiency Below Target",
                    description=f"System COP is {actual_cop:.2f} ({efficiency*100:.1f}% of target)",
                    component_id="COOLING_SYSTEM",
                    location="Data Center",
                    measured_value=actual_cop,
                    expected_value=expected_cop,
                    deviation_percent=(1 - efficiency) * 100,
                    confidence_level=confidence,
                    recommended_actions=[
                        "Optimize CRAC staging sequence",
                        "Review setpoint strategy",
                        "Check for unnecessary cooling",
                        "Verify equipment efficiency",
                        "Consider economizer operation"
                    ],
                    estimated_repair_time="1-3 hours",
                    maintenance_priority="Low"
                )
        
        return None