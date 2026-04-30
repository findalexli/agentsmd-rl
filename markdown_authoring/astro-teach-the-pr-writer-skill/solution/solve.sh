#!/usr/bin/env bash
set -euo pipefail

cd /workspace/astro

# Idempotency guard
if grep -qF "**New features (minor)** \u2014 start with \"Adds\", name the new API, and describe wha" ".agents/skills/astro-pr-writer/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/astro-pr-writer/SKILL.md b/.agents/skills/astro-pr-writer/SKILL.md
@@ -101,9 +101,95 @@ Explain docs impact clearly.
 - Add detail only when it helps reviewer understanding.
 - Avoid repeating the same point across sections.
 
+## Changesets
+
+Every PR that modifies a package requires a changeset file. Only `examples/*` changes are exempt.
+
+### Format
+
+Create `.changeset/<descriptive-slug>.md` with YAML front matter listing affected packages and bump type, followed by a plain-text description that becomes the changelog entry:
+
+```md
+---
+'astro': patch
+---
+
+Fixes a case where fonts files would unnecessarily be copied several times during the build
+```
+
+- Package names must match the `name` field in the package's `package.json` exactly (e.g., `'astro'`, `'@astrojs/node'`)
+- Bump types: `patch`, `minor`, or `major`
+- A single changeset file can cover multiple packages
+- `major` and `minor` bumps to the core `astro` package are blocked by CI and require maintainer review
+
+### Writing the Changeset Message
+
+Begin with a **present tense verb** that completes the sentence "This PR …":
+
+- Adds, Removes, Fixes, Updates, Refactors, Improves, Deprecates
+
+Describe the change **as a user of Astro will experience it**, not how it was implemented internally:
+
+```md
+// Too implementation-focused
+Logs helpful errors if content is invalid
+
+// Better — user-facing impact
+Adds logging for content collections configuration errors.
+```
+
+**Patch updates** — one line is usually enough; no end punctuation required unless writing multiple sentences:
+
+```md
+---
+'astro': patch
+---
+
+Fixes a bug where the toolbar audit would incorrectly flag images as above the fold
+```
+
+**New features (minor)** — start with "Adds", name the new API, and describe what users can now do. Include a code example when helpful. New features are also an opportunity to write a richer description that can feed into blog posts — see https://contribute.docs.astro.build/docs-for-code-changes/changesets/#new-features for guidance.
+
+```md
+---
+'astro': minor
+---
+
+Adds a new, optional property `timeout` for the `client:idle` directive
+
+This value allows you to specify a maximum time to wait, in milliseconds, before hydrating a UI framework component.
+```
+
+**Breaking changes (major)** — use verbs like "Removes", "Changes", or "Deprecates". Must include migration guidance; use diff code samples when appropriate:
+
+```md
+---
+'astro': major
+---
+
+Removes support for returning simple objects from endpoints. You must now return a `Response` instead.
+```
+
+**Additional rules:**
+
+- Include the specific API name (with backtick formatting) when the change is tied to a recognizable option or function
+- When the API is not user-facing, describe the use case or end result instead
+- For longer changesets, use `####` and deeper headings (never `##` or `###`) to divide sections — this keeps the CHANGELOG readable
+- Changes to default values must mention the old default, the new default, and how to restore previous behavior
+
+### Creating a Changeset
+
+Write the changeset file manually in `.changeset/` with a descriptive kebab-case slug as the filename (e.g., `.changeset/fix-font-copy-on-build.md`).
+
+### When Writing a PR
+
+- Always check that a changeset exists before posting the PR
+- Do not mention "added changeset" in the `Changes` section — it is process noise, not a behavior change
+
 ## Self-Check Before Posting
 
 - Title is reviewer-friendly (not commit-style)
 - `Changes` bullets describe behavior/implementation/impact
 - `Testing` explains scenarios and outcomes, not shell commands
 - `Docs` decision is explicit
+- Changeset file exists in `.changeset/` for any package-modifying PR
PATCH

echo "Gold patch applied."
