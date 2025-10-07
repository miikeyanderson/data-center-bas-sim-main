#!/usr/bin/env python3
"""
Professional Fault Simulation and Diagnostics Demonstration

This script demonstrates the advanced fault simulation and diagnostic capabilities
of the BAS data center simulation system. It showcases:

1. Sensor fault injection (drift, bias, noise, stuck sensors)
2. Actuator fault simulation (stiction, backlash, oscillation)
3. Control system faults (short-cycling, instability, communication dropout)
4. Real-time fault detection and diagnosis
5. Root cause analysis with maintenance recommendations
6. Professional diagnostic reporting

Usage:
    python demo_fault_simulation.py [--duration MINUTES] [--faults SCENARIO]
    
    --duration: Simulation duration in minutes (default: 15)
    --faults: Fault scenario - 'light', 'moderate', 'aggressive' (default: moderate)
    --output: Output directory for reports (default: reports/fault_demo/)
    --config: Configuration file (default: config/scenarios/fault_demo.yaml)
"""

import sys
import argparse
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Import simulation components
from sim.environment import Room, RoomConfig
from sim.crac import CRACUnit, CRACConfig
from sim.sensor_faults import TemperatureSensor, create_default_sensor_configs
from sim.actuator_faults import ActuatorModel, create_default_actuator_configs
from control.pid import PIDController, PIDConfig
from control.alarms import AlarmManager
from control.system_faults import ControlSystemFaultManager, create_default_control_system_config
from diagnostics.engine import DiagnosticEngine
from diagnostics.root_cause import RootCauseAnalyzer
from diagnostics.reports import DiagnosticReporter, ReportConfig, ReportFormat
from config.config_loader import ConfigLoader


