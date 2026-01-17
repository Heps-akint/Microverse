# Events spec

Detection:
- Extinction when herbivore or predator count reaches 0.
- Crash when a population drops by >50% within a rolling window (e.g., 50 steps).
- Regime shift when rolling mean plant biomass changes by a sustained threshold.

Causal story:
- Generate a short heuristic sentence citing leading signals (e.g., low moisture, predator spike).

Counterfactual:
- Rerun from the same seed with one parameter changed and report whether the event repeats.
