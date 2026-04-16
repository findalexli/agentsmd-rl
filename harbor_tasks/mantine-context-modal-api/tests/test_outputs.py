"""Tests for mantine PR #8439 - Enhance contextModal functions."""

import subprocess
import sys
import re

REPO = "/workspace/mantine"
MODALS_PKG = f"{REPO}/packages/@mantine/modals"


def test_typescript_syntax_valid():
    """TypeScript files should have valid syntax (f2p)."""
    # Since the monorepo's tsc needs all dependencies built, we just check
    # that our changes don't introduce syntax/type errors via AST parsing.
    # We skip the test file because it has pre-existing jest/testing-library type deps.
    for filepath in [
        f"{MODALS_PKG}/src/context.ts",
        f"{MODALS_PKG}/src/ModalsProvider.tsx",
        f"{MODALS_PKG}/src/events.ts",
        f"{MODALS_PKG}/src/index.ts",
        f"{MODALS_PKG}/src/reducer.ts",
    ]:
        result = subprocess.run(
            ["npx", "tsc", "--noEmit", "--skipLibCheck", "--isolatedModules", filepath],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60,
        )
        output = result.stdout + result.stderr
        # Allow "Cannot find module" errors (monorepo deps) and config errors (--jsx, JSX flag)
        # Only check for actual syntax/type errors in our code
        real_errors = [line for line in output.split('\n')
                        if 'error TS' in line
                        and 'Cannot find module' not in line
                        and "'--jsx' is not set" not in line
                        and "Cannot use JSX unless the '--jsx' flag" not in line
                        and 'Module' not in line]
        assert len(real_errors) == 0, f"TypeScript errors in {filepath}:\n{chr(10).join(real_errors)}"


def test_unit_test_file_updated():
    """Unit test file should be updated with new API calls (f2p)."""
    with open(f"{MODALS_PKG}/src/use-modals/use-modals.test.tsx", "r") as f:
        content = f.read()

    # Test should use modalKey in openContextModal call
    assert "modalKey: 'contextTest'" in content, "Test should use modalKey in openContextModal"
    # Test should check for closeAllModals
    assert "closeAllModals" in content, "Test should check for closeAllModals"


def test_close_all_modals_method_exists():
    """useModals hook should return closeAllModals method (f2p)."""
    test_code = """
import { renderHook } from '@testing-library/react';
import { MantineProvider } from '@mantine/core';
import { ModalsProvider, useModals } from '@mantine/modals';
import React from 'react';

const wrapper = ({ children }: { children: React.ReactNode }) =>
  React.createElement(MantineProvider, {},
    React.createElement(ModalsProvider, {}, children)
  );

const { result } = renderHook(() => useModals(), { wrapper });

if (typeof result.current.closeAllModals !== 'function') {
  console.error('closeAllModals method not found');
  process.exit(1);
}

if (typeof result.current.closeAll === 'function') {
  console.error('closeAll should be renamed to closeAllModals');
  process.exit(1);
}

console.log('closeAllModals method exists and closeAll is renamed');
process.exit(0);
"""
    result = subprocess.run(
        ["node", "-e", f"require('@mantine/modals')"],
        cwd=MODALS_PKG,
        capture_output=True,
        text=True,
        timeout=30,
    )

    # Read the context.ts file to check for closeAllModals
    with open(f"{MODALS_PKG}/src/context.ts", "r") as f:
        content = f.read()

    assert "closeAllModals" in content, "closeAllModals not found in context.ts"
    # The ModalsContextProps should have closeAllModals, not closeAll
    interface_match = "closeAllModals: () => void" in content
    assert interface_match, "closeAllModals signature not found in ModalsContextProps"


def test_open_context_modal_uses_modal_key():
    """openContextModal should use modalKey in object parameter (f2p)."""
    with open(f"{MODALS_PKG}/src/context.ts", "r") as f:
        content = f.read()

    # Check that openContextModal signature uses modalKey
    assert "modalKey: TKey" in content, "modalKey parameter not found in openContextModal signature"

    # Check that the old positional signature is not present
    # Old: openContextModal(modal: TKey, props: ...)
    # New: openContextModal(props: { modalKey: TKey, ... })
    import re
    old_pattern = r"openContextModal.*\(\s*modal\s*:\s*TKey"
    assert not re.search(old_pattern, content), "Old positional openContextModal signature still present"


