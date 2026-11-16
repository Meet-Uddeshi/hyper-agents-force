#!/usr/bin/env python3
"""
GitHub Actions CI/CD Native Automation PR Bot for Hyper Agents Force.

Parses git diffs, classifies modified domains, routes files to specialist review agents,
executes automated verification tests, and generates structured PR comment review cards.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

WORKSPACE_DIR = Path(__file__).resolve().parent.parent

try:
    from bin.security_guardrails import SecurityGuardrails
    from bin.eval_harness import AutoEvalHarness
    from bin.log4j_scanner import Log4jScanner
except ImportError:
    from security_guardrails import SecurityGuardrails
    from eval_harness import AutoEvalHarness
    from log4j_scanner import Log4jScanner


class CIBot:
    """Automates pull request domain routing, security audit, and review card generation."""

    @classmethod
    def get_changed_files(cls, base_ref: str = "HEAD~1") -> List[str]:
        """Gets list of modified files using git diff if available."""
        try:
            res = subprocess.run(["git", "diff", "--name-only", base_ref], cwd=str(WORKSPACE_DIR), capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                return [f.strip() for f in res.stdout.splitlines() if f.strip()]
        except Exception:
            pass

        # Fallback: scan recently modified files in workspace
        files = []
        for p in WORKSPACE_DIR.rglob("*"):
            if p.is_file() and not any(k in p.parts for k in [".git", "node_modules", ".venv", ".agent"]):
                files.append(str(p.relative_to(WORKSPACE_DIR)))
        return files[:10]

    @classmethod
    def classify_diff_domains(cls, changed_files: List[str]) -> Dict[str, List[str]]:
        """Maps modified files to their target specialist domain agents."""
        domain_map = {
            "frontend-specialist": [],
            "backend-specialist": [],
            "security-specialist": [],
            "database-architect": [],
        }

        for f in changed_files:
            lower = f.lower()
            if lower.endswith((".tsx", ".jsx", ".vue", ".svelte", ".html", ".css", ".scss")):
                domain_map["frontend-specialist"].append(f)
            elif lower.endswith((".py", ".go", ".rs", ".java", ".cs", ".php", ".rb")):
                domain_map["backend-specialist"].append(f)

            if any(k in lower for k in ["auth", "token", "crypto", "secret", "perm", "session", "security", "guard", "login"]):
                domain_map["security-specialist"].append(f)
            if any(k in lower for k in ["migration", "schema", "model", "query", "sql", "db", "table", "entity"]):
                domain_map["database-architect"].append(f)

        return {k: v for k, v in domain_map.items() if v}

    @classmethod
    def run_pr_review(cls, changed_files: Optional[List[str]] = None) -> Dict[str, Any]:
        """Executes full automated PR review pass."""
        files = changed_files or cls.get_changed_files()
        domains = cls.classify_diff_domains(files)

        # 1. Security scan
        sec_audit = SecurityGuardrails.audit_workspace(WORKSPACE_DIR)
        log4j_res = Log4jScanner.scan_workspace(WORKSPACE_DIR)

        # 2. Automated evaluation harness
        eval_res = AutoEvalHarness.run_eval()

        # 3. Assemble review markdown
        md_lines = [
            "# Hyper Agents Force: Pull Request Review Card",
            "",
            f"**Modified Files Analyzed**: `{len(files)}`",
            f"**Automated Verification Status**: `[{eval_res.get('status', 'SKIPPED')}]`",
            f"**Security Guardrails Status**: `[{sec_audit['risk_level']}]` (Log4j CVEs: `{log4j_res['vulnerabilities_found']}`)",
            "",
            "## 1. Domain Specialist Routing",
        ]

        if domains:
            for agent, agent_files in domains.items():
                md_lines.append(f"- `@{agent}` assigned to review `{len(agent_files)}` file(s):")
                for af in agent_files[:3]:
                    md_lines.append(f"  * `{af}`")
        else:
            md_lines.append("- General review pass (no domain-specific boundaries triggered).")

        md_lines.extend([
            "",
            "## 2. Security & Guardrails Verification",
            f"- **Shielded Files Check**: `{len(sec_audit['shielded_files_found'])}` detected",
            f"- **Hardcoded Secret Leaks**: `{len(sec_audit['secrets_in_code'])}` detected",
            f"- **Log4j Vulnerability Check**: `{log4j_res['vulnerabilities_found']}` detected",
        ])

        md_lines.extend([
            "",
            "## 3. Human-in-the-Loop Sign-off Checklist",
            "- [ ] **Gate 1: Domain Knowledge Alignment** (Architectural boundaries and data flows verified)",
            "- [ ] **Gate 2: Implementation Plan Approved** (Changes adhere to SOLID & Zero Assumptions rule)",
            "- [ ] **Gate 3: Verification Sign-off** (Automated tests green and security checks passed)",
        ])

        review_markdown = "\n".join(md_lines)
        out_file = WORKSPACE_DIR / ".agent" / "context" / "PR_REVIEW_COMMENT.md"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(review_markdown, encoding="utf-8")

        return {
            "files": files,
            "domains": domains,
            "security": sec_audit,
            "log4j": log4j_res,
            "eval": eval_res,
            "review_markdown": review_markdown,
            "comment_file": str(out_file),
        }


def main():
    res = CIBot.run_pr_review()
    print("\n" + res["review_markdown"] + "\n")


if __name__ == "__main__":
    main()
