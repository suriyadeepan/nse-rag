- Always read `.current` to establish the active feature and its authoritative requirements, plan, TODO, and journal;

- Do not read from or write to these directories: ./docs/user/

- **Architecture:** Respect established architecture and compatibility constraints. Record new decisions and deviations in the approved plan.

- **Branch/docs:** One feature branch at a time. Keep all feature documents in `docs/`:
  - `docs/00x-<feature>-requirements.md` — Canonical feature requirements.
  - `docs/00x-<feature>-plan.md` — Implementation plan.
  - `docs/00x-<feature>-todo.md` — Canonical task/status source.
  - `docs/00x-<feature>.md` — Durable implementation journal: decisions, facts, changes, failures, configuration and evidence.
  - `docs/tutorial-00x-<feature>.md` — User-facing tutorial; create on request or completion. Append, never overwrite.

- **Project state:** Never duplicate task status across documents. Keep plan/TODO aligned. Journal implementation history, not task status.

- **Testing:** Maintain unit, integration and deployment smoke tests. Track implementation, automated testing and real-world verification separately. Use prescribed environments (`uv` for Python). Convert repeatable manual checks/fixes into regression tests. Record commands, results and evidence in the journal. Never claim unverified success.

- **Git:** Inspect `git status` before each top-level TODO, not nested items. If dirty, inspect and ask how to proceed. Never silently carry, overwrite or discard changes. Stage only task-related files; review staged diffs and run `git diff --cached --check`. Auto-commit only when TODO items are completed, only after all relevant tests and verification pass.

- **Efficiency:** Minimize tokens/tool calls. Read only relevant files. Keep responses concise.
