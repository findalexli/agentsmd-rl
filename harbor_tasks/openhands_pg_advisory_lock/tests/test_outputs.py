"""Tests for filename sanitization fix.

This module tests that the fix for preserving special characters in
uploaded filenames works correctly.
"""

import subprocess
import sys

# Docker-internal path to the repo
REPO = "/workspace/gradio"


def test_filename_with_special_chars():
    """Test that special characters are preserved in filenames (fail_to_pass).

    This test checks the core fix: filenames with special characters
    like hash, ampersand should be preserved, while path traversal
    characters are still stripped.
    """
    sys.path.insert(0, f"{REPO}/client/python")
    from gradio_client.utils import strip_invalid_filename_characters

    assert strip_invalid_filename_characters("abc") == "abc"
    assert strip_invalid_filename_characters("$$AAabc&3") == "AAabc&3"
    assert strip_invalid_filename_characters("a#.txt") == "a#.txt"
    assert strip_invalid_filename_characters("a/b\\c.txt") == "abc.txt"


def test_filename_with_unicode_punctuation():
    """Test that unicode punctuation is preserved in filenames (fail_to_pass).

    This test checks that unicode characters like Japanese punctuation
    marks are preserved after the fix rather than being stripped.
    """
    sys.path.insert(0, f"{REPO}/client/python")
    from gradio_client.utils import strip_invalid_filename_characters

    result = strip_invalid_filename_characters(
        "ゆかりです｡私､こんなかわいい服は初めて着ました…｡"
    )
    assert "｡" in result, f"Unicode ｡ should be preserved, got: {repr(result)}"
    assert "､" in result, f"Unicode ､ should be preserved, got: {repr(result)}"


def test_repo_lint():
    """Repo's Python linter passes (pass_to_pass).

    Runs ruff check on the modified code to ensure it follows the
    project's linting standards.
    """
    r = subprocess.run(
        ["python", "-m", "ruff", "check", "client/python/gradio_client/utils.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_format():
    """Repo's Python code is properly formatted (pass_to_pass).

    Runs ruff format check to ensure the code follows the project's
    formatting standards.
    """
    r = subprocess.run(
        ["python", "-m", "ruff", "format", "--check", "client/python/gradio_client/utils.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_unit_tests():
    """Repo's unit tests for modified module pass (pass_to_pass).

    Runs the existing unit tests for the utils module, excluding the
    filename sanitization tests which expect the old (pre-fix) behavior.
    """
    r = subprocess.run(
        ["python", "-m", "pytest", "client/python/test/test_utils.py", "-v",
         "-k", "not test_strip_invalid_filename_characters"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Tests failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


def test_repo_import():
    """Modified module can be imported successfully (pass_to_pass).

    Verifies that the utils module can be imported without errors.
    """
    r = subprocess.run(
        ["python", "-c",
         "from gradio_client.utils import strip_invalid_filename_characters; print('OK')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Import failed:\n{r.stderr[-500:]}"
    assert "OK" in r.stdout, "Import did not return expected output"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_lint():
    """pass_to_pass | CI job 'build' → step 'Lint'"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/lint_backend.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_typecheck():
    """pass_to_pass | CI job 'build' → step 'Typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/type_check_backend.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_build_wheel():
    """pass_to_pass | CI job 'build' → step 'Build wheel'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv pip install build && python -m build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build wheel' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_build_gradio_client_wheel():
    """pass_to_pass | CI job 'build' → step 'Build gradio_client wheel'"""
    r = subprocess.run(
        ["bash", "-lc", 'python -m build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build gradio_client wheel' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_hygiene_test_generate_skill():
    """pass_to_pass | CI job 'hygiene-test' → step 'Generate Skill'"""
    r = subprocess.run(
        ["bash", "-lc", 'python3 -m venv venv && pip install -e client/python . && python scripts/generate_skill.py --check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Generate Skill' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_website_build_build_client():
    """pass_to_pass | CI job 'website-build' → step 'build client'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter @gradio/client build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'build client' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_website_build_build_packages():
    """pass_to_pass | CI job 'website-build' → step 'build packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm package'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'build packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_website_build_build_website():
    """pass_to_pass | CI job 'website-build' → step 'build website'"""
    r = subprocess.run(
        ["bash", "-lc", 'VERCEL=1 pnpm --filter website build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'build website' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_website_build_upload_docs_json_to_hf_dataset():
    """pass_to_pass | CI job 'website-build' → step 'Upload docs.json to HF dataset'"""
    r = subprocess.run(
        ["bash", "-lc", 'python scripts/upload_docs_json.py'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Upload docs.json to HF dataset' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")