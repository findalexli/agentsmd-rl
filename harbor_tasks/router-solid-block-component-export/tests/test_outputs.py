"""Tests for router-solid-block-component-export task.

This task involves refactoring the Block component export from:
- Old: function overloads with deprecated signature
- New: const arrow function implementing BlockComponent interface
"""

import subprocess
import re
import os

REPO = "/workspace/router"
TARGET_FILE = os.path.join(REPO, "packages/solid-router/src/useBlocker.tsx")

def read_target_file():
    """Read the target source file."""
    with open(TARGET_FILE, 'r') as f:
        return f.read()


def test_repo_eslint_solid_router():
    """Repo's ESLint passes for solid-router package (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-router:test:eslint", "--skip-nx-cache"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


def test_repo_unit_tests_blocker():
    """Repo's unit tests for blocker.test.tsx pass (pass_to_pass)."""
    # Run only the blocker.test.tsx file which covers the Block component
    r = subprocess.run(
        ["pnpm", "vitest", "run", "tests/blocker.test.tsx", "--reporter=verbose"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=f"{REPO}/packages/solid-router",
    )
    assert r.returncode == 0, f"Blocker tests failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"

def test_block_export_uses_const_arrow():
    """F2P: Block export should use const arrow function implementing BlockComponent."""
    content = read_target_file()

    # Check for the new signature: export const Block: BlockComponent
    assert "export const Block: BlockComponent" in content, \
        "Block should be exported as const implementing BlockComponent interface"

    # Check it's a const, not a function declaration
    block_line = None
    for line in content.split('\n'):
        if 'export const Block' in line:
            block_line = line.strip()
            break

    assert block_line is not None, "Could not find Block export line"
    assert re.search(r'export\s+const\s+Block:\s*BlockComponent', block_line), \
        f"Block should be exported as 'const Block: BlockComponent', got: {block_line}"

def test_no_deprecated_function_overload():
    """F2P: Old deprecated function overload should be removed."""
    content = read_target_file()

    # Should NOT have the deprecated standalone function signature
    # The old code had: export function Block(opts: LegacyPromptProps): SolidNode
    deprecated_pattern = r'export\s+function\s+Block\s*\(\s*opts\s*:\s*LegacyPromptProps\s*\)'
    assert not re.search(deprecated_pattern, content), \
        "Deprecated function overload 'export function Block(opts: LegacyPromptProps)' should be removed"

def test_block_has_function_implementation():
    """F2P: Block should have function implementation body."""
    content = read_target_file()

    # After the const declaration, should have function implementation
    assert "= function Block(" in content, \
        "Block should be implemented as a function expression assigned to const"

def test_legacy_prompt_props_still_exists():
    """P2P: LegacyPromptProps type should still exist for backward compatibility."""
    content = read_target_file()

    assert "type LegacyPromptProps" in content, \
        "LegacyPromptProps type should exist for backward compatibility"

def test_useBlocker_hook_exports():
    """P2P: useBlocker hook should still be exported."""
    content = read_target_file()

    assert "export function useBlocker" in content or "export const useBlocker" in content, \
        "useBlocker hook should be exported"

def test_prompt_props_type_exists():
    """P2P: PromptProps type should exist."""
    content = read_target_file()

    assert "type PromptProps" in content, \
        "PromptProps type should exist"

def test_block_uses_correct_param_type():
    """F2P: Block should accept PromptProps | LegacyPromptProps as parameter."""
    content = read_target_file()

    # Find the Block function signature
    block_func_match = re.search(
        r'export const Block: BlockComponent = function Block\(([^)]+)\)',
        content
    )
    assert block_func_match is not None, "Could not find Block function signature"

    param = block_func_match.group(1)
    assert "PromptProps | LegacyPromptProps" in param, \
        f"Block parameter should be 'PromptProps | LegacyPromptProps', got: {param}"
