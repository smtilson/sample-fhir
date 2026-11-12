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

| Epoch | Title | Deliverables |
| :--- | :--- | :--- |
| **Epoch 0** | Tooling, Scaffolding & TDD Baseline | FastAPI + Beanie setup, Flutter skeleton, Docker-Compose, pytest & flutter_test |
| **Epoch 1** | Accounts & Authentication Flow | User registration, password hashing, JWT tokens, Flutter login/register UI, Cognito parity notes |
| **Epoch 2** | Core Todo Domain & Persistence (Stage 1) | Simple Todo schema, Beanie models, CRUD service layer, unit & API tests |
| **Epoch 3** | Incremental FHIR Task Evolution (Stage 2) | FHIR status state machine, `executionPeriod`, HL7 FHIR R4 Task JSON export serializer |
| **Epoch 4** | Flutter UI/UX — Phase 1: Browser (Web) | Material 3 dashboard, explicit checkboxes & confirm dialogs (no swipes), filter chips |
| **Epoch 5** | Machine Learning Bulk Data Export Layer | Authorized NDJSON/JSON export endpoints, query filters, task analytics |
| **Epoch 6** | Multi-Platform Expansion & AWS Deployment | Mobile (Phase 2) & Desktop (Phase 3) verification, Docker & AWS App Runner / DocumentDB configs |

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

## Epoch 1: Accounts & Authentication Flow

### [SMP-EP1-TK01] User Document Model & Credential Security
- **Summary:** Implement the `User` Beanie document model with encrypted password hashing using bcrypt.
- **Referenced Questions:** `[Q-SAMPLE-AUTH-01]` (Resolved: Self-contained JWT).
- **Tasks & Acceptance Criteria:**
  1. Write failing unit test verifying password cannot be saved in plaintext.
  2. Implement `User` model with fields: `id`, `email`, `hashed_password`, `full_name`, `is_active`, `created_at`.
  3. Implement utility functions `hash_password()` and `verify_password()`.
- **TDD Test Spec:** `test_password_hashing()` verifies bcrypt salt generation and verification matching.
- **Devin re-Cognito:** In AWS Cognito, you do not manage a `User` database document or password hashes yourself. Cognito User Pools store credentials and handle bcrypt/Argon2 hashing securely behind AWS-managed KMS encryption. The application only stores the Cognito `sub` (User UUID) as a foreign key on tasks.

---

### [SMP-EP1-TK02] FastAPI Authentication & Token Endpoints
- **Summary:** Build endpoints for user registration, login (OAuth2 password flow), and current user info.
- **Referenced Questions:** `[Q-SAMPLE-AUTH-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write tests for:
     - `POST /api/v1/auth/register` (creates user, fails on duplicate email).
     - `POST /api/v1/auth/token` (returns JWT access and refresh tokens).
     - `GET /api/v1/auth/me` (returns current user profile given Bearer token).
  2. Return 401 Unauthorized for invalid credentials or missing tokens.
- **TDD Test Spec:** API tests verify registration, successful token retrieval, and token validation.
- **Devin re-Cognito:** With Cognito, login and registration are performed via the Cognito IDP API (`InitiateAuth`, `SignUp`) or the Cognito Hosted UI. Cognito issues standard OIDC tokens (ID token, Access token, Refresh token). The FastAPI backend doesn't issue tokens; it simply acts as a Resource Server validating incoming Cognito JWT signatures against AWS's public JWKS endpoint (`https://cognito-idp.<region>.amazonaws.com/<userPoolId>/.well-known/jwks.json`).

---

