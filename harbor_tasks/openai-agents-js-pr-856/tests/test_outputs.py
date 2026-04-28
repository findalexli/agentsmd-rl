import os
import subprocess

REPO = "/workspace/openai-agents-js"
AGENTS_MD = os.path.join(REPO, "AGENTS.md")


def test_agents_md_has_version_search_rule():
    """fail_to_pass | AGENTS.md includes the rule to web-search for latest
    stable major versions of official GitHub Actions."""
    with open(AGENTS_MD) as f:
        content = f.read()
    assert "web-search for the latest stable major versions of official actions" in content, (
        "AGENTS.md is missing the rule about web-searching for latest stable "
        "major versions of official actions"
    )


def test_agents_md_has_before_updating_pins_clause():
    """fail_to_pass | AGENTS.md includes the 'before updating version pins'
    clause to complete the GitHub Actions version-pinning guidance."""
    with open(AGENTS_MD) as f:
        content = f.read()
    assert "before updating version pins" in content, (
        "AGENTS.md is missing the 'before updating version pins' clause"
    )


# === CI-mined tests (pass_to_pass regression guards) ===
def test_ci_build_run_build():
    """pass_to_pass | CI job 'test' -> step 'Build all packages'"""
    r = subprocess.run(
        ["bash", "-lc", "pnpm build"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build all packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_test_check_generated_declarations():
    """pass_to_pass | CI job 'test' -> step 'Check generated declarations'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm -r -F "@openai/*" dist:check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check generated declarations' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_test_run_linter():
    """pass_to_pass | CI job 'test' -> step 'Run linter'"""
    r = subprocess.run(
        ["bash", "-lc", "pnpm lint"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run linter' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_test_type_check_docs_scripts():
    """pass_to_pass | CI job 'test' -> step 'Type-check docs scripts'"""
    r = subprocess.run(
        ["bash", "-lc", "pnpm docs:scripts:check"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Type-check docs scripts' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_test_compile_examples():
    """pass_to_pass | CI job 'test' -> step 'Compile examples'"""
    r = subprocess.run(
        ["bash", "-lc", "pnpm -r build-check"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Compile examples' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' -> step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", "pnpm test"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
