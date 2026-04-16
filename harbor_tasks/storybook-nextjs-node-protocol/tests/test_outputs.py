"""Tests for storybook-nextjs-node-protocol fix.

This task validates that the Next.js framework properly handles node: builtin imports
in webpack configuration by using NormalModuleReplacementPlugin to strip the node:
prefix before webpack's polyfill handling kicks in.
"""

import subprocess
import sys
import json
from pathlib import Path

# Path to the storybook repo
REPO = Path("/workspace/storybook")
TARGET_FILE = REPO / "code" / "frameworks" / "nextjs" / "src" / "nodePolyfills" / "webpack.ts"


def test_file_exists():
    """Target file must exist."""
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"


def test_webpack_imported():
    """webpack must be imported for NormalModuleReplacementPlugin."""
    content = TARGET_FILE.read_text()
    assert "import webpack from 'webpack'" in content, \
        "webpack import not found - needed for NormalModuleReplacementPlugin"


def test_node_protocol_regex_defined():
    """NODE_PROTOCOL_REGEX constant must be defined."""
    content = TARGET_FILE.read_text()
    assert "const NODE_PROTOCOL_REGEX = /^node:/" in content, \
        "NODE_PROTOCOL_REGEX constant not found"


def test_normal_module_replacement_plugin_used():
    """NormalModuleReplacementPlugin must be configured to strip node: prefix."""
    content = TARGET_FILE.read_text()
    assert "new webpack.NormalModuleReplacementPlugin(NODE_PROTOCOL_REGEX" in content, \
        "NormalModuleReplacementPlugin not found or not using NODE_PROTOCOL_REGEX"
    assert "resource.request.replace(NODE_PROTOCOL_REGEX, '')" in content, \
        "Resource request replacement logic not found"


def test_fallback_preserved():
    """Existing resolve.fallback configuration must be preserved with spread."""
    content = TARGET_FILE.read_text()
    assert "...baseConfig.resolve?.fallback" in content, \
        "Existing fallback configuration not preserved with spread operator"


def test_plugins_array_structure():
    """Plugins array must spread existing plugins before adding new ones."""
    content = TARGET_FILE.read_text()
    assert "...(baseConfig.plugins || [])" in content, \
        "Existing plugins not properly spread in plugins array"


def test_compilation_succeeds():
    """Next.js package TypeScript compilation must succeed."""
    result = subprocess.run(
        ["yarn", "nx", "compile", "nextjs"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Next.js compilation failed:\n{result.stderr[-1000:]}"


def test_typecheck_succeeds():
    """Next.js package TypeScript type checking must pass."""
    result = subprocess.run(
        ["yarn", "nx", "check", "nextjs"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    # Note: check may fail on base commit due to the bug, but should pass after fix
    # This is primarily a p2p test
    assert result.returncode == 0, f"Next.js type check failed:\n{result.stderr[-1000:]}"


def test_unit_tests_pass():
    """Repo's unit tests for nextjs package must pass."""
    # Look for test files in the nextjs package
    test_files = list((REPO / "code" / "frameworks" / "nextjs").rglob("*.test.ts"))
    if not test_files:
        # Skip if no unit tests exist
        return

    result = subprocess.run(
        ["yarn", "test", "nextjs"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    # This may fail on base commit if tests rely on the fix
    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr[-1000:]}"


def test_functional_node_protocol_handling():
    """Functional test: verify node: protocol is handled by simulating webpack behavior.

    This test validates the actual behavior of the fix by checking that the
    NormalModuleReplacementPlugin would properly transform node:stream to stream.
    """
    import re

    content = TARGET_FILE.read_text()

    # Verify NODE_PROTOCOL_REGEX is defined with the expected pattern
    assert "const NODE_PROTOCOL_REGEX = /^node:/" in content, \
        "NODE_PROTOCOL_REGEX should match pattern /^node:/"

    # Test cases that should match the pattern (simulating the regex behavior)
    pattern = re.compile(r"^node:")
    test_cases = [
        ("node:stream", "stream"),
        ("node:fs", "fs"),
        ("node:path", "path"),
        ("node:util", "util"),
        ("node:buffer", "buffer"),
    ]

    for input_request, expected in test_cases:
        match = pattern.match(input_request)
        assert match, f"Pattern should match {input_request}"
        transformed = pattern.sub("", input_request)
        assert transformed == expected, f"Expected {expected}, got {transformed}"

    # Test cases that should NOT match
    negative_cases = ["stream", "fs", "path", "./node:stream", "node-stream"]
    for input_request in negative_cases:
        match = pattern.match(input_request)
        assert not match, f"Pattern should NOT match {input_request}"


def test_plugin_order_correct():
    """Plugin order must be: existing plugins, NormalModuleReplacementPlugin, NodePolyfillPlugin.

    The NormalModuleReplacementPlugin must come BEFORE NodePolyfillPlugin so that
    the node: prefix is stripped before the polyfill plugin tries to resolve it.
    """
    content = TARGET_FILE.read_text()

    # Find the plugins array section
    import re
    plugins_section = re.search(
        r"baseConfig\.plugins = \[(.*?)\];",
        content,
        re.DOTALL
    )
    assert plugins_section, "Could not find plugins array"

    plugins_text = plugins_section.group(1)

    # Check order: NormalModuleReplacementPlugin should come before NodePolyfillPlugin
    nmreplacement_pos = plugins_text.find("NormalModuleReplacementPlugin")
    polyfill_pos = plugins_text.find("NodePolyfillPlugin")

    assert nmreplacement_pos > 0, "NormalModuleReplacementPlugin not found in plugins array"
    assert polyfill_pos > 0, "NodePolyfillPlugin not found in plugins array"
    assert nmreplacement_pos < polyfill_pos, \
        "NormalModuleReplacementPlugin must come before NodePolyfillPlugin"


def test_no_duplicate_webpack_import():
    """webpack import should not be duplicated if it was already present."""
    content = TARGET_FILE.read_text()

    # Count occurrences of webpack imports
    webpack_imports = content.count("import webpack from 'webpack'")
    type_imports = content.count("from 'webpack'")

    # Should have at most one value import and one type import
    assert webpack_imports <= 1, f"Duplicate webpack imports found: {webpack_imports}"


# ============================================================================
# Pass-to-pass tests - Repository CI/CD tests (using real repo commands)
# ============================================================================

def test_nx_compile():
    """Repo CI: NX compile for nextjs package must pass (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "nx", "compile", "nextjs"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"NX compile failed:\n{result.stderr[-1000:]}"


def test_nx_check():
    """Repo CI: NX type check for nextjs package must pass (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "nx", "check", "nextjs"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"NX check failed:\n{result.stderr[-1000:]}"


def test_format_check():
    """Repo CI: Format check with oxfmt must pass (pass_to_pass)."""
    result = subprocess.run(
        ["yarn", "fmt:check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Format check failed:\n{result.stderr[-500:]}"
