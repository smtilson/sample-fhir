# System Architecture & Planning Questions

This document outlines the architectural dimensions, technology options, tradeoffs, and open decision points for the electronic medical records (EMR/EHR) system.

Each decision point contains a structured question formulated by **Devin**, followed by a placeholder for your answer (**S:**). Please review each section and fill in your response below each question.

---

## Table of Contents
1. [Backend Framework: FastAPI vs. Flask](#1-backend-framework-fastapi-vs-flask)
2. [NoSQL Database & FHIR Storage on AWS](#2-nosql-database--fhir-storage-on-aws)
3. [FHIR Standard & SMART on FHIR Specification](#3-fhir-standard--smart-on-fhir-specification)
4. [Identity, Authentication & HIPAA Compliance](#4-identity-authentication--hipaa-compliance)
5. [Machine Learning Pipeline & Analytics](#5-machine-learning-pipeline--analytics)
6. [Frontend (Flutter) Architecture](#6-frontend-flutter-architecture)
7. [Testing & Quality Assurance Strategy](#7-testing--quality-assurance-strategy)

---

## 1. Backend Framework: FastAPI vs. Flask

You specifically asked: **"Would Flask also be an option alongside FastAPI?"**

### Comparative Analysis

| Feature | FastAPI | Flask |
| :--- | :--- | :--- |
| **Data Validation & Typing** | Built on **Pydantic v2**. Enforces strict Python type hints at runtime. Auto-serializes and validates deeply nested JSON (crucial for complex FHIR JSON resources). | Requires external libraries (e.g., Marshmallow, Pydantic). Manual schema validation wiring. |
| **API Documentation** | Auto-generates interactive **OpenAPI (Swagger)** and ReDoc documentation out of the box based on type annotations. | Requires extensions (`flask-swagger-ui`, `apispec`, or `flask-restx`). |
| **Async / Concurrency** | Native `async`/`await` support on ASGI (Uvicorn). Excellent for concurrent API calls, async DB drivers (Motor, aioboto3), and streaming responses. | Traditionally WSGI (synchronous). Flask 2.0+ added basic async support, but the ecosystem and middleware remain largely WSGI-centric. |
| **Machine Learning Serving** | Very popular in modern ML serving (compatible with HuggingFace, PyTorch, ONNX runtime; low overhead serialization). | Long-standing industry standard for simple ML model serving, but heavier serialization overhead without Pydantic. |
| **Ecosystem & Simplicity** | Minimalist microframework with modern defaults; steeper learning curve if unfamiliar with async/type hints. | Extremely mature, vast ecosystem of older extensions, simple for beginners, but requires stitching together many libraries for a large enterprise system. |

#### [Q-BACKEND-01] Framework Selection
**Devin:** Given that FHIR resources require rigorous schema validation (hundreds of deeply nested JSON fields) and your plan involves machine learning APIs and high test coverage:
- Would you prefer **FastAPI** (for native Pydantic schema validation, OpenAPI generation, and async performance)?
- Or do you want to consider **Flask** (simpler traditional WSGI structure, but requiring extra manual configuration for validation and docs)?
- Or would you prefer to evaluate a hybrid/microservice setup (e.g., FastAPI for FHIR/ML APIs, and Flask/serverless for lightweight tasks)?

**S:** 

---

## 2. NoSQL Database & FHIR Storage on AWS

Medical data adhering to FHIR (Fast Healthcare Interoperability Resources) is represented as hierarchical, nested JSON documents (e.g., `Patient`, `Observation`, `Encounter`, `Condition`).

### AWS NoSQL Database Candidates

1. **Amazon DocumentDB (with MongoDB compatibility)**
   - *Pros:* Native JSON/BSON document store. Highly intuitive mapping from FHIR JSON resources directly to collections. Supports rich aggregation pipelines and indexing on arbitrary nested keys (e.g., `code.coding.system`, `subject.reference`).
   - *Cons:* Provisioned cluster model (always-on compute instances, higher baseline cost than purely serverless).
2. **Amazon DynamoDB (Key-Value / Document Store)**
   - *Pros:* Fully serverless, pay-per-request, single-digit millisecond latency, automated scaling, zero instance management.
   - *Cons:* Limited document size (400 KB max item limit). Querying arbitrary nested fields requires careful partition/sort key design (Single-Table Design) or secondary indexes (GSIs). Complex FHIR searches (e.g., searching observations by date range + patient ID + LOINC code) often require DynamoDB Streams feeding into Amazon OpenSearch Service.
3. **AWS HealthLake (Managed FHIR Store)**
   - *Pros:* Purpose-built, HIPAA-eligible AWS service designed specifically for FHIR R4. Automatically validates FHIR resources, provides built-in FHIR search query endpoints (`GET /Observation?patient=...&code=...`), and exports integrated data directly to S3 in Parquet/JSON format for AWS SageMaker / ML pipelines.
   - *Cons:* Proprietary managed API with specific pricing structure; less customizable if non-standard data schemas are required.
4. **Hybrid / Custom FHIR Engine (e.g., DocumentDB + OpenSearch)**
   - *Pros:* Maximum flexibility for custom indexes, full-text clinical notes search, and tailored aggregations.
   - *Cons:* Higher development and operational maintenance overhead.

#### [Q-DATA-01] Primary Data Store Choice
**Devin:** How do you want to approach the database backend on AWS?
- **Option A:** Fully managed FHIR service via **AWS HealthLake** (fastest compliance, built-in FHIR R4 APIs and ML export, less custom backend code needed).
- **Option B:** **Amazon DocumentDB** (MongoDB compatible JSON document store; full control over custom schemas, aggregations, and indexes).
- **Option C:** **Amazon DynamoDB** (Serverless, low cost at low volumes; requires specialized indexing patterns or DynamoDB + OpenSearch for multi-field FHIR queries).
- **Option D:** Undecided / Start with an abstract repository interface tested locally against MongoDB or in-memory fixtures, deferring the AWS provider choice.

**S:** 

#### [Q-DATA-02] Data Isolation & Multi-Tenancy
**Devin:** Will this system serve multiple organizations/clinics (multi-tenant) or a single organization/user base? If multi-tenant, should data be partitioned logically (tenant ID column/field) or physically (separate database/collection per tenant) for compliance?

**S:** 

---

## 3. FHIR Standard & SMART on FHIR Specification

### Overview
- **FHIR (Fast Healthcare Interoperability Resources):** Standard by HL7 defining data models for healthcare concepts (Patient, Observation, DiagnosticReport, etc.). FHIR Release 4 (R4) is the US federal standard (ONC rule).
- **SMART on FHIR:** An open standards framework that extends OAuth 2.0 and OpenID Connect (OIDC) to allow applications to securely authenticate and launch either standalone or within an Electronic Health Record (EHR) system (like Epic or Cerner).

### Key Architectural Considerations
1. **SMART Launch Modes:**
   - *Standalone Launch:* The user opens the Flutter mobile/web app, logs into the app's authorization server, and obtains access tokens.
   - *EHR Launch:* A doctor or clinician launches your app from inside an EHR portal (e.g., Epic App Orchard), passing a `launch` token and patient context.
2. **Scopes:** Fine-grained access permissions defined by SMART (e.g., `patient/Patient.read`, `patient/Observation.read`, `user/*.*`).
3. **CapabilityStatement (`/metadata`):** FHIR servers publish a statement describing which resources and search interactions they support.

#### [Q-FHIR-01] FHIR Standard Version & Resource Scope
**Devin:**
- Which version of FHIR do you wish to target? (FHIR R4 is strongly recommended as the industry standard).
- What core resources will your initial application require? (e.g., `Patient`, `Observation` [vitals, lab results], `Condition`, `MedicationRequest`, `DocumentReference` [clinical notes])?

**S:** 

#### [Q-FHIR-02] SMART on FHIR Launch Requirements
**Devin:**
- Do you require **EHR Launch** integration (allowing clinical staff to launch your app directly from an existing hospital EHR like Epic/Cerner)?
- Or do you only need **Standalone Launch** (independent patient/user app with standard OAuth2 / OIDC credentials)?
- Or both?

**S:** 

---

## 4. Identity, Authentication & HIPAA Compliance

### Security Requirements for Protected Health Information (PHI)
Under HIPAA:
- **Encryption at Rest:** AES-256 for all stored medical records (AWS KMS).
- **Encryption in Transit:** TLS 1.3 enforced for all network connections.
- **Audit Logging:** Every Read, Create, Update, and Delete of PHI must be logged with timestamp, user identity, IP address, and resource ID.
- **Authentication & RBAC:** Multi-factor authentication (MFA) recommended; role-based access control (e.g., Patient, Clinician, Admin).

### Auth Provider Options
1. **Amazon Cognito User Pools:** Fully managed on AWS, supports MFA, OAuth 2.0 / OIDC tokens, fine-grained IAM integration.
2. **Third-Party Auth Provider (e.g., Auth0, Keycloak, Firebase Auth):** Rich OIDC feature set, pre-built SMART on FHIR templates (especially Keycloak/Auth0).
3. **Custom FastAPI Auth Engine (JWT + PyJWT + Passlib):** Complete control, but requires manual implementation of OAuth2 password flows, MFA, and refresh token rotation.

#### [Q-AUTH-01] Identity & Access Management Provider
**Devin:** Which authentication strategy would you like to use for user accounts?
- **Option A:** **Amazon Cognito** (native AWS integration, HIPAA-eligible).
- **Option B:** **Custom Auth Service** built in FastAPI using OAuth2/JWT standards.
- **Option C:** **External Managed OIDC Provider** (e.g., Auth0, Keycloak).

**S:** 

#### [Q-AUTH-02] User Roles & Self-Registration
**Devin:** Who are the primary end users of the application?
- Patients self-registering and viewing/logging their own data?
- Healthcare providers/clinicians managing multiple patients?
- Both (requiring strict role-based access control and patient-clinician linkage)?

**S:** 

---

## 5. Machine Learning Pipeline & Analytics

### ML Architecture Components
1. **Data Ingestion & De-Identification:** Medical data must be scrubbed of direct identifiers (HIPAA Safe Harbor 18 identifiers) before training or export unless running on HIPAA-compliant infrastructure under a Business Associate Agreement (BAA).
2. **Data Pipeline:**
   - *Batch Processing:* Periodic ETL jobs extracting FHIR observations into training datasets (e.g., Pandas, Polars, Parquet files in S3).
   - *Streaming / Real-time Inference:* When new data is submitted (e.g., new glucose readings or vitals), the backend runs inference immediately.
3. **Execution Environment:**
   - *Embedded in Backend:* Lightweight models (Scikit-Learn, XGBoost, ONNX Runtime) loaded directly in memory in the FastAPI process.
   - *Asynchronous Worker:* Celery + Redis or AWS SQS + AWS Lambda / ECS task for long-running computations.
   - *AWS SageMaker Endpoint:* Dedicated managed inference endpoint for larger neural networks or deep learning models.

#### [Q-ML-01] Scope & Nature of Machine Learning Models
**Devin:** What kind of machine learning tasks do you anticipate performing on the medical data?
- Predictive analytics (e.g., risk scoring, anomaly detection on vital signs)?
- Natural Language Processing (e.g., clinical note summarization, medical terminology extraction)?
- Time-series forecasting (e.g., glucose levels, heart rate variability)?
- Real-time inference (instant response to the user) vs. asynchronous/batch insights?

**S:** 

#### [Q-ML-02] ML Hosting & Inference Strategy
**Devin:** Where should model inference run initially?
- Directly within the Python backend API (simplest for MVP, fast local development)?
- In an asynchronous task queue / worker (Celery/SQS) to prevent blocking HTTP requests?
- On AWS SageMaker or dedicated serverless containers?

**S:** 

---

## 6. Frontend (Flutter) Architecture

### Why Flutter?
Flutter delivers high-performance native binaries for iOS, Android, Web, and Desktop from a single Dart codebase.

### Key Architectural Choices for Flutter Beginners
1. **State Management Pattern:**
   - **Riverpod:** Modern, compile-safe, testable, no dependency on the `BuildContext`. Excellent for beginners and advanced apps alike.
   - **BLoC (Business Logic Component):** Event-driven, rigid separation of presentation and business logic, standard in enterprise apps, highly testable.
   - **Provider:** Older, simple standard, but being largely superseded by Riverpod.
2. **Local Storage & Offline Sync:**
   - `flutter_secure_storage`: Stores sensitive tokens (OAuth refresh tokens, encryption keys) in the platform KeyStore/Keychain.
   - `drift` (SQLite) or `hive` / `isar` (NoSQL): For local caching of FHIR records on device.
3. **Networking & FHIR Client:**
   - `dio` or `http`: Modern HTTP client with interceptors for attaching OAuth Bearer tokens, token refresh, and retry logic.
   - FHIR Dart packages: Existing open-source Dart libraries (`fhir`, `fhir_at_rest`) parse and serialize FHIR resources with full type safety.

#### [Q-FLUTTER-01] Target Platforms
**Devin:** Which platforms should we prioritize for the Flutter application first?
- Mobile (iOS & Android)?
- Web (Browser-based dashboard)?
- Both mobile and web simultaneously?

**S:** 

#### [Q-FLUTTER-02] State Management Preference
**Devin:** Since you mentioned you are new to Flutter, would you like us to adopt **Riverpod** (widely regarded as the cleanest, most test-friendly state management tool for Flutter today), or **BLoC** (strict event/state architecture)?

**S:** 

---

## 7. Testing & Quality Assurance Strategy

You requested a **test-driven development (TDD)** approach with deep test coverage across both Python (`pytest`) and Flutter.

### Testing Stack

| Layer | Python Backend Stack | Flutter Frontend Stack |
| :--- | :--- | :--- |
| **Unit Tests** | `pytest`, `pytest-cov`, `pytest-mock` | `flutter_test` (built into Flutter SDK) |
| **Data Validation Tests** | Pydantic model validation tests, FHIR schema conformance tests | Dart unit tests, JSON serialization tests (`fhir` package) |
| **API / Endpoint Tests** | `httpx.AsyncClient` or FastAPI `TestClient`, simulated database fixtures | Mock HTTP clients (`mocktail` / `http_mock_adapter`) |
| **UI / Widget Tests** | N/A | `testWidgets` in `flutter_test` (renders widgets in headless tester) |
| **End-to-End (E2E)** | Automated pytest integration scenarios against local test container DB | `integration_test` package (runs on real simulator/emulator/browser) |

#### [Q-TEST-01] Code Coverage & CI/CD Expectations
**Devin:** What minimum test coverage percentage target would you like to set for both backend and frontend codebases (e.g., 85% or 90%)? Should pull requests automatically enforce this via GitHub Actions?

**S:** 

---

## Summary of Open Question Index

To track answers easily and cross-reference them in the development tickets, the question identifiers are:
- `[Q-BACKEND-01]`: Web Framework Selection (FastAPI vs. Flask)
- `[Q-DATA-01]`: Primary AWS NoSQL Data Store / FHIR Storage (HealthLake vs. DocumentDB vs. DynamoDB vs. Abstracted)
- `[Q-DATA-02]`: Multi-Tenancy and Data Isolation
- `[Q-FHIR-01]`: FHIR Release & Resource Scope
- `[Q-FHIR-02]`: SMART on FHIR Launch Context (Standalone vs. EHR Launch)
- `[Q-AUTH-01]`: Identity Provider (Cognito vs. Custom vs. External OIDC)
- `[Q-AUTH-02]`: User Roles & Registration Workflows
- `[Q-ML-01]`: Machine Learning Model Scope & Tasks
- `[Q-ML-02]`: ML Hosting & Inference Pipeline
- `[Q-FLUTTER-01]`: Flutter Target Platforms (Mobile vs. Web)
- `[Q-FLUTTER-02]`: Flutter State Management Choice
- `[Q-TEST-01]`: Test Coverage Threshold & CI Automation
