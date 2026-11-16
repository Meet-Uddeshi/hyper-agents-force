# OPENAI CODEX INSTRUCTIONS - HYPER AGENTS FORCE

## Coding Invariants & System Protocol
- Language Standards: PEP 8 for Python, Google Style for Java, strict typing for TypeScript.
- No Emojis: Strictly prohibited across all code, comments, and documentation.
- Zero Assumptions: Never guess requirements. Stop and clarify if specifications are incomplete.
- Architecture: Separation of Concerns. Keep controllers thin; place business invariants in Service layers.
- Data Leakage Prevention: Never print or log authorization headers, passwords, or secret keys.

## Agent System Integration
- Specialist Agents: Located under `./.agent/agents/` (110 agents).
- Domain Skills: Detailed procedures located in `./.agent/skills/` (377 skills).
- Collaborative Teams: Shared task board tracked in `./.agent/context/TEAM_BOARD.md` and `./.agent/memory/memory.db`.
- Human-in-the-Loop: Follow 3-gate verification (Domain Knowledge -> Plan Approval -> Verification Sign-off).
