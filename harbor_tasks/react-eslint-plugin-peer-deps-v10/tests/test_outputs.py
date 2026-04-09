"""
Task: react-eslint-plugin-peer-deps-v10
Repo: facebook/react @ 03ca38e6e7b84cf20438c1d333636b3d662ca726
PR:   35720

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/react"
PKG_PATH = Path(f"{REPO}/packages/eslint-plugin-react-hooks/package.json")


def _load_pkg():
    return json.loads(PKG_PATH.read_text())


def _eslint_range():
    return _load_pkg().get("peerDependencies", {}).get("eslint", "")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — structure / validity checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_package_json_valid():
    """package.json is valid JSON and readable."""
    data = json.loads(PKG_PATH.read_text())
    assert isinstance(data, dict), "package.json must be a JSON object"


# [static] pass_to_pass
def test_package_structure_intact():
    """Essential package fields (name, version, peerDependencies) are present."""
    pkg = _load_pkg()
    assert pkg.get("name") == "eslint-plugin-react-hooks", f"name wrong: {pkg.get(name)}"
    assert "version" in pkg, "version field missing"
    assert isinstance(pkg.get("peerDependencies"), dict), "peerDependencies must be an object"
    assert "eslint" in pkg["peerDependencies"], "eslint missing from peerDependencies"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_eslint_v10_in_peer_deps():
    """peerDependencies.eslint must include ^10.0.0."""
    r = _eslint_range()
    assert "^10.0.0" in r, (
        f"ESLint v10 not declared in peerDependencies. Got: {r!r}"
    )


# [pr_diff] fail_to_pass
def test_v10_uses_or_separator():
    """ESLint v10 must be appended with the '|| ^10.0.0' OR pattern, consistent with existing entries."""
    r = _eslint_range()
    assert "|| ^10.0.0" in r, (
        f"Expected '|| ^10.0.0' OR format, consistent with existing entries. Got: {r!r}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression / anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_backward_compat_maintained():
    """ESLint versions 3–9 must remain in the peerDependency range."""
    r = _eslint_range()
    expected = ["^3.0.0", "^4.0.0", "^5.0.0", "^6.0.0", "^7.0.0", "^8.0.0-0", "^9.0.0"]
    missing = [v for v in expected if v not in r]
    assert not missing, (
        f"Backward compatibility broken — missing from range: {missing}. Got: {r!r}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's ESLint check passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/tasks/eslint.js"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_eslint_plugin_tests():
    """eslint-plugin-react-hooks tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/packages/eslint-plugin-react-hooks",
    )
    assert r.returncode == 0, f"Tests failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"
