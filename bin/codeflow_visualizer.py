#!/usr/bin/env python3
"""
Interactive Visual Codeflow Graph Generator for Hyper Agents Force.

Reverse-engineers project structure into a self-contained, offline interactive HTML
visualization file (.agent/context/CODEFLOW_GRAPH.html) inspired by Codeflow.
Zero CDN or external network dependencies.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_HTML_OUTPUT = WORKSPACE_DIR / ".agent" / "context" / "CODEFLOW_GRAPH.html"

try:
    from bin.code_graph import CodeGraphEngine
except ImportError:
    from code_graph import CodeGraphEngine


def generate_codeflow_html(graph_data: Dict[str, Any]) -> str:
    """Generates a standalone, responsive, self-contained SVG/Canvas interactive graph HTML."""
    json_nodes = json.dumps(graph_data["nodes"])
    json_links = json.dumps(graph_data["links"])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hyper Agents Force - Codeflow AST Graph Explorer</title>
<style>
  :root {{
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --border-color: #334155;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --accent: #38bdf8;
    --file-color: #38bdf8;
    --class-color: #a855f7;
    --func-color: #22c55e;
    --module-color: #f59e0b;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background-color: var(--bg-primary);
    color: var(--text-primary);
    overflow: hidden;
    width: 100vw;
    height: 100vh;
    display: flex;
    flex-direction: column;
  }}
  header {{
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
    padding: 12px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    z-index: 10;
  }}
  .logo {{
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: var(--accent);
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .toolbar {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .search-input {{
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 13px;
    width: 240px;
    outline: none;
  }}
  .search-input:focus {{ border-color: var(--accent); }}
  .filter-select {{
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 13px;
    outline: none;
  }}
  .btn {{
    background: #0284c7;
    border: none;
    color: white;
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
  }}
  .btn:hover {{ background: #0369a1; }}
  main {{
    flex: 1;
    position: relative;
    display: flex;
  }}
  #canvas-container {{
    flex: 1;
    height: 100%;
    position: relative;
    cursor: grab;
  }}
  #canvas-container:active {{ cursor: grabbing; }}
  canvas {{
    width: 100%;
    height: 100%;
    display: block;
  }}
  #sidebar {{
    width: 340px;
    background: var(--bg-secondary);
    border-left: 1px solid var(--border-color);
    padding: 20px;
    overflow-y: auto;
    z-index: 10;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }}
  .card {{
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 14px;
  }}
  .card h3 {{
    font-size: 14px;
    color: var(--text-primary);
    margin-bottom: 8px;
    word-break: break-all;
  }}
  .badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 8px;
  }}
  .badge-file {{ background: rgba(56, 189, 248, 0.2); color: var(--file-color); }}
  .badge-class {{ background: rgba(168, 85, 247, 0.2); color: var(--class-color); }}
  .badge-function, .badge-method {{ background: rgba(34, 197, 94, 0.2); color: var(--func-color); }}
  .badge-module {{ background: rgba(245, 158, 11, 0.2); color: var(--module-color); }}
  .meta-row {{
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: var(--text-secondary);
    margin-bottom: 6px;
  }}
  .code-snippet {{
    background: #020617;
    border: 1px solid var(--border-color);
    padding: 8px;
    border-radius: 4px;
    font-family: monospace;
    font-size: 12px;
    color: #38bdf8;
    overflow-x: auto;
    margin-top: 8px;
  }}
  .legend {{
    display: flex;
    gap: 12px;
    font-size: 12px;
    color: var(--text-secondary);
    align-items: center;
  }}
  .legend-dot {{
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;
  }}
</style>
</head>
<body>

<header>
  <div class="logo">
    <span>HYPER AGENTS FORCE</span>
    <span style="font-weight: normal; color: var(--text-secondary); font-size: 13px;">| Codeflow Graph Canvas</span>
  </div>
  <div class="legend">
    <span><span class="legend-dot" style="background: var(--file-color);"></span> File</span>
    <span><span class="legend-dot" style="background: var(--class-color);"></span> Class</span>
    <span><span class="legend-dot" style="background: var(--func-color);"></span> Function</span>
    <span><span class="legend-dot" style="background: var(--module-color);"></span> Module</span>
  </div>
  <div class="toolbar">
    <input type="text" id="search" class="search-input" placeholder="Search symbol or file...">
    <select id="typeFilter" class="filter-select">
      <option value="ALL">All Types</option>
      <option value="file">Files Only</option>
      <option value="class">Classes Only</option>
      <option value="function">Functions Only</option>
    </select>
    <button class="btn" onclick="resetView()">Reset View</button>
  </div>
</header>

<main>
  <div id="canvas-container">
    <canvas id="graphCanvas"></canvas>
  </div>
  <div id="sidebar">
    <h2 style="font-size: 15px; font-weight: 700;">Node Inspector</h2>
    <div id="inspectorContent">
      <p style="color: var(--text-secondary); font-size: 13px;">Click on any node in the canvas to inspect its AST relationships, dependencies, and callers.</p>
    </div>
    <div class="card" style="margin-top: auto;">
      <h4 style="font-size: 12px; color: var(--text-secondary); margin-bottom: 6px;">Graph Statistics</h4>
      <div class="meta-row"><span>Total Nodes:</span><strong id="statNodes">0</strong></div>
      <div class="meta-row"><span>Total Edges:</span><strong id="statEdges">0</strong></div>
      <div class="meta-row"><span>Engine:</span><span>Zero-Config SQLite</span></div>
    </div>
  </div>
</main>

<script>
  const rawNodes = {json_nodes};
  const rawLinks = {json_links};

  document.getElementById('statNodes').innerText = rawNodes.length;
  document.getElementById('statEdges').innerText = rawLinks.length;

  const canvas = document.getElementById('graphCanvas');
  const ctx = canvas.getContext('2d');
  let width, height;

  function resize() {{
    const rect = canvas.parentElement.getBoundingClientRect();
    width = canvas.width = rect.width;
    height = canvas.height = rect.height;
  }}
  window.addEventListener('resize', () => {{ resize(); draw(); }});
  resize();

  // Position nodes in a deterministic circular/force simulation layout
  const nodes = rawNodes.map((n, idx) => {{
    const angle = (idx / Math.max(1, rawNodes.length)) * 2 * Math.PI;
    const radius = Math.min(width, height) * 0.35 + (idx % 3) * 40;
    return {{
      ...n,
      x: width / 2 + Math.cos(angle) * radius,
      y: height / 2 + Math.sin(angle) * radius,
      vx: 0, vy: 0,
      radius: n.node_type === 'file' ? 14 : (n.node_type === 'class' ? 10 : 7)
    }};
  }});

  const nodeMap = new Map();
  nodes.forEach(n => nodeMap.set(n.node_id, n));

  const links = rawLinks.map(l => ({{
    ...l,
    sourceNode: nodeMap.get(l.source_id),
    targetNode: nodeMap.get(l.target_id)
  }})).filter(l => l.sourceNode && l.targetNode);

  let cameraX = 0, cameraY = 0, zoom = 1.0;
  let isDragging = false, dragStartX = 0, dragStartY = 0;
  let selectedNode = null;
  let searchTerm = "";
  let typeFilter = "ALL";

  function getNodeColor(type) {{
    if (type === 'file') return '#38bdf8';
    if (type === 'class') return '#a855f7';
    if (type === 'function' || type === 'method') return '#22c55e';
    return '#f59e0b';
  }}

  function draw() {{
    ctx.clearRect(0, 0, width, height);
    ctx.save();
    ctx.translate(width / 2 + cameraX, height / 2 + cameraY);
    ctx.scale(zoom, zoom);
    ctx.translate(-width / 2, -height / 2);

    // Draw links
    links.forEach(link => {{
      const s = link.sourceNode;
      const t = link.targetNode;
      const isHighlighted = selectedNode && (selectedNode.node_id === s.node_id || selectedNode.node_id === t.node_id);

      ctx.beginPath();
      ctx.moveTo(s.x, s.y);
      ctx.lineTo(t.x, t.y);
      ctx.strokeStyle = isHighlighted ? '#38bdf8' : 'rgba(51, 65, 85, 0.4)';
      ctx.lineWidth = isHighlighted ? 2.5 : 1.0;
      ctx.stroke();
    }});

    // Draw nodes
    nodes.forEach(node => {{
      const isMatch = (!searchTerm || node.name.toLowerCase().includes(searchTerm)) &&
                      (typeFilter === 'ALL' || node.node_type === typeFilter);
      const isSelected = selectedNode && selectedNode.node_id === node.node_id;

      ctx.beginPath();
      ctx.arc(node.x, node.y, node.radius + (isSelected ? 4 : 0), 0, Math.PI * 2);
      ctx.fillStyle = isMatch ? getNodeColor(node.node_type) : 'rgba(100, 116, 139, 0.2)';
      ctx.fill();

      if (isSelected || isMatch && searchTerm) {{
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.stroke();
      }}

      // Text label
      if (node.node_type === 'file' || isSelected || (isMatch && searchTerm)) {{
        ctx.font = isSelected ? 'bold 12px sans-serif' : '10px sans-serif';
        ctx.fillStyle = isMatch ? '#f8fafc' : 'rgba(148, 163, 184, 0.3)';
        ctx.fillText(node.name, node.x + node.radius + 4, node.y + 4);
      }}
    }});

    ctx.restore();
  }}

  // Simulation step (simple repulsion)
  for (let i = 0; i < 40; i++) {{
    links.forEach(l => {{
      const dx = l.targetNode.x - l.sourceNode.x;
      const dy = l.targetNode.y - l.sourceNode.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      const force = (dist - 120) * 0.05;
      l.sourceNode.x += (dx / dist) * force;
      l.sourceNode.y += (dy / dist) * force;
      l.targetNode.x -= (dx / dist) * force;
      l.targetNode.y -= (dy / dist) * force;
    }});
  }}
  draw();

  // Canvas Interactions
  canvas.addEventListener('mousedown', (e) => {{
    isDragging = true;
    dragStartX = e.clientX - cameraX;
    dragStartY = e.clientY - cameraY;
  }});

  window.addEventListener('mousemove', (e) => {{
    if (isDragging) {{
      cameraX = e.clientX - dragStartX;
      cameraY = e.clientY - dragStartY;
      draw();
    }}
  }});

  window.addEventListener('mouseup', () => {{ isDragging = false; }});

  canvas.addEventListener('wheel', (e) => {{
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.1 : 0.9;
    zoom = Math.max(0.2, Math.min(3.0, zoom * factor));
    draw();
  }});

  canvas.addEventListener('click', (e) => {{
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Transform click to world coordinates
    const worldX = (mouseX - (width / 2 + cameraX)) / zoom + width / 2;
    const worldY = (mouseY - (height / 2 + cameraY)) / zoom + height / 2;

    let clicked = null;
    for (const node of nodes) {{
      const dx = worldX - node.x;
      const dy = worldY - node.y;
      if (Math.sqrt(dx * dx + dy * dy) <= node.radius + 4) {{
        clicked = node;
        break;
      }}
    }}

    selectedNode = clicked;
    updateInspector(clicked);
    draw();
  }});

  function updateInspector(node) {{
    const panel = document.getElementById('inspectorContent');
    if (!node) {{
      panel.innerHTML = '<p style="color: var(--text-secondary); font-size: 13px;">Click on any node in the canvas to inspect its AST relationships, dependencies, and callers.</p>';
      return;
    }}

    const callers = links.filter(l => l.target_id === node.node_id);
    const deps = links.filter(l => l.source_id === node.node_id);

    panel.innerHTML = `
      <div class="card">
        <span class="badge badge-${{node.node_type}}">${{node.node_type}}</span>
        <h3>${{node.name}}</h3>
        <div class="meta-row"><span>File:</span><span>${{node.file_path}}</span></div>
        <div class="meta-row"><span>Line:</span><span>${{node.start_line}}</span></div>
        <div class="meta-row"><span>Language:</span><span>${{node.language || 'generic'}}</span></div>
        ${{node.signature ? `<div class="code-snippet">${{node.signature}}</div>` : ''}}
      </div>
      <div class="card">
        <h4 style="font-size: 12px; margin-bottom: 8px;">Inbound Callers (${{callers.length}}):</h4>
        ${{callers.slice(0, 6).map(c => `<div class="meta-row" style="font-size: 11px;"><span>${{c.sourceNode.name}}</span><span style="color: var(--accent);">${{c.relation_type}}</span></div>`).join('') || '<p style="color: var(--text-secondary); font-size: 11px;">None detected</p>'}}
      </div>
      <div class="card">
        <h4 style="font-size: 12px; margin-bottom: 8px;">Outbound Dependencies (${{deps.length}}):</h4>
        ${{deps.slice(0, 6).map(d => `<div class="meta-row" style="font-size: 11px;"><span>${{d.targetNode.name}}</span><span style="color: var(--accent);">${{d.relation_type}}</span></div>`).join('') || '<p style="color: var(--text-secondary); font-size: 11px;">None detected</p>'}}
      </div>
    `;
  }}

  document.getElementById('search').addEventListener('input', (e) => {{
    searchTerm = e.target.value.toLowerCase().trim();
    draw();
  }});

  document.getElementById('typeFilter').addEventListener('change', (e) => {{
    typeFilter = e.target.value;
    draw();
  }});

  function resetView() {{
    cameraX = 0; cameraY = 0; zoom = 1.0;
    searchTerm = ""; typeFilter = "ALL";
    document.getElementById('search').value = "";
    document.getElementById('typeFilter').value = "ALL";
    selectedNode = null;
    updateInspector(null);
    draw();
  }}
</script>

</body>
</html>
"""


class CodeflowVisualizer:
    """Generates standalone visual Codeflow HTML canvas from SQLite AST graph."""

    @classmethod
    def generate(cls, output_file: Optional[Path] = None, root_dir: Optional[Path] = None) -> Path:
        out_path = Path(output_file or DEFAULT_HTML_OUTPUT).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)

        engine = CodeGraphEngine()
        # Build or query existing graph
        stats = engine.get_stats()
        if stats["total_nodes"] == 0:
            engine.build_graph(root_dir=root_dir)

        graph_data = engine.export_graph_json()
        html_content = generate_codeflow_html(graph_data)
        out_path.write_text(html_content, encoding="utf-8")
        return out_path


def main():
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_HTML_OUTPUT
    path = CodeflowVisualizer.generate(output_file=out)
    print(f"\nGenerated Standalone Visual Codeflow Canvas:")
    print(f"Path: {path}")
    print(f"Open this file in any browser to inspect interactive codebase graph (zero network needed).\n")


if __name__ == "__main__":
    main()
