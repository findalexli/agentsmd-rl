#!/usr/bin/env python3
"""
Tests for playwright Tracing.group() returning Disposable.

This task tests both:
1. The functional change: Tracing.group() returns a Disposable that calls groupEnd() on dispose
2. The config update: CLAUDE.md should include the flint rule
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/playwright")
TRACING_TS = REPO / "packages" / "playwright-core" / "src" / "client" / "tracing.ts"
CLAUDE_MD = REPO / "CLAUDE.md"


def test_claude_md_has_flint_rule():
    """
    [config_edit] fail_to_pass
    CLAUDE.md must be updated to include the 'npm run flint' pre-commit rule.
    """
    content = CLAUDE_MD.read_text()
    assert "npm run flint" in content, "CLAUDE.md should mention 'npm run flint'"
    assert "Before committing" in content, "CLAUDE.md should mention running flint before committing"


def test_tracing_ts_imports_disposable():
    """
    [code_edit] fail_to_pass
    tracing.ts must import DisposableStub from disposable module.
    """
    content = TRACING_TS.read_text()
    assert "DisposableStub" in content, "tracing.ts should import/use DisposableStub"
    assert "from './disposable'" in content, "tracing.ts should import from disposable module"


def test_tracing_group_returns_disposable():
    """
    [code_edit] fail_to_pass
    Tracing.group() must return a Disposable that calls groupEnd() on dispose.
    """
    content = TRACING_TS.read_text()
    # Check that we return a DisposableStub in the group method
    assert "return new DisposableStub" in content, "tracing.ts should return DisposableStub from group()"
    assert "groupEnd()" in content, "Disposable should call groupEnd() on dispose"


def test_types_d_updated():
    """
    [code_edit] fail_to_pass
    Type definitions must show group() returns Promise<Disposable>, not Promise<void>.
    """
    # Check both type definition files
    client_types = REPO / "packages" / "playwright-client" / "types" / "types.d.ts"
    core_types = REPO / "packages" / "playwright-core" / "types" / "types.d.ts"

    for types_file in [client_types, core_types]:
        content = types_file.read_text()
        # Find the Tracing.group method signature - it should return Promise<Disposable>
        assert "Promise<Disposable>" in content, f"{types_file} should have group() return Promise<Disposable>"


def test_api_docs_updated():
    """
    [config_edit] fail_to_pass
    API documentation must document the return type.
    """
    api_docs = REPO / "docs" / "src" / "api" / "class-tracing.md"
    content = api_docs.read_text()

    # Check that the group method documents the return type
    assert "returns: <[Disposable]>" in content, "API docs should document that group() returns Disposable"


def test_typescript_compiles():
    """
    [p2p] static
    Modified TypeScript files should compile without errors.
    """
    # Run TypeScript compiler check
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "-p", "packages/playwright-core/src"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stdout}\n{result.stderr}"


def test_flint_linting():
    """
    [p2p] agent_config
    Code should pass 'npm run flint' linting as per CLAUDE.md rule.
    This is a soft check - if dependencies are missing, we skip.
    """
    # First check if the flint command exists in package.json
    package_json = REPO / "package.json"
    if not package_json.exists():
        pytest.skip("package.json not found")

    # Try to run a subset of flint checks that don't need browsers
    # Just check that eslint passes on the modified file
    result = subprocess.run(
        ["npx", "eslint", "packages/playwright-core/src/client/tracing.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    # We only fail on actual errors, not warnings
    if result.returncode != 0 and "error" in result.stderr.lower():
        assert False, f"ESLint found errors:\n{result.stderr}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
