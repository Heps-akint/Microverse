#!/usr/bin/env python3
import argparse
import hashlib
import math
from typing import List, Optional, Tuple


MASK32 = 0xFFFFFFFF
DEFAULT_SCALE = 8
WATER_LEVEL = 90
PLANT_GROWTH_RATE = 0.12
PLANT_DECAY_BASE = 0.02
PLANT_DECAY_DRY = 0.08
HERBIVORE_START_ENERGY = 0.6
HERBIVORE_MAX_ENERGY = 1.6
HERBIVORE_REPRO_ENERGY = 1.2
HERBIVORE_EAT_RATE = 0.22
HERBIVORE_EAT_GAIN = 1.6
HERBIVORE_METABOLISM = 0.05
HERBIVORE_DENSITY = 128
PREDATOR_START_ENERGY = 0.9
PREDATOR_MAX_ENERGY = 2.2
PREDATOR_REPRO_ENERGY = 1.6
PREDATOR_EAT_GAIN = 1.4
PREDATOR_METABOLISM = 0.07
PREDATOR_DENSITY = 256
RIVER_PERCENTILE = 0.92
RIVER_FLOW_BASE = 0.02
RIVER_MOISTURE_GAIN = 0.06
RIVER_MOISTURE_FLOOR = 0.35
RIVER_MOISTURE_RANGE = 0.45
RIVER_COLOR = (30, 100, 160)
CRASH_WINDOW = 50
CRASH_DROP = 0.5
REGIME_WINDOW = 80
REGIME_SHIFT_DELTA = 0.12
EVENT_HOLD_STEPS = 180


class LcgRng:
    def __init__(self, seed: int) -> None:
        self.state = seed & MASK32

    def next_u32(self) -> int:
        self.state = (1664525 * self.state + 1013904223) & MASK32
        return self.state


