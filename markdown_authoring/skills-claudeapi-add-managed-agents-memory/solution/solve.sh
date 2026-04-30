#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "**Reading guide:** Start with `shared/managed-agents-overview.md`, then the topi" "skills/claude-api/SKILL.md" && grep -qF "Individual text documents inside a store (\u2264 100KB each). `create` creates at a `" "skills/claude-api/shared/managed-agents-api-reference.md" && grep -qF "| `resources`     | array    | No       | Files, GitHub repos, or memory stores," "skills/claude-api/shared/managed-agents-core.md" && grep -qF "Attach files, GitHub repositories, and memory stores to a session. **Session cre" "skills/claude-api/shared/managed-agents-environments.md" && grep -qF "Each attached store is mounted in the session container at `/mnt/memory/<store-n" "skills/claude-api/shared/managed-agents-memory.md" && grep -qF "**Which beta header goes where:** The SDK sets `managed-agents-2026-04-01` autom" "skills/claude-api/shared/managed-agents-overview.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/claude-api/SKILL.md b/skills/claude-api/SKILL.md
@@ -226,15 +226,15 @@ For placement patterns, architectural guidance, and the silent-invalidator audit
 
 **Mandatory flow:** Agent (once) → Session (every run). `model`/`system`/`tools` live on the agent, never the session. See `shared/managed-agents-overview.md` for the full reading guide, beta headers, and pitfalls.
 
-**Beta headers:** `managed-agents-2026-04-01` — the SDK sets this automatically for all `client.beta.{agents,environments,sessions,vaults}.*` calls. Skills API uses `skills-2025-10-02` and Files API uses `files-api-2025-04-14`, but you don't need to explicitly pass those in for endpoints other than `/v1/skills` and `/v1/files`.
+**Beta headers:** `managed-agents-2026-04-01` — the SDK sets this automatically for all `client.beta.{agents,environments,sessions,vaults,memory_stores}.*` calls. Skills API uses `skills-2025-10-02` and Files API uses `files-api-2025-04-14`, but you don't need to explicitly pass those in for endpoints other than `/v1/skills` and `/v1/files`.
 
 **Subcommands** — invoke directly with `/claude-api <subcommand>`:
 
 | Subcommand | Action |
 |---|---|
 | `managed-agents-onboard` | Walk the user through setting up a Managed Agent from scratch. **Read `shared/managed-agents-onboarding.md` immediately** and follow its interview script: mental model → know-or-explore branch → template config → session setup → emit code. Do not summarize — run the interview. |
 
-**Reading guide:** Start with `shared/managed-agents-overview.md`, then the topical `shared/managed-agents-*.md` files (core, environments, tools, events, client-patterns, onboarding, api-reference). For Python, TypeScript, Go, Ruby, PHP, and Java, read `{lang}/managed-agents/README.md` for code examples. For cURL, read `curl/managed-agents.md`. **Agents are persistent — create once, reference by ID.** Store the agent ID returned by `agents.create` and pass it to every subsequent `sessions.create`; do not call `agents.create` in the request path. The Anthropic CLI is one convenient way to create agents and environments from version-controlled YAML (URL in `shared/live-sources.md`). If a binding you need isn't shown in the language README, WebFetch the relevant entry from `shared/live-sources.md` rather than guess. C# does not currently have Managed Agents support; use raw HTTP from `curl/managed-agents.md` as a reference.
+**Reading guide:** Start with `shared/managed-agents-overview.md`, then the topical `shared/managed-agents-*.md` files (core, environments, tools, events, memory, client-patterns, onboarding, api-reference). For Python, TypeScript, Go, Ruby, PHP, and Java, read `{lang}/managed-agents/README.md` for code examples. For cURL, read `curl/managed-agents.md`. **Agents are persistent — create once, reference by ID.** Store the agent ID returned by `agents.create` and pass it to every subsequent `sessions.create`; do not call `agents.create` in the request path. The Anthropic CLI is one convenient way to create agents and environments from version-controlled YAML (URL in `shared/live-sources.md`). If a binding you need isn't shown in the language README, WebFetch the relevant entry from `shared/live-sources.md` rather than guess. C# does not currently have Managed Agents support; use raw HTTP from `curl/managed-agents.md` as a reference.
 
 **When the user wants to set up a Managed Agent from scratch** (e.g. "how do I get started", "walk me through creating one", "set up a new agent"): read `shared/managed-agents-onboarding.md` and run its interview — same flow as the `managed-agents-onboard` subcommand.
 
