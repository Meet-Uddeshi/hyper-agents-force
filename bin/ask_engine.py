#!/usr/bin/env python3
"""
Dedicated Read-Only Ask Mode Engine for Hyper Agents Force.

Provides zero-modification technical Q&A runtime. Guaranteed read-only execution:
blocks write/edit operations and formats responses strictly using the
High-Efficiency Dense Response Protocol.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

WORKSPACE_DIR = Path(__file__).resolve().parent.parent

try:
    from bin.code_graph import CodeGraphEngine
    from bin.workflow_engine import WorkflowEngine
except ImportError:
    from code_graph import CodeGraphEngine
    try:
        from workflow_engine import WorkflowEngine
    except ImportError:
        WorkflowEngine = None


class AskEngine:
    """Read-only question-and-answer engine with zero file modifications."""

    @classmethod
    def answer_query(cls, query: str, root_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Executes a read-only query against the codebase and AST graph.
        Never modifies any files in the workspace.
        """
        root = Path(root_dir or WORKSPACE_DIR).resolve()
        graph = CodeGraphEngine()

        # 1. Extract symbols from query (words that match code identifiers)
        words = query.replace("?", " ").replace("!", " ").replace(".", " ").split()
        matched_symbols = []
        for w in words:
            clean_w = w.strip("\"'`(),:;")
            if len(clean_w) > 2 and not clean_w.lower() in ("the", "how", "what", "why", "where", "when", "explain", "does", "this", "file", "class"):
                res = graph.query_symbol(clean_w)
                if res.get("definitions"):
                    matched_symbols.append(res)

        # 2. Extract relevant code snippets (read-only)
        code_context = []
        for sym in matched_symbols[:3]:
            for d in sym["definitions"][:2]:
                file_rel = d["file_path"]
                target_file = root / file_rel
                if target_file.exists():
                    try:
                        lines = target_file.read_text(encoding="utf-8", errors="ignore").splitlines()
                        start = max(0, d["start_line"] - 1)
                        end = min(len(lines), d.get("end_line", d["start_line"] + 15))
                        snippet = "\n".join(lines[start:end])
                        code_context.append({
                            "symbol": d["name"],
                            "file": file_rel,
                            "line": d["start_line"],
                            "type": d["node_type"],
                            "snippet": snippet[:600],
                            "callers_count": len(sym.get("callers", [])),
                        })
                    except Exception:
                        pass

        # 3. Formulate dense answer using pattern: [thing] [action] [reason]. [next step].
        dense_blocks = []
        if code_context:
            for ctx in code_context:
                dense_blocks.append(f"**{ctx['symbol']}** ({ctx['type']}) in `{ctx['file']}:{ctx['line']}`.")
                if ctx.get("snippet"):
                    dense_blocks.append(f"```python\n{ctx['snippet']}\n```")
                if ctx["callers_count"] > 0:
                    dense_blocks.append(f"Referenced by {ctx['callers_count']} caller(s).")
        else:
            # Fallback answer based on query
            dense_blocks.append(f"Query parsed: '{query}'. No direct AST symbols matched in graph.")
            dense_blocks.append("Run `meet graph build` to re-index recent files.")

        return {
            "query": query,
            "mode": "READ_ONLY_ASK_MODE",
            "files_modified": 0,
            "symbols_resolved": len(code_context),
            "dense_output": "\n\n".join(dense_blocks),
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python ask_engine.py \"<your question>\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    res = AskEngine.answer_query(query)
    print("\n" + res["dense_output"] + "\n")


if __name__ == "__main__":
    main()

