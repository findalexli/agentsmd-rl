#!/usr/bin/env bash
set -euo pipefail

cd /workspace/hugo

if grep -q 'panicOnWarning  bool' commands/commandeer.go 2>/dev/null; then
    echo "Patch already applied; nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
index 8cdf9fdb1b6..22febd9db3c 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -7,6 +7,7 @@
 * Never export symbols that's not needed outside of the package.
 * Avoid global state at (almost) all cost.
 * This is a project with a long history; assume that a similiar problem has been solved before, look hard for helper functions before creating new ones.
+* In tests, use `qt` matchers (e.g. `b.Assert(err, qt.ErrorMatches, ...)`) instead of raw `if`/`t.Fatal` checks.
 * Use `./check.sh ./somepackage/...` when iterating.
 * Use `./check.sh` when you're done.

diff --git a/commands/commandeer.go b/commands/commandeer.go
index f233ce2c3a7..dc7bd7f3394 100644
--- a/commands/commandeer.go
+++ b/commands/commandeer.go
@@ -131,6 +131,7 @@ type rootCommand struct {
 	gc              bool
 	poll            string
 	forceSyncStatic bool
+	panicOnWarning  bool

 	// Profile flags (for debugging of performance problems)
 	cpuprofile   string
@@ -488,12 +489,18 @@ func (r *rootCommand) createLogger(running bool) (loggers.Logger, error) {
 		}
 	}

+	var logHookLast func(e *logg.Entry) error
+	if r.panicOnWarning {
+		logHookLast = loggers.PanicOnWarningHook
+	}
+
 	optsLogger := loggers.Options{
 		DistinctLevel: logg.LevelWarn,
 		Level:         level,
 		StdOut:        r.StdOut,
 		StdErr:        r.StdErr,
 		StoreErrors:   running,
+		HandlerPost:   logHookLast,
 	}

 	return loggers.New(optsLogger), nil
@@ -591,7 +598,7 @@ func applyLocalFlagsBuild(cmd *cobra.Command, r *rootCommand) {
 	cmd.Flags().BoolVar(&r.gc, "gc", false, "enable to run some cleanup tasks (remove unused cache files) after the build")
 	cmd.Flags().StringVar(&r.poll, "poll", "", "set this to a poll interval, e.g --poll 700ms, to use a poll based approach to watch for file system changes")
 	_ = cmd.RegisterFlagCompletionFunc("poll", cobra.NoFileCompletions)
-	cmd.Flags().Bool("panicOnWarning", false, "panic on first WARNING log")
+	cmd.Flags().BoolVar(&r.panicOnWarning, "panicOnWarning", false, "panic on first WARNING log")
 	cmd.Flags().Bool("templateMetrics", false, "display metrics about template executions")
 	cmd.Flags().Bool("templateMetricsHints", false, "calculate some improvement hints when combined with --templateMetrics")
 	cmd.Flags().BoolVar(&r.forceSyncStatic, "forceSyncStatic", false, "copy all files when static is changed.")
diff --git a/hugolib/integrationtest_builder.go b/hugolib/integrationtest_builder.go
index ebc458e079f..4628d5f6f32 100644
--- a/hugolib/integrationtest_builder.go
+++ b/hugolib/integrationtest_builder.go
@@ -879,12 +879,18 @@ func (s *IntegrationTestBuilder) initBuilder() error {
 			w = &s.logBuff
 		}

+		var logHookLast func(e *logg.Entry) error
+		if s.Cfg.PanicOnWarning {
+			logHookLast = loggers.PanicOnWarningHook
+		}
+
 		logger := loggers.New(
 			loggers.Options{
 				StdOut:        w,
 				StdErr:        w,
 				Level:         s.Cfg.LogLevel,
 				DistinctLevel: logg.LevelWarn,
+				HandlerPost:   logHookLast,
 			},
 		)

@@ -1143,6 +1149,9 @@ type IntegrationTestConfig struct {
 	// The log level to use.
 	LogLevel logg.Level

+	// Whether to panic on warnings.
+	PanicOnWarning bool
+
 	// Whether it needs the real file system (e.g. for js.Build tests).
 	NeedsOsFS bool

PATCH

echo "Patch applied successfully."
