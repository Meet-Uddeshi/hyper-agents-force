#!/usr/bin/env python3
"""
Unit tests for Automated Session Learner.
"""

import sys
import tempfile
from pathlib import Path

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORKSPACE_DIR))

from bin.memory_manager import MemoryManager
from bin.session_learner import SessionLearner


def test_session_learner_records_and_sanitizes_failure():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    with tempfile.TemporaryDirectory() as mem_dir:
        try:
            res = SessionLearner.capture_eval_result(
                {"passed": False, "decisive_trace": "AssertionError: token user@example.com invalid"},
                cmd="pytest tests/test_auth.py",
                agent="eval-harness",
                db_path=db_path,
                memory_dir=Path(mem_dir),
            )
            assert res is not None
            assert res["status"] == "RECORDED"
            assert "[REDACTED_PII:EMAIL]" in res["sanitized_summary"]

            mm = MemoryManager(db_path=db_path)
            saved = mm.get_memory(res["key"])
            assert saved is not None
            assert saved["category"] == "failure"

            failures_md = Path(mem_dir) / "SESSION_FAILURES.md"
            assert failures_md.exists()
            assert res["key"] in failures_md.read_text(encoding="utf-8")
        finally:
            if db_path.exists():
                db_path.unlink()
