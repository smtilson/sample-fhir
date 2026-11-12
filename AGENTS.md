# Agent Interaction & Project Guidelines

This file records operational rules, interaction protocols, and environment setup instructions for AI agents working in this repository.

---

## 1. Document-Based Collaboration Protocol

The user prefers an interactive, document-centric planning and review process before implementing the code themselves (primarily via tickets):

1. **Structured Questions Format:**
   - Architectural and technical decision questions posed by Devin must have unique tags (e.g. `[Q-BACKEND-01]`, `[Q-SAMPLE-ODM-01]`) and be prefaced with:
     ```markdown
     #### [Q-SAMPLE-ODM-01] Question Title
     **Devin:** <Context, options, and tradeoffs>
     **S:** <Placeholder for user answer>
     ```
2. **User Responses & Devin Follow-ups:**
   - The user writes answers or follow-up questions under `**S:**`.
   - When the user asks a question in the document, Devin must add the answer directly into the document, explicitly labeled as:
     ```markdown
     **Devin:** <Devin's answer to the user's question>
     ```
3. **Cognito Comparison Annotations:**
   - Whenever discussing authentication in the sample app or reviewing tickets, include notes explaining how that implementation maps to **AWS Cognito**, signed as:
     ```markdown
     **Devin re-Cognito:** [Explanation of Cognito equivalent/integration]
     ```
4. **Change Approval:**
   - After answering questions or incorporating feedback into the architecture, always summarize changes and ask for permission before modifying the development plan, tickets, or code.
5. **Record of Development Process:**
   - When decisions or changes are made, do not delete previous content in the planning document. You can strikethrough the old content or add a label indicating things have been changed, reference the place that led to the decision (the relevant question for example).
   - Tickets should never be deleted even if the development plan changes and the content of a ticket should not be changed, just updated to reflect decisions.
   - The development process and decisions made should be recorded in the relevant documents.
6. **Commit Messages:**
   - **Updated Rule:** Draft commit messages must be written to `docs/git/<branch_name>/DRAFT_COMMITS.md` (e.g., `docs/git/practice_project/DRAFT_COMMITS.md`).
   - **Updated Rule:** Commit messages must follow the **Conventional Commits** format with ticket references:
     `feat(scope): [TICKET-ID] short imperative summary`
   - **Updated Rule:** The file must maintain two distinct sections to preserve order and history:
     - `## Pending Draft Commits` (visible at the top)
     - `## Adopted Commits` (historical record at the bottom)
     When an agent checks `git log` and detects that a draft commit has been committed, it marks the commit as adopted and moves it to the `## Adopted Commits` section without overwriting or deleting historical entries.
   - **Updated Rule:** The entire `docs/git/` directory must be excluded in `.gitignore`.
   - Notify the user when a draft commit message is ready for review.

7. **Git Usage & Branch Safety:**
   - **Updated Rule:** **Strict Command Separation:**
     - **Allowed Read-Only Inspection:** Agents may freely run `git status`, `git diff`, `git log`, and `git branch --show-current` without prompting.
     - **Controlled `git branch`:** Agents may only run bare `git branch` or `git branch --list` for listing. All mutating/deletion flags (`-d`, `-D`, `-m`, `-M`, `-c`, `-C`) are **strictly forbidden**.
     - **Strictly Prohibited Mutating Commands:** Agents must NEVER execute `git commit`, `git push`, `git checkout`, `git switch`, `git reset`, `git rebase`, `git merge`, or `git clean` without explicit user permission.
   - **Updated Rule:** **Branch Switching:** Do not change or switch the working branch under any circumstances without prior notification, explicit user permission, and a detailed explanation of why.
   - **Updated Rule:** **Branch Naming Pattern:** When suggesting a new branch for a ticket, use the format:
     `feat/<feature-slug>(<ticket-id>)` (e.g., `feat/user-model(smp-ep1-tk01)`).
     Always specify which branch it should be cut from and merged back into.
   - Suggest when commits, branches, and pull requests should be created.
