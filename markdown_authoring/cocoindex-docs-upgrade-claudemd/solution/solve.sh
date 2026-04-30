#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cocoindex

# Idempotency guard
if grep -qF "CocoIndex uses a **declarative** programming model \u2014 you specify *what* your out" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -16,7 +16,7 @@ uv run maturin develop   # Build Rust code and install Python package (required
 
 ```bash
 cargo test               # Run Rust tests
-uv run dmypy run         # Type check Python code (uses mypy daemon)
+uv run mypy              # Type check Python code
 uv run pytest python/    # Run Python tests (use after both Rust and Python changes)
 ```
 
@@ -25,7 +25,7 @@ uv run pytest python/    # Run Python tests (use after both Rust and Python chan
 | Change Type | Commands to Run |
 |-------------|-----------------|
 | Rust code only | `uv run maturin develop && cargo test` |
-| Python code only | `uv run dmypy run && uv run pytest python/` |
+| Python code only | `uv run mypy && uv run pytest python/` |
 | Both Rust and Python | Run all commands from both categories above |
 
 ## Code Structure
@@ -41,25 +41,28 @@ cocoindex/
 │   ├── py/                     # Python bindings (PyO3)
 │   ├── py_utils/               # Python-Rust utility helpers (error, convert, future)
 │   ├── utils/                  # General utilities: error, batching, fingerprint, etc.
-│   └── cocoindex/              # The legacy version of the core engine. PLEASE IGNORE THIS.
+│   └── extra_text/             # Text processing utilities (splitter, language detection)
 │
 ├── python/
-│   └── cocoindex/              # Python package
-│       ├── __init__.py         # Package entry point
-│       ├── cli.py              # CLI commands
-│       ├── _internal/          # Internal implementation for the core engine
-│       │   ├── api.py          # API definitions (sync and async)
-│       │   ├── app.py          # App implementation
-│       │   ├── datatype.py     # Data type definitions
-│       │   ├── target_state.py # Target state implementation
-│       │   ├── environment.py  # Environment handling
-│       │   ├── function.py     # Function decorator implementation
-│       │   └── scope.py        # Scope implementation
-│       ├── connectors/         # External system connectors
-│       ├── connectorkits/      # Connector building utilities
-│       ├── resources/          # Abstractions for various resources (files, tables, chunks, etc.)
-│       ├── extras/             # Convenience utilities for various types of data processing, etc.
-│       └── tests/              # Python tests
+│   ├── cocoindex/              # Python package
+│   │   ├── __init__.py         # Package entry point
+│   │   ├── cli.py              # CLI commands
+│   │   ├── asyncio.py          # Async App and APIs (import cocoindex.asyncio as coco_aio)
+│   │   ├── _internal/          # Internal implementation for the core engine
+│   │   │   ├── api.py          # Shared API definitions
+│   │   │   ├── api_sync.py     # Sync APIs: App, mount, mount_run
+│   │   │   ├── api_async.py    # Async APIs: App, mount, mount_run
+│   │   │   ├── app.py          # App base implementation
+│   │   │   ├── context_keys.py # ContextKey and ContextProvider
+│   │   │   ├── environment.py  # Environment and lifespan handling
+│   │   │   ├── function.py     # @coco.function decorator implementation
+│   │   │   ├── scope.py        # Scope implementation
+│   │   │   └── target_state.py # Target state implementation
+│   │   ├── connectors/         # External system connectors (localfs, postgres, qdrant, lancedb, google_drive)
+│   │   ├── connectorkits/      # Connector building utilities
+│   │   ├── resources/          # Abstractions: file.py (FileLike), chunk.py (Chunk), schema.py
+│   │   └── extras/             # Utilities: text.py (RecursiveSplitter), sentence_transformers.py
+│   └── tests/                  # Python tests
 │
 ├── examples/                   # Example applications
 ├── docs/                       # Documentation
@@ -68,56 +71,78 @@ cocoindex/
 
 ## Key Concepts
 
-### Mental model (state-reconcile engine)
+### Mental model: declarative data pipelines
 
-* **Declare desired state** (Target States) inside **Processing Components**; the engine **reconciles** external systems to match (create/update/delete/publish).
-* **Processing Components are long-lived instances** keyed by a stable path; individual *runs* are ephemeral.
-* Composition is **tree-shaped** (parent mounts children); diffs and external Actions are computed **per component** and applied atomically when possible.
+CocoIndex uses a **declarative** programming model — you specify *what* your output should look like (target states), not *how* to incrementally update it. The engine handles change detection and applies minimal updates automatically.
 
-### Core nouns
+Think of it like:
 
