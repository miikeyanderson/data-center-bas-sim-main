# main.py
"""
Data Center BAS Simulation - End-to-End Integration

Professional BAS implementation demonstrating:
- Multi-CRAC lead/lag/standby staging
- PID temperature control with anti-windup
- Thermal room dynamics with heat balance
- Energy tracking and performance metrics
- Realistic startup/shutdown sequences

Usage:
    python main.py

Expected results:
- Temperature control within ±0.5°C under steady load
- Proper CRAC staging based on load requirements
- Energy efficient operation with minimal short-cycling
"""

from __future__ import annotations
import time
from typing import List

from sim.environment import Room, RoomConfig
from sim.crac import CRACUnit, CRACConfig
from control.pid import PIDController, PIDConfig
from control.sequences import CRACSequencer, StagingConfig


def create_test_system() -> tuple[Room, PIDController, CRACSequencer]:
    """
    Create a realistic 3-CRAC data center cooling system.

    System specifications:
    - 40kW IT load room with 2500 kJ/°C thermal mass
    - 3x 50kW CRAC units (150kW total capacity)
    - PID controller tuned for data center response
    - Lead/Lag/Standby staging strategy

    Returns:
        Tuple of (room, pid_controller, crac_sequencer)
    """

    # Room configuration - typical data center zone
    room_cfg = RoomConfig(
        initial_temp_c=22.0,        # Start at setpoint
        ambient_temp_c=22.0,        # Stable ambient
        thermal_mass_kj_per_c=2500.0,  # Medium thermal mass
        ua_kw_per_c=0.25,           # Good envelope
        it_load_kw=40.0,            # 40kW server load
        infil_ua_kw_per_c=0.0,      # No infiltration initially
        n_virtual_sensors=3
    )
    room = Room(room_cfg)

    # PID controller - tuned for data center stability
    pid_cfg = PIDConfig(
        kp=3.0,                     # Aggressive proportional
        ki=0.15,                    # Moderate integral
        kd=0.08,                    # Light derivative
        output_min=0.0,
        output_max=100.0,
        rate_limit=15.0,            # 15%/second max change
        integral_windup_limit=40.0
    )
    pid = PIDController(pid_cfg)

    # CRAC units - 3 identical 50kW units
    cracs: List[CRACUnit] = []
    for i in range(3):
        crac_cfg = CRACConfig(
            unit_id=f"CRAC-{i+1:02d}",
            q_rated_kw=50.0,            # 50kW capacity each
            efficiency_cop=3.5,         # Typical chiller COP
            min_capacity_pct=20.0,      # 20% minimum load
            max_capacity_pct=100.0,
            startup_time_s=180.0,       # 3 minutes startup
            shutdown_time_s=60.0,       # 1 minute shutdown
            mtbf_hours=8760.0,          # 1 year MTBF
            mttr_hours=4.0              # 4 hour repair time
        )
        cracs.append(CRACUnit(crac_cfg, seed=42 + i))

    # CRAC sequencer - professional staging strategy
    staging_cfg = StagingConfig(
        temp_error_threshold=0.8,   # Stage LAG at 0.8°C error
        staging_delay_s=180.0,      # 3 minute staging delay
        destaging_delay_s=300.0,    # 5 minute destaging delay
        rotation_runtime_hours=24.0,  # Daily rotation for testing
        enable_rotation=True,
        staging_hysteresis=0.2,     # Anti-chatter
        destaging_hysteresis=0.3
    )
    sequencer = CRACSequencer(cracs, staging_cfg)

    return room, pid, sequencer


