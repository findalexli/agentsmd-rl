"""
Task: uv-freethreaded-macos-download-metadata
Repo: astral-sh/uv @ 635a76cad321b1fe3593a71dc7533cabbca244aa
PR:   astral-sh/uv#18601

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
from pathlib import Path

import pytest

REPO = "/repo"
SCRIPT = f"{REPO}/crates/uv-python/fetch-download-metadata.py"

# Boilerplate injected into every subprocess to mock httpx and load the module.
_MOCK_PREAMBLE = r"""
import sys as _sys, types as _types
try:
    import httpx as _hx  # noqa: F401
except ImportError:
    _hx_mock = _types.ModuleType("httpx")
    class _Client:
        pass
    _hx_mock.AsyncClient = _Client
    _sys.modules["httpx"] = _hx_mock

import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("fetch_dm", "crates/uv-python/fetch-download-metadata.py")
mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(mod)

finder = mod.CPythonFinder(client=None)

def _artifact(platform, variant="install_only_stripped", version_tag=None, sha="abc123"):
    vt = version_tag or "3.15.0a7"
    return {
        "url": f"https://example.com/cpython-{vt}%2B20260320-{platform}-{variant}.tar.gz",
        "sha256": sha,
        "platform": platform,
        "variant": variant,
    }
"""


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo directory via subprocess."""
    script = Path(REPO) / "_eval_tmp.py"
    script.write_text(_MOCK_PREAMBLE + code)
    try:
        return subprocess.run(
            [sys.executable, str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """fetch-download-metadata.py must parse without syntax errors."""
    src = Path(SCRIPT).read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_freethreaded_suffix_stripped():
    """Freethreaded suffix on macOS is stripped and promoted to build option."""
    r = _run_py("""
cases = [
    ("aarch64-apple-darwin-freethreaded", mod.Version(3, 15, 0, "a7")),
    ("x86_64-apple-darwin-freethreaded", mod.Version(3, 14, 3, "")),
    ("aarch64-apple-darwin-freethreaded", mod.Version(3, 13, 1, "")),
]
for platform, version in cases:
    artifact = _artifact(platform, version_tag=str(version))
    result = finder._parse_ndjson_artifact(version, 20260320, artifact)
    assert result is not None, f"returned None for {platform}"
    assert "freethreaded" in result.build_options, (
        f"build_options={result.build_options} for {platform}, expected 'freethreaded'"
    )
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_freethreaded_variant_set():
    """Variant is FREETHREADED for macOS freethreaded artifacts across versions."""
    r = _run_py("""
cases = [
    ("x86_64-apple-darwin-freethreaded", mod.Version(3, 14, 3, "")),
    ("aarch64-apple-darwin-freethreaded", mod.Version(3, 15, 0, "a7")),
    ("aarch64-apple-darwin-freethreaded", mod.Version(3, 13, 0, "rc2")),
]
for platform, version in cases:
    artifact = _artifact(platform, version_tag=str(version))
    result = finder._parse_ndjson_artifact(version, 20260320, artifact)
    assert result is not None, f"returned None for {platform}"
    assert result.variant == mod.Variant.FREETHREADED, (
        f"variant={result.variant} for {platform}, expected FREETHREADED"
    )
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_freethreaded_triple_matches_normal():
    """Platform triple for freethreaded build matches the normal build."""
    r = _run_py("""
pairs = [
    ("aarch64-apple-darwin", "aarch64-apple-darwin-freethreaded", mod.Version(3, 15, 0, "a7")),
    ("x86_64-apple-darwin", "x86_64-apple-darwin-freethreaded", mod.Version(3, 14, 3, "")),
    ("aarch64-apple-darwin", "aarch64-apple-darwin-freethreaded", mod.Version(3, 13, 1, "")),
]
for normal_plat, ft_plat, version in pairs:
    normal_art = _artifact(normal_plat, version_tag=str(version))
    ft_art = _artifact(ft_plat, version_tag=str(version), sha="def456")
    normal = finder._parse_ndjson_artifact(version, 20260320, normal_art)
    ft = finder._parse_ndjson_artifact(version, 20260320, ft_art)
    assert normal is not None and ft is not None, (
        f"one artifact None: normal={normal}, ft={ft}"
    )
    assert normal.triple == ft.triple, (
        f"triples differ: normal={normal.triple} vs freethreaded={ft.triple}"
    )
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests via subprocess
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_debug_suffix_still_works():
    """Debug suffix on macOS is still stripped and promoted correctly (regression)."""
    r = _run_py("""
cases = [
    ("aarch64-apple-darwin-debug", mod.Version(3, 14, 3, ""), "install_only"),
    ("x86_64-apple-darwin-debug", mod.Version(3, 13, 1, ""), "install_only_stripped"),
    ("aarch64-apple-darwin-debug", mod.Version(3, 15, 0, "a7"), "install_only"),
]
for platform, version, variant in cases:
    artifact = _artifact(platform, variant=variant, version_tag=str(version))
    result = finder._parse_ndjson_artifact(version, 20260320, artifact)
    assert result is not None, f"returned None for debug artifact {platform}"
    assert "debug" in result.build_options, (
        f"build_options={result.build_options} for {platform}, expected 'debug'"
    )
    assert result.variant == mod.Variant.DEBUG, (
        f"variant={result.variant} for {platform}, expected DEBUG"
    )
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] pass_to_pass
def test_linux_platform_unaffected():
    """Non-macOS platforms are parsed correctly and unaffected by suffix stripping."""
    r = _run_py("""
cases = [
    ("x86_64-unknown-linux-gnu", mod.Version(3, 14, 3, "")),
    ("aarch64-unknown-linux-gnu", mod.Version(3, 15, 0, "a7")),
    ("x86_64_v3-unknown-linux-gnu", mod.Version(3, 13, 1, "")),
]
for platform, version in cases:
    artifact = _artifact(platform, version_tag=str(version))
    result = finder._parse_ndjson_artifact(version, 20260320, artifact)
    assert result is not None, f"returned None for linux artifact {platform}"
    assert result.triple.platform == "linux", (
        f"platform={result.triple.platform} for {platform}, expected 'linux'"
    )
    assert result.variant is None, (
        f"variant={result.variant} for {platform}, expected None"
    )
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static / agent_config) — AST-based checks
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — CLAUDE.md:16 @ 635a76cad321b1fe3593a71dc7533cabbca244aa
def test_no_local_imports():
    """fetch-download-metadata.py has no import statements inside function or method bodies."""
    src = Path(SCRIPT).read_text()
    tree = ast.parse(src)

    violations = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for child in ast.walk(node):
                if child is node:
                    continue
                if isinstance(child, (ast.Import, ast.ImportFrom)):
                    violations.append(
                        f"line {child.lineno}: import inside function '{node.name}'"
                    )
    assert not violations, (
        "Local imports found (CLAUDE.md:16 — prefer top-level imports):\n"
        + "\n".join(violations)
    )


# [static] pass_to_pass
def test_not_stub():
    """The _parse_ndjson_artifact method has real logic, not just pass/return."""
    src = Path(SCRIPT).read_text()
    tree = ast.parse(src)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_parse_ndjson_artifact":
            body_stmts = [
                s for s in node.body
                if not isinstance(s, (ast.Pass, ast.Expr))
                or (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
            ]
            assert len(body_stmts) >= 5, (
                f"_parse_ndjson_artifact body has only {len(body_stmts)} statements — looks like a stub"
            )
            found = True
            break
    assert found, "_parse_ndjson_artifact method not found"
