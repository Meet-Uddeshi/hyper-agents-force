---
trigger: always_on
---

# MULTI-AGENT SYSTEM PROTOCOL: RUNTIME COMPLEXITY ESCALATION, CONTEXT & MEMORY ENGINEERING

> **UNIVERSAL WORKSPACE INVARIANT:** This rule is always active across all agents and sessions. It governs how specialist agents detect runtime complexity, self-escalate to Superpower skills, communicate with peer agents, share context without token bloat, and maintain cognitive memory.

---

## 1. DYNAMIC RUNTIME COMPLEXITY ESCALATION PROTOCOL

Whenever ANY agent (whether single assistant, specialist, or subagent) encounters execution complexity, it is an **IRON RULE** that the agent must immediately suspend ad-hoc actions and invoke the designated Superpower skill via `read_file`:

| Runtime Complexity Trigger | Observable Threshold | Target Superpower Skill | Mandatory Action |
| :--- | :--- | :--- | :--- |
| **Design Ambiguity & Trade-offs** | Multiple architectural approaches, unclear requirements, or user trade-offs. | `brainstorming` (`.agent/skills/brainstorming/SKILL.md`) | Stop code generation. Propose 2-3 concrete options with pros/cons; get user alignment before proceeding. |
| **Multi-Step / Multi-File Work** | Implementation spans > 2 files or requires > 3 distinct steps. | `writing-plans` & `executing-plans` | Produce bite-sized implementation plan with explicit checkpoints; execute one step at a time. |
| **Runtime Crash / Failing Test / Bug** | Any uncaught exception, build error, or failing test assertion. | `systematic-debugging` & `root-cause-tracing` | Isolate minimal reproduction. Trace root cause with evidence before modifying any code. |
| **New Production Logic Implementation** | Authoring core services, controllers, algorithms, or API endpoints. | `test-driven-development` | Write failing automated test first (RED), implement minimal code to pass (GREEN), then refactor. |
| **Cross-Domain Task Delegation** | Independent work streams (e.g., UI frontend + API backend). | `subagent-driven-development` | Spawn specialized subagents with isolated context and bounded scopes. |
| **Pre-Completion Claim** | Agent is about to declare the task complete or create a PR. | `verification-before-completion` | Run automated test suites and verify observable evidence before claiming completion. |

---

## 2. INTER-AGENT COMMUNICATION & CONTEXT SHARING (BLACKBOARD PROTOCOL)

Agents operating in a multi-agent workflow must coordinate and share context to eliminate redundant computation and prevent contradictory edits:

### 2.1 Communication Channels
1. **Hierarchical Dispatch:** Primary agent launches subagent via `invoke_subagent`.
2. **Peer Messaging:** Active agents message peers via `send_message(Recipient, Message)` for consultations and code reviews.
3. **Shared Blackboard:** All active agents read from and write to `.agent/context/BLACKBOARD.md`.

### 2.2 Standard Context Handoff Payload (CHP)
When handing off between agents, the sending agent must supply:
1. **Task Objective:** Clear definition of success.
2. **Discovered Invariants:** Key codebase patterns, routes, and schemas discovered.
3. **Active Constraints:** Rate limits, zero-emoji policy, error handling standards.
4. **Handoff Artifacts:** Exact file paths to modified files, diffs, and tests.

---

## 3. AGENT CONTEXT ENGINEERING SYSTEM

Context is a finite, scarce resource. Agents must adhere to strict context engineering:

1. **Attention Curve Optimization:**
   - Place critical system constraints and objective at the **Head** of the prompt.
   - Place exact output schemas, deliverables, and validation criteria at the **Tail**.
2. **Subagent Context Boundary Insulation:**
   - Heavy reconnaissance (scanning hundreds of files, reading compiler logs, AST extraction) must occur inside subagents.
   - Subagents must return condensed conclusions (under 300 words) with file references, never dumping raw logs or large file bodies into parent context.
3. **Progressive Disclosure:**
   - Agents read `SKILL.md` first. Never read all files in a skill directory unless specifically required.

---

## 4. AGENT MEMORY ENGINEERING SYSTEM

Every agent operates within a dual-tier cognitive memory model:

1. **Layer 1: Ephemeral Session Memory (`SESSION_FAILURES.md`):**
   - Maintained in the current working directory.
   - Records every failed approach, incorrect assumption, and invalid path immediately upon occurrence.
   - **Rule:** Before retrying any failed command or editing an alternative file, the agent must check `SESSION_FAILURES.md` to avoid repeating errors.
