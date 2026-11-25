#!/usr/bin/env python3
"""
Unified Context Bundler for Hyper Agents Force.

Assembles a compact, token-budgeted context payload for any prompt by combining:
  - Bounded FTS5 persistent memories (LIMIT 5)
  - Recent blackboard coordination events
  - Matching AST knowledge graph symbols and callers
  - Autonomous specialist agent and workflow routing
  - Secret and PII sanitization via SecurityGuardrails
"""

import re
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = WORKSPACE_DIR / ".agent" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

try:
    from bin.memory_manager import MemoryManager
    from bin.code_graph import CodeGraphEngine
    from bin.security_guardrails import SecurityGuardrails
except ImportError:
    from memory_manager import MemoryManager
    from code_graph import CodeGraphEngine
    from security_guardrails import SecurityGuardrails

try:
    from workflow_engine import WorkflowEngine
except ImportError:
    WorkflowEngine = None

STOP_WORDS = {
    "the", "and", "for", "with", "this", "that", "from", "into", "what",
    "when", "where", "which", "have", "will", "should", "could", "would",
    "about", "need", "want", "make", "create", "update", "check", "file",
}


class ContextBundler:
    """Builds sanitized, token-bounded context bundles for agent prompts."""

    @staticmethod
    def extract_keywords(prompt: str, max_terms: int = 5) -> List[str]:
        """Extracts candidate code identifiers and domain keywords in one pass."""
        seen = set()
        ident: List[str] = []
        general: List[str] = []
        for tok in re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", prompt):
            if tok in seen or tok.lower() in STOP_WORDS:
                continue
            seen.add(tok)
            if "_" in tok or (not tok.islower() and not tok.isupper() and not tok.istitle()):
                ident.append(tok)
                if len(ident) >= max_terms:
                    return ident
            elif len(general) < max_terms:
                general.append(tok)
        return (ident + general)[:max_terms]

    @classmethod
    def bundle(
        cls,
        prompt: str,
        agent: Optional[str] = None,
        db_path: Optional[Path] = None,
        memory_limit: int = 5,
    ) -> Dict[str, Any]:
        """Assembles memories, AST symbols, events, and agent routing into one dict."""
        keywords = cls.extract_keywords(prompt)
        search_query = " ".join(keywords[:3]) if keywords else prompt[:60]

        mem_mgr = MemoryManager(db_path=db_path)
        memories = mem_mgr.query_memories(search_term=search_query, limit=memory_limit)
        if not memories:
            memories = mem_mgr.query_memories(limit=min(3, memory_limit))
        events = mem_mgr.query_events(limit=3)

        graph_matches: List[Dict[str, Any]] = []
        warnings: List[str] = []
        try:
            graph = CodeGraphEngine(db_path=db_path)
            for sym in keywords[:3]:
                res = graph.query_symbol(sym)
                if res.get("definitions"):
                    graph_matches.append({
                        "symbol": sym,
                        "definitions": res["definitions"][:2],
                        "callers_count": len(res.get("referenced_by", [])),
                    })
        except Exception as exc:
            warnings.append(f"CodeGraphEngine degraded: {exc}")

        routing: Dict[str, Any] = {}
        if WorkflowEngine:
            try:
                engine = WorkflowEngine()
                ans = engine.generate_answer(prompt, explicit_agent=agent)
                routing = {
                    "agent": ans.get("agent"),
                    "workflow": ans.get("workflow"),
                    "mode": ans.get("detection_mode"),
                }
            except Exception as exc:
                warnings.append(f"WorkflowEngine degraded: {exc}")

        sanitized_memories = []
        for m in memories:
            sanitized_memories.append({
                "key": m.get("key"),
                "category": m.get("category"),
                "content": SecurityGuardrails.sanitize_text(str(m.get("content", "")))[:240],
            })

        return {
            "prompt": SecurityGuardrails.sanitize_text(prompt),
            "keywords": keywords,
            "routing": routing,
            "memories": sanitized_memories,
            "recent_events": [
                {
                    "agent": e.get("agent"),
                    "type": e.get("event_type"),
                    "desc": SecurityGuardrails.sanitize_text(str(e.get("description", "")))[:120],
                }
                for e in events
            ],
            "graph_symbols": graph_matches,
            "warnings": warnings,
        }

    @classmethod
    def render_markdown(cls, bundle_data: Dict[str, Any]) -> str:
        """Formats a context bundle as a compact markdown block."""
        lines = ["### Context Bundle"]
        routing = bundle_data.get("routing") or {}
        if routing.get("agent"):
            lines.append(f"- **Agent**: `{routing['agent']}` | **Workflow**: `/{routing.get('workflow', 'none')}`")

        memories = bundle_data.get("memories") or []
        if memories:
            lines.append("- **Relevant Memories (Bounded)**:")
            for m in memories:
                lines.append(f"  - `{m['key']}` ({m['category']}): {m['content']}")

        symbols = bundle_data.get("graph_symbols") or []
        if symbols:
            lines.append("- **AST Graph Matches**:")
            for s in symbols:
                first_def = s["definitions"][0]
                lines.append(
                    f"  - `{s['symbol']}` ({first_def.get('node_type')}) at "
                    f"`{first_def.get('file_path')}:{first_def.get('start_line')}` "
                    f"[{s['callers_count']} refs]"
                )

        events = bundle_data.get("recent_events") or []
        if events:
            lines.append("- **Recent Blackboard Events**:")
            for e in events:
                lines.append(f"  - `{e['agent']}` [{e['type']}]: {e['desc']}")

        return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python context_bundler.py \"<prompt>\" [--json]")
        sys.exit(1)

    as_json = "--json" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--json"]
    prompt = " ".join(args)

    data = ContextBundler.bundle(prompt)
    if as_json:
        print(json.dumps(data, indent=2))
    else:
        print("\n" + ContextBundler.render_markdown(data) + "\n")


if __name__ == "__main__":
    main()
