#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "- `blocks/` \u2192 Server-persisted configuration objects for external service creden" "src/prefect/AGENTS.md" && grep -qF "- **`position` in JSON schema** \u2014 `model_json_schema()` injects a `position` key" "src/prefect/blocks/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/prefect/AGENTS.md b/src/prefect/AGENTS.md
@@ -49,5 +49,6 @@ Use `get_logger()` from `prefect.logging` instead of raw `logging.getLogger()` 
 - `runner/` → Thin facade over extracted single-responsibility classes for local flow run execution (see runner/AGENTS.md)
 - `deployments/` → YAML-driven deployment lifecycle: project init, build/push/pull steps, and triggering remote flow runs (see deployments/AGENTS.md)
 - `utilities/` → Cross-cutting helpers: async utils, schema hydration, callables introspection, and more (see utilities/AGENTS.md)
+- `blocks/` → Server-persisted configuration objects for external service credentials and settings (see blocks/AGENTS.md)
 - `docker/` → `DockerImage` class for building and pushing Docker images during deployment
 - `telemetry/` → OS-level resource metric collection and run telemetry
diff --git a/src/prefect/blocks/AGENTS.md b/src/prefect/blocks/AGENTS.md
@@ -0,0 +1,48 @@
+# Blocks
+
+Reusable, server-persisted configuration objects for connecting workflows to external services. Blocks store credentials and settings securely and are shared across runs via the Prefect server.
+
+## Purpose & Scope
+
+Blocks handle configuration lifecycle: define fields in Python, register schema with the server, save/load named instances, and serialize secrets safely. They do NOT execute workflow logic — that belongs in flows and tasks. Block subclasses define the interface; `core.py` handles all server interaction.
+
+## Entry Points & Contracts
+
+- `Block` (`core.py`) — base class for all blocks. Subclass it, declare Pydantic fields, optionally set `_block_type_slug`, `_logo_url`, etc.
+- `abstract.py` — abstract interfaces (`CredentialsBlock`, `NotificationBlock`, `DatabaseBlock`, `ObjectStorageBlock`, `SecretBlock`, `JobBlock`) to signal capability and constrain API shape.
+- `system.py` — built-in `Secret[T]` block for storing a single secret value.
+- `notifications.py` — `SlackWebhook` and Apprise-based notification blocks.
+- `webhook.py` — `Webhook` block for calling HTTP endpoints.
+- `redis.py` — `RedisStorageContainer` implementing `WritableFileSystem`.
+
+## Usage Patterns
+
+**Define a block:**
+```python
+class MyBlock(Block):
+    _block_type_slug = "my-block"
+    api_key: SecretStr
+    endpoint: str
+```
+
+**Save and load:**
+```python
+await MyBlock(api_key="...", endpoint="...").save("prod")
+block = await MyBlock.load("prod")
+```
+
+**Sync/async dispatch:** All I/O methods (`save`, `load`, `register_type_and_schema`, `delete`) use `@async_dispatch` — the same method name works in sync and async contexts.
+
+## Anti-Patterns
+
+- **Don't call `register_type_and_schema()` manually before `save()`** — `save()` calls it automatically and handles idempotency.
+- **Don't change `_block_type_slug` after a block has been registered** — the slug is the server-side primary key; renaming it creates a new block type and orphans existing documents.
+- **Don't use `load(validate=False)` as the normal path** — it bypasses validation and leaves missing fields as `None`. It exists only for schema migration scenarios.
+
+## Pitfalls
+
+- **`position` in JSON schema** — `model_json_schema()` injects a `position` key (0-based field declaration order) into every property, including nested block definitions. This key affects the schema checksum. Adding or reordering fields changes the checksum and invalidates previously stored schema references.
+- **Schema checksum stability** — the checksum covers field definitions including `position`. Any field addition, removal, or reorder creates a new schema version on the server.
+- **Secret fields use dot-notation paths** — `"credentials.api_key"` means a nested field is secret; `"passwords.*"` means all values under that key are secret. The `secret_fields` list in the schema drives serialization obfuscation.
+- **Nested blocks are registered transitively** — `register_type_and_schema()` walks all field annotations recursively. A deeply nested block that fails registration will surface an error at the outermost `save()` call.
+- **Sync/async paths must stay in lockstep** — `_save_sync` and `asave` / `_save` must produce identical results. Changes to one must be mirrored in the other.
PATCH

echo "Gold patch applied."
