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


# ---------------------------------------------------------------------------
# Helper: extract the "refresh in result" if-block body and execute it
# with a mocked auth.set generator, returning what was captured.
# ---------------------------------------------------------------------------

def _run_refresh_branch(result_obj: dict) -> dict:
    """Execute the refresh branch with the given result object and return captured auth entry."""
    script = f"""
    'use strict';
    const fs = require('fs');
    const src = fs.readFileSync('{AUTH_FILE}', 'utf8');

    const marker = '"refresh" in result';
    const mIdx = src.indexOf(marker);
    if (mIdx === -1) {{ process.stdout.write(JSON.stringify({{error: 'no_refresh_branch'}})); process.exit(0); }}

    const after = src.substring(mIdx);
    const bodyStart = after.indexOf('{{');
    let depth = 0, bodyEnd = -1;
    for (let i = bodyStart; i < after.length; i++) {{
      if (after[i] === '{{') depth++;
      if (after[i] === '}}') {{ depth--; if (depth === 0) {{ bodyEnd = i; break; }} }}
    }}
    if (bodyEnd === -1) {{ process.stdout.write(JSON.stringify({{error: 'no_block_end'}})); process.exit(0); }}

    const body = after.substring(bodyStart + 1, bodyEnd).trim();

    let captured = null;
    const auth = {{ set: function*(id, obj) {{ captured = obj; }} }};
    const input = {{ providerID: 'test-provider' }};
    const result = {json.dumps(result_obj)};

    try {{
      const fn = new Function('auth', 'input', 'result',
        'const gen = (function*() {{' + body + '}})();' +
        'let step; do {{ step = gen.next(); }} while (!step.done);'
      );
      fn(auth, input, result);
      process.stdout.write(JSON.stringify({{captured}}));
    }} catch(e) {{
      process.stdout.write(JSON.stringify({{error: e.message}}));
    }}
    """
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, timeout=15, cwd=REPO,
    )
    data = json.loads(r.stdout.decode())
    assert "error" not in data, f"Node execution error: {data['error']}"
    assert data["captured"] is not None, "auth.set was never called"
    return data["captured"]


def _run_key_branch(result_obj: dict) -> dict:
    """Execute the 'key in result' branch and return captured auth entry."""
    script = f"""
    'use strict';
    const fs = require('fs');
    const src = fs.readFileSync('{AUTH_FILE}', 'utf8');

    const marker = '"key" in result';
    const mIdx = src.indexOf(marker);
    if (mIdx === -1) {{ process.stdout.write(JSON.stringify({{error: 'no_key_branch'}})); process.exit(0); }}

    const after = src.substring(mIdx);
    const bodyStart = after.indexOf('{{');
    let depth = 0, bodyEnd = -1;
    for (let i = bodyStart; i < after.length; i++) {{
      if (after[i] === '{{') depth++;
      if (after[i] === '}}') {{ depth--; if (depth === 0) {{ bodyEnd = i; break; }} }}
    }}
    const body = after.substring(bodyStart + 1, bodyEnd).trim();

    let captured = null;
    const auth = {{ set: function*(id, obj) {{ captured = obj; }} }};
    const input = {{ providerID: 'test' }};
    const result = {json.dumps(result_obj)};

    try {{
      const fn = new Function('auth', 'input', 'result',
        'const gen = (function*() {{' + body + '}})();' +
        'let step; do {{ step = gen.next(); }} while (!step.done);'
      );
      fn(auth, input, result);
      process.stdout.write(JSON.stringify({{captured}}));
    }} catch(e) {{
      process.stdout.write(JSON.stringify({{error: e.message}}));
    }}
    """
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, timeout=15, cwd=REPO,
    )
    data = json.loads(r.stdout.decode())
    assert "error" not in data, f"Node execution error: {data['error']}"
    assert data["captured"] is not None, "auth.set was never called"
    return data["captured"]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_extra_fields_preserved():
    """Extra OAuth fields (enterpriseUrl, arbitrary) are forwarded to auth.set."""
    # Case 1: enterpriseUrl + custom field
    c1 = _run_refresh_branch({
        "type": "success", "provider": "github",
        "refresh": "ref_tok", "access": "acc_tok", "expires": 9999,
        "accountId": "acct1",
        "enterpriseUrl": "https://enterprise.example.com",
        "customField": 42,
    })
    assert c1["enterpriseUrl"] == "https://enterprise.example.com"
    assert c1["customField"] == 42
    assert c1["accountId"] == "acct1"

    # Case 2: only enterpriseUrl, no accountId
    c2 = _run_refresh_branch({
        "type": "success", "provider": "gitlab",
        "refresh": "r2", "access": "a2", "expires": 1000,
        "enterpriseUrl": "https://git.corp.internal",
    })
    assert c2["enterpriseUrl"] == "https://git.corp.internal"
    assert c2["access"] == "a2"

    # Case 3: multiple arbitrary extra fields of different types
    c3 = _run_refresh_branch({
        "type": "success", "provider": "azure",
        "refresh": "r3", "access": "a3", "expires": 500,
        "tenantId": "t-123",
        "orgName": "myorg",
        "maxRetries": 3,
        "verified": True,
    })
    assert c3["tenantId"] == "t-123"
    assert c3["orgName"] == "myorg"
    assert c3["maxRetries"] == 3
    assert c3["verified"] is True


