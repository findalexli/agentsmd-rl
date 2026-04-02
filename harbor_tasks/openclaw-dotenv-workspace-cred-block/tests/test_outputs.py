"""
Task: openclaw-dotenv-workspace-cred-block
Repo: openclaw/openclaw @ 29cb1e3c7edd54a3d060419ffa153eecbd19c133
PR:   57767

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/openclaw"
TARGET = f"{REPO}/src/infra/dotenv.ts"

# ---------------------------------------------------------------------------
# Helper: extract shouldBlockWorkspaceDotEnvKey from the TS source and call it
# ---------------------------------------------------------------------------

_EXTRACT_JS = r"""
const fs = require('fs');
const code = fs.readFileSync(process.argv[1], 'utf8');

let js = code;
js = js.replace(/^import\s+.*?;?\s*$/gm, '');
js = js.replace(/^export\s+/gm, '');
js = js.replace(/:\s*(string|boolean|number|void|Record<[^>]+>|Set<[^>]+>|[A-Z]\w*(\[\])?)\b/g, '');
js = js.replace(/\s+as\s+const\b/g, '');

const preamble = `
  function isDangerousHostEnvVarName(key) { return false; }
  function isDangerousHostEnvOverrideVarName(key) { return false; }
  function normalizeEnvVarKey(key) { return key; }
  function resolveConfigDir() { return '/tmp'; }
  const dotenv = { parse: () => ({}) };
  const fs = require('fs');
  const path = require('path');
`;

const lines = js.split('\n');
const relevantCode = [];
let braceDepth = 0;
let capturing = false;

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  if (/^\s*(const\s+BLOCKED_WORKSPACE|function\s+shouldBlock)/.test(line)) {
    capturing = true;
    braceDepth = 0;
  }
  if (capturing) {
    relevantCode.push(line);
    for (const ch of line) {
      if (ch === '{' || ch === '[' || ch === '(') braceDepth++;
      if (ch === '}' || ch === ']' || ch === ')') braceDepth--;
    }
    if (braceDepth <= 0 && (line.trimEnd().endsWith(';') || line.trimEnd().endsWith('}'))) {
      capturing = false;
    }
  }
}

const fullCode = preamble + '\n' + relevantCode.join('\n') + `
  module.exports = { shouldBlockWorkspaceDotEnvKey };
`;

const m = { exports: {} };
const fn = new Function('require', 'module', 'exports', '__filename', '__dirname', fullCode);
fn(require, m, m.exports, __filename, __dirname);
const { shouldBlockWorkspaceDotEnvKey } = m.exports;

