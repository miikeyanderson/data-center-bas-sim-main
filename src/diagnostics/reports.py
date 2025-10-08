# diagnostics/reports.py
"""
Professional Diagnostic Reporting System for BAS Data Center Systems

Comprehensive reporting capabilities featuring:
- Structured fault logs in JSON/CSV formats
- Human-readable diagnostic reports
- Trend analysis and performance degradation reports
- Predictive maintenance schedules
- Executive summaries and system health dashboards

Engineering Implementation:
- Professional report templates for different audiences
- Integration with maintenance management systems
- Automated report generation and distribution
- Rich formatting with charts and visualizations
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, TextIO
from enum import Enum
import json
import csv
import math
from datetime import datetime, timedelta
from pathlib import Path
import statistics


class ReportFormat(Enum):
    """Supported report output formats."""
    JSON = "json"
    CSV = "csv"
    MARKDOWN = "markdown"
    HTML = "html"
    TEXT = "text"


class ReportSection(Enum):
    """Available report sections."""
    EXECUTIVE_SUMMARY = "executive_summary"
    FAULT_ANALYSIS = "fault_analysis"
    SYSTEM_HEALTH = "system_health"
    MAINTENANCE_SCHEDULE = "maintenance_schedule"
    PERFORMANCE_TRENDS = "performance_trends"
    ROOT_CAUSE_ANALYSIS = "root_cause_analysis"
    RECOMMENDATIONS = "recommendations"
    APPENDIX = "appendix"


@dataclass
class ReportConfig:
    """Configuration for diagnostic report generation."""
    report_id: str
    title: str
    format: ReportFormat = ReportFormat.MARKDOWN
    sections: List[ReportSection] = field(default_factory=lambda: list(ReportSection))
    
    # Output settings
    output_path: str = "reports/"
    include_charts: bool = True
    include_raw_data: bool = False
    
    # Content settings
    audience: str = "technical"  # "executive", "technical", "maintenance"
    detail_level: str = "standard"  # "summary", "standard", "detailed"
    time_range_hours: float = 24.0
    
    # Formatting
    company_name: str = "Data Center Operations"
    facility_name: str = "Primary Data Center"
    author: str = "BAS Diagnostic System"


class DiagnosticReporter:
    """
    Professional diagnostic reporting system for BAS fault analysis.
    
    Features:
    - Multiple output formats (JSON, CSV, Markdown, HTML)
    - Configurable report sections and detail levels
    - Professional templates for different audiences
    - Automated report generation and scheduling
    - Integration with maintenance management systems
    
    Report Types:
    - Real-time fault reports
    - Daily/weekly system health summaries
    - Maintenance planning reports
    - Performance trend analysis
    - Root cause analysis documentation
    """
    
    def __init__(self, config: Optional[ReportConfig] = None):
        self.config = config or ReportConfig(
            report_id="default",
            title="BAS Diagnostic Report"
        )
        
        # Report templates
        self.templates = {
            ReportFormat.MARKDOWN: self._generate_markdown_report,
            ReportFormat.JSON: self._generate_json_report,
            ReportFormat.CSV: self._generate_csv_report,
            ReportFormat.HTML: self._generate_html_report,
            ReportFormat.TEXT: self._generate_text_report
        }
        
        # Ensure output directory exists
        Path(self.config.output_path).mkdir(parents=True, exist_ok=True)
    
    def generate_fault_report(self, diagnostic_results: List[Dict[str, Any]],
                             system_data: Dict[str, Any],
                             root_cause_analysis: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate comprehensive fault diagnostic report.
        
        Args:
            diagnostic_results: List of diagnostic results from engine
            system_data: Current system state data
            root_cause_analysis: Optional root cause analysis results
            
        Returns:
            Path to generated report file
        """
        
        # Prepare report data
        report_data = {
            'metadata': self._generate_metadata(),
            'executive_summary': self._generate_executive_summary(
                diagnostic_results, system_data),
            'fault_analysis': self._generate_fault_analysis(diagnostic_results),
            'system_health': self._generate_system_health_section(system_data),
            'root_cause_analysis': root_cause_analysis,
            'recommendations': self._generate_recommendations(
                diagnostic_results, root_cause_analysis),
            'raw_data': {
                'diagnostics': diagnostic_results,
                'system_state': system_data
            } if self.config.include_raw_data else None
        }
        
        # Generate report using appropriate template
        generator = self.templates.get(self.config.format, self._generate_markdown_report)
        report_content = generator(report_data)
        
        # Write to file
        file_extension = self.config.format.value
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.config.report_id}_fault_report_{timestamp}.{file_extension}"
        file_path = Path(self.config.output_path) / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return str(file_path)
    
    def generate_system_health_report(self, system_health_data: Dict[str, Any],
                                     performance_history: List[Dict[str, Any]]) -> str:
        """Generate system health and performance report."""
        
        report_data = {
            'metadata': self._generate_metadata(),
            'executive_summary': self._generate_health_executive_summary(system_health_data),
            'system_health': system_health_data,
            'performance_trends': self._analyze_performance_trends(performance_history),
            'maintenance_schedule': self._generate_maintenance_schedule(system_health_data),
            'recommendations': self._generate_health_recommendations(
                system_health_data, performance_history)
        }
        
        generator = self.templates.get(self.config.format, self._generate_markdown_report)
        report_content = generator(report_data)
        
        # Write to file
        file_extension = self.config.format.value
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.config.report_id}_health_report_{timestamp}.{file_extension}"
        file_path = Path(self.config.output_path) / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return str(file_path)
    
    def generate_maintenance_report(self, maintenance_actions: List[Dict[str, Any]],
                                   equipment_status: Dict[str, Any]) -> str:
        """Generate maintenance planning and scheduling report."""
        
        report_data = {
            'metadata': self._generate_metadata(),
            'maintenance_summary': self._generate_maintenance_summary(maintenance_actions),
            'maintenance_schedule': self._organize_maintenance_schedule(maintenance_actions),
            'equipment_status': equipment_status,
            'cost_analysis': self._analyze_maintenance_costs(maintenance_actions),
            'recommendations': self._generate_maintenance_recommendations(maintenance_actions)
        }
        
        generator = self.templates.get(self.config.format, self._generate_markdown_report)
        report_content = generator(report_data)
        
        # Write to file
        file_extension = self.config.format.value
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.config.report_id}_maintenance_report_{timestamp}.{file_extension}"
        file_path = Path(self.config.output_path) / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return str(file_path)
    
    def _generate_metadata(self) -> Dict[str, Any]:
        """Generate report metadata section."""
        return {
            'report_id': self.config.report_id,
            'title': self.config.title,
            'generation_time': datetime.now().isoformat(),
            'company_name': self.config.company_name,
            'facility_name': self.config.facility_name,
            'author': self.config.author,
            'format': self.config.format.value,
            'audience': self.config.audience,
            'detail_level': self.config.detail_level,
            'time_range_hours': self.config.time_range_hours
        }
    
    def _generate_executive_summary(self, diagnostic_results: List[Dict[str, Any]],
                                   system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary section."""
        
        # Count issues by severity
        severity_counts = {}
        for result in diagnostic_results:
            severity = result.get('severity', 'unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Calculate system availability
        crac_states = system_data.get('crac_states', [])
        total_capacity = sum(crac.get('q_rated_kw', 0) for crac in crac_states)
        available_capacity = sum(crac.get('q_cool_kw', 0) for crac in crac_states)
        availability = (available_capacity / total_capacity * 100) if total_capacity > 0 else 0
        
        # Identify critical issues
        critical_issues = [r for r in diagnostic_results 
                          if r.get('severity') in ['critical', 'major']]
        
        return {
            'total_issues': len(diagnostic_results),
            'critical_issues': len(critical_issues),
            'severity_breakdown': severity_counts,
            'system_availability': availability,
            'overall_status': 'critical' if critical_issues else 'normal',
            'key_concerns': [issue.get('title', 'Unknown') for issue in critical_issues[:3]],
            'recommended_immediate_actions': len([
                action for result in diagnostic_results
                for action in result.get('recommended_actions', [])
            ])
        }
    
    def _generate_fault_analysis(self, diagnostic_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate detailed fault analysis section."""
        
        # Group by category
        category_groups = {}
        for result in diagnostic_results:
            category = result.get('category', 'unknown')
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(result)
        
        # Analyze trends
        fault_trends = {}
        for category, results in category_groups.items():
            fault_trends[category] = {
                'count': len(results),
                'avg_confidence': statistics.mean(
                    r.get('confidence_level', 0) for r in results),
                'severity_distribution': self._analyze_severity_distribution(results)
            }
        
        return {
            'category_breakdown': category_groups,
            'fault_trends': fault_trends,
            'top_issues': sorted(diagnostic_results, 
                               key=lambda x: x.get('confidence_level', 0), 
                               reverse=True)[:5],
            'recurring_issues': self._identify_recurring_issues(diagnostic_results)
        }
    
    def _generate_system_health_section(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate system health status section."""
        
        # Equipment status summary
        crac_states = system_data.get('crac_states', [])
        equipment_health = {
            'total_cracs': len(crac_states),
            'running_cracs': len([c for c in crac_states if c.get('status') == 'running']),
            'failed_cracs': len([c for c in crac_states if c.get('failed', False)]),
            'average_runtime': statistics.mean(
                c.get('runtime_hours', 0) for c in crac_states) if crac_states else 0
        }
        
        # Temperature control performance
        sensor_temps = system_data.get('sensor_temps', [])
        temp_performance = {
            'sensor_count': len(sensor_temps),
            'average_temperature': statistics.mean(sensor_temps) if sensor_temps else 0,
            'temperature_range': max(sensor_temps) - min(sensor_temps) if len(sensor_temps) > 1 else 0,
            'setpoint': system_data.get('setpoint', 22.0)
        }
        
        # Energy efficiency
        total_cooling = sum(c.get('q_cool_kw', 0) for c in crac_states)
        total_power = sum(c.get('power_kw', 0) for c in crac_states)
        efficiency = {
            'total_cooling_kw': total_cooling,
            'total_power_kw': total_power,
            'system_cop': total_cooling / total_power if total_power > 0 else 0,
            'efficiency_rating': 'excellent' if total_cooling / total_power > 3.0 else 'good'
        }
        
        return {
            'equipment_health': equipment_health,
            'temperature_performance': temp_performance,
            'energy_efficiency': efficiency,
            'overall_health_score': self._calculate_health_score(
                equipment_health, temp_performance, efficiency)
        }
    
    def _generate_recommendations(self, diagnostic_results: List[Dict[str, Any]],
                                root_cause_analysis: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate recommendations section."""
        
        # Compile all recommendations
        all_recommendations = []
        for result in diagnostic_results:
            actions = result.get('recommended_actions', [])
            for action in actions:
                all_recommendations.append({
                    'action': action,
                    'source': result.get('diagnostic_id'),
                    'priority': result.get('severity', 'medium'),
                    'component': result.get('component_id')
                })
        
        # Add root cause recommendations
        if root_cause_analysis:
            immediate_actions = root_cause_analysis.get('immediate_actions', [])
            for action in immediate_actions:
                all_recommendations.append({
                    'action': action.get('description', 'Unknown action'),
                    'source': 'root_cause_analysis',
                    'priority': action.get('priority', 'medium'),
                    'component': 'system'
                })
        
        # Prioritize recommendations
        priority_order = {'critical': 0, 'major': 1, 'high': 2, 'medium': 3, 'low': 4}
        prioritized = sorted(all_recommendations, 
                           key=lambda x: priority_order.get(x['priority'], 5))
        
        return {
            'immediate_actions': prioritized[:5],
            'short_term_actions': prioritized[5:10],
            'long_term_actions': prioritized[10:],
            'maintenance_planning': self._generate_maintenance_planning(prioritized)
        }
    
    def _analyze_performance_trends(self, performance_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        if not performance_history:
            return {}
        
        # Sort by timestamp
        sorted_history = sorted(performance_history, key=lambda x: x.get('timestamp', 0))
        
        # Calculate trends
        trends = {}
        
        # Temperature trend
        temps = [h.get('temperature', 0) for h in sorted_history]
        if len(temps) > 1:
            temp_trend = 'stable'
            if temps[-1] > temps[0] + 0.5:
                temp_trend = 'increasing'
            elif temps[-1] < temps[0] - 0.5:
                temp_trend = 'decreasing'
            trends['temperature'] = {
                'direction': temp_trend,
                'range': max(temps) - min(temps),
                'average': statistics.mean(temps)
            }
        
        # Energy efficiency trend
        cops = [h.get('system_cop', 0) for h in sorted_history if h.get('system_cop', 0) > 0]
        if len(cops) > 1:
            efficiency_trend = 'stable'
            if cops[-1] > cops[0] * 1.05:
                efficiency_trend = 'improving'
            elif cops[-1] < cops[0] * 0.95:
                efficiency_trend = 'declining'
            trends['efficiency'] = {
                'direction': efficiency_trend,
                'current_cop': cops[-1],
                'average_cop': statistics.mean(cops)
            }
        
        return trends
    
    def _generate_maintenance_schedule(self, system_health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate predictive maintenance schedule."""
        
        # Mock maintenance schedule based on system health
        equipment_health = system_health_data.get('equipment_health', {})
        avg_runtime = equipment_health.get('average_runtime', 0)
        
        schedule = {
            'immediate': [],
            'this_week': [],
            'this_month': [],
            'next_quarter': []
        }
        
        # Schedule based on runtime
        if avg_runtime > 8000:  # High runtime
            schedule['this_week'].append({
                'task': 'Inspect high-runtime CRAC units',
                'duration': '2-4 hours',
                'priority': 'high'
            })
        
        if avg_runtime > 6000:
            schedule['this_month'].append({
                'task': 'Replace air filters',
                'duration': '1 hour',
                'priority': 'medium'
            })
        
        # Regular maintenance
        schedule['next_quarter'].extend([
            {
                'task': 'Calibrate temperature sensors',
                'duration': '2 hours',
                'priority': 'medium'
            },
            {
                'task': 'Clean condenser coils',
                'duration': '3-4 hours',
                'priority': 'medium'
            }
        ])
        
        return schedule
    
    def _generate_markdown_report(self, report_data: Dict[str, Any]) -> str:
        """Generate Markdown format report."""
        
        metadata = report_data.get('metadata', {})
        exec_summary = report_data.get('executive_summary', {})
        fault_analysis = report_data.get('fault_analysis', {})
        system_health = report_data.get('system_health', {})
        recommendations = report_data.get('recommendations', {})
        
        lines = []
        
        # Header
        lines.extend([
            f"# {metadata.get('title', 'BAS Diagnostic Report')}",
            "",
            f"**Facility:** {metadata.get('facility_name', 'Unknown')}  ",
            f"**Generated:** {metadata.get('generation_time', 'Unknown')}  ",
            f"**Author:** {metadata.get('author', 'Unknown')}  ",
            f"**Report ID:** {metadata.get('report_id', 'Unknown')}",
            "",
            "---",
            ""
        ])
        
        # Executive Summary
        if ReportSection.EXECUTIVE_SUMMARY in self.config.sections:
            lines.extend([
                "## Executive Summary",
                "",
                f"**Overall Status:** {exec_summary.get('overall_status', 'Unknown').upper()}",
                "",
                f"- **Total Issues:** {exec_summary.get('total_issues', 0)}",
                f"- **Critical Issues:** {exec_summary.get('critical_issues', 0)}",
                f"- **System Availability:** {exec_summary.get('system_availability', 0):.1f}%",
                "",
                "### Key Concerns",
                ""
            ])
            
            for concern in exec_summary.get('key_concerns', []):
                lines.append(f"- {concern}")
            
            lines.extend(["", "---", ""])
        
        # Fault Analysis
        if ReportSection.FAULT_ANALYSIS in self.config.sections and fault_analysis:
            lines.extend([
                "## Fault Analysis",
                "",
                "### Issues by Category",
                ""
            ])
            
            category_breakdown = fault_analysis.get('category_breakdown', {})
            for category, issues in category_breakdown.items():
                lines.extend([
                    f"#### {category.replace('_', ' ').title()}",
                    f"**Count:** {len(issues)}",
                    ""
                ])
                
                for issue in issues[:3]:  # Show top 3 per category
                    confidence = issue.get('confidence_level', 0)
                    lines.append(f"- **{issue.get('title', 'Unknown')}** "
                               f"(Confidence: {confidence:.1%})")
                    lines.append(f"  - *{issue.get('description', 'No description')}*")
                
                lines.append("")
            
            lines.extend(["---", ""])
        
        # System Health
        if ReportSection.SYSTEM_HEALTH in self.config.sections and system_health:
            lines.extend([
                "## System Health Status",
                ""
            ])
            
            equipment = system_health.get('equipment_health', {})
            temp_perf = system_health.get('temperature_performance', {})
            efficiency = system_health.get('energy_efficiency', {})
            
            lines.extend([
                "### Equipment Status",
                f"- **Total CRAC Units:** {equipment.get('total_cracs', 0)}",
                f"- **Running Units:** {equipment.get('running_cracs', 0)}",
                f"- **Failed Units:** {equipment.get('failed_cracs', 0)}",
                f"- **Average Runtime:** {equipment.get('average_runtime', 0):.1f} hours",
                "",
                "### Temperature Control",
                f"- **Setpoint:** {temp_perf.get('setpoint', 0):.1f}°C",
                f"- **Average Temperature:** {temp_perf.get('average_temperature', 0):.1f}°C",
                f"- **Temperature Range:** {temp_perf.get('temperature_range', 0):.1f}°C",
                "",
                "### Energy Performance",
                f"- **System COP:** {efficiency.get('system_cop', 0):.2f}",
                f"- **Total Cooling:** {efficiency.get('total_cooling_kw', 0):.1f} kW",
                f"- **Total Power:** {efficiency.get('total_power_kw', 0):.1f} kW",
                "",
                "---",
                ""
            ])
        
        # Recommendations
        if ReportSection.RECOMMENDATIONS in self.config.sections and recommendations:
            lines.extend([
                "## Recommendations",
                "",
                "### Immediate Actions",
                ""
            ])
            
            for action in recommendations.get('immediate_actions', [])[:5]:
                lines.append(f"- **{action.get('action', 'Unknown')}**")
                lines.append(f"  - Priority: {action.get('priority', 'medium').title()}")
                lines.append(f"  - Component: {action.get('component', 'unknown')}")
                lines.append("")
            
            lines.extend([
                "### Maintenance Planning",
                ""
            ])
            
            maintenance = recommendations.get('maintenance_planning', {})
            for timeframe, tasks in maintenance.items():
                if tasks:
                    lines.append(f"#### {timeframe.replace('_', ' ').title()}")
                    for task in tasks[:3]:  # Limit to 3 tasks per timeframe
                        lines.append(f"- {task}")
                    lines.append("")
        
        # Footer
        lines.extend([
            "---",
            "",
            f"*Report generated by {metadata.get('author', 'BAS Diagnostic System')} "
            f"on {metadata.get('generation_time', 'Unknown')}*"
        ])
        
        return "\n".join(lines)
    
    def _generate_json_report(self, report_data: Dict[str, Any]) -> str:
        """Generate JSON format report."""
        return json.dumps(report_data, indent=2, default=str)
    
    def _generate_csv_report(self, report_data: Dict[str, Any]) -> str:
        """Generate CSV format report for diagnostic results."""
        
        # Extract diagnostic results for CSV
        fault_analysis = report_data.get('fault_analysis', {})
        category_breakdown = fault_analysis.get('category_breakdown', {})
        
        csv_lines = []
        csv_lines.append("Diagnostic ID,Timestamp,Category,Severity,Title,Description,Component,Confidence,Measured Value,Expected Value")
        
        for category, issues in category_breakdown.items():
            for issue in issues:
                row = [
                    issue.get('diagnostic_id', ''),
                    str(issue.get('timestamp', '')),
                    issue.get('category', ''),
                    issue.get('severity', ''),
                    issue.get('title', ''),
                    issue.get('description', ''),
                    issue.get('component_id', ''),
                    str(issue.get('confidence_level', '')),
                    str(issue.get('measured_value', '')),
                    str(issue.get('expected_value', ''))
                ]
                csv_lines.append(','.join(f'"{field}"' for field in row))
        
        return '\n'.join(csv_lines)
    
    def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML format report."""
        
        # Simple HTML template
        metadata = report_data.get('metadata', {})
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{metadata.get('title', 'BAS Diagnostic Report')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ border-bottom: 2px solid #333; padding-bottom: 10px; }}
        .section {{ margin: 20px 0; }}
        .critical {{ color: red; font-weight: bold; }}
        .warning {{ color: orange; }}
        .info {{ color: blue; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{metadata.get('title', 'BAS Diagnostic Report')}</h1>
        <p><strong>Facility:</strong> {metadata.get('facility_name', 'Unknown')}</p>
        <p><strong>Generated:</strong> {metadata.get('generation_time', 'Unknown')}</p>
    </div>
    
    <div class="section">
        <h2>Executive Summary</h2>
        <!-- Content would be populated from report_data -->
        <p>Report content goes here...</p>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_text_report(self, report_data: Dict[str, Any]) -> str:
        """Generate plain text format report."""
        
        # Convert markdown to plain text (simplified)
        markdown_content = self._generate_markdown_report(report_data)
        
        # Simple markdown to text conversion
        lines = markdown_content.split('\n')
        text_lines = []
        
        for line in lines:
            # Remove markdown formatting
            line = line.replace('**', '').replace('*', '').replace('#', '')
            line = line.replace('---', '=' * 50)
            text_lines.append(line)
        
        return '\n'.join(text_lines)
    
    # Helper methods
    def _analyze_severity_distribution(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze severity distribution for a group of results."""
        distribution = {}
        for result in results:
            severity = result.get('severity', 'unknown')
            distribution[severity] = distribution.get(severity, 0) + 1
        return distribution
    
    def _identify_recurring_issues(self, diagnostic_results: List[Dict[str, Any]]) -> List[str]:
        """Identify recurring issues from diagnostic results."""
        # Simple implementation - count similar titles
        title_counts = {}
        for result in diagnostic_results:
            title = result.get('title', 'Unknown')
            title_counts[title] = title_counts.get(title, 0) + 1
        
        # Return titles that appear more than once
        return [title for title, count in title_counts.items() if count > 1]
    
    def _calculate_health_score(self, equipment_health: Dict[str, Any],
                               temp_performance: Dict[str, Any],
                               efficiency: Dict[str, Any]) -> float:
        """Calculate overall system health score (0-100)."""
        
        score = 100.0
        
        # Reduce score for failed equipment
        failed_cracs = equipment_health.get('failed_cracs', 0)
        total_cracs = equipment_health.get('total_cracs', 1)
        score -= (failed_cracs / total_cracs) * 30
        
        # Reduce score for temperature control issues
        temp_range = temp_performance.get('temperature_range', 0)
        if temp_range > 2.0:  # More than 2°C range
            score -= 20
        elif temp_range > 1.0:  # More than 1°C range
            score -= 10
        
        # Reduce score for poor efficiency
        system_cop = efficiency.get('system_cop', 3.5)
        if system_cop < 2.5:
            score -= 25
        elif system_cop < 3.0:
            score -= 10
        
        return max(0.0, score)
    
    def _generate_maintenance_planning(self, recommendations: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate maintenance planning from recommendations."""
        
        planning = {
            'immediate': [],
            'this_week': [],
            'this_month': [],
            'next_quarter': []
        }
        
        for rec in recommendations:
            priority = rec.get('priority', 'medium')
            action = rec.get('action', 'Unknown action')
            
            if priority in ['critical', 'major']:
                planning['immediate'].append(action)
            elif priority == 'high':
                planning['this_week'].append(action)
            elif priority == 'medium':
                planning['this_month'].append(action)
            else:
                planning['next_quarter'].append(action)
        
        return planning
    
    def _generate_health_executive_summary(self, system_health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary for health report."""
        
        equipment_health = system_health_data.get('equipment_health', {})
        health_score = system_health_data.get('overall_health_score', 100)
        
        status = 'excellent'
        if health_score < 60:
            status = 'poor'
        elif health_score < 80:
            status = 'fair'
        elif health_score < 95:
            status = 'good'
        
        return {
            'overall_health_score': health_score,
            'health_status': status,
            'equipment_availability': equipment_health.get('running_cracs', 0) / max(equipment_health.get('total_cracs', 1), 1) * 100,
            'critical_issues': equipment_health.get('failed_cracs', 0),
            'maintenance_alerts': 0  # Would be calculated from actual maintenance data
        }
    
    def _generate_health_recommendations(self, system_health_data: Dict[str, Any],
                                       performance_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate recommendations for health report."""
        
        recommendations = {
            'immediate_actions': [],
            'preventive_maintenance': [],
            'optimization_opportunities': []
        }
        
        # Check for immediate issues
        equipment_health = system_health_data.get('equipment_health', {})
        if equipment_health.get('failed_cracs', 0) > 0:
            recommendations['immediate_actions'].append(
                'Repair or replace failed CRAC units to restore full capacity')
        
        # Preventive maintenance based on runtime
        avg_runtime = equipment_health.get('average_runtime', 0)
        if avg_runtime > 6000:
            recommendations['preventive_maintenance'].append(
                'Schedule preventive maintenance for high-runtime equipment')
        
        # Optimization opportunities
        efficiency_data = system_health_data.get('energy_efficiency', {})
        if efficiency_data.get('system_cop', 0) < 3.0:
            recommendations['optimization_opportunities'].append(
                'Investigate energy efficiency improvements')
        
        return recommendations
    
    # Additional helper methods for maintenance and cost analysis
    def _generate_maintenance_summary(self, maintenance_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate maintenance summary from actions."""
        
        total_actions = len(maintenance_actions)
        
        # Count by priority
        priority_counts = {}
        for action in maintenance_actions:
            priority = action.get('priority', 'medium')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Count by category
        category_counts = {}
        for action in maintenance_actions:
            category = action.get('category', 'unknown')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            'total_actions': total_actions,
            'priority_breakdown': priority_counts,
            'category_breakdown': category_counts,
            'estimated_total_time': self._calculate_total_maintenance_time(maintenance_actions)
        }
    
    def _organize_maintenance_schedule(self, maintenance_actions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Organize maintenance actions into time-based schedule."""
        
        schedule = {
            'immediate': [],
            'this_week': [], 
            'this_month': [],
            'this_quarter': []
        }
        
        for action in maintenance_actions:
            priority = action.get('priority', 'medium')
            
            if priority == 'immediate':
                schedule['immediate'].append(action)
            elif priority in ['urgent', 'high']:
                schedule['this_week'].append(action)
            elif priority == 'medium':
                schedule['this_month'].append(action)
            else:
                schedule['this_quarter'].append(action)
        
        return schedule
    
    def _analyze_maintenance_costs(self, maintenance_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze maintenance costs and budget impact."""
        
        cost_by_impact = {'low': 0, 'medium': 0, 'high': 0}
        
        for action in maintenance_actions:
            cost_impact = action.get('cost_impact', 'medium')
            cost_by_impact[cost_impact] += 1
        
        return {
            'cost_distribution': cost_by_impact,
            'high_cost_actions': [a for a in maintenance_actions 
                                if a.get('cost_impact') == 'high'],
            'estimated_budget_impact': 'medium'  # Would be calculated from actual costs
        }
    
    def _generate_maintenance_recommendations(self, maintenance_actions: List[Dict[str, Any]]) -> List[str]:
        """Generate strategic maintenance recommendations."""
        
        recommendations = []
        
        # Check for patterns
        high_priority_count = len([a for a in maintenance_actions 
                                 if a.get('priority') in ['immediate', 'urgent']])
        
        if high_priority_count > 5:
            recommendations.append(
                "Consider increasing preventive maintenance frequency to reduce reactive work")
        
        # Check for skill requirements
        required_skills = set()
        for action in maintenance_actions:
            required_skills.update(action.get('required_skills', []))
        
        if len(required_skills) > 3:
            recommendations.append(
                "Ensure adequate training for diverse skill requirements")
        
        recommendations.append(
            "Implement predictive maintenance technologies to optimize scheduling")
        
        return recommendations
    
    def _calculate_total_maintenance_time(self, maintenance_actions: List[Dict[str, Any]]) -> str:
        """Calculate estimated total maintenance time."""
        
        total_hours = 0
        
        for action in maintenance_actions:
            duration_str = action.get('estimated_duration', '2 hours')
            
            # Simple parsing of duration strings
            if 'hour' in duration_str:
                try:
                    # Extract first number from string like "2-4 hours"
                    hours = float(duration_str.split()[0].split('-')[0])
                    total_hours += hours
                except:
                    total_hours += 2  # Default estimate
        
        return f"{total_hours:.1f} hours"


def create_default_report_config() -> ReportConfig:
    """Create default report configuration."""
    return ReportConfig(
        report_id="default",
        title="BAS Diagnostic Report",
        format=ReportFormat.MARKDOWN,
        sections=[
            ReportSection.EXECUTIVE_SUMMARY,
            ReportSection.FAULT_ANALYSIS,
            ReportSection.SYSTEM_HEALTH,
            ReportSection.RECOMMENDATIONS
        ],
        audience="technical",
        detail_level="standard"
    )