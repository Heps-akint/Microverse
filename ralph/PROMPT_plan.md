You are running ONE Ralph PLANNING iteration.

Inputs (must read first):
- AGENTS.md (how to validate + repo rules)
- PRD.md (the “what”)
- specs/* (detailed requirements by topic)
- IMPLEMENTATION_PLAN.md (may exist and may be wrong)
- progress.md (what was tried before)

Task:
1) Compare PRD/specs against the current codebase.
2) Produce/refresh IMPLEMENTATION_PLAN.md as a prioritized list of SMALL tasks.
3) Each task must:
   - reference exactly one PRD ID
   - be doable in one session
   - state required validation commands (from AGENTS.md)

Constraints:
- PLAN ONLY. Do not implement code changes (except editing docs: IMPLEMENTATION_PLAN.md, and if needed specs/* clarifications).
- Do not tick PRD items in PRD.md during planning.
- If specs are missing for a PRD item, create a new specs/<topic>.md file only if necessary, but keep it short and testable.

Output requirements:
- Update IMPLEMENTATION_PLAN.md.
- Append a short entry to progress.md describing what changed in the plan and why.
- If you changed any docs, make a git commit containing only doc changes with message: `chore(plan): update implementation plan`.
