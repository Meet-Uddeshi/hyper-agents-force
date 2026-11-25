#!/usr/bin/env python3
"""
Automated Session Learner for Hyper Agents Force.

Captures test failures, decisive error traces, and verified solutions into
persistent SQLite memory (memory.db) and syncs SESSION_FAILURES.md.
"""

import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MEMORY_DIR = WORKSPACE_DIR / ".agent" / "memory"

try:
    from bin.memory_manager import MemoryManager
    from bin.security_guardrails import SecurityGuardrails
except ImportError:
    from memory_manager import MemoryManager
    from security_guardrails import SecurityGuardrails


class SessionLearner:
    """Persists cross-session failures and verified resolutions safely."""

    @staticmethod
    def record_learning(
        key: str,
        summary: str,
        category: str = "failure",
        agent: str = "session-learner",
        tags: str = "auto-learned",
        db_path: Optional[Path] = None,
        memory_dir: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """Logs sanitized learning into SQLite and appends to SESSION_FAILURES.md if failure."""
        safe_summary = SecurityGuardrails.sanitize_text(summary.strip())
        mem_mgr = MemoryManager(db_path=db_path)

        mem_id = mem_mgr.log_memory(
            key=key,
            content=safe_summary,
            category=category,
            agent=agent,
            tags=tags,
        )
        mem_mgr.log_event(
            session_id="session-learner",
            agent=agent,
            event_type="LEARNING_CAPTURED",
            description=f"Recorded {category}: {key}",
            payload={"key": key, "category": category},
        )

        mem_root = Path(memory_dir or DEFAULT_MEMORY_DIR)
        mem_root.mkdir(parents=True, exist_ok=True)
        failures_md = mem_root / "SESSION_FAILURES.md"

        if category == "failure":
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if not failures_md.exists():
                failures_md.write_text("# Session Failures & Resolutions\n\n", encoding="utf-8")
            entry = f"- **[{timestamp}] `{key}`** ({agent}): {safe_summary}\n"
            with open(failures_md, "a", encoding="utf-8") as fh:
                fh.write(entry)

        return {
            "status": "RECORDED",
            "id": mem_id,
            "key": key,
            "category": category,
            "sanitized_summary": safe_summary,
        }

    @classmethod
    def capture_eval_result(
        cls,
        eval_result: Dict[str, Any],
        cmd: str = "",
        agent: str = "eval-harness",
        db_path: Optional[Path] = None,
        memory_dir: Optional[Path] = None,
    ) -> Optional[Dict[str, Any]]:
        """Automatically records decisive failure traces from AutoEvalHarness output."""
        if eval_result.get("passed"):
            return None

        trace = eval_result.get("decisive_trace") or eval_result.get("error") or "Test execution failed"
        first_line = str(trace).strip().splitlines()[-1][:200] if trace else "Unknown failure"
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        key = f"failure:eval-{stamp}"
        summary = f"Command `{cmd or eval_result.get('command', 'test')}` failed: {first_line}"

        return cls.record_learning(
            key=key,
            summary=summary,
            category="failure",
            agent=agent,
            tags="eval,test-failure",
            db_path=db_path,
            memory_dir=memory_dir,
        )


def main():
    if len(sys.argv) < 3:
        print("Usage: python session_learner.py <key> <summary> [--category failure|pattern] [--json]")
        sys.exit(1)

    as_json = "--json" in sys.argv
    category = "failure"
    args = []
    skip_next = False
    for idx, arg in enumerate(sys.argv[1:], start=1):
        if skip_next:
            skip_next = False
            continue
        if arg == "--json":
            continue
        if arg == "--category" and idx + 1 < len(sys.argv):
            category = sys.argv[idx + 1]
            skip_next = True
            continue
        args.append(arg)

    if len(args) < 2:
        print("Usage: python session_learner.py <key> <summary>")
        sys.exit(1)

    res = SessionLearner.record_learning(key=args[0], summary=" ".join(args[1:]), category=category)
    if as_json:
        print(json.dumps(res, indent=2))
    else:
        print(f"[OK] Recorded learning `{res['key']}` ({res['category']})")


if __name__ == "__main__":
    main()
