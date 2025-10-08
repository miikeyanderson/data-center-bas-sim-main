# io/historian.py
"""
BAS Historian for Data Center Telemetry

Professional data logging system for BAS applications:
- CSV format for easy analysis and trending
- Configurable sampling rates (1-5 second intervals)
- Comprehensive system data capture
- Automatic file rotation and management
- Integration with alarm systems

Data logged:
- Time, setpoint, average temperature, individual sensors
- CRAC command percentages, cooling outputs, power consumption
- Alarm states and priorities
- System performance metrics

File format: ISO timestamp, comma-separated values
"""
from __future__ import annotations
import csv
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


@dataclass
class HistorianConfig:
    """Configuration for historian data logging."""
    base_directory: str = "logs"
    file_prefix: str = "datacenter_telemetry"
    sample_interval_s: float = 5.0          # Log every 5 seconds
    
    # File management
    max_file_size_mb: float = 10.0          # Rotate at 10MB
    max_files: int = 100                    # Keep 100 files max
    auto_rotate: bool = True
    
    # Data options
    include_alarms: bool = True
    include_diagnostics: bool = True
    timestamp_format: str = "%Y-%m-%d %H:%M:%S.%f"


class CSVHistorian:
    """
    Professional BAS historian with CSV output.
    
    Features:
    - Structured data logging with consistent column headers
    - Automatic file rotation based on size/time
    - Configurable sampling intervals
    - Integration with alarm and control systems
    - Performance metrics tracking
    
    Usage:
        historian = CSVHistorian(HistorianConfig())
        historian.log_data(sim_time, room, cracs, alarms, pid_output)
        historian.close()
    """
    
    def __init__(self, cfg: Optional[HistorianConfig] = None):
        self.cfg = cfg or HistorianConfig()
        
        # State tracking
        self.last_log_time: float = 0.0
        self.current_file_path: Optional[str] = None
        self.current_file_handle = None
        self.csv_writer = None
        self.headers_written: bool = False
        
        # Statistics
        self.records_written: int = 0
        self.files_created: int = 0
        self.total_data_mb: float = 0.0
        
        # Ensure log directory exists
        self._ensure_log_directory()
    
    def _ensure_log_directory(self) -> None:
        """Create log directory if it doesn't exist."""
        log_dir = Path(self.cfg.base_directory)
        log_dir.mkdir(parents=True, exist_ok=True)
    
    def _should_log(self, sim_time: float) -> bool:
        """Check if enough time has elapsed for next log entry."""
        return (sim_time - self.last_log_time) >= self.cfg.sample_interval_s
    
    def _get_new_filename(self) -> str:
        """Generate new filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.cfg.file_prefix}_{timestamp}.csv"
        return os.path.join(self.cfg.base_directory, filename)
    
    def _should_rotate_file(self) -> bool:
        """Check if current file should be rotated."""
        if not self.current_file_path or not os.path.exists(self.current_file_path):
            return True
        
        if self.cfg.auto_rotate:
            file_size_mb = os.path.getsize(self.current_file_path) / (1024 * 1024)
            return file_size_mb >= self.cfg.max_file_size_mb
        
        return False
    
    def _rotate_file(self) -> None:
        """Close current file and open new one."""
        if self.current_file_handle:
            self.current_file_handle.close()
        
        self.current_file_path = self._get_new_filename()
        self.current_file_handle = open(self.current_file_path, 'w', newline='')
        self.csv_writer = csv.writer(self.current_file_handle)
        self.headers_written = False
        self.files_created += 1
        
        # Clean up old files if needed
        self._cleanup_old_files()
    
    def _cleanup_old_files(self) -> None:
        """Remove old log files to stay within limits."""
        if not self.cfg.auto_rotate or self.cfg.max_files <= 0:
            return
        
        log_dir = Path(self.cfg.base_directory)
        pattern = f"{self.cfg.file_prefix}_*.csv"
        log_files = sorted(log_dir.glob(pattern))
        
        while len(log_files) > self.cfg.max_files:
            oldest_file = log_files.pop(0)
            try:
                oldest_file.unlink()
            except OSError:
                pass  # File might be in use
    
    def _write_headers(self) -> None:
        """Write CSV column headers."""
        headers = [
            # Time and control
            "timestamp", "sim_time_s", "setpoint_c", "avg_temp_c", "pid_output_pct",
            
            # PID individual terms
            "pid_p_term", "pid_i_term", "pid_d_term",
            
            # Individual sensors (up to 5)
            "sensor_1_c", "sensor_2_c", "sensor_3_c", "sensor_4_c", "sensor_5_c",
            
            # CRAC data (up to 3 units)
            "crac_1_id", "crac_1_status", "crac_1_cmd_pct", "crac_1_cool_kw", "crac_1_power_kw", "crac_1_airflow_cfm",
            "crac_2_id", "crac_2_status", "crac_2_cmd_pct", "crac_2_cool_kw", "crac_2_power_kw", "crac_2_airflow_cfm",
            "crac_3_id", "crac_3_status", "crac_3_cmd_pct", "crac_3_cool_kw", "crac_3_power_kw", "crac_3_airflow_cfm",
            
            # System totals
            "total_cooling_kw", "total_power_kw", "energy_efficiency_cop",
            
            # Staging status
            "lead_unit", "lag_staged", "standby_staged", "active_unit_count",
            
            # Alarms
            "active_alarms", "critical_alarms", "high_alarms", "alarm_list"
        ]
        
        if self.cfg.include_diagnostics:
            headers.extend([
                "room_thermal_mass", "room_ua_coeff", "it_load_kw",
                "pid_integral", "pid_max_error", "system_runtime_hours"
            ])
        
        self.csv_writer.writerow(headers)
        self.headers_written = True
    
    def log_data(self, sim_time: float, room_data: Dict, crac_data: List[Dict],
                 alarm_data: Dict, pid_output: float, **kwargs) -> None:
        """
        Log comprehensive system data to CSV.
        
        Args:
            sim_time: Simulation time in seconds
            room_data: Room temperature and sensor data
            crac_data: List of CRAC unit states
            alarm_data: Alarm manager summary
            pid_output: Current PID controller output
            **kwargs: Additional data to log (including 'pid_terms' dict)
        """
        
        # Check if we should log this timestep
        if not self._should_log(sim_time):
            return
        
        # Rotate file if needed
        if self._should_rotate_file():
            self._rotate_file()
        
        # Write headers if new file
        if not self.headers_written:
            self._write_headers()
        
        # Prepare data row
        timestamp = datetime.now().strftime(self.cfg.timestamp_format)
        
        # Basic control data
        row_data = [
            timestamp,
            f"{sim_time:.1f}",
            f"{room_data.get('setpoint_c', 0.0):.2f}",
            f"{room_data.get('avg_temp_c', 0.0):.2f}",
            f"{pid_output:.1f}"
        ]
        
        # PID individual terms
        pid_terms = kwargs.get('pid_terms', {})
        row_data.extend([
            f"{pid_terms.get('p_term', 0.0):.2f}",
            f"{pid_terms.get('i_term', 0.0):.2f}",
            f"{pid_terms.get('d_term', 0.0):.2f}"
        ])
        
        # Individual sensors (pad to 5)
        sensors = room_data.get('sensor_temps', [])
        for i in range(5):
            if i < len(sensors):
                row_data.append(f"{sensors[i]:.2f}")
            else:
                row_data.append("")
        
        # CRAC data (pad to 3 units)
        for i in range(3):
            if i < len(crac_data):
                crac = crac_data[i]
                row_data.extend([
                    crac.get('unit_id', f'CRAC-{i+1:02d}'),
                    crac.get('status', 'off'),
                    f"{crac.get('cmd_pct', 0.0):.1f}",
                    f"{crac.get('q_cool_kw', 0.0):.1f}",
                    f"{crac.get('power_kw', 0.0):.1f}",
                    f"{crac.get('airflow_cfm', 0.0):.0f}"
                ])
            else:
                row_data.extend(["", "", "0.0", "0.0", "0.0", "0.0"])
        
        # System totals
        total_cooling = sum(c.get('q_cool_kw', 0.0) for c in crac_data)
        total_power = sum(c.get('power_kw', 0.0) for c in crac_data)
        system_cop = total_cooling / total_power if total_power > 0 else 0.0
        
        row_data.extend([
            f"{total_cooling:.1f}",
            f"{total_power:.1f}",
            f"{system_cop:.2f}"
        ])
        
        # Staging status
        staging_data = kwargs.get('staging_data', {})
        active_units = sum(1 for c in crac_data if c.get('status') == 'running')
        
        row_data.extend([
            staging_data.get('lead_unit', ''),
            str(staging_data.get('lag_staged', False)),
            str(staging_data.get('standby_staged', False)),
            str(active_units)
        ])
        
        # Alarm data
        if self.cfg.include_alarms and alarm_data:
            active_alarms = alarm_data.get('active_alarms', 0)
            priority_counts = alarm_data.get('priority_breakdown', {})
            
            # Create alarm list string
            active_alarm_list = kwargs.get('active_alarm_list', [])
            alarm_list_str = ';'.join(active_alarm_list) if active_alarm_list else ""
            
            row_data.extend([
                str(active_alarms),
                str(priority_counts.get('critical', 0)),
                str(priority_counts.get('high', 0)),
                alarm_list_str
            ])
        else:
            row_data.extend(["0", "0", "0", ""])
        
        # Diagnostic data
        if self.cfg.include_diagnostics:
            diag_data = kwargs.get('diagnostics', {})
            row_data.extend([
                f"{diag_data.get('thermal_mass_kj_per_c', 0.0):.0f}",
                f"{diag_data.get('ua_kw_per_c', 0.0):.3f}",
                f"{diag_data.get('it_load_kw', 0.0):.1f}",
                f"{diag_data.get('pid_integral', 0.0):.2f}",
                f"{diag_data.get('pid_max_error', 0.0):.2f}",
                f"{diag_data.get('system_runtime_hours', 0.0):.1f}"
            ])
        
        # Write the row
        self.csv_writer.writerow(row_data)
        self.current_file_handle.flush()  # Ensure data is written
        
        # Update statistics
        self.records_written += 1
        self.last_log_time = sim_time
        
        # Update file size tracking
        if self.current_file_path:
            try:
                file_size_mb = os.path.getsize(self.current_file_path) / (1024 * 1024)
                self.total_data_mb = file_size_mb
            except OSError:
                pass
    
    def get_statistics(self) -> Dict:
        """Get historian performance statistics."""
        return {
            "records_written": self.records_written,
            "files_created": self.files_created,
            "total_data_mb": self.total_data_mb,
            "current_file": self.current_file_path,
            "sample_interval_s": self.cfg.sample_interval_s,
            "last_log_time": self.last_log_time
        }
    
    def close(self) -> None:
        """Close current file and cleanup resources."""
        if self.current_file_handle:
            self.current_file_handle.close()
            self.current_file_handle = None
            self.csv_writer = None


def create_test_historian() -> CSVHistorian:
    """Create historian configured for testing."""
    test_config = HistorianConfig(
        base_directory="test_logs",
        file_prefix="test_datacenter",
        sample_interval_s=1.0,  # 1 second for testing
        max_file_size_mb=1.0,   # Small files for testing
        max_files=5
    )
    return CSVHistorian(test_config)