2. **Layer 2: Persistent Architectural Memory (`.agent/memory/ARCHITECTURE_MEMORY.md`):**
   - Records permanent project conventions, technology stack boundaries, and established patterns.
   - **Rule:** Before proposing architectural refactoring or schema alterations, the agent must consult this memory.

---

## 5. DUAL EXECUTION METHODOLOGY: SUBAGENTS VS. AGENT TEAMS

Hyper Agents Force provides two complementary execution paradigms, accessible either manually via explicit syntax or autonomously through prompt template detection:

### 5.1 Subagents System (Specialist Invocation)
- **Paradigm:** Single focused specialist agent executing an isolated task.
- **Manual Invocation Prefix:** `@agent-name` (e.g., `@fastapi-reviewer`, `@debugger`, `@frontend-specialist`).
- **Autonomous Detection:** Triggered when the prompt represents a single focused task, bug fix, component implementation, or domain review.
- **Execution Lifecycle:**
  1. Primary agent dispatches subagent with isolated context.
  2. Subagent executes using required domain skills.
  3. Subagent returns concise findings (< 300 words) or artifact paths.

### 5.2 Agent Teams System (Collaborative Team Structure)
- **Paradigm:** Decentralized collaborative team with distributed roles, shared visibility, and peer-to-peer coordination.
- **Manual Invocation Prefix:** `$team-name` or `#team-name` (e.g., `$team-fullstack`, `$team:auth-audit`, `#team-mobile`).
- **Autonomous Detection:** Triggered when the prompt defines a multi-role project, team objective, cross-functional dependencies, and work backlog.
- **Core Roles & Functions:**
  1. **Team Lead:** Main Agent with leadership responsibility. Formulates the team objective, decomposes work into a Directed Acyclic Graph (DAG) of tasks, monitors progress, and verifies final delivery.
  2. **Centralized Shared Task Board:** Centralized task repository visible to all teammates (SQLite table `team_tasks`, synchronized in real time to `.agent/context/TEAM_BOARD.md`). Tasks flow through atomic states: `BLOCKED -> UNCLAIMED -> IN_PROGRESS -> DONE`.
  3. **Team Members:** Specialized individual workers equipped with distinct skills, agent rules, and domain focus. Teammates query the shared board for unblocked tasks, claim tasks atomically, and publish deliverables.
  4. **Teammate-to-Teammate Communication:** Direct peer message stream (`team_messages`) enabling teammates to exchange API specifications, review requests, and handoff notifications without routing through a central bottleneck.
  5. **Shared Context & Visibility:** All teammates operate against the live shared board and SQLite memory, ensuring full visibility with zero token duplication.

---

## 6. WORKFLOW AUTOMATION & STRUCTURED ANSWER PROTOCOL (PYTHON & NODE.JS)

All 108 agents are equipped with the Workflow Automation Engine to standardize complex task execution and formulate structured, reproducible answers:

### 6.1 Available Workflows Catalog (`.agent/workflows/`)
- `/plan`: Sequential project planning with milestone checklists.
- `/orchestrate`: Multi-agent orchestration requiring minimum 3 agents.
- `/test`: Automated test generation, execution, and coverage analysis.
- `/mobile-test`: Mobile automation auditing, screen objects, and locators.
- `/debug`: 4-phase systematic root-cause investigation.
- `/review`: Structured pull request, code smell, and security review.
- `/audit`: Security, accessibility (WCAG), performance, and dependency audit.
- `/reverse-engineer`: Reference application feature extraction and contract synthesis.
- `/unslop`: Visual modernization and anti-slop design token enforcement.
- `/understand`: Codebase onboarding, AST scanning, and architecture tours.
- `/deploy`: Production deployment verification and infrastructure staging.
- `/enhance`: Iterative feature enhancement and non-breaking refactoring.
- `/create`: Green-field application scaffolding and feature implementation.
- `/brainstorm`: Structured architectural trade-off exploration.
- `/preview`: Local development server lifecycle management.
- `/status`: Real-time agent status tracking and progress reporting.
- `/ui-ux-pro-max`: Design system planning and high-fidelity UI implementation.

### 6.2 Programmatic Automation Execution
Any agent can trigger or inspect workflows programmatically using either Python or Node.js scripts:
- **Python Workflow Runner:**
  ```bash
  python .agent/scripts/workflow_engine.py run <workflow> --args "<scope>" --agent <agent_name>
  ```