---

## 2. Terminal & Environment Execution (WSL)

The user develops using **Windows Subsystem for Linux (WSL)**, where the Python virtual environment and development tools are configured.

### Rules for Executing Commands:
- **Do NOT run bare Windows `python` or `py.exe`**: The Windows environment may lack pip or have conflicting library paths.
- **Run all Python, pip, pytest, and backend terminal commands via WSL**:
  ```bash
  wsl -e bash -lc "cd /mnt/c/Users/seant/OneDrive/Desktop/main_repos/sample-fhir && <command>"
  ```
- **Workspace Path Mapping:**
  - Windows: `C:\Users\seant\OneDrive\Desktop\main_repos\sample-fhir`
  - WSL: `/mnt/c/Users/seant/OneDrive/Desktop/main_repos/sample-fhir`
- When activating a specific virtualenv in WSL, invoke the venv's python directly or source its activate script:
  ```bash
  wsl -e bash -lc "cd /mnt/c/Users/seant/OneDrive/Desktop/main_repos/sample-fhir && source <venv-path>/bin/activate && pytest"
  ```
- **Updated Rule:** **Strict Single-Command Execution (No Batching):**
  - Agents are **strictly forbidden** from batching, chaining, or executing multiple terminal commands in a single turn.
  - Run exactly **ONE command at a time** so the user has full oversight over every individual operation.
- **Updated Rule:** **Pre-Execution Explanation First:**
  - Before any terminal command is called, the agent must output a clear, verbose description in the chat text *first*, explaining:
    1. The exact command to be run.
    2. Why it is necessary.
    3. What every parameter/flag accomplishes.
  - This ensures the user reads the full explanation before seeing or clicking the "Allow" button.
- **Updated Rule:** **Mandatory Interleaved Reporting (Before Any Next Command):**
  - Immediately after a command finishes executing, the agent must render the **Post-Execution Structured Analysis** in the chat response:
    1. **Actual Result:** What the command produced or returned.
    2. **Outcome Assessment:** Whether this was the expected/desired result.
    3. **Diagnostic Analysis (if unexpected or failure):** Potential causes and concrete solutions.
  - The agent must **NEVER** issue, propose, or ask approval for a subsequent command until the previous command's post-execution report has been displayed to the user.

---

## 3. Engineering & Testing Standards

1. **Semi Test-Driven Development (TDD) 'Second' & Collaborative Coding:**
   - **Updated Rule:** **User-Led Coding in Ask Mode:** The user writes code with suggestions from the agent in Ask Mode.
   - **Updated Rule:** **Agent Test Authorship:** After a function is drafted, the agent proposes relevant unit tests, creates test files/directories (`tests/unit/`), and writes the tests and fixtures with thorough explanatory comments.
   - **Updated Rule:** **Inspection Prompt:** After writing tests, the agent prompts the user to review and run the tests.
   - **Updated Rule:** **Automated Test Execution & Strict Anti-Loop Policy:**
     - The agent is allowed to run non-mutating test commands via WSL (`pytest`, `flutter test`).
     - **CRITICAL:** If tests fail, the agent **MUST STOP IMMEDIATELY**.
     - Agents are **strictly forbidden** from entering an autonomous loop of: *fail test -> edit code -> re-test -> edit code*. Present the failure output to the user so the user maintains full visibility of the codebase.
   - **Updated Rule:** **Mocking Boundaries:** Unit and repository tests must strictly use in-memory mocks (`mongomock-motor`, in-memory test doubles) set up via fixtures so tests run self-contained and offline. Integration database requirements are deferred.
   - Python Backend: `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-mock`, `httpx` / `TestClient`.
   - Flutter Frontend: `flutter_test` (unit tests and headless `testWidgets` with `WidgetTester`), `mocktail` for API mocks.
2. **Architecture & Modularity:**
   - Use Clean / Hexagonal Architecture: domain logic and FHIR entities must remain decoupled from specific database drivers (Beanie/MongoDB/DocumentDB) and web frameworks.
   - Design data models to align with HL7 FHIR standards (`Task`, `Patient`, `Observation`).
