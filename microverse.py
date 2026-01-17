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


def build_heightmap(cells: List[int], width: int, height: int, passes: int = 2) -> List[int]:
    heights = [cell & 0xFF for cell in cells]
    for _ in range(passes):
        next_heights = [0] * len(heights)
        for y in range(height):
            row = y * width
            up = ((y - 1) % height) * width
            down = ((y + 1) % height) * width
            for x in range(width):
                idx = row + x
                left = row + (x - 1) % width
                right = row + (x + 1) % width
                total = (
                    heights[idx]
                    + heights[left]
                    + heights[right]
                    + heights[up + x]
                    + heights[down + x]
                )
                next_heights[idx] = total // 5
        heights = next_heights
    return heights


def color_for(height: int, temp: int, moist: int) -> Tuple[int, int, int]:
    water_level = 90
    if height < water_level:
        depth = height / float(water_level)
        return (
            clamp_byte(20 + 30 * depth),
            clamp_byte(40 + 80 * depth),
            clamp_byte(120 + 100 * depth),
        )
    if height > 220:
        return (230, 230, 230)
    if moist < 80:
        base = (194, 178, 128)
    elif temp < 110:
        base = (80, 140, 70)
    else:
        base = (60, 120, 60)
    elevation = (height - water_level) / float(255 - water_level)
    shade = 0.6 + 0.4 * elevation
    return (
        clamp_byte(base[0] * shade),
        clamp_byte(base[1] * shade),
        clamp_byte(base[2] * shade),
    )


def build_world_surface(sim: Simulation):
    import pygame

    heights = build_heightmap(sim.cells, sim.width, sim.height)
    surface = pygame.Surface((sim.width, sim.height))
    for y in range(sim.height):
        row = y * sim.width
        for x in range(sim.width):
            idx = row + x
            val = sim.cells[idx]
            temp = (val >> 8) & 0xFF
            moist = (val >> 16) & 0xFF
            surface.set_at((x, y), color_for(heights[idx], temp, moist))
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
