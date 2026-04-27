#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "- **`command_to_string` always uses POSIX quoting (`shlex.join`), even on Window" "src/prefect/utilities/AGENTS.md" && grep -qF "When a flow is decorated with an infrastructure decorator (`@docker`, `@ecs`, `@" "src/prefect/workers/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/prefect/utilities/AGENTS.md b/src/prefect/utilities/AGENTS.md
@@ -15,7 +15,7 @@ Does NOT include: server-specific utilities (`server/utilities/`), concurrency s
 - `callables.py` — Function signature introspection and parameter coercion
 - `collections.py` — Extended collection helpers (visit, flatten, remove nested keys)
 - `annotations.py` — Custom Prefect type annotations used in flow/task signatures
-- `processutils.py` — Subprocess execution and output streaming helpers (`run_process`, `consume_process_output`, `stream_text`)
+- `processutils.py` — Subprocess execution, output streaming, and command serialization helpers (`run_process`, `consume_process_output`, `stream_text`, `command_to_string`, `command_from_string`)
 - `pydantic.py` — Pydantic v1/v2 compatibility shims
 - `templating.py` — Jinja template utilities and `maybe_template()` detection
 - `filesystem.py` — File filtering (`filter_files`), path normalization, and `tmpchdir` context manager
@@ -77,3 +77,5 @@ Handlers return `Placeholder` subclasses (e.g. `RemoveValue`, `InvalidJSON`, `In
 - **Passing the same key in both an explicit parameter and a `**kwargs` dict raises `TypeError`.** `parameters_to_args_kwargs` detects when a VAR_KEYWORD (`**kwargs`) dict contains a key that also appears as an explicit parameter and raises rather than silently letting the variadic entry win. Exception: POSITIONAL_ONLY parameters are exempt because `fn(1, **{'a': 2})` is legal when `a` is positional-only.
 - **`filter_files` with `include_dirs=True` (the default) always includes all ancestor directories of matched files**, even if those directories weren't directly matched by the ignore patterns. This ensures `shutil.copytree`'s `ignore_func` doesn't skip directories containing files that should be copied. Side effect: callers expecting only pathspec-matched entries will receive additional directory paths. The parent-dir expansion does NOT run when `include_dirs=False`.
 - **Never access `EngineContext.run_results` directly via `id(obj)`.** Always call `get_state_for_result(obj)`.
+- **`command_to_string` always uses POSIX quoting (`shlex.join`), even on Windows.** This is intentional for platform-neutral storage — bundle commands are serialized by one platform and may be deserialized by another. `command_from_string` uses a dual-path approach: if the string was POSIX-serialized by Prefect (round-trips cleanly through `shlex.split`/`shlex.join`), it uses POSIX parsing; otherwise it falls back to native Windows command-line parsing (`CommandLineToArgvW`). Do not use `" ".join(command)` or `shlex.split(command)` directly when working with stored Prefect commands — use these helpers instead.
+- **`get_sys_executable()` no longer quotes the Python path on Windows.** It previously returned `'"path/to/python"'` (with embedded quotes) on Windows; now it returns the raw path. Code relying on the old quoted form (e.g., joining into a shell string) will break — use `subprocess.list2cmdline` or `command_to_string` for shell-safe serialization instead.
diff --git a/src/prefect/workers/AGENTS.md b/src/prefect/workers/AGENTS.md
@@ -26,6 +26,14 @@ Workers stamp two env vars into `os.environ` for their own process, so all API r
 
 These are separate from the per-flow-run attribution vars injected into the child process environment by `prepare_for_flow_run(worker_name=..., worker_id=...)`.
 
+## Bundle Launcher Override
+
+When a flow is decorated with an infrastructure decorator (`@docker`, `@ecs`, `@kubernetes`, etc.) and a `launcher` argument is supplied, `InfrastructureBoundFlow` stores a normalized `BundleLauncherOverride` on `flow.launcher`. `BaseWorker.submit()` extracts this via `getattr(flow, "launcher", None)` and calls `resolve_bundle_step_with_launcher(step, launcher, side)` before converting steps to commands.
+
+**Non-obvious:** the launcher replaces the `uv run ...` prefix entirely. With a launcher, the resulting command is `[*launcher, "-m", "<module>", "--key", "<path>"]` rather than `["uv", "run", "--with", "...", "--python", "X.Y", "-m", "<module>", "--key", "<path>"]`. Launchers and `requires` are mutually exclusive — `convert_step_to_command` raises `ValueError` if a step has both.
+
+Work-pool-level launchers are configured via `prefect work-pool storage configure s3|gcs|azure --launcher <executable>` and are stored in the step dict itself. Flow-level launchers (via the decorator) are resolved at submit time and win over the work-pool step configuration.
+
 ## Anti-Patterns
 
 - Do not set `PREFECT__WORKER_NAME` / `PREFECT__WORKER_ID` in `os.environ` from outside `BaseWorker` — setup/teardown own this lifecycle.
PATCH

echo "Gold patch applied."
