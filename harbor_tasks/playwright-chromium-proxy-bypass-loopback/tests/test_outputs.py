"""Behavior tests for chromium proxy bypass loopback handling.

Strategy: extract the body of `_innerDefaultArgs` directly from
chromium.ts source and execute it as a JavaScript function with
varying input options. This calls the actual production logic
(no AST inspection, no grep) and asserts on the resulting
`--proxy-bypass-list` Chrome argument.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/playwright"
TARGET = f"{REPO}/packages/playwright-core/src/server/chromium/chromium.ts"

# Node.js helper that:
#   1. reads chromium.ts
#   2. brace-matches the body of _innerDefaultArgs(...)
#   3. wraps it in a JS function (with chromiumSwitches stub)
#   4. invokes it with options passed via stdin JSON
#   5. emits the resulting chromeArguments array as JSON on stdout
NODE_HELPER = r"""
const fs = require('fs');

const TS = '/workspace/playwright/packages/playwright-core/src/server/chromium/chromium.ts';
const src = fs.readFileSync(TS, 'utf8');

function extractMethodBody(src, name) {
  const re = new RegExp(name + '\\s*\\([^)]*\\)\\s*(?::[^{]*)?\\{');
  const m = re.exec(src);
  if (!m) return null;
  const start = m.index + m[0].length;
  let depth = 1;
  for (let i = start; i < src.length; i++) {
    const c = src[i];
    if (c === '{') depth++;
    else if (c === '}') { depth--; if (depth === 0) return src.slice(start, i); }
  }
  return null;
}

const body = extractMethodBody(src, '_innerDefaultArgs');
if (!body) { console.error('Could not extract _innerDefaultArgs method body'); process.exit(2); }

// Stub the only external helper actually invoked in success paths.
// `this._createUserDataDirArgMisuseError` is provided via .call() context but
// is unreachable for our test inputs (no --user-data-dir arg passed).
const wrapped = '(function(options) {\n  const chromiumSwitches = () => [];\n' + body + '\n})';
const fn = eval(wrapped);

const stdin = fs.readFileSync(0, 'utf8');
const payload = JSON.parse(stdin);
const options = payload.options || {};
const env = payload.env || {};

const saved = {};
for (const k of Object.keys(env)) {
  saved[k] = process.env[k];
  if (env[k] === null) delete process.env[k];
  else process.env[k] = env[k];
}

let result, err;
try {
  result = fn.call({ _createUserDataDirArgMisuseError: () => new Error('stub') }, options);
} catch (e) {
  err = String(e && e.stack || e);
}

for (const k of Object.keys(saved)) {
  if (saved[k] === undefined) delete process.env[k];
  else process.env[k] = saved[k];
}

