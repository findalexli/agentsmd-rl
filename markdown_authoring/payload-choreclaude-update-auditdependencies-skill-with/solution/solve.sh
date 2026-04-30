#!/usr/bin/env bash
set -euo pipefail

cd /workspace/payload

# Idempotency guard
if grep -qF "- If the same vulnerable package appears through many transitive paths, a global" ".claude/skills/audit-dependencies/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/audit-dependencies/SKILL.md b/.claude/skills/audit-dependencies/SKILL.md
@@ -3,14 +3,14 @@ name: audit-dependencies
 description: Use when fixing dependency vulnerabilities, running pnpm audit, or when the audit-dependencies CI check fails
 user-invocable: true
 disable-model-invocation: true
-argument-hint: "critical|high|moderate|low"
+argument-hint: 'critical|high|moderate|low'
 ---
 
 # Audit Dependencies
 
 ## Overview
 
-Fix dependency vulnerabilities reported by `.github/workflows/audit-dependencies.sh`. Always prefer direct dependency bumps over pnpm overrides. Every override requires justification for why a direct bump isn't feasible.
+Fix dependency vulnerabilities reported by `.github/workflows/audit-dependencies.sh`. Prefer fixes in this order: direct dependency bump > lockfile update > pnpm override. Every override requires justification for why simpler approaches aren't feasible.
 
 ## Core Workflow
 
