# Global Engineering Rules

This directory contains workspace-wide behavioral guidelines, development standards, and debugging protocols for day-to-day software engineering and multi-agent coordination.

## Directory Structure

### 1. `debugging/`
- `systematic-debugging.md` - Mandatory systematic four-phase debugging protocol before applying fixes.
- `root-cause-tracing.md` - Backward execution and dataflow tracing to isolate the root defect.
- `condition-based-waiting.md` - Deterministic polling and async condition checks to prevent flaky tests.
- `defense-in-depth.md` - Multi-layer validation and defensive assertion boundaries.

### 2. `testing/`
- `test-driven-development.md` - Red-Green-Refactor iron law and test construction standards.
- `testing-anti-patterns.md` - Detection and elimination of testing antipatterns and mock abuse.
- `verification-before-completion.md` - Verification gates and evidence checklist before declaring task completion.

### 3. `planning/`
- `brainstorming.md` - Requirements clarification, architecture exploration, and design alignment.
- `writing-plans.md` - Bite-sized, verifiable task implementation plan authoring.
- `executing-plans.md` - Checkpoint-driven execution against detailed task specifications.

### 4. `execution/`
- `subagent-driven-development.md` - Isolated subagent dispatch per task with verification gates.
- `dispatching-parallel-agents.md` - Concurrent agent dispatch across non-conflicting modules.
- `finishing-a-development-branch.md` - Clean branch integration and verification before merging.

### 5. `code-review/`
- `requesting-code-review.md` - Pre-merge code review dispatch and checklist enforcement.
- `receiving-code-review.md` - Objective evaluation, response, and verification of review feedback.
- `code-reviewer.md` - Specialist code reviewer subagent prompt template.

### 6. `standards/`
- `karpathy-guidelines.md` - Concrete coding discipline to avoid LLM hallucinations, bloat, and regression.
- `superpowers.md` - Disciplined software engineering standards and adaptive protocol.
- `using-superpowers.md` - Guidelines for invoking and following superpower methodologies.
- `caveman.md` - High-efficiency, low-token communication mode for rapid interaction.
- `ponytail.md` - Minimalist coding standard to eliminate dead code and over-engineered abstractions.