diff --git a/skills/claude-api/shared/managed-agents-api-reference.md b/skills/claude-api/shared/managed-agents-api-reference.md
@@ -8,7 +8,7 @@ All endpoints require `x-api-key` and `anthropic-version: 2023-06-01` headers. M
 anthropic-beta: managed-agents-2026-04-01
 ```
 
-The SDK adds this header automatically for all `client.beta.{agents,environments,sessions,vaults}.*` calls. Skills endpoints use `skills-2025-10-02`; Files endpoints use `files-api-2025-04-14`.
+The SDK adds this header automatically for all `client.beta.{agents,environments,sessions,vaults,memory_stores}.*` calls. Skills endpoints use `skills-2025-10-02`; Files endpoints use `files-api-2025-04-14`.
 
 ---
 
@@ -26,9 +26,12 @@ All resources are under the `beta` namespace. Python and TypeScript share identi
 | Session Resources | `sessions.resources.add` / `retrieve` / `update` / `list` / `delete` | `Sessions.Resources.Add` / `Get` / `Update` / `List` / `Delete` |
 | Vaults | `vaults.create` / `retrieve` / `update` / `list` / `delete` / `archive` | `Vaults.New` / `Get` / `Update` / `List` / `Delete` / `Archive` |
 | Credentials | `vaults.credentials.create` / `retrieve` / `update` / `list` / `delete` / `archive` | `Vaults.Credentials.New` / `Get` / `Update` / `List` / `Delete` / `Archive` |
+| Memory Stores | `memory_stores.create` / `retrieve` / `update` / `list` / `delete` / `archive` | `MemoryStores.New` / `Get` / `Update` / `List` / `Delete` / `Archive` |
+| Memories | `memory_stores.memories.create` / `retrieve` / `update` / `list` / `delete` | `MemoryStores.Memories.New` / `Get` / `Update` / `List` / `Delete` |
+| Memory Versions | `memory_stores.memory_versions.list` / `retrieve` / `redact` | `MemoryStores.MemoryVersions.List` / `Get` / `Redact` |
 
 **Naming quirks to watch for:**
-- Agents have **no delete** — only `archive`. Archive is **permanent**: the agent becomes read-only, new sessions cannot reference it, and there is no unarchive. Confirm with the user before archiving a production agent. Environments, Sessions, Vaults, and Credentials have both `delete` and `archive`; Session Resources, Files, and Skills are `delete`-only.
+- Agents have **no delete** — only `archive`. Archive is **permanent**: the agent becomes read-only, new sessions cannot reference it, and there is no unarchive. Confirm with the user before archiving a production agent. Environments, Sessions, Vaults, Credentials, and Memory Stores have both `delete` and `archive`; Session Resources, Files, Skills, and Memories are `delete`-only; Memory Versions have neither — only `redact`.
 - Session resources use `add` (not `create`).
 - Go's event stream is `StreamEvents` (not `Stream`).
 
@@ -75,7 +78,7 @@ All resources are under the `beta` namespace. Python and TypeScript share identi
 | Method   | Path                                                    | Operation        | Description                              |
 | -------- | ------------------------------------------------------- | ---------------- | ---------------------------------------- |
 | `GET` | `/v1/sessions/{session_id}/resources` | ListResources | List resources attached to session |
-| `POST` | `/v1/sessions/{session_id}/resources` | AddResource | Attach file or github_repository mount (SDK method: `add`, not `create`) |
+| `POST` | `/v1/sessions/{session_id}/resources` | AddResource | Attach `file` or `github_repository` resource (SDK method: `add`, not `create`). `memory_store` resources attach at session-create time only. |
 | `GET` | `/v1/sessions/{session_id}/resources/{resource_id}` | GetResource | Get a single resource |
 | `POST` | `/v1/sessions/{session_id}/resources/{resource_id}` | UpdateResource | Update resource |
 | `DELETE` | `/v1/sessions/{session_id}/resources/{resource_id}` | DeleteResource | Remove resource from session |
@@ -117,6 +120,41 @@ Credentials are individual secrets stored inside a vault.
 | `DELETE` | `/v1/vaults/{vault_id}/credentials/{credential_id}`               | DeleteCredential   | Delete credential            |
 | `POST`   | `/v1/vaults/{vault_id}/credentials/{credential_id}/archive`       | ArchiveCredential  | Archive credential           |
 
+## Memory Stores
+
+Workspace-scoped persistent memory that survives across sessions. Attach to a session via a `{"type": "memory_store", "memory_store_id": ...}` entry in `resources[]` (session-create time only). See `shared/managed-agents-memory.md` for the conceptual guide, the FUSE-mount agent interface, preconditions, and versioning.
+
+| Method   | Path                                             | Operation          | Description                              |
+| -------- | ------------------------------------------------ | ------------------ | ---------------------------------------- |
+| `POST`   | `/v1/memory_stores`                              | CreateMemoryStore  | Create a store (`name`, `description`, `metadata`) |
+| `GET`    | `/v1/memory_stores`                              | ListMemoryStores   | List stores (`include_archived`, `created_at_{gte,lte}`) |
+| `GET`    | `/v1/memory_stores/{memory_store_id}`            | GetMemoryStore     | Get store details                        |
+| `POST`   | `/v1/memory_stores/{memory_store_id}`            | UpdateMemoryStore  | Update store                             |
+| `DELETE` | `/v1/memory_stores/{memory_store_id}`            | DeleteMemoryStore  | Delete store                             |
+| `POST`   | `/v1/memory_stores/{memory_store_id}/archive`    | ArchiveMemoryStore | Archive store. Makes it **read-only**; existing sessions continue, new sessions cannot reference it. No unarchive. |
+
+## Memories
+
+Individual text documents inside a store (≤ 100KB each). `create` creates at a `path` and returns `409` (`memory_path_conflict_error`, with `conflicting_memory_id`) if the path is occupied; `update` mutates by `mem_...` ID (rename and/or content). Only `update` accepts a `precondition` (`{"type": "content_sha256", "content_sha256": ...}`) — on mismatch returns `409` (`memory_precondition_failed_error`). List endpoints accept `view: "basic"|"full"` (controls whether `content` is populated; `retrieve` defaults to `full`).
+
+| Method   | Path                                                              | Operation      | Description                              |
+| -------- | ----------------------------------------------------------------- | -------------- | ---------------------------------------- |
+| `GET`    | `/v1/memory_stores/{memory_store_id}/memories`                    | ListMemories   | Returns `Memory \| MemoryPrefix`; filter by `path_prefix`, `depth`, `order_by`/`order` |
+| `POST`   | `/v1/memory_stores/{memory_store_id}/memories`                    | CreateMemory   | Create at `path` (SDK: `memories.create`); `409 memory_path_conflict_error` if occupied |
+| `GET`    | `/v1/memory_stores/{memory_store_id}/memories/{memory_id}`        | GetMemory      | Read one memory (defaults to `view="full"`) |
+| `PATCH`  | `/v1/memory_stores/{memory_store_id}/memories/{memory_id}`        | UpdateMemory   | Change `content`, `path`, or both by ID; optional `precondition` |
+| `DELETE` | `/v1/memory_stores/{memory_store_id}/memories/{memory_id}`        | DeleteMemory   | Delete (optional `expected_content_sha256`) |
+
+## Memory Versions
+
+Immutable per-mutation snapshots (`memver_...`) — the audit and rollback surface. `operation` ∈ `created` / `modified` / `deleted`.
+
+| Method   | Path                                                                          | Operation             | Description                              |
+| -------- | ----------------------------------------------------------------------------- | --------------------- | ---------------------------------------- |
+| `GET`    | `/v1/memory_stores/{memory_store_id}/memory_versions`                         | ListMemoryVersions    | Newest-first; filter by `memory_id`, `operation`, `session_id`, `api_key_id`, `created_at_{gte,lte}` |
+| `GET`    | `/v1/memory_stores/{memory_store_id}/memory_versions/{version_id}`            | GetMemoryVersion      | List fields + full `content`             |
+| `POST`   | `/v1/memory_stores/{memory_store_id}/memory_versions/{version_id}/redact`     | RedactMemoryVersion   | Clear `content`/`content_sha256`/`content_size_bytes`/`path`; preserve actor + timestamps |
+
 ## Files
 
 | Method   | Path                                             | Operation        | Description                              |
diff --git a/skills/claude-api/shared/managed-agents-core.md b/skills/claude-api/shared/managed-agents-core.md
@@ -21,7 +21,7 @@ Agent (config) ───────▶│  (agent loop: Claude + tool calls)  
 Environment (template) ──▶ Container (tool execution workspace)
                                  │
                          Session ─┤
-                                 ├── Resources (files, repos — mounted at startup)
+                                 ├── Resources (files, repos, memory stores — attached at startup)
                                  ├── Vault IDs (MCP credential references)
                                  └── Conversation (event stream in/out)
 ```
