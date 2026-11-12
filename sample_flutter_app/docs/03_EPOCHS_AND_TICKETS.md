# Sample App Development Epochs & Tickets

This document defines the actionable engineering tickets for the **Sample Todo & Account Application**.

Tickets are organized into sequential **Epochs** reflecting the finalized architecture decisions:
- **ODM:** Beanie + Motor over MongoDB (local) / Amazon DocumentDB (AWS).
- **FHIR Alignment:** Hybrid incremental progression (simple Todo CRUD first, followed by FHIR `Task` concepts).
- **Machine Learning:** Dedicated, secure bulk data export endpoints (no embedded ML models).
- **Authentication:** Self-contained FastAPI JWT with explicit `**Devin re-Cognito:**` parity notes.
- **Flutter UI/UX:** Phased platform rollout (Browser -> Mobile -> Desktop) with explicit controls (no swipe gestures).
- **Deployment:** Local `docker-compose` first with AWS deployment blueprints.

---

## Epoch Overview

| Epoch | Title | Deliverables | Status |
| :--- | :--- | :--- | :--- |
| **Epoch 0** | Tooling, Scaffolding & TDD Baseline | FastAPI + Beanie setup, Flutter skeleton, Docker-Compose, pytest & flutter_test | Active Baseline |
| **Epoch 1** | Minimal Accounts & Simple Task Backend | Atomic User testing (Model & Security, Schemas, API Endpoints), user-scoped simple Task model, FastAPI CRUD routes | Active (Fast-Track per `[Q-SAMPLE-REORG-01]`) |
| **Epoch 2** | Flutter UI & FastAPI Synchronization | Flutter API client, Task List Screen with explicit checkboxes, task creation form, live backend sync | Active (Fast-Track per `[Q-SAMPLE-REORG-01]`) |
| **Epoch 3** | Authentication & Token Hardening | Password hashing verification, JWT access/refresh tokens, OAuth2 flows, secure storage, Cognito parity | Deferred per `[Q-SAMPLE-REORG-01]` |
| **Epoch 4** | Incremental FHIR Task Evolution | FHIR status state machine, `executionPeriod`, HL7 FHIR R4 Task JSON export serializer | Deferred per `[Q-SAMPLE-REORG-01]` |
| **Epoch 5** | Flutter UI/UX Polish — Browser (Web) | Material 3 search bar, filter chips (`All`, `Active`, `Completed`), explicit action buttons, responsive constraints | Deferred per `[Q-SAMPLE-REORG-01]` |
| **Epoch 6** | Machine Learning Bulk Data Export Layer | Authorized NDJSON/JSON export endpoints, query filters, task analytics | Preserved |
| **Epoch 7** | Multi-Platform Expansion & AWS Deployment | Mobile (Phase 2) & Desktop (Phase 3) verification, Docker & AWS App Runner / DocumentDB configs | Preserved |

---

## Epoch 0: Tooling, Scaffolding & TDD Baseline

### [SMP-EP0-TK01] FastAPI Backend Scaffolding & Pytest Setup
- **Summary:** Initialize the backend directory with `pyproject.toml`, FastAPI application factory, and configure `pytest` with `pytest-asyncio` and `pytest-cov`.
- **Referenced Questions:** `[Q-SAMPLE-ODM-01]` (Resolved: Beanie).
- **Tasks & Acceptance Criteria:**
  1. Define dependencies: `fastapi`, `uvicorn`, `beanie`, `motor`, `pydantic-settings`, `pytest`, `pytest-asyncio`, `pytest-cov`, `httpx`, `ruff`, `mypy`.
  2. Implement `tests/conftest.py` with an async test client fixture.
  3. Create health check endpoint `GET /api/v1/health` returning `{"status": "ok"}`.
- **TDD Test Spec:** `pytest tests/api/test_health.py` asserts 200 OK and valid JSON response.

---

