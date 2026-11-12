# Sample App Architecture & Planning Questions

This document outlines the architecture, technology tradeoffs, and decision points for the **Sample Todo & Account Application**. 

The goal of this sub-project is to provide a hands-on environment to master Flutter, test-driven development (TDD), and FastAPI + NoSQL ODM patterns, while modeling data according to the principles of HL7 FHIR and preparing for AWS deployment and machine learning integrations.

Questions are formatted with a `Devin:` prompt, followed by a placeholder `S:` for your response.

---

## Table of Contents
1. [Backend ODM (Object Document Mapper) Options](#1-backend-odm-object-document-mapper-options)
2. [Data Model Alignment with FHIR Standards](#2-data-model-alignment-with-fhir-standards)
3. [Machine Learning Accessibility & Endpoints](#3-machine-learning-accessibility--endpoints)
4. [Authentication & User Accounts](#4-authentication--user-accounts)
5. [Flutter UI/UX Design Principles](#5-flutter-uiux-design-principles)
6. [AWS Platform Deployment Considerations](#6-aws-platform-deployment-considerations)

---

## 1. Backend ODM (Object Document Mapper) Options

You specifically asked: **"Basing it on some ODM (beanie? give me options)"**.

Because our backend is **FastAPI** (which natively relies on **Pydantic** for validation and serialization) and our database is a NoSQL document store (MongoDB or Amazon DocumentDB), an ODM maps Python classes directly to database documents.

### ODM Comparison Matrix

| Option | Architecture | Pydantic v2 Support | Async Native | Best Suited For |
| :--- | :--- | :--- | :--- | :--- |
| **1. Beanie** | Built directly on **Pydantic v2** and **Motor** (official async MongoDB driver). Models inherit from `beanie.Document`, which is a `pydantic.BaseModel`. | Native & Full | Yes (100% async) | **Recommended for FastAPI.** Zero boilerplate; document models are simultaneously your FastAPI request/response validation schemas. |
| **2. ODMantic** | Also bridges Pydantic with Motor. Focuses heavily on clean syntax, relations, and GraphQL-like queries. | Support for v2 in progress; historically slower to upgrade than Beanie. | Yes (async) | Good for small projects, but smaller community and slower release cycle than Beanie. |
| **3. MongoEngine** | The oldest and most mature MongoDB ODM in Python (modeled after Django ORM). | No native Pydantic integration (requires manual schema translation). | No (Synchronous / WSGI-oriented). | Legacy Flask/Django systems. Poor fit for modern async FastAPI. |
| **4. Raw Motor + Pydantic v2 (Repository Pattern)** | No ODM library; use official `motor.motor_asyncio` client with custom Pydantic models and repository classes. | Native | Yes | Maximum control and zero library abstraction magic. Requires writing CRUD helper methods manually. |
| **5. PynamoDB** | Pythonic ORM/ODM specifically for **Amazon DynamoDB** (rather than MongoDB/DocumentDB). | Requires separate Pydantic conversion layer. | Sync (or async via aioboto3 wrappers). | Use this if you choose Amazon DynamoDB instead of MongoDB/DocumentDB for the NoSQL layer. |

**S:** Is it the case that PynamoDB is necessary for working with AWS or is it possible to use beanie on AWS but just use a different database service?

**Devin:** No, PynamoDB is not necessary on AWS. Beanie communicates using the standard MongoDB wire protocol, which is fully supported on AWS by **Amazon DocumentDB** (AWS's native managed MongoDB-compatible document database) as well as **MongoDB Atlas on AWS**. You can use Beanie with zero code changes between local MongoDB and Amazon DocumentDB on AWS; only the connection string URI changes.

#### [Q-SAMPLE-ODM-01] ODM Selection
**Devin:** Would you like to proceed with **Beanie** as the primary ODM for this sample app?
- **Option A: Beanie** (Strongly recommended: natively unifies Pydantic v2 data validation, async Motor performance, and FastAPI schemas).
- **Option B: Raw Motor + Pydantic Repository** (No ODM dependency; manual repository methods).
- **Option C: PynamoDB** (If you prefer testing directly against Amazon DynamoDB instead of MongoDB/DocumentDB).

**S:** What is the upside of option C? I don't understand what DynamoDB offers that MongoDB/DocumentDB doesn't.

**Devin:** Here is the direct breakdown of what DynamoDB offers versus MongoDB / Amazon DocumentDB:
- **Upsides of DynamoDB (Option C):**
  1. *True Serverless Pay-per-Request:* If traffic drops to zero, your database bill is $0.00/month. By contrast, Amazon DocumentDB runs on dedicated compute instances with a minimum baseline cost of ~$50–$80/month unless stopped.
  2. *Stateless Connection Scaling:* DynamoDB communicates via HTTP requests without persistent TCP connection pools, making it seamless with serverless AWS Lambda invocations.
  3. *Predictable Latency:* Returns in single-digit milliseconds regardless of dataset size for primary key lookups.
- **Downsides of DynamoDB for this project:**
  1. *Rigid Query Patterns:* DynamoDB requires strict Single-Table Design with predefined Partition and Sort keys. You cannot flexibly query or aggregate deeply nested JSON fields without creating Global Secondary Indexes (GSIs) or syncing tables to OpenSearch.
  2. *400 KB Item Size Limit:* Deeply nested medical records can hit this limit.
  3. *PynamoDB vs. Beanie:* PynamoDB is mostly synchronous and lacks native Pydantic v2 validation.
- **Conclusion & Decision:** We will proceed with **Option A (Beanie)** over MongoDB locally and Amazon DocumentDB on AWS.

---

## 2. Data Model Alignment with FHIR Standards

While this is a "Todo" application to learn Flutter, designing the data model to mirror **HL7 FHIR** ensures the architectural patterns you learn here translate directly to the healthcare project.

### Mapping Todos to FHIR `Task` Resource
In the HL7 FHIR specification, tasks, action items, and workflows are represented by the **`Task`** resource:
- **`identifier`**: Unique system and business ID.
- **`status`**: State machine (`draft`, `requested`, `received`, `accepted`, `in-progress`, `completed`, `cancelled`, `failed`).
- **`intent`**: Why the task exists (`proposal`, `plan`, `order`).
- **`priority`**: Urgency level (`routine`, `urgent`, `asap`, `stat`).
- **`description`**: Human-readable title or summary of the task.
- **`note`**: Detailed text, checklist notes, or instructions.
- **`for` / `owner`**: Reference to the User or Patient (`User/123`).
- **`authoredOn`**: Creation timestamp.
- **`lastModified`**: Updated timestamp.
- **`executionPeriod`**: Start time and due date/completion timestamp.
- **`tags` / `category`**: Codes grouping tasks (e.g., `personal`, `clinical`, `medication`, `follow-up`).

#### [Q-SAMPLE-FHIR-01] Data Model Strictness
**Devin:** How closely should the sample Todo model mimic the FHIR `Task` resource?
- **Option A: Full FHIR Task JSON alignment:** The Todo schema uses exact FHIR R4 field names and enum codes (`status: in-progress`, `priority: urgent`, `executionPeriod`). This provides maximal familiarity with FHIR.
- **Option B: Simplified Todo schema with FHIR conceptual mapping:** Use standard consumer app fields (`title`, `description`, `is_completed`, `due_date`, `priority`) with an export converter that outputs valid FHIR R4 `Task` JSON.

**S:** I would like a hybrid approach. Create descriptive tickets so that the app can be tested while the full task isn't yet built out in all of the FHIR detail specified in Option A. So we should start with something smaller. Implement CRUD and tests. Implement the front end, and then gradually add in the FHIR details.

---

## 3. Machine Learning Accessibility & Endpoints

You requested: *"I want there to be easily accessible endpoints for some machine learning platform to access."*

An ML platform (e.g., AWS SageMaker, automated training pipelines, or a local Jupyter Notebook) needs two primary capabilities:
1. **Bulk Training Data Extraction:** Ability to pull structured, timestamped task activity data with filters (e.g., completed tasks, time-to-completion, priority labels).
2. **Real-time Inference / Suggestions:** Ability to send text or task parameters and receive ML-generated predictions.

### Proposed ML API Endpoints
- `GET /api/v1/ml/export/tasks`:
  - Query parameters: `from_date`, `to_date`, `status`, `include_anonymized_user_id`.
  - Format: JSON or NDJSON (Newline Delimited JSON, the standard format for ML and FHIR Bulk Data Access).
  - Returns: Clean tabular/vectorizable records (task length, description character count, priority, completion duration in seconds).
- `POST /api/v1/ml/predict-priority`:
  - Request: `{"title": "Schedule urgent follow-up with Dr. Smith"}`
  - Response: `{"suggested_priority": "urgent", "confidence": 0.94, "suggested_tags": ["appointment", "medical"]}`
- `POST /api/v1/ml/predict-completion-time`:
  - Request: `{"task_id": "...", "complexity": "..."}`
  - Response: `{"estimated_hours": 3.5, "suggested_due_date": "2026-11-15T18:00:00Z"}`

#### [Q-SAMPLE-ML-01] Initial ML Capability for Sample App
**Devin:** What ML functionality would you like to build first into the sample app?
- **Option A: Smart Task Prioritization & Tagging:** A lightweight NLP model (scikit-learn / HuggingFace) that reads the task description and automatically suggests the priority (`routine` vs. `urgent`) and category tags.
- **Option B: Completion Duration / Due Date Estimator:** A regression model that predicts how long a task will take based on historical completion logs.
- **Option C: ML-ready Data Export only:** Focus on clean, high-throughput bulk export endpoints and API keys, deferring actual model inference.

**S:** I do not want to build any ML capability into the app. I like the option of just doing clean ML data exports. Maybe those endpoints should be separate and eventually require authorization of some form.

---

## 4. Authentication & User Accounts

The sample app requires accounts so each user has their own private tasks and can experience the full Flutter authentication flow (login, register, token refresh, and persistent session).

### Architecture for Sample App
- **Password Security:** `passlib` with `bcrypt` or `argon2-cffi`.
- **Token Mechanism:** Stateless JSON Web Tokens (JWT) signed using HMAC-SHA256 (`PyJWT`).
- **Endpoints:**
  - `POST /api/v1/auth/register`: Create user account.
  - `POST /api/v1/auth/token`: OAuth2 password flow returning `{access_token, refresh_token, token_type: "bearer"}`.
  - `GET /api/v1/auth/me`: Get current logged-in user profile.
  - `POST /api/v1/auth/refresh`: Refresh expired access token.

#### [Q-SAMPLE-AUTH-01] Auth Architecture for Sample App
**Devin:** For the sample app, do you prefer a self-contained FastAPI JWT authentication system (fastest to set up, zero external cloud dependencies, fully testable with pytest), or do you want to connect directly to AWS Cognito from day one?
- **Option A: Self-contained FastAPI JWT** (Recommended for local learning and quick testing).
- **Option B: AWS Cognito User Pool** (Direct AWS cloud integration).

**S:** For this sample app, I want self contained. I do want you to make comments along the way referencing how this would work with Cognito. Sign those comments "**Devin re-Cognito:** [comment]".

#### [Q-SAMPLE-REORG-01] Streamlined Early Roadmap: Fast-Tracking Flutter UI & FastAPI Synchronization
**Devin:** To get to hands-on Flutter learning and frontend-backend synchronization as quickly as possible, should we reorganize the early roadmap to establish minimal accounts (name, email, password) and simple user-scoped tasks (name, completion status, metadata), moving Flutter UI and API sync immediately into Epoch 2 while deferring complex JWT token flows, FHIR lifecycle state machines, and ML exports to later epochs?
- **Option A: Full Auth & Deep Schema First** (Build complete OAuth2 password flow, JWT access/refresh tokens, and full task schema before starting Flutter).
- **Option B: Streamlined Account/Task & Fast-Track Flutter Sync** (Recommended: Simple user creation with bcrypt hash, simple user-scoped task model, immediately followed by Flutter UI and live API sync. Heavy auth and FHIR deferred to later epochs).

**S:** I want to change the development plan right now to get to understand flutter and syncing it with fastapi right now. So I want to reorganize things so that the most basic accounts are set up, don't worry about serious auth issues. just user creation, that model should just have a name, email, and password. then there should be a simple model for tasks with simply the name of the task, completion status, and metadata. I then want to pivot to having the flutter UI be able to display this. For password storage, use simple bcrypt hash; for task association, keep tasks scoped to user.

**Devin:** Understood. We have reorganized the roadmap accordingly:
1. **Epoch 1:** Minimal User model (`name`, `email`, bcrypt-hashed `password`) and simple user-scoped Task model (`user_id`, `name`, `is_completed`, `metadata`) with straightforward FastAPI CRUD endpoints.
2. **Epoch 2:** Flutter Frontend & FastAPI Sync (HTTP client, Task List UI with checkboxes, task creation form, and live sync).
3. **Subsequent Epochs:** Heavy auth (JWT/OAuth2/tokens), FHIR Task state machine evolution, ML bulk data export, and multi-platform deployment are preserved and deferred to Epochs 3 through 6.

---

## 5. Flutter UI/UX Design Principles

Since you are completely new to Flutter, creating an app that follows modern Flutter best practices and Material 3 design will give you strong architectural intuition.

### Key UI/UX Capabilities for the Todo App
1. **Design System:** Material 3 (`useMaterial3: true`), with dynamic color theming, responsive typography, and clean light/dark mode support.
2. **Interactive Patterns:**
   - **Dismissible Task Cards:** Swipe left to delete (with confirmation snackbar and undo action), swipe right to mark complete.
   - **Filter & Search Bar:** Filter chips (`All`, `Active`, `Completed`, `Urgent`) and quick search by task title.
   - **Bottom Sheet for Creation:** Floating Action Button (FAB) opens an ergonomic modal bottom sheet with keyboard auto-focus and priority selector chips.
   - **Optimistic UI Updates:** When the user taps complete, the UI instantly checks off the task, syncing with the FastAPI backend in the background. If the request fails, the UI rolls back and displays an error snackbar.
   - **Empty States & Skeletons:** Friendly illustrations or icons when the task list is empty, with skeleton loading shimmer while fetching records.

#### [Q-SAMPLE-UI-01] Flutter Client Form Factor
**Devin:** Would you like to run and test the Flutter sample app primarily as:
- **Option A: Flutter Desktop / Web** (Easiest to run and test immediately on your Windows machine in Chrome or native Windows app without needing an Android emulator/device).
- **Option B: Mobile (Android/iOS)** (Using Android Studio Emulator or physical device).
- **Option C: Both.**

**S:** I want to run and test on both Desktop and Mobile. Let's prioritize browser, then mobile, then desktop. Do this incrementally and reflect this in the ticket structure. I also do not want the swipe left and right gestures for task management.

---

## 6. AWS Platform Deployment Considerations

### Cloud Architecture for the Sample App
1. **Backend Container:** Dockerized FastAPI app deployed to **AWS App Runner** (fully managed container runner, auto-TLS, auto-scaling, very simple setup) or **AWS ECS Fargate**.
2. **Database:** **Amazon DocumentDB** (or a free MongoDB Atlas cluster hosted in AWS).
3. **Frontend:** Flutter Web build deployed to an **Amazon S3** static bucket accelerated by **Amazon CloudFront** CDN.
4. **Secrets:** Managed via AWS Systems Manager Parameter Store or environment variables.

#### [Q-SAMPLE-AWS-01] Local vs. Cloud Deployment Target
**Devin:** Do you want the sample app to initially run 100% locally via `docker-compose` (FastAPI + MongoDB/DocumentDB container + Flutter), with AWS deployment scripts prepared for when you are ready to push to AWS?

**S:** I want to be able to run and test the sample app locally via `docker-compose` and then deploy to be able to deploy to AWS if/when necessary.

---

## Question Summary & Final Decision Index

- `[Q-SAMPLE-ODM-01]`: **Resolved: Option A (Beanie)**. Uses Beanie + Motor over MongoDB locally and Amazon DocumentDB on AWS.
- `[Q-SAMPLE-FHIR-01]`: **Resolved: Hybrid Incremental Approach**. Start with a lightweight, testable Todo schema for fast CRUD & frontend progress, then incrementally add FHIR `Task` concepts and serialization across later tickets.
- `[Q-SAMPLE-ML-01]`: **Resolved: Clean ML Bulk Export Endpoints**. No ML models/NLP inside the app; build dedicated, authorized bulk data export endpoints (`/api/v1/ml/export/tasks`) returning structured NDJSON.
- `[Q-SAMPLE-AUTH-01]`: **Resolved: Self-contained FastAPI JWT**. Use self-contained JWT for local development and testing, accompanied by `**Devin re-Cognito:**` annotations in docs and tickets explaining the Cognito equivalent.
- `[Q-SAMPLE-REORG-01]`: **Resolved: Fast-Track Flutter UI & FastAPI Sync**. Streamline Epoch 1 to minimal accounts (`name`, `email`, bcrypt `password`) and simple user-scoped tasks (`name`, `is_completed`, `metadata`); move Flutter UI & API sync directly to Epoch 2; defer advanced auth, FHIR evolution, and ML export to later epochs.
- `[Q-SAMPLE-UI-01]`: **Resolved: Multi-Platform Phased Rollout (No Swipes)**. Phased priority: 1. Browser (Flutter Web) -> 2. Mobile (Android/iOS) -> 3. Desktop (Windows). No swipe gestures; use explicit checkboxes, action buttons, and confirmation dialogs.
- `[Q-SAMPLE-AWS-01]`: **Resolved: Local Docker-Compose First**. Local development and testing via `docker-compose`, with AWS deployment scripts (AWS App Runner / DocumentDB / S3) ready for cloud deployment when needed.