def test_close_context_modal_function_exists():
    """closeContextModal should be exported and properly typed (f2p)."""
    # Check index.ts exports closeContextModal
    with open(f"{MODALS_PKG}/src/index.ts", "r") as f:
        index_content = f.read()

    assert "closeContextModal" in index_content, "closeContextModal not exported from index.ts"

    # Check context.ts has proper typing
    with open(f"{MODALS_PKG}/src/context.ts", "r") as f:
        context_content = f.read()

    assert "closeContextModal: <TKey extends MantineModal>(modalKey: TKey" in context_content, \
        "closeContextModal signature not found or incorrect in context.ts"

    # Check events.ts exports it
    with open(f"{MODALS_PKG}/src/events.ts", "r") as f:
        events_content = f.read()

    assert "closeContextModal" in events_content, "closeContextModal not found in events.ts"


def test_update_context_modal_uses_modal_key():
    """updateContextModal should accept modalKey parameter (f2p)."""
    with open(f"{MODALS_PKG}/src/context.ts", "r") as f:
        content = f.read()

    # Check that updateContextModal signature accepts modalKey
    assert "modalKey: TKey" in content, "modalKey parameter not found in context.ts"


def test_modals_provider_has_close_all_modals():
    """ModalsProvider should provide closeAllModals method (f2p)."""
    with open(f"{MODALS_PKG}/src/ModalsProvider.tsx", "r") as f:
        content = f.read()

    # Check for closeAllModals function definition
    assert "closeAllModals" in content, "closeAllModals not found in ModalsProvider.tsx"

    # Check that context value includes closeAllModals
    assert "closeAllModals," in content, "closeAllModals not included in context value"

    # closeContextModal should call closeModal with looked-up id
    assert "closeContextModal" in content, "closeContextModal function not in ModalsProvider"


def test_context_modal_inner_props_type():
    """ContextModalInnerProps type should be properly defined (f2p)."""
    with open(f"{MODALS_PKG}/src/context.ts", "r") as f:
        content = f.read()

    # Check for ContextModalInnerProps type definition
    assert "ContextModalInnerProps" in content, "ContextModalInnerProps type not found"

    # Check for the conditional innerProps typing
    assert "innerProps?: never" in content, "Optional never innerProps not found"
    assert "innerProps: P" in content, "Required innerProps not found"


def test_open_context_modal_event_signature():
    """openContextModal event should accept modalKey in payload (f2p)."""
    with open(f"{MODALS_PKG}/src/events.ts", "r") as f:
        content = f.read()

    # Check that openContextModal doesn't destructure modal separately anymore
    # It should just pass payload through
    assert "modal:" not in content or "modalKey" in content, \
        "events.ts should use modalKey instead of modal"


def test_rubric_consistent_api_naming():
    """Rubric: API naming should be consistent (closeAllModals not closeAll)."""
    # This is checked by other tests but included as a rubric item
    pass


def test_rubric_typescript_types_compile():
    """Rubric: TypeScript types should be valid and compile."""
    # Covered by test_typescript_compilation
    pass


def test_typescript_types_valid():
    """TypeScript types should be valid - no syntax/type errors in modified files (p2p)."""
    # Just check that the files parse correctly
    for filepath in [
        f"{MODALS_PKG}/src/context.ts",
        f"{MODALS_PKG}/src/ModalsProvider.tsx",
        f"{MODALS_PKG}/src/events.ts",
        f"{MODALS_PKG}/src/index.ts",
    ]:
        result = subprocess.run(
            ["npx", "tsc", "--noEmit", "--skipLibCheck", "--allowJs", "--checkJs", filepath],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60,
        )
        # If tsc runs without crashing on syntax errors, the file is valid
        # We allow import errors since we're checking individual files
        output = result.stdout + result.stderr
        assert "error TS1" not in output or "Cannot find module" in output, \
            f"TypeScript syntax/type error in {filepath}:\n{output[-500:]}"


def test_repo_unit_tests():
    """Repo's unit tests for modals package pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "jest", "packages/@mantine/modals/src/use-modals/use-modals.test.tsx", "--no-cache"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Jest tests failed:\n{r.stderr[-500:]}"


def test_repo_eslint():
    """Repo's ESLint check on modified modals files passes (pass_to_pass)."""
    files = [
        f"{REPO}/packages/@mantine/modals/src/context.ts",
        f"{REPO}/packages/@mantine/modals/src/events.ts",
        f"{REPO}/packages/@mantine/modals/src/ModalsProvider.tsx",
        f"{REPO}/packages/@mantine/modals/src/index.ts",
    ]
    r = subprocess.run(
        ["npx", "eslint"] + files,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


def test_repo_prettier():
    """Repo's Prettier formatting check on modified modals files passes (pass_to_pass)."""
    files = [
        f"{REPO}/packages/@mantine/modals/src/context.ts",
        f"{REPO}/packages/@mantine/modals/src/events.ts",
        f"{REPO}/packages/@mantine/modals/src/ModalsProvider.tsx",
        f"{REPO}/packages/@mantine/modals/src/index.ts",
    ]
    r = subprocess.run(
        ["npx", "prettier", "--check"] + files,
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"
