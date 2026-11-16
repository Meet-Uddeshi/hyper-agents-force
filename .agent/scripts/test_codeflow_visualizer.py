#!/usr/bin/env python3
"""
Unit tests for Interactive Visual Codeflow Graph Generator.
"""

import sys
import tempfile
from pathlib import Path

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORKSPACE_DIR))

from bin.codeflow_visualizer import CodeflowVisualizer


def test_html_generation():
    """Verify standalone Codeflow HTML is generated with embedded nodes and canvas."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_html = Path(tmp_dir) / "test_codeflow.html"
        generated = CodeflowVisualizer.generate(output_file=out_html)

        assert generated.exists()
        content = generated.read_text(encoding="utf-8")
        assert "<canvas id=\"graphCanvas\">" in content
        assert "Codeflow AST Graph Explorer" in content
        assert "rawNodes =" in content
        assert "rawLinks =" in content
        assert len(content) > 5000


if __name__ == "__main__":
    test_html_generation()
    print("All codeflow visualizer tests passed successfully.")
