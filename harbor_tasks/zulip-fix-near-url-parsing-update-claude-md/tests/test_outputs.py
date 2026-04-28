"""
Task: zulip-fix-near-url-parsing-update-claude-md
Repo: zulip/zulip @ 305c52c35a7dad3e6c9bde470e8f717186abaae5
PR:   37872

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import importlib.util
import subprocess
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

REPO = "/workspace/zulip"
FETCH_SCRIPT = (
    Path(REPO) / ".claude" / "skills" / "fetch-zulip-messages" / "fetch-zulip-web-public-messages"
)


def _load_fetch_module():
    """Import the fetch-zulip-web-public-messages script as a module."""
    # Use SourceFileLoader since the script has no .py extension
    loader = SourceFileLoader("fetch_zulip", str(FETCH_SCRIPT))
    spec = importlib.util.spec_from_loader("fetch_zulip", loader)
    mod = importlib.util.module_from_spec(spec)
    # Prevent the module from calling sys.exit on import
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """fetch-zulip-web-public-messages parses without syntax errors."""
    import py_compile
    py_compile.compile(str(FETCH_SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_parse_near_url():
    """parse_zulip_url must handle near/ID anchor format."""
    mod = _load_fetch_module()
    url = "https://chat.zulip.org/#narrow/channel/101-design/topic/cool.20feature/near/54321"
    server, channel_id, topic, anchor = mod.parse_zulip_url(url)
    assert server == "https://chat.zulip.org", f"Wrong server: {server}"
    assert channel_id == 101, f"Wrong channel_id: {channel_id}"
    assert topic == "cool feature", f"Wrong topic: {topic}"
    assert anchor == "54321", f"Wrong anchor: {anchor}"


# [pr_diff] fail_to_pass
def test_parse_near_url_stream_variant():
    """parse_zulip_url must handle near/ID with stream prefix."""
    mod = _load_fetch_module()
    url = "https://zulip.example.com/#narrow/stream/42-general/topic/hello/near/99999"
    server, channel_id, topic, anchor = mod.parse_zulip_url(url)
    assert server == "https://zulip.example.com", f"Wrong server: {server}"
    assert channel_id == 42, f"Wrong channel_id: {channel_id}"
    assert topic == "hello", f"Wrong topic: {topic}"
    assert anchor == "99999", f"Wrong anchor: {anchor}"


# [pr_diff] fail_to_pass
def test_error_message_mentions_near():
    """Error message should document the near/ID URL format."""
    r = subprocess.run(
        [sys.executable, str(FETCH_SCRIPT), "https://invalid.example.com/#bad-url"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode != 0, "Should fail on bad URL"
    assert "near" in r.stderr, (
        f"Error message should mention 'near' format. Got:\n{r.stderr}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_parse_with_url_still_works():
    """parse_zulip_url must still handle the original with/ID format."""
    mod = _load_fetch_module()
    url = "https://chat.zulip.org/#narrow/channel/137-feedback/topic/hello.20world/with/12345"
    server, channel_id, topic, anchor = mod.parse_zulip_url(url)
    assert server == "https://chat.zulip.org", f"Wrong server: {server}"
    assert channel_id == 137, f"Wrong channel_id: {channel_id}"
    assert topic == "hello world", f"Wrong topic: {topic}"
    assert anchor == "12345", f"Wrong anchor: {anchor}"


# [static] pass_to_pass
def test_parse_url_no_anchor():
    """parse_zulip_url must handle URLs without any anchor."""
    mod = _load_fetch_module()
    url = "https://chat.zulip.org/#narrow/channel/9-errors/topic/bug.20report"
    server, channel_id, topic, anchor = mod.parse_zulip_url(url)
    assert server == "https://chat.zulip.org", f"Wrong server: {server}"
    assert channel_id == 9, f"Wrong channel_id: {channel_id}"
    assert topic == "bug report", f"Wrong topic: {topic}"
    assert anchor is None, f"Expected None anchor, got: {anchor}"


# ---------------------------------------------------------------------------
# Config-derived (pr_diff) — CLAUDE.md update
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_claude_md_zulip_chat_links():
    """CLAUDE.md must have a section about handling Zulip chat links."""
    claude_md = Path(REPO) / ".claude" / "CLAUDE.md"
    content = claude_md.read_text()
    assert "zulip" in content.lower() and "chat" in content.lower() and "link" in content.lower(), (
        "CLAUDE.md should have a section about Zulip chat links"
    )
    assert "fetch-zulip-messages" in content, (
        "CLAUDE.md should reference the fetch-zulip-messages skill"
    )
    assert "WebFetch" in content or "webfetch" in content.lower(), (
        "CLAUDE.md should warn against using WebFetch for Zulip URLs"
    )


# ---------------------------------------------------------------------------
# Repo CI-derived pass_to_pass tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_pylint_errors_only():
    """Pylint finds no errors in fetch-zulip-web-public-messages (pass_to_pass)."""
    # Install pylint temporarily and run with orjson generated members
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "pylint", "-q"],
        capture_output=True, timeout=60,
    )
    # Run pylint with errors-only and generated-members for orjson C extensions
    r = subprocess.run(
        [
            sys.executable, "-m", "pylint",
            "--errors-only",
            "--generated-members=orjson.dumps,orjson.loads,orjson.JSONDecodeError,orjson.OPT_INDENT_2",
            str(FETCH_SCRIPT),
        ],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Pylint errors found:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_pyflakes_clean():
    """Pyflakes finds no issues in fetch-zulip-web-public-messages (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "pyflakes", "-q"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        [sys.executable, "-m", "pyflakes", str(FETCH_SCRIPT)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Pyflakes errors found:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_script_help_works():
    """fetch-zulip-web-public-messages --help runs without error (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, str(FETCH_SCRIPT), "--help"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Script --help failed:\n{r.stderr}"
    assert "usage:" in r.stdout.lower(), "Help output should contain 'usage:'"


# [repo_tests] pass_to_pass
def test_repo_ruff():
    """Ruff linter passes on fetch-zulip-web-public-messages (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(FETCH_SCRIPT)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff found issues:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_black():
    """Black format check passes on fetch-zulip-web-public-messages (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "black", "-q"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        [sys.executable, "-m", "black", "--check", str(FETCH_SCRIPT)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Black format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_isort():
    """isort import order check passes on fetch-zulip-web-public-messages (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "isort", "-q"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        [sys.executable, "-m", "isort", "--check", str(FETCH_SCRIPT)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_bandit():
    """Bandit security linter passes on fetch-zulip-web-public-messages (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "bandit", "-q"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        [sys.executable, "-m", "bandit", "-r", str(FETCH_SCRIPT), "-ll", "-ii"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Bandit returns 0 when no issues found, 1 when issues found
    assert r.returncode == 0, f"Bandit found security issues:\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_script_imports_cleanly():
    """fetch-zulip-web-public-messages imports without errors (pass_to_pass)."""
    # Test that the script can be imported as a module without side effects
    test_code = """
import importlib.util
from importlib.machinery import SourceFileLoader
import sys

# Prevent sys.exit on import
sys.exit = lambda x: None

script = '/workspace/zulip/.claude/skills/fetch-zulip-messages/fetch-zulip-web-public-messages'
loader = SourceFileLoader('fetch_test_module', script)
spec = importlib.util.spec_from_loader('fetch_test_module', loader)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Verify key functions exist
assert hasattr(mod, 'parse_zulip_url'), "Missing parse_zulip_url function"
assert hasattr(mod, 'fetch_messages'), "Missing fetch_messages function"
assert hasattr(mod, 'main'), "Missing main function"
print("SUCCESS: Script imports cleanly")
"""
    r = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Script import test failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_pycodestyle():
    """pycodestyle (PEP 8) check passes on fetch-zulip-web-public-messages (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "pycodestyle", "-q"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        [sys.executable, "-m", "pycodestyle", "--max-line-length=100", str(FETCH_SCRIPT)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"pycodestyle found issues:\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_flake8():
    """Flake8 linter passes on fetch-zulip-web-public-messages (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "flake8", "-q"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        [sys.executable, "-m", "flake8", "--max-line-length=100", str(FETCH_SCRIPT)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Flake8 found issues:\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_script_dry_run_syntax():
    """Script dry-run shows proper argument handling without network (pass_to_pass)."""
    # Test that the script properly handles URL validation before network calls
    r = subprocess.run(
        [sys.executable, str(FETCH_SCRIPT), "https://chat.zulip.org/#narrow/channel/101/topic/test"],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    # Should fail with network error (no API key/spectator access), not syntax error
    # Exit code will be non-zero due to network/API failure, but no Python exceptions
    assert "Traceback" not in r.stderr, f"Script had unhandled exception:\n{r.stderr}"
    assert "Error:" in r.stderr or r.returncode != 0, "Should have expected error output"


# [repo_tests] pass_to_pass
def test_ci_bash_ruff_lint():
    """CI-style lint: ruff check invoked through bash -lc (pass_to_pass)."""
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        ["bash", "-lc", f"python3 -m ruff check '{FETCH_SCRIPT}'"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff CI lint (bash -lc) failed:\n{r.stdout[-500:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_ubuntu_22_04_production_build_build_production_tarball():
    """pass_to_pass | CI job 'Ubuntu 22.04 production build' → step 'Build production tarball'"""
    r = subprocess.run(
        ["bash", "-lc", './tools/ci/production-build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build production tarball' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_ubuntu_22_04_production_build_verify_pnpm_store_path():
    """pass_to_pass | CI job 'Ubuntu 22.04 production build' → step 'Verify pnpm store path'"""
    r = subprocess.run(
        ["bash", "-lc", 'set -x\npath="$(pnpm store path)"\n[[ "$path" == /__w/.pnpm-store/* ]]'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify pnpm store path' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")