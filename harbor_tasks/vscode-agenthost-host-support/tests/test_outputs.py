"""
Task: vscode-agenthost-host-support
Repo: microsoft/vscode @ 0930f054ee7006081f7eecdd11c3a55fa940e604

Fix: Add --host CLI option to agent host server, create serverUrls.ts
utility, and update startup to show local/network URLs.

All checks must pass for reward = 1. Any failure = reward 0.
"""

from pathlib import Path

REPO = "/workspace/vscode"


def test_server_urls_file_exists():
    """serverUrls.ts utility file should be created."""
    assert Path(f"{REPO}/src/vs/platform/agentHost/node/serverUrls.ts").exists(), \
        "serverUrls.ts should exist"


def test_server_urls_test_file_exists():
    """serverUrls.test.ts test file should be created."""
    assert Path(f"{REPO}/src/vs/platform/agentHost/test/node/serverUrls.test.ts").exists(), \
        "serverUrls.test.ts should exist"


def test_resolve_server_urls_exported():
    """resolveServerUrls function should be exported from serverUrls.ts."""
    src = Path(f"{REPO}/src/vs/platform/agentHost/node/serverUrls.ts").read_text()
    assert "export function resolveServerUrls" in src, \
        "resolveServerUrls should be exported"


def test_format_websocket_url_exported():
    """formatWebSocketUrl function should be exported."""
    src = Path(f"{REPO}/src/vs/platform/agentHost/node/serverUrls.ts").read_text()
    assert "export function formatWebSocketUrl" in src, \
        "formatWebSocketUrl should be exported"


def test_host_option_in_cli_script():
    """code-agent-host.js should accept --host CLI argument."""
    src = Path(f"{REPO}/scripts/code-agent-host.js").read_text()
    assert "'host'" in src or '"host"' in src, \
        "code-agent-host.js should have host in parsed args"


def test_host_in_server_options():
    """IServerOptions interface should include host property."""
    src = Path(f"{REPO}/src/vs/platform/agentHost/node/agentHostServerMain.ts").read_text()
    assert "host:" in src or "host?" in src or "readonly host" in src, \
        "IServerOptions should have host property"


def test_host_passed_to_server():
    """Host option should be passed to wsServer creation."""
    src = Path(f"{REPO}/src/vs/platform/agentHost/node/agentHostServerMain.ts").read_text()
    assert "host: options.host" in src or "host: options" in src, \
        "Host should be passed to WebSocket server"


def test_resolve_server_urls_imported():
    """agentHostServerMain.ts should import resolveServerUrls."""
    src = Path(f"{REPO}/src/vs/platform/agentHost/node/agentHostServerMain.ts").read_text()
    assert "resolveServerUrls" in src, \
        "Should import resolveServerUrls"
