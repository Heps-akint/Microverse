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
- [ ] Passes

Acceptance criteria:
- Side panel shows live plots (population timeseries at minimum).
- Shows at least one map view (heatmap for moisture or plant cover).
- “Event detection” highlights at least: extinction, population crash, regime shift.

---

## PRD-08: Explainability + counterfactual re-sim
- [ ] Passes

Acceptance criteria:
- System outputs a short causal story when an event is detected (heuristic is fine).
- A counterfactual rerun can be triggered (change one parameter) and reports whether the event persists.

---

## PRD-09: Export still + HTML report (no external assets)
- [ ] Passes

Acceptance criteria:
- Keypress exports a high-res still PNG.
- Keypress exports an HTML report containing plots + key events + seed + parameters.
