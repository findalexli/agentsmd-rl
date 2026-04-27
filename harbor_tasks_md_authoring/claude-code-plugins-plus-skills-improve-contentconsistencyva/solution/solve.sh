#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-plugins-plus-skills

# Idempotency guard
if grep -qF "Checks content for tone, terminology, formatting, and structural consistency acr" "plugins/productivity/000-jeremy-content-consistency-validator/skills/000-jeremy-content-consistency-validator/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/productivity/000-jeremy-content-consistency-validator/skills/000-jeremy-content-consistency-validator/SKILL.md b/plugins/productivity/000-jeremy-content-consistency-validator/skills/000-jeremy-content-consistency-validator/SKILL.md
@@ -12,68 +12,80 @@ compatible-with: claude-code, codex, openclaw
 
 ## Overview
 
-Cross-platform content consistency auditing for organizations maintaining messaging across websites, GitHub repositories, and local documentation. This read-only skill discovers content sources, extracts key messaging elements, and generates severity-graded discrepancy reports -- without modifying any files.
+Checks content for tone, terminology, formatting, and structural consistency across multiple documentation sources (websites, GitHub repos, local docs). Generates read-only discrepancy reports with severity-classified findings and actionable fix suggestions including file paths and line numbers.
+
+## Examples
+
+- **Pre-release audit**: Before tagging a new version, run the validator to catch version mismatches between your README, docs site, and changelog — e.g., the website says v2.1.0 but the GitHub README still references v2.0.0.
+- **Post-rebrand check**: After renaming a product or updating terminology (e.g., "plugin" to "extension"), validate that all docs, landing pages, and contributing guides use the new term consistently.
+- **Onboarding review**: When a new contributor flags confusing docs, run a consistency check to surface contradictory feature claims, outdated contact info, or missing sections across your documentation sources.
 
 ## Prerequisites
 
 - Access to at least two content sources (website, GitHub repo, or local docs directory)
 - WebFetch permissions configured for remote URLs (deployed sites, GitHub raw content)
 - Local documentation stored in recognizable paths (`docs/`, `claudes-docs/`, `internal/`)
-- Grep and diff access for comparing extracted content fragments
 
 ## Instructions
 
-1. Discover all content sources by scanning for website build directories (e.g., `dist/`, `build/`, `public/`, `out/`, `_site/`), GitHub README/CONTRIBUTING files, and local documentation folders.
-2. Extract structured data from each source: version numbers, feature claims, product names, taglines, contact information, URLs, and technical requirements.
-3. Build a cross-source comparison matrix pairing each source against every other source (website vs GitHub, website vs local docs, GitHub vs local docs).
-4. Classify discrepancies by severity:
-   - **Critical**: conflicting version numbers, contradictory feature lists, mismatched contact info, broken cross-references.
-   - **Warning**: inconsistent terminology (e.g., "plugin" vs "extension"), missing information in one source, outdated dates.
-   - **Informational**: stylistic differences, platform-specific wording, differing detail levels.
-5. Apply trust priority when noting conflicts: website (most authoritative) > GitHub (developer-facing) > local docs (internal use).
-6. Generate the final Markdown report with executive summary, per-pair comparison tables, a terminology consistency matrix, and prioritized action items with file paths and line numbers.
-7. Save the report to `consistency-reports/YYYY-MM-DD-HH-MM-SS.md`.
-
-## Output
-
-- Markdown report containing:
-  - Executive summary with discrepancy counts grouped by severity
-  - Source-pair comparison sections (website vs GitHub, website vs local docs, GitHub vs local docs)
-  - Terminology consistency matrix showing term usage across all sources
-  - Prioritized action items with specific file locations, line numbers, and suggested corrections
-- Report file saved to `consistency-reports/` with timestamped filename
+1. **Discover sources** — scan for build directories (`dist/`, `build/`, `public/`, `out/`, `_site/`), GitHub README/CONTRIBUTING files, and local doc folders:
+   ```bash
+   find . -maxdepth 3 -name "README*" -o -name "CONTRIBUTING*" | head -20
+   ls -d docs/ claudes-docs/ internal/ 2>/dev/null
+   ```
+2. **Extract structured data** from each source: version numbers, feature claims, product names, taglines, contact info, URLs, and technical requirements:
+   ```bash
+   grep -rn 'v[0-9]\+\.[0-9]\+' docs/ README.md
+   grep -rn -i 'features\|capabilities' docs/ README.md
+   ```
+3. **Verify extraction** — confirm at least 3 data points per source. If a source returns empty, check the Error Handling table before continuing.
+4. **Build comparison matrix** pairing each source against every other (website vs GitHub, website vs local docs, GitHub vs local docs):
+   ```bash
+   diff <(grep -i 'version' README.md) <(grep -i 'version' docs/overview.md)
+   ```
+5. **Classify discrepancies** by severity:
+   - **Critical**: conflicting version numbers, contradictory feature lists, mismatched contact info, broken cross-references
+   - **Warning**: inconsistent terminology (e.g., "plugin" vs "extension"), missing information in one source, outdated dates
+   - **Informational**: stylistic differences, platform-specific wording, differing detail levels
+6. **Apply trust priority**: website (most authoritative) > GitHub (developer-facing) > local docs (internal use).
+7. **Generate report** as Markdown with: executive summary, per-pair comparison tables, terminology consistency matrix, and prioritized action items with file paths and line numbers.
+8. **Save** to `consistency-reports/YYYY-MM-DD-HH-MM-SS.md`.
+
+## Report Format
+
+```markdown
+# Consistency Report — YYYY-MM-DD
+
+## Executive Summary
+| Severity | Count |
+|----------|-------|
+| Critical | 2     |
+| Warning  | 5     |
+| Info     | 3     |
+
+## Website vs GitHub
+| Field        | Website       | GitHub        | Severity |
+|-------------|---------------|---------------|----------|
+| Version     | v2.1.0        | v2.0.0        | Critical |
+| Feature X   | listed        | missing       | Warning  |
+
+## Action Items
+1. **Critical** — Update `README.md:14` version from v2.0.0 → v2.1.0
+2. **Warning** — Add "Feature X" to `README.md` feature list
+```
 
 ## Error Handling
 
 | Error | Cause | Solution |
 |-------|-------|----------|
