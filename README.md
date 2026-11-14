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
- [Installation & Quick Start](#installation--quick-start)
  - [1. Installation via UV (Recommended)](#1-installation-via-uv-recommended)
  - [2. Installation via Pip](#2-installation-via-pip)
  - [3. Installation via NPM / NPX](#3-installation-via-npm--npx)
- [CLI Reference](#cli-reference)
- [MCP Configuration & Tool Connection](#mcp-configuration--tool-connection)
- [Prompt Templates & Examples](#prompt-templates--examples)
  - [Standard Prompt Template](#standard-prompt-template)
  - [Example 1: Complex System Architecture](#example-1-complex-system-architecture)
  - [Example 2: Systematic Debugging & Root Cause Analysis](#example-2-systematic-debugging--root-cause-analysis)
  - [Example 3: AI & Machine Learning Pipeline Engineering](#example-3-ai--machine-learning-pipeline-engineering)
  - [Example 4: Multi-Agent Parallel Orchestration](#example-4-multi-agent-parallel-orchestration)
- [Memory & Blackboard System](#memory--blackboard-system)
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

## Installation & Quick Start

Hyper Agents Force provides native support for **UV**, **Pip**, and **NPM**.

### 1. Installation via UV (Recommended)

[UV](https://github.com/astral-sh/uv) provides sub-second virtualenv setup and package execution:

```bash
# Clone the repository
git clone https://github.com/your-username/hyper-agents-force.git
cd hyper-agents-force

# Option A: Install into existing project virtualenv
uv pip install -e .

# Option B: Run commands directly without installation
uv run hyper-agents-force --help

# Option C: Deploy to your current project workspace
uv run hyper-agents-force install -p

# Option D: Deploy to user global profile (~/.gemini/)
uv run hyper-agents-force install -u
```

### 2. Installation via Pip

```bash
# Clone and enter the repository
git clone https://github.com/your-username/hyper-agents-force.git
cd hyper-agents-force

# Install in editable mode
pip install -e .

# Verify installation
hyper-agents-force doctor

# Deploy into the current project workspace
hyper-agents-force install -p

# Deploy into user profile (~/.gemini/)
hyper-agents-force install -u
```

### 3. Installation via NPM / NPX

For JavaScript, TypeScript, and Node.js environments:

```bash
# Option A: Run directly with npx (zero installation)
npx hyper-agents-force -p       # Deploy .agent/ & GEMINI.md to current project
npx hyper-agents-force -u       # Deploy to user profile (~/.gemini/)
npx hyper-agents-force doctor   # Run diagnostic health check

# Option B: Install globally
npm install -g .
hyper-agents-force -p
```

---

## CLI Reference

The unified CLI (`hyper-agents-force`, `hyper`, `meet-ai`) provides complete control over your agents, memory, MCP, and workflows:

```bash
# System Health Check
hyper-agents-force doctor

# Multi-Level Deployment
hyper-agents-force install -p           # Current project directory
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

# Workflow Execution
hyper-agents-force run audit            # Run security, CVE, lint, and test audit
hyper-agents-force run plan-and-solve   # Run architecture planning & execution

# Intelligent Prompt Routing
hyper-agents-force answer "Design a PostgreSQL schema with Prisma"
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

## Prompt Templates & Examples

### Standard Prompt Template

Use this structured prompt format when interacting with Antigravity, Gemini CLI, or Claude Code. You do **not** need to manually specify agent names or skills—the runtime's Intelligent Routing Engine autonomously resolves the optimal specialist agent and injects the required skills based on your task and context:

```markdown
Task:
{Clear 1-2 sentence description of what needs to be accomplished}

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

### Example 1: Complex System Architecture

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
3. Architecture Decision Record (ADR-004) documenting the boundary choices.

Verification:
- Run npm run build
- Run npm test
- Verify no infrastructure dependencies are imported inside the domain core.
```

#### Autonomous Execution Result:
* **Autonomous Agent**: `code-architect`
* **Auto-Injected Skills**: `clean-code`, `architecture`, `architecture-decision-records`, `hexagonal-architecture`
* **Autonomous Actions**: Scans structural call hierarchy, isolates ports and adapters, writes domain entities with zero external dependencies, generates ADR-004, and validates build and test pipelines.

---

### Example 2: Systematic Debugging & Root Cause Analysis

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
* **Autonomous Agent**: `debugger`
* **Auto-Injected Skills**: `systematic-debugging`, `root-cause-tracing`, `clean-code`
* **Autonomous Actions**: Executes 4-phase debugging protocol: isolates leak without modifying production code, writes deterministic reproduction test, refactors to backpressure-aware Node stream pipeline, and confirms memory stabilization.

---

### Example 3: AI & Machine Learning Pipeline Engineering

#### User Prompt:
```markdown
Task:
Build an agentic research assistant pipeline in LangGraph with persistent SQLite checkpointing and semantic vector retrieval.

Context:
- Project Tech Stack: Python 3.11, LangGraph, ChromaDB, Gemini 2.0 Flash
- Constraints: Bounded context window, structured JSON output, citation verification
- Relevant Files: src/agents/researcher.py, src/pipeline/graph.py

Deliverables:
1. StateGraph implementation with researcher and reviewer agent nodes.
2. SQLite checkpoint saver for interrupt-and-resume execution.
3. Evaluation benchmark verifying retrieval faithfulness and answer relevance.

Verification:
- Run pytest tests/test_agent_pipeline.py
- Verify latency and token consumption metrics remain within budget.
```

#### Autonomous Execution Result:
* **Autonomous Agent**: `ai-engineer`
* **Auto-Injected Skills**: `agentic-frameworks`, `context-engineering`, `production-rag`, `inference-engineering`
* **Autonomous Actions**: Compiles StateGraph with cyclical review loop, configures SQLite checkpointing saver, implements token-bounded RAG retrieval, and executes evaluation benchmark.

---

### Example 4: Multi-Agent Parallel Orchestration

#### User Prompt:
```markdown
Task:
Coordinate a parallel full-stack feature release: create the database migration, implement the REST API endpoints, and build the responsive dark-mode React dashboard component simultaneously.

Context:
- Project Tech Stack: PostgreSQL, Prisma, Express/TypeScript, React 19, Tailwind CSS
- Constraints: Independent parallel execution across modules with verified integration
- Relevant Files: prisma/schema.prisma, src/api/routes.ts, src/components/Dashboard.tsx

Deliverables:
1. Database schema migration with optimized foreign key indexes.
2. REST API endpoints with request validation middleware.
3. Responsive dashboard UI component adhering to design standards.
4. End-to-end integration test validating full contract.

Verification:
- Run npx prisma validate
- Run npm run build
- Run npm test tests/e2e/feature.test.ts
```

#### Autonomous Execution Result:
* **Autonomous Agent**: `orchestrator`
* **Auto-Injected Skills**: `parallel-agents`, `multi-agent-orchestration`, `task-coordination`
* **Autonomous Actions**: Dispatches parallel subagents (`database-architect` for schema, `backend-specialist` for API, `frontend-specialist` for UI), orchestrates dependency ordering, writes real-time event telemetry to `.agent/context/BLACKBOARD.md`, and runs integration verification.

---

## Memory & Blackboard System

Hyper Agents Force features a **dual-tier persistent memory architecture**:

1. **Structured SQLite Database (`.agent/memory/memory.db`)**:
   - `architecture_memory`: Durable records of architectural patterns, decisions, and system invariants.
   - `session_failures`: High-fidelity records of bugs, stack traces, and verified solutions.
   - `blackboard_events`: Inter-agent message journal tracking active workflows and task ownership.
   - **FTS5 Virtual Table**: Provides sub-millisecond full-text semantic keyword search.
   - **Bounded Query Execution**: All agent queries enforce `LIMIT 5` to safeguard context limits.

2. **Dual-Mode Human Markdown Sync**:
   - Automatically maintains synchronized human-readable Markdown files:
     - [`.agent/memory/ARCHITECTURE_MEMORY.md`](file:///d:/Personal/hyper-agents-force/.agent/memory/ARCHITECTURE_MEMORY.md)
     - [`.agent/memory/SESSION_FAILURES.md`](file:///d:/Personal/hyper-agents-force/.agent/memory/SESSION_FAILURES.md)
     - [`.agent/context/BLACKBOARD.md`](file:///d:/Personal/hyper-agents-force/.agent/context/BLACKBOARD.md)

---

## Verification & Test Suite

Verify that all agents, skills, memory engines, and routing matrices function correctly:

```bash
# Run complete test suite (Intelligent Routing, Memory SQLite/FTS5, Workflow Engines, CLI)
python -m pytest .agent/scripts/ -v

# Run 110-Agent Comprehensive Prompt-Trigger Matrix Verification
python .agent/scripts/test_all_108_agents.py

# Re-index Catalog Summary
python .agent/scripts/analyze_catalog.py
```

Expected result:
```
======================= 16 passed in 5.90s =======================
TEST RUN COMPLETED: Passed: 110 / 110 (100.0%)
```