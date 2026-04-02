"""
Task: react-devtools-client-options
Repo: facebook/react @ bd76b456c127222f59888953348d40cf8f03e3a0
PR:   (adds path support and ClientOptions to react-devtools-core)

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"
BACKEND = f"{REPO}/packages/react-devtools-core/src/backend.js"
STANDALONE = f"{REPO}/packages/react-devtools-core/src/standalone.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """backend.js and standalone.js must parse without syntax errors."""
    for filepath in [BACKEND, STANDALONE]:
        r = subprocess.run(
            ["node", "--check", filepath],
            capture_output=True, text=True, timeout=15,
        )
        assert r.returncode == 0, (
            f"Syntax error in {filepath}:\n{r.stderr}"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral and structural tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_path_prefix_logic():
    """prefixedPath adds leading slash to bare paths, leaves slashed/empty paths unchanged.

    Extracts the actual prefixedPath expression from backend.js and evaluates
    it with multiple inputs via node. This tests behavior, not just presence.
    """
    # AST-only extraction here because the full connectToDevTools() opens WebSockets
    # and cannot be called without a running DevTools server.
    src = Path(BACKEND).read_text()
    match = re.search(r'const prefixedPath\s*=\s*[^\n]+', src)
    assert match, "prefixedPath computation not found in backend.js"
    prefixed_path_line = match.group(0)

    test_cases = [
        # (input path, expected prefixedPath)
        ("devtools",   "/devtools"),    # bare path → add slash
        ("/devtools",  "/devtools"),    # already has slash → unchanged
        ("a/b/c",      "/a/b/c"),       # nested bare path → add slash
        ("",           ""),             # empty → no suffix
    ]

    for path_val, expected in test_cases:
        script = f"""
const path = {json.dumps(path_val)};
{prefixed_path_line}
process.stdout.write(prefixedPath);
"""
        r = subprocess.run(
            ["node", "-e", script],
            capture_output=True, text=True, timeout=10,
        )
        assert r.returncode == 0, (
            f"Node eval failed for path={path_val!r}: {r.stderr}"
        )
        assert r.stdout == expected, (
            f"path={path_val!r}: expected prefixedPath={expected!r}, got {r.stdout!r}"
        )


# [pr_diff] fail_to_pass
def test_path_appended_to_websocket_uri():
    """WebSocket URI construction includes prefixedPath, not just host:port.

    # AST-only because: connectToDevTools() opens a live WebSocket; the URI
    # construction line is pure string concatenation that can be eval'd safely.
    """
    src = Path(BACKEND).read_text()
    # After the fix the uri line must reference prefixedPath
    match = re.search(r'const uri\s*=\s*[^\n]+', src)
    assert match, "URI construction not found in backend.js"
    uri_line = match.group(0)
    assert "prefixedPath" in uri_line, (
        f"URI construction does not include prefixedPath:\n  {uri_line}"
    )

    # Eval the URI line with concrete values to verify behavioral correctness
    test_cases = [
        ("localhost", 8097, False, "devtools",  "ws://localhost:8097/devtools"),
        ("localhost", 8097, True,  "/secure",   "wss://localhost:8097/secure"),
        ("myhost",    9000, False, "",           "ws://myhost:9000"),
    ]
    for host, port, use_https, path_val, expected_uri in test_cases:
        script = f"""
