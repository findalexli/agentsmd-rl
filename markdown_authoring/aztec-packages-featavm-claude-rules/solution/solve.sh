#!/usr/bin/env bash
set -euo pipefail

cd /workspace/aztec-packages

# Idempotency guard
if grep -qF "- **vm2/** - AVM implementation (not enabled, but might need to be fixed for com" "barretenberg/cpp/CLAUDE.md" && grep -qF "The **Aztec Virtual Machine (AVM)** executes public transactions and proves corr" "barretenberg/cpp/pil/vm2/CLAUDE.md" && grep -qF "**Scope:** Use this guide when working in `barretenberg/cpp/src/barretenberg/vm2" "barretenberg/cpp/src/barretenberg/vm2/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/barretenberg/cpp/CLAUDE.md b/barretenberg/cpp/CLAUDE.md
@@ -54,9 +54,9 @@ Bootstrap modes:
 - **stdlib/** - Circuit-friendly implementations of primitives
 - **ultra_honk/** - Ultra Honk prover/verifier
 - **chonk/** - Client-side IVC (Incremental Verifiable Computation)
-- **vm2/** - AVM implementation (not enabled, but might need to be fixed for compilation issues in root ./bootstrap.sh)
 - **bbapi/** - BB API for external interaction. If changing here, we will also want to update the ts/ folder because bb.js consumes this. (first build ninja bb in build/)
 - **dsl/** - ACIR definition in C++. This is dictated by the serialization in noir/, so refactor should generally not change the structure without confirming that the user is changing noir.
+- **vm2/** - AVM implementation (not enabled, but might need to be fixed for compilation issues in root ./bootstrap.sh). If working in vm2, use barretenberg/cpp/src/barretenberg/vm2/CLAUDE.md
 
 ### ts/ => typescript code for bb.js
 
diff --git a/barretenberg/cpp/pil/vm2/CLAUDE.md b/barretenberg/cpp/pil/vm2/CLAUDE.md
@@ -0,0 +1,28 @@
+# AVM relations and PIL development guide
+
+**Scope:** Use this guide when editing PIL relation files in `barretenberg/cpp/pil/vm2`. After changing PIL you must regenerate C++ and recompile; the C++ side is in `barretenberg/cpp/src/barretenberg/vm2`. See that directory’s CLAUDE.md for build and test.
+
+## Related rules
+
+- **barretenberg/cpp/src/barretenberg/vm2/CLAUDE.md** — AVM C++ simulator, tracegen, prover; build targets and tests.
+- **barretenberg/cpp/CLAUDE.md** — Barretenberg root; bootstrap and general cpp workflow.
+
+---
+
+## Overview
+
+The **Aztec Virtual Machine (AVM)** executes public transactions and proves correct execution. The **PIL files** in this directory define **relations**: constraints on a trace (matrix of columns and rows) that characterize valid execution. PIL is Polygon’s Polynomial Identity Language.
+
+PIL is the source of truth for relation constraints; it is compiled into C++ used by the AVM prover in `barretenberg/cpp/src/barretenberg/vm2`.
+
+## Workflow: changing PIL
+
+**IMPORTANT:** Any change to PIL files requires regenerating C++ and recompiling the AVM.
+
+1. **Ensure `bb-pilcom` is built** (once per checkout / when pilcom changes). From repo root: run `./bootstrap.sh` in `bb-pilcom/` (e.g. `bb-pilcom/bootstrap.sh`). Changes to PIL do not require rebuilding pilcom.
+2. **Regenerate C++:** From `barretenberg/cpp/`, run:
+   ```bash
+   ./scripts/avm2_gen.sh
+   ```
+   Check the output for errors. On success, generated files under `barretenberg/cpp/src/barretenberg/vm2/generated/` are updated.
+3. **Recompile AVM:** Follow build and test instructions in `barretenberg/cpp/src/barretenberg/vm2/CLAUDE.md` (e.g. build `bb-avm` or `vm2_tests`).
diff --git a/barretenberg/cpp/src/barretenberg/vm2/CLAUDE.md b/barretenberg/cpp/src/barretenberg/vm2/CLAUDE.md
@@ -0,0 +1,73 @@
+# AVM development guide (C++)
+
+**Scope:** Use this guide when working in `barretenberg/cpp/src/barretenberg/vm2` — the AVM C++ simulator, trace generation, and prover. For barretenberg-wide build and workflow, see `barretenberg/cpp/CLAUDE.md`. For PIL relation sources and codegen, see `barretenberg/cpp/pil/vm2/CLAUDE.md`.
+
+## Related rules
+
+- **barretenberg/cpp/CLAUDE.md** — Barretenberg root: build presets, bootstrap, other cpp targets, VKs, benchmarking.
+- **barretenberg/cpp/pil/vm2/CLAUDE.md** — PIL relations in `barretenberg/cpp/pil/vm2`; regenerating C++ from `.pil` files.
+- **yarn-project/CLAUDE.md** — TypeScript monorepo; running AVM-related TS tests (bb-prover, simulator).
+
+---
+
+## Overview
+
+The **Aztec Virtual Machine (AVM)** executes public transactions and proves that execution was correct. This directory contains:
+
+- **Simulation** — Runs a transaction. Two modes:
+  - **Fast mode:** Minimal output; used by block building.
+  - **Witness generation:** Produces execution events for tracegen and proving.
+- **Trace generation (tracegen)** — Turns execution events into a trace (matrix of rows/columns) encoding execution and memory.
+- **Constraining (proving)** — Uses Barretenberg to produce a ZK proof that the trace satisfies the AVM relations.
+
+## Directory layout
+
+```
+barretenberg/cpp/src/barretenberg/vm2/
+├── simulation/
+│   ├── lib/                # Shared simulation; no events.
+│   ├── standalone/         # Fast mode only; no events.
+│   └── gadgets/            # Witness-generation; emits events.
+├── tracegen/               # Trace generation from events.
+├── constraining/           # Prover and verifier.
+├── common/                 # Shared config and utilities.
+├── dsl/                    # Noir interface to AVM recursive verifier.
+├── generated/              # Generated from PIL in barretenberg/cpp/pil/vm2 (see barretenberg/cpp/pil/vm2/CLAUDE.md).
+├── integration_tests/      # Simulation + tracegen + proving tests.
+├── optimized/              # Hand-tuned relation implementations.
+├── testing/                # Shared test fixtures and helpers.
+├── tooling/                # AVM CLI debugger and stats.
+├── simulation_helper.*pp   # External simulation API.
+├── tracegen_helper.*pp     # External tracegen API.
+└── proving_helper.*pp      # External proving API.
+```
+
+## Git workflow
+
+**IMPORTANT:** For AVM work, use base branch `merge-train/avm`, not `master`.
+
+- `git diff merge-train/avm...HEAD`
+- `git log merge-train/avm..HEAD`
+
+## Build and test
+
+Configure once: `cmake --preset clang20-assert`. All commands below are from `barretenberg/cpp/`.
+
+1. **`bb-avm`** — CLI to simulate and prove.
+   - Build: `cmake --build --preset clang20-assert --target bb-avm` (slow, ~4 min). Prefer the linter for quick iteration.
+   - Binary: `barretenberg/cpp/build/bin/bb-avm`.
+2. **`vm2_tests`** — AVM unit tests.
+   - Build: `cmake --build --preset clang20-assert --target vm2_tests`. Run from `barretenberg/cpp/build`: `./bin/vm2_tests --gtest_filter="*test_name*"`.
+3. **`nodejs_module`** — Fast simulation only; builds quickly.
+   - Build: `cmake --build --preset clang20-assert --target nodejs_module`. For TS: from `barretenberg/cpp/`, run `(cd ../../barretenberg/ts/; ./scripts/copy_native.sh)` then bootstrap `yarn-project` (see yarn-project/CLAUDE.md).
+
+## AVM and TypeScript
+
+Most end-to-end AVM behavior is tested from TypeScript. Ensure `yarn-project` is bootstrapped (see yarn-project/CLAUDE.md); rebuild only if the repo or TS files changed.
+
+- **`bb-avm` (bulk test):** From `yarn-project/bb-prover`:
+  `LOG_LEVEL=verbose yarn test src/avm_proving_tests/avm_bulk.test.ts`.
+  The run prints a line like:
+  `…/barretenberg/cpp/build/bin/bb-avm avm_prove --avm-inputs /tmp/…/avm_inputs.bin -o /tmp/bb-… -v`.
+  For C++-only iteration you can re-run that `bb-avm` command directly.
+- **Fast simulation:** From `yarn-project/simulator`: `yarn test src/public`.
PATCH

echo "Gold patch applied."
