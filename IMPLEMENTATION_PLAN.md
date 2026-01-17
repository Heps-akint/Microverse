# IMPLEMENTATION_PLAN

Purpose: the “how-next”. Disposable. Rewritten by planning mode whenever it drifts.

Rules:
- Each task references one PRD ID.
- One build iteration completes ONE task.
- Tasks must be small enough to fit in a single Codex session.

---

## Now (highest priority first)

1) [x] TASK-PRD-01-A: Bootstrap `microverse.py` CLI + deterministic selftest digest
   - PRD: PRD-01
   - What to change: Create `microverse.py` with argparse, seed handling, deterministic RNG, fixed-step loop, and `--selftest` mode that prints `DIGEST=...`.
   - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`
   - Completion definition: `microverse.py` runs in selftest and exits 0 with a stable digest for seed 123.

2) [x] TASK-PRD-01-B: Windowed run path + deterministic world stub
   - PRD: PRD-01
   - What to change: Add pygame window loop that renders a deterministic placeholder world from the seed; log the digest on startup.
   - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`; `python microverse.py --seed 123`
   - Completion definition: Running with `--seed 123` opens a window and shows the same world across runs.

3) [x] TASK-PRD-03-A: Deterministic heightmap + biome color fields
   - PRD: PRD-03
   - What to change: Implement height/temperature/rainfall fields and biome color mapping (no assets) and wire them into rendering.
   - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`
   - Completion definition: Terrain and biome colors are deterministic from seed and visible in the renderer.

4) [ ] TASK-PRD-02-A: Camera flight + time controls + HUD
   - PRD: PRD-02
   - What to change: Add camera movement controls, pause/1x/2x/4x/8x time scaling, and HUD text for seed/sim time/dt/fps.
   - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`; `python microverse.py --seed 123`
   - Completion definition: Camera moves as expected; HUD shows required fields; time controls update sim speed.

5) [ ] TASK-PRD-04-A: Day/night lighting + sky/water cues
   - PRD: PRD-04
   - What to change: Add sun angle over time, sky color gradient by sun elevation, and water/land shading differences.
   - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`
   - Completion definition: Lighting visibly shifts with time and water reflects brighter than land.

6) [ ] TASK-PRD-05-A: Climate fields + deterministic update loop
   - PRD: PRD-05
   - What to change: Add moisture/temperature/rainfall fields and update rules (rainfall, evaporation, plant consumption).
   - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`
   - Completion definition: Climate fields evolve deterministically from seed across steps.

7) [ ] TASK-PRD-06-A: Plants + herbivores (energy budget)
   - PRD: PRD-06
   - What to change: Implement plant growth and herbivore agents with energy gain/loss, reproduction, and death.
   - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`
   - Completion definition: Herbivore counts change over time based on plant availability.

8) [ ] TASK-PRD-06-B: Predators + population dynamics
   - PRD: PRD-06
   - What to change: Add predator agents that seek herbivores and integrate with population metrics.
   - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`
   - Completion definition: Predator/herbivore populations show non-trivial dynamics for some seeds.

---

## Later / parking lot
- [ ] TASK-PRD-07-A: In-app dashboard (plots + heatmap + event highlights)
  - PRD: PRD-07
  - What to change: Add side panel with population timeseries plot, moisture/plant heatmap, and event highlight UI.
  - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`
  - Completion definition: Dashboard renders in-app and updates live during simulation.

- [ ] TASK-PRD-08-A: Event detection + causal story + counterfactual rerun
  - PRD: PRD-08
  - What to change: Detect extinction/crash/regime shift, generate a short text explanation, and run a parameter-perturbed rerun to compare outcomes.
  - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`
  - Completion definition: Events trigger a short causal story and a counterfactual result summary.

- [ ] TASK-PRD-09-A: Export still PNG + HTML report
  - PRD: PRD-09
  - What to change: Add keybindings to save PNG still and HTML report with embedded plots and key events.
  - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`
  - Completion definition: Keypresses create the PNG and HTML report without external assets.
