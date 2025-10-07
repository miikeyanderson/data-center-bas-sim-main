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
    }
};

// Initialize Node-RED
RED.init(server, settings);

// Add the Node-RED UI and admin endpoints
app.use(settings.httpAdminRoot, RED.httpAdmin);
app.use(settings.httpNodeRoot, RED.httpNode);

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