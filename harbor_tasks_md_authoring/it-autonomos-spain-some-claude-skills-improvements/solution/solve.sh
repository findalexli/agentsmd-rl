#!/usr/bin/env bash
set -euo pipefail

cd /workspace/it-autonomos-spain

# Idempotency guard
if grep -qF ".claude/skills/tests-local-run-local-tests/SKILL.md" ".claude/skills/tests-local-run-local-tests/SKILL.md" && grep -qF "grep -oE 'id=\"[^\"]+\"' HTML_FILE | sed 's/id=\"//;s/\"$//' | grep -v -E '(-contact-" ".claude/skills/tests-local-test-and-update-internal-links/SKILL.md" && grep -qF ".claude/skills/tests-local-test-local-site-links/SKILL.md" ".claude/skills/tests-local-test-local-site-links/SKILL.md" && grep -qF ".claude/skills/tests-prod-run-prod-tests/SKILL.md" ".claude/skills/tests-prod-run-prod-tests/SKILL.md" && grep -qF ".claude/skills/tests-prod-test-bitly-links/SKILL.md" ".claude/skills/tests-prod-test-bitly-links/SKILL.md" && grep -qF ".claude/skills/tests-prod-test-prod-site-links/SKILL.md" ".claude/skills/tests-prod-test-prod-site-links/SKILL.md" && grep -qF ".claude/skills/tests-run-all-tests/SKILL.md" ".claude/skills/tests-run-all-tests/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/tests-local-run-local-tests/SKILL.md b/.claude/skills/tests-local-run-local-tests/SKILL.md
@@ -1,7 +1,6 @@
 ---
 name: tests-local-run-local-tests
 description: "Run all LOCAL validation checks that don't require network access to the live site."
-disable-model-invocation: true
 allowed-tools: Read, Glob, Grep, Bash, Task
 ---
 
diff --git a/.claude/skills/tests-local-test-and-update-internal-links/SKILL.md b/.claude/skills/tests-local-test-and-update-internal-links/SKILL.md
@@ -1,7 +1,6 @@
 ---
 name: tests-local-test-and-update-internal-links
 description: "Verify internal links database integrity and update with new pages/anchors."
-disable-model-invocation: true
 user-invocable: false
 allowed-tools: Read, Glob, Grep, Bash, Task, Edit
 ---
@@ -62,7 +61,7 @@ The following ID patterns are **excluded** from anchor tracking (technical IDs,
 
 | Pattern | Description |
 |---------|-------------|
-| `*-contact-form` | Contact form element IDs |
+| `*-contact-form*` | Contact form element IDs (including language-suffixed variants like `-contact-form-en`) |
 | `hs-script-loader` | HubSpot script loader ID |
 | UUID patterns | Auto-generated IDs like `f47ac10b-58cc-4372-a567-0e02b2c3d479` |
 
@@ -87,7 +86,7 @@ bundle exec jekyll build
    - Convert `path` to HTML file path
    - Extract anchors from HTML using:
      ```bash
-     grep -oE 'id="[^"]+"' HTML_FILE | sed 's/id="//;s/"$//' | grep -v -E '(-contact-form$|^hs-script-loader$|^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$)' | sort -u
+     grep -oE 'id="[^"]+"' HTML_FILE | sed 's/id="//;s/"$//' | grep -v -E '(-contact-form|^hs-script-loader$|^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$)' | sort -u
      ```
    - Compare with `anchors` array for that page
    - Identify NEW anchors (in HTML but not in database)
diff --git a/.claude/skills/tests-local-test-local-site-links/SKILL.md b/.claude/skills/tests-local-test-local-site-links/SKILL.md
@@ -1,7 +1,6 @@
 ---
 name: tests-local-test-local-site-links
 description: "Check all links and anchors on the LOCAL development server using lychee link checker."
-disable-model-invocation: true
 user-invocable: false
 allowed-tools: Read, Glob, Grep, Bash, Task
 ---
diff --git a/.claude/skills/tests-prod-run-prod-tests/SKILL.md b/.claude/skills/tests-prod-run-prod-tests/SKILL.md
@@ -1,7 +1,6 @@
 ---
 name: tests-prod-run-prod-tests
 description: "Run all PROD validation checks that require network access to the live site (itautonomos.com)."
-disable-model-invocation: true
 allowed-tools: Read, Glob, Grep, Bash, Task
 ---
 
diff --git a/.claude/skills/tests-prod-test-bitly-links/SKILL.md b/.claude/skills/tests-prod-test-bitly-links/SKILL.md
@@ -1,7 +1,6 @@
 ---
 name: tests-prod-test-bitly-links
 description: "Verify bit.ly shortlinks redirect correctly and check for untracked links on the site."
-disable-model-invocation: true
 user-invocable: false
 allowed-tools: Read, Glob, Grep, Bash, WebFetch, Task
 ---
diff --git a/.claude/skills/tests-prod-test-prod-site-links/SKILL.md b/.claude/skills/tests-prod-test-prod-site-links/SKILL.md
@@ -1,7 +1,6 @@
 ---
 name: tests-prod-test-prod-site-links
 description: "Check all links and anchors on the PROD website (itautonomos.com) using lychee link checker."
-disable-model-invocation: true
 user-invocable: false
 allowed-tools: Read, Glob, Grep, Bash, Task
 ---
diff --git a/.claude/skills/tests-run-all-tests/SKILL.md b/.claude/skills/tests-run-all-tests/SKILL.md
@@ -1,7 +1,6 @@
 ---
 name: tests-run-all-tests
 description: "Run all automated checks for the project (LOCAL + PROD) and provide a unified summary."
-disable-model-invocation: true
 allowed-tools: Read, Glob, Grep, Bash, Task
 ---
 
PATCH

echo "Gold patch applied."
