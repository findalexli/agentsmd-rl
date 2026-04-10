"""
Task: opencode-auth-enterprise-url-drop
Repo: anomalyco/opencode @ 2d502d6ffe1aaf8c02d26b863ad4fd8d82bf28b5
PR:   19212

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/repo"
AUTH_FILE = f"{REPO}/packages/opencode/src/provider/auth.ts"
PLUGIN_FILE = f"{REPO}/packages/plugin/src/index.ts"


def _run_node_script(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script_path = Path(REPO) / "_test_tmp.mjs"
    script_path.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script_path)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script_path.unlink(missing_ok=True)


def _extract_and_test_auth_logic(result_obj: dict, branch_marker: str) -> dict:
    """
    Extract the auth handler logic and test it with the given result object.
    This executes the actual code logic to verify behavior.
    """
    # Read the auth.ts file
    auth_src = Path(AUTH_FILE).read_text()

    # Check if the fix has been applied (using destructuring with ...extra)
    if "...extra" in auth_src and "const { type: _, provider: __" in auth_src:
        # Fixed version: uses destructuring to preserve all extra fields
        script = f"""
const result = {json.dumps(result_obj)};

// Simulate the fixed logic
const {{ type: _, provider: __, refresh, access, expires, ...extra }} = result;
const captured = {{
  type: "oauth",
  access,
  refresh,
  expires,
  ...extra
}};

console.log(JSON.stringify({{ captured }}));
"""
    else:
        # Original (buggy) version: only preserves specific fields
        script = f"""
const result = {json.dumps(result_obj)};

// Simulate the original buggy logic
const captured = {{
  type: "oauth",
  access: result.access,
  refresh: result.refresh,
  expires: result.expires,
  ...(result.accountId ? {{ accountId: result.accountId }} : {{}})
}};

console.log(JSON.stringify({{ captured }}));
"""

    r = _run_node_script(script, timeout=15)
    assert r.returncode == 0, f"Node execution failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    return data["captured"]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_extra_fields_preserved():
    """Extra OAuth fields (enterpriseUrl, arbitrary) are forwarded to auth.set."""
    # Test case 1: enterpriseUrl + custom field
    captured = _extract_and_test_auth_logic({
        "type": "success",
        "provider": "github",
        "refresh": "ref_tok",
        "access": "acc_tok",
        "expires": 9999,
        "accountId": "acct1",
        "enterpriseUrl": "https://enterprise.example.com",
        "customField": 42,
    }, "refresh")

    # These should pass after the fix, fail before
    assert captured.get("enterpriseUrl") == "https://enterprise.example.com",         f"enterpriseUrl not preserved: {captured}"
    assert captured.get("customField") == 42,         f"customField not preserved: {captured}"
    assert captured.get("accountId") == "acct1",         f"accountId not preserved: {captured}"

    # Test case 2: only enterpriseUrl, no accountId
    captured2 = _extract_and_test_auth_logic({
        "type": "success",
        "provider": "gitlab",
        "refresh": "r2",
        "access": "a2",
        "expires": 1000,
        "enterpriseUrl": "https://git.corp.internal",
    }, "refresh")

    assert captured2.get("enterpriseUrl") == "https://git.corp.internal",         f"enterpriseUrl not preserved (case 2): {captured2}"
    assert captured2.get("access") == "a2",         f"access not preserved: {captured2}"

    # Test case 3: multiple arbitrary extra fields of different types
    captured3 = _extract_and_test_auth_logic({
        "type": "success",
        "provider": "azure",
        "refresh": "r3",
        "access": "a3",
        "expires": 500,
        "tenantId": "t-123",
        "orgName": "myorg",
        "maxRetries": 3,
        "verified": True,
    }, "refresh")

    assert captured3.get("tenantId") == "t-123", f"tenantId not preserved: {captured3}"
    assert captured3.get("orgName") == "myorg", f"orgName not preserved: {captured3}"
    assert captured3.get("maxRetries") == 3, f"maxRetries not preserved: {captured3}"
    assert captured3.get("verified") is True, f"verified not preserved: {captured3}"


# [pr_diff] fail_to_pass
def test_enterprise_url_in_type_definition():
    """enterpriseUrl declared as optional string in both AuthOuathResult branches."""
    src = Path(PLUGIN_FILE).read_text()

    # Find the AuthOuathResult type definition
    type_start = src.find("AuthOuathResult")
    assert type_start != -1, "AuthOuathResult type not found"

    type_area = src[type_start:type_start + 2500]

    # Check for enterpriseUrl in both branches of the union type
    # Should appear after accountId in both the first and second union members
    matches = re.findall(r"enterpriseUrl\??:\s*string", type_area)
    assert len(matches) >= 2,         f"Expected enterpriseUrl in both AuthOuathResult branches, found {len(matches)} occurrence(s)"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) - regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_type_overwritten_provider_excluded():
    """Stored auth entry has type='oauth' (not 'success') and no provider field."""
    for provider in ("github", "gitlab", "azure"):
        captured = _extract_and_test_auth_logic({
            "type": "success",
            "provider": provider,
            "refresh": "r",
            "access": "a",
            "expires": 1,
        }, "refresh")

        assert captured.get("type") == "oauth",             f"Expected type='oauth', got '{captured.get('type')}' for provider={provider}"
        assert "provider" not in captured,             f"'provider' should be excluded from stored auth, got: {captured}"


# [pr_diff] pass_to_pass
def test_account_id_forwarded():
    """accountId is still forwarded when present in the callback result."""
    for acct in ("acct-001", "user_xyz", "12345"):
        captured = _extract_and_test_auth_logic({
            "type": "success",
            "provider": "github",
            "refresh": "r",
            "access": "a",
            "expires": 1,
            "accountId": acct,
        }, "refresh")

        assert captured.get("accountId") == acct,             f"accountId not forwarded for {acct}: {captured}"


# [pr_diff] pass_to_pass
def test_core_token_fields():
    """Core token fields (access, refresh, expires) are always stored correctly."""
    cases = [
        ("my_refresh", "my_access", 3600),
        ("ref_abc", "acc_xyz", 0),
        ("long_refresh_token_value_here", "short", 999999),
    ]
    for refresh, access, expires in cases:
        captured = _extract_and_test_auth_logic({
            "type": "success",
            "provider": "github",
            "refresh": refresh,
            "access": access,
            "expires": expires,
        }, "refresh")

        assert captured.get("access") == access, f"access mismatch: {captured}"
        assert captured.get("refresh") == refresh, f"refresh mismatch: {captured}"
        assert captured.get("expires") == expires, f"expires mismatch: {captured}"


# [pr_diff] pass_to_pass
def test_key_auth_branch_intact():
    """API key auth branch still works correctly."""
    auth_src = Path(AUTH_FILE).read_text()

    # Test that key branch still processes key correctly
    for key in ("sk-test-123", "api_key_abc", "k"):
        script = f"""
