"""
Task: playwright-cli-daemon-skip-browser-download
Repo: microsoft/playwright @ 9c069597ff7c822052832c0e46eda76f37f9c1ef
PR:   39978

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/playwright"
TARGET_FILE = "packages/playwright-core/src/tools/cli-daemon/program.ts"


def _read_source():
    """Read the target source file."""
    return Path(f"{REPO}/{TARGET_FILE}").read_text()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_typescript_valid_syntax():
    """Modified TypeScript file must have valid syntax (parsable)."""
    src = _read_source()

    # Basic TypeScript syntax validation - check for balanced braces
    open_braces = src.count('{')
    close_braces = src.count('}')
    assert open_braces == close_braces, f"Unbalanced braces: {open_braces} open, {close_braces} close"

    open_parens = src.count('(')
    close_parens = src.count(')')
    assert open_parens == close_parens, f"Unbalanced parentheses: {open_parens} open, {close_parens} close"

    # Check for basic TypeScript keywords that indicate valid structure
    assert "import " in src, "Missing import statements"
    assert "export " in src or "async function" in src, "Missing expected declarations"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_env_var_check_exists():
    """PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD env var check exists at start of ensureConfiguredBrowserInstalled."""
    src = _read_source()

    # Check that the env var check exists
    assert "getAsBooleanFromENV('PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD')" in src, \
        "Missing PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD env var check"

    # Check that it's imported from the right module
    assert "import { getAsBooleanFromENV } from '../../server/utils/env'" in src, \
        "Missing import for getAsBooleanFromENV"


def test_resolve_and_install_helper_exists():
    """resolveAndInstall() helper function exists and uses resolveBrowsers()."""
    src = _read_source()

    # Check that resolveAndInstall function is defined
    assert "async function resolveAndInstall(nameOrChannel: string)" in src, \
        "Missing resolveAndInstall() helper function"

    # Check that it uses resolveBrowsers with correct options
    assert "browserRegistry.resolveBrowsers([nameOrChannel], { shell: 'no' })" in src, \
        "resolveAndInstall() should call resolveBrowsers with shell: 'no' option"


def test_ffmpeg_dependency_installation():
    """ffmpeg is resolved and installed as a dependency in findOrInstallDefaultBrowser."""
    src = _read_source()

    # The PR adds await resolveAndInstall('ffmpeg') in findOrInstallDefaultBrowser
    # before returning when a browser channel is found
    assert "await resolveAndInstall('ffmpeg')" in src, \
        "Missing ffmpeg dependency installation in findOrInstallDefaultBrowser"


def test_chromium_uses_resolve_and_install():
    """Chromium installation uses resolveAndInstall() helper instead of manual executable check."""
    src = _read_source()

    # Check that chromium installation uses the new helper
    assert "await resolveAndInstall('chromium')" in src, \
        "Chromium installation should use resolveAndInstall() helper"

    # Check that old manual executable check pattern is removed
    old_pattern = "!fs.existsSync(chromiumExecutable?.executablePath()!)"
    assert old_pattern not in src, \
        "Old manual executable check pattern should be removed"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

def test_not_stub():
    """Modified functions have real logic, not just pass/return."""
    src = _read_source()

    # Check that ensureConfiguredBrowserInstalled has the env var check
    assert "if (getAsBooleanFromENV('PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD'))" in src, \
        "ensureConfiguredBrowserInstalled should have env var check"

    # Check that resolveAndInstall has meaningful body
    assert "browserRegistry.install(executables)" in src, \
        "resolveAndInstall should call browserRegistry.install"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI checks that must pass before and after fix
# ---------------------------------------------------------------------------

def test_repo_build():
    """Repo builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-1000:]}"


def test_repo_eslint():
    """ESLint passes on modified cli-daemon directory (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "eslint", "--", "--max-warnings=0", "packages/playwright-core/src/tools/cli-daemon/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


def test_repo_lint_packages():
    """Workspace packages are consistent (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint packages failed:\n{r.stderr[-500:]}"


def test_repo_check_deps():
    """Dependency structure is valid (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "check-deps"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Check deps failed:\n{r.stderr[-500:]}"


def test_repo_eslint_env_utils():
    """ESLint passes on env utils module (imported by solution) (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "eslint", "--", "--max-warnings=0", "packages/playwright-core/src/server/utils/env.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint on env.ts failed:\n{r.stderr[-500:]}"


def test_repo_eslint_registry():
    """ESLint passes on browser registry (used by solution) (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "eslint", "--", "--max-warnings=0", "packages/playwright-core/src/server/registry/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint on registry failed:\n{r.stderr[-500:]}"


def test_repo_eslint_tools():
    """ESLint passes on all tools directory (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "eslint", "--", "--max-warnings=0", "packages/playwright-core/src/tools/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint on tools failed:\n{r.stderr[-500:]}"
