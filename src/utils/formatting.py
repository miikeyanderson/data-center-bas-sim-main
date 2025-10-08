# utils/formatting.py
"""
Professional BAS formatting utilities for engineering units and displays.

This module provides standard formatting functions that signal professional
Building Automation System (BAS) engineering knowledge.
"""

from typing import Union


def format_time_hms(seconds: float) -> str:
    """
    Format time duration in professional HH:MM:SS format.
    
    Args:
        seconds: Time duration in seconds
        
    Returns:
        Formatted time string in HH:MM:SS format
        
    Examples:
        >>> format_time_hms(65)
        '00:01:05'
        >>> format_time_hms(3725)
        '01:02:05'
        >>> format_time_hms(45)
        '00:00:45'
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_temperature_dual(temp_c: float, show_fahrenheit: bool = True) -> str:
    """
    Format temperature with dual units (°C and °F) for professional displays.
    
    Args:
        temp_c: Temperature in Celsius
        show_fahrenheit: Whether to include Fahrenheit conversion
        
    Returns:
        Formatted temperature string
        
    Examples:
        >>> format_temperature_dual(22.0)
        '22.0°C (71.6°F)'
        >>> format_temperature_dual(22.0, False)
        '22.0°C'
    """
    if show_fahrenheit:
        temp_f = temp_c * 9/5 + 32
        return f"{temp_c:.1f}°C ({temp_f:.1f}°F)"
    else:
        return f"{temp_c:.1f}°C"


def format_airflow(cfm: float, show_metric: bool = True) -> str:
    """
    Format airflow with dual units (CFM and L/s) for professional displays.
    
    Args:
        cfm: Airflow in cubic feet per minute
        show_metric: Whether to include L/s conversion
        
    Returns:
        Formatted airflow string
        
    Examples:
        >>> format_airflow(8000)
        '8000 CFM (3776 L/s)'
        >>> format_airflow(8000, False)
        '8000 CFM'
    """
    if show_metric:
        # Convert CFM to L/s: 1 CFM = 0.472 L/s
        l_per_s = cfm * 0.472
        return f"{cfm:.0f} CFM ({l_per_s:.0f} L/s)"
    else:
        return f"{cfm:.0f} CFM"


def format_power(kw: float, show_btu: bool = False) -> str:
    """
    Format power with optional BTU/hr conversion for professional displays.
    
    Args:
        kw: Power in kilowatts
        show_btu: Whether to include BTU/hr conversion
        
    Returns:
        Formatted power string
        
    Examples:
        >>> format_power(50.0)
        '50.0 kW'
        >>> format_power(50.0, True)
        '50.0 kW (170,653 BTU/hr)'
    """
    if show_btu:
        # Convert kW to BTU/hr: 1 kW = 3412.14 BTU/hr
        btu_hr = kw * 3412.14
        return f"{kw:.1f} kW ({btu_hr:,.0f} BTU/hr)"
    else:
        return f"{kw:.1f} kW"


def format_runtime_professional(runtime_hours: float) -> str:
    """
    Format runtime in professional format showing both hours and HH:MM:SS.
    
    Args:
        runtime_hours: Runtime in hours
        
    Returns:
        Professional runtime display
        
    Examples:
        >>> format_runtime_professional(1.5)
        '1.5 hrs (01:30:00)'
        >>> format_runtime_professional(25.25)
        '25.3 hrs (25:15:00)'
    """
    total_seconds = runtime_hours * 3600
    time_str = format_time_hms(total_seconds)
    return f"{runtime_hours:.1f} hrs ({time_str})"


def format_alarm_duration(seconds: float) -> str:
    """
    Format alarm duration in professional HH:MM:SS format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Professional alarm duration display
    """
    return format_time_hms(seconds)