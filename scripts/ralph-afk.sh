#!/usr/bin/env bash
# ralph-afk.sh — Run Claude in Docker Sandbox AFK loop
#
# Usage:
#   bash scripts/ralph-afk.sh <PRD_FILE> <PLAN_FILE> [MAX_ITERATIONS]
#
# Example:
#   bash scripts/ralph-afk.sh docs/prd.md docs/plan.md 5
#
# Prerequisites:
#   1. Install sbx CLI:  brew install docker/tap/sbx
#   2. Login:            sbx login
#   3. Docker Desktop running

set -euo pipefail

PRD_FILE="${1:?Usage: ralph-afk.sh <PRD_FILE> <PLAN_FILE> [MAX_ITERATIONS]}"
PLAN_FILE="${2:?Usage: ralph-afk.sh <PRD_FILE> <PLAN_FILE> [MAX_ITERATIONS]}"
MAX_ITERATIONS="${3:-10}"

# Resolve to absolute paths
PRD_FILE="$(cd "$(dirname "$PRD_FILE")" && pwd)/$(basename "$PRD_FILE")"
PLAN_FILE="$(cd "$(dirname "$PLAN_FILE")" && pwd)/$(basename "$PLAN_FILE")"

# Check sbx is available
if ! command -v sbx &> /dev/null; then
  echo "ERROR: sbx CLI not found. Install with: brew install docker/tap/sbx"
  exit 1
fi

SANDBOX_NAME="claude-$(basename "$(pwd)")"

echo "=== Ralph AFK Loop ==="
echo "PRD:            $PRD_FILE"
echo "Plan:           $PLAN_FILE"
echo "Max Iterations: $MAX_ITERATIONS"
echo "Sandbox:        $SANDBOX_NAME"
echo "====================="
echo ""

for i in $(seq 1 "$MAX_ITERATIONS"); do
  echo "--- Iteration $i / $MAX_ITERATIONS ---"

  # Get latest 5 commits for context (refreshed each iteration)
  COMMITS=$(git log --oneline -5 2>/dev/null || echo "No commits yet")

  FULL_PROMPT="You are Ralph, an autonomous coding agent working inside a Docker sandbox.

## Previous Commits
$COMMITS

## PRD
$(cat "$PRD_FILE")

## Plan
$(cat "$PLAN_FILE")

## Instructions
Follow the plan and implement the next uncompleted phase. Work through the phases in order.

After completing your work:
1. Run relevant tests to verify your changes work
2. Commit with a descriptive message that includes: what changed, key decisions, files modified
3. If there are no more tasks to complete, output exactly: no more tasks

IMPORTANT:
- Do NOT ask for permission — just do the work
- Do NOT push to remote
- If you encounter environment issues (missing dependencies, import errors), run: pip install -r requirements.txt
- If you see sqlite3 / native module errors, try: pip install --force-reinstall pysqlite3"

  # Run Claude in Docker Sandbox via sbx
  RESULT=$(sbx run "$SANDBOX_NAME" claude . -- \
    --dangerously-skip-permissions \
    --print \
    --output-format stream-json \
    "$FULL_PROMPT" 2>&1) || true

  # Stream output to terminal
  echo "$RESULT"

  # Check if Claude signaled completion
  if echo "$RESULT" | grep -q "no more tasks"; then
    echo ""
    echo "=== Ralph complete after $i iteration(s) ==="
    exit 0
  fi

  echo ""
  echo "Iteration $i complete. Continuing..."
  echo ""
done

echo "=== Ralph stopped: reached max iterations ($MAX_ITERATIONS) ==="
exit 0
