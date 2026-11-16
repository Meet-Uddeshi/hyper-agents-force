"""
Test Suite for Human-in-the-Loop (HITL) Middleware.

Verifies:
1. Checkpoint creation across DOMAIN_KNOWLEDGE, PLAN_APPROVAL, and VERIFICATION_SIGNOFF stages.
2. Approval workflow with human feedback.
3. Rejection / change-request workflow.
4. Stage, status, and team filtering.
5. CLI integration for hitl commands.
"""

import sys
import tempfile
import sqlite3
import json
from pathlib import Path
import pytest

SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = SCRIPT_DIR.parent.parent
BIN_DIR = WORKSPACE_DIR / "bin"
if str(BIN_DIR) not in sys.path:
    sys.path.insert(0, str(BIN_DIR))

from hitl_middleware import HitlMiddleware


@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    yield db_path
    if db_path.exists():
        try:
            db_path.unlink()
        except OSError:
            pass


def test_hitl_creation_and_retrieval(temp_db):
    hitl = HitlMiddleware(db_path=temp_db)

    # 1. Domain knowledge checkpoint
    cp1 = hitl.create_checkpoint(
        system_type="subagent",
        stage="DOMAIN_KNOWLEDGE",
        agent_name="database-architect",
        summary="Validate PostgreSQL JSONB schema vs normalization",
        context_payload={"tech_stack": "PostgreSQL, Prisma", "invariants": "Strict 3NF"}
    )
    assert cp1["checkpoint_id"].startswith("hitl-domain_knowled")
    assert cp1["status"] == "PENDING"
    assert cp1["stage"] == "DOMAIN_KNOWLEDGE"

    fetched = hitl.get_checkpoint(cp1["checkpoint_id"])
    assert fetched is not None
    assert fetched["agent_name"] == "database-architect"
    assert fetched["context_payload"]["tech_stack"] == "PostgreSQL, Prisma"


def test_hitl_approval_and_rejection(temp_db):
    hitl = HitlMiddleware(db_path=temp_db)

    # Plan approval checkpoint
    cp = hitl.create_checkpoint(
        system_type="team",
        stage="PLAN_APPROVAL",
        agent_name="architect",
        summary="Approve 4-step migration plan",
        team_id="team-alpha"
    )
    cid = cp["checkpoint_id"]

    # Test rejection
    res_rej = hitl.resolve_checkpoint(cid, status="REJECTED", user_feedback="Step 2 lacks backup")
    assert res_rej["status"] == "REJECTED"
    assert res_rej["user_feedback"] == "Step 2 lacks backup"
    assert not hitl.is_checkpoint_approved(cid)

    # Test subsequent approval
    res_app = hitl.resolve_checkpoint(cid, status="APPROVED", user_feedback="Backup added, approved")
    assert res_app["status"] == "APPROVED"
    assert hitl.is_checkpoint_approved(cid)


def test_hitl_filtering(temp_db):
    hitl = HitlMiddleware(db_path=temp_db)

    hitl.create_checkpoint(system_type="subagent", stage="DOMAIN_KNOWLEDGE", agent_name="agent-a", summary="DK 1")
    hitl.create_checkpoint(system_type="team", stage="VERIFICATION_SIGNOFF", agent_name="agent-b", summary="VS 1", team_id="team-1")

    pending = hitl.list_checkpoints(status="PENDING")
    assert len(pending) == 2

    dk_only = hitl.list_checkpoints(stage="DOMAIN_KNOWLEDGE")
    assert len(dk_only) == 1
    assert dk_only[0]["agent_name"] == "agent-a"

    team_only = hitl.list_checkpoints(team_id="team-1")
    assert len(team_only) == 1
    assert team_only[0]["stage"] == "VERIFICATION_SIGNOFF"


def test_hitl_render_prompt(temp_db):
    hitl = HitlMiddleware(db_path=temp_db)
    cp = hitl.create_checkpoint(
        system_type="team",
        stage="VERIFICATION_SIGNOFF",
        agent_name="test-engineer",
        summary="E2E test suite finished with 24/24 passing",
        context_payload={"test_command": "pytest -v", "test_outcome": "24 passed", "deliverables": ["tests/e2e.py"]}
    )
    prompt_card = hitl.render_checkpoint_prompt(cp["checkpoint_id"])
    assert "HUMAN-IN-THE-LOOP CHECKPOINT" in prompt_card
    assert "VERIFICATION_SIGNOFF" in prompt_card
    assert "pytest -v" in prompt_card
    assert "Action Required:" in prompt_card
