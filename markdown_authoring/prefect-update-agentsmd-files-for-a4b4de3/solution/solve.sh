#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "- **`resolve_block_document_references` raises `ValueError` for malformed block " "src/prefect/utilities/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/prefect/utilities/AGENTS.md b/src/prefect/utilities/AGENTS.md
@@ -70,6 +70,7 @@ Handlers return `Placeholder` subclasses (e.g. `RemoveValue`, `InvalidJSON`, `In
 ## Pitfalls
 
 - `maybe_template(s)` (in `templating.py`) only checks whether a string looks like it contains a Jinja expression — it does not validate that it's well-formed. A string with `{{` but no `}}` returns `True`.
+- **`resolve_block_document_references` raises `ValueError` for malformed block placeholders.** Placeholders must follow the format `prefect.blocks.<block-type-slug>.<block-document-name>` (at least two dot-separated parts after the prefix). A placeholder like `{{ prefect.blocks.only-type }}` (missing the document name) raises `ValueError` before any network call is made.
 - `HydrationContext` workspace variables are loaded once at build time. Stale contexts don't reflect variable updates made after context creation.
 - **Non-UTF-8 subprocess output is silently replaced.** `consume_process_output` and `stream_text` (via `TextReceiveStream(errors="replace")`) replace invalid bytes with the Unicode replacement character `\ufffd` rather than raising. If captured output contains `\ufffd`, the subprocess emitted bytes that were not valid UTF-8.
 - **`parameters_to_args_kwargs` adjusts the positional/keyword split based on the wrapper's signature, not the wrapped function's.** For `@functools.wraps`-decorated callables, it inspects the *wrapper* (via `follow_wrapped=False`) to count how many positional slots are actually available and routes excess parameters to `**kwargs`. This means `args` and `kwargs` from this function are shaped for the *wrapper* call, not the inner function — callers must not assume all POSITIONAL_OR_KEYWORD parameters end up in `args`.
PATCH

echo "Gold patch applied."
