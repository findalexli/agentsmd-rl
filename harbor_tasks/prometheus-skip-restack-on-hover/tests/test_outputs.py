"""Tests for prometheus/prometheus#18230: Skip recomputing stacked chart data on hover."""

import subprocess
import re

REPO = "/workspace/prometheus"
TARGET_FILE = f"{REPO}/web/ui/mantine-ui/src/pages/query/uPlotStackHelpers.ts"
UI_DIR = f"{REPO}/web/ui/mantine-ui"

def test_hook_accepts_opts_parameter():
    """The setSeries hook callback must accept the third opts parameter."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Look for the setSeries hook with three parameters: u, _i, opts
    pattern = r'opts\.hooks\.setSeries\.push\(\s*\(\s*u\s*,\s*_i\s*,\s*opts\s*\)'
    match = re.search(pattern, content)
    assert match, "Hook callback must accept three parameters: (u, _i, opts)"


def test_hook_checks_opts_show():
    """The hook must check 'if (opts.show != null)' before restacking."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for the conditional check that prevents restacking on hover
    assert "if (opts.show != null)" in content, \
        "Hook must check 'if (opts.show != null)' before restacking"


def test_hook_conditionally_restack():
    """Restacking operations must only happen inside the opts.show != null conditional."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find the setSeries hook and verify restacking is inside the conditional
    # Look for the pattern where restacking operations are gated by opts.show check
    pattern = r'if \(opts\.show != null\)\s*\{[^}]*stack\([^)]*\)[^}]*delBand[^}]*addBand[^}]*setData[^}]*\}'

    # A simpler approach: verify that stack(), delBand, addBand, setData calls
    # appear after the if (opts.show != null) check within the hook
    hook_start = content.find('opts.hooks.setSeries.push')
    hook_section = content[hook_start:hook_start + 800]

    # Check that the conditional is in this section
    assert "if (opts.show != null)" in hook_section, \
        "opts.show check must be in the setSeries hook"

    # Verify restacking operations are after the conditional
    conditional_idx = hook_section.find("if (opts.show != null)")
    restack_section = hook_section[conditional_idx:]

    assert "stack(" in restack_section, "stack() call must be inside the conditional"
    assert "delBand" in restack_section, "delBand call must be inside the conditional"
    assert "setData" in restack_section, "setData call must be inside the conditional"


def test_hook_not_called_on_hover():
    """The hook should NOT restack when called without opts.show (simulating hover)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # The logic should be: if opts.show is defined (toggle), restack; otherwise skip
    # This is the critical behavioral change - hover/focus doesn't trigger expensive restack

    # Find the hook callback and verify the conditional structure
    hook_pattern = r'opts\.hooks\.setSeries\.push\(\s*\([^)]*\)\s*=>\s*\{([^}]*\{[^}]*\}[^}]*)\}\s*\)'
    match = re.search(hook_pattern, content, re.DOTALL)

    if match:
        hook_body = match.group(1)
        # The body should have the conditional check
        assert "if (opts.show != null)" in hook_body, \
            "Hook body must conditionally check opts.show"
    else:
        # Fallback: just check the conditional exists in the file
        assert "if (opts.show != null)" in content, \
            "Required conditional check not found"


def test_comment_updated():
    """The comment should be updated to reflect the new behavior."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Comment should indicate it's for toggle, not focus/hover
    assert "restack on toggle (but not on focus/hover)" in content or \
           "restack on toggle" in content and "not on" in content, \
        "Comment should indicate restacking only happens on toggle, not hover/focus"


def test_repo_ui_lint():
    """UI linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=UI_DIR,
    )
    assert r.returncode == 0, f"UI lint failed:\n{r.stderr[-500:]}"


def test_repo_ui_unit_tests():
    """UI unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "test", "--", "--run"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=UI_DIR,
    )
    assert r.returncode == 0, f"UI tests failed:\n{r.stderr[-500:]}"


def test_target_file_exists():
    """The target file exists and is readable (pass_to_pass)."""
    import os
    assert os.path.isfile(TARGET_FILE), f"Target file not found: {TARGET_FILE}"
