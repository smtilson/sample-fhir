# Development Epochs & Tickets

This document defines the actionable engineering tickets for the development lifecycle of the electronic health records system.

Tickets are structured in sequential **Epochs** (phases). Every ticket that depends on an unresolved architectural decision references the corresponding question from `docs/01_ARCHITECTURE_AND_QUESTIONS.md`.

---

## Epoch Overview

| Epoch | Title | Focus Area |
| :--- | :--- | :--- |
| **Epoch 0** | Foundation, Environment & TDD Infrastructure | Project setup, testing harnesses (pytest & flutter_test), CI automation |
| **Epoch 1** | Identity, Authentication & Security Baseline | User accounts, RBAC, OAuth2/OIDC, HIPAA audit logging |
| **Epoch 2** | FHIR Domain Modeling & NoSQL Storage Engine | FHIR R4 schema validation, repository ports, AWS NoSQL persistence |
| **Epoch 3** | Web API & SMART on FHIR Interoperability | REST endpoints, `/metadata` CapabilityStatement, SMART scopes |
| **Epoch 4** | Flutter Cross-Platform Client Application | Mobile/web UI, state management, secure token storage, widget tests |
| **Epoch 5** | Data Processing & Machine Learning Pipeline | FHIR data transformation, de-identification, model inference service |
| **Epoch 6** | End-to-End Integration, Auditing & Hardening | Full-stack E2E tests, HIPAA security validation, release readiness |

---

## Epoch 0: Foundation, Environment & TDD Infrastructure

### [EP0-TK01] Backend Project Scaffolding & Pytest Harness
- **Summary:** Set up the Python project structure using standard packaging (e.g., `pyproject.toml`), virtual environment, dependency management, and configure `pytest`.
- **Referenced Questions:** None (tooling foundation).
- **Tasks & Acceptance Criteria:**
  1. Configure `pyproject.toml` with `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-mock`, `ruff`, and `mypy`.
  2. Implement `tests/conftest.py` with initial fixtures.
  3. Create a smoke test `tests/unit/test_smoke.py` asserting environment sanity.
  4. Ensure `pytest --cov=src --cov-report=term-missing` runs with 100% pass rate.
- **TDD Test Spec:** `test_environment_is_healthy()` passes and code coverage tool generates reports.

---

### [EP0-TK02] Flutter Project Scaffolding & `flutter_test` Setup
- **Summary:** Initialize the Flutter workspace with cross-platform targets and configure the testing environment including `flutter_test` and `mocktail`.
- **Referenced Questions:** `[Q-FLUTTER-01]` (Target Platforms).
- **Tasks & Acceptance Criteria:**
  1. Generate Flutter skeleton app (`flutter create`).
  2. Add dependencies for testing (`mocktail`, `flutter_test`).
  3. Establish folder structure: `lib/src/{models, views, controllers, services}` and `test/{unit, widgets}`.
  4. Implement an initial unit test and widget test verifying the test runner functions smoothly.
- **TDD Test Spec:** `flutter test` executes in under 5 seconds and passes all unit and widget tests.

---

### [EP0-TK03] Continuous Integration (CI) Workflow Pipeline
- **Summary:** Create automated GitHub Actions workflows to enforce testing and quality gates on all pull requests.
- **Referenced Questions:** `[Q-TEST-01]` (Coverage Threshold & CI Automation).
- **Tasks & Acceptance Criteria:**
  1. Create `.github/workflows/backend-ci.yml` running `ruff check`, `mypy`, and `pytest --cov --cov-fail-under=XX`.
  2. Create `.github/workflows/flutter-ci.yml` running `flutter analyze` and `flutter test`.
  3. Verify PRs cannot be merged if tests fail or code coverage drops below the required threshold.
- **TDD Test Spec:** CI pipeline executes both test suites cleanly against pull request branches.

---

## Epoch 1: Identity, Authentication & Security Baseline

### [EP1-TK01] User Domain Model & Password Hashing
- **Summary:** Implement the core User domain entity, role definitions (Patient, Practitioner, Admin), and secure credential hashing utilities.
- **Referenced Questions:** `[Q-AUTH-01]` (Identity Provider), `[Q-AUTH-02]` (User Roles).
- **Tasks & Acceptance Criteria:**
  1. Write failing unit tests for User entity validation (email format, role assignment, password strength).
  2. Implement password hashing using bcrypt or Argon2id.
  3. Implement domain entities with role-based permission checks (e.g., `user.can_read_patient(patient_id)`).
- **TDD Test Spec:** Unit tests verify invalid emails are rejected, passwords cannot be stored in plaintext, and role permissions correctly allow or deny access.

---

