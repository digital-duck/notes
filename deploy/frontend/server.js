const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3100;

// Enable CORS for all routes
app.use(cors());

// Serve static files (CSS, JS, images)
app.use('/assets', express.static(path.join(__dirname, 'assets')));

// Serve the main HTML file
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        message: 'Alpine.js Frontend Server Running',
        backend_api: 'http://localhost:8000'
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Frontend server running on http://localhost:${PORT}`);
    console.log(`📡 Backend API should be running on http://localhost:8000`);
    console.log(`🔗 Make sure CORS is enabled on your FastAPI backend`);
    console.log(`\n📋 Setup Instructions:`);
    console.log(`   1. Run FastAPI backend: python main.py (port 8000)`);
    console.log(`   2. Run this frontend: npm start (port 3100)`);
    console.log(`   3. Open http://localhost:3100 in your browser`);
});