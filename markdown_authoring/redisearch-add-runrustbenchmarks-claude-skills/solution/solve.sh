#!/usr/bin/env bash
set -euo pipefail

cd /workspace/redisearch

# Idempotency guard
if grep -qF "- `<crate> <bench>`: Run specific bench in a benchmakr crate (e.g., `/run-rust-b" ".skills/run-rust-benchmarks/SKILL.md" && grep -qF "- `<crate> <test>`: Run specific test in crate (e.g., `/run-rust-tests hyperlogl" ".skills/run-rust-tests/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.skills/run-rust-benchmarks/SKILL.md b/.skills/run-rust-benchmarks/SKILL.md
@@ -0,0 +1,38 @@
+---
+name: run-rust-benchmarks
+description: Run Rust benchmarks and compare performance with the C implementation
+---
+
+# Rust Benchmarks Skill
+
+Run Rust benchmarks and compare performance with the C implementation.
+
+## Arguments
+- `<crate>`: Run the given benchmark crate (e.g., `/run-rust-benchmarks rqe_iterators_bencher`)
+- `<crate> <bench>`: Run specific bench in a benchmakr crate (e.g., `/run-rust-benchmarks rqe_iterators_bencher "Iterator - InvertedIndex - Numeric - Read Dense"`)
+
+Arguments provided: `$ARGUMENTS`
+
+## Instructions
+
+1. Check the arguments provided above:
+   - If a crate name is provided, run benchmarks for that crate:
+     ```bash
+     cd src/redisearch_rs && cargo bench -p <crate_name>
+     ```
+   - If both crate and bench name are provided, run the specific bench:
+     ```bash
+     cd src/redisearch_rs && cargo bench -p <crate_name> <bench_name>
+     ```
+2. Once the benchmarks are complete, generate a summary comparing the average run times between the Rust and C implementations.
+
+## Common Benchmark Commands
+
+```bash
+# Bench given crate
+cd src/redisearch_rs && cargo bench -p rqe_iterators_bencher
+cd src/redisearch_rs && cargo bench -p inverted_index_bencher
+
+# Run a specific benchmark
+cd src/redisearch_rs && cargo bench -p rqe_iterators_bencher "Iterator - InvertedIndex - Numeric - Read Dense"
+```
diff --git a/.skills/run-rust-tests/SKILL.md b/.skills/run-rust-tests/SKILL.md
@@ -10,8 +10,8 @@ Run Rust tests after making changes to verify correctness.
 ## Arguments
 - No arguments: Analyze changes and run tests for affected crates only
 - `all`: Run all Rust tests
-- `<crate>`: Run tests for specific crate (e.g., `/rust-test hyperloglog`)
-- `<crate> <test>`: Run specific test in crate (e.g., `/rust-test hyperloglog test_merge`)
+- `<crate>`: Run tests for specific crate (e.g., `/run-rust-tests hyperloglog`)
+- `<crate> <test>`: Run specific test in crate (e.g., `/run-rust-tests hyperloglog test_merge`)
 
 Arguments provided: `$ARGUMENTS`
 
PATCH

echo "Gold patch applied."
