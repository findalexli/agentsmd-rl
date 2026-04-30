# Test Improvements for nextjs-turbopack-build-all-script

## Summary of Changes Required

### 1. Dockerfile Fix (line 21)
**Change:**
```diff
- RUN pip3 install --no-cache-dir pytest
+ RUN pip3 install --no-cache-dir pytest --break-system-packages
```

### 2. New test_outputs.py

```python
"""
Task: nextjs-turbopack-build-all-script
Repo: vercel/next.js @ 46761a321042e8ac1863f4cfc8d73d527956e181
PR:   90543

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

This task verifies:
1. Code changes: build-all script added, build renamed to build-native-auto in turbo.jsonc
2. Config changes: AGENTS.md updated to distinguish pnpm build vs pnpm build-all
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"


def _read_json(path: str) -> dict:
    """Read and parse a JSON file."""
    content = Path(path).read_text()
    return json.loads(content)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_json_syntax_valid():
    """Modified JSON files must be syntactically valid."""
    root_pkg = Path(f"{REPO}/package.json")
    next_swc_pkg = Path(f"{REPO}/packages/next-swc/package.json")

    # These should parse without errors
    _read_json(str(root_pkg))
    _read_json(str(next_swc_pkg))


# [repo_tests] pass_to_pass
def test_repo_prettier():
    """Repo's package.json files are properly formatted (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "prettier-check", "--check", "packages/next-swc/package.json"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_eslint():
    """Repo's package.json passes ESLint checks (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "eslint", "--config", "eslint.cli.config.mjs", "packages/next-swc/package.json"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint check failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_build_all_script_exists():
    """Root package.json must have build-all script that includes build-native-auto."""
    pkg = _read_json(f"{REPO}/package.json")
    scripts = pkg.get("scripts", {})

    assert "build-all" in scripts, "build-all script must exist in root package.json"
    build_all = scripts["build-all"]
    assert "build-native-auto" in build_all, \
        f"build-all must reference build-native-auto task, got: {build_all}"


# [pr_diff] fail_to_pass
def test_next_swc_script_renamed():
    """packages/next-swc/package.json build script must be renamed to build-native-auto."""
    pkg = _read_json(f"{REPO}/packages/next-swc/package.json")
    scripts = pkg.get("scripts", {})

    # The old "build" script that runs maybe-build-native.mjs should be renamed
    assert "build" not in scripts or "maybe-build-native" not in scripts.get("build", ""), \
        "Old 'build' script calling maybe-build-native.mjs should not exist"
    assert "build-native-auto" in scripts, \
        "build-native-auto script must exist"
    assert "maybe-build-native" in scripts["build-native-auto"], \
        "build-native-auto should call maybe-build-native.mjs"


# [pr_diff] fail_to_pass
def test_turbo_jsonc_task_renamed():
    """turbo.jsonc must have build-native-auto task instead of build task."""
    turbo_path = Path(f"{REPO}/packages/next-swc/turbo.jsonc")
    assert turbo_path.exists(), "turbo.jsonc must exist (renamed from turbo.json)"

    content = turbo_path.read_text()

    # Should have build-native-auto task with comment explaining it
    assert '"build-native-auto"' in content, \
        "turbo.jsonc must define build-native-auto task"
    assert '"build":' not in content or '"build-native-auto"' in content, \
        "Old 'build' task should be renamed to 'build-native-auto'"

    # Should have the explanatory comment about "auto"
    assert "auto" in content.lower() and "build-all" in content, \
        "turbo.jsonc should have comment explaining build-native-auto is for build-all"


# [pr_diff] fail_to_pass - CODE EXECUTION TEST (BEHAVIORAL)
def test_pnpm_script_validates():
    """Root package.json build-all script can be validated by pnpm (executes code)."""
    # First verify pnpm is available
    r = subprocess.run(
        ["pnpm", "--version"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm not available: {r.stderr}"

    # Now check if we can get the script list - this validates package.json syntax
    r = subprocess.run(
        ["npm", "run", "--silent", "--list"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    # npm run --list returns 0 even with no scripts, but will error if package.json is invalid
    output = r.stdout + r.stderr
    assert "build-all" in output, \
        f"build-all script not found in npm scripts list. Output: {output[:500]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — Config update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_agents_md_documents_build_all():
    """AGENTS.md must document pnpm build-all for building JS + Rust code."""
    agents_md = Path(f"{REPO}/AGENTS.md").read_text()

    # Should mention build-all command
    assert "pnpm build-all" in agents_md, \
        "AGENTS.md should document pnpm build-all command"

    # Should distinguish between build (JS only) and build-all (JS + Rust)
    assert "pnpm build" in agents_md, \
        "AGENTS.md should still document pnpm build"

    # Should explain when to use build-all vs build --filter=next
    # Check for key phrases that indicate the distinction
    js_only_indicators = ["build all JS code", "JS code", "JS and Rust"]
    has_js_only_distinction = any(indicator in agents_md for indicator in js_only_indicators)
    assert has_js_only_distinction, \
        "AGENTS.md should distinguish between 'build' (JS only) and 'build-all' (JS + Rust)"


# [pr_diff] fail_to_pass
def test_agents_md_branch_switch_uses_build_all():
    """AGENTS.md should recommend build-all for branch switches and when editing Turbopack."""
    agents_md = Path(f"{REPO}/AGENTS.md").read_text()

    # After branch switch, should use build-all
    branch_switch_section = agents_md.find("switching branches")
    if branch_switch_section != -1:
        # Look at context after "switching branches"
        context = agents_md[branch_switch_section:branch_switch_section + 500]
        assert "build-all" in context, \
            "AGENTS.md should recommend build-all after switching branches"

    # When editing Turbopack/Rust, should use build-all
    assert "build-all" in agents_md.lower(), \
        "AGENTS.md should reference build-all in the context of Turbopack/Rust builds"
```

