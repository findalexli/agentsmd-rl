#!/usr/bin/env python3
"""
Test outputs for @mantine/modals breaking changes fix.

This task tests that the breaking API changes in @mantine/modals are reverted.
The base commit has the buggy API, and the fix restores the original API:

1. openContextModal takes two arguments (modal, props) not one object with modalKey
2. closeAll is the method name, not closeAllModals
3. updateContextModal only needs modalId, not modalKey
4. Simpler OpenContextModal type without ContextModalInnerProps helper
"""

import subprocess
import re

REPO = "/workspace/mantine"
MODALS_SRC = f"{REPO}/packages/@mantine/modals/src"


def read_file(path: str) -> str:
    """Read file contents."""
    with open(path, "r") as f:
        return f.read()


# =============================================================================
# FAIL-TO-PASS TESTS
# These test that the buggy API is fixed
# =============================================================================

def test_open_context_modal_signature():
    """
    F2P: openContextModal should take two arguments (modal, props).

    In the buggy state, it took one object: openContextModal({ modalKey, ...props })
    After fix, it takes two args: openContextModal(modal, props)
    """
    provider_src = read_file(f"{MODALS_SRC}/ModalsProvider.tsx")

    # Check for the correct signature: (modal: string, { modalId, ...props }: OpenContextModal)
    pattern = r"\(modal:\s*string,\s*\{\s*modalId,\s*\.\.\.props\s*\}:\s*OpenContextModal"
    match = re.search(pattern, provider_src)

    assert match is not None, (
        "openContextModal should take two arguments (modal: string, { modalId, ...props }). "
        "Found buggy signature with single object argument."
    )


def test_context_has_close_all():
    """
    F2P: ModalsContextProps should have closeAll, not closeAllModals.

    In the buggy state, the method was named closeAllModals.
    After fix, it should be closeAll.
    """
    context_src = read_file(f"{MODALS_SRC}/context.ts")

    # Check for closeAll in the interface
    assert "closeAll:" in context_src, (
        "ModalsContextProps should have closeAll method. "
        "Found closeAllModals instead (or missing)."
    )

    # Make sure closeAllModals is NOT in the interface (it's in events.ts but not context)
    # The context interface should use closeAll
    interface_match = re.search(
        r"interface ModalsContextProps \{[^}]+\}",
        context_src,
        re.DOTALL
    )
    if interface_match:
        interface_content = interface_match.group(0)
        # closeAllModals should not be in the context interface
        assert "closeAllModals" not in interface_content, (
            "ModalsContextProps should not have closeAllModals - use closeAll instead"
        )


def test_update_context_modal_no_modal_key():
    """
    F2P: updateContextModal should not require modalKey parameter.

    In the buggy state, updateContextModal expected { modalKey, modalId, ...newProps }.
    After fix, it only needs { modalId, ...newProps }.
    """
    provider_src = read_file(f"{MODALS_SRC}/ModalsProvider.tsx")

    # The fixed version has a simpler signature without modalKey lookup logic
    # Check that the function doesn't have modalKey in its destructuring
    pattern = r"updateContextModal\s*=\s*useCallback\(\s*\(\{\s*modalId,\s*\.\.\.newProps\s*\}"
    match = re.search(pattern, provider_src)

    assert match is not None, (
        "updateContextModal should only destructure modalId (not modalKey). "
        "Found buggy signature that requires modalKey."
    )


def test_open_context_modal_type_signature():
    """
    F2P: openContextModal type should take two arguments in context.ts.

    The buggy state had: (props: { modalKey: TKey } & OpenContextModal<TKey> & DataAttributes) => string
    After fix: (modal: TKey, props: OpenContextModal<...>) => string
    """
    context_src = read_file(f"{MODALS_SRC}/context.ts")

    # Look for the fixed signature pattern in the interface
    # Should have: openContextModal: <TKey extends MantineModal>(
    #   modal: TKey,
    #   props: OpenContextModal<...>
    # ) => string;
    pattern = r"openContextModal:\s*<TKey\s+extends\s+MantineModal>\(\s*modal:\s*TKey,"
    match = re.search(pattern, context_src)

    assert match is not None, (
        "openContextModal type signature should take (modal: TKey, props: ...) as two arguments. "
        "Found buggy single-argument signature with modalKey in props object."
    )


def test_no_context_modal_inner_props_type():
    """
    F2P: ContextModalInnerProps type should not exist (it was removed).

    The buggy state had a complex ContextModalInnerProps helper type.
    After fix, OpenContextModal is a simple interface.
    """
    context_src = read_file(f"{MODALS_SRC}/context.ts")

    # ContextModalInnerProps should NOT be in the file
    assert "ContextModalInnerProps" not in context_src, (
        "ContextModalInnerProps type should be removed. "
        "OpenContextModal should be a simple interface."
    )