class FaultSimulationDemo:
    """
    Professional fault simulation demonstration platform.
    
    Orchestrates the complete fault simulation workflow:
    - System initialization with fault injection capabilities
    - Real-time simulation with progressive fault introduction
    - Continuous diagnostic monitoring and analysis
    - Professional reporting and documentation
    """
    
    def __init__(self, config_path: str = "config/scenarios/fault_demo.yaml"):
        """Initialize the fault simulation demonstration."""
        
        print("🔧 Initializing Professional Fault Simulation Demo")
        print("=" * 60)
        
        # Load configuration
        self.config_loader = ConfigLoader()
        self.config = self.config_loader.load_config(config_path)
        
        # Initialize random seed for reproducibility
        import random
        random.seed(self.config.get('fault_simulation', {}).get('random_seed', 12345))
        
        # Simulation parameters
        self.sim_time = 0.0
        self.dt = self.config['simulation']['timestep_s']
        self.duration = self.config['simulation']['duration_minutes'] * 60.0
        self.output_interval = self.config['simulation']['output_interval_s']
        self.last_output_time = 0.0
        
        # Initialize system components
        self._initialize_thermal_system()
        self._initialize_control_system()
        self._initialize_fault_simulation()
        self._initialize_diagnostics()
        
        # Data collection
        self.telemetry_data = []
        self.fault_events = []
        self.diagnostic_results = []
        
        print(f"✅ System initialized with {len(self.crac_units)} CRAC units")
        print(f"✅ Fault simulation enabled with {len(self.sensor_models)} sensors")
        print(f"✅ Diagnostic engine ready with {len(self.diagnostic_engine.diagnostic_rules)} rules")
        print()
    
    def _initialize_thermal_system(self):
        """Initialize thermal system (room and CRAC units)."""
        
        # Initialize room
        room_config = RoomConfig(
            initial_temp_c=self.config['room']['initial_temp_c'],
            ambient_temp_c=self.config['room']['ambient_temp_c'],
            thermal_mass_kj_per_c=self.config['room']['thermal_mass_kj_per_c'],
            ua_kw_per_c=self.config['room']['ua_kw_per_c'],
            it_load_kw=self.config['room']['it_load_kw'],
            n_virtual_sensors=self.config['room']['n_virtual_sensors']
        )
        self.room = Room(room_config)
        
        # Initialize CRAC units
        self.crac_units = []
        for crac_config in self.config['crac_units']:
            config_obj = CRACConfig(
                unit_id=crac_config['unit_id'],
                q_rated_kw=crac_config['q_rated_kw'],
                efficiency_cop=crac_config['efficiency_cop'],
                min_capacity_pct=crac_config['min_capacity_pct'],
                max_capacity_pct=crac_config['max_capacity_pct'],
                startup_time_s=crac_config['startup_time_s'],
                shutdown_time_s=crac_config['shutdown_time_s'],
                mtbf_hours=crac_config['mtbf_hours'],
                mttr_hours=crac_config['mttr_hours']
            )
            crac = CRACUnit(config_obj)
            self.crac_units.append(crac)
    
    def _initialize_control_system(self):
        """Initialize control system components."""
        
        # PID controller
        pid_config = PIDConfig(
            kp=self.config['pid_controller']['kp'],
            ki=self.config['pid_controller']['ki'],
            kd=self.config['pid_controller']['kd'],
            output_min=self.config['pid_controller']['output_min'],
            output_max=self.config['pid_controller']['output_max']
        )
        self.pid_controller = PIDController(pid_config)
        self.setpoint = self.config['simulation']['setpoint_c']
        
        # Alarm manager
        self.alarm_manager = AlarmManager()
        
        # Control system fault manager
        control_config = create_default_control_system_config()
        self.control_fault_manager = ControlSystemFaultManager(control_config)
    
    def _initialize_fault_simulation(self):
        """Initialize fault simulation components."""
        
        # Temperature sensors with fault simulation
        sensor_configs = create_default_sensor_configs()
        self.sensor_models = []
        for config in sensor_configs:
            sensor = TemperatureSensor(config)
            self.sensor_models.append(sensor)
        
        # Actuator models with fault simulation
        actuator_configs = create_default_actuator_configs()
        self.actuator_models = []
        for config in actuator_configs:
            actuator = ActuatorModel(config)
            self.actuator_models.append(actuator)
        
        print(f"📡 Initialized {len(self.sensor_models)} sensor fault models")
        print(f"🔧 Initialized {len(self.actuator_models)} actuator fault models")
    
    def _initialize_diagnostics(self):
        """Initialize diagnostic and analysis components."""
        
        # Diagnostic engine
        self.diagnostic_engine = DiagnosticEngine()
        
        # Root cause analyzer
        self.root_cause_analyzer = RootCauseAnalyzer()
        
        # Diagnostic reporter
        report_config = ReportConfig(
            report_id="fault_demo",
            title="BAS Fault Simulation Diagnostic Report",
            format=ReportFormat.MARKDOWN,
            output_path="reports/fault_demo/",
            audience="technical",
            detail_level="detailed"
        )
        self.diagnostic_reporter = DiagnosticReporter(report_config)
        
        # Create output directory
        Path("reports/fault_demo").mkdir(parents=True, exist_ok=True)
    
    def inject_demonstration_faults(self):
        """Inject specific faults for demonstration purposes."""
        
        print("💥 Injecting demonstration faults...")
        
        # Inject sensor faults at different times
        fault_schedule = [
            (300, "sensor", 0, "drift"),      # 5 min: Sensor 1 drift
            (600, "sensor", 1, "bias"),       # 10 min: Sensor 2 bias
            (900, "actuator", 0, "stiction"), # 15 min: Actuator 1 stiction
            (1200, "control", None, "short_cycling"), # 20 min: Short cycling
            (1500, "sensor", 2, "stuck"),     # 25 min: Sensor 3 stuck
        ]
        
        current_faults = []
        for fault_time, fault_type, component_idx, fault_name in fault_schedule:
            if self.sim_time >= fault_time and (fault_time, fault_type, component_idx, fault_name) not in current_faults:
                
                if fault_type == "sensor" and component_idx < len(self.sensor_models):
                    from sim.sensor_faults import SensorFaultType, SensorFaultConfig
                    fault_type_map = {
                        "drift": SensorFaultType.DRIFT,
                        "bias": SensorFaultType.BIAS,
                        "stuck": SensorFaultType.STUCK
                    }
                    if fault_name in fault_type_map:
                        self.sensor_models[component_idx].inject_fault(
                            fault_type_map[fault_name], None, self.sim_time)
                        print(f"  🔴 Injected {fault_name} fault in sensor {component_idx+1}")
                
                elif fault_type == "actuator" and component_idx < len(self.actuator_models):
                    from sim.actuator_faults import ActuatorFaultType, ActuatorFaultConfig
                    fault_type_map = {
                        "stiction": ActuatorFaultType.STICTION,
                        "backlash": ActuatorFaultType.BACKLASH,
                        "oscillation": ActuatorFaultType.OSCILLATION
                    }
                    if fault_name in fault_type_map:
                        self.actuator_models[component_idx].inject_fault(
                            fault_type_map[fault_name], None, self.sim_time)
                        print(f"  🔴 Injected {fault_name} fault in actuator {component_idx+1}")
                
                elif fault_type == "control":
                    from control.system_faults import ControlFaultType
                    fault_type_map = {
                        "short_cycling": ControlFaultType.SHORT_CYCLING,
                        "instability": ControlFaultType.LOOP_INSTABILITY,
                        "saturation": ControlFaultType.CONTROLLER_SAT
                    }
                    if fault_name in fault_type_map:
                        self.control_fault_manager.inject_fault(
                            fault_type_map[fault_name], None, self.sim_time)
                        print(f"  🔴 Injected {fault_name} control fault")
                
                current_faults.append((fault_time, fault_type, component_idx, fault_name))
                
                # Log fault event
                self.fault_events.append({
                    'timestamp': self.sim_time,
                    'fault_type': fault_type,
                    'component': component_idx,
                    'fault_name': fault_name,
                    'description': f"{fault_name} fault injected in {fault_type}"
                })
    
    def run_simulation_step(self):
        """Execute one simulation timestep with fault injection and diagnostics."""
        
        # Update sensor readings with faults
        sensor_readings = []
        true_temp = self.room.temp_c
        
        for i, sensor in enumerate(self.sensor_models):
            sensor.update(true_temp, self.dt, self.sim_time)
            sensor_readings.append(sensor.filtered_value)
        
        # Calculate average temperature for control
        avg_temp = sum(sensor_readings) / len(sensor_readings) if sensor_readings else true_temp
        
        # PID control calculation
        pid_output = self.pid_controller.update(avg_temp, self.setpoint, self.dt)
        
        # Apply control system faults
        modified_pid_output, modified_setpoint = self.control_fault_manager.update(
            pid_output, avg_temp, self.setpoint, self.dt, self.sim_time)
        
        # Update actuator models with faults
        for i, actuator in enumerate(self.actuator_models):
            # Simple mapping: each actuator gets portion of total command
            actuator_command = modified_pid_output / len(self.actuator_models)
            actuator.update(actuator_command, self.dt, self.sim_time)
        
        # Calculate total cooling from CRAC units
        total_cooling = 0.0
        for i, crac in enumerate(self.crac_units):
            # Apply actuator position to CRAC command
            if i < len(self.actuator_models):
                actual_command = self.actuator_models[i].position
            else:
                actual_command = modified_pid_output
            
            crac.cmd_pct = actual_command
            crac.enable = actual_command > 5.0  # Enable if command > 5%
            crac.step(self.dt)
            total_cooling += crac.q_cool_kw
        
        # Update room thermal model
        self.room.step(self.dt, total_cooling)
        
        # Update alarm system
        alarm_data = {
            "avg_temp": avg_temp,
            "setpoint": modified_setpoint,
            "crac_states": [crac.get_state() for crac in self.crac_units],
            "sensor_temps": sensor_readings
        }
        self.alarm_manager.update(self.sim_time, alarm_data)
        
        # Run diagnostics
        system_data = {
            "timestamp": self.sim_time,
            "avg_temp": avg_temp,
            "setpoint": modified_setpoint,
            "pid_output": modified_pid_output,
            "sensor_temps": sensor_readings,
            "crac_states": [crac.get_state() for crac in self.crac_units],
            "actuator_states": [act.get_actuator_state() for act in self.actuator_models],
            "active_alarms": [alarm.config.alarm_id for alarm in self.alarm_manager.get_active_alarms()],
            "control_faults": self.control_fault_manager.get_active_faults()
        }
        
        new_diagnostics = self.diagnostic_engine.update(system_data, self.sim_time)
        
        # Perform root cause analysis if new critical diagnostics
        critical_diagnostics = [d for d in new_diagnostics if d.severity.value in ['critical', 'major']]
        if critical_diagnostics:
            diagnostic_dicts = [d.to_dict() for d in new_diagnostics]
            root_cause = self.root_cause_analyzer.analyze_fault(diagnostic_dicts, system_data)
            
            # Generate immediate fault report
            report_path = self.diagnostic_reporter.generate_fault_report(
                diagnostic_dicts, system_data, root_cause.to_dict())
            print(f"📋 Generated fault report: {report_path}")
        
        # Store telemetry data
        telemetry = {
            'timestamp': self.sim_time,
            'room_temp': self.room.temp_c,
            'avg_sensor_temp': avg_temp,
            'setpoint': modified_setpoint,
            'pid_output': pid_output,
            'modified_pid_output': modified_pid_output,
            'total_cooling': total_cooling,
            'active_alarms': len(self.alarm_manager.get_active_alarms()),
            'active_diagnostics': len(self.diagnostic_engine.get_active_diagnostics()),
            'sensor_readings': sensor_readings,
            'crac_states': [crac.get_state() for crac in self.crac_units],
            'fault_events': len(self.fault_events)
        }
        self.telemetry_data.append(telemetry)
        
        # Advance simulation time
        self.sim_time += self.dt
    
    def display_status(self):
        """Display current simulation status."""
        
        if self.sim_time - self.last_output_time >= self.output_interval:
            
            # Calculate summary statistics
            avg_temp = sum(s.filtered_value for s in self.sensor_models) / len(self.sensor_models)
            active_faults = sum(len(s.get_active_faults()) for s in self.sensor_models)
            active_faults += sum(len(a.get_active_faults()) for a in self.actuator_models)
            active_faults += len(self.control_fault_manager.get_active_faults())
            
            active_alarms = len(self.alarm_manager.get_active_alarms())
            active_diagnostics = len(self.diagnostic_engine.get_active_diagnostics())
            
            # Display status
            elapsed_min = self.sim_time / 60.0
            total_min = self.duration / 60.0
            progress = (self.sim_time / self.duration) * 100
            
            print(f"⏱️  Time: {elapsed_min:5.1f}/{total_min:4.1f} min ({progress:5.1f}%) | "
                  f"🌡️  Temp: {avg_temp:5.1f}°C | "
                  f"🔥 Faults: {active_faults:2d} | "
                  f"🚨 Alarms: {active_alarms:2d} | "
                  f"🔍 Diagnostics: {active_diagnostics:2d}")
            
            # Show active faults
            if active_faults > 0:
                fault_details = []
                for i, sensor in enumerate(self.sensor_models):
                    faults = sensor.get_active_faults()
                    if faults:
                        fault_details.append(f"S{i+1}:{','.join(f.value for f in faults)}")
                
                for i, actuator in enumerate(self.actuator_models):
                    faults = actuator.get_active_faults()
                    if faults:
                        fault_details.append(f"A{i+1}:{','.join(f.value for f in faults)}")
                
                control_faults = self.control_fault_manager.get_active_faults()
                if control_faults:
                    fault_details.append(f"C:{','.join(f.value for f in control_faults)}")
                
                if fault_details:
                    print(f"    Active Faults: {' | '.join(fault_details)}")
            
            self.last_output_time = self.sim_time
    
    def run_demonstration(self, duration_minutes: Optional[float] = None):
        """Run the complete fault simulation demonstration."""
        
        if duration_minutes:
            self.duration = duration_minutes * 60.0
        
        print("🚀 Starting Fault Simulation Demonstration")
        print(f"Duration: {self.duration/60:.1f} minutes")
        print("=" * 60)
        
        start_time = time.time()
        
        # Main simulation loop
        while self.sim_time < self.duration:
            
            # Inject demonstration faults at scheduled times
            self.inject_demonstration_faults()
            
            # Run simulation step
            self.run_simulation_step()
            
            # Display status
            self.display_status()
        
        # Generate final reports
        print("\n📊 Generating final diagnostic reports...")
        self._generate_final_reports()
        
        elapsed_real_time = time.time() - start_time
        print(f"\n✅ Simulation completed in {elapsed_real_time:.1f} seconds")
        print(f"📈 Simulated {self.duration/60:.1f} minutes of system operation")
        print(f"🔥 Total fault events: {len(self.fault_events)}")
        print(f"📋 Reports generated in: reports/fault_demo/")
    
    def _generate_final_reports(self):
        """Generate comprehensive final reports."""
        
        # System health summary
        health_data = self.diagnostic_engine.get_system_health_summary()
        
        # Performance history for trending
        performance_history = [
            {
                'timestamp': data['timestamp'],
                'temperature': data['avg_sensor_temp'],
                'system_cop': sum(crac['q_cool_kw'] for crac in data['crac_states']) /
                             max(sum(crac['power_kw'] for crac in data['crac_states']), 0.1)
            }
            for data in self.telemetry_data[-100:]  # Last 100 data points
        ]
        
        # Generate health report
        health_report_path = self.diagnostic_reporter.generate_system_health_report(
            health_data, performance_history)
        print(f"  📊 System health report: {health_report_path}")
        
        # Generate maintenance report if there are active diagnostics
        active_diagnostics = self.diagnostic_engine.get_active_diagnostics()
        if active_diagnostics:
            maintenance_actions = []
            equipment_status = {"crac_units": len(self.crac_units), "sensors": len(self.sensor_models)}
            
            maintenance_report_path = self.diagnostic_reporter.generate_maintenance_report(
                maintenance_actions, equipment_status)
            print(f"  🔧 Maintenance report: {maintenance_report_path}")
        
        # Export telemetry data
        telemetry_path = "reports/fault_demo/telemetry_data.json"
        with open(telemetry_path, 'w') as f:
            json.dump(self.telemetry_data, f, indent=2, default=str)
        print(f"  📁 Telemetry data: {telemetry_path}")
        
        # Export fault events
        fault_events_path = "reports/fault_demo/fault_events.json"
        with open(fault_events_path, 'w') as f:
            json.dump(self.fault_events, f, indent=2, default=str)
        print(f"  💥 Fault events: {fault_events_path}")


