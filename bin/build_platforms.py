#!/usr/bin/env python3
"""
Platform Synchronization & Compliance Engine for Hyper Agents Force.

This script ensures all platform adapter directories (Cursor, Claude, Copilot, Codex, Gemini, Antigravity)
remain synchronized with the common engine, conform to zero-emoji standards, and strictly enforce the
24,000-byte rule file limit.
"""

import sys
import shutil
import re
from pathlib import Path
from typing import Dict, Any, List

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
PLATFORMS_DIR = WORKSPACE_DIR / "platforms"
SOURCE_GEMINI_MD = WORKSPACE_DIR / "GEMINI.md"
SOURCE_MCP_JSON = WORKSPACE_DIR / ".agent" / "mcp.json"

MAX_RULE_BYTES = 24000
EMOJI_PATTERN = re.compile(
    r"[\U00010000-\U0010ffff]|[\u2600-\u27bf]|[\u2300-\u23ff]|[\u2b50-\u2b55]"
)


def sync_core_adapters() -> List[str]:
    """Synchronizes shared configuration into platform adapter directories."""
    logs = []

    # Ensure platform directories exist
    for plat in ["gemini", "antigravity", "claude", "cursor", "copilot", "codex"]:
        (PLATFORMS_DIR / plat).mkdir(parents=True, exist_ok=True)

    # Sync GEMINI.md
    if SOURCE_GEMINI_MD.exists():
        gemini_dest = PLATFORMS_DIR / "gemini" / "GEMINI.md"
        shutil.copy2(SOURCE_GEMINI_MD, gemini_dest)
        logs.append(f"Synced GEMINI.md -> {gemini_dest}")

        antigrav_dest = PLATFORMS_DIR / "antigravity" / "GEMINI.md"
        shutil.copy2(SOURCE_GEMINI_MD, antigrav_dest)
        logs.append(f"Synced GEMINI.md -> {antigrav_dest}")

    # Sync MCP config
    if SOURCE_MCP_JSON.exists():
        claude_mcp = PLATFORMS_DIR / "claude" / ".mcp.json"
        shutil.copy2(SOURCE_MCP_JSON, claude_mcp)
        logs.append(f"Synced mcp.json -> {claude_mcp}")

        cursor_mcp = PLATFORMS_DIR / "cursor" / ".cursor" / "mcp.json"
        cursor_mcp.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE_MCP_JSON, cursor_mcp)
        logs.append(f"Synced mcp.json -> {cursor_mcp}")

    return logs


def audit_platforms() -> Dict[str, Any]:
    """Audits all platform adapter files for size limits and emoji bans."""
    audit_results = {
        "passed": True,
        "files_checked": 0,
        "size_violations": [],
        "emoji_violations": [],
        "file_summary": [],
    }

    for path in sorted(PLATFORMS_DIR.rglob("*")):
        if not path.is_file():
            continue

        audit_results["files_checked"] += 1
        size = path.stat().st_size
        rel_path = path.relative_to(PLATFORMS_DIR)

        # Check rule file size limit (applies to markdown and mdc rule files)
        if path.suffix.lower() in [".md", ".mdc", ".cursorrules"]:
            if size > MAX_RULE_BYTES:
                audit_results["passed"] = False
                audit_results["size_violations"].append(
                    {"file": str(rel_path), "size": size, "limit": MAX_RULE_BYTES}
                )

        # Check emoji violation
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            if EMOJI_PATTERN.search(content):
                audit_results["passed"] = False
                audit_results["emoji_violations"].append(str(rel_path))
        except Exception:
            pass

        audit_results["file_summary"].append({
            "platform": str(rel_path).split("\\")[0].split("/")[0],
            "file": str(rel_path),
            "size_bytes": size,
        })

    return audit_results


def main():
    print("================================================================================")
    print("       HYPER AGENTS FORCE - PLATFORM ADAPTER SYNCHRONIZATION & AUDIT            ")
    print("================================================================================")

    sync_logs = sync_core_adapters()
    for log in sync_logs:
        print(f"  - {log}")

    audit = audit_platforms()
    print(f"\nAudit complete across {audit['files_checked']} platform adapter files:")
    print(f"- Max rule size limit: {MAX_RULE_BYTES} bytes")
    print(f"- Size violations:     {len(audit['size_violations'])}")
    print(f"- Emoji violations:    {len(audit['emoji_violations'])}")

    if not audit["passed"]:
        if audit["size_violations"]:
            print("\n[ERROR] Rule size violations detected:")
            for v in audit["size_violations"]:
                print(f"  * {v['file']}: {v['size']} bytes (max {v['limit']} bytes)")
        if audit["emoji_violations"]:
            print("\n[ERROR] Emoji violations detected:")
            for f in audit["emoji_violations"]:
                print(f"  * {f}")
        sys.exit(1)

    print("\nAll platform adapters are synchronized, within byte limits, and emoji-free.\n")


if __name__ == "__main__":
    main()
