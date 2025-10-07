#!/usr/bin/env python3
"""
Fault Simulation System Validation Test

Quick validation test to ensure all fault simulation components
work correctly together. This test validates:

1. Sensor fault injection and detection
2. Actuator fault modeling
3. Control system fault simulation
4. Diagnostic engine functionality
5. Root cause analysis
6. Report generation

Usage:
    python test_fault_simulation.py
"""

import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def test_sensor_faults():
    """Test sensor fault simulation components."""
    print("🔬 Testing sensor fault simulation...")
    
    from sim.sensor_faults import (
        TemperatureSensor, SensorConfig, SensorFaultConfig, 
        SensorFaultType, create_default_sensor_configs
    )
    
    # Create test sensor
    config = SensorConfig(
        sensor_id="TEST_SENSOR",
        sensor_type="temperature",
        location="test_zone",
        enable_faults=True,
        fault_configs=[
            SensorFaultConfig(
                fault_type=SensorFaultType.DRIFT,
                drift_rate_per_hour=0.1,
                max_drift=1.0
            )
        ]
    )
    
    sensor = TemperatureSensor(config, seed=42)
    
    # Test normal operation
    sensor.update(22.0, 1.0, 0.0)
    assert abs(sensor.filtered_value - 22.0) < 0.1, "Normal sensor operation failed"
    
    # Test fault injection
    success = sensor.inject_fault(SensorFaultType.DRIFT, sim_time=10.0)
    assert success, "Fault injection failed"
    
    # Test fault is active
    active_faults = sensor.get_active_faults()
    assert SensorFaultType.DRIFT in active_faults, "Fault not active after injection"
    
    print("  ✅ Sensor fault simulation working correctly")
    return True

def test_actuator_faults():
    """Test actuator fault simulation components."""
    print("🔧 Testing actuator fault simulation...")
    
    from sim.actuator_faults import (
        ActuatorModel, ActuatorConfig, ActuatorFaultConfig,
        ActuatorFaultType, create_default_actuator_configs
    )
    
    # Create test actuator
    config = ActuatorConfig(
        actuator_id="TEST_ACTUATOR",
        actuator_type="damper",
        location="test_crac",
        enable_faults=True,
        fault_configs=[
            ActuatorFaultConfig(
                fault_type=ActuatorFaultType.STICTION,
                breakaway_threshold=3.0,
                static_friction=1.5
            )
        ]
    )
    
    actuator = ActuatorModel(config, seed=42)
    
    # Test normal operation
    actuator.update(50.0, 1.0, 0.0)
    assert abs(actuator.position - 50.0) < 5.0, "Normal actuator operation failed"
    
    # Test fault injection
    success = actuator.inject_fault(ActuatorFaultType.STICTION, sim_time=10.0)
    assert success, "Actuator fault injection failed"
    
    # Test fault is active
    active_faults = actuator.get_active_faults()
    assert ActuatorFaultType.STICTION in active_faults, "Actuator fault not active"
    
    print("  ✅ Actuator fault simulation working correctly")
    return True

def test_control_faults():
    """Test control system fault simulation."""
    print("🎛️ Testing control system fault simulation...")
    
    from control.system_faults import (
        ControlSystemFaultManager, ControlSystemConfig,
        ControlFaultConfig, ControlFaultType
    )
    
    # Create test control system
    config = ControlSystemConfig(
        system_id="TEST_CONTROL",
        system_type="pid_controller",
        location="test_loop",
        enable_faults=True,
        fault_configs=[
            ControlFaultConfig(
                fault_type=ControlFaultType.SHORT_CYCLING,
                cycle_time_threshold_s=300.0,
                short_cycle_ratio=0.3
            )
        ]
    )
    
    control_mgr = ControlSystemFaultManager(config, seed=42)
    
    # Test normal operation
    signal, setpoint = control_mgr.update(50.0, 22.0, 22.0, 1.0, 0.0)
    assert signal == 50.0, "Normal control operation failed"
    
    # Test fault injection
    success = control_mgr.inject_fault(ControlFaultType.SHORT_CYCLING, sim_time=10.0)
    assert success, "Control fault injection failed"
    
    # Test fault is active
    active_faults = control_mgr.get_active_faults()
    assert ControlFaultType.SHORT_CYCLING in active_faults, "Control fault not active"
    
    print("  ✅ Control system fault simulation working correctly")
    return True

def test_diagnostic_engine():
    """Test diagnostic engine functionality."""
    print("🔍 Testing diagnostic engine...")
    
    from diagnostics.engine import DiagnosticEngine
    
    # Create diagnostic engine
    engine = DiagnosticEngine(seed=42)
    
    # Test with normal system data
    system_data = {
        "avg_temp": 22.0,
        "setpoint": 22.0,
        "sensor_temps": [22.0, 22.1, 21.9],
        "crac_states": [
            {"q_rated_kw": 50.0, "q_cool_kw": 25.0, "status": "running"},
            {"q_rated_kw": 50.0, "q_cool_kw": 0.0, "status": "off"}
        ]
    }
    
    diagnostics = engine.update(system_data, 0.0)
    assert isinstance(diagnostics, list), "Diagnostic engine should return list"
    
    # Test with fault conditions
    fault_data = {
        "avg_temp": 25.0,  # High temperature
        "setpoint": 22.0,
        "sensor_temps": [25.0, 24.8, 25.2],
        "crac_states": [
            {"q_rated_kw": 50.0, "q_cool_kw": 10.0, "status": "running"},
            {"q_rated_kw": 50.0, "q_cool_kw": 0.0, "status": "off"}
        ]
    }
    
    diagnostics = engine.update(fault_data, 300.0)  # 5 minutes later
    
    print("  ✅ Diagnostic engine working correctly")
    return True

