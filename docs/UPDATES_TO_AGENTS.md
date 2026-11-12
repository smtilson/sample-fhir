# Updates to Agent File (`AGENTS.md`) — Changelog & Audit Trail

This document provides a historical record of updates made to [`AGENTS.md`](../AGENTS.md), documenting the evolution of rules governing how AI agents operate in this repository.

---

## 1. Summary of Changes: Old Rules vs. Updated Rules

| Category | Old Rule / Initial State | Updated Rule | Rationale / Origin |
| :--- | :--- | :--- | :--- |
| **Commit Message File & Location** | Draft a commit message in a "separate document" after tickets are completed or partially addressed. | Draft commit messages into `docs/git/<branch_name>/DRAFT_COMMITS.md` (e.g., `docs/git/practice_project/DRAFT_COMMITS.md`). Exclude `docs/git/` from version control via `.gitignore`. | `[Q-AGENT-GIT-02]`: Ensures commits are organized per-branch, tracked locally, and not committed to git. |
| **Commit Message Lifecycle & Format** | Summarize changes and reference tickets; format unspecified. | Use **Conventional Commits** (`feat(scope): [TICKET-ID] summary`). File structured with `## Pending Draft Commits` at the top and `## Adopted Commits` at the bottom. Order is preserved. Agents check `git log` to verify adoption. | `[Q-AGENT-GIT-02]`: Standardizes format across models and maintains an audit trail of adopted vs. pending commits. |
| **Git Command Permissions** | *"Do not make git commands yourself without permission from the user under any circumstances."* | **Strict Command Separation:**<br>• **Allowed Read-Only:** `git status`, `git diff`, `git log`, `git branch --show-current`, bare `git branch --list`.<br>• **Strictly Forbidden Mutating:** `git commit`, `git push`, `git checkout`, `git switch`, `git branch -d/-D`, `git reset`, `git rebase`, `git merge`. | `[Q-AGENT-GIT-01]`: Enables agents to inspect status and diffs without asking, while completely preventing unintended mutations or branch deletion. |
| **Branch Switching Safety** | Unspecified. | **Absolute Prohibition:** Agents must NEVER switch or change the working branch without prior notification, explicit user permission, and a detailed explanation of why. | `[Q-AGENT-GIT-01]`: Prevents context corruption and unintended branch checkouts. |
| **Branch Naming Convention** | Suggest when new branches should be created; naming unspecified. | Branch names must follow: `feat/<feature-slug>(<ticket-id>)` (e.g., `feat/user-model(smp-ep1-tk01)`). Agents must specify which branch it is cut from and merged into. | `[Q-AGENT-GIT-03]`: Explicit naming standard compatible with any AI model. |
| **Semi-TDD 'Second' Execution Flow** | Write failing tests after initial function is written but before code is finished. | **User-Led Coding in Ask Mode:** The user writes code with agent guidance in Ask Mode. Once a function is drafted, the agent proposes unit tests, creates test files, writes commented tests & fixtures, and prompts the user to inspect/run them. | `[Q-AGENT-TEST-01]`: Keeps the user in full control of core application code while leveraging the agent for thorough test creation. |
| **Automated Test Execution & Loop Prevention** | Unspecified whether agents could run test commands or fix loops. | **Strict Anti-Loop Boundary:** Agents have permission to run read-only test runners (`pytest`, `flutter test`), but **MUST STOP IMMEDIATELY if tests fail**. Agents are strictly forbidden from entering an autonomous fix-and-retest loop. Present failure output to user immediately. | `[Q-AGENT-TEST-02]`: Prevents loss of visibility and runaway agent loops modifying code without user oversight. |
| **Mocking & Database Boundaries** | Backend testing stack listed, but mocking boundaries unspecified. | Unit and repository tests must strictly use **in-memory mocks** (`mongomock-motor`, in-memory test doubles) set up by fixtures to run fast and self-contained. Integration database requirements are deferred. | `[Q-AGENT-TEST-03]`: Ensures unit tests run instantly and offline without Docker dependencies. |
| **Pre-Execution Command Descriptions** | Commands were explained with brief or bundled descriptions, sometimes appearing after tool execution prompts. | **Explanation First in Text:** Before any terminal command is invoked, the agent must output a clear, verbose description in chat text first (command, rationale, parameter breakdown) so the user reads it before clicking the "Allow" button. | User requirement: Ensure full comprehension of command effects before approval prompt appears. |
| **Command Execution & Reporting Sequence** | Multiple commands could be batched in a single turn, resulting in repeated "Allow" popups without intermediate feedback. | **Strict Single-Command & Interleaved Reporting:** Agents are strictly forbidden from batching terminal commands. Run exactly ONE command at a time. The post-execution report (Actual result, Outcome assessment, Diagnostics) must be displayed in chat before any subsequent command can be proposed or approved. | User requirement: Eliminate rapid-fire approval popups and guarantee full visibility between command steps. |
| **Atomic Test Responsibilities** | Tests bundled multiple lifecycle operations together (e.g. create + read, or update + delete). | **Strictly Atomic Tests:** Each test verifies exactly ONE operation or failure mode. Never bundle create/read or update/delete. Test database-level CRUD, field validation, and database constraints (`DuplicateKeyError`) in `tests/unit/` *before* testing HTTP API routes in `tests/api/`. | User requirement: Ensures failures identify the precise broken operation without ambiguity. |
| **Layered Fixtures Architecture** | Tests performed inline database insertions or ad-hoc data setup. | **Two-Tier Fixture Hierarchy:** Fixtures must be structured in clean layers: 1) Raw data fixture returning a list of dictionaries; 2) Persisted instances fixture accepting the raw data and inserting records into the in-memory database; 3) Tests consume the appropriate fixture layer. | User requirement: Promotes DRY, modular, and maintainable test fixtures across unit and API suites. |

