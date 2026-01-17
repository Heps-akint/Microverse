#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/ralph_loop_codex.sh build 10
#   ./scripts/ralph_loop_codex.sh plan  3
MODE="${1:-build}"               # build|plan
MAX_ITERATIONS="${2:-0}"         # 0 = unlimited

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_ONCE="$ROOT/scripts/ralph_once_codex.sh"

if [[ ! -x "$RUN_ONCE" ]]; then
  echo "Making executable: $RUN_ONCE"
  chmod +x "$RUN_ONCE"
fi

if ! git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not a git repo: $ROOT" >&2
  exit 1
fi

BRANCH="$(git -C "$ROOT" branch --show-current)"
echo "Mode: $MODE"
echo "Branch: $BRANCH"
if [[ "$MAX_ITERATIONS" -gt 0 ]]; then
  echo "Max iterations: $MAX_ITERATIONS"
fi
echo "----------------------------------------"

i=0
while true; do
  if [[ "$MAX_ITERATIONS" -gt 0 && "$i" -ge "$MAX_ITERATIONS" ]]; then
    echo "Reached max iterations: $MAX_ITERATIONS"
    break
  fi

  echo "========== Ralph iteration $((i+1)) =========="
  "$RUN_ONCE" "$MODE"

  # Push best-effort (won’t fail the loop if no remote).
  if git -C "$ROOT" remote get-url origin >/dev/null 2>&1; then
    git -C "$ROOT" push origin "$BRANCH" || git -C "$ROOT" push -u origin "$BRANCH" || true
  fi

  i=$((i+1))
done
