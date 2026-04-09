"""
Task: playwright-feattrace-add-trace-close-command
Repo: playwright @ 21268964f99d52e5a48e24c04df5f6dc9e7fa0bc
PR:   39903

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/playwright"
TRACE_UTILS = Path(REPO) / "packages/playwright-core/src/tools/trace/traceUtils.ts"
TRACE_CLI = Path(REPO) / "packages/playwright-core/src/tools/trace/traceCli.ts"
SKILL_MD = Path(REPO) / "packages/playwright-core/src/tools/trace/SKILL.md"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js in the repo directory."""
    script = Path(REPO) / "_harbor_eval.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified TypeScript files must exist and contain valid content."""
    for ts_file in [TRACE_UTILS, TRACE_CLI]:
        assert ts_file.is_file(), f"Missing: {ts_file}"
        content = ts_file.read_text()
        assert len(content) > 100, f"File too small: {ts_file}"
        assert "import" in content, f"No imports in {ts_file.name}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - repo CI/CD checks
# ---------------------------------------------------------------------------

def test_repo_eslint():
    """Repo's ESLint check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "eslint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


def test_repo_lint_packages():
    """Repo's package consistency check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint packages failed:\n{r.stderr[-500:]}"


def test_repo_build():
    """Repo's build passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_close_trace_function_exported():
    """traceUtils.ts exports an async closeTrace function with fs cleanup logic."""
    r = _run_node(r"""
const fs = require('fs');
const source = fs.readFileSync(
    'packages/playwright-core/src/tools/trace/traceUtils.ts', 'utf8'
);

// Must have the exported async function
if (!/export\s+async\s+function\s+closeTrace/.test(source)) {
    console.error('No exported async closeTrace function found');
    process.exit(1);
}

// Extract body and verify it has fs removal logic
const m = source.match(/export\s+async\s+function\s+closeTrace\s*\(\)[^{]*\{([\s\S]*?)\n\}/);
if (!m) {
    console.error('Could not parse closeTrace function body');
    process.exit(1);
}
if (!/rm|rmSync|unlink/.test(m[1])) {
    console.error('closeTrace body has no removal operation');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_close_trace_removes_directory():
    """closeTrace function body, extracted from source and executed, removes a directory."""
    r = _run_node(r"""
const fs = require('fs');
const path = require('path');
const os = require('os');

// Read source and extract the closeTrace function body
const source = fs.readFileSync(
    'packages/playwright-core/src/tools/trace/traceUtils.ts', 'utf8'
);
const m = source.match(/export\s+async\s+function\s+closeTrace\s*\(\)[^{]*\{([\s\S]*?)\n\}/);
if (!m) {
    console.error('closeTrace function not found in source');
    process.exit(1);
}

// Create a test directory with nested content
const traceDir = path.join(os.tmpdir(), 'playwright-trace');
fs.mkdirSync(path.join(traceDir, 'nested'), { recursive: true });
fs.writeFileSync(path.join(traceDir, 'trace.json'), '{"events":[]}');
fs.writeFileSync(path.join(traceDir, 'nested', 'snapshot.html'), '<html></html>');

if (!fs.existsSync(traceDir)) {
    console.error('Setup failed: directory not created');
    process.exit(1);
}

// Execute the ACTUAL function body extracted from source
const AsyncFn = Object.getPrototypeOf(async function(){}).constructor;
const closeFn = new AsyncFn('fs', 'traceDir', m[1]);
closeFn(fs, traceDir).then(() => {
    if (fs.existsSync(traceDir)) {
        console.error('Directory still exists after executing closeTrace body');
        process.exit(1);
    }
    console.log('PASS');
}).catch(e => {
    console.error('Execution failed:', e.message);
    process.exit(1);
});
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_close_command_registered():
    """traceCli.ts registers a 'close' subcommand that references closeTrace."""
    r = _run_node(r"""
const fs = require('fs');
const source = fs.readFileSync(
    'packages/playwright-core/src/tools/trace/traceCli.ts', 'utf8'
);

if (!/\.command\(\s*['"]close['"]\s*\)/.test(source)) {
    console.error('No .command("close") registration found');
    process.exit(1);
}
if (!/closeTrace/.test(source)) {
    console.error('closeTrace not referenced in CLI module');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_open_trace_uses_close_trace():
    """openTrace delegates cleanup to closeTrace() instead of inline rm."""
    r = _run_node(r"""
const fs = require('fs');
const source = fs.readFileSync(
    'packages/playwright-core/src/tools/trace/traceUtils.ts', 'utf8'
);

// Extract openTrace function body
const m = source.match(/export\s+async\s+function\s+openTrace[^{]*\{([\s\S]*?)\n\}/);
if (!m) {
    console.error('openTrace function not found');
    process.exit(1);
}
const body = m[1];

// Must call closeTrace()
if (!/closeTrace\s*\(/.test(body)) {
    console.error('openTrace does not call closeTrace()');
    process.exit(1);
}

// Must NOT have inline fs.promises.rm(traceDir...) anymore
if (/fs\.promises\.rm\s*\(\s*traceDir/.test(body)) {
    console.error('openTrace still contains inline rm(traceDir) logic');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Config edit tests (agent_config) — SKILL.md documentation
# ---------------------------------------------------------------------------

def test_skill_md_close_section():
    """SKILL.md documents the trace close command with a heading and code block."""
    content = SKILL_MD.read_text()
    has_heading = any(
        "close" in line.lower() and line.strip().startswith("#")
        for line in content.split("\n")
    )
    assert has_heading, "SKILL.md must have a heading for the close command"
    assert "npx playwright trace close" in content, \
        "SKILL.md must show 'npx playwright trace close' usage"


def test_skill_md_workflow_mentions_close():
    """SKILL.md workflow steps include a numbered step for trace close."""
    content = SKILL_MD.read_text()
    lines = content.split("\n")
    has_close_step = any(
        "close" in line.lower() and "trace" in line.lower()
        for line in lines
        if line.strip() and line.strip()[0].isdigit()
    )
    assert has_close_step, \
        "SKILL.md must have a numbered workflow step mentioning 'trace close'"
