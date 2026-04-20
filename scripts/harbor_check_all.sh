#!/usr/bin/env bash
# Batch-run harbor check across all tasks in harbor_tasks/, parallelized.
# Uses Claude Haiku (fast, cheap: ~$0.25/M input).
# Writes per-task JSON results to pipeline_logs/harbor_check/<task>.json
# Output: summary CSV + aggregate stats.
set -euo pipefail
cd "$(dirname "$0")/.."
set -a
source .env
set +a

TASK_DIR=${TASK_DIR:-harbor_tasks}
OUT_DIR=pipeline_logs/harbor_check_$(date +%Y%m%d_%H%M)
mkdir -p "$OUT_DIR"
CONCURRENCY=${CONCURRENCY:-8}

# Collect all tasks with environment/Dockerfile + tests/ + instruction.md
tasks=()
for t in $(ls "$TASK_DIR"/); do
  d="$TASK_DIR/$t"
  if [ -d "$d/environment" ] && [ -f "$d/instruction.md" ] && [ -d "$d/tests" ]; then
    tasks+=("$t")
  fi
done
echo "Tasks to check: ${#tasks[@]}"
echo "Output dir: $OUT_DIR"
echo "Concurrency: $CONCURRENCY"
echo

# Write task list
printf '%s\n' "${tasks[@]}" > "$OUT_DIR/task_list.txt"

# Parallel launcher (xargs -P)
check_one() {
  local t="$1"
  local out="$OUT_DIR/${t}.json"
  if [ -f "$out" ]; then
    echo "  skip $t (cached)"; return 0
  fi
  if timeout 180 harbor check -m haiku -o "$out" "$TASK_DIR/$t" > "$OUT_DIR/${t}.log" 2>&1; then
    echo "  ✓ $t"
  else
    echo "  ✗ $t (err)"
  fi
}
export -f check_one
export OUT_DIR TASK_DIR

printf '%s\0' "${tasks[@]}" | xargs -0 -n 1 -P "$CONCURRENCY" -I {} bash -c 'check_one "$@"' _ {}

echo
echo "=== Aggregating results ==="
.venv/bin/python -c "
import json, os
from pathlib import Path
from collections import Counter, defaultdict

out_dir = Path('$OUT_DIR')
results = {}
for f in out_dir.glob('*.json'):
    try:
        d = json.loads(f.read_text())
        results[f.stem] = d.get('checks', {})
    except Exception as e:
        pass

print(f'Parsed {len(results)} task reports')
print()

# Aggregate per-check outcomes
crit_totals = defaultdict(Counter)
for task, checks in results.items():
    for name, info in checks.items():
        crit_totals[name][info.get('outcome', '?')] += 1

print('Per-criterion pass rates:')
for name in sorted(crit_totals.keys()):
    c = crit_totals[name]
    total = sum(c.values())
    pass_n = c.get('pass', 0)
    print(f'  {name}: {pass_n}/{total} pass ({pass_n/max(1,total)*100:.0f}%)  | ' + ', '.join(f'{k}={v}' for k,v in c.most_common()))

# Tasks that FAIL the most critical checks
print()
print('Top 15 FAIL-prone tasks (by # of failed checks):')
task_fail_counts = {t: sum(1 for ch in chs.values() if ch.get('outcome') == 'fail') for t, chs in results.items()}
for t, n in sorted(task_fail_counts.items(), key=lambda x: -x[1])[:15]:
    print(f'  {t}: {n} fails')

# Tasks with spec-solution coupling issues
print()
print('Tasks FAILING behavior_in_task_description (spec too vague):')
bad_spec = [t for t, chs in results.items() if chs.get('behavior_in_task_description', {}).get('outcome') == 'fail']
print(f'  count: {len(bad_spec)}')
for t in bad_spec[:10]:
    reason = results[t]['behavior_in_task_description'].get('explanation', '')[:100]
    print(f'  {t}: {reason}')

# Write summary
with open(out_dir / 'SUMMARY.json', 'w') as f:
    json.dump({
        'tasks_checked': len(results),
        'criterion_outcomes': {k: dict(v) for k, v in crit_totals.items()},
        'tasks_with_fails': {t: n for t, n in task_fail_counts.items() if n > 0},
        'bad_spec_tasks': bad_spec,
    }, f, indent=2)
print()
print(f'Summary: {out_dir}/SUMMARY.json')
"
