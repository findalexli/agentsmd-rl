#!/usr/bin/env bash
set -euo pipefail

cd /workspace/focus-spec

# Idempotency guard
if grep -qF "* **Suggestion-first feedback:** When a concrete fix exists, post it as a GitHub" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -87,7 +87,7 @@ AI agents generating or reviewing content MUST act as strict technical editors e
 
 * Use BCP-14 keywords: MUST, MUST NOT, SHOULD, SHOULD NOT, MAY (all uppercase).
 * DO NOT use: "REQUIRED", "SHALL", "SHALL NOT", "RECOMMENDED", "OPTIONAL"
-* **Location:** Normative keywords MUST ONLY appear under a "Requirements" header. Flag any normative keywords leaking into "Description", "Examples", or other non-normative sections.
+* **Location:** In spec content, capitalized BCP-14 keywords MUST NOT appear outside "Requirements" sections unless quoted. Do not flag lowercase usage (e.g., "may", "should").
 * **Format:** Write normative statements as bullet lists, not lengthy sentences.
 * **Single Constraint:** Each normative bullet MUST express exactly one requirement. Do not combine multiple distinct obligations using "and"/"or", though these conjunctions are permitted within conditional clauses and mathematical validations.
 * **Conditional Phrasing:** Normative statements with conditions MUST use standard phrasing: "when / if / unless / only when / only if / except when / except if".
@@ -101,22 +101,50 @@ AI agents generating or reviewing content MUST act as strict technical editors e
 * **No Mixing:** Do not mix Entity IDs and Display Names within the same normative requirement.
 * **Column values:** Enclosed in double quotes (e.g., `"Usage"`, `"Tax"`).
 * **Glossary terms:** Link with `[*term*](#glossary:term)` format.
-* **Linking Rule:** First mention of Column/Attribute names and Glossary terms should link to their definition section. They MUST ONLY be hyperlinked the *first occurrence* per section.
+* **Linking Rule:** Link entity names and Glossary terms ONLY on their first occurrence per source file. Exception: Functional links using different anchor text are exempt.
 * **Lists:** All unordered lists MUST use asterisks (`*`), never dashes (`-`) or plus signs (`+`). Nested bullet points MUST use exactly two spaces per level.
 * **Notes:** Important notes must use the blockquote format (`> Important Consideration`).
+* **Anchors:** Pandoc auto-generates custom heading anchors. DO NOT flag missing HTML `<a name="">` tags.
 
 ### Validation & Schema Accuracy
 
 * **Mathematical & Schema Accuracy:** AI reviewers MUST rigorously calculate, parse, and verify all data within examples (especially JSON snippets and tables). Flag any mathematical inconsistencies or hallucinated data.
 * **JSON Formatting:** JSON blocks MUST use double quotation marks for keys. Verify that the JSON is structurally valid.
-* **Example Disclaimer:** Any section containing examples MUST include the exact warning note: `> Note: The following examples are informative and non-normative. They do not define requirements.`
+* **Example Disclaimer:** Top-level sections with examples MUST begin with this exact note (skip all subsections): `> Note: The following examples are informative and non-normative. They do not define requirements.`
 
 ### File Organization
 
 * Each section has a `.mdpp` template that includes individual `.md` files
 * All `.md` files in a directory must be included in the corresponding `.mdpp`
 * Code blocks must be aligned to start of line (not indented)
 
+### Review Conduct
+
+* **Suggestion-first feedback:** When a concrete fix exists, post it as a GitHub `suggestion` block so the author can accept with one click. Use plain-text comments only when the feedback requires discussion rather than a specific replacement.
+* **Self-contained comments:** Every review comment or suggestion MUST include all context needed for the author to evaluate it independently. Do not reference other comments (e.g., "same as above" or "see my comment on line X").
+* **Diff-scope discipline:** Only flag issues on lines changed or added by the PR. Pre-existing problems are out of scope unless they create a direct inconsistency with new content in the same PR.
+* **Deduplication:** If your tooling can read PR threads, do not flag already-raised issues or post competing suggestions. To add details, reply to the existing thread.
+
+### Issue and Pull Request Templates
+
+GitHub does not auto-apply templates when issues or PRs are created via API. AI agents MUST include the required template content in the body.
+
+#### Pull Requests
+
+PR bodies MUST complete `.github/pull_request_template.md`, including the summary, "Type of Change", and "Author Checklist" (with [AI Usage Guidelines](guidelines/contributors/ai-usage-guidelines.md) attestation).
+
+#### Issues
+
+Issue templates are `.yml` form definitions in `.github/ISSUE_TEMPLATE/`. Use the correct title prefix and fill all fields marked required in the template.
+
+| Type | Title Prefix | Template |
+|---|---|---|
+| Action Item | `[AI] ` | `action-item.yml` |
+| Feature Request | `[FR] ` | `feature-request.yml` |
+| Feedback | `[Feedback] ` | `feedback.yml` |
+| Maintenance | `[Maintenance] ` | `maintenance.yml` |
+| Work Item | `[WI]` | `work-item.yml` |
+
 ## Context Files
 
 ### Working Files
PATCH

echo "Gold patch applied."
