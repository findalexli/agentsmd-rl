#!/usr/bin/env bash
set -euo pipefail

cd /workspace/worktrunk

# Idempotency guard
if grep -qF "running `wt-perf cache-check` against a real `wt list statusline --claude-code`" ".claude/skills/running-tend/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/running-tend/SKILL.md b/.claude/skills/running-tend/SKILL.md
@@ -133,6 +133,40 @@ Files to update:
 After bumping, run the full test suite (`cargo run -- hook pre-merge --yes`)
 and verify `cargo msrv verify` passes.
 
+## Weekly Maintenance: Statusline Cache-Check
+
+Detect new in-process cache-miss duplicates introduced by recent changes by
+running `wt-perf cache-check` against a real `wt list statusline --claude-code`
+trace. The render runs on every Claude Code prompt redraw, so duplicate git
+subprocesses there compound into measurable fseventsd / IPC load.
+
+```bash
+# Run from any worktree of this repo
+cat > /tmp/statusline-input.json <<'EOF'
+{"hook_event_name":"Status","workspace":{"current_dir":"REPLACE_WITH_CWD"},
+ "model":{"display_name":"Opus"},"context_window":{"used_percentage":42.0}}
+EOF
+sed -i '' "s|REPLACE_WITH_CWD|$PWD|" /tmp/statusline-input.json
+
+RUST_LOG=debug cargo run --release -- list statusline --claude-code \
+  < /tmp/statusline-input.json 2>&1 \
+  | grep wt-trace \
+  | cargo run -p wt-perf -- cache-check
+```
+
+The report flags commands invoked more than once with the same context.
+Triage each duplicate:
+
+- **Legitimate** (different cwd, different ref form that can't be normalized,
+  intentional double-call across phases) — note in the response and move on.
+- **Cache miss** (same logical operation should hit cache but doesn't) —
+  open an issue or fix it. Past examples: `merge_base("main", "<sha>")` vs
+  `merge_base("main", "branch")` keying separately;
+  `worktree_at(cwd)` vs `worktree_at(porcelain_path)` not canonicalizing.
+
+Baseline as of 2026-04-13: 29 git subprocesses per render on a clean tree
+(see PR #2209). A jump above ~32 on a clean tree warrants investigation.
+
 ## README Date Check
 
 The README blockquote opens with a month+year (e.g., "**April 2026**"). During daily
PATCH

echo "Gold patch applied."
