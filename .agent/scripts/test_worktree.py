#!/usr/bin/env python3
"""
Unit tests for Multi-Agent Git Worktree & Sandbox Workspace Isolation.
"""

import sys
from pathlib import Path

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORKSPACE_DIR))

from bin.worktree_manager import WorktreeManager


def test_worktree_lifecycle():
    """Verify creation, diff inspection, and clean teardown of isolated worktrees."""
    tid = "task-unit-test-01"

    # 1. Create
    res = WorktreeManager.create_worktree(task_id=tid, team_id="test-team", agent_name="tester")
    assert res["status"] == "READY"
    assert res["mode"] in ("GIT_WORKTREE", "DIRECTORY_SANDBOX")
    assert Path(res["path"]).exists()

    # 2. Diff
    diff_res = WorktreeManager.diff_worktree(task_id=tid)
    assert "diff" in diff_res

    # 3. Cleanup
    cleaned = WorktreeManager.cleanup_worktree(task_id=tid)
    assert cleaned is True
    assert not Path(res["path"]).exists()


if __name__ == "__main__":
    test_worktree_lifecycle()
    print("All worktree tests passed successfully.")