# [pr_diff] fail_to_pass
def test_enterprise_url_in_type_definition():
    """enterpriseUrl declared as optional string in both AuthOuathResult branches."""
    src = Path(PLUGIN_FILE).read_text()
    type_start = src.index("AuthOuathResult")
    type_area = src[type_start:type_start + 2000]
    matches = re.findall(r"enterpriseUrl\s*\??\s*:\s*string", type_area)
    assert len(matches) >= 2, \
        f"Expected enterpriseUrl in both AuthOuathResult branches, found {len(matches)} occurrence(s)"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_type_overwritten_provider_excluded():
    """Stored auth entry has type='oauth' (not 'success') and no provider field."""
    for provider in ("github", "gitlab", "azure"):
        captured = _run_refresh_branch({
            "type": "success", "provider": provider,
            "refresh": "r", "access": "a", "expires": 1,
        })
        assert captured["type"] == "oauth", \
            f"Expected type='oauth', got '{captured.get('type')}' for provider={provider}"
        assert "provider" not in captured, \
            f"'provider' should be excluded from stored auth, got: {captured}"


# [pr_diff] pass_to_pass
def test_account_id_forwarded():
    """accountId is still forwarded when present in the callback result."""
    for acct in ("acct-001", "user_xyz", "12345"):
        captured = _run_refresh_branch({
            "type": "success", "provider": "github",
            "refresh": "r", "access": "a", "expires": 1,
            "accountId": acct,
        })
        assert captured["accountId"] == acct, \
            f"accountId not forwarded for {acct}: {captured}"


# [pr_diff] pass_to_pass
def test_core_token_fields():
    """Core token fields (access, refresh, expires) are always stored correctly."""
    cases = [
        ("my_refresh", "my_access", 3600),
        ("ref_abc", "acc_xyz", 0),
        ("long_refresh_token_value_here", "short", 999999),
    ]
    for refresh, access, expires in cases:
        captured = _run_refresh_branch({
            "type": "success", "provider": "github",
            "refresh": refresh, "access": access, "expires": expires,
        })
        assert captured["access"] == access
        assert captured["refresh"] == refresh
        assert captured["expires"] == expires


# [pr_diff] pass_to_pass
def test_key_auth_branch_intact():
    """API key auth branch still works correctly."""
    for key in ("sk-test-123", "api_key_abc", "k"):
        captured = _run_key_branch({
            "type": "success", "provider": "github", "key": key,
        })
        assert captured["key"] == key, f"key not forwarded for {key}: {captured}"
        assert captured["type"] == "api", f"Expected type='api', got '{captured.get('type')}'"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:13 @ 2d502d6
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
        assert curr_count <= orig_count, \
            f"New 'any' type in {relpath}: {orig_count} → {curr_count}"


# [agent_config] pass_to_pass — AGENTS.md:11 @ 2d502d6
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
    assert curr_funcs <= orig_funcs + 1, \
        f"Too many new named functions: {orig_funcs} → {curr_funcs}"


# [agent_config] pass_to_pass — AGENTS.md:12 @ 2d502d6
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
    assert curr_count <= orig_count, \
        f"New try/catch blocks in auth.ts: {orig_count} → {curr_count}"


# [agent_config] pass_to_pass — AGENTS.md:70 @ 2d502d6
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
    assert curr_count <= orig_count, \
        f"New 'let' declarations in auth.ts: {orig_count} → {curr_count}"
