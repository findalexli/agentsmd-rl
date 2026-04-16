"""Tests for mantine-modals-type-inference task."""

import subprocess
import sys
import os

REPO = "/workspace/mantine"
MODALS_SRC = f"{REPO}/packages/@mantine/modals/src/context.ts"


def run_command(cmd, cwd=REPO, timeout=60):
    """Run a command and return the result."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    return result


def test_typescript_compilation():
    """TypeScript compilation passes for the modals package (pass_to_pass)."""
    # The modals package uses the root tsconfig, compile from root
    result = run_command(
        ["yarn", "tsc", "--noEmit"],
        cwd=REPO,
        timeout=180
    )
    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stderr[-1000:]}"


def test_type_inference_improved():
    """Type inference uses 'infer M' syntax instead of intermediate type (fail_to_pass)."""
    with open(MODALS_SRC, 'r') as f:
        content = f.read()

    # Check that the new improved type inference is present
    assert "infer M" in content, "Type definition should use 'infer M' for direct type inference"

    # Check that the old intermediate type is removed
    assert "MantineModalsOverwritten" not in content, "Old intermediate type MantineModalsOverwritten should be removed"

    # Check the simplified type definition
    assert "export type MantineModals = MantineModalsOverride extends { modals: infer M }" in content, \
        "MantineModals type should use direct conditional type with infer"


def test_no_duplicate_modals_type():
    """No duplicate 'modals' property in type definition (fail_to_pass)."""
    with open(MODALS_SRC, 'r') as f:
        content = f.read()

    # The old code had 'modals' appearing multiple times in the conditional
    # New code should have a cleaner structure

    # Count occurrences of "modals:" in the type definitions
    lines = content.split('\n')
    modals_prop_count = sum(1 for line in lines if 'modals:' in line and 'Record' in line)

    # Should have at most 1 occurrence (in the default branch of the conditional)
    # or 0 if using the cleaner infer pattern
    assert modals_prop_count <= 1, \
        f"Should not have duplicate modals property definitions, found {modals_prop_count}"


def test_modals_type_is_direct():
    """MantineModals type maps directly to inferred type or default (fail_to_pass)."""
    with open(MODALS_SRC, 'r') as f:
        content = f.read()

    # The new implementation should have:
    # export type MantineModals = MantineModalsOverride extends { modals: infer M }
    #   ? M
    #   : Record<string, React.FC<ContextModalProps<any>>>;

    # Check for the pattern: direct conditional with infer
    assert "? M" in content, "Should directly use inferred type 'M' in conditional"

    # Check that it maps to Record in the else branch
    assert ": Record<string, React.FC<ContextModalProps<any>>>" in content, \
        "Should map to default Record type in else branch"


def test_repo_jest_modals():
    """Repo's Jest tests for modals package pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "jest", "packages/@mantine/modals/src/use-modals/use-modals.test.tsx"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Jest tests failed:\n{r.stderr[-500:]}"


def test_repo_eslint_modals():
    """Repo's ESLint check on modals package passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "eslint", "packages/@mantine/modals", "--cache"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint check failed:\n{r.stderr[-500:]}"


def test_repo_prettier_modals():
    """Repo's Prettier check on modals source passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "prettier", "--check", "packages/@mantine/modals/src/**/*.{ts,tsx}"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


