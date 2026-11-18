# Sample App Development Plan & TDD Strategy

This document provides a concrete test-driven development (TDD) blueprint for the **Sample Todo & Account Application**, designed to help you quickly build proficiency in Flutter, FastAPI, and NoSQL ODM development.

---

## 1. Project Directory Structure

The sample app workspace is organized into two independent sub-projects:

```
sample_flutter_app/
├── README.md
├── docs/
│   ├── 01_ARCHITECTURE_AND_QUESTIONS.md
│   ├── 02_DEVELOPMENT_PLAN.md
│   └── 03_EPOCHS_AND_TICKETS.md
├── backend/
│   ├── pyproject.toml
│   ├── src/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Pydantic Settings (DB URL, JWT Secret)
│   │   ├── core/
│   │   │   ├── security.py      # Password hashing & JWT creation/verification
│   │   │   └── database.py      # Beanie / Motor initialization
│   │   ├── models/              # Beanie Document models (User, Task)
│   │   ├── schemas/             # Pydantic schemas (TaskCreate, TaskOut, FHIRTaskExport)
│   │   ├── services/            # Business logic & ML bulk export serializer
│   │   └── api/                 # FastAPI routers (auth, tasks, ml_export)
│   └── tests/
│       ├── conftest.py          # Fixtures: async client, test DB, auth tokens
│       ├── unit/                # Unit tests: models, hashing, FHIR serializer
│       └── api/                 # Integration tests: HTTP route responses
└── frontend/                    # Flutter project
    ├── pubspec.yaml             # Dart dependencies
    ├── lib/
    │   ├── main.dart            # Flutter entry point & app theme (Material 3)
    │   └── src/
    │       ├── models/          # Dart models (Todo/Task, User, AuthToken)
    │       ├── services/        # HTTP API client & secure storage
    │       ├── controllers/     # State management (Riverpod / BLoC)
    │       ├── views/           # UI Screens (Login, TodoList, TaskDetail)
    │       └── widgets/         # Reusable widgets (TaskCard, CreateTaskSheet, ConfirmDialog)
    └── test/
        ├── unit/                # Unit tests (models, API client parsing)
        └── widgets/             # Widget tests (LoginScreen, TodoListScreen)
```

---

## 2. Test-Driven Development (TDD) Strategy

### 2.0 Roadmap Evolution & Fast-Track Sync (`[Q-SAMPLE-REORG-01]`)

Per user decision `[Q-SAMPLE-REORG-01]`, the development plan is reorganized to prioritize understanding Flutter and synchronizing it with the FastAPI backend immediately:
- **Phase 1 (Active Focus — Fast-Track Sync):**
  1. **Minimal Accounts:** User creation with `name`, `email`, and simple bcrypt-hashed `password`. No complex JWT token or OAuth2 infrastructure required in this initial stage.
  2. **Simple Tasks:** User-scoped task model with `name`, `is_completed` (completion status), `metadata` (JSON/dict), and `user_id`.
  3. **Flutter UI & Live Sync:** Flutter frontend connecting to FastAPI endpoints, displaying user-scoped tasks, toggling completion with checkboxes, and submitting new tasks.
- **Phase 2 (Deferred Hardening & Standards Alignment):**
  1. Advanced JWT tokens, refresh tokens, and AWS Cognito architecture mapping.
  2. Incremental FHIR Task lifecycle state machine and R4 JSON export.
  3. Authorized ML bulk data export and analytics.
  4. Multi-platform expansion and AWS cloud deployment.

### 2.0.1 Codebase & Architecture Audit Review Milestone (`docs/REPORT_2026-11-14_1428.md`)

An extensive architectural and codebase audit report was authored on 2026-11-14 (`docs/REPORT_2026-11-14_1428.md`) evaluating the repository baseline, test fixtures, configuration, dependencies, and API surface across tickets `[SMP-EP0-TK01]` through `[SMP-EP1-TK05]`.

As part of the development plan, **the entire audit report must be read through and its points systematically addressed as a dedicated cleanup milestone** alongside/in conjunction with Epoch 2 synchronization work:

1. **High-Severity & Frontend Blockers:**
   - `[AUDIT-APP-02]`: Add CORS middleware (`CORSMiddleware`) before Flutter Web requests fail.
   - `[AUDIT-CFG-01]`: Restrict demo mode defaults to avoid unintended in-memory execution and seed password exposure.
   - `[AUDIT-DB-01]`: Remove top-level `mongomock` import from runtime `src/core/database.py` (preventing production import crash).
   - `[AUDIT-DEP-01]`: Correct `pyproject.toml` package discovery and missing README reference.
