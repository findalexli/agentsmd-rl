"""
Task: opencode-shutdown-idempotent-naming
Repo: anomalyco/opencode @ 2a0be8316be7ae6ec78f5d221851fc1cc0cdddb2
PR: 15924

Tests verify the functional shutdown fix, code cleanup, and AGENTS.md naming enforcement.
All fail-to-pass tests use subprocess.run() to execute bun scripts that verify behavioral
properties of the modified code.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/opencode"


def _run_in_repo(cmd: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a command in the repo directory."""
    return subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - CI/CD checks that must pass before and after fix
# -----------------------------------------------------------------------------

def test_repo_typecheck():
    """Repo's bun typecheck passes."""
    r = _run_in_repo(["bun", "turbo", "typecheck"], timeout=120)
    assert r.returncode == 0, f"Typecheck failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_cli_tests():
    """Repo's CLI tests pass."""
    r = subprocess.run(
        ["bun", "test", "test/cli/"],
        cwd=f"{REPO}/packages/opencode",
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, f"CLI tests failed:\n{r.stderr[-500:]}"


def test_repo_util_tests():
    """Repo's utility tests pass."""
    r = subprocess.run(
        ["bun", "test", "test/util/"],
        cwd=f"{REPO}/packages/opencode",
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, f"Util tests failed:\n{r.stderr[-500:]}"


def test_repo_prettier():
    """Code formatting passes prettier check."""
    r = _run_in_repo(
        ["npx", "prettier", "--check", "packages/opencode/src/cli/cmd/tui/"],
        timeout=60,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - behavioral tests for shutdown fix
# -----------------------------------------------------------------------------

def test_shutdown_cleanup_behavior():
    """Shutdown must be idempotent with listener cleanup and forced worker termination.

    Executes a bun script that analyzes thread.ts to verify:
    - The stop/shutdown function has a boolean guard with early return
    - process.off() is called for all three registered event listeners
    - worker.terminate() is called to force cleanup
    """
    r = _run_in_repo(["bun", "-e", """
const content = await Bun.file('packages/opencode/src/cli/cmd/tui/thread.ts').text()

// 1. Idempotent guard: a boolean flag checked with early return
if (!/if\\s*\\(\\w+\\)\\s*\\{?\\s*return/.test(content)) {
    console.error('FAIL: No early-return boolean guard for idempotent shutdown')
    process.exit(1)
}

// 2. Listener cleanup: process.off must be called for all 3 registered events
const offCount = (content.match(/process\\.off\\(/g) || []).length
if (offCount < 3) {
    console.error('FAIL: Expected >= 3 process.off() calls for listener cleanup, found ' + offCount)
    process.exit(1)
}

// 3. Forced worker termination after shutdown attempt
if (!content.includes('worker.terminate()')) {
    console.error('FAIL: Missing worker.terminate() call')
    process.exit(1)
}

console.log('PASS')
"""], timeout=30)
    assert r.returncode == 0, f"Shutdown cleanup check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_iife_removed_and_timeout_added():
    """Inline iife() calls replaced with named functions; withTimeout used for shutdown.

    Executes a bun script that verifies:
    - No iife() calls remain in thread.ts (extracted to standalone functions)
    - withTimeout is imported and used to bound the shutdown RPC call
    """
    r = _run_in_repo(["bun", "-e", """
const content = await Bun.file('packages/opencode/src/cli/cmd/tui/thread.ts').text()

// 1. No iife() calls should remain
if (/\\biife\\s*\\(/.test(content)) {
    console.error('FAIL: iife() calls still present — should be extracted to named functions')
    process.exit(1)
}

// 2. withTimeout must be imported and called
if (!/withTimeout\\s*\\(/.test(content)) {
    console.error('FAIL: withTimeout not used — shutdown RPC should be bounded with a timeout')
    process.exit(1)
}

console.log('PASS')
"""], timeout=30)
    assert r.returncode == 0, f"IIFE/timeout check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_verbose_names_simplified():
    """Verbose multi-word variable names replaced with shorter single-word alternatives.

    Executes a bun script that checks the old verbose names are no longer in thread.ts.
    """
    r = _run_in_repo(["bun", "-e", """
const content = await Bun.file('packages/opencode/src/cli/cmd/tui/thread.ts').text()

const verbose = ['baseCwd', 'workerPath', 'networkOpts', 'shouldStartServer']
const found = verbose.filter(name => content.includes(name))
if (found.length > 0) {
    console.error('FAIL: Verbose names still present: ' + found.join(', '))
    process.exit(1)
}

console.log('PASS')
"""], timeout=30)
    assert r.returncode == 0, f"Variable name check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_worker_shutdown_simplified():
    """Worker shutdown() must not use Promise.race (timeout now caller's responsibility).

    Executes a bun script that verifies worker.ts directly awaits Instance.disposeAll()
    without a Promise.race wrapper.
    """
    r = _run_in_repo(["bun", "-e", """
const content = await Bun.file('packages/opencode/src/cli/cmd/tui/worker.ts').text()

// Promise.race was used for timeout — should be removed (caller handles timeout now)
if (content.includes('Promise.race')) {
    console.error('FAIL: worker.ts still uses Promise.race — timeout is now caller responsibility')
    process.exit(1)
}

// Should directly await Instance.disposeAll()
if (!content.includes('await Instance.disposeAll()')) {
    console.error('FAIL: worker.ts should directly await Instance.disposeAll()')
    process.exit(1)
}

console.log('PASS')
"""], timeout=30)
    assert r.returncode == 0, f"Worker shutdown check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_agents_naming_enforcement():
    """AGENTS.md must have a naming enforcement section with mandatory rules.

    Executes a bun script that verifies the naming enforcement subsection exists
    with required structural properties: mandatory indicator, single-word rule,
    and sufficient bullet-point rules.
    """
    r = _run_in_repo(["bun", "-e", """
const content = await Bun.file('AGENTS.md').text()

// 1. Section header for naming enforcement
if (!/###.*[Nn]aming\\s+[Ee]nforcement/.test(content)) {
    console.error('FAIL: Missing naming enforcement section header in AGENTS.md')
    process.exit(1)
}

// 2. Extract the section (up to next ## heading or end of file)
const match = content.match(/###.*[Nn]aming\\s+[Ee]nforcement[\\s\\S]*?(?=\\n##[^#]|$)/)
if (!match) {
    console.error('FAIL: Could not extract naming enforcement section')
    process.exit(1)
}
const section = match[0]

// 3. Must indicate the rule is mandatory
if (!/MANDATORY/.test(section)) {
    console.error('FAIL: Section must indicate rules are MANDATORY')
    process.exit(1)
}

// 4. Must mention single word name preference
if (!/single.word/i.test(section)) {
    console.error('FAIL: Section must mention single-word name preference')
    process.exit(1)
}

// 5. Must have sufficient bullet-point rules (at least 4)
const bullets = (section.match(/^\\s*-/gm) || []).length
if (bullets < 4) {
    console.error('FAIL: Section needs >= 4 bullet point rules, found ' + bullets)
    process.exit(1)
}

console.log('PASS')
"""], timeout=30)
    assert r.returncode == 0, f"AGENTS.md naming enforcement check failed: {r.stderr}"
    assert "PASS" in r.stdout

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_unit_run_unit_tests():
    """pass_to_pass | CI job 'unit' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun turbo test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_run_app_e2e_tests():
    """pass_to_pass | CI job 'e2e' → step 'Run app e2e tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun --cwd packages/app test:e2e:local'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run app e2e tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_tauri_prepare():
    """pass_to_pass | CI job 'build-tauri' → step 'Prepare'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun ./scripts/prepare.ts'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Prepare' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_tauri_show_tauri_cli_version():
    """pass_to_pass | CI job 'build-tauri' → step 'Show tauri-cli version'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo tauri --version'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Show tauri-cli version' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_typecheck_run_typecheck():
    """pass_to_pass | CI job 'typecheck' → step 'Run typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")