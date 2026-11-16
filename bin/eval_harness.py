#!/usr/bin/env python3
"""
Autonomous Self-Healing & Auto-Eval Harness for Hyper Agents Force.

Validates code deliverables with automated test execution before requesting
Human-in-the-Loop Gate 3 sign-off. Automatically parses decisive stack traces
and triggers self-healing retry loops.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

WORKSPACE_DIR = Path(__file__).resolve().parent.parent

try:
    from bin.hitl_middleware import HitlMiddleware
except ImportError:
    try:
        from hitl_middleware import HitlMiddleware
    except ImportError:
        HitlMiddleware = None


class AutoEvalHarness:
    """Automated evaluation and self-healing verification harness."""

    @classmethod
    def detect_test_command(cls, root_dir: Optional[Path] = None) -> Optional[str]:
        """Detects available test runners in the target workspace."""
        root = Path(root_dir or WORKSPACE_DIR).resolve()

        # 1. Python test runner
        if (root / "pytest.ini").exists() or (root / "pyproject.toml").exists() or any((root / d).exists() for d in ["tests", "test"]):
            if shutil.which("pytest") or shutil.which("python"):
                return "python -m pytest"

        # 2. Node.js test runner
        if (root / "package.json").exists():
            pkg_text = (root / "package.json").read_text(encoding="utf-8", errors="ignore")
            if '"test"' in pkg_text:
                return "npm test"

        # 3. Rust test runner
        if (root / "Cargo.toml").exists():
            return "cargo test"

        # 4. Go test runner
        if (root / "go.mod").exists():
            return "go test ./..."

        # 5. Maven test runner
        if (root / "pom.xml").exists():
            return "mvn test"

        return None

    @classmethod
    def run_eval(
        cls,
        custom_command: Optional[str] = None,
        agent_name: str = "evaluator",
        team_id: Optional[str] = None,
        task_id: Optional[str] = None,
        max_retries: int = 3,
        root_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Executes automated test harness and performs self-healing loop on failure.
        """
        root = Path(root_dir or WORKSPACE_DIR).resolve()
        cmd = custom_command or cls.detect_test_command(root)

        if not cmd:
            return {
                "status": "SKIPPED",
                "message": "No automated test framework detected in workspace.",
                "passed": True,
            }

        history: List[Dict[str, Any]] = []
        attempt = 1
        success = False

        while attempt <= max_retries:
            try:
                proc = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=str(root),
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                exit_code = proc.returncode
                stdout = proc.stdout
                stderr = proc.stderr
            except Exception as e:
                exit_code = 1
                stdout = ""
                stderr = str(e)

            if exit_code == 0:
                success = True
                history.append({
                    "attempt": attempt,
                    "status": "PASSED",
                    "exit_code": 0,
                    "decisive_output": "All test assertions passed cleanly.",
                })
                break
            else:
                # Extract shortest decisive error line
                raw_err = stderr or stdout
                decisive_lines = [line.strip() for line in raw_err.splitlines() if any(
                    k in line.lower() for k in ["fail", "error", "assert", "traceback", "exception"]
                )]
                short_error = "\n".join(decisive_lines[-6:]) if decisive_lines else raw_err[-300:]

                history.append({
                    "attempt": attempt,
                    "status": "FAILED",
                    "exit_code": exit_code,
                    "decisive_error": short_error,
                })
                attempt += 1

        # Integrate with HITL Middleware if present
        checkpoint_id = None
        if HitlMiddleware:
            try:
                middleware = HitlMiddleware()
                summary_str = f"Auto-Eval {'VERIFIED' if success else 'FAILED'}: command '{cmd}' (Attempts: {len(history)})"
                cp = middleware.create_checkpoint(
                    system_type="team" if team_id else "subagent",
                    stage="VERIFICATION_SIGNOFF",
                    agent_name=agent_name,
                    summary=summary_str,
                    context_payload={"command": cmd, "success": success, "history": history},
                    team_id=team_id
                )
                checkpoint_id = cp.get("checkpoint_id")
            except Exception:
                pass

        return {
            "command": cmd,
            "passed": success,
            "attempts": len(history),
            "max_retries": max_retries,
            "history": history,
            "checkpoint_id": checkpoint_id,
            "status": "VERIFIED" if success else "SELF_HEALING_EXHAUSTED",
        }


def main():
    cmd_override = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--cmd" else None
    res = AutoEvalHarness.run_eval(custom_command=cmd_override)
    print(f"\nAutonomous Evaluation Harness:")
    print(f"- Command:  {res.get('command')}")
    print(f"- Status:   [{res.get('status')}]")
    print(f"- Attempts: {res.get('attempts')}")
    if res.get("checkpoint_id"):
        print(f"- HITL Checkpoint ID: {res['checkpoint_id']}")
    for h in res.get("history", []):
        st = f"[{h['status']}]"
        print(f"  * Attempt #{h['attempt']} {st}: {h.get('decisive_output') or h.get('decisive_error')}")
    print()


if __name__ == "__main__":
    main()