const tests = JSON.parse(process.argv[2]);
const results = {};
for (const [key, expected] of Object.entries(tests)) {
  try {
    const actual = shouldBlockWorkspaceDotEnvKey(key);
    results[key] = { expected, actual: !!actual, pass: !!actual === expected };
  } catch (e) {
    results[key] = { expected, actual: 'ERROR: ' + e.message, pass: false };
  }
}
console.log(JSON.stringify(results));
"""


def _check_keys(test_map: dict[str, bool]) -> dict:
    """Call shouldBlockWorkspaceDotEnvKey for each key and return results."""
    r = subprocess.run(
        ["node", "-e", _EXTRACT_JS, TARGET, json.dumps(test_map)],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"Extraction failed:\nstdout: {r.stdout.decode()}\nstderr: {r.stderr.decode()}"
    )
    results = json.loads(r.stdout.decode())
    return results


def _assert_all_pass(test_map: dict[str, bool]):
    """Run key checks and assert every one matches expected."""
    results = _check_keys(test_map)
    failures = {k: v for k, v in results.items() if not v["pass"]}
    assert not failures, f"Key check failures: {json.dumps(failures, indent=2)}"


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_exists_and_parses():
    """Target file exists and has no obvious syntax errors."""
    assert Path(TARGET).exists(), f"{TARGET} does not exist"
    # Basic parse check: node can read and eval the relevant section
    r = subprocess.run(
        ["node", "-e", f"""
            const code = require('fs').readFileSync('{TARGET}', 'utf8');
            try {{ new Function(code); }} catch(e) {{
                if (e instanceof SyntaxError
                    && !e.message.includes('import')
                    && !e.message.includes('export')
                    && !e.message.includes('await'))
                    process.exit(1);
            }}
        """],
        capture_output=True, timeout=10,
    )
    assert r.returncode == 0, "TypeScript file has syntax errors"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_core_credential_keys_blocked():
    """ANTHROPIC_API_KEY and OPENAI_API_KEY must be blocked from workspace .env."""
    _assert_all_pass({
        "ANTHROPIC_API_KEY": True,
        "OPENAI_API_KEY": True,
    })


# [pr_diff] fail_to_pass
def test_oauth_and_secondary_keys_blocked():
    """ANTHROPIC_OAUTH_TOKEN and OPENAI_API_KEYS must be blocked."""
    _assert_all_pass({
        "ANTHROPIC_OAUTH_TOKEN": True,
        "OPENAI_API_KEYS": True,
    })


# [pr_diff] fail_to_pass
def test_gateway_auth_vars_blocked():
    """Gateway authentication vars must be blocked from workspace .env."""
    _assert_all_pass({
        "OPENCLAW_GATEWAY_TOKEN": True,
        "OPENCLAW_GATEWAY_PASSWORD": True,
        "OPENCLAW_GATEWAY_SECRET": True,
    })


# [pr_diff] fail_to_pass
def test_live_provider_keys_blocked():
    """OPENCLAW_LIVE_* provider keys must be blocked."""
    _assert_all_pass({
        "OPENCLAW_LIVE_ANTHROPIC_KEY": True,
        "OPENCLAW_LIVE_ANTHROPIC_KEYS": True,
        "OPENCLAW_LIVE_OPENAI_KEY": True,
        "OPENCLAW_LIVE_GEMINI_KEY": True,
    })


# [pr_diff] fail_to_pass
def test_prefix_based_blocking():
    """Suffixed variants (e.g. _SECONDARY, _BACKUP) must be blocked via prefix matching."""
    _assert_all_pass({
        "ANTHROPIC_API_KEY_SECONDARY": True,
        "ANTHROPIC_API_KEY_V2": True,
        "OPENAI_API_KEY_BACKUP": True,
        "OPENAI_API_KEY_SECONDARY": True,
    })


# ---------------------------------------------------------------------------
# Pass-to-pass — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_original_blocked_keys_preserved():
    """Pre-existing blocked keys (proxy, state-dir) must still be blocked."""
    _assert_all_pass({
        "ALL_PROXY": True,
        "HTTP_PROXY": True,
        "HTTPS_PROXY": True,
        "OPENCLAW_STATE_DIR": True,
        "OPENCLAW_CONFIG_PATH": True,
    })


# [pr_diff] pass_to_pass
def test_safe_keys_allowed():
    """Unrelated env vars must NOT be blocked."""
    _assert_all_pass({
        "MY_CUSTOM_VAR": False,
        "DATABASE_URL": False,
        "APP_SECRET": False,
        "NODE_ENV": False,
    })


# [pr_diff] pass_to_pass
def test_base_url_suffix_still_blocked():
    """_BASE_URL suffix blocking must still work."""
    _assert_all_pass({
        "OPENAI_BASE_URL": True,
        "CUSTOM_SERVICE_BASE_URL": True,
    })


# [pr_diff] pass_to_pass
def test_case_insensitive_blocking():
    """Blocking must be case-insensitive (function uppercases input)."""
    _assert_all_pass({
        "anthropic_api_key": True,
        "Openai_Api_Key": True,
        "openclaw_gateway_token": True,
    })


# ---------------------------------------------------------------------------
# Anti-stub (static, pass_to_pass)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_function_not_stub():
    """shouldBlockWorkspaceDotEnvKey must have real logic, not just return true/false."""
    code = Path(TARGET).read_text()
    import re
    fn_match = re.search(
        r"function shouldBlockWorkspaceDotEnvKey[\s\S]*?\n\}", code
    )
    assert fn_match, "shouldBlockWorkspaceDotEnvKey function not found"
    body = fn_match.group(0)
    assert re.search(r"\.has\(|\.includes\(|===|\.test\(|\.some\(|\.startsWith\(|\.endsWith\(", body), \
        "Function body has no checking logic"
    non_comment_lines = [
        l for l in body.split("\n")
        if l.strip() and not l.strip().startswith("//")
    ]
    assert len(non_comment_lines) >= 4, "Function body is too short (likely a stub)"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:146 @ 29cb1e3c7edd54a3d060419ffa153eecbd19c133
def test_no_inline_lint_suppressions():
    """No inline lint suppressions in dotenv.ts (CLAUDE.md:146)."""
    code = Path(TARGET).read_text()
    assert "@ts-nocheck" not in code, "@ts-nocheck found in dotenv.ts"
    assert "@ts-ignore" not in code, "@ts-ignore found in dotenv.ts"
    for i, line in enumerate(code.split("\n"), 1):
        assert "eslint-disable" not in line, f"eslint-disable at line {i}: {line.strip()}"
        assert "oxlint-disable" not in line, f"oxlint-disable at line {i}: {line.strip()}"


# [agent_config] pass_to_pass — CLAUDE.md:144 @ 29cb1e3c7edd54a3d060419ffa153eecbd19c133
def test_no_bare_any_type():
    """No bare 'any' type annotations in dotenv.ts (CLAUDE.md:144)."""
    import re
    code = Path(TARGET).read_text()
    for i, line in enumerate(code.split("\n"), 1):
        if "//" in line:
            line = line[:line.index("//")]
        if re.search(r":\s*any\b", line):
            raise AssertionError(f"Bare 'any' type at line {i}: {line.strip()}")
