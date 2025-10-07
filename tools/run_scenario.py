#!/usr/bin/env python3
# tools/run_scenario.py
"""
BAS Scenario Runner for Data Center Testing

Professional scenario execution framework for validating BAS control logic:
- Load scenario configurations from JSON files
- Execute complex test patterns (load ramps, equipment failures)
- Validate system response against criteria
- Generate detailed test reports with telemetry

Usage:
    python tools/run_scenario.py scenarios/rising_load.json
    python tools/run_scenario.py scenarios/crac_failure.json --historian --output results/
"""
from __future__ import annotations
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sim.environment import Room, RoomConfig
from sim.crac import CRACUnit, CRACConfig
from control.pid import PIDController, PIDConfig
from control.sequences import CRACSequencer, StagingConfig
from control.alarms import AlarmManager
from telemetry.historian import CSVHistorian, HistorianConfig


class ScenarioRunner:
    """
    Professional scenario execution engine for BAS testing.
    
    Features:
    - JSON-driven scenario configuration
    - Dynamic load profiles and failure injection
    - Real-time system monitoring and validation
    - Comprehensive test reporting
    - Integration with historian and alarm systems
    """
    
    def __init__(self):
        self.scenario_config: Dict = {}
        self.room: Optional[Room] = None
        self.pid: Optional[PIDController] = None
        self.sequencer: Optional[CRACSequencer] = None
        self.alarm_mgr: Optional[AlarmManager] = None
        self.historian: Optional[CSVHistorian] = None
        
        # Test results
        self.test_results: Dict = {}
        self.telemetry_data: List[Dict] = []
        
    def load_scenario(self, scenario_path: str) -> None:
        """Load scenario configuration from JSON file."""
        with open(scenario_path, 'r') as f:
            self.scenario_config = json.load(f)
        
        print(f"📋 Loaded scenario: {self.scenario_config['scenario']['name']}")
        print(f"   Description: {self.scenario_config['scenario']['description']}")
    
    def setup_system(self, enable_historian: bool = False) -> None:
        """Initialize BAS system components from scenario config."""
        
        # Room configuration
        room_cfg_data = self.scenario_config.get('room_config', {})
        room_cfg = RoomConfig(**room_cfg_data)
        self.room = Room(room_cfg)
        
        # PID controller (use reasonable defaults)
        pid_cfg = PIDConfig(
            kp=3.0, ki=0.15, kd=0.08,
            output_min=0.0, output_max=100.0,
            rate_limit=15.0, integral_windup_limit=40.0
        )
        self.pid = PIDController(pid_cfg)
        
        # CRAC units (3x 50kW standard configuration)
        cracs: List[CRACUnit] = []
        for i in range(3):
            crac_cfg = CRACConfig(
                unit_id=f"CRAC-{i+1:02d}",
                q_rated_kw=60.0, efficiency_cop=3.5,  # Increased capacity
                min_capacity_pct=20.0, max_capacity_pct=100.0,
                startup_time_s=30.0, shutdown_time_s=15.0,  # Faster for scenarios
                mtbf_hours=8760.0, mttr_hours=4.0
            )
            cracs.append(CRACUnit(crac_cfg, seed=42 + i))
        
        # CRAC sequencer
        staging_cfg = StagingConfig(
            temp_error_threshold=0.8, staging_delay_s=180.0,
            destaging_delay_s=300.0, rotation_runtime_hours=24.0,
            enable_rotation=True, staging_hysteresis=0.2,
            destaging_hysteresis=0.3
        )
        self.sequencer = CRACSequencer(cracs, staging_cfg)
        
        # Alarm manager
        self.alarm_mgr = AlarmManager()
        
        # Initialize room at proper starting temperature
        scenario = self.scenario_config['scenario']
        self.room.temp_c = scenario.get('initial_temp_c', 22.0)
        
        # Pre-condition system for stable operation (run setup for 10 minutes)
        print("🔄 Pre-conditioning system to steady state...")
        setup_steps = 600  # 10 minutes at 1s timestep
        for step in range(setup_steps):
            # Enable LEAD CRAC and run PID to find equilibrium
            pid_output = self.pid.update(scenario.get('setpoint_c', 22.0), self.room.temp_c, 1.0)
            self.sequencer.update(1.0, scenario.get('setpoint_c', 22.0), self.room.temp_c, pid_output)
            total_cooling = self.sequencer.get_total_cooling_kw()
            self.room.step(1.0, total_cooling)
            
            # Show progress every 2 minutes
            if step % 120 == 0:
                print(f"   Setup: {step/60:.1f}m | Temp: {self.room.temp_c:.1f}°C | Cooling: {total_cooling:.1f}kW")
        
        print(f"✅ System pre-conditioned: {self.room.temp_c:.1f}°C")
        
        # Don't reset PID - keep the integral state for smooth transition
        
        # Historian (optional)
        if enable_historian:
            hist_cfg = HistorianConfig(
                base_directory="scenario_logs",
                file_prefix=f"scenario_{int(time.time())}",
                sample_interval_s=5.0
            )
            self.historian = CSVHistorian(hist_cfg)
        
        print("🔧 System components initialized")
    
    def execute_scenario(self) -> Dict:
        """Execute the loaded scenario and return results."""
        scenario = self.scenario_config['scenario']
        duration_s = scenario['duration_minutes'] * 60.0
        setpoint_c = scenario['setpoint_c']
        
        dt = 1.0  # 1 second timestep
        total_steps = int(duration_s / dt)
        
        print(f"🚀 Starting scenario execution")
        print(f"   Duration: {scenario['duration_minutes']:.1f} minutes")
        print(f"   Setpoint: {setpoint_c:.1f}°C")
        print("=" * 60)
        
        # Execution state
        start_time = time.time()
        lag_staging_time: Optional[float] = None
        max_temp_reached = self.room.temp_c
        alarms_triggered: List[str] = []
        
        for step in range(total_steps):
            sim_time = step * dt
            
            # Apply dynamic load profile
            self._apply_load_profile(sim_time)
            
            # Apply failure events
            self._apply_failure_events(sim_time)
            
            # PID control
            pid_output = self.pid.update(setpoint_c, self.room.temp_c, dt)
            
            # CRAC sequencer
            self.sequencer.update(dt, setpoint_c, self.room.temp_c, pid_output)
            
            # Room thermal dynamics
            total_cooling = self.sequencer.get_total_cooling_kw()
            self.room.step(dt, total_cooling)
            
            # Update alarms
            system_data = self._collect_system_data(sim_time, setpoint_c, pid_output)
            self.alarm_mgr.update(sim_time, system_data)
            
            # Track key metrics
            max_temp_reached = max(max_temp_reached, self.room.temp_c)
            
            # Check for LAG staging
            if lag_staging_time is None:
                system_state = self.sequencer.get_system_state()
                if system_state['lag_staged']:
                    lag_staging_time = sim_time
            
            # Track active alarms
            active_alarms = self.alarm_mgr.get_active_alarms()
            for alarm in active_alarms:
                if alarm.config.alarm_id not in alarms_triggered:
                    alarms_triggered.append(alarm.config.alarm_id)
            
            # Log to historian
            if self.historian:
                self._log_telemetry(sim_time, setpoint_c, pid_output, system_data)
            
            # Collect telemetry
            self.telemetry_data.append({
                'time_s': sim_time,
                'temp_c': self.room.temp_c,
                'setpoint_c': setpoint_c,
                'pid_output': pid_output,
                'total_cooling': total_cooling,
                'lag_staged': system_state['lag_staged'],
                'active_alarms': len(active_alarms)
            })
            
            # Periodic status
            if step % 60 == 0:  # Every minute
                temp_error = abs(self.room.temp_c - setpoint_c)
                print(f"⏱️  {sim_time/60:5.1f}m | "
                      f"🌡️  {self.room.temp_c:5.2f}°C | "
                      f"❄️  {total_cooling:5.1f}kW | "
                      f"🎯 ±{temp_error:.2f}°C | "
                      f"🚨 {len(active_alarms)} alarms")
        
        execution_time = time.time() - start_time
        
        # Compile results
        results = self._validate_scenario_results(
            lag_staging_time, max_temp_reached, alarms_triggered
        )
        results.update({
            'execution_time_s': execution_time,
            'total_steps': total_steps,
            'scenario_name': scenario['name']
        })
        
        self.test_results = results
        return results
    
    def _apply_load_profile(self, sim_time: float) -> None:
        """Apply dynamic IT load changes based on scenario profile."""
        load_profile = self.scenario_config.get('load_profile')
        if not load_profile:
            return
        
        if load_profile['type'] == 'ramp':
            start_time = load_profile['start_time_s']
            end_time = load_profile['end_time_s']
            start_load = load_profile['start_load_kw']
            end_load = load_profile['end_load_kw']
            
            if start_time <= sim_time <= end_time:
                # Linear interpolation
                progress = (sim_time - start_time) / (end_time - start_time)
                current_load = start_load + progress * (end_load - start_load)
                self.room.cfg.it_load_kw = current_load
            elif sim_time > end_time:
                self.room.cfg.it_load_kw = end_load
    
    def _apply_failure_events(self, sim_time: float) -> None:
        """Apply equipment failure events based on scenario."""
        failure_events = self.scenario_config.get('failure_events', [])
        
        for event in failure_events:
            if event['type'] == 'crac_failure':
                failure_time = event['failure_time_s']
                duration_hours = event['duration_hours']
                target_role = event['target_unit']
                
                if abs(sim_time - failure_time) < 0.5:  # Within 0.5s of event
                    # Find target unit by role
                    for assignment in self.sequencer.assignments:
                        if assignment.role.value.upper() == target_role.upper():
                            assignment.unit.force_failure(duration_hours)
                            print(f"💥 Forced failure: {assignment.unit.cfg.unit_id} "
                                  f"({target_role}) at t={sim_time:.0f}s")
                            break
    
    def _collect_system_data(self, sim_time: float, setpoint_c: float, 
                           pid_output: float) -> Dict:
        """Collect system data for alarm evaluation."""
        # Get CRAC states
        crac_states = []
        for assignment in self.sequencer.assignments:
            crac_states.append({
                'unit_id': assignment.unit.cfg.unit_id,
                'status': assignment.unit.status.value,
                'cmd_pct': assignment.unit.cmd_pct,
                'q_cool_kw': assignment.unit.q_cool_kw,
                'power_kw': assignment.unit.power_kw,
                'failed': assignment.unit.failed
            })
        
        # Room sensors (simulate multiple sensors with small variance)
        import random
        base_temp = self.room.temp_c
        sensor_temps = [
            base_temp + random.uniform(-0.2, 0.2) 
            for _ in range(self.room.cfg.n_virtual_sensors)
        ]
        
        return {
            'avg_temp': self.room.temp_c,
            'setpoint': setpoint_c,
            'sensor_temps': sensor_temps,
            'crac_states': crac_states,
            'pid_output': pid_output,
            'sim_time': sim_time
        }
    
    def _log_telemetry(self, sim_time: float, setpoint_c: float,
                      pid_output: float, system_data: Dict) -> None:
        """Log data to historian if enabled."""
        if not self.historian:
            return
        
        # Room data
        room_data = {
            'setpoint_c': setpoint_c,
            'avg_temp_c': self.room.temp_c,
            'sensor_temps': system_data['sensor_temps']
        }
        
        # CRAC data
        crac_data = system_data['crac_states']
        
        # Alarm data
        alarm_summary = self.alarm_mgr.get_alarm_summary()
        active_alarms = [a.config.alarm_id for a in self.alarm_mgr.get_active_alarms()]
        
        # Staging data
        system_state = self.sequencer.get_system_state()
        staging_data = {
            'lead_unit': next((a['unit_id'] for a in system_state['assignments']
                              if a['role'] == 'lead'), ''),
            'lag_staged': system_state['lag_staged'],
            'standby_staged': system_state['standby_staged']
        }
        
        self.historian.log_data(
            sim_time, room_data, crac_data, alarm_summary, pid_output,
            staging_data=staging_data, active_alarm_list=active_alarms
        )
    
    def _validate_scenario_results(self, lag_staging_time: Optional[float],
                                 max_temp: float, alarms: List[str]) -> Dict:
        """Validate scenario results against expected criteria."""
        scenario = self.scenario_config['scenario']
        expected = self.scenario_config.get('expected_behavior', {})
        criteria = self.scenario_config.get('validation_criteria', {})
        
        results = {
            'scenario_name': scenario['name'],
            'test_passed': True,
            'validation_details': {},
            'lag_staging_time_s': lag_staging_time,
            'max_temperature_c': max_temp,
            'alarms_triggered': alarms
        }
        
        # Temperature validation
        max_allowed = criteria.get('max_temperature_c', 25.0)
        temp_pass = max_temp <= max_allowed
        results['validation_details']['temperature_control'] = {
            'passed': temp_pass,
            'max_temp_c': max_temp,
            'limit_c': max_allowed
        }
        
        # LAG staging validation (if applicable)
        if 'min_lag_staging_time_s' in criteria:
            min_time = criteria['min_lag_staging_time_s']
            max_time = criteria['max_lag_staging_time_s']
            
            staging_pass = (lag_staging_time is not None and 
                           min_time <= lag_staging_time <= max_time)
            results['validation_details']['lag_staging'] = {
                'passed': staging_pass,
                'actual_time_s': lag_staging_time,
                'min_time_s': min_time,
                'max_time_s': max_time
            }
        
        # Alarm validation
        allowed_alarms = set(criteria.get('alarm_tolerance', []))
        required_alarms = set(criteria.get('required_alarms', []))
        triggered_alarms = set(alarms)
        
        unexpected_alarms = triggered_alarms - allowed_alarms - required_alarms
        missing_alarms = required_alarms - triggered_alarms
        
        alarm_pass = len(unexpected_alarms) == 0 and len(missing_alarms) == 0
        results['validation_details']['alarms'] = {
            'passed': alarm_pass,
            'unexpected_alarms': list(unexpected_alarms),
            'missing_alarms': list(missing_alarms),
            'triggered_alarms': alarms
        }
        
        # Overall pass/fail
        all_validations = [v['passed'] for v in results['validation_details'].values()]
        results['test_passed'] = all(all_validations)
        
        return results
    
    def generate_report(self, output_dir: Optional[str] = None) -> str:
        """Generate detailed test report."""
        if not self.test_results:
            return "No test results available"
        
        report_lines = []
        results = self.test_results
        
        # Header
        report_lines.extend([
            "=" * 80,
            f"BAS SCENARIO TEST REPORT",
            "=" * 80,
            f"Scenario: {results['scenario_name']}",
            f"Execution Time: {results['execution_time_s']:.2f}s",
            f"Overall Result: {'✅ PASS' if results['test_passed'] else '❌ FAIL'}",
            ""
        ])
        
        # Validation details
        report_lines.append("VALIDATION RESULTS:")
        for test_name, details in results['validation_details'].items():
            status = "✅ PASS" if details['passed'] else "❌ FAIL"
            report_lines.append(f"  {test_name.upper()}: {status}")
            
            for key, value in details.items():
                if key != 'passed':
                    report_lines.append(f"    {key}: {value}")
        
        report_lines.append("")
        
        # Key metrics
        report_lines.extend([
            "KEY METRICS:",
            f"  Max Temperature: {results['max_temperature_c']:.2f}°C",
            f"  LAG Staging Time: {results['lag_staging_time_s']:.1f}s" 
            if results['lag_staging_time_s'] else "  LAG Staging: Not triggered",
            f"  Alarms Triggered: {', '.join(results['alarms_triggered']) if results['alarms_triggered'] else 'None'}",
            ""
        ])
        
        # Final status
        if results['test_passed']:
            report_lines.extend([
                "🎉 SCENARIO VALIDATION SUCCESSFUL",
                "   System behavior meets all specified criteria"
            ])
        else:
            report_lines.extend([
                "⚠️  SCENARIO VALIDATION FAILED", 
                "   Review validation details above"
            ])
        
        report = "\n".join(report_lines)
        
        # Save to file if output directory specified
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            timestamp = int(time.time())
            report_file = Path(output_dir) / f"scenario_report_{timestamp}.txt"
            report_file.write_text(report)
            print(f"📊 Report saved to: {report_file}")
        
        return report
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self.historian:
            self.historian.close()


def main():
    parser = argparse.ArgumentParser(description='Run BAS scenario tests')
    parser.add_argument('scenario_file', help='Path to scenario JSON file')
    parser.add_argument('--historian', action='store_true', 
                       help='Enable CSV historian logging')
    parser.add_argument('--output', help='Output directory for reports')
    
    args = parser.parse_args()
    
    # Validate scenario file exists
    if not Path(args.scenario_file).exists():
        print(f"❌ Scenario file not found: {args.scenario_file}")
        return 1
    
    try:
        # Initialize and run scenario
        runner = ScenarioRunner()
        runner.load_scenario(args.scenario_file)
        runner.setup_system(enable_historian=args.historian)
        
        # Execute scenario
        results = runner.execute_scenario()
        
        print("\n" + "=" * 60)
        
        # Generate and display report
        report = runner.generate_report(args.output)
        print(report)
        
        # Cleanup
        runner.cleanup()
        
        # Return appropriate exit code
        return 0 if results['test_passed'] else 1
        
    except Exception as e:
        print(f"❌ Scenario execution failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())