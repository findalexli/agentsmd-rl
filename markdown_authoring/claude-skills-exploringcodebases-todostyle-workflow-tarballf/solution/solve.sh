#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-skills

# Idempotency guard
if grep -qF "curl -sL \"https://api.github.com/repos/$OWNER/$REPO/tarball/$REF\" -o /tmp/$REPO." "exploring-codebases/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/exploring-codebases/SKILL.md b/exploring-codebases/SKILL.md
@@ -9,14 +9,14 @@ description: >-
   the divergent "what's here?" skill — for targeted "where is X?" queries,
   use searching-codebases instead.
 metadata:
-  version: 2.0.0
+  version: 2.1.0
 ---
 
 # Exploring Codebases
 
 Exploratory code analysis for unfamiliar repositories. This skill is a
 **workflow**, not a tool — it orchestrates tree-sitting (structural) and
-featuring (semantic) into a progressive disclosure sequence.
+featuring (semantic) over a local copy of the repo.
 
 ## Dependencies
 
@@ -30,67 +30,50 @@ uv pip install tree-sitter-language-pack --python /home/claude/.venv/bin/python
 
 ## Workflow
 
-```bash
-TREESIT=/mnt/skills/user/tree-sitting/scripts/treesit.py
-PYTHON=/home/claude/.venv/bin/python
-```
-
-### Phase 1: Structural Orientation
+Four steps, in order. Do not skip step 1.
 
-Get oriented — what's here, how big, what languages?
+### 1. Get the repo (tarball, not per-file)
 
 ```bash
-$PYTHON $TREESIT /path/to/repo --stats
+OWNER=... REPO=... REF=main
+curl -sL "https://api.github.com/repos/$OWNER/$REPO/tarball/$REF" -o /tmp/$REPO.tar.gz
+mkdir -p /tmp/$REPO && tar -xzf /tmp/$REPO.tar.gz -C /tmp/$REPO --strip-components=1
 ```
 
-Default depth=1 shows root-level files and one level of subdirectories
-with file counts, symbol counts, and languages. Takes ~700ms total
-(scan + output).
+One HTTP call gets the whole repo. Do NOT curl the README, cat individual
+files, or fetch via `contents/PATH` before this — they're all in the tarball.
+Every pre-tarball `curl`/`cat` on a file that's already in the repo is
+wasted tool budget.
 
-### Phase 2: Drill Into Structure
+For private repos, add `-H "Authorization: Bearer $GH_TOKEN"`.
 
-Follow what looks interesting. Each call auto-scans — no state to manage.
+### 2. Tree-sitting (structural inventory)
 
 ```bash
-# Drill into a directory with full detail (signatures, docs, children, imports)
-$PYTHON $TREESIT /path/to/repo --path=src/core --detail=full
+TREESIT=/mnt/skills/user/tree-sitting/scripts/treesit.py
+PYTHON=/home/claude/.venv/bin/python
 
-# Search for patterns across the codebase
-$PYTHON $TREESIT /path/to/repo 'find:*Handler*:function'
+# Structural overview — files, symbol counts, languages at depth=1
+$PYTHON $TREESIT /tmp/$REPO --stats
 
-# Read a specific implementation
-$PYTHON $TREESIT /path/to/repo --no-tree 'source:handle_request'
+# Drill into interesting paths. BATCH queries in one call — each extra
+# query adds ~0ms on top of the scan cost. Separate invocations re-scan.
+$PYTHON $TREESIT /tmp/$REPO --path=SUBDIR --detail=full \
+  'find:*Handler*:function' 'source:main' 'refs:Config'
 ```
 
-**Heuristics for what to drill into first:**
-- Directories with high symbol counts relative to file counts (dense logic)
-- Entry point patterns: `main`, `cli`, `app`, `server`, `routes`, `handler`
-- Files with many imports (integration points)
-- The root directory's top-level files (often config + entry points)
-
-### Phase 3: Feature Synthesis (featuring)
-
-Once you understand the structure, generate the "what does it DO?" layer:
+### 3. Featuring (feature synthesis)
 
 ```bash
-$PYTHON /mnt/skills/user/featuring/scripts/gather.py /path/to/repo \
+$PYTHON /mnt/skills/user/featuring/scripts/gather.py /tmp/$REPO \
   --skip tests,.github,node_modules --source-budget 8000
 ```
 
-Read the gather output, then synthesize `_FEATURES.md` following the featuring
-skill's format. This is the LLM step — identify capabilities, group symbols
-into features, write user-facing descriptions.
+### 4. Reason about the combined output
 
-### Phase 4: Targeted Deep Dives
-
-With structural inventory + feature map in hand, read specific implementations
-where the feature narrative needs verification or behavior isn't clear:
-
-```bash
-$PYTHON $TREESIT /path/to/repo --no-tree 'source:authenticate' 'refs:AuthToken'
-```
-
-Multiple queries in one call — each adds ~0ms on top of the scan cost.
+Synthesize steps 2+3 into understanding — identify capabilities, group symbols
+into features, write user-facing descriptions. Produce `_FEATURES.md` when
+warranted. This is the LLM step; everything before was mechanical.
 
 ## When to Use This vs Other Skills
 
@@ -106,19 +89,12 @@ Exploring is the **divergent** skill — you don't know what you're looking
 for yet. Searching is the **convergent** skill — you know what you want,
 you need to find it.
 
-## Output
-
-The exploration produces understanding, not necessarily files. But the
-concrete artifacts, when warranted, are:
-
-- `_FEATURES.md` — top-down feature documentation (via featuring)
-- Mental model of codebase structure, entry points, and architecture
-
-## Scaling
-
-For large repos (>100 files), use `--skip` aggressively in Phase 1 to
-exclude tests, vendored code, generated files, and docs. Focus the initial
-scan on `--path=src` or the primary source directory. Expand scope as needed.
+## Notes
 
-For monorepos, treat each package/service as a separate exploration.
-Generate per-subsystem `_FEATURES.md` files linked from a root index.
+- **Scale**: For large repos (>100 files), use `--skip tests,vendored,docs,...`
+  in step 2 to focus the initial scan. Expand scope as needed.
+- **Monorepos**: Treat each package/service as a separate exploration.
+  Generate per-subsystem `_FEATURES.md` files linked from a root index.
+- **Drill heuristics** (for step 2): directories with high symbol count vs
+  file count (dense logic), entry-point patterns (`main`, `cli`, `app`,
+  `server`, `routes`), files with many imports (integration points).
PATCH

echo "Gold patch applied."
