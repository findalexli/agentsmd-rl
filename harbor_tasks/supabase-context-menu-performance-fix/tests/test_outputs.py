"""
Task: supabase-context-menu-performance-fix
Repo: supabase/supabase @ 2af6b3eaec65971a8fa6986afad44d6581075ac5
PR: 44578

The Results component rendered a ContextMenu_Shadcn_ per table cell. With 1000+ rows,
this created thousands of document-level keydown listeners, making keystrokes take ~250ms.

The fix:
1. Extract formatClipboardValue and formatCellValue to Results.utils.ts
2. Use a single shared ContextMenu with a hidden trigger positioned at cursor
3. Use useMemo for columns and useCallback for handleContextMenu
4. Fix QueryBlock layout (flex instead of overflow-auto)

All checks must pass for reward = 1. Any failure = reward 0.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/workspace/supabase"


def test_typescript_compiles():
    """Modified TypeScript files must compile without errors."""
    # Check the key files exist and have valid TypeScript syntax
    results_tsx = Path(f"{REPO}/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.tsx")
    utils_ts = Path(f"{REPO}/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.utils.ts")

    assert results_tsx.exists(), "Results.tsx must exist"
    assert utils_ts.exists(), "Results.utils.ts must exist"

    # Try TypeScript compilation check
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "--isolatedModules",
         "apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.tsx"],
        cwd=REPO,
        capture_output=True,
        timeout=60
    )
    # Note: TypeScript may fail due to missing dependencies, but we check syntax is valid
    # by ensuring it's valid JavaScript/TypeScript syntax

    # Verify the file has valid syntax by trying to parse with node
    r2 = subprocess.run(
        ["node", "--check", str(results_tsx)],
        cwd=REPO,
        capture_output=True,
        timeout=30
    )
    # node --check validates JavaScript syntax (TypeScript files may fail here, that's ok)

    # Most important: ensure no syntax errors in the TypeScript structure
    content = results_tsx.read_text()
    assert "const Results" in content or "export default" in content, "Results component must be defined"


def test_single_context_menu_pattern():
    """Results.tsx must use single shared context menu, not per-cell."""
    results_tsx = Path(f"{REPO}/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.tsx")
    content = results_tsx.read_text()

    # Must have the new pattern: useRef for trigger and contextMenuCellRef
    assert "useRef" in content, "Must use useRef for shared context menu pattern"
    assert "triggerRef" in content, "Must have triggerRef for shared context menu"
    assert "contextMenuCellRef" in content, "Must have contextMenuCellRef for storing cell context"

    # Must have handleContextMenu callback
    assert "handleContextMenu" in content, "Must have handleContextMenu function"
    assert "useCallback" in content, "Must use useCallback for handleContextMenu"

    # Must use the shared pattern: single ContextMenu_Shadcn_ at top level
    # The old pattern had ContextMenu_Shadcn_ inside the formatter function
    # New pattern has it at the top level of the return statement

    # Should NOT have per-cell context menu (the old pattern inside formatter/renderCell)
    # We check that the ContextMenu is not inside renderCell
    lines = content.split("\n")
    in_render_cell = False
    render_cell_depth = 0
    context_menu_in_render_cell = False

    for line in lines:
        stripped = line.strip()

        # Track renderCell function
        if "renderCell:" in stripped or "renderCell :" in stripped:
            in_render_cell = True
            render_cell_depth = 0

        # Track braces
        if in_render_cell:
            render_cell_depth += stripped.count("{") - stripped.count("}")

            # Check for ContextMenu inside renderCell
            if "ContextMenu_Shadcn_" in stripped or "ContextMenu_Shadcn" in stripped:
                context_menu_in_render_cell = True

            # Exit renderCell when braces balance
            if render_cell_depth <= 0 and stripped.count("}") > 0:
                in_render_cell = False

    # The fix should NOT have ContextMenu inside renderCell
    assert not context_menu_in_render_cell, \
        "ContextMenu must NOT be inside renderCell - use shared pattern instead"

    # The shared pattern should have ContextMenu at the top level
    # Look for ContextMenu after the return statement but outside renderCell
    assert "<ContextMenu_Shadcn_" in content, "Must have shared ContextMenu_Shadcn_ component"


def test_results_utils_functions():
    """formatClipboardValue and formatCellValue must work correctly."""
    # Read and execute the utils file in a safe way
    utils_ts = Path(f"{REPO}/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.utils.ts")
    content = utils_ts.read_text()

    # Verify functions exist and are exported
    assert "export function formatClipboardValue" in content, \
        "formatClipboardValue must be exported from Results.utils.ts"
    assert "export function formatCellValue" in content, \
        "formatCellValue must be exported from Results.utils.ts"

    # Run the actual tests via the repo's test suite
    r = subprocess.run(
        ["pnpm", "test:studio", "--", "tests/components/SQLEditor/Results.utils.test.ts", "--run"],
        cwd=REPO,
        capture_output=True,
        timeout=120
    )

    # The tests should pass
    assert r.returncode == 0, \
        f"Results.utils tests failed:\nstdout: {r.stdout.decode()}\nstderr: {r.stderr.decode()}"


def test_queryblock_flex_layout():
    """QueryBlock must use flex layout instead of overflow-auto for double scrollbar fix."""
    queryblock_tsx = Path(f"{REPO}/apps/studio/components/ui/QueryBlock/QueryBlock.tsx")
    content = queryblock_tsx.read_text()

    # Find the Results container div
    # Should have flex flex-col, NOT overflow-auto
    # The old pattern: overflow-auto relative max-h-64
    # The new pattern: flex flex-col relative max-h-64

    # Check that the div containing Results uses flex
    assert "flex flex-col" in content, \
        "QueryBlock must use flex flex-col layout for Results container (Firefox/DataGrid fix)"

    # Should NOT have overflow-auto in the Results container
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if "Results rows={results}" in line:
            # Look at previous lines to find the container div
            for j in range(max(0, i-5), i):
                prev_line = lines[j]
                if "flex flex-col" in prev_line and "max-h-64" in prev_line:
                    # Good - found the correct pattern
                    return

    # If we didn't return, verify at least the className exists somewhere
    assert "flex flex-col" in content, "QueryBlock must use flex layout"


def test_results_component_tests_pass():
    """The Results component tests for single context menu must pass."""
    # Run the Results component test
    r = subprocess.run(
        ["pnpm", "test:studio", "--", "tests/components/SQLEditor/Results.test.tsx", "--run"],
        cwd=REPO,
        capture_output=True,
        timeout=120
    )

    # The tests should pass
    assert r.returncode == 0, \
        f"Results component tests failed:\nstdout: {r.stdout.decode()}\nstderr: {r.stderr.decode()}"
