#!/usr/bin/env bash
set -euo pipefail

cd /workspace/awesome-claude-md

# Idempotency guard
if grep -qF "- Test changelog generates with correct sections for features, fixes, and breaki" "templates/conventional-changelog/CLAUDE.md" && grep -qF "- Config: `knip.config.ts`, `knip.json`, or `knip.config.js` at project root" "templates/knip/CLAUDE.md" && grep -qF "- Config: `.lintstagedrc.js`, `lint-staged.config.js`, or `lint-staged` field in" "templates/lint-staged/CLAUDE.md" && grep -qF "- Test OKLCH colors render correctly in browsers supporting the `oklch()` functi" "templates/oklch-colors/CLAUDE.md" && grep -qF "- Config: `renovate.json`, `.github/renovate.json`, or `renovate.json5` at proje" "templates/renovate/CLAUDE.md" && grep -qF "- Test hooks reinstall correctly after `rm -rf .git/hooks` and `npx simple-git-h" "templates/simple-git-hooks/CLAUDE.md" && grep -qF "- Test uplink fallback when the upstream npmjs registry is unreachable." "templates/verdaccio/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/templates/conventional-changelog/CLAUDE.md b/templates/conventional-changelog/CLAUDE.md
@@ -39,11 +39,16 @@ conventional-changelog.config.js // or in package.json
 6. **Never generate changelog without version bump.** Tag first.
 7. **Never forget to commit CHANGELOG.md.** Should be in version control.
 
+## File Naming
+
+- Config: `conventional-changelog.config.js` or `.changelogrc` at project root
+- Output: `CHANGELOG.md` in project root, committed to version control
+
 ## Testing
 
-- Test changelog generates with correct sections.
-- Test links work correctly.
-- Test with different presets.
-- Test changelog links work.
-- Test changelog links work.
+- Test changelog generates with correct sections for features, fixes, and breaking changes.
+- Test links to commits and issues resolve correctly.
+- Test with different presets (angular, atom, ember, eslint).
+- Test `releaseCount: 0` regenerates the full changelog from all commits.
+- Test custom `writerOpts` templates render expected output.
 
diff --git a/templates/knip/CLAUDE.md b/templates/knip/CLAUDE.md
@@ -39,11 +39,16 @@ src/
 6. **Never ignore monorepo configuration.** `workspaces` in config.
 7. **Never use without understanding false positives.** Some exports used dynamically.
 
+## File Naming
+
+- Config: `knip.config.ts`, `knip.json`, or `knip.config.js` at project root
+- Workspace configs: one `knip.config.ts` per workspace root in monorepos
+
 ## Testing
 
-- Test with known unused code to verify detection.
-- Test fix removes correct code.
-- Test in CI blocks unused code.
-- Test with monorepo setup.
-- Test with monorepo setup.
+- Test with known unused code to verify detection accuracy.
+- Test `--fix` removes correct code without breaking imports.
+- Test CI pipeline fails when unused exports are introduced.
+- Test monorepo workspace cross-references resolve correctly.
+- Test dynamic imports are handled or explicitly ignored.
 
diff --git a/templates/lint-staged/CLAUDE.md b/templates/lint-staged/CLAUDE.md
@@ -39,10 +39,16 @@ src/
 6. **Never use lint-staged without git hooks.** Integrate with Husky.
 7. **Never ignore exit codes.** Non-zero exit blocks commit.
 
+## File Naming
+
+- Config: `.lintstagedrc.js`, `lint-staged.config.js`, or `lint-staged` field in `package.json`
+- Hooks: `.husky/pre-commit` contains `npx lint-staged`
+
 ## Testing
 
-- Test with staged file that has lint error.
-- Test auto-fix applies correctly.
-- Test commit blocked when unfixable errors exist.
-- Test with multiple staged files.
+- Test with a staged file that has a lint error and verify commit is blocked.
+- Test auto-fix applies correctly and stages the fixed file.
+- Test commit is blocked when unfixable errors exist in staged files.
+- Test with multiple staged files across different glob patterns.
+- Test that unstaged files are not modified by lint-staged commands.
 
