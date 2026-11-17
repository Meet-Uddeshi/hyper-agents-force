# Hyper Agents Force

> Autonomous Multi-Agent System, Intelligent Routing Engine, and Enterprise MCP Platform.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B-green.svg)](https://nodejs.org/)
[![MCP](https://img.shields.io/badge/MCP-Standard%202024--11--05-orange.svg)](https://modelcontextprotocol.io/)
[![Agents](https://img.shields.io/badge/Agents-110%20Verified-purple.svg)](#agent-catalog-overview)
[![Skills](https://img.shields.io/badge/Skills-377%20Modules-brightgreen.svg)](#skills-architecture)
[![License](https://img.shields.io/badge/License-UNLICENSED-lightgrey.svg)](#license)

**Hyper Agents Force** is an enterprise-grade agentic operating framework designed for Google Antigravity, Gemini CLI, Claude Code, and autonomous AI coding environments. It couples **110 specialized domain agents**, **377 production skills**, a **dual workflow engine** (Python + Node.js), a **deterministic SQLite memory system with FTS5 full-text indexing**, and native **Model Context Protocol (MCP)** integration into a unified, zero-dependency engineering runtime.

---

## Table of Contents

- [Overview](#overview)
- [Architecture & Core Systems](#architecture--core-systems)
- [Agents, Skills, Rules & Workflows](#agents-skills-rules--workflows)
  - [Agent Catalog (110 Specialists)](#agent-catalog-110-specialists)
  - [Skills Architecture (377 Modules)](#skills-architecture-377-modules)
  - [Rules Architecture (Workspace & Domain)](#rules-architecture-workspace--domain)
  - [Workflow Automation Engine](#workflow-automation-engine)
- [Global Rules Deployment](#global-rules-deployment)
- [Universal Multi-Platform Support](#universal-multi-platform-support)
  - [Supported IDEs & Agents](#supported-ides--agents)
  - [Platform Directory Adapters](#platform-directory-adapters)
  - [Targeted Platform Installation](#targeted-platform-installation)
- [Installation & Quick Start](#installation--quick-start)
  - [1. Installation via UV (Recommended)](#1-installation-via-uv-recommended)
  - [2. Installation via Pip](#2-installation-via-pip)
  - [3. Installation via NPM / NPX](#3-installation-via-npm--npx)
- [CLI Reference](#cli-reference)
- [MCP Configuration & Tool Connection](#mcp-configuration--tool-connection)
- [Dual Execution Methodology: Subagents vs. Agent Teams](#dual-execution-methodology-subagents-vs-agent-teams)
  - [1. Subagents System (Specialist Model)](#1-subagents-system-specialist-model)
  - [2. Agent Teams System (Collaborative Team Structure)](#2-agent-teams-system-collaborative-team-structure)
  - [Manual Calling Prefixes (@agent vs $team)](#manual-calling-prefixes-agent-vs-team)
- [Human-in-the-Loop (HITL) Middleware](#human-in-the-loop-hitl-middleware)
  - [The 3 Alignment & Verification Gates](#the-3-alignment--verification-gates)
  - [Subagent HITL Lifecycle](#subagent-hitl-lifecycle)
  - [Agent Team HITL Lifecycle](#agent-team-hitl-lifecycle)
- [Prompt Templates & Examples](#prompt-templates--examples)
  - [Subagent System Prompt Template](#subagent-system-prompt-template)
  - [Example 1: Systematic Debugging (Subagent System)](#example-1-systematic-debugging--root-cause-analysis-subagent-system)
  - [Example 2: Complex System Architecture (Subagent System)](#example-2-complex-system-architecture-subagent-system)
  - [Agent Team System Prompt Template](#agent-team-system-prompt-template)
  - [Example 3: Full-Stack Feature Team (Agent Team System)](#example-3-collaborative-full-stack-feature-team-agent-team-system)
  - [Example 4: Mobile Platform & Security Team (Agent Team System)](#example-4-mobile-platform--security-audit-team-agent-team-system)
- [Manual On-Demand Workflows & Prompt Templates](#manual-on-demand-workflows--prompt-templates)
  - [1. AI Security & Log4j Vulnerability Audit](#1-ai-security--log4j-vulnerability-audit)
  - [2. Codeflow AST Knowledge Graph & Interactive Canvas](#2-codeflow-ast-knowledge-graph--interactive-canvas)
  - [3. Greenfield Tech Stack & Architecture Advisor](#3-greenfield-tech-stack--architecture-advisor)
  - [4. Read-Only Ask Mode & Dense Response Protocol](#4-read-only-ask-mode--dense-response-protocol)
- [Memory & Shared Board System](#memory--shared-board-system)
- [Verification & Test Suite](#verification--test-suite)
- [License](#license)

---

## Overview

Modern software development requires specialized domain knowledge across architecture, security, state management, accessibility, machine learning, and infrastructure. Generic AI prompts often produce shallow code, hallucinations, and untracked side effects.

**Hyper Agents Force** solves this with a deterministic, multi-tiered hierarchy:
1. **Intelligent Prompt-Trigger Routing**: Automatically detects prompt keywords and constraints, instantly routing tasks to the exact matching specialist agent without manual lookup.
2. **Deterministic Dual Workflow Engine**: Runs automated, multi-step agent pipelines in either native Python or Node.js.
3. **Blackboard Coordination Architecture**: Enables multi-agent communication and task handoffs through `.agent/context/BLACKBOARD.md` and SQLite event journals.
4. **SQLite FTS5 Persistent Memory**: Stores bounded architectural decisions, failures, and session context, preventing LLM token window saturation.
5. **Universal Zero-Assumption Mandate**: Requires agents to pause and verify assumptions rather than guessing, enforcing rigorous development gates.

---

## Architecture & Core Systems

```
Hyper Agents Force Runtime
├── .agent/
│   ├── agents/          # 110 Specialist Agent Definitions (.md)
│   ├── skills/          # 377 Domain Skill Packages (SKILL.md + assets)
│   ├── rules/           # 24 Language & Technology Rule Modules
│   ├── workflows/       # Deterministic Agent Execution Pipelines (.md)
│   ├── context/         # Shared Blackboard & Communication Bus
│   ├── memory/          # SQLite FTS5 Database (memory.db) & Markdown Sync
│   ├── scripts/         # Automated Test Suites & Catalog Indexers
│   └── mcp.json         # Unified Model Context Protocol Registry
├── global-rules/        # Engineering Standards for Global User Deployment
│   ├── debugging/       # Systematic 4-phase debugging protocols
│   ├── testing/         # TDD, verification gates, anti-pattern detection
│   ├── planning/        # Brainstorming, spec writing, execution plans
│   ├── execution/       # Subagent dispatch, parallelization, branch finishing
│   ├── code-review/     # Requesting & receiving code reviews
│   └── standards/       # Karpathy guidelines, Superpowers, low-token modes
├── bin/                 # Dual CLI Runners (Python CLI + Node.js Runner)
├── GEMINI.md            # Root Workspace Rules & Intelligent Routing Matrix
└── package.json / pyproject.toml
```

---

## Agents, Skills, Rules & Workflows

### Agent Catalog (110 Specialists)

Agents are configured with explicit triggers, required skills, operating rules, input/output contracts, and delivery verification gates:

| Domain | Key Agents | Capabilities |
| :--- | :--- | :--- |
| **Frontend & UI** | `frontend-specialist`, `react-reviewer`, `vue-reviewer`, `unslop`, `a11y-architect` | React 19, Next.js App Router, Vue 3 Composition API, WCAG AAA accessibility, anti-slop design. |
| **Mobile Development** | `mobile-developer`, `flutter-reviewer`, `swift-reviewer`, `mobile-automation-engineer` | React Native, Flutter / Riverpod, SwiftUI / Actor concurrency, Appium automation. |
| **Backend & APIs** | `backend-specialist`, `fastapi-reviewer`, `django-reviewer`, `go-reviewer`, `rust-reviewer` | High-throughput REST / GraphQL / gRPC, Tokio async, Go channels, Spring Boot, ASP.NET Core. |
| **Database & Cloud** | `database-architect`, `database-reviewer`, `cloud-architect`, `devops-specialist` | PostgreSQL, SQLite FTS5, Prisma, indexing, query optimization, Docker, Kubernetes. |
| **AI & ML Engineering** | `ai-engineer`, `ml-engineer`, `rag-pipeline-reviewer`, `mle-reviewer` | LangGraph, LlamaIndex, vector databases, multi-head attention, PyTorch, LoRA fine-tuning. |
| **Security & Auditing** | `security-specialist`, `security-auditor`, `code-reviewer`, `lint-and-validate` | Static analysis, CVE dependency audits, secret stripping, HIPAA / SOC2 compliance. |
| **QA & Verification** | `qa-automation-engineer`, `testing-specialist`, `verify`, `debugger` | Unit/integration testing, end-to-end Cypress/Playwright, test-driven development. |
| **Architecture & Planning** | `architect`, `code-architect`, `plan`, `code-simplifier` | Clean Architecture, Hexagonal DDD, modular boundaries, line-reduction refactoring. |
| **Exploration & Docs** | `explorer-agent`, `explore`, `document-specialist`, `doc-reviewer` | Deep codebase mapping, structural call graphs, living docs, architectural ADRs. |
| **Coordination & Swarm** | `orchestrator`, `coordinator`, `chief-of-staff`, `loop-operator` | Multi-agent coordination, subagent task fan-out, blackboard event management. |
| **Specialized Domains** | `game-developer`, `healthcare-reviewer`, `bengali-nlp`, `seo-specialist` | Phaser 2D games, HIPAA healthcare data compliance, Bengali NLP, Core Web Vitals. |

### Skills Architecture (377 Modules)

Every skill in `.agent/skills/` contains a standardized `SKILL.md` that instructs agents on step-by-step procedures, tool usage, common pitfalls, and verification checklists.

Categories include:
* **Architecture**: Clean code, hexagonal architecture, microservices, domain-driven design.
* **Languages & Frameworks**: Next.js, React, Vue, Svelte, Tailwind, Python, FastAPI, Go, Rust, Java, Kotlin, Swift.
* **UI/UX Database (`ui-ux-pro-max`)**: Complete offline databases with 37 CSV datasets covering colors, typography, Google font pairings, layout patterns, component checklists, and 23 frontend stacks.
* **Testing & Quality**: Test-driven development, Vitest, Pytest, Playwright, mock avoidance.
* **AI & Embeddings**: Semantic search, vector embeddings, chunking strategies, prompt engineering.

### Rules Architecture (Workspace & Domain)

1. **Root Rule (`GEMINI.md`)**: Defines system invariants, zero-emoji policy, blackboard protocol, and the 110-agent routing matrix.
2. **Domain Rules (`.agent/rules/<domain>/`)**: Contains specialized coding standards, hooks, and security guidelines for 24 tech stacks (React, Python, Go, Rust, Vue, etc.).
3. **Hard Cap Constraint**: All rule files strictly observe a 24,000-byte cap to prevent silent truncation by Antigravity and Gemini CLI context windows.

### Workflow Automation Engine

Workflows in `.agent/workflows/` execute pre-orchestrated agent sequences:
* `audit.md`: Runs security scanning, package vulnerability review, linting, and tests.
* `plan-and-solve.md`: Dispatches `architect` -> `plan` -> `subagent execution` -> `verify`.
* `ui-ux-pro-max.md`: Queries design guidelines, color palettes, and component standards from CLI.
* `test.md`: Executes test suites across Python, Node.js, and browser environments.

---

## Global Rules Deployment

### Why Save Rules at the Global Level?

When engineering rules are kept only inside a single project directory, other workspaces and fresh AI sessions cannot access them. 

By saving `global-rules` at the **user profile level** (`~/.gemini/rules/`), Antigravity, Gemini CLI, and compatible AI tools **automatically load and enforce these rules across every project and every session on your machine**:
* **Universal Debugging Discipline**: Systematic 4-phase debugging is enforced across all repositories automatically.
* **Consistent Quality**: Test-driven development, plan-writing, and code review standards apply universally without copying files.
* **Zero Duplication**: Edit your engineering rules once in your global profile, and all current and future projects immediately inherit the updates.

### Deploying Global Rules

You can install global rules automatically via the CLI:

```bash
# Deploy global rules to your user profile (~/.gemini/rules/)
hyper-agents-force install -u

# Or deploy system-wide for all users
hyper-agents-force install -g
```

#### Manual Global Installation:
* **Windows (PowerShell)**:
  ```powershell
  New-Item -ItemType Directory -Force "$HOME\.gemini\rules"
  Copy-Item -Recurse -Force "global-rules\*" "$HOME\.gemini\rules\"
  ```
* **Linux / macOS (Bash)**:
  ```bash
  mkdir -p ~/.gemini/rules
  cp -r global-rules/* ~/.gemini/rules/
  ```

---

## Universal Multi-Platform Support

Hyper Agents Force is built with a universal decoupled architecture. The shared intelligence core—including all 110 specialist agents, 377 domain skills, workflows, SQLite persistent memory, and Human-in-the-Loop (HITL) middleware—lives inside `.agent/`.

Platform-specific adapters are stored independently inside `platforms/`:

```
platforms/
├── cursor/              # Cursor IDE
│   ├── .cursorrules     # Root rules with DLP, thin controllers & zero assumptions
│   └── .cursor/
│       ├── mcp.json     # Cursor Model Context Protocol server configuration
│       └── rules/       # Modular MDC rules (core, team, frontend, backend, testing)
├── claude/              # Claude Code
│   ├── CLAUDE.md        # Root entry point with agent & team routing
│   └── .mcp.json        # Claude MCP configuration
├── copilot/             # GitHub Copilot
│   └── .github/
│       └── copilot-instructions.md  # Workspace instructions referencing .agent/
├── codex/               # OpenAI Codex
│   └── .codex/
│       └── instructions.md          # Workspace instructions referencing .agent/
├── gemini/              # Gemini CLI
│   └── GEMINI.md        # Root instructions & prompt routing matrix
└── antigravity/         # Google Antigravity
    └── GEMINI.md        # Workspace instructions & prompt routing matrix
```

### Targeted Platform Installation

When deploying with a platform flag (e.g., `--cursor`, `--claude`, `--copilot`, `--codex`, `--gemini`, or `--all`), the installer copies **only** the common `.agent/` runtime and that platform's specific configuration files into your destination project:

- **Zero Workspace Clutter**: A Cursor project receives only `.cursorrules` and `.cursor/`—no stray `GEMINI.md` or `CLAUDE.md`. A Claude Code workspace receives only `CLAUDE.md` and `.mcp.json`.
- **Shared Intelligence Core**: Regardless of IDE or CLI, all platforms share the exact same 110 agents, 377 skills, SQLite memory database, and HITL verification middleware.
- **Universal Multi-Platform Deployment**: Using `--all` deploys adapters for every platform simultaneously, ideal for cross-functional teams using different tools on the same repository.

---

## Installation & Quick Start

Hyper Agents Force provides native support for **UV**, **Pip**, and **NPM**.

### 1. Installation via UV (Recommended)

[UV](https://github.com/astral-sh/uv) provides sub-second virtualenv setup and package execution:

```bash
# Clone the repository
git clone https://github.com/Meet-Uddeshi/hyper-agents-force.git
cd hyper-agents-force

# Option A: Install into system Python
uv pip install -e . --system

# Option B: Install into project virtualenv
uv venv
.venv\Scripts\activate      # Windows (or: source .venv/bin/activate on Linux/macOS)
uv pip install -e .

# Option C: Direct installation from GitHub without cloning
uv tool install git+https://github.com/Meet-Uddeshi/hyper-agents-force.git

# Verify installation
hyper doctor
```

### 2. Installation via Pip

```bash
# Option A: Clone and install in editable mode
git clone https://github.com/Meet-Uddeshi/hyper-agents-force.git
cd hyper-agents-force
pip install -e .

# Option B: Direct install from GitHub
pip install git+https://github.com/Meet-Uddeshi/hyper-agents-force.git

# Verify installation
hyper doctor

# Deploy for your specific platform
hyper --cursor             # Deploy Cursor adapter + .agent/
hyper --claude             # Deploy Claude Code adapter + .agent/
hyper --copilot            # Deploy GitHub Copilot adapter + .agent/
hyper --codex              # Deploy OpenAI Codex adapter + .agent/
hyper --all                # Deploy all platform adapters simultaneously
hyper install -p           # Default deployment (./.agent/ & GEMINI.md)
hyper install -u           # Deploy into user profile (~/.gemini/)
```

### 3. Installation via NPM / NPX

For JavaScript, TypeScript, and Node.js environments:

```bash
# Option A: Local link from cloned repository
git clone https://github.com/Meet-Uddeshi/hyper-agents-force.git
cd hyper-agents-force
npm link

# Option B: Run directly via GitHub with npx (zero local cloning required)
npx github:Meet-Uddeshi/hyper-agents-force --cursor
npx github:Meet-Uddeshi/hyper-agents-force --claude
npx github:Meet-Uddeshi/hyper-agents-force --copilot
npx github:Meet-Uddeshi/hyper-agents-force --all
npx github:Meet-Uddeshi/hyper-agents-force doctor

# Option C: Run directly with Node without installation
node bin/meet-ai-agents.js --cursor
node bin/meet-ai-agents.js doctor
```

---

## CLI Reference

The unified CLI (`hyper-agents-force`, `hyper`, `meet-ai`) provides complete control over your agents, memory, MCP, and workflows:

```bash
# System Health Check
hyper-agents-force doctor

# Targeted Platform Deployment
hyper-agents-force --cursor             # Deploy Cursor rules (.cursorrules, .cursor/rules/*.mdc, mcp.json)
hyper-agents-force --claude             # Deploy Claude Code entry point (CLAUDE.md, .mcp.json)
hyper-agents-force --copilot            # Deploy GitHub Copilot instructions (.github/)
hyper-agents-force --codex              # Deploy OpenAI Codex instructions (.codex/)
hyper-agents-force --gemini             # Deploy Gemini CLI rules (GEMINI.md)
hyper-agents-force --all                # Deploy all platform adapters simultaneously
hyper-agents-force install --cursor -p  # Explicit platform install at project level

# Multi-Level Deployment
hyper-agents-force install -p           # Current project directory (default)
hyper-agents-force install -u           # User profile level (~/.gemini/)
hyper-agents-force install -g           # System-wide global level
hyper-agents-force install -p --dry-run # Simulate deployment without file writes

# Listing Resources
hyper-agents-force list agents          # List all 110 specialist agents
hyper-agents-force list skills          # List all 377 domain skills
hyper-agents-force list workflows       # List available execution workflows

# MCP Management
hyper-agents-force mcp list             # Check configured MCP servers & status
hyper-agents-force mcp test             # Ping servers and validate credentials
hyper-agents-force mcp sync             # Sync mcp.json across environments

# Memory & Blackboard
hyper-agents-force memory status        # Inspect SQLite FTS5 database stats
hyper-agents-force memory query "query" # Search memory with full-text search
hyper-agents-force memory blackboard   # View current active blackboard tasks

# Collaborative Agent Team Management & Shared Board
hyper-agents-force team create --id <id> --name <name> --lead <lead> --objective <goal>
hyper-agents-force team board --id <id>     # Display live shared task board & sync to TEAM_BOARD.md
hyper-agents-force team task-add --id <id>  # Add task with dependencies to shared DAG board
hyper-agents-force team tasks --id <id>     # List unblocked tasks ready for claiming
hyper-agents-force team claim --id <id>     # Atomically claim unblocked task for an agent
hyper-agents-force team complete --id <id>  # Complete task & unblock downstream dependents
hyper-agents-force team msg --id <id>       # Send direct peer-to-peer message between teammates
hyper-agents-force team route "<prompt>"    # Autonomously classify prompt intent (Subagent vs Team)

# Human-in-the-Loop (HITL) Verification Middleware
hyper-agents-force hitl list                 # List pending checkpoints awaiting human verification
hyper-agents-force hitl show <checkpoint_id> # Display structured verification prompt card
hyper-agents-force hitl approve <id> --feedback "Confirmed" # Approve gate and permit execution
hyper-agents-force hitl reject <id> --feedback "Changes..." # Request rework or clarify assumptions
hyper-agents-force hitl request --system <subagent|team> --stage <DOMAIN_KNOWLEDGE|PLAN_APPROVAL|VERIFICATION_SIGNOFF> --agent <agent> --summary "<summary>"

# Workflow Execution
hyper-agents-force run audit            # Run security, CVE, lint, and test audit
hyper-agents-force run plan-and-solve   # Run architecture planning & execution

# Intelligent Prompt Routing
hyper-agents-force answer "Design a PostgreSQL schema with Prisma"

# AI Security Guardrails & Log4j Scanner
hyper-agents-force secure audit             # Audit workspace for exposed secrets, .env files, and injections
hyper-agents-force secure log4j             # Scan pom.xml, gradle, and properties for Log4j CVEs
hyper-agents-force secure log4j --fix       # Automatically patch vulnerable Log4j dependencies to 2.17.1

# Greenfield Tech Stack & Architecture Advisor
hyper-agents-force advise "Idea"            # Run dynamic architecture advisor and technology stack evaluator
hyper-agents-force advise "Idea" --json     # Export structured recommendations to JSON

# Zero-Configuration Codebase Knowledge Graph (Graphify & Codeflow)
hyper-agents-force graph build              # Build AST knowledge graph in SQLite and export code_graph.cyp
hyper-agents-force graph stats              # Inspect AST node counts, dependencies, and relation edges
hyper-agents-force graph query "Symbol"     # Query symbol dependencies, callers, and relationships
hyper-agents-force graph visual             # Generate standalone interactive CODEFLOW_GRAPH.html canvas

# Read-Only Ask Mode (Dense Response Protocol)
hyper-agents-force ask "Question"           # Zero-write Q&A runtime answering without file modifications
hyper-agents-force ask "Question" --raw     # Output raw high-density answer payload

# Autonomous Self-Healing Test Harness
hyper-agents-force eval run                 # Run tests, intercept errors, capture decisive trace, retry loop
hyper-agents-force eval run --cmd "pytest"  # Execute specific test command under self-healing retry loop

# Multi-Agent Git Worktree Workspace Isolation
hyper-agents-force worktree list            # List active isolated worktrees and sandboxes
hyper-agents-force worktree create <name>   # Provision isolated worktree branch for agent task
hyper-agents-force worktree diff <name>     # Inspect isolated worktree changes
hyper-agents-force worktree merge <name>    # Merge validated worktree changes into main branch
hyper-agents-force worktree cleanup <name>  # Safely dismantle worktree directory and branch

# Live Mission Control Dashboard & Terminal TUI
hyper-agents-force dashboard --web          # Launch zero-dependency web dashboard on port 4242
hyper-agents-force dashboard --tui          # Launch live interactive terminal TUI status display

# Continuous PR Bot & GitHub Actions
hyper-agents-force ci review                # Run PR diff classifier, route specialist review, generate check card
```

---

## MCP Configuration & Tool Connection

Hyper Agents Force integrates with the **Model Context Protocol (MCP)**, connecting external developer tools, databases, and issue trackers directly to agents.

### 1. Configuration File (`.agent/mcp.json`)

MCP servers are registered in `.agent/mcp.json`. Each server defines its command, environment variables, and associated agents:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      },
      "associated_agents": ["github-ops", "devops-specialist", "code-reviewer"]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "${DATABASE_URL}"],
      "associated_agents": ["database-architect", "database-reviewer"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "${WORKSPACE_ROOT}"],
      "associated_agents": ["explorer-agent", "file-analyzer"]
    }
  }
}
```

### 2. Environment Variables Setup

Copy `.env.example` to `.env` and provide your API tokens:

```bash
cp .env.example .env
```

Edit `.env`:
```env
GITHUB_TOKEN=ghp_your_personal_access_token
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
JIRA_API_TOKEN=your_jira_token
LINEAR_API_KEY=your_linear_key
SLACK_BOT_TOKEN=xoxb-your-slack-token
```

### 3. Validate Connection

Run the diagnostic command:

```bash
hyper-agents-force mcp list
```

Ready servers display `[READY]`, while unconfigured servers list their missing environment variables.

---

## Dual Execution Methodology: Subagents vs. Agent Teams

Hyper Agents Force provides two complementary execution models designed to handle both isolated specialist tasks and multi-faceted, collaborative engineering projects:

### 1. Subagents System (Specialist Model)
- **Architecture**: Single focused specialist agent executing in an isolated context boundary.
- **Role & Function**: Solves targeted bugs, reviews code, implements individual components, or executes single-domain investigations. The agent reports findings and deliverables directly back to the parent session or user.
- **Manual Calling Prefix**: `@agent-name` (e.g., `@fastapi-reviewer`, `@debugger`, `@frontend-specialist`, `@database-architect`).
- **Autonomous Detection**: Automatically triggered when user prompts follow the single-task structure (isolated task objective, technical constraints, targeted deliverables, and verification command).

### 2. Agent Teams System (Collaborative Team Structure)
- **Architecture**: Decentralized collaborative team with distributed roles, shared context visibility, and peer-to-peer coordination.
- **Role & Function**:
  - **Team Lead**: Main Agent with leadership responsibility. Formulates the team objective, decomposes work into a Directed Acyclic Graph (DAG) of tasks, monitors execution, and verifies final delivery.
  - **Centralized Shared Task Board**: Centralized task repository visible to all teammates (backed by SQLite `team_tasks` and synchronized in real time to [`.agent/context/TEAM_BOARD.md`](file:///d:/Personal/hyper-agents-force/.agent/context/TEAM_BOARD.md)). Tasks flow through atomic lifecycle states: `BLOCKED -> UNCLAIMED -> IN_PROGRESS -> DONE`.
  - **Team Members**: Specialized individual workers equipped with distinct skills, agent rules, and domain focus. Teammates query the shared board for unblocked tasks, claim tasks atomically, and publish deliverables.
  - **Teammate-to-Teammate Communication (P2P Message Bus)**: Direct peer message stream (`team_messages`) enabling teammates to exchange API specifications, review requests, and handoff notifications without routing through a central bottleneck.
  - **Shared Context & Visibility**: All teammates operate against the live shared board and SQLite memory, ensuring full visibility with zero token duplication.
- **Manual Calling Prefix**: `$team-name` or `#team-name` (e.g., `$team-fullstack`, `$team:auth-audit`, `#team-mobile`).
- **Autonomous Detection**: Automatically triggered when user prompts follow the collaborative project structure (team objective, cross-functional roles, work backlog with task dependencies, and team delivery gates).

### Manual Calling Prefixes (@agent vs $team)

Developers can explicitly override automatic routing using standard prefixes:
- **`@agent-name <prompt>`**: Immediately pins execution to that specific specialist agent (e.g., `@rust-reviewer verify thread safety in worker.rs`).
- **`$team-name <prompt>`**: Immediately initializes a collaborative agent team with that team tag (e.g., `$team-ecommerce build checkout flow and Stripe webhook`).

---

## Human-in-the-Loop (HITL) Middleware

Hyper Agents Force incorporates an explicit **Human-in-the-Loop (HITL) Middleware** ([`bin/hitl_middleware.py`](file:///d:/Personal/hyper-agents-force/bin/hitl_middleware.py)) operating across both Subagents and Agent Teams. This middleware prevents uncontrolled hallucinated writes, verifies domain alignment upfront, and requires user validation before changes are finalized.

### The 3 Alignment & Verification Gates

```
Human-in-the-Loop 3-Gate Pipeline
┌────────────────────────────────────────────────────────┐
│ Gate 1: DOMAIN_KNOWLEDGE (Discovery & Alignment)       │
│ - Validates existing architecture & domain entities    │
│ - Intercepts ambiguity; prompts user for clarification │
└──────────────────────────┬─────────────────────────────┘
                           │ Approved
┌──────────────────────────▼─────────────────────────────┐
│ Gate 2: PLAN_APPROVAL (Pre-Mutation Review)            │
│ - Evaluates proposed file scope & implementation steps │
│ - User confirms non-breaking strategy                  │
└──────────────────────────┬─────────────────────────────┘
                           │ Approved
┌──────────────────────────▼─────────────────────────────┐
│ Gate 3: VERIFICATION_SIGNOFF (Post-Execution Evidence) │
│ - Runs automated test suites & verifies observable logs│
│ - User performs final sign-off before task close       │
└────────────────────────────────────────────────────────┘
```

1. **Gate 1: DOMAIN_KNOWLEDGE (Pre-Execution Discovery & Alignment)**:
   - **Purpose**: Prevents premature code generation based on shallow guesses or unverified assumptions.
   - **Mechanism**: The agent scans project conventions, database schemas, and SQLite invariants. If any ambiguity or conflicting architectural patterns exist, the agent logs a `DOMAIN_KNOWLEDGE` checkpoint and asks the user strategic clarification questions. Work pauses until the user validates the domain context.
2. **Gate 2: PLAN_APPROVAL (Pre-Modification Plan Approval)**:
   - **Purpose**: Gives users complete oversight before files are modified on disk.
   - **Mechanism**: For any non-trivial change (affecting > 2 files or modifying core services), the agent or Team Lead generates an implementation plan with targeted file paths. Work proceeds only when the user approves (`hyper-agents-force hitl approve <id>`).
3. **Gate 3: VERIFICATION_SIGNOFF (Post-Execution User Verification)**:
   - **Purpose**: Guarantees observable, verified evidence before a subagent finishes or a team signs off on deliverables.
   - **Mechanism**: The completing agent runs automated tests, compiles diffs, and registers a `VERIFICATION_SIGNOFF` checkpoint. The mission is officially closed only when the human user confirms the test results and delivery.

### Subagent HITL Lifecycle
- Single specialist checks domain invariants -> presents plan -> requests user approval -> implements fix -> runs tests -> presents evidence to user for sign-off.

### Agent Team HITL Lifecycle
- Team Lead runs Gate 1 (Domain Knowledge) with user to align on team objectives and domain models.
- Work backlog DAG is published to the shared board ([`.agent/context/TEAM_BOARD.md`](file:///d:/Personal/hyper-agents-force/.agent/context/TEAM_BOARD.md)).
- Teammates autonomously claim and implement unblocked tasks.
- Team Lead runs Gate 3 (Verification Sign-Off) presenting full integration test results for user approval.

---

## Prompt Templates & Examples

You do **not** need to manually look up agent names or skills. Hyper Agents Force inspects prompt structure and intent to autonomously determine whether to dispatch a **Subagent** or assemble an **Agent Team**, selecting the optimal lead, specialists, and skills automatically.

---

### Subagent System Prompt Template

Use this format for single-domain tasks, bug fixes, component refactoring, or code reviews:

```markdown
Task:
{Clear 1-2 sentence description of single focused task or bug}

Context:
- Project Tech Stack: {e.g., Next.js 15, PostgreSQL, Prisma, TypeScript}
- Constraints: {e.g., Zero breaking schema changes, Must include index optimization}
- Relevant Files: {e.g., schema.prisma, src/lib/db.ts}

Deliverables:
1. {Concrete deliverable 1, e.g., Migration file}
2. {Concrete deliverable 2, e.g., Repository queries}
3. {Concrete deliverable 3, e.g., Automated verification test}

Verification:
- Run {command, e.g., npx prisma validate && npm test}
- Confirm zero errors before completing.
```

---

### Example 1: Systematic Debugging & Root Cause Analysis (Subagent System)

#### User Prompt:
```markdown
Task:
Investigate and resolve a memory leak occurring during bulk CSV data imports in production.

Context:
- Project Tech Stack: Node.js, TypeScript, PostgreSQL
- Current Behavior: Process crashes with JavaScript heap out of memory after importing ~5,000 records
- Relevant Files: src/workers/importer.ts

Deliverables:
1. Minimal reproducing test case demonstrating heap exhaustion.
2. Stream-based chunk processing fix preventing memory accumulation.
3. Memory profiling evidence confirming heap stability under 50,000 rows.

Verification:
- Run npm test tests/importer.test.ts
- Verify heap allocation remains under 120 MB throughout execution.
```

#### Autonomous Execution Result:
* **Execution System**: Subagent System (Specialist Agent Invocation)
* **Autonomous Agent**: `debugger`
* **Auto-Injected Skills**: `systematic-debugging`, `root-cause-tracing`, `clean-code`
* **Autonomous Actions**: Executes 4-phase debugging protocol: isolates leak without modifying production code, writes deterministic reproduction test, refactors to backpressure-aware Node stream pipeline, and confirms memory stabilization.

---

### Example 2: Complex System Architecture (Subagent System)

#### User Prompt:
```markdown
Task:
Refactor our monolithic order processing service into a decoupled Hexagonal (Ports & Adapters) architecture.

Context:
- Project Tech Stack: Node.js, TypeScript, PostgreSQL, Stripe SDK
- Constraints: Zero breaking changes to public API, isolate domain logic from infrastructure adapters
- Relevant Files: src/services/OrderService.ts

Deliverables:
1. Domain entity models and repository interfaces (Ports).
2. Infrastructure adapters for Postgres and Stripe.
3. Architecture Decision Record (ADR-004) documenting boundary choices.

Verification:
- Run npm run build
- Run npm test
- Verify no infrastructure dependencies are imported inside the domain core.
```

#### Autonomous Execution Result:
* **Execution System**: Subagent System (Specialist Agent Invocation)
* **Autonomous Agent**: `code-architect`
* **Auto-Injected Skills**: `clean-code`, `architecture`, `architecture-decision-records`, `hexagonal-architecture`
* **Autonomous Actions**: Scans structural call hierarchy, isolates ports and adapters, writes domain entities with zero external dependencies, generates ADR-004, and validates build and test pipelines.

---

### Agent Team System Prompt Template

Use this format for multi-domain features, full-stack applications, security audits, or projects requiring cross-functional agent collaboration:

```markdown
Task:
Team Objective: {High-level project mission requiring collaborative multi-agent execution}

Context:
- Project Tech Stack: {e.g., PostgreSQL, Express, TypeScript, React 19, Tailwind CSS}
- Cross-Functional Roles: {e.g., Architect (Lead), Database Architect, Backend Specialist, Frontend Specialist, Test Engineer}
- Team Coordination: Shared Task Board (.agent/context/TEAM_BOARD.md) & Teammate-to-Teammate P2P Messaging

Deliverables:
Work Backlog:
1. [ ] task-001: {e.g., Database Schema & Migrations}
2. [ ] task-002: {e.g., REST API Endpoints} (Depends on: task-001)
3. [ ] task-003: {e.g., React Dashboard UI Component} (Depends on: task-002)
4. [ ] task-004: {e.g., Security Audit & E2E Integration Suite} (Depends on: task-002, task-003)

Verification:
Team Delivery Gate:
- Run {command, e.g., npm run test:e2e && npm run audit}
- Confirm Team Lead verification sign-off and all tasks marked DONE on shared task board.
```

---

### Example 3: Collaborative Full-Stack Feature Team (Agent Team System)

#### User Prompt:
```markdown
Task:
Team Objective: Build a real-time analytics dashboard with PostgreSQL persistence, REST API endpoints, and a responsive Tailwind CSS interface.

Context:
- Project Tech Stack: PostgreSQL, Prisma, Express, TypeScript, React 19, Tailwind CSS
- Cross-Functional Roles: Architect (Lead), Database Architect, Backend Specialist, Frontend Specialist, Test Engineer
- Team Coordination: Shared Task Board (.agent/context/TEAM_BOARD.md) & Teammate-to-Teammate P2P Messaging

Deliverables:
Work Backlog:
1. [ ] task-001: Schema design for analytics events and daily aggregations.
2. [ ] task-002: Express REST API endpoints with request validation middleware. (Depends on: task-001)
3. [ ] task-003: Responsive analytics dashboard component with charts. (Depends on: task-002)
4. [ ] task-004: End-to-end integration test suite verifying end-to-end contract. (Depends on: task-002, task-003)

Verification:
Team Delivery Gate:
- Run npm run test:e2e
- Verify Team Lead sign-off, all tasks DONE on board, and zero regressions.
```

#### Autonomous Execution Result:
* **Execution System**: Agent Team System (Collaborative Team Structure)
* **Autonomous Team Lead**: `architect`
* **Autonomous Team Roster**: `database-architect`, `backend-specialist`, `frontend-specialist`, `test-engineer`
* **Auto-Injected Skills**: `team-coordination`, `clean-code`, `database-design`, `react-best-practices`, `testing-patterns`
* **Autonomous Actions**:
  1. Team Lead `architect` initializes team `team-analytics`, defines task DAG with dependencies, and synchronizes `.agent/context/TEAM_BOARD.md`.
  2. Teammate `database-architect` detects unblocked `task-001`, claims it atomically, outputs `prisma/schema.prisma`, and completes the task.
  3. `task-002` automatically transitions from `BLOCKED` to `UNCLAIMED`. Teammate `backend-specialist` claims `task-002`, implements API routes, and delivers direct peer message to `frontend-specialist` with endpoint contracts.
  4. `task-003` unlocks. Teammate `frontend-specialist` claims `task-003` and implements the dashboard components using verified API contracts.
  5. `task-004` unlocks. Teammate `test-engineer` claims `task-004`, executes Playwright integration suite, verifies assertions, and marks task complete.
  6. Team Lead `architect` reviews all artifacts, confirms zero regressions, and delivers final sign-off.

---

### Example 4: Mobile Platform & Security Audit Team (Agent Team System)

#### User Prompt:
```markdown
Task:
Team Objective: Implement biometric authentication and secure token storage for iOS and Android with automated security penetration audit.

Context:
- Project Tech Stack: React Native, Expo, TypeScript, SecureStore, Biometrics API
- Cross-Functional Roles: Mobile Developer (Lead), Security Specialist, Mobile Automation Engineer
- Team Coordination: Shared Task Board (.agent/context/TEAM_BOARD.md) & Teammate-to-Teammate P2P Messaging

Deliverables:
Work Backlog:
1. [ ] task-001: Biometric auth service wrapper with FaceID and TouchID fallback handling.
2. [ ] task-002: Keychain secure token storage adapter. (Depends on: task-001)
3. [ ] task-003: Mobile penetration audit against OWASP Mobile Top 10 vulnerabilities. (Depends on: task-002)
4. [ ] task-004: Appium cross-platform automation test suite for authentication flows. (Depends on: task-001, task-002)

Verification:
Team Delivery Gate:
- Run npm run test:mobile && npm run audit:security
- Confirm zero critical vulnerabilities and verified test passing across simulators.
```

#### Autonomous Execution Result:
* **Execution System**: Agent Team System (Collaborative Team Structure)
* **Autonomous Team Lead**: `mobile-developer`
* **Autonomous Team Roster**: `mobile-developer`, `security-specialist`, `mobile-automation-engineer`
* **Auto-Injected Skills**: `team-coordination`, `mobile-design`, `security-scan`, `mobile-automation`, `clean-code`
* **Autonomous Actions**:
  1. Team Lead `mobile-developer` scaffolds team `team-mobile-auth`, publishes work DAG to shared board, and commits to SQLite.
  2. Teammate `mobile-developer` claims unblocked `task-001`, implements biometric hooks, and marks complete.
  3. Teammate `mobile-developer` claims unblocked `task-002`, implements Keychain storage adapter, and marks complete.
  4. Downstream tasks `task-003` and `task-004` unlock concurrently.
  5. Teammate `security-specialist` claims `task-003`, audits secure storage against token leakage, and sends direct peer message to `mobile-developer`.
  6. Teammate `mobile-automation-engineer` claims `task-004`, executes Appium test suite, and confirms all gestures and bio-prompts pass.
  7. Team Lead `mobile-developer` verifies full compliance and provides delivery sign-off.

---

## Manual On-Demand Workflows & Prompt Templates

Neither the AI Security Guardrails audit nor the Codebase Knowledge Graph generation is executed automatically upon installation. They are completely optional and run strictly on-demand as per user choice to preserve user sovereignty, privacy, and performance.

---

### 1. AI Security & Log4j Vulnerability Audit

Hyper Agents Force provides deterministic security guardrails to shield credentials, mask sensitive tokens and PII, sanitize prompt injections, and scan for vulnerable Log4j libraries.

#### Prompt Template:
```markdown
Task:
Audit workspace security guardrails and scan for Log4j vulnerabilities.

Context:
- Project Tech Stack: {e.g., Java, Spring Boot, Maven, React, Node.js}
- Constraints: Ensure zero secret leakage, shield .env files, scan for CVE-2021-44228
- Relevant Files: {e.g., pom.xml, .env, package.json}

Deliverables:
1. Security audit report covering credential shielding and PII exposure.
2. Log4j dependency scan report identifying vulnerable components.
3. Automated version patch if vulnerabilities exist.

Verification:
- Run meet secure audit
- Run meet secure log4j --fix
```

#### CLI On-Demand Invocations:
```bash
# Run security audit on workspace
hyper-agents-force secure audit

# Scan Java / JVM dependencies for Log4j CVEs
hyper-agents-force secure log4j

# Scan and automatically patch vulnerable Log4j coordinates to 2.17.1
hyper-agents-force secure log4j --fix
```

---

### 2. Codeflow AST Knowledge Graph & Interactive Canvas

Inspired by Codeflow and Graphify, Hyper Agents Force includes a zero-configuration codebase knowledge graph engine. It parses Python, TypeScript, JavaScript, Go, Rust, and Java into a local SQLite graph store (`.agent/context/code_graph.db`), automatically exports Neo4j Cypher statements to [`.agent/context/code_graph.cyp`](file:///d:/Personal/hyper-agents-force/.agent/context/code_graph.cyp) without requiring Neo4j or environment variables, and generates a standalone offline interactive visual canvas at [`.agent/context/CODEFLOW_GRAPH.html`](file:///d:/Personal/hyper-agents-force/.agent/context/CODEFLOW_GRAPH.html).

#### Prompt Template:
```markdown
Task:
Parse codebase AST knowledge graph and generate interactive visual codeflow canvas.

Context:
- Project Tech Stack: {e.g., Python, TypeScript, Go}
- Storage: Embedded SQLite (Zero environment variables required)
- Output Artifacts: .agent/context/code_graph.cyp and .agent/context/CODEFLOW_GRAPH.html

Deliverables:
1. SQLite knowledge graph mapping files, classes, functions, and import dependencies.
2. Neo4j-compatible Cypher export for optional graph DB ingestion.
3. Standalone offline HTML visualizer with pan, zoom, and node filtering.

Verification:
- Run meet graph build
- Run meet graph visual
```

#### CLI On-Demand Invocations:
```bash
# Build SQLite AST knowledge graph and generate code_graph.cyp
hyper-agents-force graph build

# Inspect AST node counts, relationship edges, and dependency statistics
hyper-agents-force graph stats

# Query callers, callees, and dependencies for a symbol
hyper-agents-force graph query "AuthService"

# Generate standalone offline visual canvas
hyper-agents-force graph visual
```

---

### 3. Greenfield Tech Stack & Architecture Advisor

When starting a project from scratch, the Tech Stack Advisor dynamically evaluates your idea, target audience, throughput requirements, and team constraints to recommend programming languages, frameworks, databases, and deployment architectures. Recommendations are computed dynamically via multi-criteria matrix evaluation rather than hardcoded tables.

#### Prompt Template:
```markdown
I have an idea about {detailed description of your project concept, target audience, expected scale, and functional requirements}.
```

#### Alternative Structured Prompt Template:
```markdown
Task:
Evaluate technology stack and system architecture for a new greenfield project.

Idea:
{Describe idea, e.g., Real-time collaborative whiteboard with multiplayer presence}

Audience & Scale:
- Target Users: {e.g., Enterprise design teams, 10,000 concurrent sessions}
- Throughput: {e.g., Realtime sub-50ms sync, WebSocket streaming}
- Platform: {e.g., Web, iOS, Desktop}

Deliverables:
1. Primary language and framework evaluation with trade-off rationale.
2. Database and cache selection matching data access patterns.
3. System architecture topology and deployment strategy.

Verification:
- Run meet advise "{Idea description}"
```

#### CLI On-Demand Invocations:
```bash
# Run dynamic advisory analysis
hyper-agents-force advise "Realtime collaborative canvas with CRDT synchronization"

# Output structured recommendations in JSON format
hyper-agents-force advise "High-frequency crypto trading engine" --json
```

---

### 4. Read-Only Ask Mode & Dense Response Protocol

Ask Mode provides a guaranteed read-only Q&A environment with zero codebase modifications and zero file writes. It answers questions using the High-Efficiency Dense Response Protocol ([`global-rules/standards/dense-communication.md`](file:///d:/Personal/hyper-agents-force/global-rules/standards/dense-communication.md)), enforcing the 9 rules:
1. **Answer first**: Pattern `[thing] [action] [reason]. [next step].`
2. **Kill ceremony**: Zero greetings, hedging, or filler words.
3. **Short words**: Concise vocabulary without invented abbreviations.
4. **Articles optional**: High signal-to-noise ratio.
5. **One idea per sentence**: ASD-STE100 standard floor (under 20 words per sentence).
6. **Payload verbatim**: Exact code blocks, paths, and decisive error lines.
7. **Bounded status**: Status text only for phase shifts.
8. **User language**: Match language strictly.
9. **Zero caveman**: Professional, dense, direct communication without artificial roleplay.

#### Prompt Template:
```markdown
[ASK MODE]
{Your technical question, debugging inquiry, or architectural question}
```

#### CLI On-Demand Invocations:
```bash
# Ask questions in read-only mode with dense response protocol
hyper-agents-force ask "Why is the SQLite memory query bounded to LIMIT 5?"

# Output raw high-density answer payload
hyper-agents-force ask "What are the dependencies of the security guardrails engine?" --raw
```

---

## Memory & Shared Board System

Hyper Agents Force features a **unified SQLite + Markdown cognitive architecture**:

1. **Structured SQLite Database (`.agent/memory/memory.db`)**:
   - `memories`: Durable records of architectural patterns, system invariants, decisions, and failure solutions.
   - `blackboard_events`: Inter-agent event journal tracking active workflows and task ownership.
   - `agent_teams`: Active collaborative teams, team identifiers, leads, and objectives.
   - `team_members`: Team roster, member specialist roles, and assigned skill configurations.
   - `team_tasks`: Centralized claim-based DAG task board tracking states (`BLOCKED`, `UNCLAIMED`, `IN_PROGRESS`, `DONE`), dependencies, and artifacts.
   - `team_messages`: Peer-to-peer inter-agent communication stream for review requests and direct handoffs.
   - **FTS5 Virtual Table**: Provides sub-millisecond full-text semantic keyword search.
   - **Bounded Query Execution**: All agent queries enforce `LIMIT 5` to safeguard context limits.

2. **Dual-Mode Human Markdown Sync**:
   - Automatically maintains synchronized human-readable Markdown files:
     - [`.agent/memory/ARCHITECTURE_MEMORY.md`](file:///d:/Personal/hyper-agents-force/.agent/memory/ARCHITECTURE_MEMORY.md)
     - [`.agent/memory/SESSION_FAILURES.md`](file:///d:/Personal/hyper-agents-force/.agent/memory/SESSION_FAILURES.md)
     - [`.agent/context/BLACKBOARD.md`](file:///d:/Personal/hyper-agents-force/.agent/context/BLACKBOARD.md)
     - [`.agent/context/TEAM_BOARD.md`](file:///d:/Personal/hyper-agents-force/.agent/context/TEAM_BOARD.md)

---

## Verification & Test Suite

Verify that all agents, skills, memory engines, routing matrices, and multi-platform adapters function correctly:

```bash
# Run multi-platform synchronization and compliance audit (zero emojis & byte caps)
python bin/build_platforms.py

# Run complete test suite (Platforms, Intelligent Routing, Memory SQLite/FTS5, HITL, Workflow Engines, CLI)
python -m pytest .agent/scripts/ -v

# Run 110-Agent Comprehensive Prompt-Trigger Matrix Verification
python .agent/scripts/test_all_108_agents.py

# Re-index Catalog Summary
python .agent/scripts/analyze_catalog.py
```

Expected result:
```
======================= 18 passed in 21.12s =======================
TEST RUN COMPLETED: Passed: 110 / 110 (100.0%)
```