### [SMP-EP1-TK03] Flutter Authentication Service & Secure Storage
- **Summary:** Implement Flutter client service for auth HTTP calls and token persistence via `flutter_secure_storage`.
- **Referenced Questions:** `[Q-SAMPLE-AUTH-01]`, `[Q-SAMPLE-UI-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write unit tests mocking HTTP responses for login and register.
  2. Implement `AuthService` storing access and refresh tokens securely (Keychain on iOS/macOS, KeyStore on Android, LocalStorage on Web).
  3. Ensure logout clears tokens from secure storage.
- **TDD Test Spec:** Unit tests verify tokens are retrieved, saved, and deleted from secure storage mock.
- **Devin re-Cognito:** In Flutter with AWS, you can use the official `amplify_flutter` or `amazon_cognito_identity_dart_2` package. Instead of storing raw tokens manually, the SDK handles token refresh, session caching, and multi-factor authentication (MFA) automatically.

---

### [SMP-EP1-TK04] Flutter Login & Registration Screens (Browser-First)
- **Summary:** Build the user interface for Login and Registration with form validation and widget tests, verified in Flutter Web.
- **Referenced Questions:** `[Q-SAMPLE-UI-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write widget tests (`testWidgets`): test email and password inputs, validation error on short password, submit button click.
  2. Implement responsive Material 3 LoginScreen and RegisterScreen suitable for browser windows.
  3. Display loading spinner while authenticating and error snackbar on failure.
- **TDD Test Spec:** Widget tests verify all UI states (validation failure, loading state, successful navigation).

---

## Epoch 2: Core Todo Domain & Persistence (Stage 1)

### [SMP-EP2-TK01] Simple Todo Document Schema & Model
- **Summary:** Implement a clean, lightweight Todo schema to enable rapid CRUD development and immediate testing.
- **Referenced Questions:** `[Q-SAMPLE-FHIR-01]` (Resolved: Hybrid incremental approach).
- **Tasks & Acceptance Criteria:**
  1. Write unit tests validating task creation with default values (`is_completed: false`, `priority: routine`).
  2. Implement `TodoDocument(beanie.Document)` with fields:
     - `id`: Pydantic / Mongo ObjectId
     - `user_id`: Reference to user
     - `title`: String
     - `description`: Optional String
     - `is_completed`: Boolean
     - `priority`: Enum (`routine`, `urgent`)
     - `due_date`: Optional datetime
     - `created_at`, `updated_at`, `completed_at`
- **TDD Test Spec:** Schema tests verify model validation and serialization to/from JSON.

---

### [SMP-EP2-TK02] Todo Service Layer & CRUD Repository
- **Summary:** Implement application service managing Todo creation, filtering, updating, and strict user data scoping.
- **Referenced Questions:** `[Q-SAMPLE-ODM-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write tests ensuring users cannot read or mutate other users' todos.
  2. Implement methods: `create_todo()`, `get_todos(user_id, is_completed, priority)`, `toggle_completion()`, `delete_todo()`.
  3. Automatically record `completed_at` when `is_completed` becomes `True`.
- **TDD Test Spec:** Unit tests verify strict user scoping and timestamp tracking.

---

### [SMP-EP2-TK03] Todo REST API Endpoints
- **Summary:** Build the authenticated REST routes for Todo management.
- **Referenced Questions:** `[Q-SAMPLE-ODM-01]`.
- **Tasks & Acceptance Criteria:**
  1. Implement endpoints:
     - `GET /api/v1/todos` (with query filters: `is_completed`, `priority`, `search`)
     - `POST /api/v1/todos` (creates todo, returns 201 Created)
     - `GET /api/v1/todos/{id}` (returns todo details)
     - `PATCH /api/v1/todos/{id}` (updates fields or toggles completion)
     - `DELETE /api/v1/todos/{id}` (deletes todo, returns 204 No Content)
  2. Write integration tests for all status codes (200, 201, 204, 400, 404).
- **TDD Test Spec:** API tests verify complete CRUD workflow for authenticated users.

---

## Epoch 3: Incremental FHIR Task Evolution (Stage 2)

### [SMP-EP3-TK01] FHIR Task State Machine & Schema Expansion
- **Summary:** Incrementally evolve the internal Todo model to adopt HL7 FHIR `Task` concepts and lifecycle states.
- **Referenced Questions:** `[Q-SAMPLE-FHIR-01]`.
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

### [SMP-EP3-TK02] FHIR R4 Task JSON Export Serializer
- **Summary:** Build an export serializer that converts internal task documents into official HL7 FHIR R4 `Task` JSON resources.
- **Referenced Questions:** `[Q-SAMPLE-FHIR-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write unit tests validating exported JSON against the official HL7 FHIR R4 Task schema.
  2. Correctly structure `resourceType: "Task"`, `for: {"reference": "User/..."}`, `authoredOn`, and `executionPeriod`.
  3. Add endpoint `GET /api/v1/todos/{id}/fhir` returning `application/fhir+json`.
- **TDD Test Spec:** Pytest validates exported JSON structure against HL7 FHIR R4 specification.

---

## Epoch 4: Flutter UI/UX — Phase 1: Browser (Web)

### [SMP-EP4-TK01] Todo State Management Architecture
- **Summary:** Implement client-side state management (Riverpod/BLoC) handling task list loading, filtering, and error handling for Flutter Web.
- **Referenced Questions:** `[Q-SAMPLE-UI-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write unit tests for the TodoNotifier/Cubit simulating initial fetch, filter change, and task addition.
  2. Implement optimistic update logic: immediately reflect toggled checkbox in UI; revert if server returns error.
- **TDD Test Spec:** Unit tests assert state transitions: `Loading -> Success([todos]) -> Error(message)`.

---

### [SMP-EP4-TK02] Todo List Screen with Filter Chips & Search (Browser-First)
- **Summary:** Build the main dashboard screen featuring Material 3 search bar, filter chips (`All`, `Active`, `Completed`, `Urgent`), and responsive desktop/browser layout.
- **Referenced Questions:** `[Q-SAMPLE-UI-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write widget tests asserting filter chip taps filter the displayed task cards.
  2. Render empty state illustration when list is empty.
  3. Ensure layout adapts smoothly to wide browser screens (max content width constraint).
- **TDD Test Spec:** Widget test asserts tapping "Completed" chip hides active tasks.

---

### ~~[SMP-EP4-TK03-ORIG] Dismissible Task Card Widget with Swipe Gestures~~
*Superseded based on user decision in `[Q-SAMPLE-UI-01]`: Swipe gestures rejected in favor of explicit controls.*
~~- **Summary:** Create interactive task card widget with swipe-to-delete (left) and swipe-to-complete (right) gestures.~~
~~- **Tasks & Acceptance Criteria:**~~
~~  1. Simulate drag gestures left and right on `Dismissible`.~~
~~  2. Swiping right toggles completion and plays a brief check animation.~~
~~  3. Swiping left shows red delete background with trash icon, removes item, and shows SnackBar with "Undo" button.~~

### [SMP-EP4-TK03] Explicit Task Card Widget (No Swipe Gestures)
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

### [SMP-EP4-TK04] Modal Bottom Sheet / Dialog for Task Creation
- **Summary:** Develop an ergonomic creation form opened via Floating Action Button (FAB).
- **Referenced Questions:** `[Q-SAMPLE-UI-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write widget tests for text field input, priority chip selection (`Routine`, `Urgent`), and save button.
  2. Auto-focus text input; submit on Enter key in browser.
  3. Validate that blank titles cannot be submitted.
- **TDD Test Spec:** Widget test verifies button remains disabled when input is empty and adds task on submit.

---

## Epoch 5: Machine Learning Bulk Data Export Layer

### ~~[SMP-EP5-TK01-ORIG] ML Task Priority Inference Service~~
*Superseded based on user decision in `[Q-SAMPLE-ML-01]`: Do not build ML models into the app.*
~~- **Summary:** Build a lightweight NLP inference service suggesting task priority and tags based on the task description.~~
~~- **Tasks & Acceptance Criteria:**~~
~~  1. Implement inference module using scikit-learn pipeline.~~
~~  2. Create endpoint `POST /api/v1/ml/predict-priority` returning predicted priority and confidence.~~

### ~~[SMP-EP5-TK02-ORIG] Flutter Smart Priority Suggestion Integration~~
*Superseded based on user decision in `[Q-SAMPLE-ML-01]`: No embedded ML suggestions in UI.*
~~- **Summary:** Integrate the ML priority prediction endpoint into the Flutter task creation sheet with 400ms debounce.~~

---

### [SMP-EP5-TK01] Authorized ML Bulk Data Export Endpoint
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

### [SMP-EP5-TK02] Task Metrics & Aggregation Endpoint
*(Active replacement per `[Q-SAMPLE-ML-01]`)*
- **Summary:** Expose summary statistics for task velocity and completion patterns.
- **Referenced Questions:** `[Q-SAMPLE-ML-01]`.
- **Tasks & Acceptance Criteria:**
  1. Implement `GET /api/v1/ml/analytics/summary` returning: `total_tasks`, `completed_count`, `active_count`, `completion_rate`, `average_completion_hours`.
  2. Write tests asserting correct aggregation calculations against test fixtures.
- **TDD Test Spec:** Test asserts exact counts and average calculations across varied completed/pending tasks.

---

## Epoch 6: Multi-Platform Expansion & AWS Deployment

### [SMP-EP6-TK01] Multi-Platform Verification — Phase 2: Mobile & Phase 3: Desktop
- **Summary:** Verify and adapt the Flutter client for Mobile (Android/iOS) and native Windows Desktop.
- **Referenced Questions:** `[Q-SAMPLE-UI-01]`.
- **Tasks & Acceptance Criteria:**
  1. **Phase 2 (Mobile):** Verify touch targets (minimum 48x48dp), mobile soft keyboard avoidance, and hardware back button behavior.
  2. **Phase 3 (Desktop):** Verify native Windows build (`flutter run -d windows`), title bar rendering, and keyboard shortcuts (`Ctrl+N` for new task).
- **TDD Test Spec:** Widget tests verify responsive layout across mobile and desktop viewport dimensions.

---

### [SMP-EP6-TK02] Full Backend E2E Test Suite
- **Summary:** Automated integration test suite running full user workflows against a real test MongoDB database.
- **Referenced Questions:** `[Q-SAMPLE-ODM-01]`.
- **Tasks & Acceptance Criteria:**
  1. Workflow: Register user -> Login -> Create Tasks -> Transition FHIR states -> Export ML Dataset -> Fetch Analytics.
  2. Execute with zero mocks on domain and data persistence layers.
- **TDD Test Spec:** Pytest suite passes 100% with no unhandled exceptions.

---

### [SMP-EP6-TK03] AWS Deployment Blueprint (App Runner + DocumentDB + S3)
- **Summary:** Create Dockerfiles and AWS deployment guides for cloud production.
- **Referenced Questions:** `[Q-SAMPLE-AWS-01]` (Resolved: Local Docker first, AWS ready).
- **Tasks & Acceptance Criteria:**
  1. Multi-stage `backend/Dockerfile` optimizing image size for AWS App Runner / ECS Fargate.
  2. Build and export Flutter Web bundle (`flutter build web`) for deployment to Amazon S3 + CloudFront CDN.
  3. Document DocumentDB connection string configuration and VPC peering setup in AWS.
- **TDD Test Spec:** Docker build succeeds and container passes health check.
