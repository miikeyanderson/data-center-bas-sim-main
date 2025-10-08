# Data Center BAS - Graphics Requirements
## Niagara HMI Specifications

### Document Information
- **System**: Data Center HVAC with N+1 CRAC Units
- **HMI Platform**: Niagara Workbench Graphics
- **Target Users**: Operations staff, maintenance technicians, facility managers
- **Resolution**: 1920×1080 minimum (responsive design)
- **Date**: 2025-10-07

---

## 1. NAVIGATION STRUCTURE

### Main Navigation Menu
- **Overview**: System summary and status
- **Equipment**: Individual CRAC unit details
- **Trends**: Historical data and performance charts  
- **Alarms**: Active alarms and alarm history
- **Controls**: Manual overrides and setpoint adjustments
- **Reports**: Performance reports and KPI dashboard

### Breadcrumb Navigation
- Always show current location: Home > Equipment > CRAC1
- Quick navigation to parent levels
- Context-sensitive help links

---

## 2. OVERVIEW SCREEN (Main Dashboard)

### Layout: 12-Column Grid System

#### Top Status Bar (Full Width)
- **System Status Indicator**: Normal/Warning/Alarm/Critical
- **Current Space Temperature**: Large display with setpoint
- **Temperature Error**: Color-coded deviation from setpoint
- **Active Alarms Count**: With severity breakdown
- **System Mode**: Auto/Manual/Maintenance
- **Date/Time**: Local time with simulation time if applicable

#### CRAC Status Cards (4 columns each)
```
┌─────────────────┬─────────────────┬─────────────────┐
│     CRAC-1      │     CRAC-2      │     CRAC-3      │
│   (LEAD)        │    (LAG)        │   (STANDBY)     │
├─────────────────┼─────────────────┼─────────────────┤
│ Status: ON      │ Status: ON      │ Status: OFF     │
│ Output: 85%     │ Output: 65%     │ Output: 0%      │
│ Power: 18.5kW   │ Power: 14.2kW   │ Power: 0.0kW    │
│ Supply: 13.2°C  │ Supply: 14.1°C  │ Supply: --      │
│ Runtime: 247h   │ Runtime: 183h   │ Runtime: 0h     │
│ [Manual] [Reset]│ [Manual] [Reset]│ [Manual] [Test] │
└─────────────────┴─────────────────┴─────────────────┘
```

#### Performance Summary (Full Width)
- **Temperature Accuracy**: 95.5% within ±0.5°C (last 24h)
- **System COP**: 2.75 (current), 2.82 (24h avg)
- **Energy Consumption**: 45.2 kWh today
- **LAG Staging Events**: 12 today, last at 14:23

#### Mini Trend Charts (3 columns each)
- **Space Temperature vs Setpoint** (last 4 hours)
- **Total Cooling Output** (last 4 hours)  
- **System COP Trend** (last 4 hours)

---

## 3. EQUIPMENT SCREEN

### Individual CRAC Detail View

#### Equipment Header
- **Unit Identification**: CRAC-1 (Lead Unit)
- **Status Indicators**: Running/Off, Normal/Alarm, Auto/Manual
- **Role Badge**: Lead/Lag/Standby with role rotation timer

#### Real-Time Data (2-column layout)
```
┌─────────────────────┬─────────────────────┐
│ CURRENT STATUS      │ OPERATIONAL DATA    │
├─────────────────────┼─────────────────────┤
│ Unit Status: ON     │ Capacity: 85.2%     │
│ Command: 85%        │ Cooling: 42.6 kW    │
│ Mode: AUTO          │ Power: 18.5 kW      │
│ Role: LEAD          │ COP: 2.30           │
│ Alarms: 0 Active    │ Supply Temp: 13.2°C │
│ Runtime: 247.3 hrs  │ Return Temp: 22.1°C │
│ Starts: 23 today    │ Airflow: 8,200 CFM  │
└─────────────────────┴─────────────────────┘
```

#### Control Panel
- **Manual Override Toggle**: Auto/Manual with 4-hour timeout
- **Capacity Slider**: 15-100% (manual mode only)
- **Start/Stop Buttons**: With confirmation dialog
- **Reset Alarms**: Unit-specific alarm reset
- **Maintenance Mode**: Lockout for service

#### Historical Data Table
- **Runtime History**: Daily totals for last 30 days
- **Start/Stop Log**: Last 100 events with timestamps
- **Alarm History**: Last 50 alarms with resolution times
- **Maintenance Log**: Scheduled and completed work orders

---

## 4. TRENDS SCREEN

### Trend Chart Configuration

