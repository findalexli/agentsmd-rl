"""
Test suite for Hugo CSS external source maps fix.
Tests validate that:
1. External source maps properly resolve source file paths
2. Source map sources are correctly filtered and processed
3. Repo tests pass after the fix
"""

import json
import os
import subprocess
import sys

REPO = "/workspace/hugo"

# Path constants for the files modified in this PR
SOURCEMAP_GO = os.path.join(REPO, "internal/js/esbuild/sourcemap.go")
BUILD_GO = os.path.join(REPO, "internal/js/esbuild/build.go")
CSS_TEST_GO = os.path.join(REPO, "tpl/css/build_integration_test.go")
JS_TEST_GO = os.path.join(REPO, "resources/resource_transformers/js/js_integration_test.go")


def test_sourcemap_fix_behavior():
    """
    Fail-to-pass test: Verify sourcemap.go properly handles source filtering.

    The fix changes how sources are processed - instead of a separate function,
    sources are now filtered inline with proper source content alignment.
    """
    # The fix ensures that sources are properly filtered when resolve() returns empty
    # We need to verify the code structure contains the fix

    with open(SOURCEMAP_GO, 'r') as f:
        content = f.read()

    # After fix: should have inline loop processing sources with sourcesContent alignment
    # The fix adds a loop that processes sources and tracks sourcesContent together
    assert "hasSourcesContent := len(sm.SourcesContent) == len(sm.Sources)" in content, \
        "Missing hasSourcesContent check in sourcemap.go"

    # Should have the inline loop that filters sources
    assert "for i, src := range sm.Sources" in content, \
        "Missing inline source processing loop in sourcemap.go"

    # Should track sourcesContent alongside sources
    assert "sourcesContent = append(sourcesContent, sm.SourcesContent[i])" in content, \
        "Missing sourcesContent alignment in sourcemap.go"

    # The old fixSourceMapSources function should be removed
    assert "func fixSourceMapSources" not in content, \
        "Old fixSourceMapSources function should be removed from sourcemap.go"


def test_build_go_source_resolution():
    """
    Fail-to-pass test: Verify build.go returns absolute filenames for source files.

    The fix adds logic to distinguish between output files (in OutDir) and source files.
    """
    with open(BUILD_GO, 'r') as f:
        content = f.read()

    # After fix: should check if path is an output file
    assert 'strings.HasPrefix(s, opts.OutDir)' in content, \
        "Missing OutDir prefix check in build.go"

    # Should have comment explaining the fix
    assert "s is already the absolute filename set by the Hugo resolve plugin" in content, \
        "Missing explanatory comment in build.go"

    # Should return s (the absolute filename) for source files
    assert "// This is an output file, not a source file." in content, \
        "Missing output file detection comment in build.go"


def test_css_integration_source_count():
    """
    Fail-to-pass test: Verify CSS integration test checks for correct source count.

    The fix ensures that external source maps include all 4 CSS sources.
    The test was updated from checking 4 sources to properly validating source count.
    """
    with open(CSS_TEST_GO, 'r') as f:
        content = f.read()

    # Should import esbuild package for source validation
    assert '"github.com/gohugoio/hugo/internal/js/esbuild"' in content, \
        "Missing esbuild import in CSS integration test"

    # Should import quicktest for assertions
    assert 'qt "github.com/frankban/quicktest"' in content, \
        "Missing quicktest import in CSS integration test"

    # Should validate source count equals 4 (main.css + foo.css + bar.css + baz.css)
    assert 'b.Assert(len(sources), qt.Equals, 4)' in content, \
        "Missing source count assertion (4 sources) in CSS integration test"

    # Should call SourcesFromSourceMap
    assert 'sources := esbuild.SourcesFromSourceMap(' in content, \
        "Missing SourcesFromSourceMap call in CSS integration test"


def test_js_integration_source_count():
    """
    Fail-to-pass test: Verify JS integration test expects correct source count.

    The test was updated from 4 to 5 expected sources in the source map.
    """
    with open(JS_TEST_GO, 'r') as f:
        content = f.read()

    # Look for the checkMap call with 5 sources (was 4 before fix)
    # This validates that the source map now includes all expected sources
    assert 'checkMap("public/js/main.js.map", 5)' in content, \
        "JS integration test should expect 5 sources in source map (was 4 before fix)"


