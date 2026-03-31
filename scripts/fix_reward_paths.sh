#!/usr/bin/env bash
#
# Fix reward file paths in harbor task test.sh scripts.
#
# Harbor's verifier reads reward from /logs/verifier/reward.txt (mounted volume).
# Many tasks write to wrong paths (/tests/, /workspace/, /tmp/, etc.) that are
# invisible to Harbor. This script fixes them all.
#
# Usage:
#   bash scripts/fix_reward_paths.sh --dry-run    # Preview changes
#   bash scripts/fix_reward_paths.sh              # Apply changes
#
# The fixes are ordered most-specific → least-specific to avoid double-transforms.

set -euo pipefail

TASKS_DIR="${1:-harbor_tasks}"
DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=1
    TASKS_DIR="${2:-harbor_tasks}"
fi

CORRECT="/logs/verifier/reward"
FIXED=0
SKIPPED=0
ALREADY_CORRECT=0

log() { echo "[fix-reward] $*"; }

# Collect all test.sh files
mapfile -t TEST_FILES < <(find "$TASKS_DIR" -path "*/tests/test.sh" -type f | sort)
log "Found ${#TEST_FILES[@]} test.sh files"

# Count current state
CORRECT_COUNT=$(grep -rl "$CORRECT" "${TEST_FILES[@]}" 2>/dev/null | wc -l)
WRONG_COUNT=$(( ${#TEST_FILES[@]} - CORRECT_COUNT ))
log "Already correct: $CORRECT_COUNT, needs fix: ~$WRONG_COUNT"

for f in "${TEST_FILES[@]}"; do
    task_name=$(echo "$f" | sed "s|$TASKS_DIR/||;s|/tests/test.sh||")

    # Skip if already uses correct path and has no wrong paths
    if grep -q "$CORRECT" "$f" && ! grep -q '/tests/reward\.\|/workspace/reward\.\|/tmp/reward\.\|/repo/reward\.' "$f" 2>/dev/null; then
        (( ALREADY_CORRECT++ )) || true
        continue
    fi

    # Track if we changed anything
    changed=0

    # ── Pass 1: $TASK_DIR/tests/reward → /logs/verifier/reward ──────────
    # Most specific — must run BEFORE the /tests/reward pass to avoid
    # creating $TASK_DIR/logs/verifier/reward (wrong).
    if grep -q 'TASK_DIR.*/tests/reward\|TASK_DIR.*/reward\.' "$f" 2>/dev/null; then
        if (( DRY_RUN )); then
            log "  [DRY] $task_name: \$TASK_DIR/tests/reward → $CORRECT"
            grep -n 'TASK_DIR.*reward' "$f" | head -5
        else
            # Replace "$TASK_DIR/tests/reward.txt" → "/logs/verifier/reward.txt"
            sed -i 's|"\$TASK_DIR/tests/reward\.txt"|"/logs/verifier/reward.txt"|g' "$f"
            sed -i 's|"\$TASK_DIR/tests/reward\.json"|"/logs/verifier/reward.json"|g' "$f"
            # Also handle unquoted: $TASK_DIR/tests/reward.txt
            sed -i 's|\$TASK_DIR/tests/reward\.txt|/logs/verifier/reward.txt|g' "$f"
            sed -i 's|\$TASK_DIR/tests/reward\.json|/logs/verifier/reward.json|g' "$f"
            # Handle outlier: $TASK_DIR/reward.txt (areal-pad-packed-zero-length)
            sed -i 's|"\$TASK_DIR/reward\.txt"|"/logs/verifier/reward.txt"|g' "$f"
            sed -i 's|"\$TASK_DIR/reward\.json"|"/logs/verifier/reward.json"|g' "$f"
            sed -i 's|\$TASK_DIR/reward\.txt|/logs/verifier/reward.txt|g' "$f"
            sed -i 's|\$TASK_DIR/reward\.json|/logs/verifier/reward.json|g' "$f"
            # Handle Python f-string: {TASK_DIR}/tests/reward
            sed -i 's|{TASK_DIR}/tests/reward\.txt|/logs/verifier/reward.txt|g' "$f"
            sed -i 's|{TASK_DIR}/tests/reward\.json|/logs/verifier/reward.json|g' "$f"
        fi
        changed=1
    fi

    # ── Pass 2: $REPO/reward → /logs/verifier/reward ────────────────────
    if grep -q '"$REPO/reward\.\|$REPO/reward\.\|$REPO/../reward\.' "$f" 2>/dev/null; then
        if (( DRY_RUN )); then
            log "  [DRY] $task_name: \$REPO/reward → $CORRECT"
            grep -n 'REPO.*reward' "$f" | head -5
        else
            sed -i 's|"\$REPO/reward\.txt"|"/logs/verifier/reward.txt"|g' "$f"
            sed -i 's|"\$REPO/reward\.json"|"/logs/verifier/reward.json"|g' "$f"
            sed -i 's|\$REPO/reward\.txt|/logs/verifier/reward.txt|g' "$f"
            sed -i 's|\$REPO/reward\.json|/logs/verifier/reward.json|g' "$f"
            # Handle $REPO/../reward (openclaw tasks)
            sed -i 's|"\$REPO/\.\./reward\.txt"|"/logs/verifier/reward.txt"|g' "$f"
            sed -i 's|"\$REPO/\.\./reward\.json"|"/logs/verifier/reward.json"|g' "$f"
            sed -i 's|\$REPO/\.\./reward\.txt|/logs/verifier/reward.txt|g' "$f"
            sed -i 's|\$REPO/\.\./reward\.json|/logs/verifier/reward.json|g' "$f"
        fi
        changed=1
    fi

    # ── Pass 3: REWARD_FILE="/tests/reward.txt" variable definitions ────
    # Some tasks define REWARD_FILE="/tests/reward.txt" and use $REWARD_FILE.
    # Fix the definition; all uses propagate automatically.
    if grep -q 'REWARD_FILE=.*/tests/reward\|REWARD_JSON=.*/tests/reward' "$f" 2>/dev/null; then
        if (( DRY_RUN )); then
            log "  [DRY] $task_name: REWARD_FILE=/tests/ → $CORRECT"
            grep -n 'REWARD_FILE\|REWARD_JSON' "$f" | head -5
        else
            sed -i 's|REWARD_FILE="/tests/reward\.txt"|REWARD_FILE="/logs/verifier/reward.txt"|g' "$f"
            sed -i 's|REWARD_JSON="/tests/reward\.json"|REWARD_JSON="/logs/verifier/reward.json"|g' "$f"
        fi
        changed=1
    fi

    # ── Pass 4: /workspace/ruff/reward → /logs/verifier/reward ──────────
    # Must run BEFORE generic /workspace/reward to avoid partial match.
    if grep -q '/workspace/ruff/reward\.' "$f" 2>/dev/null; then
        if (( DRY_RUN )); then
            log "  [DRY] $task_name: /workspace/ruff/reward → $CORRECT"
        else
            sed -i 's|/workspace/ruff/reward|/logs/verifier/reward|g' "$f"
        fi
        changed=1
    fi

    # ── Pass 5: /workspace/next.js/reward → /logs/verifier/reward ───────
    if grep -q '/workspace/next\.js/reward\.' "$f" 2>/dev/null; then
        if (( DRY_RUN )); then
            log "  [DRY] $task_name: /workspace/next.js/reward → $CORRECT"
        else
            sed -i 's|/workspace/next\.js/reward|/logs/verifier/reward|g' "$f"
        fi
        changed=1
    fi

    # ── Pass 6: /workspace/repo/reward → /logs/verifier/reward ──────────
    if grep -q '/workspace/repo/reward\.' "$f" 2>/dev/null; then
        if (( DRY_RUN )); then
            log "  [DRY] $task_name: /workspace/repo/reward → $CORRECT"
        else
            sed -i 's|/workspace/repo/reward|/logs/verifier/reward|g' "$f"
        fi
        changed=1
    fi

    # ── Pass 7: /workspace/reward → /logs/verifier/reward ───────────────
    # Generic /workspace/reward.* (after project-specific paths handled above)
    if grep -q '/workspace/reward\.' "$f" 2>/dev/null; then
        if (( DRY_RUN )); then
            log "  [DRY] $task_name: /workspace/reward → $CORRECT"
        else
            sed -i 's|/workspace/reward|/logs/verifier/reward|g' "$f"
        fi
        changed=1
    fi

    # ── Pass 8: /tests/reward → /logs/verifier/reward ───────────────────
    # After $TASK_DIR and REWARD_FILE passes already handled their cases.
    if grep -q '> */tests/reward\.\|>/tests/reward\.\|> /tests/reward\.\|open(.*/tests/reward' "$f" 2>/dev/null; then
        if (( DRY_RUN )); then
            log "  [DRY] $task_name: /tests/reward → $CORRECT"
        else
            sed -i "s|/tests/reward|/logs/verifier/reward|g" "$f"
        fi
        changed=1
    fi

    # ── Pass 9: /tmp/reward → /logs/verifier/reward ─────────────────────
    if grep -q '/tmp/reward\.' "$f" 2>/dev/null; then
        if (( DRY_RUN )); then
            log "  [DRY] $task_name: /tmp/reward → $CORRECT"
        else
            sed -i 's|/tmp/reward|/logs/verifier/reward|g' "$f"
        fi
        changed=1
    fi

    # ── Pass 10: /repo/reward → /logs/verifier/reward ───────────────────
    if grep -q '/repo/reward\.' "$f" 2>/dev/null; then
        if (( DRY_RUN )); then
            log "  [DRY] $task_name: /repo/reward → $CORRECT"
        else
            sed -i 's|/repo/reward|/logs/verifier/reward|g' "$f"
        fi
        changed=1
    fi

    if (( changed )); then
        (( FIXED++ )) || true
    fi
done

log ""
log "=== Summary ==="
log "Already correct: $ALREADY_CORRECT"
log "Fixed: $FIXED"
log "Total: ${#TEST_FILES[@]}"

if (( DRY_RUN )); then
    log "(dry run — no files modified)"
else
    # Verify: count how many now use the correct path
    AFTER_CORRECT=$(grep -rl "$CORRECT" "${TEST_FILES[@]}" 2>/dev/null | wc -l)
    AFTER_WRONG=$(grep -rl 'reward\.txt\|reward\.json' "${TEST_FILES[@]}" 2>/dev/null | grep -v "$CORRECT" | grep -v 'LOG_DIR\|LOGS\|REWARD_FILE\|REWARD_JSON' | wc -l || true)
    log "After fix: $AFTER_CORRECT using correct path"
    if (( AFTER_WRONG > 0 )); then
        log "WARNING: $AFTER_WRONG files may still have wrong paths. Inspect manually:"
        grep -rl 'reward\.txt\|reward\.json' "${TEST_FILES[@]}" 2>/dev/null | while read -r ff; do
            if ! grep -q "$CORRECT" "$ff" && ! grep -q 'LOG_DIR\|LOGS.*reward\|REWARD_FILE\|REWARD_JSON' "$ff"; then
                echo "  $ff"
            fi
        done | head -10
    fi
fi
