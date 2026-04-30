#!/usr/bin/env bash
set -euo pipefail

cd /workspace/kubb

# Idempotency guard
if grep -qF "AGENTS.md" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -58,10 +58,8 @@ You have new skills. If any skill might be relevant then you MUST read it.
 
 - [changelog](.skills/changelog/SKILL.md) - Automatically creates user-facing changelogs from git commits by analyzing commit history, categorizing changes, and transforming technical commits into clear, customer-friendly release notes. Turns hours of manual changelog writing into minutes of automated generation.
 - [coding-style](.skills/coding-style/SKILL.md) - Coding style, testing, and PR guidelines for the Kubb ecosystem. Use when writing or reviewing code for the Kubb ecosystem.
-- [components-generators](.skills/components-generators/SKILL.md) - Guidance for writing `@kubb/renderer-jsx` components and generators (React-based and function-based).
 - [documentation](.skills/documentation/SKILL.md) - Use when writing blog posts or documentation markdown files - provides writing style guide (active voice, present tense), content structure patterns, and SEO optimization. Overrides brevity rules for proper grammar.
 - [jsdoc](.skills/jsdoc/SKILL.md) - Guidelines for writing minimal, high-quality JSDoc comments in TypeScript.
-- [plugin-architecture](.skills/plugin-architecture/SKILL.md) - Explains plugin lifecycle, generator types, and common utilities used by plugins in the Kubb ecosystem.
 - [pr](.skills/pr/SKILL.md) - Rules and checklist for preparing PRs, creating changesets, and releasing packages in the monorepo.
 - [testing](.skills/testing/SKILL.md) - Testing, CI, and troubleshooting guidance for running the repository's test suite and interpreting CI failures.
-  </skills>
+</skills>
PATCH

echo "Gold patch applied."
