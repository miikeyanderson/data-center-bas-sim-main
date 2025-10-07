#!/usr/bin/env python3
"""
Professional BAS Analysis & Visualization Tool

Generates control performance plots and KPIs that demonstrate real
Building Automation System engineering expertise.

Usage:
    python analyze.py --csv logs/datacenter_telemetry_*.csv
    python analyze.py --csv logs/latest.csv --output reports/
    python analyze.py --compare before.csv after.csv
"""

import argparse
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings

# Import professional formatting utilities
from utils.formatting import format_temperature_dual, format_power, format_time_hms

# Suppress pandas warnings for cleaner output
warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)

# Professional BAS color scheme
BAS_COLORS = {
    'setpoint': '#2E86AB',       # Blue - setpoint/target
    'measurement': '#A23B72',    # Purple - actual measurement  
    'error': '#F18F01',          # Orange - error/deviation
    'output': '#C73E1D',         # Red - controller output
    'lead': '#2F9B69',           # Green - lead equipment
    'lag': '#F4A261',            # Amber - lag equipment
    'standby': '#6C757D',        # Gray - standby equipment
    'alarm': '#DC3545',          # Alert red - alarms
    'normal': '#28A745'          # Success green - normal operation
}

class BASAnalyzer:
    """Professional BAS data analysis and visualization."""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Configure matplotlib for professional plots
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams.update({
            'figure.figsize': (12, 6),
            'font.size': 10,
            'axes.titlesize': 12,
            'axes.labelsize': 11,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'legend.fontsize': 9,
            'figure.dpi': 150,
            'savefig.dpi': 150,
            'savefig.bbox': 'tight'
        })
    
    def load_data(self, csv_path: str) -> pd.DataFrame:
        """Load and prepare telemetry data for analysis."""
        df = pd.read_csv(csv_path)
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['elapsed_seconds'] = (df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds()
        df['elapsed_minutes'] = df['elapsed_seconds'] / 60.0
        
        return df
    
    def calculate_kpis(self, df: pd.DataFrame) -> Dict:
        """Calculate professional BAS KPIs."""
        timestep_s = df['elapsed_seconds'].diff().median()
        duration_hours = df['elapsed_seconds'].iloc[-1] / 3600.0
        
        # Temperature performance
        temp_error = df['average_temp_c'] - df['setpoint_c']
        temp_std = df['average_temp_c'].std()
        max_error = abs(temp_error).max()
        avg_error = abs(temp_error).mean()
        
        # Control accuracy (±0.5°C band)
        in_range = (abs(temp_error) <= 0.5).sum() / len(df) * 100
        
        # Equipment runtime analysis
        runtime_kpis = {}
        switching_kpis = {}
        
        for i in range(1, 4):  # CRAC 1-3
            status_col = f'crac_{i}_status'
            if status_col in df.columns:
                # Runtime calculation
                running_mask = df[status_col] == 'running'
                runtime_hours = running_mask.sum() * timestep_s / 3600.0
                runtime_pct = runtime_hours / duration_hours * 100
                
                # Switching count (status changes)
                status_changes = (df[status_col] != df[status_col].shift()).sum() - 1
                switches = status_changes // 2  # Each on/off cycle = 2 changes
                
                runtime_kpis[f'crac_{i}'] = {
                    'hours': runtime_hours,
                    'percentage': runtime_pct
                }
                switching_kpis[f'crac_{i}'] = switches
        
        # Energy performance
        total_energy = df['total_cooling_kw'].sum() * timestep_s / 3600.0  # kWh
        avg_power = df['total_power_kw'].mean()
        avg_cooling = df['total_cooling_kw'].mean()
        avg_cop = df['energy_efficiency_cop'].mean()
        
        # Controller performance
        pid_output_sat = ((df['pid_output_pct'] >= 99.0) | 
                         (df['pid_output_pct'] <= 1.0)).sum() / len(df) * 100
        
        return {
            'simulation': {
                'duration_hours': duration_hours,
                'timestep_seconds': timestep_s,
                'samples': len(df)
            },
            'temperature': {
                'setpoint_c': df['setpoint_c'].iloc[0],
                'avg_temp_c': df['average_temp_c'].mean(),
                'std_dev_c': temp_std,
                'max_error_c': max_error,
                'avg_error_c': avg_error,
                'control_accuracy_pct': in_range
            },
            'equipment': {
                'runtime': runtime_kpis,
                'switching': switching_kpis
            },
            'energy': {
                'total_cooling_kwh': total_energy,
                'avg_power_kw': avg_power,
                'avg_cooling_kw': avg_cooling,
                'avg_cop': avg_cop
            },
            'control': {
                'saturation_pct': pid_output_sat
            }
        }
    
    def plot_pid_performance(self, df: pd.DataFrame, title: str = "PID Loop Performance") -> str:
        """Generate PID terms and controller output visualization."""
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
        time_minutes = df['elapsed_minutes']
        
        # Temperature tracking
        ax1.plot(time_minutes, df['average_temp_c'], 
                label='Zone Temperature', color=BAS_COLORS['measurement'], linewidth=2)
        ax1.axhline(df['setpoint_c'].iloc[0], color=BAS_COLORS['setpoint'], 
                   linestyle='--', linewidth=2, label='Setpoint')
        
        # Add ±0.5°C control band
        setpoint = df['setpoint_c'].iloc[0]
        ax1.fill_between(time_minutes, setpoint-0.5, setpoint+0.5, 
                        alpha=0.2, color=BAS_COLORS['setpoint'], label='±0.5°C Band')
        
        ax1.set_ylabel('Temperature (°C)')
        ax1.set_title(f'{title} - Temperature Control')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # PID terms (if available)
        if 'pid_p_term' in df.columns:
            ax2.plot(time_minutes, df['pid_p_term'], label='P Term', color='#1f77b4')
            ax2.plot(time_minutes, df['pid_i_term'], label='I Term', color='#ff7f0e')
            ax2.plot(time_minutes, df['pid_d_term'], label='D Term', color='#2ca02c')
            ax2.set_ylabel('PID Terms (%)')
            ax2.set_title('PID Controller Terms')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        else:
            # Show temperature error instead
            temp_error = df['average_temp_c'] - df['setpoint_c']
            ax2.plot(time_minutes, temp_error, color=BAS_COLORS['error'], linewidth=2)
            ax2.axhline(0, color='black', linestyle='-', alpha=0.5)
            ax2.fill_between(time_minutes, -0.5, 0.5, alpha=0.2, color=BAS_COLORS['setpoint'])
            ax2.set_ylabel('Temperature Error (°C)')
            ax2.set_title('Temperature Error from Setpoint')
            ax2.grid(True, alpha=0.3)
        
        # Controller output
        ax3.plot(time_minutes, df['pid_output_pct'], 
                color=BAS_COLORS['output'], linewidth=2, label='Controller Output')
        ax3.axhline(100, color='red', linestyle='--', alpha=0.7, label='Saturation Limits')
        ax3.axhline(0, color='red', linestyle='--', alpha=0.7)
        ax3.set_ylabel('Output (%)')
        ax3.set_xlabel('Time (minutes)')
        ax3.set_title('Controller Output')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        filename = self.output_dir / "pid_performance.png"
        plt.savefig(filename)
        plt.close()
        
        return str(filename)
    
    def plot_equipment_runtime(self, df: pd.DataFrame) -> str:
        """Generate equipment runtime and switching analysis."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Runtime bar chart
        runtime_data = {}
        switching_data = {}
        timestep_s = df['elapsed_seconds'].diff().median()
        duration_hours = df['elapsed_seconds'].iloc[-1] / 3600.0
        
        for i in range(1, 4):
            status_col = f'crac_{i}_status'
            if status_col in df.columns:
                running_mask = df[status_col] == 'running'
                runtime_hours = running_mask.sum() * timestep_s / 3600.0
                runtime_data[f'CRAC-{i:02d}'] = runtime_hours
                
                # Count switches
                status_changes = (df[status_col] != df[status_col].shift()).sum() - 1
                switching_data[f'CRAC-{i:02d}'] = status_changes // 2
        
        # Runtime chart
        bars1 = ax1.bar(runtime_data.keys(), runtime_data.values(), 
                       color=[BAS_COLORS['lead'], BAS_COLORS['lag'], BAS_COLORS['standby']])
        ax1.set_ylabel('Runtime (hours)')
        ax1.set_title('Equipment Runtime')
        ax1.grid(True, alpha=0.3)
        
        # Add runtime percentages on bars
        for bar, hours in zip(bars1, runtime_data.values()):
            pct = hours / duration_hours * 100
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{pct:.1f}%', ha='center', va='bottom')
        
        # Switching chart
        bars2 = ax2.bar(switching_data.keys(), switching_data.values(),
                       color=[BAS_COLORS['lead'], BAS_COLORS['lag'], BAS_COLORS['standby']])
        ax2.set_ylabel('Switch Count')
        ax2.set_title('Equipment Switching Events')
        ax2.grid(True, alpha=0.3)
        
        # Add switch counts on bars
        for bar, switches in zip(bars2, switching_data.values()):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{switches}', ha='center', va='bottom')
        
        plt.tight_layout()
        filename = self.output_dir / "equipment_runtime.png"
        plt.savefig(filename)
        plt.close()
        
        return str(filename)
    
    def plot_energy_performance(self, df: pd.DataFrame) -> str:
        """Generate energy consumption and efficiency analysis."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        time_minutes = df['elapsed_minutes']
        
        # Power consumption over time
        ax1.plot(time_minutes, df['total_cooling_kw'], 
                label='Cooling Output', color=BAS_COLORS['measurement'], linewidth=2)
        ax1.plot(time_minutes, df['total_power_kw'], 
                label='Power Consumption', color=BAS_COLORS['output'], linewidth=2)
        ax1.set_ylabel('Power (kW)')
        ax1.set_title('Energy Performance Over Time')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # System efficiency (COP)
        ax2.plot(time_minutes, df['energy_efficiency_cop'], 
                color=BAS_COLORS['normal'], linewidth=2, label='System COP')
        avg_cop = df['energy_efficiency_cop'].mean()
        ax2.axhline(avg_cop, color=BAS_COLORS['setpoint'], 
                   linestyle='--', label=f'Average COP: {avg_cop:.2f}')
        ax2.set_ylabel('COP (Coefficient of Performance)')
        ax2.set_xlabel('Time (minutes)')
        ax2.set_title('System Efficiency')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        filename = self.output_dir / "energy_performance.png"
        plt.savefig(filename)
        plt.close()
        
        return str(filename)
    
    def plot_system_overview(self, df: pd.DataFrame) -> str:
        """Generate comprehensive system overview dashboard."""
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        time_minutes = df['elapsed_minutes']
        
        # Temperature control (top row, spans 2 columns)
        ax1 = fig.add_subplot(gs[0, :2])
        ax1.plot(time_minutes, df['average_temp_c'], 
                label='Zone Temp', color=BAS_COLORS['measurement'], linewidth=2)
        setpoint = df['setpoint_c'].iloc[0]
        ax1.axhline(setpoint, color=BAS_COLORS['setpoint'], 
                   linestyle='--', linewidth=2, label=f'Setpoint: {setpoint:.1f}°C')
        ax1.fill_between(time_minutes, setpoint-0.5, setpoint+0.5, 
                        alpha=0.2, color=BAS_COLORS['setpoint'])
        ax1.set_ylabel('Temperature (°C)')
        ax1.set_title('Zone Temperature Control')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Equipment status (top right)
        ax2 = fig.add_subplot(gs[0, 2])
        runtime_data = {}
        for i in range(1, 4):
            status_col = f'crac_{i}_status'
            if status_col in df.columns:
                running_mask = df[status_col] == 'running'
                runtime_pct = running_mask.sum() / len(df) * 100
                runtime_data[f'C{i}'] = runtime_pct
        
        bars = ax2.bar(runtime_data.keys(), runtime_data.values(),
                      color=[BAS_COLORS['lead'], BAS_COLORS['lag'], BAS_COLORS['standby']])
        ax2.set_ylabel('Runtime %')
        ax2.set_title('Equipment Utilization')
        for bar, pct in zip(bars, runtime_data.values()):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{pct:.0f}%', ha='center', va='bottom', fontsize=8)
        
        # Controller output (middle left)
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.plot(time_minutes, df['pid_output_pct'], 
                color=BAS_COLORS['output'], linewidth=1.5)
        ax3.axhline(100, color='red', linestyle='--', alpha=0.7)
        ax3.set_ylabel('Output %')
        ax3.set_title('Controller Output')
        ax3.grid(True, alpha=0.3)
        
        # Power consumption (middle center)
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.plot(time_minutes, df['total_power_kw'], 
                color=BAS_COLORS['output'], linewidth=1.5)
        ax4.set_ylabel('Power (kW)')
        ax4.set_title('Power Consumption')
        ax4.grid(True, alpha=0.3)
        
        # System COP (middle right)
        ax5 = fig.add_subplot(gs[1, 2])
        ax5.plot(time_minutes, df['energy_efficiency_cop'], 
                color=BAS_COLORS['normal'], linewidth=1.5)
        avg_cop = df['energy_efficiency_cop'].mean()
        ax5.axhline(avg_cop, color=BAS_COLORS['setpoint'], linestyle='--')
        ax5.set_ylabel('COP')
        ax5.set_title(f'Efficiency (Avg: {avg_cop:.2f})')
        ax5.grid(True, alpha=0.3)
        
        # Equipment timeline (bottom row, spans all columns)
        ax6 = fig.add_subplot(gs[2, :])
        y_pos = 0
        colors = [BAS_COLORS['lead'], BAS_COLORS['lag'], BAS_COLORS['standby']]
        
        for i, color in enumerate(colors, 1):
            status_col = f'crac_{i}_status'
            if status_col in df.columns:
                running_mask = df[status_col] == 'running'
                # Create step plot for on/off status
                ax6.fill_between(time_minutes, y_pos, y_pos + 0.8, 
                               where=running_mask, color=color, alpha=0.7,
                               label=f'CRAC-{i:02d}', step='pre')
                y_pos += 1
        
        ax6.set_xlabel('Time (minutes)')
        ax6.set_ylabel('Equipment')
        ax6.set_title('Equipment Operation Timeline')
        ax6.set_yticks(range(len(colors)))
        ax6.set_yticklabels([f'CRAC-{i:02d}' for i in range(1, len(colors)+1)])
        ax6.grid(True, alpha=0.3)
        
        plt.suptitle('BAS System Performance Dashboard', fontsize=14, y=0.98)
        filename = self.output_dir / "system_overview.png"
        plt.savefig(filename, bbox_inches='tight')
        plt.close()
        
        return str(filename)
    
    def compare_scenarios(self, before_csv: str, after_csv: str, 
                         before_label: str = "Before", after_label: str = "After") -> str:
        """Generate before/after comparison plots."""
        df_before = self.load_data(before_csv)
        df_after = self.load_data(after_csv)
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # Temperature comparison
        ax1.plot(df_before['elapsed_minutes'], df_before['average_temp_c'], 
                label=before_label, color=BAS_COLORS['error'], linewidth=2)
        ax1.plot(df_after['elapsed_minutes'], df_after['average_temp_c'], 
                label=after_label, color=BAS_COLORS['measurement'], linewidth=2)
        setpoint = df_after['setpoint_c'].iloc[0]
        ax1.axhline(setpoint, color=BAS_COLORS['setpoint'], 
                   linestyle='--', label=f'Setpoint: {setpoint:.1f}°C')
        ax1.set_ylabel('Temperature (°C)')
        ax1.set_title('Temperature Control Comparison')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Controller output comparison
        ax2.plot(df_before['elapsed_minutes'], df_before['pid_output_pct'], 
                label=before_label, color=BAS_COLORS['error'], linewidth=2)
        ax2.plot(df_after['elapsed_minutes'], df_after['pid_output_pct'], 
                label=after_label, color=BAS_COLORS['output'], linewidth=2)
        ax2.set_ylabel('Controller Output (%)')
        ax2.set_title('Controller Output Comparison')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Energy comparison
        ax3.plot(df_before['elapsed_minutes'], df_before['total_power_kw'], 
                label=before_label, color=BAS_COLORS['error'], linewidth=2)
        ax3.plot(df_after['elapsed_minutes'], df_after['total_power_kw'], 
                label=after_label, color=BAS_COLORS['output'], linewidth=2)
        ax3.set_ylabel('Power (kW)')
        ax3.set_xlabel('Time (minutes)')
        ax3.set_title('Power Consumption Comparison')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Efficiency comparison
        ax4.plot(df_before['elapsed_minutes'], df_before['energy_efficiency_cop'], 
                label=before_label, color=BAS_COLORS['error'], linewidth=2)
        ax4.plot(df_after['elapsed_minutes'], df_after['energy_efficiency_cop'], 
                label=after_label, color=BAS_COLORS['normal'], linewidth=2)
        ax4.set_ylabel('System COP')
        ax4.set_xlabel('Time (minutes)')
        ax4.set_title('Efficiency Comparison')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.suptitle(f'{before_label} vs {after_label} Performance Analysis', fontsize=14)
        plt.tight_layout()
        filename = self.output_dir / "scenario_comparison.png"
        plt.savefig(filename)
        plt.close()
        
        return str(filename)
    
    def generate_report(self, csv_path: str, report_name: str = "baseline") -> Dict:
        """Generate complete analysis report with all plots and KPIs."""
        print(f"🔍 Analyzing BAS performance data: {csv_path}")
        
        df = self.load_data(csv_path)
        kpis = self.calculate_kpis(df)
        
        print(f"📊 Generating plots...")
        
        # Generate all plots
        plots = {
            'pid_performance': self.plot_pid_performance(df, f"{report_name.title()} PID Performance"),
            'equipment_runtime': self.plot_equipment_runtime(df),
            'energy_performance': self.plot_energy_performance(df),
            'system_overview': self.plot_system_overview(df)
        }
        
        # Save KPIs to JSON (convert numpy types to native Python types)
        kpi_file = self.output_dir / f"{report_name}_kpis.json"
        def convert_numpy(obj):
            if hasattr(obj, 'item'):
                return obj.item()
            elif isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(v) for v in obj]
            return obj
        
        with open(kpi_file, 'w') as f:
            json.dump(convert_numpy(kpis), f, indent=2)
        
        # Generate summary report
        self.generate_markdown_summary(kpis, plots, report_name)
        
        print(f"✅ Analysis complete! Reports saved to: {self.output_dir}")
        print(f"📈 Key KPI: {kpis['temperature']['control_accuracy_pct']:.1f}% time in ±0.5°C band")
        print(f"⚡ Energy: {kpis['energy']['avg_power_kw']:.1f} kW avg power, {kpis['energy']['avg_cop']:.2f} COP")
        
        return {
            'kpis': kpis,
            'plots': plots,
            'report_file': str(kpi_file)
        }
    
    def generate_markdown_summary(self, kpis: Dict, plots: Dict, report_name: str):
        """Generate markdown summary for README inclusion."""
        md_content = f"""# {report_name.title()} Performance Analysis

## 📈 System Performance Dashboard

| Temperature Control | Equipment Runtime | Energy Performance | System Overview |
|-------|-------|-------|-------|
| ![PID](reports/{Path(plots['pid_performance']).name}) | ![Runtime](reports/{Path(plots['equipment_runtime']).name}) | ![Energy](reports/{Path(plots['energy_performance']).name}) | ![Overview](reports/{Path(plots['system_overview']).name}) |

## 🎯 Key Performance Indicators

### Temperature Control
- **Setpoint**: {format_temperature_dual(kpis['temperature']['setpoint_c'])}
- **Average Temperature**: {format_temperature_dual(kpis['temperature']['avg_temp_c'])}
- **Control Accuracy**: {kpis['temperature']['control_accuracy_pct']:.1f}% within ±0.5°C
- **Standard Deviation**: {kpis['temperature']['std_dev_c']:.3f}°C
- **Maximum Error**: {kpis['temperature']['max_error_c']:.3f}°C

### Equipment Performance
"""
        
        # Add equipment runtime details
        for crac_id, runtime in kpis['equipment']['runtime'].items():
            unit_name = crac_id.replace('_', '-').upper()
            switches = kpis['equipment']['switching'].get(crac_id, 0)
            md_content += f"- **{unit_name}**: {runtime['hours']:.2f} hrs ({runtime['percentage']:.1f}%) — {switches} switches\n"
        
        md_content += f"""
### Energy Efficiency
- **Average Power**: {format_power(kpis['energy']['avg_power_kw'])}
- **Average Cooling**: {format_power(kpis['energy']['avg_cooling_kw'])}
- **System COP**: {kpis['energy']['avg_cop']:.2f}
- **Total Energy**: {kpis['energy']['total_cooling_kwh']:.2f} kWh

### Control System
- **Simulation Duration**: {format_time_hms(kpis['simulation']['duration_hours'] * 3600)}
- **Controller Saturation**: {kpis['control']['saturation_pct']:.1f}% of time
- **Data Points**: {kpis['simulation']['samples']:,} samples

---
*Analysis generated by BAS Professional Analysis Tool*
"""
        
        md_file = self.output_dir / f"{report_name}_summary.md"
        with open(md_file, 'w') as f:
            f.write(md_content)


def main():
    parser = argparse.ArgumentParser(description="Professional BAS Analysis Tool")
    parser.add_argument('--csv', required=True, help='CSV telemetry file to analyze')
    parser.add_argument('--output', default='reports', help='Output directory for plots')
    parser.add_argument('--compare', nargs=2, metavar=('BEFORE', 'AFTER'), 
                       help='Compare two CSV files (before vs after)')
    parser.add_argument('--name', default='baseline', help='Report name prefix')
    
    args = parser.parse_args()
    
    analyzer = BASAnalyzer(args.output)
    
    if args.compare:
        print(f"🔍 Comparing scenarios: {args.compare[0]} vs {args.compare[1]}")
        analyzer.compare_scenarios(args.compare[0], args.compare[1])
        print("✅ Comparison complete!")
    else:
        analyzer.generate_report(args.csv, args.name)


if __name__ == "__main__":
    main()