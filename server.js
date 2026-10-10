#!/usr/bin/env node
/**
 * Salesforce & Local Business Lead Generation Engine - NPM Web Server
 * Serves dashboard pages (index.html, website_leads.html, india_leads.html)
 * and proxies API requests (/api/*) to the Python backend daemon (app.py).
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

let currentPort = parseInt(process.env.PORT || '3000', 10);
const PYTHON_PORT = 8000;

// Ensure python backend (app.py) is running in the background for API routes
function ensurePythonBackend() {
    const req = http.get(`http://127.0.0.1:${PYTHON_PORT}/api/scan`, () => {
        console.log(`⚡ Python API engine active on port ${PYTHON_PORT}`);
    });
    req.on('error', () => {
        console.log(`🚀 Launching Python API engine (app.py) on port ${PYTHON_PORT}...`);
        const pyProc = spawn('python3', ['app.py'], {
            cwd: __dirname,
            stdio: 'inherit'
        });
        pyProc.on('error', (err) => {
            console.error(`Failed to start app.py: ${err.message}`);
        });
    });
}

ensurePythonBackend();

const MIME_TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css',
    '.js': 'text/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.ico': 'image/x-icon',
    '.csv': 'text/csv; charset=utf-8',
    '.xls': 'application/vnd.ms-excel'
};

const server = http.createServer((req, res) => {
    const parsedUrl = new URL(req.url, `http://${req.headers.host}`);
    let urlPath = parsedUrl.pathname;

    if (urlPath === '/') urlPath = '/index.html';

    // Proxy API and Export requests to Python backend on port 8000
    if (urlPath.startsWith('/api/')) {
        const proxyReq = http.request({
            hostname: '127.0.0.1',
            port: PYTHON_PORT,
            path: req.url,
            method: req.method,
            headers: req.headers
        }, (proxyRes) => {
            res.writeHead(proxyRes.statusCode, proxyRes.headers);
            proxyRes.pipe(res, { end: true });
        });

        proxyReq.on('error', (err) => {
            res.writeHead(502, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Python backend connecting...', details: err.message }));
        });

        req.pipe(proxyReq, { end: true });
        return;
    }

    // Serve static dashboard files
    let filePath = path.join(__dirname, urlPath);
    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';

    fs.readFile(filePath, (err, data) => {
        if (err) {
            res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
            res.end(`<!DOCTYPE html><html><head><title>404 Not Found</title></head><body style="font-family:sans-serif; background:#090d16; color:#fff; text-align:center; padding:4rem;"><h1>404 Page Not Found</h1><p><a href="/index.html" style="color:#00a1e0;">Return to Dashboard</a></p></body></html>`);
            return;
        }
        res.writeHead(200, { 'Content-Type': contentType });
        res.end(data);
    });
});

function listenOnPort(port) {
    server.removeAllListeners('error');
    server.on('error', (err) => {
        if (err.code === 'EADDRINUSE') {
            console.log(`⚠️ Port ${port} is currently in use. Trying port ${port + 1}...`);
            listenOnPort(port + 1);
        } else {
            console.error('Server error:', err);
        }
    });

    server.listen(port, () => {
        console.log(`\n==================================================`);
        console.log(`🌐 NPM Node Dashboard Server active at: http://localhost:${port}`);
        console.log(`   ⚡ Salesforce Leads: http://localhost:${port}/index.html`);
        console.log(`   🗺️ Local Web Leads:  http://localhost:${port}/website_leads.html`);
        console.log(`   🇮🇳 India Leads:      http://localhost:${port}/india_leads.html`);
        console.log(`==================================================\n`);
    });
}

listenOnPort(currentPort);
