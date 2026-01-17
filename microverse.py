#!/usr/bin/env python3
import argparse
import hashlib
from typing import List, Optional, Tuple


MASK32 = 0xFFFFFFFF
DEFAULT_SCALE = 8


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
        self.cells = [self.rng.next_u32() for _ in range(width * height)]

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

    def run_fixed(self, steps: int, dt: float = 1.0) -> None:
        for _ in range(steps):
            self.step(dt)

    def digest(self) -> str:
        h = hashlib.sha256()
        h.update(self.tick.to_bytes(4, "little"))
        for val in self.cells:
            h.update(val.to_bytes(4, "little"))
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


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


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


def color_for(height: int, temp: int, rain: int) -> Tuple[int, int, int]:
    water_level = 90
    if height < water_level:
        depth = height / float(water_level)
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
    elevation = (height - water_level) / float(255 - water_level)
    shade = 0.6 + 0.4 * elevation
    return (
        clamp_byte(base[0] * shade),
        clamp_byte(base[1] * shade),
        clamp_byte(base[2] * shade),
    )


def build_world_surface(sim: Simulation):
    import pygame

    heights, temps, rains = build_fields(sim.width, sim.height, sim.seed)
    surface = pygame.Surface((sim.width, sim.height))
    for y in range(sim.height):
        row = y * sim.width
        for x in range(sim.width):
            idx = row + x
            surface.set_at((x, y), color_for(heights[idx], temps[idx], rains[idx]))
    return surface


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
    size = (sim.width * scale, sim.height * scale)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Microverse")
    base_surface = build_world_surface(sim)
    if scale != 1:
        frame_surface = pygame.transform.scale(base_surface, size)
    else:
        frame_surface = base_surface
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        screen.blit(frame_surface, (0, 0))
        pygame.display.flip()
        clock.tick(30)
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
