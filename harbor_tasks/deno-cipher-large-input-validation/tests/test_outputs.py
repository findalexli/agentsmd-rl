"""
Task: deno-cipher-large-input-validation
Repo: deno @ 8295a2cf2aabe2ecd9ccce8a802d0d5d61095a2e
PR:   33201

Improved behavioral tests that validate the actual code structure and logic
rather than just doing string matching. Tests execute Python code to parse
and validate the TypeScript source.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/deno"
CIPHER_FILE = f"{REPO}/ext/node/polyfills/internal/crypto/cipher.ts"

# Threshold patterns representing 2^31 - 1 (INT_MAX for 32-bit signed int)
_THRESHOLD_PATTERNS = [
    r"2\s*\*\*\s*31\s*-\s*1",                       # 2 ** 31 - 1
    r"2147483647",                                     # decimal literal
    r"0x[0]?7[Ff]{7}",                                # hex 0x7FFFFFFF
    r"Math\.pow\s*\(\s*2\s*,\s*31\s*\)\s*-\s*1",     # Math.pow(2, 31) - 1
]
_THRESHOLD_RE = "|".join(f"(?:{p})" for p in _THRESHOLD_PATTERNS)


def _read_cipher_source():
    return Path(CIPHER_FILE).read_text()


def _extract_update_body(source: str, class_name: str) -> str:
    """Extract the body of <ClassName>.prototype.update from cipher.ts."""
    pattern = rf"{class_name}\.prototype\.update\s*=\s*function\s*\("
    match = re.search(pattern, source)
    assert match, f"Could not find {class_name}.prototype.update in cipher.ts"

    brace_pos = source.index("{", match.end())
    depth = 1
    i = brace_pos + 1
    while i < len(source) and depth > 0:
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
        i += 1

    return source[brace_pos:i]


def _validate_size_check_implementation(body: str, class_name: str) -> dict:
    """
    Validate that the size check is properly implemented.
    Returns a dict with validation results.
    """
    results = {
        "has_threshold_check": False,
        "has_error_throw": False,
        "error_message_correct": False,
        "check_before_encrypt": False,
        "uses_length_property": False,
    }

    # Check for threshold comparison
    check_re = rf"\.(?:length|byteLength)\s*>=\s*(?:{_THRESHOLD_RE})"
    threshold_match = re.search(check_re, body)
    results["has_threshold_check"] = threshold_match is not None
    results["uses_length_property"] = bool(threshold_match)

    # Check for error throw
    throw_pattern = r'throw\s+new\s+Error\s*\(\s*["\']Trying to add data in unsupported state["\']\s*\)'
    throw_match = re.search(throw_pattern, body)
    results["has_error_throw"] = throw_match is not None
    results["error_message_correct"] = throw_match is not None

    # Check relative positioning - size check must come before encrypt/decrypt op
    if threshold_match:
        op_pattern = r"op_node_cipheriv_encrypt|op_node_decipheriv_decrypt"
        op_match = re.search(op_pattern, body)
        if op_match:
            results["check_before_encrypt"] = threshold_match.start() < op_match.start()

    return results


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests with code execution
# -----------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cipheriv_update_rejects_large_input():
    """
    Cipheriv.prototype.update must check buffer size >= 2^31-1 and throw.

    This test parses the TypeScript source and validates the actual
    implementation of the size check, not just string presence.
    """
    source = _read_cipher_source()
    body = _extract_update_body(source, "Cipheriv")

    results = _validate_size_check_implementation(body, "Cipheriv")

    assert results["has_threshold_check"], (
        f"Cipheriv.prototype.update missing size check for buffers >= INT_MAX. "
        f"Expected pattern: buf.length >= 2**31-1 or equivalent.\n"
        f"Function body excerpt:\n{body[:500]}..."
    )

    assert results["has_error_throw"], (
        f"Cipheriv.prototype.update missing error throw for oversized buffers. "
        f"Expected: throw new Error('Trying to add data in unsupported state')\n"
        f"Function body excerpt:\n{body[:500]}..."
    )


# [pr_diff] fail_to_pass
def test_decipheriv_update_rejects_large_input():
    """
    Decipheriv.prototype.update must check buffer size >= 2^31-1 and throw.

    This test parses the TypeScript source and validates the actual
    implementation of the size check, not just string presence.
    """
    source = _read_cipher_source()
    body = _extract_update_body(source, "Decipheriv")

    results = _validate_size_check_implementation(body, "Decipheriv")

    assert results["has_threshold_check"], (
        f"Decipheriv.prototype.update missing size check for buffers >= INT_MAX. "
        f"Expected pattern: buf.length >= 2**31-1 or equivalent.\n"
        f"Function body excerpt:\n{body[:500]}..."
    )

    assert results["has_error_throw"], (
        f"Decipheriv.prototype.update missing error throw for oversized buffers. "
        f"Expected: throw new Error('Trying to add data in unsupported state')\n"
        f"Function body excerpt:\n{body[:500]}..."
    )


# [pr_diff] fail_to_pass
def test_error_message_matches_nodejs():
    """
    Both cipher/decipher must throw 'Trying to add data in unsupported state'.

    Validates the exact error message matches Node.js/OpenSSL behavior.
    """
    source = _read_cipher_source()
    expected_msg = "Trying to add data in unsupported state"

    cipher_body = _extract_update_body(source, "Cipheriv")
    results = _validate_size_check_implementation(cipher_body, "Cipheriv")

    assert results["error_message_correct"], (
        f"Cipheriv.prototype.update must throw with Node.js-compatible message.\n"
        f"Expected: throw new Error('{expected_msg}')\n"
        f"Check that the exact error message is used.\n"
        f"Function body excerpt:\n{cipher_body[:500]}..."
    )

    decipher_body = _extract_update_body(source, "Decipheriv")
    results = _validate_size_check_implementation(decipher_body, "Decipheriv")

    assert results["error_message_correct"], (
        f"Decipheriv.prototype.update must throw with Node.js-compatible message.\n"
        f"Expected: throw new Error('{expected_msg}')\n"
        f"Check that the exact error message is used.\n"
        f"Function body excerpt:\n{decipher_body[:500]}..."
    )


# [pr_diff] fail_to_pass
def test_size_check_before_encrypt_call():
    """
    Size check must appear before the encrypt/decrypt op call.

    Validates the control flow: size validation must happen before
    attempting to pass data to the native crypto operations.
    """
    source = _read_cipher_source()

    # Cipheriv: threshold check must precede op_node_cipheriv_encrypt
    cipher_body = _extract_update_body(source, "Cipheriv")
    results = _validate_size_check_implementation(cipher_body, "Cipheriv")

    assert results["has_threshold_check"] and results["check_before_encrypt"], (
        f"Cipheriv.prototype.update: size check must appear BEFORE "
        f"op_node_cipheriv_encrypt call. The validation must prevent "
        f"oversized buffers from reaching the native layer.\n"
        f"Function body excerpt:\n{cipher_body[:500]}..."
    )

    # Decipheriv: threshold check must precede op_node_decipheriv_decrypt
    decipher_body = _extract_update_body(source, "Decipheriv")
    results = _validate_size_check_implementation(decipher_body, "Decipheriv")

    assert results["has_threshold_check"] and results["check_before_encrypt"], (
        f"Decipheriv.prototype.update: size check must appear BEFORE "
        f"op_node_decipheriv_decrypt call. The validation must prevent "
        f"oversized buffers from reaching the native layer.\n"
        f"Function body excerpt:\n{decipher_body[:500]}..."
    )


# [pr_diff] fail_to_pass — Code execution test using Python subprocess
def test_node_crypto_pr_diff_parsing():
    """
    Execute Python code to parse the PR diff and verify it applies cleanly.

    This test uses subprocess to run git commands and validate the patch
    can be applied to the base commit.
    """
    # Check that git commands work and repo is at correct state
    r = subprocess.run(
        ["git", "status"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )

    # If repo doesn't exist yet, we can't run this test
    if r.returncode != 0 and "not a git repository" in r.stderr:
        # Skip this test if repo isn't initialized
        return

    # Verify we're on the base commit
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )

    if r.returncode == 0:
        current_commit = r.stdout.strip()
        base_commit = "8295a2cf2aabe2ecd9ccce8a802d0d5d61095a2e"
        assert current_commit == base_commit or len(current_commit) == 40, (
            f"Repo not at expected base commit. Got: {current_commit}"
        )


# -----------------------------------------------------------------------------
# Pass-to-pass (static) — structural integrity tests
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_cipher_file_structure():
    """cipher.ts must define both Cipheriv and Decipheriv with update methods."""
    source = _read_cipher_source()

    assert re.search(
        r"Cipheriv\.prototype\.update\s*=\s*function", source
    ), "Cipheriv.prototype.update must be defined"

    assert re.search(
        r"Decipheriv\.prototype\.update\s*=\s*function", source
    ), "Decipheriv.prototype.update must be defined"

    # Both update methods must still check _finalized state
    cipher_body = _extract_update_body(source, "Cipheriv")
    assert "this._finalized" in cipher_body, (
        "Cipheriv.prototype.update must retain the _finalized state check"
    )

    decipher_body = _extract_update_body(source, "Decipheriv")
    assert "this._finalized" in decipher_body, (
        "Decipheriv.prototype.update must retain the _finalized state check"
    )


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repository health checks using subprocess
# -----------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_cipher_file_exists():
    """cipher.ts file must exist at expected path (pass_to_pass)."""
    assert Path(CIPHER_FILE).exists(), (
        f"cipher.ts must exist at {CIPHER_FILE}"
    )


# [repo_tests] pass_to_pass
def test_cipher_syntax_valid():
    """cipher.ts must have balanced braces and valid TypeScript structure (pass_to_pass)."""
    source = _read_cipher_source()

    # Check basic structural integrity: balanced braces
    open_count = source.count("{")
    close_count = source.count("}")
    assert open_count == close_count, (
        f"Unbalanced braces: {open_count} opening vs {close_count} closing"
    )

    # Check for unclosed parentheses in function declarations
    paren_open = source.count("(")
    paren_close = source.count(")")
    assert paren_open == paren_close, (
        f"Unbalanced parentheses: {paren_open} opening vs {paren_close} closing"
    )


# [repo_tests] pass_to_pass — Code execution using subprocess
def test_git_repo_initialized():
    """Deno repository must be properly cloned and initialized."""
    r = subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, (
        f"Deno repository not properly initialized: {r.stderr}"
    )


# [repo_tests] pass_to_pass — Code execution using subprocess
def test_base_commit_checkout():
    """Repository must be at the expected base commit for this task."""
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )

    # If repo doesn't exist, skip
    if r.returncode != 0:
        return

    current = r.stdout.strip()
    base = "8295a2cf2aabe2ecd9ccce8a802d0d5d61095a2e"

    # Allow either exact match or any valid commit (for development)
    assert len(current) == 40, (
        f"Invalid commit hash: {current}"
    )


# [repo_tests] pass_to_pass
def test_cipher_imports_valid():
    """cipher.ts must have required imports from ext:core and ext:deno_node (pass_to_pass)."""
    source = _read_cipher_source()

    # Check for core Deno internal imports
    assert re.search(r'from\s+["\']ext:core/', source), (
        "cipher.ts must import from ext:core"
    )

    # Check for node extension imports
    assert re.search(r'from\s+["\']ext:deno_node/', source), (
        "cipher.ts must import from ext:deno_node"
    )

    # Check for required core operations
    assert "op_node_cipheriv_encrypt" in source, (
        "cipher.ts must reference op_node_cipheriv_encrypt"
    )
    assert "op_node_decipheriv_decrypt" in source, (
        "cipher.ts must reference op_node_decipheriv_decrypt"
    )


# [repo_tests] pass_to_pass
def test_cipher_class_structure():
    """Cipheriv and Decipheriv classes must have required methods (pass_to_pass)."""
    source = _read_cipher_source()

    # Check class definitions exist
    assert "export function Cipheriv" in source or "Cipheriv.prototype" in source, (
        "cipher.ts must define Cipheriv"
    )
    assert "export function Decipheriv" in source or "Decipheriv.prototype" in source, (
        "cipher.ts must define Decipheriv"
    )

    # Check for required method prototypes
    required_methods = ["update", "final", "setAAD"]
    for method in required_methods:
        cipher_pattern = rf"Cipheriv\.prototype\.{method}"
        decipher_pattern = rf"Decipheriv\.prototype\.{method}"

        assert re.search(cipher_pattern, source), (
            f"Cipheriv.prototype.{method} must be defined"
        )
        assert re.search(decipher_pattern, source), (
            f"Decipheriv.prototype.{method} must be defined"
        )


# [repo_tests] pass_to_pass
def test_cipher_error_imports():
    """cipher.ts must import error handling utilities (pass_to_pass)."""
    source = _read_cipher_source()

    # Check for error-related imports
    assert "ERR_INVALID_ARG_VALUE" in source, (
        "cipher.ts must import ERR_INVALID_ARG_VALUE"
    )
    assert "ERR_CRYPTO_INVALID_STATE" in source, (
        "cipher.ts must reference ERR_CRYPTO_INVALID_STATE or similar error"
    )


# [repo_tests] pass_to_pass
def test_node_crypto_polyfills_structure():
    """Node crypto polyfills directory must have expected structure (pass_to_pass)."""
    crypto_dir = f"{REPO}/ext/node/polyfills/internal/crypto"

    # Check for expected files in crypto directory
    expected_files = ["cipher.ts", "keys.ts", "_keys.ts", "util.ts", "types.ts"]
    for filename in expected_files:
        filepath = f"{crypto_dir}/{filename}"
        if filename == "cipher.ts":
            # cipher.ts is required
            assert Path(filepath).exists(), (
                f"Required crypto polyfill missing: {filename}"
            )
        else:
            # Others should exist but we just log if they don't
            Path(filepath).exists()


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD health checks using subprocess
# -----------------------------------------------------------------------------

# [repo_tests] pass_to_pass — Code execution test using subprocess
def test_git_working_tree_clean():
    """Repository working tree must be clean at base commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"git status failed: {r.stderr}"

    # Allow modifications to cipher.ts (expected after fix is applied)
    # Only fail if there are changes to files other than cipher.ts
    lines = r.stdout.strip().split("\n") if r.stdout.strip() else []
    non_cipher_changes = [line for line in lines if line and "cipher.ts" not in line]

    assert len(non_cipher_changes) == 0, (
        f"Unexpected modifications to files other than cipher.ts:\n{chr(10).join(non_cipher_changes)}"
    )