def main():
    """Main entry point for fault simulation demonstration."""
    
    parser = argparse.ArgumentParser(
        description="Professional BAS Fault Simulation Demonstration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run 15-minute demonstration with moderate faults
    python demo_fault_simulation.py --duration 15
    
    # Run aggressive fault scenario
    python demo_fault_simulation.py --duration 20 --config config/scenarios/fault_demo.yaml
    
    # Custom output directory
    python demo_fault_simulation.py --output reports/custom_demo/
        """
    )
    
    parser.add_argument('--duration', type=float, default=15.0,
                       help='Simulation duration in minutes (default: 15)')
    parser.add_argument('--config', default='config/scenarios/fault_demo.yaml',
                       help='Configuration file path')
    parser.add_argument('--output', default='reports/fault_demo/',
                       help='Output directory for reports')
    
    args = parser.parse_args()
    
    try:
        # Initialize and run demonstration
        demo = FaultSimulationDemo(args.config)
        demo.run_demonstration(args.duration)
        
        print("\n🎉 Fault simulation demonstration completed successfully!")
        print(f"📂 Results available in: {args.output}")
        print("\n🔍 Review the generated reports to see:")
        print("  • Real-time fault detection and diagnosis")
        print("  • Root cause analysis with maintenance recommendations")
        print("  • System performance impact assessment")
        print("  • Professional diagnostic documentation")
        
    except KeyboardInterrupt:
        print("\n⚠️  Demonstration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()