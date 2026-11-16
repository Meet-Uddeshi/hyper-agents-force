#!/usr/bin/env python3
"""
Unit tests for Codebase Knowledge Graph Engine and Cypher Exporter.
"""

import sys
import tempfile
from pathlib import Path

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORKSPACE_DIR))

from bin.code_graph import CodeGraphEngine


def test_python_ast_parsing():
    """Verify AST parsing of Python classes, functions, and imports."""
    mock_py = """
import os
from pathlib import Path

class UserService:
    def __init__(self, db):
        self.db = db

    def get_user(self, user_id):
        return self.db.find(user_id)

def create_app():
    service = UserService(None)
    return service
"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        test_file = tmp_path / "app.py"
        test_file.write_text(mock_py, encoding="utf-8")

        db_path = tmp_path / "test_graph.db"
        engine = CodeGraphEngine(db_path=db_path)
        res = engine.build_graph(root_dir=tmp_path)

        assert res["status"] == "SUCCESS"
        assert res["files_scanned"] == 1
        assert res["nodes_indexed"] >= 3
        assert res["edges_indexed"] >= 3

        # Test query symbol
        q = engine.query_symbol("UserService")
        assert len(q["definitions"]) >= 1
        assert q["definitions"][0]["name"] == "UserService"
        assert q["definitions"][0]["node_type"] == "class"


def test_cypher_export():
    """Verify automatic generation of Cypher statements for Neo4j."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        test_file = tmp_path / "main.py"
        test_file.write_text("class Core:\n    pass\n", encoding="utf-8")

        db_path = tmp_path / "test_graph.db"
        engine = CodeGraphEngine(db_path=db_path)
        engine.build_graph(root_dir=tmp_path)

        cyp_path = tmp_path / "test.cyp"
        engine.export_cypher(output_path=cyp_path)

        assert cyp_path.exists()
        content = cyp_path.read_text(encoding="utf-8")
        assert "CREATE CONSTRAINT" in content
        assert "MERGE (n:Class" in content or "MERGE (n:File" in content


if __name__ == "__main__":
    test_python_ast_parsing()
    test_cypher_export()
    print("All code graph tests passed successfully.")
