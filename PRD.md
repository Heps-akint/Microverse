# PRD

Purpose: Microverse is a single Python program that generates a deterministic procedural world from a seed, renders it in real time, simulates simple ecology, and shows a live scientific dashboard plus exports.

---

## PRD-01: One-command runnable demo (seeded, deterministic)
- [x] Passes

Acceptance criteria:
- Running `python microverse.py` opens a window and shows a generated world.
- Running with `--seed 123` reproduces the same world (visually and via a deterministic hash in logs).
- There is a `--selftest` headless mode that runs N steps and prints a stable digest (for regression).

---

## PRD-02: Camera flight + time controls
- [x] Passes

Acceptance criteria:
- WASD + mouse (or arrows) moves camera; you can “fly”.
- Controls: pause, 1x, 2x, 4x, 8x time.
- HUD shows current seed, sim time, dt, fps.

---

## PRD-03: Procedural terrain + biomes (no assets)
- [x] Passes

Acceptance criteria:
- Terrain heightmap generated from noise/fractal function.
- Biome map derived from (temperature, rainfall) fields.
- Colors/textures are functions (no image files).

---

## PRD-04: Day/night lighting + sky/water cues
- [x] Passes

Acceptance criteria:
- Sun direction changes over time and affects shading.
- Sky color changes with sun elevation.
- Water regions reflect light more than land (approximate is fine).

---

## PRD-05: Physics-lite climate loop (deterministic)
- [x] Passes

Acceptance criteria:
- Rainfall/evaporation/soil moisture fields evolve over time.
- Rivers are approximated (flow accumulation or simple erosion pass).
- All updates are deterministic from seed + parameters.

---

## PRD-06: Agent-based ecology (plants → herbivores → predators)
- [x] Passes

Acceptance criteria:
- Plants grow based on light + moisture.
- Herbivores seek plants; predators seek herbivores.
- Populations show non-trivial dynamics (oscillation/collapse) for some seeds.

---

## PRD-07: Live dashboard inside the app
- [x] Passes

Acceptance criteria:
- Side panel shows live plots (population timeseries at minimum).
- Shows at least one map view (heatmap for moisture or plant cover).
- “Event detection” highlights at least: extinction, population crash, regime shift.

---

## PRD-08: Explainability + counterfactual re-sim
- [x] Passes

Acceptance criteria:
- System outputs a short causal story when an event is detected (heuristic is fine).
- A counterfactual rerun can be triggered (change one parameter) and reports whether the event persists.

---

## PRD-09: Export still + HTML report (no external assets)
- [x] Passes

Acceptance criteria:
- Keypress exports a high-res still PNG.
- Keypress exports an HTML report containing plots + key events + seed + parameters.

---

## PRD-10: Full 3D renderer (CPU) with sky, fog, and water cues
- [x] Passes

Acceptance criteria:
- 3D view is rendered with camera position, yaw, pitch, and altitude.
- Terrain is rendered in 3D with a horizon line; fog/atmosphere fades distant terrain.
- Water surfaces show a distinct shading/reflectance cue.
- A render-quality toggle exists (low/med/high) to target 30 FPS on low-end laptops.

---

## PRD-11: Runtime “laws” controls (sun angle, rainfall, temperature, gravity)
- [x] Passes

Acceptance criteria:
- Keybinds adjust sun angle offset, rainfall multiplier, temperature offset, and gravity.
- HUD displays the current values of these runtime “law” controls.
- Changes take effect immediately and deterministically in the simulation.

---

## PRD-12: Start empty, spawn ecology interactively
- [x] Passes

Acceptance criteria:
- On startup, there are zero herbivores and predators.
- Keybinds spawn herbivores and predators at runtime.
- A keybind clears all agents (reset populations without regenerating the world).

---

## PRD-13: Pure-Python video export
- [x] Passes

Acceptance criteria:
- A keybind starts/stops video capture.
- Video export uses pure-Python encoding with no external tools.
- Exported video filename is deterministic (includes seed and tick).

---

## PRD-14: Expanded analytics (energy flow + histograms)
- [ ] Fails

Acceptance criteria:
- Dashboard shows at least one energy-flow or consumption plot.
- Dashboard includes a histogram of plant biomass or moisture.
- HTML report includes the new analytics plots.

---

## PRD-15: Benchmark flyover mode
- [ ] Fails

Acceptance criteria:
- A CLI flag runs a deterministic 10-second flyover path.
- Benchmark outputs a report with timing stats and a short video clip.
- Benchmark is reproducible from a seed.

---

## PRD-16: Time machine (save, rewind, branch)
- [ ] Fails

Acceptance criteria:
- Simulation state can be saved periodically into a ring buffer.
- Keybinds jump backward and forward through saved states.
- Branching creates a new timeline from a past state without breaking determinism.

---

## PRD-17: Procedural soundtrack (optional)
- [ ] Fails

Acceptance criteria:
- Audio is generated procedurally from world state with no external assets.
- Sound can be toggled on/off at runtime.
- Audio generation does not break determinism of the simulation state.

---

## PRD-18: Photomode path-traced stills
- [ ] Fails

Acceptance criteria:
- A keybind renders a high-quality still using a slow path-traced mode.
- Output uses deterministic settings and includes seed/tick in filename.
- Photomode does not alter simulation state unless explicitly resumed.