### [SMP-EP0-TK02] Flutter Project Scaffolding & Testing Harness
- **Summary:** Initialize the Flutter client application and verify that `flutter test` executes cleanly.
- **Referenced Questions:** `[Q-SAMPLE-UI-01]` (Resolved: Browser-first).
- **Tasks & Acceptance Criteria:**
  1. Run `flutter create frontend --org com.sample.todo`.
  2. Add dependencies to `pubspec.yaml`: `flutter_riverpod` (or chosen state manager), `http` or `dio`, `flutter_secure_storage`, `mocktail` (dev).
  3. Write a smoke test in `test/widgets/smoke_test.dart`.
- **TDD Test Spec:** `flutter test` passes 100% of tests.

---

### [SMP-EP0-TK03] Local Docker-Compose Environment
- **Summary:** Create a `docker-compose.yml` to run MongoDB locally alongside the FastAPI backend for development.
- **Referenced Questions:** `[Q-SAMPLE-AWS-01]` (Resolved: Local Docker-compose first).
- **Tasks & Acceptance Criteria:**
  1. Create `docker-compose.yml` launching `mongo:7` on port 27017 and a volume for data persistence.
  2. Ensure the FastAPI backend connects to the local MongoDB instance via environment variable `DATABASE_URL`.
- **TDD Test Spec:** Backend successfully connects and initializes Beanie collections on startup.

---

## Epoch 1: Minimal Accounts & Simple Task Backend

*(Reorganized and streamlined per user decision `[Q-SAMPLE-REORG-01]` and testing standards in `AGENTS.md`. Decomposes the User subsystem into three distinct atomic testing tiers: Document Model & Security, Transport Schemas, and API Endpoints, followed by Simple Tasks).*

### [SMP-EP1-TK01] User Document Model & Security Unit Testing
*(Updated per `[Q-SAMPLE-REORG-01]` and atomic testing guidelines)*
- **Summary:** Implement and unit test the `User` Beanie document model with `name`, `email` (unique index), and bcrypt `password`, plus native bcrypt password hashing utilities.
- **Referenced Questions:** `[Q-SAMPLE-AUTH-01]`, `[Q-SAMPLE-REORG-01]` (Resolved: Simple bcrypt hash, minimal model).
- **Tasks & Acceptance Criteria:**
  1. Implement `User` Beanie document model in `src/models/user.py`:
     - `id`: Pydantic / Mongo ObjectId
     - `name`: String
     - `email`: Indexed(str, unique=True)
     - `password`: String (bcrypt hash)
     - `Settings`: collection name `"users"`
  2. Implement utility functions `hash_password()` and `verify_password()` in `src/core/security.py` using direct `bcrypt`.
  3. Provide layered test fixtures in `tests/conftest.py`: raw data list (`sample_users_raw_data`) and persisted instance (`persisted_user`).
  4. Write atomic unit tests in `tests/unit/test_user_model.py`:
     - Insertion assigns MongoDB ObjectId and increments count.
     - Document retrieval by ID and by unique email.
     - Querying non-existent ID or email returns `None`.
     - Inserting duplicate email raises `pymongo.errors.DuplicateKeyError` directly at the database layer.
     - Missing required fields (`name`, `email`, `password`) raise Pydantic `ValidationError`.
     - Document update (`.set()`) and deletion (`.delete()`).
  5. Write unit tests in `tests/unit/test_security.py` verifying bcrypt salting and password verification.
- **TDD Test Spec:** `pytest tests/unit/test_user_model.py tests/unit/test_security.py` passes 100%.

---

