This file is a merged representation of the entire codebase, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
4. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

## Additional Info

# Directory Structure
```
.agents/
  AGENT.md
.gitignore
main.py
pyproject.toml
```

# Files

## File: .agents/AGENT.md
```markdown
# 🤖 Agent Guide

This document defines how an agent should operate within this project. **Follow these instructions strictly.**

---

### 🧭 Project Awareness & Context

- **Always read `.agents/PLANNING.md`** at the start of a new conversation to understand the project's architecture, goals, style, and constraints.
- **Check `.agents/TASKS.md`** before starting a new task. If the task isn’t listed, add it with a brief description and today's date.
- **Check `.agents/RULES.md`** for any rules the project has.
- **Check `.agents/CONTEXT.md`** for the context and files of the project.
- **NEVER modify the `.agents/CONTEXT.md`** file.
- **Use consistent naming conventions, file structure, and architecture patterns** as described in `.agents/PLANNING.md`.

---

### 🧱 Code Structure & Modularity

- **Never create a file longer than 500 lines of code.** If a file approaches this limit, refactor by splitting it into modules or helper files.
- **Organize code into clearly separated modules**, grouped by feature or responsibility.
- **Use clear, consistent imports** (prefer relative imports within packages).

---

### ✅ Task Completion

- **Mark completed tasks in `.agents/TASKS.md`** immediately after finishing them.
- **Add discovered bugs or sub-tasks** during development under “Discovered During Work” in `.agents/TASKS.md`.
- **Focus ONLY on the requested problem or feature**.
  - If unrelated issues are found, log them under “Discovered During Work.”
  - Do not fix unrelated issues unless they block the current task.

---

### 📚 Documentation & Explainability

- **Update `README.md`** when new features are added, dependencies change, or setup steps are modified.
- **Update `.agents/`** when new features are added, tasks are done or there is any relevant change on the codebase, **ALWAYS** make sure the `.agents/` folder is up to date with the codebase.
- **For complex logic, add inline `# Reason:` comment** explaining the why, not just the what.

---

### 🧠 AI Behavior Rules

- **Never assume missing context. Ask questions if uncertain.**
- **Always confirm file paths and module names** exist before referencing them in code.
- **Never delete or overwrite existing code** unless explicitly instructed to or if part of a task from `.agents/TASKS.md`.
- **Focus ONLY on the problem and prompt at hand** Do not build unrelated features.
- **ALWAYS plan before codign complex tasks** Wait for approval before proceeding with implementation.
- When planning, analyze options first — don’t implement until requested.
- Install new dependencies only if absolutely required by the task.
- If an error occurs during execution or installation, document the error in `.agents/TASKS.md` and propose a resolution before proceeding.
- Use environment variables over hard-coded keys.

---

### Coding Rules

- Always use modern type hints in python (3.13+).
- Always use `uv` as a python manager. Run libraries with `uv run ...`.
- For `python` testing use `assert` when enough or `pytes` when necessary.
- Use `pnpm` on node if possible, except if other package manager is being used.
- Always prefer typescript over javascript.
- Always prefer ES-modules in JS.
- Always use function components in `react`.

---

## ✔️ Summary

**Stick to these principles.**
Keep `.agents/` and the codebase in sync.
Communicate context, plan carefully, commit small, test everything.
If you’re unsure — ask.
No assumptions.
No shortcuts.

---
```

## File: .gitignore
```
# Python-generated files
__pycache__/
*.py[oc]
build/
dist/
wheels/
*.egg-info

# Virtual environments
.venv
```

## File: main.py
```python
def main():
    print("Hello from show-up-crawler!")


if __name__ == "__main__":
    main()
```

## File: pyproject.toml
```toml
[project]
name = "show-up-crawler"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "scrapy>=2.13.3",
]
```
