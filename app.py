#!/usr/bin/env python3
"""
Salesforce Lead Generation Engine - Web Dashboard Server
Runs a lightweight web dashboard on http://localhost:8000
"""

import http.server
import socketserver
import json
import urllib.parse
from src.collectors.job_signals import JobSignalCollector
from src.collectors.tech_detector import TechDetectorCollector
from src.collectors.intent_finder import IntentFinderCollector
from src.processing.lead_scorer import LeadScorer
from src.processing.outreach_generator import OutreachGenerator

PORT = 8000

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Salesforce Lead Generation Studio</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0f172a;
            --panel-bg: #1e293b;
            --accent-sf: #00a1e0;
            --accent-hover: #0081b8;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --card-border: #334155;
            --grade-a: #10b981;
            --grade-b: #f59e0b;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-main);
            padding: 2rem;
        }

        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--card-border);
        }

        .logo-title {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .logo-badge {
            background: linear-gradient(135deg, #00a1e0, #0047bb);
            padding: 0.6rem 1rem;
            border-radius: 8px;
            font-weight: 700;
            font-size: 1.2rem;
            color: white;
            box-shadow: 0 4px 15px rgba(0, 161, 224, 0.4);
        }

        h1 { font-size: 1.75rem; font-weight: 700; }
        p.subtitle { color: var(--text-muted); font-size: 0.95rem; margin-top: 0.25rem; }

        .btn {
            background: var(--accent-sf);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }

        .btn:hover { background: var(--accent-hover); transform: translateY(-2px); }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: var(--panel-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 1.25rem;
        }

        .stat-val { font-size: 2rem; font-weight: 700; color: var(--accent-sf); margin-top: 0.5rem; }
        .stat-lbl { color: var(--text-muted); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }

        .leads-table-container {
            background: var(--panel-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            overflow: hidden;
        }

        table { width: 100%; border-collapse: collapse; text-align: left; }
        th, td { padding: 1rem 1.25rem; border-bottom: 1px solid var(--card-border); }
        th { background: #182234; color: var(--text-muted); font-weight: 600; font-size: 0.85rem; text-transform: uppercase; }

        tr:hover { background: rgba(255,255,255,0.02); }

        .badge-score {
            display: inline-block;
            padding: 0.3rem 0.75rem;
            border-radius: 20px;
            font-weight: 700;
            font-size: 0.85rem;
        }
        .score-high { background: rgba(16, 185, 129, 0.2); color: var(--grade-a); border: 1px solid var(--grade-a); }
        .score-med { background: rgba(245, 158, 11, 0.2); color: var(--grade-b); border: 1px solid var(--grade-b); }

        .tag {
            background: #2a3a52;
            color: #7dd3fc;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            display: inline-block;
            margin-right: 0.3rem;
            margin-bottom: 0.3rem;
        }

        .pitch-preview {
            background: #0f172a;
            border: 1px solid var(--card-border);
            padding: 0.75rem;
            border-radius: 6px;
            font-size: 0.82rem;
            color: #cbd5e1;
            max-width: 320px;
            white-space: pre-line;
        }
    </style>
</head>
<body>

    <div class="header">
        <div class="logo-title">
            <div class="logo-badge">SF LeadGen</div>
            <div>
                <h1>Salesforce Project Opportunities Studio</h1>
                <p class="subtitle">AI-Powered Lead Discovery, Intent Scoring & Outreach Generator</p>
            </div>
        </div>
        <button class="btn" onclick="location.reload()">🔄 Refresh Leads</button>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-lbl">Identified Leads</div>
            <div class="stat-val" id="total-leads">--</div>
        </div>
        <div class="stat-card">
            <div class="stat-lbl">Hot Opportunities (A+)</div>
            <div class="stat-val" style="color: #10b981;" id="hot-leads">--</div>
        </div>
        <div class="stat-card">
            <div class="stat-lbl">Active Hiring Signals</div>
            <div class="stat-val" style="color: #f59e0b;" id="hiring-signals">--</div>
        </div>
        <div class="stat-card">
            <div class="stat-lbl">Active RFPs & Intent</div>
            <div class="stat-val" style="color: #3b82f6;" id="rfp-count">--</div>
        </div>
    </div>

    <div class="leads-table-container">
        <table>
            <thead>
                <tr>
                    <th>Company / Domain</th>
                    <th>Score & Grade</th>
                    <th>Signals & Intent</th>
                    <th>Detected Tech</th>
                    <th>Generated Pitch Preview</th>
                </tr>
            </thead>
            <tbody id="leads-body">
                <!-- Dynamic standard rows -->
            </tbody>
        </table>
    </div>

    <script>
        fetch('/api/leads')
            .then(res => res.json())
            .then(data => {
                document.getElementById('total-leads').innerText = data.length;
                document.getElementById('hot-leads').innerText = data.filter(l => l.score >= 85).length;
                document.getElementById('hiring-signals').innerText = data.filter(l => l.hiring_signal).length;
                document.getElementById('rfp-count').innerText = data.filter(l => l.intent_signal).length;

                const tbody = document.getElementById('leads-body');
                tbody.innerHTML = data.map(lead => `
                    <tr>
                        <td>
                            <strong>${lead.company_name}</strong><br>
                            <span style="color: #94a3b8; font-size: 0.85rem;">${lead.domain}</span>
                        </td>
                        <td>
                            <span class="badge-score ${lead.score >= 80 ? 'score-high' : 'score-med'}">
                                ${lead.score}/100 • ${lead.grade}
                            </span>
                        </td>
                        <td>
                            ${lead.hiring_signal ? `<div>💼 <strong>Job:</strong> ${lead.hiring_signal}</div>` : ''}
                            ${lead.intent_signal ? `<div style="margin-top:4px;">🎯 <strong>RFP/News:</strong> ${lead.intent_signal}</div>` : ''}
                        </td>
                        <td>
                            ${(lead.tech_footprint || []).map(t => `<span class="tag">${t}</span>`).join('') || '<span style="color:#64748b;">Scanning...</span>'}
                        </td>
                        <td>
                            <div class="pitch-preview">
                                <strong>Subject:</strong> ${lead.pitch.subject}<br><br>
                                ${lead.pitch.body.substring(0, 140)}...
                            </div>
                        </td>
                    </tr>
                `).join('');
            });
    </script>
</body>
</html>
"""

class LeadGenDashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        elif self.path == "/api/leads":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            # Execute pipeline
            job_leads = JobSignalCollector().search_job_signals()
            intent_leads = IntentFinderCollector().find_intent_leads()
            tech_collector = TechDetectorCollector()

            domains = list({l.get("domain") for l in job_leads + intent_leads if l.get("domain")})
            tech_scans = [tech_collector.scan_domain(d) for d in domains]

            scored_leads = LeadScorer().score_and_merge_leads(job_leads, tech_scans, intent_leads)
            pitch_gen = OutreachGenerator()

            for lead in scored_leads:
                lead["pitch"] = pitch_gen.generate_pitch(lead)

            self.wfile.write(json.dumps(scored_leads).encode("utf-8"))
        else:
            self.send_error(404)

def run_server():
    with socketserver.TCPServer(("", PORT), LeadGenDashboardHandler) as httpd:
        print(f"🌐 Salesforce Lead Generation Dashboard active at: http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nDashboard server stopped.")

if __name__ == "__main__":
    run_server()
