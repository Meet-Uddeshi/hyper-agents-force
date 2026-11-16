#!/usr/bin/env python3
"""
Unit tests for Autonomous Self-Healing & Auto-Eval Test Harness.
"""

import sys
from pathlib import Path

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORKSPACE_DIR))

from bin.eval_harness import AutoEvalHarness


def test_command_detection():
    """Verify test runner auto-detection."""
    cmd = AutoEvalHarness.detect_test_command(WORKSPACE_DIR)
    assert cmd is not None
    assert "pytest" in cmd or "python" in cmd


def test_eval_success_and_hitl():
    """Verify clean passing command sets VERIFIED status and logs to HITL."""
    res = AutoEvalHarness.run_eval(custom_command="python -V", agent_name="test-eval")
    assert res["passed"] is True
    assert res["status"] == "VERIFIED"
    assert res["attempts"] == 1
    assert res.get("checkpoint_id") is not None


if __name__ == "__main__":
    test_command_detection()
    test_eval_success_and_hitl()
    print("All eval harness tests passed successfully.")
