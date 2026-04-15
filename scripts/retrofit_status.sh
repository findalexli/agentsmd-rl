#!/usr/bin/env bash
# Quick status report for the overnight retrofit run.
set -euo pipefail
cd "$(dirname "$0")/.."

LOG_DIR=$(ls -td pipeline_logs/retrofit_* 2>/dev/null | head -1)
if [[ -z "$LOG_DIR" ]]; then
  echo "No retrofit log dir found under pipeline_logs/"
  exit 1
fi
LOG="$LOG_DIR/run.log"

echo "═══════════════════════════════════════════════════════════════════"
echo "  RETROFIT STATUS — $LOG_DIR"
echo "═══════════════════════════════════════════════════════════════════"
echo "  Log: $LOG ($(wc -l < "$LOG" | tr -d ' ') lines)"
echo "  Started: $(head -5 "$LOG" | grep -oE '[0-9-]{10} [0-9:]{8}' | head -1)"
echo "  Latest : $(tail -1 "$LOG" | grep -oE '[0-9-]{10} [0-9:]{8}' | head -1)"
echo

# Is the retrofit process still running?
if ps -p 21841 >/dev/null 2>&1; then
  echo "  Process 21841: RUNNING"
else
  echo "  Process 21841: NOT RUNNING (may have completed or died)"
fi
echo

# Counts from log
done=$(grep -c " done," "$LOG" 2>/dev/null | tail -1 || echo 0)
valid=$(grep "Progress:" "$LOG" 2>/dev/null | tail -1 | grep -oE '[0-9]+ valid' | awk '{print $1}' || echo 0)
judge_done=$(grep -c "judge:" "$LOG" 2>/dev/null || echo 0)
reconcile_needed=$(grep -c "reconcile needed" "$LOG" 2>/dev/null || echo 0)
reconcile_done=$(grep -c "post-reconcile judge" "$LOG" 2>/dev/null || echo 0)
errors=$(grep -c "ERROR\|Traceback" "$LOG" 2>/dev/null || echo 0)
rate_limited=$(grep -c "rate-limited" "$LOG" 2>/dev/null || echo 0)
pass_count=$(grep -c " PASS " "$LOG" 2>/dev/null || echo 0)

echo "  ── Pipeline progress ──"
echo "  Tasks completed:        $pass_count"
echo "  Valid (nop=0, gold=1):  $valid"
echo "  Judge calls finished:   $judge_done"
echo "  Reconcile triggered:    $reconcile_needed"
echo "  Reconcile completed:    $reconcile_done"
echo "  Rate-limit events:      $rate_limited"
echo "  Errors / tracebacks:    $errors"
echo

echo "  ── Recent activity (last 10 PASS/FAIL events) ──"
grep -E "PASS|FAIL|ERROR" "$LOG" 2>/dev/null | tail -10 | sed 's/.*INFO: //; s/.*WARNING: /WARN: /; s/.*ERROR: /ERR:  /'
echo

echo "  ── Latest heartbeat ──"
grep "HEARTBEAT" "$LOG" 2>/dev/null | tail -1

echo

# Count actual quality.json files on disk (true success signal)
judged_on_disk=$(find harbor_tasks -maxdepth 2 -name quality.json 2>/dev/null | wc -l | tr -d ' ')
reconciled_on_disk=$(find harbor_tasks -maxdepth 2 -name reconcile_status.json 2>/dev/null | wc -l | tr -d ' ')
echo "  ── Disk state ──"
echo "  Tasks with quality.json:        $judged_on_disk"
echo "  Tasks with reconcile_status.json: $reconciled_on_disk"
echo

# E2B active sandboxes
if [[ -n "${E2B_API_KEY:-}" ]]; then
  active=$(curl -s -H "X-API-Key: $E2B_API_KEY" https://api.e2b.app/v2/sandboxes | .venv/bin/python -c "import json, sys; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "?")
  echo "  Active E2B sandboxes: $active"
fi
