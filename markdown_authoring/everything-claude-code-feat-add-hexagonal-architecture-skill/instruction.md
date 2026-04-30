# feat: add hexagonal architecture SKILL.

Source: [affaan-m/everything-claude-code#1034](https://github.com/affaan-m/everything-claude-code/pull/1034)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/hexagonal-architecture/SKILL.md`

## What to add / change

## 🚀 Add Hexagonal Architecture Skill

### 📌 Overview
This PR introduces a new skill: **Hexagonal Architecture (Ports & Adapters)**.

The goal of this skill is to guide AI agents in designing and refactoring systems using a clean, maintainable, and testable architecture pattern that decouples business logic from infrastructure concerns.

---

### 🎯 Why this is useful
Hexagonal Architecture is widely used in modern backend systems to:
- Improve separation of concerns
- Enable easier testing (domain without infrastructure)
- Reduce coupling to frameworks (Spring, DBs, external APIs)
- Support long-term maintainability and scalability

This aligns well with the repository’s focus on **high-quality engineering patterns and reusable workflows**.

---

### 🧠 What this skill provides
The skill helps agents:

- Identify core **domain logic vs infrastructure**
- Define **ports (interfaces)** and **adapters (implementations)**
- Refactor tightly coupled code into modular layers
- Enforce clean boundaries between:
  - Domain
  - Application
  - Infrastructure

---

### ⚙️ Capabilities
- Analyze existing codebases for architectural issues
- Suggest hexagonal refactoring strategies
- Generate boilerplate structure for:
  - Ports (interfaces)
  - Adapters (DB, messaging, REST)
- Guide testability improvements (mocking ports)

---

### 💡 Example use cases
- Refactoring legacy Spring Boot applications
- Designing microservices with clear boundarie

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