-* **Scope**: pure value that identifies a component instance and its place in the tree.
-* **Function**: a Python function decorated with `@coco.function` that can be called normally but gains tracking (deps, memoization, tracing).
-* **Processing Component**: a mounted instance of a Coco function at a specific **Scope**.
-* **Target State**: a **unit of desired external state** (e.g., a table, a table row, a blob, a message). The engine turns diffs into **Actions** (insert/update/delete/publish) to keep targets in sync.
-* **App**: bundles a top-level function and arguments; the top-level function is **mounted as the root component** each run.
-* **(Reserved) Context**: future React-style provider mechanism (typed keys; provide/use). Do **not** overload "Context" to mean Scope.
+* **React**: declare UI as function of state → React re-renders what changed
+* **Spreadsheets**: declare formulas → cells recompute when inputs change
+* **CocoIndex**: declare target states as function of source → engine syncs what changed
 
-### Canonical API shapes (free functions; Scope first)
+### Core concepts
+
+**App** — The top-level runnable unit. Bundles a main function with its arguments. When you call `app.update()`, the main function runs as the root processing component.
+
+**Processing Component** — The unit of execution that owns a set of target states. Created by `mount()` or `mount_run()` at a specific scope. When a component finishes, its target states sync atomically to external systems.
+
+**Scope** — Stable identifier for a processing component across runs (like a path in a tree: `scope / "process" / filename`). CocoIndex uses scopes to:
+
+* Match components to their previous runs for change detection
+* Determine ownership of target states (if a scope disappears, its target states are cleaned up)
+
+**Target State** — What you want to exist in an external system (a file, a database row, a table). You *declare* target states; CocoIndex keeps them in sync — creating, updating, or removing as needed.
+
+**Target** — The API object used to declare target states (e.g., `DirTarget`, `TableTarget`). Targets can be nested: a container target state (directory/table) provides a Target for declaring child target states (files/rows).
+
+**Function** — A Python function decorated with `@coco.function`. Use `memo=True` to enable memoization (skip execution when inputs and code are unchanged).
+
+**Context** — React-style provider mechanism for sharing resources. Define keys with `ContextKey[T]`, provide values in lifespan via `builder.provide()`, use in functions via `scope.use()`.
+
+### Key APIs
 
 ```python
-# Mounting & target states
-coco.mount(scope: Scope, fn, *args, **kw) -> ComponentHandle                # no data dependency
-coco.mount_run(scope: Scope, fn, *args, **kw) -> ComponentRunHandle[T]      # creates dependency; one up-to-date run
-coco.declare_target_state(scope: Scope, target_state: TargetState) -> None  # scope-owned external outcome
+# Mounting processing components
+coco.mount(fn, scope, *args, **kw)      # child runs independently, no data dependency
+coco.mount_run(fn, scope, *args, **kw)  # returns value, creates data dependency
 
-# Scope composition
+# Scope composition (stable identifiers)
 child_scope = scope / "setup"
-file_scope  = scope / "process" / (kind, arg)
+file_scope  = scope / "process" / filename
+
+# Declaring target states (typically via Target methods)
+dir_target.declare_file(scope, filename=name, content=data)
+table_target.declare_row(scope, row=MyRow(...))
 ```
 
-**Handles**
+**Mount handles:**
 
-* `ComponentHandle` (from `mount`): exposes `ready()` to wait (join) until the child is **FRESH** for the current epoch; **does not** create a parent→child data dependency.
-* `ComponentRunHandle[T]` (from `mount_run`): exposes a `result()` method to block on the result of the component, which creates a data dependency.
+* `mount()` → `ProcessingUnitMountHandle`: call `wait_until_ready()` to block until target states are synced
+* `mount_run()` → `ProcessingUnitMountRunHandle[T]`: call `result()` to get return value (implicitly waits)
 
-### Target States → Actions
+### How syncing works
 
-* "A **Target State** is a unit of desired external state. Users declare Target States; CocoIndex executes **Actions** on external systems to keep them in sync (inserts, updates, deletes, publishes)."
-* When a component re-runs, CocoIndex diffs **current run's declared Target States vs previous run's** at the same Scope and applies a **bundled change**.
+When a processing component finishes, CocoIndex compares its declared target states with those from the previous run at the same scope:
+
+* New target states → create (insert row, create file)
+* Changed target states → update
+* Missing target states → delete
+
+Changes are applied atomically per component. If a source item is deleted (scope no longer mounted), all its target states are cleaned up automatically.
 
 ### Example
 
 ```python
-@coco.function
+@coco.function(memo=True)
 def process_file(scope: coco.Scope, file: FileLike, target: localfs.DirTarget) -> None:
     html = _markdown_it.render(file.read_text())
     outname = "__".join(file.relative_path.parts) + ".html"
     target.declare_file(scope, filename=outname, content=html)
 
 @coco.function
 def app_main(scope: coco.Scope, sourcedir: pathlib.Path, outdir: pathlib.Path) -> None:
-    target = coco.mount_run(localfs.dir_target, scope / "setup", outdir).result()
+    target = coco.mount_run(localfs.declare_dir_target, scope / "setup", outdir).result()
 
     files = localfs.walk_dir(
         sourcedir, path_matcher=PatternFilePathMatcher(included_patterns=["*.md"])
PATCH

echo "Gold patch applied."
