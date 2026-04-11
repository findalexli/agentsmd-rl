"""Behavioral tests for the DELETE user endpoint task.

These tests verify the actual execution behavior of the deleteUser function,
ensuring it:
1. Properly deletes existing users
2. Throws AppError with proper context when user not found
3. Has proper JSDoc documentation
4. Logs operations appropriately
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/output"


def _compile_ts():
    """Compile TypeScript files to JavaScript."""
    r = subprocess.run(
        ["npx", "tsc"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    if r.returncode != 0:
        raise RuntimeError(f"TypeScript compilation failed: {r.stderr}")


def _run_ts(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute TypeScript/JavaScript code via Node in the repo directory."""
    # Ensure TypeScript is compiled first
    _compile_ts()

    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


def test_delete_user_returns_deleted_user():
    """deleteUser returns the deleted user record when successful."""
    r = _run_ts("""
import { deleteUser } from './src/api/users.js';

deleteUser('user-1').then(result => {
  console.log(JSON.stringify(result));
}).catch(err => {
  console.error(err.message);
  process.exit(1);
});
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["id"] == 'user-1', f"Expected user-1, got {data['id']}"
    assert data["name"] == 'Alice', f"Expected name Alice, got {data['name']}"


def test_delete_user_throws_app_error_when_not_found():
    """deleteUser throws AppError with proper context when user not found."""
    r = _run_ts("""
import { deleteUser } from './src/api/users.js';
import { AppError } from './src/errors.js';

deleteUser('non-existent-user').then(() => {
  console.log('SHOULD_HAVE_THROWN');
}).catch(err => {
  if (err instanceof AppError) {
    console.log(JSON.stringify({
      isAppError: true,
      message: err.message,
      context: err.context
    }));
  } else {
    console.log(JSON.stringify({
      isAppError: false,
      message: err.message
    }));
  }
});
""")
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    assert "SHOULD_HAVE_THROWN" not in r.stdout, "Expected error to be thrown but got success"
    data = json.loads(r.stdout.strip())
    assert data.get("isAppError") == True, f"Expected AppError but got: {data}"
    assert "not found" in data.get("message", "").lower() or data.get("message") == "User not found", \
        f"Error message should indicate user not found: {data}"
    assert data.get("context", {}).get("userId") == "non-existent-user", \
        f"Error context should include userId: {data}"


def test_delete_user_includes_operation_in_error_context():
    """deleteUser includes operation name in error context on unexpected failures."""
    # This test verifies that the catch block adds operation to context
    # The operation field is added when the repository throws a non-AppError
    # which happens when trying to delete a non-existent user
    r = _run_ts("""
import { deleteUser } from './src/api/users.js';

// Try to delete a non-existent user - this triggers the catch block
deleteUser('definitely-non-existent-user-xyz').then(() => {
  console.log('SHOULD_HAVE_THROWN');
}).catch(err => {
  console.log(JSON.stringify({
    name: err.name,
    message: err.message,
    context: err.context
  }));
});
""")
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    assert "SHOULD_HAVE_THROWN" not in r.stdout, "Expected error to be thrown"
    data = json.loads(r.stdout.strip())
    # Check that error context includes the operation field
    ctx = data.get("context", {})
    assert ctx.get("operation") == "deleteUser", \
        f"Error context should include operation 'deleteUser': {data}"


def test_delete_user_logs_deletion():
    """deleteUser logs the deletion operation with user ID."""
    r = _run_ts("""
import { deleteUser } from './src/api/users.js';

deleteUser('user-2').then(() => {
  console.log('SUCCESS');
}).catch(err => {
  console.error(err.message);
  process.exit(1);
});
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    # Check that the log output contains the user ID
    assert "user-2" in r.stderr or "user-2" in r.stdout, \
        f"Expected logging to include userId 'user-2': stdout={r.stdout}, stderr={r.stderr}"
    assert "deleted" in r.stderr.lower() or "deleted" in r.stdout.lower() or "SUCCESS" in r.stdout, \
        f"Expected success or deletion message: stdout={r.stdout}, stderr={r.stderr}"


def test_delete_user_has_jsdoc():
    """deleteUser function has JSDoc documentation with @param and @return tags."""
    users_file = Path(REPO) / "src" / "api" / "users.ts"
    content = users_file.read_text()

    # Check for JSDoc comment before deleteUser function
    assert "/**" in content, "Function should have JSDoc comment"
    assert "@param" in content, "JSDoc should include @param tag"
    assert "@return" in content or "@returns" in content, "JSDoc should include @return/@returns tag"
    assert "userId" in content, "JSDoc should document userId parameter"


def test_typescript_compiles():
    """TypeScript code compiles without errors (pass_to_pass gate)."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript compilation failed:\n{r.stderr}"


def test_app_error_class_exists():
    """AppError class exists and is properly exported (pass_to_pass gate)."""
    r = _run_ts("""
import { AppError } from './src/errors.js';

const err = new AppError('Test message', { userId: '123' }, 'TEST_ERROR');
console.log(JSON.stringify({
  name: err.name,
  message: err.message,
  code: err.code,
  context: err.context
}));
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data.get("name") == "AppError", f"Error name should be AppError: {data}"
    assert data.get("context", {}).get("userId") == "123", f"Context should include userId: {data}"
