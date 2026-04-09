"""
Task: gradio-add-test-utils
Repo: gradio-app/gradio @ 30bf54c187478cdafa70037f088e353f5629a995
PR:   13151

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/gradio"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_render_core_exports_intact():
    """render.ts still exports render, cleanup, and fireEvent functions."""
    render_ts = Path(REPO) / "js" / "tootils" / "src" / "render.ts"
    content = render_ts.read_text()
    assert "export async function render" in content, \
        "render function export missing"
    assert "function cleanup" in content, \
        "cleanup function missing"
    assert "fireEvent" in content, \
        "fireEvent export missing"


# [repo_ci] pass_to_pass - Repo CI: code formatting check
def test_repo_formatting():
    """Repo's code formatting passes (pass_to_pass)."""
    # Install pnpm if not available
    r = subprocess.run(["npm", "install", "-g", "pnpm"], capture_output=True, timeout=60)
    # Run format check using npx to ensure prettier is available
    r = subprocess.run(
        ["npx", "prettier", "--check", "--ignore-path", ".config/.prettierignore", "--config", ".config/.prettierrc.json", "--plugin", "prettier-plugin-svelte", "."],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\\n{r.stderr[-500:]}"


# [repo_ci] pass_to_pass - Repo CI: client node tests
def test_repo_client_node_tests():
    """Repo's client node tests pass (pass_to_pass)."""
    # Install pnpm if not available
    r = subprocess.run(["npm", "install", "-g", "pnpm"], capture_output=True, timeout=60)
    # Run client tests using npx vitest directly in the client/js directory
    env = {"NODE_NO_WARNINGS": "1", "TEST_MODE": "node"}
    r = subprocess.run(
        ["npx", "vitest", "run", "-c", "vite.config.ts"],
        capture_output=True, text=True, timeout=120, cwd=Path(REPO) / "client/js",
        env=env,
    )
    assert r.returncode == 0, f"Client node tests failed:\\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_package_json_exports_download_command():
    """package.json must have ./download-command export entry."""
    r = subprocess.run(
        ["node", "-e", """
const pkg = JSON.parse(require('fs').readFileSync('js/tootils/package.json', 'utf8'));
const exp = pkg.exports;
if (!exp || !exp['./download-command']) {
  console.error('Missing ./download-command export');
  process.exit(1);
}
console.log(JSON.stringify({ found: exp['./download-command'] }));
"""],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Missing ./download-command export:\\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    assert "download-command" in data["found"], \
        f"Export path should reference download-command, got: {data['found']}"


# [pr_diff] fail_to_pass
def test_render_event_buffer():
    """render.ts must buffer dispatched events for retrospective replay."""
    render_ts = Path(REPO) / "js" / "tootils" / "src" / "render.ts"
    content = render_ts.read_text()
    # The event buffer array must exist
    assert "event_buffer" in content, \
        "render.ts should declare an event_buffer array"
    # The dispatcher must push events into the buffer
    assert "event_buffer.push" in content, \
        "dispatcher should push events into event_buffer"


# [pr_diff] fail_to_pass
def test_listen_retrospective_mode():
    """listen() must accept a retrospective option and replay buffered events."""
    render_ts = Path(REPO) / "js" / "tootils" / "src" / "render.ts"
    content = render_ts.read_text()
    assert "retrospective" in content, \
        "listen function should support retrospective option"
    # Verify retrospective mode iterates over the buffer
    assert "for" in content and "event_buffer" in content, \
        "retrospective mode should iterate over event_buffer"


# [pr_diff] fail_to_pass
def test_mock_client_function():
    """render.ts must export a mock_client function for file upload tests."""
    render_ts = Path(REPO) / "js" / "tootils" / "src" / "render.ts"
    content = render_ts.read_text()
    assert "mock_client" in content, \
        "render.ts should export mock_client"
    assert "upload" in content and "stream" in content, \
        "mock_client should provide upload and stream mocks"


# [pr_diff] fail_to_pass
def test_download_module_functions():
    """download.ts must export download_file, upload_file, and drop_file."""
    download_ts = Path(REPO) / "js" / "tootils" / "src" / "download.ts"
    assert download_ts.exists(), "js/tootils/src/download.ts must exist"
    content = download_ts.read_text()
    for fn_name in ["download_file", "upload_file", "drop_file"]:
        assert f"export async function {fn_name}" in content, \
            f"download.ts must export {fn_name}"


# [pr_diff] fail_to_pass
def test_fixtures_module():
    """fixtures.ts must export all 6 test fixture constants."""
    fixtures_ts = Path(REPO) / "js" / "tootils" / "src" / "fixtures.ts"
    assert fixtures_ts.exists(), "js/tootils/src/fixtures.ts must exist"
    content = fixtures_ts.read_text()
    expected = ["TEST_TXT", "TEST_JPG", "TEST_PNG", "TEST_MP4", "TEST_WAV", "TEST_PDF"]
    for name in expected:
        assert f"export const {name}" in content, \
            f"fixtures.ts must export {name}"


# [pr_diff] fail_to_pass
def test_vite_config_browser_commands():
    """vite.config.ts must register expect_download, set_file_inputs, drop_files commands."""
    vite_config = Path(REPO) / "js" / "spa" / "vite.config.ts"
    content = vite_config.read_text()
    assert "expect_download" in content, \
        "vite.config.ts must import expect_download"
    assert "set_file_inputs" in content, \
        "vite.config.ts must import set_file_inputs"
    assert "drop_files" in content, \
        "vite.config.ts must import drop_files"
    # Must be in the commands section
    assert "commands" in content, \
        "vite.config.ts must register commands in browser config"


# ---------------------------------------------------------------------------
# Config/documentation update tests (agentmd-edit)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_readme_correct_package_name():
    """README.md must reference @gradio/tootils, not the old @gradio/button."""
    readme = Path(REPO) / "js" / "tootils" / "README.md"
    content = readme.read_text()
    assert "@gradio/tootils" in content or "tootils" in content.split("\n")[0], \
        "README should reference @gradio/tootils package"
    assert "@gradio/button" not in content, \
        "README should NOT still reference the old @gradio/button placeholder"


# [pr_diff] fail_to_pass
def test_readme_documents_render_function():
    """README.md must document the render function including its signature."""
    readme = Path(REPO) / "js" / "tootils" / "README.md"
    content = readme.read_text()
    assert "render" in content.lower(), \
        "README should document the render function"
    # Must describe the signature or parameters
    assert "Component" in content and "props" in content, \
        "README should describe render's parameters (Component, props)"
    # Must mention the return value
    assert "listen" in content, \
        "README should document the listen helper returned by render"


# [pr_diff] fail_to_pass
def test_readme_documents_file_utilities():
    """README.md must document download_file, upload_file, and drop_file utilities."""
    readme = Path(REPO) / "js" / "tootils" / "README.md"
    content = readme.read_text()
    assert "download_file" in content, \
        "README should document download_file"
    assert "upload_file" in content, \
        "README should document upload_file"
    assert "drop_file" in content, \
        "README should document drop_file"


# [pr_diff] fail_to_pass
def test_readme_documents_test_fixtures():
    """README.md must document the pre-built test fixture constants."""
    readme = Path(REPO) / "js" / "tootils" / "README.md"
    content = readme.read_text()
    # Must mention at least some fixtures by name
    assert "TEST_TXT" in content or "TEST_JPG" in content or "TEST_PNG" in content, \
        "README should document the test fixture constants (TEST_TXT, TEST_JPG, etc.)"
    # Must mention the fixture file source
    assert "test_files" in content or "test/test_files" in content, \
        "README should reference the test_files directory where fixtures live"
