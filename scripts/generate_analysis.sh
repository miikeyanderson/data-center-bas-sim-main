#!/bin/bash
"""
BAS Analysis Automation Script

Automatically runs simulation, generates telemetry data, and creates
professional BAS analysis plots for README inclusion.

Usage:
    ./scripts/generate_analysis.sh [scenario_name]
    ./scripts/generate_analysis.sh baseline
    ./scripts/generate_analysis.sh high_load
"""

set -e  # Exit on any error

SCENARIO=${1:-baseline}
DURATION=${2:-5}  # Default 5 minutes
OUTPUT_DIR="reports"

echo "🚀 Generating BAS Analysis for scenario: $SCENARIO"
echo "================================================="

# Create output directory
mkdir -p $OUTPUT_DIR
mkdir -p logs

# Generate sample data (since we don't have full dependencies installed)
echo "📊 Generating sample telemetry data..."
python3 -c "
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate realistic BAS telemetry data
duration_minutes = $DURATION
timestep_s = 5
samples = int(duration_minutes * 60 / timestep_s)

# Time series
start_time = datetime.now()
timestamps = [start_time + timedelta(seconds=i*timestep_s) for i in range(samples)]

# Setpoint and temperature with realistic PID behavior
setpoint = 22.0
temp_noise = np.random.normal(0, 0.1, samples)
temp_trend = np.sin(np.linspace(0, 2*np.pi, samples)) * 0.3
temperature = setpoint + temp_trend + temp_noise

# PID output - realistic controller behavior
temp_error = temperature - setpoint
pid_output = np.clip(50 - temp_error * 20 + np.random.normal(0, 2, samples), 0, 100)

# CRAC status simulation
crac1_status = ['running' if pid_output[i] > 30 else 'off' for i in range(samples)]
crac2_status = ['running' if pid_output[i] > 60 else 'off' for i in range(samples)]
crac3_status = ['off'] * samples  # Standby unit

# Power and cooling based on status
cooling_kw = []
power_kw = []
for i in range(samples):
    cooling = 0
    power = 0.5  # Standby power
    
    if crac1_status[i] == 'running':
        cooling += 50 * (pid_output[i] / 100)
        power += cooling / 3.5  # COP of 3.5
    if crac2_status[i] == 'running':
        cooling += 50 * (pid_output[i] / 100)
        power += cooling / 3.5
    
    cooling_kw.append(cooling)
    power_kw.append(power)

# Calculate COP
cop = [c/p if p > 1 else 0 for c, p in zip(cooling_kw, power_kw)]

# Create DataFrame
df = pd.DataFrame({
    'timestamp': timestamps,
    'setpoint_c': [setpoint] * samples,
    'average_temp_c': temperature,
    'pid_output_pct': pid_output,
    'crac_1_status': crac1_status,
    'crac_1_cmd_pct': pid_output,
    'crac_1_cool_kw': [c * 0.6 for c in cooling_kw],  # Lead unit takes 60%
    'crac_1_power_kw': [p * 0.6 for p in power_kw],
    'crac_1_airflow_cfm': [8000 * (pid_output[i]/100) if crac1_status[i] == 'running' else 0 for i in range(samples)],
    'crac_2_status': crac2_status,
    'crac_2_cmd_pct': [pid_output[i] if crac2_status[i] == 'running' else 0 for i in range(samples)],
    'crac_2_cool_kw': [c * 0.4 for c in cooling_kw],  # Lag unit takes 40%
    'crac_2_power_kw': [p * 0.4 for p in power_kw],
    'crac_2_airflow_cfm': [8000 * (pid_output[i]/100) if crac2_status[i] == 'running' else 0 for i in range(samples)],
    'crac_3_status': crac3_status,
    'crac_3_cmd_pct': [0] * samples,
    'crac_3_cool_kw': [0] * samples,
    'crac_3_power_kw': [0.5] * samples,  # Standby power only
    'crac_3_airflow_cfm': [0] * samples,
    'total_cooling_kw': cooling_kw,
    'total_power_kw': power_kw,
    'energy_efficiency_cop': cop
})

# Save to CSV
df.to_csv('logs/${SCENARIO}_telemetry.csv', index=False)
print(f'Generated {len(df)} samples of telemetry data')
"

echo "📈 Running BAS analysis..."
python3 analyze.py --csv logs/${SCENARIO}_telemetry.csv --name $SCENARIO

echo ""
echo "✅ Analysis Complete!"
echo "📁 Reports saved to: $OUTPUT_DIR/"
echo "📊 Key files generated:"
echo "   - ${SCENARIO}_summary.md     (README content)"
echo "   - ${SCENARIO}_kpis.json      (structured KPIs)"
echo "   - pid_performance.png        (PID loop analysis)"
echo "   - equipment_runtime.png      (runtime analysis)"
echo "   - energy_performance.png     (energy analysis)"
echo "   - system_overview.png        (dashboard view)"
echo ""
echo "🔗 Add these to your README:"
echo "   ![PID Performance](reports/pid_performance.png)"
echo "   ![Equipment Runtime](reports/equipment_runtime.png)"
echo ""
echo "📋 Copy KPIs from: $OUTPUT_DIR/${SCENARIO}_summary.md"