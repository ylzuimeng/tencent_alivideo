#!/usr/bin/env bash
# ralph-once.sh — Run Claude once in Docker Sandbox (HITL test mode)
#
# Usage:
#   bash scripts/ralph-once.sh <PRD_FILE> <PLAN_FILE> [PROMPT]
#
# Example:
#   bash scripts/ralph-once.sh docs/prd.md docs/plan.md "Implement phase 1"
#
# Prerequisites:
#   1. Install sbx CLI:  brew install docker/tap/sbx
#   2. Login:            sbx login
#   3. Docker Desktop running

set -euo pipefail

PRD_FILE="${1:?Usage: ralph-once.sh <PRD_FILE> <PLAN_FILE> [PROMPT]}"
PLAN_FILE="${2:?Usage: ralph-once.sh <PRD_FILE> <PLAN_FILE> [PROMPT]}"
PROMPT="${3:-Follow the plan and implement the next phase.}"

# Resolve to absolute paths
PRD_FILE="$(cd "$(dirname "$PRD_FILE")" && pwd)/$(basename "$PRD_FILE")"
PLAN_FILE="$(cd "$(dirname "$PLAN_FILE")" && pwd)/$(basename "$PLAN_FILE")"

# Check sbx is available
if ! command -v sbx &> /dev/null; then
  echo "ERROR: sbx CLI not found. Install with: brew install docker/tap/sbx"
  exit 1
fi

# Get last 5 commits for context
COMMITS=$(git log --oneline -5 2>/dev/null || echo "No commits yet")

# Build the prompt
FULL_PROMPT="You are Ralph, an autonomous coding agent working inside a Docker sandbox.

## Previous Commits
$COMMITS

## PRD
$(cat "$PRD_FILE")

## Plan
$(cat "$PLAN_FILE")

## Instructions
$PROMPT

After completing your work:
1. Run tests to verify your changes
2. Commit with a descriptive message
3. If there are no more tasks to complete, output exactly: no more tasks

If you encounter environment issues (missing dependencies, import errors), run:
  pip install -r requirements.txt"

SANDBOX_NAME="claude-$(basename "$(pwd)")"

echo "=== Ralph ONCE ==="
echo "PRD:     $PRD_FILE"
echo "Plan:    $PLAN_FILE"
echo "Prompt:  $PROMPT"
echo "Sandbox: $SANDBOX_NAME"
echo "=================="
echo ""

# Run Claude in Docker Sandbox via sbx
# --dangerously-skip-permissions: no permission prompts (AFK mode)
# --print: non-interactive, output to stdout
sbx run "$SANDBOX_NAME" claude . -- \
  --dangerously-skip-permissions \
  --print \
  "$FULL_PROMPT"
