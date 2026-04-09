"""
Task: workerd-improve-containerclient-tests
Repo: cloudflare/workerd @ e5eaa43c16c57bab977e5b53f4e57ca4418d084d
PR:   6217

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/workerd"
TEST_JS = Path(REPO) / "src/workerd/server/tests/container-client/test.js"
README = Path(REPO) / "src/workerd/server/tests/container-client/README.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified JS files must parse without syntax errors."""
    r = subprocess.run(
        ["node", "--check", str(TEST_JS)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"test.js has syntax errors:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass — BEHAVIORAL: extracts + runs actual code from test.js
def test_ws_timeout_mechanism():
    """WebSocket promise rejects with timeout instead of hanging when no message arrives.

    Extracts the promise-creation code from testInterceptWebSocket, provides a
    mock WebSocket that never fires messages, and verifies the promise rejects
    (fix has timeout) rather than hanging forever (base has no timeout).
    """
    content = TEST_JS.read_text()

    # Find the testInterceptWebSocket method first, then locate markers within it
    ws_method = content.find("testInterceptWebSocket")
    assert ws_method != -1, "Could not find testInterceptWebSocket method in test.js"

    start_marker = "// Listen for response"
    end_marker = "// Send a test message"
    start = content.find(start_marker, ws_method)
    end = content.find(end_marker, max(start, 0))
    assert start != -1 and end != -1, (
        "Could not find promise creation section (between '// Listen for response' "
        "and '// Send a test message' comments) in testInterceptWebSocket"
    )

    block = content[start + len(start_marker) : end].strip()
    # Patch 5-second timeout down to 200ms for fast testing
    block = block.replace("5_000", "200").replace("5000", "200")

    script_content = (
        "// Mock WebSocket -- addEventListener is no-op, message never arrives\n"
        "const ws = {\n"
        "    accept() {},\n"
        "    send() {},\n"
        "    close() {},\n"
        "    addEventListener() {}\n"
        "};\n\n"
        + block
        + "\n\n"
        "// Detect promise variable: 'promise' (fix) or 'messagePromise' (base)\n"
        "const p = typeof promise !== 'undefined' ? promise\n"
        "        : typeof messagePromise !== 'undefined' ? messagePromise\n"
        "        : null;\n"
        "if (!p) { console.error('No promise variable found'); process.exit(1); }\n\n"
        "const HARD_LIMIT = 3000;\n"
        "const result = await Promise.race([\n"
        "    p.then(() => 'resolved').catch(e => 'rejected:' + e.message),\n"
        "    new Promise(r => setTimeout(() => r('hung'), HARD_LIMIT))\n"
        "]);\n\n"
        "if (result.startsWith('rejected:')) {\n"
        "    console.log('PASS');\n"
        "} else if (result === 'hung') {\n"
        "    console.error('FAIL: promise hangs -- no timeout mechanism');\n"
        "    process.exit(1);\n"
        "} else {\n"
        "    console.error('FAIL: promise resolved unexpectedly');\n"
        "    process.exit(1);\n"
        "}\n"
    )

    script = Path(REPO) / "_eval_ws_timeout.mjs"
    script.write_text(script_content)
    try:
        r = subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=15, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)
    assert r.returncode == 0, f"WebSocket timeout test failed:\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_retry_no_verbose_logging():
    """TCP port retry loop must not log verbose info on each retry attempt."""
    content = TEST_JS.read_text()
    assert "Retrying getTcpPort" not in content, (
        "Verbose console.info retry logging still present -- "
        "remove the per-retry console.info messages"
    )


# [pr_diff] fail_to_pass
def test_readme_safe_docker_cleanup():
    """README uses pipe-based docker cleanup that is safe when no containers match."""
    content = README.read_text()
    assert "docker rm -f $(" not in content, (
        "README uses $() subshell for docker cleanup -- errors when no containers exist. "
        "Use pipe: docker ps -aq ... | xargs -r docker rm -f"
    )


# [pr_diff] fail_to_pass
def test_readme_correct_target():
    """README uses correct Bazel target with :container-client@ suffix."""
    content = README.read_text()
    assert ":container-client@" in content, (
        "README should specify the full Bazel target with :container-client@ suffix"
    )
