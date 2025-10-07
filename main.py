# main.py
"""
Professional Data Center BAS Simulation Platform

Enterprise-grade Building Automation System simulation with:
- Multi-CRAC lead/lag/standby staging
- PID temperature control with anti-windup
- Thermal room dynamics with heat balance
- Energy tracking and performance metrics
- Professional configuration management
- Comprehensive CLI interface

Usage:
    python main.py run --config config/default.yaml
    python main.py run --config config/default.yaml --scenario high_load
    python main.py validate --config config/custom.yaml
    python main.py benchmark --config config/default.yaml --duration 30
    python main.py export --config config/default.yaml --format csv

For more information: python main.py --help
"""

from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
import statistics

# Configuration management
from config.config_loader import ConfigLoader, load_config_with_overrides, ConfigValidationError

# Core simulation components
from sim.environment import Room, RoomConfig
from sim.crac import CRACUnit, CRACConfig
from control.pid import PIDController, PIDConfig
from control.sequences import CRACSequencer, StagingConfig


def create_system_from_config(config: Dict[str, Any]) -> tuple[Room, PIDController, CRACSequencer]:
    """
    Create BAS simulation system from configuration.
    
    Args:
        config: Validated configuration dictionary
        
    Returns:
        Tuple of (room, pid_controller, crac_sequencer)
    """
    # Create room from config
    room_cfg = RoomConfig(**config['room'])
    room = Room(room_cfg)
    
    # Create PID controller from config
    pid_cfg = PIDConfig(**config['pid_controller'])
    pid = PIDController(pid_cfg)
    
    # Create CRAC units from config
    cracs: List[CRACUnit] = []
    for i, crac_config in enumerate(config['crac_units']):
        crac_cfg = CRACConfig(**crac_config)
        cracs.append(CRACUnit(crac_cfg, seed=42 + i))
    
    # Create CRAC sequencer from config
    staging_cfg = StagingConfig(**config.get('staging_config', {}))
    sequencer = CRACSequencer(cracs, staging_cfg)
    
    return room, pid, sequencer