diff --git a/templates/oklch-colors/CLAUDE.md b/templates/oklch-colors/CLAUDE.md
@@ -39,10 +39,16 @@ styles/
 6. **Never use raw OKLCH in legacy codebases.** Gradual migration.
 7. **Never forget about HDR displays.** OKLCH supports wide gamut.
 
+## File Naming
+
+- Theme files: `theme.css` or `tokens.css` for OKLCH color definitions
+- Fallbacks: `fallback.css` for browsers without OKLCH support
+
 ## Testing
 
-- Test in browsers supporting oklch().
-- Test gradients vs HSL comparison.
-- Test fallback rendering.
-- Test with HDR displays.
+- Test OKLCH colors render correctly in browsers supporting the `oklch()` function.
+- Test gradients appear smooth compared to equivalent HSL gradients.
+- Test fallback colors display correctly in older browsers.
+- Test wide-gamut colors on HDR displays.
+- Test `color-mix()` produces expected intermediate values.
 
diff --git a/templates/renovate/CLAUDE.md b/templates/renovate/CLAUDE.md
@@ -39,10 +39,15 @@ package.json
 6. **Never ignore security updates.** `extends: ["github>whitesource/merge-confidence:beta"]`.
 7. **Never skip the onboarding PR.** Review Renovate's initial configuration.
 
+## File Naming
+
+- Config: `renovate.json`, `.github/renovate.json`, or `renovate.json5` at project root
+- Presets: shared configs via `extends` from npm packages or GitHub repos
+
 ## Testing
 
-- Test PRs pass CI before merging.
-- Test grouped updates work correctly.
-- Test scheduling respects time windows.
-- Test with private packages.
-- Test with private packages.
+- Test that PRs pass CI before auto-merge triggers.
+- Test grouped updates bundle related packages into a single PR.
+- Test scheduling respects configured time windows and timezone.
+- Test private package updates resolve through configured registries.
+- Test major version updates are never auto-merged without review.
diff --git a/templates/simple-git-hooks/CLAUDE.md b/templates/simple-git-hooks/CLAUDE.md
@@ -38,10 +38,15 @@ src/
 6. **Never mix with husky/lefthook.** Use one git hooks manager.
 7. **Never forget `$1` for commit-msg hook.** Passes commit message file.
 
+## File Naming
+
+- Config: `simple-git-hooks` field in `package.json` — no separate config file needed
+- Hooks: installed to `.git/hooks/` directory automatically on `postinstall`
+
 ## Testing
 
-- Test hooks run on appropriate git actions.
-- Test that failing commands block git operation.
-- Test reinstall after `rm -rf .git/hooks`.
-- Test with multiple hooks.
-- Test with multiple hooks.
+- Test hooks run on the appropriate git actions (commit, push, merge).
+- Test that failing commands block the git operation with a non-zero exit code.
+- Test hooks reinstall correctly after `rm -rf .git/hooks` and `npx simple-git-hooks`.
+- Test with multiple hooks configured (pre-commit and commit-msg simultaneously).
+- Test that `git commit --no-verify` bypasses hooks when needed.
diff --git a/templates/verdaccio/CLAUDE.md b/templates/verdaccio/CLAUDE.md
@@ -40,10 +40,15 @@ packages/
 6. **Never forget uplink timeout settings.** Prevent hanging.
 7. **Never use default config in production.** Customize auth, access, storage.
 
+## File Naming
+
+- Config: `config.yaml` at Verdaccio root — YAML format required
+- Storage: `storage/` directory for cached and published packages
+
 ## Testing
 
-- Test publishing and installing packages.
-- Test auth with different providers.
-- Test uplink fallback when npmjs down.
-- Test with scoped packages.
-- Test with scoped packages.
+- Test publishing and installing private scoped packages end-to-end.
+- Test authentication with htpasswd and configured auth plugins.
+- Test uplink fallback when the upstream npmjs registry is unreachable.
+- Test access control rules restrict unauthorized publishing.
+- Test `max_body_size` rejects packages exceeding the configured limit.
PATCH

echo "Gold patch applied."
