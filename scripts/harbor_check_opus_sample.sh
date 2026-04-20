#!/usr/bin/env bash
# Run harbor check with Opus 4.6 on a 10% sample for haiku reliability check.
set -euo pipefail
cd "$(dirname "$0")/.."
set -a
source .env
set +a

TASK_DIR=${TASK_DIR:-harbor_tasks}
# Use the SAME task list as the haiku audit, but 10% sample
HAIKU_RUN=$(ls -td pipeline_logs/harbor_check_* | head -1)
if [ ! -f "$HAIKU_RUN/task_list.txt" ]; then
  echo "ERROR: haiku audit task_list.txt not found at $HAIKU_RUN"
  exit 1
fi

OUT_DIR="$HAIKU_RUN"/opus_sample
mkdir -p "$OUT_DIR"
CONCURRENCY=${CONCURRENCY:-4}

# 10% random sample (seeded)
.venv/bin/python -c "
import random
random.seed(42)
lines = [l.strip() for l in open('$HAIKU_RUN/task_list.txt') if l.strip()]
sample = random.sample(lines, max(10, len(lines) // 10))
print('\n'.join(sample))
" > "$OUT_DIR/sample_tasks.txt"

n=$(wc -l < "$OUT_DIR/sample_tasks.txt")
echo "Opus sample: $n tasks (10% of $(wc -l < $HAIKU_RUN/task_list.txt))"
echo "Output: $OUT_DIR"
echo

check_one() {
  local t="$1"
  local out="$OUT_DIR/${t}.json"
  if [ -f "$out" ]; then echo "  skip $t (cached)"; return 0; fi
  if timeout 240 harbor check -m opus -o "$out" "$TASK_DIR/$t" > "$OUT_DIR/${t}.log" 2>&1; then
    echo "  ✓ $t"
  else
    echo "  ✗ $t (err)"
  fi
}
export -f check_one
export OUT_DIR TASK_DIR

xargs -a "$OUT_DIR/sample_tasks.txt" -n 1 -P "$CONCURRENCY" -I {} bash -c 'check_one "$@"' _ {}

echo
echo "=== Comparing Haiku vs Opus on sample ==="
.venv/bin/python -c "
import json, os
from pathlib import Path
from collections import Counter

haiku_dir = Path('$HAIKU_RUN')
opus_dir = Path('$OUT_DIR')
sample = [l.strip() for l in open(opus_dir / 'sample_tasks.txt') if l.strip()]

agree = Counter()
disagree = Counter()
total_per_crit = Counter()

for t in sample:
    haiku_f = haiku_dir / f'{t}.json'
    opus_f = opus_dir / f'{t}.json'
    if not haiku_f.exists() or not opus_f.exists():
        continue
    try:
        h = json.loads(haiku_f.read_text())['checks']
        o = json.loads(opus_f.read_text())['checks']
    except: continue
    for crit in set(h.keys()) & set(o.keys()):
        total_per_crit[crit] += 1
        if h[crit]['outcome'] == o[crit]['outcome']:
            agree[crit] += 1
        else:
            disagree[crit] += 1

print('Per-criterion agreement rate (haiku vs opus):')
for crit in sorted(total_per_crit.keys()):
    tot = total_per_crit[crit]
    a = agree[crit]
    print(f'  {crit}: {a}/{tot} = {a/max(1,tot)*100:.0f}% agreement')
"
