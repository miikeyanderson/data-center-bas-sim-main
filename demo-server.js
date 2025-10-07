#!/usr/bin/env node

/**
 * Data Center BAS Control System - Demo Server
 * 
 * Professional Node-RED based demonstration server for the BAS control system.
 * Provides live interactive dashboard with simulated data center operations.
 */

const express = require('express');
const RED = require('node-red');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
const server = require('http').createServer(app);

// Enable CORS for demo purposes
app.use(cors());

// Serve static files (reports, images, etc.)
app.use('/reports', express.static(path.join(__dirname, 'reports')));
app.use('/docs', express.static(path.join(__dirname, 'docs')));

// Demo landing page
app.get('/', (req, res) => {
    res.send(`
<!DOCTYPE html>
<html>
<head>
    <title>Data Center BAS Control System - Live Demo</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        /* Professional BAS/SCADA Industrial Interface Styling */
        body { 
            font-family: 'Arial', 'Helvetica', sans-serif; 
            margin: 0; 
            background: #202945; /* Industrial dark navy background */
            color: #ffffff;
            min-height: 100vh;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            padding: 20px; 
        }
        
        /* Industrial Header with System Status */
        .header {
            background: linear-gradient(145deg, #2c3e50, #34495e);
            border: 2px solid #3498db;
            padding: 25px;
            margin-bottom: 25px;
            position: relative;
            box-shadow: inset 0 1px 3px rgba(255,255,255,0.1);
        }
        .header h1 {
            color: #3498db;
            font-size: 2.2em;
            margin: 0 0 8px 0;
            font-weight: bold;
            text-shadow: 0 1px 2px rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .header p {
            color: #bdc3c7;
            font-size: 1.1em;
            margin: 0 0 15px 0;
        }
        
        /* System Status Indicator */
        .status {
            background: linear-gradient(145deg, #27ae60, #2ecc71);
            color: #ffffff;
            padding: 12px 25px;
            border-left: 4px solid #1e8449;
            margin: 15px 0;
            font-weight: bold;
            position: relative;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .status::before {
            content: "●";
            color: #a3f7a3;
            font-size: 1.2em;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        /* Professional Grid Layout */
        .demo-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin: 30px 0;
        }
        
        /* Industrial Control Panels */
        .demo-card {
            background: linear-gradient(145deg, #383838, #404040);
            border: 2px solid #555555;
            padding: 25px;
            position: relative;
            box-shadow: inset 0 1px 3px rgba(255,255,255,0.1), 0 4px 8px rgba(0,0,0,0.3);
        }
        .demo-card::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #3498db, #2980b9);
        }
        .demo-card h3 {
            color: #3498db;
            margin: 0 0 15px 0;
            font-size: 1.3em;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .demo-card ul {
            color: #bdc3c7;
            text-align: left;
            line-height: 1.6;
        }
        .demo-card li {
            margin-bottom: 5px;
        }
        
        /* Industrial Button Styling */
        .demo-btn {
            display: inline-block;
            background: linear-gradient(145deg, #2980b9, #3498db);
            color: white;
            padding: 14px 28px;
            text-decoration: none;
            border: 2px solid #2980b9;
            font-weight: bold;
            margin: 15px 0;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: 0 3px 6px rgba(0,0,0,0.3);
        }
        .demo-btn:hover {
            background: linear-gradient(145deg, #1f4e79, #2980b9);
            border-color: #3498db;
            box-shadow: 0 4px 8px rgba(52, 152, 219, 0.3);
        }
        
        /* Performance Dashboard Styling */
        .performance-preview {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin: 20px 0;
        }
        .performance-preview img {
            width: 100%;
            border: 2px solid #555555;
            box-shadow: 0 3px 6px rgba(0,0,0,0.4);
        }
        
        /* Equipment Status Icons */
        .equipment-status {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            padding: 15px;
            background: rgba(52, 73, 94, 0.3);
            border: 1px solid #555555;
        }
        .equipment-item {
            text-align: center;
            color: #bdc3c7;
        }
        .equipment-item .status-led {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin: 0 auto 5px;
            box-shadow: 0 0 8px currentColor;
        }
        .status-online { background: #27ae60; color: #27ae60; }
        .status-standby { background: #f39c12; color: #f39c12; }
        .status-offline { background: #7f8c8d; color: #7f8c8d; }
        
        /* Pulse Animation */
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        /* Industrial Typography */
        .data-value {
            font-family: 'Courier New', monospace;
            font-size: 1.2em;
            color: #3498db;
            font-weight: bold;
        }
        
        /* Footer Styling */
        .footer-info {
            text-align: center;
            margin: 40px 0;
            color: #7f8c8d;
            border-top: 1px solid #555555;
            padding-top: 20px;
        }
        .footer-info a {
            color: #3498db;
            text-decoration: none;
        }
        .footer-info a:hover {
            color: #5dade2;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>
                <svg width="32" height="32" viewBox="0 0 32 32" fill="currentColor">
                    <rect x="4" y="4" width="24" height="24" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>
                    <rect x="8" y="8" width="4" height="4" fill="currentColor"/>
                    <rect x="14" y="8" width="4" height="4" fill="currentColor"/>
                    <rect x="20" y="8" width="4" height="4" fill="currentColor"/>
                    <rect x="8" y="14" width="16" height="2" fill="currentColor"/>
                    <rect x="8" y="18" width="16" height="2" fill="currentColor"/>
                    <rect x="8" y="22" width="16" height="2" fill="currentColor"/>
                </svg>
                Data Center BAS Control System
            </h1>
            <p>Professional Building Automation System with Real-Time Control & Monitoring</p>
            
            <!-- Equipment Status Strip -->
            <div class="equipment-status">
                <div class="equipment-item">
                    <div class="status-led status-online"></div>
                    <div>CRAC-01</div>
                    <div style="font-size: 0.8em;">LEAD</div>
                </div>
                <div class="equipment-item">
                    <div class="status-led status-standby"></div>
                    <div>CRAC-02</div>
                    <div style="font-size: 0.8em;">LAG</div>
                </div>
                <div class="equipment-item">
                    <div class="status-led status-offline"></div>
                    <div>CRAC-03</div>
                    <div style="font-size: 0.8em;">STANDBY</div>
                </div>
                <div class="equipment-item">
                    <div class="data-value">72.1°F</div>
                    <div>Zone Temp</div>
                    <div style="font-size: 0.8em;">SP: 72.0°F</div>
                </div>
                <div class="equipment-item">
                    <div class="data-value">3.24</div>
                    <div>System COP</div>
                    <div style="font-size: 0.8em;">GOOD</div>
                </div>
            </div>
            
            <div class="status">
                SYSTEM OPERATIONAL - All Controllers Online - 0 Active Alarms
            </div>
        </div>

        <div class="demo-grid">
            <div class="demo-card">
                <h3>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>
                    </svg>
                    Interactive HMI Dashboard
                </h3>
                <p>Professional Node-RED interface with industrial BAS features:</p>
                <ul>
                    <li>Interactive data center floor plan with equipment mimics</li>
                    <li>Real-time temperature and airflow visualization</li>
                    <li>Professional alarm management with priority classification</li>
                    <li>CRAC role override & maintenance mode controls</li>
                    <li>P/I/D control loop analysis with individual terms</li>
                </ul>
                <a href="/ui" class="demo-btn">Launch HMI Dashboard</a>
            </div>

            <div class="demo-card">
                <h3>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 2l3.09 6.26L22 9l-5.91 5.74L17.18 22 12 19.27 6.82 22l1.09-7.26L2 9l6.91-1.74L12 2z"/>
                    </svg>
                    Node-RED Flow Editor
                </h3>
                <p>Configure and modify the control system logic:</p>
                <ul>
                    <li>Visual programming interface for BAS controls</li>
                    <li>MQTT/HTTP/WebSocket integration protocols</li>
                    <li>Real-time data processing and alarm handling</li>
                    <li>Professional PID control algorithms</li>
                    <li>Equipment staging and sequencing logic</li>
                </ul>
                <a href="/red" class="demo-btn">Open Flow Editor</a>
            </div>
        </div>

        <div class="demo-card">
            <h3>📊 System Performance Analysis</h3>
            <p>Professional engineering analysis with real-time metrics validation against industry standards:</p>
            <div class="performance-preview">
                <img src="/reports/pid_performance.png" alt="PID Performance Analysis">
                <img src="/reports/equipment_runtime.png" alt="Equipment Runtime Analysis">
                <img src="/reports/energy_performance.png" alt="Energy Performance Analysis">
                <img src="/reports/system_overview.png" alt="System Overview Dashboard">
            </div>
            <p><strong>Features:</strong> ASHRAE compliance validation, TIA-942 N+1 redundancy testing, Energy Star COP monitoring</p>
        </div>

        <div class="footer-info">
            <p><strong>Ready to deploy your own professional BAS system?</strong></p>
            <p>Complete source code and documentation: <a href="https://github.com/miikeyanderson/data-center-bas-sim-main">GitHub Repository</a></p>
            <p style="margin-top: 15px; font-size: 0.9em;">
                Demonstrates: ASHRAE Guidelines • TIA-942 Standards • Energy Star Compliance • PID Control Theory • Industrial Alarm Management
            </p>
        </div>
    </div>
</body>
</html>
    `);
});

