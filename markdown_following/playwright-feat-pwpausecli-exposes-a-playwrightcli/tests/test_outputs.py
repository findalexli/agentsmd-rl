"""
Task: playwright-feat-pwpausecli-exposes-a-playwrightcli
Repo: microsoft/playwright @ 982b9b279557229b12d049ebd3063da408ba5253
PR:   39408

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
Behavioral tests: verify exports via require() and call signatures via node reflection.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/playwright"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI checks that must pass before AND after fix
# ---------------------------------------------------------------------------

def test_repo_tsc():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "tsc"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_check_deps():
    """Repo's dependency check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "check-deps"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Check deps failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_lint_packages():
    """Repo's package linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint packages failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_lint_tests():
    """Repo's test linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint-tests"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_test_types():
    """Repo's test types check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "test-types"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Test types failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_build():
    """Repo build succeeds — compiles TypeScript to JavaScript (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_modified_files_exist():
    """Key modified TypeScript source files exist and are non-empty."""
    files = [
        "packages/playwright-core/src/server/utils/network.ts",
        "packages/playwright/src/worker/testInfo.ts",
        "packages/playwright/src/program.ts",
        "packages/playwright/src/cli/daemon/daemon.ts",
        "packages/playwright/src/mcp/test/browserBackend.ts",
        "packages/playwright/src/index.ts",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} does not exist"
        assert p.stat().st_size > 0, f"{f} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via require() / node reflection
# ---------------------------------------------------------------------------

def test_decorate_server_exported():
    """decorateServer is exported from network.ts so daemon.ts can import it.

    Verifies by requiring the compiled lib and checking the export exists.
    """
    r = subprocess.run(
        ["node", "-e",
         "const m = require('/workspace/playwright/packages/playwright-core/lib/server/utils/network.js'); "
         "if (typeof m.decorateServer !== 'function') { "
         "  console.error('decorateServer not exported or not a function'); "
         "  process.exit(1); "
         "} "
         "console.log('OK');"],
        capture_output=True, text=True, timeout=15, cwd=REPO,
    )
    assert r.returncode == 0, f"decorateServer export check failed: {r.stderr or r.stdout}"


def test_session_config_exported():
    """sessionConfigFromArgs is exported from cli/client/program.js.

    Verifies by requiring the compiled lib and checking the export exists.
    """
    r = subprocess.run(
        ["node", "-e",
         "const m = require('/workspace/playwright/packages/playwright/lib/cli/client/program.js'); "
         "if (typeof m.sessionConfigFromArgs !== 'function') { "
         "  console.error('sessionConfigFromArgs not exported or not a function'); "
         "  process.exit(1); "
         "} "
         "console.log('OK');"],
        capture_output=True, text=True, timeout=15, cwd=REPO,
    )
    assert r.returncode == 0, f"sessionConfigFromArgs export check failed: {r.stderr or r.stdout}"


def test_finish_callbacks_is_set():
    """Multiple finish callbacks can register and all are invoked.

    Verifies by checking the compiled index.js registers multiple finish callbacks
    and testInfo.js iterates over and awaits all registered callbacks.
    """
    r = subprocess.run(
        ["node", "-e",
         "const fs = require('fs'); "
         "const testInfoSrc = fs.readFileSync('/workspace/playwright/packages/playwright/lib/worker/testInfo.js', 'utf-8'); "
         "const indexSrc = fs.readFileSync('/workspace/playwright/packages/playwright/lib/index.js', 'utf-8'); "
         # Verify multiple callbacks are registered in index.js
         "let registered = 0; "
         "const lines = indexSrc.split('\\n'); "
         "for (const line of lines) { "
         "  if ((line.includes('didFinishTestFunction') || line.includes('runDaemonForContext')) && /\\.(add|push|on)\\(/.test(line)) { "
         "    registered++; "
         "  } "
         "} "
         "if (registered < 2) { "
         "  console.error('Must register at least 2 finish callbacks in index.js'); "
         "  process.exit(1); "
         "} "
         # Verify callbacks are iterated and invoked in testInfo.js
         "const methodStart = testInfoSrc.indexOf('async _didFinishTestFunction()'); "
         "const methodEnd = testInfoSrc.indexOf('async attach', methodStart); "
         "const methodBody = testInfoSrc.substring(methodStart, methodEnd); "
         "const hasLoop = /for\\s*\\(/.test(methodBody) || methodBody.includes('.forEach('); "
         "const hasAwait = /await\\s+\\w+\\(\\)/.test(methodBody); "
         "if (!hasLoop || !hasAwait) { "
         "  console.error('testInfo.js must iterate over and await finish callbacks'); "
         "  process.exit(1); "
         "} "
         # Verify old singular callback assignment is gone
         "if (indexSrc.includes('_onDidFinishTestFunctionCallback =')) { "
         "  console.error('Old singular callback assignment must be replaced'); "
         "  process.exit(1); "
         "} "
         "console.log('OK');"],
        capture_output=True, text=True, timeout=15, cwd=REPO,
    )
    assert r.returncode == 0, f"Callbacks check failed: {r.stderr or r.stdout}"


def test_pwpause_cli_overrides():
    """PWPAUSE=cli creates a distinct code path that configures timeout overrides
    without triggering pause mode.

    Verifies by checking the compiled JS has a PWPAUSE=cli branch that sets
    timeout-related overrides and that the old unconditional pause is removed.
    """
    r = subprocess.run(
        ["node", "-e",
         "const fs = require('fs'); "
         "const src = fs.readFileSync('/workspace/playwright/packages/playwright/lib/program.js', 'utf-8'); "
         # Check PWPAUSE is compared to 'cli'
         "const hasCliCheck = /process\\.env\\.PWPAUSE\\s*===?\\s*['\"]cli['\"]/.test(src) || "
         "                    /['\"]cli['\"]\\s*===?\\s*process\\.env\\.PWPAUSE/.test(src); "
         "if (!hasCliCheck) { "
         "  console.error('program.ts must check for PWPAUSE cli mode'); "
         "  process.exit(1); "
         "} "
         # Find the cli conditional block and verify it configures timeout overrides
         "const cliIdx = src.search(/PWPAUSE.*?['\"]cli['\"]|['\"]cli['\"].*?PWPAUSE/); "
         "const cliBlock = src.substring(cliIdx, cliIdx + 400); "
         "if (!/\\.timeout\\s*=/.test(cliBlock)) { "
         "  console.error('PWPAUSE=cli branch must configure a test timeout override'); "
         "  process.exit(1); "
         "} "
         "if (!/actionTimeout\\s*[=:]/.test(cliBlock)) { "
         "  console.error('PWPAUSE=cli branch must configure an action timeout override'); "
         "  process.exit(1); "
         "} "
         # Check old unconditional pause assignment is gone
         "if (src.includes('pause: process.env.PWPAUSE')) { "
         "  console.error('pause must not be unconditionally set from PWPAUSE'); "
         "  process.exit(1); "
         "} "
         "console.log('OK');"],
        capture_output=True, text=True, timeout=15, cwd=REPO,
    )
    assert r.returncode == 0, f"PWPAUSE=cli overrides check failed: {r.stderr or r.stdout}"


def test_run_daemon_for_context_exported():
    """runDaemonForContext is an exported async function in browserBackend.js.

    Verifies by requiring the module and checking the export is an async function.
    """
    r = subprocess.run(
        ["node", "-e",
         "const m = require('/workspace/playwright/packages/playwright/lib/mcp/test/browserBackend.js'); "
         "if (typeof m.runDaemonForContext !== 'function') { "
         "  console.error('runDaemonForContext not exported or not a function'); "
         "  process.exit(1); "
         "} "
         "console.log('OK');"],
        capture_output=True, text=True, timeout=15, cwd=REPO,
    )
    assert r.returncode == 0, f"runDaemonForContext export check failed: {r.stderr or r.stdout}"


def test_daemon_accepts_no_shutdown():
    """startMcpDaemonServer accepts noShutdown parameter to keep daemon alive.

    Verifies by inspecting the compiled daemon.js function signature and checking
    the browser close handler is conditional.
    """
    r = subprocess.run(
        ["node", "-e",
         "const fs = require('fs'); "
         "const fnBody = fs.readFileSync('/workspace/playwright/packages/playwright/lib/cli/daemon/daemon.js', 'utf-8'); "
         "const match = fnBody.match(/async function startMcpDaemonServer\\s*\\([^)]*\\)/); "
         "if (!match) { "
         "  console.error('startMcpDaemonServer function not found'); "
         "  process.exit(1); "
         "} "
         "const sig = match[0]; "
         "const hasFourthParam = sig.split(',').length >= 4; "
         "const hasOptionsParam = sig.includes('{') && sig.includes('}'); "
         "if (!hasFourthParam && !hasOptionsParam) { "
         "  console.error('startMcpDaemonServer must accept a shutdown-control parameter'); "
         "  process.exit(1); "
         "} "
         "const closeHandlerIndex = fnBody.indexOf('browserContext.on(\\\"close\\\"'); "
         "const codeBeforeClose = fnBody.substring(Math.max(0, closeHandlerIndex - 100), closeHandlerIndex); "
         "if (!codeBeforeClose.includes('if (')) { "
         "  console.error('browser close handler must be conditional'); "
         "  process.exit(1); "
         "} "
         "console.log('OK');"],
        capture_output=True, text=True, timeout=15, cwd=REPO,
    )
    assert r.returncode == 0, f"noShutdown parameter check failed: {r.stderr or r.stdout}"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — SKILL.md and reference doc tests
# ---------------------------------------------------------------------------

def test_skill_md_updated():
    """SKILL.md allowed-tools includes npx/npm and links to playwright-tests reference.

    Verifies by parsing the SKILL.md frontmatter and checking the specific tasks section.
    """
    r = subprocess.run(
        ["node", "-e",
         "const fs = require('fs'); "
         "const src = fs.readFileSync('/workspace/playwright/packages/playwright/src/skill/SKILL.md', 'utf-8'); "
         "const fmStart = src.indexOf('---'); "
         "const fmEnd = src.indexOf('---', fmStart + 3); "
         "if (fmStart === -1 || fmEnd === -1) { "
         "  console.error('SKILL.md has no frontmatter'); "
         "  process.exit(1); "
         "} "
         "const fm = src.slice(fmStart + 3, fmEnd); "
         "if (!fm.includes('Bash(npx:*)')) { "
         "  console.error('allowed-tools must include Bash(npx:*)'); "
         "  process.exit(1); "
         "} "
         "if (!fm.includes('Bash(npm:*)')) { "
         "  console.error('allowed-tools must include Bash(npm:*)'); "
         "  process.exit(1); "
         "} "
         "if (!src.includes('references/playwright-tests.md')) { "
         "  console.error('Specific tasks must link to references/playwright-tests.md'); "
         "  process.exit(1); "
         "} "
         "console.log('OK');"],
        capture_output=True, text=True, timeout=15, cwd=REPO,
    )
    assert r.returncode == 0, f"SKILL.md update check failed: {r.stderr or r.stdout}"


def test_playwright_tests_reference_created():
    """playwright-tests.md reference doc exists and documents PWPAUSE=cli workflow.

    Verifies by checking the file exists and parsing its content.
    """
    r = subprocess.run(
        ["node", "-e",
         "const fs = require('fs'); "
         "const refPath = '/workspace/playwright/packages/playwright/src/skill/references/playwright-tests.md'; "
         "if (!fs.existsSync(refPath)) { "
         "  console.error('references/playwright-tests.md does not exist'); "
         "  process.exit(1); "
         "} "
         "const src = fs.readFileSync(refPath, 'utf-8'); "
         "if (!src.includes('PWPAUSE=cli')) { "
         "  console.error('Must document PWPAUSE=cli env var'); "
         "  process.exit(1); "
         "} "
         "if (!src.includes('playwright-cli')) { "
         "  console.error('Must mention playwright-cli for connecting'); "
         "  process.exit(1); "
         "} "
         "if (!src.includes('--session=')) { "
         "  console.error('Must show --session= flag for connecting to test session'); "
         "  process.exit(1); "
         "} "
         "console.log('OK');"],
        capture_output=True, text=True, timeout=15, cwd=REPO,
    )
    assert r.returncode == 0, f"playwright-tests.md reference check failed: {r.stderr or r.stdout}"
