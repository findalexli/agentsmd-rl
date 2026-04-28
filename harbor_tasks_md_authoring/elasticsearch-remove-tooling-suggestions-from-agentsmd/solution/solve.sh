#!/usr/bin/env bash
set -euo pipefail

cd /workspace/elasticsearch

# Idempotency guard
if grep -qF "AGENTS.md" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -106,25 +106,4 @@ If you encounter any of the following methods, you must go and read their javado
 ## Backwards compatibility
 - For changes to a `Writeable` implementation (`writeTo` and constructor from `StreamInput`), add a new `public static final <UNIQUE_DESCRIPTIVE_NAME> = TransportVersion.fromName("<unique_descriptive_name>")` and use it in the new code paths. Confirm the backport branches and then generate a new version file with `./gradlew generateTransportVersion`.
 
-## CI failure triage with Buildkite and Gradle Enterprise build scans
-
-Prefer Gradle Enterprise build scans (`https://gradle-enterprise.elastic.co/s/<id>`) over raw logs for root-cause analysis when available.
-
-**Primary tool: `dvcli`.** Use it for root-cause analysis on Gradle Enterprise build scans (`https://gradle-enterprise.elastic.co/s/<id>`) whenever possible.
-It extracts failed tasks, exact failed tests, primary assertion/error, and reproduction details without requiring the agent to authenticate.
-
-1. If given a Gradle Enterprise build scan link directly, start from that link instead of searching Buildkite logs first.
-2. If given a Buildkite link, use the Buildkite MCP server to retrieve Gradle build scans.
-    - For Buildkite URLs that include `#<job_id>`, prioritize that specific job and resolve its corresponding `build-scan-<job_id>` entry.
-    - Otherwise call `buildkite-list_annotations` and inspect `context=gradle-build-scans-failed` (failed jobs only). If needed, inspect `context=gradle-build-scans` (all jobs).
-    - If annotations are incomplete, call `buildkite-get_build` and map failed job IDs to `meta_data` keys: `build-scan-<job_id>` and `build-scan-id-<job_id>`.
-    - Buildkite UI fallback (when MCP is unavailable): Build page -> `Jobs` -> `Failures`, then open/copy the Gradle Enterprise build scan links shown per failed job.
-3. Run `dvcli` against the resolved build scan link to extract failure details.
-    - If `dvcli` is unavailable, fall back to Buildkite MCP logs (`buildkite-search_logs`, `buildkite-tail_logs`, `buildkite-read_logs`), artifacts, and annotations.
-    - If either tool is missing, suggest installation to the user for faster future triage:
-        - `dvcli` / `develocity-cli-client`: `https://github.com/breskeby/develocity-cli-client`
-        - Buildkite MCP setup for AI tools: `https://buildkite.com/docs/apis/mcp-server/remote/configuring-ai-tools`
-
-In reports, list exact failed tests first, then failed tasks and related build scan URLs.
-
 Stay aligned with `CONTRIBUTING.md`, `BUILDING.md`, and `TESTING.asciidoc`; this AGENTS guide summarizes—but does not replace—those authoritative docs.
PATCH

echo "Gold patch applied."
