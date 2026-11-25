#!/usr/bin/env python3
"""
Codebase Knowledge Graph Engine (AST Graphify) for Hyper Agents Force.

Parses source code into an offline structural graph (files, classes, functions,
imports, calls, and endpoints) stored in SQLite (.agent/memory/memory.db).
Enables 0-token repetitive codebase context queries across sessions.
"""

import os
import re
import sys
import ast
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = WORKSPACE_DIR / ".agent" / "memory" / "memory.db"

# Language classification
LANGUAGE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".cs": "csharp",
    ".php": "php",
    ".rb": "ruby",
}

IGNORED_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", ".agent",
    ".worktrees", ".sandboxes", "dist", "build", ".next", ".cache",
}


class CodeGraphEngine:
    """Extracts, indexes, and queries codebase structural relationships via SQLite."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path or DEFAULT_DB_PATH).resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def _init_schema(self) -> None:
        """Initializes graph nodes and edges schema."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS code_nodes (
                    node_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    node_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    start_line INTEGER,
                    end_line INTEGER,
                    signature TEXT,
                    docstring TEXT,
                    language TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS code_edges (
                    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    relation_type TEXT NOT NULL,
                    context TEXT,
                    FOREIGN KEY (source_id) REFERENCES code_nodes(node_id),
                    FOREIGN KEY (target_id) REFERENCES code_nodes(node_id)
                );
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_code_nodes_name ON code_nodes(name);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_code_nodes_type ON code_nodes(node_type, file_path);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_code_edges_source ON code_edges(source_id, relation_type);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_code_edges_target ON code_edges(target_id, relation_type);")
            conn.commit()

    def parse_python_file(self, file_path: Path, rel_path_str: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Extracts AST nodes and edges from Python source."""
        nodes = []
        edges = []

        file_node_id = f"file:{rel_path_str}"
        nodes.append({
            "node_id": file_node_id,
            "name": file_path.name,
            "node_type": "file",
            "file_path": rel_path_str,
            "start_line": 1,
            "end_line": 1,
            "signature": rel_path_str,
            "docstring": "",
            "language": "python",
        })

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content, filename=str(file_path))
        except Exception:
            return nodes, edges

        class ASTVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_class = None

            def visit_Import(self, node):
                for alias in node.names:
                    edges.append({
                        "source_id": file_node_id,
                        "target_id": f"module:{alias.name}",
                        "relation_type": "imports",
                        "context": f"import {alias.name}",
                    })
                self.generic_visit(node)

            def visit_ImportFrom(self, node):
                mod = node.module or ""
                for alias in node.names:
                    edges.append({
                        "source_id": file_node_id,
                        "target_id": f"module:{mod}.{alias.name}" if mod else f"module:{alias.name}",
                        "relation_type": "imports",
                        "context": f"from {mod} import {alias.name}",
                    })
                self.generic_visit(node)

            def visit_ClassDef(self, node):
                class_id = f"{file_node_id}#{node.name}"
                doc = ast.get_docstring(node) or ""
                nodes.append({
                    "node_id": class_id,
                    "name": node.name,
                    "node_type": "class",
                    "file_path": rel_path_str,
                    "start_line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno),
                    "signature": f"class {node.name}",
                    "docstring": doc[:200],
                    "language": "python",
                })
                edges.append({
                    "source_id": file_node_id,
                    "target_id": class_id,
                    "relation_type": "defines",
                    "context": "class definition",
                })

                for base in node.bases:
                    if isinstance(base, ast.Name):
                        edges.append({
                            "source_id": class_id,
                            "target_id": f"class:{base.id}",
                            "relation_type": "inherits",
                            "context": f"inherits {base.id}",
                        })

                old_class = self.current_class
                self.current_class = class_id
                self.generic_visit(node)
                self.current_class = old_class

            def visit_FunctionDef(self, node):
                self._handle_func(node)

            def visit_AsyncFunctionDef(self, node):
                self._handle_func(node, is_async=True)

            def _handle_func(self, node, is_async=False):
                parent_id = self.current_class or file_node_id
                node_type = "method" if self.current_class else "function"
                func_id = f"{parent_id}.{node.name}"
                doc = ast.get_docstring(node) or ""
                async_str = "async " if is_async else ""
                args = [a.arg for a in node.args.args]
                sig = f"{async_str}def {node.name}({', '.join(args[:4])})"

                nodes.append({
                    "node_id": func_id,
                    "name": node.name,
                    "node_type": node_type,
                    "file_path": rel_path_str,
                    "start_line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno),
                    "signature": sig,
                    "docstring": doc[:200],
                    "language": "python",
                })
                edges.append({
                    "source_id": parent_id,
                    "target_id": func_id,
                    "relation_type": "defines",
                    "context": f"{node_type} definition",
                })

                # Scan function calls
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Call):
                        if isinstance(sub.func, ast.Name):
                            edges.append({
                                "source_id": func_id,
                                "target_id": f"call:{sub.func.id}",
                                "relation_type": "calls",
                                "context": f"calls {sub.func.id}()",
                            })
                        elif isinstance(sub.func, ast.Attribute):
                            edges.append({
                                "source_id": func_id,
                                "target_id": f"call:{sub.func.attr}",
                                "relation_type": "calls",
                                "context": f"calls .{sub.func.attr}()",
                            })

                self.generic_visit(node)

        visitor = ASTVisitor()
        visitor.visit(tree)
        return nodes, edges

    def parse_generic_code_file(self, file_path: Path, rel_path_str: str, lang: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Extracts structural definitions and imports for JS, TS, Go, Rust, Java via regex."""
        nodes = []
        edges = []

        file_node_id = f"file:{rel_path_str}"
        nodes.append({
            "node_id": file_node_id,
            "name": file_path.name,
            "node_type": "file",
            "file_path": rel_path_str,
            "start_line": 1,
            "end_line": 1,
            "signature": rel_path_str,
            "docstring": "",
            "language": lang,
        })

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return nodes, edges

        lines = content.splitlines()

        # Regex patterns for imports, functions, classes
        import_pat = re.compile(r"""(?:import\s+.*?from\s+['"]([^'"]+)['"]|require\(['"]([^'"]+)['"]\)|import\s+['"]([^'"]+)['"])""")
        func_pat = re.compile(r"""(?:function\s+([A-Za-z0-9_$]+)|(?:const|let|var)\s+([A-Za-z0-9_$]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>|(?:export\s+(?:async\s+)?function\s+([A-Za-z0-9_$]+))|func\s+([A-Za-z0-9_$]+)\s*\(|fn\s+([A-Za-z0-9_$]+)\s*\()""")
        class_pat = re.compile(r"""(?:class|struct|interface|type)\s+([A-Za-z0-9_$]+)""")

        for line_no, line in enumerate(lines, start=1):
            line_str = line.strip()

            # Imports
            imp_m = import_pat.search(line_str)
            if imp_m:
                mod = imp_m.group(1) or imp_m.group(2) or imp_m.group(3)
                if mod:
                    edges.append({
                        "source_id": file_node_id,
                        "target_id": f"module:{mod}",
                        "relation_type": "imports",
                        "context": line_str[:120],
                    })

            # Classes / Structs
            cls_m = class_pat.search(line_str)
            if cls_m and not line_str.startswith("//") and not line_str.startswith("/*"):
                cname = cls_m.group(1)
                cid = f"{file_node_id}#{cname}"
                nodes.append({
                    "node_id": cid,
                    "name": cname,
                    "node_type": "class",
                    "file_path": rel_path_str,
                    "start_line": line_no,
                    "end_line": line_no,
                    "signature": line_str[:80],
                    "docstring": "",
                    "language": lang,
                })
                edges.append({
                    "source_id": file_node_id,
                    "target_id": cid,
                    "relation_type": "defines",
                    "context": f"defines {cname}",
                })

            # Functions
            func_m = func_pat.search(line_str)
            if func_m and not line_str.startswith("//") and not line_str.startswith("/*"):
                fname = func_m.group(1) or func_m.group(2) or func_m.group(3) or func_m.group(4) or func_m.group(5)
                if fname and len(fname) > 1:
                    fid = f"{file_node_id}.{fname}"
                    nodes.append({
                        "node_id": fid,
                        "name": fname,
                        "node_type": "function",
                        "file_path": rel_path_str,
                        "start_line": line_no,
                        "end_line": line_no,
                        "signature": line_str[:80],
                        "docstring": "",
                        "language": lang,
                    })
                    edges.append({
                        "source_id": file_node_id,
                        "target_id": fid,
                        "relation_type": "defines",
                        "context": f"defines {fname}",
                    })

        return nodes, edges

    def build_graph(self, root_dir: Optional[Path] = None, clear_existing: bool = True) -> Dict[str, Any]:
        """Scans workspace and indexes all source files into the graph database."""
        root = Path(root_dir or WORKSPACE_DIR).resolve()

        if clear_existing:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM code_nodes;")
                conn.execute("DELETE FROM code_edges;")
                conn.commit()

        total_files = 0
        all_nodes = []
        all_edges = []

        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if any(part in IGNORED_DIRS for part in p.parts):
                continue

            lang = LANGUAGE_EXTENSIONS.get(p.suffix.lower())
            if not lang:
                continue

            rel_str = str(p.relative_to(root)).replace("\\", "/")
            total_files += 1

            if lang == "python":
                n, e = self.parse_python_file(p, rel_str)
            else:
                n, e = self.parse_generic_code_file(p, rel_str, lang)

            all_nodes.extend(n)
            all_edges.extend(e)

        # Batch insert
        with self._get_connection() as conn:
            cur = conn.cursor()
            for node in all_nodes:
                cur.execute("""
                    INSERT OR REPLACE INTO code_nodes
                    (node_id, name, node_type, file_path, start_line, end_line, signature, docstring, language)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    node["node_id"], node["name"], node["node_type"], node["file_path"],
                    node["start_line"], node["end_line"], node["signature"], node["docstring"], node["language"]
                ))

            for edge in all_edges:
                cur.execute("""
                    INSERT INTO code_edges (source_id, target_id, relation_type, context)
                    VALUES (?, ?, ?, ?)
                """, (edge["source_id"], edge["target_id"], edge["relation_type"], edge.get("context", "")))
            conn.commit()

        # Auto-export standalone Cypher script for Neo4j (zero env configuration needed)
        cypher_file = self.export_cypher()

        return {
            "root_dir": str(root),
            "files_scanned": total_files,
            "nodes_indexed": len(all_nodes),
            "edges_indexed": len(all_edges),
            "cypher_file": str(cypher_file),
            "status": "SUCCESS",
        }

    def export_cypher(self, output_path: Optional[Path] = None) -> Path:
        """Exports the SQLite graph as a Cypher script for Neo4j Desktop or AuraDB."""
        out = Path(output_path or (WORKSPACE_DIR / ".agent" / "context" / "code_graph.cyp")).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            "// Hyper Agents Force - Codebase Knowledge Graph (Cypher Export)",
            "// Execute in Neo4j Browser or cypher-shell (Zero environment configuration required)",
            "",
            "// Constraints & Indices",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:CodeNode) REQUIRE n.node_id IS UNIQUE;",
            ""
        ]

        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT node_id, name, node_type, file_path, start_line, language FROM code_nodes;")
            for r in cur.fetchall():
                label = r["node_type"].capitalize() if r["node_type"] in ("file", "class", "function", "method", "module") else "CodeNode"
                escaped_name = r["name"].replace('"', '\\"')
                escaped_path = r["file_path"].replace('"', '\\"')
                escaped_id = r["node_id"].replace('"', '\\"')
                lines.append(f'MERGE (n:{label} {{node_id: "{escaped_id}"}}) SET n.name = "{escaped_name}", n.file_path = "{escaped_path}", n.start_line = {r["start_line"]}, n.language = "{r["language"]}";')

            lines.append("")
            lines.append("// Relationships")
            cur.execute("SELECT source_id, target_id, relation_type, context FROM code_edges;")
            for r in cur.fetchall():
                rel = r["relation_type"].upper()
                escaped_src = r["source_id"].replace('"', '\\"')
                escaped_tgt = r["target_id"].replace('"', '\\"')
                escaped_ctx = (r["context"] or "").replace('"', '\\"').replace("\n", " ")[:80]
                lines.append(f'MATCH (s {{node_id: "{escaped_src}"}}), (t {{node_id: "{escaped_tgt}"}}) MERGE (s)-[:{rel} {{context: "{escaped_ctx}"}}]->(t);')

        out.write_text("\n".join(lines), encoding="utf-8")
        return out

    def query_symbol(self, symbol_name: str) -> Dict[str, Any]:
        """Finds symbol definition, direct callers, and outgoing dependencies."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            # 1. Look up node
            cur.execute("SELECT * FROM code_nodes WHERE name = ? LIMIT 5", (symbol_name,))
            definitions = [dict(r) for r in cur.fetchall()]

            if not definitions:
                # Fallback search substring
                cur.execute("SELECT * FROM code_nodes WHERE name LIKE ? LIMIT 5", (f"%{symbol_name}%",))
                definitions = [dict(r) for r in cur.fetchall()]

            callers = []
            dependencies = []

            for d in definitions:
                nid = d["node_id"]
                # Who calls or references this?
                cur.execute("""
                    SELECT e.relation_type, e.context, n.node_id, n.name, n.file_path, n.start_line
                    FROM code_edges e
                    JOIN code_nodes n ON e.source_id = n.node_id
                    WHERE e.target_id = ? OR e.target_id LIKE ?
                    LIMIT 20
                """, (nid, f"%{symbol_name}%"))
                callers.extend([dict(r) for r in cur.fetchall()])

                # What does this depend on?
                cur.execute("""
                    SELECT e.relation_type, e.target_id, e.context
                    FROM code_edges e
                    WHERE e.source_id = ?
                    LIMIT 20
                """, (nid,))
                dependencies.extend([dict(r) for r in cur.fetchall()])

        return {
            "symbol": symbol_name,
            "definitions": definitions,
            "callers": callers,
            "dependencies": dependencies,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Returns node and edge counts and top languages."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM code_nodes;")
            total_nodes = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM code_edges;")
            total_edges = cur.fetchone()[0]

            cur.execute("SELECT node_type, COUNT(*) FROM code_nodes GROUP BY node_type;")
            type_breakdown = {r[0]: r[1] for r in cur.fetchall()}

            cur.execute("SELECT relation_type, COUNT(*) FROM code_edges GROUP BY relation_type;")
            rel_breakdown = {r[0]: r[1] for r in cur.fetchall()}

        return {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "node_types": type_breakdown,
            "relation_types": rel_breakdown,
        }

    def export_graph_json(self) -> Dict[str, Any]:
        """Exports graph in node-link format for visualization."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT node_id, name, node_type, file_path, start_line, language FROM code_nodes;")
            nodes = [dict(r) for r in cur.fetchall()]

            cur.execute("SELECT source_id, target_id, relation_type, context FROM code_edges;")
            edges = [dict(r) for r in cur.fetchall()]

        return {"nodes": nodes, "links": edges}


def main():
    if len(sys.argv) < 2:
        print("Usage: python code_graph.py [build|stats|query <symbol>]")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    engine = CodeGraphEngine()

    if cmd == "build":
        path = sys.argv[2] if len(sys.argv) > 2 else None
        res = engine.build_graph(root_dir=Path(path) if path else None)
        print(f"\nBuilt Codebase Knowledge Graph:")
        print(f"- Files Scanned: {res['files_scanned']}")
        print(f"- Nodes Indexed: {res['nodes_indexed']}")
        print(f"- Edges Indexed: {res['edges_indexed']}\n")

    elif cmd == "stats":
        stats = engine.get_stats()
        print(f"\nCodebase Knowledge Graph Statistics:")
        print(f"- Total Nodes: {stats['total_nodes']}")
        print(f"- Total Edges: {stats['total_edges']}")
        print(f"- Node Breakdown: {stats['node_types']}")
        print(f"- Edge Breakdown: {stats['relation_types']}\n")

    elif cmd == "query":
        sym = sys.argv[2] if len(sys.argv) > 2 else "main"
        res = engine.query_symbol(sym)
        print(f"\nQuery Symbol: '{sym}' (Found {len(res['definitions'])} definitions, {len(res['callers'])} callers):")
        for d in res["definitions"]:
            print(f"- [{d['node_type'].upper()}] {d['name']} in {d['file_path']}:{d['start_line']}")
            if d.get("signature"):
                print(f"  Signature: {d['signature']}")
        if res["callers"]:
            print("Referenced/Called by:")
            for c in res["callers"][:5]:
                print(f"  * {c.get('name', c.get('node_id'))} ({c['file_path']}) [{c['relation_type']}]")
        print()


if __name__ == "__main__":
    main()