@@ -23,8 +23,11 @@ digraph audit {
     "Research breaking changes" [shape=box];
     "Breaking changes acceptable?" [shape=diamond];
     "Apply direct bump" [shape=box];
+    "Is version pinned or ranged?" [shape=diamond];
+    "Lockfile update" [shape=box];
     "Apply pnpm override" [shape=box];
     "More packages?" [shape=diamond];
+    "Present plan to user" [shape=box];
     "Install and verify" [shape=box];
     "Build and verify" [shape=box];
     "Commit and create PR" [shape=box];
@@ -33,14 +36,18 @@ digraph audit {
     "Group by package" -> "Trace dependency chain";
     "Trace dependency chain" -> "Can bump direct dep?";
     "Can bump direct dep?" -> "Research breaking changes" [label="yes"];
-    "Can bump direct dep?" -> "Apply pnpm override" [label="no - explain why"];
+    "Can bump direct dep?" -> "Is version pinned or ranged?" [label="no"];
     "Research breaking changes" -> "Breaking changes acceptable?";
     "Breaking changes acceptable?" -> "Apply direct bump" [label="yes"];
-    "Breaking changes acceptable?" -> "Apply pnpm override" [label="no - explain why"];
+    "Breaking changes acceptable?" -> "Is version pinned or ranged?" [label="no"];
+    "Is version pinned or ranged?" -> "Lockfile update" [label="ranged - fix is in range"];
+    "Is version pinned or ranged?" -> "Apply pnpm override" [label="pinned - explain why"];
     "Apply direct bump" -> "More packages?";
+    "Lockfile update" -> "More packages?";
     "Apply pnpm override" -> "More packages?";
     "More packages?" -> "Trace dependency chain" [label="yes"];
-    "More packages?" -> "Install and verify" [label="no"];
+    "More packages?" -> "Present plan to user" [label="no"];
+    "Present plan to user" -> "Install and verify";
     "Install and verify" -> "Build and verify";
     "Build and verify" -> "Commit and create PR";
 }
@@ -87,29 +94,59 @@ For transitive deps, walk up the chain to find the nearest package you control:
 
 **Parallelize research**: When multiple packages need breaking change analysis, dispatch parallel agents (one per package) to research simultaneously.
 
+#### Check if a lockfile update is sufficient
+
+Before reaching for an override, check whether the parent's version specifier is **pinned** (exact version like `3.10.3`) or **ranged** (like `^2.3.1`, `~4.0.3`):
+
+```bash
+pnpm view <parent> dependencies.<vulnerable-pkg>
+```
+
+If the range already includes the fixed version, a lockfile update is all that's needed:
+
+```bash
+pnpm update <vulnerable-pkg> --recursive
+```
+
+No `package.json` changes required — the lockfile was just stale.
+
 #### Fall back to override only when justified
 
-Add a scoped pnpm override in root `package.json` only when:
+Add a pnpm override in root `package.json` only when:
 
+- The parent pins an exact version that doesn't satisfy the fix
 - No version of the parent package fixes the vulnerability
 - The parent bump has high breaking change risk (major API changes, no test coverage, requires code changes across many files)
 - The user explicitly decides to defer the parent bump to a separate PR
 
-Override format: `"<parent>><vulnerable-pkg>": "<fixed-version>"`
+Override format: `"<parent>><vulnerable-pkg>": "^<fixed-version>"`
+
+**Override syntax rules:**
+
+- Use `^` ranges, not `>=`. `>=` can cross major versions and cause unexpected resolutions (e.g., `"picomatch": ">=2.3.2"` can resolve to 4.x).
+- pnpm only supports single-level parent scoping: `"parent>pkg"` works, `"grandparent>parent>pkg"` does not.
+- pnpm does not support version selectors in override keys: `"pkg@^2"` does not work.
+- If the same vulnerable package appears through many transitive paths, a global override may be needed. Be careful that it doesn't affect unrelated consumers on a different major version — use parent-scoped overrides when the package spans multiple major versions across the tree.
+- pnpm only honors `overrides` in the root workspace `package.json`. Overrides in workspace packages are ignored.
 
 Before adding any override, verify the target version exists:
 
 ```bash
 pnpm view <pkg>@<version> version
 ```
 
-### 3. Apply Fixes
+### 3. Present Plan to User
+
+Before applying fixes, present a summary table to the user showing each vulnerability, the proposed fix strategy (direct bump / lockfile update / override), and justification. Get confirmation before proceeding.
+
+### 4. Apply Fixes
 
 - Edit `package.json` files for direct bumps
+- Run `pnpm update <pkg> --recursive` for lockfile-only fixes
 - Edit root `package.json` `pnpm.overrides` for overrides (keep alphabetical)
 - If a direct bump changes behavior, update consuming code (e.g., adding `allowOverwrite: true` when an API default changes)
 
-### 4. Install and Verify
+### 5. Install and Verify
 
 ```bash
 pnpm install
@@ -129,7 +166,7 @@ Then re-run the audit script with the same severity:
 
 The audit script must exit 0. If vulnerabilities remain, check for additional instances of the same dependency in other workspace packages.
 
-### 5. Build and Verify
+### 6. Build and Verify
 
 ```bash
 pnpm run build:core
@@ -141,7 +178,7 @@ For packages with changed dependencies, also run their specific build:
 pnpm run build:<package-name>
 ```
 
-### 6. Look Up CVEs
+### 7. Look Up CVEs
 
 For each fixed vulnerability, find the GitHub Security Advisory (GHSA):
 
@@ -152,7 +189,7 @@ For each fixed vulnerability, find the GitHub Security Advisory (GHSA):
 
 **Parallelize CVE lookups**: Dispatch parallel agents to search for CVEs across all packages simultaneously.
 
-### 7. Commit and Create PR
+### 8. Commit and Create PR
 
 Commit with conventional commit format:
 
@@ -171,7 +208,7 @@ Create PR using `gh pr create` with this body structure:
 
 - **[Package name] in [workspace path]**
   - [old version] → [new version]. Fixes [GHSA-xxxx-xxxx-xxxx](https://github.com/advisories/GHSA-xxxx-xxxx-xxxx) ([description]).
-  - [Why this approach: direct bump because X / override because Y]
+  - [Why this approach: direct bump because X / lockfile update because Y / override because Z]
   - [Any code changes required by the bump]
 
 ## Design Decisions
@@ -181,11 +218,17 @@ Create PR using `gh pr create` with this body structure:
 
 ## Common Mistakes
 
-| Mistake                                 | Fix                                                                                                                     |
-| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
-| Jumping straight to overrides           | Always check if bumping the parent resolves it first                                                                    |
-| Not checking all workspace packages     | Same dep may appear in multiple `package.json` files (e.g., `changelogen` in both `tools/releaser` and `tools/scripts`) |
-| Overriding with a nonexistent version   | Verify the target version exists with `pnpm view` before installing                                                     |
-| Not falling back to `--ignore-scripts`  | Pre-existing native build failures block `pnpm install`; use `--ignore-scripts` to get lockfile updated                 |
-| Missing code changes for breaking bumps | If a bump changes API defaults, update the calling code                                                                 |
-| Forgetting advisory links in PR         | Always look up and include GHSA links for each vulnerability                                                               |
+| Mistake                                           | Fix                                                                                                                                                         |
+| ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
+| Jumping straight to overrides                     | Check: can you bump the parent? If not, does the semver range already allow the fix (lockfile update)? Only then override.                                  |
+| Using `>=` in override ranges                     | Use `^` to stay within the same major version. `>=2.3.2` can resolve to 4.x.                                                                                |
+| Not checking pinned vs ranged                     | `pnpm view <parent> dependencies.<pkg>` — if ranged and the fix is in range, just `pnpm update`.                                                            |
+| Nested override scoping (`a>b>c`)                 | pnpm only supports single-level: `"parent>pkg"`. For deeper chains, override the direct parent or use a global override.                                    |
+| Version selectors in override keys (`pkg@^2`)     | Not supported by pnpm. Use parent-scoped or global overrides instead.                                                                                       |
+| Global override affecting multiple major versions | `"picomatch": ">=4.0.4"` forces all picomatch to 4.x, breaking consumers that need 2.x. Scope overrides to the parent when a package spans multiple majors. |
+| Not checking all workspace packages               | Same dep may appear in multiple `package.json` files (e.g., `changelogen` in both `tools/releaser` and `tools/scripts`)                                     |
+| Overriding with a nonexistent version             | Verify the target version exists with `pnpm view` before installing                                                                                         |
+| Not falling back to `--ignore-scripts`            | Pre-existing native build failures block `pnpm install`; use `--ignore-scripts` to get lockfile updated                                                     |
+| Missing code changes for breaking bumps           | If a bump changes API defaults, update the calling code                                                                                                     |
+| Forgetting advisory links in PR                   | Always look up and include GHSA links for each vulnerability                                                                                                |
+| Applying fixes without user confirmation          | Present the full plan (strategy per vuln + justification) and get confirmation before making changes                                                        |
PATCH

echo "Gold patch applied."
