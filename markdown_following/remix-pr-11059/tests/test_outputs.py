import json
import os
import subprocess

REPO = "/workspace/remix"
COMPONENT = os.path.join(REPO, "packages", "component")


def _parse_vitest_json(stdout: str):
    """Extract the vitest JSON results object from stdout (may contain other log lines)."""
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith("{") and '"testResults"' in line:
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    # Try parsing the whole output
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        pass
    raise AssertionError(f"Could not find vitest JSON in output.\nstdout: {stdout[-2000:]}")


def _run_vitest(test_file=None, timeout=300):
    """Run vitest with JSON reporter and return (parsed_results, returncode)."""
    cmd = ["npx", "vitest", "run", "--reporter=json"]
    if test_file:
        cmd.append(test_file)
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=COMPONENT, timeout=timeout)
    results = _parse_vitest_json(r.stdout)
    return results, r.returncode


def _find_test(results, substring):
    """Find the first assertion result whose title contains `substring`."""
    for suite in results.get("testResults", []):
        for t in suite.get("assertionResults", []):
            if substring in t.get("title", ""):
                return t
    return None


# -- f2p tests ----------------------------------------------------------

def test_removes_attributes():
    """f2p: Removing props should fully remove reflected attributes from DOM elements."""
    results, _ = _run_vitest("src/test/vdom.insert-remove.test.tsx", timeout=120)
    t = _find_test(results, "removes attributes")
    assert t is not None, "Test 'removes attributes' not found (may not exist or be filtered)"
    assert t["status"] == "passed", f"Test 'removes attributes' status: {t['status']} (expected 'passed')"


def test_removes_reflected_attributes_cleanly():
    """f2p: Removing host props on a div should remove all reflected attributes without leaving empty strings."""
    results, _ = _run_vitest("src/test/vdom.insert-remove.test.tsx", timeout=120)
    t = _find_test(results, "removes reflected attributes without leaving empty values")
    assert t is not None, (
        "Test 'removes reflected attributes without leaving empty values' not found — "
        "it may not exist yet or the test file is missing the new test case"
    )
    assert t["status"] == "passed", f"Test status: {t['status']}"


def test_updates_element_with_attributes():
    """f2p: Updating an element's attributes should reuse the same DOM node and apply new values."""
    results, _ = _run_vitest("src/test/vdom.replacements.test.tsx", timeout=120)
    t = _find_test(results, "updates an element with attributes")
    assert t is not None, "Test 'updates an element with attributes' not found"
    assert t["status"] == "passed", f"Test status: {t['status']}"


# -- p2p tests ----------------------------------------------------------

def test_repo_full_test_suite():
    """p2p: The full component test suite passes (excluding fixed-on-gold tests)."""
    results, rc = _run_vitest(timeout=600)
    for suite in results.get("testResults", []):
        for t in suite.get("assertionResults", []):
            assert t.get("status") != "failed", (
                f"Test '{t.get('title')}' failed in suite '{suite.get('name')}': {t.get('failureMessages', [])}"
            )


def test_repo_typecheck():
    """p2p: TypeScript typecheck passes for the component package."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        capture_output=True, text=True, cwd=COMPONENT, timeout=120,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_build_packages():
    """pass_to_pass | CI job 'build' → step 'Build packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_lint():
    """pass_to_pass | CI job 'check' → step 'Lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_typecheck():
    """pass_to_pass | CI job 'check' → step 'Typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_check_change_files():
    """pass_to_pass | CI job 'check' → step 'Check change files'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm changes:validate'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check change files' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_format_format():
    """pass_to_pass | CI job 'format' → step 'Format'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm format'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Format' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")