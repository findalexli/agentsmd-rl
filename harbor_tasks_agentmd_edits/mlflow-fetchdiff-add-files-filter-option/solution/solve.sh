#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mlflow

# Idempotent: skip if already applied
if grep -q 'file_patterns' .claude/skills/src/skills/commands/fetch_diff.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.claude/skills/fetch-diff/SKILL.md b/.claude/skills/fetch-diff/SKILL.md
index a4b3a255e4f4e..4e2169b71805a 100644
--- a/.claude/skills/fetch-diff/SKILL.md
+++ b/.claude/skills/fetch-diff/SKILL.md
@@ -12,13 +12,23 @@ Fetches a pull request diff, filters out auto-generated files, and adds line num
 ## Usage

 ```bash
-uv run skills fetch-diff <pr_url>
+uv run skills fetch-diff <pr_url> [--files <pattern> ...]
 ```

-Example:
+Examples:

 ```bash
+# Fetch the full diff
 uv run skills fetch-diff https://github.com/mlflow/mlflow/pull/123
+
+# Fetch only Python files
+uv run skills fetch-diff https://github.com/mlflow/mlflow/pull/123 --files '*.py'
+
+# Fetch only frontend files
+uv run skills fetch-diff https://github.com/mlflow/mlflow/pull/123 --files 'mlflow/server/js/*'
+
+# Multiple patterns
+uv run skills fetch-diff https://github.com/mlflow/mlflow/pull/123 --files '*.py' '*.ts'
 ```

 Token is auto-detected from `GH_TOKEN` env var or `gh auth token`.
diff --git a/.claude/skills/src/skills/commands/fetch_diff.py b/.claude/skills/src/skills/commands/fetch_diff.py
index f9dde7a48a645..e3c485031347b 100644
--- a/.claude/skills/src/skills/commands/fetch_diff.py
+++ b/.claude/skills/src/skills/commands/fetch_diff.py
@@ -5,6 +5,7 @@

 import argparse
 import asyncio
+import fnmatch
 import re
 import sys
 from pathlib import Path
@@ -61,7 +62,7 @@ def should_exclude_file(file_path: str) -> bool:
     return False


-def filter_diff(full_diff: str) -> str:
+def filter_diff(full_diff: str, file_patterns: list[str] | None = None) -> str:
     """Filter out excluded files and add line numbers to diff."""
     lines = full_diff.split("\n")
     filtered_diff: list[str] = []
@@ -71,7 +72,10 @@ def filter_diff(full_diff: str) -> str:
         if line.startswith("diff --git"):
             if match := re.match(r"diff --git a/(.*?) b/(.*?)$", line):
                 file_path = match.group(2)
-                if file_path == "dev/null":
+                if file_path == "dev/null" or (
+                    file_patterns
+                    and not any(fnmatch.fnmatch(file_path, pat) for pat in file_patterns)
+                ):
                     in_included_file = False
                 else:
                     in_included_file = not should_exclude_file(file_path)
@@ -114,7 +118,7 @@ def filter_diff(full_diff: str) -> str:
     return "\n".join(result_lines)


-async def fetch_diff(pr_url: str) -> str:
+async def fetch_diff(pr_url: str, file_patterns: list[str] | None = None) -> str:
     owner, repo, pr_number = parse_pr_url(pr_url)

     async with GitHubClient() as client:
@@ -131,15 +135,20 @@ async def fetch_diff(pr_url: str) -> str:
         else:
             diff = await client.get_pr_diff(owner, repo, pr_number)

-    return filter_diff(diff)
+    return filter_diff(diff, file_patterns)


 def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
     parser = subparsers.add_parser("fetch-diff", help="Fetch PR diff with line numbers")
     parser.add_argument("pr_url", help="GitHub PR URL")
+    parser.add_argument(
+        "--files",
+        nargs="+",
+        help="Glob patterns to filter files (e.g. '*.py' 'mlflow/server/*')",
+    )
     parser.set_defaults(func=run)


 def run(args: argparse.Namespace) -> None:
-    result = asyncio.run(fetch_diff(args.pr_url))
+    result = asyncio.run(fetch_diff(args.pr_url, args.files))
     print(result)

PATCH

echo "Patch applied successfully."