#### Primary Trends (Real-Time)
- **Space Temperature**: 1-second resolution, 8-hour window
- **CRAC Outputs**: All 3 units, 1-second resolution, 4-hour window
- **Power Consumption**: Total and individual, 1-minute resolution, 24-hour window
- **COP Performance**: 5-minute average, 7-day window

#### Trend Controls
- **Time Range Selector**: 1h, 4h, 24h, 7d, 30d, Custom
- **Data Resolution**: Auto-scale based on time range
- **Y-Axis Options**: Auto-scale, fixed scale, split axis
- **Export Function**: CSV export with date range selection

#### Trend Analysis Tools
- **Zoom/Pan**: Mouse wheel and drag functionality
- **Cursor Values**: Real-time value display at mouse position
- **Min/Max Markers**: Automatic highlighting of extremes
- **Average Lines**: Moving averages (1h, 4h, 24h)

---

## 5. ALARMS SCREEN

### Active Alarms Table
```
┌──────────┬──────────┬───────────────┬──────────┬──────────┬────────────┐
│   Time   │ Priority │   Alarm Tag   │  Source  │  State   │   Action   │
├──────────┼──────────┼───────────────┼──────────┼──────────┼────────────┤
│ 14:23:15 │   HIGH   │  TEMP_HIGH    │ SpaceTemp│  ACTIVE  │ [ACK][RST] │
│ 13:45:32 │ MEDIUM   │ CRAC2_FAIL    │  CRAC-2  │   ACK    │   [RST]    │
│ 12:18:07 │   LOW    │  LOW_COP      │  System  │ CLEARED  │            │
└──────────┴──────────┴───────────────┴──────────┴──────────┴────────────┘
```

### Alarm Summary Panel
- **Current Active**: 2 alarms (1 HIGH, 1 MEDIUM)
- **Unacknowledged**: 1 alarm requiring attention
- **Cleared Today**: 8 alarms automatically resolved
- **Average Response**: 2.3 minutes to acknowledgment

### Alarm History Filter
- **Date Range**: From/To date picker
- **Priority Filter**: All, Critical, High, Medium, Low
- **Source Filter**: All, Equipment, System, Safety
- **State Filter**: All, Active, Acknowledged, Cleared

---

## 6. CONTROLS SCREEN

### System Controls Panel

#### Setpoint Control
- **Current Setpoint**: 22.0°C (large display)
- **Setpoint Adjustment**: ±2°C range with 0.1°C increments
- **Temporary Override**: 1-8 hour duration selection
- **Schedule Override**: Disable/Enable automatic schedules

#### Operating Mode Controls
- **System Mode**: Auto/Manual/Maintenance (radio buttons)
- **Staging Mode**: Enable/Disable automatic LAG staging
- **Role Rotation**: Enable/Disable daily rotation
- **Emergency Override**: Force all units to maximum

#### Manual Unit Controls (3-column layout)
```
┌─────────────────┬─────────────────┬─────────────────┐
│     CRAC-1      │     CRAC-2      │     CRAC-3      │
├─────────────────┼─────────────────┼─────────────────┤
│ [START] [STOP]  │ [START] [STOP]  │ [START] [STOP]  │
│ Capacity: 85%   │ Capacity: 65%   │ Capacity: 0%    │
│ ┌─────────────┐ │ ┌─────────────┐ │ ┌─────────────┐ │
│ │ ■■■■■■■■□□□ │ │ │ ■■■■■■□□□□□ │ │ │ □□□□□□□□□□□ │ │
│ └─────────────┘ │ └─────────────┘ │ └─────────────┘ │
│ [AUTO] [MANUAL] │ [AUTO] [MANUAL] │ [AUTO] [MANUAL] │
└─────────────────┴─────────────────┴─────────────────┘
```

### Safety Interlocks
- **Fire Alarm Status**: Normal (green indicator)
- **Emergency Stop**: Normal (green indicator)  
- **Water Detection**: Normal (green indicator)
- **Interlock Override**: Emergency authorization required

---

## 7. REPORTS SCREEN

### KPI Dashboard

#### Performance Metrics (Current Period)
- **Temperature Accuracy**: 95.5% within ±0.5°C
- **Steady-State Stability**: 0.008°C standard deviation
- **Average COP**: 2.82 (target: ≥2.70)
- **Energy Efficiency**: 98.2% of baseline consumption

#### Trend Indicators (vs Previous Period)
- **Accuracy**: ↑ 2.3% improvement
- **COP**: ↓ 0.05 slight decrease
- **Energy**: ↓ 1.8% reduction
- **Uptime**: ↑ 99.8% excellent availability