### [EP1-TK02] Authentication & Token Issuance Service
- **Summary:** Implement authentication service issuing signed JWT access and refresh tokens, or integrating with the chosen IAM provider.
- **Referenced Questions:** `[Q-AUTH-01]` (Cognito vs. Custom vs. External OIDC).
- **Tasks & Acceptance Criteria:**
  1. Write unit tests for token generation, signature validation, expiration checking, and revocation.
  2. Implement token creation with standard claims (`sub`, `role`, `exp`, `iss`) matching SMART on FHIR conventions.
  3. Implement dependency injection fixture to mock authentication in test suites.
- **TDD Test Spec:** Expired or tampered tokens return 401 Unauthorized; valid tokens decrypt to expected user claims.

---

### [EP1-TK03] HIPAA Audit Logging Interceptor
- **Summary:** Implement automated audit logging recording every access, mutation, or export of Protected Health Information (PHI).
- **Referenced Questions:** `[Q-AUTH-01]` (Audit context and storage).
- **Tasks & Acceptance Criteria:**
  1. Write tests ensuring that calling a PHI data method emits an audit event with timestamp, user ID, client IP, action type (READ/WRITE), and target resource ID.
  2. Ensure sensitive data (passwords, encryption keys, raw clinical notes) are never logged in plaintext audit logs.
- **TDD Test Spec:** `test_patient_read_generates_audit_event()` verifies audit trail entries are created for every simulated query.

---

## Epoch 2: FHIR Domain Modeling & NoSQL Storage Engine

### [EP2-TK01] FHIR R4 Domain Models & Validation
- **Summary:** Implement strict domain models for core FHIR resources (`Patient`, `Observation`, `Condition`, `Encounter`) with standard HL7 FHIR validation.
- **Referenced Questions:** `[Q-BACKEND-01]` (Pydantic models in FastAPI vs. Flask), `[Q-FHIR-01]` (FHIR Release & Resource Scope).
- **Tasks & Acceptance Criteria:**
  1. Write unit tests verifying valid FHIR R4 JSON documents deserialize correctly into domain models.
  2. Write unit tests ensuring invalid FHIR payloads (missing `status`, invalid LOINC code format, missing `subject`) raise validation errors with detailed issue paths.
  3. Implement models with serialization to/from standard FHIR JSON.
- **TDD Test Spec:** `pytest tests/unit/test_fhir_models.py` validates compliance against official HL7 sample fixtures.

---

### [EP2-TK02] Abstract Repository Ports & In-Memory Test Fixture
- **Summary:** Define abstract repository interfaces (`IPatientRepository`, `IObservationRepository`) following Clean Architecture, and build an in-memory implementation for rapid testing.
- **Referenced Questions:** `[Q-DATA-01]` (NoSQL Storage Strategy).
- **Tasks & Acceptance Criteria:**
  1. Define abstract base classes (`IPatientRepository`) specifying CRUD operations: `save()`, `get_by_id()`, `search()`.
  2. Implement `InMemoryPatientRepository` for unit test suites.
  3. Write a shared contract test suite (`test_patient_repository_contract.py`) that all concrete database adapters must satisfy.
- **TDD Test Spec:** All repository contract tests pass identically against the in-memory test double.

---

### [EP2-TK03] AWS NoSQL Database Persistence Adapter
- **Summary:** Implement the concrete database adapter for the selected AWS NoSQL option (DocumentDB, DynamoDB, or AWS HealthLake).
- **Referenced Questions:** `[Q-DATA-01]` (Primary Storage Choice), `[Q-DATA-02]` (Multi-Tenancy).
- **Tasks & Acceptance Criteria:**
  1. Implement the adapter satisfying the repository port interface.
  2. Ensure indexes for efficient querying by patient ID, observation date, and code are defined.
  3. Run the shared repository contract tests against a local test container or local mock.
- **TDD Test Spec:** Contract tests pass with zero schema discrepancies between domain models and database records.

---

