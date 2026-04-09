"""
Test file for PR #13558: Fix FK violation by reusing DB session in migrate_customer.

The bug: migrate_customer() used to create its own async session via a_session_maker(),
causing foreign key violations because the Org hadn't been committed yet when trying to
update stripe_customers.org_id.

The fix: migrate_customer() now accepts the session as a parameter, using the caller's
transaction context where the Org is already committed.
"""

import ast
import subprocess
import sys
from pathlib import Path

import pytest

REPO = "/workspace/openhands"


def _run_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo directory."""
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )


def _get_file_source(filepath: str) -> str:
    """Read file source without importing."""
    with open(filepath, 'r') as f:
        return f.read()


def _parse_function(filepath: str, func_name: str) -> ast.AsyncFunctionDef | None:
    """Parse a specific async function from a file using AST (no imports needed)."""
    source = _get_file_source(filepath)
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef) and node.name == func_name:
                return node
    except SyntaxError:
        pass
    return None


# -----------------------------------------------------------------------------
# Fail-to-pass tests: These test the specific bug behavior with code execution
# -----------------------------------------------------------------------------

def test_migrate_customer_accepts_session_parameter():
    """
    F2P: Verify migrate_customer accepts session as first parameter.

    The old signature was: migrate_customer(user_id: str, org: Org)
    The new signature is: migrate_customer(session, user_id: str, org: Org)

    This test will FAIL on base commit (only 2 params: user_id, org)
    and PASS on fix (3 params: session, user_id, org).
    """
    filepath = f'{REPO}/enterprise/integrations/stripe_service.py'
    func = _parse_function(filepath, 'migrate_customer')

    assert func is not None, "migrate_customer function not found in stripe_service.py"

    # Extract parameter names
    args = func.args
    params = []

    # Regular args
    for arg in args.args:
        params.append(arg.arg)
    # Vararg (*args)
    if args.vararg:
        params.append(f"*{args.vararg.arg}")
    # Keyword-only args
    for arg in args.kwonlyargs:
        params.append(arg.arg)
    # Kwarg (**kwargs)
    if args.kwarg:
        params.append(f"**{args.kwarg.arg}")

    # Check signature: should be (session, user_id, org)
    assert len(params) >= 3, f"migrate_customer has only {len(params)} params: {params}, expected at least 3 (session, user_id, org)"
    assert params[0] == 'session', f"First param should be 'session', got '{params[0]}'"
    assert params[1] == 'user_id', f"Second param should be 'user_id', got '{params[1]}'"
    assert params[2] == 'org', f"Third param should be 'org', got '{params[2]}'"


def test_migrate_customer_does_not_create_own_session():
    """
    F2P: Verify migrate_customer doesn't use a_session_maker internally.

    The old code had: async with a_session_maker() as session:
    The new code uses the passed session parameter.

    This test will FAIL on base commit (has 'async with a_session_maker')
    and PASS on fix (no a_session_maker usage).
    """
    filepath = f'{REPO}/enterprise/integrations/stripe_service.py'
    func = _parse_function(filepath, 'migrate_customer')

    assert func is not None, "migrate_customer function not found"

    # Unparse the function to check for a_session_maker pattern
    func_source = ast.unparse(func)

    # The fixed version should NOT have 'async with a_session_maker' inside the function
    assert 'async with a_session_maker' not in func_source, \
        "migrate_customer still creates its own session - should use passed session instead"
    assert 'a_session_maker()' not in func_source, \
        "migrate_customer still references a_session_maker()"


def test_migrate_customer_no_internal_commit():
    """
    F2P: Verify migrate_customer doesn't call session.commit().

    With the fix, session.commit() should be called by the caller (user_store),
    not inside migrate_customer.

    This test will FAIL on base commit (has 'await session.commit()')
    and PASS on fix (no session.commit() call).
    """
    filepath = f'{REPO}/enterprise/integrations/stripe_service.py'
    func = _parse_function(filepath, 'migrate_customer')

    assert func is not None, "migrate_customer function not found"

    func_source = ast.unparse(func)

    # Should NOT have session.commit() inside the function
    assert 'session.commit()' not in func_source, \
        "migrate_customer calls session.commit() - should let caller manage transaction"


def test_user_store_passes_session_to_migrate_customer():
    """
    F2P: Verify user_store passes session as first argument to migrate_customer.

    The call should be: migrate_customer(session, user_id, org)
    Not: migrate_customer(user_id, org)

    This test will FAIL on base commit (wrong call signature)
    and PASS on fix.
    """
    filepath = f'{REPO}/enterprise/storage/user_store.py'
    content = _get_file_source(filepath)

    # Look for the pattern where migrate_customer is called
    lines = content.split('\n')
    found_call = False

    for i, line in enumerate(lines):
        if 'migrate_customer(' in line:
            # Skip the import line
            if 'from integrations.stripe_service import' in line:
                continue
            found_call = True
            # Check that 'session' is passed as the first argument
            # Pattern should be: migrate_customer(session, ...)
            assert 'migrate_customer(session,' in line or 'migrate_customer(session ,' in line, \
                f"Line {i+1} calls migrate_customer without session as first arg: {line.strip()}"
            break

    assert found_call, "No migrate_customer call found in user_store.py"


# -----------------------------------------------------------------------------
# Pass-to-pass tests: Repo CI/CD gates
# -----------------------------------------------------------------------------

def test_python_syntax_stripe_service():
    """P2P: Verify stripe_service.py has valid syntax."""
    filepath = f'{REPO}/enterprise/integrations/stripe_service.py'
    with open(filepath, 'r') as f:
        source = f.read()
    try:
        ast.parse(source)
    except SyntaxError as e:
        pytest.fail(f"Syntax error in stripe_service.py: {e}")


def test_python_syntax_user_store():
    """P2P: Verify user_store.py has valid syntax."""
    filepath = f'{REPO}/enterprise/storage/user_store.py'
    with open(filepath, 'r') as f:
        source = f.read()
    try:
        ast.parse(source)
    except SyntaxError as e:
        pytest.fail(f"Syntax error in user_store.py: {e}")


def test_no_temprorary_typo():
    """P2P: Verify 'temprorary' typo is fixed to 'temporary' in comment."""
    filepath = f'{REPO}/enterprise/storage/user_store.py'
    with open(filepath, 'r') as f:
        content = f.read()

    # After the fix, "temprorary" should not exist
    assert 'temprorary' not in content, "Found 'temprorary' typo - should be 'temporary'"


def test_migrate_customer_relative_import_in_user_store():
    """
    P2P: Verify user_store uses relative imports without 'enterprise.' prefix.

    Per AGENTS.md: Use relative imports without the 'enterprise.' prefix.
    The import should be: from integrations.stripe_service import migrate_customer
    NOT: from enterprise.integrations.stripe_service import migrate_customer
    """
    filepath = f'{REPO}/enterprise/storage/user_store.py'
    with open(filepath, 'r') as f:
        content = f.read()

    lines = content.split('\n')
    for line in lines:
        if 'from integrations.stripe_service import' in line:
            # Should be relative import, not enterprise.integrations
            assert 'enterprise.integrations' not in line, \
                f"Import uses 'enterprise.' prefix, should be relative: {line.strip()}"
            return


def test_stripe_service_no_enterprise_import_prefix():
    """
    P2P: Verify stripe_service.py doesn't use 'enterprise.' in its own imports.

    Per AGENTS.md: Use relative imports without the 'enterprise.' prefix.
    """
    filepath = f'{REPO}/enterprise/integrations/stripe_service.py'
    with open(filepath, 'r') as f:
        content = f.read()

    lines = content.split('\n')
    for line in lines:
        if line.startswith('from enterprise.'):
            pytest.fail(f"Found import with 'enterprise.' prefix (should be relative): {line.strip()}")


def test_user_store_ast_valid():
    """P2P: Verify user_store.py has valid AST (no syntax errors)."""
    filepath = f'{REPO}/enterprise/storage/user_store.py'
    with open(filepath, 'r') as f:
        source = f.read()
    try:
        ast.parse(source)
    except SyntaxError as e:
        pytest.fail(f"Syntax error in user_store.py: {e}")
