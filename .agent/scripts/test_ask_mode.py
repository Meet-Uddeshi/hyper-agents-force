#!/usr/bin/env python3
"""
Unit tests for Read-Only Ask Mode Engine.
"""

import sys
from pathlib import Path

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORKSPACE_DIR))

from bin.ask_engine import AskEngine


def test_ask_query_read_only():
    """Verify Ask Mode returns structured answer without modifying any files."""
    query = "Explain how Installer class operates in installer.py"
    res = AskEngine.answer_query(query)

    assert res["mode"] == "READ_ONLY_ASK_MODE"
    assert res["files_modified"] == 0
    assert "Installer" in res["dense_output"]
    # Verify no greetings or ceremony
    assert not res["dense_output"].startswith("Sure")
    assert not res["dense_output"].startswith("Hello")


if __name__ == "__main__":
    test_ask_query_read_only()
    print("All ask mode tests passed successfully.")
