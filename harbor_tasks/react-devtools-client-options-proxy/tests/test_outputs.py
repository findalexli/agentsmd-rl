"""
Task: react-devtools-client-options-proxy
Repo: react @ bd76b456c127222f59888953348d40cf8f03e3a0
PR:   35886

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"


def _yarn_install():
    """Install dependencies if not already present."""
    # Check if node_modules exists
    if not Path(f"{REPO}/node_modules").exists():
        r = subprocess.run(
            ["yarn", "install", "--frozen-lockfile"],
            cwd=REPO, capture_output=True, text=True, timeout=300,
        )
        if r.returncode != 0:
            raise RuntimeError(f"yarn install failed: {r.stderr[-500:]}")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified JS files must not have syntax errors (checked where possible)."""
    # preload.js is plain JS (no Flow) — node --check works
    r = subprocess.run(
        ["node", "--check", "packages/react-devtools/preload.js"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in preload.js:\n{r.stderr}"

    # Flow-typed files can't be node-checked, but verify non-empty
    for f in [
        "packages/react-devtools-core/src/backend.js",
        "packages/react-devtools-core/src/standalone.js",
    ]:
        content = Path(f"{REPO}/{f}").read_text()
        assert len(content) > 500, f"{f} appears truncated or empty"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo's own CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_eslint():
    """Repo's ESLint passes on all files (pass_to_pass)."""
    _yarn_install()
    r = subprocess.run(
        ["node", "./scripts/tasks/eslint.js"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_flow():
    """Repo's Flow typecheck passes for dom-node renderer (pass_to_pass)."""
    _yarn_install()
    r = subprocess.run(
        ["yarn", "flow", "dom-node"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"Flow check failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_backend_uri_includes_path():
    """connectToDevTools URI must append the path parameter."""
    # Use Node to read the actual source and verify + test the URI logic
    script = r"""
    const fs = require('fs');
    const src = fs.readFileSync('packages/react-devtools-core/src/backend.js', 'utf8');

    // 1) The URI construction line must reference a path-related variable
    const uriLine = src.match(/const uri = (.+);/);
    if (!uriLine) {
        console.error('NO_URI_LINE');
        process.exit(1);
    }
    if (!/[Pp]ath/.test(uriLine[1])) {
        console.error('URI_NO_PATH: ' + uriLine[1]);
        process.exit(1);
    }

    // 2) The path prefix logic must exist
    if (!src.includes("!path.startsWith('/')")) {
        console.error('NO_PREFIX_LOGIC');
        process.exit(1);
    }

    // 3) Test the prefix logic with varied inputs
    function buildUri(protocol, host, port, path) {
        const prefixedPath = path !== '' && !path.startsWith('/') ? '/' + path : path;
        return protocol + '://' + host + ':' + port + prefixedPath;
    }

    const results = {
        with_slash: buildUri('ws', 'localhost', 8097, '/__devtools__/'),
        without_slash: buildUri('ws', 'myhost', 9000, 'devtools'),
        empty: buildUri('wss', 'secure.host', 443, ''),
        nested: buildUri('ws', 'example.com', 8080, '/deep/path/ws'),
    };
    console.log(JSON.stringify(results));
    """
    r = subprocess.run(
        ["node", "-e", script], cwd=REPO,
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Script failed: {r.stderr.strip()}"
    results = json.loads(r.stdout.strip())
    assert results["with_slash"] == "ws://localhost:8097/__devtools__/"
    assert results["without_slash"] == "ws://myhost:9000/devtools"
    assert results["empty"] == "wss://secure.host:443"
    assert results["nested"] == "ws://example.com:8080/deep/path/ws"


# [pr_diff] fail_to_pass
def test_standalone_client_overrides_in_response():
    """startServer response template must use client override variables, not raw server values."""
    # Use Node to verify the response.end() template uses client override vars
    script = r"""
    const fs = require('fs');
    const src = fs.readFileSync('packages/react-devtools-core/src/standalone.js', 'utf8');

    // Find the response.end() block (the template served to connecting clients)
    const responseMatch = src.match(/response\.end\([\s\S]*?\n\s*\);/);
    if (!responseMatch) {
        console.error('NO_RESPONSE_END');
        process.exit(1);
    }
    const block = responseMatch[0];

    // The connectToDevTools call in the response must reference client-overridden values
    // On the base commit it uses raw 'port' and 'host'; after the fix it uses
    // clientPort/clientHost or clientOptions?.port etc.
    if (!block.includes('client') && !block.includes('Client')) {
        console.error('RESPONSE_NO_CLIENT_OVERRIDE: ' + block.substring(0, 200));
        process.exit(1);
    }

    // Verify the path is conditionally included in the response
    if (!block.includes('path')) {
        console.error('RESPONSE_NO_PATH');
        process.exit(1);
    }

    // Test the client override fallback logic with varied inputs
    function getClientValues(host, port, useHttps, clientOptions) {
        const clientHost = clientOptions?.host ?? host;
        const clientPort = clientOptions?.port ?? port;
        const clientUseHttps = clientOptions?.useHttps ?? useHttps;
        return { clientHost, clientPort, clientUseHttps };
    }

    const results = [
        getClientValues('localhost', 8097, false, { host: 'proxy.example.com', port: 443, useHttps: true }),
        getClientValues('localhost', 8097, false, {}),
        getClientValues('0.0.0.0', 3000, true, undefined),
        getClientValues('myhost', 9090, false, { port: 8443 }),
    ];
    console.log(JSON.stringify(results));
    """
    r = subprocess.run(
        ["node", "-e", script], cwd=REPO,
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Script failed: {r.stderr.strip()}"
    results = json.loads(r.stdout.strip())

    # Full override
    assert results[0]["clientHost"] == "proxy.example.com"
    assert results[0]["clientPort"] == 443
    assert results[0]["clientUseHttps"] is True

    # Empty override -> falls back to server values
    assert results[1]["clientHost"] == "localhost"
    assert results[1]["clientPort"] == 8097

    # Undefined clientOptions -> falls back to server values
    assert results[2]["clientHost"] == "0.0.0.0"
    assert results[2]["clientUseHttps"] is True

    # Partial override
    assert results[3]["clientPort"] == 8443
    assert results[3]["clientHost"] == "myhost"


# [pr_diff] fail_to_pass
def test_standalone_retry_passes_all_params():
    """Error retry handlers in startServer must forward all parameters, not just port."""
    src = Path(f"{REPO}/packages/react-devtools-core/src/standalone.js").read_text()

    # Find all setTimeout retry calls that invoke startServer
    # On the base commit: setTimeout(() => startServer(port), 1000)  -- 1 arg
    # After fix: setTimeout(() => startServer(port, host, ..., clientOptions), 1000)  -- 6 args
    retry_blocks = re.findall(
        r"setTimeout\([^;]*?startServer\(([^)]*)\)", src, re.DOTALL
    )
    assert len(retry_blocks) >= 2, (
        f"Expected >= 2 retry handlers calling startServer, found {len(retry_blocks)}"
    )

    for i, args_str in enumerate(retry_blocks):
        args = [a.strip() for a in args_str.split(",") if a.strip()]
        assert len(args) >= 4, (
            f"Retry handler {i} only passes {len(args)} arg(s) to startServer, "
            f"expected >= 4 (must forward host, httpsOptions, etc.): {args_str[:80]}"
        )


# [pr_diff] fail_to_pass
def test_preload_returns_client_fields():
    """preload.js readEnv() must return path, clientHost, clientPort, clientUseHttps."""
    src = Path(f"{REPO}/packages/react-devtools/preload.js").read_text()

    # Find the return statement object in readEnv
    return_match = re.search(r"return\s*\{([^}]+)\}", src, re.DOTALL)
    assert return_match, "No return statement with object literal found in preload.js"

    return_body = return_match.group(1)
    required_fields = ["path", "clientHost", "clientPort", "clientUseHttps"]
    for field in required_fields:
        assert field in return_body, (
            f"Field '{field}' missing from readEnv() return object"
        )

    # Also verify the env vars are actually read
    env_vars = [
        "REACT_DEVTOOLS_PATH",
        "REACT_DEVTOOLS_CLIENT_HOST",
        "REACT_DEVTOOLS_CLIENT_PORT",
        "REACT_DEVTOOLS_CLIENT_USE_HTTPS",
    ]
    for var in env_vars:
        assert var in src, f"Environment variable '{var}' not read in preload.js"


# [pr_diff] fail_to_pass
def test_app_passes_client_options():
    """app.html must destructure client fields from readEnv and pass clientOptions to startServer."""
    src = Path(f"{REPO}/packages/react-devtools/app.html").read_text()

    # Verify readEnv destructuring includes client fields
    destructure_match = re.search(r"const\s*\{([^}]+)\}\s*=\s*readEnv\(\)", src)
    assert destructure_match, "No readEnv() destructuring found in app.html"
    destructured = destructure_match.group(1)
    for field in ["clientHost", "clientPort", "clientUseHttps", "path"]:
        assert field in destructured, (
            f"'{field}' not destructured from readEnv() in app.html"
        )

    # Verify startServer call passes client options (not just port, host, options)
    start_match = re.search(r"\.startServer\(([^;]+)\)", src, re.DOTALL)
    assert start_match, "No .startServer() call found in app.html"
    call_args = start_match.group(1)
    assert "clientHost" in call_args or "client" in call_args.lower(), (
        f"startServer call doesn't include client options: {call_args[:120]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Key modified functions must have real logic, not stubs."""
    # Verify backend.js connectToDevTools has URI construction with path
    backend_src = Path(
        f"{REPO}/packages/react-devtools-core/src/backend.js"
    ).read_text()
    assert "const uri = " in backend_src, "connectToDevTools missing URI construction"

    # Verify standalone.js startServer has response.end with template string
    standalone_src = Path(
        f"{REPO}/packages/react-devtools-core/src/standalone.js"
    ).read_text()
    assert "response.end(" in standalone_src, "startServer missing response.end"
    assert "connectToDevTools" in standalone_src, (
        "startServer response doesn't include connectToDevTools"
    )

    # Verify preload.js has readEnv with return object
    preload_src = Path(f"{REPO}/packages/react-devtools/preload.js").read_text()
    assert "readEnv" in preload_src, "preload.js missing readEnv function"
    assert "return {" in preload_src or "return{" in preload_src, (
        "readEnv missing return object"
    )
