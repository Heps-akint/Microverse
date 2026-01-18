# IMPLEMENTATION_PLAN

Purpose: the “how-next”. Disposable. Rewritten by planning mode whenever it drifts.

Rules:
- Each task references one PRD ID.
- One build iteration completes ONE task.
- Tasks must be small enough to fit in a single Codex session.

---

## Now (highest priority first)

- [x] TASK-PRD-10-A: 3D camera pose state + HUD display
  - PRD: PRD-10
  - What to change: Add camera altitude, yaw, and pitch state plus keybinds to adjust them; show the pose values in the HUD while keeping the 2D renderer unchanged.
  - Required validation: `python -m py_compile microverse.py`
  - Completion definition: Camera pose state updates deterministically via inputs and the HUD reflects yaw/pitch/alt values.

- [x] TASK-PRD-10-B: 2.5D heightmap renderer + 2D/3D toggle
  - PRD: PRD-10
  - What to change: Implement a column-cast 2.5D heightmap renderer driven by the camera pose and add a toggle key to switch between 2D and 3D views; include a clear horizon line.
  - Required validation: `python -m py_compile microverse.py`
  - Completion definition: 3D mode renders a terrain view using the camera pose with a visible horizon and a working 2D/3D toggle.

- [x] TASK-PRD-10-C: 2.5D fog + water reflectance cues
  - PRD: PRD-10
  - What to change: Add atmospheric fog fading and water reflectance shading cues to the 2.5D renderer.
  - Required validation: `python -m py_compile microverse.py`
  - Completion definition: Distant terrain fades with fog and water surfaces are visually distinct in 3D mode.

- [x] TASK-PRD-10-D: Render-quality presets + dynamic resolution scaling
  - PRD: PRD-10
  - What to change: Add low/med/high quality presets (step size, max distance, vertical resolution) and a dynamic resolution scaler targeting 30 FPS.
  - Required validation: `python -m py_compile microverse.py`
  - Completion definition: Users can switch quality presets and the renderer scales resolution when FPS drops.

- [x] TASK-PRD-11-A: Runtime “laws” state + keybinds + HUD display
  - PRD: PRD-11
  - What to change: Add runtime modifiers for sun angle offset, rainfall multiplier, temperature offset, and gravity; wire keybinds and HUD display without altering simulation behavior yet.
  - Required validation: `python -m py_compile microverse.py`
  - Completion definition: Runtime keys adjust parameters and the HUD reflects current values deterministically.

- [x] TASK-PRD-11-B: Apply runtime “laws” to sim + lighting
  - PRD: PRD-11
  - What to change: Apply the law modifiers in lighting (sun angle offset), climate updates (rainfall multiplier, temperature offset), and agent movement cost/energy (gravity) deterministically.
  - Required validation: `python -m py_compile microverse.py`
  - Completion definition: Simulation responds immediately and deterministically to runtime law changes.

- [ ] TASK-PRD-12-A: Empty-start ecology + interactive spawning/reset
  - PRD: PRD-12
  - What to change: Start with zero herbivores/predators and add keybinds to spawn herbivores/predators and clear all agents without regenerating the world.
  - Required validation: `python -m py_compile microverse.py`
  - Completion definition: Populations start at zero and can be spawned/cleared via keybinds.

- [ ] TASK-PRD-13-A: Pure-Python video capture (AVI, raw RGB)
  - PRD: PRD-13
  - What to change: Add a simple AVI writer using `struct` and uncompressed RGB frames, plus capture toggle keybinds and deterministic filenames.
  - Required validation: `python -m py_compile microverse.py`
  - Completion definition: A keybind starts/stops capture and writes a valid AVI video using pure-Python code.

- [ ] TASK-PRD-14-A: Energy flow tracking + dashboard plot
  - PRD: PRD-14
  - What to change: Track herbivore/predator energy gains/losses per tick and display a dashboard plot of energy flow.
  - Required validation: `python -m py_compile microverse.py`
  - Completion definition: Dashboard shows a live energy-flow plot.

- [ ] TASK-PRD-14-B: Histogram plot + HTML report integration
  - PRD: PRD-14
  - What to change: Add a histogram (plant biomass or moisture) to the dashboard and include it in the HTML report.
  - Required validation: `python -m py_compile microverse.py`
  - Completion definition: Dashboard and HTML report include the histogram plot.

- [ ] TASK-PRD-15-A: Deterministic benchmark flyover + timing stats
  - PRD: PRD-15
  - What to change: Add a `--benchmark` CLI flag that runs a fixed 10s camera flyover path and prints timing stats (frame time, avg FPS) deterministically.
  - Required validation: `python -m py_compile microverse.py`
  - Completion definition: Benchmark mode runs the deterministic path and reports timing stats.

- [ ] TASK-PRD-15-B: Benchmark video + report artifact
  - PRD: PRD-15
  - What to change: Reuse the video writer and HTML report generation to emit a short benchmark clip and a timing report file (seed + tick in name).
  - Required validation: `python -m py_compile microverse.py`
  - Completion definition: Benchmark mode outputs a deterministic report and video artifact.

- [ ] TASK-PRD-16-A: Time machine ring buffer + rewind/forward controls
  - PRD: PRD-16
  - What to change: Snapshot core simulation state into a ring buffer and add keybinds to jump backward/forward through saved states.
  - Required validation: `python -m py_compile microverse.py`
  - Completion definition: Users can rewind/advance through saved states deterministically.

- [ ] TASK-PRD-16-B: Time machine branching
  - PRD: PRD-16
  - What to change: Allow resuming from a past snapshot and create a new deterministic branch timeline without corrupting the buffer.
  - Required validation: `python -m py_compile microverse.py`
  - Completion definition: Branching creates a new timeline from a past state.

- [ ] TASK-PRD-17-A: Procedural soundtrack toggle
  - PRD: PRD-17
  - What to change: Generate synth audio from world state via the standard library `wave` module, with on/off toggle.
  - Required validation: `python -m py_compile microverse.py`
  - Completion definition: Audio can be toggled and is procedurally generated.

- [ ] TASK-PRD-18-A: Photomode path-traced still render
  - PRD: PRD-18
  - What to change: Add a slow photomode renderer that path-traces a still and saves a deterministic PNG.
  - Required validation: `python -m py_compile microverse.py`
  - Completion definition: Photomode generates a high-quality still without changing sim state.

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
