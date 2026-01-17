# Simulation spec

Rule: deterministic from seed.
State fields (grid):
- height, water_mask, moisture, temperature, rainfall, plant_biomass
Time:
- dt-scaled updates with fixed-step option in --selftest

MVP climate:
- rainfall adds moisture
- evaporation removes moisture (depends on temperature)
- plants consume moisture
- rivers approximated via flow accumulation from height + rainfall
