# Sample Flutter Todo & Account App — Architecture & Planning

This sub-project provides a hands-on learning application to familiarize yourself with **Flutter** (for cross-platform frontend), **FastAPI** (for backend REST APIs), and **NoSQL ODM** data modeling, while building practical intuition for **HL7 FHIR Task concepts**, **machine learning endpoints**, and **AWS cloud architecture**.

---

## Purpose of this Sub-Project

- **Familiarize with Flutter:** Learn Flutter widget composition, state management, gesture handling, and the headless `flutter_test` framework from the ground up.
- **FastAPI + NoSQL ODM:** Practice async document persistence with ODMs like **Beanie** (Pydantic v2 + Motor) over MongoDB / Amazon DocumentDB.
- **FHIR Principles Compatibility:** Structure tasks and todos following the official HL7 FHIR `Task` and `Goal` resource paradigms (`status`, `intent`, `priority`, `executionPeriod`).
- **Machine Learning Integration:** Expose bulk NDJSON export endpoints and an NLP smart priority suggestion endpoint (`/api/v1/ml/predict-priority`).
- **AWS Cloud Readiness:** Design containers ready for AWS App Runner / ECS Fargate, DocumentDB, and S3 + CloudFront.

---

## Planning Documents

Please review the planning documents located in [`docs/`](docs/):

1. **[`docs/01_ARCHITECTURE_AND_QUESTIONS.md`](docs/01_ARCHITECTURE_AND_QUESTIONS.md)**
   - **ODM Evaluation:** In-depth comparison of **Beanie** vs. **ODMantic** vs. **Raw Motor + Pydantic** vs. **PynamoDB**.
   - **FHIR Task Alignment:** How the Todo schema maps to official FHIR `Task` fields.
   - **ML Accessibility:** Specification for bulk export and real-time inference endpoints.
   - **Flutter UI/UX Design:** Material 3 styling, swipe-to-complete gestures, and optimistic UI updates.
   - **Structured Questions:** Questions with IDs (e.g., `[Q-SAMPLE-ODM-01]`, `[Q-SAMPLE-AUTH-01]`) formatted with `Devin:` and placeholder `S:` prompts.

2. **[`docs/02_DEVELOPMENT_PLAN.md`](docs/02_DEVELOPMENT_PLAN.md)**
   - **TDD Guide for Beginners:** Unit testing with `pytest` and widget testing with `flutter_test` (using `WidgetTester` without an emulator).
   - **Folder Structure:** Modular separation of backend (`models`, `schemas`, `services`, `api`) and frontend (`models`, `services`, `controllers`, `views`, `widgets`).
   - **Local Commands:** How to run, test, and develop both services locally.

3. **[`docs/03_EPOCHS_AND_TICKETS.md`](docs/03_EPOCHS_AND_TICKETS.md)**
   - **Development Tickets across 7 Epochs:**
     - **Epoch 0:** Tooling, Scaffolding & TDD Baseline (`[SMP-EP0-TK01]` to `[SMP-EP0-TK03]`)
     - **Epoch 1:** Accounts & Authentication Flow (`[SMP-EP1-TK01]` to `[SMP-EP1-TK04]`)
     - **Epoch 2:** Todo Data Model (FHIR-aligned) & Persistence (`[SMP-EP2-TK01]` to `[SMP-EP2-TK03]`)
     - **Epoch 3:** REST API & ML-Accessible Endpoints (`[SMP-EP3-TK01]` to `[SMP-EP3-TK03]`)
     - **Epoch 4:** Flutter UI/UX & State Management (`[SMP-EP4-TK01]` to `[SMP-EP4-TK04]`)
     - **Epoch 5:** ML Feature Integration (`[SMP-EP5-TK01]` to `[SMP-EP5-TK02]`)
     - **Epoch 6:** End-to-End Testing & Deployment Packaging (`[SMP-EP6-TK01]` to `[SMP-EP6-TK03]`)
   - Every ticket includes concrete acceptance criteria, TDD test specifications, and links to the open questions.

---

## Next Steps

Review [`sample_flutter_app/docs/01_ARCHITECTURE_AND_QUESTIONS.md`](docs/01_ARCHITECTURE_AND_QUESTIONS.md), add your answers under the **`S:`** placeholders, and we can proceed with scaffolding **Epoch 0**!
