"""
Test suite for Hugo CSS external source maps fix.
Tests validate that:
1. External source maps properly resolve source file paths (behavioral f2p)
2. Source maps work with both minified and unminified CSS (behavioral f2p)
3. Repo tests pass at both base and gold (pass-to-pass)
"""

import json
import os
import subprocess
import sys
import tempfile

REPO = "/workspace/hugo"


def _build_hugo():
    """Build Hugo binary and return path, caching at /tmp/hugo."""
    hugo_bin = "/tmp/hugo"
    if not os.path.exists(hugo_bin):
        result = subprocess.run(
            ["go", "build", "-o", hugo_bin, "./"],
            cwd=REPO, capture_output=True, text=True, timeout=600
        )
        assert result.returncode == 0, f"go build failed:\n{result.stderr[-1000:]}"
    return hugo_bin


def _create_hugo_project(tmpdir, minify="true", source_map="external"):
    """Create a minimal Hugo project with CSS imports for testing source maps."""
    os.makedirs(f"{tmpdir}/assets/css", exist_ok=True)
    os.makedirs(f"{tmpdir}/layouts/_default", exist_ok=True)

    with open(f"{tmpdir}/hugo.toml", "w") as f:
        f.write('baseURL = "http://example.org/"\n')

    with open(f"{tmpdir}/assets/css/main.css", "w") as f:
        f.write('@import "./foo.css";\n@import "./bar.css";\n@import "./baz.css";\n.main { color: red; }\n')

    with open(f"{tmpdir}/assets/css/foo.css", "w") as f:
        f.write(".foo { color: blue; }\n")

    with open(f"{tmpdir}/assets/css/bar.css", "w") as f:
        f.write(".bar { color: green; }\n")

    with open(f"{tmpdir}/assets/css/baz.css", "w") as f:
        f.write(".baz { color: yellow; }\n")

    with open(f"{tmpdir}/layouts/index.html", "w") as f:
        f.write(
            '{{ with resources.Get "css/main.css" }}\n'
            '{{ $opts := (dict "minify" MINIFY "sourceMap" "SOURCE_MAP" "sourcesContent" true) }}\n'
            '{{ with . | css.Build $opts }}\n'
            '<link rel="stylesheet" href="{{ .RelPermalink }}">\n'
            '{{ end }}\n'
            '{{ end }}'
            .replace("MINIFY", minify).replace("SOURCE_MAP", source_map)
        )


# === fail_to_pass tests ===

def test_css_external_sourcemap_sources():
    """f2p: CSS external source map has populated sources array after fix.

    At base (unfixed), the resolve function returns "" for source files
    not found by the assets resolver, leaving the source map sources
    empty. At gold, source files get their absolute filenames preserved.
    """
    hugo = _build_hugo()

    with tempfile.TemporaryDirectory() as tmpdir:
        _create_hugo_project(tmpdir, minify="true", source_map="external")

        result = subprocess.run(
            [hugo, "--source", tmpdir],
            capture_output=True, text=True, timeout=120
        )
        assert result.returncode == 0, f"Hugo build failed: {result.stderr[-800:]}"

        map_path = os.path.join(tmpdir, "public", "css", "main.css.map")
        assert os.path.exists(map_path), "Source map file was not generated"

        with open(map_path) as f:
            sm = json.load(f)

        sources = sm.get("sources", [])
        assert len(sources) >= 2, (
            f"Source map sources should have at least 2 entries, "
            f"got {len(sources)}: {sources}"
        )

        source_basenames = [os.path.basename(s) for s in sources]
        for expected in ["main.css", "foo.css"]:
            assert expected in source_basenames, (
                f"'{expected}' missing from source map sources: {sources}"
            )


