"""
Test suite for Gradio PR #12933 - Block.svelte border fix
Tests verify the CSS border fix in Block.svelte:
- fail_to_pass: Buggy code (base commit) should fail these tests
- pass_to_pass: Fixed code and other checks should pass
"""

import subprocess
import re

# The Docker-internal path where the repo is cloned
REPO = "/repo"
FILE_PATH = f"{REPO}/js/atoms/src/Block.svelte"


def read_svelte_file():
    """Read the Block.svelte file content."""
    with open(FILE_PATH, "r") as f:
        return f.read()


# === fail_to_pass tests: These should FAIL on base commit (buggy code) ===

def test_hide_container_no_inherited_border_var():
    """FAIL_TO_PASS: hide-container must NOT set --block-border-width CSS variable (inherited to children).

    The bug: --block-border-width: 0 in .hide-container inherits to child blocks,
    causing them to lose their borders.
    """
    content = read_svelte_file()
    # Check that .hide-container does NOT contain --block-border-width: 0
    match = re.search(r'\.hide-container[^\{]*\{[^\}]*--block-border-width:\s*0', content, re.DOTALL)
    assert match is None, f"BUG FOUND: .hide-container still sets --block-border-width: 0 (inheritable bug)"


def test_hide_container_uses_direct_border_zero():
    """FAIL_TO_PASS: hide-container must zero its own border directly, not via inherited CSS variable.

    The fix uses border-width: 0 directly on .hide-container.
    """
    content = read_svelte_file()
    # Check that .hide-container has direct border-width: 0
    match = re.search(r'\.hide-container:not\(\.fullscreen\)\s*\{[^\}]*border-width:\s*0', content, re.DOTALL)
    assert match is not None, f"BUG: .hide-container should use direct 'border-width: 0', not '--block-border-width: 0'"


def test_child_block_retains_border():
    """FAIL_TO_PASS: Child .block inside hide-container should retain its border.

    This is tested by verifying the .block class sets its own border-width,
    which would override any inherited --block-border-width.
    """
    content = read_svelte_file()
    # Check that .block class has border-width: var(--block-border-width)
    match = re.search(r'\.block\s*\{[^\}]*border-width:\s*var\(--block-border-width\)', content, re.DOTALL)
    assert match is not None, f"BUG: .block class should set border-width to retain its border"


# === pass_to_pass tests: These should PASS on fixed code ===

def test_block_class_preserves_styling():
    """PASS_TO_PASS: .block CSS class retains core visual properties."""
    content = read_svelte_file()
    # Check .block has essential CSS properties
    block_css = re.search(r'\.block\s*\{([^\}]*)\}', content, re.DOTALL)
    assert block_css is not None, ".block class not found in CSS"
    css_content = block_css.group(1)

    # Core properties should exist
    assert "box-shadow:" in css_content, ".block missing box-shadow"
    assert "border-color:" in css_content, ".block missing border-color"
    assert "border-radius:" in css_content, ".block missing border-radius"
    assert "background:" in css_content, ".block missing background"


def test_hide_container_preserves_other_resets():
    """PASS_TO_PASS: hide-container preserves its other CSS resets."""
    content = read_svelte_file()
    match = re.search(r'\.hide-container:not\(\.fullscreen\)\s*\{([^\}]*)\}', content, re.DOTALL)
    assert match is not None, ".hide-container CSS not found"

    css_content = match.group(1)
    # These resets should be preserved
    assert "margin: 0" in css_content, "hide-container missing margin reset"
    assert "box-shadow: none" in css_content, "hide-container missing box-shadow reset"
    assert "background: transparent" in css_content or "background: transparent" in css_content, "hide-container missing background reset"
    assert "padding: 0" in css_content, "hide-container missing padding reset"
    assert "overflow: visible" in css_content, "hide-container missing overflow reset"


def test_file_is_valid_svelte():
    """PASS_TO_PASS: Block.svelte must exist and be a valid Svelte component."""
    content = read_svelte_file()
    # Basic Svelte structure checks
    assert "<script" in content, "Missing script tag"
    assert "</script>" in content, "Missing closing script tag"
    assert "<style" in content, "Missing style tag"
    assert "</style>" in content, "Missing closing style tag"


def test_svelte_template_integrity():
    """PASS_TO_PASS: Key Svelte template bindings preserved."""
    content = read_svelte_file()
    # Check key template bindings exist
    assert "class:hide-container" in content, "Missing hide-container class binding"
    assert "class:fullscreen" in content, "Missing fullscreen class binding"
    assert "style:flex-grow" in content, "Missing flex-grow style binding"
    assert "<slot" in content, "Missing slot for content"
