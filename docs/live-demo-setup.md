# Live Demo Setup Guide

## Option 1: GitHub Pages Deployment (Recommended)

### Step 1: Create GitHub Pages Branch
```bash
# Create and switch to gh-pages branch
git checkout -b gh-pages

# Copy essential files for web demo
mkdir -p web-demo
cp hmi/enhanced-node-red-flows.json web-demo/
cp -r reports/ web-demo/
```

### Step 2: Create Web Demo HTML
Create `web-demo/index.html`:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Data Center BAS Control System - Live Demo</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        .demo-container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .performance-images { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }
        .performance-images img { width: 100%; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="demo-container">
        <h1>🏢 Data Center BAS Control System - Live Demo</h1>
        
        <h2>📊 Performance Analysis Dashboard</h2>
        <div class="performance-images">
            <img src="reports/pid_performance.png" alt="PID Performance Analysis">
            <img src="reports/equipment_runtime.png" alt="Equipment Runtime Analysis">
            <img src="reports/energy_performance.png" alt="Energy Performance Analysis">
            <img src="reports/system_overview.png" alt="System Overview Dashboard">
        </div>
        
        <h2>🎛️ Interactive HMI Dashboard</h2>
        <p><strong>Professional Node-RED Interface featuring:</strong></p>
        <ul>
            <li>Interactive data center floor plan with real-time mimic diagram</li>
            <li>Animated airflow visualization showing cooling distribution</li>
            <li>Advanced fault injection controls for comprehensive testing</li>
            <li>Individual role override controls with maintenance mode</li>
        </ul>
        
        <div style="border: 2px solid #004B87; border-radius: 8px; padding: 20px; margin: 20px 0; background: #f8f9fa;">
            <h3>🚀 Try the Live Demo</h3>
            <p>Experience the full BAS control system with real-time simulation:</p>
            <a href="https://your-demo-url.herokuapp.com" target="_blank" 
               style="background: #004B87; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 600;">
               Launch Live Demo →
            </a>
        </div>
    </div>
</body>
</html>
```

### Step 3: Enable GitHub Pages
1. Go to your repo Settings → Pages
2. Select "Deploy from a branch"
3. Choose "gh-pages" branch
4. Your demo will be live at: `https://username.github.io/repo-name`

## Option 2: Heroku Deployment

### Step 1: Create Heroku App Files
Create `package.json`:
```json
{
  "name": "datacenter-bas-demo",
  "version": "1.0.0",
  "description": "Data Center BAS Control System Demo",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "node-red": "^3.1.0",
    "express": "^4.18.0"
  },
  "engines": {
    "node": "18.x"
  }
}
```

Create `server.js`:
```javascript
const express = require('express');
const RED = require('node-red');
const app = express();
const server = require('http').createServer(app);

const settings = {
    httpAdminRoot: "/red",
    httpNodeRoot: "/api",
    userDir: "./node-red-data/",
    flowFile: "flows.json",
    functionGlobalContext: {},
    logging: {
        console: {
            level: "info",
            metrics: false,
            audit: false
        }
    }
};

RED.init(server, settings);
app.use(settings.httpAdminRoot, RED.httpAdmin);
app.use(settings.httpNodeRoot, RED.httpNode);

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`BAS Demo running on port ${PORT}`);
    RED.start();
});
```

### Step 2: Deploy to Heroku
```bash
# Install Heroku CLI and login
heroku create your-bas-demo

# Deploy
git add package.json server.js
git commit -m "Add Heroku deployment files"
git push heroku main
```

## Option 3: Embedded Screenshots/GIFs

### Create Animated Demo
```bash
# Install screen recording tools
brew install ffmpeg

# Record your demo and convert to GIF
ffmpeg -i demo-recording.mov -vf "fps=10,scale=800:-1" demo.gif
```

Add to README:
```markdown
## 🎥 Live Demo

![BAS Control Demo](docs/images/bas-demo.gif)

**[Try Live Demo →](https://your-demo-url.com)**
```

## Option 4: Replit/CodeSandbox Embed

Create a shareable online IDE environment:

1. **Replit**: Upload your Node-RED flows
2. **CodeSandbox**: Create React/Vue wrapper
3. **Embed in README**:

```markdown
## 🔴 Live Interactive Demo

<iframe src="https://replit.com/@username/bas-demo?embed=true" 
        width="100%" height="600px" frameborder="0"></iframe>
```

## Recommended Approach

**For professional BAS demonstration:**

1. **GitHub Pages** for static analysis dashboards
2. **Heroku/Railway** for live Node-RED instance
3. **Add demo badge** to README:

```markdown
[![Live Demo](https://img.shields.io/badge/Live-Demo-blue?style=for-the-badge&logo=heroku)](https://your-demo-url.herokuapp.com)
```

This provides both static performance analysis and interactive real-time control interface for maximum impact.