### [SMP-EP1-TK02] User Transport Schemas & Validation Unit Testing
*(Created per atomic testing guidelines in `AGENTS.md`)*
- **Summary:** Implement and unit test Pydantic transport DTO schemas (`UserCreate`, `UserOut`) ensuring input formatting constraints, email validation, and strict credential shielding in isolation from the database and HTTP transport.
- **Referenced Questions:** `[Q-SAMPLE-REORG-01]`.
- **Tasks & Acceptance Criteria:**
  1. Implement `UserCreate(BaseModel)` in `src/schemas/user.py`:
     - `name`: String (min length 1)
     - `email`: `EmailStr` (validates standard email formatting)
     - `password`: String (min length 4)
  2. Implement `UserOut(BaseModel)` in `src/schemas/user.py`:
     - `id`: String (hex identifier)
     - `name`: String
     - `email`: String
     - `model_config = ConfigDict(from_attributes=True)`
     - Strictly omits `password` and `hashed_password` to prevent credential exposure.
  3. Write isolated unit tests in `tests/unit/test_user_schemas.py`:
     - Valid payload successfully parses into `UserCreate`.
     - Invalid email formats (e.g. `"not-an-email"`, `"missing@domain"`) raise `pydantic.ValidationError`.
     - Empty string `name` or short `password` raises `pydantic.ValidationError`.
     - `UserOut` maps from attributes (`from_attributes=True`).
     - Assert that neither `password` nor `hashed_password` exists in `UserOut.model_fields` or `.model_dump()`.
- **TDD Test Spec:** `pytest tests/unit/test_user_schemas.py` passes 100%.

---

### [SMP-EP1-TK03] User API Endpoints & Route Wire-up Integration
*(Created per atomic testing guidelines in `AGENTS.md`)*
- **Summary:** Build and integration-test the FastAPI user endpoints, wire them into `create_app()`, and verify HTTP status codes and error mappings.
- **Referenced Questions:** `[Q-SAMPLE-AUTH-01]`, `[Q-SAMPLE-REORG-01]`.
- **Tasks & Acceptance Criteria:**
  1. Implement `src/api/users.py` router:
     - `POST /api/v1/users`: Validates payload, checks if email is registered (raises `HTTPException(400, "Email already registered")`), hashes password, saves user, returns 201 Created with `UserOut`.
     - `GET /api/v1/users`: Returns list of existing users as `list[UserOut]` for the active-user switcher.
     - `GET /api/v1/users/{id}`: Returns user by ID, or raises 404 Not Found.
  2. Register `users_router` on `create_app()` in `src/main.py`.
  3. Write HTTP integration tests in `tests/api/test_users.py`:
     - `POST /api/v1/users`: Returns 201 Created with valid `UserOut`, verifies password is never returned in response, and verifies password in DB is bcrypt-hashed.
     - Duplicate email registration returns clean HTTP 400 Bad Request with `"Email already registered"`.
     - Malformed input payload returns HTTP 422 Unprocessable Entity.
     - `GET /api/v1/users`: Returns list of registered users.
     - `GET /api/v1/users/{id}`: Returns 200 for valid ID and 404 for unknown/malformed ID.
- **TDD Test Spec:** `pytest tests/api/test_users.py` passes 100%.
- **Devin re-Cognito:** In AWS Cognito, user creation is performed via the Cognito IDP API (`SignUp` or `AdminCreateUser`). Your FastAPI backend does not need user creation endpoints or password hashing routines; instead, Flutter calls Cognito directly, and FastAPI acts as a Resource Server validating incoming Cognito JWT bearer tokens.

---

### [SMP-EP1-TK04] User-Scoped Simple Task Model & CRUD Endpoints
*(Renumbered from former TK02 per user decision `[Q-SAMPLE-REORG-01]`)*
- **Summary:** Implement a lightweight, user-scoped Task document model with `name`, completion status, and metadata, backed by complete FastAPI CRUD routes.
- **Referenced Questions:** `[Q-SAMPLE-REORG-01]` (Resolved: Scoped to user, simple fields: name, is_completed, metadata).
- **Tasks & Acceptance Criteria:**
  1. Implement `Task` Beanie document model with fields:
     - `id`: Pydantic / Mongo ObjectId
     - `user_id`: String / ObjectId (foreign key linking task to user)
     - `name`: String (title/name of the task)
     - `is_completed`: Boolean (default: `False`)
     - `metadata`: Dict[str, Any] (JSON object for flexible attributes, default: `{}`)
  2. Create REST API endpoints:
     - `POST /api/v1/tasks`: Creates a task scoped to `user_id` (returns 201 Created).
     - `GET /api/v1/tasks`: Lists tasks (supports query parameter `?user_id={id}` to filter by user).
     - `GET /api/v1/tasks/{id}`: Returns single task by ID.
     - `PATCH /api/v1/tasks/{id}`: Updates task fields (e.g., toggle `is_completed`, update `metadata`).
     - `DELETE /api/v1/tasks/{id}`: Deletes task by ID (returns 204 No Content).
  3. Write tests verifying task creation, user filtering, completion toggling, and deletion.