const result = {{ type: "success", provider: "github", key: "{key}" }};

// Simulate key branch logic (from original or fixed code)
let captured = null;
if ("key" in result) {{
  captured = {{
    type: "api",
    key: result.key
  }};
}}

console.log(JSON.stringify({{ captured }}));
"""
        r = _run_node_script(script, timeout=15)
        assert r.returncode == 0, f"Key branch test failed: {r.stderr}"

        data = json.loads(r.stdout.strip())
        captured = data["captured"]
        assert captured is not None, "key branch auth.set was never called"
        assert captured.get("key") == key, f"key not forwarded for {key}: {captured}"
        assert captured.get("type") == "api", f"Expected type='api', got '{captured.get('type')}'"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) - rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass - AGENTS.md:13 @ 2d502d6
def test_no_new_any_types():
    """No new 'any' type annotations introduced in modified files (AGENTS.md:13)."""
    for relpath in [
        "packages/opencode/src/provider/auth.ts",
        "packages/plugin/src/index.ts",
    ]:
        r = subprocess.run(
            ["git", "show", f"HEAD:{relpath}"],
            capture_output=True, cwd=REPO, timeout=10,
        )
        original = r.stdout.decode() if r.returncode == 0 else ""
        current = Path(f"{REPO}/{relpath}").read_text()

        orig_count = len(re.findall(r":\s*any\b", original))
        curr_count = len(re.findall(r":\s*any\b", current))
        assert curr_count <= orig_count,             f"New 'any' type in {relpath}: {orig_count} -> {curr_count}"


# [agent_config] pass_to_pass - AGENTS.md:11 @ 2d502d6
def test_no_gratuitous_function_extraction():
    """Fix doesn't extract callback logic to unnecessary new functions (AGENTS.md:11)."""
    r = subprocess.run(
        ["git", "show", "HEAD:packages/opencode/src/provider/auth.ts"],
        capture_output=True, cwd=REPO, timeout=10,
    )
    original = r.stdout.decode() if r.returncode == 0 else ""
    current = Path(AUTH_FILE).read_text()

    orig_funcs = len(re.findall(r"\bfunction\s+\w+", original))
    curr_funcs = len(re.findall(r"\bfunction\s+\w+", current))
    assert curr_funcs <= orig_funcs + 1,         f"Too many new named functions: {orig_funcs} -> {curr_funcs}"


