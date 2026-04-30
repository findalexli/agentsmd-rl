#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "- **`generate_parameter_schema` silently downgrades unsupported parameter types " "src/prefect/utilities/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/prefect/utilities/AGENTS.md b/src/prefect/utilities/AGENTS.md
@@ -77,6 +77,7 @@ Handlers return `Placeholder` subclasses (e.g. `RemoveValue`, `InvalidJSON`, `In
 - **`parameters_to_args_kwargs` skips the positional-to-keyword rewrite entirely when the function signature contains `*args`.** Inserting KEYWORD_ONLY parameters before a VAR_POSITIONAL parameter is invalid in Python, so the original signature is used as-is in that case.
 - **Passing the same key in both an explicit parameter and a `**kwargs` dict raises `TypeError`.** `parameters_to_args_kwargs` detects when a VAR_KEYWORD (`**kwargs`) dict contains a key that also appears as an explicit parameter and raises rather than silently letting the variadic entry win. Exception: POSITIONAL_ONLY parameters are exempt because `fn(1, **{'a': 2})` is legal when `a` is positional-only.
 - **`filter_files` with `include_dirs=True` (the default) always includes all ancestor directories of matched files**, even if those directories weren't directly matched by the ignore patterns. This ensures `shutil.copytree`'s `ignore_func` doesn't skip directories containing files that should be copied. Side effect: callers expecting only pathspec-matched entries will receive additional directory paths. The parent-dir expansion does NOT run when `include_dirs=False`.
+- **`generate_parameter_schema` silently downgrades unsupported parameter types to `Any`.** When a parameter's type raises `ValueError`, `TypeError`, or `PydanticInvalidForJsonSchema` during JSON schema generation (e.g., `Callable`, custom types Pydantic can't serialize), the type is replaced with `Any` in the output schema without warning. If a flow parameter shows up as `Any` in the schema, the declared type is not JSON-schema-compatible.
 - **Never access `EngineContext.run_results` directly via `id(obj)`.** Always call `get_state_for_result(obj)`.
 - **`command_to_string` always uses POSIX quoting (`shlex.join`), even on Windows.** This is intentional for platform-neutral storage — bundle commands are serialized by one platform and may be deserialized by another. `command_from_string` uses a dual-path approach: if the string was POSIX-serialized by Prefect (round-trips cleanly through `shlex.split`/`shlex.join`), it uses POSIX parsing; otherwise it falls back to native Windows command-line parsing (`CommandLineToArgvW`). Do not use `" ".join(command)` or `shlex.split(command)` directly when working with stored Prefect commands — use these helpers instead.
 - **`get_sys_executable()` no longer quotes the Python path on Windows.** It previously returned `'"path/to/python"'` (with embedded quotes) on Windows; now it returns the raw path. Code relying on the old quoted form (e.g., joining into a shell string) will break — use `subprocess.list2cmdline` or `command_to_string` for shell-safe serialization instead.
PATCH

echo "Gold patch applied."