3. **Cloud & Multi-Platform Readiness:**
   - Backend designed for local `docker-compose` and deployment to **AWS App Runner / ECS Fargate** and **Amazon DocumentDB**.
   - Flutter client designed for responsive multi-platform support, phased as:
     1. Browser (Flutter Web)
     2. Mobile (Android / iOS)
     3. Desktop (Windows)
   - Do NOT use swipe gestures for task management; use explicit checkboxes, action buttons, and confirmation dialogs.
4. **Documentation & Code Quality:**
   - All code must be thoroughly documented with docstrings and comments explaining complex logic, FHIR resource mappings, and business rules.
   - API endpoints must include comprehensive OpenAPI/Swagger documentation.
   - Code must follow PEP 8 style guidelines for Python and Dart linting rules.
   - Type hinting should be used consistently in Python and Dart.

---

## 4. Operational Clarification Questions (Git & Testing Parameters)

To ensure any AI model (across different providers and token budgets) behaves consistently without ambiguity, please answer the following operational questions. Once answered, these will become permanent instructions in this file.

#### [Q-AGENT-GIT-01] Read-Only vs. Mutating Git Commands
**Devin:** The current rule states: *"Do not make git commands yourself without permission from the user under any circumstances."*
- Does this restriction apply only to **mutating commands** (`git commit`, `git push`, `git checkout -b`, `git merge`, `git reset`, `git rebase`)?
- Can agents run **read-only inspection commands** freely without asking (`git status`, `git diff`, `git log`, `git branch`)?
*(Note: Allowing read-only commands is recommended because agents need to inspect file diffs and status to draft accurate commit messages and verify what changed).*

**S:** It only applies to mutating commands. Read-only commands are allowed. However, do not change the working branch without permission, notification, and an explanation of why. I am concerned that if I allow the agent to use the read only `git branch` command it might pass it a flag like ` -d` and delete a branch. How do we structure the instructions to prevent this?

**Devin:** To prevent unintended branch deletion or mutation, we structured the rule in Section 1.7 as a strict whitelist:
- Agents are permitted to run only specific read-only commands: `git status`, `git diff`, `git log`, `git branch --show-current`, and `git branch --list` (strictly without flags).
- Flags that delete or rename branches (`-d`, `-D`, `-m`, `-M`, `-c`, `-C`) are explicitly categorized as prohibited mutating actions.
- Branch switching (`git checkout`, `git switch`) is strictly forbidden without prior notification and explicit user approval.

#### [Q-AGENT-GIT-02] Draft Commit Messages Document Location & Format
**Devin:** The current rule states: *"After tickets have been completed or partially addressed draft a commit message that summarizes the changes and includes references to the tickets that were addressed in a separate document."*
- What file path should be used for this document? (e.g., `docs/DRAFT_COMMITS.md` or `COMMITS.md` at the project root?)
- Should this file act as a running append-only history of drafted commits, or an active staging file overwritten with the latest drafted commit?
- Should commit messages adhere to Conventional Commits format (e.g., `feat(auth): [SMP-EP1-TK02] implement password hashing and JWT token issuance`)?

**S:** The file path should be something like `docs/git/<branch_name>/DRAFT_COMMITS.md` and all of the draft commits for that branch should be appended to the file. When a commit message has been adopted (is there a way that you can see this?) the relevant draft commit should be marked as complete or something similar and moved to a section of the file so only the unadopted commits are visible at the top. The relative orders of used and unused draft commit messages should be preserved. This file should not be over written (I may edit it later maybe). Use the conventional format. These commit drafts files should be in `.gitignore`.

**Devin:** Yes, agents can easily verify if a commit message was adopted! Agents can run read-only `git log -n 5` or `git log --oneline`. When a commit in `git log` matches the subject of a pending draft commit, the agent marks it adopted and moves it from `## Pending Draft Commits` to `## Adopted Commits` at the bottom of `docs/git/<branch_name>/DRAFT_COMMITS.md`. We have also added `docs/git/` to `.gitignore`.