- **TDD Test Spec:** `pytest tests/api/test_tasks.py` verifies full CRUD cycle and user-scoping.

---

### ~~[SMP-EP1-TK02-ORIG] FastAPI Authentication & Token Endpoints~~
*Superseded & Deferred to `[SMP-EP3-TK01-AUTH]` per user decision in `[Q-SAMPLE-REORG-01]`: Full OAuth2 password flow and JWT token generation deferred to allow immediate Flutter sync.*
~~- **Summary:** Build endpoints for user registration, login (OAuth2 password flow), and current user info.~~
~~- **Tasks & Acceptance Criteria:**~~
~~  1. Write tests for: `POST /api/v1/auth/register`, `POST /api/v1/auth/token`, `GET /api/v1/auth/me`.~~
~~  2. Return 401 Unauthorized for invalid credentials or missing tokens.~~

---

### ~~[SMP-EP1-TK03-ORIG] Flutter Authentication Service & Secure Storage~~
*Superseded & Deferred to `[SMP-EP3-TK02-AUTH]` per user decision in `[Q-SAMPLE-REORG-01]`: Token storage deferred until token machinery is implemented in Epoch 3.*
~~- **Summary:** Implement Flutter client service for auth HTTP calls and token persistence via `flutter_secure_storage`.~~

---

### ~~[SMP-EP1-TK04-ORIG] Flutter Login & Registration Screens (Browser-First)~~
*Superseded & Deferred to `[SMP-EP3-TK03-AUTH]` per user decision in `[Q-SAMPLE-REORG-01]`: Replaced in early stage by simple User Selection and direct Task List Screen in Epoch 2.*
~~- **Summary:** Build the user interface for Login and Registration with form validation and widget tests, verified in Flutter Web.~~

---

## Epoch 2: Flutter UI & FastAPI Synchronization (The Immediate Priority)

*(Reorganized per `[Q-SAMPLE-REORG-01]`: Fast-tracks building the Flutter frontend and establishing live HTTP synchronization with the FastAPI backend).*

### [SMP-EP2-TK01] Flutter API Client & Data Models
- **Summary:** Implement Dart models (`User`, `Task`) and an HTTP service client connecting to the running FastAPI backend.
- **Referenced Questions:** `[Q-SAMPLE-REORG-01]`, `[Q-SAMPLE-UI-01]`.
- **Tasks & Acceptance Criteria:**
  1. Define Dart models:
     - `User`: `id`, `name`, `email` with `fromJson` and `toJson`.
     - `Task`: `id`, `userId`, `name`, `isCompleted`, `metadata` (Map<String, dynamic>) with `fromJson` and `toJson`.
  2. Implement `ApiClient` using the `http` package:
     - `fetchUsers()` -> `GET /api/v1/users`
     - `createUser(name, email, password)` -> `POST /api/v1/users`
     - `fetchTasks({String? userId})` -> `GET /api/v1/tasks?user_id=...`
     - `createTask(userId, name, metadata)` -> `POST /api/v1/tasks`
     - `updateTaskStatus(taskId, isCompleted)` -> `PATCH /api/v1/tasks/{id}`
     - `deleteTask(taskId)` -> `DELETE /api/v1/tasks/{id}`
  3. Write unit tests with `mocktail` asserting JSON parsing and HTTP response handling.