### [EP2-TK04] FHIR Search Query Engine & Pagination
- **Summary:** Implement search filtering according to the FHIR REST specification (e.g., `GET /Observation?patient=123&code=http://loinc.org|8867-4&date=ge2026-01-01`).
- **Referenced Questions:** `[Q-DATA-01]`, `[Q-FHIR-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write unit tests parsing FHIR search parameter strings into database query criteria.
  2. Implement pagination support with FHIR `Bundle` return type (containing `link: next`, `total`, `entry`).
- **TDD Test Spec:** Multi-criteria search tests verify accurate filtering and cursor-based pagination.

---

## Epoch 3: Web API & SMART on FHIR Interoperability

### [EP3-TK01] REST API Routing & Endpoint Layer
- **Summary:** Build the web API routes for FHIR resource CRUD operations using the selected Python web framework.
- **Referenced Questions:** `[Q-BACKEND-01]` (FastAPI vs. Flask).
- **Tasks & Acceptance Criteria:**
  1. Write API integration tests using `httpx` or `TestClient` verifying HTTP status codes: `200 OK`, `201 Created` (with `Location` header), `400 Bad Request`, `404 Not Found`.
  2. Implement endpoints:
     - `POST /fhir/Patient` & `GET /fhir/Patient/{id}`
     - `POST /fhir/Observation` & `GET /fhir/Observation?patient={id}`
  3. Wire authentication middleware to protect endpoints.
- **TDD Test Spec:** Full HTTP request/response test suite executing across all core FHIR endpoints.

---

### [EP3-TK02] SMART on FHIR CapabilityStatement (`/metadata`)
- **Summary:** Expose the FHIR `CapabilityStatement` endpoint describing server capabilities, supported FHIR resources, and SMART on FHIR OAuth URIs.
- **Referenced Questions:** `[Q-FHIR-01]`, `[Q-FHIR-02]`.
- **Tasks & Acceptance Criteria:**
  1. Write tests asserting `GET /fhir/metadata` returns `Content-Type: application/fhir+json` with valid `CapabilityStatement` resource.
  2. Ensure the response includes the `rest.security.extension` declaring SMART on FHIR authorization and token endpoints (`.well-known/smart-configuration`).
- **TDD Test Spec:** Automated schema validation test against the HL7 CapabilityStatement schema.

---

### [EP3-TK03] SMART on FHIR Scope-Based Authorization Guard
- **Summary:** Implement fine-grained scope verification for SMART on FHIR scopes (e.g., `patient/Observation.read`, `patient/*.write`).
- **Referenced Questions:** `[Q-FHIR-02]` (Launch Requirements).
- **Tasks & Acceptance Criteria:**
  1. Write tests simulating requests with insufficient scopes (e.g., token has `patient/Patient.read` but requests `Observation`), asserting `403 Forbidden`.
  2. Implement scope-checking decorator/middleware that validates user context and patient compartment rules.
- **TDD Test Spec:** Matrix of test scenarios verifying valid scopes pass and unauthorized scopes fail.

---

## Epoch 4: Flutter Cross-Platform Client Application

### [EP4-TK01] Flutter State Management & API Client Setup
- **Summary:** Implement the core networking layer in Flutter with authentication interceptors and state management (Riverpod/BLoC).
- **Referenced Questions:** `[Q-FLUTTER-01]`, `[Q-FLUTTER-02]` (State Management).
- **Tasks & Acceptance Criteria:**
  1. Write unit tests for API client testing token injection, base URL handling, and timeout policies using mock HTTP adapter.
  2. Configure state management providers/controllers for user session and patient state.
- **TDD Test Spec:** Unit tests verify API client correctly attaches `Authorization: Bearer <token>` and handles 401 token refreshes.

---

### [EP4-TK02] Secure Token Storage & Authentication Flow (Flutter)
- **Summary:** Build the login screen, token reception, and secure storage on mobile/web using `flutter_secure_storage`.
- **Referenced Questions:** `[Q-AUTH-01]`, `[Q-FLUTTER-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write widget tests for the Login Screen (`testWidgets`): test email and password input fields, validation errors on invalid input, and submit button behavior.
  2. Mock the authentication service to test successful login and failed login error messages.
  3. Ensure tokens are written to secure hardware storage (Keychain/KeyStore).
- **TDD Test Spec:** Widget tests verify all UI states (idle, loading spinner, error snackbar, navigation to home screen on success).

---

### [EP4-TK03] Patient Vitals & Observation Dashboard UI
- **Summary:** Develop the dashboard displaying patient medical history, vital signs (heart rate, blood pressure, glucose), and lab observations.
- **Referenced Questions:** `[Q-FLUTTER-01]`, `[Q-FHIR-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write widget tests rendering patient card and vitals summary list with mock FHIR observation data.
  2. Verify that empty state, loading state, and error state widgets render appropriately.
  3. Implement responsive layout compatible with mobile and web screen widths.
- **TDD Test Spec:** Widget tests verify values (e.g. "120/80 mmHg", "98.6 °F") render accurately from FHIR Observation inputs.

---

### [EP4-TK04] Clinical Observation Data Entry Form
- **Summary:** Build the form allowing users/practitioners to log new clinical measurements (vitals, symptoms) with client-side FHIR validation.
- **Referenced Questions:** `[Q-FLUTTER-01]`, `[Q-FHIR-01]`.
- **Tasks & Acceptance Criteria:**
  1. Write widget tests simulating typing systolic/diastolic blood pressure, pulse, or body temperature.
  2. Assert client-side validation catches out-of-range or non-numeric entries before submission.
  3. Verify successful submission triggers API POST and refreshes local state.
- **TDD Test Spec:** `testWidgets` verifies button remains disabled while fields are invalid, and emits expected JSON payload upon submit.

---

## Epoch 5: Data Processing & Machine Learning Pipeline

### [EP5-TK01] Medical Data Transformation & De-Identification Engine
- **Summary:** Implement data extraction and anonymization routines to prepare FHIR observation data for machine learning processing.
- **Referenced Questions:** `[Q-ML-01]` (ML Scope), `[Q-AUTH-01]` (HIPAA Safe Harbor).
- **Tasks & Acceptance Criteria:**
  1. Write unit tests ensuring direct identifiers (names, addresses, phone numbers, exact birthdates) are stripped or hashed.
  2. Implement data transformation pipeline aggregating longitudinal observations into tabular feature arrays (e.g., Pandas / Polars DataFrames).
- **TDD Test Spec:** Unit tests assert output dataset contains zero HIPAA 18 direct identifiers and verifies schema matches ML feature requirements.

---

### [EP5-TK02] ML Inference Service & Model Wrapper
- **Summary:** Implement model loading, feature preprocessing, and prediction generation behind a clean domain service interface.
- **Referenced Questions:** `[Q-ML-01]`, `[Q-ML-02]` (ML Hosting & Inference Strategy).
- **Tasks & Acceptance Criteria:**
  1. Write unit tests with synthetic feature inputs validating inference output structure (e.g., risk probability between 0.0 and 1.0, prediction class).
  2. Implement model runner with graceful fallback and error handling if input values are out of bounds or missing.
- **TDD Test Spec:** `test_model_inference_returns_valid_prediction()` passes in under 100ms.

---

### [EP5-TK03] ML Prediction API & Patient Insights Integration
- **Summary:** Connect the ML inference service to an authenticated API endpoint and display risk scores / analytical insights in the Flutter UI.
- **Referenced Questions:** `[Q-BACKEND-01]`, `[Q-ML-02]`.
- **Tasks & Acceptance Criteria:**
  1. Implement backend endpoint `GET /fhir/Patient/{id}/$insights` returning ML predictions packaged as standard FHIR `RiskAssessment` resources.
  2. Create Flutter widget displaying the risk score or analytical trend.
  3. Write corresponding pytest API tests and Flutter widget tests.
- **TDD Test Spec:** API test verifies `RiskAssessment` resource structure and Flutter widget test verifies visual display of insight metrics.

---

## Epoch 6: End-to-End Integration, Auditing & Hardening

### [EP6-TK01] Full Backend E2E Integration Test Suite
- **Summary:** Construct end-to-end integration test scenarios simulating a complete user journey through all backend layers.
- **Referenced Questions:** `[Q-TEST-01]` (Code Coverage & CI).
- **Tasks & Acceptance Criteria:**
  1. Scenario: Register user -> Authenticate -> Ingest Patient -> Ingest Observations -> Execute Search -> Generate ML Insight -> Verify Audit Trail.
  2. Execute with zero mocks on domain and data persistence layers.
- **TDD Test Spec:** Pytest E2E test runs successfully and confirms all state transitions and audit logs are recorded.

---

### [EP6-TK02] Flutter Integration Test Suite (`integration_test`)
- **Summary:** Implement end-to-end automated UI integration tests running on a real simulator/emulator or browser.
- **Referenced Questions:** `[Q-FLUTTER-01]`, `[Q-TEST-01]`.
- **Tasks & Acceptance Criteria:**
  1. Configure Flutter `integration_test` runner.
  2. Automate user journey: Launch App -> Input Login -> View Patient Vitals -> Enter New Observation -> Verify Dashboard Updates.
- **TDD Test Spec:** `flutter test integration_test/app_test.dart` passes completely.

---

### [EP6-TK03] HIPAA Compliance & Security Audit Verification
- **Summary:** Execute comprehensive security verification covering encryption at rest, TLS settings, OWASP vulnerabilities, and secret scanning.
- **Referenced Questions:** `[Q-AUTH-01]`, `[Q-DATA-01]`.
- **Tasks & Acceptance Criteria:**
  1. Run automated dependency vulnerability scanner (e.g., `pip-audit`, `safety`).
  2. Verify all database connections enforce TLS/SSL and encrypted-at-rest volumes.
  3. Confirm every endpoint handling PHI produces compliant audit records.
- **TDD Test Spec:** Automated security checklist verification test passes with zero high/critical vulnerabilities.