#### [Q-AGENT-GIT-03] Branch Naming & Base Branch Conventions
**Devin:** When an agent suggests creating a new branch for a ticket or feature:
- What naming pattern should the agent suggest? (e.g., `<ticket-id>/<short-description>`, such as `smp-ep1-tk01/user-model` or `feat/user-model`?)
- What branch should new feature branches be cut from and merged into? (`practice_project`, `main`, or another target branch?)

**S:** Branch names should follow the pattern `feat/user-model(<ticket-id>)`. They should be cut and merged into the branch they are relevant to.

**Devin:** Understood. Agents will format suggested branch names as `feat/<feature-slug>(<ticket-id>)` (e.g. `feat/user-model(smp-ep1-tk01)`) and always explicitly state the relevant base branch it should be branched from and merged into.

#### [Q-AGENT-TEST-01] 'Semi-TDD Second' Agent Execution Flow
**Devin:** The current rule specifies: *"Semi Test-Driven Development (TDD) 'Second': After initial drafts of functions make suggestions to work on tests for those functions... Write failing unit/integration tests after initial function is written but before the code is necessarily finished."*
When an agent is tasked with implementing a ticket:
- **Option A (Autonomous Flow):** The agent writes the initial function/class skeleton, writes the failing unit tests, runs them to confirm failure, then implements the complete function logic until tests pass.
- **Option B (Interactive Prompting Flow):** The agent drafts the initial function signature/skeleton, stops and prompts you: *"I have drafted the initial function. Would you like me to write the tests now, or would you like to review first?"*
- **Option C:** A different specific sequence you prefer.

**S:** I want to write as much of the code as possible using suggestions from the agent in Ask Mode. I then would want some tests to be written. I am not super confident that the agent will write the appropriate tests. After a function is written or worked on I then want the agent to propose some unit tests, create the relevant files and/or directories,then write the tests and fixtures (appropriately commented), and then prompt me to run the tests to see the results.

**Devin:** Understood. The workflow is user-led: you write the application code using agent guidance in Ask Mode. Once a function is drafted, the agent proposes unit tests, creates the test files/directories, writes the tests and fixtures with clear explanatory comments, and prompts you to run the tests and review the results.

#### [Q-AGENT-TEST-02] Automated Test Execution Permissions
**Devin:** When an agent writes or modifies code:
- Does the agent have blanket permission to execute non-mutating test commands via WSL (`wsl -e bash -lc "pytest ..."` or `flutter test`) to verify that tests pass?
- Or must the agent ask your permission before running any terminal command, including test runners?

**S:** The agent can run tests but should not move past them if they fail so that I can look at what is going on. I do not want the loop where the agent runs the tests, goes fixes the code, then runs the tests, and works on the code some more etc. I want to avoid that loop as much as possible because then I will lose sight of what is going on in the code base.

**Devin:** Understood. The agent has permission to execute read-only test commands via WSL (`pytest`, `flutter test`), but with a strict anti-loop boundary: if any test fails, the agent must stop immediately, print the failure output, and hand control back to you. The agent is strictly prohibited from entering an autonomous fix-and-retest loop.

#### [Q-AGENT-TEST-03] Mocking Strategy & Database Boundaries for Tests
**Devin:** When writing backend tests in pytest:
- Should unit and repository tests strictly use **in-memory mocks** (`mongomock-motor`, in-memory repository doubles) so tests run instantly and offline without requiring a running Docker database?
- Should integration tests assume a local MongoDB container is running via `docker-compose`, or should the agent prioritize tests that run cleanly without external service dependencies?

**S:** Unit tests should use in memory mocks or in memory test dbs that are sete up by fixtures. I am not sure about integration tests yet.

**Devin:** Understood. All unit and repository tests will strictly use in-memory mocks (`mongomock-motor`, test doubles) configured through fixtures to run fast and self-contained. Integration database dependencies remain deferred until decided.

