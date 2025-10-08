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
        
        /* Fan Spin Animation */
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
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
    <!-- Tailwind CSS CDN for ShadCN UI compatibility -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Recharts for ShadCN UI Charts -->
    <script src="https://unpkg.com/recharts@2.8.0/esm/index.js" type="module"></script>
    <!-- React for Recharts -->
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <!-- Configure Tailwind for ShadCN UI theme -->
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        border: "hsl(var(--border))",
                        input: "hsl(var(--input))",
                        ring: "hsl(var(--ring))",
                        background: "hsl(var(--background))",
                        foreground: "hsl(var(--foreground))",
                        primary: {
                            DEFAULT: "hsl(var(--primary))",
                            foreground: "hsl(var(--primary-foreground))",
                        },
                        secondary: {
                            DEFAULT: "hsl(var(--secondary))",
                            foreground: "hsl(var(--secondary-foreground))",
                        },
                        destructive: {
                            DEFAULT: "hsl(var(--destructive))",
                            foreground: "hsl(var(--destructive-foreground))",
                        },
                        muted: {
                            DEFAULT: "hsl(var(--muted))",
                            foreground: "hsl(var(--muted-foreground))",
                        },
                        accent: {
                            DEFAULT: "hsl(var(--accent))",
                            foreground: "hsl(var(--accent-foreground))",
                        },
                        popover: {
                            DEFAULT: "hsl(var(--popover))",
                            foreground: "hsl(var(--popover-foreground))",
                        },
                        card: {
                            DEFAULT: "hsl(var(--card))",
                            foreground: "hsl(var(--card-foreground))",
                        },
                    },
                    borderRadius: {
                        lg: "var(--radius)",
                        md: "calc(var(--radius) - 2px)",
                        sm: "calc(var(--radius) - 4px)",
                    },
                }
            }
        }
    </script>
    <style>
        /* ShadCN UI CSS Variables */
        :root {
            --background: 0 0% 100%;
            --foreground: 222.2 84% 4.9%;
            --card: 0 0% 100%;
            --card-foreground: 222.2 84% 4.9%;
            --popover: 0 0% 100%;
            --popover-foreground: 222.2 84% 4.9%;
            --primary: 221.2 83.2% 53.3%;
            --primary-foreground: 210 40% 98%;
            --secondary: 210 40% 96%;
            --secondary-foreground: 222.2 84% 4.9%;
            --muted: 210 40% 96%;
            --muted-foreground: 215.4 16.3% 46.9%;
            --accent: 210 40% 96%;
            --accent-foreground: 222.2 84% 4.9%;
            --destructive: 0 84.2% 60.2%;
            --destructive-foreground: 210 40% 98%;
            --border: 214.3 31.8% 91.4%;
            --input: 214.3 31.8% 91.4%;
            --ring: 221.2 83.2% 53.3%;
            --radius: 0.5rem;
            
            /* BAS specific colors */
            --temp-color: 271 81% 56%;      /* Purple for temperature */
            --setpoint-color: 221.2 83.2% 53.3%;  /* Blue for setpoint */
            --power-color: 25 95% 53%;      /* Orange for power */
            --cooling-color: 142 76% 36%;   /* Green for cooling */
            --cop-color: 215 16% 47%;       /* Grey for COP */
            --alarm-color: 0 84% 60%;       /* Red for alarms */
        }
        
        .dark {
            --background: 222.2 84% 4.9%;
            --foreground: 210 40% 98%;
            --card: 222.2 84% 4.9%;
            --card-foreground: 210 40% 98%;
            --popover: 222.2 84% 4.9%;
            --popover-foreground: 210 40% 98%;
            --primary: 217.2 91.2% 59.8%;
            --primary-foreground: 222.2 84% 4.9%;
            --secondary: 217.2 32.6% 17.5%;
            --secondary-foreground: 210 40% 98%;
            --muted: 217.2 32.6% 17.5%;
            --muted-foreground: 215 20.2% 65.1%;
            --accent: 217.2 32.6% 17.5%;
            --accent-foreground: 210 40% 98%;
            --destructive: 0 62.8% 30.6%;
            --destructive-foreground: 210 40% 98%;
            --border: 217.2 32.6% 17.5%;
            --input: 217.2 32.6% 17.5%;
            --ring: 224.3 76.3% 94.1%;
        }
        
        * {
            border-color: hsl(var(--border));
        }
        
        body {
            background-color: hsl(var(--background));
            color: hsl(var(--foreground));
        }
        
        /* Chart canvas styling */
        .chart-canvas {
            background: hsl(var(--muted));
            border-radius: calc(var(--radius) - 2px);
        }
        
        /* Chart-specific CSS variables for ShadCN */
        :root {
            --chart-1: 220 70% 50%;
            --chart-2: 160 60% 45%;
            --chart-3: 30 80% 55%;
            --chart-4: 280 65% 60%;
            --chart-5: 340 75% 55%;
        }
        
        /* Sparkline container styling */
        .sparkline-container {
            height: 40px;
            width: 100%;
            margin-top: 4px;
        }
        
        /* Custom BAS color classes */
        .text-temp { color: hsl(var(--temp-color)); }
        .text-setpoint { color: hsl(var(--setpoint-color)); }
        .text-power { color: hsl(var(--power-color)); }
        .text-cooling { color: hsl(var(--cooling-color)); }
        .text-cop { color: hsl(var(--cop-color)); }
        .text-alarm { color: hsl(var(--alarm-color)); }
        
        .bg-temp { background-color: hsl(var(--temp-color)); }
        .bg-setpoint { background-color: hsl(var(--setpoint-color)); }
        .bg-power { background-color: hsl(var(--power-color)); }
        .bg-cooling { background-color: hsl(var(--cooling-color)); }
        .bg-cop { background-color: hsl(var(--cop-color)); }
        .bg-alarm { background-color: hsl(var(--alarm-color)); }
        
        .border-l-temp { border-left-color: hsl(var(--temp-color)); }
        .border-l-setpoint { border-left-color: hsl(var(--setpoint-color)); }
        .border-l-cooling { border-left-color: hsl(var(--cooling-color)); }
        .border-l-cop { border-left-color: hsl(var(--cop-color)); }
    </style>
    <script>
        // Enhanced data storage for professional SCADA charts
        let tempData = [];
        let energyData = [];
        let cracOutputData = [];
        let kpiHistoryData = [];
        
        // Chart configuration and state
        let maxDataPoints = 1440; // 24 hours at 1-minute intervals
        let currentTimeRange = '1h'; // 15min, 1h, 4h, 24h, 7d
        let isRealTimeMode = true;
        
        // Chart configurations for ShadCN/Recharts
        const tempChartConfig = {
            temperature: {
                label: "Zone Temp",
                color: "hsl(var(--chart-1))"
            },
            setpoint: {
                label: "Setpoint",
                color: "hsl(var(--chart-2))"
            },
            tolerance_high: {
                label: "High Limit",
                color: "hsl(var(--chart-3))"
            },
            tolerance_low: {
                label: "Low Limit", 
                color: "hsl(var(--chart-3))"
            }
        };
        
        const energyChartConfig = {
            power: {
                label: "Power (kW)",
                color: "hsl(var(--chart-4))"
            },
            cooling: {
                label: "Cooling (kW)",
                color: "hsl(var(--chart-5))"
            },
            cop: {
                label: "COP",
                color: "hsl(var(--chart-1))"
            }
        };
        
        // Time range selection functions
        function setTimeRange(range) {
            currentTimeRange = range;
            updateTimeRangeButtons();
            updateChartTimeRange();
        }
        
        function updateTimeRangeButtons() {
            document.querySelectorAll('.time-range-btn').forEach(btn => {
                btn.classList.remove('bg-primary', 'text-primary-foreground');
                btn.classList.add('bg-muted', 'text-muted-foreground');
            });
            
            const activeBtn = document.querySelector('[data-range="' + currentTimeRange + '"]');
            if (activeBtn) {
                activeBtn.classList.remove('bg-muted', 'text-muted-foreground');
                activeBtn.classList.add('bg-primary', 'text-primary-foreground');
            }
        }
        
        function updateChartTimeRange() {
            // Filter data based on time range
            const now = Date.now() / 1000;
            const ranges = {
                '15min': 15 * 60,
                '1h': 60 * 60,
                '4h': 4 * 60 * 60,
                '24h': 24 * 60 * 60,
                '7d': 7 * 24 * 60 * 60
            };
            
            const timeLimit = now - ranges[currentTimeRange];
            
            // Update chart data based on time range
            renderCharts();
        }
        
        // Data export functions
        function exportToCSV(chartType) {
            let data, filename;
            const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
            
            if (chartType === 'temperature') {
                data = tempData;
                filename = 'temperature_data_' + timestamp + '.csv';
            } else if (chartType === 'energy') {
                data = energyData;
                filename = 'energy_data_' + timestamp + '.csv';
            }
            
            if (!data || data.length === 0) return;
            
            // Create CSV content
            const headers = Object.keys(data[0]).join(',');
            const rows = data.map(row => Object.values(row).join(','));
            const csvContent = [headers, ...rows].join('\n');
            
            // Download file
            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            window.URL.revokeObjectURL(url);
        }
        
        // Enhanced chart rendering system using vanilla JS (ShadCN-inspired)
        function renderCharts() {
            renderTemperatureChart();
            renderEnergyChart();
            renderSparklines();
        }
        
        // Generate SVG-based temperature chart
        function renderTemperatureChart() {
            const container = document.getElementById('temp-chart-container');
            if (!container || tempData.length === 0) return;
            
            const filteredData = getFilteredData(tempData);
            const svgContent = generateTemperatureChartSVG(filteredData);
            container.innerHTML = svgContent;
        }
        
        // Generate SVG-based energy chart
        function renderEnergyChart() {
            const container = document.getElementById('energy-chart-container');
            if (!container || energyData.length === 0) return;
            
            const filteredData = getFilteredData(energyData);
            const svgContent = generateEnergyChartSVG(filteredData);
            container.innerHTML = svgContent;
        }
        
        // Generate sparklines for KPI cards
        function renderSparklines() {
            if (kpiHistoryData.length < 5) return;
            
            const sparklineData = kpiHistoryData.slice(-20);
            
            // Temperature band compliance sparkline
            const tempSparkline = document.getElementById('temp-sparkline');
            if (tempSparkline) {
                const complianceData = sparklineData.map(d => ({
                    time: d.time,
                    value: d.temperature_compliance
                }));
                tempSparkline.innerHTML = generateSparklineSVG(complianceData, '#10b981');
            }
            
            // COP efficiency sparkline
            const copSparkline = document.getElementById('cop-sparkline');
            if (copSparkline) {
                const copData = sparklineData.map(d => ({
                    time: d.time,
                    value: d.cop_efficiency
                }));
                copSparkline.innerHTML = generateSparklineSVG(copData, '#3b82f6');
            }
            
            // Failover time sparkline (simulated stable performance)
            const failoverSparkline = document.getElementById('failover-sparkline');
            if (failoverSparkline) {
                const failoverData = sparklineData.map(d => ({
                    time: d.time,
                    value: d.failover_time + (Math.random() - 0.5) * 2 // 10.3-14.3s range
                }));
                failoverSparkline.innerHTML = generateSparklineSVG(failoverData, '#f59e0b');
            }
            
            // Alarms sparkline (mostly zero with occasional spikes)
            const alarmsSparkline = document.getElementById('alarms-sparkline');
            if (alarmsSparkline) {
                const alarmsData = sparklineData.map(d => ({
                    time: d.time,
                    value: d.active_alarms
                }));
                alarmsSparkline.innerHTML = generateSparklineSVG(alarmsData, '#ef4444');
            }
        }
        
        // Filter data based on current time range
        function getFilteredData(data) {
            if (!data || data.length === 0) return [];
            
            const ranges = {
                '15min': 15,
                '1h': 60,
                '4h': 240, 
                '24h': 1440,
                '7d': 10080
            };
            
            const maxPoints = ranges[currentTimeRange] || 60;
            return data.slice(-maxPoints);
        }
        
        // Generate SVG for temperature chart
        function generateTemperatureChartSVG(data) {
            if (!data || data.length === 0) {
                return '<div class="flex items-center justify-center h-48 text-muted-foreground">No data available</div>';
            }
            
            const width = 800;
            const height = 192;
            const margin = { top: 20, right: 30, bottom: 30, left: 50 };
            const chartWidth = width - margin.left - margin.right;
            const chartHeight = height - margin.top - margin.bottom;
            
            // Calculate scales
            const setpoint = 72.0;
            const temps = data.map(d => d.temp);
            const minTemp = Math.min(...temps, setpoint - 1);
            const maxTemp = Math.max(...temps, setpoint + 1);
            const tempRange = Math.max(2.0, maxTemp - minTemp + 0.5);
            
            const xScale = data.length > 1 ? chartWidth / (data.length - 1) : chartWidth / 2;
            const yScale = chartHeight / tempRange;
            
            // Generate path for temperature line
            const tempPath = data.map((d, i) => {
                const x = data.length === 1 ? margin.left + chartWidth / 2 : margin.left + (i * xScale);
                const y = margin.top + chartHeight - ((d.temp - minTemp) * yScale);
                return i === 0 ? 'M ' + x + ' ' + y : 'L ' + x + ' ' + y;
            }).join(' ');
            
            // Generate path for setpoint line
            const setpointY = margin.top + chartHeight - ((setpoint - minTemp) * yScale);
            const setpointPath = 'M ' + margin.left + ' ' + setpointY + ' L ' + (margin.left + chartWidth) + ' ' + setpointY;
            
            // Generate tolerance band
            const toleranceTop = margin.top + chartHeight - ((setpoint + 0.5 - minTemp) * yScale);
            const toleranceBottom = margin.top + chartHeight - ((setpoint - 0.5 - minTemp) * yScale);
            const tolerancePath = 'M ' + margin.left + ' ' + toleranceTop + ' L ' + (margin.left + chartWidth) + ' ' + toleranceTop + ' L ' + (margin.left + chartWidth) + ' ' + toleranceBottom + ' L ' + margin.left + ' ' + toleranceBottom + ' Z';
            
            // Generate current value indicator
            let currentValueIndicator = '';
            if (data.length > 0) {
                const lastX = data.length === 1 ? margin.left + chartWidth / 2 : margin.left + ((data.length - 1) * xScale);
                const lastY = margin.top + chartHeight - ((data[data.length - 1].temp - minTemp) * yScale);
                currentValueIndicator = '<circle cx="' + lastX + '" cy="' + lastY + '" r="4" fill="hsl(var(--chart-1))" stroke="white" stroke-width="2" />';
            }
            
            const svg = [
                '<svg width="100%" height="100%" viewBox="0 0 ' + width + ' ' + height + '" class="w-full h-full">',
                '  <!-- Background -->',
                '  <rect width="' + width + '" height="' + height + '" fill="hsl(var(--muted))" rx="6" />',
                '  <!-- Grid lines -->',
                '  <defs>',
                '    <pattern id="grid" width="40" height="24" patternUnits="userSpaceOnUse">',
                '      <path d="M 40 0 L 0 0 0 24" fill="none" stroke="hsl(var(--border))" stroke-width="0.5" opacity="0.3"/>',
                '    </pattern>',
                '  </defs>',
                '  <rect x="' + margin.left + '" y="' + margin.top + '" width="' + chartWidth + '" height="' + chartHeight + '" fill="url(#grid)" />',
                '  <!-- Tolerance band -->',
                '  <path d="' + tolerancePath + '" fill="hsl(var(--chart-2))" opacity="0.1" />',
                '  <!-- Setpoint line -->',
                '  <path d="' + setpointPath + '" stroke="hsl(var(--chart-2))" stroke-width="2" stroke-dasharray="5,5" fill="none" />',
                '  <!-- Temperature line -->',
                '  <path d="' + tempPath + '" stroke="hsl(var(--chart-1))" stroke-width="3" fill="none" />',
                '  <!-- Y-axis labels -->',
                '  <text x="10" y="' + (margin.top + 5) + '" fill="hsl(var(--muted-foreground))" font-size="12">' + maxTemp.toFixed(1) + '°F</text>',
                '  <text x="10" y="' + (setpointY + 5) + '" fill="hsl(var(--muted-foreground))" font-size="12">' + setpoint.toFixed(1) + '°F</text>',
                '  <text x="10" y="' + (margin.top + chartHeight - 5) + '" fill="hsl(var(--muted-foreground))" font-size="12">' + minTemp.toFixed(1) + '°F</text>',
                '  <!-- Current value indicator -->',
                '  ' + currentValueIndicator,
                '</svg>'
            ].join('\n');
            
            return svg;
        }
        
        // Generate SVG for energy chart
        function generateEnergyChartSVG(data) {
            if (!data || data.length === 0) {
                return '<div class="flex items-center justify-center h-48 text-muted-foreground">No data available</div>';
            }
            
            const width = 800;
            const height = 192;
            const margin = { top: 20, right: 30, bottom: 30, left: 50 };
            const chartWidth = width - margin.left - margin.right;
            const chartHeight = height - margin.top - margin.bottom;
            
            // Calculate scales
            const powers = data.map(d => d.power);
            const coolings = data.map(d => d.cooling);
            const maxPower = Math.max(...powers) * 1.1;
            const maxCooling = Math.max(...coolings) * 1.1;
            const maxValue = Math.max(maxPower, maxCooling);
            
            const xScale = data.length > 1 ? chartWidth / (data.length - 1) : chartWidth / 2;
            const yScale = chartHeight / maxValue;
            
            // Generate path for power line
            const powerPath = data.map((d, i) => {
                const x = data.length === 1 ? margin.left + chartWidth / 2 : margin.left + (i * xScale);
                const y = margin.top + chartHeight - (d.power * yScale);
                return i === 0 ? 'M ' + x + ' ' + y : 'L ' + x + ' ' + y;
            }).join(' ');
            
            // Generate path for cooling line
            const coolingPath = data.map((d, i) => {
                const x = data.length === 1 ? margin.left + chartWidth / 2 : margin.left + (i * xScale);
                const y = margin.top + chartHeight - (d.cooling * yScale);
                return i === 0 ? 'M ' + x + ' ' + y : 'L ' + x + ' ' + y;
            }).join(' ');
            
            // Generate current value indicators
            let currentValueIndicators = '';
            if (data.length > 0) {
                const lastX = data.length === 1 ? margin.left + chartWidth / 2 : margin.left + ((data.length - 1) * xScale);
                const powerY = margin.top + chartHeight - (data[data.length - 1].power * yScale);
                const coolingY = margin.top + chartHeight - (data[data.length - 1].cooling * yScale);
                currentValueIndicators = 
                    '<circle cx="' + lastX + '" cy="' + powerY + '" r="4" fill="hsl(var(--chart-4))" stroke="white" stroke-width="2" />' +
                    '<circle cx="' + lastX + '" cy="' + coolingY + '" r="4" fill="hsl(var(--chart-5))" stroke="white" stroke-width="2" />';
            }
            
            const svg = [
                '<svg width="100%" height="100%" viewBox="0 0 ' + width + ' ' + height + '" class="w-full h-full">',
                '  <!-- Background -->',
                '  <rect width="' + width + '" height="' + height + '" fill="hsl(var(--muted))" rx="6" />',
                '  <!-- Grid lines -->',
                '  <rect x="' + margin.left + '" y="' + margin.top + '" width="' + chartWidth + '" height="' + chartHeight + '" fill="url(#grid)" />',
                '  <!-- Power line -->',
                '  <path d="' + powerPath + '" stroke="hsl(var(--chart-4))" stroke-width="3" fill="none" />',
                '  <!-- Cooling line -->',
                '  <path d="' + coolingPath + '" stroke="hsl(var(--chart-5))" stroke-width="3" fill="none" />',
                '  <!-- Y-axis labels -->',
                '  <text x="10" y="' + (margin.top + 5) + '" fill="hsl(var(--chart-4))" font-size="12">Power: ' + maxPower.toFixed(0) + 'kW</text>',
                '  <text x="10" y="' + (margin.top + 20) + '" fill="hsl(var(--chart-5))" font-size="12">Cooling: ' + maxCooling.toFixed(0) + 'kW</text>',
                '  <!-- Current value indicators -->',
                '  ' + currentValueIndicators,
                '</svg>'
            ].join('\n');
            
            return svg;
        }
        
        // Generate sparkline SVG
        function generateSparklineSVG(data, color) {
            if (!data || data.length < 2) return '';
            
            const width = 120;
            const height = 40;
            const margin = 2;
            
            const values = data.map(d => d.value);
            const minValue = Math.min(...values);
            const maxValue = Math.max(...values);
            const range = Math.max(maxValue - minValue, 1);
            
            const xScale = (width - 2 * margin) / (data.length - 1);
            const yScale = (height - 2 * margin) / range;
            
            const path = data.map((d, i) => {
                const x = margin + (i * xScale);
                const y = margin + (height - 2 * margin) - ((d.value - minValue) * yScale);
                return i === 0 ? 'M ' + x + ' ' + y : 'L ' + x + ' ' + y;
            }).join(' ');
            
            const lastX = margin + ((data.length - 1) * xScale);
            const lastY = margin + (height - 2 * margin) - ((data[data.length - 1].value - minValue) * yScale);
            
            const svg = [
                '<svg width="' + width + '" height="' + height + '" viewBox="0 0 ' + width + ' ' + height + '">',
                '  <path d="' + path + '" stroke="' + color + '" stroke-width="2" fill="none" />',
                '  <circle cx="' + lastX + '" cy="' + lastY + '" r="2" fill="' + color + '" />',
                '</svg>'
            ].join('\n');
            
            return svg;
        }
        
        // Update fan animations and RPM displays
        function updateFanAnimations(leadPct, lagOn) {
            // Calculate RPM for each CRAC based on output percentage
            const crac01Rpm = Math.round((leadPct / 100) * 1500 + 200); // 200-1700 RPM range
            const crac02Rpm = lagOn ? Math.round(800 + Math.random() * 200) : 0; // 800-1000 RPM when on
            const crac03Rpm = 0; // Standby unit
            
            // Calculate valve positions (cooling coil damper positions)
            const crac01ValvePct = leadPct;
            const crac02ValvePct = lagOn ? Math.round(25 + Math.random() * 30) : 0; // 25-55% when on
            const crac03ValvePct = 0; // Standby
            
            // Update RPM displays
            const rpm01 = document.getElementById('crac-01-rpm');
            const rpm02 = document.getElementById('crac-02-rpm');
            const rpm03 = document.getElementById('crac-03-rpm');
            
            if (rpm01) rpm01.textContent = crac01Rpm;
            if (rpm02) rpm02.textContent = crac02Rpm;
            if (rpm03) rpm03.textContent = crac03Rpm;
            
            // Update valve position displays and animations
            updateValvePositions(crac01ValvePct, crac02ValvePct, crac03ValvePct);
            
            // Calculate rotation speeds (degrees per second)
            const crac01Speed = (crac01Rpm / 60) * 360; // RPM to degrees per second
            const crac02Speed = (crac02Rpm / 60) * 360;
            const crac03Speed = 0;
            
            // Apply rotation animations to fan blades
            animateFanBlades('crac-01-blades', crac01Speed);
            animateFanBlades('crac-02-blades', crac02Speed);
            animateFanBlades('crac-03-blades', crac03Speed);
        }
        
        // Animate fan blades with CSS transforms
        function animateFanBlades(bladeId, degreesPerSecond) {
            const fanBlades = document.getElementById(bladeId);
            if (!fanBlades) return;
            
            if (degreesPerSecond > 0) {
                const rotationDuration = 360 / degreesPerSecond; // seconds for full rotation
                fanBlades.style.animation = 'spin ' + rotationDuration.toFixed(2) + 's linear infinite';
            } else {
                fanBlades.style.animation = 'none';
            }
        }
        
        // Update valve positions and animations
        function updateValvePositions(crac01Pct, crac02Pct, crac03Pct) {
            // Update CRAC-01 valve
            updateValveIndicator('crac-01-valve-pos', 'crac-01-valve-pct', crac01Pct, 30);
            
            // Update CRAC-02 valve
            updateValveIndicator('crac-02-valve-pos', 'crac-02-valve-pct', crac02Pct, 20);
            
            // Update CRAC-03 valve
            updateValveIndicator('crac-03-valve-pos', 'crac-03-valve-pct', crac03Pct, 30);
        }
        
        // Update individual valve indicator
        function updateValveIndicator(valvePosId, valvePctId, percentage, maxHeight) {
            const valvePos = document.getElementById(valvePosId);
            const valvePct = document.getElementById(valvePctId);
            
            if (valvePos) {
                const height = (percentage / 100) * maxHeight;
                const yPosition = valvePos.getAttribute('y').replace(/\d+/, function(match) {
                    return parseInt(match) + maxHeight - height;
                });
                
                // Clear existing animations
                valvePos.innerHTML = '';
                
                // Set new height and position
                valvePos.setAttribute('height', height);
                valvePos.setAttribute('y', yPosition);
                
                // Add subtle animation for active valves
                if (percentage > 0) {
                    const animate1 = document.createElementNS('http://www.w3.org/2000/svg', 'animate');
                    animate1.setAttribute('attributeName', 'opacity');
                    animate1.setAttribute('values', '0.7;1;0.7');
                    animate1.setAttribute('dur', '2s');
                    animate1.setAttribute('repeatCount', 'indefinite');
                    valvePos.appendChild(animate1);
                }
            }
            
            if (valvePct) {
                valvePct.textContent = percentage + '%';
            }
        }
        
        // Update floorplan with real-time data
        function updateFloorplan(zoneTemp, setpoint, leadPct, lagOn, power, cooling, cop) {
            // Generate individual rack temperatures with realistic variation
            const baseTemp = zoneTemp;
            const rackTemps = [];
            
            // Simulate temperature distribution across racks
            for (let i = 1; i <= 11; i++) {
                // Add positional variation (edge racks run slightly warmer)
                const positionFactor = (i === 1 || i === 11) ? 0.5 : 0;
                // Add load variation (some racks have higher IT load)
                const loadFactor = (i === 4 || i === 9) ? 0.3 : 0;
                // Add random variation
                const randomFactor = (Math.random() - 0.5) * 0.6;
                
                const rackTemp = baseTemp + positionFactor + loadFactor + randomFactor;
                rackTemps.push(rackTemp);
            }
            
            // Update rack temperature sensors
            rackTemps.forEach((temp, index) => {
                const rackId = 'A' + (index + 1);
                const tempSensor = document.querySelector('.temp-sensor[data-temp]');
                
                // Find the specific rack's sensor
                const rack = document.querySelector('[data-rack="' + rackId + '"]');
                if (rack) {
                    const sensor = rack.parentNode.querySelector('.temp-sensor');
                    const tempText = rack.parentNode.querySelector('text:last-child');
                    
                    if (sensor && tempText) {
                        // Update temperature value
                        sensor.setAttribute('data-temp', temp.toFixed(1));
                        tempText.textContent = Math.round(temp) + '°';
                        
                        // Update sensor color based on temperature
                        if (temp >= 75) {
                            sensor.setAttribute('fill', '#ef4444'); // Red - Critical
                        } else if (temp >= 73) {
                            sensor.setAttribute('fill', '#f59e0b'); // Amber - Warning
                        } else {
                            sensor.setAttribute('fill', '#10b981'); // Green - Normal
                        }
                    }
                }
            });
            
            // Update CRAC unit status
            const crac01 = document.getElementById('crac-01');
            const crac02 = document.getElementById('crac-02');
            const crac03 = document.getElementById('crac-03');
            
            // CRAC-01 (LEAD) - Always running
            if (crac01) {
                crac01.querySelector('rect').setAttribute('fill', '#27ae60'); // Green
                crac01.querySelector('.status-indicator').setAttribute('fill', '#a3f7a3');
            }
            
            // CRAC-02 (LAG) - Based on staging
            if (crac02) {
                if (lagOn) {
                    crac02.querySelector('rect').setAttribute('fill', '#3498db'); // Blue - Active
                    crac02.querySelector('.status-indicator').setAttribute('fill', '#5dade2');
                } else {
                    crac02.querySelector('rect').setAttribute('fill', '#7f8c8d'); // Gray - Standby
                    crac02.querySelector('.status-indicator').setAttribute('fill', '#bdc3c7');
                }
            }
            
            // CRAC-03 (STANDBY) - Always ready
            if (crac03) {
                crac03.querySelector('rect').setAttribute('fill', '#95a5a6'); // Gray
                crac03.querySelector('.status-indicator').setAttribute('fill', '#bdc3c7');
            }
            
            // Note: Fan animations removed for simple layout
            
            // Update floorplan summary metrics
            const avgTemp = rackTemps.reduce((sum, temp) => sum + temp, 0) / rackTemps.length;
            const totalAirflow = 8000 + (lagOn ? 8000 : 0); // CFM per CRAC
            const loadUtilization = ((power / 50) * 100); // Percentage of total capacity
            
            const avgTempElement = document.getElementById('floorplan-avg-temp');
            const airflowElement = document.getElementById('floorplan-airflow');
            const loadElement = document.getElementById('floorplan-load');
            
            if (avgTempElement) avgTempElement.textContent = avgTemp.toFixed(1) + '°F';
            if (airflowElement) airflowElement.textContent = totalAirflow.toLocaleString() + ' CFM';
            if (loadElement) loadElement.textContent = loadUtilization.toFixed(0) + '%';
            
            // Update system status
            const statusElement = document.getElementById('floorplan-status');
            if (statusElement) {
                const criticalRacks = rackTemps.filter(temp => temp >= 75).length;
                const warningRacks = rackTemps.filter(temp => temp >= 73 && temp < 75).length;
                
                if (criticalRacks > 0) {
                    statusElement.textContent = 'Critical: ' + criticalRacks + ' rack(s) >75°F - Check cooling distribution';
                    statusElement.className = 'text-xs fill-alarm font-medium';
                } else if (warningRacks > 0) {
                    statusElement.textContent = 'Warning: ' + warningRacks + ' rack(s) >73°F - Monitor temperature trends';
                    statusElement.className = 'text-xs fill-power font-medium';
                } else {
                    statusElement.textContent = 'Normal Operation - All Equipment Online';
                    statusElement.className = 'text-xs fill-cooling font-medium';
                }
            }
        }
        
        // Add interactive click handlers for floorplan
        function initFloorplanInteractivity() {
            // Add click handlers for racks
            document.querySelectorAll('.rack').forEach(rack => {
                rack.style.cursor = 'pointer';
                rack.addEventListener('click', function() {
                    const rackId = this.getAttribute('data-rack');
                    const temp = this.getAttribute('data-temp');
                    alert('Rack ' + rackId + '\\nInlet Temperature: ' + temp + '°F\\nStatus: Normal\\nIT Load: 4.2 kW');
                });
            });
            
            // Add click handlers for CRAC units
            document.querySelectorAll('.crac-unit').forEach(crac => {
                crac.style.cursor = 'pointer';
                crac.addEventListener('click', function() {
                    const cracId = this.getAttribute('data-crac');
                    const role = this.querySelector('text:nth-child(4)').textContent;
                    alert(cracId + '\\nRole: ' + role + '\\nStatus: Running\\nOutput: 65%\\nSupply Temp: 55°F');
                });
            });
        }
        
        // Dynamic insight generation functions
        function generateTemperatureInsight(error, temp, setpoint, lead_pct, lag_on) {
            const absError = Math.abs(error);
            const currentTime = new Date().toLocaleTimeString();
            
            if (absError < 0.1) {
                return 'Temperature control within ±0.1°F band. Excellent stability. Updated: ' + currentTime;
            } else if (absError < 0.3) {
                return 'Temperature control within ±0.5°F band. Current: ' + temp.toFixed(1) + '°F. Updated: ' + currentTime;
            } else if (absError < 0.7) {
                return error > 0 ? 
                    'Zone running ' + error.toFixed(1) + '°F above setpoint. CRAC response at ' + lead_pct.toFixed(0) + '%. Updated: ' + currentTime :
                    'Zone running ' + Math.abs(error).toFixed(1) + '°F below setpoint. Reducing cooling output. Updated: ' + currentTime;
            } else {
                return error > 0 ?
                    'HIGH DEVIATION: +' + error.toFixed(1) + '°F above setpoint. ' + (lag_on ? 'Lag unit staging.' : 'Increasing lead output.') + ' Updated: ' + currentTime :
                    'Temperature significantly below setpoint. Minimum cooling engaged. Updated: ' + currentTime;
            }
        }
        
        function generateEnergyInsight(cop, power, cooling, lead_pct) {
            const currentTime = new Date().toLocaleTimeString();
            
            if (cop > 3.2) {
                return 'System COP: ' + cop.toFixed(2) + '. Efficiency above baseline (' + (((cop - 2.5) / 2.5) * 100).toFixed(0) + '% better). Updated: ' + currentTime;
            } else if (cop > 2.8) {
                return 'System COP: ' + cop.toFixed(2) + '. Efficiency within normal range. Power: ' + power.toFixed(1) + 'kW. Updated: ' + currentTime;
            } else if (cop > 2.3) {
                return 'System COP: ' + cop.toFixed(2) + '. Below optimal efficiency. Consider maintenance check. Updated: ' + currentTime;
            } else {
                return 'LOW EFFICIENCY: COP ' + cop.toFixed(2) + '. Immediate maintenance required. Power: ' + power.toFixed(1) + 'kW. Updated: ' + currentTime;
            }
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
            
            // Enhanced airflow and valve position parameters for backend
            const airflowData = {
                crac01: {
                    cfm: 8000 * (lead_pct / 100),
                    velocity_fpm: 450 + (lead_pct / 100) * 350, // 450-800 FPM
                    static_pressure_iwc: 0.5 + (lead_pct / 100) * 0.3, // 0.5-0.8 inches WC
                    differential_pressure_iwc: 0.1 + (lead_pct / 100) * 0.15, // Across filters
                    fan_power_kw: 1.2 + (lead_pct / 100) * 3.8, // 1.2-5.0 kW
                    valve_position_pct: lead_pct,
                    coil_leaving_temp_f: 55 + (1 - lead_pct / 100) * 5, // 50-60°F
                    coil_entering_temp_f: temp + 5 // Return air + heat pickup
                },
                crac02: {
                    cfm: lag_on ? 8000 * 0.4 : 0, // 40% when staging
                    velocity_fpm: lag_on ? 580 : 0,
                    static_pressure_iwc: lag_on ? 0.65 : 0,
                    differential_pressure_iwc: lag_on ? 0.18 : 0,
                    fan_power_kw: lag_on ? 3.2 : 0.1, // Standby power
                    valve_position_pct: lag_on ? 40 : 0,
                    coil_leaving_temp_f: lag_on ? 57 : temp,
                    coil_entering_temp_f: lag_on ? temp + 4 : temp
                },
                crac03: {
                    cfm: 0, // Standby
                    velocity_fpm: 0,
                    static_pressure_iwc: 0,
                    differential_pressure_iwc: 0,
                    fan_power_kw: 0.1, // Standby power only
                    valve_position_pct: 0,
                    coil_leaving_temp_f: temp, // Ambient
                    coil_entering_temp_f: temp
                },
                total: {
                    cfm: 8000 * (lead_pct / 100) + (lag_on ? 3200 : 0),
                    air_changes_per_hour: (8000 * (lead_pct / 100) + (lag_on ? 3200 : 0)) / 833, // Assuming 50,000 ft³ room
                    mixed_air_temp_f: temp + 2, // Return air temperature
                    supply_air_temp_f: 55 + Math.random() * 3 // 55-58°F range
                }
            };
            
            // Store airflow data for potential API access or logging
            window.currentAirflowData = airflowData;
            
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
            
            // Generate dynamic, contextual chart insights
            const tempInsight = generateTemperatureInsight(error, temp, setpoint, lead_pct, lag_on);
            const energyInsight = generateEnergyInsight(cop, power, cooling, lead_pct);
            
            document.getElementById('temp-insight').textContent = tempInsight;
            document.getElementById('energy-insight').textContent = energyInsight;
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
            
            // Update time and data status
            const hours = Math.floor(t / 3600);
            const minutes = Math.floor((t % 3600) / 60);
            const seconds = Math.floor(t % 60);
            document.getElementById('sim-time').textContent = 
                hours.toString().padStart(2, '0') + ':' +
                minutes.toString().padStart(2, '0') + ':' +
                seconds.toString().padStart(2, '0');
            
            // Update data status indicator
            const currentTimeStamp = new Date().toLocaleTimeString();
            document.getElementById('data-status').textContent = 'LIVE';
            document.getElementById('last-update').textContent = 'Last Update: ' + currentTimeStamp;
            
            // Flash data status indicator to show active updates
            const dataStatus = document.getElementById('data-status');
            dataStatus.style.color = '#22c55e'; // Green
            setTimeout(() => {
                dataStatus.style.color = '#10b981'; // Slightly dimmer green
            }, 100);
            
            // Store enhanced data for charts with timestamps
            const timestamp = Date.now() / 1000;
            tempData.push({ 
                temp, 
                setpoint, 
                time: timestamp,
                tolerance_high: setpoint + 0.5,
                tolerance_low: setpoint - 0.5
            });
            energyData.push({ 
                power, 
                cooling, 
                cop, 
                time: timestamp 
            });
            
            // Store CRAC output data for trending
            cracOutputData.push({
                time: timestamp,
                lead_pct,
                lag_pct: lag_on ? 25 : 0,
                standby_pct: 0
            });
            
            // Store KPI history for sparklines
            const inBandCompliance = Math.abs(error) < 0.5 ? 100 : 85 + Math.random() * 10;
            kpiHistoryData.push({
                time: timestamp,
                temperature_compliance: inBandCompliance,
                cop_efficiency: cop,
                failover_time: 12.3,
                active_alarms: 0
            });
            
            // Limit data points (keep more data for longer timeframes)
            if (tempData.length > maxDataPoints) tempData.shift();
            if (energyData.length > maxDataPoints) energyData.shift();
            if (cracOutputData.length > maxDataPoints) cracOutputData.shift();
            if (kpiHistoryData.length > maxDataPoints) kpiHistoryData.shift();
            
            // Update floorplan
            updateFloorplan(temp, setpoint, lead_pct, lag_on, power, cooling, cop);
            
            // Update enhanced charts
            renderCharts();
        }
        
        // UI interaction functions
        function scrollToChart(chartId) {
            document.getElementById(chartId).scrollIntoView({ behavior: 'smooth' });
        }
        
        
        // Initialize enhanced chart system
        function initEnhancedCharts() {
            // Set initial time range
            setTimeRange('1h');
            
            // Initialize chart containers
            if (!document.getElementById('temp-chart-container')) {
                console.warn('Temperature chart container not found');
            }
            if (!document.getElementById('energy-chart-container')) {
                console.warn('Energy chart container not found');
            }
            
            // Initialize sparkline containers
            document.querySelectorAll('.sparkline-container').forEach(container => {
                if (!container.innerHTML) {
                    container.innerHTML = '<div class="flex items-center justify-center h-full text-muted-foreground text-xs">No data</div>';
                }
            });
        }
        
        // Initialize on load
        window.addEventListener('load', function() {
            initEnhancedCharts();
            initFloorplanInteractivity();
            updateLiveData();
            setInterval(updateLiveData, 500);
        });
    </script>