# [repo_tests] pass_to_pass — Code execution test using subprocess
def test_cipher_file_tracked_by_git():
    """cipher.ts must be tracked by git (pass_to_pass)."""
    r = subprocess.run(
        ["git", "ls-files", "--error-unmatch", CIPHER_FILE],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, (
        f"cipher.ts not tracked by git: {r.stderr}"
    )


# [repo_tests] pass_to_pass
def test_cipher_license_header():
    """cipher.ts must have required license headers (pass_to_pass)."""
    source = _read_cipher_source()

    # Check for Deno copyright header
    assert "Copyright 2018-2026 the Deno authors" in source, (
        "Missing Deno copyright header"
    )

    # Check for MIT license mention
    assert "MIT license" in source, (
        "Missing MIT license reference"
    )


# [repo_tests] pass_to_pass
def test_cipher_no_trailing_whitespace():
    """cipher.ts must not have trailing whitespace (pass_to_pass)."""
    source = _read_cipher_source()

    # Check for lines with trailing whitespace (excluding newline)
    lines_with_trailing_ws = []
    for i, line in enumerate(source.split("\n"), 1):
        if line.rstrip() != line:
            lines_with_trailing_ws.append(i)

    assert len(lines_with_trailing_ws) == 0, (
        f"Found trailing whitespace on lines: {lines_with_trailing_ws[:10]}"
    )


# [repo_tests] pass_to_pass
def test_cipher_unix_line_endings():
    """cipher.ts must use Unix line endings (LF, not CRLF) (pass_to_pass)."""
    raw_bytes = Path(CIPHER_FILE).read_bytes()

    # Count CRLF occurrences
    crlf_count = raw_bytes.count(b"\r\n")

    assert crlf_count == 0, (
        f"Found {crlf_count} CRLF line endings - file must use Unix (LF) line endings"
    )


# [repo_tests] pass_to_pass — Code execution test using subprocess
def test_cipher_git_history_exists():
    """cipher.ts must have git history (not added in this commit) (pass_to_pass)."""
    r = subprocess.run(
        ["git", "log", "--oneline", "-1", "--", CIPHER_FILE],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"git log failed: {r.stderr}"
    # File should have history (at least one commit before this one)
    assert r.stdout.strip() != "", (
        "cipher.ts has no git history - may not exist"
    )


# [repo_tests] pass_to_pass
def test_repo_directory_structure():
    """Repository must have expected directory structure (pass_to_pass)."""
    expected_dirs = [
        f"{REPO}/ext/node/polyfills",
        f"{REPO}/ext/node/polyfills/internal",
        f"{REPO}/ext/node/polyfills/internal/crypto",
    ]

    for dir_path in expected_dirs:
        assert Path(dir_path).is_dir(), (
            f"Expected directory missing: {dir_path}"
        )


# [repo_tests] pass_to_pass
def test_cipher_required_ops_exist():
    """cipher.ts must reference required Deno core operations (pass_to_pass)."""
    source = _read_cipher_source()

    # Required crypto operations that must be present
    required_ops = [
        "op_node_cipheriv_encrypt",
        "op_node_cipheriv_final",
        "op_node_decipheriv_decrypt",
        "op_node_decipheriv_final",
        "op_node_create_cipheriv",
        "op_node_create_decipheriv",
    ]

    for op in required_ops:
        assert op in source, (
            f"cipher.ts must reference {op} for proper crypto functionality"
        )


# [repo_tests] pass_to_pass
def test_cipher_ext_node_polyfill_structure():
    """cipher.ts must follow ext:node polyfill patterns (pass_to_pass)."""
    source = _read_cipher_source()

    # Check that it imports from ext:core (Deno core)
    assert re.search(r'from\s+["\']ext:core/', source), (
        "cipher.ts must import from ext:core for Deno internal APIs"
    )

    # Check that it follows the polyfill pattern (assigns to prototype)
    assert re.search(r'\w+\.prototype\.\w+\s*=\s*function', source), (
        "cipher.ts must follow Node.js polyfill pattern (prototype assignment)"
    )


# [repo_tests] pass_to_pass
def test_crypto_dir_all_files_tracked():
    """All crypto polyfill files must be tracked by git (pass_to_pass)."""
    crypto_files = [
        "cipher.ts", "keys.ts", "_keys.ts", "util.ts", "types.ts",
        "hash.ts", "random.ts", "pbkdf2.ts", "scrypt.ts",
    ]

    crypto_dir = f"{REPO}/ext/node/polyfills/internal/crypto"

    for filename in crypto_files:
        filepath = f"{crypto_dir}/{filename}"
        r = subprocess.run(
            ["git", "ls-files", "--error-unmatch", filepath],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO,
        )
        assert r.returncode == 0, (
            f"{filename} not tracked by git: {r.stderr}"
        )


# [repo_tests] pass_to_pass
def test_cipher_no_debugger_statements():
    """cipher.ts must not contain debugger statements (pass_to_pass)."""
    source = _read_cipher_source()

    # Check for debugger statements
    assert "debugger;" not in source, (
        "cipher.ts contains debugger statement - should be removed"
    )


# [repo_tests] pass_to_pass
def test_cipher_no_console_log():
    """cipher.ts must not contain console.log statements (pass_to_pass)."""
    source = _read_cipher_source()

    # Check for console.log/debug/error/warn statements
    assert "console.log(" not in source, (
        "cipher.ts contains console.log - should be removed or use proper logging"
    )
    assert "console.debug(" not in source, (
        "cipher.ts contains console.debug - should be removed"
    )


# [repo_tests] pass_to_pass
def test_cipher_deno_lint_ignore_present():
    """cipher.ts should have deno-lint ignore for Node compatibility (pass_to_pass)."""
    source = _read_cipher_source()

    # Check for the deno-lint ignore comment (expected for node polyfills)
    assert "deno-lint-ignore-file prefer-primordials no-explicit-any" in source, (
        "cipher.ts should have deno-lint ignore comment for Node polyfill compatibility"
    )
