#!/usr/bin/env bash
set -euo pipefail

cd /workspace/worktrunk

# Idempotency guard
if grep -qF "4. **Check library API compatibility**: Run `cargo semver-checks check-release -" ".claude/skills/release/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/release/SKILL.md b/.claude/skills/release/SKILL.md
@@ -12,21 +12,22 @@ metadata:
 1. **Run tests**: `cargo run -- hook pre-merge --yes`
 2. **Check current version**: Read `version` in `Cargo.toml`
 3. **Review commits**: Check commits since last release to understand scope of changes
-4. **Credit contributors**: Check for external PR authors and issue reporters (see "Credit External Contributors" and "Credit Issue Reporters" below)
-5. **Confirm release type with user**: Present changes summary and ask user to confirm patch/minor/major (see below)
-6. **Bump version** (must run on a clean tree — before editing CHANGELOG):
+4. **Check library API compatibility**: Run `cargo semver-checks check-release -p worktrunk` (install with `cargo install cargo-semver-checks --locked` if missing). If it reports breaking changes, the bump must be minor (pre-1.0) or major (post-1.0). See "Library API Compatibility" below.
+5. **Credit contributors**: Check for external PR authors and issue reporters (see "Credit External Contributors" and "Credit Issue Reporters" below)
+6. **Confirm release type with user**: Present changes summary (including semver-checks result) and ask user to confirm patch/minor/major (see below)
+7. **Bump version** (must run on a clean tree — before editing CHANGELOG):
    ```bash
    cargo release X.Y.Z -p worktrunk -x --no-publish --no-push --no-tag --no-verify --no-confirm && cargo check
    ```
-   This bumps `Cargo.toml`, `Cargo.lock`, and applies `pre-release-replacements` (e.g., SKILL.md), then auto-commits. We'll reset this commit in step 8 to fold in the CHANGELOG.
-7. **Update CHANGELOG**: Add `## X.Y.Z` section at top with changes (see MANDATORY verification below)
-8. **Commit**: Reset the auto-commit from step 6, stage everything, and create the final release commit:
+   This bumps `Cargo.toml`, `Cargo.lock`, and applies `pre-release-replacements` (e.g., SKILL.md), then auto-commits. We'll reset this commit in step 9 to fold in the CHANGELOG.
+8. **Update CHANGELOG**: Add `## X.Y.Z` section at top with changes (see MANDATORY verification below)
+9. **Commit**: Reset the auto-commit from step 7, stage everything, and create the final release commit:
    ```bash
    git reset --soft HEAD~1 && git add -A && git commit -m "Release vX.Y.Z"
    ```
-9. **Merge to main**: `wt merge --no-remove` (rebases onto main, pushes, keeps worktree)
-10. **Tag and push**: `git tag vX.Y.Z && git push origin vX.Y.Z`
-11. **Wait for release workflow**: Poll with `gh pr checks --required` or `gh run view <run-id>` every 60 seconds until complete (avoid `gh run watch` — it can hang). Non-required checks are ignored
+10. **Merge to main**: `wt merge --no-remove` (rebases onto main, pushes, keeps worktree)
+11. **Tag and push**: `git tag vX.Y.Z && git push origin vX.Y.Z`
+12. **Wait for release workflow**: Poll with `gh pr checks --required` or `gh run view <run-id>` every 60 seconds until complete (avoid `gh run watch` — it can hang). Non-required checks are ignored
 
 The tag push triggers the release workflow which builds binaries and publishes to crates.io, Homebrew, and winget automatically.
 
@@ -218,6 +219,22 @@ Recommendation: Minor release (0.3.0) — new features, no breaking changes
 
 Current project status: early release, breaking changes acceptable, optimize for best solution over compatibility.
 
+## Library API Compatibility
+
+Worktrunk is primarily a CLI, but it also publishes a library crate (`[lib]` in `Cargo.toml`) that downstream crates depend on. `cargo-semver-checks` compares the current public API against the last version published to crates.io and flags semver violations.
+
+```bash
+cargo semver-checks check-release -p worktrunk
+```
+
+Interpreting results:
+
+- **No issues reported**: any bump level is valid from the library's perspective. Choose based on CLI changes and new features.
+- **Breaking changes reported**: while pre-1.0, these require at minimum a minor bump (e.g., 0.37.0 → 0.38.0). A patch release is not allowed.
+- **Tool fails to run** (e.g., missing baseline): likely the crate hasn't been published yet or the registry cache is stale. Try `cargo semver-checks check-release -p worktrunk --baseline-version <last-published>`.
+
+This check validates the chosen bump — it doesn't distinguish patch vs. minor when no breakage exists. Continue using the commit review to decide between patch (fixes only) and minor (new features).
+
 ## Troubleshooting
 
 ### Release workflow fails after tag push
PATCH

echo "Gold patch applied."