---

## 2. Complete Record of Dialogue & Clarification Questions

The following dialogue between **Devin** and **S** (the user) took place in Section 4 of `AGENTS.md` and led directly to the updated rules:

---

### [Q-AGENT-GIT-01] Read-Only vs. Mutating Git Commands

**Devin:** The current rule states: *"Do not make git commands yourself without permission from the user under any circumstances."*
- Does this restriction apply only to **mutating commands** (`git commit`, `git push`, `git checkout -b`, `git merge`, `git reset`, `git rebase`)?
- Can agents run **read-only inspection commands** freely without asking (`git status`, `git diff`, `git log`, `git branch`)?
*(Note: Allowing read-only commands is recommended because agents need to inspect file diffs and status to draft accurate commit messages and verify what changed).*

**S:** It only applies to mutating commands. Read-only commands are allowed. However, do not change the working branch without permission, notification, and an explanation of why. I am concerned that if I allow the agent to use the read only `git branch` command it might pass it a flag like ` -d` and delete a branch. How do we structure the instructions to prevent this?

**Devin:** To prevent unintended branch deletion or mutation, we structured the rule in Section 1.7 as a strict whitelist:
- Agents are permitted to run only specific read-only commands: `git status`, `git diff`, `git log`, `git branch --show-current`, and `git branch --list` (strictly without flags).
- Flags that delete or rename branches (`-d`, `-D`, `-m`, `-M`, `-c`, `-C`) are explicitly categorized as prohibited mutating actions.
- Branch switching (`git checkout`, `git switch`) is strictly forbidden without prior notification and explicit user approval.

---

### [Q-AGENT-GIT-02] Draft Commit Messages Document Location & Format

**Devin:** The current rule states: *"After tickets have been completed or partially addressed draft a commit message that summarizes the changes and includes references to the tickets that were addressed in a separate document."*
- What file path should be used for this document? (e.g., `docs/DRAFT_COMMITS.md` or `COMMITS.md` at the project root?)
- Should this file act as a running append-only history of drafted commits, or an active staging file overwritten with the latest drafted commit?
- Should commit messages adhere to Conventional Commits format (e.g., `feat(auth): [SMP-EP1-TK02] implement password hashing and JWT token issuance`)?

**S:** The file path should be something like `docs/git/<branch_name>/DRAFT_COMMITS.md` and all of the draft commits for that branch should be appended to the file. When a commit message has been adopted (is there a way that you can see this?) the relevant draft commit should be marked as complete or something similar and moved to a section of the file so only the unadopted commits are visible at the top. The relative orders of used and unused draft commit messages should be preserved. This file should not be over written (I may edit it later maybe). Use the conventional format. These commit drafts files should be in `.gitignore`.

