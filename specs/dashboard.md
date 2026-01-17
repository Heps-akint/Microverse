# Dashboard spec

Layout:
- Right-side panel (~25% width) with a fixed background so the world view stays readable.
- Panel sections: timeseries plot, heatmap preview, recent events list.

Timeseries:
- Track rolling samples for plant biomass mean, herbivore count, predator count.
- Plot updates each sim step; keep last N samples (e.g., 300).

Heatmap:
- Render a small grid preview for moisture or plant biomass.
- Palette should be deterministic and legible against the panel background.

Event highlights:
- Show badges for extinction (population hits 0), crash (drop > X% over a window), regime shift (rolling mean changes by threshold).