const host = {json.dumps(host)};
const port = {port};
const useHttps = {"true" if use_https else "false"};
const path = {json.dumps(path_val)};
const protocol = useHttps ? 'wss' : 'ws';
const prefixedPath = path !== '' && !path.startsWith('/') ? '/' + path : path;
{uri_line}
process.stdout.write(uri);
"""
        r = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=10)
        assert r.returncode == 0, f"Node eval failed: {r.stderr}"
        assert r.stdout == expected_uri, (
            f"host={host} port={port} https={use_https} path={path_val!r}: "
            f"expected {expected_uri!r}, got {r.stdout!r}"
        )


# [pr_diff] fail_to_pass
def test_connect_options_has_path_field():
    """ConnectOptions Flow type includes path?: string field.

    # AST-only because: Flow type annotations are stripped at runtime;
    # they cannot be tested by importing or calling the module.
    """
    src = Path(BACKEND).read_text()
    # Find the ConnectOptions type block
    match = re.search(r'type ConnectOptions\s*=\s*\{([^}]+)\}', src, re.DOTALL)
    assert match, "ConnectOptions type not found in backend.js"
    type_body = match.group(1)
    assert "path?" in type_body or "path " in type_body, (
        f"path field not in ConnectOptions:\n{type_body}"
    )


# [pr_diff] fail_to_pass
def test_client_options_type_defined():
    """ClientOptions Flow type is defined in standalone.js with host, port, useHttps fields.

    # AST-only because: Flow type declarations have no runtime representation.
    """
    src = Path(STANDALONE).read_text()
    match = re.search(r'type ClientOptions\s*=\s*\{([^}]+)\}', src, re.DOTALL)
    assert match, "ClientOptions type not found in standalone.js"
    type_body = match.group(1)
    assert "host?" in type_body or "host " in type_body, "ClientOptions missing host field"
    assert "port?" in type_body or "port " in type_body, "ClientOptions missing port field"
    assert "useHttps?" in type_body or "useHttps " in type_body, "ClientOptions missing useHttps field"


# [pr_diff] fail_to_pass
def test_startserver_has_path_and_client_options():
    """startServer function signature includes path and clientOptions parameters.

    # AST-only because: startServer() starts a live WebSocket+HTTP server;
    # it cannot be invoked safely in the test environment.
    """
    src = Path(STANDALONE).read_text()
    match = re.search(r'function startServer\s*\(([^)]+)\)', src, re.DOTALL)
    assert match, "startServer function not found in standalone.js"
    sig = match.group(1)
    assert "path" in sig, f"startServer missing 'path' parameter. Signature:\n{sig}"
    assert "clientOptions" in sig, (
        f"startServer missing 'clientOptions' parameter. Signature:\n{sig}"
    )


# [pr_diff] fail_to_pass
def test_server_restart_forwards_path_and_client_options():
    """Both server.on('error') and httpServer.on('error') restart callbacks pass path and clientOptions.

    Without this fix, a server restart after an error would lose path/clientOptions,
    silently reverting the proxy configuration.

    # AST-only because: triggering server errors requires binding to a port
    # and forcing an error condition, which is not feasible in the test environment.
    """
    src = Path(STANDALONE).read_text()

    # Find all startServer( call sites inside error handlers
    # There should be at least 2 (server.on('error') and httpServer.on('error'))
    # Each must include path and clientOptions
    restart_calls = re.findall(
        r'startServer\s*\(([^;]+?)\)',
        src,
        re.DOTALL,
    )
    # Filter to calls that look like restarts (have multiple arguments)
    restart_calls = [c for c in restart_calls if ',' in c]

    assert len(restart_calls) >= 2, (
        f"Expected at least 2 startServer restart calls, found {len(restart_calls)}"
    )

    for call_args in restart_calls:
        assert "path" in call_args, (
            f"startServer restart call missing 'path':\nstartServer({call_args})"
        )
        assert "clientOptions" in call_args, (
            f"startServer restart call missing 'clientOptions':\nstartServer({call_args})"
        )


# [pr_diff] fail_to_pass
def test_response_uses_client_override_variables():
    """HTTP response uses clientHost/clientPort/clientUseHttps overrides, not bare server vars.

    When a reverse proxy fronts the server, the client script must connect to
    the proxy's address, not the internal server address.

    # AST-only because: triggering the HTTP request handler requires a running
    # HTTP server and an actual incoming connection.
    """
    src = Path(STANDALONE).read_text()

    # Client override variables must be defined via nullish coalescing
    assert "clientOptions?.host ?? host" in src, (
        "clientHost fallback (clientOptions?.host ?? host) not found in standalone.js"
    )
    assert "clientOptions?.port ?? port" in src, (
        "clientPort fallback (clientOptions?.port ?? port) not found in standalone.js"
    )
    assert "clientOptions?.useHttps ?? useHttps" in src, (
        "clientUseHttps fallback (clientOptions?.useHttps ?? useHttps) not found in standalone.js"
    )

    # The served script template literal must use client vars, not server vars
    # Find the response.end( block
    response_match = re.search(
        r'response\.end\s*\((.+?)(?=\n\s*\}\);|\n\s*\n)',
        src,
        re.DOTALL,
    )
    assert response_match, "response.end( block not found in standalone.js"
    response_block = response_match.group(1)
    assert "clientPort" in response_block or "clientHost" in response_block, (
        "response.end does not reference client override variables"
    )