2. **Atomic Testing & Fixture Refactoring:**
   - `[AUDIT-TEST-01]`: Refactor API integration tests (`tests/api/test_users.py`, `tests/api/test_tasks.py`) to consume persisted fixtures rather than setting up state via inline `client.post` requests (eliminating operation bundling).
   - `[AUDIT-TEST-02]`: Correct fixture layering violations in `tests/conftest.py` so Layer 1 fixtures remain pure data without database side-effects.
   - `[AUDIT-TEST-03]`: Disaggregate multi-contract bundled tests into single-responsibility atomic tests.
   - `[AUDIT-TEST-04]`: Validate demo mode through real ASGI lifespan handling rather than manual setup.
3. **API Reliability & Error Handling:**
   - `[AUDIT-API-01]` & `[AUDIT-API-02]`: Eliminate duplicated get-or-404 code and replace overly broad `except Exception` blocks with targeted ObjectId validation.
   - `[AUDIT-API-03]`: Safely handle concurrent `DuplicateKeyError` exceptions.
   - `[AUDIT-API-04]`: Establish and test an explicit policy for orphaned tasks when a user is deleted.
4. **Tooling, Hygiene & Documentation:**
   - `[AUDIT-DB-02]`: Consolidate the duplicated `mongomock` compatibility shim into a single shared utility.
   - `[AUDIT-DEP-02]`: Align package dependencies (`email-validator`, remove unused `passlib`).
   - `[AUDIT-REPO-01]` & `[AUDIT-DOC-01]`: Commit untracked test files (`test_demo_mode.py`), update ticket status markers, and address open questions `[Q-AUDIT-01]` through `[Q-AUDIT-05]`.

---

### 2.1 Backend TDD (Python & FastAPI)

Every backend feature follows an atomic, three-tier testing progression where each layer is tested in isolation before moving up the stack:

#### The Three-Tier Backend Testing Hierarchy:

1. **Tier 1 — Document Model & Database CRUD (`tests/unit/test_*_model.py`):**
   - Tests Beanie ODM document models directly against an in-memory database (`mongomock-motor`) without HTTP routing or FastAPI middleware.
   - Verifies single-operation CRUD: inserting records, querying by ID, querying by index, updating fields, and deleting records.
   - Verifies database-level constraint enforcement: asserts that MongoDB unique indexes raise `pymongo.errors.DuplicateKeyError` on duplicate key inserts.
   - Verifies document instantiation validation: asserts that missing required fields raise Pydantic `ValidationError`.

2. **Tier 2 — Transport Schemas & Validation (`tests/unit/test_*_schemas.py`):**
   - Tests Pydantic DTO (Data Transfer Object) schemas in complete isolation from the database and web framework.
   - Input validation: verifies `EmailStr` format validation, string constraints, and rejection of malformed or empty payloads.
   - Public contract & credential shielding: verifies output schemas (e.g., `UserOut`) correctly map from attributes and strictly omit sensitive fields (passwords, hashes) from schema definitions and serialization dictionaries.

3. **Tier 3 — Transport & API Route Integration (`tests/api/test_*.py`):**
   - Tests HTTP route handlers and middleware using `httpx.AsyncClient` with `ASGITransport`.
   - Verifies application wire-up: routers registered on `create_app()` and exposed in OpenAPI documentation.
   - Verifies HTTP status codes and contracts: `201 Created`, `200 OK`, `404 Not Found`, `422 Unprocessable Entity`.
   - Verifies error mapping: confirms that endpoints catch database-level constraints and map them to clean client responses (e.g., converting duplicate key violations into `HTTP 400 Bad Request`).

#### Key Backend Testing Techniques:
- **Asynchronous Testing:** Using `pytest-asyncio` with `httpx.AsyncClient` allows testing async endpoints in memory without spinning up a live network socket:
  ```python
  @pytest.mark.asyncio
  async def test_create_todo_returns_201(async_client, auth_headers):
      payload = {"title": "Take vital signs", "priority": "urgent"}
      response = await async_client.post("/api/v1/tasks", json=payload, headers=auth_headers)
      assert response.status_code == 201
      data = response.json()
      assert data["title"] == "Take vital signs"
      assert data["status"] == "in-progress"
  ```
