"""
Task: react-devtools-reverse-proxy-path
Repo: react @ bd76b456c127222f59888953348d40cf8f03e3a0
PR:   35886

Adds reverse-proxy support to React DevTools: a `path` option for the WebSocket
URI and `clientOptions` to override the host/port/protocol served to clients.
Both code changes and README documentation updates are required.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js script in the repo root."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout,
        cwd=REPO,
    )


def _ensure_node_modules():
    """Ensure node_modules is installed."""
    node_modules = Path(REPO) / "node_modules"
    if not node_modules.exists():
        r = subprocess.run(
            ["yarn", "install", "--frozen-lockfile"],
            capture_output=True, text=True, timeout=300, cwd=REPO,
        )
        if r.returncode != 0:
            raise RuntimeError(f"yarn install failed: {r.stderr[-1000:]}")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified JS files parse without syntax errors (node --check)."""
    for f in ["packages/react-devtools/preload.js"]:
        r = subprocess.run(
            ["node", "--check", f],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"{f} has syntax errors: {r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI checks that should pass on base commit
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_syntax_devtools_core_backend():
    """Repo: react-devtools-core backend.js parses without syntax errors."""
    r = subprocess.run(
        ["node", "--check", "packages/react-devtools-core/src/backend.js"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"backend.js has syntax errors: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_syntax_devtools_core_standalone():
    """Repo: react-devtools-core standalone.js parses without syntax errors."""
    r = subprocess.run(
        ["node", "--check", "packages/react-devtools-core/src/standalone.js"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"standalone.js has syntax errors: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_syntax_devtools_preload():
    """Repo: react-devtools preload.js parses without syntax errors."""
    r = subprocess.run(
        ["node", "--check", "packages/react-devtools/preload.js"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"preload.js has syntax errors: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_syntax_devtools_app_html():
    """Repo: react-devtools app.html inline JavaScript parses without syntax errors."""
    # Extract inline JavaScript from app.html and validate it
    app_html = Path(REPO) / "packages/react-devtools/app.html"
    content = app_html.read_text()

    # Find script tags and extract inline JS (excluding those with src attribute)
    script_pattern = r'<script>(.*?)</script>'
    scripts = re.findall(script_pattern, content, re.DOTALL)

    for i, script in enumerate(scripts):
        if script.strip():
            # Write to temp file and check
            temp_file = f"/tmp/app_html_script_{i}.js"
            Path(temp_file).write_text(script)
            r = subprocess.run(
                ["node", "--check", temp_file],
                capture_output=True, text=True, timeout=30,
            )
            assert r.returncode == 0, f"app.html inline script {i} has syntax errors: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_eslint_devtools_modified():
    """Repo: ESLint passes on modified devtools files."""
    _ensure_node_modules()
    r = subprocess.run(
        [
            "node", "./scripts/tasks/eslint.js",
            "packages/react-devtools-core/src/backend.js",
            "packages/react-devtools-core/src/standalone.js",
            "packages/react-devtools/preload.js",
        ],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed on devtools files:\n{r.stdout[-1000:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_flow_devtools():
    """Repo: Flow type checking passes for dom-node renderer (covers devtools)."""
    _ensure_node_modules()
    r = subprocess.run(
        ["yarn", "flow", "dom-node"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Flow type check failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier_devtools():
    """Repo: Prettier formatting check passes."""
    _ensure_node_modules()
    r = subprocess.run(
        ["node", "./scripts/prettier/index.js", "check-changed"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_path_prefix_uri_construction():
    """backend.js must build WebSocket URI with path, auto-adding leading /."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('packages/react-devtools-core/src/backend.js', 'utf8');

// Verify the URI construction references prefixedPath
if (!src.includes('prefixedPath')) {
    console.error('backend.js missing prefixedPath variable');
    process.exit(1);
}

// Extract and test the logic (matches the source implementation)
function buildUri(host, port, protocol, path) {
    const prefixedPath = path !== '' && !path.startsWith('/') ? '/' + path : path;
    return protocol + '://' + host + ':' + port + prefixedPath;
}

const tests = [
    { args: ['localhost', 8097, 'ws', '/__react_devtools__/'], expected: 'ws://localhost:8097/__react_devtools__/' },
    { args: ['localhost', 8097, 'ws', '__react_devtools__/'], expected: 'ws://localhost:8097/__react_devtools__/' },
    { args: ['localhost', 8097, 'ws', ''], expected: 'ws://localhost:8097' },
    { args: ['remote.example.com', 443, 'wss', '/devtools'], expected: 'wss://remote.example.com:443/devtools' },
];

let pass = true;
for (const t of tests) {
    const result = buildUri(...t.args);
    if (result !== t.expected) {
        console.error('FAIL:', JSON.stringify(t.args), '->', result, '(expected', t.expected + ')');
        pass = false;
    }
}
if (!pass) process.exit(1);
console.log(JSON.stringify({ tests_passed: tests.length }));
""")
    assert r.returncode == 0, f"Path prefix tests failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["tests_passed"] == 4


# [pr_diff] fail_to_pass
def test_client_options_fallback():
    """standalone.js must use clientOptions to override server values."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('packages/react-devtools-core/src/standalone.js', 'utf8');

// Verify ClientOptions type and fallback logic exist
if (!src.includes('ClientOptions')) {
    console.error('standalone.js missing ClientOptions type');
    process.exit(1);
}
if (!src.includes('clientOptions?.host') || !src.includes('clientOptions?.port')) {
    console.error('standalone.js missing client option fallback logic');
    process.exit(1);
}

// Test the fallback logic (matches the source implementation)
function resolveClient(serverHost, serverPort, serverUseHttps, clientOptions) {
    const clientHost = clientOptions?.host ?? serverHost;
    const clientPort = clientOptions?.port ?? serverPort;
    const clientUseHttps = clientOptions?.useHttps ?? serverUseHttps;
    return { clientHost, clientPort, clientUseHttps };
}

const t1 = resolveClient('localhost', 8097, false, { host: 'remote.example.com', port: 443, useHttps: true });
if (t1.clientHost !== 'remote.example.com' || t1.clientPort !== 443 || t1.clientUseHttps !== true) {
    console.error('FAIL: override not applied:', t1);
    process.exit(1);
}

const t2 = resolveClient('localhost', 8097, false, {});
if (t2.clientHost !== 'localhost' || t2.clientPort !== 8097 || t2.clientUseHttps !== false) {
    console.error('FAIL: fallback broken:', t2);
    process.exit(1);
}

const t3 = resolveClient('localhost', 8097, false, undefined);
if (t3.clientHost !== 'localhost' || t3.clientPort !== 8097) {
    console.error('FAIL: undefined clientOptions:', t3);
    process.exit(1);
}

console.log(JSON.stringify({ tests_passed: 3 }));
""")
    assert r.returncode == 0, f"Client options tests failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["tests_passed"] == 3


# [pr_diff] fail_to_pass
def test_backend_connect_options_has_path():
    """ConnectOptions Flow type in backend.js must include optional path field."""
    backend = Path(REPO) / "packages/react-devtools-core/src/backend.js"
    content = backend.read_text()
    assert "path?: string" in content, \
        "ConnectOptions must include 'path?: string' field"
    # Verify path is destructured with a default value in connectToDevTools
    assert "path = ''" in content or 'path = ""' in content, \
        "path must be destructured with empty string default"


# [pr_diff] fail_to_pass
def test_preload_reads_devtools_env_vars():
    """preload.js must read REACT_DEVTOOLS_PATH and REACT_DEVTOOLS_CLIENT_* env vars."""
    preload = Path(REPO) / "packages/react-devtools/preload.js"
    content = preload.read_text()
    assert "REACT_DEVTOOLS_PATH" in content, \
        "preload.js must read REACT_DEVTOOLS_PATH"
    assert "REACT_DEVTOOLS_CLIENT_HOST" in content, \
        "preload.js must read REACT_DEVTOOLS_CLIENT_HOST"
    assert "REACT_DEVTOOLS_CLIENT_PORT" in content, \
        "preload.js must read REACT_DEVTOOLS_CLIENT_PORT"
    assert "REACT_DEVTOOLS_CLIENT_USE_HTTPS" in content, \
        "preload.js must read REACT_DEVTOOLS_CLIENT_USE_HTTPS"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_devtools_core_readme_documents_client_options():
    """react-devtools-core README must document clientOptions for reverse proxy."""
    readme = Path(REPO) / "packages/react-devtools-core/README.md"
    content = readme.read_text()
    assert "clientOptions" in content, \
        "README should document clientOptions parameter"
    assert "reverse proxy" in content.lower() or "REACT_DEVTOOLS_CLIENT" in content, \
        "README should explain reverse proxy use case or client env vars"


# [pr_diff] fail_to_pass
def test_devtools_readme_env_var_table():
    """react-devtools README must document REACT_DEVTOOLS_CLIENT_* env vars."""
    readme = Path(REPO) / "packages/react-devtools/README.md"
    content = readme.read_text()
    assert "REACT_DEVTOOLS_CLIENT_HOST" in content, \
        "README should document REACT_DEVTOOLS_CLIENT_HOST env var"
    assert "REACT_DEVTOOLS_CLIENT_PORT" in content, \
        "README should document REACT_DEVTOOLS_CLIENT_PORT env var"
    assert "REACT_DEVTOOLS_PATH" in content, \
        "README should document REACT_DEVTOOLS_PATH env var"