class Simulation:
    def __init__(self, width: int, height: int, seed: int) -> None:
        self.width = width
        self.height = height
        self.seed = seed
        self.rng = LcgRng(seed)
        self.tick = 0
        size = width * height
        self.cells = [self.rng.next_u32() for _ in range(size)]
        heights, temps, rains = build_fields(width, height, seed)
        self.heights = heights
        self.base_temperature = [temp / 255.0 for temp in temps]
        self.base_rainfall = [rain / 255.0 for rain in rains]
        self.flow_accum, self.river_mask, self.river_strength = build_flow_fields(
            heights, self.base_rainfall, width, height
        )
        self.temperature = list(self.base_temperature)
        self.rainfall = list(self.base_rainfall)
        self.water_mask = [height < WATER_LEVEL for height in heights]
        self.moisture = [0.0 for _ in range(size)]
        self.plant_biomass = [0.0 for _ in range(size)]
        self.agent_rng = LcgRng(seed ^ 0x5F356495)
        self.herbivore_x: List[int] = []
        self.herbivore_y: List[int] = []
        self.herbivore_energy: List[float] = []
        self.predator_x: List[int] = []
        self.predator_y: List[int] = []
        self.predator_energy: List[float] = []
        for idx in range(size):
            if self.water_mask[idx]:
                self.moisture[idx] = 1.0
                self.plant_biomass[idx] = 0.0
            else:
                base_moisture = 0.6 * self.base_rainfall[idx] + 0.2 * self.base_temperature[idx]
                river_strength = self.river_strength[idx]
                if river_strength > 0.0:
                    base_moisture = max(
                        base_moisture, RIVER_MOISTURE_FLOOR + RIVER_MOISTURE_RANGE * river_strength
                    )
                self.moisture[idx] = clamp_unit(base_moisture)
                plant = 0.5 * self.base_rainfall[idx] + 0.5 * self.base_temperature[idx]
                self.plant_biomass[idx] = clamp_unit(plant)
        self._seed_herbivores()
        self._seed_predators()

    def _seed_herbivores(self) -> None:
        land_indices = [idx for idx, water in enumerate(self.water_mask) if not water]
        if not land_indices:
            return
        target = max(4, (self.width * self.height) // HERBIVORE_DENSITY)
        for _ in range(target):
            idx = land_indices[self.agent_rng.next_u32() % len(land_indices)]
            self.herbivore_x.append(idx % self.width)
            self.herbivore_y.append(idx // self.width)
            energy = HERBIVORE_START_ENERGY + 0.4 * self.plant_biomass[idx]
            self.herbivore_energy.append(clamp_range(energy, 0.2, HERBIVORE_MAX_ENERGY))

    def _seed_predators(self) -> None:
        land_indices = [idx for idx, water in enumerate(self.water_mask) if not water]
        if not land_indices:
            return
        target = max(2, (self.width * self.height) // PREDATOR_DENSITY)
        for _ in range(target):
            idx = land_indices[self.agent_rng.next_u32() % len(land_indices)]
            self.predator_x.append(idx % self.width)
            self.predator_y.append(idx // self.width)
            energy = PREDATOR_START_ENERGY + 0.2 * self.plant_biomass[idx]
            self.predator_energy.append(clamp_range(energy, 0.3, PREDATOR_MAX_ENERGY))

    def step(self, dt: float) -> None:
        dt_scaled = int(dt * 1000)
        self.tick = (self.tick + dt_scaled) & MASK32
        w = self.width
        h = self.height
        cells = self.cells
        next_cells = [0] * len(cells)
        for idx, val in enumerate(cells):
            left = cells[idx - 1] if idx % w else cells[idx + w - 1]
            up = cells[idx - w] if idx >= w else cells[idx + (h - 1) * w]
            mix = (val + left + up + self.rng.next_u32() + self.tick) & MASK32
            mix ^= ((mix << 13) & MASK32) ^ (mix >> 7)
            next_cells[idx] = mix
        self.cells = next_cells
        if dt <= 0.0:
            return
        sim_time = self.tick / 1000.0
        season_phase = (sim_time / 120.0) * 2.0 * math.pi
        temp_shift = 0.08 * math.sin(season_phase)
        rain_factor = 0.8 + 0.2 * math.sin(season_phase + 1.3)
        for idx in range(len(self.moisture)):
            temp = clamp_unit(self.base_temperature[idx] + temp_shift)
            rain = clamp_unit(self.base_rainfall[idx] * rain_factor)
            self.temperature[idx] = temp
            self.rainfall[idx] = rain
            moisture = self.moisture[idx]
            rain_add = rain * 0.1 * dt
            evaporation = (0.01 + 0.05 * temp) * dt
            plant_use = self.plant_biomass[idx] * 0.04 * dt
            river_strength = self.river_strength[idx]
            river_add = river_strength * RIVER_MOISTURE_GAIN * dt
            moisture = moisture + rain_add - evaporation - plant_use + river_add
            if river_strength > 0.0:
                moisture = max(moisture, RIVER_MOISTURE_FLOOR + RIVER_MOISTURE_RANGE * river_strength)
            if self.water_mask[idx]:
                moisture = max(0.85, moisture)
            self.moisture[idx] = clamp_unit(moisture)
        self.update_plants(dt)
        self.update_herbivores(dt)
        self.update_predators(dt)

    def update_plants(self, dt: float) -> None:
        if dt <= 0.0:
            return
        for idx in range(len(self.plant_biomass)):
            if self.water_mask[idx]:
                self.plant_biomass[idx] = 0.0
                continue
            moisture = self.moisture[idx]
            light = clamp_unit(0.3 + 0.7 * self.temperature[idx])
            growth = light * moisture * PLANT_GROWTH_RATE * dt
            decay = (PLANT_DECAY_BASE + PLANT_DECAY_DRY * (1.0 - moisture)) * dt
            biomass = self.plant_biomass[idx] + growth - decay
            self.plant_biomass[idx] = clamp_unit(biomass)

    def update_herbivores(self, dt: float) -> None:
        if dt <= 0.0 or not self.herbivore_x:
            return
        width = self.width
        height = self.height
        next_x: List[int] = []
        next_y: List[int] = []
        next_energy: List[float] = []
        for idx in range(len(self.herbivore_x)):
            x = self.herbivore_x[idx]
            y = self.herbivore_y[idx]
            energy = self.herbivore_energy[idx]
            best_biomass = -1.0
            best_positions: List[Tuple[int, int]] = []
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                nx = x + dx
                ny = y + dy
                if nx < 0 or nx >= width or ny < 0 or ny >= height:
                    continue
                nidx = ny * width + nx
                if self.water_mask[nidx]:
                    continue
                biomass = self.plant_biomass[nidx]
                if biomass > best_biomass + 1e-6:
                    best_biomass = biomass
                    best_positions = [(nx, ny)]
                elif abs(biomass - best_biomass) <= 1e-6:
                    best_positions.append((nx, ny))
            if best_positions:
                choice = best_positions[self.agent_rng.next_u32() % len(best_positions)]
                x, y = choice
            pos_idx = y * width + x
            available = self.plant_biomass[pos_idx]
            eat = min(available, HERBIVORE_EAT_RATE * dt)
            if eat > 0.0:
                self.plant_biomass[pos_idx] = clamp_unit(available - eat)
            energy += eat * HERBIVORE_EAT_GAIN
            energy -= HERBIVORE_METABOLISM * dt
            if energy <= 0.0:
                continue
            energy = min(energy, HERBIVORE_MAX_ENERGY)
            reproduced = energy >= HERBIVORE_REPRO_ENERGY
            if reproduced:
                energy *= 0.5
            next_x.append(x)
            next_y.append(y)
            next_energy.append(energy)
            if reproduced:
                child_x, child_y = self._pick_spawn(x, y)
                next_x.append(child_x)
                next_y.append(child_y)
                next_energy.append(energy)
        self.herbivore_x = next_x
        self.herbivore_y = next_y
        self.herbivore_energy = next_energy

    def update_predators(self, dt: float) -> None:
        if dt <= 0.0 or not self.predator_x:
            return
        width = self.width
        height = self.height
        prey_alive = [True for _ in range(len(self.herbivore_x))]
        prey_cells: List[List[int]] = [[] for _ in range(width * height)]
        for idx, (hx, hy) in enumerate(zip(self.herbivore_x, self.herbivore_y)):
            prey_cells[hy * width + hx].append(idx)
        next_x: List[int] = []
        next_y: List[int] = []
        next_energy: List[float] = []
        for idx in range(len(self.predator_x)):
            x = self.predator_x[idx]
            y = self.predator_y[idx]
            energy = self.predator_energy[idx]
            prey_positions: List[Tuple[int, int]] = []
            plant_positions: List[Tuple[int, int]] = []
            best_prey = 0
            best_plant = -1.0
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                nx = x + dx
                ny = y + dy
                if nx < 0 or nx >= width or ny < 0 or ny >= height:
                    continue
                nidx = ny * width + nx
                if self.water_mask[nidx]:
                    continue
                prey_count = len(prey_cells[nidx])
                if prey_count:
                    if prey_count > best_prey:
                        best_prey = prey_count
                        prey_positions = [(nx, ny)]
                    elif prey_count == best_prey:
                        prey_positions.append((nx, ny))
                biomass = self.plant_biomass[nidx]
                if biomass > best_plant + 1e-6:
                    best_plant = biomass
                    plant_positions = [(nx, ny)]
                elif abs(biomass - best_plant) <= 1e-6:
                    plant_positions.append((nx, ny))
            if prey_positions:
                choice = prey_positions[self.agent_rng.next_u32() % len(prey_positions)]
                x, y = choice
            elif plant_positions:
                choice = plant_positions[self.agent_rng.next_u32() % len(plant_positions)]
                x, y = choice
            pos_idx = y * width + x
            prey_list = prey_cells[pos_idx]
            if prey_list:
                prey_pick = self.agent_rng.next_u32() % len(prey_list)
                prey_idx = prey_list.pop(prey_pick)
                if prey_alive[prey_idx]:
                    prey_alive[prey_idx] = False
                    energy += PREDATOR_EAT_GAIN
            energy -= PREDATOR_METABOLISM * dt
            if energy <= 0.0:
                continue
            energy = min(energy, PREDATOR_MAX_ENERGY)
            reproduced = energy >= PREDATOR_REPRO_ENERGY
            if reproduced:
                energy *= 0.5
            next_x.append(x)
            next_y.append(y)
            next_energy.append(energy)
            if reproduced:
                child_x, child_y = self._pick_spawn(x, y)
                next_x.append(child_x)
                next_y.append(child_y)
                next_energy.append(energy)
        self.predator_x = next_x
        self.predator_y = next_y
        self.predator_energy = next_energy
        if prey_alive:
            survivors_x: List[int] = []
            survivors_y: List[int] = []
            survivors_energy: List[float] = []
            for alive, hx, hy, he in zip(
                prey_alive,
                self.herbivore_x,
                self.herbivore_y,
                self.herbivore_energy,
            ):
                if alive:
                    survivors_x.append(hx)
                    survivors_y.append(hy)
                    survivors_energy.append(he)
            self.herbivore_x = survivors_x
            self.herbivore_y = survivors_y
            self.herbivore_energy = survivors_energy

    def _pick_spawn(self, x: int, y: int) -> Tuple[int, int]:
        candidates: List[Tuple[int, int]] = []
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            nx = x + dx
            ny = y + dy
            if nx < 0 or nx >= self.width or ny < 0 or ny >= self.height:
                continue
            idx = ny * self.width + nx
            if self.water_mask[idx]:
                continue
            candidates.append((nx, ny))
        if not candidates:
            return x, y
        return candidates[self.agent_rng.next_u32() % len(candidates)]

    def run_fixed(self, steps: int, dt: float = 1.0) -> None:
        for _ in range(steps):
            self.step(dt)

    def digest(self) -> str:
        h = hashlib.sha256()
        h.update(self.tick.to_bytes(4, "little"))
        for val in self.cells:
            h.update(val.to_bytes(4, "little"))
        for field in (
            self.temperature,
            self.rainfall,
            self.moisture,
            self.plant_biomass,
            self.river_strength,
        ):
            for value in field:
                h.update(clamp_byte(value * 255.0).to_bytes(1, "little"))
        h.update(len(self.herbivore_x).to_bytes(4, "little"))
        for x, y, energy in zip(self.herbivore_x, self.herbivore_y, self.herbivore_energy):
            h.update(x.to_bytes(2, "little"))
            h.update(y.to_bytes(2, "little"))
            scaled_energy = (energy / HERBIVORE_MAX_ENERGY) * 255.0
            h.update(clamp_byte(scaled_energy).to_bytes(1, "little"))
        h.update(len(self.predator_x).to_bytes(4, "little"))
        for x, y, energy in zip(self.predator_x, self.predator_y, self.predator_energy):
            h.update(x.to_bytes(2, "little"))
            h.update(y.to_bytes(2, "little"))
            scaled_energy = (energy / PREDATOR_MAX_ENERGY) * 255.0
            h.update(clamp_byte(scaled_energy).to_bytes(1, "little"))
        return h.hexdigest()


def clamp_byte(value: float) -> int:
    if value < 0:
        return 0
    if value > 255:
        return 255
    return int(value)


def clamp_unit(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def clamp_range(value: float, lower: float, upper: float) -> float:
    if value < lower:
        return lower
    if value > upper:
        return upper
    return value


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_color(a: Tuple[int, int, int], b: Tuple[int, int, int], t: float) -> Tuple[float, float, float]:
    return (lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t))


def blend_color(a: Tuple[int, int, int], b: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
    mixed = lerp_color(a, b, t)
    return (clamp_byte(mixed[0]), clamp_byte(mixed[1]), clamp_byte(mixed[2]))


def smoothstep(t: float) -> float:
    return t * t * (3.0 - 2.0 * t)


def hash_u32(x: int, y: int, seed: int) -> int:
    n = (x * 374761393 + y * 668265263 + seed * 700001) & MASK32
    n = (n ^ (n >> 13)) & MASK32
    n = (n * 1274126177) & MASK32
    n ^= n >> 16
    return n & MASK32


def hash_unit(x: int, y: int, seed: int) -> float:
    return hash_u32(x, y, seed) / float(MASK32)


def value_noise(x: int, y: int, seed: int, scale: int) -> float:
    if scale <= 1:
        return hash_unit(x, y, seed)
    x0 = (x // scale) * scale
    y0 = (y // scale) * scale
    x1 = x0 + scale
    y1 = y0 + scale
    sx = (x - x0) / float(scale)
    sy = (y - y0) / float(scale)
    u = smoothstep(sx)
    v = smoothstep(sy)
    v00 = hash_unit(x0, y0, seed)
    v10 = hash_unit(x1, y0, seed)
    v01 = hash_unit(x0, y1, seed)
    v11 = hash_unit(x1, y1, seed)
    ix0 = lerp(v00, v10, u)
    ix1 = lerp(v01, v11, u)
    return lerp(ix0, ix1, v)


def fbm_noise(x: int, y: int, seed: int, scales: List[int]) -> float:
    total = 0.0
    amplitude = 1.0
    norm = 0.0
    for scale in scales:
        total += value_noise(x, y, seed, scale) * amplitude
        norm += amplitude
        amplitude *= 0.5
    if norm == 0.0:
        return 0.0
    return total / norm


def build_noise_scales(width: int, height: int) -> List[int]:
    min_dim = max(4, min(width, height))
    base = max(4, min_dim // 2)
    scales = [base]
    for _ in range(3):
        base = max(2, base // 2)
        if base == scales[-1]:
            break
        scales.append(base)
    return scales


def build_fields(width: int, height: int, seed: int) -> Tuple[List[int], List[int], List[int]]:
    scales = build_noise_scales(width, height)
    size = width * height
    heights = [0] * size
    temps = [0] * size
    rains = [0] * size
    for y in range(height):
        row = y * width
        if height > 1:
            lat = abs((y / (height - 1)) * 2.0 - 1.0)
            lat_warm = 1.0 - lat
        else:
            lat_warm = 1.0
        for x in range(width):
            idx = row + x
            height_noise = fbm_noise(x, y, seed + 101, scales)
            temp_noise = fbm_noise(x, y, seed + 202, scales)
            rain_noise = fbm_noise(x, y, seed + 303, scales)
            height_val = clamp_unit(height_noise)
            temp_val = clamp_unit(0.6 * temp_noise + 0.4 * lat_warm - 0.2 * height_val)
            rain_val = clamp_unit(0.7 * rain_noise + 0.3 * (1.0 - height_val))
            heights[idx] = clamp_byte(height_val * 255.0)
            temps[idx] = clamp_byte(temp_val * 255.0)
            rains[idx] = clamp_byte(rain_val * 255.0)
    return heights, temps, rains


def build_flow_fields(
    heights: List[int], base_rainfall: List[float], width: int, height: int
) -> Tuple[List[float], List[bool], List[float]]:
    size = width * height
    flow_to = list(range(size))
    for y in range(height):
        row = y * width
        for x in range(width):
            idx = row + x
            best_idx = idx
            best_height = heights[idx]
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx = x + dx
                ny = y + dy
                if nx < 0 or nx >= width or ny < 0 or ny >= height:
                    continue
                nidx = ny * width + nx
                nheight = heights[nidx]
                if nheight < best_height:
                    best_height = nheight
                    best_idx = nidx
            flow_to[idx] = best_idx
    accum = [base_rainfall[idx] + RIVER_FLOW_BASE for idx in range(size)]
    order = sorted(range(size), key=lambda i: heights[i], reverse=True)
    for idx in order:
        dest = flow_to[idx]
        if dest != idx:
            accum[dest] += accum[idx]
    river_mask = [False for _ in range(size)]
    river_strength = [0.0 for _ in range(size)]
    land_indices = [idx for idx, height in enumerate(heights) if height >= WATER_LEVEL]
    if not land_indices:
        return accum, river_mask, river_strength
    land_accum = sorted(accum[idx] for idx in land_indices)
    cutoff_index = int(len(land_accum) * RIVER_PERCENTILE)
    if cutoff_index >= len(land_accum):
        cutoff_index = len(land_accum) - 1
    cutoff = land_accum[cutoff_index]
    max_accum = land_accum[-1]
    if max_accum <= cutoff + 1e-6:
        return accum, river_mask, river_strength
    span = max_accum - cutoff
    for idx in land_indices:
        if accum[idx] >= cutoff:
            river_mask[idx] = True
            river_strength[idx] = clamp_unit((accum[idx] - cutoff) / span)
    return accum, river_mask, river_strength


def normalize_vec3(x: float, y: float, z: float) -> Tuple[float, float, float]:
    length = math.sqrt(x * x + y * y + z * z)
    if length == 0.0:
        return (0.0, 0.0, 1.0)
    return (x / length, y / length, z / length)


def build_normals(heights: List[int], width: int, height: int, strength: float = 1.35) -> List[Tuple[float, float, float]]:
    normals: List[Tuple[float, float, float]] = []
    for y in range(height):
        row = y * width
        for x in range(width):
            idx = row + x
            left = heights[idx - 1] if x > 0 else heights[idx]
            right = heights[idx + 1] if x < width - 1 else heights[idx]
            up = heights[idx - width] if y > 0 else heights[idx]
            down = heights[idx + width] if y < height - 1 else heights[idx]
            dx = (right - left) / 255.0
            dy = (down - up) / 255.0
            nx = -dx * strength
            ny = -dy * strength
            nz = 1.0
            normals.append(normalize_vec3(nx, ny, nz))
    return normals


def color_for(height: int, temp: int, rain: int) -> Tuple[int, int, int]:
    if height < WATER_LEVEL:
        depth = height / float(WATER_LEVEL)
        return (
            clamp_byte(20 + 30 * depth),
            clamp_byte(40 + 80 * depth),
            clamp_byte(120 + 100 * depth),
        )
    if height > 230:
        return (230, 230, 230)
    if height > 210:
        base = (120, 120, 120)
    elif temp < 80:
        if rain < 90:
            base = (160, 160, 150)
        else:
            base = (90, 130, 110)
    elif temp > 170:
        if rain < 80:
            base = (210, 185, 110)
        elif rain < 150:
            base = (160, 170, 90)
        else:
            base = (50, 120, 70)
    else:
        if rain < 90:
            base = (170, 170, 120)
        elif rain < 160:
            base = (90, 150, 90)
        else:
            base = (70, 140, 90)
    elevation = (height - WATER_LEVEL) / float(255 - WATER_LEVEL)
    shade = 0.6 + 0.4 * elevation
    return (
        clamp_byte(base[0] * shade),
        clamp_byte(base[1] * shade),
        clamp_byte(base[2] * shade),
    )


def sky_color_for(sun_elev: float, sun_height: float) -> Tuple[int, int, int]:
    night = (10, 14, 28)
    day = (120, 170, 220)
    dusk = (240, 140, 90)
    base = lerp_color(night, day, sun_height)
    twilight = clamp_unit(1.0 - abs(sun_elev) * 1.4)
    if twilight > 0.0:
        base = lerp_color(base, dusk, twilight * 0.6)
    return (clamp_byte(base[0]), clamp_byte(base[1]), clamp_byte(base[2]))


def sun_state(sim_time: float) -> Tuple[Tuple[float, float, float], float, Tuple[int, int, int]]:
    day_length = 60.0
    phase = (sim_time / day_length) * 2.0 * math.pi
    sun_elev = math.sin(phase)
    sun_height = clamp_unit((sun_elev + 0.15) / 1.15)
    sun_az = phase * 0.35
    sun_dir = normalize_vec3(math.cos(sun_az), math.sin(sun_az), max(0.2, sun_height))
    sky_color = sky_color_for(sun_elev, sun_height)
    return sun_dir, sun_height, sky_color


def shade_color(
    base: Tuple[int, int, int],
    normal: Tuple[float, float, float],
    sun_dir: Tuple[float, float, float],
    sun_height: float,
    sky_color: Tuple[int, int, int],
    is_water: bool,
) -> Tuple[int, int, int]:
    dot = normal[0] * sun_dir[0] + normal[1] * sun_dir[1] + normal[2] * sun_dir[2]
    dot = max(0.0, dot)
    ambient = 0.22 + 0.35 * sun_height
    diffuse = 0.6 * dot * (0.25 + 0.75 * sun_height)
    light = ambient + diffuse
    r = base[0] * light
    g = base[1] * light
    b = base[2] * light
    sky_tint = 0.08 + 0.12 * sun_height
    r = r * (1.0 - sky_tint) + sky_color[0] * sky_tint
    g = g * (1.0 - sky_tint) + sky_color[1] * sky_tint
    b = b * (1.0 - sky_tint) + sky_color[2] * sky_tint
    if is_water:
        reflect = 0.2 + 0.35 * sun_height
        r = r * (1.0 - reflect) + sky_color[0] * reflect
        g = g * (1.0 - reflect) + sky_color[1] * reflect
        b = b * (1.0 - reflect) + sky_color[2] * reflect
        spec = (dot ** 12) * (0.45 + 0.35 * sun_height)
        r += 255.0 * spec
        g += 255.0 * spec
        b += 255.0 * spec
    return (clamp_byte(r), clamp_byte(g), clamp_byte(b))


def render_lit_surface(
    surface,
    base_colors: List[Tuple[int, int, int]],
    normals: List[Tuple[float, float, float]],
    water_mask: List[bool],
    sun_dir: Tuple[float, float, float],
    sun_height: float,
    sky_color: Tuple[int, int, int],
    width: int,
    height: int,
) -> None:
    surface.lock()
    for y in range(height):
        row = y * width
        for x in range(width):
            idx = row + x
            color = shade_color(
                base_colors[idx],
                normals[idx],
                sun_dir,
                sun_height,
                sky_color,
                water_mask[idx],
            )
            surface.set_at((x, y), color)
    surface.unlock()


def build_world_data(
    sim: Simulation,
) -> Tuple[List[Tuple[int, int, int]], List[bool], List[Tuple[float, float, float]]]:
    heights, temps, rains = build_fields(sim.width, sim.height, sim.seed)
    base_rainfall = [rain / 255.0 for rain in rains]
    _, river_mask, river_strength = build_flow_fields(
        heights, base_rainfall, sim.width, sim.height
    )
    base_colors: List[Tuple[int, int, int]] = []
    water_mask: List[bool] = []
    for idx, height in enumerate(heights):
        color = color_for(height, temps[idx], rains[idx])
        if river_mask[idx]:
            tint = 0.35 + 0.35 * river_strength[idx]
            color = blend_color(color, RIVER_COLOR, clamp_unit(tint))
        base_colors.append(color)
        water_mask.append(height < WATER_LEVEL or river_mask[idx])
    normals = build_normals(heights, sim.width, sim.height)
    return base_colors, water_mask, normals


def build_world_surface(sim: Simulation):
    import pygame

    base_colors, water_mask, normals = build_world_data(sim)
    surface = pygame.Surface((sim.width, sim.height))
    sun_dir, sun_height, sky_color = sun_state(0.0)
    render_lit_surface(
        surface,
        base_colors,
        normals,
        water_mask,
        sun_dir,
        sun_height,
        sky_color,
        sim.width,
        sim.height,
    )
    return surface, base_colors, water_mask, normals


def viewport_dim(world_dim: int) -> int:
    target = int(world_dim * 0.75)
    if target < 320:
        target = 320
    return min(world_dim, target)


def update_history(history: List[float], value: float, max_len: int) -> None:
    history.append(value)
    if len(history) > max_len:
        del history[: len(history) - max_len]


def mean(values: List[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def draw_series(pygame, surface, rect, series: List[float], color: Tuple[int, int, int], scale: float) -> None:
    if len(series) < 2 or rect.width < 2 or rect.height < 2:
        return
    scale = max(scale, 1e-6)
    span = len(series) - 1
    points = []
    for idx, value in enumerate(series):
        t = idx / span if span else 0.0
        x = rect.left + int(t * (rect.width - 1))
        norm = clamp_unit(value / scale)
        y = rect.bottom - 1 - int(norm * (rect.height - 1))
        points.append((x, y))
    if len(points) >= 2:
        pygame.draw.lines(surface, color, False, points, 2)


def heatmap_color(value: float, water: bool) -> Tuple[int, int, int]:
    if water:
        return (18, 30, 46)
    value = clamp_unit(value)
    low = (16, 24, 16)
    mid = (40, 110, 60)
    high = (170, 220, 120)
    if value < 0.5:
        return blend_color(low, mid, smoothstep(value * 2.0))
    return blend_color(mid, high, smoothstep((value - 0.5) * 2.0))


def draw_heatmap(
    pygame,
    surface,
    rect,
    values: List[float],
    width: int,
    height: int,
    water_mask: Optional[List[bool]],
) -> None:
    if rect.width < 2 or rect.height < 2 or width <= 0 or height <= 0:
        return
    heat_surface = pygame.Surface((width, height))
    for y in range(height):
        row = y * width
        for x in range(width):
            idx = row + x
            water = water_mask[idx] if water_mask else False
            heat_surface.set_at((x, y), heatmap_color(values[idx], water))
    scaled = pygame.transform.scale(heat_surface, (rect.width, rect.height))
    surface.blit(scaled, rect)


def draw_dashboard_panel(
    pygame,
    screen,
    panel_rect,
    font,
    plant_history: List[float],
    herb_history: List[float],
    pred_history: List[float],
    heatmap_values: List[float],
    heatmap_width: int,
    heatmap_height: int,
    heatmap_water_mask: Optional[List[bool]],
    event_rows: List[Tuple[str, str, bool]],
) -> None:
    panel_bg = (18, 18, 22)
    panel_border = (60, 60, 70)
    text_color = (220, 220, 230)
    subtitle_color = (170, 170, 185)
    plant_color = (80, 200, 120)
    herb_color = (220, 200, 80)
    pred_color = (220, 80, 80)
    pygame.draw.rect(screen, panel_bg, panel_rect)
    pygame.draw.rect(screen, panel_border, panel_rect, 1)
    padding = 10
    cursor_x = panel_rect.left + padding
    cursor_y = panel_rect.top + padding
    title = font.render("Dashboard", True, text_color)
    screen.blit(title, (cursor_x, cursor_y))
    cursor_y += title.get_height() + 6
    subtitle = font.render("Timeseries", True, subtitle_color)
    screen.blit(subtitle, (cursor_x, cursor_y))
    cursor_y += subtitle.get_height() + 6
    plot_height = int(panel_rect.height * 0.35)
    plot_rect = pygame.Rect(
        cursor_x,
        cursor_y,
        panel_rect.width - padding * 2,
        plot_height,
    )
    pygame.draw.rect(screen, (26, 26, 32), plot_rect)
    for idx in range(1, 4):
        y = plot_rect.top + int(plot_rect.height * idx / 4)
        pygame.draw.line(screen, (40, 40, 46), (plot_rect.left, y), (plot_rect.right, y), 1)
    inner_plot = plot_rect.inflate(-4, -4)
    pop_scale = 1.0
    if herb_history:
        pop_scale = max(pop_scale, max(herb_history))
    if pred_history:
        pop_scale = max(pop_scale, max(pred_history))
    draw_series(pygame, screen, inner_plot, plant_history, plant_color, 1.0)
    draw_series(pygame, screen, inner_plot, herb_history, herb_color, pop_scale)
    draw_series(pygame, screen, inner_plot, pred_history, pred_color, pop_scale)
    cursor_y = plot_rect.bottom + 8
    plant_value = plant_history[-1] if plant_history else 0.0
    herb_value = herb_history[-1] if herb_history else 0.0
    pred_value = pred_history[-1] if pred_history else 0.0
    entries = [
        (plant_color, f"Plants: {plant_value:.2f}"),
        (herb_color, f"Herb: {int(round(herb_value))}"),
        (pred_color, f"Pred: {int(round(pred_value))}"),
    ]
    for color, text in entries:
        label = font.render(text, True, color)
        screen.blit(label, (cursor_x, cursor_y))
        cursor_y += label.get_height() + 4
    cursor_y += 4
    subtitle = font.render("Heatmap (Plants)", True, subtitle_color)
    screen.blit(subtitle, (cursor_x, cursor_y))
    cursor_y += subtitle.get_height() + 6
    heatmap_height_px = min(panel_rect.width - padding * 2, max(60, int(panel_rect.height * 0.25)))
    heatmap_rect = pygame.Rect(
        cursor_x,
        cursor_y,
        panel_rect.width - padding * 2,
        heatmap_height_px,
    )
    pygame.draw.rect(screen, (26, 26, 32), heatmap_rect)
    inner_heatmap = heatmap_rect.inflate(-4, -4)
    draw_heatmap(
        pygame,
        screen,
        inner_heatmap,
        heatmap_values,
        heatmap_width,
        heatmap_height,
        heatmap_water_mask,
    )
    cursor_y = heatmap_rect.bottom + 8
    subtitle = font.render("Events", True, subtitle_color)
    screen.blit(subtitle, (cursor_x, cursor_y))
    cursor_y += subtitle.get_height() + 6
    event_colors = {
        "Extinction": (190, 70, 70),
        "Crash": (210, 150, 70),
        "Regime shift": (80, 170, 190),
    }
    for label, detail, active in event_rows:
        if cursor_y >= panel_rect.bottom - padding:
            break
        badge_text = label if not detail else f"{label}: {detail}"
        badge_color = event_colors.get(label, panel_border)
        if not active:
            badge_color = (45, 45, 52)
        text_tint = (240, 240, 240) if active else (150, 150, 160)
        badge = font.render(badge_text, True, text_tint)
        badge_rect = pygame.Rect(
            cursor_x,
            cursor_y,
            panel_rect.width - padding * 2,
            badge.get_height() + 6,
        )
        pygame.draw.rect(screen, badge_color, badge_rect)
        pygame.draw.rect(screen, panel_border, badge_rect, 1)
        screen.blit(badge, (badge_rect.left + 6, badge_rect.top + 3))
        cursor_y = badge_rect.bottom + 6


def run_window(sim: Simulation) -> int:
    try:
        import pygame
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "pygame is required for windowed mode. "
            "Install with: python -m pip install pygame"
        ) from exc

    pygame.init()
    scale = DEFAULT_SCALE
    world_size = (sim.width * scale, sim.height * scale)
    view_size = (viewport_dim(world_size[0]), viewport_dim(world_size[1]))
    panel_width = max(200, view_size[0] // 3)
    screen = pygame.display.set_mode((view_size[0] + panel_width, view_size[1]))
    pygame.display.set_caption("Microverse")
    base_surface, base_colors, water_mask, normals = build_world_surface(sim)
    if scale != 1:
        world_surface = pygame.Surface(world_size)
    else:
        world_surface = base_surface
    camera_x = max(0.0, (world_size[0] - view_size[0]) * 0.5)
    camera_y = max(0.0, (world_size[1] - view_size[1]) * 0.5)
    move_speed = 320.0
    dragging = False
    last_mouse = (0, 0)
    paused = False
    time_scale = 1.0
    sim_time = 0.0
    font = pygame.font.Font(None, 20)
    clock = pygame.time.Clock()
    history_len = 300
    plant_history: List[float] = []
    herb_history: List[float] = []
    pred_history: List[float] = []
    event_age = {"extinction": 0, "crash": 0, "regime": 0}
    event_detail = {"extinction": "", "crash": "", "regime": ""}
    crash_window = min(CRASH_WINDOW, history_len)
    regime_window = min(REGIME_WINDOW, max(1, history_len // 2))
    panel_rect = pygame.Rect(view_size[0], 0, panel_width, view_size[1])

    def update_events() -> None:
        for key in event_age:
            if event_age[key] > 0:
                event_age[key] -= 1
                if event_age[key] == 0:
                    event_detail[key] = ""
        extinction_labels = []
        herb_count = int(round(herb_history[-1])) if herb_history else 0
        pred_count = int(round(pred_history[-1])) if pred_history else 0
        if herb_history and herb_count == 0:
            extinction_labels.append("Herbivores")
        if pred_history and pred_count == 0:
            extinction_labels.append("Predators")
        if extinction_labels:
            event_age["extinction"] = EVENT_HOLD_STEPS
            event_detail["extinction"] = ", ".join(extinction_labels)
        crash_labels = []
        if crash_window >= 2 and len(herb_history) >= crash_window:
            window = herb_history[-crash_window:]
            peak = max(window)
            if peak > 0.0 and herb_history[-1] <= peak * (1.0 - CRASH_DROP):
                crash_labels.append("Herbivores")
        if crash_window >= 2 and len(pred_history) >= crash_window:
            window = pred_history[-crash_window:]
            peak = max(window)
            if peak > 0.0 and pred_history[-1] <= peak * (1.0 - CRASH_DROP):
                crash_labels.append("Predators")
        if crash_labels:
            event_age["crash"] = EVENT_HOLD_STEPS
            event_detail["crash"] = ", ".join(crash_labels)
        if len(plant_history) >= regime_window * 2:
            recent = mean(plant_history[-regime_window:])
            prior = mean(plant_history[-2 * regime_window : -regime_window])
            delta = recent - prior
            if abs(delta) >= REGIME_SHIFT_DELTA:
                trend = "Up" if delta > 0.0 else "Down"
                event_age["regime"] = EVENT_HOLD_STEPS
                event_detail["regime"] = f"{trend} {abs(delta):.2f}"

    def sample_history() -> None:
        plant_mean = 0.0
        if sim.plant_biomass:
            plant_mean = sum(sim.plant_biomass) / len(sim.plant_biomass)
        update_history(plant_history, plant_mean, history_len)
        update_history(herb_history, float(len(sim.herbivore_x)), history_len)
        update_history(pred_history, float(len(sim.predator_x)), history_len)
        update_events()

    sample_history()
    running = True
    while running:
        frame_dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_1:
                    time_scale = 1.0
                    paused = False
                elif event.key == pygame.K_2:
                    time_scale = 2.0
                    paused = False
                elif event.key == pygame.K_4:
                    time_scale = 4.0
                    paused = False
                elif event.key == pygame.K_8:
                    time_scale = 8.0
                    paused = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (2, 3):
                dragging = True
                last_mouse = event.pos
            elif event.type == pygame.MOUSEBUTTONUP and event.button in (2, 3):
                dragging = False
            elif event.type == pygame.MOUSEMOTION and dragging:
                dx = event.pos[0] - last_mouse[0]
                dy = event.pos[1] - last_mouse[1]
                camera_x -= dx
                camera_y -= dy
                last_mouse = event.pos
        keys = pygame.key.get_pressed()
        move_x = 0.0
        move_y = 0.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_x -= 1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_x += 1.0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move_y -= 1.0
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_y += 1.0
        if move_x or move_y:
            camera_x += move_x * move_speed * frame_dt
            camera_y += move_y * move_speed * frame_dt
        max_x = max(0.0, world_size[0] - view_size[0])
        max_y = max(0.0, world_size[1] - view_size[1])
        camera_x = clamp_range(camera_x, 0.0, max_x)
        camera_y = clamp_range(camera_y, 0.0, max_y)
        active_scale = 0.0 if paused else time_scale
        sim_dt = frame_dt * active_scale
        if sim_dt > 0.0:
            sim.step(sim_dt)
            sim_time += sim_dt
            sample_history()
        sun_dir, sun_height, sky_color = sun_state(sim_time)
        render_lit_surface(
            base_surface,
            base_colors,
            normals,
            water_mask,
            sun_dir,
            sun_height,
            sky_color,
            sim.width,
            sim.height,
        )
        if scale != 1:
            pygame.transform.scale(base_surface, world_size, world_surface)
        view_rect = pygame.Rect(int(camera_x), int(camera_y), view_size[0], view_size[1])
        screen.fill(sky_color)
        screen.blit(world_surface, (0, 0), view_rect)
        event_rows = [
            ("Extinction", event_detail["extinction"], event_age["extinction"] > 0),
            ("Crash", event_detail["crash"], event_age["crash"] > 0),
            ("Regime shift", event_detail["regime"], event_age["regime"] > 0),
        ]
        draw_dashboard_panel(
            pygame,
            screen,
            panel_rect,
            font,
            plant_history,
            herb_history,
            pred_history,
            sim.plant_biomass,
            sim.width,
            sim.height,
            sim.water_mask,
            event_rows,
        )
        hud_lines = [
            f"Seed: {sim.seed}",
            f"Sim time: {sim_time:.2f}s",
            f"dt: {sim_dt:.3f}s",
            f"FPS: {clock.get_fps():.1f}",
            f"Speed: {'paused' if paused else f'{time_scale:.0f}x'}",
            f"Herbivores: {len(sim.herbivore_x)}",
            f"Predators: {len(sim.predator_x)}",
        ]
        hud_surfaces = [font.render(line, True, (230, 230, 230)) for line in hud_lines]
        hud_width = max(surface.get_width() for surface in hud_surfaces)
        hud_height = sum(surface.get_height() for surface in hud_surfaces) + 2 * (len(hud_surfaces) - 1)
        padding = 6
        hud_rect = pygame.Rect(8, 8, hud_width + padding * 2, hud_height + padding * 2)
        pygame.draw.rect(screen, (12, 12, 12), hud_rect)
        pygame.draw.rect(screen, (60, 60, 60), hud_rect, 1)
        y = hud_rect.top + padding
        for surface in hud_surfaces:
            screen.blit(surface, (hud_rect.left + padding, y))
            y += surface.get_height() + 2
        pygame.display.flip()
    pygame.quit()
    return 0


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Microverse deterministic stub.")
    parser.add_argument("--seed", type=int, default=0, help="Deterministic seed.")
    parser.add_argument(
        "--steps",
        type=int,
        default=300,
        help="Fixed steps to advance (used for selftest).",
    )
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="Run headless regression and print DIGEST.",
    )
    parser.add_argument("--width", type=int, default=64, help="Grid width.")
    parser.add_argument("--height", type=int, default=64, help="Grid height.")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    if args.steps < 0:
        raise SystemExit("steps must be >= 0")
    sim = Simulation(width=args.width, height=args.height, seed=args.seed)
    if args.selftest:
        sim.run_fixed(args.steps, dt=1.0)
        digest = sim.digest()
        print(f"DIGEST={digest}")
        return 0
    digest = sim.digest()
    print(f"DIGEST={digest}")
    return run_window(sim)


if __name__ == "__main__":
    raise SystemExit(main())
