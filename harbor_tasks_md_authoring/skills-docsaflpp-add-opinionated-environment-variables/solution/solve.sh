#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "`AFL_FINAL_SYNC` tells the primary instance to do a final import from all second" "plugins/testing-handbook-skills/skills/aflpp/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/testing-handbook-skills/skills/aflpp/SKILL.md b/plugins/testing-handbook-skills/skills/aflpp/SKILL.md
@@ -313,6 +313,63 @@ apt install gnuplot
 | `-m 1000` | Memory limit in megabytes (default: 0 = unlimited) |
 | `-x ./dict.dict` | Use dictionary file to guide mutations |
 
+## Environment Variables That Matter
+
+AFL++ has [many environment variables](https://aflplus.plus/docs/env_variables/), but most are niche. These are the ones that matter in practice.
+
+### Always Set These
+
+```bash
+# Every campaign should use tmpfs — SSDs will thank you, and it's faster
+AFL_TMPDIR=/dev/shm
+```
+
+`AFL_TMPDIR` is a free performance win with no downsides — not setting it wears out your SSD and slows fuzzing.
+
+### Slow Targets
+
+```bash
+# Speeds up calibration ~2.5x — use when targets are slow (e.g., >10 ms/exec)
+AFL_FAST_CAL=1
+```
+
+`AFL_FAST_CAL` reduces calibration time with negligible precision loss. Recommended specifically for slow targets where calibration would otherwise take a long time.
+
+### Multi-Core Campaigns
+
+```bash
+# On the primary (-M) instance only — needed for afl-cmin, not for fuzzing itself
+AFL_FINAL_SYNC=1
+
+# On all instances — cache test cases in memory (default: 50 MB, good range: 50-250 MB)
+AFL_TESTCACHE_SIZE=100
+```
+
+`AFL_FINAL_SYNC` tells the primary instance to do a final import from all secondaries when stopping. This does not affect the fuzzing process itself — it only matters when you later run `afl-cmin` for corpus minimization, ensuring the primary's queue has the full combined corpus. `AFL_TESTCACHE_SIZE` caches test cases in memory to reduce disk I/O; the default is 50 MB and values between 50-250 MB work well for most campaigns.
+
+### CI/Automated Fuzzing
+
+```bash
+# Fail fast if fuzzing isn't finding anything
+AFL_EXIT_ON_TIME=3600  # 1 hour with no new paths = stop
+
+# Or run until "done" (all queue entries processed)
+AFL_EXIT_WHEN_DONE=1
+
+# Headless environments
+AFL_NO_UI=1
+```
+
+Unbounded fuzzing in CI wastes resources. Set time limits or use exit conditions.
+
+### Variables to Avoid
+
+| Variable | Why Skip It |
+|----------|-------------|
+| `AFL_NO_ARITH` | Can hurt coverage on binary formats, but may be useful for text-based targets |
+| `AFL_SHUFFLE_QUEUE` | Only for exotic setups, usually harmful |
+| `AFL_DISABLE_TRIM` | Trimming is valuable, don't disable without reason |
+
 ## Multi-Core Fuzzing
 
 AFL++ excels at multi-core fuzzing with two major advantages:
PATCH

echo "Gold patch applied."
