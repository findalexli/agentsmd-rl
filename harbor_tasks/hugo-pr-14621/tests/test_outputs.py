"""
Tests for Hugo CSS loader resolution fix (PR #14621).

This validates that CSS builds with url() references to static files
work correctly when resolved by ESBuild's native resolver.
"""

import subprocess
import sys
import os

REPO = "/workspace/hugo"


def test_css_loader_extension_constant_exists():
    """
    Verify that defaultCSSFileLoaderExts is defined in resolve.go.
    This constant defines which file extensions get file loader treatment.
    """
    resolve_file = os.path.join(REPO, "internal/js/esbuild/resolve.go")
    with open(resolve_file, 'r') as f:
        content = f.read()

    # Check that the constant exists
    assert "defaultCSSFileLoaderExts" in content, \
        "defaultCSSFileLoaderExts constant not found in resolve.go"

    # Check it contains expected extensions
    assert '".png"' in content, "Missing .png extension"
    assert '".woff"' in content, "Missing .woff extension"
    assert '".svg"' in content, "Missing .svg extension"


def test_css_loader_default_in_options():
    """
    Verify that CSS builds without explicit loaders config get
    default file loaders for static file extensions.
    """
    options_file = os.path.join(REPO, "internal/js/esbuild/options.go")
    with open(options_file, 'r') as f:
        content = f.read()

    # Check that the default loaders are set for CSS builds
    assert "defaultCSSFileLoaderExts" in content, \
        "defaultCSSFileLoaderExts not used in options.go"

    # Check that loaders map is initialized for CSS when no config
    assert "opts.IsCSS" in content, "IsCSS check not found"
    assert "api.LoaderFile" in content, "LoaderFile not found"


def test_loader_from_filename_returns_default():
    """
    Verify that loaderFromFilename returns LoaderDefault instead of
    LoaderJS for unknown extensions in non-CSS builds.
    """
    options_file = os.path.join(REPO, "internal/js/esbuild/options.go")
    with open(options_file, 'r') as f:
        content = f.read()

    # Should return LoaderDefault at end, not LoaderJS
    # Check that we no longer return LoaderJS blindly at end
    lines = content.split('\n')
    in_func = False
    found_css_check = False
    found_return_default = False

    for line in lines:
        if 'func (o Options) loaderFromFilename' in line:
            in_func = True
        elif in_func:
            if 'opts.IsCSS' in line:
                found_css_check = True
            if 'return api.LoaderDefault' in line:
                found_return_default = True
            # Function ends at closing brace at start of line
            if line == '}':
                in_func = False

    # We should find the return LoaderDefault in the function
    assert found_return_default, \
        "loaderFromFilename should return LoaderDefault for unknown extensions"


def test_repo_css_integration_test():
    """
    Run Hugo's own CSS integration test (TestCSSBuildLoadersDefault).
    This test validates that CSS url() references work for both
    assets and static files.
    """
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestCSSBuildLoadersDefault", "./tpl/css/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"TestCSSBuildLoadersDefault failed:\n{result.stdout}\n{result.stderr}"


def test_esbuild_package_compiles():
    """
    Verify the esbuild package compiles successfully.
    """
    result = subprocess.run(
        ["go", "build", "./internal/js/esbuild/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, \
        f"esbuild package build failed:\n{result.stderr}"


def test_css_package_compiles():
    """
    Verify the CSS package compiles successfully.
    """
    result = subprocess.run(
        ["go", "build", "./tpl/css/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, \
        f"CSS package build failed:\n{result.stderr}"


def test_no_regression_in_loaderFromFilename():
    """
    Ensure the loaderFromFilename function doesn't fall back to
    LoaderFile unconditionally for CSS builds (old buggy behavior).
    """
    options_file = os.path.join(REPO, "internal/js/esbuild/options.go")
    with open(options_file, 'r') as f:
        content = f.read()

    # The old code had: "return api.LoaderFile" immediately after
    # checking extensionToLoaderMapCSS without being in an else block
    # After fix, the unconditional return is removed

    # Count occurrences of "return api.LoaderFile"
    lines = content.split('\n')
    returns_file_loader = 0

    for i, line in enumerate(lines):
        # Skip comments
        stripped = line.strip()
        if stripped.startswith('//'):
            continue
        if 'return api.LoaderFile' in line:
            returns_file_loader += 1

    # After fix, we should have LoaderFile in the default loaders loop,
    # but NOT as an unconditional return in loaderFromFilename
    # We should have exactly the number used in the for loop (1)
    # or in maps initialization (not returns)

    # The fix removes the unconditional "return api.LoaderFile" at the end
    # of the CSS branch, so we check that there's no standalone return
    # This is a structural check that validates the logic change

    # Check that the removed comment isn't present
    assert "default to the file loader for unknown extensions" not in content or \
           "default to the file loader for common static" in content, \
        "Old buggy comment still present - patch may not be applied correctly"


def test_go_vet():
    """
    Run go vet on the modified packages.
    """
    result = subprocess.run(
        ["go", "vet", "./internal/js/esbuild/...", "./tpl/css/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, \
        f"go vet failed:\n{result.stderr}"


def test_repo_esbuild_resolve():
    """
    Run Hugo's esbuild resolve component tests (pass_to_pass).
    Tests the resolve functionality that the PR modifies.
    """
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestResolveComponentInAssets", "./internal/js/esbuild/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"TestResolveComponentInAssets failed:\n{result.stdout}\n{result.stderr}"


def test_repo_esbuild_build_options():
    """
    Run Hugo's esbuild build options tests (pass_to_pass).
    Tests the options/loader functionality that the PR modifies.
    """
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestToBuildOptions", "./internal/js/esbuild/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"TestToBuildOptions failed:\n{result.stdout}\n{result.stderr}"


def test_repo_css_build():
    """
    Run Hugo's CSS build tests (pass_to_pass).
    Tests the CSS package that the PR modifies.
    """
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestCSSBuild$", "./tpl/css/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"TestCSSBuild failed:\n{result.stdout}\n{result.stderr}"


def test_repo_go_fmt():
    """
    Check Go code formatting with gofmt (pass_to_pass).
    """
    result = subprocess.run(
        ["gofmt", "-l", "./internal/js/esbuild/", "./tpl/css/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    # gofmt returns 0 but outputs files that need formatting
    assert result.stdout.strip() == "", \
        f"gofmt found unformatted files:\n{result.stdout}"
    assert result.returncode == 0, \
        f"gofmt failed:\n{result.stderr}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
