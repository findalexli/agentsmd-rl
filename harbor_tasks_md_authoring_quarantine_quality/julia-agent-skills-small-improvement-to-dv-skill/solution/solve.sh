#!/usr/bin/env bash
set -euo pipefail

cd /workspace/julia-agent-skills

# Idempotency guard
if grep -qF "The server starts at `http://localhost:SOMEPORT/` with hot reload.  The port num" "skills/documenter-vitepress/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/documenter-vitepress/SKILL.md b/skills/documenter-vitepress/SKILL.md
@@ -14,6 +14,7 @@ If the user needs to bootstrap or configure docs setup (dependencies, `make.jl`,
 This skill focuses on the day-to-day local iteration loop after setup already exists.
 
 The fast loop has two stages:
+
 1. Run `makedocs` to regenerate `build/.documenter/` content from `src/`.
 2. Run VitePress dev server via `dev_docs` to preview.
 
@@ -35,27 +36,30 @@ include("make.jl")
 ```
 
 Or from shell:
+
 - Standalone docs repo: `julia --project=. -e 'include("make.jl")'`
 - Package docs in `docs/`: `julia --project=docs -e 'include("docs/make.jl")'`
 
 ### Step 3: Start the dev server (background process)
 
 `dev_docs` is a long-running process and blocks the current task/thread. Start it in a non-blocking way:
 
-From shell:
+From shell (be sure to run this in the background):
+
 ```bash
 julia --project=. -e 'using DocumenterVitepress; DocumenterVitepress.dev_docs("build")'
 ```
 
-From Julia REPL:
+From Julia REPL / MCP tool:
+
 ```julia
 using DocumenterVitepress
 Threads.@spawn DocumenterVitepress.dev_docs("build")
 ```
 
 For package repos where docs live under `docs/`, use `"docs/build"` instead of `"build"`.
 
-The server starts at `http://localhost:5173/` with hot reload.
+The server starts at `http://localhost:SOMEPORT/` with hot reload.  The port number is reported in the output of the command.
 
 Gotcha: `dev_docs` expects the build directory path (for example, `build`), not `build/.documenter`. It appends `/.documenter` internally.
 
PATCH

echo "Gold patch applied."
