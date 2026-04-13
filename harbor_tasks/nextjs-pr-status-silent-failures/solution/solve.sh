#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'FAILED_CONCLUSIONS' scripts/pr-status.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Add "reject" to .alexrc allowed words (it's a technical term in JavaScript Promise context)
if [ -f .alexrc ] && ! grep -q '"reject"' .alexrc 2>/dev/null; then
  # Use sed to add "reject" to the allow array in .alexrc
  sed -i 's/"railway",/"railway",\n    "reject",/' .alexrc || true
fi

git apply - <<'PATCH'
diff --git a/scripts/pr-status.js b/scripts/pr-status.js
index 6440c7de1e43f9..eddf58b167c56e 100644
--- a/scripts/pr-status.js
+++ b/scripts/pr-status.js
@@ -216,6 +216,8 @@ function getRunMetadata(runId) {
   )
 }

+const FAILED_CONCLUSIONS = new Set(['failure', 'timed_out', 'startup_failure'])
+
 function getFailedJobs(runId) {
   // Fetch all jobs first, then filter for failures in JS.
   // We can't use jq filtering during pagination because a page full of
@@ -223,8 +225,8 @@ function getFailedJobs(runId) {
   // stop pagination before reaching later pages that contain failures.
   const allJobs = getAllJobs(runId)
   return allJobs
-    .filter((j) => j.conclusion === 'failure')
-    .map((j) => ({ id: j.id, name: j.name }))
+    .filter((j) => FAILED_CONCLUSIONS.has(j.conclusion))
+    .map((j) => ({ id: j.id, name: j.name, conclusion: j.conclusion }))
 }

 function getAllJobs(runId) {
@@ -235,11 +237,38 @@ function getAllJobs(runId) {
     const jqQuery =
       '.jobs[] | {id, name, status, conclusion, started_at, completed_at}'
     let output
-    try {
-      output = exec(
-        `gh api "repos/vercel/next.js/actions/runs/${runId}/jobs?per_page=100&page=${page}" --jq '${jqQuery}'`
+    let lastError
+    // Retry up to 3 times for transient API errors (e.g. HTTP 502)
+    for (let attempt = 1; attempt <= 3; attempt++) {
+      try {
+        output = exec(
+          `gh api "repos/vercel/next.js/actions/runs/${runId}/jobs?per_page=100&page=${page}" --jq '${jqQuery}'`
+        )
+        lastError = null
+        break
+      } catch (error) {
+        lastError = error
+        if (attempt < 3) {
+          const delay = attempt * 2000
+          console.error(
+            `API request failed (attempt ${attempt}/3), retrying in ${delay / 1000}s...`
+          )
+          execSync(`sleep ${delay / 1000}`)
+        }
+      }
+    }
+    if (lastError) {
+      // If all retries failed on the first page, we have no data at all — throw
+      // so callers know the fetch failed instead of silently returning [].
+      if (page === 1) {
+        throw new Error(
+          `Failed to fetch jobs for run ${runId} after 3 attempts: ${lastError.message}`
+        )
+      }
+      // For later pages we already have partial data; warn and return what we have
+      console.error(
+        `Warning: Failed to fetch page ${page} of jobs after 3 attempts. Returning ${allJobs.length} jobs from previous pages.`
       )
-    } catch {
       break
     }

@@ -261,7 +290,7 @@ function getAllJobs(runId) {

 function categorizeJobs(jobs) {
   return {
-    failed: jobs.filter((j) => j.conclusion === 'failure'),
+    failed: jobs.filter((j) => FAILED_CONCLUSIONS.has(j.conclusion)),
     inProgress: jobs.filter((j) => j.status === 'in_progress'),
     queued: jobs.filter((j) => j.status === 'queued'),
     succeeded: jobs.filter((j) => j.conclusion === 'success'),
@@ -634,8 +663,13 @@ function generateIndexMd(
       const testsStr = testCount
         ? `${testCount.failed}/${testCount.total}`
         : 'N/A'
+      const nameStr = escapeMarkdownTableCell(job.name)
+      const conclusionTag =
+        job.conclusion && job.conclusion !== 'failure'
+          ? ` (${job.conclusion})`
+          : ''
       lines.push(
-        `| ${job.id} | ${escapeMarkdownTableCell(job.name)} | ${duration} | ${testsStr} | [Details](job-${job.id}.md) |`
+        `| ${job.id} | ${nameStr}${conclusionTag} | ${duration} | ${testsStr} | [Details](job-${job.id}.md) |`
       )
     }
     lines.push('')
@@ -1056,7 +1090,7 @@ async function getFlakyTests(currentBranch, runsToCheck = 5) {
   )

   // Get recent failed build-and-test runs across ALL branches
-  const jqQuery = `.workflow_runs[] | select(.conclusion == "failure") | {id, head_branch}`
+  const jqQuery = `.workflow_runs[] | select(.conclusion == "failure" or .conclusion == "timed_out") | {id, head_branch}`
   let output
   try {
     output = exec(
@@ -1094,7 +1128,8 @@ async function getFlakyTests(currentBranch, runsToCheck = 5) {
   const runJobResults = await Promise.all(
     allRuns.map(async (run) => {
       try {
-        const jobsJq = '.jobs[] | select(.conclusion == "failure") | {id, name}'
+        const jobsJq =
+          '.jobs[] | select(.conclusion == "failure" or .conclusion == "timed_out" or .conclusion == "startup_failure") | {id, name}'
         const jobsOutput = exec(
           `gh api "repos/vercel/next.js/actions/runs/${run.id}/jobs?per_page=100" --jq '${jobsJq}'`
         )

PATCH

echo "Patch applied successfully."