// Node-RED settings
const settings = {
    httpAdminRoot: "/red",
    httpNodeRoot: "/api",
    httpStatic: path.join(__dirname, 'public'),
    userDir: path.join(__dirname, '.node-red'),
    flowFile: "demo-flows.json",
    credentialsFile: "demo-flows_cred.json",
    functionGlobalContext: {
        // Add any global context variables here
    },
    logging: {
        console: {
            level: "info",
            metrics: false,
            audit: false
        }
    },
    editorTheme: {
        projects: {
            enabled: false
        },
        header: {
            title: "Data Center BAS Control System",
            image: "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIiByeD0iNCIgZmlsbD0iIzAwNEI4NyIvPgo8cGF0aCBkPSJNOCA4SDI0VjI0SDhWOFoiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgZmlsbD0ibm9uZSIvPgo8Y2lyY2xlIGN4PSIxNiIgY3k9IjE2IiByPSI0IiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K"
        },
        palette: {
            theme: "default"
        }
    },
    ui: {
        path: "ui"
    }
};

// Initialize Node-RED
RED.init(server, settings);

// Add the Node-RED UI and admin endpoints
app.use(settings.httpAdminRoot, RED.httpAdmin);
app.use(settings.httpNodeRoot, RED.httpNode);

// Simple dashboard route
app.get('/ui', (req, res) => {
    res.send(`
<!DOCTYPE html>
<html>
<head>
    <title>BAS Dashboard - Data Center Control System</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        :root {
            --card-radius: 16px;
            --card-shadow: 0 6px 20px rgba(0,0,0,.12);
            --accent: #4B87FF;
            --temp-color: #9b59b6;      /* Purple for temperature */
            --setpoint-color: #3498db;  /* Blue for setpoint */
            --power-color: #e67e22;     /* Orange for power */
            --cooling-color: #27ae60;   /* Green for cooling */
            --cop-color: #7f8c8d;       /* Grey for COP */
            --alarm-color: #e74c3c;     /* Red for alarms */
        }
        
        body { 
            font-family: 'Arial', sans-serif; 
            margin: 0; 
            background: #f8f9fa; 
            color: #2c3e50;
            min-height: 100vh;
        }
        
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            padding: 20px; 
        }
        
        .page-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .page-header h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin: 0 0 8px 0;
            font-weight: 700;
        }
        
        .page-header p {
            color: #7f8c8d;
            font-size: 1.1em;
            margin: 0;
        }
        
        /* Top KPI Summary Strip */
        .kpi-strip {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .kpi-tile {
            background: white;
            border-radius: var(--card-radius);
            box-shadow: var(--card-shadow);
            padding: 20px;
            text-align: center;
            cursor: pointer;
            transition: transform 0.2s ease;
        }
        
        .kpi-tile:hover {
            transform: translateY(-2px);
        }
        
        .kpi-tile h2 {
            margin: 2px 0 0;
            font-weight: 700;
            font-size: 2.2em;
        }
        
        .kpi-tile .sub {
            opacity: 0.7;
            font-size: 12px;
            margin-top: 4px;
        }
        
        .kpi-temp-band h2 { color: var(--temp-color); }
        .kpi-failover h2 { color: var(--setpoint-color); }
        .kpi-cop h2 { color: var(--cop-color); }
        .kpi-alarms h2 { color: var(--alarm-color); }
        
        /* 2x2 Chart Grid */
        .chart-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .chart-card {
            background: white;
            border-radius: var(--card-radius);
            box-shadow: var(--card-shadow);
            padding: 20px;
        }
        
        .chart-card h3 {
            margin: 0 0 15px 0;
            font-size: 1.3em;
            font-weight: 600;
            color: #2c3e50;
        }
        
        .chart-caption {
            margin-top: 6px;
            opacity: 0.8;
            font-size: 12px;
            color: #7f8c8d;
        }
        
        /* Chart Areas */
        .chart-area {
            height: 200px;
            background: #f8f9fa;
            border-radius: 8px;
            position: relative;
            overflow: hidden;
            border: 1px solid #e9ecef;
        }
        
        .chart-placeholder {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: #6c757d;
            font-style: italic;
        }
        
        /* Equipment Cards */
        .equipment-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
        }
        
        .equipment-card {
            background: white;
            border-radius: var(--card-radius);
            box-shadow: var(--card-shadow);
            padding: 15px;
            border-left: 4px solid;
        }
        
        .equipment-card.lead { border-left-color: var(--cooling-color); }
        .equipment-card.lag { border-left-color: var(--setpoint-color); }
        .equipment-card.standby { border-left-color: var(--cop-color); }
        
        .equipment-card h4 {
            margin: 0 0 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .role-badge {
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: bold;
            color: white;
        }
        
        .role-lead { background: var(--cooling-color); }
        .role-lag { background: var(--setpoint-color); }
        .role-standby { background: var(--cop-color); }
        
        .metric-row {
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
            font-size: 13px;
        }
        
        .metric-value {
            font-weight: 600;
            color: var(--accent);
        }
        
        /* Engineer Mode Toggle */
        .engineer-mode {
            margin: 30px 0;
        }
        
        .engineer-toggle {
            background: var(--accent);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s ease;
        }
        
        .engineer-toggle:hover {
            background: #3d72e6;
            transform: translateY(-1px);
        }
        
        .engineer-panel {
            display: none;
            margin-top: 20px;
            background: white;
            border-radius: var(--card-radius);
            box-shadow: var(--card-shadow);
            padding: 20px;
        }
        
        .engineer-panel.open {
            display: block;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .kpi-strip {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .chart-grid {
                grid-template-columns: 1fr;
                grid-template-rows: auto;
            }
            
            .equipment-grid {
                grid-template-columns: 1fr;
            }
        }
        
        /* Animation */
        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
    <script>
        // Global data storage for charts
        let tempData = [];
        let energyData = [];
        let maxDataPoints = 60; // 30 seconds at 500ms intervals
        
        // Chart contexts
        let tempChart, energyChart;
        
        // Initialize charts
        function initCharts() {
            // Temperature Chart
            const tempCanvas = document.getElementById('temp-canvas');
            if (tempCanvas && tempCanvas.getContext) {
                tempChart = tempCanvas.getContext('2d');
                drawTemperatureChart();
            }
            
            // Energy Chart
            const energyCanvas = document.getElementById('energy-canvas');
            if (energyCanvas && energyCanvas.getContext) {
                energyChart = energyCanvas.getContext('2d');
                drawEnergyChart();
            }
        }
        
        // Draw temperature chart
        function drawTemperatureChart() {
            if (!tempChart || tempData.length === 0) return;
            
            const canvas = tempChart.canvas;
            const width = canvas.width;
            const height = canvas.height;
            
            // Clear canvas
            tempChart.clearRect(0, 0, width, height);
            
            // Draw background
            tempChart.fillStyle = '#f8f9fa';
            tempChart.fillRect(0, 0, width, height);
            
            // Draw setpoint band (±0.5°F)
            const setpoint = 72.0;
            const yScale = height / 4; // 4°F range (70-74°F)
            const yOffset = height / 2;
            
            // Setpoint band
            tempChart.fillStyle = 'rgba(52, 152, 219, 0.1)';
            const bandTop = yOffset - (0.5 * yScale / 2);
            const bandHeight = yScale / 2;
            tempChart.fillRect(0, bandTop, width, bandHeight);
            
            // Draw data lines
            if (tempData.length > 1) {
                const xStep = width / (maxDataPoints - 1);
                
                // Temperature line (purple)
                tempChart.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue('--temp-color');
                tempChart.lineWidth = 2;
                tempChart.beginPath();
                
                tempData.forEach((point, i) => {
                    const x = i * xStep;
                    const y = yOffset - ((point.temp - setpoint) * yScale / 2);
                    if (i === 0) tempChart.moveTo(x, y);
                    else tempChart.lineTo(x, y);
                });
                tempChart.stroke();
                
                // Setpoint line (blue)
                tempChart.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue('--setpoint-color');
                tempChart.lineWidth = 1;
                tempChart.setLineDash([5, 5]);
                tempChart.beginPath();
                tempChart.moveTo(0, yOffset);
                tempChart.lineTo(width, yOffset);
                tempChart.stroke();
                tempChart.setLineDash([]);
            }
            
            // Draw axis labels
            tempChart.fillStyle = '#6c757d';
            tempChart.font = '12px Arial';
            tempChart.fillText('74°F', 10, 20);
            tempChart.fillText('72°F', 10, height/2);
            tempChart.fillText('70°F', 10, height - 10);
        }
        
        // Draw energy chart
        function drawEnergyChart() {
            if (!energyChart || energyData.length === 0) return;
            
            const canvas = energyChart.canvas;
            const width = canvas.width;
            const height = canvas.height;
            
            // Clear canvas
            energyChart.clearRect(0, 0, width, height);
            
            // Draw background
            energyChart.fillStyle = '#f8f9fa';
            energyChart.fillRect(0, 0, width, height);
            
            if (energyData.length > 1) {
                const xStep = width / (maxDataPoints - 1);
                const maxPower = 60; // Max power scale
                
                // Power line (orange)
                energyChart.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue('--power-color');
                energyChart.lineWidth = 2;
                energyChart.beginPath();
                
                energyData.forEach((point, i) => {
                    const x = i * xStep;
                    const y = height - (point.power / maxPower * height);
                    if (i === 0) energyChart.moveTo(x, y);
                    else energyChart.lineTo(x, y);
                });
                energyChart.stroke();
                
                // Cooling line (green)
                energyChart.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue('--cooling-color');
                energyChart.lineWidth = 2;
                energyChart.beginPath();
                
                energyData.forEach((point, i) => {
                    const x = i * xStep;
                    const y = height - (point.cooling / (maxPower * 3) * height); // Cooling is ~3x power
                    if (i === 0) energyChart.moveTo(x, y);
                    else energyChart.lineTo(x, y);
                });
                energyChart.stroke();
            }
            
            // Draw axis labels
            energyChart.fillStyle = '#6c757d';
            energyChart.font = '12px Arial';
            energyChart.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--power-color');
            energyChart.fillText('Power', 10, 20);
            energyChart.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--cooling-color');
            energyChart.fillText('Cooling', 10, 35);
        }
        
        // Simulate live data updates
        function updateLiveData() {
            const now = Date.now();
            const t = (now / 1000) % 3600;
            
            // Simulate temperature control with realistic BAS behavior
            const setpoint = 72.0;
            const temp = setpoint + 0.3 * Math.sin(t/120) + 0.1 * Math.random() - 0.05;
            const error = temp - setpoint;
            const cop = 3.0 + 0.5 * Math.sin(t/200);
            
            // PID simulation
            const kp = 3.0, ki = 0.15, kd = 0.8;
            const p_term = kp * error;
            const i_term = Math.sin(t/300) * 2; // Simplified integral
            const d_term = Math.cos(t/180) * 0.5; // Simplified derivative
            
            // CRAC staging
            const lead_pct = Math.min(Math.max(30, 50 + error * 15), 100);
            const lag_on = lead_pct > 75;
            const power = lead_pct * 0.6 + (lag_on ? 15 : 0);
            const cooling = power * cop;
            
            // Update KPI tiles
            const inBand = Math.abs(error) < 0.5 ? 100 : 85 + Math.random() * 10;
            document.getElementById('kpi-temp-band').textContent = inBand.toFixed(1) + '%';
            document.getElementById('kpi-failover').textContent = '12.3s';
            document.getElementById('kpi-cop').textContent = cop.toFixed(2);
            document.getElementById('kpi-alarms').textContent = '0';
            
            // Update equipment metrics
            document.getElementById('lead-output').textContent = lead_pct.toFixed(1) + '%';
            document.getElementById('lead-runtime').textContent = (t/3600).toFixed(1) + 'h';
            document.getElementById('lag-output').textContent = lag_on ? '25.0%' : '0.0%';
            document.getElementById('lag-starts').textContent = lag_on ? '3' : '2';
            
            // Update chart insights
            document.getElementById('temp-insight').textContent = 
                Math.abs(error) < 0.2 ? 'System stable at setpoint.' : 'Minor temperature deviation, correcting.';
            document.getElementById('energy-insight').textContent = 
                cop > 3.0 ? 'Efficiency above Energy Star 2.5 baseline.' : 'Efficiency within normal range.';
            document.getElementById('current-cop').textContent = cop.toFixed(2);
            
            // Update timeline
            document.getElementById('timeline-lead').textContent = (t/3600).toFixed(1) + 'h';
            document.getElementById('timeline-lag').textContent = lag_on ? '0.8h' : '0.0h';
            document.getElementById('timeline-standby').textContent = (t/3600).toFixed(1) + 'h';
            
            // Update engineer mode
            document.getElementById('p-term').textContent = p_term.toFixed(1);
            document.getElementById('i-term').textContent = i_term.toFixed(1);
            document.getElementById('d-term').textContent = d_term.toFixed(1);
            document.getElementById('controller-status').textContent = 
                lead_pct > 95 ? 'High output, approaching saturation' : 'Stable operation, no saturation detected';
            
            // Update time
            const hours = Math.floor(t / 3600);
            const minutes = Math.floor((t % 3600) / 60);
            const seconds = Math.floor(t % 60);
            document.getElementById('sim-time').textContent = 
                hours.toString().padStart(2, '0') + ':' +
                minutes.toString().padStart(2, '0') + ':' +
                seconds.toString().padStart(2, '0');
            
            // Store data for charts
            tempData.push({ temp, setpoint, time: t });
            energyData.push({ power, cooling, cop, time: t });
            
            // Limit data points
            if (tempData.length > maxDataPoints) tempData.shift();
            if (energyData.length > maxDataPoints) energyData.shift();
            
            // Update charts
            drawTemperatureChart();
            drawEnergyChart();
        }
        
        // UI interaction functions
        function scrollToChart(chartId) {
            document.getElementById(chartId).scrollIntoView({ behavior: 'smooth' });
        }
        
        function toggleEngineerMode() {
            const panel = document.getElementById('engineer-panel');
            panel.classList.toggle('open');
        }
        
        // Initialize on load
        window.addEventListener('load', function() {
            initCharts();
            updateLiveData();
            setInterval(updateLiveData, 500);
        });
    </script>
</head>
<body>
    <div class="container">
        <!-- Page Header -->
        <div class="page-header fade-in">
            <h1>System Performance Analysis</h1>
            <p>Data Center Building Automation System - Enterprise Dashboard</p>
        </div>

        <!-- Top KPI Summary Strip -->
        <div class="kpi-strip fade-in">
            <div class="kpi-tile kpi-temp-band" onclick="scrollToChart('temp-chart')">
                <div class="sub">Temperature In-Band</div>
                <h2 id="kpi-temp-band">96.4%</h2>
                <div class="sub">Within ±0.5°F tolerance</div>
            </div>
            <div class="kpi-tile kpi-failover" onclick="scrollToChart('equipment-chart')">
                <div class="sub">Failover Time</div>
                <h2 id="kpi-failover">12.3s</h2>
                <div class="sub">STANDBY → ACTIVE</div>
            </div>
            <div class="kpi-tile kpi-cop" onclick="scrollToChart('energy-chart')">
                <div class="sub">Average COP</div>
                <h2 id="kpi-cop">3.24</h2>
                <div class="sub">Energy efficiency ratio</div>
            </div>
            <div class="kpi-tile kpi-alarms" onclick="scrollToChart('equipment-chart')">
                <div class="sub">Active Alarms</div>
                <h2 id="kpi-alarms">0</h2>
                <div class="sub">All systems normal</div>
            </div>
        </div>

        <!-- 2x2 Chart Grid -->
        <div class="chart-grid fade-in">
            <!-- A1: Zone Temperature vs Setpoint -->
            <div class="chart-card" id="temp-chart">
                <h3>Zone Temperature vs Setpoint</h3>
                <div class="chart-area">
                    <canvas id="temp-canvas" width="800" height="200"></canvas>
                </div>
                <div class="chart-caption">
                    Temperature control within ±0.5°F band. <span id="temp-insight">System stable at setpoint.</span>
                </div>
            </div>
            
            <!-- A2: Equipment Utilization -->
            <div class="chart-card" id="utilization-chart">
                <h3>Equipment Utilization</h3>
                <div class="equipment-grid">
                    <div class="equipment-card lead">
                        <h4>CRAC-01 <span class="role-badge role-lead">LEAD</span></h4>
                        <div class="metric-row">
                            <span>Output:</span>
                            <span class="metric-value" id="lead-output">65.2%</span>
                        </div>
                        <div class="metric-row">
                            <span>Runtime:</span>
                            <span class="metric-value" id="lead-runtime">2.4h</span>
                        </div>
                    </div>
                    <div class="equipment-card lag">
                        <h4>CRAC-02 <span class="role-badge role-lag">LAG</span></h4>
                        <div class="metric-row">
                            <span>Output:</span>
                            <span class="metric-value" id="lag-output">25.0%</span>
                        </div>
                        <div class="metric-row">
                            <span>Starts:</span>
                            <span class="metric-value" id="lag-starts">3</span>
                        </div>
                    </div>
                    <div class="equipment-card standby">
                        <h4>CRAC-03 <span class="role-badge role-standby">STANDBY</span></h4>
                        <div class="metric-row">
                            <span>Status:</span>
                            <span class="metric-value">READY</span>
                        </div>
                        <div class="metric-row">
                            <span>Availability:</span>
                            <span class="metric-value">100%</span>
                        </div>
                    </div>
                </div>
                <div class="chart-caption">
                    <span id="staging-events">2 staging events</span> in current session. N+1 redundancy maintained.
                </div>
            </div>
            
            <!-- B1: Power vs Cooling with COP -->
            <div class="chart-card" id="energy-chart">
                <h3>Power vs Cooling with COP</h3>
                <div class="chart-area">
                    <canvas id="energy-canvas" width="800" height="200"></canvas>
                </div>
                <div class="chart-caption">
                    System COP: <span id="current-cop">3.24</span>. <span id="energy-insight">Efficiency above Energy Star 2.5 baseline.</span>
                </div>
            </div>
            
            <!-- B2: Equipment Timeline -->
            <div class="chart-card" id="timeline-chart">
                <h3>Equipment Timeline</h3>
                <div class="chart-area">
                    <div class="chart-placeholder">
                        <div style="text-align: center;">
                            <div style="font-size: 1.2em; margin-bottom: 10px;">System Timeline</div>
                            <div style="font-size: 0.9em;">
                                <div style="margin: 5px 0;">
                                    <span style="color: var(--cooling-color);">●</span> LEAD Active: <span id="timeline-lead">2.4h</span>
                                </div>
                                <div style="margin: 5px 0;">
                                    <span style="color: var(--setpoint-color);">●</span> LAG Staged: <span id="timeline-lag">0.8h</span>
                                </div>
                                <div style="margin: 5px 0;">
                                    <span style="color: var(--cop-color);">●</span> STANDBY Ready: <span id="timeline-standby">2.4h</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="chart-caption">
                    <span id="timeline-insight">No maintenance windows scheduled. All units operational.</span>
                </div>
            </div>
        </div>

        <!-- Engineer Mode Section -->
        <div class="engineer-mode fade-in">
            <button class="engineer-toggle" onclick="toggleEngineerMode()">
                🔬 Engineer Mode: Advanced Diagnostics
            </button>
            <div class="engineer-panel" id="engineer-panel">
                <h3>PID Controller Analysis</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin: 20px 0;">
                    <div style="text-align: center;">
                        <h4 style="color: var(--alarm-color);">P-Term</h4>
                        <div style="font-size: 1.5em; font-weight: bold;" id="p-term">2.1</div>
                        <div style="font-size: 0.8em; color: #6c757d;">Proportional Response</div>
                    </div>
                    <div style="text-align: center;">
                        <h4 style="color: var(--power-color);">I-Term</h4>
                        <div style="font-size: 1.5em; font-weight: bold;" id="i-term">-0.3</div>
                        <div style="font-size: 0.8em; color: #6c757d;">Integral Accumulation</div>
                    </div>
                    <div style="text-align: center;">
                        <h4 style="color: var(--cooling-color);">D-Term</h4>
                        <div style="font-size: 1.5em; font-weight: bold;" id="d-term">0.1</div>
                        <div style="font-size: 0.8em; color: #6c757d;">Derivative Action</div>
                    </div>
                </div>
                <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                    <strong>Controller Status:</strong> <span id="controller-status">Stable operation, no saturation detected</span>
                </div>
            </div>
        </div>

        <!-- Status Footer -->
        <div style="margin-top: 40px; padding: 20px; text-align: center; background: white; border-radius: var(--card-radius); box-shadow: var(--card-shadow);">
            <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;">
                <div>
                    <strong>Simulation Time:</strong> <span id="sim-time" style="font-family: monospace; color: var(--accent);">00:00:00</span>
                </div>
                <div>
                    <strong>Real-time Factor:</strong> <span style="color: var(--accent);">50×</span>
                </div>
                <div>
                    <strong>System Status:</strong> <span style="color: var(--cooling-color);">OPERATIONAL</span>
                </div>
                <div style="margin-top: 10px;">
                    <a href="/red" style="margin: 0 10px; color: var(--accent); text-decoration: none;">🔧 Flow Editor</a>
                    <a href="/" style="margin: 0 10px; color: var(--accent); text-decoration: none;">🏠 Home</a>
                    <a href="https://github.com/miikeyanderson/data-center-bas-sim-main" style="margin: 0 10px; color: var(--accent); text-decoration: none;">📁 Source</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    `);
});


