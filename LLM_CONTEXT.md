# LLM Context & Agent Reference

Purpose: provide a single reference for LLM-driven agents making code changes so all modifications stay aligned with project architecture and conventions.

**Project Overview**
- **Name:**: `hackathon-2025` (local workspace root)
- **Entry points:**: `app.py` (application runner), `logic.py` (business logic), `ui_components.py` (UI helpers)
- **Dependencies:**: listed in `requirements.txt` — update when adding libraries.

**High-level Architecture**
- **Separation of concerns:**: Keep UI in `ui_components.py`, core algorithms and domain logic in `logic.py`, and orchestration / app lifecycle in `app.py`.
- **Single responsibility:**: Each module should have a clear responsibility; avoid mixing UI rendering with core logic.
- **State management:**: Prefer pure functions in `logic.py` with explicit inputs/outputs for easier testing and traceability.

**Agent Roles & Permissions**
- **Allowed automated edits:**: Small feature additions, bug fixes, tests, documentation updates, refactors that preserve public behavior.
- **Restricted edits (require human review):**: Major architecture changes, new persistent storage layers, external integrations (APIs, DB), changes to `requirements.txt` that add native dependencies, or anything that may require infra changes.

**Agent Checklist Before Modifying Code**
1. **Read:**: Open `LLM_CONTEXT.md`, `app.py`, `logic.py`, and `ui_components.py` to understand current structure.
2. **Intent:**: Confirm the exact change, inputs, and expected outputs (unit-level). Include a short one-line rationale.
3. **Scope:**: Limit edits to the smallest set of files needed. Prefer adding new functions rather than modifying many files.
4. **Tests:**: Add or update unit tests for any behavior change. If tests are not present, add a minimal test demonstrating the change.
5. **Run quick checks:**: Run linters and tests locally (see Commands below).
6. **Commit:**: Use the commit message format below and request a human review for restricted changes.

**Coding & Style Guidelines**
- **Formatting:**: Use `black` for formatting (if installed); otherwise follow PEP8 conventions.
- **Type hints:**: Add Python type annotations for public functions where reasonable.
- **Docstrings:**: Document public functions with a one-line summary, parameters, return values, and exceptions.
- **Logging:**: Use the Python `logging` module for operational messages; avoid prints in library code.

**Testing & Validation**
- **Unit tests:**: Place tests adjacent or in a `tests/` folder (create it if missing). Tests should run quickly (<2s each ideally).
- **Manual run:**: If change affects runtime behavior, run `python app.py` locally and verify the intended flow.

**Run Commands**
- **Run app:**: `python app.py`
- **Install deps:**: `pip install -r requirements.txt`
- **Run tests (example):**: `pytest` (if tests exist)

**Commit & PR Guidelines**
- **Commit message format:**: `type(scope): short description\n\nBody (optional)` where `type` is `feat`, `fix`, `chore`, `refactor`, or `docs` and `scope` is the module, e.g., `logic`.
- **PR description:**: Always include: what changed, why, how to test, and any migration steps.

**Change Logging & Architecture Decisions**
- **Where to record decisions:**: Update this `LLM_CONTEXT.md` under a `Decision Log` section for any architecture-level decisions.
- **Changelog:**: For visible changes, add an entry to a `CHANGELOG.md` (or append to this file under `Change Log`).

**Examples: Agent Prompt Templates**
- **Small change / bugfix:**
  - Task: Fix function `foo()` in `logic.py` so it returns empty list instead of `None` when no results.
  - Required context: show `logic.py` function definition, current failing test or example call, desired return.
  - Output: Provide the exact patch (diff) and new/updated tests.

- **Feature addition (human review required if large):**
  - Task: Add new validation pipeline for user input.
  - Required context: API signature, expected validation rules, sample inputs/outputs, backward-compatibility constraints.
  - Output: Code + tests + README snippet explaining the behavior.

**Do's and Don'ts for Agents**
- **Do:**: Keep changes minimal and reversible, include tests, write clear commit messages, update documentation.
- **Don't:**: Push large refactors without approval, remove or rename public APIs without a migration plan, add heavy runtime dependencies silently.

**Rollback & Safety**
- For any risky change, include a single-commit reversible patch and explicit steps to revert.
- If tests fail or app runtime shows errors, revert the change and open an issue with logs and steps to reproduce.

**Decision Log**
- _(Add entries here for architecture/major-decision history — date, owner, summary, impact)_

---
_This file is the canonical LLM-facing context. Update it whenever architecture, conventions, or workflows change._
