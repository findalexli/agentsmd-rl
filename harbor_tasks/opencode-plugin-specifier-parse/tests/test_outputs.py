"""
Task: opencode-plugin-specifier-parse
Repo: anomalyco/opencode @ 3a0e00dd7f9192730f6d0eeee37ae0a5fb023927
PR:   #21135

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
PKG = f"{REPO}/packages/opencode"
RESULTS_PATH = "/tmp/_parse_specifier_results.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_bun(code: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Write a temp TypeScript file and execute it with bun."""
    script = Path(PKG) / "_test_eval.ts"
    script.write_text(code)
    try:
        return subprocess.run(
            ["bun", "run", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=PKG,
        )
    finally:
        script.unlink(missing_ok=True)


_results = None
_error = None


def _load_all_results() -> dict:
    """Run parsePluginSpecifier on all test specs in one bun invocation."""
    code = (
        'import { parsePluginSpecifier } from "./src/plugin/shared"\n'
        "const specs = [\n"
        '  "acme",\n'
        '  "acme@1.0.0",\n'
        '  "@opencode/acme",\n'
        '  "@opencode/acme@1.0.0",\n'
        '  "acme@git+ssh://git@github.com/opencode/acme.git",\n'
        '  "@opencode/acme@git+ssh://git@github.com/opencode/acme.git",\n'
        '  "npm:@opencode/acme@1.0.0",\n'
        '  "npm:@opencode/acme",\n'
        '  "acme@npm:@opencode/acme@1.0.0",\n'
        "]\n"
        "const results: Record<string, any> = {}\n"
        "for (const spec of specs) {\n"
        "  results[spec] = parsePluginSpecifier(spec)\n"
        "}\n"
        f"await Bun.write({json.dumps(RESULTS_PATH)}, JSON.stringify(results))\n"
    )
    r = _run_bun(code)
    assert r.returncode == 0, (
        f"Failed to evaluate parsePluginSpecifier:\n{r.stderr}\n{r.stdout}"
    )
    data = json.loads(Path(RESULTS_PATH).read_text())
    Path(RESULTS_PATH).unlink(missing_ok=True)
    return data


def _get(spec: str) -> dict:
    """Get cached parse result for a specifier."""
    global _results, _error
    if _error is not None:
        raise AssertionError(_error)
    if _results is None:
        try:
            _results = _load_all_results()
        except Exception as e:
            _error = str(e)
            raise
    return _results[spec]


# ---------------------------------------------------------------------------
# Pass-to-pass — import sanity and basic specifiers
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_modified_files_importable():
    """Both modified TypeScript source files must import without errors."""
    code = 'import "./src/plugin/shared"\nimport "./src/npm/index"\n'
    r = _run_bun(code)
    assert r.returncode == 0, f"Import failed:\n{r.stderr}"


# [pr_diff] pass_to_pass
def test_parse_basic_specifiers():
    """Simple and scoped package specifiers must still parse correctly."""
    r = _get("acme")
    assert r["pkg"] == "acme"
    assert r["version"] == "latest"

    r = _get("acme@1.0.0")
    assert r["pkg"] == "acme"
    assert r["version"] == "1.0.0"

    r = _get("@opencode/acme")
    assert r["pkg"] == "@opencode/acme"
    assert r["version"] == "latest"

    r = _get("@opencode/acme@1.0.0")
    assert r["pkg"] == "@opencode/acme"
    assert r["version"] == "1.0.0"


# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (tsgo --noEmit in packages/opencode)."""
    r = subprocess.run(
        ["bun", "run", "typecheck"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=PKG,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's unit tests pass (bun test --timeout 30000 in packages/opencode).

    Note: The repo has 3 pre-existing test failures unrelated to this PR.
    We check that at least 1824 tests pass (the expected count).
    """
    r = subprocess.run(
        ["bun", "test", "--timeout", "30000"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=PKG,
    )
    # Check that tests ran and we got the expected pass count
    # The repo has 3 pre-existing failures; we verify the fix doesn't add more
    output = r.stdout + r.stderr
    pass_count = 0
    for line in output.split("\n"):
        if "pass" in line and line.strip() and line.strip()[0].isdigit():
            try:
                pass_count = int(line.strip().split()[0])
                break
            except (ValueError, IndexError):
                continue
    assert pass_count >= 1824, (
        f"Expected at least 1824 passing tests, got {pass_count}.\n"
        f"Output tail:\n{output[-800:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_parse_git_ssh_urls():
    """git+ssh URLs with embedded @ in the host must be correctly parsed.

    The old lastIndexOf('@') approach splits at the wrong @ character,
    producing garbage package names like 'acme@git+ssh://git'.
    """
    r = _get("acme@git+ssh://git@github.com/opencode/acme.git")
    assert r["pkg"] == "acme", f"Expected pkg='acme', got {r['pkg']!r}"
    assert r["version"] == "git+ssh://git@github.com/opencode/acme.git"

    r2 = _get("@opencode/acme@git+ssh://git@github.com/opencode/acme.git")
    assert r2["pkg"] == "@opencode/acme", (
        f"Expected pkg='@opencode/acme', got {r2['pkg']!r}"
    )
    assert r2["version"] == "git+ssh://git@github.com/opencode/acme.git"


# [pr_diff] fail_to_pass
def test_parse_bare_npm_protocol():
    """npm:@scope/pkg@version must extract the scoped package name without prefix.

    The old code keeps the 'npm:' prefix in the package name.
    """
    r = _get("npm:@opencode/acme@1.0.0")
    assert r["pkg"] == "@opencode/acme", (
        f"Expected pkg='@opencode/acme', got {r['pkg']!r}"
    )
    assert r["version"] == "1.0.0"


# [pr_diff] fail_to_pass
def test_parse_unversioned_npm_protocol():
    """npm:@scope/pkg (no version) must return pkg='@scope/pkg' with version 'latest'.

    The old lastIndexOf('@') splits at the scope @, producing pkg='npm:'.
    """
    r = _get("npm:@opencode/acme")
    assert r["pkg"] == "@opencode/acme", (
        f"Expected pkg='@opencode/acme', got {r['pkg']!r}"
    )
    assert r["version"] == "latest"


# [pr_diff] fail_to_pass
def test_parse_npm_alias():
    """pkg@npm:@scope/pkg@version must keep the alias name as pkg.

    The old code splits at the last @ and produces a garbled package name.
    """
    r = _get("acme@npm:@opencode/acme@1.0.0")
    assert r["pkg"] == "acme", f"Expected pkg='acme', got {r['pkg']!r}"
    assert r["version"] == "npm:@opencode/acme@1.0.0"