-| Website content unreachable | Deployed URL returns 4xx/5xx or local build directory missing | Verify the site is deployed or run the local build; check WebFetch permissions |
-| GitHub API rate limit exceeded | Too many raw content fetches in a short window | Pause and retry after the rate-limit reset window; use authenticated requests |
-| No documentation directory found | Expected paths (`docs/`, `claudes-docs/`) do not exist | Confirm correct working directory; specify the documentation path explicitly |
-| Empty content extraction | Source page uses client-side rendering not visible to fetch | Use a local build output directory instead of the live URL |
-| Diff command failure | File paths contain special characters | Quote all file paths passed to diff and grep commands |
-
-## Examples
-
-**Example 1: Pre-release version audit**
-- Scenario: A new version (v2.1.0) ships but internal training docs still reference v2.0.0.
-- Action: Run the validator across the website, GitHub README, and `docs/` directory.
-- Result: Report flags version mismatch as Critical, listing each file and line where the old version appears.
-
-**Example 2: Feature claim alignment after adding a new capability**
-- Scenario: The website announces "AI-powered search" but the GitHub README omits it.
-- Action: Validator extracts feature lists from both sources and compares.
-- Result: Warning-level discrepancy noting the missing feature mention in the GitHub README with a suggested addition.
-
-**Example 3: Terminology consistency check**
-- Scenario: The website uses "plugins" while local docs use "extensions" and GitHub uses "add-ons."
-- Action: Validator builds a terminology matrix across all three sources.
-- Result: Informational note with a recommendation to standardize on a single term, listing every occurrence.
+| Website content unreachable | URL returns 4xx/5xx or build dir missing | Verify site is deployed or run local build; check WebFetch permissions |
+| GitHub API rate limit | Too many fetches in short window | Pause and retry after reset window; use authenticated requests |
+| No documentation directory | Expected paths don't exist | Confirm working directory; specify doc path explicitly |
+| Empty content extraction | Client-side rendering not visible to fetch | Use local build output directory instead of live URL |
+| Diff command failure | File paths contain special characters | Quote all file paths passed to diff and grep |
 
 ## Resources
 
 - Content source discovery logic: `${CLAUDE_SKILL_DIR}/references/how-it-works.md`
-- Trust priority and validation timing guidance: `${CLAUDE_SKILL_DIR}/references/best-practices.md`
-- Concrete use-case walkthroughs: `${CLAUDE_SKILL_DIR}/references/example-use-cases.md`
-- YAML 1.2 specification (for config file validation): https://yaml.org/spec/
-- GitHub REST API documentation: https://docs.github.com/en/rest
\ No newline at end of file
+- Trust priority and validation timing: `${CLAUDE_SKILL_DIR}/references/best-practices.md`
+- Use-case walkthroughs: `${CLAUDE_SKILL_DIR}/references/example-use-cases.md`
PATCH

echo "Gold patch applied."
