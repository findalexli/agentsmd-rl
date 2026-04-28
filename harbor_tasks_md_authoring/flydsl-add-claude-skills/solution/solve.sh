#!/usr/bin/env bash
set -euo pipefail

cd /workspace/flydsl

# Idempotency guard
if grep -qF "User: /bisect-perf-regression v0.1.0 v0.2.0 -- python -m pytest tests/bench.py -" ".claude/skills/bisect-perf-regression/SKILL.md" && grep -qF "| `[container@host]` | No | Target in format `container@hostname`. If omitted, b" ".claude/skills/build-flydsl/SKILL.md" && grep -qF "description: Connect to a remote host via SSH and build a Docker image with rocp" ".claude/skills/build-rocm-image/SKILL.md" && grep -qF "`gpu.barrier()` requires ALL threads in the workgroup to reach it. If some threa" ".claude/skills/debug-flydsl-kernel/SKILL.md" && grep -qF "FlyDSL is a Python DSL and MLIR-based compiler for writing high-performance GPU " ".claude/skills/flydsl-kernel-authoring/SKILL.md" && grep -qF "Use this skill whenever the user says \"format code\", \"clean up code\", \"lint\", \"f" ".claude/skills/format-code/SKILL.md" && grep -qF "| High `s_waitcnt vmcnt(0)` stall before MFMA | Global load latency exposed | Im" ".claude/skills/gemm-optimization/SKILL.md" && grep -qF "- **VGPR context**: LDS ops use **arch_vgpr** (not accum_vgpr). On CDNA3, arch_v" ".claude/skills/lds-optimization/SKILL.md" && grep -qF "- **Don't assume occupancy can increase**: on MI308 with 512 max VGPRs, adding p" ".claude/skills/prefetch-data-load/SKILL.md" && grep -qF "FlyDSL (Flexible Layout Python DSL) \u2014 a Python DSL and MLIR-based compiler stack" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/bisect-perf-regression/SKILL.md b/.claude/skills/bisect-perf-regression/SKILL.md
@@ -0,0 +1,531 @@
+---
+name: bisect-perf-regression
+description: >
+  Find the exact commit that caused a GPU kernel performance regression using
+  binary search (git bisect). Given a good commit (fast), a bad commit (slow,
+  defaults to HEAD), and a benchmark command, automatically checks out commits,
+  runs the benchmark, extracts the metric, and narrows down to the offending
+  commit. Reports the regression commit with its diff and suggested root cause.
+  Usage: /bisect-perf-regression <good_commit> [bad_commit] -- <bench_cmd>
+tools: Bash,Read,Grep,Glob,Agent
+---
+
+# Bisect Performance Regression
+
+Find the exact git commit that introduced a kernel performance regression using
+binary search.
+
+## Arguments
+
+| Argument | Required | Default | Description |
+|----------|----------|---------|-------------|
+| `<GOOD_COMMIT>` | Yes | — | Commit hash or tag where performance was acceptable |
+| `<BAD_COMMIT>` | No | `HEAD` | Commit hash where performance has regressed |
+| `<BENCH_CMD>` | Yes | — | Benchmark command that prints a performance metric |
+
+The arguments are parsed from the user's input. Typical invocations:
+
+```
+/bisect-perf-regression abc1234 def5678 -- python bench_pa.py --batch 32
+/bisect-perf-regression v0.2.0 -- pytest tests/test_perf.py -k test_decode
+/bisect-perf-regression abc1234 -- ./run_bench.sh
+```
+
+If any required argument is missing, ask the user before proceeding.
+
+## Prerequisites
+
+- Must be inside a git repository
+- Working tree should be clean (no uncommitted changes) — the skill will
+  `git stash` if needed and restore at the end
+- The benchmark command must be runnable at every commit in the range
+  (dependencies must be compatible)
+- If a build step is needed between checkouts (e.g., `pip install -e .`),
+  the user must include it in the bench command or specify it separately
+
+## Algorithm
+
+```
+Binary search over commits between GOOD and BAD:
+
+1. Establish baseline: run bench at GOOD, run bench at BAD
+2. Verify regression exists: bad_metric must be significantly worse than good_metric
+3. Bisect: pick midpoint commit, run bench, classify as good or bad
+4. Repeat until a single commit is identified
+5. Report the offending commit with diff and analysis
+```
+
+---
+
+## Step 0: Validate Environment
+
+Before starting, verify the environment is ready:
+
+```bash
+# Must be in a git repo
+git rev-parse --is-inside-work-tree
+
+# Check that both commits exist
+git cat-file -t <GOOD_COMMIT>
+git cat-file -t <BAD_COMMIT>
+
+# Check working tree is clean
+git status --porcelain
+```
+
+If working tree is dirty:
+1. Show the user what's uncommitted
+2. Ask: "Stash uncommitted changes before bisecting? They will be restored afterward."
+3. If approved: `git stash push -m "bisect-perf-regression: auto-stash"`
+4. Set a flag to `git stash pop` at the end
+
+Save the current branch/commit to restore later:
+
+```bash
+ORIGINAL_REF=$(git symbolic-ref --short HEAD 2>/dev/null || git rev-parse HEAD)
+```
+
+---
+
+## Step 1: Enumerate Commits
+
+List all commits in the bisect range:
+
+```bash
+git rev-list --reverse <GOOD_COMMIT>..<BAD_COMMIT>
+```
+
+Report to user:
+
+```
+Bisect range: <GOOD_COMMIT_SHORT>..<BAD_COMMIT_SHORT>
+Total commits in range: N
+Estimated bisect steps: ceil(log2(N))
+```
+
+If > 100 commits, warn the user about the time cost.
+If 0 commits, the range is invalid — ask the user to check the commits.
+
+---
+
+## Step 2: Establish Baselines
+
+Run the benchmark at both endpoints to confirm the regression exists
+and to calibrate the metric.
+
+### 2.1 Determine the performance metric
+
+Ask the user how to extract the metric if not obvious. Common patterns:
+
+| Benchmark Output | Extraction Method |
+|------------------|-------------------|
+| `Latency: 1.23 ms` | `grep -oP 'Latency:\s*\K[\d.]+'` |
+| `Throughput: 456 GB/s` | `grep -oP 'Throughput:\s*\K[\d.]+'` |
+| `kernel_time_us: 789` | `grep -oP 'kernel_time_us:\s*\K[\d.]+'` |
+| JSON output `{"time": 1.23}` | `python3 -c "import json,sys; print(json.load(sys.stdin)['time'])"` |
+| pytest duration | `grep -oP '\d+\.\d+s'` |
+
+If the user doesn't specify, attempt auto-detection:
+1. Run the bench command once at the current commit
+2. Show the output and ask: "Which number is the performance metric?
+   Should lower be better (latency) or higher be better (throughput)?"
+
+The user must confirm:
+- **Metric extraction command** (grep/awk/python one-liner)
+- **Polarity**: `lower_is_better` (latency, time) or `higher_is_better` (throughput, bandwidth)
+
+### 2.2 Run baselines
+
+```bash
+# Baseline: GOOD commit
+git checkout <GOOD_COMMIT> --quiet
+# Optional build step if user specified
+<BUILD_CMD>
+# Run benchmark (multiple times for stability)
+for i in 1 2 3; do <BENCH_CMD> 2>&1 | <METRIC_EXTRACTION>; done
+```
+
+Take the **median** of 3 runs as the baseline value.
+
+```bash
+# Baseline: BAD commit
+git checkout <BAD_COMMIT> --quiet
+<BUILD_CMD>
+for i in 1 2 3; do <BENCH_CMD> 2>&1 | <METRIC_EXTRACTION>; done
+```
+
+Report baselines:
+
+```
+Baseline results:
+  GOOD (<GOOD_SHORT>): <metric> = <value> <unit>
+  BAD  (<BAD_SHORT>):  <metric> = <value> <unit>
+  Regression: <percentage>% <worse_direction>
+```
+
+### 2.3 Validate regression
+
+Calculate regression percentage:
+
+```python
+if lower_is_better:
+    regression_pct = (bad_value - good_value) / good_value * 100
+else:
+    regression_pct = (good_value - bad_value) / good_value * 100
+```
+
+- If regression < 5%: warn that the difference may be noise. Ask user to
+  confirm the threshold or increase run count.
+- If regression < 0%: the "bad" commit is actually faster — the commits may
+  be swapped. Ask the user.
+
+Set the **threshold** for classifying a commit as "bad":
+
+```python
+# A commit is "bad" if its metric is within 30% of the regression toward the bad value
+# This accounts for noise and gradual changes
+threshold = good_value + (bad_value - good_value) * 0.3  # for lower_is_better
+```
+
+Let the user override this threshold if needed.
+
+---
+
+## Step 3: Binary Search (Bisect)
+
+### 3.1 Bisect loop
+
+```python
+commits = [list of commits from git rev-list]
+lo = 0                    # index of last known good
+hi = len(commits) - 1     # index of first known bad
+
+step = 0
+while lo + 1 < hi:
+    step += 1
+    mid = (lo + hi) // 2
+    commit = commits[mid]
+
+    # Checkout and benchmark
+    git checkout <commit> --quiet
+    <BUILD_CMD>
+    results = [run_bench() for _ in range(3)]
+    metric = median(results)
+
+    # Classify
+    if is_bad(metric, threshold):
+        hi = mid
+        verdict = "BAD"
+    else:
+        lo = mid
+        verdict = "GOOD"
+
+    print(f"Step {step}: {commit[:8]} = {metric} -> {verdict}  (remaining: {hi-lo-1})")
+
+# The first bad commit is commits[hi]
+regression_commit = commits[hi]
+last_good_commit = commits[lo]
+```
+
+### 3.2 Step-by-step reporting
+
+After each bisect step, report progress:
+
+```
+Step 1/7: testing abc1234... metric=1.45ms -> GOOD (6 commits remaining)
+Step 2/7: testing def5678... metric=2.31ms -> BAD  (3 commits remaining)
+Step 3/7: testing 789abcd... metric=1.52ms -> GOOD (1 commit remaining)
+...
+```
+
+### 3.3 Handle edge cases
+
+**Build failure at a commit**:
+- If the build or benchmark fails (non-zero exit code), skip this commit
+- Expand the search: try the adjacent commit in the same direction
+- If 3 consecutive commits fail, ask the user for guidance
+
+**Flaky results (close to threshold)**:
+- If the metric is within 10% of the threshold, run 5 iterations instead of 3
+- If still ambiguous, report it and ask the user to classify manually
+
+**Merge commits**:
+- By default, follow first-parent only: `git rev-list --first-parent`
+- If the regression commit is a merge, offer to re-bisect within the merged branch
+
+---
+
+## Step 4: Report the Regression Commit
+
+Once the bisect is complete:
+
+```bash
+# Show the offending commit
+git log -1 --format='%H%n%an <%ae>%n%ai%n%s%n%n%b' <REGRESSION_COMMIT>
+
+# Show the diff
+git diff <LAST_GOOD>..<REGRESSION_COMMIT> --stat
+git diff <LAST_GOOD>..<REGRESSION_COMMIT>
+```
+
+### 4.1 Generate the report
+
+```
+============================================================
+PERFORMANCE REGRESSION BISECT RESULT
+============================================================
+
+Regression introduced by:
+  Commit:  <full_hash>
+  Author:  <author>
+  Date:    <date>
+  Message: <commit message>
+
+Performance impact:
+  Before (<LAST_GOOD_SHORT>): <metric> = <good_value>
+  After  (<REGRESSION_SHORT>): <metric> = <bad_value>
+  Regression: <pct>% <direction>
+
+Files changed:
+  <file_list with +/- line counts>
+
+Bisect log:
+  Step 1: <commit> = <value> -> GOOD
+  Step 2: <commit> = <value> -> BAD
+  ...
+
+============================================================
+```
+
+### 4.2 Analyze the diff for root cause
+
+Read the diff and look for common regression patterns:
+
+| Pattern | Example | Likely Cause |
+|---------|---------|--------------|
+| Changed loop bounds | `range(N)` -> `range(N*2)` | More iterations, doubled work |
+| Added synchronization | Added `s_barrier`, `tl.debug_barrier()` | Extra sync stalls |
+| Changed tile sizes | `BLOCK_SIZE=64` -> `BLOCK_SIZE=32` | Worse occupancy or more iterations |
+| Added memory ops | New `tl.load` / `gl.load` inside loop | More memory traffic |
+| Changed dtype | `fp16` -> `fp32` | 2x memory bandwidth, 2x register pressure |
+| Removed prefetch | Deleted double-buffer logic | Load latency exposed |
+| Changed `waves_per_eu` | `waves_per_eu=2` -> `waves_per_eu=1` | Reduced occupancy |
+| Added masking | New `tl.where` / boundary checks | Extra ALU + potential branch divergence |
+| Refactored layout | Changed `BlockedLayout` params | Possible bank conflicts or non-coalesced access |
+| Added `num_stages` change | `num_stages=1` -> `num_stages=2` | Triton pipelining change |
+
+Provide a short root cause hypothesis based on the diff.
+
+---
+
+## Step 5: Cleanup
+
+Restore the original state:
+
+```bash
+# Return to original branch/commit
+git checkout <ORIGINAL_REF> --quiet
+
+# Restore stashed changes if any
+git stash pop  # only if we stashed in Step 0
+```
+
+Verify the working tree is back to its original state:
+
+```bash
+git status
+git log -1 --oneline
+```
+
+---
+
+## Complete Execution Script
+
+Here is the full procedure as pseudocode for reference:
+
+```python
+# === INPUTS ===
+good_commit = "<GOOD_COMMIT>"
+bad_commit  = "<BAD_COMMIT>"   # default: HEAD
+bench_cmd   = "<BENCH_CMD>"
+build_cmd   = "<BUILD_CMD>"    # optional, default: ""
+metric_cmd  = "<METRIC_EXTRACTION>"
+lower_is_better = True         # or False for throughput
+num_runs    = 3                # runs per commit
+
+# === SAVE STATE ===
+original_ref = run("git symbolic-ref --short HEAD 2>/dev/null || git rev-parse HEAD")
+stashed = False
+if run("git status --porcelain").strip():
+    run("git stash push -m 'bisect-perf-regression: auto-stash'")
+    stashed = True
+
+# === ENUMERATE ===
+commits = run(f"git rev-list --reverse {good_commit}..{bad_commit}").splitlines()
+total = len(commits)
+steps = ceil(log2(total))
+print(f"Bisecting {total} commits (~{steps} steps)")
+
+# === BASELINES ===
+def bench(commit):
+    run(f"git checkout {commit} --quiet")
+    if build_cmd:
+        run(build_cmd)
+    values = []
+    for _ in range(num_runs):
+        output = run(f"{bench_cmd} 2>&1")
+        val = float(run(f"echo '{output}' | {metric_cmd}"))
+        values.append(val)
+    return median(values)
+
+good_val = bench(good_commit)
+bad_val  = bench(bad_commit)
+regression_pct = abs(bad_val - good_val) / good_val * 100
+
+if lower_is_better:
+    threshold = good_val + (bad_val - good_val) * 0.3
+    is_bad = lambda v: v > threshold
+else:
+    threshold = good_val - (good_val - bad_val) * 0.3
+    is_bad = lambda v: v < threshold
+
+# === BISECT ===
+lo, hi = -1, total  # -1 = good_commit, total = bad_commit (virtual indices)
+# Map: -1 -> good_commit, 0..total-1 -> commits[], total -> bad_commit
+def get_commit(idx):
+    if idx == -1: return good_commit
+    if idx == total: return bad_commit
+    return commits[idx]
+
+lo, hi = -1, total
+step = 0
+log_entries = []
+
+while hi - lo > 1:
+    step += 1
+    mid = (lo + hi) // 2
+    commit = get_commit(mid)
+    try:
+        val = bench(commit)
+        bad = is_bad(val)
+    except Exception as e:
+        # Build/bench failure — skip this commit
+        print(f"Step {step}: {commit[:8]} SKIP (error: {e})")
+        # Try shifting mid toward hi
+        mid += 1
+        if mid >= hi:
+            mid = (lo + hi) // 2 - 1
+        if mid <= lo:
+            print("Cannot find testable commit in range")
+            break
+        commit = get_commit(mid)
+        val = bench(commit)
+        bad = is_bad(val)
+
+    if bad:
+        hi = mid
+        verdict = "BAD"
+    else:
+        lo = mid
+        verdict = "GOOD"
+
+    remaining = hi - lo - 1
+    log_entries.append(f"Step {step}: {commit[:8]} = {val} -> {verdict} ({remaining} left)")
+    print(log_entries[-1])
+
+first_bad = get_commit(hi)
+last_good = get_commit(lo)
+
+# === REPORT ===
+print(f"\nRegression commit: {first_bad}")
+run(f"git log -1 {first_bad}")
+run(f"git diff {last_good}..{first_bad}")
+
+# === CLEANUP ===
+run(f"git checkout {original_ref} --quiet")
+if stashed:
+    run("git stash pop")
+```
+
+---
+
+## Configuration Options
+
+The user may customize these via conversation:
+
+| Option | Default | Description |
+|--------|---------|-------------|
+| `num_runs` | 3 | Benchmark iterations per commit (more = less noise) |
+| `threshold_pct` | 30% | % of regression gap to classify bad (lower = stricter) |
+| `build_cmd` | none | Command to run after checkout (e.g., `pip install -e .`) |
+| `first_parent` | true | Follow first-parent only (skip merge internals) |
+| `timeout` | 600s | Max time per benchmark run |
+| `skip_on_fail` | true | Skip commits where build/bench fails |
+| `warmup_runs` | 1 | Discard first N runs before measuring |
+
+---
+
+## Error Handling
+
+- **Benchmark command not found**: Check PATH, suggest activating venv or conda
+- **Build failure**: Show error, try adjacent commit, report if > 3 failures
+- **Metric extraction fails**: Show raw output, ask user to fix the extraction
+- **Git checkout conflict**: `git checkout -f` only if user approves
+- **Interrupted (Ctrl+C)**: Restore original branch before exiting
+- **Regression not found**: If all commits are "good", the regression may be
+  environmental (driver, library, hardware thermal). Suggest running the bad
+  commit again to confirm.
+
+## Example Sessions
+
+### Example 1: Paged Attention Latency Regression
+
+```
+User: /bisect-perf-regression a1b2c3d -- python bench_pa.py --batch 32
+
+Claude: The bad commit defaults to HEAD. Let me enumerate the range...
+
+Bisect range: a1b2c3d..f4e5d6c (HEAD)
+Total commits: 23
+Estimated steps: 5
+
+Running baseline at GOOD (a1b2c3d)... 142.3 us
+Running baseline at BAD  (f4e5d6c)... 198.7 us
+Regression: 39.6% slower (latency, lower is better)
+Threshold: 159.2 us
+
+Step 1/5: 7890abc = 143.1 us -> GOOD (11 left)
+Step 2/5: 1234def = 197.2 us -> BAD  (5 left)
+Step 3/5: 5678abc = 145.8 us -> GOOD (2 left)
+Step 4/5: 9012def = 196.5 us -> BAD  (1 left)
+Step 5/5: 3456abc = 195.9 us -> BAD  (0 left)
+
+============================================================
+REGRESSION COMMIT FOUND
+============================================================
+Commit:  3456abcdef123456
+Author:  developer@example.com
+Date:    2026-02-28
+Message: refactor: split KV loop into separate key and value phases
+
+Changed files:
+  pa_decode_gluon.py | 45 +++++++++++++++++++++------------------------
+
+Root cause: The refactor moved value cache loads AFTER the QK MFMA
+computation, breaking the previous load-compute overlap. Before this
+commit, value loads were issued concurrently with QK MFMA; after, they
+are sequential, adding ~55us of exposed load latency.
+```
+
+### Example 2: With Build Step
+
+```
+User: /bisect-perf-regression v0.1.0 v0.2.0 -- python -m pytest tests/bench.py -k "test_throughput" --tb=no
+
+Claude: Does this project need a build step after checkout?
+
+User: Yes, run pip install -e . after each checkout
+
+Claude: Got it. Using build_cmd="pip install -e ."
+...
+```
diff --git a/.claude/skills/build-flydsl/SKILL.md b/.claude/skills/build-flydsl/SKILL.md
@@ -0,0 +1,140 @@
+---
+name: build-flydsl
+description: >
+  Build and install FlyDSL (Flexible Layout Python DSL) on a remote host or Docker container.
+  FlyDSL is a Python DSL and MLIR-based compiler stack for authoring high-performance GPU kernels
+  with explicit layouts and tiling on AMD GPUs. Requires building LLVM/MLIR from source (~30min)
+  then FlyDSL C++ and Python bindings (~5min).
+  Usage: /build-flydsl [container@host]
+tools: Bash
+---
+
+# Build and Install FlyDSL
+
+Build FlyDSL from source on a remote host or Docker container. FlyDSL requires a custom
+LLVM/MLIR build with Python bindings, followed by the FlyDSL C++ dialect and Python package.
+
+## Arguments
+
+| Argument | Required | Description |
+|----------|----------|-------------|
+| `[container@host]` | No | Target in format `container@hostname`. If omitted, build locally. Example: `hungry_dijkstra@hjbog-srdc-39.amd.com` |
+
+## Prerequisites
+
+- **ROCm 6.x or 7.x** (for GPU execution)
+- **cmake** >= 3.20, C++17 compiler, **ninja** (recommended)
+- **Python** 3.10+ with pip
+- **Git** (to clone LLVM)
+- **Disk space**: ~50GB for LLVM build + FlyDSL
+- **CPU cores**: more is better (use `-j$(nproc)` or `-j128`)
+
+## Build Steps
+
+### Step 1: Build LLVM/MLIR (~30 min with -j128)
+
+This clones ROCm/llvm-project, checks out the commit specified in `thirdparty/llvm-hash.txt`,
+and builds MLIR with Python bindings.
+
+```bash
+cd /FlyDSL
+bash scripts/build_llvm.sh -j128
+```
+
+**What it does**:
+1. Clones `https://github.com/ROCm/llvm-project.git` to `../llvm-project/`
+2. Checks out the pinned commit from `thirdparty/llvm-hash.txt`
+3. CMake configure + build + install to `../llvm-project/mlir_install/`
+4. Creates tarball `../llvm-project/mlir_install.tgz`
+
+**If you already have an MLIR build**, skip this step and set:
+```bash
+export MLIR_PATH=/path/to/llvm-project/mlir_install
+```
+
+### Step 2: Build FlyDSL (~5 min)
+
+```bash
+cd /FlyDSL
+bash scripts/build.sh -j128
+```
+
+**What it does**:
+1. Auto-detects `MLIR_PATH` from common locations (or uses env var)
+2. CMake configure + build the Fly dialect (C++) and Python bindings
+3. Output: `build-fly/python_packages/flydsl/` with embedded MLIR bindings
+
+### Step 3: Install (editable mode)
+
+```bash
+cd /FlyDSL
+pip install -e .
+```
+
+**Or without installing** (just set paths):
+```bash
+export PYTHONPATH=/FlyDSL/build-fly/python_packages:$(pwd):$PYTHONPATH
+export LD_LIBRARY_PATH=/FlyDSL/build-fly/python_packages/flydsl/_mlir/_mlir_libs:$LD_LIBRARY_PATH
+```
+
+### Step 4: Verify
+
+```bash
+python3 -c "import flydsl; print('FlyDSL OK')"
+bash scripts/run_tests.sh  # GEMM correctness tests (~15s)
+```
+
+## Remote/Docker Execution
+
+For building inside a Docker container on a remote host:
+
+```bash
+# SSH command pattern
+ssh -o LogLevel=ERROR <HOST> 'docker exec <CONTAINER> bash -c "cd /FlyDSL && CMD"'
+
+# Full build sequence (run each step, wait for completion)
+ssh ... 'docker exec -d <CONTAINER> bash -c "cd /FlyDSL && bash scripts/build_llvm.sh -j128 > /tmp/build_llvm.log 2>&1"'
+# Monitor: ssh ... 'docker exec <CONTAINER> tail -5 /tmp/build_llvm.log'
+# Wait for "LLVM_BUILD_DONE" or "Creating tarball..." followed by completion
+
+ssh ... 'docker exec <CONTAINER> bash -c "cd /FlyDSL && bash scripts/build.sh -j128"'
+ssh ... 'docker exec <CONTAINER> bash -c "cd /FlyDSL && pip install -e ."'
+ssh ... 'docker exec <CONTAINER> bash -c "python3 -c \"import flydsl; print(\\\"FlyDSL OK\\\")\""'
+```
+
+## Build Artifacts (Do NOT Commit)
+
+The following directories are build artifacts generated by CMake and should NOT be committed to git:
+- `python/flydsl/_mlir/` — MLIR Python bindings (compiled `.so` files, platform-specific)
+- `build/`, `build-fly/` — CMake build directories
+
+These are already in `.gitignore`. After a fresh clone, run the build steps above to regenerate.
+
+## Rebuild After Code Changes
+
+```bash
+# C++ changes (dialect, MLIR passes):
+bash scripts/build.sh -j128
+
+# Python-only changes:
+# No rebuild needed — editable install picks up changes automatically.
+
+# Clear kernel cache if stale results:
+rm -rf ~/.flydsl/cache
+# Or disable cache:
+export FLYDSL_RUNTIME_ENABLE_CACHE=0
+```
+
+## Troubleshooting
+
+- **`std::gcd not found` or redeclaration errors**: Wrong LLVM picked up. `unset MLIR_PATH` and let `build.sh` auto-detect.
+- **`No module named flydsl`**: Run `pip install -e .` or set `PYTHONPATH`.
+- **MLIR `.so` load errors**: Set `LD_LIBRARY_PATH` to include `build-fly/python_packages/flydsl/_mlir/_mlir_libs/`.
+- **Build OOM**: Reduce parallelism (e.g., `-j64` instead of `-j128`).
+- **Docker `exec -d` for long builds**: Use background mode and monitor log file. LLVM build takes ~30min with 128 cores.
+
+## Verified Environments
+
+| Container | Image | Host | Status |
+|-----------|-------|------|--------|
+| hungry_dijkstra | rocm/pytorch:rocm7.2_ubuntu24.04_py3.12_pytorch_release_2.8.0 | hjbog-srdc-39.amd.com | Verified 2026-03-10 |
diff --git a/.claude/skills/build-rocm-image/SKILL.md b/.claude/skills/build-rocm-image/SKILL.md
@@ -0,0 +1,155 @@
+---
+name: build-rocm-image
+description: Connect to a remote host via SSH and build a Docker image with rocprofv3, vllm, aiter, FlyDSL, and custom triton (rocm-maxnreg-support-v35 branch). Use when user wants to build/rebuild the ROCm development image on a remote host. Usage: /build-rocm-image <hostname>
+tools: Bash
+---
+
+# Build ROCm Development Image
+
+Build a Docker image on a remote host with rocm gpu access based on `rocm/vllm-dev:nightly` with custom triton from the `rocm-maxnreg-support-v35` branch.
+
+## Arguments
+
+| Argument | Required | Description |
+|----------|----------|-------------|
+| `<HOST>` | Yes | The remote hostname to SSH into and build the image on. Example: `hjbog-srdc-39.amd.com` |
+
+When this skill is invoked, the argument passed in is the target hostname. Replace all occurrences of `<HOST>` below with the provided hostname. If no hostname is provided, ask the user for it before proceeding.
+
+## Target Host
+
+- **Host**: `<HOST>` (provided as argument)
+- **Access**: SSH (key-based authentication)
+
+## Base Image
+
+- **Image**: `rocm/vllm-dev:nightly`
+- **Included**: rocprofv3 (ROCm 7.0), PyTorch 2.9
+
+## Customization
+
+- **Triton**: Replace stock triton 3.4.0 with custom build from https://<GITHUB_TOKEN>@github.com/ROCm/triton branch `rocm-maxnreg-support-v35`
+- **vLLM**: Replace pre-installed version with https://<GITHUB_TOKEN>@github.com/ROCm/vllm branch `ps_pa`
+- **aiter**: Replace pre-installed version with latest from https://<GITHUB_TOKEN>@github.com/ROCm/aiter main branch (develop)
+- **FlyDSL**: Install from https://<GITHUB_TOKEN>@github.com/ROCm/FlyDSL develop branch
+
+## Build Steps
+
+### Step 1: Generate Dockerfile on remote host
+
+```bash
+ssh -o ConnectTimeout=30 <HOST> "cat > /tmp/Dockerfile.rocm-custom << 'DOCKERFILE'
+FROM rocm/vllm-dev:nightly
+
+# Uninstall existing triton, vllm, aiter
+RUN pip uninstall -y triton pytorch-triton-rocm vllm aiter 2>/dev/null; true
+
+# Install build dependencies
+RUN pip install ninja cmake pybind11
+
+# Clone and build custom triton from ROCm fork (rocm-maxnreg-support-v35 branch)
+RUN cd /tmp && \
+    git clone --depth 1 --branch rocm-maxnreg-support-v35 https://<GITHUB_TOKEN>@github.com/ROCm/triton.git triton-custom && \
+    cd triton-custom/python && \
+    pip install -e . && \
+    cd / && rm -rf /tmp/triton-custom
+
+# Clone and install aiter from main branch (develop)
+RUN cd /tmp && \
+    git clone --depth 1 --branch main https://<GITHUB_TOKEN>@github.com/ROCm/aiter.git && \
+    cd aiter && \
+    pip install -e . && \
+    cd / && rm -rf /tmp/aiter
+
+# Clone and install FlyDSL from develop branch
+RUN cd /tmp && \
+    git clone --depth 1 --branch develop https://<GITHUB_TOKEN>@github.com/ROCm/FlyDSL.git && \
+    cd FlyDSL && \
+    pip install -e . && \
+    cd / && rm -rf /tmp/FlyDSL
+
+# Clone and install vllm from ROCm/vllm ps_pa branch
+RUN cd /tmp && \
+    git clone --depth 1 --branch ps_pa https://<GITHUB_TOKEN>@github.com/ROCm/vllm.git && \
+    cd vllm && \
+    pip install -e . && \
+    cd / && rm -rf /tmp/vllm
+
+# Install rocprof-trace-decoder: download installer, extract .so, copy to /opt/rocm/lib
+RUN cd /tmp && \
+    wget -q https://<GITHUB_TOKEN>@github.com/ROCm/rocprof-trace-decoder/releases/download/0.1.6/rocprof-trace-decoder-manylinux-2.28-0.1.6-Linux.sh && \
+    chmod +x rocprof-trace-decoder-manylinux-2.28-0.1.6-Linux.sh && \
+    ./rocprof-trace-decoder-manylinux-2.28-0.1.6-Linux.sh --skip-license --prefix=/tmp/rtd-install && \
+    find /tmp/rtd-install -name '*.so*' -exec cp -a {} /opt/rocm/lib/ \; && \
+    ldconfig && \
+    rm -rf /tmp/rocprof-trace-decoder-manylinux-2.28-0.1.6-Linux.sh /tmp/rtd-install
+
+# Verify installations
+RUN python3 -c 'import triton; print(f\"triton version: {triton.__version__}\")' && \
+    python3 -c 'import vllm; print(f\"vllm version: {vllm.__version__}\")' && \
+    python3 -c 'import aiter; print(\"aiter OK\")' && \
+    python3 -c 'import flydsl; print(\"FlyDSL OK\")' && \
+    which rocprofv3 && echo 'rocprofv3 OK' && \
+    ls /opt/rocm/lib/librocprof*decoder* && echo 'rocprof-trace-decoder OK'
+
+LABEL description=\"ROCm dev image with vllm(ROCm/ps_pa), aiter(main), FlyDSL(develop), rocprofv3, rocprof-trace-decoder, and custom triton (rocm-maxnreg-support-v35)\"
+DOCKERFILE
+"
+```
+
+### Step 2: Build the image
+
+Build the image with a descriptive tag. Use `--network=host` to ensure git clone works.
+
+```bash
+ssh -o ConnectTimeout=30 <HOST> "docker build --network=host -t rocm-dev-custom:triton-maxnreg-v35 -f /tmp/Dockerfile.rocm-custom /tmp"
+```
+
+**Note**: The triton build can take 30-60 minutes. Use `--progress=plain` to see full build logs.
+
+### Step 3: Verify the built image
+
+```bash
+ssh -o ConnectTimeout=30 <HOST> "docker run --rm rocm-dev-custom:triton-maxnreg-v35 bash -c '
+echo \"=== Triton ===\"
+python3 -c \"import triton; print(triton.__version__)\"
+echo \"=== vLLM ===\"
+python3 -c \"import vllm; print(vllm.__version__)\"
+echo \"=== aiter ===\"
+python3 -c \"import aiter; print(aiter.__version__)\" 2>/dev/null || python3 -c \"import aiter; print(\\\"aiter OK\\\")\"
+echo \"=== FlyDSL ===\"
+python3 -c \"import flydsl; print(flydsl.__version__)\" 2>/dev/null || python3 -c \"import flydsl; print(\\\"FlyDSL OK\\\")\"
+echo \"=== rocprofv3 ===\"
+rocprofv3 --version 2>/dev/null || which rocprofv3
+echo \"=== ROCm ===\"
+cat /opt/rocm/.info/version
+'"
+```
+
+### Step 4: Clean up
+
+```bash
+ssh -o ConnectTimeout=30 <HOST> "rm -f /tmp/Dockerfile.rocm-custom"
+```
+
+## Output
+
+Report to the user:
+- The image name and tag
+- Versions of triton, vllm, aiter, and ROCm inside the image
+- The triton git branch used
+- Any build warnings or errors
+
+## Error Handling
+
+- If SSH connection fails, inform the user they need a valid SSH key and Conductor reservation
+- If triton build fails, check if `rocm-maxnreg-support-v35` branch exists and suggest verifying the branch name
+- If disk space is insufficient, suggest cleaning unused images with `docker image prune`
+
+## Example Usage
+
+To start a container from the built image with GPU access:
+
+```bash
+ssh <HOST> "docker run -it --device=/dev/kfd --device=/dev/dri --group-add video --shm-size=64g rocm-dev-custom:triton-maxnreg-v35 bash"
+```
diff --git a/.claude/skills/debug-flydsl-kernel/SKILL.md b/.claude/skills/debug-flydsl-kernel/SKILL.md
@@ -0,0 +1,249 @@
+---
+name: debug-flydsl-kernel
+description: >
+  Debug FlyDSL GPU kernels that produce NaN, inf, wrong results, or crash.
+  Covers cache invalidation, tracing pitfalls (runtime conditionals, range vs
+  range_constexpr), scf.for state packing, buffer_load addressing, MFMA operand
+  layout verification, LDS bank conflict diagnosis, and systematic error
+  isolation (all-1s test, single-partition test, host-side tensor inspection).
+  Use when a FlyDSL kernel produces incorrect output or compilation errors.
+  Usage: /debug-flydsl-kernel
+tools: Read,Edit,Bash,Grep,Glob,Agent
+---
+
+# Debug FlyDSL Kernel
+
+## Step 0: Clear All Caches (ALWAYS DO THIS FIRST)
+
+FlyDSL aggressively caches compiled kernels. Stale cache is the #1 cause of "my fix didn't work":
+
+```bash
+rm -rf ~/.flydsl /tmp/flydsl*
+```
+
+Also clear Python-level caches if using `@functools.lru_cache`:
+```python
+compile_my_kernel.cache_clear()
+```
+
+## Step 1: Classify the Error
+
+| Symptom | Likely Cause | Go to |
+|---|---|---|
+| All NaN output | Softmax -inf/-inf, division by zero, uninitialized buffer | Section 2 |
+| All zeros output | Wrong output address, uninitialized temp buffer | Section 3 |
+| Partially wrong (>50% mismatch) | Wrong partition count, missing partitions, layout mismatch | Section 4 |
+| Small errors (1-5% mismatch) | FP8 quantization, scale factor, off-by-one masking | Section 5 |
+| Compilation error / crash | Type mismatch, scf.for state, range vs range_constexpr | Section 6 |
+| GPU hang | Infinite loop, deadlock in barrier, OOB memory access | Section 7 |
+
+## 2. Debugging NaN
+
+### 2.1 Softmax NaN: -inf minus -inf
+
+When ALL tokens in a partition are masked (out of context), `qk_max = -inf`. Then `exp(s - qk_max) = exp(-inf - (-inf)) = exp(NaN) = NaN`.
+
+**Fix**: Guard the exp calculation:
+```python
+safe_diff = arith.select(qk_max > NEG_INF, diff, ZERO_F)
+```
+
+### 2.2 Division by zero in normalization
+
+When `exp_sum = 0` (all probs zero), `1/exp_sum = inf`.
+
+**Fix**:
+```python
+safe_sum = arith.select(running_sum > ZERO_F, running_sum, arith.constant(1.0, type=T.f32))
+inv_sum = arith.constant(1.0, type=T.f32) / safe_sum
+```
+
+### 2.3 Host-side NaN check
+
+Add prints in the Python launch function to check intermediate buffers:
+```python
+torch.cuda.synchronize()
+print(f"exp_sums nan={exp_sums.isnan().sum()}, inf={exp_sums.isinf().sum()}")
+print(f"max_logits nan={max_logits.isnan().sum()}, range=[{max_logits.min():.4f}, {max_logits.max():.4f}]")
+print(f"temp_out nan={temporary_output.isnan().sum()}")
+```
+
+## 3. Debugging All-Zeros Output
+
+### 3.1 Wrong output address
+
+Check stride parameters: if `stride_out_seq` or `stride_out_part` is wrong, output writes go to incorrect locations. Print strides:
+```python
+print(f"out strides: {output.stride()}, temp strides: {temporary_output.stride()}")
+```
+
+### 3.2 Partition slot mismatch
+
+For multi-partition kernels, verify the output is written to `part_z` slot (not absolute partition index). The reduce kernel reads from `part_z = 0..grid_z-1` slots.
+
+### 3.3 exp_sums at zero / max_logits at -inf
+
+If the main kernel doesn't write exp_sums/max_logits, the reduce kernel produces zeros. Initialize sentinel values before kernel launch:
+```python
+exp_sums.fill_(-999.0)  # sentinel
+# ... launch kernel ...
+torch.cuda.synchronize()
+print(f"exp_sums[0,0,0,:4] = {exp_sums[0,0,0,:4]}")  # should NOT be -999
+```
+
+## 4. Debugging Large Mismatch (>50%)
+
+### 4.1 Missing partitions
+
+If `grid_z < total_partitions` and the kernel processes only ONE partition per CTA (no loop), most of the context is skipped. Verify:
+```python
+total_parts = math.ceil(context_len / KV_COMPUTE_BLOCK)
+print(f"grid_z={grid_z}, total_parts={total_parts}")
+assert grid_z == total_parts or kernel_has_multi_partition_loop
+```
+
+### 4.2 All-1s isolation test
+
+Fill query, key_cache, value_cache with 1.0 to eliminate data-dependent bugs:
+```python
+query.fill_(1.0)
+key_cache.fill_(1.0)
+value_cache.fill_(1.0)
+```
+With uniform input: all softmax probs are equal, PV output = 1.0. Any deviation reveals layout/addressing bugs.
+
+**Caveat**: All-1s test does NOT catch V/P operand misalignment (since uniform values produce correct results regardless of ordering).
+
+### 4.3 Single-partition test
+
+Force `max_context_partition_num=1` (one_shot mode) to bypass the reduce kernel and test the main kernel in isolation.
+
+### 4.4 Compare against Gluon
+
+Run both Gluon and FlyDSL on the same input and compare element-wise:
+```python
+torch.testing.assert_close(flydsl_output, gluon_output, atol=5e-3, rtol=5e-3)
+```
+
+## 5. Debugging Small Errors (1-5%)
+
+### 5.1 FP8 probability requantization
+
+FP8 PV MFMA introduces ~0.03 max error vs bf16 reference. This is inherent to the FP8 data path and NOT a bug. Expected tolerance: `atol=5e-3`.
+
+### 5.2 Per-tensor vs per-row quantization
+
+If the reference uses per-row Q quantization but FlyDSL uses per-tensor, expect ~1-3% mismatch. Verify quantization mode matches.
+
+### 5.3 Scale factor mismatch
+
+Verify `_scale = softmax_scale * q_scale * k_scale` matches the reference. Common bug: applying v_scale twice (once in prob scaling, once after PV).
+
+## 6. Compilation Errors
+
+### 6.1 `range()` vs `range_constexpr()` inside @flyc.kernel
+
+FlyDSL's AST rewriter converts ALL `range()` to `scf.for` (runtime loops). Use `range_constexpr()` for compile-time unrolled loops:
+```python
+# WRONG: i becomes an ArithValue, can't index Python lists
+for i in range(4): result[i] = ...
+
+# CORRECT: i is a Python int
+for i in range_constexpr(4): result[i] = ...
+```
+
+### 6.2 Runtime conditional as Python bool
+
+FlyDSL tracing evaluates Python `if` at trace time. Runtime GPU values can't be used:
+```python
+# WRONG: "cannot evaluate dynamic 'Boolean' as Python bool during tracing"
+if kv_tok < context_len:  # runtime comparison
+    fx.printf(...)
+
+# CORRECT: use arith.select for runtime conditionals
+val = arith.select(kv_tok < context_len, good_val, bad_val)
+```
+
+Python `if` is fine for COMPILE-TIME decisions (e.g., `if trans_v:` where trans_v is a Python bool).
+
+### 6.3 scf.for state packing
+
+All loop-carried values must be raw SSA values (not Python wrappers):
+```python
+def _unwrap(v):
+    return v.ir_value() if hasattr(v, 'ir_value') else v
+
+init_state = [_unwrap(v) for v in [val1, val2, vec_val]]
+```
+
+Supported state types: `f32` (scalar), `f32x4` (vector), `i32`, `i64`, `index`.
+
+### 6.4 buffer_load type mismatch
+
+`buffer_ops.buffer_load(rsrc, offset, vec_width=4, dtype=T.i32)` — the offset is in units of `dtype`. For FP8 data addressed in bytes, divide by element size:
+```python
+k_addr_bytes = ...  # address in FP8 elements (= bytes for FP8)
+k_4xi32 = buffer_ops.buffer_load(k_rsrc, k_addr_bytes // 4, vec_width=4, dtype=T.i32)
+```
+
+### 6.5 vector.store requires vector type
+
+LDS `vector.store` requires the value to be a vector, not scalar:
+```python
+# WRONG
+vector.store(scalar_i32, lds_ptr, [idx])
+
+# CORRECT
+vec = vector.from_elements(T.vec(1, T.i32), [scalar_i32])
+vector.store(vec, lds_ptr, [idx])
+```
+
+## 7. GPU Hang
+
+### 7.1 Infinite scf.for loop
+
+If loop bounds are wrong (`stop < start` with unsigned comparison issues, or `step=0`), the GPU hangs. Verify bounds on host:
+```python
+print(f"loop: start={part_start}, stop={part_end}, step={cpb}")
+```
+
+### 7.2 Barrier deadlock
+
+`gpu.barrier()` requires ALL threads in the workgroup to reach it. If some threads take a different branch (runtime `if`), the barrier deadlocks. FlyDSL doesn't support divergent barriers.
+
+### 7.3 Recovery from GPU hang
+
+```bash
+# Check GPU state
+rocm-smi
+# If GPU shows 100% usage with no progress, reset:
+sudo amdgpu-reset  # or reboot
+```
+
+## 8. Diagnostic Workflow
+
+```
+1. Clear caches (rm -rf ~/.flydsl)
+2. Run with all-1s input → passes? Layout is OK, data issue
+3. Run with single partition (one_shot) → passes? Multi-partition/reduce bug
+4. Add host-side prints (tensor shapes, strides, NaN checks)
+5. Compare intermediate buffers (exp_sums, max_logits, temp_out)
+6. If layout bug suspected: trace one thread's addresses manually
+   (tid=0: lane16id=0, rowid=0, warp_id=0)
+7. For MFMA bugs: verify operand order (K is LHS, Q is RHS for QK)
+```
+
+## 9. Common Pitfalls Checklist
+
+- [ ] Cleared `~/.flydsl` cache after code change
+- [ ] `range_constexpr()` for all compile-time loops (not `range()`)
+- [ ] No Python `if` on runtime GPU values
+- [ ] `buffer_load` offset units match dtype (bytes/4 for i32)
+- [ ] `vector.store` uses vector type (not scalar)
+- [ ] `scf.for` state packed with `_unwrap()` (raw SSA values)
+- [ ] Output written to correct partition slot (`part_z`, not absolute index)
+- [ ] `exp_sums`/`max_logits` strides match actual tensor layout
+- [ ] Softmax guards against `-inf - (-inf) = NaN`
+- [ ] Division by zero guarded (`select(sum > 0, sum, 1.0)`)
+- [ ] K/V address calculation matches tensor layout (4D vs 5D trans_v)
+- [ ] MFMA operand order: `mfma(LHS, RHS, acc)` — LHS→M, RHS→N
diff --git a/.claude/skills/flydsl-kernel-authoring/SKILL.md b/.claude/skills/flydsl-kernel-authoring/SKILL.md
@@ -0,0 +1,735 @@
+# FlyDSL Kernel Authoring Skill
+
+## Overview
+
+FlyDSL is a Python DSL and MLIR-based compiler for writing high-performance GPU kernels on AMD GPUs (MI300X/MI350). It provides explicit layout algebra for controlling data movement, tiling, and memory access patterns. The layout system is the core abstraction that distinguishes FlyDSL from Triton/Gluon.
+
+**Repository**: `/FlyDSL/` (installed in editable mode)
+**Target GPU**: gfx942 (MI300X, CDNA3), gfx950 (MI350, CDNA4)
+**Python**: 3.12, ROCm 7.2
+
+---
+
+## 1. Architecture and Compilation
+
+### Pipeline
+```
+Python (@flyc.kernel/@flyc.jit)
+  -> AST Rewriting (for/if -> scf.for/scf.if)
+  -> MLIR Tracing (generates Fly dialect + gpu/arith/scf/memref ops)
+  -> MlirCompiler.compile() (Fly -> ROCDL -> LLVM -> HSACO binary)
+  -> JITCFunction (ExecutionEngine wrapper)
+```
+
+### Key Passes
+1. `gpu-kernel-outlining` - Move kernel bodies to `gpu.func`
+2. `fly-layout-lowering` - Lower layout algebra to arithmetic
+3. `convert-fly-to-rocdl` - Fly ops -> ROCDL intrinsics
+4. `gpu-module-to-binary` - Emit HSACO binary
+
+### Key Source Paths
+- `python/flydsl/compiler/` - JIT compilation (jit_function.py, kernel_function.py)
+- `python/flydsl/expr/` - DSL expression API (primitive.py, derived.py, typing.py)
+- `python/flydsl/expr/primitive.py` - All layout algebra functions
+- `python/flydsl/expr/derived.py` - CopyAtom, MmaAtom, TiledCopy, TiledMma wrappers
+- `python/flydsl/expr/gpu.py` - GPU operations (thread_idx, block_idx, barrier)
+- `python/flydsl/expr/buffer_ops.py` - AMD buffer load/store intrinsics
+- `python/flydsl/expr/rocdl.py` - MFMA and other ROCm intrinsics
+- `python/flydsl/utils/smem_allocator.py` - LDS (shared memory) management
+- `kernels/` - Pre-built kernels (preshuffle_gemm.py, layernorm, softmax, rmsnorm)
+
+---
+
+## 2. Layout System (Core Abstraction)
+
+### Core Types
+| Type | Description | Example |
+|------|-------------|---------|
+| `!fly.int_tuple` | Integer tuple (can be nested) | `(8, 16)`, `(8, (4, 2))` |
+| `!fly.layout` | (Shape, Stride) pair | `(8, 16):(1, 8)` (col-major) |
+| `!fly.memref` | Memory reference with layout | Typed pointer + layout info |
+
+### Construction
+```python
+import flydsl.expr as fx
+
+shape = fx.make_shape(8, 16)              # IntTuple (8, 16)
+stride = fx.make_stride(1, 8)             # IntTuple (1, 8)
+layout = fx.make_layout(shape, stride)    # Layout (8,16):(1,8)
+
+# Shorthand with Python tuples
+layout = fx.make_layout((8, 16), (1, 8))
+
+# Coordinates
+coord = fx.make_coord(i, j)
+
+# Nested shapes for hierarchical tiling
+shape_nested = fx.make_shape(9, (4, 8))   # (9, (4, 8))
+
+# Identity layout
+identity = fx.make_identity_layout((M, N))
+```
+
+### Coordinate Mapping
+The fundamental operation maps logical coordinates to physical memory indices.
+
+**Formula**: `Index = sum(coord_i * stride_i)`
+
+```python
+idx = fx.crd2idx(coord, layout)    # Coordinate -> linear index
+coord = fx.idx2crd(idx, layout)    # Linear index -> coordinate
+s = fx.size(layout)                # Total element count (product of shape)
+```
+
+**Example**: For layout `(8, 16):(1, 8)` (8x16, column-major):
+- `crd2idx((3, 5), layout)` = `3*1 + 5*8` = 43
+- `idx2crd(43, layout)` = `(43 % 8, 43 / 8)` = `(3, 5)`
+
+### Query Operations
+```python
+fx.size(layout)           # Total element count
+fx.get_shape(layout)      # Extract shape IntTuple
+fx.get_stride(layout)     # Extract stride IntTuple
+fx.get(int_tuple, i)      # Get i-th element
+fx.rank(int_tuple)        # Number of top-level modes
+```
+
+### Layout Algebra Operations
+
+#### Composition: `fx.composition(A, B)`
+Compose two layouts: `result(x) = A(B(x))`. Used to apply permutations or tile coordinate mappings.
+
+#### Complement: `fx.complement(tiler, target_size)`
+Compute remaining modes not covered by tiler, up to target_size. Internal building block for divides.
+
+#### Coalesce: `fx.coalesce(layout)`
+Simplify layout by merging adjacent modes. Preserves mapping but flattens structure.
+
+#### Right Inverse: `fx.right_inverse(layout)`
+Compute right inverse of layout mapping.
+
+#### Recast: `fx.recast_layout(layout, old_bits, new_bits)`
+Adjust layout for type width change (e.g., FP16->FP8).
+
+### Product Operations (Combine Layouts)
+Products combine two layouts to create a larger layout:
+
+```python
+fx.logical_product(layout, tiler)   # Basic mode-wise concatenation
+fx.raked_product(thr, val)          # Interleaved access pattern (common for TiledCopy)
+fx.block_product(layout, tiler)     # Blocked access pattern
+fx.zipped_product(layout, tiler)    # Zipped modes
+fx.tiled_product(layout, tiler)     # Hierarchical tiled structure
+fx.flat_product(layout, tiler)      # Flattened result
+```
+
+### Divide Operations (Partition Layouts)
+Divides split a layout by a divisor, creating tile + rest dimensions:
+
+```python
+fx.logical_divide(layout, divisor)  # Basic partitioning (uses complement internally)
+fx.zipped_divide(layout, divisor)   # Zipped division
+fx.tiled_divide(layout, divisor)    # Hierarchical tiled division
+fx.flat_divide(layout, divisor)     # Flattened division
+```
+
+### Structural Operations
+```python
+fx.select(int_tuple, indices=[0, 2])      # Pick specific modes
+fx.group(int_tuple, begin=1, end=3)        # Group modes into nested tuple
+fx.append(base, elem)                      # Append mode
+fx.prepend(base, elem)                     # Prepend mode
+fx.zip(lhs, rhs)                           # Zip two IntTuples
+fx.slice(src, coord)                       # Slice at coordinate (None = keep mode)
+```
+
+---
+
+## 3. Writing Kernels
+
+### Basic Pattern
+```python
+import flydsl.compiler as flyc
+import flydsl.expr as fx
+from flydsl.expr import arith, gpu, buffer_ops, range_constexpr
+from flydsl.expr.typing import T
+
+@flyc.kernel
+def my_kernel(
+    A: fx.Tensor,         # GPU tensor (memref via DLPack)
+    B: fx.Tensor,
+    N: fx.Constexpr[int], # Compile-time constant
+):
+    tid = gpu.thread_idx.x    # Returns Int32
+    bid = gpu.block_idx.x
+    # ... kernel body ...
+
+@flyc.jit
+def launch(
+    A: fx.Tensor,
+    B: fx.Tensor,
+    N: fx.Constexpr[int],
+    stream: fx.Stream = fx.Stream(None),
+):
+    my_kernel(A, B, N).launch(
+        grid=(N // 256,), block=(256,), stream=stream
+    )
+
+# Usage:
+import torch
+A = torch.randn(1024, device="cuda", dtype=torch.float32)
+B = torch.empty(1024, device="cuda", dtype=torch.float32)
+launch(A, B, 1024)
+```
+
+### Parameter Types
+| Type | Description | At host boundary |
+|------|-------------|-----------------|
+| `fx.Tensor` | GPU tensor (memref) | Auto-converted from torch.Tensor via DLPack |
+| `fx.Constexpr[int]` | Compile-time constant | Different values -> different compiled kernels |
+| `fx.Int32` | Runtime i32 | Auto-converted from Python int |
+| `fx.Stream` | CUDA/HIP stream | `fx.Stream(None)` for default stream |
+
+### Thread/Block Hierarchy
+```python
+from flydsl.expr import gpu
+
+tid_x = gpu.thread_idx.x    # Thread index (Int32)
+bid_x = gpu.block_idx.x     # Block index (Int32)
+bdim_x = gpu.block_dim.x    # Block dimension
+gdim_x = gpu.grid_dim.x     # Grid dimension
+gpu.barrier()                # Workgroup synchronization
+```
+
+### Control Flow
+```python
+from flydsl.expr import range_constexpr
+
+# Compile-time unrolled loop (emitted inline in IR)
+for i in range_constexpr(N):
+    ...
+
+# Runtime loop (lowered to scf.for via AST rewriting)
+for i in range(runtime_value):
+    ...
+```
+
+### scf.for with Loop-Carried Values (Software Pipelining)
+
+Use `init=` on `range()` to create an `scf.for` with explicit SSA phi nodes for loop-carried state. This is required for software pipelining (prefetch patterns) where data must flow across iterations.
+
+**Pattern** (from `preshuffle_gemm.py`):
+```python
+# Prologue: load first tile
+tile_0 = prefetch(0)
+init_state = [acc_init, tile_0_flat_val1, tile_0_flat_val2, ...]
+
+# scf.for with loop-carried state
+# CRITICAL: bounds MUST be arith.index() values, NOT Python ints!
+_start = arith.index(0)
+_stop = arith.index(N - 1)
+_step = arith.index(1)
+for iv, state in range(_start, _stop, _step, init=init_state):
+    acc_in = state[0]
+    tile_in = state[1:]
+
+    next_tile = prefetch(iv + 1)      # load NEXT data
+    acc_in = compute(acc_in, tile_in)  # compute CURRENT
+
+    results = yield [acc_in] + next_tile  # carry to next iter
+
+# Epilogue: process last tile from results
+acc_final = results[0]
+tile_final = results[1:]
+compute(acc_final, tile_final)
+```
+
+**How it works in MLIR:**
+| Element | Meaning |
+|---|---|
+| `init=init_state` | List of SSA values that seed the `scf.for` block arguments for iteration 0 |
+| `state` | The loop-carried block arguments (phi nodes) for THIS iteration |
+| `yield [...]` | `scf.yield` feeds values back as next iteration's `state` |
+| `results` | After loop exits, holds the last `yield`'s values (the `scf.for` op results) |
+
+**Three critical pitfalls (all verified by debugging):**
+
+1. **Loop bounds must be `arith.index()`, NOT Python ints.** If you write `range(0, 15, 1, init=...)`, the AST rewriter treats constant bounds as a Python `range` and unrolls the loop — silently ignoring `init=`. Use `arith.index(0)`, `arith.index(15)`, `arith.index(1)` instead.
+
+2. **All `init` values must be raw MLIR `ir.Value`s.** FlyDSL wrappers like `Int32` / `Float32` don't have `.type` (only `.dtype`), and `scf.ForOp.__init__` calls `arg.type`. Unwrap via:
+   ```python
+   def _unwrap(v):
+       return v.ir_value() if hasattr(v, 'ir_value') else v
+   init_state = [_unwrap(v) for v in raw_list]
+   ```
+
+3. **Clear `SmemPtr._view_cache` before epilogue.** `SmemPtr.get()` caches the `memref.view` it creates. If called inside the `scf.for` body, the cached view is defined in the loop scope. Using it in the epilogue (outside the loop) causes an SSA dominance error. Fix:
+   ```python
+   # After the scf.for loop, before epilogue compute:
+   my_smem_ptr._view_cache = None
+   ```
+
+### Arithmetic Operations
+```python
+from flydsl.expr import arith
+
+c42 = arith.constant(42, index=True)           # index type constant
+c3_14 = arith.constant(3.14, type=T.f32())     # f32 constant
+
+# NOTE: arith.constant takes `type` as keyword arg, NOT positional
+result = arith.addf(a, b)    # float add
+result = arith.mulf(a, b)    # float multiply
+result = arith.negf(a)       # float negate
+result = arith.maximumf(a, b)  # float max (works on scalars AND vectors)
+result = arith.select(cond, true_val, false_val)
+
+# Compare floats (returns i1/vector<Nxi1>)
+is_less = arith.cmpf(a, b, predicate="olt")    # ordered less-than
+```
+
+### Vector Arithmetic (IMPORTANT)
+All arith ops (`addf`, `mulf`, `negf`, `maximumf`, `cmpf`, `select`) work on **both scalars and vectors**.
+To broadcast a scalar to a vector, use `arith.constant_vector`:
+
+```python
+from flydsl._mlir.ir import VectorType
+
+# Create a splat constant vector (e.g., all 2.0)
+vec_type = VectorType.get([vec_width], fx.T.f32())
+scale_vec = arith.constant_vector(2.0, vec_type)
+
+# Now use it with vector ops
+vA = fx.memref_load_vec(rA)        # load vec from register
+vC = arith.mulf(vA, scale_vec)    # element-wise scale
+```
+
+### Arith Ops Availability Table
+| Operation | Function | Works on Vectors | Notes |
+|-----------|----------|-----------------|-------|
+| Add | `arith.addf(a, b)` | Yes | |
+| Multiply | `arith.mulf(a, b)` | Yes | |
+| Negate | `arith.negf(a)` | Yes | |
+| Max | `arith.maximumf(a, b)` | Yes | Good for ReLU |
+| Compare | `arith.cmpf(a, b, pred)` | Yes | Returns i1/vec<i1> |
+| Select | `arith.select(cond, t, f)` | Yes | |
+| Abs | `arith.absf(a)` | **NO - does not exist** | Use `negf+cmpf+select` |
+| FMA | `arith.fma(a, b, c)` | Not verified | Use `mulf+addf` instead |
+| Splat const | `arith.constant_vector(val, vty)` | Creates vector | For scalar broadcast |
+
+### Printf Debugging
+```python
+fx.printf("tid={} bid={} val={}", tid, bid, value)
+```
+
+---
+
+## 4. Data Movement Patterns
+
+### Layout-Based Copy (Preferred for Element-wise Kernels)
+
+The standard pattern: divide tensor by tile size, slice by block/thread, copy via atoms.
+
+```python
+@flyc.kernel
+def my_kernel(A: fx.Tensor, B: fx.Tensor, BLOCK_DIM: fx.Constexpr[int]):
+    bid = fx.block_idx.x
+    tid = fx.thread_idx.x
+
+    # 1. Divide tensor into blocks
+    tA = fx.logical_divide(A, fx.make_layout(BLOCK_DIM, 1))
+    tB = fx.logical_divide(B, fx.make_layout(BLOCK_DIM, 1))
+
+    # 2. Select this block's tile
+    tA = fx.slice(tA, (None, bid))
+    tB = fx.slice(tB, (None, bid))
+
+    # 3. Further divide for per-thread access
+    tA = fx.logical_divide(tA, fx.make_layout(1, 1))  # 1 element per thread
+    tB = fx.logical_divide(tB, fx.make_layout(1, 1))
+
+    # 4. Allocate registers
+    RABTy = fx.MemRefType.get(fx.T.f32(), fx.LayoutType.get(1, 1), fx.AddressSpace.Register)
+    copyAtom = fx.make_copy_atom(fx.UniversalCopy32b(), fx.Float32)
+    rA = fx.memref_alloca(RABTy, fx.make_layout(1, 1))
+
+    # 5. Copy: global -> register -> compute -> global
+    fx.copy_atom_call(copyAtom, fx.slice(tA, (None, tid)), rA)
+    # ... compute on register values ...
+    fx.copy_atom_call(copyAtom, rA, fx.slice(tB, (None, tid)))
+```
+
+### Vectorized Loads (Wide Copies)
+```python
+VEC_WIDTH = 4
+copy_bits = VEC_WIDTH * 32   # 128 bits
+MemRefTy = fx.MemRefType.get(fx.T.f32(), fx.LayoutType.get(VEC_WIDTH, 1), fx.AddressSpace.Register)
+copyAtom = fx.make_copy_atom(fx.UniversalCopy(copy_bits), fx.Float32)
+
+rA = fx.memref_alloca(MemRefTy, fx.make_layout(VEC_WIDTH, 1))
+
+# Divide for VEC_WIDTH elements per thread
+tA = fx.logical_divide(tA, fx.make_layout(VEC_WIDTH, 1))
+fx.copy_atom_call(copyAtom, fx.slice(tA, (None, tid)), rA)
+
+# Load/store as vectors
+vec = fx.memref_load_vec(rA)     # Load vector from register memref
+fx.memref_store_vec(vec, rA)     # Store vector to register memref
+```
+
+### TiledCopy Abstraction (for 2D Copies)
+```python
+# Define thread and value layouts
+thr_layout = fx.make_layout((4, 1), (1, 1))    # 4 threads
+val_layout = fx.make_layout((1, 8), (1, 1))    # 8 values per thread
+
+# Create copy atom
+copy_atom = fx.make_copy_atom(fx.rocdl.BufferCopy128b(), fx.Float32)
+
+# Build tiled copy with raked product layout
+layout_thr_val = fx.raked_product(thr_layout, val_layout)
+tile_mn = fx.make_tile(4, 8)
+tiled_copy = fx.make_tiled_copy(copy_atom, layout_thr_val, tile_mn)
+
+# Get this thread's slice and partition
+thr_copy = tiled_copy.get_slice(tid)
+partition_src = thr_copy.partition_S(src_tensor)
+partition_dst = thr_copy.partition_D(dst_tensor)
+frag = fx.make_fragment_like(partition_src)
+
+# Execute copy: src -> fragment -> dst
+fx.copy(copy_atom, partition_src, frag)
+fx.copy(copy_atom, frag, partition_dst)
+```
+
+### Buffer Load/Store (AMD Intrinsics)
+```python
+from flydsl.expr import buffer_ops
+
+rsrc = buffer_ops.create_buffer_resource(tensor)
+# offset is in ELEMENTS (not bytes)
+data = buffer_ops.buffer_load(rsrc, offset, vec_width=4)
+buffer_ops.buffer_store(data, rsrc, offset)
+```
+
+### Copy Atom Types
+| Type | Bits | Usage |
+|------|------|-------|
+| `fx.UniversalCopy32b()` | 32 | 1x f32 element copy |
+| `fx.UniversalCopy(64)` | 64 | 2x f32 elements |
+| `fx.UniversalCopy(128)` | 128 | 4x f32 elements |
+| `fx.rocdl.BufferCopy128b()` | 128 | AMD buffer load 4xf32 |
+
+---
+
+## 5. Shared Memory (LDS)
+
+### SmemAllocator Pattern
+```python
+from flydsl.utils.smem_allocator import SmemAllocator
+from flydsl.expr.typing import T
+from flydsl.compiler.kernel_function import CompilationContext
+
+allocator = SmemAllocator(None, arch="gfx942", global_sym_name="smem0")
+lds_a = allocator.allocate_array(T.f16, 8192)  # Allocate typed arrays
+lds_b = allocator.allocate_array(T.f16, 8192)
+
+@flyc.kernel
+def my_kernel(A: fx.Tensor, ...):
+    lds_base = allocator.get_base()       # Get base ptr inside kernel
+    lds_a_ptr = lds_a(lds_base)           # SmemPtr for typed access
+    val = lds_a_ptr.load([idx])
+    lds_a_ptr.store(val, [idx])
+
+    # Finalize in GPU module body (before launch)
+    comp_ctx = CompilationContext.get_current()
+    with ir.InsertionPoint(comp_ctx.gpu_module_body):
+        allocator.finalize()
+```
+
+### LDS Capacity
+| Architecture | GPU | LDS per CU |
+|---|---|---|
+| gfx942 | MI300X | 64 KB |
+| gfx950 | MI350 | 160 KB |
+
+---
+
+## 6. MFMA Integration (Matrix Math)
+
+### Available MFMA Instructions
+```python
+from flydsl.expr import rocdl
+
+# FP16/BF16 MFMA
+result = rocdl.mfma_f32_16x16x16_f16(a, b, acc)
+
+# FP8 MFMA
+result = rocdl.mfma_f32_16x16x32_fp8(a, b, acc)
+
+# INT8 MFMA
+result = rocdl.mfma_i32_16x16x32i8(a, b, acc)
+```
+
+### GEMM Pattern (Preshuffle)
+The preshuffle GEMM pattern in `kernels/preshuffle_gemm.py`:
+1. B matrix is pre-shuffled to layout: (N/16, K/64, 4, 16, kpack_bytes)
+2. A tiles loaded from global to LDS with XOR16 swizzle for bank-conflict avoidance
+3. K64-byte micro-steps: each step issues 2x K32 MFMA operations
+4. Ping-pong LDS (lds_stage=2) for overlapping loads with compute
+5. Epilogue: either direct row-major store or CShuffle via LDS for packing
+
+---
+
+## 7. Reduction Patterns
+
+### Warp Reduction (AMD wave64)
+XOR-shuffle-based intra-wave reduction:
+```python
+width_i32 = arith.constant(64, type=T.i32())
+for sh in [32, 16, 8, 4, 2, 1]:
+    off = arith.constant(sh, type=T.i32())
+    peer = gpu.ShuffleOp(val, off, width_i32, mode="xor").shuffleResult
+    val = arith.AddFOp(val, peer).result  # or MaximumFOp for max
+```
+
+### Block Reduction
+1. Intra-wave XOR shuffle (shifts: 32, 16, 8, 4, 2, 1)
+2. Lane 0 writes per-wave partial to LDS
+3. `gpu.barrier()`
+4. Wave 0 reads and reduces NUM_WAVES partials from LDS
+
+See `kernels/reduce.py` for reusable implementations.
+
+---
+
+## 8. Common Patterns and Recipes
+
+### Element-wise Kernel Template
+```python
+@flyc.kernel
+def elementwise_kernel(In: fx.Tensor, Out: fx.Tensor, BLOCK: fx.Constexpr[int], VEC: fx.Constexpr[int]):
+    bid, tid = fx.block_idx.x, fx.thread_idx.x
+    tile = BLOCK * VEC
+    tIn = fx.logical_divide(In, fx.make_layout(tile, 1))
+    tOut = fx.logical_divide(Out, fx.make_layout(tile, 1))
+    tIn = fx.slice(tIn, (None, bid))
+    tOut = fx.slice(tOut, (None, bid))
+    tIn = fx.logical_divide(tIn, fx.make_layout(VEC, 1))
+    tOut = fx.logical_divide(tOut, fx.make_layout(VEC, 1))
+    MemTy = fx.MemRefType.get(fx.T.f32(), fx.LayoutType.get(VEC, 1), fx.AddressSpace.Register)
+    copy = fx.make_copy_atom(fx.UniversalCopy(VEC * 32), fx.Float32)
+    rIn = fx.memref_alloca(MemTy, fx.make_layout(VEC, 1))
+    rOut = fx.memref_alloca(MemTy, fx.make_layout(VEC, 1))
+    fx.copy_atom_call(copy, fx.slice(tIn, (None, tid)), rIn)
+    # Transform
+    v = fx.memref_load_vec(rIn)
+    v = fx.arith.mulf(v, v)  # example: square
+    fx.memref_store_vec(v, rOut)
+    fx.copy_atom_call(copy, rOut, fx.slice(tOut, (None, tid)))
+```
+
+### Element-wise Kernel Cookbook (GPU-Verified)
+All recipes below follow the same vectorized copy_atom pattern (256 threads, vec_width=4, 128-bit loads).
+Only the compute section between `memref_load_vec` and `memref_store_vec` differs.
+
+```python
+from flydsl._mlir.ir import VectorType
+
+# --- Scale: C = A * scalar ---
+vA = fx.memref_load_vec(rA)
+vec_ty = VectorType.get([vec_width], fx.T.f32())
+scale = arith.constant_vector(2.0, vec_ty)
+vC = arith.mulf(vA, scale)
+
+# --- Multiply: C = A * B ---
+vC = arith.mulf(fx.memref_load_vec(rA), fx.memref_load_vec(rB))
+
+# --- FMA: D = A * B + C ---
+vAB = arith.mulf(fx.memref_load_vec(rA), fx.memref_load_vec(rB))
+vD = arith.addf(vAB, fx.memref_load_vec(rC))
+
+# --- ReLU: C = max(A, 0) ---
+vA = fx.memref_load_vec(rA)
+vec_ty = VectorType.get([vec_width], fx.T.f32())
+zero_vec = arith.constant_vector(0.0, vec_ty)
+vC = arith.maximumf(vA, zero_vec)
+
+# --- Abs: C = |A| (arith.absf does NOT exist) ---
+vA = fx.memref_load_vec(rA)
+vec_ty = VectorType.get([vec_width], fx.T.f32())
+zero_vec = arith.constant_vector(0.0, vec_ty)
+neg_vA = arith.negf(vA)
+is_neg = arith.cmpf(vA, zero_vec, predicate="olt")
+vC = arith.select(is_neg, neg_vA, vA)
+```
+
+### Naive GEMM Template (for understanding, not performance)
+```python
+@flyc.kernel
+def naive_gemm(A: fx.Tensor, B: fx.Tensor, C: fx.Tensor,
+               M: fx.Constexpr[int], N: fx.Constexpr[int], K: fx.Constexpr[int],
+               BM: fx.Constexpr[int], BN: fx.Constexpr[int]):
+    tid, bid = gpu.thread_idx.x, gpu.block_idx.x
+    bm, bn = bid // (N // BN), bid % (N // BN)
+    tm, tn = tid // BN, tid % BN
+    row, col = bm * BM + tm, bn * BN + tn
+    rsrc_a = buffer_ops.create_buffer_resource(A)
+    rsrc_b = buffer_ops.create_buffer_resource(B)
+    rsrc_c = buffer_ops.create_buffer_resource(C)
+    acc = arith.constant(0.0, type=fx.T.f32())
+    for k in range_constexpr(K):
+        a = buffer_ops.buffer_load(rsrc_a, row * K + k, vec_width=1)
+        b = buffer_ops.buffer_load(rsrc_b, k * N + col, vec_width=1)
+        acc = arith.addf(acc, arith.mulf(a, b))
+    buffer_ops.buffer_store(acc, rsrc_c, row * N + col)
+```
+
+---
+
+## 9. Environment and Debugging
+
+### IR Dump
+```bash
+FLYDSL_DUMP_IR=1 FLYDSL_DUMP_DIR=./dumps python my_kernel.py
+```
+Produces numbered `.mlir` files per pipeline stage plus `final_isa.s`.
+
+### Key Environment Variables
+| Variable | Default | Description |
+|---|---|---|
+| `FLYDSL_DUMP_IR` | false | Dump IR at each stage |
+| `FLYDSL_DEBUG_ENABLE_DEBUG_INFO` | true | Emit DWARF debug info (source-to-asm mapping) |
+| `FLYDSL_RUNTIME_ENABLE_CACHE` | true | Enable kernel caching |
+| `FLYDSL_RUNTIME_CACHE_DIR` | ~/.flydsl/cache | Cache directory |
+| `FLYDSL_COMPILE_OPT_LEVEL` | 2 | Optimization level (0-3) |
+| `ARCH` | auto-detect | Override GPU architecture |
+
+### Disable Cache for Development
+```bash
+FLYDSL_RUNTIME_ENABLE_CACHE=0 python my_kernel.py
+```
+
+### Source-to-Assembly Debug Info
+
+FlyDSL supports source-to-assembly mapping for rocprofv3 ATT traces via the MLIR
+`ensure-debug-info-scope-on-llvm-func` pass (equivalent to Triton's `add_di_scope`).
+
+**How it works**:
+1. FlyDSL's `FuncLocationTracker` generates MLIR `loc()` metadata pointing to Python source lines
+2. The `ensure-debug-info-scope-on-llvm-func{emission-kind=LineTablesOnly}` pass converts MLIR locations into LLVM `DISubprogramAttr` / `DICompileUnitAttr` metadata
+3. The `-g` flag in `gpu-module-to-binary` preserves this metadata as `.debug_line` in the HSACO binary
+4. rocprofv3 ATT reads `.debug_line` to produce `code.json` with `"source_file:line"` entries
+
+**Pipeline position**: After `reconcile-unrealized-casts`, before `gpu-module-to-binary`:
+```
+... -> reconcile-unrealized-casts
+    -> ensure-debug-info-scope-on-llvm-func{emission-kind=LineTablesOnly}  (conditional on enable_debug_info)
+    -> gpu-module-to-binary{format=fatbin opts=-g}
+```
+
+**Verification**: With `FLYDSL_DUMP_IR=1`, check `final_isa.s` for `.file` and `.loc` directives.
+The PA decode kernel achieves 99.9% coverage (1109/1110 ISA instructions mapped to source).
+
+**Key insight**: Without this pass, MLIR `loc()` metadata is silently dropped during MLIR-to-LLVM-IR
+translation. The `-g` flag alone is useless — it preserves debug info, but there's none to preserve
+without the DI scope pass.
+
+### Autotune Module
+
+FlyDSL includes a Triton-style autotune module at `/FlyDSL/python/flydsl/autotune.py`:
+
+```python
+from flydsl.autotune import autotune, Config, do_bench
+
+@autotune(
+    configs=[
+        Config(block_dim=64, vec_width=4),
+        Config(block_dim=128, vec_width=4),
+        Config(block_dim=256, vec_width=4),
+    ],
+    key=['const_n'],     # re-tune when these arg values change
+    warmup=5, rep=25,    # benchmark timing params
+)
+@flyc.jit
+def myKernel(A, C, n: fx.Int32, const_n: fx.Constexpr[int],
+             block_dim: fx.Constexpr[int], vec_width: fx.Constexpr[int],
+             stream: fx.Stream = fx.Stream(None)):
+    ...
+```
+
+- `Config` kwargs become `Constexpr` args injected into `@jit` call
+- `Config.num_warps`, `waves_per_eu`, `maxnreg` are special compiler-level options
+- First call benchmarks all configs; subsequent calls use cached best
+- Disk cache at `~/.flydsl/autotune/{func_name}.json`
+- `do_bench(fn, warmup=5, rep=25)` benchmarks using CUDA/HIP events, returns median ms
+
+**IMPORTANT**: `waves_per_eu` does NOT work via `gpu-module-to-binary opts=`. It needs to be
+set as an LLVM function attribute or through `rocdl-attach-target`. This is a known limitation.
+
+**DLTensorAdaptor bug**: Do NOT use `flyc.from_dlpack()` with pre-wrapped tensors when calling
+a `@jit` function with varying `Constexpr` values. The `DLTensorAdaptor` caches MLIR types from
+the first `ir.Context`, which become invalid when a new context is created (causes segfault).
+Pass raw `torch.Tensor` objects instead.
+
+---
+
+## 10. Troubleshooting
+
+### Common Issues
+
+1. **`arith.constant` signature**: Use `arith.constant(value, type=T.f32())` -- `type` is a keyword argument, NOT positional.
+
+2. **`buffer_ops.buffer_load` offset**: The `offset` parameter is in ELEMENTS, not bytes.
+
+3. **Cache stale after code changes**: Disable cache with `FLYDSL_RUNTIME_ENABLE_CACHE=0` or clear `~/.flydsl/cache/`.
+
+4. **LDS overflow**: Check capacity (64KB on gfx942, 160KB on gfx950). Use `SmemAllocator` which tracks allocations.
+
+5. **Dynamic vs Constexpr**: `Constexpr[int]` values are baked into IR -- different values produce different compiled kernels. Use `Int32` for truly dynamic values.
+
+6. **Tensor layout marking**: For dynamic shapes or alignment, use `flyc.from_dlpack(tensor).mark_layout_dynamic(leading_dim=0, divisibility=4)`.
+
+7. **SmemAllocator finalize**: Must call `allocator.finalize()` inside the GPU module body (use `CompilationContext.get_current().gpu_module_body`).
+
+8. **AMD wavefront size**: Always 64 on gfx9xx. Use shifts [32, 16, 8, 4, 2, 1] for full-wave reduction.
+
+9. **tile_k alignment for GEMM**: `tile_k * elem_bytes` must be divisible by 64 (K64-byte micro-step).
+
+10. **INT4 (W4A8)**: A matrix is int8, B matrix is packed int4 (2 values/byte), unpacked to int8 in-kernel.
+
+11. **`arith.absf` does not exist**: FlyDSL does not expose `arith.absf`. Use `negf + cmpf("olt") + select` pattern instead. See Element-wise Kernel Cookbook.
+
+12. **Scalar broadcast to vector**: Use `arith.constant_vector(value, VectorType.get([width], fx.T.f32()))` to create a splat constant vector. Do NOT try to use a scalar directly with vector `mulf`/`addf` — types must match.
+
+---
+
+## 11. Comparison with Triton/Gluon
+
+| Aspect | FlyDSL | Triton | Gluon |
+|--------|--------|--------|-------|
+| Layout control | Explicit layout algebra (Shape, Stride, Layout) | Implicit via block pointers | Implicit |
+| Tiling | Manual via divide/product operations | Auto-tiling with `tl.program_id` | Auto-tiling |
+| Memory access | Copy atoms, buffer load/store, TiledCopy | `tl.load`/`tl.store` | `gluon.load`/`gluon.store` |
+| MFMA | Direct `rocdl.mfma_*` intrinsics | `tl.dot` | `gluon.dot` |
+| Shared memory | SmemAllocator with explicit management | Implicit scratchpad | Implicit |
+| Abstraction level | Low (near hardware) | Medium | Medium-High |
+| Compilation | MLIR (Fly dialect -> LLVM -> HSACO) | MLIR (Triton dialect -> LLVM) | MLIR |
+| Control | Maximum control over data layout and movement | Less control, more automation | Least control |
+
+FlyDSL gives maximum control at the cost of verbosity. The layout algebra is the key differentiator -- it enables precise control over how data is arranged in registers, shared memory, and global memory, and how threads map to data.
+
+---
+
+## 12. Running Kernels
+
+### SSH to Remote Host
+```bash
+# Run a kernel
+ssh -o LogLevel=ERROR hjbog-srdc-39.amd.com 'docker exec hungry_dijkstra bash -c "cd /FlyDSL && python3 my_kernel.py"'
+
+# Run existing tests
+ssh -o LogLevel=ERROR hjbog-srdc-39.amd.com 'docker exec hungry_dijkstra bash -c "cd /FlyDSL && python3 tests/kernels/test_vec_add.py"'
+
+# Run benchmarks
+ssh -o LogLevel=ERROR hjbog-srdc-39.amd.com 'docker exec hungry_dijkstra bash -c "cd /FlyDSL && bash scripts/run_benchmark.sh"'
+```
diff --git a/.claude/skills/format-code/SKILL.md b/.claude/skills/format-code/SKILL.md
@@ -0,0 +1,95 @@
+---
+name: format-code
+description: >
+  Format and clean up code before committing. Removes unused imports/variables from Python files
+  (autoflake), formats Python with black, and formats C/C++ with clang-format (Google style).
+  Use this skill whenever the user says "format code", "clean up code", "lint", "format before commit",
+  "code formatting", "/format-code", or wants to tidy up changed files before a git commit.
+  Also trigger when the user mentions autoflake, black formatting, or clang-format in the context
+  of cleaning up their working tree.
+user_invocable: true
+---
+
+# Format Code
+
+Format and clean up changed files before committing. Operates only on files that are staged
+(`git diff --cached`) or modified in the working tree (`git diff`), so unchanged files are
+never touched.
+
+## Pipeline
+
+For each changed file, the pipeline runs in order:
+
+1. **Python (.py)**: autoflake (remove unused imports & variables) -> black (format)
+2. **C/C++ (.c, .cc, .cpp, .cxx, .h, .hpp, .hxx)**: clang-format with Google style
+
+## Steps
+
+### 1. Ensure tools are installed
+
+Check each tool and install any that are missing. Do all checks first, then install in one batch.
+
+```bash
+# Check availability
+command -v autoflake &>/dev/null || NEED_PY=1
+command -v black &>/dev/null || NEED_PY=1
+command -v clang-format &>/dev/null || NEED_CF=1
+
+# Install if needed
+if [ -n "$NEED_PY" ]; then
+  pip install autoflake black
+fi
+if [ -n "$NEED_CF" ]; then
+  sudo apt-get install -y clang-format 2>/dev/null || pip install clang-format
+fi
+```
+
+### 2. Collect changed files
+
+Gather the union of staged and unstaged changed files (no duplicates):
+
+```bash
+(git diff --name-only --cached; git diff --name-only) | sort -u
+```
+
+If no files are changed, tell the user there is nothing to format and stop.
+
+### 3. Format Python files
+
+For every `.py` file in the changed set:
+
+```bash
+# Remove unused imports and variables (in-place)
+autoflake --in-place --remove-all-unused-imports --remove-unused-variables "$file"
+
+# Format with black (default settings)
+black "$file"
+```
+
+### 4. Format C/C++ files
+
+For every `.c`, `.cc`, `.cpp`, `.cxx`, `.h`, `.hpp`, `.hxx` file in the changed set:
+
+```bash
+clang-format -i --style=Google "$file"
+```
+
+### 5. Report summary
+
+After formatting, print a summary listing:
+- How many Python files were cleaned and formatted
+- How many C/C++ files were formatted
+- The names of all formatted files
+
+If any files were staged before formatting, remind the user to re-stage them
+(`git add <files>`) since the in-place edits made them show as modified again.
+
+## Notes
+
+- This skill never adds or removes files from git staging -- it only modifies file contents in place.
+- Files that are not Python or C/C++ are silently skipped.
+- autoflake's `--remove-unused-variables` only removes simple unused assignments (e.g. `x = 1`
+  where `x` is never read). It does not remove unused functions or classes -- that requires
+  manual review.
+- black uses its default configuration. If the project has a `pyproject.toml` with `[tool.black]`
+  settings, black will pick those up automatically.
diff --git a/.claude/skills/gemm-optimization/SKILL.md b/.claude/skills/gemm-optimization/SKILL.md
@@ -0,0 +1,698 @@
+---
+name: gemm-optimization
+description: >
+  Comprehensive guide to optimizing GEMM (General Matrix Multiply) kernels in
+  FlyDSL on AMD CDNA GPUs. Covers tiling strategy, LDS ping-pong double-buffer,
+  XOR bank-conflict swizzle, A/B data prefetch pipeline, 2-stage software
+  pipelining, MFMA instruction scheduling (hot_loop_scheduler), epilogue
+  strategies (direct store vs CShuffle), TFLOPS/bandwidth calculation, main-loop
+  instruction count analysis, and bottleneck identification from ATT traces.
+  Based on the production preshuffle_gemm kernel.
+  Usage: /gemm-optimization
+tools: Read,Edit,Bash,Grep,Glob,Agent
+---
+
+# GEMM Optimization Guide
+
+Comprehensive guide to writing and optimizing high-performance GEMM kernels in
+FlyDSL on AMD CDNA GPUs (MI300X gfx942, MI350 gfx950).
+
+Based on the production `kernels/preshuffle_gemm.py` implementation.
+
+---
+
+## 1. Tiling Strategy
+
+### 1.1 Three-Level Tiling
+
+GEMM tiles the output C[M, N] and the reduction K into blocks:
+
+```
+C[M, N] = A[M, K] × B[K, N]^T
+
+Grid mapping:
+  block_x → M tiles (tile_m rows each)
+  block_y → N tiles (tile_n cols each)
+
+Thread mapping (256 threads = 4 waves × 64 lanes):
+  wave_id = tid // 64  ∈ [0, 3]     → N dimension partitioning
+  lane_id = tid % 64   ∈ [0, 63]    → M + N dimension within wave
+  lane_div_16 = lane_id // 16       → M dimension (4 groups of 16)
+  lane_mod_16 = lane_id % 16        → N dimension within MFMA
+```
+
+### 1.2 Derived Tile Parameters
+
+```python
+m_repeat   = tile_m // 16            # M-direction 16x16 MFMA repeat count
+n_per_wave = tile_n // 4             # N range per wave (4 waves split tile_n)
+num_acc_n  = n_per_wave // 16        # N-direction 16x16 accumulators per wave
+k_unroll   = tile_k_bytes // a_elem_vec_pack // 64  # K-steps per tile (K64 micro-steps)
+```
+
+### 1.3 Recommended Tile Configurations
+
+| Scenario | tile_m | tile_n | tile_k | Data Type | Notes |
+|----------|--------|--------|--------|-----------|-------|
+| Small batch (M ≤ 32) | 16 | 64-128 | 256-512 | FP8/INT8 | Memory-bound, large tile_k for reuse |
+| Medium batch | 64 | 256 | 128 | FP8/INT8/BF16 | Balanced compute/memory |
+| Large batch (M ≥ 4096) | 128 | 256 | 128 | FP8/INT8 | Compute-dense, needs async copy |
+| FP4 (gfx950) | 32-64 | 128-256 | 256 | FP4 | MFMA_SCALE instructions |
+
+### 1.4 Tile Size Constraints
+
+- `tile_m` must be multiple of 16 (MFMA M dimension)
+- `tile_n` must be multiple of 64 (4 waves × 16 N per MFMA)
+- `tile_k * elem_bytes` must be multiple of 64 (K64-byte micro-step)
+- `tile_m * tile_k * elem_bytes` should fit comfortably in LDS (64KB on gfx942, 160KB on gfx950)
+- B matrix is pre-shuffled to `(N/16, K/64, 4, 16, kpack_bytes)` layout — tile_k must divide K evenly
+
+### 1.5 MFMA Count Per Tile
+
+Total MFMA instructions per tile:
+
+```
+MFMA_per_tile = k_unroll × m_repeat × num_acc_n × 2
+                                                  ↑ 2x K32 per K64 micro-step
+
+Example (tile 64×256×128, FP8):
+  k_unroll = 128 / 64 = 2
+  m_repeat = 64 / 16 = 4
+  num_acc_n = 256 / 4 / 16 = 4
+  MFMA_per_tile = 2 × 4 × 4 × 2 = 64 MFMAs
+
+Example (tile 64×256×512, FP8):
+  k_unroll = 512 / 64 = 8
+  MFMA_per_tile = 8 × 4 × 4 × 2 = 256 MFMAs
+```
+
+---
+
+## 2. LDS Ping-Pong Double Buffer (2-Stage Pipeline)
+
+### 2.1 Concept
+
+With `lds_stage=2`, the kernel allocates **two separate LDS buffers** for the A
+tile. While one buffer is used for MFMA computation, the next K-tile's A data
+is loaded into the other buffer. This hides the global-to-LDS load latency.
+
+```
+Time →
+Buffer PONG: [Compute tile_k=0] [   Load tile_k=2  ] [Compute tile_k=2] ...
+Buffer PING: [   Load tile_k=1  ] [Compute tile_k=1] [   Load tile_k=3  ] ...
+```
+
+### 2.2 FlyDSL Implementation
+
+```python
+# Two independent SmemAllocators (separate LDS regions)
+allocator_pong = SmemAllocator(None, arch="gfx942", global_sym_name="smem0")
+allocator_ping = SmemAllocator(None, arch="gfx942", global_sym_name="smem1")
+
+lds_a_pong = allocator_pong.allocate_array(T.i8, buffer_size_bytes)
+lds_a_ping = allocator_ping.allocate_array(T.i8, buffer_size_bytes)
+```
+
+### 2.3 Main Loop Structure (2-Stage)
+
+Each iteration processes **2 K-tiles** (one pong, one ping):
+
+```python
+def _build_pingpong_body(k_iv, inner_state):
+    accs_in, bt_flat_in, a0pf_in = _unpack_state(inner_state)
+    b_tile_pong_in = _unflatten_b_tile(bt_flat_in)
+
+    # Phase 1: compute on PONG, prefetch to PING
+    next_k1 = k_iv + tile_k
+    store_a_tile_to_lds(prefetch_a_tile(next_k1), lds_a_ping)  # A → PING LDS
+    b_tile_ping = prefetch_b_tile(next_k1)                      # B → VGPR
+    accs_in, _ = compute_tile(accs_in, b_tile_pong_in, lds_a_pong,
+                              a0_prefetch=a0pf_in)
+    hot_loop_scheduler()                                         # instruction hints
+    rocdl.s_waitcnt(num_b_loads)
+    gpu.barrier()
+    a0_prefetch_ping = prefetch_a0_pack(lds_a_ping)
+
+    # Phase 2: compute on PING, prefetch to PONG
+    next_k2 = k_iv + (tile_k * 2)
+    store_a_tile_to_lds(prefetch_a_tile(next_k2), lds_a_pong)  # A → PONG LDS
+    b_tile_pong_new = prefetch_b_tile(next_k2)                   # B → VGPR
+    accs_in, _ = compute_tile(accs_in, b_tile_ping, lds_a_ping,
+                              a0_prefetch=a0_prefetch_ping)
+    hot_loop_scheduler()
+    rocdl.s_waitcnt(num_b_loads)
+    gpu.barrier()
+    a0_prefetch_pong_new = prefetch_a0_pack(lds_a_pong)
+
+    return _pack_state(accs_in, _flatten_b_tile(b_tile_pong_new),
+                       a0_prefetch_pong_new)
+```
+
+### 2.4 LDS Size Budget
+
+```
+lds_tile_bytes = tile_m × tile_k × elem_bytes
+2-stage total = 2 × lds_tile_bytes
++ CShuffle epilogue (optional): tile_m × tile_n × 2 bytes
+
+Example (64×128, FP8): 2 × 64 × 128 = 16 KB total
+Example (128×128, FP8): 2 × 128 × 128 = 32 KB total
+```
+
+Limits: 64 KB on gfx942, 160 KB on gfx950.
+
+---
+
+## 3. LDS XOR Bank-Conflict Swizzle
+
+### 3.1 The Problem
+
+A tile stored row-major in LDS with stride = tile_k creates bank conflicts when
+multiple rows are read simultaneously (threads in the same wave access the same
+bank for different addresses).
+
+### 3.2 XOR Swizzle Formula
+
+```python
+def swizzle_xor16(row, col, k_blocks16):
+    """XOR-with-row swizzle at 16-byte granularity."""
+    rem = row % k_blocks16
+    return col ^ (rem * 16)
+```
+
+- `k_blocks16 = tile_k_bytes // a_elem_vec_pack // 16` — number of 16-byte blocks in K
+- Applied to both **write** (global → LDS) and **read** (LDS → VGPR) paths
+- Zero LDS overhead (no extra bytes), ~1 SALU instruction per address
+
+### 3.3 Write Path
+
+```python
+# In store_a_tile_to_lds():
+col_swz_bytes = swizzle_xor16(row_a_local, col_local_bytes, k_blocks16)
+lds_offset = row_a_local * lds_stride_bytes + col_swz_bytes
+lds_ptr.store(data, [lds_offset])
+```
+
+### 3.4 Read Path
+
+```python
+# In lds_load_packs_k64():
+col_base_swz_bytes = swizzle_xor16(curr_row_a_lds, col_base, k_blocks16)
+lds_offset = curr_row_a_lds * lds_stride_bytes + col_base_swz_bytes
+a_pack = lds_ptr.load([lds_offset])
+```
+
+**Critical**: swizzle must be consistent between write and read. If one path
+uses swizzle but the other doesn't, data will be read from wrong positions.
+
+---
+
+## 4. Data Prefetch Pipeline
+
+### 4.1 A Matrix: Global → LDS
+
+Two paths for loading A into LDS:
+
+**Synchronous** (default): Global → VGPR → LDS
+```python
+a_regs = prefetch_a_tile(base_k)          # buffer_load_dwordx4 → VGPR
+store_a_tile_to_lds(a_regs, lds_buffer)   # ds_write from VGPR → LDS
+```
+
+**Asynchronous** (use_async_copy=True): Global → LDS directly
+```python
+prefetch_a_to_lds(base_k, lds_buffer)  # raw_ptr_buffer_load_lds (DMA)
+```
+Async copy bypasses VGPR, reducing register pressure. Available on gfx942/gfx950.
+
+### 4.2 B Matrix: Global → VGPR (Preshuffle)
+
+B is pre-shuffled to match MFMA register layout, loaded directly to VGPR:
+
+```python
+b_tile = prefetch_b_tile(base_k)  # buffer_load_dwordx4 → VGPR
+# b_tile structure: k_unroll × [(packs0[num_acc_n], packs1[num_acc_n])]
+```
+
+Each K64 micro-step needs `2 × num_acc_n` i64 values for B (K32 × 2).
+
+### 4.3 A0 Prefetch (Cross-Tile LDS Prefetch)
+
+After `gpu.barrier()` completes (LDS is valid), immediately load the first A
+pack from LDS into VGPR registers, overlapping with upcoming VMEM loads:
+
+```python
+a0_prefetch = lds_load_packs_k64(row_a_lds, col_offset_base_bytes, lds_buffer)
+```
+
+This hides the first `ds_read` latency (~20-40 cycles) behind the global loads
+that follow.
+
+### 4.4 Pipeline Timeline
+
+```
+Iter i:
+  1. [VMEM] Load A(i+1) → PING LDS, Load B(i+1) → VGPR
+  2. [MFMA] Compute tile(i) using PONG LDS + B(i) VGPR
+  3. [SCHED] hot_loop_scheduler() — interleave MFMA with pending loads
+  4. [SYNC] s_waitcnt + barrier — wait for PING LDS to be valid
+  5. [LDS] A0 prefetch from PING — ds_read first pack
+
+  Swap PING ↔ PONG, repeat for i+1
+```
+
+---
+
+## 5. Instruction Scheduling (hot_loop_scheduler)
+
+### 5.1 Purpose
+
+The `hot_loop_scheduler()` inserts `rocdl.sched_*` hints between the MFMA
+compute phase and the next iteration's loads. These hints tell the compiler
+how to interleave different instruction types to maximize pipeline utilization.
+
+### 5.2 Scheduling Primitives
+
+| Hint | Meaning | Maps to |
+|------|---------|---------|
+| `rocdl.sched_barrier(0)` | Full scheduling barrier — no reordering across | Compiler fence |
+| `rocdl.sched_mfma(N)` | Allow N MFMA instructions | `v_mfma_*` |
+| `rocdl.sched_dsrd(N)` | Allow N LDS read instructions | `ds_read_*` |
+| `rocdl.sched_dswr(N)` | Allow N LDS write instructions | `ds_write_*` |
+| `rocdl.sched_vmem(N)` | Allow N global memory instructions | `buffer_load_*` |
+
+### 5.3 Standard Schedule Pattern (gfx942, sync copy)
+
+```python
+def hot_loop_scheduler():
+    mfma_group = num_acc_n
+    mfma_total = (k_unroll * 2) * m_repeat * mfma_group
+    mfma_per_iter = 2 * mfma_group
+    sche_iters = mfma_total // mfma_per_iter
+
+    # Prologue: pre-load first 2 LDS packs, interleave with first few MFMAs
+    rocdl.sched_dsrd(2)                    # 2 ds_read for a0_prefetch
+    rocdl.sched_mfma(1)
+    rocdl.sched_mfma(1)
+
+    # Main schedule: each iteration = 1 VMEM + mfma_group MFMAs + 1 ds_read + mfma_group MFMAs
+    dswr_tail = num_a_loads
+    dswr_start = max(sche_iters - dswr_tail - 2, 0)
+    for sche_i in range_constexpr(sche_iters):
+        rocdl.sched_vmem(1)                # 1 global load (B tile or A tile)
+        rocdl.sched_mfma(mfma_group)       # N MFMA instructions
+        rocdl.sched_dsrd(1)                # 1 LDS read (A data)
+        rocdl.sched_mfma(mfma_group)       # N more MFMAs
+        if sche_i >= dswr_start - 1:
+            rocdl.sched_dswr(1)            # LDS write (next A tile, tail end)
+
+    rocdl.sched_barrier(0)                 # fence
+```
+
+### 5.4 Key Scheduling Insights
+
+1. **MFMA instructions dominate**: they form the backbone of the schedule
+2. **LDS reads (ds_read) interleave with MFMAs**: one ds_read per 2×mfma_group MFMAs
+3. **Global loads (VMEM) interleave**: one buffer_load per scheduler iteration
+4. **LDS writes (ds_write) go at the tail**: they overlap with the last MFMAs
+   of the current tile, landing before the `gpu.barrier()` at iteration boundary
+5. **dswr_start** ensures LDS writes are scheduled early enough to complete
+   before the barrier, but late enough to not interfere with compute
+
+### 5.5 Async Copy Schedule (gfx950)
+
+For async copy, the scheduler uses `_build_scheduler()` to evenly distribute
+ds_read and VMEM loads across all MFMAs:
+
+```python
+dsrd_schedule = _build_scheduler(num_ds_load - dsrd_preload, mfma_total)
+vmem_schedule = _build_scheduler(num_gmem_loads, mfma_total)
+```
+
+This produces a per-MFMA schedule: after each `sched_mfma(1)`, emit the
+appropriate number of `sched_dsrd` and `sched_vmem` hints.
+
+---
+
+## 6. MFMA Inner Loop Structure
+
+### 6.1 K64 Micro-Step (FP8/INT8)
+
+Each K64 micro-step performs 2× K32 MFMA calls:
+
+```python
+for ku in range_constexpr(k_unroll):           # K dimension (K64 steps)
+    b_packs0, b_packs1 = b_tile_in[ku]        # B data for this K64 step
+    col_base = col_offset_base_bytes + ku * 64 # LDS column offset
+
+    for mi in range_constexpr(m_repeat):       # M dimension (16-row blocks)
+        curr_row_a_lds = row_a_lds + (mi * 16)
+        a0, a1 = lds_load_packs_k64(...)      # Load A from LDS (2× i64)
+
+        for ni in range_constexpr(num_acc_n):  # N dimension (16-col accumulators)
+            acc[mi * num_acc_n + ni] = mfma_k64_bytes(
+                acc[mi * num_acc_n + ni],
+                a0, a1,
+                b_packs0[ni], b_packs1[ni]
+            )
+```
+
+### 6.2 MFMA Instruction Selection
+
+| Data Type | K per MFMA | Instruction | Accumulator |
+|-----------|-----------|-------------|-------------|
+| FP8 | K=32 | `mfma_f32_16x16x32_fp8_fp8` | f32×4 |
+| INT8 | K=32 | `mfma_i32_16x16x32i8` | i32×4 |
+| BF16 | K=16 | `mfma_f32_16x16x16bf16_1k` | f32×4 |
+| FP16 | K=16 | `mfma_f32_16x16x16f16` | f32×4 |
+| FP4 (gfx950) | K=128 | `mfma_scale_f32_16x16x128_f8f6f4` | f32×4 |
+
+---
+
+## 7. Epilogue Strategies
+
+### 7.1 Direct Store (Default)
+
+Each thread writes its MFMA accumulator elements directly to global memory:
+
+```python
+# Row mapping: MFMA output layout → global C matrix
+for mi in range_constexpr(m_repeat):
+    for ii in range(4):  # 4 rows per lane_div_16 group
+        row = bx_m + mi * 16 + lane_div_16 * 4 + ii
+        for ni in range_constexpr(num_acc_n):
+            col = by_n + wave_id * n_per_wave + ni * 16 + lane_mod_16
+            # scale + truncate + store
+            val = acc[mi * num_acc_n + ni][ii] * scale_a * scale_b
+            buffer_store(truncate(val, out_dtype), c_rsrc, row * N + col)
+```
+
+**Pros**: no extra LDS, simple
+**Cons**: non-coalesced stores for some tile sizes
+
+### 7.2 CShuffle Epilogue
+
+Rearranges thread-to-element mapping via LDS for coalesced global writes:
+
+1. **Write to LDS**: accumulator values written row-major to `lds_out`
+2. **Barrier**: synchronize all threads
+3. **Shuffle read**: threads re-map to `(MLane=8, NLane=32)` for contiguous output
+4. **Store**: `buffer_store_dwordx2` for 4-element vectorized writes
+
+```python
+# CShuffle parameters
+e_vec = 4 if (tile_n % 128 == 0) else 2
+m_reps_shuffle = tile_m // 8
+n_reps_shuffle = tile_n // (32 * e_vec)
+```
+
+**Pros**: coalesced stores, higher memory throughput
+**Cons**: extra LDS allocation + barrier
+
+**When to use**: for large tile_n (≥ 128) where output coalescing matters.
+
+---
+
+## 8. Performance Metrics and Bottleneck Analysis
+
+### 8.1 TFLOPS Calculation
+
+```python
+flops = 2 * M * N * K                      # each multiply-add = 2 FLOPs
+tflops = flops / (us / 1e6) / 1e12         # TFLOPS
+
+# Peak references (gfx942 MI300X, single GCD):
+#   FP8:  ~653 TFLOPS peak (mfma_f32_16x16x32_fp8)
+#   BF16: ~326 TFLOPS peak
+#   INT8: ~653 TOPS peak
+```
+
+### 8.2 Bandwidth Calculation
+
+```python
+# FP8/INT8:
+bytes_moved = (M * K * elem_bytes)     # A matrix
+            + (N * K * elem_bytes)     # B matrix (pre-shuffled)
+            + (M * N * 2)              # C output (bf16/fp16)
+            + (M + N) * 4             # per-token scales (f32)
+
+# INT4:
+bytes_moved = (M * K) + (N * K) // 2 + (M * N * 2) + (M + N) * 4
+
+# FP4 (MXFP4):
+bytes_moved = (M * K) // 2 + (N * K) // 2 + (M * N * 2) + (M + N) * (K // 32)
+
+tbps = bytes_moved / 1e12 / (us / 1e6)  # TB/s
+```
+
+### 8.3 Memory-Bound vs Compute-Bound
+
+```
+Arithmetic Intensity = flops / bytes_moved
+
+AI < roofline_crossover → memory-bound
+AI > roofline_crossover → compute-bound
+
+Practical rule: M ≤ 512 → memory-bound (focus on bandwidth)
+               M > 512 → compute-bound (focus on MFMA utilization)
+```
+
+### 8.4 Bottleneck Identification from ATT Traces
+
+Run `/kernel-trace-analysis` on the GEMM kernel, then check:
+
+| Symptom | Bottleneck | Action |
+|---------|-----------|--------|
+| High `s_waitcnt vmcnt(0)` stall before MFMA | Global load latency exposed | Improve prefetch overlap, increase tile_k |
+| High `s_waitcnt lgkmcnt(0)` stall | LDS latency exposed | Increase write-read distance, check bank conflicts |
+| High `s_barrier` stall | Workgroup sync overhead | Check LDS stage, reduce barrier count |
+| Low MFMA utilization (< 50%) | Memory-bound | Increase tile size, prefetch more aggressively |
+| Many `s_nop` between MFMAs | Pipeline bubbles | Interleave loads between MFMAs, tune scheduler |
+| High-cycle `buffer_load` | TA-blocked | Reduce concurrent loads, check access coalescing |
+
+---
+
+## 9. Main-Loop Instruction Count Analysis
+
+### 9.1 Counting Method
+
+Dump ISA and count instructions in the main MFMA loop:
+
+```bash
+FLYDSL_DUMP_IR=1 python my_gemm.py
+# Check final_isa.s for the hot loop between two s_barrier instructions
+```
+
+Or use rocprofv3 ATT trace `code.json` to identify the loop body by examining
+instructions between repeated `s_barrier` patterns.
+
+### 9.2 Expected Instruction Counts Per Tile (FP8, sync copy)
+
+For tile (64, 256, 128), FP8, lds_stage=2:
+
+| Category | Count | Formula |
+|----------|-------|---------|
+| **MFMA** | 64 | k_unroll × m_repeat × num_acc_n × 2 = 2×4×4×2 |
+| **ds_read** (A from LDS) | ~16 | k_unroll × m_repeat × 2 (a0, a1 per mi) |
+| **buffer_load** (B from global) | ~16 | k_unroll × 2 × num_acc_n |
+| **buffer_load** (A to VGPR) | ~8 | num_a_loads (A tile for next iter) |
+| **ds_write** (A VGPR → LDS) | ~8 | num_a_loads (store to LDS) |
+| **s_barrier** | 1 | synchronization |
+| **SALU** (address, swizzle) | ~20-30 | offset computation, XOR swizzle |
+| **Total** | ~130-150 | depends on tile config |
+
+### 9.3 Ideal Ratios
+
+```
+MFMA ratio = MFMA_count / total_instructions
+  > 40%: good (compute-dominant loop)
+  30-40%: acceptable (some overhead)
+  < 30%: too much non-MFMA overhead, review scheduling
+
+Memory instructions = ds_read + buffer_load + ds_write
+Memory ratio = memory_count / total_instructions
+  < 40%: good overlap
+  > 50%: memory-dominant, try larger tile_k or fewer loads
+```
+
+### 9.4 Comparing with Reference Kernels
+
+When aligning FlyDSL GEMM with reference implementations (e.g., aiter):
+
+```bash
+# Count key instructions in ISA
+grep -c "v_mfma"        final_isa.s       # MFMA count
+grep -c "s_barrier"     final_isa.s       # barrier count
+grep -c "buffer_load"   final_isa.s       # global loads
+grep -c "ds_read"       final_isa.s       # LDS reads
+grep -c "ds_write"      final_isa.s       # LDS writes
+```
+
+Target: FlyDSL MFMA count should match reference; barrier count ≤ reference.
+
+---
+
+## 10. Register Budget
+
+### 10.1 VGPR Estimation
+
+```
+Accumulators: m_repeat × num_acc_n × 4 VGPRs (f32×4 per accumulator)
+B tile:       k_unroll × 2 × num_acc_n × 2 VGPRs (i64 per B pack)
+A prefetch:   2 × 2 VGPRs (a0 prefetch, 2× i64)
+A tile regs:  num_a_loads × 4 VGPRs (if sync copy, dwordx4 per load)
+Address:      ~10-20 VGPRs (offsets, indices)
+```
+
+Example (tile 64×256×128, FP8):
+```
+Accumulators: 4 × 4 × 4 = 64 VGPRs
+B tile:       2 × 2 × 4 × 2 = 32 VGPRs
+A prefetch:   4 VGPRs
+A tile regs:  8 × 4 = 32 VGPRs
+Address:      ~16 VGPRs
+Total:        ~148 arch_vgpr
+```
+
+### 10.2 Occupancy Impact
+
+On gfx942 (256 arch_vgpr + 256 accum_vgpr per SIMD):
+
+| arch_vgpr | accum_vgpr | Waves/SIMD | Assessment |
+|-----------|-----------|------------|------------|
+| ≤ 128 | ≤ 128 | 2 | Good |
+| 129-256 | ≤ 256 | 1 | Acceptable for compute-bound |
+| > 256 | any | SPILL | Critical regression |
+
+MFMA accumulators use **accum_vgpr** (separate file). Prefetch buffers, B tile,
+and A tile use **arch_vgpr**. These do not compete.
+
+---
+
+## 11. Async Copy (gfx942/gfx950)
+
+### 11.1 When to Use
+
+- `tile_m ≥ 128` (enough compute to hide async DMA latency)
+- Saves arch_vgpr (A data bypasses VGPR, goes directly Global → LDS)
+- Requires `use_async_copy=True`
+
+### 11.2 Implementation
+
+```python
+# Direct global → LDS DMA
+rocdl.raw_ptr_buffer_load_lds(
+    a_rsrc, lds_ptr, size_i32, global_offset,
+    soffset, offset_imm, aux,
+)
+# gfx942: 4 bytes per DMA op
+# gfx950: 16 bytes per DMA op
+```
+
+### 11.3 Trade-offs
+
+| Aspect | Sync Copy | Async Copy |
+|--------|----------|------------|
+| Path | Global → VGPR → LDS | Global → LDS (DMA) |
+| arch_vgpr usage | +32 for A tile regs | 0 (A bypasses VGPR) |
+| Scheduling | Explicit ds_write interleaving | DMA engine handles transfer |
+| Best for | Small tile_m, low register pressure | Large tile_m (≥ 128) |
+| gfx942 granularity | 16B (dwordx4) | 4B (1 dword per DMA) |
+| gfx950 granularity | 16B (dwordx4) | 16B (4 dwords per DMA) |
+
+---
+
+## 12. B Matrix Preshuffle Layout
+
+### 12.1 Preshuffle Format
+
+B is pre-transposed and reshuffled on CPU before kernel launch:
+
+```
+Original B: [N, K]  (row-major)
+Preshuffle: [N/16, K/kpack, 4, 16, kpack_bytes]
+```
+
+Where:
+- `kpack = 64 // elem_bytes` for FP8/INT8 (kpack=64), `4` for BF16/FP16 (kpack=4)
+- The `4` dimension maps to 4 dwords per lane (buffer_load_dwordx4)
+- The `16` dimension maps to 16 lanes within MFMA
+
+### 12.2 Benefits
+
+- Global loads map directly to MFMA register layout — no VALU shuffle needed
+- Coalesced global access (consecutive threads load consecutive addresses)
+- One-time CPU cost, amortized over many kernel invocations
+
+---
+
+## 13. Quick Reference: Optimization Checklist
+
+| Stage | Check | Action if Failing |
+|-------|-------|-------------------|
+| **Tiling** | tile_m × tile_n fills GPU (enough blocks) | Reduce tile size |
+| **Tiling** | tile_k × elem_bytes ≤ LDS budget / 2 | Reduce tile_k |
+| **LDS** | Bank conflict count (trace ds_read stalls) | Apply XOR swizzle |
+| **Prefetch** | VMEM stalls before MFMA in trace | Improve prefetch pipeline |
+| **2-Stage** | Using lds_stage=2 | Enable double-buffer |
+| **Scheduler** | s_nop / idle between MFMAs | Tune hot_loop_scheduler |
+| **Epilogue** | Output store bandwidth | Use CShuffle for large tile_n |
+| **Registers** | arch_vgpr ≤ 256 | Reduce buffers, use async copy |
+| **ISA Count** | MFMA ratio ≥ 40% | Reduce non-MFMA overhead |
+| **Performance** | TFLOPS vs peak | Identify bottleneck category |
+
+---
+
+## 14. Worked Example: Optimizing a 5120×5120×8320 FP8 GEMM
+
+### Step 1: Choose tile size
+
+```
+tile_m=64, tile_n=256, tile_k=128
+Grid: (5120/64) × (5120/256) = 80 × 20 = 1600 blocks
+```
+
+### Step 2: Estimate MFMA count
+
+```
+k_unroll = 128/64 = 2, m_repeat = 64/16 = 4, num_acc_n = 256/4/16 = 4
+MFMA_per_tile = 2 × 4 × 4 × 2 = 64
+Total MFMAs per block = 64 × (8320/128) = 64 × 65 = 4160
+```
+
+### Step 3: Estimate LDS usage
+
+```
+lds_tile = 64 × 128 = 8 KB
+2-stage = 16 KB (well within 64 KB limit)
+```
+
+### Step 4: Estimate VGPR
+
+```
+Accumulators: 4 × 4 × 4 = 64 (→ accum_vgpr)
+B tile: 2 × 2 × 4 × 2 = 32
+A tile: 8 × 4 = 32
+Total arch_vgpr ≈ 80 + overhead → ~120 (occupancy = 2 waves)
+```
+
+### Step 5: Calculate theoretical performance
+
+```
+flops = 2 × 5120 × 5120 × 8320 = 436 GFLOP
+Target: ~500 TFLOPS → ~0.87 ms
+bytes = 5120×8320 + 5120×8320 + 5120×5120×2 + (5120+5120)×4
+     = 85.2M + 52.4M + 0.04M = 137.6 MB
+Bandwidth: 137.6 MB / 0.87 ms = 158 GB/s (well below HBM peak)
+→ Compute-bound, focus on MFMA utilization
+```
+
+### Step 6: Profile and iterate
+
+```bash
+rocprofv3 --kernel-trace --stats -f csv -- python test_preshuffle_gemm.py \
+    --in_dtype fp8 -M 5120 -N 5120 -K 8320 --tile_m 64 --tile_n 256 --tile_k 128
+```
+
+Compare GPU kernel time with theoretical minimum. If >1.5× theoretical,
+run ATT trace analysis (`/kernel-trace-analysis`) to identify bottleneck.
\ No newline at end of file
diff --git a/.claude/skills/lds-optimization/SKILL.md b/.claude/skills/lds-optimization/SKILL.md
@@ -0,0 +1,371 @@
+---
+name: lds-optimization
+description: >
+  Optimize LDS (Local Data Share / shared memory) access patterns in FlyDSL
+  GPU kernels. Diagnose bank conflicts and high lgkmcnt stalls from ATT trace
+  data, then apply swizzle or padding layouts to eliminate conflicts. Also
+  increase the distance between LDS write and subsequent LDS read to hide LDS
+  latency. LDS read preceded by write always requires a sync (s_waitcnt
+  lgkmcnt or s_barrier). Use when trace analysis shows ds_read/ds_write/lgkmcnt
+  as a bottleneck.
+  Usage: /lds-optimization
+tools: Read,Edit,Bash,Grep,Glob,Agent
+---
+
+# LDS Optimization
+
+Diagnose and fix LDS (shared memory) performance issues in FlyDSL kernels
+on AMD CDNA GPUs (MI300X/MI308/MI350).
+
+## When To Use
+
+Run `/kernel-trace-analysis` first. Apply this skill when the trace shows:
+
+| Signal | Threshold | Example |
+|--------|-----------|---------|
+| `s_waitcnt lgkmcnt(0)` with high stall | > 3000 cycles per instance | `L605: stall=4080 s_waitcnt lgkmcnt(0)` |
+| `ds_write` / `ds_read` with high latency | > 500 cycles per instance | `L761: stall=960 ds_write2_b32` |
+| Multiple `s_barrier` between `ds_write` and `ds_read` | Barrier stall > 5000 | `L606: stall=17024 s_barrier` |
+| Total LDS-related stall > 15% of kernel stall | Sum all lgkmcnt + ds stalls | Softmax reduce phase in PA decode |
+
+## LDS Architecture on CDNA3 (gfx942)
+
+### Hardware Facts
+
+- LDS size: **64 KB per CU** (workgroup-shared)
+- LDS is organized into **32 banks**, each **4 bytes wide**
+- Bank index = `(byte_address / 4) % 32`
+- **Bank conflict**: when 2+ threads in the same wavefront access **different addresses** in the **same bank** in the same cycle, accesses are serialized
+- **Broadcast**: when 2+ threads access the **same address** in the same bank, hardware broadcasts (no conflict)
+- LDS throughput: **128 bytes/cycle** (peak, no conflicts)
+- LDS latency: **~20-40 cycles** (async, hidden if enough work between write and read)
+- **VGPR context**: LDS ops use **arch_vgpr** (not accum_vgpr). On CDNA3, arch_vgpr and accum_vgpr are separate 256-entry register files. LDS optimization does not interact with MFMA accumulator register pressure. See `/kernel-trace-analysis` Section 5.5 for VGPR architecture details.
+
+### LDS Instruction Model
+
+LDS operations (`ds_read_*`, `ds_write_*`, `ds_bpermute_*`, `ds_swizzle_*`) are **asynchronous**:
+
+```
+ds_write_b32 v_addr, v_data    ; issues async write, returns immediately
+; ... other instructions ...    ; LDS write completes in background
+s_waitcnt lgkmcnt(0)            ; stall until all LDS/SMEM ops complete
+ds_read_b32 v_result, v_addr   ; now safe to read
+```
+
+Key rules:
+1. **Write-before-read requires sync**: any `ds_read` that depends on a prior `ds_write` must have `s_waitcnt lgkmcnt(0)` or `s_barrier` in between
+2. **`s_barrier` implies cross-wave sync**: if wave A writes and wave B reads, `s_barrier` is required (not just `lgkmcnt`)
+3. **Longer write-read distance = better latency hiding**: more instructions between `ds_write` and the subsequent `s_waitcnt lgkmcnt(0)` allow the write to complete in the background
+
+## Diagnosing LDS Bottlenecks from Trace
+
+### Step 1: Identify LDS-heavy regions
+
+```python
+import json
+
+with open('ui_output_agent_XXX_dispatch_YYY/code.json') as f:
+    data = json.load(f)
+instructions = data['code']
+# Columns: [ISA, _, LineNum, Source, Codeobj, Vaddr, Hit, Latency, Stall, Idle]
+
+# Find all LDS-related instructions
+lds_insts = [i for i in instructions if i[0].startswith('ds_') or
+             ('lgkmcnt' in i[0] and i[8] > 0)]
+
+total_lds_stall = sum(i[8] for i in lds_insts)
+total_stall = sum(i[8] for i in instructions)
+print(f"LDS stall: {total_lds_stall} / {total_stall} = {100*total_lds_stall/total_stall:.1f}%")
+
+# Show hottest LDS instructions
+for i in sorted(lds_insts, key=lambda x: x[8], reverse=True)[:15]:
+    print(f"  L{i[2]:>4d}  stall={i[8]:>6d}  idle={i[9]:>6d}  {i[0][:55]}  | :{i[3].split(':')[-1]}")
+```
+
+### Step 2: Classify the bottleneck type
+
+**Type A: Bank Conflicts** (high stall on `ds_read`/`ds_write` themselves)
+
+```
+L 766  stall=  160  ds_read2_b64 v[44:47], v28 offset1:8        ; <-- bank conflict
+L 767  stall=  320  ds_read2_b64 v[36:39], v28 offset0:16 offset1:24  ; <-- bank conflict
+```
+
+Signs:
+- `ds_read_*` / `ds_write_*` instructions with stall > 100 cycles per hit
+- Multiple reads/writes with similar base address but different offsets that map to same banks
+- `ds_read2_b64` / `ds_write2_b32` with offsets that are multiples of 32 (= same bank)
+
+**Type B: Write-Read Latency Exposed** (high stall on `s_waitcnt lgkmcnt(0)` after `ds_write`)
+
+```
+L 761  stall=  960  ds_write2_b32 v28, v41, v43 offset0:32 offset1:48
+L 764  stall= 4560  s_waitcnt lgkmcnt(0)    ; <-- write latency fully exposed
+L 765  stall= 1468  s_barrier
+L 766  stall=  160  ds_read2_b64 v[44:47], v28 offset1:8
+```
+
+Signs:
+- `s_waitcnt lgkmcnt(0)` with > 2000 stall cycles immediately after `ds_write`
+- Very few instructions between `ds_write` and `s_waitcnt`
+- This means the write hasn't completed by the time we need to wait
+
+**Type C: Cross-Wave Reduce Serialization** (high stall on `s_barrier` in reduce chains)
+
+```
+L 605  stall= 4080  s_waitcnt lgkmcnt(0)     ; wait for ds_bpermute
+L 606  stall=17024  s_barrier                 ; cross-wave sync
+L 607  stall=27220  s_waitcnt vmcnt(0)        ; also waiting for global loads
+```
+
+Signs:
+- `ds_bpermute` -> `lgkmcnt(0)` -> `s_barrier` -> `ds_write LDS` -> `lgkmcnt(0)` -> `s_barrier` -> `ds_read LDS` pattern
+- Multiple barriers (> 4) in a reduce region
+
+## Optimization Method 1: Swizzle Layout
+
+### The Problem
+
+When multiple threads access LDS with a stride that is a multiple of 32 banks (128 bytes), every access hits the same bank:
+
+```
+Thread 0: addr = base + 0*128  -> bank 0
+Thread 1: addr = base + 1*128  -> bank 0  <- CONFLICT with thread 0
+Thread 2: addr = base + 2*128  -> bank 0  <- CONFLICT
+...
+```
+
+### The Solution: XOR-Based Swizzle
+
+Swizzle XORs bits of the row index into the column index of the LDS address, distributing accesses across different banks:
+
+```
+swizzled_col = original_col XOR (row >> shift)
+```
+
+This ensures threads accessing the same column in different rows hit different banks.
+
+### FlyDSL XOR Swizzle with SmemAllocator
+
+In FlyDSL, LDS is managed through `SmemAllocator`. To apply swizzle, XOR the
+row index into the LDS address when computing store/load offsets:
+
+```python
+from flydsl.utils.smem_allocator import SmemAllocator
+from flydsl.expr import arith
+
+allocator = SmemAllocator(None, arch="gfx942", global_sym_name="smem0")
+lds_key = allocator.allocate_array(T.f16, KV_BLOCK_SIZE * HEAD_SIZE)
+
+@flyc.kernel
+def my_kernel(...):
+    lds_base = allocator.get_base()
+    lds_key_ptr = lds_key(lds_base)
+
+    # XOR-swizzle address: distribute bank accesses
+    # row_idx and col_idx are the logical 2D coordinates
+    # XOR_BITS controls swizzle width (typically 4 for fp16 vec=8)
+    swizzled_col = arith.xori(col_idx, arith.andi(row_idx, XOR_MASK))
+    lds_offset = row_idx * PADDED_STRIDE + swizzled_col
+    lds_key_ptr.store(data, [lds_offset])
+```
+
+### Choosing Swizzle Parameters
+
+The goal is to make vectorized access span enough banks:
+
+| Data Type | Element Size | Recommended Vec Width | Banks Covered per Vec |
+|-----------|-------------|----------------------|----------------------|
+| fp32      | 4 bytes     | 4                    | 4 banks (16 bytes)   |
+| fp16/bf16 | 2 bytes     | 8                    | 4 banks (16 bytes)   |
+| fp8       | 1 byte      | 16                   | 4 banks (16 bytes)   |
+
+For XOR mask: use `32 / (vec * element_size / 4) - 1` to ensure full bank coverage.
+
+### Example: Fix Bank Conflicts in KV Cache Load to LDS
+
+Before (conflict-prone, linear layout):
+
+```python
+# Linear shared memory layout — threads in same warp hit same banks
+lds_key = allocator.allocate_array(T.f16, KV_BLOCK_SIZE * HEAD_SIZE)
+# Store key tile: all threads write to column 0,1,2... -> bank conflicts
+lds_offset = row * HEAD_SIZE + col
+lds_key_ptr.store(data, [lds_offset])
+```
+
+After (swizzled, conflict-free):
+
+```python
+# XOR-swizzle distributes accesses across banks
+XOR_BITS = 4  # for fp16 vec=8: covers 4 banks per vec
+lds_key = allocator.allocate_array(T.f16, KV_BLOCK_SIZE * HEAD_SIZE)
+swizzled_col = arith.xori(col, arith.shli(arith.andi(row, 0x7), XOR_BITS))
+lds_offset = row * HEAD_SIZE + swizzled_col
+lds_key_ptr.store(data, [lds_offset])  # now conflict-free
+```
+
+## Optimization Method 2: Padding
+
+### The Problem
+
+Same as swizzle — stride-aligned accesses cause bank conflicts. Padding adds extra unused elements to change the effective stride.
+
+### The Solution
+
+Add 1 element of padding per row to break the alignment:
+
+```python
+# Without padding: row stride = HEAD_SIZE (e.g., 128)
+# Bank stride = 128 * 2 / 4 = 64 -> 64 % 32 = 0 -> ALL rows hit same bank column
+
+# With padding: row stride = HEAD_SIZE + 1 (e.g., 129)
+# Bank stride = 129 * 2 / 4 = 64.5 -> fractional -> conflicts eliminated
+```
+
+### FlyDSL Padding Implementation
+
+```python
+PADDING = 1  # or a small number
+PADDED_HEAD_SIZE = HEAD_SIZE + PADDING
+
+# Allocate with extra column for padding
+lds_key = allocator.allocate_array(T.f16, KV_BLOCK_SIZE * PADDED_HEAD_SIZE)
+
+@flyc.kernel
+def my_kernel(...):
+    lds_base = allocator.get_base()
+    lds_key_ptr = lds_key(lds_base)
+
+    # Write key data using padded stride (ignore padding column)
+    lds_offset = row * PADDED_HEAD_SIZE + col
+    lds_key_ptr.store(data, [lds_offset])
+
+    # Read back using same padded stride
+    data = lds_key_ptr.load([row * PADDED_HEAD_SIZE + col])
+```
+
+### Padding Amount
+
+The minimum padding to eliminate all bank conflicts:
+
+```
+padding_elements = 32 / (element_size_bytes)  # worst case
+```
+
+But usually 1-4 elements suffice. The cost is extra LDS usage:
+- 1 element padding per row: `KV_BLOCK_SIZE * element_size` extra bytes
+- Must ensure total LDS usage stays within 64 KB per CU
+
+### Swizzle vs Padding Trade-offs
+
+| Aspect | Swizzle | Padding |
+|--------|---------|---------|
+| LDS overhead | None (zero extra bytes) | Extra bytes per row |
+| Complexity | Need correct XOR mask params | Simple: just add 1 to stride |
+| Address computation | XOR adds ~1 SALU instruction | Simple offset, no extra compute |
+| Risk | Wrong params = silent bank conflicts | Exceeding 64KB LDS = kernel fail |
+| Preferred when | LDS near capacity, need zero overhead | Simple cases, LDS has headroom |
+
+**Recommendation**: Prefer swizzle (zero overhead). Use padding only when swizzle layout is hard to integrate with the kernel's access pattern.
+
+## Optimization Method 3: Increase Write-Read Distance
+
+### The Problem
+
+When `ds_write` is immediately followed by `s_waitcnt lgkmcnt(0)` and then `ds_read`, the ~20-40 cycle LDS write latency is fully exposed as stall:
+
+```
+ds_write_b32 ...          ; async write issued
+s_waitcnt lgkmcnt(0)      ; STALL: write hasn't completed yet (3000+ cycles)
+ds_read_b32 ...           ; read must wait for write
+```
+
+### The Solution
+
+Insert useful compute work between the write and the wait:
+
+```
+ds_write_b32 ...          ; async write issued
+; --- insert independent compute here ---
+v_mfma_f32_16x16x32 ...  ; MFMA takes ~64 cycles, overlaps with LDS write
+v_add_f32 ...             ; more independent ALU work
+v_mul_f32 ...
+; --- write has completed by now ---
+s_waitcnt lgkmcnt(0)      ; no stall (or minimal stall)
+ds_read_b32 ...           ; data ready immediately
+```
+
+### FlyDSL-Level Implementation
+
+At the Python/FlyDSL level, you control write-read distance by reordering operations:
+
+```python
+# BEFORE: write and read are close together
+lds_ptr.store(data, [offset])               # ds_write
+gpu.barrier()                                # s_barrier (includes lgkmcnt wait)
+result = lds_ptr.load([offset])             # ds_read
+
+# AFTER: insert independent work between write and barrier
+lds_ptr.store(data, [offset])               # ds_write (async)
+
+# Do independent compute that doesn't need the LDS data
+next_offsets = compute_next_offsets()        # SALU/VALU work
+next_data = buffer_ops.buffer_load(rsrc, next_offsets, vec_width=4)  # global load (also async)
+scale_factor = buffer_ops.buffer_load(rsrc_scale, scale_off, vec_width=1)
+
+gpu.barrier()                                # by now, LDS write has completed
+result = lds_ptr.load([offset])             # ds_read (no stall)
+```
+
+### What to Insert Between Write and Read
+
+Prioritize by latency-hiding value:
+
+1. **Global loads for next phase** (`buffer_ops.buffer_load`) — these are also async, ~300+ cycle latency
+2. **Address computation** (`compute_offsets`) — SALU/VALU, ~4-8 cycles each
+3. **Independent MFMA chains** — if available, ~64 cycles per MFMA
+4. **Scalar loads** (`s_load_dword*`) — kernel arguments, ~20 cycles
+
+Avoid inserting:
+- Operations that depend on the LDS write result (data dependency)
+- More LDS operations (would compete for LDS bandwidth)
+- Operations that increase register pressure beyond budget
+
+## Verification Checklist
+
+After applying LDS optimizations:
+
+1. **Correctness**: Run tests. Swizzle changes must be applied consistently to both write and read paths — if the write uses swizzled addresses, the read must use the same swizzle.
+
+2. **Re-profile**: Run `/kernel-trace-analysis` and check:
+   - `ds_read_*` / `ds_write_*` stall should decrease
+   - `s_waitcnt lgkmcnt(0)` stall after `ds_write` should decrease
+   - No new bank conflicts introduced
+
+3. **LDS usage**: Check total LDS consumption:
+   ```python
+   # Estimate: sum of all allocator.allocate_array() sizes * element_size
+   # Must be <= 65536 bytes (64 KB) per workgroup on gfx942
+   # Must be <= 163840 bytes (160 KB) per workgroup on gfx950
+   ```
+
+4. **Register pressure**: Swizzle adds ~1-2 SALU instructions for address XOR. Padding doesn't add register pressure but uses more LDS. Neither should significantly impact VGPR count.
+
+## Quick Reference: Common LDS Patterns in Paged Attention
+
+| Pattern | Location | Typical Issue | Fix |
+|---------|----------|---------------|-----|
+| K/V cache tile in LDS | QK/PV MFMA loop | Bank conflicts from stride=HEAD_SIZE | Swizzle with XOR on row index |
+| Softmax reduce via LDS | `ds_write -> barrier -> ds_read` | Write-read latency exposed + too many barriers | Increase write-read distance; replace with `ds_bpermute` chain |
+| Cross-wave max/sum broadcast | `ds_write -> barrier -> ds_read` from different wave | Cross-wave sync overhead | Merge max+sum into single reduce pass |
+| MFMA accumulator shuffle | `ds_write accum -> barrier -> ds_read permuted` | Bank conflicts if accumulator layout misaligns | Swizzle or use `ds_bpermute` for permutation |
+
+## Output
+
+After optimization, report:
+- Which LDS bottleneck type was identified (bank conflict / write-read latency / reduce serialization)
+- Which optimization was applied (swizzle / padding / distance increase)
+- Before/after `lgkmcnt` stall cycles and `ds_*` instruction stalls
+- LDS usage before/after (bytes)
+- Any impact on VGPR count or occupancy
\ No newline at end of file
diff --git a/.claude/skills/prefetch-data-load/SKILL.md b/.claude/skills/prefetch-data-load/SKILL.md
@@ -0,0 +1,376 @@
+---
+name: prefetch-data-load
+description: >
+  Apply prefetch optimization to FlyDSL kernel loops: pre-load the first
+  iteration's data before the loop, issue async loads for the next iteration
+  inside the loop body, and swap buffers at the loop tail via scf.for
+  loop-carried values. This overlaps data load latency with compute
+  instructions. Use when a kernel has a loop where buffer_load feeds into
+  MFMA/compute and load latency is exposed.
+  Usage: /prefetch-data-load
+tools: Read,Edit,Bash,Grep,Glob,Agent
+---
+
+# Prefetch Data Load Optimization
+
+Apply software prefetch (double-buffering) to overlap async data loads with
+compute in FlyDSL GPU kernel loops.
+
+## Core Principle
+
+GPU global memory loads (`buffer_ops.buffer_load`, `buffer_load_dwordx4`)
+are **asynchronous** -- the load instruction returns immediately and the
+hardware fetches data in the background. The data is only needed when a
+subsequent instruction actually **consumes** it. If we issue the load early
+enough, the data arrives by the time we need it, effectively hiding the load
+latency behind compute work.
+
+**Without prefetch** (load latency fully exposed):
+
+```
+for i in range(N):
+    data = load(ptr + i)     # <-- stall: wait for data
+    result = compute(data)   # <-- cannot start until load completes
+```
+
+Timeline:
+```
+|--load--|--stall--|--compute--|--load--|--stall--|--compute--|
+```
+
+**With prefetch** (load overlapped with compute):
+
+```
+# Pre-load first iteration BEFORE the loop
+next_data = load(ptr + 0)
+
+for i in range(N):
+    # Swap: the prefetched data becomes current
+    data = next_data
+
+    # Issue load for NEXT iteration (async, non-blocking)
+    if i + 1 < N:
+        next_data = load(ptr + i + 1)
+
+    # Compute using CURRENT data -- overlaps with next load
+    result = compute(data)
+```
+
+Timeline:
+```
+|--load₀--|--compute₀ + load₁--|--compute₁ + load₂--|--compute₂--|
+```
+
+The total time drops from `N * (load + compute)` to roughly
+`load + N * max(load, compute)`.
+
+## FlyDSL Implementation: scf.for with Loop-Carried Prefetch
+
+In FlyDSL kernels, Python-level `for _pi in range(N)` gets traced into N flat
+copies that LLVM re-rolls. This makes the `data = next_data` swap **invisible**
+to MLIR — both variables alias the same SSA value, so LLVM hoists loads as
+loop-invariant.
+
+**Solution**: Use FlyDSL's `scf.for` with `init=` (loop-carried values) to
+create genuine SSA phi nodes. See the `flydsl-kernel-authoring` skill, section
+"scf.for with Loop-Carried Values", for the full pattern and three critical
+pitfalls.
+
+### Transformation Steps
+
+Given a loop like:
+
+```python
+for i in range(START, END):
+    # === LOAD PHASE ===
+    offsets = compute_offsets(i)
+    data_A = buffer_ops.buffer_load(rsrc_A, offsets, vec_width=4)
+    data_B = buffer_ops.buffer_load(rsrc_B, offsets, vec_width=4)
+
+    # === COMPUTE PHASE ===
+    result = rocdl.mfma_f32_16x16x16_f16(transform(data_A), transform(data_B), acc)
+```
+
+Apply the following transformation using `scf.for` with `init=`:
+
+#### Step 1: Prologue — load first iteration before loop
+
+```python
+offsets_0 = compute_offsets(START)
+next_data_A = buffer_ops.buffer_load(rsrc_A, offsets_0, vec_width=4)
+next_data_B = buffer_ops.buffer_load(rsrc_B, offsets_0, vec_width=4)
+
+init_state = [_unwrap(v) for v in [next_data_A, next_data_B, acc]]
+```
+
+#### Step 2: scf.for with loop-carried state
+
+```python
+_start = arith.index(0)
+_stop = arith.index(N - 1)  # N-1 iterations; last handled in epilogue
+_step = arith.index(1)
+
+for iv, state in range(_start, _stop, _step, init=init_state):
+    # Swap: prefetched -> current
+    data_A = state[0]
+    data_B = state[1]
+    acc = state[2]
+
+    # Prefetch next iteration (async, non-blocking)
+    offsets_next = compute_offsets(iv + 1)
+    next_data_A = buffer_ops.buffer_load(rsrc_A, offsets_next, vec_width=4)
+    next_data_B = buffer_ops.buffer_load(rsrc_B, offsets_next, vec_width=4)
+
+    # Compute using current data (overlaps with next load)
+    acc = rocdl.mfma_f32_16x16x16_f16(transform(data_A), transform(data_B), acc)
+
+    results = yield [_unwrap(v) for v in [next_data_A, next_data_B, acc]]
+```
+
+#### Step 3: Epilogue — process last iteration
+
+```python
+data_A = results[0]
+data_B = results[1]
+acc = results[2]
+acc = rocdl.mfma_f32_16x16x16_f16(transform(data_A), transform(data_B), acc)
+```
+
+### Handling auxiliary data (block tables, scales)
+
+Any offset calculations, block table lookups, or scale factor loads needed
+for the *next* iteration's data should also be carried as loop state:
+
+```python
+init_state = [_unwrap(v) for v in [
+    next_data_A, next_data_B, next_block_id, next_scale, acc
+]]
+
+for iv, state in range(_start, _stop, _step, init=init_state):
+    data_A, data_B, block_id, scale, acc = state
+
+    # Prefetch next iteration
+    next_block_id = load_block_table(iv + 1)
+    offsets_next = compute_offsets(iv + 1, next_block_id)
+    next_data_A = buffer_ops.buffer_load(rsrc_A, offsets_next, vec_width=4)
+    next_data_B = buffer_ops.buffer_load(rsrc_B, offsets_next, vec_width=4)
+    next_scale = buffer_ops.buffer_load(rsrc_scale, next_block_id, vec_width=1)
+
+    # Compute with current data
+    acc = rocdl.mfma_f32_16x16x16_f16(
+        transform(data_A) * scale, transform(data_B), acc
+    )
+
+    results = yield [_unwrap(v) for v in [
+        next_data_A, next_data_B, next_block_id, next_scale, acc
+    ]]
+```
+
+### PA Decode Kernel Example (verified, 112us, 0.75x vs Gluon)
+
+State inventory (15 values carried across iterations):
+- 8 x `vector<4xi32>` — K data (4 tiles x 2 loads)
+- 1 x `i32` — partition_start
+- 2 x `i32` — block table values (phys_block/page_off or phys_0/phys_1)
+- 2 x `f32` — running_max, running_sum (online softmax)
+- 2 x `vector<4xf32>` — PV accumulators
+
+```python
+# Pack/unpack helpers
+def _pack(kv_flat, part_start, bt_vals, rmax, rsum, acc_pv):
+    raw = kv_flat + [part_start] + bt_vals + [rmax, rsum] + acc_pv
+    return [v.ir_value() if hasattr(v, 'ir_value') else v for v in raw]
+
+def _unpack(state):
+    kv_flat = list(state[0:8])
+    kv = [[kv_flat[t*2], kv_flat[t*2+1]] for t in range(4)]
+    return kv, state[8], list(state[9:11]), state[11], state[12], [state[13], state[14]]
+
+# Prologue
+pf_0 = issue_bt_k_loads(partition_0)
+init_state = _pack(flatten(pf_0['kv']), pf_0['part_start'], ...)
+
+# scf.for (bounds MUST be arith.index, not Python ints!)
+for iv, state in range(arith.index(0), arith.index(N-1), arith.index(1), init=init_state):
+    kv, part_start, bt, rmax, rsum, acc = _unpack(state)
+    rmax, rsum, acc = compute_qk_softmax_pv(kv, part_start, bt, rmax, rsum, acc)
+    pf_next = issue_bt_k_loads(next_partition(iv + 1))
+    results = yield _pack(flatten(pf_next['kv']), pf_next['part_start'], ...)
+
+# Epilogue: clear SmemPtr caches, compute last partition, write output
+smem_ptr._view_cache = None
+kv, part_start, bt, rmax, rsum, acc = _unpack(results)
+compute_qk_softmax_pv(kv, part_start, bt, rmax, rsum, acc)
+write_output(rmax, rsum, acc)
+```
+
+**ISA result**: 8 K-prefetch `buffer_load_dwordx4` appear at the END of the
+loop body (after PV MFMA), overlapping with the MFMA pipeline drain. The
+prologue has 8 K loads before the loop. The epilogue has 8 V loads only (no
+K loads needed).
+
+### Three Critical Pitfalls
+
+1. **Loop bounds must be `arith.index()`, NOT Python ints.** If you write
+   `range(0, 15, 1, init=...)`, the AST rewriter treats constant bounds as a
+   Python `range` and unrolls the loop — silently ignoring `init=`. Use
+   `arith.index(0)`, `arith.index(15)`, `arith.index(1)` instead.
+
+2. **All `init` values must be raw MLIR `ir.Value`s.** FlyDSL wrappers like
+   `Int32` / `Float32` don't have `.type` (only `.dtype`), and
+   `scf.ForOp.__init__` calls `arg.type`. Unwrap via:
+   ```python
+   def _unwrap(v):
+       return v.ir_value() if hasattr(v, 'ir_value') else v
+   init_state = [_unwrap(v) for v in raw_list]
+   ```
+
+3. **Clear `SmemPtr._view_cache` before epilogue.** `SmemPtr.get()` caches the
+   `memref.view` it creates. If called inside the `scf.for` body, the cached
+   view is defined in the loop scope. Using it in the epilogue (outside the loop)
+   causes an SSA dominance error. Fix:
+   ```python
+   my_smem_ptr._view_cache = None
+   ```
+
+## Applicable Patterns
+
+This optimization applies whenever you see this pattern in a kernel:
+
+| Signal | Description |
+|--------|-------------|
+| `for ... in range(N)` loop with `buffer_load` followed by MFMA | Load-then-compute in a loop body |
+| Block table lookup inside loop | `buffer_load(block_table_rsrc, idx)` followed by `buffer_load(cache_rsrc, page_id * stride)` |
+| KV cache iteration | Paged attention, flash attention, any tiled GEMM with paged memory |
+| Scale factor loads | FP8 per-token quantization scales loaded per KV block |
+
+## Compiler Constraints
+
+FlyDSL kernels compile to GCN ISA where `s_waitcnt` insertion is controlled by
+the **compiler**, not by the programmer. You cannot directly eliminate `s_waitcnt`
+instructions. Instead, prefetch restructures the code so the compiler places
+`s_waitcnt` after enough compute work to hide the latency.
+
+### Register Budget
+
+**Always check register headroom before adding prefetch buffers:**
+
+On CDNA3 (gfx942 MI300X/MI308), VGPRs are split into **two separate register files**:
+- **arch_vgpr** (256 per SIMD): used by VALU, VMEM loads, LDS ops, and prefetch buffers
+- **accum_vgpr / AGPR** (256 per SIMD): used exclusively by MFMA result writeback
+
+Prefetch buffers consume **arch_vgpr only** (they hold global load results). MFMA accumulators use **accum_vgpr only**. These do not compete.
+
+```python
+# Estimate arch_vgpr cost of prefetch buffers:
+#   - Each buffer_load_dwordx4 = 4 arch_vgpr per load
+#   - 8 K-cache loads = 8 x 4 = 32 arch_vgpr for one buffer set
+#   - Double-buffering = 2 x 32 = 64 arch_vgpr (but one set is reused)
+#   - Net additional arch_vgpr ~ 32 (the "next" buffer)
+#
+# On MI300X (gfx942): 256 arch_vgpr + 256 accum_vgpr per SIMD
+# Occupancy = 256 / max(arch_vgpr, accum_vgpr) waves per SIMD
+#
+# Example: arch=148, accum=148 -> occupancy bottleneck = 148 -> 1 wave
+# Adding 32 arch_vgpr -> arch=180, accum=148 -> bottleneck = 180 -> still 1 wave (safe)
+# Adding 120 arch_vgpr -> arch=268 -> SPILL (critical, exceeds 256 per SIMD)
+```
+
+**Critical thresholds (gfx942, per register file):**
+| Register File | Count | Max Waves/SIMD | Impact |
+|--------------|-------|---------------|--------|
+| arch_vgpr <= 128 | or accum <= 128 | 2 | Good occupancy |
+| arch_vgpr <= 256 | or accum <= 256 | 1 | Minimum occupancy |
+| arch_vgpr > 256 | or accum > 256 | **SPILL** | Register overflow -> severe perf regression |
+
+**How to check current VGPR allocation** (from rocprofv3 database):
+```sql
+SELECT ks.KernelName, ki.arch_vgpr_count, ki.accum_vgpr_count
+FROM rocpd_kernel_dispatch kd
+JOIN rocpd_info_kernel_symbol ks ON kd.kernel_symbol_id = ks.id
+JOIN rocpd_info_kernel ki ON kd.kernel_id = ki.id
+WHERE ks.KernelName LIKE '%target_kernel%'
+LIMIT 5;
+```
+
+**WARNING**: Do NOT use `maxnreg` to force `accum_vgpr=0` in hopes of freeing
+register space for prefetch. This forces MFMA results through arch_vgpr via
+`v_accvgpr_read` spills, causing massive slowdown (measured 4.5x GPU kernel
+regression).
+
+### What Prefetch Can and Cannot Do
+
+**CAN do:**
+- Restructure the loop so `buffer_load` is issued earlier via `scf.for` loop-carried values
+- The compiler will then schedule the corresponding `s_waitcnt` further from the load
+- Overlap next iteration's loads with current iteration's MFMA compute
+
+**CANNOT do:**
+- Directly control `s_waitcnt vmcnt(N)` counter values
+- Force the compiler to use `vmcnt(N>0)` instead of `vmcnt(0)`
+- Eliminate barriers (`s_barrier`) — these come from explicit `gpu.barrier()` or cross-wave reduce primitives
+
+### Hoisting Loads into Barrier-Wait Regions
+
+A powerful technique specific to multi-phase kernels (like paged attention with
+softmax reduce):
+
+If a kernel has a phase that spends time in `s_barrier` waits (e.g., softmax
+cross-wave reduce), and the **next** phase needs data from global memory (e.g.,
+V-value loads), hoist those loads into the barrier-stalling region. The barrier
+must wait regardless — issuing loads during that wait is essentially free.
+
+```python
+# BEFORE: V-value loads happen AFTER softmax reduce completes
+softmax_reduce(qk_scores)  # <-- 96K stall cycles in barriers
+v_data = buffer_ops.buffer_load(rsrc_v, offsets, vec_width=4)  # <-- additional load latency
+
+# AFTER: V-value loads issued BEFORE/DURING softmax reduce
+v_data_prefetch = buffer_ops.buffer_load(rsrc_v, offsets, vec_width=4)  # <-- async, non-blocking
+softmax_reduce(qk_scores)  # <-- barrier stalls now overlap with v_data fetch
+v_data = v_data_prefetch  # <-- data likely already arrived
+```
+
+This works because:
+- `buffer_load` returns immediately (async)
+- The barrier stalls are **dead time** where no useful work happens
+- By the time barriers complete (~96K cycles), the V-value load (~17K cycles)
+  has long since arrived
+
+## Rules and Pitfalls
+
+### Do
+- **Prefetch ALL data** needed for the next iteration: keys, values, scales, block table entries
+- **Place prefetch loads** immediately after the swap, BEFORE any compute that consumes current data
+- **Use scf.for with init=** to carry prefetched data across iterations (Python variable swap is invisible to MLIR)
+- **Minimize work between load and consume**: the more compute between prefetch issue and data use, the better the overlap
+- **Keep the swap simple**: just unpack from `state`, no computation
+- **Check VGPR budget**: calculate `current_arch_vgpr + prefetch_vgprs <= 256` to avoid spills
+- **Hoist cross-phase loads into barrier regions**: if a kernel has barrier-heavy phases (reduce/sync), issue the next phase's loads before/during those barriers
+- **Unwrap all init values to raw ir.Value**: use `v.ir_value() if hasattr(v, 'ir_value') else v`
+
+### Don't
+- **Don't prefetch if loop body is already memory-bound**: prefetching helps when compute (MFMA) duration >= load latency. If the loop is purely loads with no compute, prefetching won't help.
+- **Don't prefetch too many buffers**: each prefetched variable occupies registers. If register pressure is already high (causing spills), prefetching more data makes it worse. Check `waves_per_eu` / occupancy.
+- **Don't assume occupancy can increase**: on MI308 with 512 max VGPRs, adding prefetch buffers that push total VGPRs above 256 will drop occupancy from 2 to 1 wave/SIMD. This may or may not be acceptable — profile both configurations.
+- **Don't reorder loads that have data dependencies**: if `load_B` depends on the result of `load_A` (e.g., block table lookup -> cache load), they must stay sequential within the prefetch block.
+- **Don't forget to handle conditional branches**: if scale loads are conditional (`KV_QUANT_MODE`), the prefetch must replicate the same conditions.
+- **Don't break the prologue/epilogue semantics**: the prologue covers iteration 0; `scf.for` runs N-1 iterations carrying prefetched data; epilogue processes the last iteration from `results`.
+- **Don't use Python ints as scf.for bounds**: use `arith.index()` or the loop will be unrolled, silently ignoring `init=`.
+
+## Verification
+
+After applying prefetch:
+
+1. **Correctness**: Run the existing test suite. Output must match bit-for-bit (fp32 accumulation) or within tolerance (fp8/bf16).
+2. **Performance**: Profile with `rocprofv3 --kernel-trace`. Look for:
+   - Reduced `VMEM` stall cycles in the loop body
+   - Higher MFMA utilization percentage
+   - Overall kernel duration reduction
+3. **Register pressure**: Check that `waves_per_eu` (occupancy) didn't drop. If it did, consider prefetching fewer buffers (e.g., only keys, not values).
+
+## When NOT To Use
+
+- **Single-iteration loops** (`range(1)`): no next iteration to prefetch
+- **Compute-bound kernels**: if MFMA utilization is already >90%, the bottleneck is compute, not memory — prefetching won't help
+- **Very high register pressure**: if occupancy is already 1 wave/EU and the kernel spills, adding prefetch buffers will make it worse
\ No newline at end of file
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1,128 @@
+# FlyDSL Project Guide
+
+FlyDSL (Flexible Layout Python DSL) — a Python DSL and MLIR-based compiler stack for authoring high-performance GPU kernels with explicit layouts and tiling on AMD GPUs (MI300X/MI350).
+
+## Repository Layout
+
+```
+FlyDSL/
+├── python/flydsl/          # Python DSL core
+│   ├── expr/               # DSL expression API (arith, vector, gpu, rocdl, buffer_ops)
+│   ├── compiler/           # JIT compilation (ast_rewriter, kernel_function, jit_function)
+│   ├── utils/              # Utilities (smem_allocator, env, logger)
+│   └── _mlir/              # Embedded MLIR Python bindings (built, not edited)
+├── kernels/                # Production GPU kernels (importable as kernels.*)
+│   ├── pa_decode_fp8.py    # Paged attention decode (FP8)
+│   ├── preshuffle_gemm.py  # GEMM kernels
+│   ├── layernorm_kernel.py # LayerNorm
+│   ├── softmax_kernel.py   # Softmax
+│   └── layout_utils.py     # Layout coordinate helpers
+├── include/flydsl/         # C++ Fly dialect headers
+├── lib/                    # C++ dialect implementation
+├── tests/                  # All tests
+│   ├── kernels/            # Kernel correctness tests (test_pa, test_preshuffle_gemm, etc.)
+│   ├── pyir/               # IR-level tests
+│   └── unit/               # Unit tests (streams, async, etc.)
+├── examples/               # Runnable examples (vectorAdd, tiledCopy, tiledMma)
+├── scripts/                # Build & test scripts
+│   ├── build_llvm.sh       # Build LLVM/MLIR from source (~30min)
+│   ├── build.sh            # Build FlyDSL C++ + Python bindings (~5min)
+│   └── run_tests.sh        # Run all tests
+└── docs/                   # Architecture, layout system, kernel authoring guides
+```
+
+## Build & Install
+
+```bash
+# Build LLVM/MLIR (one-time, ~30min)
+bash scripts/build_llvm.sh
+
+# Build FlyDSL
+bash scripts/build.sh
+
+# Install in dev mode
+pip install -e .
+```
+
+## Running Tests
+
+```bash
+# All tests
+PYTHONPATH=./ pytest tests/
+
+# Specific kernel test
+PYTHONPATH=./ python tests/kernels/test_pa.py --num_iters 50
+
+# Disable JIT cache during development
+FLYDSL_RUNTIME_ENABLE_CACHE=0 PYTHONPATH=./ python tests/kernels/test_pa.py
+```
+
+## Code Style
+
+- **Python**: black (line-length=120), ruff for linting. Config in `pyproject.toml`.
+- **C++**: LLVM style (ColumnLimit=100). Config in `.clang-format`.
+- **Imports**: isort with `flydsl` as known first-party.
+
+## Key Concepts
+
+### DSL Expression API (`python/flydsl/expr/`)
+
+Kernels are written in Python using the FlyDSL expression API:
+- `arith` — arithmetic ops (constant, select, index_cast, trunci, extsi, etc.)
+- `vector` — vector ops (extract, insert, load_op, store, broadcast, from_elements, bitcast)
+- `gpu` — GPU indexing (thread_idx, block_idx, barrier)
+- `rocdl` — AMD-specific intrinsics (mfma, cvt_pk_fp8_f32, ds_bpermute)
+- `buffer_ops` — buffer resource ops (create_buffer_resource, buffer_load, buffer_store)
+
+### Kernel Authoring Pattern
+
+```python
+import flydsl.compiler as flyc
+import flydsl.expr as fx
+from flydsl.expr import arith, vector, gpu, rocdl, buffer_ops
+from flydsl.expr.typing import T, Int32
+
+@flyc.kernel
+def my_kernel(input_ptr: fx.Tensor, output_ptr: fx.Tensor, N: Int32):
+    tid = gpu.thread_idx.x + gpu.block_idx.x * arith.constant(256, type=T.i32)
+    rsrc_in = buffer_ops.create_buffer_resource(input_ptr, max_size=True)
+    val = buffer_ops.buffer_load(rsrc_in, tid, vec_width=1, dtype=T.f32)
+    # ... compute ...
+    rsrc_out = buffer_ops.create_buffer_resource(output_ptr, max_size=True)
+    buffer_ops.buffer_store(result, rsrc_out, tid)
+```
+
+### SmemAllocator & SmemPtr
+
+Shared memory (LDS) is managed via `SmemAllocator` and `SmemPtr`:
+```python
+from flydsl.utils.smem_allocator import SmemAllocator, SmemPtr
+
+allocator = SmemAllocator(None, arch=arch, global_sym_name="my_smem")
+allocator.ptr = size_in_bytes
+base = allocator.get_base()
+lds_view = SmemPtr(base, offset, T.f32, shape=(N,)).get()  # returns memref for loads/stores
+```
+
+### scf.for Loops with Loop-Carried Values
+
+FlyDSL supports `scf.for` loops via Python `range()` with `init=` keyword:
+```python
+loop_start = arith.index(0)
+loop_stop = arith.index(N)
+loop_step = arith.index(1)
+for iv, state in range(loop_start, loop_stop, loop_step, init=[init_val1, init_val2]):
+    # Use state[0], state[1] ...
+    # Yield updated values:
+    results = yield [new_val1, new_val2]
+# After loop: results contains final values
+```
+
+Important: clear `SmemPtr._view_cache = None` after exiting scf.for to avoid MLIR dominance errors in epilogue code.
+
+## Development Notes
+
+- Always set `FLYDSL_RUNTIME_ENABLE_CACHE=0` when iterating on kernel code to bypass JIT cache
+- `PYTHONPATH=./` is required when running from the repo root
+- Kernel files in `kernels/` are importable as `from kernels.pa_decode_fp8 import ...`
+- The `_mlir` package is auto-generated during build — never edit it directly
PATCH

echo "Gold patch applied."
