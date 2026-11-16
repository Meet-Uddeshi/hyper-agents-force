"""
Hyper Agents Force - Human-in-the-Loop (HITL) Middleware.

Provides deterministic human verification and alignment gates across both
Subagent and Agent Team workflows:
  1. Gate 1: DOMAIN_KNOWLEDGE - Verifies project domain models, invariants, and boundaries.
  2. Gate 2: PLAN_APPROVAL    - Pre-mutation approval of implementation plans and affected files.
  3. Gate 3: VERIFICATION_SIGNOFF - Post-execution verification with observable test evidence.
"""

import os
import sys
import json
import sqlite3
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
AGENT_DIR = WORKSPACE_DIR / ".agent"
DB_PATH = AGENT_DIR / "memory" / "memory.db"


class HitlMiddleware:
    """
    Human-in-the-Loop (HITL) Middleware for Subagent and Agent Team workflows.
    Ensures safe, aligned, and human-verified execution at critical gates.
    """

    STAGES = ["DOMAIN_KNOWLEDGE", "PLAN_APPROVAL", "VERIFICATION_SIGNOFF"]
    STATUSES = ["PENDING", "APPROVED", "REJECTED", "CLARIFIED"]

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_table()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_table(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS hitl_checkpoints (
                checkpoint_id TEXT PRIMARY KEY,
                system_type TEXT NOT NULL,
                team_id TEXT,
                agent_name TEXT NOT NULL,
                stage TEXT NOT NULL,
                summary TEXT NOT NULL,
                context_payload TEXT DEFAULT '{}',
                status TEXT DEFAULT 'PENDING',
                user_feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP
            );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_hitl_status ON hitl_checkpoints(status);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_hitl_stage ON hitl_checkpoints(stage);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_hitl_team ON hitl_checkpoints(team_id);")
            conn.commit()

    def create_checkpoint(
        self,
        system_type: str,
        stage: str,
        agent_name: str,
        summary: str,
        context_payload: Optional[Dict[str, Any]] = None,
        team_id: Optional[str] = None,
        checkpoint_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Registers a new Human-in-the-Loop checkpoint requiring user alignment or sign-off.
        """
        if stage not in self.STAGES:
            raise ValueError(f"Invalid HITL stage '{stage}'. Must be one of: {', '.join(self.STAGES)}")

        cid = checkpoint_id or f"hitl-{re.sub(r'[^a-zA-Z0-9_-]', '-', stage).lower()[:15]}-{datetime.utcnow().strftime('%y%m%d%H%M%S')}"
        payload = context_payload or {}

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO hitl_checkpoints
                (checkpoint_id, system_type, team_id, agent_name, stage, summary, context_payload, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDING')
                """,
                (cid, system_type, team_id, agent_name, stage, summary, json.dumps(payload))
            )

            # Record event in blackboard ledger if table exists
            try:
                cursor.execute(
                    """
                    INSERT INTO blackboard_events (session_id, agent, event_type, description, payload)
                    VALUES (?, ?, 'hitl_checkpoint_created', ?, ?)
                    """,
                    (team_id or "session", agent_name, f"HITL Checkpoint [{cid}] at stage {stage}: {summary}", json.dumps({"checkpoint_id": cid, "stage": stage}))
                )
            except sqlite3.OperationalError:
                pass

            conn.commit()

        return self.get_checkpoint(cid)

    def get_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM hitl_checkpoints WHERE checkpoint_id = ?", (checkpoint_id,))
            row = cursor.fetchone()
            if not row:
                return None
            res = dict(row)
            try:
                res["context_payload"] = json.loads(res.get("context_payload") or "{}")
            except Exception:
                res["context_payload"] = {}
            return res

    def list_checkpoints(
        self,
        status: Optional[str] = None,
        stage: Optional[str] = None,
        team_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM hitl_checkpoints WHERE 1=1"
        params = []
        if status:
            query += " AND status = ?"
            params.append(status.upper())
        if stage:
            query += " AND stage = ?"
            params.append(stage.upper())
        if team_id:
            query += " AND team_id = ?"
            params.append(team_id)
        if agent_name:
            query += " AND agent_name = ?"
            params.append(agent_name)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                try:
                    item["context_payload"] = json.loads(item.get("context_payload") or "{}")
                except Exception:
                    item["context_payload"] = {}
                results.append(item)
            return results

    def resolve_checkpoint(
        self,
        checkpoint_id: str,
        status: str,
        user_feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Resolves a pending checkpoint with human verification (APPROVED, REJECTED, or CLARIFIED).
        """
        st = status.upper()
        if st not in self.STATUSES:
            raise ValueError(f"Invalid status '{status}'. Must be one of: {', '.join(self.STATUSES)}")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE hitl_checkpoints
                SET status = ?, user_feedback = ?, resolved_at = CURRENT_TIMESTAMP
                WHERE checkpoint_id = ?
                """,
                (st, user_feedback or "", checkpoint_id)
            )
            if cursor.rowcount == 0:
                raise KeyError(f"Checkpoint not found: {checkpoint_id}")

            cursor.execute("SELECT * FROM hitl_checkpoints WHERE checkpoint_id = ?", (checkpoint_id,))
            row = cursor.fetchone()
            res = dict(row)

            # Record event in blackboard ledger
            try:
                cursor.execute(
                    """
                    INSERT INTO blackboard_events (session_id, agent, event_type, description, payload)
                    VALUES (?, ?, 'hitl_checkpoint_resolved', ?, ?)
                    """,
                    (res.get("team_id") or "session", res.get("agent_name", "user"), f"HITL Checkpoint [{checkpoint_id}] resolved as {st}. Feedback: {user_feedback or 'None'}", json.dumps({"checkpoint_id": checkpoint_id, "status": st}))
                )
            except sqlite3.OperationalError:
                pass

            conn.commit()

        try:
            res["context_payload"] = json.loads(res.get("context_payload") or "{}")
        except Exception:
            res["context_payload"] = {}
        return res

    def is_checkpoint_approved(self, checkpoint_id: str) -> bool:
        cp = self.get_checkpoint(checkpoint_id)
        return bool(cp and cp.get("status") == "APPROVED")

    def render_checkpoint_prompt(self, checkpoint_id: str) -> str:
        """
        Renders a structured, actionable verification card for user interaction.
        """
        cp = self.get_checkpoint(checkpoint_id)
        if not cp:
            return f"Checkpoint '{checkpoint_id}' not found."

        stage = cp["stage"]
        lines = [
            f"================================================================================",
            f"      HUMAN-IN-THE-LOOP CHECKPOINT: [{cp['checkpoint_id']}]",
            f"================================================================================",
            f"- System Architecture: {cp['system_type'].upper()}",
            f"- Responsible Agent:   @{cp['agent_name']}",
            f"- Execution Stage:     {stage}",
            f"- Current Status:      {cp['status']}",
            f"- Created At:          {cp['created_at']}",
            f"",
            f"Summary:",
            f"  {cp['summary']}",
            f""
        ]

        payload = cp.get("context_payload", {})
        if stage == "DOMAIN_KNOWLEDGE":
            lines.extend([
                "Domain Discovery Questions / Invariant Alignment:",
                f"- Tech Stack:        {payload.get('tech_stack', 'Not specified')}",
                f"- Invariants:        {payload.get('invariants', 'Standard Clean Code')}",
                f"- Questions for User: {payload.get('questions', 'None. Please confirm assumptions.')}",
            ])
        elif stage == "PLAN_APPROVAL":
            lines.extend([
                "Proposed Execution Plan & File Scope:",
                f"- Target Files:      {', '.join(payload.get('target_files', [])) or 'None'}",
                f"- Plan Steps:        {payload.get('plan_steps', 'Standard multi-step plan')}",
            ])
        elif stage == "VERIFICATION_SIGNOFF":
            lines.extend([
                "Verification Evidence & Delivery Sign-Off:",
                f"- Test Command:      {payload.get('test_command', 'pytest / npm test')}",
                f"- Test Outcome:      {payload.get('test_outcome', 'PASS')}",
                f"- Output Deliverables: {', '.join(payload.get('deliverables', [])) or 'None'}",
            ])

        if cp.get("user_feedback"):
            lines.extend([
                f"",
                f"User Feedback: {cp['user_feedback']}"
            ])

        lines.extend([
            f"",
            f"Action Required:",
            f"- Approve: hyper-agents-force hitl approve {cp['checkpoint_id']} --feedback \"Confirmed\"",
            f"- Reject:  hyper-agents-force hitl reject {cp['checkpoint_id']} --feedback \"Requesting changes...\"",
            f"================================================================================"
        ])

        return "\n".join(lines)
