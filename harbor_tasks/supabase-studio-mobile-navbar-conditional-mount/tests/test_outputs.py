"""
Task: supabase-studio-mobile-navbar-conditional-mount
Repo: supabase @ bb66ba884c52443d964df4eb7567ba35a73a5abc
PR:   44565

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/supabase"
TARGET_FILE = f"{REPO}/apps/studio/components/layouts/DefaultLayout.tsx"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    # Check TypeScript syntax using tsc --noEmit
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "--jsx", "react-jsx"],
        cwd=f"{REPO}/apps/studio",
        capture_output=True,
        timeout=120,
    )
    # Note: We allow some errors from other files, but DefaultLayout.tsx must not have parse errors
    # A parse error would have exit code 1 with "error TS" messages
    if r.returncode != 0:
        stderr = r.stderr.decode()
        stdout = r.stdout.decode()
        output = stderr + stdout
        # Check specifically for syntax/parse errors in DefaultLayout.tsx
        if "DefaultLayout.tsx" in output and ("error TS" in output or "parse" in output.lower()):
            assert False, f"Syntax error in DefaultLayout.tsx:\n{output}"
    # If we get here, the file parses correctly


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_usebreakpoint_imported():
    """useBreakpoint must be imported from 'common' hook library."""
    src = Path(TARGET_FILE).read_text()
    # Check for the import of useBreakpoint
    assert "useBreakpoint" in src, "useBreakpoint must be imported from 'common'"
    # Verify it's imported from 'common'
    # Match patterns like: import { useBreakpoint } from 'common'
    #                      import { useParams, useBreakpoint } from 'common'
    assert "from 'common'" in src or 'from "common"' in src, "useBreakpoint must be imported from 'common' package"


# [pr_diff] fail_to_pass
def test_mobile_conditional_render():
    """MobileNavigationBar must be conditionally rendered based on isMobile breakpoint."""
    src = Path(TARGET_FILE).read_text()

    # Check that useBreakpoint('md') is called
    assert "useBreakpoint('md')" in src or 'useBreakpoint("md")' in src, \
        "useBreakpoint('md') must be called to detect mobile viewport"

    # Check that isMobile variable is created
    assert "const isMobile = useBreakpoint" in src, \
        "isMobile variable must be created from useBreakpoint hook"

    # Check for conditional rendering pattern: {isMobile && (...)}
    # This ensures MobileNavigationBar only mounts on mobile
    conditional_pattern = r"\{\s*isMobile\s*&&\s*\(\s*<MobileNavigationBar"
    assert re.search(conditional_pattern, src, re.DOTALL), \
        "MobileNavigationBar must be conditionally rendered with {isMobile && (...)} pattern"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """DefaultLayout component is not a stub (has real logic)."""
    src = Path(TARGET_FILE).read_text()

    # Check that DefaultLayout is still a proper component with content
    assert "export const DefaultLayout" in src, "DefaultLayout must be exported"

    # Check it has the key elements that make it a real component
    required_elements = [
        "PropsWithChildren",
        "return",
        "SidebarProvider",
        "LayoutHeader",
        "MobileNavigationBar",
    ]
    for elem in required_elements:
        assert elem in src, f"DefaultLayout must contain {elem}"

    # Make sure the main component body has substantial content
    # Count lines in the DefaultLayout function (approximate)
    lines = src.split('\n')
    # Find the DefaultLayout function and count lines until closing brace
    func_start = -1
    for i, line in enumerate(lines):
        if 'export const DefaultLayout' in line:
            func_start = i
            break

    # The component should have substantial content (not just a stub)
    if func_start != -1:
        func_body = '\n'.join(lines[func_start:func_start+50])
        # Should have multiple JSX elements, not just a trivial return
        assert func_body.count('<') > 5, "DefaultLayout must have substantial JSX content"


# [static] pass_to_pass
def test_layout_header_still_renders():
    """LayoutHeader must still render unconditionally (only MobileNavigationBar is conditional)."""
    src = Path(TARGET_FILE).read_text()

    # LayoutHeader should NOT be inside the isMobile conditional
    # Find the LayoutHeader and make sure it's after the conditional block closes
    lines = src.split('\n')

    # Find the line with LayoutHeader
    layout_header_line = -1
    conditional_close_line = -1
    is_mobile_start_line = -1

    for i, line in enumerate(lines):
        if '<LayoutHeader' in line:
            layout_header_line = i
        if '{isMobile && (' in line or '{isMobile&&(' in line:
            is_mobile_start_line = i
        # Look for the closing of the conditional block
        if is_mobile_start_line != -1 and line.strip() == ')}' and i > is_mobile_start_line:
            conditional_close_line = i

    # LayoutHeader should be after the conditional block closes
    # Or if there's no conditional block found, make sure LayoutHeader exists
    assert layout_header_line != -1, "LayoutHeader must be present in the layout"

    # If we found the conditional, LayoutHeader should come after it
    if conditional_close_line != -1:
        assert layout_header_line > conditional_close_line, \
            "LayoutHeader should render after and outside the isMobile conditional"
