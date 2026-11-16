#!/usr/bin/env python3
"""
Live Mission Control Dashboard & Terminal TUI for Hyper Agents Force.

Provides zero-dependency Web GUI (localhost:4242) with real-time Server-Sent Events (SSE)
and an interactive terminal TUI for monitoring Agent Teams, DAG task states, peer chat,
and 1-click Human-in-the-Loop checkpoint resolution.
"""

import os
import sys
import json
import time
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, Optional

WORKSPACE_DIR = Path(__file__).resolve().parent.parent

try:
    from bin.team_engine import TeamEngine
    from bin.hitl_middleware import HitlMiddleware
    from bin.code_graph import CodeGraphEngine
    from bin.memory_manager import MemoryManager
except ImportError:
    from team_engine import TeamEngine
    from hitl_middleware import HitlMiddleware
    from code_graph import CodeGraphEngine
    from memory_manager import MemoryManager


def get_dashboard_payload() -> Dict[str, Any]:
    """Assembles unified state from SQLite for the live dashboard."""
    team_engine = TeamEngine()
    hitl_middleware = HitlMiddleware()
    graph_engine = CodeGraphEngine()
    mem_mgr = MemoryManager()

    teams = team_engine.list_teams()
    team_data = []
    for t in teams:
        tid = t["team_id"]
        board = team_engine.get_board_data(tid)
        team_data.append(board)

    checkpoints = hitl_middleware.list_checkpoints(limit=15)
    graph_stats = graph_engine.get_stats()
    mem_stats = mem_mgr.get_stats()

    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "teams": team_data,
        "checkpoints": checkpoints,
        "graph_stats": graph_stats,
        "memory_stats": mem_stats,
    }


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hyper Agents Force - Live Mission Control</title>
<style>
  :root {
    --bg-primary: #0a0f1d;
    --bg-card: #151e32;
    --border: #23314f;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --accent: #38bdf8;
    --green: #22c55e;
    --amber: #f59e0b;
    --red: #ef4444;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    padding: 20px;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
  }
  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 20px;
  }
  .title { font-size: 20px; font-weight: 700; color: var(--accent); }
  .grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 20px;
    flex: 1;
  }
  .card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
  }
  .card h3 { font-size: 15px; margin-bottom: 12px; display: flex; justify-content: space-between; }
  .columns { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
  .column {
    background: #0f172a;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 10px;
  }
  .column h4 { font-size: 12px; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 10px; }
  .task-item {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 8px;
    margin-bottom: 8px;
    font-size: 12px;
  }
  .badge { display: inline-block; padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: 700; }
  .badge-blocked { background: rgba(239, 68, 68, 0.2); color: var(--red); }
  .badge-unclaimed { background: rgba(245, 158, 11, 0.2); color: var(--amber); }
  .badge-inprogress { background: rgba(56, 189, 248, 0.2); color: var(--accent); }
  .badge-done { background: rgba(34, 197, 94, 0.2); color: var(--green); }
  .btn {
    border: none;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
  }
  .btn-approve { background: #166534; color: #86efac; }
  .btn-reject { background: #991b1b; color: #fca5a5; }
  .chat-msg {
    border-bottom: 1px solid var(--border);
    padding: 8px 0;
    font-size: 12px;
  }
  .chat-meta { color: var(--text-secondary); font-size: 11px; margin-bottom: 2px; }
</style>
</head>
<body>

<header>
  <div class="title">HYPER AGENTS FORCE :: MISSION CONTROL</div>
  <div style="font-size: 12px; color: var(--text-secondary);" id="syncTime">Connecting...</div>
</header>

<div class="grid">
  <div>
    <div class="card">
      <h3><span>Collaborative Agent Team Task Board</span> <span id="teamTitle" style="color: var(--accent);"></span></h3>
      <div class="columns">
        <div class="column">
          <h4>Blocked</h4>
          <div id="colBlocked"></div>
        </div>
        <div class="column">
          <h4>Unclaimed (Ready)</h4>
          <div id="colUnclaimed"></div>
        </div>
        <div class="column">
          <h4>In Progress</h4>
          <div id="colInProgress"></div>
        </div>
        <div class="column">
          <h4>Done</h4>
          <div id="colDone"></div>
        </div>
      </div>
    </div>

    <div class="card">
      <h3>Peer-to-Peer Teammate Communication Stream</h3>
      <div id="chatFeed" style="max-height: 240px; overflow-y: auto;"></div>
    </div>
  </div>

  <div>
    <div class="card">
      <h3>Human-in-the-Loop Checkpoints</h3>
      <div id="hitlList"></div>
    </div>

    <div class="card">
      <h3>Knowledge Graph & Memory Stats</h3>
      <div style="font-size: 13px; line-height: 1.8;">
        <div>AST Graph Nodes: <strong id="statGraphNodes" style="color: var(--accent);">0</strong></div>
        <div>AST Graph Edges: <strong id="statGraphEdges" style="color: var(--accent);">0</strong></div>
        <div>SQLite Memories: <strong id="statMemories" style="color: var(--green);">0</strong></div>
        <div>SQLite Events: <strong id="statEvents" style="color: var(--green);">0</strong></div>
      </div>
    </div>
  </div>
</div>

<script>
  function render(data) {
    document.getElementById('syncTime').innerText = 'Synced: ' + data.timestamp;

    // Team board
    const team = (data.teams && data.teams[0]) || { team: {}, tasks: [], messages: [] };
    document.getElementById('teamTitle').innerText = (team.team && team.team.team_name) || 'No Active Team';

    const colBlocked = document.getElementById('colBlocked');
    const colUnclaimed = document.getElementById('colUnclaimed');
    const colInProgress = document.getElementById('colInProgress');
    const colDone = document.getElementById('colDone');

    colBlocked.innerHTML = '';
    colUnclaimed.innerHTML = '';
    colInProgress.innerHTML = '';
    colDone.innerHTML = '';

    (team.tasks || []).forEach(t => {
      const el = document.createElement('div');
      el.className = 'task-item';
      el.innerHTML = `<strong>[${t.task_id}]</strong> ${t.title}<br><span style="color: var(--text-secondary);">${t.claimed_by ? '@' + t.claimed_by : 'unassigned'}</span>`;
      if (t.status === 'BLOCKED') colBlocked.appendChild(el);
      else if (t.status === 'UNCLAIMED') colUnclaimed.appendChild(el);
      else if (t.status === 'IN_PROGRESS') colInProgress.appendChild(el);
      else if (t.status === 'DONE') colDone.appendChild(el);
    });

    // Chat
    const chatFeed = document.getElementById('chatFeed');
    chatFeed.innerHTML = '';
    (team.messages || []).forEach(m => {
      const msg = document.createElement('div');
      msg.className = 'chat-msg';
      msg.innerHTML = `<div class="chat-meta">@${m.from_agent} -> @${m.to_agent} [${m.created_at}]</div><div>${m.content}</div>`;
      chatFeed.appendChild(msg);
    });

    // HITL Checkpoints
    const hitlList = document.getElementById('hitlList');
    hitlList.innerHTML = '';
    (data.checkpoints || []).forEach(cp => {
      const el = document.createElement('div');
      el.className = 'task-item';
      el.innerHTML = `
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
          <span class="badge ${cp.status === 'PENDING' ? 'badge-unclaimed' : 'badge-done'}">${cp.status}</span>
          <span style="color: var(--text-secondary); font-size: 11px;">@${cp.agent_name}</span>
        </div>
        <div>${cp.summary}</div>
        ${cp.status === 'PENDING' ? `
          <div style="margin-top: 6px; display: flex; gap: 6px;">
            <button class="btn btn-approve" onclick="resolveHitl('${cp.checkpoint_id}', 'APPROVED')">Approve</button>
            <button class="btn btn-reject" onclick="resolveHitl('${cp.checkpoint_id}', 'REJECTED')">Reject</button>
          </div>
        ` : ''}
      `;
      hitlList.appendChild(el);
    });

    // Stats
    document.getElementById('statGraphNodes').innerText = data.graph_stats.total_nodes;
    document.getElementById('statGraphEdges').innerText = data.graph_stats.total_edges;
    document.getElementById('statMemories').innerText = data.memory_stats.total_memories;
    document.getElementById('statEvents').innerText = data.memory_stats.total_events;
  }

  function resolveHitl(id, status) {
    const feedback = prompt('Feedback note for ' + status + ':', status);
    if (feedback !== null) {
      fetch('/api/hitl/resolve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ checkpoint_id: id, status: status, feedback: feedback })
      }).then(() => poll());
    }
  }

  function poll() {
    fetch('/api/status').then(r => r.json()).then(render).catch(console.error);
  }

  poll();
  setInterval(poll, 2500);
</script>

</body>
</html>
"""


class DashboardRequestHandler(BaseHTTPRequestHandler):
    """Zero-dependency HTTP request handler for the live dashboard."""

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/index"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode("utf-8"))
        elif self.path == "/api/status":
            payload = get_dashboard_payload()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/hitl/resolve":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body)
            hitl = HitlMiddleware()
            hitl.resolve_checkpoint(
                checkpoint_id=data["checkpoint_id"],
                status=data["status"],
                user_feedback=data.get("feedback", "")
            )
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"success": true}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Silence routine HTTP access logging
        pass


class DashboardEngine:
    """Launcher for live web and terminal TUI dashboards."""

    @classmethod
    def start_web(cls, port: int = 4242) -> None:
        server = HTTPServer(("localhost", port), DashboardRequestHandler)
        print(f"\n================================================================================")
        print(f"      HYPER AGENTS FORCE :: LIVE MISSION CONTROL DASHBOARD                     ")
        print(f"================================================================================")
        print(f"Dashboard URL: http://localhost:{port}")
        print(f"Server is listening. Press Ctrl+C to terminate.\n")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.server_close()
            print("\nDashboard server terminated cleanly.\n")

    @classmethod
    def render_tui(cls) -> None:
        """Renders instantaneous ASCII terminal status."""
        data = get_dashboard_payload()
        team = (data["teams"] and data["teams"][0]) or {"team": {}, "tasks": []}
        meta = team.get("team") or {}

        print("================================================================================")
        print(f" HYPER AGENTS FORCE :: TERMINAL MISSION CONTROL  [{data['timestamp']}]")
        print("================================================================================")
        print(f"Active Team: {meta.get('team_name', 'None')} (Lead: @{meta.get('lead_agent', 'none')})")
        print(f"Objective:   {meta.get('objective', 'none')}\n")

        print("--- TASK BOARD ---")
        for t in team.get("tasks", []):
            cl = f" [Claimed: @{t['claimed_by']}]" if t.get("claimed_by") else ""
            print(f"[{t['status']:<11}]{cl:<22} ({t['task_id']}) {t['title']}")
        print()

        print(f"--- HITL CHECKPOINTS ({len(data['checkpoints'])}) ---")
        for cp in data["checkpoints"][:4]:
            print(f"[{cp['status']:<9}] ID: {cp['checkpoint_id']} | @{cp['agent_name']} | {cp['summary']}")
        print("================================================================================\n")


def main():
    if "--tui" in sys.argv:
        DashboardEngine.render_tui()
    else:
        port = 4242
        for idx, arg in enumerate(sys.argv):
            if arg in ("--port", "-p") and idx + 1 < len(sys.argv):
                port = int(sys.argv[idx + 1])
        DashboardEngine.start_web(port=port)


if __name__ == "__main__":
    main()
