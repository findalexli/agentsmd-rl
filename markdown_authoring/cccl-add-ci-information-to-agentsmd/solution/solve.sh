#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cccl

# Idempotency guard
if grep -qF "* To reduce overhead, you can add an override matrix in `workflows.override`. Th" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -249,6 +249,68 @@ Test organization:
 
 ---
 
+## Continuous Integration (CI)
+
+See `ci-overview.md` for detailed examples and troubleshooting guidance.
+
+CCCL's CI is built on GitHub Actions and relies on a dynamically generated job matrix plus several helper scripts.
+
+### Key Components
+
+* **`ci/matrix.yaml`**
+
+  * Declares build and test jobs for `pull_request`, `nightly`, and `weekly` workflows.
+  * Pull request (PR) runs typically spawn ~250 jobs.
+  * To reduce overhead, you can add an override matrix in `workflows.override`. This limits the PR CI run to a targeted subset of jobs. Overrides are recommended when:
+    * Changes touch high-dependency areas (e.g. top-level CI/devcontainers, libcudacxx, thrust, CUB). See `ci/inspect_changes.sh` for dependency information.
+    * A smaller subset of jobs is enough to validate the change (e.g. infra changes, targeted fixes).
+  * Important rules:
+    * PR merges are blocked while an override matrix is active.
+    * The override must be reset to empty (not removed) before merging.
+    * Only add overrides when starting a new draft that qualifies; never remove one without being asked.
+
+* **`.github/actions/workflow-build/`**
+
+  * Runs `build-workflow.py`.
+  * Reads `ci/matrix.yaml` and prunes jobs using `ci/inspect_changes.sh`.
+  * Calls `prepare-workflow-dispatch.py` to produce a formatted job matrix for dispatch.
+
+* **`.github/actions/workflow-run-job-{linux,windows}/`**
+
+  * Runs a single matrix job inside a devcontainer.
+
+* **`.github/actions/workflow-results/`**
+
+  * Aggregates artifacts and results.
+  * Marks workflow as failed if any job fails or an override matrix is present.
+
+* **`.github/workflows/ci-workflow-{pull-request,nightly,weekly}.yml`**
+
+  * Top-level GitHub Actions workflows invoking CI.
+
+* **`ci/inspect_changes.sh`**
+
+  * Detects which subprojects changed between commits.
+  * Defines internal dependencies between CCCL projects. If a project is marked dirty, all dependent projects are also marked dirty and tested.
+  * Allows `build-workflow.py` to skip unaffected jobs.
+
+---
+
+### Commit Message Controls
+
+Tags appended to the commit summary (case-sensitive) control CI behavior:
+
+* `[skip-matrix]`: Skip CCCL project build/test jobs. (Docs, devcontainers, and third-party builds still run.)
+* `[skip-vdc]`: Skip "Verify Devcontainer" jobs. Safe unless CI or devcontainer infra is modified.
+* `[skip-docs]`: Skip doc tests/previews. Safe if docs are unaffected.
+* `[skip-matx]`: Skip building the MatX third-party smoke test.
+
+> ⚠️ All of these tags block merging until removed and a full CI run (with no overrides) succeeds.
+
+Use these tags for early iterations to save resources. Remove them before review/merge.
+
+---
+
 ## Code Formatting and Linting
 
 > ⚠️ Always run before committing. CI will fail otherwise.
@@ -264,15 +326,16 @@ pre-commit run --files <file1> <file2>
 
 ## General Guidelines
 
-* Always validate changes with builds and tests
-* Always run `pre-commit` before committing
-* Review `CONTRIBUTING.md` before submitting PRs
+* Validate changes with builds/tests; report results.
+* Run `pre-commit` before committing.
+* Review `CONTRIBUTING.md` and `ci-overview.md` before starting work.
+
+### Performance Tips
 
-Performance tips:
+* Use development containers with `sccache` (CCCL team only).
+* Limit architectures to reduce compile time (e.g. `-arch "native"` or `"80"` if no GPU).
+* Build with Ninja for fast, parallel builds.
 
-* Use development containers with `sccache` (internal users)
-* Limit architectures to target hardware (e.g. `-arch "native"`)
-* Build with Ninja parallelization (`--parallel <N>`)
 
 ---
 
PATCH

echo "Gold patch applied."
