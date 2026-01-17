You are running ONE Ralph BUILD iteration.

Inputs (must read first):
- AGENTS.md
- PRD.md
- specs/*
- IMPLEMENTATION_PLAN.md
- progress.md

Task:
1) Select the single highest-priority unchecked task in IMPLEMENTATION_PLAN.md.
2) Before changing anything, search the codebase to confirm what exists. Do not assume missing.
3) Implement only what is needed to complete that one task.
4) Run the required validation commands (from AGENTS.md and the task’s “Required validation”).
5) Update state:
   - Mark the task as done in IMPLEMENTATION_PLAN.md
   - If the PRD item is now fully satisfied, tick its checkbox in PRD.md
   - Append an entry to progress.md (what you did, what you ran, results, what’s next)

Constraints:
- ONE task only.
- If you find unrelated bugs, either fix ONLY if they block validation, otherwise add a new task to IMPLEMENTATION_PLAN.md.
- No placeholders. If you can’t finish, leave clear next steps and exact errors in progress.md.

Git:
- `git add -A`
- Commit message must reference the PRD ID, e.g. `feat(prd-01): ...` or `fix(prd-01): ...`
- Push the current branch if a remote exists.
