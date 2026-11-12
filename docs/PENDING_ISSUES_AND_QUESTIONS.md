# Pending Issues & Technical Questions

This document tracks unresolved technical issues, environmental friction points, dependency conflicts, and architectural open questions across the repository.

---

## 1. Dependency & Environment Issues

### [ISSUE-DEP-01] `aioboto3` and `boto3` Pip Dependency Resolution Hang

- **Status:** Open / Documented
- **Affected Files:** `requirements.txt`
- **Symptom:** Running `pip install -r requirements.txt` hangs indefinitely or takes an excessively long time during dependency resolution.
- **Root Cause Analysis:**
  1. **Strict Version Lock in `aiobotocore`:** `aioboto3` depends on `aiobotocore`, which pins `botocore` to an exact patch/minor version range (e.g., `botocore>=1.34.41,<1.34.42`). Meanwhile, standalone `boto3` also depends on `botocore`.
  2. **Pip Backtracking Storm:** In `requirements.txt`, `aioboto3>=12.3.0` has no upper bound. Pip's modern resolver starts at the latest version of `aioboto3`, sees that its required `botocore` conflicts with the latest `boto3`, and backtracks through dozens of historical releases. Each candidate wheel of `botocore` is ~13MB, resulting in gigabytes of repeated downloads and hours of resolver calculation.
  3. **WSL2 /drvfs + OneDrive I/O Amplification:** Unpacking hundreds of thousands of AWS service definitions across the WSL2 9P filesystem bridge (`/mnt/c/...`) into a folder monitored by Microsoft OneDrive causes aggressive file-locking and disk write penalties.
- **Immediate Workaround (Applied):**
  - For local backend development of the sample app, bypass the root `requirements.txt` and install only the lightweight backend package dependencies:
    ```bash
    pip install fastapi uvicorn pydantic pydantic-settings beanie motor bcrypt httpx pytest pytest-asyncio mongomock-motor
    ```
- **Proposed Long-Term Solutions:**
  1. **Pin Exact Compatible Triplet:** Pin `boto3`, `aioboto3`, and `aiobotocore` to exact known-compatible release versions (or let `pip-tools` / `uv` generate a locked `requirements.lock`).
  2. **Split Requirements Files:** Separate root dependencies into modular files:
     - `requirements/base.txt` (FastAPI, Pydantic, Beanie, Motor, httpx)
     - `requirements/dev.txt` (pytest, ruff, mypy)
     - `requirements/aws.txt` (boto3, aioboto3)
     - `requirements/ml.txt` (scikit-learn, pandas, numpy)
  3. **Evaluate `aioboto3` Necessity:** If async AWS calls are not strictly required for early S3 uploads, standalone `boto3` (run in a thread pool via `starlette.concurrency.run_in_threadpool`) avoids `aiobotocore` conflicts entirely.
- **Devin re-Cognito:** When AWS Cognito integration is implemented later, authentication token verification in FastAPI does *not* require `boto3` or `aioboto3`. Token verification only requires fetching the public JWKS JSON once via HTTP (`httpx`) and validating the JWT locally via `pyjwt[crypto]`. `boto3` is only needed if making admin API calls directly to Cognito User Pools (`AdminCreateUser`, etc.).

---

### [ISSUE-DEP-02] `passlib` Compatibility with Modern `bcrypt`

- **Status:** Open / Tracked
- **Affected Files:** `requirements.txt`, `sample_flutter_app/backend/pyproject.toml`
- **Symptom:** Note in `requirements.txt`: `# There is a passlib issue.`
- **Technical Context:**
  - `passlib==1.7.4` has not been updated since 2020.
  - When `bcrypt >= 4.0.0` is installed, `passlib` tries to read `bcrypt.__about__.__version__` (which was removed in bcrypt 4.0+), throwing a runtime warning or error.
- **Proposed Solutions:**
  1. Use direct `bcrypt` calls (`bcrypt.hashpw` and `bcrypt.checkpw`) directly without `passlib` as an intermediary.
  2. Or use `pwdlib` / `argon2-cffi` which natively supports modern Pydantic v2 and Python 3.10+.

---

### [ISSUE-DEP-03] `mongomock` `Database.list_collection_names()` Unexpected Keyword Argument `authorizedCollections`

- **Status:** Resolved / Shimmed in `tests/conftest.py`
- **Affected Files:** `sample_flutter_app/backend/tests/conftest.py`
- **Symptom:** During `init_beanie()`, Pytest raises:
  `TypeError: Database.list_collection_names() got an unexpected keyword argument 'authorizedCollections'`
- **Technical Context:**
  - Beanie 1.25+ queries collection caches by calling `self.database.list_collection_names(authorizedCollections=True, nameOnly=True)`.
  - PyMongo supports these keyword arguments, but `mongomock`'s signature only accepts `(session, filter, comment)`.
