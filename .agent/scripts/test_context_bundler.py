#!/usr/bin/env python3
"""
Unit tests for Unified Context Bundler.
"""

import sys
import tempfile
from pathlib import Path

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORKSPACE_DIR))

from bin.memory_manager import MemoryManager
from bin.context_bundler import ContextBundler


def test_context_bundler_assembles_bounded_sanitized_context():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    try:
        mm = MemoryManager(db_path=db_path)
        dummy_pw = "postgres://admin:secret_pw_123@localhost:5432/app"
        mm.log_memory(
            key="invariant:auth-rule",
            content=f"Auth middleware must validate expiry; never hardcode {dummy_pw}",
            category="invariant",
            agent="security-auditor",
            tags="auth,security",
        )

        bundle = ContextBundler.bundle(
            "Fix AuthMiddleware expiry validation bug",
            db_path=db_path,
            memory_limit=5,
        )
        assert "AuthMiddleware" in bundle["keywords"]
        assert len(bundle["memories"]) <= 5
        assert len(bundle["memories"]) >= 1
        assert "secret_pw_123" not in bundle["memories"][0]["content"]
        assert "[REDACTED_PASSWORD]" in bundle["memories"][0]["content"]

        md = ContextBundler.render_markdown(bundle)
        assert "### Context Bundle" in md
        assert "invariant:auth-rule" in md
    finally:
        if db_path.exists():
            db_path.unlink()