def test_css_test_loop_variations():
    """
    Fail-to-pass test: Verify CSS tests run with both minify=true and minify=false.

    The fix adds a loop to test both minified and unminified CSS builds.
    """
    with open(CSS_TEST_GO, 'r') as f:
        content = f.read()

    # Should have loop over minify values
    assert 'for _, minify := range []string{"true", "false"}' in content, \
        "Missing minify loop in CSS integration test"

    # Should have MINIFY placeholder replacement
    assert '"MINIFY", minify,' in content, \
        "Missing MINIFY placeholder replacement in CSS integration test"


def test_repo_css_integration_tests():
    """
    Pass-to-pass test: Hugo's CSS integration tests pass.

    Run the CSS build integration tests to verify they work correctly.
    """
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestCSSBuild", "./tpl/css/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, \
        f"CSS integration tests failed:\n{result.stderr[-1000:]}\n{result.stdout[-500:]}"


def test_repo_sourcemap_package_tests():
    """
    Pass-to-pass test: Hugo's sourcemap package tests pass.

    Run tests for the esbuild sourcemap package.
    """
    result = subprocess.run(
        ["go", "test", "-v", "./internal/js/esbuild/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, \
        f"Esbuild package tests failed:\n{result.stderr[-1000:]}\n{result.stdout[-500:]}"


def test_repo_js_integration_tests():
    """
    Pass-to-pass test: Hugo's JS integration tests pass.

    Run the JS build integration tests.
    """
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestBuildJS", "./resources/resource_transformers/js/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, \
        f"JS integration tests failed:\n{result.stderr[-1000:]}\n{result.stdout[-500:]}"


def test_go_build():
    """
    Pass-to-pass test: Hugo compiles successfully.

    Verify the Go code compiles without errors.
    """
    result = subprocess.run(
        ["go", "build", "-o", "/tmp/hugo", "./"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, \
        f"Hugo build failed:\n{result.stderr[-1000:]}"


def test_go_vet():
    """
    Pass-to-pass test: Hugo passes go vet static analysis.
    """
    result = subprocess.run(
        ["go", "vet", "./internal/js/esbuild/...", "./tpl/css/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"go vet failed:\n{result.stderr[-500:]}"


def test_gofmt():
    """
    Pass-to-pass test: Hugo code passes gofmt formatting check.

    Repo CI runs gofmt to ensure code formatting is consistent.
    """
    result = subprocess.run(
        ["gofmt", "-l", "./internal/js/esbuild/", "./tpl/css/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, \
        f"gofmt check failed:\n{result.stderr[-500:]}"
    assert result.stdout.strip() == "", \
        f"gofmt found formatting issues in:\n{result.stdout}"


def test_staticcheck():
    """
    Pass-to-pass test: Hugo passes staticcheck linter.

    Repo CI runs staticcheck for static analysis.
    """
    # Install staticcheck if not already installed
    install_result = subprocess.run(
        ["go", "install", "honnef.co/go/tools/cmd/staticcheck@latest"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    # Run staticcheck on the modified packages
    result = subprocess.run(
        ["staticcheck", "./internal/js/esbuild/...", "./tpl/css/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, \
        f"staticcheck failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_go_mod_verify():
    """
    Pass-to-pass test: Hugo go.mod is valid and dependencies are clean.
    """
    result = subprocess.run(
        ["go", "mod", "verify"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, \
        f"go mod verify failed:\n{result.stderr[-500:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_brew():
    """pass_to_pass | CI job 'test' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'brew install pandoc'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_choco():
    """pass_to_pass | CI job 'test' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'choco install pandoc'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_pandoc():
    """pass_to_pass | CI job 'test' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pandoc -v'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_choco():
    """pass_to_pass | CI job 'test' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'choco install mingw'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_staticcheck():
    """pass_to_pass | CI job 'test' → step 'Run staticcheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'export STATICCHECK_CACHE="${{ runner.temp }}/staticcheck"\nstaticcheck ./...\nrm -rf ${{ runner.temp }}/staticcheck'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step 'Run staticcheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_check():
    """pass_to_pass | CI job 'test' → step 'Check'"""
    r = subprocess.run(
        ["bash", "-lc", 'sass --version;\nmage -v check;'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step 'Check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_test():
    """pass_to_pass | CI job 'test' → step 'Test'"""
    r = subprocess.run(
        ["bash", "-lc", 'mage -v test'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step 'Test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_build_for_dragonfly():
    """pass_to_pass | CI job 'test' → step 'Build for dragonfly'"""
    r = subprocess.run(
        ["bash", "-lc", 'go install\ngo clean -i -cache'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step 'Build for dragonfly' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")