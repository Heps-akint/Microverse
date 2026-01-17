#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-build}"  # build|plan
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ "$MODE" == "plan" ]]; then
  PROMPT_FILE="$ROOT/ralph/PROMPT_plan.md"
else
  PROMPT_FILE="$ROOT/ralph/PROMPT_build.md"
fi

if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "Missing prompt: $PROMPT_FILE" >&2
  exit 1
fi

if ! command -v codex >/dev/null 2>&1; then
  echo "codex CLI not found in PATH" >&2
  exit 1
fi

# Detect supported exec flags (don’t guess).
HELP="$(codex exec --help 2>&1 || true)"

# Build invocation as an array.
CMD=(codex exec)

# Prefer fully-automatic approvals if available (for true unattended runs).
# If you want manual approvals, delete this block.
if echo "$HELP" | grep -qiE 'full[- ]?auto'; then
  CMD+=(--full-auto)
fi

# Prefer machine-readable output if available (nice for logs).
if echo "$HELP" | grep -qiE 'json'; then
  CMD+=(--json)
fi

# Prefer prompt file if supported; else fallback to stdin; else inline string.
if echo "$HELP" | grep -qiE 'prompt[-_ ]file'; then
  CMD+=(--prompt-file "$PROMPT_FILE")
  "${CMD[@]}"
  exit 0
fi

if echo "$HELP" | grep -qiE 'stdin|read from stdin'; then
  cat "$PROMPT_FILE" | "${CMD[@]}"
  exit 0
fi

# Fallback: pass prompt content as argument (least ideal, but works in many CLIs).
PROMPT_CONTENT="$(cat "$PROMPT_FILE")"
"${CMD[@]}" "$PROMPT_CONTENT"