</head>
<body>
    <div class="container mx-auto px-4 max-w-7xl">

        <!-- Top KPI Summary Strip -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <!-- Temperature In-Band KPI Card -->
            <div class="bg-card text-card-foreground rounded-lg border shadow-sm p-6 cursor-pointer transition-all hover:shadow-md hover:-translate-y-1" onclick="scrollToChart('temp-chart')">
                <div class="text-sm font-medium text-muted-foreground">Temperature In-Band</div>
                <div class="text-3xl font-bold text-temp" id="kpi-temp-band">96.4%</div>
                <div class="text-xs text-muted-foreground mt-1">Within ±0.5°F tolerance</div>
                <div class="sparkline-container mt-2" id="temp-sparkline"></div>
            </div>
            
            <!-- Failover Time KPI Card -->
            <div class="bg-card text-card-foreground rounded-lg border shadow-sm p-6 cursor-pointer transition-all hover:shadow-md hover:-translate-y-1" onclick="scrollToChart('equipment-chart')">
                <div class="text-sm font-medium text-muted-foreground">Failover Time</div>
                <div class="text-3xl font-bold text-setpoint" id="kpi-failover">12.3s</div>
                <div class="text-xs text-muted-foreground mt-1">STANDBY → ACTIVE</div>
                <div class="sparkline-container mt-2" id="failover-sparkline"></div>
            </div>
            
            <!-- COP KPI Card -->
            <div class="bg-card text-card-foreground rounded-lg border shadow-sm p-6 cursor-pointer transition-all hover:shadow-md hover:-translate-y-1" onclick="scrollToChart('energy-chart')">
                <div class="text-sm font-medium text-muted-foreground">Average COP</div>
                <div class="text-3xl font-bold text-cop" id="kpi-cop">3.24</div>
                <div class="text-xs text-muted-foreground mt-1">Energy efficiency ratio</div>
                <div class="sparkline-container mt-2" id="cop-sparkline"></div>
            </div>
            
            <!-- Alarms KPI Card -->
            <div class="bg-card text-card-foreground rounded-lg border shadow-sm p-6 cursor-pointer transition-all hover:shadow-md hover:-translate-y-1" onclick="scrollToChart('equipment-chart')">
                <div class="text-sm font-medium text-muted-foreground">Active Alarms</div>
                <div class="text-3xl font-bold text-alarm" id="kpi-alarms">0</div>
                <div class="text-xs text-muted-foreground mt-1">All systems normal</div>
                <div class="sparkline-container mt-2" id="alarms-sparkline"></div>
            </div>
        </div>

        <!-- Data Center Floorplan Section -->
        <div class="mb-8">
            
            <div class="bg-card text-card-foreground rounded-lg border shadow-sm p-6">
                <div class="w-full h-96 bg-muted rounded-md overflow-hidden" id="floorplan-container">
                    <svg width="100%" height="100%" viewBox="0 0 800 400" id="floorplan-svg" class="w-full h-full">
                        <!-- Room Outline -->
                        <rect x="10" y="10" width="780" height="380" fill="#f8f9fa" stroke="#34495e" stroke-width="3" rx="5"/>
                        
                        <!-- Room Label -->
                        <text x="400" y="35" text-anchor="middle" class="text-sm font-bold fill-foreground">Data Center Room - Zone A</text>
                        
                        <!-- Cold Aisle (Blue) -->
                        <rect x="50" y="60" width="700" height="80" fill="#dbeafe" stroke="#3b82f6" stroke-width="2" stroke-dasharray="5,5" rx="4"/>
                        <text x="400" y="105" text-anchor="middle" class="text-xs font-medium fill-blue-600">COLD AISLE - Supply Air 55°F</text>
                        
                        <!-- Hot Aisle (Red) -->
                        <rect x="50" y="260" width="700" height="80" fill="#fef2f2" stroke="#ef4444" stroke-width="2" stroke-dasharray="5,5" rx="4"/>
                        <text x="400" y="305" text-anchor="middle" class="text-xs font-medium fill-red-600">HOT AISLE - Return Air 75°F</text>
                        
                        <!-- Server Racks Row 1 (facing cold aisle) -->
                        <g id="rack-row-1">
                            <!-- Rack A1 -->
                            <rect x="80" y="150" width="40" height="100" fill="#2d3748" stroke="#4a5568" stroke-width="2" rx="3" class="rack" data-rack="A1" data-temp="71.8"/>
                            <text x="100" y="170" text-anchor="middle" class="text-xs fill-white font-medium">A1</text>
                            <circle cx="100" cy="185" r="4" class="temp-sensor" fill="#10b981" data-temp="71.8"/>
                            <text x="100" y="189" text-anchor="middle" class="text-xs fill-white">72°</text>
                            
                            <!-- Rack A2 -->
                            <rect x="140" y="150" width="40" height="100" fill="#2d3748" stroke="#4a5568" stroke-width="2" rx="3" class="rack" data-rack="A2" data-temp="72.1"/>
                            <text x="160" y="170" text-anchor="middle" class="text-xs fill-white font-medium">A2</text>
                            <circle cx="160" cy="185" r="4" class="temp-sensor" fill="#10b981" data-temp="72.1"/>
                            <text x="160" y="189" text-anchor="middle" class="text-xs fill-white">72°</text>
                            
                            <!-- Rack A3 -->
                            <rect x="200" y="150" width="40" height="100" fill="#2d3748" stroke="#4a5568" stroke-width="2" rx="3" class="rack" data-rack="A3" data-temp="71.9"/>
                            <text x="220" y="170" text-anchor="middle" class="text-xs fill-white font-medium">A3</text>
                            <circle cx="220" cy="185" r="4" class="temp-sensor" fill="#10b981" data-temp="71.9"/>
                            <text x="220" y="189" text-anchor="middle" class="text-xs fill-white">72°</text>
                            
                            <!-- Rack A4 -->
                            <rect x="260" y="150" width="40" height="100" fill="#2d3748" stroke="#4a5568" stroke-width="2" rx="3" class="rack" data-rack="A4" data-temp="72.3"/>
                            <text x="280" y="170" text-anchor="middle" class="text-xs fill-white font-medium">A4</text>
                            <circle cx="280" cy="185" r="4" class="temp-sensor" fill="#f59e0b" data-temp="72.3"/>
                            <text x="280" y="189" text-anchor="middle" class="text-xs fill-white">72°</text>
                            
                            <!-- Rack A5 -->
                            <rect x="320" y="150" width="40" height="100" fill="#2d3748" stroke="#4a5568" stroke-width="2" rx="3" class="rack" data-rack="A5" data-temp="72.0"/>
                            <text x="340" y="170" text-anchor="middle" class="text-xs fill-white font-medium">A5</text>
                            <circle cx="340" cy="185" r="4" class="temp-sensor" fill="#10b981" data-temp="72.0"/>
                            <text x="340" y="189" text-anchor="middle" class="text-xs fill-white">72°</text>
                            
                            <!-- Rack A6 -->
                            <rect x="380" y="150" width="40" height="100" fill="#2d3748" stroke="#4a5568" stroke-width="2" rx="3" class="rack" data-rack="A6" data-temp="71.7"/>
                            <text x="400" y="170" text-anchor="middle" class="text-xs fill-white font-medium">A6</text>
                            <circle cx="400" cy="185" r="4" class="temp-sensor" fill="#10b981" data-temp="71.7"/>
                            <text x="400" y="189" text-anchor="middle" class="text-xs fill-white">72°</text>
                            
                            <!-- Rack A7 -->
                            <rect x="440" y="150" width="40" height="100" fill="#2d3748" stroke="#4a5568" stroke-width="2" rx="3" class="rack" data-rack="A7" data-temp="72.2"/>
                            <text x="460" y="170" text-anchor="middle" class="text-xs fill-white font-medium">A7</text>
                            <circle cx="460" cy="185" r="4" class="temp-sensor" fill="#10b981" data-temp="72.2"/>
                            <text x="460" y="189" text-anchor="middle" class="text-xs fill-white">72°</text>
                            
                            <!-- Rack A8 -->
                            <rect x="500" y="150" width="40" height="100" fill="#2d3748" stroke="#4a5568" stroke-width="2" rx="3" class="rack" data-rack="A8" data-temp="71.6"/>
                            <text x="520" y="170" text-anchor="middle" class="text-xs fill-white font-medium">A8</text>
                            <circle cx="520" cy="185" r="4" class="temp-sensor" fill="#10b981" data-temp="71.6"/>
                            <text x="520" y="189" text-anchor="middle" class="text-xs fill-white">72°</text>
                            
                            <!-- Rack A9 -->
                            <rect x="560" y="150" width="40" height="100" fill="#2d3748" stroke="#4a5568" stroke-width="2" rx="3" class="rack" data-rack="A9" data-temp="72.4"/>
                            <text x="580" y="170" text-anchor="middle" class="text-xs fill-white font-medium">A9</text>
                            <circle cx="580" cy="185" r="4" class="temp-sensor" fill="#f59e0b" data-temp="72.4"/>
                            <text x="580" y="189" text-anchor="middle" class="text-xs fill-white">72°</text>
                            
                            <!-- Rack A10 -->
                            <rect x="620" y="150" width="40" height="100" fill="#2d3748" stroke="#4a5568" stroke-width="2" rx="3" class="rack" data-rack="A10" data-temp="71.8"/>
                            <text x="640" y="170" text-anchor="middle" class="text-xs fill-white font-medium">A10</text>
                            <circle cx="640" cy="185" r="4" class="temp-sensor" fill="#10b981" data-temp="71.8"/>
                            <text x="640" y="189" text-anchor="middle" class="text-xs fill-white">72°</text>
                            
                            <!-- Rack A11 -->
                            <rect x="680" y="150" width="40" height="100" fill="#2d3748" stroke="#4a5568" stroke-width="2" rx="3" class="rack" data-rack="A11" data-temp="72.1"/>
                            <text x="700" y="170" text-anchor="middle" class="text-xs fill-white font-medium">A11</text>
                            <circle cx="700" cy="185" r="4" class="temp-sensor" fill="#10b981" data-temp="72.1"/>
                            <text x="700" y="189" text-anchor="middle" class="text-xs fill-white">72°</text>
                        </g>
                        
                        <!-- CRAC Units -->
                        <!-- CRAC-01 (Left) -->
                        <g id="crac-01" class="crac-unit" data-crac="CRAC-01">
                            <rect x="20" y="160" width="50" height="80" fill="#27ae60" stroke="#1e8449" stroke-width="3" rx="5"/>
                            <text x="45" y="185" text-anchor="middle" class="text-xs fill-white font-bold">CRAC</text>
                            <text x="45" y="200" text-anchor="middle" class="text-xs fill-white font-bold">01</text>
                            <text x="45" y="215" text-anchor="middle" class="text-xs fill-white">LEAD</text>
                            <circle cx="45" cy="225" r="6" fill="#a3f7a3" class="status-indicator">
                                <animate attributeName="opacity" values="1;0.5;1" dur="2s" repeatCount="indefinite"/>
                            </circle>
                            <!-- Airflow arrows -->
                            <path d="M 70 180 L 80 180 M 75 175 L 80 180 L 75 185" stroke="#ffffff" stroke-width="2" fill="none"/>
                            <path d="M 70 200 L 80 200 M 75 195 L 80 200 L 75 205" stroke="#ffffff" stroke-width="2" fill="none"/>
                            <path d="M 70 220 L 80 220 M 75 215 L 80 220 L 75 225" stroke="#ffffff" stroke-width="2" fill="none"/>
                        </g>
                        
                        <!-- CRAC-02 (Center) -->
                        <g id="crac-02" class="crac-unit" data-crac="CRAC-02">
                            <rect x="375" y="350" width="50" height="40" fill="#3498db" stroke="#2980b9" stroke-width="3" rx="5"/>
                            <text x="400" y="368" text-anchor="middle" class="text-xs fill-white font-bold">CRAC-02</text>
                            <text x="400" y="380" text-anchor="middle" class="text-xs fill-white">LAG</text>
                            <circle cx="385" cy="385" r="4" fill="#5dade2"/>
                            <!-- Airflow arrows -->
                            <path d="M 390 340 L 390 350 M 385 345 L 390 350 L 395 345" stroke="#3498db" stroke-width="2" fill="none"/>
                            <path d="M 400 340 L 400 350 M 395 345 L 400 350 L 405 345" stroke="#3498db" stroke-width="2" fill="none"/>
                            <path d="M 410 340 L 410 350 M 405 345 L 410 350 L 415 345" stroke="#3498db" stroke-width="2" fill="none"/>
                        </g>
                        
                        <!-- CRAC-03 (Right) -->
                        <g id="crac-03" class="crac-unit" data-crac="CRAC-03">
                            <rect x="730" y="160" width="50" height="80" fill="#95a5a6" stroke="#7f8c8d" stroke-width="3" rx="5"/>
                            <text x="755" y="185" text-anchor="middle" class="text-xs fill-white font-bold">CRAC</text>
                            <text x="755" y="200" text-anchor="middle" class="text-xs fill-white font-bold">03</text>
                            <text x="755" y="215" text-anchor="middle" class="text-xs fill-white">STANDBY</text>
                            <circle cx="755" cy="225" r="6" fill="#bdc3c7" class="status-indicator"/>
                        </g>
                        
                        <!-- Temperature Legend -->
                        <g id="temp-legend" transform="translate(620, 50)">
                            <rect x="0" y="0" width="160" height="90" fill="rgba(255,255,255,0.9)" stroke="#34495e" stroke-width="1" rx="3"/>
                            <text x="80" y="15" text-anchor="middle" class="text-xs font-bold fill-foreground">Temperature Status</text>
                            
                            <circle cx="15" cy="30" r="6" fill="#10b981"/>
                            <text x="25" y="35" class="text-xs fill-foreground">Normal (70-73°F)</text>
                            
                            <circle cx="15" cy="50" r="6" fill="#f59e0b"/>
                            <text x="25" y="55" class="text-xs fill-foreground">Warning (73-75°F)</text>
                            
                            <circle cx="15" cy="70" r="6" fill="#ef4444"/>
                            <text x="25" y="75" class="text-xs fill-foreground">Critical (>75°F)</text>
                        </g>
                        
                        <!-- System Status -->
                        <g id="system-status" transform="translate(50, 350)">
                            <rect x="0" y="0" width="280" height="35" fill="rgba(255,255,255,0.9)" stroke="#34495e" stroke-width="1" rx="3"/>
                            <text x="10" y="15" class="text-xs font-bold fill-foreground">System Status:</text>
                            <text x="10" y="28" class="text-xs fill-cooling font-medium" id="floorplan-status">Normal Operation - All Equipment Online</text>
                        </g>
                    </svg>
                </div>
                
                <div class="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="text-center">
                        <div class="text-2xl font-bold text-cooling" id="floorplan-avg-temp">72.0°F</div>
                        <div class="text-sm text-muted-foreground">Average Rack Inlet</div>
                    </div>
                    <div class="text-center">
                        <div class="text-2xl font-bold text-setpoint" id="floorplan-airflow">24,000 CFM</div>
                        <div class="text-sm text-muted-foreground">Total Airflow</div>
                    </div>
                    <div class="text-center">
                        <div class="text-2xl font-bold text-primary" id="floorplan-load">85%</div>
                        <div class="text-sm text-muted-foreground">IT Load Utilization</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 2x2 Chart Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <!-- A1: Zone Temperature vs Setpoint (spans 2 columns) -->
            <div class="lg:col-span-2 bg-card text-card-foreground rounded-lg border shadow-sm" id="temp-chart">
                <div class="p-6">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-lg font-semibold">Zone Temperature vs Setpoint</h3>
                        <div class="flex gap-1">
                            <button class="time-range-btn px-2 py-1 text-xs rounded bg-muted text-muted-foreground hover:bg-primary hover:text-primary-foreground" data-range="15min" onclick="setTimeRange('15min')">15m</button>
                            <button class="time-range-btn px-2 py-1 text-xs rounded bg-primary text-primary-foreground" data-range="1h" onclick="setTimeRange('1h')">1h</button>
                            <button class="time-range-btn px-2 py-1 text-xs rounded bg-muted text-muted-foreground hover:bg-primary hover:text-primary-foreground" data-range="4h" onclick="setTimeRange('4h')">4h</button>
                            <button class="time-range-btn px-2 py-1 text-xs rounded bg-muted text-muted-foreground hover:bg-primary hover:text-primary-foreground" data-range="24h" onclick="setTimeRange('24h')">24h</button>
                            <button class="text-xs px-2 py-1 rounded border hover:bg-muted" onclick="exportToCSV('temperature')" title="Export CSV">⬇</button>
                        </div>
                    </div>
                    <div class="h-48 bg-muted rounded-md" id="temp-chart-container">
                        <div class="flex items-center justify-center h-full text-muted-foreground">Loading chart...</div>
                    </div>
                    <p class="text-sm text-muted-foreground mt-2">
                        Temperature control within ±0.5°F tolerance band. <span id="temp-insight" class="font-medium">System stable at setpoint.</span>
                    </p>
                </div>
            </div>
            
            <!-- A2: Equipment Utilization -->
            <div class="bg-card text-card-foreground rounded-lg border shadow-sm" id="utilization-chart">
                <div class="p-6">
                    <h3 class="text-lg font-semibold mb-4">Equipment Utilization</h3>
                    <div class="space-y-3">
                        <!-- CRAC-01 Card -->
                        <div class="bg-secondary rounded-md p-3 border-l-4 border-l-cooling">
                            <div class="flex items-center justify-between mb-2">
                                <h4 class="font-medium">CRAC-01</h4>
                                <span class="inline-flex items-center rounded-full bg-cooling px-2 py-1 text-xs font-medium text-white">LEAD</span>
                            </div>
                            <div class="space-y-1 text-sm">
                                <div class="flex justify-between">
                                    <span>Output:</span>
                                    <span class="font-medium text-primary" id="lead-output">65.2%</span>
                                </div>
                                <div class="flex justify-between">
                                    <span>Runtime:</span>
                                    <span class="font-medium text-primary" id="lead-runtime">2.4h</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- CRAC-02 Card -->
                        <div class="bg-secondary rounded-md p-3 border-l-4 border-l-setpoint">
                            <div class="flex items-center justify-between mb-2">
                                <h4 class="font-medium">CRAC-02</h4>
                                <span class="inline-flex items-center rounded-full bg-setpoint px-2 py-1 text-xs font-medium text-white">LAG</span>
                            </div>
                            <div class="space-y-1 text-sm">
                                <div class="flex justify-between">
                                    <span>Output:</span>
                                    <span class="font-medium text-primary" id="lag-output">25.0%</span>
                                </div>
                                <div class="flex justify-between">
                                    <span>Starts:</span>
                                    <span class="font-medium text-primary" id="lag-starts">3</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- CRAC-03 Card -->
                        <div class="bg-secondary rounded-md p-3 border-l-4 border-l-cop">
                            <div class="flex items-center justify-between mb-2">
                                <h4 class="font-medium">CRAC-03</h4>
                                <span class="inline-flex items-center rounded-full bg-cop px-2 py-1 text-xs font-medium text-white">STANDBY</span>
                            </div>
                            <div class="space-y-1 text-sm">
                                <div class="flex justify-between">
                                    <span>Status:</span>
                                    <span class="font-medium text-primary">READY</span>
                                </div>
                                <div class="flex justify-between">
                                    <span>Availability:</span>
                                    <span class="font-medium text-primary">100%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <p class="text-sm text-muted-foreground mt-4">
                        <span id="staging-events" class="font-medium">2 staging events</span> in current session. N+1 redundancy maintained.
                    </p>
                </div>
            </div>
            
            <!-- B1: Power vs Cooling with COP (spans 2 columns) -->
            <div class="lg:col-span-2 bg-card text-card-foreground rounded-lg border shadow-sm" id="energy-chart">
                <div class="p-6">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-lg font-semibold">Power vs Cooling with COP</h3>
                        <div class="flex gap-1">
                            <button class="time-range-btn px-2 py-1 text-xs rounded bg-muted text-muted-foreground hover:bg-primary hover:text-primary-foreground" data-range="15min" onclick="setTimeRange('15min')">15m</button>
                            <button class="time-range-btn px-2 py-1 text-xs rounded bg-primary text-primary-foreground" data-range="1h" onclick="setTimeRange('1h')">1h</button>
                            <button class="time-range-btn px-2 py-1 text-xs rounded bg-muted text-muted-foreground hover:bg-primary hover:text-primary-foreground" data-range="4h" onclick="setTimeRange('4h')">4h</button>
                            <button class="time-range-btn px-2 py-1 text-xs rounded bg-muted text-muted-foreground hover:bg-primary hover:text-primary-foreground" data-range="24h" onclick="setTimeRange('24h')">24h</button>
                            <button class="text-xs px-2 py-1 rounded border hover:bg-muted" onclick="exportToCSV('energy')" title="Export CSV">⬇</button>
                        </div>
                    </div>
                    <div class="h-48 bg-muted rounded-md" id="energy-chart-container">
                        <div class="flex items-center justify-center h-full text-muted-foreground">Loading chart...</div>
                    </div>
                    <p class="text-sm text-muted-foreground mt-2">
                        System COP: <span id="current-cop" class="font-medium text-cop">3.24</span>. <span id="energy-insight" class="font-medium">Efficiency above Energy Star 2.5 baseline.</span>
                    </p>
                </div>
            </div>
            
            <!-- B2: Equipment Timeline -->
            <div class="bg-card text-card-foreground rounded-lg border shadow-sm" id="timeline-chart">
                <div class="p-6">
                    <h3 class="text-lg font-semibold mb-4">Equipment Timeline</h3>
                    <div class="h-48 bg-muted rounded-md flex items-center justify-center">
                        <div class="text-center space-y-4">
                            <div class="text-lg font-medium">System Timeline</div>
                            <div class="space-y-2 text-sm">
                                <div class="flex items-center gap-2">
                                    <div class="w-3 h-3 rounded-full bg-cooling"></div>
                                    <span>LEAD Active: <span id="timeline-lead" class="font-medium">2.4h</span></span>
                                </div>
                                <div class="flex items-center gap-2">
                                    <div class="w-3 h-3 rounded-full bg-setpoint"></div>
                                    <span>LAG Staged: <span id="timeline-lag" class="font-medium">0.8h</span></span>
                                </div>
                                <div class="flex items-center gap-2">
                                    <div class="w-3 h-3 rounded-full bg-cop"></div>
                                    <span>STANDBY Ready: <span id="timeline-standby" class="font-medium">2.4h</span></span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <p class="text-sm text-muted-foreground mt-4">
                        <span id="timeline-insight" class="font-medium">No maintenance windows scheduled. All units operational.</span>
                    </p>
                </div>
            </div>
        </div>

        <!-- Engineer Mode Section -->
        <div class="mb-8">
            <div class="bg-card text-card-foreground rounded-lg border shadow-sm p-6" id="engineer-panel">
                <h3 class="text-lg font-semibold mb-4">PID Controller Analysis</h3>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                    <div class="text-center">
                        <h4 class="text-lg font-medium text-alarm mb-2">P-Term</h4>
                        <div class="text-2xl font-bold" id="p-term">2.1</div>
                        <div class="text-sm text-muted-foreground">Proportional Response</div>
                    </div>
                    <div class="text-center">
                        <h4 class="text-lg font-medium text-power mb-2">I-Term</h4>
                        <div class="text-2xl font-bold" id="i-term">-0.3</div>
                        <div class="text-sm text-muted-foreground">Integral Accumulation</div>
                    </div>
                    <div class="text-center">
                        <h4 class="text-lg font-medium text-cooling mb-2">D-Term</h4>
                        <div class="text-2xl font-bold" id="d-term">0.1</div>
                        <div class="text-sm text-muted-foreground">Derivative Action</div>
                    </div>
                </div>
                <div class="bg-muted rounded-lg p-4">
                    <span class="font-semibold">Controller Status:</span> 
                    <span id="controller-status" class="text-muted-foreground">Stable operation, no saturation detected</span>
                </div>
            </div>
        </div>

        <!-- Status Footer -->
        <div class="bg-card text-card-foreground rounded-lg border shadow-sm p-6 text-center">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 items-center">
                <div>
                    <span class="font-semibold">Simulation Time:</span> 
                    <span id="sim-time" class="font-mono text-primary">00:00:00</span>
                </div>
                <div>
                    <span class="font-semibold">Real-time Factor:</span> 
                    <span class="text-primary">50×</span>
                </div>
                <div>
                    <span class="font-semibold">Data Status:</span> 
                    <span id="data-status" class="font-bold text-green-500">LIVE</span>
                </div>
                <div>
                    <span class="font-semibold">System Status:</span> 
                    <span class="text-cooling font-medium">OPERATIONAL</span>
                </div>
            </div>
            <div class="mt-3 pt-3 border-t">
                <span id="last-update" class="text-sm text-muted-foreground">Last Update: --:--:--</span>
            </div>
            <div class="flex flex-wrap justify-center gap-4 mt-4 pt-4 border-t">
                <a href="/red" class="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2">
                    🔧 Flow Editor
                </a>
                <a href="/" class="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2">
                    🏠 Home
                </a>
                <a href="https://github.com/miikeyanderson/data-center-bas-sim-main" class="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2">
                    📁 Source
                </a>
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