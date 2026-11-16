---
description: Collaborative Agent Team Workflow. Orchestrates decentralized peer-to-peer team execution with a Team Lead, shared claim-based task board, and direct teammate messaging.
---

# Collaborative Agent Team Execution

You are operating in **COLLABORATIVE AGENT TEAM MODE**. In this mode, multiple specialist agents collaborate through a centralized shared task board and peer-to-peer message stream.

## Team Mission / Objective
$ARGUMENTS

---

## 1. Collaborative Team Structure & Core Roles

1. **Team Lead (Leadership & Verification)**:
   - Primary Agent overseeing architectural integrity, task decomposition, and delivery sign-off.
   - Decomposes the mission into discrete DAG tasks with explicit inputs, outputs, and dependencies.
   - Signs off on final verification before declaring the mission completed.

2. **Team Members (Specialized Teammates)**:
   - Autonomous individual workers equipped with specific skills and rules.
   - Query the shared task board for unblocked tasks (`meet team tasks --id <team_id> --unblocked`).
   - Claim tasks with atomic locks (`meet team claim --id <team_id> --task-id <id> --agent <agent_name>`).
   - Post completion artifacts and unblock dependent tasks (`meet team complete`).

3. **Centralized Shared Task Board**:
   - Backed by SQLite (`agent_teams`, `team_tasks`, `team_members`, `team_messages`).
   - Dual-mode synchronized to `.agent/context/TEAM_BOARD.md` for transparency.

4. **Teammate-to-Teammate Communication**:
   - Direct message bus allowing teammates to exchange reviews, APIs, and handoffs without token bloat.

---

## 2. Step-by-Step Implementation Sequence

1. **Initialize Team Roster**: Define team ID, human-readable name, Team Lead, and member roster with roles.
   ```bash
   meet team create --id team-alpha --name "Core Feature Team" --lead architect --objective "Implement secure auth and dashboard" --members "backend-specialist,frontend-specialist,security-auditor,test-engineer"
   ```

2. **Decompose Tasks & Dependencies**: Populate shared task board with directed dependencies.
   ```bash
   meet team task-add --id team-alpha --task-id task-001 --title "Database Schema" --desc "Design user and session tables"
   meet team task-add --id team-alpha --task-id task-002 --title "Auth API Endpoints" --desc "Implement login and registration" --deps "task-001"
   meet team task-add --id team-alpha --task-id task-003 --title "React Auth UI" --desc "Build login form component" --deps "task-002"
   meet team task-add --id team-alpha --task-id task-004 --title "Security Audit & E2E Tests" --desc "Run OWASP audit and Playwright tests" --deps "task-002,task-003"
   ```

3. **Synchronize Shared Task Board**: Render shared Markdown view for immediate developer and agent visibility.
   ```bash
   meet team board --id team-alpha --sync
   ```

4. **Autonomous Task Claiming & Execution**:
   - Teammate queries unblocked tasks.
   - Teammate claims task atomically.
   - Teammate implements required code following strict TDD and clean code rules.

5. **Peer Review & Teammate Communication**:
   - Teammate sends notification or review request to peer.
   ```bash
   meet team msg --id team-alpha --from backend-specialist --to security-auditor --content "Auth endpoints ready for token validation review in src/api/auth.ts"
   ```

6. **Task Completion & Unblock Dependents**:
   - Record outputs and unblock downstream tasks.
   ```bash
   meet team complete --id team-alpha --task-id task-002 --agent backend-specialist --outputs "src/api/auth.ts,src/api/session.ts"
   ```

7. **Final Delivery & Verification Gate**:
   - Team Lead verifies all automated tests pass, zero regressions, and signs off.

---

## 3. Automation Scripts

- **Python CLI**: `python bin/cli.py team board --id team-alpha`
- **Node.js Runner**: `node bin/meet-ai-agents.js team board --id team-alpha`
