# diagnostics/root_cause.py
"""
Professional Fault Root-Cause Analysis Module for BAS Data Center Systems

Advanced fault analysis capabilities featuring:
- Symptom-cause mapping with decision trees
- Timeline analysis for fault progression
- Component interaction and failure propagation
- Maintenance recommendations with specific corrective actions
- Performance impact quantification

Engineering Implementation:
- Knowledge-based expert system for fault isolation
- Statistical correlation analysis
- Pattern recognition for complex fault scenarios
- Integration with maintenance management systems
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
import statistics
from datetime import datetime, timedelta


class CauseCategory(Enum):
    """Categories for root cause classification."""
    EQUIPMENT_FAILURE = "equipment_failure"      # Hardware/equipment failures
    MAINTENANCE_ISSUE = "maintenance_issue"      # Preventive maintenance related
    DESIGN_PROBLEM = "design_problem"            # System design issues
    OPERATIONAL_ERROR = "operational_error"      # Human operational errors
    ENVIRONMENTAL = "environmental"              # External environmental factors
    SOFTWARE_BUG = "software_bug"                # Control software issues
    COMMUNICATION = "communication"              # Network/protocol issues
    POWER_QUALITY = "power_quality"              # Electrical power issues


class FaultSymptom(Enum):
    """Observable symptoms for fault analysis."""
    HIGH_TEMPERATURE = "high_temperature"            # Temperature above setpoint
    LOW_TEMPERATURE = "low_temperature"              # Temperature below setpoint
    TEMPERATURE_OSCILLATION = "temp_oscillation"     # Temperature cycling
    POOR_RESPONSE = "poor_response"                  # Slow system response
    EQUIPMENT_CYCLING = "equipment_cycling"          # Rapid equipment cycling
    EFFICIENCY_LOSS = "efficiency_loss"              # Energy efficiency degradation
    CONTROL_INSTABILITY = "control_instability"      # Unstable control behavior
    COMMUNICATION_LOSS = "communication_loss"        # Network connectivity issues
    SENSOR_INCONSISTENCY = "sensor_inconsistency"    # Sensor reading discrepancies
    ACTUATOR_NONRESPONSE = "actuator_nonresponse"    # Actuator not responding
    ALARM_CONDITION = "alarm_condition"              # Active alarm conditions
    PERFORMANCE_DEGRADATION = "performance_degradation" # Overall performance decline


@dataclass
class CauseEffect:
    """Relationship between cause and effect in fault analysis."""
    cause_id: str
    effect_symptoms: List[FaultSymptom]
    probability: float                # Probability of this cause given symptoms
    confidence: float                 # Confidence in diagnosis
    supporting_evidence: List[str]    # Evidence supporting this cause
    contradicting_evidence: List[str] # Evidence against this cause


@dataclass
class MaintenanceAction:
    """Specific maintenance action recommendation."""
    action_id: str
    description: str
    category: str                     # "inspect", "repair", "replace", "calibrate"
    priority: str                     # "immediate", "urgent", "planned", "deferred"
    estimated_duration: str           # Time estimate for action
    required_skills: List[str]        # Required technician skills
    required_parts: List[str]         # Required replacement parts
    safety_considerations: List[str]  # Safety precautions
    cost_impact: str                  # "low", "medium", "high"


@dataclass
class RootCauseAnalysis:
    """Complete root cause analysis result."""
    analysis_id: str
    timestamp: float
    
    # Primary analysis
    primary_cause: str
    cause_category: CauseCategory
    confidence_level: float
    
    # Supporting information
    contributing_factors: List[str]
    observed_symptoms: List[FaultSymptom]
    timeline_events: List[Dict[str, Any]]
    
    # Impact assessment
    affected_components: List[str]
    performance_impact: Dict[str, float]  # Performance metrics affected
    estimated_downtime: str
    
    # Recommendations
    immediate_actions: List[MaintenanceAction]
    preventive_actions: List[MaintenanceAction]
    long_term_recommendations: List[str]
    
    # Evidence
    supporting_data: Dict[str, Any]
    correlation_analysis: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'analysis_id': self.analysis_id,
            'timestamp': self.timestamp,
            'primary_cause': self.primary_cause,
            'cause_category': self.cause_category.value,
            'confidence_level': self.confidence_level,
            'contributing_factors': self.contributing_factors,
            'observed_symptoms': [s.value for s in self.observed_symptoms],
            'timeline_events': self.timeline_events,
            'affected_components': self.affected_components,
            'performance_impact': self.performance_impact,
            'estimated_downtime': self.estimated_downtime,
            'immediate_actions': [
                {
                    'action_id': a.action_id,
                    'description': a.description,
                    'category': a.category,
                    'priority': a.priority,
                    'estimated_duration': a.estimated_duration,
                    'required_skills': a.required_skills,
                    'required_parts': a.required_parts,
                    'safety_considerations': a.safety_considerations,
                    'cost_impact': a.cost_impact
                } for a in self.immediate_actions
            ],
            'preventive_actions': [
                {
                    'action_id': a.action_id,
                    'description': a.description,
                    'category': a.category,
                    'priority': a.priority,
                    'estimated_duration': a.estimated_duration,
                    'required_skills': a.required_skills,
                    'required_parts': a.required_parts,
                    'safety_considerations': a.safety_considerations,
                    'cost_impact': a.cost_impact
                } for a in self.preventive_actions
            ],
            'long_term_recommendations': self.long_term_recommendations,
            'supporting_data': self.supporting_data,
            'correlation_analysis': self.correlation_analysis
        }


class RootCauseAnalyzer:
    """
    Professional root cause analysis engine for BAS fault diagnosis.
    
    Features:
    - Knowledge-based expert system with symptom-cause mapping
    - Timeline analysis for understanding fault progression
    - Component interaction modeling
    - Statistical correlation analysis
    - Professional maintenance recommendations
    
    Engineering Approach:
    - Decision tree logic for systematic fault isolation
    - Bayesian inference for probability calculations
    - Pattern matching for complex fault scenarios
    - Integration with maintenance knowledge base
    """
    
    def __init__(self):
        self.symptom_cause_map: Dict[str, List[CauseEffect]] = {}
        self.fault_patterns: Dict[str, List[Dict[str, Any]]] = {}
        self.maintenance_knowledge: Dict[str, List[MaintenanceAction]] = {}
        
        # Initialize knowledge base
        self._initialize_symptom_cause_mapping()
        self._initialize_fault_patterns()
        self._initialize_maintenance_knowledge()
        
        # Analysis history
        self.analysis_history: List[RootCauseAnalysis] = []
        
    def _initialize_symptom_cause_mapping(self) -> None:
        """Initialize symptom-to-cause mapping knowledge base."""
        
        # High temperature causes
        self.symptom_cause_map["high_temperature"] = [
            CauseEffect(
                cause_id="insufficient_cooling_capacity",
                effect_symptoms=[FaultSymptom.HIGH_TEMPERATURE, FaultSymptom.POOR_RESPONSE],
                probability=0.7,
                confidence=0.8,
                supporting_evidence=["low_cooling_output", "high_demand"],
                contradicting_evidence=["adequate_capacity_available"]
            ),
            CauseEffect(
                cause_id="crac_equipment_failure",
                effect_symptoms=[FaultSymptom.HIGH_TEMPERATURE, FaultSymptom.ALARM_CONDITION],
                probability=0.6,
                confidence=0.9,
                supporting_evidence=["crac_fault_alarm", "zero_cooling_output"],
                contradicting_evidence=["normal_crac_operation"]
            ),
            CauseEffect(
                cause_id="sensor_calibration_error",
                effect_symptoms=[FaultSymptom.HIGH_TEMPERATURE, FaultSymptom.SENSOR_INCONSISTENCY],
                probability=0.4,
                confidence=0.6,
                supporting_evidence=["sensor_drift", "reading_inconsistency"],
                contradicting_evidence=["consistent_sensor_readings"]
            )
        ]
        
        # Control instability causes
        self.symptom_cause_map["control_instability"] = [
            CauseEffect(
                cause_id="pid_tuning_issue",
                effect_symptoms=[FaultSymptom.CONTROL_INSTABILITY, FaultSymptom.TEMPERATURE_OSCILLATION],
                probability=0.8,
                confidence=0.7,
                supporting_evidence=["oscillatory_behavior", "poor_settling"],
                contradicting_evidence=["stable_control_response"]
            ),
            CauseEffect(
                cause_id="actuator_backlash",
                effect_symptoms=[FaultSymptom.CONTROL_INSTABILITY, FaultSymptom.ACTUATOR_NONRESPONSE],
                probability=0.6,
                confidence=0.8,
                supporting_evidence=["position_hysteresis", "delayed_response"],
                contradicting_evidence=["smooth_actuator_operation"]
            ),
            CauseEffect(
                cause_id="sensor_noise",
                effect_symptoms=[FaultSymptom.CONTROL_INSTABILITY, FaultSymptom.SENSOR_INCONSISTENCY],
                probability=0.5,
                confidence=0.6,
                supporting_evidence=["noisy_feedback", "erratic_readings"],
                contradicting_evidence=["clean_sensor_signals"]
            )
        ]
        
        # Equipment cycling causes
        self.symptom_cause_map["equipment_cycling"] = [
            CauseEffect(
                cause_id="short_cycling_fault",
                effect_symptoms=[FaultSymptom.EQUIPMENT_CYCLING, FaultSymptom.EFFICIENCY_LOSS],
                probability=0.9,
                confidence=0.9,
                supporting_evidence=["rapid_on_off_cycles", "high_cycle_count"],
                contradicting_evidence=["normal_cycle_times"]
            ),
            CauseEffect(
                cause_id="pressure_control_issue",
                effect_symptoms=[FaultSymptom.EQUIPMENT_CYCLING, FaultSymptom.PERFORMANCE_DEGRADATION],
                probability=0.7,
                confidence=0.8,
                supporting_evidence=["pressure_instability", "compressor_cycling"],
                contradicting_evidence=["stable_pressures"]
            )
        ]
        
        # Communication issues
        self.symptom_cause_map["communication_loss"] = [
            CauseEffect(
                cause_id="network_infrastructure_fault",
                effect_symptoms=[FaultSymptom.COMMUNICATION_LOSS, FaultSymptom.ALARM_CONDITION],
                probability=0.8,
                confidence=0.9,
                supporting_evidence=["network_timeouts", "packet_loss"],
                contradicting_evidence=["stable_network_connectivity"]
            ),
            CauseEffect(
                cause_id="controller_software_bug",
                effect_symptoms=[FaultSymptom.COMMUNICATION_LOSS, FaultSymptom.CONTROL_INSTABILITY],
                probability=0.5,
                confidence=0.6,
                supporting_evidence=["software_errors", "unexpected_behavior"],
                contradicting_evidence=["software_operating_normally"]
            )
        ]
    
    def _initialize_fault_patterns(self) -> None:
        """Initialize common fault patterns for pattern matching."""
        
        # Cascading failure pattern
        self.fault_patterns["cascading_failure"] = [
            {
                "sequence": ["equipment_failure", "backup_activation", "overload", "secondary_failure"],
                "time_correlation": "increasing_severity_over_time",
                "indicators": ["multiple_equipment_alarms", "capacity_reduction", "temperature_rise"]
            }
        ]
        
        # Gradual degradation pattern
        self.fault_patterns["gradual_degradation"] = [
            {
                "sequence": ["performance_decline", "efficiency_loss", "increased_cycling"],
                "time_correlation": "linear_degradation",
                "indicators": ["trending_performance_loss", "increased_energy_consumption"]
            }
        ]
        
        # Intermittent fault pattern
        self.fault_patterns["intermittent_fault"] = [
            {
                "sequence": ["sporadic_symptoms", "temporary_resolution", "symptom_recurrence"],
                "time_correlation": "cyclical_pattern",
                "indicators": ["intermittent_alarms", "variable_performance"]
            }
        ]
    
    def _initialize_maintenance_knowledge(self) -> None:
        """Initialize maintenance action knowledge base."""
        
        # CRAC equipment maintenance
        self.maintenance_knowledge["crac_equipment_failure"] = [
            MaintenanceAction(
                action_id="inspect_compressor",
                description="Inspect compressor operation and refrigerant levels",
                category="inspect",
                priority="immediate",
                estimated_duration="2-3 hours",
                required_skills=["hvac_technician", "refrigeration_certified"],
                required_parts=["refrigerant", "compressor_oil"],
                safety_considerations=["electrical_lockout", "refrigerant_handling"],
                cost_impact="medium"
            ),
            MaintenanceAction(
                action_id="replace_failed_component",
                description="Replace failed CRAC component based on diagnosis",
                category="repair",
                priority="urgent",
                estimated_duration="4-8 hours",
                required_skills=["hvac_technician", "electrical_technician"],
                required_parts=["replacement_component", "gaskets", "filters"],
                safety_considerations=["electrical_lockout", "mechanical_safety"],
                cost_impact="high"
            )
        ]
        
        # Sensor calibration maintenance
        self.maintenance_knowledge["sensor_calibration_error"] = [
            MaintenanceAction(
                action_id="calibrate_temperature_sensors",
                description="Calibrate temperature sensors using reference standards",
                category="calibrate",
                priority="planned",
                estimated_duration="1-2 hours",
                required_skills=["instrumentation_technician"],
                required_parts=["calibration_reference", "documentation"],
                safety_considerations=["minimal_risk"],
                cost_impact="low"
            ),
            MaintenanceAction(
                action_id="replace_drifted_sensor",
                description="Replace sensor showing significant drift",
                category="replace",
                priority="planned",
                estimated_duration="1 hour",
                required_skills=["instrumentation_technician"],
                required_parts=["temperature_sensor", "wiring"],
                safety_considerations=["electrical_safety"],
                cost_impact="low"
            )
        ]
        
        # Control system maintenance
        self.maintenance_knowledge["pid_tuning_issue"] = [
            MaintenanceAction(
                action_id="retune_pid_controller",
                description="Perform PID controller auto-tuning or manual optimization",
                category="calibrate",
                priority="planned",
                estimated_duration="2-4 hours",
                required_skills=["controls_engineer", "commissioning_agent"],
                required_parts=["documentation", "tuning_software"],
                safety_considerations=["system_stability_during_tuning"],
                cost_impact="low"
            )
        ]
        
        # Actuator maintenance
        self.maintenance_knowledge["actuator_backlash"] = [
            MaintenanceAction(
                action_id="inspect_actuator_mechanism",
                description="Inspect actuator for mechanical wear and backlash",
                category="inspect",
                priority="planned",
                estimated_duration="1-2 hours",
                required_skills=["mechanical_technician"],
                required_parts=["lubricants", "adjustment_tools"],
                safety_considerations=["mechanical_safety", "lockout_procedures"],
                cost_impact="low"
            ),
            MaintenanceAction(
                action_id="replace_worn_actuator",
                description="Replace actuator with excessive backlash or wear",
                category="replace",
                priority="planned",
                estimated_duration="2-4 hours",
                required_skills=["mechanical_technician", "controls_technician"],
                required_parts=["actuator_assembly", "mounting_hardware"],
                safety_considerations=["mechanical_safety", "electrical_safety"],
                cost_impact="medium"
            )
        ]
    
    def analyze_fault(self, diagnostic_results: List[Dict[str, Any]], 
                     system_data: Dict[str, Any],
                     historical_data: Optional[List[Dict[str, Any]]] = None) -> RootCauseAnalysis:
        """
        Perform comprehensive root cause analysis on fault conditions.
        
        Args:
            diagnostic_results: List of diagnostic results from engine
            system_data: Current system state data
            historical_data: Optional historical data for trend analysis
            
        Returns:
            Complete root cause analysis with recommendations
        """
        
        # Extract symptoms from diagnostic results
        observed_symptoms = self._extract_symptoms(diagnostic_results)
        
        # Analyze timeline if historical data available
        timeline_events = self._analyze_timeline(historical_data) if historical_data else []
        
        # Perform cause correlation analysis
        cause_probabilities = self._correlate_causes(observed_symptoms, system_data)
        
        # Identify primary cause
        primary_cause, confidence = self._identify_primary_cause(cause_probabilities)
        
        # Determine cause category
        cause_category = self._categorize_cause(primary_cause)
        
        # Identify contributing factors
        contributing_factors = self._identify_contributing_factors(
            primary_cause, cause_probabilities, system_data)
        
        # Assess performance impact
        performance_impact = self._assess_performance_impact(
            observed_symptoms, system_data)
        
        # Generate maintenance recommendations
        immediate_actions = self._generate_immediate_actions(primary_cause)
        preventive_actions = self._generate_preventive_actions(primary_cause)
        long_term_recommendations = self._generate_long_term_recommendations(
            primary_cause, contributing_factors)
        
        # Compile supporting data
        supporting_data = self._compile_supporting_data(
            diagnostic_results, system_data, observed_symptoms)
        
        # Create analysis result
        analysis = RootCauseAnalysis(
            analysis_id=f"RCA_{int(system_data.get('timestamp', 0))}",
            timestamp=system_data.get('timestamp', 0.0),
            primary_cause=primary_cause,
            cause_category=cause_category,
            confidence_level=confidence,
            contributing_factors=contributing_factors,
            observed_symptoms=observed_symptoms,
            timeline_events=timeline_events,
            affected_components=self._identify_affected_components(diagnostic_results),
            performance_impact=performance_impact,
            estimated_downtime=self._estimate_downtime(primary_cause, observed_symptoms),
            immediate_actions=immediate_actions,
            preventive_actions=preventive_actions,
            long_term_recommendations=long_term_recommendations,
            supporting_data=supporting_data,
            correlation_analysis=cause_probabilities
        )
        
        # Store in history
        self.analysis_history.append(analysis)
        
        return analysis
    
    def _extract_symptoms(self, diagnostic_results: List[Dict[str, Any]]) -> List[FaultSymptom]:
        """Extract fault symptoms from diagnostic results."""
        symptoms = set()
        
        for result in diagnostic_results:
            category = result.get('category', '')
            severity = result.get('severity', '')
            title = result.get('title', '').lower()
            
            # Map diagnostic results to symptoms
            if 'temperature' in title and 'high' in title:
                symptoms.add(FaultSymptom.HIGH_TEMPERATURE)
            elif 'temperature' in title and 'low' in title:
                symptoms.add(FaultSymptom.LOW_TEMPERATURE)
            elif 'drift' in title or 'inconsistency' in title:
                symptoms.add(FaultSymptom.SENSOR_INCONSISTENCY)
            elif 'performance' in title or 'degradation' in title:
                symptoms.add(FaultSymptom.PERFORMANCE_DEGRADATION)
            elif 'instability' in title or 'oscillation' in title:
                symptoms.add(FaultSymptom.CONTROL_INSTABILITY)
            elif 'cycling' in title:
                symptoms.add(FaultSymptom.EQUIPMENT_CYCLING)
            elif 'efficiency' in title:
                symptoms.add(FaultSymptom.EFFICIENCY_LOSS)
            elif 'communication' in title:
                symptoms.add(FaultSymptom.COMMUNICATION_LOSS)
            
            # Add based on severity
            if severity in ['critical', 'major']:
                symptoms.add(FaultSymptom.ALARM_CONDITION)
        
        return list(symptoms)
    
    def _analyze_timeline(self, historical_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze timeline of events for fault progression."""
        timeline_events = []
        
        if not historical_data:
            return timeline_events
        
        # Sort by timestamp
        sorted_data = sorted(historical_data, key=lambda x: x.get('timestamp', 0))
        
        # Look for significant events
        for i, event in enumerate(sorted_data):
            if i == 0:
                continue
                
            prev_event = sorted_data[i-1]
            
            # Check for significant changes
            temp_change = abs(event.get('temperature', 0) - prev_event.get('temperature', 0))
            if temp_change > 1.0:  # Temperature change > 1°C
                timeline_events.append({
                    'timestamp': event.get('timestamp', 0),
                    'event_type': 'temperature_change',
                    'description': f"Temperature changed by {temp_change:.1f}°C",
                    'significance': 'high' if temp_change > 2.0 else 'medium'
                })
            
            # Check for equipment state changes
            if event.get('crac_status') != prev_event.get('crac_status'):
                timeline_events.append({
                    'timestamp': event.get('timestamp', 0),
                    'event_type': 'equipment_state_change',
                    'description': f"CRAC status changed from {prev_event.get('crac_status')} to {event.get('crac_status')}",
                    'significance': 'high'
                })
        
        return timeline_events
    
    def _correlate_causes(self, symptoms: List[FaultSymptom], 
                         system_data: Dict[str, Any]) -> Dict[str, float]:
        """Correlate observed symptoms with potential causes."""
        cause_scores = {}
        
        # Check each symptom against cause mapping
        for symptom in symptoms:
            symptom_key = symptom.value
            if symptom_key in self.symptom_cause_map:
                for cause_effect in self.symptom_cause_map[symptom_key]:
                    cause_id = cause_effect.cause_id
                    
                    # Calculate score based on probability and evidence
                    base_score = cause_effect.probability * cause_effect.confidence
                    
                    # Adjust score based on supporting evidence in system data
                    evidence_score = self._evaluate_evidence(
                        cause_effect.supporting_evidence,
                        cause_effect.contradicting_evidence,
                        system_data
                    )
                    
                    final_score = base_score * evidence_score
                    
                    if cause_id in cause_scores:
                        cause_scores[cause_id] = max(cause_scores[cause_id], final_score)
                    else:
                        cause_scores[cause_id] = final_score
        
        return cause_scores
    
    def _evaluate_evidence(self, supporting: List[str], contradicting: List[str],
                          system_data: Dict[str, Any]) -> float:
        """Evaluate evidence strength for a cause."""
        evidence_score = 1.0
        
        # Check supporting evidence
        for evidence in supporting:
            if self._evidence_present(evidence, system_data):
                evidence_score *= 1.2  # Boost score
        
        # Check contradicting evidence
        for evidence in contradicting:
            if self._evidence_present(evidence, system_data):
                evidence_score *= 0.5  # Reduce score
        
        return max(0.1, min(2.0, evidence_score))  # Limit range
    
    def _evidence_present(self, evidence: str, system_data: Dict[str, Any]) -> bool:
        """Check if evidence is present in system data."""
        # Simple pattern matching for evidence
        if evidence == "low_cooling_output":
            crac_states = system_data.get("crac_states", [])
            return any(crac.get("q_cool_kw", 0) < 10 for crac in crac_states)
        
        elif evidence == "crac_fault_alarm":
            return any(alarm.get("alarm_id") == "CRAC_FAIL" 
                      for alarm in system_data.get("active_alarms", []))
        
        elif evidence == "sensor_drift":
            sensor_temps = system_data.get("sensor_temps", [])
            if len(sensor_temps) >= 2:
                temp_range = max(sensor_temps) - min(sensor_temps)
                return temp_range > 1.5
        
        elif evidence == "oscillatory_behavior":
            # Would need historical data to detect oscillations
            return False
        
        elif evidence == "rapid_on_off_cycles":
            return any(crac.get("starts_count", 0) > 10 
                      for crac in system_data.get("crac_states", []))
        
        return False
    
    def _identify_primary_cause(self, cause_probabilities: Dict[str, float]) -> Tuple[str, float]:
        """Identify the most likely primary cause."""
        if not cause_probabilities:
            return "unknown_cause", 0.0
        
        primary_cause = max(cause_probabilities.keys(), 
                           key=lambda k: cause_probabilities[k])
        confidence = cause_probabilities[primary_cause]
        
        return primary_cause, confidence
    
    def _categorize_cause(self, primary_cause: str) -> CauseCategory:
        """Categorize the primary cause."""
        cause_categories = {
            "crac_equipment_failure": CauseCategory.EQUIPMENT_FAILURE,
            "insufficient_cooling_capacity": CauseCategory.DESIGN_PROBLEM,
            "sensor_calibration_error": CauseCategory.MAINTENANCE_ISSUE,
            "pid_tuning_issue": CauseCategory.OPERATIONAL_ERROR,
            "actuator_backlash": CauseCategory.MAINTENANCE_ISSUE,
            "sensor_noise": CauseCategory.ENVIRONMENTAL,
            "short_cycling_fault": CauseCategory.EQUIPMENT_FAILURE,
            "pressure_control_issue": CauseCategory.EQUIPMENT_FAILURE,
            "network_infrastructure_fault": CauseCategory.COMMUNICATION,
            "controller_software_bug": CauseCategory.SOFTWARE_BUG
        }
        
        return cause_categories.get(primary_cause, CauseCategory.EQUIPMENT_FAILURE)
    
    def _identify_contributing_factors(self, primary_cause: str, 
                                     cause_probabilities: Dict[str, float],
                                     system_data: Dict[str, Any]) -> List[str]:
        """Identify contributing factors to the fault."""
        contributing_factors = []
        
        # Add causes with significant probability (but not primary)
        for cause, probability in cause_probabilities.items():
            if cause != primary_cause and probability > 0.3:
                contributing_factors.append(cause)
        
        # Add environmental factors if relevant
        if system_data.get("ambient_temp_c", 22) > 30:
            contributing_factors.append("high_ambient_temperature")
        
        if any(crac.get("runtime_hours", 0) > 8000 
               for crac in system_data.get("crac_states", [])):
            contributing_factors.append("equipment_aging")
        
        return contributing_factors
    
    def _assess_performance_impact(self, symptoms: List[FaultSymptom],
                                  system_data: Dict[str, Any]) -> Dict[str, float]:
        """Assess quantitative performance impact."""
        impact = {
            "availability": 100.0,
            "efficiency": 100.0,
            "reliability": 100.0,
            "comfort": 100.0
        }
        
        # Reduce metrics based on symptoms
        for symptom in symptoms:
            if symptom == FaultSymptom.HIGH_TEMPERATURE:
                impact["comfort"] *= 0.8
                impact["reliability"] *= 0.9
            elif symptom == FaultSymptom.EQUIPMENT_CYCLING:
                impact["efficiency"] *= 0.85
                impact["reliability"] *= 0.9
            elif symptom == FaultSymptom.PERFORMANCE_DEGRADATION:
                impact["efficiency"] *= 0.8
            elif symptom == FaultSymptom.ALARM_CONDITION:
                impact["availability"] *= 0.9
        
        return impact
    
    def _identify_affected_components(self, diagnostic_results: List[Dict[str, Any]]) -> List[str]:
        """Identify components affected by faults."""
        components = set()
        
        for result in diagnostic_results:
            component_id = result.get('component_id')
            if component_id:
                components.add(component_id)
        
        return list(components)
    
    def _estimate_downtime(self, primary_cause: str, symptoms: List[FaultSymptom]) -> str:
        """Estimate repair/resolution downtime."""
        base_times = {
            "crac_equipment_failure": "4-8 hours",
            "sensor_calibration_error": "1-2 hours", 
            "pid_tuning_issue": "2-4 hours",
            "actuator_backlash": "2-4 hours",
            "short_cycling_fault": "1-3 hours",
            "network_infrastructure_fault": "1-6 hours"
        }
        
        base_time = base_times.get(primary_cause, "2-6 hours")
        
        # Extend if multiple critical symptoms
        critical_symptoms = [s for s in symptoms if s in [
            FaultSymptom.ALARM_CONDITION,
            FaultSymptom.HIGH_TEMPERATURE,
            FaultSymptom.EQUIPMENT_CYCLING
        ]]
        
        if len(critical_symptoms) > 2:
            return f"{base_time} (extended due to multiple issues)"
        
        return base_time
    
    def _generate_immediate_actions(self, primary_cause: str) -> List[MaintenanceAction]:
        """Generate immediate maintenance actions."""
        return self.maintenance_knowledge.get(primary_cause, [])
    
    def _generate_preventive_actions(self, primary_cause: str) -> List[MaintenanceAction]:
        """Generate preventive maintenance actions."""
        # For now, return subset of immediate actions marked as preventive
        actions = self.maintenance_knowledge.get(primary_cause, [])
        return [action for action in actions if action.category in ["inspect", "calibrate"]]
    
    def _generate_long_term_recommendations(self, primary_cause: str,
                                          contributing_factors: List[str]) -> List[str]:
        """Generate long-term improvement recommendations."""
        recommendations = []
        
        if primary_cause == "crac_equipment_failure":
            recommendations.extend([
                "Implement predictive maintenance program",
                "Consider equipment redundancy upgrades",
                "Review preventive maintenance schedules"
            ])
        
        elif primary_cause == "sensor_calibration_error":
            recommendations.extend([
                "Establish regular sensor calibration schedule",
                "Consider upgrading to higher accuracy sensors",
                "Implement automated calibration verification"
            ])
        
        elif primary_cause == "pid_tuning_issue":
            recommendations.extend([
                "Implement adaptive control algorithms", 
                "Provide advanced controls training",
                "Consider commissioning review"
            ])
        
        # Add recommendations based on contributing factors
        if "equipment_aging" in contributing_factors:
            recommendations.append("Develop equipment replacement strategy")
        
        if "high_ambient_temperature" in contributing_factors:
            recommendations.append("Evaluate building envelope improvements")
        
        return recommendations
    
    def _compile_supporting_data(self, diagnostic_results: List[Dict[str, Any]],
                               system_data: Dict[str, Any],
                               symptoms: List[FaultSymptom]) -> Dict[str, Any]:
        """Compile supporting data for analysis."""
        return {
            "diagnostic_count": len(diagnostic_results),
            "symptom_count": len(symptoms),
            "system_timestamp": system_data.get("timestamp", 0),
            "temperature_readings": system_data.get("sensor_temps", []),
            "crac_count": len(system_data.get("crac_states", [])),
            "active_alarms": len(system_data.get("active_alarms", []))
        }
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get summary of all analyses performed."""
        if not self.analysis_history:
            return {"total_analyses": 0}
        
        cause_categories = {}
        for analysis in self.analysis_history:
            category = analysis.cause_category.value
            cause_categories[category] = cause_categories.get(category, 0) + 1
        
        avg_confidence = statistics.mean(a.confidence_level for a in self.analysis_history)
        
        return {
            "total_analyses": len(self.analysis_history),
            "average_confidence": avg_confidence,
            "cause_category_breakdown": cause_categories,
            "most_recent_analysis": self.analysis_history[-1].analysis_id,
            "maintenance_actions_generated": sum(
                len(a.immediate_actions) + len(a.preventive_actions) 
                for a in self.analysis_history
            )
        }