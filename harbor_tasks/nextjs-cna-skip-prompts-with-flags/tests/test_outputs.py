"""
Task: nextjs-cna-skip-prompts-with-flags
Repo: vercel/next.js @ e6bf5f69a23e6b8681dbc9cb59e7c1cdbe3b9b3c

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess

REPO = "/workspace/next.js"
CNA = f"{REPO}/packages/create-next-app"
ENTRY = f"{CNA}/index.ts"


def _run_cna(args, tmp_path, name="app"):
    """Run create-next-app via tsx with given args, stdin=/dev/null."""
    dest = tmp_path / name
    cmd = ["tsx", ENTRY, str(dest)] + args
    return subprocess.run(
        cmd, capture_output=True, timeout=45, stdin=subprocess.DEVNULL,
        cwd=CNA,
    )


def _strip_ansi(text):
    """Remove ANSI escape codes from text."""
    return re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", text)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compilation(tmp_path):
    """packages/create-next-app/index.ts loads without syntax errors."""
    r = subprocess.run(
        ["tsx", ENTRY, "--help"],
        capture_output=True, timeout=30, cwd=CNA,
    )
    assert r.returncode == 0, f"tsx failed to load index.ts:\n{r.stderr.decode()[-1000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_partial_flags_no_prompts(tmp_path):
    """CLI with partial flags (--ts --tailwind --app) must NOT show interactive prompts."""
    r = _run_cna(["--ts", "--tailwind", "--app", "--skip-install"],
                 tmp_path, "partial1")
    assert r.returncode == 0, f"CLI failed with exit {r.returncode}"
    output = _strip_ansi(r.stdout.decode())
    # On buggy code, the CLI shows interactive prompt markers even with flags
    prompt_markers = ["Use arrow-keys", "Return to submit", "? Which", "? Would you like"]
    found = [m for m in prompt_markers if m.lower() in output.lower()]
    assert len(found) == 0, f"Interactive prompts shown despite flags: {found}"


# [pr_diff] fail_to_pass
def test_output_shows_defaults_summary(tmp_path):
    """Output shows a summary of defaulted options when partial flags given."""
    r = _run_cna(["--ts", "--tailwind", "--app", "--skip-install"],
                 tmp_path, "partial2")
    assert r.returncode == 0, f"CLI failed: {r.returncode}"
    output = _strip_ansi(r.stdout.decode())
    # The fix adds a "Using defaults for unprovided options" section
    assert "default" in output.lower() and "option" in output.lower(), (
        f"No defaults summary found in output:\n{output[:500]}"
    )


# [pr_diff] fail_to_pass
def test_output_includes_override_flags(tmp_path):
    """Output includes --flag patterns so caller knows how to change defaults."""
    r = _run_cna(["--ts", "--tailwind", "--app", "--skip-install"],
                 tmp_path, "partial3")
    assert r.returncode == 0, f"CLI failed: {r.returncode}"
    output = _strip_ansi(r.stdout.decode())
    all_flags = set(re.findall(r"--[a-z][\w-]+", output))
    input_flags = {"--ts", "--tailwind", "--app", "--skip-install"}
    override_flags = all_flags - input_flags
    assert len(override_flags) >= 3, (
        f"Only {len(override_flags)} override flags in output: {override_flags}"
    )


# [pr_diff] fail_to_pass
def test_different_flag_combo_no_prompts(tmp_path):
    """Different flag combo (--eslint --src-dir) also skips prompts — fix is general."""
    r = _run_cna(["--eslint", "--src-dir", "--skip-install"],
                 tmp_path, "combo2")
    assert r.returncode == 0, f"CLI failed with exit {r.returncode}"
    output = _strip_ansi(r.stdout.decode())
    # Must not show interactive prompts
    prompt_markers = ["Use arrow-keys", "Return to submit", "? Which", "? Would you like"]
    found = [m for m in prompt_markers if m.lower() in output.lower()]
    assert len(found) == 0, f"Interactive prompts shown for --eslint --src-dir: {found}"
    # Must mention at least some defaulted options
    assert "default" in output.lower(), "No defaults summary for --eslint --src-dir combo"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_cna_version():
    """create-next-app --version works (pass_to_pass)."""
    r = subprocess.run(
        ["tsx", ENTRY, "--version"],
        capture_output=True, text=True, timeout=30, cwd=CNA,
    )
    assert r.returncode == 0, f"--version failed:\n{r.stderr}"
    assert "16." in r.stdout or "15." in r.stdout or "17." in r.stdout, (
        f"Unexpected version output: {r.stdout}"
    )


# [repo_tests] pass_to_pass
def test_repo_cna_help():
    """create-next-app --help works (pass_to_pass)."""
    r = subprocess.run(
        ["tsx", ENTRY, "--help"],
        capture_output=True, text=True, timeout=30, cwd=CNA,
    )
    assert r.returncode == 0, f"--help failed:\n{r.stderr}"
    assert "Usage:" in r.stdout, f"Missing usage info in help:\n{r.stdout[:500]}"
    assert "--ts" in r.stdout, f"Missing --ts flag in help:\n{r.stdout[:500]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_yes_flag_still_works(tmp_path):
    """--yes --skip-install still works without hanging."""
    r = _run_cna(["--yes", "--skip-install"], tmp_path, "yesapp")
    assert r.returncode == 0, f"--yes flag failed with exit {r.returncode}"


# [pr_diff] pass_to_pass
def test_yes_flag_no_defaults_summary(tmp_path):
    """--yes flag does NOT produce a defaults summary."""
    r = _run_cna(["--yes", "--skip-install"], tmp_path, "yescheck")
    assert r.returncode == 0, f"--yes flag failed"
    output = _strip_ansi(r.stdout.decode()).lower()
    # --yes uses recommended defaults silently; no "defaults for unprovided" summary
    assert "unprovided" not in output, "--yes flag should not produce defaults summary"
