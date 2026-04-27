#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cocoindex

# Idempotency guard
if grep -qF "**Processing Component** \u2014 The unit of execution that owns a set of target state" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -56,7 +56,7 @@ cocoindex/
 │   │   │   ├── context_keys.py # ContextKey and ContextProvider
 │   │   │   ├── environment.py  # Environment and lifespan handling
 │   │   │   ├── function.py     # @coco.function decorator implementation
-│   │   │   ├── scope.py        # Scope implementation
+│   │   │   ├── component_ctx.py # ComponentContext and component_subpath
 │   │   │   └── target_state.py # Target state implementation
 │   │   ├── connectors/         # External system connectors (localfs, postgres, qdrant, lancedb, google_drive)
 │   │   ├── connectorkits/      # Connector building utilities
@@ -85,35 +85,49 @@ Think of it like:
 
 **App** — The top-level runnable unit. Bundles a main function with its arguments. When you call `app.update()`, the main function runs as the root processing component.
 
-**Processing Component** — The unit of execution that owns a set of target states. Created by `mount()` or `mount_run()` at a specific scope. When a component finishes, its target states sync atomically to external systems.
+**Processing Component** — The unit of execution that owns a set of target states. Created by `mount()` or `mount_run()` at a specific component path. When a component finishes, its target states sync atomically to external systems.
 
-**Scope** — Stable identifier for a processing component across runs (like a path in a tree: `scope / "process" / filename`). CocoIndex uses scopes to:
+**Component Path** — Stable identifier for a processing component across runs. Created via `coco.component_subpath("process", filename)`. CocoIndex uses component paths to:
 
 * Match components to their previous runs for change detection
-* Determine ownership of target states (if a scope disappears, its target states are cleaned up)
+* Determine ownership of target states (if a path disappears, its target states are cleaned up)
 
 **Target State** — What you want to exist in an external system (a file, a database row, a table). You *declare* target states; CocoIndex keeps them in sync — creating, updating, or removing as needed.
 
 **Target** — The API object used to declare target states (e.g., `DirTarget`, `TableTarget`). Targets can be nested: a container target state (directory/table) provides a Target for declaring child target states (files/rows).
 
 **Function** — A Python function decorated with `@coco.function`. Use `memo=True` to enable memoization (skip execution when inputs and code are unchanged).
 
-**Context** — React-style provider mechanism for sharing resources. Define keys with `ContextKey[T]`, provide values in lifespan via `builder.provide()`, use in functions via `scope.use()`.
+**Context** — React-style provider mechanism for sharing resources. Define keys with `ContextKey[T]`, provide values in lifespan via `builder.provide()`, use in functions via `coco.use_context(key)`.
 
 ### Key APIs
 
 ```python
-# Mounting processing components
-coco.mount(fn, scope, *args, **kw)      # child runs independently, no data dependency
-coco.mount_run(fn, scope, *args, **kw)  # returns value, creates data dependency
+# Mounting processing components (subpath first, then function)
+coco.mount(coco.component_subpath("name"), fn, *args, **kw)      # child runs independently
+coco.mount_run(coco.component_subpath("name"), fn, *args, **kw)  # returns value, creates dependency
 
-# Scope composition (stable identifiers)
-child_scope = scope / "setup"
-file_scope  = scope / "process" / filename
+# Component subpath composition
+subpath = coco.component_subpath("process", filename)  # multiple parts
+subpath = coco.component_subpath("a") / "b" / "c"      # chaining with /
+
+# Using component_subpath as context manager (applies to all nested mount calls)
+with coco.component_subpath("process"):
+    for f in files:
+        coco.mount(coco.component_subpath(str(f.relative_path)), process_file, f, target)
 
 # Declaring target states (typically via Target methods)
-dir_target.declare_file(scope, filename=name, content=data)
-table_target.declare_row(scope, row=MyRow(...))
+dir_target.declare_file(filename=name, content=data)
+table_target.declare_row(row=MyRow(...))
+
+# Using context values
+db = coco.use_context(PG_DB)  # retrieve value provided in lifespan
+
+# Explicit context management (for ThreadPoolExecutor)
+ctx = coco.get_component_context()
+with ctx.attach():
+    # coco APIs work correctly in this thread
+    coco.mount(...)
 ```
 
 **Mount handles:**
@@ -123,37 +137,40 @@ table_target.declare_row(scope, row=MyRow(...))
 
 ### How syncing works
 
-When a processing component finishes, CocoIndex compares its declared target states with those from the previous run at the same scope:
+When a processing component finishes, CocoIndex compares its declared target states with those from the previous run at the same component path:
 
 * New target states → create (insert row, create file)
 * Changed target states → update
 * Missing target states → delete
 
-Changes are applied atomically per component. If a source item is deleted (scope no longer mounted), all its target states are cleaned up automatically.
+Changes are applied atomically per component. If a source item is deleted (path no longer mounted), all its target states are cleaned up automatically.
 
 ### Example
 
 ```python
 @coco.function(memo=True)
-def process_file(scope: coco.Scope, file: FileLike, target: localfs.DirTarget) -> None:
+def process_file(file: FileLike, target: localfs.DirTarget) -> None:
     html = _markdown_it.render(file.read_text())
     outname = "__".join(file.relative_path.parts) + ".html"
-    target.declare_file(scope, filename=outname, content=html)
+    target.declare_file(filename=outname, content=html)
 
 @coco.function
-def app_main(scope: coco.Scope, sourcedir: pathlib.Path, outdir: pathlib.Path) -> None:
-    target = coco.mount_run(localfs.declare_dir_target, scope / "setup", outdir).result()
+def app_main(sourcedir: pathlib.Path, outdir: pathlib.Path) -> None:
+    target = coco.mount_run(
+        coco.component_subpath("setup"), localfs.declare_dir_target, outdir
+    ).result()
 
     files = localfs.walk_dir(
         sourcedir, path_matcher=PatternFilePathMatcher(included_patterns=["*.md"])
     )
-    for f in files:
-        coco.mount(process_file, scope / "process" / str(f.relative_path), f, target)
+    with coco.component_subpath("process"):
+        for f in files:
+            coco.mount(coco.component_subpath(str(f.relative_path)), process_file, f, target)
 
 
 app = coco.App(
-    app_main,
     coco.AppConfig(name="FilesTransform"),
+    app_main,
     sourcedir=pathlib.Path("./docs"),
     outdir=pathlib.Path("./out"),
 )
PATCH

echo "Gold patch applied."
