#!/usr/bin/env python3
"""
Deterministic Pre-AI & Post-AI Hook Engine for Hyper Agents Force.

Enforces security guardrails, rule compliance, skill/workflow routing,
zero-emoji policy, 24KB rule size caps, and test verification via code
rather than relying solely on soft markdown instructions.

Exit Codes:
  0 -> Allow / Pass
  2 -> Deterministic Block (Security, Policy, or Verification Failure)
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
for _p in (str(WORKSPACE_DIR), str(WORKSPACE_DIR / "bin")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from bin.security_guardrails import SecurityGuardrails
    from bin.memory_manager import MemoryManager
    from bin.hitl_middleware import HitlMiddleware
    from bin.context_bundler import ContextBundler
    from bin.session_learner import SessionLearner
    from bin.eval_harness import AutoEvalHarness
    from bin.log4j_scanner import Log4jScanner
except ImportError:
    from security_guardrails import SecurityGuardrails
    from memory_manager import MemoryManager
    from hitl_middleware import HitlMiddleware
    from context_bundler import ContextBundler
    from session_learner import SessionLearner
    from eval_harness import AutoEvalHarness
    from log4j_scanner import Log4jScanner

MAX_RULE_BYTES = 24000
EMOJI_PATTERN = re.compile(
    r"[\U00010000-\U0010ffff]|[\u2600-\u27bf]|[\u2300-\u23ff]|[\u2b50-\u2b55]"
)

DANGEROUS_SHELL_PATTERNS = [
    re.compile(r"(?i)\brm\s+-[rf]{1,2}\s+(/|~|\$HOME|\*)(\s|$)"),
    re.compile(r"(?i)\bgit\s+push\s+.*(--force|-f)\b"),
    re.compile(r"(?i)\bgit\s+reset\s+--hard\s+origin\b"),
    re.compile(r"(?i)\b(mkfs|fdisk|format)\b"),
    re.compile(r"(?i)\b(cat|type|head|tail|more|less|Get-Content|gc)\s+[^\n]*\.env(\.|$|\s)"),
    re.compile(r"(?i)\b(printenv|env)\b\s*($|\|)"),
]

FILLER_PHRASES = [
    re.compile(r"(?i)\b(sure!|certainly!|happy to help|hope this helps|let me now)\b"),
]


class HookEngine:
    """Deterministic Pre-AI, Tool-Boundary, and Post-AI guardrail engine."""

    @staticmethod
    def _log_hook_event(
        event_type: str,
        description: str,
        payload: Dict[str, Any],
        agent: str = "hook-engine",
        db_path: Optional[Path] = None,
    ) -> None:
        try:
            mem = MemoryManager(db_path=db_path)
            mem.log_event(
                session_id="hook-guardrail",
                agent=agent,
                event_type=event_type,
                description=description,
                payload=payload,
            )
        except Exception:
            pass

    @classmethod
    def pre_prompt(
        cls,
        prompt: str,
        agent: Optional[str] = None,
        db_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """Runs before the AI model sees the user prompt."""
        if not prompt or not prompt.strip():
            return {"stage": "pre-prompt", "decision": "allow", "exit_code": 0, "reason": "Empty prompt"}

        chk = SecurityGuardrails.check_prompt_injection(prompt)
        if not chk["is_safe"]:
            cls._log_hook_event(
                "HOOK_BLOCKED_INJECTION",
                f"Blocked prompt injection (risk={chk['risk_score']:.2f})",
                {"threats": chk["detected_threats"]},
                agent=agent or "hook-engine",
                db_path=db_path,
            )
            return {
                "stage": "pre-prompt",
                "decision": "block",
                "exit_code": 2,
                "reason": f"Prompt injection detected: {', '.join(chk['detected_threats'])}",
                "risk_score": chk["risk_score"],
            }

        bundle = ContextBundler.bundle(prompt, agent=agent, db_path=db_path)
        return {
            "stage": "pre-prompt",
            "decision": "allow",
            "exit_code": 0,
            "reason": "Prompt verified safe; context bundled.",
            "sanitized_prompt": bundle["prompt"],
            "routing": bundle["routing"],
            "context_markdown": ContextBundler.render_markdown(bundle),
        }

    @classmethod
    def pre_tool_use(
        cls,
        tool_name: str = "",
        file_path: str = "",
        command: str = "",
        checkpoint_id: str = "",
        agent: str = "hook-engine",
        db_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """Runs before file read/write or shell execution."""
        if file_path and SecurityGuardrails.is_shielded_file(file_path):
            cls._log_hook_event(
                "HOOK_BLOCKED_SHIELDED_FILE",
                f"Blocked {tool_name or 'tool'} access to shielded file: {file_path}",
                {"tool": tool_name, "file": file_path},
                agent=agent,
                db_path=db_path,
            )
            return {
                "stage": "pre-tool",
                "decision": "block",
                "exit_code": 2,
                "reason": f"Access to shielded credential file is prohibited: {file_path}",
            }

        if command:
            for pat in DANGEROUS_SHELL_PATTERNS:
                if pat.search(command):
                    cls._log_hook_event(
                        "HOOK_BLOCKED_COMMAND",
                        "Blocked unsafe or secret-exposing shell command",
                        {"command": command[:160]},
                        agent=agent,
                        db_path=db_path,
                    )
                    return {
                        "stage": "pre-tool",
                        "decision": "block",
                        "exit_code": 2,
                        "reason": f"Command blocked by security guardrail policy: {command[:120]}",
                    }

        if checkpoint_id:
            hitl = HitlMiddleware(db_path=db_path)
            if not hitl.is_checkpoint_approved(checkpoint_id):
                return {
                    "stage": "pre-tool",
                    "decision": "block",
                    "exit_code": 2,
                    "reason": f"HITL checkpoint `{checkpoint_id}` is not approved.",
                }

        return {
            "stage": "pre-tool",
            "decision": "allow",
            "exit_code": 0,
            "reason": "Tool call passed security and HITL checks.",
        }

    @classmethod
    def post_tool_use(
        cls,
        file_path: str = "",
        content: Optional[str] = None,
        agent: str = "hook-engine",
        db_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """Runs after file write/edit to enforce zero-emoji, 24KB cap, secret scan, and Log4j checks."""
        violations: List[str] = []
        p = Path(file_path) if file_path else None

        text = content
        if text is None and p and p.exists() and p.is_file():
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                text = ""

        if text:
            if EMOJI_PATTERN.search(text):
                violations.append(f"Zero-Emoji policy violation in {file_path or 'content'}")

            # Check hardcoded secrets (skip security_guardrails regex definition file)
            if not p or p.name not in ("security_guardrails.py", ".env.example"):
                _, leaks = SecurityGuardrails.mask_secrets(text)
                if leaks:
                    leak_types = ", ".join(sorted(set(item["type"] for item in leaks)))
                    violations.append(f"Secret leak detected ({leak_types}) in {file_path or 'content'}")

        if p:
            norm = str(p).replace("\\", "/").lower()
            is_rule_file = (
                p.suffix.lower() in (".md", ".mdc", ".cursorrules")
                and any(seg in norm for seg in ("/rules/", "global-rules/", "platforms/", "gemini.md", "claude.md"))
            )
            if is_rule_file:
                byte_len = p.stat().st_size if (content is None and p.exists()) else len((text or "").encode("utf-8"))
                if byte_len > MAX_RULE_BYTES:
                    violations.append(
                        f"Rule file size violation in {file_path}: {byte_len} bytes (max {MAX_RULE_BYTES})"
                    )

            if p.name.lower() in ("pom.xml", "build.gradle", "build.gradle.kts", "gradle.properties") and p.exists():
                vulns = Log4jScanner.scan_file(p)
                if vulns:
                    violations.append(f"Vulnerable Log4j dependency in {p.name} ({len(vulns)} findings)")

        if violations:
            cls._log_hook_event(
                "HOOK_POST_TOOL_VIOLATION",
                "; ".join(violations),
                {"file": file_path, "violations": violations},
                agent=agent,
                db_path=db_path,
            )
            return {
                "stage": "post-tool",
                "decision": "block",
                "exit_code": 2,
                "reason": "; ".join(violations),
                "violations": violations,
            }

        return {
            "stage": "post-tool",
            "decision": "allow",
            "exit_code": 0,
            "reason": "Post-tool compliance checks passed.",
        }

    @classmethod
    def stop(
        cls,
        run_eval: bool = False,
        cmd: Optional[str] = None,
        response_text: str = "",
        agent: str = "hook-engine",
        db_path: Optional[Path] = None,
        memory_dir: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """Runs after AI finishes turn: advisory dense-style check, eval verification, and session learning."""
        warnings: List[str] = []

        if response_text:
            if EMOJI_PATTERN.search(response_text):
                return {
                    "stage": "stop",
                    "decision": "block",
                    "exit_code": 2,
                    "reason": "Zero-Emoji policy violation in AI response.",
                }
            for pat in FILLER_PHRASES:
                if pat.search(response_text):
                    warnings.append("Advisory: filler/ceremony phrase detected (violates dense-communication.md)")
                    break

        eval_summary = None
        if run_eval:
            eval_summary = AutoEvalHarness.run_eval(
                cmd=cmd,
                agent=agent,
                max_retries=0,
                register_hitl=False,
            )
            if not eval_summary.get("passed"):
                SessionLearner.capture_eval_result(
                    eval_summary,
                    cmd=cmd or "",
                    agent=agent,
                    db_path=db_path,
                    memory_dir=memory_dir,
                )
                return {
                    "stage": "stop",
                    "decision": "block",
                    "exit_code": 2,
                    "reason": f"Verification failed: {eval_summary.get('decisive_trace') or eval_summary.get('error')}",
                    "warnings": warnings,
                    "eval": eval_summary,
                }

        return {
            "stage": "stop",
            "decision": "allow",
            "exit_code": 0,
            "reason": "Stop gate passed.",
            "warnings": warnings,
            "eval": eval_summary,
        }


def _parse_stdin_json(has_cli_args: bool = False) -> Dict[str, Any]:
    """Reads optional hook JSON payload from stdin with a short non-blocking timeout."""
    if has_cli_args or sys.stdin is None or sys.stdin.isatty():
        return {}
    import threading
    result: List[str] = []

    def _reader():
        try:
            result.append(sys.stdin.read().strip())
        except Exception:
            pass

    t = threading.Thread(target=_reader, daemon=True)
    t.start()
    t.join(timeout=0.15)
    if not result or not result[0]:
        return {}
    try:
        return json.loads(result[0])
    except Exception:
        return {}


def main():
    parser = argparse.ArgumentParser(description="Deterministic Hook Engine for Hyper Agents Force")
    parser.add_argument("stage", choices=["pre-prompt", "pre-tool", "post-tool", "stop"], help="Hook lifecycle stage")
    parser.add_argument("--prompt", type=str, default="", help="User prompt text")
    parser.add_argument("--agent", type=str, default=None, help="Target agent name")
    parser.add_argument("--tool", type=str, default="", help="Tool name")
    parser.add_argument("--file", type=str, default="", help="Target file path")
    parser.add_argument("--command", type=str, default="", help="Shell command")
    parser.add_argument("--checkpoint", type=str, default="", help="HITL checkpoint ID")
    parser.add_argument("--response", type=str, default="", help="AI response text")
    parser.add_argument("--run-eval", action="store_true", help="Run test verification on stop")
    parser.add_argument("--eval-cmd", type=str, default=None, help="Explicit test command")
    parser.add_argument("--json", action="store_true", help="Output JSON result")

    args = parser.parse_args()
    has_cli_args = any([args.prompt, args.file, args.command, args.response, args.run_eval])
    stdin_data = _parse_stdin_json(has_cli_args=has_cli_args)

    prompt = args.prompt or stdin_data.get("prompt", "")
    tool_name = args.tool or stdin_data.get("tool_name", "")
    tool_input = stdin_data.get("tool_input") or {}
    file_path = args.file or tool_input.get("file_path") or tool_input.get("path") or ""
    command = args.command or tool_input.get("command") or ""

    if args.stage == "pre-prompt":
        res = HookEngine.pre_prompt(prompt=prompt, agent=args.agent)
    elif args.stage == "pre-tool":
        res = HookEngine.pre_tool_use(
            tool_name=tool_name,
            file_path=file_path,
            command=command,
            checkpoint_id=args.checkpoint,
            agent=args.agent or "hook-engine",
        )
    elif args.stage == "post-tool":
        res = HookEngine.post_tool_use(file_path=file_path, agent=args.agent or "hook-engine")
    else:
        res = HookEngine.stop(
            run_eval=args.run_eval,
            cmd=args.eval_cmd,
            response_text=args.response,
            agent=args.agent or "hook-engine",
        )

    if args.json or stdin_data:
        print(json.dumps(res, indent=2))
    else:
        tag = "[ALLOW]" if res["decision"] == "allow" else "[BLOCKED]"
        print(f"{tag} ({res['stage']}) {res['reason']}")
        if res.get("context_markdown"):
            print("\n" + res["context_markdown"])
        for w in res.get("warnings") or []:
            print(f"[WARN] {w}")

    sys.exit(res["exit_code"])


if __name__ == "__main__":
    main()