def test_css_unminified_sourcemap_sources():
    """f2p: Unminified CSS external source map also has populated sources.

    Tests with minify=false to verify the fix works across minify
    configurations (varying the input parameter).
    """
    hugo = _build_hugo()

    with tempfile.TemporaryDirectory() as tmpdir:
        _create_hugo_project(tmpdir, minify="false", source_map="external")

        result = subprocess.run(
            [hugo, "--source", tmpdir],
            capture_output=True, text=True, timeout=120
        )
        assert result.returncode == 0, f"Hugo build failed: {result.stderr[-800:]}"

        map_path = os.path.join(tmpdir, "public", "css", "main.css.map")
        assert os.path.exists(map_path), "Source map file was not generated"

        with open(map_path) as f:
            sm = json.load(f)

        sources = sm.get("sources", [])
        assert len(sources) >= 2, (
            f"Unminified source map sources should have at least 2 entries, "
            f"got {len(sources)}: {sources}"
        )

        source_strings = " ".join(sources)
        assert "main.css" in source_strings, (
            f"'main.css' missing from unminified source map sources: {sources}"
        )


# === pass_to_pass tests ===

def test_repo_css_integration_tests():
    """p2p: Hugo's CSS build integration tests pass."""
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestCSSBuild", "./tpl/css/"],
        cwd=REPO, capture_output=True, text=True, timeout=300
    )
    assert result.returncode == 0, (
        f"CSS integration tests failed:\n{result.stderr[-1000:]}\n{result.stdout[-500:]}"
    )


def test_repo_sourcemap_package_tests():
    """p2p: Hugo's esbuild sourcemap package tests pass."""
    result = subprocess.run(
        ["go", "test", "-v", "./internal/js/esbuild/..."],
        cwd=REPO, capture_output=True, text=True, timeout=300
    )
    assert result.returncode == 0, (
        f"Esbuild package tests failed:\n{result.stderr[-1000:]}\n{result.stdout[-500:]}"
    )


def test_repo_js_integration_tests():
    """p2p: Hugo's JS build integration tests pass."""
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestBuildJS",
         "./resources/resource_transformers/js/..."],
        cwd=REPO, capture_output=True, text=True, timeout=300
    )
    assert result.returncode == 0, (
        f"JS integration tests failed:\n{result.stderr[-1000:]}\n{result.stdout[-500:]}"
    )


def test_go_build():
    """p2p: Hugo compiles successfully."""
    result = subprocess.run(
        ["go", "build", "./..."],
        cwd=REPO, capture_output=True, text=True, timeout=600
    )
    assert result.returncode == 0, (
        f"Hugo build failed:\n{result.stderr[-1000:]}"
    )


def test_go_vet():
    """p2p: Modified packages pass go vet static analysis."""
    result = subprocess.run(
        ["go", "vet", "./internal/js/esbuild/...", "./tpl/css/..."],
        cwd=REPO, capture_output=True, text=True, timeout=120
    )
    assert result.returncode == 0, (
        f"go vet failed:\n{result.stderr[-500:]}"
    )


def test_gofmt():
    """p2p: Modified packages pass gofmt formatting check."""
    result = subprocess.run(
        ["gofmt", "-l", "./internal/js/esbuild/", "./tpl/css/"],
        cwd=REPO, capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, (
        f"gofmt check failed:\n{result.stderr[-500:]}"
    )
    assert result.stdout.strip() == "", (
        f"gofmt found formatting issues in:\n{result.stdout}"
    )


def test_go_mod_verify():
    """p2p: Hugo go.mod is valid and dependencies are clean."""
    result = subprocess.run(
        ["go", "mod", "verify"],
        cwd=REPO, capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, (
        f"go mod verify failed:\n{result.stderr[-500:]}"
    )


def test_staticcheck():
    """p2p: Modified packages pass staticcheck linter."""
    install_result = subprocess.run(
        ["go", "install", "honnef.co/go/tools/cmd/staticcheck@latest"],
        cwd=REPO, capture_output=True, text=True, timeout=180
    )

    result = subprocess.run(
        ["staticcheck", "./internal/js/esbuild/...", "./tpl/css/..."],
        cwd=REPO, capture_output=True, text=True, timeout=180
    )

    assert result.returncode == 0, (
        f"staticcheck failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"
    )
