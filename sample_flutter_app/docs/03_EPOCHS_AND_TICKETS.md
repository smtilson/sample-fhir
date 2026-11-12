# Sample App Development Epochs & Tickets

This document defines the actionable engineering tickets for the **Sample Todo & Account Application**.

Tickets are organized into sequential **Epochs**. Any ticket that depends on an architectural choice references the corresponding question from `sample_flutter_app/docs/01_ARCHITECTURE_AND_QUESTIONS.md`.

---

## Epoch Overview

| Epoch | Title | Deliverables |
| :--- | :--- | :--- |
| **Epoch 0** | Tooling, Scaffolding & TDD Baseline | FastAPI + Beanie setup, Flutter project skeleton, pytest & flutter_test |
| **Epoch 1** | Accounts & Authentication Flow | User registration, password hashing, JWT tokens, Flutter login/register UI |
| **Epoch 2** | Todo Data Model (FHIR-aligned) & Persistence | Beanie/ODM models, FHIR Task field mapping, CRUD service layer |
| **Epoch 3** | REST API & ML-Accessible Endpoints | Full Task CRUD endpoints, Bulk ML dataset export, task analytics |
| **Epoch 4** | Flutter UI/UX & State Management | Task list screen, dismissible swipe cards, filter chips, bottom sheet creation |
| **Epoch 5** | ML Feature Integration | NLP task priority inference endpoint, Flutter smart priority suggestion |
| **Epoch 6** | E2E Testing & Deployment Packaging | End-to-end integration tests, Dockerization, AWS App Runner / S3 configs |

---

## Epoch 0: Tooling, Scaffolding & TDD Baseline

### [SMP-EP0-TK01] FastAPI Backend Scaffolding & Pytest Setup
- **Summary:** Initialize the backend directory with `pyproject.toml`, FastAPI application factory, and configure `pytest` with `pytest-asyncio` and `pytest-cov`.
- **Referenced Questions:** `[Q-SAMPLE-ODM-01]` (ODM Selection).
- **Tasks & Acceptance Criteria:**
  1. Define dependencies: `fastapi`, `uvicorn`, `beanie` (or selected ODM), `motor`, `pydantic-settings`, `pytest`, `pytest-asyncio`, `pytest-cov`, `httpx`, `ruff`, `mypy`.
  2. Implement `tests/conftest.py` with an async test client fixture.
  3. Create health check endpoint `GET /api/v1/health` returning `{"status": "ok"}`.
- **TDD Test Spec:** `pytest tests/api/test_health.py` asserts 200 OK and valid JSON response.

---

### [SMP-EP0-TK02] Flutter Project Scaffolding & Testing Harness
- **Summary:** Initialize the Flutter client application and verify that `flutter test` executes cleanly.
- **Referenced Questions:** `[Q-SAMPLE-UI-01]` (Target Form Factor).
- **Tasks & Acceptance Criteria:**
  1. Run `flutter create frontend --org com.sample.todo`.
  2. Add dependencies to `pubspec.yaml`: `flutter_riverpod` (or chosen state manager), `http` or `dio`, `flutter_secure_storage`, `mocktail` (dev).
  3. Write a smoke test in `test/widgets/smoke_test.dart`.
- **TDD Test Spec:** `flutter test` passes 100% of tests.

---

### [SMP-EP0-TK03] Local Docker-Compose Environment
- **Summary:** Create a `docker-compose.yml` to run MongoDB locally alongside the FastAPI backend for development.
- **Referenced Questions:** `[Q-SAMPLE-AWS-01]` (Local vs. Cloud Deployment).
- **Tasks & Acceptance Criteria:**
  1. Create `docker-compose.yml` launching `mongo:7` on port 27017 and a volume for data persistence.
  2. Ensure the FastAPI backend connects to the local MongoDB instance via environment variable `DATABASE_URL`.
- **TDD Test Spec:** Backend successfully connects and initializes ODM collections on startup.

---

## Epoch 1: Accounts & Authentication Flow

### [SMP-EP1-TK01] User Document Model & Credential Security
- **Summary:** Implement the `User` ODM document model with encrypted password hashing using bcrypt.
- **Referenced Questions:** `[Q-SAMPLE-AUTH-01]` (Auth Architecture).
- **Tasks & Acceptance Criteria:**
  1. Write failing unit test verifying password cannot be saved in plaintext.
  2. Implement `User` model with fields: `id`, `email`, `hashed_password`, `full_name`, `is_active`, `created_at`.
  3. Implement utility functions `hash_password()` and `verify_password()`.
