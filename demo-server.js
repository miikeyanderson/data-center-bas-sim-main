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
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            margin: 0; 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 40px 20px; 
        }
        .header {
            text-align: center;
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            margin-bottom: 40px;
        }
        .header h1 {
            color: #004B87;
            font-size: 2.5em;
            margin: 0 0 10px 0;
        }
        .header p {
            color: #6c757d;
            font-size: 1.2em;
            margin: 0;
        }
        .demo-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin: 40px 0;
        }
        .demo-card {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
        }
        .demo-card:hover {
            transform: translateY(-5px);
        }
        .demo-card h3 {
            color: #004B87;
            margin: 0 0 15px 0;
        }
        .demo-btn {
            display: inline-block;
            background: #004B87;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            margin: 15px 0;
            transition: background 0.3s;
        }
        .demo-btn:hover {
            background: #003d6b;
        }
        .performance-preview {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }
        .performance-preview img {
            width: 100%;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .status {
            background: #d4edda;
            color: #155724;
            padding: 10px 20px;
            border-radius: 6px;
            margin: 20px 0;
            text-align: center;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏢 Data Center BAS Control System</h1>
            <p>Professional Building Automation System with Real-Time Control & Monitoring</p>
            <div class="status">
                ✅ System Online - Live Demo Available
            </div>
        </div>

        <div class="demo-grid">
            <div class="demo-card">
                <h3>🎛️ Interactive HMI Dashboard</h3>
                <p>Experience the professional Node-RED interface with:</p>
                <ul style="text-align: left;">
                    <li>Interactive data center floor plan</li>
                    <li>Real-time mimic diagram with airflow</li>
                    <li>Advanced fault injection controls</li>
                    <li>Role override & maintenance modes</li>
                </ul>
                <a href="/ui" class="demo-btn">Launch HMI Dashboard →</a>
            </div>

            <div class="demo-card">
                <h3>⚙️ Node-RED Flow Editor</h3>
                <p>View and modify the control system logic:</p>
                <ul style="text-align: left;">
                    <li>Visual programming interface</li>
                    <li>MQTT/HTTP/WebSocket integration</li>
                    <li>Real-time data processing</li>
                    <li>Professional control algorithms</li>
                </ul>
                <a href="/red" class="demo-btn">Open Flow Editor →</a>
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

        <div style="text-align: center; margin: 40px 0; color: #6c757d;">
            <p>🚀 <strong>Ready to deploy your own?</strong> Check out the <a href="https://github.com/miikeyanderson/data-center-bas-sim-main" style="color: #004B87;">GitHub repository</a> for complete setup instructions.</p>
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

// Copy enhanced flows to demo flows
const enhancedFlowsPath = path.join(__dirname, 'hmi', 'enhanced-node-red-flows.json');
const demoFlowsPath = path.join(__dirname, '.node-red', 'demo-flows.json');

// Ensure .node-red directory exists
const nodeRedDir = path.join(__dirname, '.node-red');
if (!fs.existsSync(nodeRedDir)) {
    fs.mkdirSync(nodeRedDir, { recursive: true });
}

// Copy flows if enhanced flows exist
if (fs.existsSync(enhancedFlowsPath)) {
    try {
        fs.copyFileSync(enhancedFlowsPath, demoFlowsPath);
        console.log('✅ Enhanced Node-RED flows loaded for demo');
    } catch (error) {
        console.log('⚠️ Could not copy enhanced flows, using default');
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