def test_close_context_modal_uses_close_modal():
    """
    F2P: closeContextModal should just call closeModal (same implementation).

    After fix, closeContextModal is an alias for closeModal.
    """
    provider_src = read_file(f"{MODALS_SRC}/ModalsProvider.tsx")

    # In the context value, closeContextModal should be: closeContextModal: closeModal
    pattern = r"closeContextModal:\s*closeModal"
    match = re.search(pattern, provider_src)

    assert match is not None, (
        "closeContextModal should be an alias for closeModal in the context value."
    )


def test_modals_type_simplified():
    """
    F2P: MantineModals type should use MantineModalsOverwritten pattern.

    After fix, it uses the MantineModalsOverwritten helper for better type inference.
    """
    context_src = read_file(f"{MODALS_SRC}/context.ts")

    # Check for MantineModalsOverwritten
    assert "MantineModalsOverwritten" in context_src, (
        "MantineModals type should use MantineModalsOverwritten helper pattern."
    )


def test_open_context_modal_in_events():
    """
    F2P: events.ts openContextModal should handle the two-argument conversion.

    The events system receives a payload with 'modal' key and needs to call the
    provider function with two arguments.
    """
    provider_src = read_file(f"{MODALS_SRC}/ModalsProvider.tsx")

    # Check for the conversion in useModalsEvents call
    pattern = r"openContextModal:\s*\(\{\s*modal,\s*\.\.\.payload\s*\}:\s*any\)\s*=>\s*openContextModal\(modal,\s*payload\)"
    match = re.search(pattern, provider_src)

    assert match is not None, (
        "ModalsProvider should convert single-arg event payload to two-arg call: "
        "openContextModal: ({ modal, ...payload }: any) => openContextModal(modal, payload)"
    )


# =============================================================================
# PASS-TO-PASS TESTS
# These test that repo's own tests still pass after the fix
# =============================================================================

def test_repo_jest_modals():
    """
    P2P: Jest tests for @mantine/modals should pass (repo CI).

    Run the test suite for the modals package using the repo's jest config.
    """
    result = subprocess.run(
        ["npx", "jest", "packages/@mantine/modals", "--no-coverage"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, (
        f"Jest tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"
    )


def test_repo_eslint_modals():
    """
    P2P: ESLint passes on @mantine/modals source (repo CI).

    Runs the repo's eslint command on the modals package.
    """
    result = subprocess.run(
        ["npx", "eslint", "packages/@mantine/modals/src", "--no-cache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, (
        f"ESLint failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"
    )


def test_repo_prettier_check():
    """
    P2P: Prettier formatting check passes (repo CI).

    Runs the repo's prettier check on modals package TypeScript files.
    """
    result = subprocess.run(
        ["npx", "prettier", "--check", "packages/@mantine/modals/**/*.{ts,tsx}"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, (
        f"Prettier check failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"
    )


def test_modals_package_builds():
    """
    P2P: @mantine/modals package should be buildable.

    Try to build the modals package specifically.
    """
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--project", "tsconfig.json"],
        cwd=f"{REPO}/packages/@mantine/modals",
        capture_output=True,
        text=True,
        timeout=60
    )

    # If it fails due to workspace deps, skip the test
    # The main verification is in the F2P tests
    if result.returncode != 0:
        # Check if it's just workspace dependency resolution issues
        if "Cannot find module '@mantine/core'" in result.stdout or \
           "Cannot find module '@mantine/hooks'" in result.stdout:
            # Skip this test - workspace deps not built but code itself is correct
            import pytest
            pytest.skip("Workspace dependencies not built, but code verification passes via other tests")
        else:
            assert False, f"TypeScript compilation failed:\n{result.stdout}\n{result.stderr}"


def test_no_close_context_modal_export():
    """
    P2P: closeContextModal should not be exported from index.ts.

    The fix removes this export since it's now redundant with closeModal.
    """
    index_src = read_file(f"{MODALS_SRC}/index.ts")

    # Check that closeContextModal is NOT exported
    lines = index_src.split("\n")
    for line in lines:
        # Skip comment lines
        if line.strip().startswith("//"):
            continue
        # If closeContextModal appears in a non-comment line, it should not be an export
        if "closeContextModal" in line and "export" in line:
            assert False, (
                "closeContextModal should not be exported from index.ts - "
                "users should use closeModal instead"
            )


def test_reducer_uses_generic_open_context_modal():
    """
    P2P: reducer.ts should reference OpenContextModal<any> not bare OpenContextModal.

    The fix adds the generic parameter to make types work correctly.
    """
    reducer_src = read_file(f"{MODALS_SRC}/reducer.ts")

    assert "OpenContextModal<any>" in reducer_src, (
        "reducer.ts should use OpenContextModal<any> with explicit generic parameter."
    )