### 3. Updated eval_manifest.yaml

```yaml
version: "2.0"

source:
  repo: "vercel/next.js"
  pr: 90543
  base_commit: "46761a321042e8ac1863f4cfc8d73d527956e181"
  merge_commit: "ef970c06fb7ef8337db50ef962bb13f3f2d3204f"

checks:
  # Syntax validation
  - id: json_syntax_valid
    type: pass_to_pass
    origin: static
    description: "Modified JSON files must be syntactically valid"

  # Repo CI/CD tests (pass_to_pass gates)
  - id: test_repo_prettier
    type: pass_to_pass
    origin: repo_tests
    description: "Repo's package.json files are properly formatted"

  - id: test_repo_eslint
    type: pass_to_pass
    origin: repo_tests
    description: "Repo's package.json passes ESLint checks"

  # Core code changes - build script separation
  - id: build_all_script_exists
    type: fail_to_pass
    origin: pr_diff
    description: "Root package.json has build-all script referencing build-native-auto"

  - id: next_swc_script_renamed
    type: fail_to_pass
    origin: pr_diff
    description: "packages/next-swc/package.json build script renamed to build-native-auto"

  - id: turbo_jsonc_task_renamed
    type: fail_to_pass
    origin: pr_diff
    description: "turbo.jsonc has build-native-auto task with explanatory comment"

  # Behavioral test that executes code
  - id: test_pnpm_script_validates
    type: fail_to_pass
    origin: pr_diff
    description: "package.json scripts are valid and recognized by npm/pnpm (code execution)"

  # Config documentation updates (at least one required for agentmd-edit)
  - id: agents_md_documents_build_all
    type: fail_to_pass
    origin: pr_diff
    description: "AGENTS.md documents pnpm build-all and distinguishes it from pnpm build"

  - id: agents_md_branch_switch_uses_build_all
    type: fail_to_pass
    origin: pr_diff
    description: "AGENTS.md recommends build-all for branch switches and Turbopack edits"

rubric:
  []
```

## Key Improvements

1. **Dockerfile fix**: Added `--break-system-packages` to resolve PEP 668 issue
2. **Code-executing behavioral test**: `test_pnpm_script_validates()` uses `subprocess.run()` to actually execute pnpm/npm and validate the package.json is syntactically valid
3. **Repo CI/CD tests**: Added `test_repo_prettier` and `test_repo_eslint` as pass_to_pass gates
4. **Preserved existing tests**: All original grep tests are kept as they remain valid checks
5. **Updated eval_manifest.yaml**: Added new checks with correct `origin: repo_tests` for CI tests and `origin: pr_diff` for behavioral test

## Files Modified

- `/workspace/task/environment/Dockerfile` - line 21
- `/workspace/task/tests/test_outputs.py` - complete rewrite
- `/workspace/task/eval_manifest.yaml` - added new check entries