**Devin:** Yes, agents can easily verify if a commit message was adopted! Agents can run read-only `git log -n 5` or `git log --oneline`. When a commit in `git log` matches the subject of a pending draft commit, the agent marks it adopted and moves it from `## Pending Draft Commits` to `## Adopted Commits` at the bottom of `docs/git/<branch_name>/DRAFT_COMMITS.md`. We have also added `docs/git/` to `.gitignore`.

---

### [Q-AGENT-GIT-03] Branch Naming & Base Branch Conventions

**Devin:** When an agent suggests creating a new branch for a ticket or feature:
- What naming pattern should the agent suggest? (e.g., `<ticket-id>/<short-description>`, such as `smp-ep1-tk01/user-model` or `feat/user-model`?)
- What branch should new feature branches be cut from and merged into? (`practice_project`, `main`, or another target branch?)

**S:** Branch names should follow the pattern `feat/user-model(<ticket-id>)`. They should be cut and merged into the branch they are relevant to.

**Devin:** Understood. Agents will format suggested branch names as `feat/<feature-slug>(<ticket-id>)` (e.g. `feat/user-model(smp-ep1-tk01)`) and always explicitly state the relevant base branch it should be branched from and merged into.

---

### [Q-AGENT-TEST-01] 'Semi-TDD Second' Agent Execution Flow

**Devin:** The current rule specifies: *"Semi Test-Driven Development (TDD) 'Second': After initial drafts of functions make suggestions to work on tests for those functions... Write failing unit/integration tests after initial function is written but before the code is necessarily finished."*
When an agent is tasked with implementing a ticket:
- **Option A (Autonomous Flow):** The agent writes the initial function/class skeleton, writes the failing unit tests, runs them to confirm failure, then implements the complete function logic until tests pass.
- **Option B (Interactive Prompting Flow):** The agent drafts the initial function signature/skeleton, stops and prompts you: *"I have drafted the initial function. Would you like me to write the tests now, or would you like to review first?"*
- **Option C:** A different specific sequence you prefer.

**S:** I want to write as much of the code as possible using suggestions from the agent in Ask Mode. I then would want some tests to be written. I am not super confident that the agent will write the appropriate tests. After a function is written or worked on I then want the agent to propose some unit tests, create the relevant files and/or directories,then write the tests and fixtures (appropriately commented), and then prompt me to run the tests to see the results.

**Devin:** Understood. The workflow is user-led: you write the application code using agent guidance in Ask Mode. Once a function is drafted, the agent proposes unit tests, creates the test files/directories, writes the tests and fixtures with clear explanatory comments, and prompts you to run the tests and review the results.

---

### [Q-AGENT-TEST-02] Automated Test Execution Permissions

**Devin:** When an agent writes or modifies code:
- Does the agent have blanket permission to execute non-mutating test commands via WSL (`wsl -e bash -lc "pytest ..."` or `flutter test`) to verify that tests pass?
- Or must the agent ask your permission before running any terminal command, including test runners?

**S:** The agent can run tests but should not move past them if they fail so that I can look at what is going on. I do not want the loop where the agent runs the tests, goes fixes the code, then runs the tests, and works on the code some more etc. I want to avoid that loop as much as possible because then I will lose sight of what is going on in the code base.

**Devin:** Understood. The agent has permission to execute read-only test commands via WSL (`pytest`, `flutter test`), but with a strict anti-loop boundary: if any test fails, the agent must stop immediately, print the failure output, and hand control back to you. The agent is strictly prohibited from entering an autonomous fix-and-retest loop.

---

### [Q-AGENT-TEST-03] Mocking Strategy & Database Boundaries for Tests

**Devin:** When writing backend tests in pytest:
- Should unit and repository tests strictly use **in-memory mocks** (`mongomock-motor`, in-memory repository doubles) so tests run instantly and offline without requiring a running Docker database?
- Should integration tests assume a local MongoDB container is running via `docker-compose`, or should the agent prioritize tests that run cleanly without external service dependencies?

**S:** Unit tests should use in memory mocks or in memory test dbs that are sete up by fixtures. I am not sure about integration tests yet.

**Devin:** Understood. All unit and repository tests will strictly use in-memory mocks (`mongomock-motor`, test doubles) configured through fixtures to run fast and self-contained. Integration database dependencies remain deferred until decided.
