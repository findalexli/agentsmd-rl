"""
Test outputs for hugo-minify-svg-namespaces benchmark.

This tests that SVG minification properly preserves Alpine.js directives
(x-bind:href, :href) by configuring KeepNamespaces in the minifier.
"""

import subprocess
import sys
import os

# Path to the hugo repo inside the container
REPO = "/workspace/hugo"


def test_go_mod_dependencies_updated():
    """
    Fail-to-pass: Verify that tdewolff/minify dependency is updated to v2.24.11.

    This ensures the fix includes the required dependency update.
    """
    go_mod_path = os.path.join(REPO, "go.mod")
    with open(go_mod_path, "r") as f:
        content = f.read()

    # Check for the updated minify version
    assert "github.com/tdewolff/minify/v2 v2.24.11" in content, \
        "tdewolff/minify dependency not updated to v2.24.11"


def test_config_has_keep_namespaces():
    """
    Fail-to-pass: Verify that KeepNamespaces is configured in minifiers/config.go.

    This ensures the configuration change is present.
    """
    config_path = os.path.join(REPO, "minifiers/config.go")
    with open(config_path, "r") as f:
        content = f.read()

    # Check for the KeepNamespaces configuration
    assert 'KeepNamespaces: []string{"", "x-bind"}' in content, \
        "KeepNamespaces not configured with empty string and x-bind in SVG minifier"


def test_minifiers_test_has_alpine_cases():
    """
    Fail-to-pass: Verify that minifiers/minifiers_test.go has Issue #14669 test cases.

    This ensures the regression tests for Alpine.js directives are present.
    """
    test_path = os.path.join(REPO, "minifiers/minifiers_test.go")
    with open(test_path, "r") as f:
        content = f.read()

    # Check for Issue #14669 test cases
    assert "Issue #14669" in content or "14669" in content, \
        "Issue #14669 test cases not found in minifiers_test.go"

    # Check for the actual test cases with x-bind:href and :href
    assert 'x-bind:href="myicon"' in content, \
        "x-bind:href test case not found in minifiers_test.go"
    assert ':href="myicon"' in content, \
        ":href test case not found in minifiers_test.go"


def test_repo_minifiers_test():
    """
    Pass-to-pass: Run the minifiers package tests to ensure no regressions.

    This is the repo's own test suite for the minifiers package.
    """
    result = subprocess.run(
        ["go", "test", "-v", "./minifiers/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, \
        f"Minifiers package tests failed:\n{result.stderr[-1000:]}\n{result.stdout[-1000:]}"


def test_repo_go_build():
    """
    Pass-to-pass: Verify the project builds successfully.

    This ensures no compilation errors after the changes.
    """
    result = subprocess.run(
        ["go", "build", "-o", "/tmp/hugo", "./"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, \
        f"Hugo build failed:\n{result.stderr[-1000:]}"


def test_repo_go_vet():
    """
    Pass-to-pass: Run go vet to catch common issues.
    """
    result = subprocess.run(
        ["go", "vet", "./minifiers/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, \
        f"go vet found issues:\n{result.stderr}"


def test_repo_minifiers_race():
    """
    Pass-to-pass: Run minifiers tests with race detector.

    This ensures no data races in the minifiers package.
    """
    result = subprocess.run(
        ["go", "test", "-race", "-timeout", "120s", "./minifiers/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, \
        f"Race detector found issues:\n{result.stderr[-1000:]}"


def test_repo_gofmt():
    """
    Pass-to-pass: Check that minifiers code is properly formatted.

    This runs gofmt to check for formatting issues in the modified package.
    """
    result = subprocess.run(
        ["gofmt", "-l", "./minifiers/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )

    # gofmt returns 0 but lists unformatted files if any
    assert result.returncode == 0, \
        f"gofmt check failed:\n{result.stderr}"
    assert result.stdout.strip() == "", \
        f"gofmt found unformatted files:\n{result.stdout}"


def test_repo_config_tests():
    """
    Pass-to-pass: Run configuration tests for minifiers.

    Tests the config loading and validation for minifiers package.
    """
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestConfig", "./minifiers/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, \
        f"Config tests failed:\n{result.stderr[-500:]}"
    assert "PASS" in result.stdout, \
        f"Config tests did not pass:\n{result.stdout[-500:]}"