- **Solution Applied:**
  - Added a compatibility shim in `tests/conftest.py` intercepting `mongomock.database.Database.list_collection_names` to strip `authorizedCollections` and `nameOnly` before forwarding to mongomock's native implementation.

---

## 2. Environment & Tooling Friction

### [ISSUE-ENV-01] Virtual Environment on Windows Mount (`/mnt/c/`) & OneDrive

- **Status:** Open / Monitored
- **Context:** The repository and virtualenv `.venv` live under `C:\Users\seant\OneDrive\Desktop\...`.
- **Trade-offs:**
  - **Pros:** Files are accessible from Windows IDE and backed up by OneDrive.
  - **Cons:** WSL file I/O over `/mnt/c/` is significantly slower than native Linux ext4. OneDrive background sync actively locks `.pyc` and `site-packages` files during large `pip` operations.
- **Recommendation:** If I/O or terminal sluggishness becomes problematic, consider adding `.venv/` to OneDrive's sync exclusion list, or locating the virtual environment in native WSL storage (`~/.venvs/sample-fhir`).

---

## 3. Architecture & Design Questions

### [Q-PENDING-01] Backend Integration Testing Database Strategy
- **Context:** Unit tests use `mongomock-motor` in memory. The strategy for end-to-end integration tests (local Docker container vs. spinning ephemeral test containers with `testcontainers-python` vs. shared remote DB) remains to be selected when reaching Epoch 7.

---

## 4. Agent Operating Protocols & Planning Decisions

### [Q-AGENT-TICKETS-01] Protocol for Granular Ticket Authoring & Explicit Development Planning

- **Status:** Pending User Input
- **Target File to Update:** `AGENTS.md` (Section 1: Document-Based Collaboration Protocol & Section 3: Engineering Standards)
- **Context:**
  Engineering tickets should be decomposed into smaller, highly granular, atomic pieces so they serve as clean, unambiguous instructions during development. Bundling multiple layers (e.g., domain models + schemas + route wire-up) into a single ticket obscures verification, complicates test attribution, and makes step-by-step execution harder to follow. Furthermore, the overall development process needs to be more explicitly documented and planned before code is drafted.

#### Dialogue

**Devin:** To update `AGENTS.md` with permanent rules ensuring any AI agent writes tickets with the exact granularity, explicitness, and structure you want, please provide your guidance across these areas:

1. **Ticket Scope & Atomicity Threshold:**
   - What is the target boundary for a single engineering ticket?
   - For backend features, should every domain entity strictly follow the 3-tier division: (1) Document Model & Database CRUD, (2) Transport Schemas & DTO Validation, (3) Route Handlers & Application Wire-up?
   - For frontend features, how should tickets be split? (e.g., Data models -> API client service methods -> Reusable widgets -> Screen composition & state wiring?)

2. **Required Ticket Structure & Content:**
   - What mandatory sections must every ticket include? (e.g., Exact files to create/modify, explicit function/class signatures, specific HTTP endpoints and status codes, dedicated TDD test file path and exact assertion criteria).

3. **Pre-Implementation Planning & Approval Cadence:**
   - Before implementing an epoch or feature, should the agent always propose the decomposed, atomic ticket breakdown in chat and docs, requiring your explicit review and approval before touching code?

4. **Ongoing Process & Rationale Documentation:**
   - How should decisions, intermediate testing findings, and architectural pivots be recorded in the planning documents as work progresses across tickets?

**S:** 

---

### [Q-AGENT-DIFF-01] Protocol for Minimal, Surgical File Edits vs. Full-File Overwrites

- **Status:** Pending User Input
- **Target File to Update:** `AGENTS.md` (Section 1: Document-Based Collaboration Protocol)
- **Context:**
  When modifying existing files, agents should make minimal, surgical changes rather than rewriting or overwriting the entire file from scratch. Full-file overwrites pollute git diffs, obscure what actually changed, and force the user to process differences across an entire file when only a few lines or a single function needed modification.

#### Dialogue

**Devin:** To codify permanent instructions in `AGENTS.md` ensuring minimal, readable diffs:
1. **Mandatory Surgical Edits:** Should agents be strictly forbidden from using whole-file overwrites on existing files, requiring them to use targeted line-level replacements?
2. **Diff Minimization Standard:** When adding new functions, schemas, routes, or tests to existing files, should agents strictly localize edits to only the new/modified code without touching or reformatting unchanged surrounding lines?
3. **Diff Explanation:** How should agents summarize targeted file modifications in their pre/post descriptions so you can review diffs with minimal cognitive load?

**S:**  

