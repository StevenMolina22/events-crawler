# 🤖 Agent Guide

---

## 1️⃣ Core Operating Principles

✅ **Awareness First**

* Always **read** `.agents/PLANNING.md` before starting work.
* Use `.agents/CONTEXT.md` to understand current state. **Read-only.**
* Check `.agents/TASKS.md` before starting; if task not listed, add it with date and brief.
* Adhere to `.agents/RULES.md` for **all coding constraints**.

✅ **Codebase Discussion and Planning Mode**

* If the query involves discussing the codebase (e.g., analyzing structure, explaining components) or planning a feature (e.g., proposing designs, outlining requirements), **do not generate or modify code**.
* Provide analysis, explanations, or plans in text form only, referencing `.agents/PLANNING.md` or `.agents/CONTEXT.md` as needed.
* If the query explicitly requests code implementation or modification (writing mode), confirm with the user before proceeding, especially if the request seems ambiguous.

✅ **Strict Focus**

* **Work only on the requested task.**
* Log unrelated issues under “Discovered During Work” in `.agents/TASKS.md`.
* Do not “fix extra things” unless blocking the current task.

✅ **No Assumptions**

* If missing context, **ask before coding**.
* Confirm file paths and module names exist before referencing.
* Never delete or overwrite existing code unless explicitly instructed.

✅ **Plan, then Code**

* For complex tasks, **submit a plan and wait for approval before coding**.
* Analyze options; don’t rush into implementation.

---

## 2️⃣ Workflow

### 🛠️ Task Lifecycle

1. **Read `.agents/PLANNING.md`** → vision, architecture, style.
2. **Read `.agents/CONTEXT.md`** → current state.
3. **Read `.agents/RULES.md`** → constraints, standards.
4. **Check `.agents/TASKS.md`** → confirm/add task.
5. **Plan** → submit if complex.
6. **Code** → follow constraints and architecture.
7. **Test** → assert correctness.
8. **Document** → update `.agents/TASKS.md`, `README.md` as needed.
9. **Submit** → mark task complete.

---

## 3️⃣ Code & Structure Rules

✅ **Modularity**

* Max 500 LOC per file; refactor if approaching.
* Split by feature/responsibility.
* Use consistent, clear relative imports.

✅ **Modern Standards**

* Python:

  * Use Python 3.13+ type hints.
  * Use `uv` for Python management (`uv run ...`).
  * Prefer `assert` for simple tests, `pytest` for suites.
* Node:

  * Use `pnpm` unless project requires another.
  * Prefer TypeScript and ES modules.
* React:

  * Use function components only.

✅ **Dependency Hygiene**

* Add dependencies **only if essential** for the task.

✅ **Secrets**

* Use environment variables, never hard-coded keys.

---

## 4️⃣ Quality & Traceability

✅ Update:

* `.agents/TASKS.md` upon task completion or discovering new tasks/bugs.
* `README.md` on feature, dependency, or setup changes.
* `.agents/` folder **always in sync with the codebase.**

✅ Testing:

* Write tests or assertions to confirm correctness.
* Never assume correctness without explicit verification.

✅ Documentation:

* For complex logic, use inline:

  ```python
  # Reason: why this logic is necessary
  ```
* Keep explanations high signal, low noise.

---

## 5️⃣ File Responsibilities

| File                  | Purpose                                                |
| --------------------- | ------------------------------------------------------ |
| `.agents/PLANNING.md` | Project vision, architecture, style                    |
| `.agents/RULES.md`    | Coding standards, constraints, quality gates           |
| `.agents/TASKS.md`    | Task tracking (in progress, done, discovered)          |
| `.agents/CONTEXT.md`  | Current state, dependencies, structure (**read-only**) |

---

## 6️⃣ Key Reminders

✅ **Consistency** with `.agents/PLANNING.md`
✅ **Compliance** with `.agents/RULES.md`
✅ **Traceability** via `.agents/TASKS.md`
✅ **Awareness** via `.agents/CONTEXT.md`

✅ **No assumptions, no shortcuts, no scope creep.**

If uncertain: **ask.**

---
