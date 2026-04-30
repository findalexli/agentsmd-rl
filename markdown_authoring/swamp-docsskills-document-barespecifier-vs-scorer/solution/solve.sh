#!/usr/bin/env bash
set -euo pipefail

cd /workspace/swamp

# Idempotency guard
if grep -qF "Other Deno-compatible imports (`npm:`, `jsr:`, `https://`) are inlined into the" ".claude/skills/swamp-extension-publish/references/publishing.md" && grep -qF "`swamp extension fmt` / `swamp extension push` reject the inline form as soon as" ".claude/skills/swamp-extension-quality/SKILL.md" && grep -qF "`deno.json` and writes its own with no imports map, so a bare specifier cannot" ".claude/skills/swamp-extension-quality/references/templates.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/swamp-extension-publish/references/publishing.md b/.claude/skills/swamp-extension-publish/references/publishing.md
@@ -131,12 +131,28 @@ paths — hardcoding breaks smoke tests run against a source-loaded extension.
 
 ### Import Rules
 
-- `import { z } from "npm:zod@4";` is always required
-- Any Deno-compatible import (`npm:`, `jsr:`, `https://`) can be used — swamp
-  resolves and inlines all three kinds identically, with zod as the sole
-  externalization exception
-- Extensions with a `deno.json` or `package.json` can use bare specifiers (e.g.,
-  `from "zod"`)
+`import { z } from "npm:zod@4";` is the canonical zod import for entrypoint
+files. Two distinct constraints make this the right form:
+
+- **Hermeticity at score time.** The swamp-club scorer and the local
+  `swamp extension quality` command both run in a sandbox that strips the
+  tarball's `deno.json` and writes its own with `nodeModulesDir: "auto"` and no
+  imports map. Bare specifiers like `from "zod"` resolve at bundle time via the
+  repo's `deno.json` import map, but fail at score time — `deno doc --json`
+  cannot find the bare name and the command throws before factor scoring begins.
+  The inline `npm:` form is the only form that resolves under both the bundler's
+  permissive resolution AND the scorer's hermetic resolution.
+- **Zod externalization.** Zod is the sole import that is NOT inlined into the
+  published bundle. The extension must share swamp's zod instance so schema
+  `instanceof` checks work across the module boundary — that is why zod in
+  particular is called out as the canonical inline form, not merely a
+  consequence of hermeticity.
+
+Other Deno-compatible imports (`npm:`, `jsr:`, `https://`) are inlined into the
+bundle by the swamp packager. Bare specifiers backed by `deno.json` or
+`package.json` work for the bundler, but follow the hermeticity rule above for
+anything that needs to score: prefer the inline form in entrypoint files.
+
 - All imports must be static top-level imports — dynamic `import()` calls are
   rejected during push
 - Always pin versions on all non-local imports for reproducibility. An unpinned
diff --git a/.claude/skills/swamp-extension-quality/SKILL.md b/.claude/skills/swamp-extension-quality/SKILL.md
@@ -69,6 +69,22 @@ gitlab.com (public SaaS only), codeberg.org, bitbucket.org. Self-hosted GitHub
 Enterprise, self-hosted GitLab, private Gitea, Azure DevOps, Bitbucket Server —
 none earn the 2-point verification factor. URL must be HTTPS.
 
+**Bare-specifier imports fail `swamp extension quality`.** The command runs
+hermetically — it strips the tarball's `deno.json`, so a bare `"zod"` import
+cannot resolve and the command throws
+`deno doc --json failed: Import "zod" not a dependency` **before** factor
+scoring begins. Fix: use `import { z } from "npm:zod@4"` in every entrypoint
+file. Adding `deno.json` to `additionalFiles:` does not help — it lands at
+`files/deno.json`, which the scorer does not promote. **Deno's default lint
+rules enable `no-import-prefix` whenever an `imports` map is present**, so
+`swamp extension fmt` / `swamp extension push` reject the inline form as soon as
+you add a `deno.json` with an `imports` section — the same `deno.json` the
+scorer strips. Break the deadlock one of two ways: disable the rule in your
+`deno.json` (`"lint": { "rules": { "exclude": ["no-import-prefix"] } }`), or
+suppress per-import with `// deno-lint-ignore no-import-prefix` above the zod
+import line. The deadlock goes away entirely once the scorer honours the
+tarball's `files/deno.json`.
+
 **`fast-check` is subtle.** A single missing return type on an exported function
 or a public export that leaks a private type costs the whole point. Run
 `deno doc --lint <entrypoints>` locally to catch this before publish.
@@ -122,6 +138,10 @@ surfaces rubric failures earlier and prepopulates the package cache.
 `verified-by-swamp` is the one factor the CLI cannot score — it is reserved for
 `@swamp` namespace or admin review and is granted server-side at publish time.
 
+If `swamp extension quality` throws a `deno doc` error instead of printing
+factor results, the entrypoint uses a bare specifier — see "Bare-specifier
+imports fail `swamp extension quality`" above for the fix.
+
 ## Details when needed
 
 For the full per-factor mechanics, the grade thresholds, and a worked example of
@@ -143,6 +163,9 @@ above. Do not speculate — look at the actual breakdown.
 
 Common patterns:
 
+- **`swamp extension quality` throws `Import "zod" not a dependency` instead of
+  showing factor results** → entrypoint uses bare `"zod"`; switch to
+  `"npm:zod@4"`. Adding `deno.json` to `additionalFiles:` does not resolve it.
 - **"Has README" shows 0/2 but the repo has a README** → not listed in
   `additionalFiles:`, so it is not in the tarball. Publish a new version with
   the manifest fixed.
diff --git a/.claude/skills/swamp-extension-quality/references/templates.md b/.claude/skills/swamp-extension-quality/references/templates.md
@@ -103,7 +103,7 @@ no private-type leaks), and the module-level doc signal for `has-readme`.
  * @module
  */
 
-import { z } from "zod";
+import { z } from "npm:zod@4";
 
 /** Accepted input shape for this model's operations. */
 export const argsSchema = z.object({
@@ -140,6 +140,10 @@ Rules this example demonstrates:
 - **All public types are themselves exported** (`Args`, `Result`, `argsSchema`)
   — so nothing exposed through the API refers to a private type.
 - **Module-level `@module` block at the top** — satisfies module-doc detection.
+- **Inline `npm:zod@4` specifier**, not bare `"zod"`. The scorer and
+  `swamp extension quality` run in a hermetic sandbox that strips the repo's
+  `deno.json` and writes its own with no imports map, so a bare specifier cannot
+  resolve at score time even when an import map maps it at bundle time.
 
 ## Pre-publish command sequence
 
PATCH

echo "Gold patch applied."
