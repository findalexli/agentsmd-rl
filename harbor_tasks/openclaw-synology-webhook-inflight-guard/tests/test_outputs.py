"""
Task: openclaw-synology-webhook-inflight-guard
Repo: openclaw/openclaw @ 7a953a52271b9188a5fa830739a4366614ff9916
PR:   57729

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

import pytest

REPO = "/workspace/openclaw"
HANDLER = f"{REPO}/extensions/synology-chat/src/webhook-handler.ts"
TEST_UTILS = f"{REPO}/extensions/synology-chat/src/test-http-utils.ts"
VITEST_JSON = "/tmp/vitest-behavioral.json"


def _read(path: str) -> str:
    return Path(path).read_text()


def _strip_comments(code: str) -> str:
    """Remove single-line // and block /* */ comments."""
    code = re.sub(r"//[^\n]*", "", code)
    code = re.sub(r"/\*[\s\S]*?\*/", "", code)
    return code


def _handler_code() -> str:
    return _strip_comments(_read(HANDLER))


# ---------------------------------------------------------------------------
# Behavioral vitest code — written to a temp file and executed once
# ---------------------------------------------------------------------------

_BEHAVIORAL_VITEST = r'''
import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  createWebhookHandler,
  clearSynologyWebhookRateLimiterStateForTest,
} from "./webhook-handler.js";
import { makeStalledReq, makeRes } from "./test-http-utils.js";
import type { ResolvedSynologyChatAccount } from "./types.js";

function makeAccount(
  overrides: Partial<ResolvedSynologyChatAccount> = {},
): ResolvedSynologyChatAccount {
  return {
    accountId: "default",
    enabled: true,
    token: "valid-token",
    incomingUrl: "https://nas.example.com/incoming",
    nasHost: "nas.example.com",
    webhookPath: "/webhook/synology",
    webhookPathSource: "default",
    dangerouslyAllowNameMatching: false,
    dangerouslyAllowInheritedWebhookPath: false,
    dmPolicy: "open",
    allowedUserIds: [],
    rateLimitPerMinute: 30,
    botName: "TestBot",
    allowInsecureSsl: true,
    ...overrides,
  };
}

const log = {
  info: vi.fn(),
  warn: vi.fn(),
  error: vi.fn(),
  debug: vi.fn(),
};

beforeEach(() => {
  clearSynologyWebhookRateLimiterStateForTest();
  vi.restoreAllMocks();
});

function makeHandler(accountId: string) {
  return createWebhookHandler({
    account: makeAccount({ accountId }),
    deliver: vi.fn(),
    log,
  });
}

function stalledBatch(n: number, ip: string) {
  const reqs = Array.from({ length: n }, () => {
    const r = makeStalledReq("POST");
    (r.socket as { remoteAddress?: string }).remoteAddress = ip;
    return r;
  });
  const ress = reqs.map(() => makeRes());
  return { reqs, ress };
}

describe("behavioral", () => {
  it("concurrent_requests_429", async () => {
    const handler = makeHandler("b-429-" + Date.now());
    const { reqs, ress } = stalledBatch(12, "203.0.113.1");
    reqs.map((r, i) => handler(r, ress[i]));
    await new Promise((resolve) => setTimeout(resolve, 50));

    const rejected = ress.filter((r) => r._status === 429).length;
    expect(rejected).toBeGreaterThan(0);
    expect(rejected).toBeLessThan(12);

    for (const r of reqs) r.emit("end");
  });

  it("makeres_statuscode_sync", () => {
    const res = makeRes();
    for (const code of [100, 200, 301, 404, 429, 500]) {
      res.statusCode = code;
      expect(res._status).toBe(code);
    }
    res._status = 503;
    expect(res.statusCode).toBe(503);
  });

  it("shared_limiter_across_handlers", async () => {
    const acctId = "shared-" + Date.now();
    const h1 = makeHandler(acctId);
    const h2 = makeHandler(acctId);

    const b1 = stalledBatch(5, "203.0.113.2");
    b1.reqs.map((r, i) => h1(r, b1.ress[i]));
    await new Promise((resolve) => setTimeout(resolve, 50));

    const b2 = stalledBatch(5, "203.0.113.2");
    b2.reqs.map((r, i) => h2(r, b2.ress[i]));
    await new Promise((resolve) => setTimeout(resolve, 50));

    // 5 already in-flight from h1, so at least some of h2's 5 must be rejected
    const rejected2 = b2.ress.filter((r) => r._status === 429).length;
    expect(rejected2).toBeGreaterThan(0);

    for (const r of [...b1.reqs, ...b2.reqs]) r.emit("end");
  });

  it("cleanup_resets_inflight", async () => {
    const acctId = "clear-" + Date.now();

    async function sendBatch() {
      const handler = makeHandler(acctId);
      const { reqs, ress } = stalledBatch(12, "203.0.113.3");
      const runs = reqs.map((r, i) => handler(r, ress[i]));
      await new Promise((resolve) => setTimeout(resolve, 50));
      const rej = ress.filter((r) => r._status === 429).length;
      for (const r of reqs) r.emit("end");
      await Promise.allSettled(runs);
      return rej;
    }

    const rej1 = await sendBatch();
    expect(rej1).toBeGreaterThan(0);

    clearSynologyWebhookRateLimiterStateForTest();

    const rej2 = await sendBatch();
    expect(rej2).toBeGreaterThan(0);
    expect(rej2).toBe(rej1);
  });
});
'''