- **Database Isolation:** Tests run against an isolated test MongoDB database (or `mongomock-motor`), clearing collections between test runs to ensure complete isolation.
- **Dependency Overrides:** FastAPI allows seamless mocking of authentication dependencies in tests:
  ```python
  app.dependency_overrides[get_current_user] = lambda: mock_user
  ```
  > **Devin re-Cognito:** When migrating to AWS Cognito, `get_current_user` simply verifies the Cognito JWT signature against AWS public keys (JWKS endpoint) instead of a local HMAC secret key. The FastAPI dependency override pattern in tests remains identical.

---

### 2.2 Frontend TDD (Flutter Testing for Beginners)

As someone new to Flutter, Flutter’s built-in testing capabilities are one of its greatest strengths. You don't need an emulator to test UI interactions!

#### The Three Testing Tiers:

#### 1. Unit Tests (`test/unit/`)
Tests pure Dart logic, JSON serialization, and controllers.
- *Example:* Verifying that `Task.fromJson(jsonMap)` correctly parses task fields and handles missing optional notes gracefully.
- *Execution:* Runs on the standard command line in milliseconds via `flutter test test/unit/`.

#### 2. Widget Tests (`test/widgets/`)
Widget tests mount UI components in a simulated headless test environment (`WidgetTester`).
- **Testing Explicit Task Completion (No Swipes):**
  Per user decision, task management relies on explicit controls (checkboxes and action buttons) rather than swipe gestures:
  ```dart
  testWidgets('Tapping checkbox marks task complete', (WidgetTester tester) async {
    // 1. Render the task card
    await tester.pumpWidget(MaterialApp(home: Scaffold(body: TaskCard(task: activeTask))));

    // 2. Find checkbox and simulate user tap
    final checkbox = find.byType(Checkbox);
    expect(checkbox, findsOneWidget);
    await tester.tap(checkbox);
    await tester.pumpAndSettle(); // Wait for state/animation to settle

    // 3. Verify state callback was invoked
    expect(mockController.markedCompleted, isTrue);
  });
  ```
- **Testing Explicit Delete Confirmation:**
  ```dart
  testWidgets('Tapping delete shows confirmation dialog', (WidgetTester tester) async {
    await tester.pumpWidget(MaterialApp(home: Scaffold(body: TaskCard(task: activeTask))));
    
    // Tap delete button icon
    await tester.tap(find.byIcon(Icons.delete_outline));
    await tester.pumpAndSettle();

    // Verify confirmation dialog appears
    expect(find.text('Delete Task?'), findsOneWidget);
  });
  ```
- **Simulating Text Input in Bottom Sheet:**
  ```dart
  await tester.enterText(find.byType(TextField), 'Review lab results');
  await tester.tap(find.text('Save'));
  ```

#### 3. Mocking with `mocktail`
Instead of calling real backend servers during Flutter widget tests, we mock the API client using `mocktail`:
```dart
class MockApiClient extends Mock implements ApiClient {}

// In test:
when(() => mockApiClient.fetchTasks()).thenAnswer((_) async => [sampleTask]);
```

---

## 3. Platform Rollout Strategy

Development and testing follows a phased, incremental platform sequence:
1. **Phase 1: Browser (Flutter Web)**
   - Fastest iteration during initial development.
   - Run immediately in Chrome via `flutter run -d chrome`.
   - Rapid UI feedback and cross-browser responsiveness.
2. **Phase 2: Mobile (Android & iOS)**
   - Test on Android Emulator or physical mobile device.
   - Verify keyboard avoidance, mobile touch targets, and mobile secure storage (`Keychain` / `KeyStore`).
3. **Phase 3: Desktop (Windows)**
   - Compile native Windows binary via `flutter run -d windows`.
   - Verify desktop window resizing and keyboard shortcuts.

---

## 4. Local Development Commands (WSL & Windows)

### Backend Commands (Run inside WSL)
As documented in `AGENTS.md`, execute backend commands via WSL:
- **Activate Virtual Environment:**
  ```bash
  cd /mnt/c/Users/seant/OneDrive/Desktop/main_repos/sample-fhir
  source <venv-path>/bin/activate
  ```
- **Run tests with coverage:**
  ```bash
  pytest --cov=backend/src --cov-report=term-missing
  ```
- **Run local dev server:**
  ```bash
  uvicorn backend.src.main:app --reload --port 8000
  ```
- **Interactive API Docs:** Navigate to `http://localhost:8000/docs` (Swagger UI)

### Frontend Commands (Flutter)
- **Install dependencies:** `flutter pub get`
- **Run all tests:** `flutter test`
- **Run tests with coverage:** `flutter test --coverage`
- **Phase 1 (Browser):** `flutter run -d chrome`
- **Phase 2 (Mobile):** `flutter run -d android`
- **Phase 3 (Desktop):** `flutter run -d windows`