def run_simulation(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run BAS simulation with given configuration.
    
    Args:
        config: Validated configuration dictionary
        
    Returns:
        Simulation results dictionary
    """
    print(f"🏗️  Creating BAS system from configuration...")
    room, pid, sequencer = create_system_from_config(config)
    
    # Simulation parameters from config
    sim_config = config['simulation']
    duration_minutes = sim_config['duration_minutes']
    timestep_s = sim_config['timestep_s']
    output_interval_s = sim_config.get('output_interval_s', 60.0)
    setpoint_c = sim_config['setpoint_c']
    
    total_steps = int(duration_minutes * 60 / timestep_s)
    output_interval_steps = int(output_interval_s / timestep_s)
    
    # Data collection
    temperatures: List[float] = []
    cooling_outputs: List[float] = []
    crac_states: List[dict] = []
    
    print(f"🚀 Starting {duration_minutes:.1f} minute simulation")
    print(f"📊 Setpoint: {setpoint_c:.1f}°C, Timestep: {timestep_s:.1f}s")
    print("=" * 60)
    
    start_time = time.time()
    
    for step in range(total_steps):
        sim_time = step * timestep_s
        
        # PID control calculation
        pid_output = pid.update(setpoint_c, room.temp_c, timestep_s)
        
        # CRAC sequencer update
        sequencer.update(timestep_s, setpoint_c, room.temp_c, pid_output)
        
        # Get total cooling from all CRACs
        total_cooling_kw = sequencer.get_total_cooling_kw()
        
        # Room thermal dynamics
        room.step(timestep_s, total_cooling_kw)
        
        # Data collection
        temperatures.append(room.temp_c)
        cooling_outputs.append(total_cooling_kw)
        
        # Periodic status updates
        if step % (5 * 60 // timestep_s) == 0:  # Every 5 minutes
            elapsed_min = sim_time / 60.0
            temp_error = abs(room.temp_c - setpoint_c)
            total_power = sequencer.get_total_power_kw()
            
            print(f"⏱️  {elapsed_min:5.1f}m | "
                  f"🌡️  {room.temp_c:5.2f}°C | "
                  f"❄️  {total_cooling_kw:5.1f}kW | "
                  f"⚡ {total_power:5.1f}kW | "
                  f"📊 {pid_output:5.1f}% | "
                  f"🎯 ±{temp_error:.2f}°C")
        
        # Collect detailed data at output interval
        if step % output_interval_steps == 0:
            system_state = sequencer.get_system_state()
            crac_states.append({
                'time_min': sim_time / 60.0,
                'temp_c': room.temp_c,
                'setpoint_c': setpoint_c,
                'pid_output_pct': pid_output,
                'total_cooling_kw': total_cooling_kw,
                'total_power_kw': sequencer.get_total_power_kw(),
                'lag_staged': system_state['lag_staged'],
                'standby_staged': system_state['standby_staged'],
                'num_running': sum(1 for a in system_state['assignments']
                                   if a['status'] == 'running')
            })
    
    elapsed_time = time.time() - start_time
    
    # Performance analysis
    avg_temp = statistics.mean(temperatures)
    temp_std = statistics.stdev(temperatures) if len(temperatures) > 1 else 0
    max_error = max(abs(t - setpoint_c) for t in temperatures)
    avg_error = statistics.mean([abs(t - setpoint_c) for t in temperatures])
    
    # Energy performance
    avg_cooling = statistics.mean(cooling_outputs)
    total_energy_kwh = sum(cooling_outputs) * timestep_s / 3600.0
    
    # Control performance
    temp_in_range = sum(1 for t in temperatures if abs(t - setpoint_c) <= 0.5)
    control_accuracy = temp_in_range / len(temperatures) * 100
    
    print("=" * 60)
    print(f"✅ Simulation Complete - Runtime: {elapsed_time:.2f}s")
    print()
    print("🎯 TEMPERATURE PERFORMANCE:")
    print(f"   Average: {avg_temp:.3f}°C (target: {setpoint_c:.1f}°C)")
    print(f"   Std Dev: {temp_std:.3f}°C")
    print(f"   Max Error: {max_error:.3f}°C")
    print(f"   Avg Error: {avg_error:.3f}°C")
    print(f"   In Range (±0.5°C): {control_accuracy:.1f}%")
    print()
    print("❄️  COOLING PERFORMANCE:")
    print(f"   Average Output: {avg_cooling:.1f}kW")
    print(f"   Total Energy: {total_energy_kwh:.2f}kWh")
    print()
    
    # Final system state
    final_state = sequencer.get_system_state()
    print("🏭 FINAL CRAC STATUS:")
    for assignment in final_state['assignments']:
        status_icon = "🟢" if assignment['status'] == 'running' else "🔴"
        print(f"   {assignment['unit_id']}: {status_icon} "
              f"{assignment['role'].upper()} | {assignment['status']} | "
              f"{assignment['cmd_pct']:.1f}% | "
              f"{assignment['q_cool_kw']:.1f}kW")
    
    # Test criteria evaluation
    print()
    print("📋 PERFORMANCE CRITERIA:")
    temp_pass = avg_error <= 0.5 and temp_std <= 0.3
    control_pass = control_accuracy >= 90.0
    efficiency_pass = avg_cooling > 0
    
    print(f"   Temperature Control: {'✅ PASS' if temp_pass else '❌ FAIL'} "
          f"(avg error ≤ 0.5°C, std dev ≤ 0.3°C)")
    print(f"   Control Accuracy: {'✅ PASS' if control_pass else '❌ FAIL'} "
          f"({control_accuracy:.1f}% ≥ 90%)")
    print(f"   System Efficiency: {'✅ PASS' if efficiency_pass else '❌ FAIL'}")
    
    overall_pass = temp_pass and control_pass and efficiency_pass
    print(f"\n🏆 OVERALL: {'✅ PASS' if overall_pass else '❌ FAIL'}")
    
    return {
        'duration_minutes': duration_minutes,
        'setpoint_c': setpoint_c,
        'avg_temp_c': avg_temp,
        'temp_std_c': temp_std,
        'max_error_c': max_error,
        'avg_error_c': avg_error,
        'control_accuracy_pct': control_accuracy,
        'avg_cooling_kw': avg_cooling,
        'total_energy_kwh': total_energy_kwh,
        'test_passed': overall_pass,
        'simulation_time_s': elapsed_time,
        'detailed_data': crac_states
    }


def validate_config_file(config_path: Path) -> bool:
    """
    Validate configuration file and report errors.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        True if valid, False if validation errors found
    """
    try:
        # Load schema
        schema_path = config_path.parent / "schemas" / "config_schema.yaml"
        loader = ConfigLoader(schema_path if schema_path.exists() else None)
        
        # Load and validate config
        config = loader.load_config(config_path)
        errors = loader.validate_config(config)
        
        if errors:
            print("❌ Configuration validation failed:")
            for error in errors:
                print(f"   {error}")
            return False
        else:
            print("✅ Configuration validation passed")
            print("\n📋 Configuration Summary:")
            print(loader.get_config_summary(config))
            return True
            
    except ConfigValidationError as e:
        print(f"❌ Configuration error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def export_results(config: Dict[str, Any], results: Dict[str, Any], format_type: str = "csv") -> None:
    """
    Export simulation results to specified format.
    
    Args:
        config: Configuration used for simulation
        results: Simulation results
        format_type: Export format ('csv', 'json')
    """
    if format_type == "csv":
        import csv
        from datetime import datetime
        
        # Create output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path("reports") / f"simulation_{timestamp}.csv"
        output_path.parent.mkdir(exist_ok=True)
        
        # Write detailed data to CSV
        with open(output_path, 'w', newline='') as csvfile:
            if results['detailed_data']:
                fieldnames = results['detailed_data'][0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results['detailed_data'])
        
        print(f"📊 Results exported to: {output_path}")
    
    elif format_type == "json":
        import json
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path("reports") / f"simulation_{timestamp}.json"
        output_path.parent.mkdir(exist_ok=True)
        
        export_data = {
            'config': config,
            'results': results,
            'timestamp': timestamp
        }
        
        with open(output_path, 'w') as jsonfile:
            json.dump(export_data, jsonfile, indent=2)
        
        print(f"📊 Results exported to: {output_path}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Professional Data Center BAS Simulation Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s run --config config/default.yaml
  %(prog)s run --config config/default.yaml --scenario high_load
  %(prog)s run --config config/default.yaml --set room.it_load_kw=60.0
  %(prog)s validate --config config/custom.yaml
  %(prog)s benchmark --config config/default.yaml --duration 30
  %(prog)s export --config config/default.yaml --format csv
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run BAS simulation')
    run_parser.add_argument('--config', type=Path, default='config/default.yaml',
                           help='Configuration file path')
    run_parser.add_argument('--scenario', type=str,
                           help='Scenario name (looks for config/scenarios/{name}.yaml)')
    run_parser.add_argument('--set', action='append', dest='overrides',
                           help='Override config parameter (e.g., --set room.temp=25.0)')
    run_parser.add_argument('--export', choices=['csv', 'json'],
                           help='Export results to specified format')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate configuration file')
    validate_parser.add_argument('--config', type=Path, required=True,
                                help='Configuration file to validate')
    
    # Benchmark command
    benchmark_parser = subparsers.add_parser('benchmark', help='Run performance benchmark')
    benchmark_parser.add_argument('--config', type=Path, default='config/default.yaml',
                                 help='Configuration file path')
    benchmark_parser.add_argument('--duration', type=float, default=30.0,
                                 help='Benchmark duration in minutes')
    benchmark_parser.add_argument('--iterations', type=int, default=1,
                                 help='Number of benchmark iterations')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export configuration template')
    export_parser.add_argument('--config', type=Path, default='config/default.yaml',
                              help='Configuration file path')
    export_parser.add_argument('--format', choices=['yaml', 'json'], default='yaml',
                              help='Export format')
    export_parser.add_argument('--output', type=Path,
                              help='Output file path')
    
    args = parser.parse_args()
    
    # Handle missing command
    if not args.command:
        parser.print_help()
        return 1
    
    # Validate command
    if args.command == 'validate':
        success = validate_config_file(args.config)
        return 0 if success else 1
    
    # Run command
    elif args.command == 'run':
        try:
            # Load configuration with overrides
            config = load_config_with_overrides(
                args.config,
                scenario=args.scenario,
                cli_overrides=args.overrides or []
            )
            
            print("🏭 Data Center BAS Simulation Platform")
            print("=" * 60)
            
            # Run simulation
            results = run_simulation(config)
            
            # Export results if requested
            if args.export:
                export_results(config, results, args.export)
            
            return 0 if results['test_passed'] else 1
            
        except ConfigValidationError as e:
            print(f"❌ Configuration error: {e}")
            return 1
        except Exception as e:
            print(f"❌ Simulation error: {e}")
            return 1
    
    # Benchmark command
    elif args.command == 'benchmark':
        try:
            config = load_config_with_overrides(args.config)
            
            # Override duration for benchmark
            config['simulation']['duration_minutes'] = args.duration
            
            print(f"🚀 Running benchmark: {args.iterations} iterations of {args.duration} minutes")
            
            total_start = time.time()
            all_results = []
            
            for i in range(args.iterations):
                print(f"\n--- Iteration {i+1}/{args.iterations} ---")
                results = run_simulation(config)
                all_results.append(results)
            
            total_time = time.time() - total_start
            
            # Benchmark summary
            print("\n" + "=" * 60)
            print("📊 BENCHMARK SUMMARY")
            print(f"Total Runtime: {total_time:.2f}s")
            print(f"Average Simulation Time: {statistics.mean([r['simulation_time_s'] for r in all_results]):.2f}s")
            print(f"Success Rate: {sum(1 for r in all_results if r['test_passed'])}/{len(all_results)}")
            
            return 0
            
        except Exception as e:
            print(f"❌ Benchmark error: {e}")
            return 1
    
    # Export command  
    elif args.command == 'export':
        try:
            config = load_config_with_overrides(args.config)
            
            if args.output:
                output_path = args.output
            else:
                output_path = Path(f"exported_config.{args.format}")
            
            if args.format == 'yaml':
                import yaml
                with open(output_path, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False, indent=2)
            else:  # json
                import json
                with open(output_path, 'w') as f:
                    json.dump(config, f, indent=2)
            
            print(f"📄 Configuration exported to: {output_path}")
            return 0
            
        except Exception as e:
            print(f"❌ Export error: {e}")
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())