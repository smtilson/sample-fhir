# Sample App Development Plan & TDD Strategy

This document provides a concrete test-driven development (TDD) blueprint for the **Sample Todo & Account Application**, designed to help you quickly build proficiency in Flutter, FastAPI, and NoSQL ODM development.

---

## 1. Project Directory Structure

The sample app workspace is organized cleanly into two independent sub-projects:

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
│   │   │   └── database.py      # ODM (Beanie/Motor) initialization
│   │   ├── models/              # ODM Document & Pydantic models (User, Todo/Task)
│   │   ├── schemas/             # Request & Response schemas (TaskCreate, UserOut)
│   │   ├── services/            # Business logic & ML inference services
│   │   └── api/                 # FastAPI routers (auth, tasks, ml)
│   └── tests/
│       ├── conftest.py          # Fixtures: async client, test DB, auth tokens
│       ├── unit/                # Unit tests: models, hashing, ML helpers
│       └── api/                 # Integration tests: HTTP route responses
└── frontend/                    # Flutter project
    ├── pubspec.yaml             # Dart dependencies
    ├── lib/
    │   ├── main.dart            # Flutter entry point & app theme
    │   └── src/
    │       ├── models/          # Dart models (Todo/Task, User, AuthToken)
    │       ├── services/        # HTTP API client & secure storage
    │       ├── controllers/     # State management (Riverpod / BLoC)
    │       ├── views/           # UI Screens (Login, TodoList, TaskDetail)
    │       └── widgets/         # Reusable widgets (TaskCard, CreateTaskSheet)
    └── test/
        ├── unit/                # Unit tests (models, API client parsing)
        └── widgets/             # Widget tests (LoginScreen, TodoListScreen)
```

---

## 2. Test-Driven Development (TDD) Strategy

### 2.1 Backend TDD (Python & FastAPI)

Every backend feature follows the standard TDD cycle:
1. **Red:** Write a failing test in `tests/api/` or `tests/unit/`.
2. **Green:** Implement the minimum FastAPI router, Beanie model, or service logic to pass.
3. **Refactor:** Clean up code, add typing annotations, ensure `ruff` and `mypy` pass.

#### Key Backend Testing Techniques:
- **Asynchronous Testing:** Using `pytest-asyncio` with `httpx.AsyncClient` allows testing async endpoints without spinning up a live network socket:
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

---

### 2.2 Frontend TDD (Flutter Testing for Beginners)

As someone new to Flutter, Flutter’s built-in testing capabilities are one of its greatest strengths. You don't need an emulator to test UI interactions!

#### The Three Testing Tiers:

#### 1. Unit Tests (`test/unit/`)
Tests pure Dart logic, JSON serialization, and controllers.
- *Example:* Verifying that `Task.fromJson(jsonMap)` correctly parses FHIR-aligned fields and handles missing optional notes gracefully.
- *Execution:* Runs on the standard command line in milliseconds via `flutter test test/unit/`.

#### 2. Widget Tests (`test/widgets/`)
Widget tests mount UI components in a simulated headless test environment (`WidgetTester`).
- **Simulating Taps:**
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
- **Simulating Text Input:**
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

## 3. Local Development Commands

### Backend Commands
- **Install dependencies:** `pip install -e ".[dev]"`
- **Run tests with coverage:** `pytest --cov=src --cov-report=term-missing`
- **Run local dev server:** `uvicorn src.main:app --reload --port 8000`
- **Interactive API Docs:** Navigate to `http://localhost:8000/docs` (Swagger UI)

### Frontend Commands (Flutter)
- **Install dependencies:** `flutter pub get`
- **Run all tests:** `flutter test`
- **Run tests with coverage:** `flutter test --coverage`
- **Run application on Chrome (Web):** `flutter run -d chrome`
- **Run application on Windows (Desktop):** `flutter run -d windows`
