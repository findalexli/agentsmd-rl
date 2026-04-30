#!/usr/bin/env bash
set -euo pipefail

cd /workspace/android

# Idempotency guard
if grep -qF "- **Verify code paths with logging, not reasoning.** Add `log_warn (LOG_DEFAULT," ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -199,8 +199,31 @@ This pattern ensures proper encoding, timestamps, and file attributes are handle
 3. For deep .binlog analysis, use the `azdo-build-investigator` skill.
 4. Only after the skill confirms no Azure DevOps failures should you report CI as passing.
 
+## Investigation & Debugging Practices
+
+When diagnosing runtime, build, or test failures, follow these practices. They exist because the .NET ↔ JNI ↔ C++ ↔ generated-native stack is loosely coupled and static reasoning alone is unreliable.
+
+- **Reproduce CI failures locally — do not iterate through CI.** A clean local test cycle is minutes; a CI iteration is hours. Run device tests the same way CI does:
+  ```bash
+  make prepare && make all CONFIGURATION=Release
+  ./dotnet-local.sh build tests/Mono.Android-Tests/Mono.Android-Tests/Mono.Android.NET-Tests.csproj \
+      -t:RunTestApp -c Release \
+      -p:_AndroidTypeMapImplementation=<llvm-ir|managed|trimmable> \
+      -p:UseMonoRuntime=<true|false>
+  ```
+  On Windows, use `build.cmd` and `dotnet-local.cmd` instead of `make`/`dotnet-local.sh`.
+  Results land in `TestResult-Mono.Android.NET_Tests-*.xml` at the repo root.
+
+- **When the build gets into a weird state, nuke `bin/` and `obj/` and rebuild from scratch.** Stale incremental output causes phantom errors. See **Troubleshooting → Build** below.
+
+- **Verify code paths with logging, not reasoning.** Add `log_warn (LOG_DEFAULT, "..."sv, ...)` in C++ or `Android.Util.Log` in C#, rebuild, re-run, and check `adb logcat -d`. If your log never fires, your call-graph assumption is wrong.
+
+- **Decompile the produced `.dll` before blaming runtime.** Use `ilspycmd` or `ildasm` to inspect the actual generated IL/metadata. A missing attribute or misnamed type in generator output cascades into opaque runtime failures.
+
+- **`am instrument` going silent means it crashed, not hung.** Check `adb logcat -d | grep -E 'FATAL|tombstone|signal'` for a native crash dump. Do not wait for a CI timeout to "confirm" a hang that was really an instant crash.
+
 ## Troubleshooting
-- **Build:** Clean `bin/`+`obj/`, check Android SDK/NDK, `make clean`
+- **Build:** Clean `bin/`+`obj/`, check Android SDK/NDK, `make clean && make prepare && make all`
 - **MSBuild:** Test in isolation, validate inputs
 - **Device:** Use update directories for rapid Debug iteration
 - **Performance:** See `../Documentation/guides/profiling.md` and `../Documentation/guides/tracing.md`
PATCH

echo "Gold patch applied."