// Copy production flows to demo flows
const productionFlowsPath = path.join(__dirname, 'hmi', 'production-node-red-flows.json');
const demoFlowsPath = path.join(__dirname, '.node-red', 'demo-flows.json');

// Ensure .node-red directory exists
const nodeRedDir = path.join(__dirname, '.node-red');
if (!fs.existsSync(nodeRedDir)) {
    fs.mkdirSync(nodeRedDir, { recursive: true });
}

// Copy flows if production flows exist
if (fs.existsSync(productionFlowsPath)) {
    try {
        fs.copyFileSync(productionFlowsPath, demoFlowsPath);
        console.log('✅ Production Node-RED flows loaded for demo');
    } catch (error) {
        console.log('⚠️ Could not copy production flows, using default');
    }
}

// Start the server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`
🏢 Data Center BAS Control System Demo Server
🚀 Server running on port ${PORT}
🎛️ Dashboard: http://localhost:${PORT}/ui
⚙️  Flow Editor: http://localhost:${PORT}/red
📊 Demo Home: http://localhost:${PORT}
    `);
    
    // Start Node-RED
    RED.start().catch(error => {
        console.error('Failed to start Node-RED:', error);
    });
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down BAS Demo Server...');
    RED.stop().then(() => {
        process.exit(0);
    });
});