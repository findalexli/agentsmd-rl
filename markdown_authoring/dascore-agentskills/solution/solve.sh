#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dascore

# Idempotency guard
if grep -qF "Important: if changing site structure, edit `scripts/_templates/_quarto.yml` (no" ".agents/agents.md" && grep -qF "description: Draft the next release version and changelog by fetching tags, comp" ".agents/skills/draft-release/SKILL.md" && grep -qF "All coding agents should load and follow `.agents/agents.md` before making chang" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/agents.md b/.agents/agents.md
@@ -0,0 +1,109 @@
+# DASCore Agent Guide
+
+This file gives AI/code agents a practical checklist for contributing safely to DASCore.
+
+## Scope and priorities
+
+1. Keep changes minimal, targeted, and test-backed.
+2. Preserve DASCore conventions over personal preferences.
+3. Prefer consistency with existing code/tests/docs in this repo.
+
+## Development workflow
+
+1. Work on a feature/fix branch, not `master`.
+2. Keep commits focused (one logical change per commit where possible).
+3. Use pull requests to merge to `master`.
+
+## Environment setup
+
+Follow `docs/contributing/dev_install.qmd`.
+
+Typical setup:
+
+```bash
+git pull origin master --tags
+pip install -e ".[dev]"
+pre-commit install -f
+```
+
+## Linting and formatting
+
+- Run pre-commit hooks before finalizing changes.
+- Project lint/format is driven by pre-commit and Ruff config in `pyproject.toml`.
+
+```bash
+pre-commit run --all
+```
+
+Tip: running twice can apply auto-fixes on first pass.
+
+## Testing requirements
+
+Follow `docs/contributing/testing.qmd`.
+
+Run targeted tests for changed behavior, then broader tests as needed:
+
+```bash
+pytest tests/path/to/affected_test.py
+pytest tests
+```
+
+For coverage checks:
+
+```bash
+pytest tests --cov dascore --cov-report term-missing
+```
+
+For doctests:
+
+```bash
+pytest dascore --doctest-modules
+```
+
+## Test authoring conventions
+
+- Put tests under `tests/` mirroring package structure.
+- Group tests in classes.
+- Place fixtures as close as practical to usage (class, module, then `conftest.py`).
+
+## Code conventions
+
+
+- Prefer `pathlib.Path` over raw path strings (except performance-sensitive bulk file workflows).
+- Use snake_case dataframe column names when possible.
+- Use `df["col"]` (getitem), not `df.col` (getattr).
+- Prefer non-inplace dataframe operations unless inplace is explicitly required.
+- Add type hints for public functions/methods.
+- Use NumPy-style docstrings for public APIs.
+- Keep comments meaningful; do not restate obvious code.
+
+## Documentation changes
+
+If behavior or API changes, update docs in the same PR.
+
+- Documentation source lives in `docs/` (`.qmd` files).
+- API docs are generated from docstrings.
+- Build docs workflow (see `docs/contributing/documentation.qmd`):
+
+```bash
+python scripts/build_api_docs.py
+quarto render docs
+```
+
+Important: if changing site structure, edit `scripts/_templates/_quarto.yml` (not `docs/_quarto.yml`, which is generated/overwritten).
+
+## Quality bar for agent changes
+
+Before handing off:
+
+1. Code compiles/runs for changed paths.
+2. Relevant tests pass locally.
+3. Lint/format checks pass.
+4. Docs updated for user-visible behavior changes.
+5. No unrelated refactors bundled with bug fixes.
+
+## When uncertain
+
+- Prefer existing patterns in nearby DASCore modules/tests.
+- Call out assumptions explicitly in PR notes.
+- Choose the simpler behavior-preserving implementation first.
diff --git a/.agents/skills/draft-release/SKILL.md b/.agents/skills/draft-release/SKILL.md
@@ -0,0 +1,83 @@
+---
+name: draft-release
+description: Draft the next release version and changelog by fetching tags, computing the next semantic v* tag, collecting merged PRs into master since last release via gh, and printing the proposed version and categorized changelog.
+---
+
+# draft-release
+
+Draft the next release version and changelog from merged PRs.
+
+## Inputs
+
+- `release_type` (optional): `major`, `minor`, `patch`, or `bugfix`.
+- If omitted, default to `bugfix` (`patch` and `bugfix` are equivalent).
+
+## Workflow
+
+0. Ask for elevated permissions with network access to run `git fetch --all --tags` and the GitHub CLI PR commands used to collect merged PRs (for example `gh pr list`, `gh pr view`, or `gh api`).
+1. Fetch the latest refs and tags:
+
+```bash
+git fetch --all --tags
+```
+
+2. Determine the next version number:
+- Consider only tags that start with `v` and match strict semver:
+  `^v[0-9]+\.[0-9]+\.[0-9]+$` (ignore pre-release/build suffixes).
+- Find the latest existing release tag from that set (e.g., `v1.2.3`).
+- If no matching tags exist, use `v0.0.0` as the base.
+- Bump according to `release_type`:
+  - `major`: `X+1.0.0`
+  - `minor`: `X.Y+1.0`
+  - `patch`/`bugfix` (default): `X.Y.Z+1`
+- Output the computed new tag as `vX.Y.Z`.
+
+3. Collect merged PRs since the last release:
+- Use the previous release tag identified in step 2 as the lower bound.
+- Define PR scope as changes reachable in `last_release_tag..origin/master`
+  (or `..origin/<default_branch>` if default branch is not `master`).
+- Use GitHub CLI (`gh`) to read merged PRs for that scope.
+- Include at minimum PR number, title, merge date, URL, labels, and body text.
+- Look at the git diffs to extract additional info if needed.
+
+4. Draft a changelog with these sections:
+- `New Features`
+- `Bug Fixes`
+- `Breaking Changes`
+
+5. Classify PRs deterministically:
+- `Breaking Changes` if any of:
+  - title contains `!` in conventional-commit style segment, or
+  - label indicates breaking change (e.g., `breaking`), or
+  - body contains `BREAKING CHANGE`.
+- Otherwise `New Features` if labels/titles indicate feature work
+  (e.g., `feature`, `enhancement`, `feat`).
+- Otherwise `Bug Fixes`.
+- Sort entries by PR number ascending.
+- Include a link to the PR in the changelog.
+
+6. Print to screen:
+- The new version tag.
+- The drafted changelog.
+
+## Output Format
+
+```text
+Next Version: vX.Y.Z
+
+## New Features
+- #123: Short summary (https://github.com/OWNER/REPO/pull/123)
+
+## Bug Fixes
+- #124: Short summary (https://github.com/OWNER/REPO/pull/124)
+
+## Breaking Changes
+- #125: Short summary (https://github.com/OWNER/REPO/pull/125)
+```
+
+## Notes
+
+- If there are no items for a section, include the section with `- None`.
+- Prefer explicit, user-facing PR summaries over internal implementation details.
+- If no merged PRs are found in scope, still print the next version and include
+  all sections with `- None`.
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,7 @@
+# Agent Instructions
+
+The canonical agent instructions for this repository are in:
+
+- `.agents/agents.md`
+
+All coding agents should load and follow `.agents/agents.md` before making changes.
PATCH

echo "Gold patch applied."
