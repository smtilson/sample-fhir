# Development Plan & TDD Strategy

This document outlines the software engineering methodology, test-driven development (TDD) standards, architectural boundaries, and phased roadmap for the electronic medical records (FHIR) project.

---

## 1. Guiding Engineering Principles

1. **Test-Driven Development (TDD) First:**
   - No production code is written without a prior failing test ("Red - Green - Refactor").
   - Code changes must maintain or increase test coverage.
2. **Technological Agnosticism via Clean / Hexagonal Architecture:**
   - Core healthcare logic and FHIR validation are isolated from database drivers and web frameworks.
   - Database operations are defined through abstract repository interfaces (e.g., `PatientRepository`, `ObservationRepository`). This allows seamless switching between Amazon DocumentDB, DynamoDB, AWS HealthLake, or in-memory test mocks without modifying business logic.
3. **Standards-Compliant Healthcare Interoperability:**
   - Adhere strictly to the HL7 FHIR specification (R4/R5) and the SMART App Launch framework.
4. **Security by Design (HIPAA Readiness):**
   - End-to-end encryption, strict role-based access control, comprehensive audit logging of all protected health information (PHI) access, and automated secret scanning.

---

## 2. Test-Driven Development (TDD) Framework

### 2.1 Backend Testing (Python)

The backend uses **`pytest`** as the unified test runner and assertion framework.

#### Core Python Testing Tooling
- **`pytest`**: Main test framework and test discovery engine.
- **`pytest-asyncio`**: Allows native testing of asynchronous endpoints, database connections, and event loops.
- **`pytest-cov`**: Generates terminal and HTML line/branch test coverage metrics (`coverage.py`).
- **`httpx`** (or `fastapi.testclient.TestClient` / `flask.testing.FlaskClient`): Executes HTTP requests in memory without starting an external web server process.
- **`pytest-mock`**: Ergonomic wrapper around Python's `unittest.mock` for isolating external services (e.g., AWS KMS, Cognito, S3).
- **`factory-boy` / `faker`**: Creates realistic synthetic patient profiles and clinical measurements for testing without risking real patient data.

#### TDD Cycle for Python Services
```
1. Write Unit Test (Failing / Red)
   └── e.g., test_create_observation_rejects_missing_subject()
2. Run pytest (Confirm failure with descriptive assertion error)
3. Implement Minimal Code (Passing / Green)
   └── e.g., add FHIR schema validation in Pydantic model
4. Refactor
   └── Clean up abstractions, verify code passes ruff/mypy and all tests pass
```

#### Directory Layout for Python Tests
```
backend/
├── src/
│   ├── domain/        # Pure Python FHIR business logic & entities
│   ├── services/      # Application use cases (e.g. ingest_vitals.py)
│   ├── adapters/      # DB implementations (DocumentDB, HealthLake, DynamoDB)
│   └── api/           # Web framework endpoints (FastAPI / Flask routers)
└── tests/
    ├── conftest.py    # Shared pytest fixtures (mock DB, auth tokens, sample FHIR data)
    ├── unit/          # Fast in-memory unit tests (< 10ms each)
    │   ├── test_fhir_models.py
    │   ├── test_auth_service.py
    │   └── test_ml_pipeline.py
    ├── integration/   # Tests verifying database queries and adapter contracts
    │   └── test_documentdb_repository.py
    └── api/           # Route tests verifying HTTP status codes and responses
        ├── test_patient_endpoints.py
        └── test_smart_on_fhir_launch.py
```

---

### 2.2 Frontend Testing (Flutter) — A Guide for Beginners

Since you are completely new to Flutter, here is an orientation to Flutter's built-in testing pyramid:

```
         ▲
        / \
       /   \     Integration Tests (E2E on Emulator/Device)
      /-----\    
     /       \   Widget Tests (Component & UI Testing in Memory)
    /---------\  
   /           \ Unit Tests (Dart Business Logic, State, Repositories)
  /─────────────\
```

