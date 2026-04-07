#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mlflow

# Idempotent: skip if already applied
if grep -q 'RUN_URL_PATTERN' .claude/skills/src/skills/commands/analyze_ci.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.claude/skills/analyze-ci/SKILL.md b/.claude/skills/analyze-ci/SKILL.md
index ac39ca4d3cb8e..ef67d60df964f 100644
--- a/.claude/skills/analyze-ci/SKILL.md
+++ b/.claude/skills/analyze-ci/SKILL.md
@@ -19,6 +19,9 @@ This skill analyzes logs from failed GitHub Action jobs using Claude.
 # Analyze all failed jobs in a PR
 uv run skills analyze-ci <pr_url>

+# Analyze all failed jobs in a workflow run
+uv run skills analyze-ci <run_url>
+
 # Analyze specific job URLs directly
 uv run skills analyze-ci <job_url> [job_url ...]

@@ -34,6 +37,9 @@ Output: A concise failure summary with root cause, error messages, test names, a
 # Analyze CI failures for a PR
 uv run skills analyze-ci https://github.com/mlflow/mlflow/pull/19601

+# Analyze a specific workflow run
+uv run skills analyze-ci https://github.com/mlflow/mlflow/actions/runs/22626454465
+
 # Analyze specific job URLs directly
 uv run skills analyze-ci https://github.com/mlflow/mlflow/actions/runs/12345/job/67890
 ```
diff --git a/.claude/skills/src/skills/commands/analyze_ci.py b/.claude/skills/src/skills/commands/analyze_ci.py
index e614993531f35..8248b8e4fd3d3 100644
--- a/.claude/skills/src/skills/commands/analyze_ci.py
+++ b/.claude/skills/src/skills/commands/analyze_ci.py
@@ -131,6 +131,7 @@ def truncate_logs(logs: str, max_tokens: int = MAX_LOG_TOKENS) -> str:

 PR_URL_PATTERN = re.compile(r"github\.com/([^/]+/[^/]+)/pull/(\d+)")
 JOB_URL_PATTERN = re.compile(r"github\.com/([^/]+/[^/]+)/actions/runs/(\d+)/job/(\d+)")
+RUN_URL_PATTERN = re.compile(r"github\.com/([^/]+/[^/]+)/actions/runs/(\d+)$")


 async def get_failed_jobs_from_pr(
@@ -166,6 +167,14 @@ async def resolve_urls(client: GitHubClient, urls: list[str]) -> list[Job]:
             job_id = int(match.group(3))
             job = await client.get_job(owner, repo, job_id)
             jobs.append(job)
+        elif match := RUN_URL_PATTERN.search(url):
+            repo_full = match.group(1)
+            owner, repo = repo_full.split("/")
+            run_id = int(match.group(2))
+            run_jobs = [
+                j async for j in client.get_jobs(owner, repo, run_id) if j.conclusion == "failure"
+            ]
+            jobs.extend(run_jobs)
         elif match := PR_URL_PATTERN.search(url):
             repo_full = match.group(1)
             owner, repo = repo_full.split("/")
@@ -174,6 +183,7 @@ async def resolve_urls(client: GitHubClient, urls: list[str]) -> list[Job]:
         else:
             log(f"Error: Invalid URL: {url}")
             log("Expected PR URL (github.com/owner/repo/pull/123)")
+            log("Or workflow run URL (github.com/owner/repo/actions/runs/123)")
             log("Or job URL (github.com/owner/repo/actions/runs/123/job/456)")
             sys.exit(1)

@@ -311,7 +321,7 @@ async def cmd_analyze_async(urls: list[str], debug: bool = False) -> None:

 def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
     parser = subparsers.add_parser("analyze-ci", help="Analyze failed CI jobs")
-    parser.add_argument("urls", nargs="+", help="PR URL or job URL(s)")
+    parser.add_argument("urls", nargs="+", help="PR URL, workflow run URL, or job URL(s)")
     parser.add_argument("--debug", action="store_true", help="Show token/cost info")
     parser.set_defaults(func=run)

PATCH

echo "Patch applied successfully."