- **Node.js Workflow Runner:**
  ```bash
  node .agent/scripts/workflow-engine.js run <workflow> --args "<scope>" --agent <agent_name>
  ```
- **Automated Workflow Answers:**
  ```bash
  python .agent/scripts/workflow_engine.py answer "<user query>"
  ```

### 6.3 Standard Workflow Answer Structure
When providing answers to complex user requests, agents must follow the structured workflow pattern:
1. **Target Agent & Skill Assignment:** Explicitly state the primary specialist and injected skills.
2. **Matching Workflow & Objective:** Reference the relevant workflow from `.agent/workflows/`.
3. **Sub-Commands & Capabilities:** Display the actionable sub-commands.
4. **Step-by-Step Implementation Sequence:** Provide numbered, verifiable milestones.
5. **Automation Script Invocations:** Provide exact Python and Node.js commands to execute or dry-run.
6. **Blackboard Coordination:** Automatically log task start, checkpoints, and completion to `.agent/context/BLACKBOARD.md`.

---

## 7. MANDATORY ZERO-ASSUMPTION & USER CLARIFICATION INVARIANT (ALL AGENTS)

> **IRON RULE FOR ALL AGENTS:** If ANY agent (primary specialist, subagent, reviewer, or orchestrator) has ANY doubt, ambiguity, missing context, or uncertainty to make the correct decision, the agent MUST NOT ASSUME AND CONTINUE WORK.

1. **Zero Speculation:**
   - Guessing user intent, API contracts, architectural boundaries, or business logic is strictly prohibited.
   - Proceeding on unverified assumptions is treated as a critical system violation.

2. **Immediate Pause & Inquire Protocol:**
   - Whenever an agent reaches an ambiguous branch or lacks decisive clarity, the agent must immediately pause execution.
   - Formulate clear, concise questions detailing the exact decision point, why it matters, and 2-3 concrete options with trade-offs.
   - Present the questions directly to the user (via `ask_question` or direct text).
   - Only resume work after explicit user confirmation is received.

3. **Multi-Agent Coordination & Blackboard Integration:**
   - If an agent is blocked awaiting user clarification during multi-agent orchestration, it must update `.agent/context/BLACKBOARD.md` marking the work item as `BLOCKED (Awaiting User Clarification)`.
   - Peer agents must not overwrite or assume the blocked agent's scope.

---

## 8. HUMAN-IN-THE-LOOP (HITL) MIDDLEWARE: 3-GATE PROTOCOL FOR SUBAGENTS & AGENT TEAMS

To ensure precise alignment with project domain requirements and eliminate silent regressions, all agents across both Subagent and Agent Team architectures operate under the 3-Gate Human-in-the-Loop Middleware (`bin/hitl_middleware.py`):

### 8.1 Gate 1: Domain Knowledge Discovery & Alignment (Pre-Execution)
- **Invariant:** Before modifying any files or scaffoldings, the agent must acquire and validate correct domain knowledge:
  1. Scan existing architectural patterns, database schemas, and business entity models.
  2. Consult `.agent/memory/ARCHITECTURE_MEMORY.md` and SQLite invariants for established domain rules.
  3. If domain requirements, business boundaries, or architectural decisions are ambiguous, the agent must create a `DOMAIN_KNOWLEDGE` checkpoint (`meet hitl request --stage DOMAIN_KNOWLEDGE`) and ask the user targeted clarification questions.
  4. Work is suspended until the user confirms the domain model assumptions.

### 8.2 Gate 2: Pre-Mutation Plan Approval (Pre-Modification)
- **Invariant:** Before applying edits to production modules (or when a change affects > 2 files):
  1. The subagent or Team Lead must produce a bite-sized, phased implementation plan detailing targeted files, non-breaking strategies, and risk mitigation.
  2. Register the plan checkpoint (`meet hitl request --stage PLAN_APPROVAL`).
  3. Require user confirmation (`meet hitl approve <checkpoint_id>`) before mutating code.

### 8.3 Gate 3: Verification & User Sign-Off (Post-Execution)
- **Invariant:** No task, subagent handoff, or team mission may be declared complete without human verification:
  1. The completing agent must execute automated verification suites (`pytest`, `npm test`, or domain test runners).
  2. Compile observable evidence: passing test counts, lint results, and exact file diffs.
  3. Register the verification sign-off checkpoint (`meet hitl request --stage VERIFICATION_SIGNOFF`).
  4. The Team Lead or Subagent delivers the sign-off card to the user. Final completion is certified only upon user approval.