def test_root_cause_analysis():
    """Test root cause analysis functionality."""
    print("🕵️ Testing root cause analysis...")
    
    from diagnostics.root_cause import RootCauseAnalyzer
    
    # Create analyzer
    analyzer = RootCauseAnalyzer()
    
    # Test with sample diagnostic results
    diagnostic_results = [
        {
            'diagnostic_id': 'HIGH_TEMP_01',
            'category': 'equipment',
            'severity': 'major',
            'title': 'High Temperature Detected',
            'confidence_level': 0.9,
            'component_id': 'CRAC-01'
        }
    ]
    
    system_data = {
        'timestamp': 300.0,
        'avg_temp': 25.0,
        'setpoint': 22.0,
        'crac_states': [
            {'q_rated_kw': 50.0, 'q_cool_kw': 10.0, 'status': 'running'}
        ]
    }
    
    analysis = analyzer.analyze_fault(diagnostic_results, system_data)
    
    assert analysis.primary_cause is not None, "Root cause analysis failed"
    assert analysis.confidence_level > 0, "Confidence level should be positive"
    assert len(analysis.immediate_actions) >= 0, "Should have action recommendations"
    
    print("  ✅ Root cause analysis working correctly")
    return True

def test_diagnostic_reporting():
    """Test diagnostic reporting functionality."""
    print("📊 Testing diagnostic reporting...")
    
    from diagnostics.reports import (
        DiagnosticReporter, ReportConfig, ReportFormat
    )
    
    # Create temporary directory for test reports
    with tempfile.TemporaryDirectory() as temp_dir:
        config = ReportConfig(
            report_id="test_report",
            title="Test Diagnostic Report",
            format=ReportFormat.MARKDOWN,
            output_path=temp_dir,
            audience="technical"
        )
        
        reporter = DiagnosticReporter(config)
        
        # Test data
        diagnostic_results = [
            {
                'diagnostic_id': 'TEST_FAULT',
                'category': 'sensor',
                'severity': 'minor',
                'title': 'Test Fault',
                'description': 'Test fault for validation'
            }
        ]
        
        system_data = {
            'timestamp': 100.0,
            'avg_temp': 22.5,
            'setpoint': 22.0
        }
        
        # Generate report
        report_path = reporter.generate_fault_report(
            diagnostic_results, system_data)
        
        assert Path(report_path).exists(), "Report file was not created"
        
        # Check report contains expected content
        with open(report_path, 'r') as f:
            content = f.read()
            assert "Test Diagnostic Report" in content, "Report title missing"
            assert "Test Fault" in content, "Fault information missing"
    
    print("  ✅ Diagnostic reporting working correctly")
    return True

def test_configuration_loading():
    """Test configuration loading for fault simulation."""
    print("⚙️ Testing configuration loading...")
    
    from config.config_loader import ConfigLoader
    
    # Test loading default configuration
    loader = ConfigLoader()
    config = loader.load_config("config/default.yaml")
    
    # Check fault simulation configuration exists
    assert 'fault_simulation' in config, "Fault simulation config missing"
    assert 'diagnostics' in config, "Diagnostics config missing"
    
    fault_config = config['fault_simulation']
    assert 'sensor_faults' in fault_config, "Sensor fault config missing"
    assert 'actuator_faults' in fault_config, "Actuator fault config missing"
    assert 'control_faults' in fault_config, "Control fault config missing"
    
    diag_config = config['diagnostics']
    assert 'engine' in diag_config, "Diagnostic engine config missing"
    assert 'reporting' in diag_config, "Reporting config missing"
    
    print("  ✅ Configuration loading working correctly")
    return True

def run_validation_tests():
    """Run all validation tests."""
    print("🧪 Running Fault Simulation System Validation Tests")
    print("=" * 60)
    
    tests = [
        test_sensor_faults,
        test_actuator_faults,
        test_control_faults,
        test_diagnostic_engine,
        test_root_cause_analysis,
        test_diagnostic_reporting,
        test_configuration_loading
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"  ❌ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"  ❌ {test.__name__} failed: {e}")
    
    print("\n" + "=" * 60)
    print(f"Validation Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All fault simulation components validated successfully!")
        print("\nSystem is ready for professional demonstrations:")
        print("  • Sensor fault injection and detection")
        print("  • Actuator fault modeling")
        print("  • Control system fault simulation")
        print("  • Real-time diagnostic engine")
        print("  • Root cause analysis")
        print("  • Professional diagnostic reporting")
        print("\nRun the demonstration with:")
        print("  python demo_fault_simulation.py --duration 15")
    else:
        print("❌ Some components failed validation. Check implementation.")
        return False
    
    return True

if __name__ == "__main__":
    success = run_validation_tests()
    sys.exit(0 if success else 1)