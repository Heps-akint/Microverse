# IMPLEMENTATION_PLAN

Purpose: the “how-next”. Disposable. Rewritten by planning mode whenever it drifts.

Rules:
- Each task references one PRD ID.
- One build iteration completes ONE task.
- Tasks must be small enough to fit in a single Codex session.

---

## Now (highest priority first)

- None. All PRD items are complete; add new tasks here when scope expands.

---

## Done

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

4) [x] TASK-PRD-02-A: Camera flight + time controls + HUD
   - PRD: PRD-02
   - What to change: Add camera movement controls, pause/1x/2x/4x/8x time scaling, and HUD text for seed/sim time/dt/fps.
   - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`; `python microverse.py --seed 123`
   - Completion definition: Camera moves as expected; HUD shows required fields; time controls update sim speed.

5) [x] TASK-PRD-04-A: Day/night lighting + sky/water cues
   - PRD: PRD-04
   - What to change: Add sun angle over time, sky color gradient by sun elevation, and water/land shading differences.
   - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`
   - Completion definition: Lighting visibly shifts with time and water reflects brighter than land.

6) [x] TASK-PRD-05-A: Climate fields + deterministic update loop
   - PRD: PRD-05
   - What to change: Add moisture/temperature/rainfall fields and update rules (rainfall, evaporation, plant consumption).
   - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`
   - Completion definition: Climate fields evolve deterministically from seed across steps.

7) [x] TASK-PRD-06-A: Plants + herbivores (energy budget)
   - PRD: PRD-06
   - What to change: Implement plant growth and herbivore agents with energy gain/loss, reproduction, and death.
   - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`
   - Completion definition: Herbivore counts change over time based on plant availability.

8) [x] TASK-PRD-06-B: Predators + population dynamics
   - PRD: PRD-06
   - What to change: Add predator agents that seek herbivores and integrate with population metrics.
   - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`
   - Completion definition: Predator/herbivore populations show non-trivial dynamics for some seeds.

9) [x] TASK-PRD-05-B: River/flow accumulation approximation
   - PRD: PRD-05
   - What to change: Add a deterministic flow/accumulation pass from height + rainfall, derive a river mask, and feed it into moisture updates or rendering.
   - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`
   - Completion definition: A river/flow field is deterministic from seed and used in sim/rendering with stable selftest digest.

10) [x] TASK-PRD-07-A: Dashboard panel + population timeseries plot
   - PRD: PRD-07
   - What to change: Add a right-side dashboard panel in pygame and render a scrolling timeseries plot for plants/herbivores/predators.
   - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`
   - Completion definition: The panel renders and the timeseries plot updates live during simulation.

11) [x] TASK-PRD-07-B: Heatmap view + event highlight UI
   - PRD: PRD-07
   - What to change: Render a moisture or plant-biomass heatmap in the dashboard and show event highlight badges for extinction/crash/regime shift.
   - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`
   - Completion definition: Heatmap updates live and at least one event highlight can trigger for some seeds.

12) [x] TASK-PRD-08-A: Causal story text for detected events
   - PRD: PRD-08
   - What to change: Generate a short causal story when an event is detected and surface it in the HUD or log.
   - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`
   - Completion definition: A deterministic causal story appears for detected events.

13) [x] TASK-PRD-08-B: Counterfactual rerun comparison
   - PRD: PRD-08
   - What to change: Trigger a rerun with a single parameter perturbation (e.g., rainfall scale) and report whether the event persists.
   - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`
   - Completion definition: Counterfactual run completes deterministically and reports persistence in UI/log.

14) [x] TASK-PRD-09-A: Export still PNG
   - PRD: PRD-09
   - What to change: Add a keybinding to save the current frame as a high-res PNG (no external assets).
   - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`
   - Completion definition: Keypress writes a PNG with a deterministic filename and expected content.

15) [x] TASK-PRD-09-B1: Capture report-ready data (events + history)
   - PRD: PRD-09
   - What to change: Track an append-only event log (label, detail, tick/time, story) plus snapshot the existing population history so exports have stable inputs.
   - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`
   - Completion definition: Export data structures are populated deterministically during windowed runs.

16) [x] TASK-PRD-09-B2: Build HTML report writer with embedded plots
   - PRD: PRD-09
   - What to change: Add a report builder that renders plots (timeseries + heatmap) via matplotlib, embeds them as base64 in HTML, and includes seed/parameters + event log.
   - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`
   - Completion definition: A standalone function writes an HTML report from captured data.

17) [x] TASK-PRD-09-B3: Add HTML export keybinding + deterministic filename
   - PRD: PRD-09
   - What to change: Bind a keypress to invoke the report writer, pick a deterministic filename (seed + tick), and log the export path.
   - Required validation: `python -m py_compile microverse.py`; `python microverse.py --selftest --seed 123 --steps 300`
   - Completion definition: Keypress writes an HTML report with embedded plots and event summary.
