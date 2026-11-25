#!/usr/bin/env python3
"""
AI Security & Guardrails Engine for Hyper Agents Force.

Provides Data Leakage Prevention (DLP), .env file isolation, secret and PII masking,
dummy credential emulation, and prompt injection defense.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

# Shielded sensitive filenames and patterns
SHIELDED_FILES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    ".env.staging",
    ".env.test",
    "id_rsa",
    "id_dsa",
    "id_ed25519",
}

SHIELDED_EXTENSIONS = {
    ".pem",
    ".key",
    ".pkcs12",
    ".p12",
    ".pfx",
    ".kdbx",
}

# Secret signatures
SECRET_PATTERNS = [
    ("AWS_ACCESS_KEY", re.compile(r"\b(AKIA[0-9A-Z]{16})\b")),
    ("AWS_SECRET_KEY", re.compile(r"(?i)aws_secret_access_key\s*=\s*['\"]?([A-Za-z0-9/+=]{40})['\"]?")),
    ("GITHUB_TOKEN", re.compile(r"\b(gh[pousr]_[A-Za-z0-9_]{36,255}|github_pat_[A-Za-z0-9_]{82})\b")),
    ("STRIPE_KEY", re.compile(r"\b(sk_live_[0-9a-zA-Z]{24,34})\b")),
    ("SLACK_TOKEN", re.compile(r"\b(xox[baprs]-[0-9a-zA-Z-]{10,72})\b")),
    ("JWT_TOKEN", re.compile(r"\b(eyJ[A-Za-z0-9-_=]{10,}\.eyJ[A-Za-z0-9-_=]{10,}\.[A-Za-z0-9-_.+/=]{10,})\b")),
    ("PRIVATE_KEY_BLOCK", re.compile(r"-----BEGIN [A-Z\s]+PRIVATE KEY-----[\s\S]*?-----END [A-Z\s]+PRIVATE KEY-----")),
    ("DB_CREDENTIAL_URL", re.compile(r"((?:postgres|mysql|mongodb|redis)://[^:]+:)([^@\s]+)(@)")),
]

# PII signatures
PII_PATTERNS = [
    ("EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")),
    ("IPV4_ADDR", re.compile(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")),
]

# Prompt injection signatures
INJECTION_PATTERNS = [
    re.compile(r"(?i)\bignore\s+(all\s+)?(previous|prior)\s+(instructions|prompts|directives)\b"),
    re.compile(r"(?i)\bdisregard\s+(all\s+)?(system|initial)\s+(rules|prompts|commands)\b"),
    re.compile(r"(?i)\byou\s+are\s+now\s+(in\s+)?(developer\s+mode|dan|unrestricted)\b"),
    re.compile(r"(?i)\breplay\s+(your\s+)?(system\s+prompt|initial\s+instructions)\b"),
    re.compile(r"(?i)\bprint\s+(your\s+)?(hidden|secret|internal)\s+(rules|instructions)\b"),
    re.compile(r"(?i)\bshow\s+me\s+the\s+contents\s+of\s+\.env\b"),
]


class SecurityGuardrails:
    """Enterprise AI security guardrails for credential and boundary enforcement."""

    @staticmethod
    def is_shielded_file(path_str: str) -> bool:
        """Returns True if the given file path points to a sensitive/shielded file."""
        p = Path(path_str)
        name = p.name.lower()
        if name in SHIELDED_FILES or name.startswith(".env."):
            return True
        if p.suffix.lower() in SHIELDED_EXTENSIONS:
            return True
        if "credentials.json" in name or "service-account" in name:
            return True
        return False

    @classmethod
    def mask_secrets(cls, content: str) -> Tuple[str, List[Dict[str, str]]]:
        """
        Redacts API keys, passwords, and private tokens from text.
        Returns the sanitized string and a log of detected secrets.
        """
        sanitized = content
        redactions = []

        for secret_type, pattern in SECRET_PATTERNS:
            if not pattern.search(sanitized):
                continue
            if secret_type == "DB_CREDENTIAL_URL":
                sanitized, count = pattern.subn(r"\1[REDACTED_PASSWORD]\3", sanitized)
                if count:
                    redactions.extend({"type": secret_type, "masked": "***"} for _ in range(count))
            else:
                def _repl(m, st=secret_type):
                    redactions.append({"type": st, "masked": m.group(0)[:4] + "..."})
                    return f"[REDACTED_SECRET:{st}]"
                sanitized = pattern.sub(_repl, sanitized)

        return sanitized, redactions

    @classmethod
    def mask_pii(cls, content: str) -> Tuple[str, List[Dict[str, str]]]:
        """Redacts emails and IP addresses."""
        sanitized = content
        redactions = []

        for pii_type, pattern in PII_PATTERNS:
            if not pattern.search(sanitized):
                continue
            if pii_type == "IPV4_ADDR":
                def _ip_repl(m):
                    ip = m.group(0)
                    if ip in ("127.0.0.1", "0.0.0.0", "255.255.255.255"):
                        return ip
                    redactions.append({"type": "IPV4_ADDR", "masked": ip})
                    return "[REDACTED_PII:IPV4_ADDR]"
                sanitized = pattern.sub(_ip_repl, sanitized)
            else:
                def _pii_repl(m, pt=pii_type):
                    redactions.append({"type": pt, "masked": m.group(0)})
                    return f"[REDACTED_PII:{pt}]"
                sanitized = pattern.sub(_pii_repl, sanitized)

        return sanitized, redactions

    @classmethod
    def check_prompt_injection(cls, prompt: str) -> Dict[str, Any]:
        """Scans user prompts for prompt injection, jailbreak attempts, and token traps."""
        detected = []
        for pat in INJECTION_PATTERNS:
            match = pat.search(prompt)
            if match:
                detected.append(match.group(0))

        risk_score = 0.0
        if detected:
            risk_score = min(1.0, 0.4 * len(detected))

        return {
            "is_safe": len(detected) == 0,
            "detected_threats": detected,
            "risk_score": risk_score,
        }

    @classmethod
    def audit_workspace(cls, workspace_root: Optional[Path] = None) -> Dict[str, Any]:
        """Audits workspace for unshielded credentials, exposed .env files, and leak hazards."""
        root = Path(workspace_root or Path.cwd()).resolve()
        findings = {
            "root": str(root),
            "shielded_files_found": [],
            "secrets_in_code": [],
            "risk_level": "LOW",
        }

        # Ignore virtualenvs and node_modules
        ignored_dirs = {".git", "node_modules", ".venv", "venv", "__pycache__", ".agent", ".worktrees"}

        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in ignored_dirs for part in path.parts):
                continue

            rel_str = str(path.relative_to(root))

            # 1. Check filename
            if cls.is_shielded_file(path.name):
                findings["shielded_files_found"].append(rel_str)

            # 2. Check content for hardcoded secrets
            if path.stat().st_size < 1_000_000:  # < 1MB
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                    _, leaks = cls.mask_secrets(text)
                    if leaks:
                        findings["secrets_in_code"].append({
                            "file": rel_str,
                            "leaks_count": len(leaks),
                            "types": list(set(item["type"] for item in leaks)),
                        })
                except Exception:
                    pass

        # Calculate risk level
        if findings["secrets_in_code"]:
            findings["risk_level"] = "CRITICAL"
        elif findings["shielded_files_found"]:
            findings["risk_level"] = "MEDIUM"

        return findings

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """Applies both secret and PII masking in one pass."""
        s1, _ = cls.mask_secrets(text)
        s2, _ = cls.mask_pii(s1)
        return s2


def main():
    if len(sys.argv) < 2:
        print("Usage: python security_guardrails.py [audit|check-prompt <text>|mask <file>]")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "audit":
        res = SecurityGuardrails.audit_workspace()
        print(f"\nAI Security & Guardrails Audit: {res['root']}")
        print(f"- Risk Level: [{res['risk_level']}]")
        print(f"- Shielded files detected: {len(res['shielded_files_found'])}")
        for f in res["shielded_files_found"]:
            print(f"  * {f}")
        print(f"- Hardcoded secrets in code: {len(res['secrets_in_code'])}")
        for item in res["secrets_in_code"]:
            print(f"  * {item['file']}: {item['leaks_count']} leak(s) ({', '.join(item['types'])})")
        print()
    elif cmd == "check-prompt":
        prompt = " ".join(sys.argv[2:])
        chk = SecurityGuardrails.check_prompt_injection(prompt)
        print(f"\nPrompt Safety Check: {'[SAFE]' if chk['is_safe'] else '[INJECTION_DETECTED]'}")
        print(f"- Risk Score: {chk['risk_score']:.2f}")
        if chk["detected_threats"]:
            print(f"- Detected Signatures: {', '.join(chk['detected_threats'])}")
        print()
    elif cmd == "mask":
        file_path = Path(sys.argv[2])
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            sanitized = SecurityGuardrails.sanitize_text(content)
            print(sanitized)


if __name__ == "__main__":
    main()
