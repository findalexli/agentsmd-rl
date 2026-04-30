#!/usr/bin/env bash
set -euo pipefail

cd /workspace/autoskill

# Idempotency guard
if grep -qF "Omit any empty section. Order: breaking changes, features, improvements, fixes, " "SkillBank/Common/AwesomeClaudeSkills/changelog-generator/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SkillBank/Common/AwesomeClaudeSkills/changelog-generator/SKILL.md b/SkillBank/Common/AwesomeClaudeSkills/changelog-generator/SKILL.md
@@ -1,104 +1,89 @@
 ---
-id: "33592803-d4c8-588e-986d-3af88145dbd5"
 name: changelog-generator
-description: Automatically creates user-facing changelogs from git commits by analyzing commit history, categorizing changes, and transforming technical commits into clear, customer-friendly release notes. Turns hours of manual changelog writing into minutes of automated generation.
+description: >-
+  Generates user-facing changelogs and release notes from git commit history.
+  Parses conventional commits, categorizes changes into features, fixes,
+  breaking changes, and more, then rewrites technical messages into
+  customer-friendly language. Use when the user asks to generate a changelog,
+  write release notes, summarize recent commits, prepare CHANGELOG.md, or
+  document what changed between versions.
 ---
 
 # Changelog Generator
 
-This skill transforms technical git commits into polished, user-friendly changelogs that your customers and users will actually understand and appreciate.
+Generate structured, user-facing changelogs from git commit history.
 
-## When to Use This Skill
+## Workflow
 
-- Preparing release notes for a new version
-- Creating weekly or monthly product update summaries
-- Documenting changes for customers
-- Writing changelog entries for app store submissions
-- Generating update notifications
-- Creating internal release documentation
-- Maintaining a public changelog/product updates page
+### Step 1 — Gather commits
 
-## What This Skill Does
+Determine the commit range from the user's request, then fetch commits:
 
-1. **Scans Git History**: Analyzes commits from a specific time period or between versions
-2. **Categorizes Changes**: Groups commits into logical categories (features, improvements, bug fixes, breaking changes, security)
-3. **Translates Technical → User-Friendly**: Converts developer commits into customer language
-4. **Formats Professionally**: Creates clean, structured changelog entries
-5. **Filters Noise**: Excludes internal commits (refactoring, tests, etc.)
-6. **Follows Best Practices**: Applies changelog guidelines and your brand voice
-
-## How to Use
-
-### Basic Usage
-
-From your project repository:
-
-```
-Create a changelog from commits since last release
+```bash
+# Between tags/versions
+git log v1.2.0..v1.3.0 --oneline --no-merges
+# Since a date
+git log --since="2024-03-01" --oneline --no-merges
+# Since last tag (default when no range given)
+git log "$(git describe --tags --abbrev=0)"..HEAD --oneline --no-merges
 ```
 
-```
-Generate changelog for all commits from the past week
-```
+If there are no tags and no range specified, ask the user for a date or count.
 
-```
-Create release notes for version 2.5.0
-```
+### Step 2 — Categorize each commit
 
-### With Specific Date Range
+Apply these rules based on the commit message prefix:
 
-```
-Create a changelog for all commits between March 1 and March 15
-```
+| Prefix / pattern | Category |
+|---|---|
+| `feat:` `feature:` | New Features |
+| `fix:` `bugfix:` | Bug Fixes |
+| `perf:` | Performance |
+| `BREAKING CHANGE` or `!:` suffix | Breaking Changes |
+| `security:` `vuln:` | Security |
+| `docs:` `test:` `ci:` `chore:` `refactor:` `style:` `build:` | Skip (internal) |
 
-### With Custom Guidelines
+For non-conventional messages, infer category from content. Exclude purely internal commits (test infra, CI config, linting, dependency bumps with no user impact).
 
-```
-Create a changelog for commits since v2.4.0, using my changelog 
-guidelines from CHANGELOG_STYLE.md
-```
+### Step 3 — Rewrite for a non-technical audience
 
-## Example
+Transform each kept commit into a clear, benefit-focused sentence:
 
-**User**: "Create a changelog for commits from the past 7 days"
+- Strip scope tags like `(api):` or `(auth):`
+- Expand abbreviations and jargon
+- Lead with the user-visible outcome, not the implementation
+- Use present tense: "Add", "Fix", "Improve"
+- One sentence per entry
 
-**Output**:
-```markdown
-# Updates - Week of March 10, 2024
+Example: `fix(auth): race condition in token refresh` becomes
+"Fix an issue where sessions could expire unexpectedly during use."
 
-## ✨ New Features
+### Step 4 — Format the output
 
-- **Team Workspaces**: Create separate workspaces for different 
-  projects. Invite team members and keep everything organized.
+```markdown
+# Changelog — vX.Y.Z (YYYY-MM-DD)
 
-- **Keyboard Shortcuts**: Press ? to see all available shortcuts. 
-  Navigate faster without touching your mouse.
+## Breaking Changes
+- [entry]
 
-## 🔧 Improvements
+## New Features
+- [entry]
 
-- **Faster Sync**: Files now sync 2x faster across devices
-- **Better Search**: Search now includes file contents, not just titles
+## Improvements
+- [entry]
 
-## 🐛 Fixes
+## Bug Fixes
+- [entry]
 
-- Fixed issue where large images wouldn't upload
-- Resolved timezone confusion in scheduled posts
-- Corrected notification badge count
+## Security
+- [entry]
 ```
 
-**Inspired by:** Manik Aggarwal's use case from Lenny's Newsletter
-
-## Tips
-
-- Run from your git repository root
-- Specify date ranges for focused changelogs
-- Use your CHANGELOG_STYLE.md for consistent formatting
-- Review and adjust the generated changelog before publishing
-- Save output directly to CHANGELOG.md
+Omit any empty section. Order: breaking changes, features, improvements, fixes, security. If the repo already has a `CHANGELOG.md` or `CHANGELOG_STYLE.md`, match its existing conventions instead.
 
-## Related Use Cases
+### Step 5 — Validate before presenting
 
-- Creating GitHub release notes
-- Writing app store update descriptions
-- Generating email updates for users
-- Creating social media announcement posts
+1. Confirm no internal-only commits leaked through
+2. Confirm every entry is understandable without reading source code
+3. Confirm date and version label are correct
+4. Write to `CHANGELOG.md` (prepend above existing content) or print inline, based on the user's request
PATCH

echo "Gold patch applied."