- **TDD Test Spec:** `flutter test test/unit/api_client_test.dart` passes 100%.

---

### [SMP-EP2-TK02] Flutter User Selection & Task List Screen
- **Summary:** Build the primary Flutter UI screen displaying user-scoped tasks with interactive checkboxes that sync completion status to FastAPI.
- **Referenced Questions:** `[Q-SAMPLE-REORG-01]`, `[Q-SAMPLE-UI-01]` (Resolved: Explicit checkboxes, no swipe gestures).
- **Tasks & Acceptance Criteria:**
  1. Header/Toolbar: User selector dropdown or switcher (loads users from backend, selects active user).
  2. Task List: Scrollable list of `TaskCard` widgets for the active user:
     - Displays task `name` and status.
     - Explicit checkbox: Tapping checkbox calls `apiClient.updateTaskStatus(...)` and toggles completion state.
     - Completed tasks display with struck-through title and muted text.
     - Delete icon: Tapping prompts confirmation dialog and calls `apiClient.deleteTask(...)`.
  3. Empty state: Displays helpful message when the selected user has no tasks.
  4. Write widget tests with `mocktail` verifying task list rendering, checkbox toggle API call, and delete dialog.
- **TDD Test Spec:** `flutter test test/widgets/task_list_screen_test.dart` passes 100%.

---

### [SMP-EP2-TK03] Task Creation & Metadata Form
- **Summary:** Create an ergonomic form dialog to add new tasks with name and metadata for the active user.
- **Referenced Questions:** `[Q-SAMPLE-REORG-01]`, `[Q-SAMPLE-UI-01]`.
- **Tasks & Acceptance Criteria:**
  1. Floating Action Button (FAB) opens a modal dialog or bottom sheet.
  2. Form fields:
     - `name`: Required text input (auto-focused).
     - `metadata`: Optional key-value inputs or tags.
  3. Submitting sends `POST /api/v1/tasks` and refreshes the task list on success.
  4. Write widget tests verifying input validation (empty name disabled) and submission.
- **TDD Test Spec:** `flutter test test/widgets/create_task_dialog_test.dart` passes 100%.

---

### ~~[SMP-EP2-TK01-ORIG] Simple Todo Document Schema & Model~~
*Merged into `[SMP-EP1-TK02]` per user decision in `[Q-SAMPLE-REORG-01]`.*
~~- **Summary:** Implement a clean, lightweight Todo schema to enable rapid CRUD development and immediate testing.~~

---

### ~~[SMP-EP2-TK02-ORIG] Todo Service Layer & CRUD Repository~~
*Merged into `[SMP-EP1-TK02]` per user decision in `[Q-SAMPLE-REORG-01]`.*
~~- **Summary:** Implement application service managing Todo creation, filtering, updating, and strict user data scoping.~~

---

### ~~[SMP-EP2-TK03-ORIG] Todo REST API Endpoints~~
*Merged into `[SMP-EP1-TK02]` per user decision in `[Q-SAMPLE-REORG-01]`.*
~~- **Summary:** Build the authenticated REST routes for Todo management.~~

---

## Epoch 3: Authentication & Token Hardening (Deferred)

*(Deferred per user decision `[Q-SAMPLE-REORG-01]` — incorporates former Epoch 1 auth tickets)*