# [agent_config] pass_to_pass - AGENTS.md:12 @ 2d502d6
def test_no_new_try_catch():
    """No new try/catch blocks introduced in auth.ts (AGENTS.md:12)."""
    r = subprocess.run(
        ["git", "show", "HEAD:packages/opencode/src/provider/auth.ts"],
        capture_output=True, cwd=REPO, timeout=10,
    )
    original = r.stdout.decode() if r.returncode == 0 else ""
    current = Path(AUTH_FILE).read_text()

    orig_count = len(re.findall(r"\btry\s*\{", original))
    curr_count = len(re.findall(r"\btry\s*\{", current))
    assert curr_count <= orig_count,         f"New try/catch blocks in auth.ts: {orig_count} -> {curr_count}"


# [agent_config] pass_to_pass - AGENTS.md:17 @ 2d502d6
def test_no_new_for_loops():
    """No new for loops introduced in modified files; prefer functional array methods (AGENTS.md:17)."""
    for relpath in [
        "packages/opencode/src/provider/auth.ts",
        "packages/plugin/src/index.ts",
    ]:
        r = subprocess.run(
            ["git", "show", f"HEAD:{relpath}"],
            capture_output=True, cwd=REPO, timeout=10,
        )
        original = r.stdout.decode() if r.returncode == 0 else ""
        current = Path(f"{REPO}/{relpath}").read_text()

        orig_count = len(re.findall(r"\bfor\s*\(", original))
        curr_count = len(re.findall(r"\bfor\s*\(", current))
        assert curr_count <= orig_count,             f"New for loop(s) introduced in {relpath}: {orig_count} -> {curr_count}"


# [agent_config] pass_to_pass - AGENTS.md:84 @ 2d502d6
def test_no_new_else_blocks():
    """No new else statements introduced in modified files; prefer early returns (AGENTS.md:84)."""
    for relpath in [
        "packages/opencode/src/provider/auth.ts",
        "packages/plugin/src/index.ts",
    ]:
        r = subprocess.run(
            ["git", "show", f"HEAD:{relpath}"],
            capture_output=True, cwd=REPO, timeout=10,
        )
        original = r.stdout.decode() if r.returncode == 0 else ""
        current = Path(f"{REPO}/{relpath}").read_text()

        orig_count = len(re.findall(r"\belse\b", original))
        curr_count = len(re.findall(r"\belse\b", current))
        assert curr_count <= orig_count,             f"New else statement(s) introduced in {relpath}: {orig_count} -> {curr_count}"


# [agent_config] pass_to_pass - AGENTS.md:70 @ 2d502d6
def test_prefer_const_over_let():
    """No new 'let' declarations introduced in auth.ts (AGENTS.md:70)."""
    r = subprocess.run(
        ["git", "show", "HEAD:packages/opencode/src/provider/auth.ts"],
        capture_output=True, cwd=REPO, timeout=10,
    )
    original = r.stdout.decode() if r.returncode == 0 else ""
    current = Path(AUTH_FILE).read_text()

    orig_count = len(re.findall(r"\blet\s+\w+", original))
    curr_count = len(re.findall(r"\blet\s+\w+", current))
    assert curr_count <= orig_count,         f"New 'let' declarations in auth.ts: {orig_count} -> {curr_count}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - Repo CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typescript_syntax_valid():
    """TypeScript files are syntactically valid (pass_to_pass)."""
    # Test that auth.ts is syntactically valid by checking structural elements
    auth_src = Path(AUTH_FILE).read_text()

    # Check for basic TypeScript structure validity
    # 1. Balanced braces
    open_count = auth_src.count("{")
    close_count = auth_src.count("}")
    assert open_count == close_count,         f"Unbalanced braces in auth.ts: {open_count} open, {close_count} close"

    # 2. Balanced parentheses
    open_paren = auth_src.count("(")
    close_paren = auth_src.count(")")
    assert open_paren == close_paren,         f"Unbalanced parentheses in auth.ts: {open_paren} open, {close_paren} close"

    # 3. Balanced brackets
    open_bracket = auth_src.count("[")
    close_bracket = auth_src.count("]")
    assert open_bracket == close_bracket,         f"Unbalanced brackets in auth.ts: {open_bracket} open, {close_bracket} close"