### Report Generation
- **Report Type**: Daily, Weekly, Monthly, Custom
- **Include Sections**: Performance, Alarms, Maintenance, Energy
- **Output Format**: PDF, Excel, CSV
- **Email Distribution**: Automatic scheduling available

### Historical Performance Tables
- **Daily Summary**: Last 30 days with key metrics
- **Monthly Trends**: Last 12 months performance overview
- **Comparison Analysis**: Current vs previous periods
- **Benchmark Targets**: Progress toward annual goals

---

## 8. RESPONSIVE DESIGN REQUIREMENTS

### Desktop (1920×1080+)
- Full 12-column layout with all widgets visible
- Side navigation panel always visible
- Popup dialogs for detailed equipment information

### Tablet (1024×768)
- Condensed 8-column layout
- Collapsible navigation menu
- Simplified CRAC status cards (2 columns)

### Mobile (768×1024)
- Single column stack layout
- Bottom navigation tabs
- Touch-optimized controls (minimum 44px touch targets)

---

## 9. COLOR CODING STANDARDS

### Status Colors
- **Normal**: #27AE60 (Green)
- **Warning**: #F39C12 (Orange)  
- **Alarm**: #E74C3C (Red)
- **Critical**: #C0392B (Dark Red)
- **Offline**: #95A5A6 (Gray)

### Equipment Role Colors  
- **Lead**: #3498DB (Blue)
- **Lag**: #9B59B6 (Purple)
- **Standby**: #34495E (Dark Blue)

### Temperature Range Colors
- **Normal** (21.5-22.5°C): #27AE60 (Green)
- **Minor Deviation** (±0.5-1.0°C): #F39C12 (Orange)
- **Major Deviation** (>±1.0°C): #E74C3C (Red)

---

## 10. WIDGET SPECIFICATIONS

### Temperature Display Widget
- **Size**: 200×150 pixels minimum
- **Font**: Large numeric (48px) with units (24px)
- **Background**: Color-coded based on deviation from setpoint
- **Update Rate**: 1 second
- **Precision**: 0.1°C display resolution

### CRAC Status Card Widget
- **Size**: 300×250 pixels minimum
- **Elements**: Status indicator, output bar graph, key metrics
- **Interactions**: Click for detail view, hover for tooltip
- **Update Rate**: 1 second for status, 5 seconds for metrics

### Trend Chart Widget
- **Size**: Scalable from 400×300 to full screen
- **Lines**: Maximum 6 data series with different colors/styles
- **Interactions**: Zoom, pan, cursor tracking, legend toggle
- **Export**: Right-click context menu for data export

### Alarm Summary Widget
- **Size**: 400×200 pixels minimum
- **Display**: Count by priority with color coding
- **Interactions**: Click to open alarms screen
- **Update Rate**: Immediate on alarm state change

---

## 11. USER ACCESS LEVELS

### Operator Level
- **View**: All screens (read-only)
- **Control**: Setpoint adjustment (±1°C), alarm acknowledgment
- **Restrictions**: No manual unit control, no parameter changes

### Technician Level  
- **View**: All screens with detailed data
- **Control**: Manual unit operation, maintenance mode
- **Restrictions**: No system parameter changes, no safety overrides

### Engineer Level
- **View**: All screens including configuration
- **Control**: All manual controls, parameter tuning
- **Restrictions**: Safety interlocks require dual authorization

### Administrator Level
- **View**: All screens including diagnostics
- **Control**: Complete system control including safety overrides
- **Restrictions**: All actions logged and auditable

---

## 12. IMPLEMENTATION NOTES FOR NIAGARA

### Px Programming Requirements
- Use Niagara 4.x+ Px graphics framework
- Implement responsive design using Gx layout containers
- Create reusable widget templates for CRAC status cards
- Use BajaScript for dynamic content updates

### Data Binding
- Bind all widgets to BACnet points from the points list
- Use history extensions for trend data collection
- Implement alarm aggregation using AlarmService
- Create calculated points for derived values (COP, accuracy)

### Performance Optimization
- Limit trend chart data points (max 1000 per series)
- Use efficient polling rates based on data criticality
- Implement client-side data caching for responsiveness
- Optimize graphics loading with progressive enhancement

### Security Implementation
- Integrate with Niagara user authentication
- Use role-based access control for widget visibility
- Implement secure communication (HTTPS/TLS)
- Log all user actions for audit compliance

---

**Document Control:**
- **Prepared By**: BAS Graphics Specialist
- **Implementation Platform**: Niagara 4.x+ Workbench Graphics
- **Target Resolution**: 1920×1080 minimum, responsive design
- **Accessibility**: WCAG 2.1 AA compliance for public facilities
- **Next Phase**: Detailed widget mockups and Px implementation guide