### [SMP-EP3-TK01-AUTH] FastAPI Authentication & Token Endpoints
- **Summary:** Build endpoints for user login (OAuth2 password flow), JWT token generation, and current user info.
- **Referenced Questions:** `[Q-SAMPLE-AUTH-01]`, `[Q-SAMPLE-REORG-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write tests for:
     - `POST /api/v1/auth/token` (returns JWT access and refresh tokens).
     - `GET /api/v1/auth/me` (returns current user profile given Bearer token).
  2. Return 401 Unauthorized for invalid credentials or missing tokens.
- **TDD Test Spec:** API tests verify successful token retrieval and token validation.
- **Devin re-Cognito:** With Cognito, login is performed via the Cognito IDP API (`InitiateAuth`) or Hosted UI, returning standard OIDC tokens. FastAPI simply acts as a Resource Server validating JWT signatures against AWS's public JWKS endpoint.

---

### [SMP-EP3-TK02-AUTH] Flutter Authentication Service & Secure Storage
- **Summary:** Implement Flutter client service for auth HTTP calls and token persistence via `flutter_secure_storage`.
- **Referenced Questions:** `[Q-SAMPLE-AUTH-01]`, `[Q-SAMPLE-UI-01]`, `[Q-SAMPLE-REORG-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write unit tests mocking HTTP responses for login.
  2. Implement `AuthService` storing access and refresh tokens securely (`Keychain` on iOS/macOS, `KeyStore` on Android, `LocalStorage` on Web).
  3. Ensure logout clears tokens from secure storage.
- **TDD Test Spec:** Unit tests verify tokens are retrieved, saved, and deleted from secure storage mock.
- **Devin re-Cognito:** In Flutter with AWS, the AWS Amplify Flutter SDK handles session tokens, automatic refresh, and MFA out of the box.

---

### [SMP-EP3-TK03-AUTH] Flutter Login & Registration Screens (Browser-First)
- **Summary:** Build the user interface for Login and Registration with form validation and widget tests, verified in Flutter Web.
- **Referenced Questions:** `[Q-SAMPLE-UI-01]`, `[Q-SAMPLE-REORG-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write widget tests (`testWidgets`): test email and password inputs, validation error on short password, submit button click.
  2. Implement responsive Material 3 LoginScreen and RegisterScreen suitable for browser windows.
  3. Display loading spinner while authenticating and error snackbar on failure.
- **TDD Test Spec:** Widget tests verify all UI states (validation failure, loading state, successful navigation).

---

## Epoch 4: Incremental FHIR Task Evolution (Deferred)

### [SMP-EP4-TK01] FHIR Task State Machine & Schema Expansion
*(Former `[SMP-EP3-TK01]` — deferred per `[Q-SAMPLE-REORG-01]`)*
- **Summary:** Incrementally evolve the internal Todo model to adopt HL7 FHIR `Task` concepts and lifecycle states.
- **Referenced Questions:** `[Q-SAMPLE-FHIR-01]`, `[Q-SAMPLE-REORG-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write tests for FHIR Task status state transitions:
     - `draft` -> `requested` -> `in-progress` -> `completed` / `cancelled` / `failed`
  2. Add FHIR-aligned fields to document:
     - `intent`: Enum (`order`, `plan`, `proposal`)
     - `priority`: Enum (`routine`, `urgent`, `asap`, `stat`)
     - `execution_period`: Nested object with `start` and `end`
     - `note`: Rich clinical annotations list
- **TDD Test Spec:** Tests assert invalid status transitions raise a 400 validation error.

---

### [SMP-EP4-TK02] FHIR R4 Task JSON Export Serializer
*(Former `[SMP-EP3-TK02]` — deferred per `[Q-SAMPLE-REORG-01]`)*
- **Summary:** Build an export serializer that converts internal task documents into official HL7 FHIR R4 `Task` JSON resources.
- **Referenced Questions:** `[Q-SAMPLE-FHIR-01]`, `[Q-SAMPLE-REORG-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write unit tests validating exported JSON against the official HL7 FHIR R4 Task schema.
  2. Correctly structure `resourceType: "Task"`, `for: {"reference": "User/..."}`, `authoredOn`, and `executionPeriod`.
  3. Add endpoint `GET /api/v1/todos/{id}/fhir` returning `application/fhir+json`.
- **TDD Test Spec:** Pytest validates exported JSON structure against HL7 FHIR R4 specification.

---

## Epoch 5: Flutter UI/UX Polish — Browser (Web)

*(Former Epoch 4 — advanced UI controls deferred per `[Q-SAMPLE-REORG-01]` after basic sync is established in Epoch 2)*

### [SMP-EP5-TK01] Todo State Management Architecture (Riverpod/BLoC)
- **Summary:** Implement structured client-side state management (Riverpod/BLoC) handling task list loading, filtering, and error handling for Flutter Web.
- **Referenced Questions:** `[Q-SAMPLE-UI-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write unit tests for the TodoNotifier/Cubit simulating initial fetch, filter change, and task addition.
  2. Implement optimistic update logic: immediately reflect toggled checkbox in UI; revert if server returns error.
- **TDD Test Spec:** Unit tests assert state transitions: `Loading -> Success([todos]) -> Error(message)`.

---

### [SMP-EP5-TK02] Todo List Screen with Filter Chips & Search (Browser-First)
- **Summary:** Build the main dashboard screen featuring Material 3 search bar, filter chips (`All`, `Active`, `Completed`, `Urgent`), and responsive desktop/browser layout.
- **Referenced Questions:** `[Q-SAMPLE-UI-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write widget tests asserting filter chip taps filter the displayed task cards.
  2. Render empty state illustration when list is empty.
  3. Ensure layout adapts smoothly to wide browser screens (max content width constraint).
- **TDD Test Spec:** Widget test asserts tapping "Completed" chip hides active tasks.

---

### ~~[SMP-EP5-TK03-ORIG] Dismissible Task Card Widget with Swipe Gestures~~
*Superseded based on user decision in `[Q-SAMPLE-UI-01]`: Swipe gestures rejected in favor of explicit controls.*
~~- **Summary:** Create interactive task card widget with swipe-to-delete (left) and swipe-to-complete (right) gestures.~~

---

### [SMP-EP5-TK03] Explicit Task Card Widget (No Swipe Gestures)
*(Active replacement per `[Q-SAMPLE-UI-01]`)*
- **Summary:** Create a clean task card widget using explicit controls: a checkbox for completion, an edit button, and a delete button with confirmation dialog.
- **Referenced Questions:** `[Q-SAMPLE-UI-01]` (Resolved: No swipe gestures).
- **Tasks & Acceptance Criteria:**
  1. Write widget tests for:
     - Tapping checkbox calls `onToggleComplete`.
     - Tapping delete icon opens `AlertDialog` with "Cancel" and "Delete" actions.
     - Confirming delete invokes `onDelete`.
  2. Visual styling: completed tasks display strike-through title and muted text color.
- **TDD Test Spec:** `testWidgets` verifies tapping checkbox marks item complete and delete dialog functions correctly.

---

### [SMP-EP5-TK04] Modal Bottom Sheet / Dialog for Task Creation
- **Summary:** Develop an ergonomic creation form opened via Floating Action Button (FAB).
- **Referenced Questions:** `[Q-SAMPLE-UI-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write widget tests for text field input, priority chip selection (`Routine`, `Urgent`), and save button.
  2. Auto-focus text input; submit on Enter key in browser.
  3. Validate that blank titles cannot be submitted.
- **TDD Test Spec:** Widget test verifies button remains disabled when input is empty and adds task on submit.

---

## Epoch 6: Machine Learning Bulk Data Export Layer

### ~~[SMP-EP6-TK01-ORIG] ML Task Priority Inference Service~~
*Superseded based on user decision in `[Q-SAMPLE-ML-01]`: Do not build ML models into the app.*
~~- **Summary:** Build a lightweight NLP inference service suggesting task priority and tags based on the task description.~~

---

### ~~[SMP-EP6-TK02-ORIG] Flutter Smart Priority Suggestion Integration~~
*Superseded based on user decision in `[Q-SAMPLE-ML-01]`: No embedded ML suggestions in UI.*
~~- **Summary:** Integrate the ML priority prediction endpoint into the Flutter task creation sheet with 400ms debounce.~~

---

### [SMP-EP6-TK01] Authorized ML Bulk Data Export Endpoint
*(Active replacement per `[Q-SAMPLE-ML-01]`)*
- **Summary:** Build dedicated, secured endpoints for external ML platforms to extract structured task data for training.
- **Referenced Questions:** `[Q-SAMPLE-ML-01]` (Resolved: Clean ML export only).
- **Tasks & Acceptance Criteria:**
  1. Implement `GET /api/v1/ml/export/tasks` supporting query parameters: `from_date`, `to_date`, `format=json|ndjson`.
  2. Implement separate authorization: endpoint requires an ML service API key or admin token (`X-ML-Service-Key`).
  3. Return clean tabular/vectorizable records: `task_id`, `title_length`, `description_length`, `priority`, `status`, `time_to_completion_seconds`.
  4. Ensure user identifiers are cryptographically pseudonymized (anonymized hash) to prevent data leakage.
- **TDD Test Spec:** Integration tests verify format output (JSON & NDJSON), verify 401 on missing API key, and confirm zero raw user PII.

---

### [SMP-EP6-TK02] Task Metrics & Aggregation Endpoint
*(Active replacement per `[Q-SAMPLE-ML-01]`)*
- **Summary:** Expose summary statistics for task velocity and completion patterns.
- **Referenced Questions:** `[Q-SAMPLE-ML-01]`.
- **Tasks & Acceptance Criteria:**
  1. Implement `GET /api/v1/ml/analytics/summary` returning: `total_tasks`, `completed_count`, `active_count`, `completion_rate`, `average_completion_hours`.
  2. Write tests asserting correct aggregation calculations against test fixtures.
- **TDD Test Spec:** Test asserts exact counts and average calculations across varied completed/pending tasks.

---

## Epoch 7: Multi-Platform Expansion & AWS Deployment

### [SMP-EP7-TK01] Multi-Platform Verification — Phase 2: Mobile & Phase 3: Desktop
- **Summary:** Verify and adapt the Flutter client for Mobile (Android/iOS) and native Windows Desktop.
- **Referenced Questions:** `[Q-SAMPLE-UI-01]`.
- **Tasks & Acceptance Criteria:**
  1. **Phase 2 (Mobile):** Verify touch targets (minimum 48x48dp), mobile soft keyboard avoidance, and hardware back button behavior.
  2. **Phase 3 (Desktop):** Verify native Windows build (`flutter run -d windows`), title bar rendering, and keyboard shortcuts (`Ctrl+N` for new task).
- **TDD Test Spec:** Widget tests verify responsive layout across mobile and desktop viewport dimensions.

---

### [SMP-EP7-TK02] Full Backend E2E Test Suite
- **Summary:** Automated integration test suite running full user workflows against a real test MongoDB database.
- **Referenced Questions:** `[Q-SAMPLE-ODM-01]`.
- **Tasks & Acceptance Criteria:**
  1. Workflow: Register user -> Login -> Create Tasks -> Transition FHIR states -> Export ML Dataset -> Fetch Analytics.
  2. Execute with zero mocks on domain and data persistence layers.
- **TDD Test Spec:** Pytest suite passes 100% with no unhandled exceptions.

---

### [SMP-EP7-TK03] AWS Deployment Blueprint (App Runner + DocumentDB + S3)
- **Summary:** Create Dockerfiles and AWS deployment guides for cloud production.
- **Referenced Questions:** `[Q-SAMPLE-AWS-01]` (Resolved: Local Docker first, AWS ready).
- **Tasks & Acceptance Criteria:**
  1. Multi-stage `backend/Dockerfile` optimizing image size for AWS App Runner / ECS Fargate.
  2. Build and export Flutter Web bundle (`flutter build web`) for deployment to Amazon S3 + CloudFront CDN.
  3. Document DocumentDB connection string configuration and VPC peering setup in AWS.
- **TDD Test Spec:** Docker build succeeds and container passes health check.
