#!/usr/bin/env bash
set -euo pipefail

cd /workspace/rsyslog

# Idempotency guard
if grep -qF "- `parser.c`, `prop.c`, `template.c`: core message parsing and property engine." "runtime/AGENTS.md" && grep -qF "- Base new shell tests on existing ones; include `. $srcdir/diag.sh` to gain the" "tests/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/runtime/AGENTS.md b/runtime/AGENTS.md
@@ -0,0 +1,64 @@
+# AGENTS.md – Runtime subtree
+
+These instructions apply to all files under `runtime/`, which implement the
+rsyslog core (message queues, networking backends, parsers, scheduler, stats
+collection, and process orchestration).
+
+## Purpose & scope
+- Treat this tree as the authoritative implementation of the rsyslog engine.
+  Changes here affect every module and deployment profile.
+- Consult the top-level `AGENTS.md` and component-specific guides (e.g.
+  `plugins/AGENTS.md`) when a change crosses directory boundaries.
+
+## Key components
+- `rsyslog.c` / `rsyslog.h`: main entry point and daemon lifecycle helpers.
+- `modules.c`, `module-template.h`: module loader contracts shared with
+  `plugins/` and `contrib/`.
+- `queue.c`, `wti.c`, `wtp.c`: work queue implementation and worker threads.
+- `tcpsrv.c`, `tcpclt.c`, `net*.c`: TCP/TLS listeners and clients.
+- `parser.c`, `prop.c`, `template.c`: core message parsing and property engine.
+- `statsobj.c`, `dynstats*.c`: statistics registry and dynamic counters.
+- `timezones.c`, `datetime.c`: time conversion helpers.
+
+## Build & validation
+- Bootstrap with `./autogen.sh` only when build scripts change (see root
+  instructions) and configure with `./configure --enable-testbench` so runtime
+  helpers used by the testbench stay available. Run these commands from the
+  repository root, not from within `runtime/`.
+- Build the core with `make -j$(nproc)`; this compiles the runtime and shared
+  libraries that tests dynamically load via `-M../runtime/.libs:../.libs`.
+- Prefer targeted test runs over a full `make check`:
+  - Directly invoke the most relevant shell test under `tests/` (e.g.
+    `./tests/queue-persist.sh`).
+  - Use `make check TESTS='<script>.sh'` when you need automake’s harness or
+    Valgrind variants (`*-vg.sh`).
+  - For configuration validation edits, run `./tests/validation-run.sh`.
+- When changing exported symbols, update `runtime/Makefile.am` and ensure the
+  library version script (if touched) remains consistent with existing
+  SONAME policies.
+
+## Coding expectations
+- Follow `COMMENTING_STYLE.md` and add/update "Concurrency & Locking" blocks in
+  files that manage shared state (queues, network sessions, statistics).
+- Keep worker/thread behavior aligned with `MODULE_AUTHOR_CHECKLIST.md` rules:
+  per-worker state stays in `wrkrInstanceData_t`, shared state is guarded in
+  per-action data structures.
+- Update `doc/ai/module_map.yaml` when locking guarantees, queue semantics, or
+  exported helper APIs change so module authors know what to depend on.
+- Update or create unit helpers (e.g. under `tests/` or `runtime/hashtable/`)
+  when you modify reusable primitives.
+
+## Coordination & documentation
+- Notify module owners (via metadata or review notes) when adjusting
+  `module-template.h`, initialization flows, or statistics surfaces consumed by
+  plugins.
+- Cross-reference user docs in `doc/` if behavior visible to operators changes
+  (configuration syntax, stats counters, TLS requirements, etc.).
+- Leave `ChangeLog` and `NEWS` edits to the maintainers; do not modify those
+  files in routine patches.
+
+## Debugging tips
+- Enable extra runtime logging with `export RSYSLOG_DEBUG="..."` in tests (see
+  `tests/diag.sh`) when chasing race conditions.
+- Use the testbench Valgrind helpers by running the corresponding `*-vg.sh`
+  scripts to flush out memory and threading regressions.
diff --git a/tests/AGENTS.md b/tests/AGENTS.md
@@ -0,0 +1,54 @@
+# AGENTS.md – Testbench subtree
+
+This guide covers everything under `tests/`, including shell test cases,
+helpers, suppressions, and supporting binaries.
+
+## Purpose & scope
+- The directory implements the Automake testbench that exercises rsyslog.
+- Each `.sh` script is a standalone scenario that can be executed directly or
+  through `make check`.
+- Use this guide together with the top-level `AGENTS.md` and the component
+  guide that matches the module you are testing.
+
+## Writing & updating tests
+- Base new shell tests on existing ones; include `. $srcdir/diag.sh` to gain the
+  helper functions (timeouts, Valgrind integration, rsyslogd launch helpers).
+- Name Valgrind-enabled wrappers with the `-vg.sh` suffix and toggle Valgrind by
+  exporting `USE_VALGRIND` before sourcing the non-`vg` script.
+- Put auxiliary binaries next to their scripts (e.g. `*.c` programs compiled via
+  the Automake harness) and list them in `tests/Makefile.am`.
+- Keep long-lived configuration snippets in `tests/testsuites/` and reuse them
+  instead of copying large config blocks into multiple scripts.
+- Document new environment flags or helper functions inside `diag.sh` so other
+  tests can discover them.
+
+## Running tests locally
+- Build rsyslog first (`./autogen.sh`, `./configure --enable-testbench`,
+  `make -j$(nproc)`) so the testbench can load freshly built binaries and
+  modules.
+- Execute individual scenarios directly for quick feedback
+  (`./tests/imfile-basic.sh`).
+- Use `make check TESTS='script.sh'` when you need Automake logging,
+  parallelisation control, or to exercise the Valgrind wrappers.
+- Remove stale `.log`/`.trs` files before re-running a flaky test to avoid
+  Automake caching previous outcomes.
+- For configuration validation changes, run `./tests/validation-run.sh` to
+  confirm both failure and success paths.
+
+## Debugging & environment control
+- `tests/diag.sh` documents environment variables such as `SUDO`,
+  `USE_VALGRIND`, `RSYSLOG_DEBUG`, and timeout overrides; prefer these knobs over
+  ad-hoc `sleep` loops.
+- Use `USE_GDB=1 make <test>.log` to pause execution and attach a debugger as
+  described in `tests/README`.
+- Keep suppression files (e.g. `*.supp`) current when adding new Valgrind noise;
+  failing to do so will cause CI false positives.
+
+## Coordination
+- When adding tests for a plugin or runtime subsystem, mention them in the
+  component’s `AGENTS.md` so future authors know smoke coverage exists.
+- Update `KNOWN_ISSUES` or module metadata if a test encodes a known bug or a
+  skipped scenario.
+- If a change requires additional docker services or fixtures, document setup
+  steps in `tests/CI/README` (or create it) and link from the relevant module
+  guide.
PATCH

echo "Gold patch applied."
