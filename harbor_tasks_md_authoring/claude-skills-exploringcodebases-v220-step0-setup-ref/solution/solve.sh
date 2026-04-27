#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-skills

# Idempotency guard
if grep -qF "REF=main                    # branch name, tag, or SHA. For a PR: pull/N/head" "exploring-codebases/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/exploring-codebases/SKILL.md b/exploring-codebases/SKILL.md
@@ -9,71 +9,91 @@ description: >-
   the divergent "what's here?" skill — for targeted "where is X?" queries,
   use searching-codebases instead.
 metadata:
-  version: 2.1.0
+  version: 2.2.0
 ---
 
 # Exploring Codebases
 
-Exploratory code analysis for unfamiliar repositories. This skill is a
-**workflow**, not a tool — it orchestrates tree-sitting (structural) and
-featuring (semantic) over a local copy of the repo.
+Exploratory code analysis for unfamiliar repositories. Orchestrates
+tree-sitting (structural) and featuring (semantic) over a local copy.
 
-## Dependencies
+## Workflow
+
+Five numbered steps, in order. Do not skip step 0.
 
-- **tree-sitting** — AST-powered code navigation (structural inventory)
-- **featuring** — Feature documentation generator (what/why layer)
+### 0. Setup (once per session)
 
 ```bash
 uv venv /home/claude/.venv 2>/dev/null
 uv pip install tree-sitter-language-pack --python /home/claude/.venv/bin/python
+export PYTHON=/home/claude/.venv/bin/python
+export TREESIT=/mnt/skills/user/tree-sitting/scripts/treesit.py
+export GATHER=/mnt/skills/user/featuring/scripts/gather.py
 ```
 
-## Workflow
-
-Four steps, in order. Do not skip step 1.
+If step 2's `--stats` later reports `Scanned 0 files ... Errors: 1`, the
+language pack isn't loaded — come back here and install. Treesit fails
+silently on missing deps; it does not raise a useful error.
 
 ### 1. Get the repo (tarball, not per-file)
 
 ```bash
-OWNER=... REPO=... REF=main
-curl -sL "https://api.github.com/repos/$OWNER/$REPO/tarball/$REF" -o /tmp/$REPO.tar.gz
+OWNER=...
+REPO=...
+REF=main                    # branch name, tag, or SHA. For a PR: pull/N/head
+curl -sL -H "Authorization: Bearer $GH_TOKEN" \
+  "https://api.github.com/repos/$OWNER/$REPO/tarball/$REF" -o /tmp/$REPO.tar.gz
 mkdir -p /tmp/$REPO && tar -xzf /tmp/$REPO.tar.gz -C /tmp/$REPO --strip-components=1
+ls /tmp/$REPO | head        # sanity check — did extraction land?
 ```
 
-One HTTP call gets the whole repo. Do NOT curl the README, cat individual
-files, or fetch via `contents/PATH` before this — they're all in the tarball.
-Every pre-tarball `curl`/`cat` on a file that's already in the repo is
-wasted tool budget.
+One HTTP call gets the whole repo. Do NOT curl README, cat files, or
+fetch via `contents/PATH` first — they're in the tarball. The
+Authorization header is only needed for private repos; public repos
+work without it.
 
-For private repos, add `-H "Authorization: Bearer $GH_TOKEN"`.
+**Ref selection matters.** If exploring a feature branch, PR, or tag,
+set `REF` accordingly. The default `main` will silently give you stale
+code if the question is about an unmerged branch.
 
-### 2. Tree-sitting (structural inventory)
+### 2. Structural scan
 
 ```bash
-TREESIT=/mnt/skills/user/tree-sitting/scripts/treesit.py
-PYTHON=/home/claude/.venv/bin/python
-
-# Structural overview — files, symbol counts, languages at depth=1
 $PYTHON $TREESIT /tmp/$REPO --stats
+```
 
-# Drill into interesting paths. BATCH queries in one call — each extra
-# query adds ~0ms on top of the scan cost. Separate invocations re-scan.
+Read the output. It gives file counts, symbol counts, languages, and
+per-directory symbol density. This IS the orienting artifact — treat it
+as the product of this step, not warm-up.
+
+**Drill only if you have a specific question.** For pure "what is this
+repo" exploration, skip drilling and go to step 3 — featuring surfaces
+the interesting paths for you. Drill when a user asked about a specific
+subsystem, or when step 3's output raises a question that needs source.
+
+When you do drill, BATCH queries in one call — each extra query adds
+~0ms, separate invocations re-scan from scratch:
+
+```bash
 $PYTHON $TREESIT /tmp/$REPO --path=SUBDIR --detail=full \
   'find:*Handler*:function' 'source:main' 'refs:Config'
 ```
 
-### 3. Featuring (feature synthesis)
+### 3. Feature synthesis
 
 ```bash
-$PYTHON /mnt/skills/user/featuring/scripts/gather.py /tmp/$REPO \
+$PYTHON $GATHER /tmp/$REPO \
   --skip tests,.github,node_modules --source-budget 8000
 ```
 
+Output includes a "Candidate areas for sub-files (by symbol density)"
+list near the top — that's your drill-target picker, ranked.
+
 ### 4. Reason about the combined output
 
-Synthesize steps 2+3 into understanding — identify capabilities, group symbols
-into features, write user-facing descriptions. Produce `_FEATURES.md` when
-warranted. This is the LLM step; everything before was mechanical.
+Synthesize 2+3: capabilities, feature groups, architecture, entry
+points, anomalies. Produce `_FEATURES.md` when warranted. This is the
+LLM step; everything before was mechanical.
 
 ## When to Use This vs Other Skills
 
@@ -86,15 +106,15 @@ warranted. This is the LLM step; everything before was mechanical.
 | "Document what this codebase does" | featuring directly |
 
 Exploring is the **divergent** skill — you don't know what you're looking
-for yet. Searching is the **convergent** skill — you know what you want,
-you need to find it.
+for yet. Searching is the **convergent** skill — you know what you want.
 
 ## Notes
 
-- **Scale**: For large repos (>100 files), use `--skip tests,vendored,docs,...`
-  in step 2 to focus the initial scan. Expand scope as needed.
-- **Monorepos**: Treat each package/service as a separate exploration.
+- **Large repos (>100 files)**: use `--skip tests,vendored,docs,...` in
+  step 2 to focus the scan.
+- **Monorepos**: treat each package/service as a separate exploration.
   Generate per-subsystem `_FEATURES.md` files linked from a root index.
-- **Drill heuristics** (for step 2): directories with high symbol count vs
-  file count (dense logic), entry-point patterns (`main`, `cli`, `app`,
-  `server`, `routes`), files with many imports (integration points).
+- **Drill heuristics** (if step 2 drilling is warranted): directories
+  with high symbol-to-file ratio (dense logic), entry-point names
+  (`main`, `cli`, `app`, `server`, `routes`), files with many imports
+  (integration points).
PATCH

echo "Gold patch applied."