#### 1. Unit Tests (`test/unit/`)
- **What they test:** Plain Dart classes, data parsing (FHIR JSON to Dart objects), state management notifiers/controllers, validation logic.
- **Speed:** Milliseconds. Runs via local Dart VM.
- **Tooling:** Built-in `flutter_test` package.
- **Example:** Testing that an invalid Blood Pressure measurement throws a validation exception.

#### 2. Widget Tests (`test/widgets/`)
- **What they test:** Individual UI widgets (e.g., a Patient Summary Card, Login Form, Vitals Input Field).
- **How it works:** Flutter renders the widget in a headless, virtual screen environment using `WidgetTester`. It does **not** need an Android or iOS emulator!
- **Capabilities:**
  - `tester.pumpWidget()` mounts the widget.
  - `tester.enterText(find.byType(TextField), 'John Doe')` simulates user typing.
  - `tester.tap(find.byType(ElevatedButton))` simulates button clicks.
  - `expect(find.text('Patient Saved'), findsOneWidget)` asserts UI state changes.
- **Speed:** Hundreds of widget tests run in just a few seconds.

#### 3. Integration Tests (`integration_test/`)
- **What they test:** The complete application running from end to end on an Android/iOS emulator or Chrome browser.
- **How it works:** Tests actual user journeys (e.g., launching app, logging in via OAuth, loading records from the backend API, and rendering the patient list).

#### Mocking in Flutter: `mocktail`
In modern Flutter, **`mocktail`** is the recommended mocking library (it offers clean, type-safe mocks without requiring code generation like older tools).

---

## 3. Hexagonal / Clean Architecture Pattern

To fulfill your requirement: *"I want to be somewhat agnostic about technologies that should be used until a decision needs to be made,"* the project will follow **Hexagonal (Ports and Adapters) Architecture**.

```
                   ┌──────────────────────────────────────┐
                   │            API Framework             │
                   │      (FastAPI or Flask or CLI)       │
                   └──────────────────┬───────────────────┘
                                      │ (Driving Adapter)
                                      ▼
                   ┌──────────────────────────────────────┐
                   │           Application Layer          │
                   │      (Use Cases & Orchestration)     │
                   └──────────────────┬───────────────────┘
                                      │
                                      ▼
                   ┌──────────────────────────────────────┐
                   │             Domain Core              │
                   │  (Pure FHIR Entities & Validation)   │
                   └──────────────────┬───────────────────┘
                                      │
                                      ▼ (Port / Interface)
                   ┌──────────────────────────────────────┐
                   │          Repository Ports            │
                   │  (IPatientRepository, IAuthService)  │
                   └──────────────────┬───────────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│ Amazon DocumentDB│        │ Amazon DynamoDB  │        │  AWS HealthLake  │
│     Adapter      │        │     Adapter      │        │     Adapter      │
└──────────────────┘        └──────────────────┘        └──────────────────┘
```

### Why this benefits you:
- **Framework Agnostic:** Whether we choose FastAPI or Flask (or swap later), the core business logic and FHIR entities remain 100% untouched.
- **Database Agnostic:** We can write and test the domain against an `InMemoryFHIRRepository` in pytest. When you decide between DocumentDB, DynamoDB, or AWS HealthLake, we simply implement a concrete adapter for that database.
- **Cloud Agnostic:** Local development can run entirely offline or in local containers without AWS costs.

---

## 4. Development Workflow & Git Strategy

1. **Feature Branching:** Every development ticket will have a dedicated branch (e.g., `feat/ep1-tk01-user-model`).
2. **Pre-commit Quality Gates:**
   - Python: `ruff` (linter and formatter), `mypy` (type-checker), `pytest` (test suite).
   - Flutter: `flutter analyze` (Dart analyzer) and `flutter test`.
3. **Continuous Integration (CI):**
   - GitHub Actions will run automated test suites on every pull request.
   - Enforce coverage threshold (defined in `[Q-TEST-01]`).
