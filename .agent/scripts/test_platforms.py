#!/usr/bin/env python3
"""
Unit and Integration Tests for Universal Multi-Platform Deployment.
Tests Cursor, Claude, Copilot, Codex, Gemini, and Antigravity adapter isolation.
"""

import sys
import tempfile
import shutil
from pathlib import Path

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORKSPACE_DIR))

from bin.installer import Installer
from bin.build_platforms import audit_platforms, MAX_RULE_BYTES


def test_platform_audit():
    """Verify all platform adapters meet zero-emoji and <=24,000 byte limits."""
    audit = audit_platforms()
    assert audit["passed"] is True
    assert len(audit["size_violations"]) == 0
    assert len(audit["emoji_violations"]) == 0
    assert audit["files_checked"] >= 12


def test_cursor_platform_deployment():
    """Verify Cursor deployment deploys ONLY cursor adapter files + .agent/."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        dest = Path(tmp_dir)
        res = Installer.install(target_level="project", custom_path=str(dest), platform="cursor", dry_run=False)

        assert res["status"] == "SUCCESS"
        assert res["platform"] == "cursor"
        assert (dest / ".agent").exists()
        assert (dest / ".cursorrules").exists()
        assert (dest / ".cursor" / "mcp.json").exists()
        assert (dest / ".cursor" / "rules" / "core.mdc").exists()
        assert (dest / ".cursor" / "rules" / "team.mdc").exists()

        # Ensure other platform adapters are NOT deployed
        assert not (dest / "GEMINI.md").exists()
        assert not (dest / "CLAUDE.md").exists()
        assert not (dest / ".github").exists()
        assert not (dest / ".codex").exists()


def test_claude_platform_deployment():
    """Verify Claude deployment deploys ONLY claude adapter files + .agent/."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        dest = Path(tmp_dir)
        res = Installer.install(target_level="project", custom_path=str(dest), platform="claude", dry_run=False)

        assert res["status"] == "SUCCESS"
        assert res["platform"] == "claude"
        assert (dest / ".agent").exists()
        assert (dest / "CLAUDE.md").exists()
        assert (dest / ".mcp.json").exists()

        # Ensure other platform adapters are NOT deployed
        assert not (dest / ".cursorrules").exists()
        assert not (dest / ".cursor").exists()
        assert not (dest / "GEMINI.md").exists()
        assert not (dest / ".github").exists()
        assert not (dest / ".codex").exists()


def test_copilot_platform_deployment():
    """Verify GitHub Copilot deployment deploys ONLY copilot adapter files + .agent/."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        dest = Path(tmp_dir)
        res = Installer.install(target_level="project", custom_path=str(dest), platform="copilot", dry_run=False)

        assert res["status"] == "SUCCESS"
        assert res["platform"] == "copilot"
        assert (dest / ".agent").exists()
        assert (dest / ".github" / "copilot-instructions.md").exists()

        # Ensure other platform adapters are NOT deployed
        assert not (dest / "CLAUDE.md").exists()
        assert not (dest / ".cursorrules").exists()
        assert not (dest / "GEMINI.md").exists()
        assert not (dest / ".codex").exists()


def test_codex_platform_deployment():
    """Verify OpenAI Codex deployment deploys ONLY codex adapter files + .agent/."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        dest = Path(tmp_dir)
        res = Installer.install(target_level="project", custom_path=str(dest), platform="codex", dry_run=False)

        assert res["status"] == "SUCCESS"
        assert res["platform"] == "codex"
        assert (dest / ".agent").exists()
        assert (dest / ".codex" / "instructions.md").exists()

        # Ensure other platform adapters are NOT deployed
        assert not (dest / "CLAUDE.md").exists()
        assert not (dest / ".cursorrules").exists()
        assert not (dest / "GEMINI.md").exists()
        assert not (dest / ".github").exists()


def test_all_platforms_deployment():
    """Verify --all deploys all platform adapters into destination."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        dest = Path(tmp_dir)
        res = Installer.install(target_level="project", custom_path=str(dest), platform="all", dry_run=False)

        assert res["status"] == "SUCCESS"
        assert res["platform"] == "all"
        assert (dest / ".agent").exists()
        assert (dest / "GEMINI.md").exists()
        assert (dest / "CLAUDE.md").exists()
        assert (dest / ".cursorrules").exists()
        assert (dest / ".cursor" / "rules" / "core.mdc").exists()
        assert (dest / ".github" / "copilot-instructions.md").exists()
        assert (dest / ".codex" / "instructions.md").exists()


if __name__ == "__main__":
    test_platform_audit()
    test_cursor_platform_deployment()
    test_claude_platform_deployment()
    test_copilot_platform_deployment()
    test_codex_platform_deployment()
    test_all_platforms_deployment()
    print("All multi-platform tests passed successfully.")