@@ -83,7 +83,7 @@ Key fields returned by the API:
 | `archived_at` | string | ISO 8601 timestamp (nullable) |
 | `environment_id` | string | Environment ID |
 | `agent` | object | Agent configuration |
-| `resources` | array | Attached files and repos |
+| `resources` | array | Attached files, repos, and memory stores |
 | `metadata` | object | User-provided key-value pairs (max 8 keys) |
 | `usage` | object | Token usage statistics |
 
@@ -119,7 +119,7 @@ const session = await client.beta.sessions.create(
 | `agent`         | string or object | **Yes** | String shorthand `"agent_abc123"` (latest version) or `{type: "agent", id, version}` |
 | `environment_id`| string   | **Yes**  | Environment ID                                 |
 | `title`         | string   | No       | Human-readable name (appears in logs/dashboards) |
-| `resources`     | array    | No       | Files or GitHub repos, mounted to the container at startup |
+| `resources`     | array    | No       | Files, GitHub repos, or memory stores, attached to the container at startup. Memory stores are session-create-only (not addable via `resources.add()`). |
 | `vault_ids`     | array    | No       | Vault IDs (`vlt_*`) — MCP credentials with auto-refresh. See `shared/managed-agents-tools.md` → Vaults. |
 | `metadata`      | object   | No       | User-provided key-value pairs                  |
 
diff --git a/skills/claude-api/shared/managed-agents-environments.md b/skills/claude-api/shared/managed-agents-environments.md
@@ -53,7 +53,7 @@ const env = await client.beta.environments.create({
 
 ## Resources
 
-Attach files and GitHub repositories to a session. **Session creation blocks until all resources are mounted** — the container won't go `running` until every file and repo is in place. Max **999 file resources** per session. Multiple GitHub repositories per session are supported.
+Attach files, GitHub repositories, and memory stores to a session. **Session creation blocks until all resources are mounted** — the container won't go `running` until every file and repo is in place. Max **999 file resources** per session. Multiple GitHub repositories per session are supported. For `type: "memory_store"` resources (persistent cross-session memory — max 8 per session), see `shared/managed-agents-memory.md`.
 
 ### File Uploads (input — host → agent)
 
diff --git a/skills/claude-api/shared/managed-agents-memory.md b/skills/claude-api/shared/managed-agents-memory.md
@@ -0,0 +1,197 @@
+# Managed Agents — Memory Stores
+
+> **Public beta.** Memory stores ship under the `managed-agents-2026-04-01` beta header; the SDK sets it automatically on all `client.beta.memory_stores.*` calls. If `client.beta.memory_stores` is missing, upgrade to the latest SDK release.
+
+Sessions are ephemeral by default — when one ends, anything the agent learned is gone. A **memory store** is a workspace-scoped collection of small text documents that persists across sessions. When a store is attached to a session (via `resources[]`), it is mounted into the container as a filesystem directory; the agent reads and writes it with the ordinary file tools, and a system-prompt note tells it the mount is there.
+
+Every mutation to a memory produces an immutable **memory version** (`memver_...`), giving you an audit trail and point-in-time rollback/redact.
+
+## Object model
+
+| Object | ID prefix | Scope | Notes |
+| --- | --- | --- | --- |
+| Memory store | `memstore_...` | Workspace | Attach to sessions via `resources[]` |
+| Memory | `mem_...` | Store | One text file, addressed by `path` (≤ 100KB each — prefer many small files) |
+| Memory version | `memver_...` | Memory | Immutable snapshot per mutation; `operation` ∈ `created` / `modified` / `deleted` |
+
+## Create a store
+
+`description` is passed to the agent so it knows what the store contains — write it for the model, not for humans.
+
+```python
+store = client.beta.memory_stores.create(
+    name="User Preferences",
+    description="Per-user preferences and project context.",
+)
+print(store.id)  # memstore_01Hx...
+```
+
+Other SDKs: TypeScript `client.beta.memoryStores.create({...})`; Go `client.Beta.MemoryStores.New(ctx, ...)`. See `shared/managed-agents-api-reference.md` → SDK Method Reference for the full per-language table.
+
+Stores support `retrieve` / `update` / `list` (with `include_archived`, `created_at_{gte,lte}` filters) / `delete` / **`archive`**. Archive makes the store read-only — existing session attachments continue, new sessions cannot reference it; no unarchive.
+
+### Seed with content (optional)
+
+Pre-load reference material before any session runs. `memories.create` creates a memory at the given `path`; if a memory already exists there the call returns `409` (`memory_path_conflict_error`, with the `conflicting_memory_id`). The store ID is the first positional argument.
+
+```python
+client.beta.memory_stores.memories.create(
+    store.id,
+    path="/formatting_standards.md",
+    content="All reports use GAAP formatting. Dates are ISO-8601...",
+)
+```
+
+## Attach to a session
+
+Memory stores go in the session's `resources[]` array alongside `file` and `github_repository` resources (see `shared/managed-agents-environments.md` → Resources). Memory stores attach at **session create time only** — `sessions.resources.add()` does not accept `memory_store`.
+
+```python
+session = client.beta.sessions.create(
+    agent=agent.id,
+    environment_id=environment.id,
+    resources=[
+        {
+            "type": "memory_store",
+            "memory_store_id": store.id,
+            "access": "read_write",  # or "read_only"; default is "read_write"
+            "instructions": "User preferences and project context. Check before starting any task.",
+        }
+    ],
+)
+```
+
+| Field | Required | Notes |
+| --- | --- | --- |
+| `type` | ✅ | `"memory_store"` |
+| `memory_store_id` | ✅ | `memstore_...` |
+| `access` | — | `"read_write"` (default) or `"read_only"` — enforced at the filesystem level on the mount |
+| `instructions` | — | Session-specific guidance for this store, in addition to the store's `name`/`description`. ≤ 4,096 chars. |
+
+**Max 8 memory stores per session.** Attach multiple when different slices of memory have different owners or lifecycles — e.g. one read-only shared-reference store plus one read-write per-user store, or one store per end-user/team/project sharing a single agent config.
+
+### How the agent sees it (FUSE mount)
+
+Each attached store is mounted in the session container at `/mnt/memory/<store-name>/`. The agent interacts with it using the standard file tools (`bash`, `read`, `write`, `edit`, `glob`, `grep`) — there are no dedicated memory tools. `access: "read_only"` makes the mount read-only at the filesystem level; `"read_write"` allows the agent to create, edit, and delete files under it. A short description of each mount (name, path, `instructions`, access) is automatically injected into the system prompt so the agent knows the store exists without you having to mention it.
+
+Writes the agent makes under the mount are persisted back to the store and produce memory versions just like host-side `memories.update` calls.
+
+## Manage memories directly (host-side)
+
+Use these for review workflows, correcting bad memories, or seeding stores out-of-band.
+
+### List
+
+Returns `Memory | MemoryPrefix` entries — a `MemoryPrefix` (`type: "memory_prefix"`, just a `path`) is a directory-like node when listing hierarchically. Use `path_prefix` to scope (include a trailing slash: `"/notes/"` matches `/notes/a.md` but not `/notes_backup/old.md`) and `depth` to bound the tree walk. `order_by` / `order` sort the result. Pass `view="full"` to include `content` in each item; the default `"basic"` returns metadata only.
+
+```python
+for m in client.beta.memory_stores.memories.list(store.id, path_prefix="/"):
+    if m.type == "memory":
+        print(f"{m.path}  ({m.content_size_bytes} bytes, sha={m.content_sha256[:8]})")
+    else:  # "memory_prefix"
+        print(f"{m.path}/")
+```
+
+### Read
+
+```python
+mem = client.beta.memory_stores.memories.retrieve(memory_id, memory_store_id=store.id)
+print(mem.content)
+```
+
+`retrieve` defaults to `view="full"` (content included); `view` matters mainly on list endpoints.
+
+### Create vs. update
+
+| Operation | Addressed by | Semantics |
+| --- | --- | --- |
+| `memories.create(store_id, path=..., content=...)` | **Path** | Create at `path`. `409` (`memory_path_conflict_error`, includes `conflicting_memory_id`) if the path is already occupied. |
+| `memories.update(mem_id, memory_store_id=..., path=..., content=...)` | **`mem_...` ID** | Mutate existing memory. Change `content`, `path` (rename), or both. Renaming onto an occupied path returns the same `409 memory_path_conflict_error`. |
+
+```python
+mem = client.beta.memory_stores.memories.create(
+    store.id,
+    path="/preferences/formatting.md",
+    content="Always use tabs, not spaces.",
+)
+
+client.beta.memory_stores.memories.update(
+    mem.id,
+    memory_store_id=store.id,
+    path="/archive/2026_q1_formatting.md",  # rename
+)
+```
+
+### Optimistic concurrency (precondition on `update`)
+
+`memories.update` accepts a `precondition` so you can read → modify → write back without clobbering a concurrent writer. The only supported type is `content_sha256`. On mismatch the API returns `409` (`memory_precondition_failed_error`) — re-read and retry against fresh state.
+
+```python
+client.beta.memory_stores.memories.update(
+    mem.id,
+    memory_store_id=store.id,
+    content="CORRECTED: Always use 2-space indentation.",
+    precondition={"type": "content_sha256", "content_sha256": mem.content_sha256},
+)
+```
+
+### Delete
+
+```python
+client.beta.memory_stores.memories.delete(mem.id, memory_store_id=store.id)
+```
+
+Pass `expected_content_sha256` for a conditional delete.
+
+## Audit and rollback — memory versions
+
+Every mutation creates an immutable `memver_...` snapshot. Versions accumulate for the lifetime of the parent memory; `memories.retrieve` always returns the current head, the version endpoints give you history.
+
+| Operation that triggers it | `operation` field on the version |
+| --- | --- |
+| `memories.create` at a new path | `"created"` |
+| `memories.update` changing `content`, `path`, or both (or an agent-side write to the mount) | `"modified"` |
+| `memories.delete` | `"deleted"` |
+
+Each version also records `created_by` — an actor object with `type` ∈ `session_actor` / `api_actor` / `user_actor` — and, after redaction, `redacted_at` + `redacted_by`.
+
+### List versions
+
+Newest-first, paginated. Filter by `memory_id`, `operation`, `session_id`, `api_key_id`, or `created_at_gte` / `created_at_lte`. Pass `view="full"` to include `content`; default is metadata-only.
+
+```python
+for v in client.beta.memory_stores.memory_versions.list(store.id, memory_id=mem.id):
+    print(f"{v.id}: {v.operation}")
+```
+
+### Retrieve a version
+
+```python
+version = client.beta.memory_stores.memory_versions.retrieve(
+    version_id, memory_store_id=store.id
+)
+print(version.content)
+```
+
+### Redact a version
+
+Scrubs content from a historical version while preserving the audit trail (actor + timestamps). Clears `content`, `content_sha256`, `content_size_bytes`, and `path`; everything else stays. Use for leaked secrets, PII, or user-deletion requests.
+
+```python
+client.beta.memory_stores.memory_versions.redact(version_id, memory_store_id=store.id)
+```
+
+## Endpoint reference
+
+See `shared/managed-agents-api-reference.md` → Memory Stores / Memories / Memory Versions for the full HTTP method/path tables. Raw HTTP base path:
+
+```
+POST   /v1/memory_stores
+POST   /v1/memory_stores/{memory_store_id}/archive
+GET    /v1/memory_stores/{memory_store_id}/memories
+PATCH  /v1/memory_stores/{memory_store_id}/memories/{memory_id}
+GET    /v1/memory_stores/{memory_store_id}/memory_versions
+POST   /v1/memory_stores/{memory_store_id}/memory_versions/{version_id}/redact
+```
+
+For cURL examples and the CLI (`ant beta:memory-stores ...`), WebFetch the Memory URL in `shared/live-sources.md` → Managed Agents.
diff --git a/skills/claude-api/shared/managed-agents-overview.md b/skills/claude-api/shared/managed-agents-overview.md
@@ -25,11 +25,11 @@ Managed Agents is in beta. The SDK sets required beta headers automatically:
 
 | Beta Header                    | What it enables                                      |
 | ------------------------------ | ---------------------------------------------------- |
-| `managed-agents-2026-04-01`    | Agents, Environments, Sessions, Events, Session Resources, Vaults, Credentials |
+| `managed-agents-2026-04-01`    | Agents, Environments, Sessions, Events, Session Resources, Vaults, Credentials, Memory Stores |
 | `skills-2025-10-02`            | Skills API (for managing custom skill definitions)   |
 | `files-api-2025-04-14`         | Files API for file uploads                           |
 
-**Which beta header goes where:** The SDK sets `managed-agents-2026-04-01` automatically on `client.beta.{agents,environments,sessions,vaults}.*` calls, and `files-api-2025-04-14` / `skills-2025-10-02` automatically on `client.beta.files.*` / `client.beta.skills.*` calls. You do NOT need to add the Skills or Files beta header when calling Managed Agents endpoints. **Exception — session-scoped file listing:** `client.beta.files.list({scope_id: session.id})` is a Files endpoint that takes a Managed Agents parameter, so it needs **both** headers. Pass `betas: ["managed-agents-2026-04-01"]` explicitly on that call (the SDK adds the Files header; you add the Managed Agents one). See `shared/managed-agents-environments.md` → Session outputs.
+**Which beta header goes where:** The SDK sets `managed-agents-2026-04-01` automatically on `client.beta.{agents,environments,sessions,vaults,memory_stores}.*` calls, and `files-api-2025-04-14` / `skills-2025-10-02` automatically on `client.beta.files.*` / `client.beta.skills.*` calls. You do NOT need to add the Skills or Files beta header when calling Managed Agents endpoints. **Exception — session-scoped file listing:** `client.beta.files.list({scope_id: session.id})` is a Files endpoint that takes a Managed Agents parameter, so it needs **both** headers. Pass `betas: ["managed-agents-2026-04-01"]` explicitly on that call (the SDK adds the Files header; you add the Managed Agents one). See `shared/managed-agents-environments.md` → Session outputs.
 
 
 ## Reading Guide
@@ -47,6 +47,7 @@ Managed Agents is in beta. The SDK sets required beta headers automatically:
 | Stream events / handle tool_use        | `shared/managed-agents-events.md` + language file       |
 | Set up environments                    | `shared/managed-agents-environments.md` + language file |
 | Upload files / attach repos            | `shared/managed-agents-environments.md` (Resources)     |
+| Give agents persistent memory across sessions | `shared/managed-agents-memory.md` — memory stores, `memory_store` session resource, preconditions, versions/redact |
 | Store MCP credentials                  | `shared/managed-agents-tools.md` (Vaults section)       |
 | Call a non-MCP API / CLI that needs a secret | `shared/managed-agents-client-patterns.md` Pattern 9 — no container env vars; vaults are MCP-only; keep the secret host-side via a custom tool |
 
@@ -60,4 +61,4 @@ Managed Agents is in beta. The SDK sets required beta headers automatically:
 - **Don't trust HTTP-library timeouts as wall-clock caps** — `requests` `timeout=(c, r)` and `httpx.Timeout(n)` are *per-chunk* read timeouts; they reset every byte, so a trickling connection can block indefinitely. For a hard deadline on raw-HTTP polling, track `time.monotonic()` at the loop level and bail explicitly. Prefer the SDK's `sessions.events.stream()` / `session.events.list()` over hand-rolled HTTP. See `shared/managed-agents-events.md` → Receiving Events.
 - **Messages queue** — you can send events while the session is `running` or `idle`; they're processed in order. No need to wait for a response before sending the next message.
 - **Cloud environments only** — `config.type: "cloud"` is the only supported environment type.
-- **Archive is permanent on every resource** — archiving an agent, environment, session, vault, or credential makes it read-only with no unarchive. For agents and environments specifically, archived resources cannot be referenced by new sessions (existing sessions continue). Do not call `.archive()` on a production agent or environment as cleanup — **always confirm with the user before archiving**.
+- **Archive is permanent on every resource** — archiving an agent, environment, session, vault, credential, or memory store makes it read-only with no unarchive. For agents, environments, and memory stores specifically, archived resources cannot be referenced by new sessions (existing sessions continue). Do not call `.archive()` on a production agent, environment, or memory store as cleanup — **always confirm with the user before archiving**.
PATCH

echo "Gold patch applied."