def run_steady_state_test(duration_minutes: float = 60.0,
                          setpoint_c: float = 22.0) -> dict:
    """
    Run steady-state validation test.

    Test criteria:
    - Average temperature within ±0.5°C of setpoint
    - Temperature stability (std dev < 0.3°C)
    - Proper CRAC staging behavior
    - Energy efficiency metrics

    Args:
        duration_minutes: Test duration in minutes
        setpoint_c: Temperature setpoint in °C

    Returns:
        Test results dictionary with performance metrics
    """
    print("🏗️  Creating test system...")
    room, pid, sequencer = create_test_system()

    # Simulation parameters
    dt = 1.0  # 1 second timestep
    total_steps = int(duration_minutes * 60 / dt)

    # Data collection
    temperatures: List[float] = []
    cooling_outputs: List[float] = []
    crac_states: List[dict] = []

    print(f"🚀 Starting {duration_minutes:.1f} minute steady-state test")
    print(f"📊 Setpoint: {setpoint_c:.1f}°C, Timestep: {dt:.1f}s")
    print("=" * 60)

    start_time = time.time()

    for step in range(total_steps):
        sim_time = step * dt

        # PID control calculation
        pid_output = pid.update(setpoint_c, room.temp_c, dt)

        # CRAC sequencer update
        sequencer.update(dt, setpoint_c, room.temp_c, pid_output)

        # Get total cooling from all CRACs
        total_cooling_kw = sequencer.get_total_cooling_kw()

        # Room thermal dynamics
        room.step(dt, total_cooling_kw)

        # Data collection
        temperatures.append(room.temp_c)
        cooling_outputs.append(total_cooling_kw)

        # Periodic status updates
        if step % 300 == 0:  # Every 5 minutes
            elapsed_min = sim_time / 60.0
            temp_error = abs(room.temp_c - setpoint_c)
            total_power = sequencer.get_total_power_kw()

            print(f"⏱️  {elapsed_min:5.1f}m | "
                  f"🌡️  {room.temp_c:5.2f}°C | "
                  f"❄️  {total_cooling_kw:5.1f}kW | "
                  f"⚡ {total_power:5.1f}kW | "
                  f"📊 {pid_output:5.1f}% | "
                  f"🎯 ±{temp_error:.2f}°C")

        # Collect detailed data every minute
        if step % 60 == 0:
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
    import statistics

    # Temperature performance
    avg_temp = statistics.mean(temperatures)
    temp_std = statistics.stdev(temperatures) if len(temperatures) > 1 else 0
    max_error = max(abs(t - setpoint_c) for t in temperatures)
    avg_error = statistics.mean([abs(t - setpoint_c) for t in temperatures])

    # Energy performance
    avg_cooling = statistics.mean(cooling_outputs)
    total_energy_kwh = sum(cooling_outputs) * dt / 3600.0

    # Control performance
    temp_in_range = sum(1 for t in temperatures if abs(t - setpoint_c) <= 0.5)
    control_accuracy = temp_in_range / len(temperatures) * 100

    print("=" * 60)
    print(f"✅ Test Complete - Simulation time: {elapsed_time:.2f}s")
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

    # Test pass/fail criteria
    print()
    print("📋 TEST CRITERIA:")
    temp_pass = avg_error <= 0.5 and temp_std <= 0.3
    control_pass = control_accuracy >= 90.0
    # Should not exceed 80kW
    efficiency_pass = avg_cooling > 0 and avg_cooling <= 80.0

    print(f"   Temperature Control: {'✅ PASS' if temp_pass else '❌ FAIL'} "
          f"(avg error ≤ 0.5°C, std dev ≤ 0.3°C)")
    print(f"   Control Accuracy: {'✅ PASS' if control_pass else '❌ FAIL'} "
          f"({control_accuracy:.1f}% ≥ 90%)")
    print(f"   Efficiency: {'✅ PASS' if efficiency_pass else '❌ FAIL'} "
          f"(cooling = {avg_cooling:.1f}kW ≤ 80kW)")

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


if __name__ == "__main__":
    print("🏭 Data Center BAS Simulation - Phase 2F Integration Test")
    print("=" * 60)

    # Run comprehensive validation test
    results = run_steady_state_test(duration_minutes=30.0, setpoint_c=22.0)

    if results['test_passed']:
        print("\n🎉 System validation successful!")
        print("   Ready for production deployment.")
    else:
        print("\n⚠️  System requires tuning before deployment.")
        print("   Review control parameters and thresholds.")
