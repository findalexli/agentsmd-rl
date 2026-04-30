#!/usr/bin/env bash
set -euo pipefail

cd /workspace/megatron-bridge

# Idempotency guard
if grep -qF "skills/perf-techniques/memory-tuning/SKILL.md" "skills/perf-techniques/memory-tuning/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/perf-techniques/memory-tuning/SKILL.md b/skills/perf-techniques/memory-tuning/SKILL.md
@@ -212,7 +212,6 @@ model_config = GPTModelProvider(
 
 ## Known Limitations
 
-- `expandable_segments:True` is incompatible with NCCL user-buffer registration
 - CPU offloading is blocked when PP > 1
 - Parallelism resizing (TP/PP) often has significant throughput costs
 - No automatic memory profiling to recommend the optimal strategy
PATCH

echo "Gold patch applied."
