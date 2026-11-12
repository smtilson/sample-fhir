# FHIR Healthcare Application — Planning & Architecture

Welcome to the planning phase of the FHIR healthcare system.

This project is organized as a test-driven, cross-platform healthcare application featuring a **Python backend** (with machine learning capabilities) and a **Flutter cross-platform client**, compliant with HL7 FHIR standards and designed for AWS cloud deployment.

---

## Planning Documents Guide

Please review the following planning documents located in the [`docs/`](docs/) directory:

1. **[`docs/01_ARCHITECTURE_AND_QUESTIONS.md`](docs/01_ARCHITECTURE_AND_QUESTIONS.md)**
   - **Architectural Tradeoffs:** Framework evaluations (FastAPI vs. Flask), AWS NoSQL options (DocumentDB, DynamoDB, AWS HealthLake), SMART on FHIR specifications, Authentication & HIPAA compliance, Machine Learning pipelines, and Flutter client architecture.
   - **Planning Questions:** Structured decision points formatted as:
     ```markdown
     #### [Q-BACKEND-01] Framework Selection
     Devin: ...
     S: <Your answer here>
     ```
   - **Action Item:** Review each section and enter your decisions or preferences under the `S:` lines.

2. **[`docs/02_DEVELOPMENT_PLAN.md`](docs/02_DEVELOPMENT_PLAN.md)**
   - **Test-Driven Development (TDD) Strategy:** Complete setup guide for Python (`pytest`, `pytest-cov`, `pytest-mock`, fixtures) and Flutter (`flutter_test` unit tests, widget tests, and integration tests).
   - **Hexagonal Architecture:** How decoupling domain logic from databases and frameworks keeps the system technology-agnostic until choices are locked in.
   - **Testing Pyramid for Flutter Beginners:** Explains how widget tests run headlessly in memory without an emulator.

3. **[`docs/03_EPOCHS_AND_TICKETS.md`](docs/03_EPOCHS_AND_TICKETS.md)**
   - **Development Tickets across Epochs:**
     - **Epoch 0:** Foundation, Environment Setup & TDD Infrastructure
     - **Epoch 1:** Identity, Authentication & Security Baseline (HIPAA)
     - **Epoch 2:** FHIR Domain Modeling & NoSQL Storage Engine
     - **Epoch 3:** Web API & SMART on FHIR Interoperability Layer
     - **Epoch 4:** Flutter Cross-Platform Client Application
     - **Epoch 5:** Data Processing & Machine Learning Pipeline
     - **Epoch 6:** End-to-End Integration, Security Auditing & Release Readiness
   - Every ticket outlines concrete acceptance criteria, TDD test specifications, and cross-references to the open questions in `01_ARCHITECTURE_AND_QUESTIONS.md`.

---

## Hands-On Learning Sub-Project: Sample Flutter App

To get familiar with Flutter and test-driven development before building the full healthcare platform, see the standalone sample project:

👉 **[`sample_flutter_app/`](sample_flutter_app/)**
- **Architecture & Questions:** [`sample_flutter_app/docs/01_ARCHITECTURE_AND_QUESTIONS.md`](sample_flutter_app/docs/01_ARCHITECTURE_AND_QUESTIONS.md) (ODM options such as Beanie, FHIR Task alignment, ML endpoints).
- **Development Plan & TDD:** [`sample_flutter_app/docs/02_DEVELOPMENT_PLAN.md`](sample_flutter_app/docs/02_DEVELOPMENT_PLAN.md) (FastAPI + Beanie TDD and Flutter beginner testing guide).
- **Epochs & Tickets:** [`sample_flutter_app/docs/03_EPOCHS_AND_TICKETS.md`](sample_flutter_app/docs/03_EPOCHS_AND_TICKETS.md) (Tickets across Epochs 0 through 6).

