"""
Task: uv-freethreaded-macos-download-metadata
Repo: astral-sh/uv @ 635a76cad321b1fe3593a71dc7533cabbca244aa
PR:   astral-sh/uv#18601

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import importlib.util
import sys
import types
from pathlib import Path

import pytest

REPO = "/repo"
SCRIPT = f"{REPO}/crates/uv-python/fetch-download-metadata.py"


def _load_module():
    """Load fetch-download-metadata.py as a module, mocking httpx if absent."""
    if "httpx" not in sys.modules:
        try:
            import httpx  # noqa: F401
        except ImportError:
            httpx_mock = types.ModuleType("httpx")

            class _Client:
                pass

            httpx_mock.AsyncClient = _Client
            sys.modules["httpx"] = httpx_mock

    # Remove cached module to get fresh import each time
    if "fetch_dm" in sys.modules:
        del sys.modules["fetch_dm"]

    spec = importlib.util.spec_from_file_location("fetch_dm", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_finder(mod):
    return mod.CPythonFinder(client=None)


def _make_artifact(platform, variant="install_only_stripped", version_tag="3.15.0a7",
                   url_suffix=None, sha="abc123"):
    """Helper to build NDJSON artifact dicts with varied inputs."""
    if url_suffix is None:
        url_suffix = f"{platform}-{variant}"
    return {
        "url": f"https://example.com/cpython-{version_tag}%2B20260320-{url_suffix}.tar.gz",
        "sha256": sha,
        "platform": platform,
        "variant": variant,
    }


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """fetch-download-metadata.py must parse without syntax errors."""
    import ast

    src = Path(SCRIPT).read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_freethreaded_suffix_stripped():
    """Freethreaded suffix on macOS is stripped and promoted to build option
    across multiple architectures and versions."""
    mod = _load_module()
    finder = _make_finder(mod)

    cases = [
        ("aarch64-apple-darwin-freethreaded", mod.Version(3, 15, 0, "a7"), "arm64 3.15a7"),
        ("x86_64-apple-darwin-freethreaded", mod.Version(3, 14, 3, ""), "x86_64 3.14.3"),
        ("aarch64-apple-darwin-freethreaded", mod.Version(3, 13, 1, ""), "arm64 3.13.1"),
    ]

    for platform, version, label in cases:
        artifact = _make_artifact(platform, version_tag=str(version))
        result = finder._parse_ndjson_artifact(version, 20260320, artifact)
        assert result is not None, f"[{label}] returned None for freethreaded macOS artifact"
        assert "freethreaded" in result.build_options, (
            f"[{label}] build_options={result.build_options}, expected 'freethreaded'"
        )


# [pr_diff] fail_to_pass
def test_freethreaded_variant_set():
    """Variant is FREETHREADED for macOS freethreaded artifacts across versions."""
    mod = _load_module()
    finder = _make_finder(mod)

    cases = [
        ("x86_64-apple-darwin-freethreaded", mod.Version(3, 14, 3, ""), "x86_64 3.14.3"),
        ("aarch64-apple-darwin-freethreaded", mod.Version(3, 15, 0, "a7"), "arm64 3.15a7"),
        ("aarch64-apple-darwin-freethreaded", mod.Version(3, 13, 0, "rc2"), "arm64 3.13rc2"),
    ]

    for platform, version, label in cases:
        artifact = _make_artifact(platform, version_tag=str(version))
        result = finder._parse_ndjson_artifact(version, 20260320, artifact)
        assert result is not None, f"[{label}] returned None"
        assert result.variant == mod.Variant.FREETHREADED, (
            f"[{label}] variant={result.variant}, expected FREETHREADED"
        )


# [pr_diff] fail_to_pass
def test_freethreaded_triple_matches_normal():
    """Platform triple for freethreaded build matches the normal (non-freethreaded) build."""
    mod = _load_module()
    finder = _make_finder(mod)

    pairs = [
        ("aarch64-apple-darwin", "aarch64-apple-darwin-freethreaded", mod.Version(3, 15, 0, "a7")),
        ("x86_64-apple-darwin", "x86_64-apple-darwin-freethreaded", mod.Version(3, 14, 3, "")),
        ("aarch64-apple-darwin", "aarch64-apple-darwin-freethreaded", mod.Version(3, 13, 1, "")),
    ]

    for normal_plat, ft_plat, version in pairs:
        normal_art = _make_artifact(normal_plat, version_tag=str(version))
        ft_art = _make_artifact(ft_plat, version_tag=str(version))

        normal = finder._parse_ndjson_artifact(version, 20260320, normal_art)
        ft = finder._parse_ndjson_artifact(version, 20260320, ft_art)
        assert normal is not None and ft is not None, (
            f"one artifact returned None: normal={normal}, ft={ft}"
        )
        assert normal.triple == ft.triple, (
            f"triples differ: normal={normal.triple} vs freethreaded={ft.triple}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_debug_suffix_still_works():
    """Debug suffix on macOS is still stripped and promoted correctly (regression)."""
    mod = _load_module()
    finder = _make_finder(mod)

    cases = [
        ("aarch64-apple-darwin-debug", mod.Version(3, 14, 3, ""), "install_only"),
        ("x86_64-apple-darwin-debug", mod.Version(3, 13, 1, ""), "install_only_stripped"),
        ("aarch64-apple-darwin-debug", mod.Version(3, 15, 0, "a7"), "install_only"),
    ]

    for platform, version, variant in cases:
        artifact = _make_artifact(platform, variant=variant, version_tag=str(version))
        result = finder._parse_ndjson_artifact(version, 20260320, artifact)
        assert result is not None, f"returned None for debug artifact {platform}"
        assert "debug" in result.build_options, (
            f"build_options={result.build_options}, expected 'debug' for {platform}"
        )
        assert result.variant == mod.Variant.DEBUG, (
            f"variant={result.variant}, expected DEBUG for {platform}"
        )


# [pr_diff] pass_to_pass
def test_linux_platform_unaffected():
    """Non-macOS platforms are parsed correctly and unaffected by suffix stripping."""
    mod = _load_module()
    finder = _make_finder(mod)

    cases = [
        ("x86_64-unknown-linux-gnu", mod.Version(3, 14, 3, "")),
        ("aarch64-unknown-linux-gnu", mod.Version(3, 15, 0, "a7")),
        ("x86_64_v3-unknown-linux-gnu", mod.Version(3, 13, 1, "")),
    ]

    for platform, version in cases:
        artifact = _make_artifact(platform, version_tag=str(version))
        result = finder._parse_ndjson_artifact(version, 20260320, artifact)
        assert result is not None, f"returned None for linux artifact {platform}"
        assert result.triple.platform == "linux", (
            f"platform={result.triple.platform}, expected 'linux' for {platform}"
        )
        assert result.variant is None, (
            f"variant={result.variant}, expected None for plain linux {platform}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_not_stub():
    """The suffix-stripping block has real logic, not just pass/return."""
    import ast

    # AST-only because: verifying code structure (not behavior) for anti-stub gate
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
