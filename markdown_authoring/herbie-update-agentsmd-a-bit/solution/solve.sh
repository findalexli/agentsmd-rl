#!/usr/bin/env bash
set -euo pipefail

cd /workspace/herbie

# Idempotency guard
if grep -qF "- You can enable the `egglog` backend with `--enable generate:egglog`." "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,21 +1,30 @@
 
-# Testing
+# Formatting
 
 - Run `make fmt` to format the code before finishing a task. This is
   mandatory and PRs that don't follow the coding style are rejected.
 - Always check your `git diff` before finishing a task. There's often
   leftover or dead code, and you should delete it.
+- Documentation lives in `www/doc/2.3/` and is HTML-formatted. Update
+  it if you change any user-visible options.
+
+# Testing
+
 - Run `racket src/main.rkt report bench/tutorial.fpcore tmp` to test
   that your changes work; this should take about 5-10 seconds and all
   of the tests should pass, getting basically perfect accuracy.
 - After running tests, you should be able to look into `tmp`, and see
   one directory per benchmark. Each directory has a `graph.html` with
   more detail on what happened, including tracebacks for crashes.
-- Herbie prints a seed every time it runs; you can pass --seed N after
-  the "report" argument to fix a seed. That should be perfectly
-  reproducible.
 - You can also run the unit tests with `raco test <file>`, when unit
   tests exist. Often they don't.
+- Arguments come after the word `report` before any other arguments.
+- Herbie prints a seed every time it runs; you can pass `--seed N`
+  after the "report" argument to fix the seed reproducibly.
+- You can pass `--timeout T` to time out a benchmark after T seconds.
+- You can enable the `egglog` backend with `--enable generate:egglog`.
+  Otherwise the `egg` backend is used. You'll need to add
+  `~/.cargo/bin` to the `PATH`.
 
 # Profiling
 
@@ -25,7 +34,9 @@
   `dump-trace.json` in chrome://tracing format
 - Additionally `--enable dump:rival` outputs all Rival commands it
   executes, which can be useful for debugging Rival &
-  arbitrary-precision code.
+  arbitrary-precision code, and `--enable dump:egglog` outputs all
+  egglog commands. Dumps go in `dump-XXX` in the current directory,
+  and that folder grows with every run.
   
 # Timeline
 
@@ -40,14 +51,3 @@
   `val`s must be JSON-compatible; this mostly means you have to
   convert symbols to strings.
 
-# Documentation
-
-- Documentation lives in `www/doc/2.3/` and is HTML-formatted. Update
-  it if you change any user-visible options.
-
-# PRs
-
-- PR descriptions should be 1-3 paragraphs in length. Describe the
-  current behavior and why you changed it. Avoid bullet points.
-- Be explicit about the expected impact: "should be faster", "should
-  be more accurate", "pure refactor, no changes", and so on.
PATCH

echo "Gold patch applied."