# ---------------------------------------------------------------------------
# Session fixture — npm install + behavioral vitest (runs once)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def vitest_behavioral():
    """Install npm deps, run behavioral vitest tests, return per-test results."""
    install = subprocess.run(
        ["npm", "install", "--ignore-scripts"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    if install.returncode != 0:
        return None

    test_path = Path(f"{REPO}/extensions/synology-chat/src/_behavioral.test.ts")
    test_path.write_text(_BEHAVIORAL_VITEST)
    json_path = Path(VITEST_JSON)
    try:
        r = subprocess.run(
            ["npx", "vitest", "run", str(test_path),
             "--reporter=verbose",
             "--reporter=json", f"--outputFile={VITEST_JSON}"],
            cwd=REPO, capture_output=True, text=True, timeout=60,
        )
        results = {"_ok": r.returncode == 0,
                    "_output": (r.stdout + r.stderr)[-2000:]}

        # Parse per-test results from JSON output file
        if json_path.exists():
            try:
                data = json.loads(json_path.read_text())
                for suite in data.get("testResults", []):
                    for t in suite.get("assertionResults", []):
                        title = t.get("title", "")
                        results[title] = t.get("status") == "passed"
            except (json.JSONDecodeError, KeyError):
                pass
        return results
    finally:
        test_path.unlink(missing_ok=True)
        json_path.unlink(missing_ok=True)


def _assert_vitest(vitest_behavioral, test_name):
    """Assert that a specific behavioral vitest test passed."""
    if vitest_behavioral is None:
        pytest.skip("npm install failed — cannot run vitest")
    if test_name in vitest_behavioral:
        assert vitest_behavioral[test_name], (
            f"Test '{test_name}' failed:\n{vitest_behavioral.get('_output', '')}"
        )
    else:
        # Couldn't parse individual results; fall back to overall
        assert vitest_behavioral.get("_ok"), (
            f"Behavioral tests failed:\n{vitest_behavioral.get('_output', '')}"
        )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_files_exist():
    """Modified files (webhook-handler.ts, test-http-utils.ts) must exist."""
    assert Path(HANDLER).is_file(), f"{HANDLER} does not exist"
    assert Path(TEST_UTILS).is_file(), f"{TEST_UTILS} does not exist"


# ---------------------------------------------------------------------------
# Behavioral fail-to-pass (pr_diff) — vitest execution
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_concurrent_requests_429(vitest_behavioral):
    """Excess concurrent pre-auth body reads are rejected with HTTP 429."""
    _assert_vitest(vitest_behavioral, "concurrent_requests_429")


# [pr_diff] fail_to_pass
def test_makeres_statuscode_sync(vitest_behavioral):
    """makeRes() statusCode property is synced bidirectionally to _status."""
    _assert_vitest(vitest_behavioral, "makeres_statuscode_sync")


# [pr_diff] fail_to_pass
def test_shared_limiter_across_handlers(vitest_behavioral):
    """Module-level limiter is shared across handler instances (not per-request)."""
    _assert_vitest(vitest_behavioral, "shared_limiter_across_handlers")


# [pr_diff] fail_to_pass
def test_cleanup_clears_inflight_limiter(vitest_behavioral):
    """clearSynologyWebhookRateLimiterStateForTest() resets in-flight limiter."""
    _assert_vitest(vitest_behavioral, "cleanup_resets_inflight")


# [pr_diff] fail_to_pass
def test_account_scoped_inflight_key():
    """In-flight key uses account-level scoping, not fragile remoteAddress."""
    src = _read(HANDLER)

    # Try to find and execute a dedicated key function via node
    r = subprocess.run(
        ["node", "-e", r"""
const fs = require('fs');
const src = fs.readFileSync('%s', 'utf8');
const pats = [
    /function\s+\w*[Ii]n[Ff]light[Kk]ey\w*\s*\((\w+)[^)]*\)[^{]*\{([^}]*)}/s,
    /function\s+\w*[Ww]ebhook[Kk]ey\w*\s*\((\w+)[^)]*\)[^{]*\{([^}]*)}/s,
    /(?:const|let)\s+\w*[Kk]ey\w*\s*=\s*\((\w+)[^)]*\)\s*(?::\s*\w+\s*)?=>\s*\{?([^;}{]*)/,
];
for (const pat of pats) {
    const m = src.match(pat);
    if (!m) continue;
    const param = m[1];
    let body = m[2].trim().replace(/:\s*[A-Z]\w*(\[\])?/g, '').replace(/<[^>]+>/g, '');
    if (!body.startsWith('return') && !body.includes('{')) body = 'return ' + body;
    try {
        const fn = new Function(param, body);
        const r1 = fn({ accountId: 'acct-AAA', id: 'acct-AAA' });
        const r2 = fn({ accountId: 'acct-BBB', id: 'acct-BBB' });
        if (typeof r1 === 'string' && typeof r2 === 'string' &&
            r1.includes('acct-AAA') && r2.includes('acct-BBB') && r1 !== r2) {
            console.log('OK');
            process.exit(0);
        }
    } catch(e) {}
}
process.exit(1);
""" % HANDLER],
        cwd=REPO, capture_output=True, text=True, timeout=15,
    )
    if r.returncode == 0:
        return  # Behavioral pass — key function produces distinct per-account keys

    # Structural fallback: check guard call arguments
    # Structural: key function may use syntax node can't eval (TS types, etc.)
    code = _strip_comments(src)
    # Handler uses arrow function: return async (req, res) => { ... }
    handler_body = re.search(
        r"return\s+async\s+(?:function|\([^)]*\)\s*=>)[\s\S]*$", code
    )
    assert handler_body, "No handler body found"
    guard_call = re.search(
        r"(?:begin|guard|acquire)\w*(?:Pipeline|Request|Webhook)\w*(?:OrReject)?\s*\(", handler_body.group()
    )
    assert guard_call, "No guard call in handler"
    # Extract the argument block following the opening paren
    args = handler_body.group()[guard_call.end():guard_call.end() + 500]
    assert re.search(r"[Kk]ey.*account[Ii]d", args) or re.search(
        r"[Kk]ey.*\w+\(\s*account\b", args
    ), "In-flight key does not use accountId"
    if re.search(r"[Kk]ey.*remoteAddress", args):
        assert re.search(r"[Kk]ey.*accountId", args), (
            "In-flight key uses fragile remoteAddress as sole key"
        )


# ---------------------------------------------------------------------------
# Behavioral pass-to-pass (repo_tests) — upstream vitest
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_upstream_vitest_passes(vitest_behavioral):
    """Existing upstream webhook-handler tests pass via vitest."""
    if vitest_behavioral is None:
        pytest.skip("npm install failed — cannot run vitest")

    r = subprocess.run(
        ["npx", "vitest", "run",
         "extensions/synology-chat/src/webhook-handler.test.ts",
         "--reporter=verbose"],
        cwd=REPO, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Vitest failed:\n{(r.stdout + r.stderr)[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_core_tests():
    """synology-chat core tests pass via vitest (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "extensions/synology-chat/src/core.test.ts",
         "--reporter=verbose"],
        cwd=REPO, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Core tests failed:\n{(r.stdout + r.stderr)[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_client_tests():
    """synology-chat client tests pass via vitest (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "extensions/synology-chat/src/client.test.ts",
         "--reporter=verbose"],
        cwd=REPO, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Client tests failed:\n{(r.stdout + r.stderr)[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_channel_tests():
    """synology-chat channel tests pass via vitest (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "extensions/synology-chat/src/channel.test.ts",
         "--reporter=verbose"],
        cwd=REPO, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Channel tests failed:\n{(r.stdout + r.stderr)[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_approval_auth_tests():
    """synology-chat approval-auth tests pass via vitest (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "extensions/synology-chat/src/approval-auth.test.ts",
         "--reporter=verbose"],
        cwd=REPO, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Approval-auth tests failed:\n{(r.stdout + r.stderr)[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_oxlint():
    """oxlint passes on modified synology-chat files (pass_to_pass)."""
    # The repo .oxlintrc.json ignores extensions/; use a minimal config to lint them directly.
    minimal_cfg = Path("/tmp/_oxlint_ext.json")
    minimal_cfg.write_text('{}')
    r = subprocess.run(
        ["npx", "oxlint", "-c", str(minimal_cfg),
         "extensions/synology-chat/src/webhook-handler.ts",
         "extensions/synology-chat/src/test-http-utils.ts"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    minimal_cfg.unlink(missing_ok=True)
    assert r.returncode == 0, f"oxlint failed:\n{(r.stdout + r.stderr)[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_no_conflict_markers():
    """Repo has no Git conflict markers (pass_to_pass)."""
    r = subprocess.run(
        ["node", "scripts/check-no-conflict-markers.mjs"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Conflict markers check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_extension_boundary_relative_imports():
    """Extension relative imports stay within package boundaries (pass_to_pass)."""
    r = subprocess.run(
        ["node", "scripts/check-extension-plugin-sdk-boundary.mjs",
         "--mode=relative-outside-package"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Extension boundary check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_extension_no_src_outside_plugin_sdk():
    """Extensions don't import src outside plugin-sdk (pass_to_pass)."""
    r = subprocess.run(
        ["node", "scripts/check-extension-plugin-sdk-boundary.mjs",
         "--mode=src-outside-plugin-sdk"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Extension src boundary check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_extension_no_plugin_sdk_internal():
    """Extensions don't use plugin-sdk-internal imports (pass_to_pass)."""
    r = subprocess.run(
        ["node", "scripts/check-extension-plugin-sdk-boundary.mjs",
         "--mode=plugin-sdk-internal"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Plugin-sdk-internal check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_webhook_auth_body_order():
    """Webhook auth/body order check passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "scripts/check-webhook-auth-body-order.mjs"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Webhook auth body order check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_plugin_extension_import_boundary():
    """Plugin extension import boundary check passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "scripts/check-plugin-extension-import-boundary.mjs"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Plugin extension import boundary check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_no_extension_src_imports():
    """No extension src imports check passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--import", "tsx", "scripts/check-no-extension-src-imports.ts"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"No extension src imports check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_no_extension_test_core_imports():
    """No extension test core imports check passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--import", "tsx", "scripts/check-no-extension-test-core-imports.ts"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"No extension test core imports check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_no_monolithic_plugin_sdk_entry_imports():
    """No monolithic plugin-sdk entry imports check passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--import", "tsx", "scripts/check-no-monolithic-plugin-sdk-entry-imports.ts"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"No monolithic plugin-sdk entry imports check failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Structural fail-to-pass (pr_diff) — source inspection required
# ---------------------------------------------------------------------------

# Structural: code ordering cannot be tested by execution — the behavioral
# consequence (429 rejection) is verified by test_concurrent_requests_429
# [pr_diff] fail_to_pass
def test_guard_integrated_before_auth():
    """Pre-auth concurrency guard is called before auth with early-return on rejection."""
    code = _handler_code()

    # Scope to the handler function body (createWebhookHandler's returned function)
    handler_start = re.search(
        r"return\s+async\s+(?:function|\([^)]*\)\s*=>)", code
    )
    assert handler_start, "No handler function found"
    handler_code = code[handler_start.start():]

    guard = re.search(
        r"(?:begin|guard|acquire)\w*(?:Pipeline|Request|Webhook)\w*(?:OrReject)?\s*\(", handler_code
    )
    assert guard, "No guard/begin call found in handler"

    auth = re.search(r"parseAndAuthorize\w*\s*\(", handler_code)
    assert auth, "No auth call found in handler"

    assert guard.start() < auth.start(), "Guard must appear before auth call"

    between = handler_code[guard.start() : auth.start()]
    assert re.search(r"!\s*\w+\.ok\b|!\s*ok\b", between), (
        "No early-return check on !ok between guard and auth"
    )


# Structural: resource management patterns (try/finally) require source
# inspection — behavioral proof would need a broken variant without release
# [pr_diff] fail_to_pass
def test_guard_release_lifecycle():
    """Auth is wrapped in try/finally (or equivalent) that releases the guard."""
    code = _handler_code()

    guard = re.search(
        r"(?:begin|guard|acquire)\w*(?:Pipeline|Request|Webhook)\w*(?:OrReject)?\s*\(", code
    )
    assert guard, "No guard call found"
    after = code[guard.start() :]

    has_release = bool(
        re.search(
            r"try\s*\{[\s\S]*?(?:parseAndAuthorize|readBody|readRequest)"
            r"[\s\S]*?\}\s*finally\s*\{[\s\S]*?\.?release\s*\(",
            after,
        )
        or re.search(r"\.finally\s*\(\s*\(\)\s*=>\s*\w+\.release\s*\(", after)
        or re.search(r"using\s+\w+\s*=", code[: guard.start() + 500])
    )
    assert has_release, "Auth not wrapped with release mechanism (try/finally, .finally, or using)"


# ---------------------------------------------------------------------------
# Structural fail-to-pass (agent_config) — import boundaries
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:16, extensions/AGENTS.md:27
# Structural: import paths are not observable at runtime from Python
def test_import_from_plugin_sdk():
    """New webhook-ingress imports use openclaw/plugin-sdk/* path, not core internals."""
    code = _handler_code()

    assert re.search(r"""from\s*['"]openclaw/plugin-sdk/webhook-ingress['"]""", code), (
        "webhook-ingress not imported from plugin-sdk path"
    )
    assert not re.search(r"""from\s*['"](?:src/plugin-sdk|plugin-sdk-internal)""", code), (
        "Direct import from core internals violates import boundaries"
    )


# [agent_config] pass_to_pass — AGENTS.md:144,147
# Structural: type annotations are compile-time only, not observable at runtime
def test_no_any_types():
    """No `any` type annotations in webhook-handler.ts."""
    code = _handler_code()
    any_matches = re.findall(r":\s*any\b", code)
    assert len(any_matches) == 0, f"Found {len(any_matches)} uses of `: any"


# [agent_config] pass_to_pass — AGENTS.md:158, extensions/AGENTS.md:31
# Structural: import paths are compile-time only
def test_no_relative_imports_outside_package():
    """No relative imports that escape the synology-chat extension package root."""
    code = _handler_code()
    # Relative imports reaching outside the package (e.g., ../../src/...)
    escaping = re.findall(r"""(?:from|import)\s*['"](\.\./\.\..*)['"]""", code)
    assert len(escaping) == 0, (
        f"Relative imports escape package root: {escaping}"
    )


# [agent_config] pass_to_pass — AGENTS.md:146-147
# Structural: suppression directives are compile-time/lint-time only
def test_no_ts_suppress():
    """No @ts-nocheck or inline lint suppressions in webhook-handler.ts."""
    raw = _read(HANDLER)
    assert not re.search(r"@ts-nocheck", raw), "Found @ts-nocheck in webhook-handler.ts"
    assert not re.search(r"@ts-ignore", raw), "Found @ts-ignore in webhook-handler.ts"
    assert not re.search(r"eslint-disable", raw), "Found eslint-disable in webhook-handler.ts"
    assert not re.search(r"oxlint-disable", raw), "Found oxlint-disable in webhook-handler.ts"


# [agent_config] pass_to_pass — AGENTS.md:157
# Structural: import paths are compile-time only
def test_no_sdk_self_import():
    """synology-chat extension does not import itself via openclaw/plugin-sdk/synology-chat."""
    code = _handler_code()
    assert not re.search(
        r"""from\s*['"]openclaw/plugin-sdk/synology-chat['"]""", code
    ), "webhook-handler.ts imports itself via openclaw/plugin-sdk/synology-chat (self-import)"


# [agent_config] pass_to_pass — AGENTS.md:152
# Structural: sentinel patterns are source-level
# Scoped to the handler body and new inflight-related functions, since the
# pre-existing RateLimiter class and URL parsing use ?? 0 / ?? "" legitimately.
def test_no_magic_sentinels():
    """No `?? 0`, `?? ""`, or `?? {}` sentinels in new/modified handler code."""
    code = _handler_code()
    # Scope to createWebhookHandler body only — pre-existing helpers like
    # parseRoute and parseSynologyPayload have legitimate ?? "" usage.
    handler_start = re.search(r"export\s+function\s+createWebhookHandler", code)
    assert handler_start, "createWebhookHandler not found"
    scoped = code[handler_start.start():]
    sentinels = re.findall(r'\?\?\s*(?:0\b|""|\'\'|\{\})', scoped)
    assert len(sentinels) == 0, (
        f"Found magic sentinel fallbacks in handler code: {sentinels}"
    )