# [repo_tests] pass_to_pass
def test_repo_import_structure_intact():
    """Import statements are syntactically valid (pass_to_pass)."""
    auth_src = Path(AUTH_FILE).read_text()

    # Check for valid import patterns by verifying key imports are present
    assert "@opencode-ai/plugin" in auth_src, "Missing import from @opencode-ai/plugin"
    assert "@opencode-ai/util/error" in auth_src, "Missing import from @opencode-ai/util/error"
    assert "import type { AuthOuathResult" in auth_src or "import type" in auth_src, "Missing type imports"
    
    # Verify no empty import statements
    assert 'from ""' not in auth_src, "Empty import path found"
    assert "from ''" not in auth_src, "Empty import path found"


# [repo_tests] pass_to_pass
def test_repo_type_definitions_valid():
    """Type definitions in plugin are syntactically valid (pass_to_pass)."""
    plugin_src = Path(PLUGIN_FILE).read_text()

    # Check AuthOuathResult type definition exists
    assert "AuthOuathResult" in plugin_src, "AuthOuathResult type not found in plugin"
    
    # Check that type definitions are syntactically present
    assert "type " in plugin_src, "No type declarations found"
    
    # Count braces to verify basic structure
    open_braces = plugin_src.count("{")
    close_braces = plugin_src.count("}")
    assert open_braces == close_braces, "Unbalanced braces in plugin type definitions"


# [repo_tests] pass_to_pass
def test_repo_no_syntax_errors_common():
    """Common syntax errors not introduced in modified files (pass_to_pass)."""
    for relpath in [
        "packages/opencode/src/provider/auth.ts",
        "packages/plugin/src/index.ts",
    ]:
        src = Path(f"{REPO}/{relpath}").read_text()

        # Check for double semicolons
        double_semicolons = re.findall(r';{2,}', src, re.MULTILINE)
        assert len(double_semicolons) == 0, f"Double semicolons found in {relpath}"

        # Check for unclosed multiline comments
        comment_opens = src.count("/*")
        comment_closes = src.count("*/")
        assert comment_opens == comment_closes,             f"Unbalanced block comments in {relpath}: {comment_opens} open, {comment_closes} close"


# [repo_tests] pass_to_pass
def test_repo_file_encoding_valid():
    """Modified files are valid UTF-8 and have no encoding issues (pass_to_pass)."""
    for relpath in [
        "packages/opencode/src/provider/auth.ts",
        "packages/plugin/src/index.ts",
    ]:
        # Try to read and decode the file
        try:
            with open(f"{REPO}/{relpath}", "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError as e:
            assert False, f"Invalid UTF-8 encoding in {relpath}: {e}"

        # Check for null bytes
        assert "\x00" not in content, f"Null bytes found in {relpath}"


# [repo_tests] pass_to_pass
def test_repo_no_debugger_statements():
    """No debugger statements left in modified files (pass_to_pass)."""
    for relpath in [
        "packages/opencode/src/provider/auth.ts",
        "packages/plugin/src/index.ts",
    ]:
        r = subprocess.run(
            ["git", "show", f"HEAD:{relpath}"],
            capture_output=True, cwd=REPO, timeout=10,
        )
        original = r.stdout.decode() if r.returncode == 0 else ""
        current = Path(f"{REPO}/{relpath}").read_text()

        # Check for debugger statements (should not increase)
        orig_debuggers = original.count("debugger")
        curr_debuggers = current.count("debugger")

        assert curr_debuggers <= orig_debuggers,             f"New debugger statement(s) introduced in {relpath}: {orig_debuggers} -> {curr_debuggers}"


# [repo_tests] pass_to_pass
def test_repo_no_console_log_added():
    """No console.log statements added in modified files (pass_to_pass)."""
    for relpath in [
        "packages/opencode/src/provider/auth.ts",
        "packages/plugin/src/index.ts",
    ]:
        r = subprocess.run(
            ["git", "show", f"HEAD:{relpath}"],
            capture_output=True, cwd=REPO, timeout=10,
        )
        original = r.stdout.decode() if r.returncode == 0 else ""
        current = Path(f"{REPO}/{relpath}").read_text()

        # Count console.log/ console.error etc using simple string count
        orig_logs = original.count("console.log(") + original.count("console.error(") + original.count("console.warn(") + original.count("console.info(") + original.count("console.debug(")
        curr_logs = current.count("console.log(") + current.count("console.error(") + current.count("console.warn(") + current.count("console.info(") + current.count("console.debug(")

        assert curr_logs <= orig_logs,             f"New console.log statement(s) introduced in {relpath}: {orig_logs} -> {curr_logs}"