- **TDD Test Spec:** `test_password_hashing()` verifies bcrypt salt generation and verification matching.

---

### [SMP-EP1-TK02] FastAPI Authentication Endpoints
- **Summary:** Build endpoints for user registration, login (OAuth2 password flow), and current user info.
- **Referenced Questions:** `[Q-SAMPLE-AUTH-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write tests for:
     - `POST /api/v1/auth/register` (creates user, fails on duplicate email).
     - `POST /api/v1/auth/token` (returns JWT access and refresh tokens).
     - `GET /api/v1/auth/me` (returns current user profile given Bearer token).
  2. Return 401 Unauthorized for invalid credentials or missing tokens.
- **TDD Test Spec:** API tests verify registration, successful token retrieval, and token validation.

---

### [SMP-EP1-TK03] Flutter Authentication Service & Secure Storage
- **Summary:** Implement Flutter client service for auth HTTP calls and token persistence via `flutter_secure_storage`.
- **Referenced Questions:** `[Q-SAMPLE-AUTH-01]`, `[Q-SAMPLE-UI-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write unit tests mocking HTTP responses for login and register.
  2. Implement `AuthService` storing access and refresh tokens securely in platform Keychain/KeyStore.
  3. Ensure logout clears tokens from secure storage.
- **TDD Test Spec:** Unit tests verify tokens are retrieved, saved, and deleted from secure storage mock.

---

### [SMP-EP1-TK04] Flutter Login & Registration Screens
- **Summary:** Build the user interface for Login and Registration with form validation and widget tests.
- **Referenced Questions:** `[Q-SAMPLE-UI-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write widget tests (`testWidgets`): test email and password inputs, validation error on short password, submit button click.
  2. Implement responsive Material 3 LoginScreen and RegisterScreen.
  3. Display loading spinner while authenticating and error snackbar on failure.
- **TDD Test Spec:** Widget tests verify all UI states (validation failure, loading state, successful navigation).

---

## Epoch 2: Todo Data Model (FHIR-aligned) & Persistence

### [SMP-EP2-TK01] Task Document Schema (FHIR-aligned)
- **Summary:** Define the Task ODM model mapping to the HL7 FHIR `Task` resource specifications.
- **Referenced Questions:** `[Q-SAMPLE-ODM-01]`, `[Q-SAMPLE-FHIR-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write unit tests validating task status transitions (`draft` -> `in-progress` -> `completed` / `cancelled`).
  2. Implement `TaskDocument` with fields:
     - `id`: Unique identifier
     - `owner_id`: Reference to User
     - `title`: Short task summary (maps to FHIR `Task.description`)
     - `note`: Extended description (maps to FHIR `Task.note`)
     - `status`: Enum (`draft`, `in-progress`, `completed`, `cancelled`)
     - `priority`: Enum (`routine`, `urgent`, `asap`, `stat`)
     - `due_date`: Optional ISO8601 timestamp (maps to `executionPeriod.end`)
     - `tags`: List of category strings
     - `created_at`, `updated_at`, `completed_at`
- **TDD Test Spec:** Schema tests verify valid deserialization and rejection of invalid status/priority values.

---

### [SMP-EP2-TK02] Task CRUD Service Layer
- **Summary:** Implement the application service layer managing task queries, creation, updates, and user scoping.
- **Referenced Questions:** `[Q-SAMPLE-ODM-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write tests ensuring users can only read, update, and delete their own tasks.
  2. Implement methods: `create_task()`, `get_tasks(user_id, status, priority, search)`, `toggle_task_completion()`, `delete_task()`.
  3. Automatically set `completed_at` timestamp when status transitions to `completed`.
- **TDD Test Spec:** Unit tests verify strict user data isolation and timestamp management.

---

### [SMP-EP2-TK03] FHIR R4 Task Resource Serializer
- **Summary:** Implement a converter that exports internal Todo records into compliant HL7 FHIR R4 `Task` JSON resources.
- **Referenced Questions:** `[Q-SAMPLE-FHIR-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write unit tests asserting serialized output matches official FHIR R4 schema structure (`resourceType: "Task"`).
  2. Correctly map fields to FHIR standard codings (e.g., `priority: "urgent"`).
- **TDD Test Spec:** Output JSON passes schema validation against FHIR R4 Task specifications.

---

## Epoch 3: REST API & ML-Accessible Endpoints

### [SMP-EP3-TK01] Task REST Endpoints
- **Summary:** Build the authenticated REST routes for Task management.
- **Referenced Questions:** `[Q-SAMPLE-FHIR-01]`.
- **Tasks & Acceptance Criteria:**
  1. Implement endpoints:
     - `GET /api/v1/tasks` (with filtering query params: `status`, `priority`, `search`)
     - `POST /api/v1/tasks` (creates task, returns 201 Created)
     - `GET /api/v1/tasks/{id}` (returns task details)
     - `PATCH /api/v1/tasks/{id}` (updates fields or toggles completion)
     - `DELETE /api/v1/tasks/{id}` (deletes task, returns 204 No Content)
  2. Write integration tests for all status codes (200, 201, 204, 400, 404).
- **TDD Test Spec:** API tests verify complete CRUD workflow for authenticated users.

---

### [SMP-EP3-TK02] Machine Learning Bulk Data Export Endpoint
- **Summary:** Build a high-throughput endpoint for ML platforms to export historical task records for training.
- **Referenced Questions:** `[Q-SAMPLE-ML-01]`.
- **Tasks & Acceptance Criteria:**
  1. Implement `GET /api/v1/ml/export/tasks` supporting query parameters: `from_date`, `to_date`, `format=json|ndjson`.
  2. Return clean tabular/vectorizable records including: `task_id`, `title_length`, `description_length`, `priority`, `tags`, `time_to_completion_seconds`.
  3. Ensure user identifiers are either excluded or cryptographically pseudonymized (anonymized hash).
- **TDD Test Spec:** Integration test verifies NDJSON format output and confirms no plaintext user PII is exposed.

---

### [SMP-EP3-TK03] Task Analytics & Metrics Endpoint
- **Summary:** Expose summary statistics for user productivity and task completion velocity.
- **Referenced Questions:** `[Q-SAMPLE-ML-01]`.
- **Tasks & Acceptance Criteria:**
  1. Implement `GET /api/v1/tasks/analytics` returning: `total_tasks`, `completed_count`, `active_count`, `completion_rate`, `average_completion_hours`.
  2. Write tests asserting correct aggregation math against test fixtures.
- **TDD Test Spec:** Test asserts exact counts and average calculations across varied completed/pending tasks.

---

## Epoch 4: Flutter UI/UX & State Management

### [SMP-EP4-TK01] Task State Management Architecture
- **Summary:** Implement client-side state management (Riverpod/BLoC) handling task list loading, filtering, and error handling.
- **Referenced Questions:** `[Q-SAMPLE-UI-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write unit tests for the TaskNotifier/Cubit simulating initial fetch, filter change, and task addition.
  2. Implement optimistic update logic: immediately reflect toggled task in state before server response resolves; revert if server returns error.
- **TDD Test Spec:** Unit tests assert state transitions: `Loading -> Success([tasks]) -> Error(message)`.

---

### [SMP-EP4-TK02] Task List Screen with Filter Chips & Search
- **Summary:** Build the main dashboard screen featuring Material 3 search bar, filter chips (`All`, `Active`, `Completed`, `Urgent`), and pull-to-refresh.
- **Referenced Questions:** `[Q-SAMPLE-UI-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write widget tests asserting filter chip taps filter the displayed task cards.
  2. Render empty state illustration when list is empty.
  3. Support pull-to-refresh gesture updating the task list.
- **TDD Test Spec:** Widget test asserts tapping "Completed" chip hides active tasks from the screen.

---

### [SMP-EP4-TK03] Dismissible Task Card Widget with Swipe Gestures
- **Summary:** Create interactive task card widget with swipe-to-delete (left) and swipe-to-complete (right) gestures.
- **Referenced Questions:** `[Q-SAMPLE-UI-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write widget tests simulating drag gestures left and right on `Dismissible`.
  2. Swiping right toggles completion and plays a brief check animation.
  3. Swiping left shows red delete background with trash icon, removes item, and shows SnackBar with "Undo" button.
- **TDD Test Spec:** `testWidgets` verifies dismiss gesture triggers callback and SnackBar renders.

---

### [SMP-EP4-TK04] Ergonomic Modal Bottom Sheet for Task Creation
- **Summary:** Develop a modal bottom sheet opened via Floating Action Button (FAB) for rapid task entry.
- **Referenced Questions:** `[Q-SAMPLE-UI-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write widget tests for text field input, priority chip selection (`Routine`, `Urgent`), and save button.
  2. Auto-focus text input when bottom sheet opens; submit on software keyboard "Done" action.
  3. Validate that blank titles cannot be submitted.
- **TDD Test Spec:** Widget test verifies button remains disabled when input is empty and adds task on submit.

---

## Epoch 5: Machine Learning Integration & Predictive Features

### [SMP-EP5-TK01] ML Task Priority Inference Service
- **Summary:** Build a lightweight NLP inference service suggesting task priority and tags based on the task description.
- **Referenced Questions:** `[Q-SAMPLE-ML-01]`.
- **Tasks & Acceptance Criteria:**
  1. Implement inference module (using scikit-learn pipeline or keyword/heuristic embeddings).
  2. Create endpoint `POST /api/v1/ml/predict-priority` accepting `{"text": "..."}` and returning `{"priority": "urgent"|"routine", "confidence": float, "tags": [...]}`.
  3. Write tests verifying known urgent medical keywords ("stat", "urgent", "emergency", "immediately") trigger `urgent` prediction.
- **TDD Test Spec:** Unit tests verify predicted priority matches expected thresholds across test phrases.

---

### [SMP-EP5-TK02] Flutter Smart Priority Suggestion Integration
- **Summary:** Integrate the ML priority prediction endpoint into the Flutter task creation bottom sheet.
- **Referenced Questions:** `[Q-SAMPLE-ML-01]`, `[Q-SAMPLE-UI-01]`.
- **Tasks & Acceptance Criteria:**
  1. In Flutter task creation sheet, debounce user typing by 400ms.
  2. Call ML prediction endpoint and display a subtle suggestion badge (e.g., *"Suggested: Urgent (92%)"* with one-tap apply).
  3. Write widget tests mocking the suggestion response and verifying badge displays.
- **TDD Test Spec:** Widget test asserts suggestion badge appears after typing urgent keywords.

---

## Epoch 6: End-to-End Testing & AWS Packaging

### [SMP-EP6-TK01] Backend Full E2E Test Suite
- **Summary:** Automated integration test suite running full user workflows against a real test database.
- **Referenced Questions:** `[Q-SAMPLE-ODM-01]`.
- **Tasks & Acceptance Criteria:**
  1. Workflow: Register user -> Login -> Create 3 Tasks -> Filter by Urgent -> Complete Task -> Export ML Dataset -> Fetch Analytics.
  2. Assert all database records and calculations reflect the complete workflow.
- **TDD Test Spec:** Pytest suite passes 100% with no unhandled exceptions.

---

### [SMP-EP6-TK02] Flutter E2E Integration Test (`integration_test`)
- **Summary:** Automated end-to-end user test running on Flutter Web or Desktop.
- **Referenced Questions:** `[Q-SAMPLE-UI-01]`.
- **Tasks & Acceptance Criteria:**
  1. Implement `integration_test/app_test.dart`.
  2. Automate: Launch app -> Enter credentials -> Tap Login -> Add new task -> Swipe to complete -> Verify badge update.
- **TDD Test Spec:** `flutter test integration_test/app_test.dart` passes cleanly.

---

### [SMP-EP6-TK03] AWS Deployment & Containerization Blueprint
- **Summary:** Create Dockerfiles and deployment manifests for AWS App Runner, DocumentDB, and S3/CloudFront.
- **Referenced Questions:** `[Q-SAMPLE-AWS-01]`.
- **Tasks & Acceptance Criteria:**
  1. Multi-stage `backend/Dockerfile` optimizing image size.
  2. Docker build configuration for Flutter Web (`frontend/web`).
  3. AWS deployment documentation explaining how to push backend to AWS App Runner / ECR and frontend to S3/CloudFront.
- **TDD Test Spec:** Docker build succeeds and container passes health check.
