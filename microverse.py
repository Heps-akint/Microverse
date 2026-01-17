#!/usr/bin/env python3
import argparse
import hashlib
from typing import List, Optional


MASK32 = 0xFFFFFFFF


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
    sim.run_fixed(args.steps, dt=1.0)
    digest = sim.digest()
    print(f"DIGEST={digest}")
    if not args.selftest:
        print(f"Completed {args.steps} headless steps.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
