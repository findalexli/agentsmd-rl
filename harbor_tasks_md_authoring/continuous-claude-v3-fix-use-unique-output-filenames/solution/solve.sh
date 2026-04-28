#!/usr/bin/env bash
set -euo pipefail

cd /workspace/continuous-claude-v3

# Idempotency guard
if grep -qF "$CLAUDE_PROJECT_DIR/.claude/cache/agents/aegis/output-{timestamp}.md" ".claude/agents/aegis.md" && grep -qF "$CLAUDE_PROJECT_DIR/.claude/cache/agents/agentica-agent/output-{timestamp}.md" ".claude/agents/agentica-agent.md" && grep -qF "$CLAUDE_PROJECT_DIR/.claude/cache/agents/arbiter/output-{timestamp}.md" ".claude/agents/arbiter.md" && grep -qF "$CLAUDE_PROJECT_DIR/.claude/cache/agents/architect/output-{timestamp}.md" ".claude/agents/architect.md" && grep -qF "$CLAUDE_PROJECT_DIR/.claude/cache/agents/atlas/output-{timestamp}.md" ".claude/agents/atlas.md" && grep -qF "$CLAUDE_PROJECT_DIR/.claude/cache/agents/braintrust-analyst/output-{timestamp}.m" ".claude/agents/braintrust-analyst.md" && grep -qF "$CLAUDE_PROJECT_DIR/.claude/cache/agents/critic/output-{timestamp}.md" ".claude/agents/critic.md" && grep -qF "$CLAUDE_PROJECT_DIR/.claude/cache/agents/debug-agent/output-{timestamp}.md" ".claude/agents/debug-agent.md" && grep -qF "$CLAUDE_PROJECT_DIR/.claude/cache/agents/herald/output-{timestamp}.md" ".claude/agents/herald.md" && grep -qF "$CLAUDE_PROJECT_DIR/.claude/cache/agents/judge/output-{timestamp}.md" ".claude/agents/judge.md" && grep -qF "$CLAUDE_PROJECT_DIR/.claude/cache/agents/kraken/output-{timestamp}.md" ".claude/agents/kraken.md" && grep -qF "$CLAUDE_PROJECT_DIR/.claude/cache/agents/liaison/output-{timestamp}.md" ".claude/agents/liaison.md" && grep -qF "ORACLE_OUTPUT=$(ls -t .claude/cache/agents/oracle/output-*.md 2>/dev/null | head" ".claude/agents/maestro.md" && grep -qF "$CLAUDE_PROJECT_DIR/.claude/cache/agents/oracle/output-{timestamp}.md" ".claude/agents/oracle.md" && grep -qF "Write to `$CLAUDE_PROJECT_DIR/.claude/cache/agents/pathfinder/output-{timestamp}" ".claude/agents/pathfinder.md" && grep -qF "$CLAUDE_PROJECT_DIR/.claude/cache/agents/phoenix/output-{timestamp}.md" ".claude/agents/phoenix.md" && grep -qF "$CLAUDE_PROJECT_DIR/.claude/cache/agents/plan-agent/output-{timestamp}.md" ".claude/agents/plan-agent.md" && grep -qF "$CLAUDE_PROJECT_DIR/.claude/cache/agents/profiler/output-{timestamp}.md" ".claude/agents/profiler.md" && grep -qF "$CLAUDE_PROJECT_DIR/.claude/cache/agents/review-agent/output-{timestamp}.md" ".claude/agents/review-agent.md" && grep -qF "$CLAUDE_PROJECT_DIR/.claude/cache/agents/scout/output-{timestamp}.md" ".claude/agents/scout.md" && grep -qF "$CLAUDE_PROJECT_DIR/.claude/cache/agents/session-analyst/output-{timestamp}.md" ".claude/agents/session-analyst.md" && grep -qF "$CLAUDE_PROJECT_DIR/.claude/cache/agents/sleuth/output-{timestamp}.md" ".claude/agents/sleuth.md" && grep -qF "$CLAUDE_PROJECT_DIR/.claude/cache/agents/spark/output-{timestamp}.md" ".claude/agents/spark.md" && grep -qF "$CLAUDE_PROJECT_DIR/.claude/cache/agents/surveyor/output-{timestamp}.md" ".claude/agents/surveyor.md" && grep -qF "$CLAUDE_PROJECT_DIR/.claude/cache/agents/validate-agent/output-{timestamp}.md" ".claude/agents/validate-agent.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/agents/aegis.md b/.claude/agents/aegis.md
@@ -103,7 +103,7 @@ uv run python -m runtime.harness scripts/perplexity_ask.py \
 
 **ALWAYS write findings to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/aegis/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/aegis/output-{timestamp}.md
 ```
 
 ## Output Format
diff --git a/.claude/agents/agentica-agent.md b/.claude/agents/agentica-agent.md
@@ -180,7 +180,7 @@ class ResearchCoordinator:
 
 **ALWAYS write your implementation to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/agentica-agent/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/agentica-agent/output-{timestamp}.md
 ```
 
 Include:
diff --git a/.claude/agents/arbiter.md b/.claude/agents/arbiter.md
@@ -92,7 +92,7 @@ grep -r "def function_name" src/
 
 **ALWAYS write report to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/arbiter/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/arbiter/output-{timestamp}.md
 ```
 
 ## Output Format
diff --git a/.claude/agents/architect.md b/.claude/agents/architect.md
@@ -79,7 +79,7 @@ $CLAUDE_PROJECT_DIR/thoughts/shared/plans/[feature-name]-plan.md
 
 **Also write summary to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/architect/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/architect/output-{timestamp}.md
 ```
 
 ## Output Format
diff --git a/.claude/agents/atlas.md b/.claude/agents/atlas.md
@@ -120,7 +120,7 @@ cat test-results/*.json 2>/dev/null | head -100
 
 **ALWAYS write report to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/atlas/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/atlas/output-{timestamp}.md
 ```
 
 ## Output Format
diff --git a/.claude/agents/braintrust-analyst.md b/.claude/agents/braintrust-analyst.md
@@ -41,7 +41,7 @@ Other analyses (run as needed):
 
 **ALWAYS write your findings to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/braintrust-analyst/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/braintrust-analyst/output-{timestamp}.md
 ```
 
 Use Read-then-Write pattern:
diff --git a/.claude/agents/critic.md b/.claude/agents/critic.md
@@ -84,7 +84,7 @@ rp-cli -e 'structure src/'
 
 **ALWAYS write review to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/critic/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/critic/output-{timestamp}.md
 ```
 
 ## Output Format
diff --git a/.claude/agents/debug-agent.md b/.claude/agents/debug-agent.md
@@ -82,7 +82,7 @@ git log -p --all -S 'search_term' -- '*.ts'
 
 **ALWAYS write your findings to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/debug-agent/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/debug-agent/output-{timestamp}.md
 ```
 
 ## Output Format
diff --git a/.claude/agents/herald.md b/.claude/agents/herald.md
@@ -86,7 +86,7 @@ npm version <version> --no-git-tag-version
 
 **ALWAYS write release notes to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/herald/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/herald/output-{timestamp}.md
 ```
 
 **Also update:**
diff --git a/.claude/agents/judge.md b/.claude/agents/judge.md
@@ -77,7 +77,7 @@ npm test 2>&1 | tail -20
 
 **ALWAYS write review to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/judge/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/judge/output-{timestamp}.md
 ```
 
 ## Output Format
diff --git a/.claude/agents/kraken.md b/.claude/agents/kraken.md
@@ -107,7 +107,7 @@ uv run python -m runtime.harness scripts/morph_search.py --query "function_name"
 
 **ALWAYS write your summary to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/kraken/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/kraken/output-{timestamp}.md
 ```
 
 ## Output Format
diff --git a/.claude/agents/liaison.md b/.claude/agents/liaison.md
@@ -85,7 +85,7 @@ rp-cli -e 'search "retry|backoff|circuit|timeout"'
 
 **ALWAYS write review to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/liaison/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/liaison/output-{timestamp}.md
 ```
 
 ## Output Format
diff --git a/.claude/agents/maestro.md b/.claude/agents/maestro.md
@@ -111,15 +111,17 @@ After agents complete:
 
 ```bash
 # Read agent outputs
-cat .claude/cache/agents/scout/latest-output.md
-cat .claude/cache/agents/oracle/latest-output.md
+SCOUT_OUTPUT=$(ls -t .claude/cache/agents/scout/output-*.md 2>/dev/null | head -1)
+cat "$SCOUT_OUTPUT"
+ORACLE_OUTPUT=$(ls -t .claude/cache/agents/oracle/output-*.md 2>/dev/null | head -1)
+cat "$ORACLE_OUTPUT"
 ```
 
 ## Step 5: Write Output
 
 **ALWAYS write orchestration summary to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/maestro/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/maestro/output-{timestamp}.md
 ```
 
 ## Output Format
diff --git a/.claude/agents/oracle.md b/.claude/agents/oracle.md
@@ -103,7 +103,7 @@ uv run python -m runtime.harness scripts/llm_query.py \
 
 **ALWAYS write findings to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/oracle/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/oracle/output-{timestamp}.md
 ```
 
 ## Output Format
diff --git a/.claude/agents/pathfinder.md b/.claude/agents/pathfinder.md
@@ -47,7 +47,7 @@ rp-cli -e 'structure .'
 
 ## Step 3: Output
 
-Write to `$CLAUDE_PROJECT_DIR/.claude/cache/agents/pathfinder/latest-output.md`:
+Write to `$CLAUDE_PROJECT_DIR/.claude/cache/agents/pathfinder/output-{timestamp}.md`:
 
 ```markdown
 # Repository Analysis: [repo]
diff --git a/.claude/agents/phoenix.md b/.claude/agents/phoenix.md
@@ -88,7 +88,7 @@ $CLAUDE_PROJECT_DIR/thoughts/shared/plans/refactor-[target]-plan.md
 
 **Also write summary to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/phoenix/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/phoenix/output-{timestamp}.md
 ```
 
 ## Output Format
diff --git a/.claude/agents/plan-agent.md b/.claude/agents/plan-agent.md
@@ -70,7 +70,7 @@ uv run python -m runtime.harness scripts/morph_apply.py \
 
 **ALWAYS write your plan to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/plan-agent/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/plan-agent/output-{timestamp}.md
 ```
 
 Also copy to persistent location if plan should survive cache cleanup:
diff --git a/.claude/agents/profiler.md b/.claude/agents/profiler.md
@@ -109,7 +109,7 @@ hyperfine "uv run python script.py"
 
 **ALWAYS write findings to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/profiler/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/profiler/output-{timestamp}.md
 ```
 
 ## Output Format
diff --git a/.claude/agents/review-agent.md b/.claude/agents/review-agent.md
@@ -160,7 +160,7 @@ Note any concerns in the Gaps section.
 
 **ALWAYS write output to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/review-agent/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/review-agent/output-{timestamp}.md
 ```
 
 ### Output Format
diff --git a/.claude/agents/scout.md b/.claude/agents/scout.md
@@ -102,7 +102,7 @@ grep -rc "pattern" src/ | sort -t: -k2 -n -r | head -10
 
 **ALWAYS write findings to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/scout/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/scout/output-{timestamp}.md
 ```
 
 ## Output Format
diff --git a/.claude/agents/session-analyst.md b/.claude/agents/session-analyst.md
@@ -29,7 +29,7 @@ uv run python -m runtime.harness scripts/braintrust_analyze.py --last-session
 
 **ALWAYS write to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/session-analyst/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/session-analyst/output-{timestamp}.md
 ```
 
 ## Rules
diff --git a/.claude/agents/sleuth.md b/.claude/agents/sleuth.md
@@ -78,7 +78,7 @@ grep -A 10 "Traceback" logs/*.log
 
 **ALWAYS write findings to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/sleuth/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/sleuth/output-{timestamp}.md
 ```
 
 ## Output Format
diff --git a/.claude/agents/spark.md b/.claude/agents/spark.md
@@ -67,7 +67,7 @@ npx tsc --noEmit path/to/file.ts
 
 **Write summary to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/spark/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/spark/output-{timestamp}.md
 ```
 
 ## Output Format
diff --git a/.claude/agents/surveyor.md b/.claude/agents/surveyor.md
@@ -79,7 +79,7 @@ rp-cli -e 'search "TODO.*migration|FIXME.*upgrade"'
 
 **ALWAYS write review to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/surveyor/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/surveyor/output-{timestamp}.md
 ```
 
 ## Output Format
diff --git a/.claude/agents/validate-agent.md b/.claude/agents/validate-agent.md
@@ -73,7 +73,7 @@ Check for:
 
 **ALWAYS write your validation to:**
 ```
-$CLAUDE_PROJECT_DIR/.claude/cache/agents/validate-agent/latest-output.md
+$CLAUDE_PROJECT_DIR/.claude/cache/agents/validate-agent/output-{timestamp}.md
 ```
 
 Also write to handoff directory if provided:
PATCH

echo "Gold patch applied."
