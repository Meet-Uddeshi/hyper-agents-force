# GITHUB COPILOT INSTRUCTIONS - HYPER AGENTS FORCE

## Project Architecture & Engineering Standards

You are operating inside a repository powered by Hyper Agents Force. Adhere strictly to the following engineering standards across all generated code:

### 1. Invariants & Style
- Python: Strictly PEP 8 compliant.
- Java: Strictly Google Java Style.
- TypeScript: Strict typing with zero implicit any.
- Zero Emojis: Strictly prohibited in code, comments, documentation, and commit messages. Technical English only.
- Thin Controllers: Route handlers must be logic-free, delegating data transformation and rules to Service classes.
- Zero Assumptions: If in doubt, STOP and request clarification. Never speculate.

### 2. Dual Multi-Agent Methodology
- Subagents: Invoke specialist agents using `@agent-name` (e.g. `@fastapi-reviewer`, `@frontend-specialist`, `@debugger`). Agent configurations are in `./.agent/agents/`.
- Agent Teams: Collaborative team workflows are triggered by `$team-name`. Teams coordinate via `./.agent/context/TEAM_BOARD.md` and `./.agent/memory/memory.db`.

### 3. Human-in-the-Loop (HITL) Protocol
- Gate 1 (Domain Knowledge): Validate domain models and constraints before writing code.
- Gate 2 (Plan Approval): For changes across > 2 files, present an implementation plan before mutating code.
- Gate 3 (Verification Sign-Off): Execute automated test suites and present verified evidence before concluding work.

### 4. Shared Resources
- Domain Skills: Look up procedures in `./.agent/skills/<skill>/SKILL.md`.
- Memory Database: SQLite persistent storage in `./.agent/memory/memory.db`.
