# AGENTS.md (Codex “operational contract”)

## Goal
Make it cheap for any fresh Codex session to:
1) understand how to validate changes
2) run the correct commands
3) avoid repo-specific footguns

Keep this file short. No status updates here.

## Build & Run (edit these once per project)
- Install (recommended: venv):
  - `python -m venv .venv`
  - Windows: `.venv\Scripts\activate`
  - macOS/Linux: `source .venv/bin/activate`
  - `python -m pip install -U pip`
  - Minimal required: `python -m pip install numpy`
  - Recommended for demo: `python -m pip install pygame matplotlib`
  - Optional speed: `python -m pip install numba`

- Dev run:
  - `python microverse.py`
  - Repro run: `python microverse.py --seed 123`
  - Headless regression: `python microverse.py --selftest --seed 123 --steps 300`

## Validation (the backpressure)
Run these after every change. Prefer fast + deterministic.
- Syntax check (fast):
  - `python -m py_compile microverse.py`

- Headless deterministic check (fast-ish):
  - `python microverse.py --selftest --seed 123 --steps 300`
  - Expectation: exits 0 and prints a stable digest line (e.g. `DIGEST=...`)

- Unit tests (fast):
  - (none yet) When added: `python -m unittest -q`

- Full tests (CI-like):
  - Same as selftest but longer: `python microverse.py --selftest --seed 123 --steps 3000`

- Typecheck:
  - (optional) `python -m pip install mypy`
  - `python -m mypy microverse.py`

- Lint/format:
  - (optional) `python -m pip install ruff`
  - `python -m ruff check .`
  - `python -m ruff format .`

If unsure which commands exist, discover them (README, pyproject.toml) then update this file.

## Git workflow (default)
- One Ralph iteration = one focused commit.
- Commit message format:
  - `feat(prd-XX): …` or `fix(prd-XX): …` or `chore: …`
- Always include updates to: PRD.md / IMPLEMENTATION_PLAN.md / progress.md when relevant.

## Safety rails
- Do NOT touch secrets, tokens, SSH keys, or any `.env` not required.
- Do NOT run destructive commands (`rm -rf`, `git reset --hard`, mass deletes) unless explicitly asked.
- Prefer minimal diffs. No drive-by refactors unless required to pass validation.
