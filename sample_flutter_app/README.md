# Sample Flutter Todo & Account App — Architecture & Planning

This sub-project provides a hands-on learning application to familiarize yourself with **Flutter** (for cross-platform frontend), **FastAPI** (for backend REST APIs), and **NoSQL ODM** data modeling, while building practical intuition for **HL7 FHIR Task concepts**, **machine learning endpoints**, and **AWS cloud architecture**.

---

## Purpose of this Sub-Project

- **Familiarize with Flutter:** Learn Flutter widget composition, state management, responsive UI, and the headless `flutter_test` framework starting with **Flutter Web (browser-first)**.
- **FastAPI + NoSQL ODM:** Practice async document persistence with **Beanie** (Pydantic v2 + Motor) over MongoDB locally and Amazon DocumentDB on AWS.
- **FHIR Principles Compatibility:** Incremental hybrid rollout starting with a clean Todo model, evolving into the official HL7 FHIR `Task` resource model (`status`, `intent`, `priority`, `executionPeriod`, FHIR R4 JSON export).
- **Machine Learning Integration:** Expose dedicated, secured bulk NDJSON/JSON data export endpoints (`/api/v1/ml/export/tasks`) for ML training platforms.
- **AWS Cloud Readiness:** Design containers ready for AWS App Runner / ECS Fargate, DocumentDB, and S3 + CloudFront.

---

## Planning Documents

Please review the planning documents located in [`docs/`](docs/):

1. **[`docs/01_ARCHITECTURE_AND_QUESTIONS.md`](docs/01_ARCHITECTURE_AND_QUESTIONS.md)**
   - **ODM Evaluation:** Comparison of Beanie vs. alternatives, with locked decision for Beanie + DocumentDB.
   - **FHIR Task Alignment:** Strategy for hybrid incremental rollout.
   - **ML Accessibility:** Specification for dedicated bulk export endpoints.
   - **Flutter UI/UX Design:** Material 3 styling, browser-first layout, and explicit controls (no swipe gestures).
   - **Questions & Responses:** All questions answered and decisions recorded.

2. **[`docs/02_DEVELOPMENT_PLAN.md`](docs/02_DEVELOPMENT_PLAN.md)**
   - **TDD Guide for Beginners:** Unit testing with `pytest` (executed via WSL) and widget testing with `flutter_test` (using `WidgetTester` without an emulator).
   - **Folder Structure:** Modular separation of backend (`models`, `schemas`, `services`, `api`) and frontend (`models`, `services`, `controllers`, `views`, `widgets`).
   - **Platform Rollout:** Phase 1: Browser (Flutter Web) -> Phase 2: Mobile -> Phase 3: Desktop.

3. **[`docs/03_EPOCHS_AND_TICKETS.md`](docs/03_EPOCHS_AND_TICKETS.md)**
   - **Development Tickets across 7 Epochs:**
     - **Epoch 0:** Tooling, Scaffolding & TDD Baseline (`[SMP-EP0-TK01]` to `[SMP-EP0-TK03]`)
     - **Epoch 1:** Accounts & Authentication Flow (`[SMP-EP1-TK01]` to `[SMP-EP1-TK04]`) — with `**Devin re-Cognito:**` parity notes
     - **Epoch 2:** Core Todo Domain & Persistence (Stage 1) (`[SMP-EP2-TK01]` to `[SMP-EP2-TK03]`)
     - **Epoch 3:** Incremental FHIR Task Evolution (Stage 2) (`[SMP-EP3-TK01]` to `[SMP-EP3-TK02]`)
     - **Epoch 4:** Flutter UI/UX — Phase 1: Browser (`[SMP-EP4-TK01]` to `[SMP-EP4-TK04]`)
     - **Epoch 5:** Machine Learning Bulk Data Export Layer (`[SMP-EP5-TK01]` to `[SMP-EP5-TK02]`)
     - **Epoch 6:** Multi-Platform Expansion & AWS Deployment (`[SMP-EP6-TK01]` to `[SMP-EP6-TK03]`)
   - Every ticket includes concrete acceptance criteria, TDD test specifications, and links to the open questions.

---

## Next Steps

Review [`sample_flutter_app/docs/01_ARCHITECTURE_AND_QUESTIONS.md`](docs/01_ARCHITECTURE_AND_QUESTIONS.md), add your answers under the **`S:`** placeholders, and we can proceed with scaffolding **Epoch 0**!
