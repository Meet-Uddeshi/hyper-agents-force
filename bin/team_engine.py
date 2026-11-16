"""
Hyper Agents Force - Collaborative Agent Team Engine.

Provides decentralized peer-to-peer collaboration for agent teams:
  - Team Lead & Roster Management
  - Centralized Shared Task Board (Claim-based DAG execution)
  - Teammate-to-Teammate Direct Message Bus
  - Dual-mode SQLite + Markdown Synchronization (.agent/context/TEAM_BOARD.md)
  - Autonomous Intent-Driven Routing (Subagent vs. Agent Team)
"""

import os
import sys
import json
import sqlite3
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
AGENT_DIR = WORKSPACE_DIR / ".agent"
DB_PATH = AGENT_DIR / "memory" / "memory.db"
DEFAULT_TEAM_BOARD_PATH = AGENT_DIR / "context" / "TEAM_BOARD.md"


class TeamEngine:
    """Manages collaborative agent teams, task claiming, peer messages, and board synchronization."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_teams (
                team_id TEXT PRIMARY KEY,
                team_name TEXT NOT NULL,
                lead_agent TEXT NOT NULL,
                objective TEXT NOT NULL,
                status TEXT DEFAULT 'ACTIVE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_members (
                team_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                role_description TEXT NOT NULL,
                skills_json TEXT DEFAULT '[]',
                PRIMARY KEY (team_id, agent_name)
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_tasks (
                task_id TEXT PRIMARY KEY,
                team_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                depends_on TEXT DEFAULT '[]',
                claimed_by TEXT,
                status TEXT DEFAULT 'BLOCKED',
                input_artifacts TEXT DEFAULT '[]',
                output_artifacts TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id TEXT NOT NULL,
                from_agent TEXT NOT NULL,
                to_agent TEXT NOT NULL,
                reply_to INTEGER,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            conn.commit()

    def create_team(
        self,
        team_name: str,
        lead_agent: str,
        member_agents: Optional[List[Dict[str, Any]]] = None,
        objective: str = "",
        team_id: Optional[str] = None,
        members: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        tid = team_id or f"team-{re.sub(r'[^a-zA-Z0-9_-]', '-', team_name).lower()}-{datetime.utcnow().strftime('%y%m%d%H%M')}"
        roster = members if members is not None else (member_agents or [])
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO agent_teams (team_id, team_name, lead_agent, objective, status) VALUES (?, ?, ?, ?, 'ACTIVE')",
                (tid, team_name, lead_agent, objective)
            )

            # Ensure lead is in roster
            cursor.execute(
                "INSERT OR REPLACE INTO team_members (team_id, agent_name, role_description, skills_json) VALUES (?, ?, ?, ?)",
                (tid, lead_agent, "Team Lead & Coordinator", json.dumps(["task-coordination", "leadership", "verification"]))
            )

            for m in roster:
                aname = m.get("name") or m.get("agent_name")
                desc = m.get("role") or m.get("role_description") or "Specialist Worker"
                skills = m.get("skills", ["clean-code"])
                if aname:
                    cursor.execute(
                        "INSERT OR REPLACE INTO team_members (team_id, agent_name, role_description, skills_json) VALUES (?, ?, ?, ?)",
                        (tid, aname, desc, json.dumps(skills))
                    )
            conn.commit()

        self.sync_markdown_board(tid)
        return tid

    def list_teams(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agent_teams ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def add_task(
        self,
        team_id: str,
        title: str,
        description: str,
        depends_on: Optional[List[str]] = None,
        task_id: Optional[str] = None,
        input_artifacts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        tid = task_id or f"task-{re.sub(r'[^a-zA-Z0-9_-]', '-', title).lower()[:20]}-{datetime.utcnow().strftime('%M%S')}"
        deps = depends_on or []
        inputs = input_artifacts or []

        # Determine initial status: if no dependencies, it's UNCLAIMED; otherwise BLOCKED
        status = "UNCLAIMED"
        if deps:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                for dep in deps:
                    cursor.execute("SELECT status FROM team_tasks WHERE team_id = ? AND task_id = ?", (team_id, dep))
                    row = cursor.fetchone()
                    if not row or row["status"] != "DONE":
                        status = "BLOCKED"
                        break

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO team_tasks
                (task_id, team_id, title, description, depends_on, claimed_by, status, input_artifacts, output_artifacts, updated_at)
                VALUES (?, ?, ?, ?, ?, NULL, ?, ?, '[]', CURRENT_TIMESTAMP)
                """,
                (task_id, team_id, title, description, json.dumps(deps), status, json.dumps(inputs))
            )
            conn.commit()

        self.sync_markdown_board(team_id)
        return {
            "task_id": task_id,
            "team_id": team_id,
            "title": title,
            "status": status,
            "depends_on": deps
        }

    def get_unblocked_tasks(self, team_id: str) -> List[Dict[str, Any]]:
        unblocked = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM team_tasks WHERE team_id = ? AND status IN ('UNCLAIMED', 'BLOCKED')",
                (team_id,)
            )
            rows = cursor.fetchall()
            for r in rows:
                deps = json.loads(r["depends_on"] or "[]")
                all_done = True
                for dep in deps:
                    cursor.execute("SELECT status FROM team_tasks WHERE team_id = ? AND task_id = ?", (team_id, dep))
                    drow = cursor.fetchone()
                    if not drow or drow["status"] != "DONE":
                        all_done = False
                        break
                if all_done:
                    if r["status"] == "BLOCKED":
                        cursor.execute("UPDATE team_tasks SET status = 'UNCLAIMED' WHERE task_id = ?", (r["task_id"],))
                    unblocked.append(dict(r))
            conn.commit()
        return unblocked

    def claim_task(self, team_id: str, task_id: str, agent_name: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Verify dependencies are met
            cursor.execute("SELECT depends_on, status FROM team_tasks WHERE team_id = ? AND task_id = ?", (team_id, task_id))
            row = cursor.fetchone()
            if not row:
                return False
            deps = json.loads(row["depends_on"] or "[]")
            for dep in deps:
                cursor.execute("SELECT status FROM team_tasks WHERE team_id = ? AND task_id = ?", (team_id, dep))
                drow = cursor.fetchone()
                if not drow or drow["status"] != "DONE":
                    return False

            # Atomic claim
            cursor.execute(
                """
                UPDATE team_tasks
                SET status = 'IN_PROGRESS', claimed_by = ?, updated_at = CURRENT_TIMESTAMP
                WHERE team_id = ? AND task_id = ? AND status IN ('UNCLAIMED', 'BLOCKED')
                """,
                (agent_name, team_id, task_id)
            )
            success = cursor.rowcount > 0
            if success:
                # Log peer broadcast
                cursor.execute(
                    "INSERT INTO team_messages (team_id, from_agent, to_agent, content) VALUES (?, ?, 'ALL', ?)",
                    (team_id, agent_name, f"Claimed task [{task_id}]: Starting active execution.")
                )
            conn.commit()

        if success:
            self.sync_markdown_board(team_id)
        return success

    def complete_task(
        self,
        team_id: str,
        task_id: str,
        output_artifacts: Optional[List[str]] = None,
        notes: Optional[str] = None,
        agent_name: Optional[str] = None
    ) -> List[str]:
        outputs = output_artifacts or []
        unlocked = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT claimed_by, title FROM team_tasks WHERE team_id = ? AND task_id = ?", (team_id, task_id))
            row = cursor.fetchone()
            completing_agent = agent_name or (row["claimed_by"] if row and row["claimed_by"] else "system")
            task_title = row["title"] if row else task_id

            cursor.execute(
                """
                UPDATE team_tasks
                SET status = 'DONE', output_artifacts = ?, updated_at = CURRENT_TIMESTAMP
                WHERE team_id = ? AND task_id = ?
                """,
                (json.dumps(outputs), team_id, task_id)
            )

            # Announce completion
            msg = f"Completed task [{task_id}] '{task_title}'."
            if outputs:
                msg += f" Artifacts: {', '.join(outputs)}."
            if notes:
                msg += f" Notes: {notes}"
            cursor.execute(
                "INSERT INTO team_messages (team_id, from_agent, to_agent, content) VALUES (?, ?, 'ALL', ?)",
                (team_id, completing_agent, msg)
            )

            # Check dependent tasks to unlock
            cursor.execute("SELECT * FROM team_tasks WHERE team_id = ? AND status = 'BLOCKED'", (team_id,))
            blocked_rows = cursor.fetchall()
            for b in blocked_rows:
                deps = json.loads(b["depends_on"] or "[]")
                all_done = True
                for dep in deps:
                    cursor.execute("SELECT status FROM team_tasks WHERE team_id = ? AND task_id = ?", (team_id, dep))
                    drow = cursor.fetchone()
                    if not drow or drow["status"] != "DONE":
                        all_done = False
                        break
                if all_done:
                    cursor.execute("UPDATE team_tasks SET status = 'UNCLAIMED' WHERE task_id = ?", (b["task_id"],))
                    unlocked.append(b["task_id"])

            conn.commit()

        self.sync_markdown_board(team_id)
        return unlocked

    def send_message(
        self,
        team_id: str,
        from_agent: str,
        to_agent: str,
        content: str,
        reply_to: Optional[int] = None
    ) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO team_messages (team_id, from_agent, to_agent, reply_to, content) VALUES (?, ?, ?, ?, ?)",
                (team_id, from_agent, to_agent, reply_to, content)
            )
            mid = cursor.lastrowid
            conn.commit()

        self.sync_markdown_board(team_id)
        return mid

    def get_board_data(self, team_id: str) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agent_teams WHERE team_id = ?", (team_id,))
            team = cursor.fetchone()
            if not team:
                return {}

            cursor.execute("SELECT * FROM team_members WHERE team_id = ? ORDER BY agent_name", (team_id,))
            members = [dict(r) for r in cursor.fetchall()]

            cursor.execute("SELECT * FROM team_tasks WHERE team_id = ? ORDER BY task_id", (team_id,))
            tasks = [dict(r) for r in cursor.fetchall()]

            cursor.execute("SELECT * FROM team_messages WHERE team_id = ? ORDER BY message_id DESC LIMIT 30", (team_id,))
            messages = [dict(r) for r in cursor.fetchall()]
            messages.reverse()

            return {
                "team": dict(team),
                "members": members,
                "tasks": tasks,
                "messages": messages
            }

    def render_markdown_board(self, team_id: str) -> str:
        data = self.get_board_data(team_id)
        if not data:
            return f"# Agent Team Board: {team_id} (Not Found)\n"

        t = data["team"]
        members = data["members"]
        tasks = data["tasks"]
        messages = data["messages"]

        lines = [
            f"# Live Agent Team Coordination Board",
            f"",
            f"- **Team ID:** `{t['team_id']}`",
            f"- **Team Name:** `{t['team_name']}`",
            f"- **Team Lead:** `{t['lead_agent']}`",
            f"- **Objective:** {t['objective']}",
            f"- **Status:** `{t['status']}`",
            f"- **Last Updated:** `{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}`",
            f"",
            f"## Team Roster",
            f"| Member Agent | Role / Domain Focus | Injected Skills |",
            f"| :--- | :--- | :--- |"
        ]

        for m in members:
            skills = ", ".join(json.loads(m["skills_json"] or "[]"))
            lines.append(f"| `{m['agent_name']}` | {m['role_description']} | `{skills}` |")

        lines.extend([
            f"",
            f"## Shared Task Board",
            f"| Task ID | Title & Description | Depends On | Claimed By | Status | Output Artifact |",
            f"| :--- | :--- | :--- | :--- | :--- | :--- |"
        ])

        if not tasks:
            lines.append(f"| - | No tasks created yet. | - | - | - | - |")
        else:
            for task in tasks:
                deps = ", ".join(json.loads(task["depends_on"] or "[]")) or "None"
                claimed = f"`{task['claimed_by']}`" if task["claimed_by"] else "Unclaimed"
                outs = ", ".join(json.loads(task["output_artifacts"] or "[]")) or "-"
                lines.append(f"| `{task['task_id']}` | **{task['title']}**: {task['description']} | {deps} | {claimed} | `{task['status']}` | {outs} |")

        lines.extend([
            f"",
            f"## Teammate Communication Stream (Peer-to-Peer)",
            f""
        ])

        if not messages:
            lines.append(f"- *No messages exchanged yet.*")
        else:
            for msg in messages:
                target = f"@{msg['to_agent']}" if msg['to_agent'] != 'ALL' else "ALL"
                lines.append(f"- `[{msg['timestamp']}] {msg['from_agent']} -> {target}`: {msg['content']}")

        lines.append("")
        return "\n".join(lines)

    def sync_markdown_board(self, team_id: str, filepath: Optional[Path] = None) -> str:
        md = self.render_markdown_board(team_id)
        out_path = filepath or DEFAULT_TEAM_BOARD_PATH
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        return str(out_path)

    @classmethod
    def classify_prompt_intent(cls, prompt: str) -> Dict[str, Any]:
        """
        Autonomously determines if a prompt is meant for the Subagent System or Agent Team System.
        
        Rules:
          1. Manual prefix override:
             - '@agent-name' -> Subagent mode
             - '$team-name' or '#team-name' -> Team mode
          2. Structure/Keyword detection:
             - Multi-role backlog, team objective, cross-functional dependencies -> Team mode
             - Single focused bug, component, query, or standard task -> Subagent mode
        """
        trimmed = prompt.strip()

        # Check explicit team prefix ($team or #team or $team:...)
        m_team = re.search(r"[\$#]team[:\-_]?([a-zA-Z0-9_\-]*)", trimmed, re.IGNORECASE)
        if m_team:
            team_label = m_team.group(1) or "collaborative-team"
            return {
                "system": "team",
                "mode": "EXPLICIT_TEAM_PREFIX",
                "identifier": team_label,
                "confidence": 1.0
            }

        # Check explicit subagent prefix (@agent-name)
        m_agent = re.search(r"@([a-zA-Z0-9_\-]+)", trimmed)
        if m_agent:
            agent_name = m_agent.group(1)
            return {
                "system": "subagent",
                "mode": "EXPLICIT_AGENT_PREFIX",
                "identifier": agent_name,
                "confidence": 1.0
            }

        # Template-based structural matching
        team_structural_indicators = [
            r"\bteam\s*objective\s*:",
            r"\bwork\s*backlog\s*:",
            r"\bcross-functional\s*roles\s*:",
            r"\bteam\s*delivery\s*gate\s*:",
            r"\bshared\s*task\s*board\b",
            r"\bcollaborative\s*team\b",
            r"\bteam\s*members?\s*:",
            r"\[\s*\]\s*task-\d+"
        ]

        team_score = 0
        for pattern in team_structural_indicators:
            if re.search(pattern, trimmed, re.IGNORECASE):
                team_score += 1

        if team_score >= 2 or re.search(r"\b(assemble\s*a\s*team|collaborative\s*agent\s*team|multi-agent\s*team\s*to\s*build)\b", trimmed, re.IGNORECASE):
            return {
                "system": "team",
                "mode": "TEMPLATE_AUTONOMOUS_DETECTION",
                "identifier": "dynamic-team",
                "confidence": min(1.0, 0.5 + (team_score * 0.2))
            }

        return {
            "system": "subagent",
            "mode": "TEMPLATE_AUTONOMOUS_DETECTION",
            "identifier": "specialist-agent",
            "confidence": 0.85
        }
