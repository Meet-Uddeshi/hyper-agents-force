# CLAUDE CODE - HYPER AGENTS FORCE PLATFORM INSTRUCTIONS

## 0. Scope & Universal Invariants (CRITICAL)
- **Universal Application:** Applies across all tasks, greenfield and brownfield projects.
- **Zero Emojis:** Do not use emojis in code, comments, commit messages, or outputs. Technical English only.
- **Zero Assumptions:** Never guess missing parameters or business rules. Pause and inquire.
- **Data Leakage Prevention (DLP):** Sensitive data (API keys, PII, internal IDs) must never reach public logs or responses.
- **Coding Standards:** Python follows PEP 8; Java follows Google Style; TypeScript adheres to strict nulls.

---

## 1. Dual Execution Methodology: Subagents vs. Agent Teams

Hyper Agents Force provides two complementary execution modes:

### 1.1 Subagents System (Specialist Model)
- **Invocation:** Manual prefix `@agent-name <task>` or single-task prompt template.
- **Lifecycle:** Dispatches a single focused specialist with isolated context. The agent executes using designated skills from `./.agent/skills/` and reports back directly.
- **Agent Definitions:** Discovered in `./.agent/agents/<agent>.md` (110 specialist agents available).

### 1.2 Agent Teams System (Collaborative Team Model)
- **Invocation:** Manual prefix `$team-name <task>` or collaborative project prompt template.
- **Lifecycle:** Decentralized peer-to-peer team execution.
  - **Team Lead:** Formulates objectives, decomposes work into a DAG of tasks, and verifies delivery.
  - **Shared Task Board:** Centralized SQLite board synced to `./.agent/context/TEAM_BOARD.md`. Teammates claim unblocked tasks (`UNCLAIMED -> IN_PROGRESS -> DONE`).
  - **Teammate-to-Teammate Bus:** Direct P2P messaging via `team_messages` for code reviews and handoffs.

---

## 2. Human-in-the-Loop (HITL) 3-Gate Middleware

To prevent unaligned mutations, every execution must observe the 3-Gate HITL Middleware:
1. **Gate 1 (Domain Knowledge Discovery):** Validate project domain entities and invariants before coding. If requirements are ambiguous, log a checkpoint via `python bin/cli.py hitl request --stage DOMAIN_KNOWLEDGE` and ask the user.
2. **Gate 2 (Pre-Mutation Plan Approval):** For non-trivial modifications (> 2 files), present the file scope and step-by-step diff plan for user approval before mutating files.
3. **Gate 3 (Verification & Sign-Off):** Execute automated test suites (`pytest`, `npm test`), compile observable evidence, and request user sign-off before closing any task or team delivery.

---

## 3. Workflow Automation Commands

You can execute workflows programmatically via the dual runtime:
- **Planning:** `python .agent/scripts/workflow_engine.py run plan --args "<scope>"`
- **Testing:** `python .agent/scripts/workflow_engine.py run test --args "<scope>"`
- **Auditing:** `python .agent/scripts/workflow_engine.py run audit --args "<scope>"`
- **Debugging:** `python .agent/scripts/workflow_engine.py run debug --args "<scope>"`
- **Collaborative Team:** `python bin/cli.py team board --id <team_id>`
- **Structured Answers:** `python bin/cli.py answer "<query>"`

---

## 4. Resource Locations
- **Specialist Agents:** `./.agent/agents/` (110 agents)
- **Domain Skills:** `./.agent/skills/` (377 packages)
- **Persistent SQLite Memory:** `./.agent/memory/memory.db`
- **Shared Coordination Board:** `./.agent/context/TEAM_BOARD.md`
- **MCP Configuration:** `./.mcp.json` or `./.agent/mcp.json`