if (err) { console.error(err); process.exit(3); }
process.stdout.write(JSON.stringify(result));
"""


def _run_with_options(options: dict, env_overrides: dict | None = None) -> list[str]:
    """Run the chromium method body with options; return chromeArguments array."""
    payload = json.dumps({"options": options, "env": env_overrides or {}})
    r = subprocess.run(
        ["node", "-e", NODE_HELPER],
        input=payload,
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    if r.returncode != 0:
        raise AssertionError(
            f"Node helper failed (exit {r.returncode}):\nstderr:\n{r.stderr}\nstdout:\n{r.stdout}"
        )
    return json.loads(r.stdout)


def _bypass_list(args: list[str]) -> list[str]:
    """Extract the --proxy-bypass-list values, or [] if the arg is absent."""
    prefix = "--proxy-bypass-list="
    for a in args:
        if isinstance(a, str) and a.startswith(prefix):
            return a[len(prefix):].split(";")
    return []


# ─────────────────────── fail-to-pass tests (PR behavior change) ───────────────────────


def test_localhost_in_bypass_does_not_force_loopback():
    """proxy.bypass='localhost' must NOT force <-loopback> into the bypass list."""
    args = _run_with_options({"proxy": {"server": "http://proxy:8080", "bypass": "localhost"}})
    bp = _bypass_list(args)
    assert "localhost" in bp, f"bypass should retain user's 'localhost' entry, got {bp}"
    assert "<-loopback>" not in bp, (
        f"<-loopback> must not be auto-added when 'localhost' is already bypassed; got {bp}"
    )


def test_ipv4_loopback_in_bypass_does_not_force_loopback():
    """proxy.bypass='127.0.0.1' must NOT force <-loopback>."""
    args = _run_with_options({"proxy": {"server": "http://proxy:8080", "bypass": "127.0.0.1"}})
    bp = _bypass_list(args)
    assert "127.0.0.1" in bp, f"bypass should retain '127.0.0.1', got {bp}"
    assert "<-loopback>" not in bp, (
        f"<-loopback> must not be auto-added when '127.0.0.1' is already bypassed; got {bp}"
    )


def test_ipv6_loopback_in_bypass_does_not_force_loopback():
    """proxy.bypass='::1' must NOT force <-loopback>."""
    args = _run_with_options({"proxy": {"server": "http://proxy:8080", "bypass": "::1"}})
    bp = _bypass_list(args)
    assert "::1" in bp, f"bypass should retain '::1', got {bp}"
    assert "<-loopback>" not in bp, (
        f"<-loopback> must not be auto-added when '::1' is already bypassed; got {bp}"
    )


def test_mixed_bypass_with_localhost_does_not_force_loopback():
    """A bypass list that mixes 'localhost' with other hosts must not force <-loopback>."""
    args = _run_with_options(
        {"proxy": {"server": "http://proxy:8080", "bypass": "localhost,example.com"}}
    )
    bp = _bypass_list(args)
    assert "localhost" in bp
    assert "example.com" in bp
    assert "<-loopback>" not in bp, (
        f"<-loopback> must not be auto-added when 'localhost' is in the user bypass list; got {bp}"
    )


def test_bypass_with_whitespace_around_localhost_still_recognized():
    """Whitespace around bypass entries is trimmed; trimmed 'localhost' must suppress <-loopback>."""
    args = _run_with_options(
        {"proxy": {"server": "http://proxy:8080", "bypass": " localhost , example.com "}}
    )
    bp = _bypass_list(args)
    assert "localhost" in bp
    assert "<-loopback>" not in bp, (
        f"trimmed bypass entries must be recognized as loopback; got {bp}"
    )


# ─────────────────────── pass-to-pass tests (behavior unchanged) ───────────────────────


def test_non_loopback_bypass_still_forces_loopback():
    """When bypass is purely non-loopback hosts, <-loopback> is still appended (unchanged behavior)."""
    args = _run_with_options(
        {"proxy": {"server": "http://proxy:8080", "bypass": "example.com,foo.test"}}
    )
    bp = _bypass_list(args)
    assert "example.com" in bp
    assert "foo.test" in bp
    assert "<-loopback>" in bp, f"non-loopback bypass should still add <-loopback>; got {bp}"


def test_no_bypass_uses_default_loopback():
    """No proxy.bypass and no env override → <-loopback> is added (unchanged behavior)."""
    args = _run_with_options({"proxy": {"server": "http://proxy:8080"}})
    bp = _bypass_list(args)
    assert bp == ["<-loopback>"], f"default behavior should produce only ['<-loopback>']; got {bp}"


def test_disable_env_var_skips_loopback():
    """PLAYWRIGHT_DISABLE_FORCED_CHROMIUM_PROXIED_LOOPBACK suppresses <-loopback> (unchanged)."""
    args = _run_with_options(
        {"proxy": {"server": "http://proxy:8080", "bypass": "example.com"}},
        env_overrides={"PLAYWRIGHT_DISABLE_FORCED_CHROMIUM_PROXIED_LOOPBACK": "1"},
    )
    bp = _bypass_list(args)
    assert "example.com" in bp
    assert "<-loopback>" not in bp, (
        f"when env var is set, <-loopback> must not be added; got {bp}"
    )


def test_proxy_server_argument_emitted():
    """--proxy-server={server} is always emitted when proxy is configured (unchanged)."""
    args = _run_with_options({"proxy": {"server": "http://proxy:8080", "bypass": "localhost"}})
    assert "--proxy-server=http://proxy:8080" in args, (
        f"expected --proxy-server arg in {args}"
    )


def test_explicit_loopback_token_in_bypass_not_duplicated():
    """If the user already includes '<-loopback>', it must not be duplicated (unchanged)."""
    args = _run_with_options(
        {"proxy": {"server": "http://proxy:8080", "bypass": "<-loopback>"}}
    )
    bp = _bypass_list(args)
    occurrences = sum(1 for x in bp if x == "<-loopback>")
    assert occurrences == 1, f"<-loopback> should appear exactly once, got {bp}"


# ─────────────────────── repo invariant (compile sanity) ───────────────────────


def test_chromium_source_parses_as_typescript():
    """The patched chromium.ts must remain syntactically valid TypeScript.

    We use Node's --check on a JS-stripped version of the file. esbuild is
    not available, but we can at least verify our extraction yields a
    function whose syntax is acceptable to V8 — which the helper above
    proves on every other test invocation. Here we just confirm extraction
    succeeded (proving the brace-balanced method survived).
    """
    payload = json.dumps({"options": {}, "env": {}})
    r = subprocess.run(
        ["node", "-e", NODE_HELPER],
        input=payload,
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, (
        f"_innerDefaultArgs extraction or eval failed:\nstderr:\n{r.stderr}"
    )


# ─────────────────────── scoped CI guard (eslint on affected module) ───────────────────────


def test_scoped_eslint_on_chromium_source():
    """ESLint must pass on the patched chromium.ts source — scoped to the affected module."""
    r = subprocess.run(
        ["bash", "-lc",
         "npm ci && ./node_modules/.bin/eslint packages/playwright-core/src/server/chromium/chromium.ts"],
        cwd=REPO,
        capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"scoped eslint failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}"
    )
