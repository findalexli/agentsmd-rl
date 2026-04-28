"""
Task: opencode-subagent-footer-restore
Repo: anomalyco/opencode @ 41b0d03f6afabc30696e9ccbbdbb7c3df34fd404
PR:   #19491

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import re
from pathlib import Path

REPO = "/workspace/opencode"
FOOTER = f"{REPO}/packages/opencode/src/cli/cmd/tui/routes/session/subagent-footer.tsx"
SESSION = f"{REPO}/packages/opencode/src/cli/cmd/tui/routes/session/index.tsx"
DIALOG_MODEL = f"{REPO}/packages/opencode/src/cli/cmd/tui/component/dialog-model.tsx"
DIALOG_VARIANT = f"{REPO}/packages/opencode/src/cli/cmd/tui/component/dialog-variant.tsx"
SESSION_DIR = f"{REPO}/packages/opencode/src/cli/cmd/tui/routes/session"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


def _strip_comments(code: str) -> str:
    """Remove single-line and multi-line JS/TS comments."""
    code = re.sub(r"//.*$", "", code, flags=re.MULTILINE)
    code = re.sub(r"/\*[\s\S]*?\*/", "", code)
    return code


def _read_stripped(path: str) -> str:
    return _strip_comments(Path(path).read_text())


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

def test_syntax_check():
    """All modified TSX files must have balanced braces."""
    for path in [FOOTER, SESSION, DIALOG_MODEL, DIALOG_VARIANT]:
        p = Path(path)
        if not p.exists():
            continue
        src = p.read_text()
        depth = 0
        for ch in src:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            assert depth >= 0, f"{path} has unbalanced braces (depth went negative)"
        assert depth == 0, f"{path} has unbalanced braces (final depth={depth})"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI checks that run actual repo commands
# ---------------------------------------------------------------------------

def test_repo_prettier_format():
    """Repo code formatting passes Prettier check (pass_to_pass)."""
    # Check formatting on the modified files and session directory
    modified_files = [
        "packages/opencode/src/cli/cmd/tui/component/dialog-model.tsx",
        "packages/opencode/src/cli/cmd/tui/component/dialog-variant.tsx",
        "packages/opencode/src/cli/cmd/tui/routes/session/index.tsx",
    ]
    for file in modified_files:
        r = subprocess.run(
            ["npx", "prettier", "--check", f"{REPO}/{file}"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Prettier check failed for {file}:\n{r.stderr[-500:]}"

    # Also check the entire session directory for consistent formatting
    r = subprocess.run(
        ["npx", "prettier", "--check", f"{REPO}/packages/opencode/src/cli/cmd/tui/routes/session/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed for session directory:\n{r.stderr[-500:]}"


def test_repo_node_syntax_check():
    """Modified TSX files have balanced braces via Node.js parser (pass_to_pass)."""
    # Use Node.js to verify brace balance (same logic as syntax_check but via subprocess)
    r = _run_node("""
import { readFileSync } from 'fs';

const files = [
  'packages/opencode/src/cli/cmd/tui/component/dialog-model.tsx',
  'packages/opencode/src/cli/cmd/tui/component/dialog-variant.tsx',
  'packages/opencode/src/cli/cmd/tui/routes/session/index.tsx',
];

for (const file of files) {
  const code = readFileSync(file, 'utf8');
  let depth = 0;
  for (const ch of code) {
    if (ch === '{') depth++;
    else if (ch === '}') depth--;
    if (depth < 0) {
      console.error(`Unbalanced braces in ${file}: depth went negative`);
      process.exit(1);
    }
  }
  if (depth !== 0) {
    console.error(`Unbalanced braces in ${file}: final depth=${depth}`);
    process.exit(1);
  }
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Node syntax check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_typecheck():
    """Repo typecheck passes via bun turbo typecheck (pass_to_pass)."""
    # Install unzip first (required for bun)
    subprocess.run("apt-get update -qq && apt-get install -y -qq unzip", shell=True, timeout=60)
    
    # Install bun first (not in base image)
    install_bun = subprocess.run(
        "curl -fsSL https://bun.sh/install | bash -s",
        shell=True,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert install_bun.returncode == 0, f"Bun install failed: {install_bun.stderr[-500:]}"

    bun_path = "/root/.bun/bin/bun"
    bun_env = {**os.environ, "BUN_INSTALL": "/root/.bun", "PATH": "/root/.bun/bin:" + os.environ.get("PATH", "")}

    # Install dependencies
    install_deps = subprocess.run(
        [bun_path, "install"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
        env=bun_env,
    )
    assert install_deps.returncode == 0, f"Dependencies install failed: {install_deps.stderr[-500:]}"

    # Run typecheck using bun turbo (matches CI)
    r = subprocess.run(
        [bun_path, "run", "typecheck"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
        env=bun_env,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


def test_repo_bun_unit_tests():
    """Repo unit tests pass via bun test (pass_to_pass)."""
    # Install unzip first (required for bun)
    subprocess.run("apt-get update -qq && apt-get install -y -qq unzip", shell=True, timeout=60)
    
    # Install bun first (not in base image)
    install_bun = subprocess.run(
        "curl -fsSL https://bun.sh/install | bash -s",
        shell=True,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert install_bun.returncode == 0, f"Bun install failed: {install_bun.stderr[-500:]}"

    bun_path = "/root/.bun/bin/bun"
    bun_env = {**os.environ, "BUN_INSTALL": "/root/.bun", "PATH": "/root/.bun/bin:" + os.environ.get("PATH", "")}

    # Install dependencies
    install_deps = subprocess.run(
        [bun_path, "install"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
        env=bun_env,
    )
    assert install_deps.returncode == 0, f"Dependencies install failed: {install_deps.stderr[-500:]}"

    # Run bun tests for the opencode package (matches CI's bun turbo test)
    r = subprocess.run(
        [bun_path, "test", "test/bun.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/packages/opencode",
        env=bun_env,
    )
    assert r.returncode == 0, f"Bun unit tests failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via Node subprocess
# ---------------------------------------------------------------------------

def test_subagent_footer_exists_with_navigation():
    """SubagentFooter exports a component with navigation commands and event handlers."""
    r = _run_node("""
import { readFileSync, existsSync } from 'fs';

const footerPath = '""" + FOOTER + """';
if (!existsSync(footerPath)) {
    console.error('subagent-footer.tsx does not exist');
    process.exit(1);
}

const code = readFileSync(footerPath, 'utf8');

// Must export SubagentFooter
if (!code.includes('export function SubagentFooter') &&
    !code.includes('export default function SubagentFooter') &&
    !code.includes('export const SubagentFooter')) {
    console.error('SubagentFooter not exported');
    process.exit(1);
}

// Must return JSX
if (!code.includes('return (') && !code.includes('return(')) {
    console.error('No JSX return found');
    process.exit(1);
}

// Must have navigation labels for Parent, Prev/Previous, Next
if (!code.includes('Parent')) {
    console.error('Missing Parent navigation label');
    process.exit(1);
}
if (!code.includes('Prev') && !code.includes('Previous')) {
    console.error('Missing Prev/Previous navigation label');
    process.exit(1);
}
if (!code.includes('Next')) {
    console.error('Missing Next navigation label');
    process.exit(1);
}

// Must have mouse event handlers for interactivity
if (!code.includes('onMouseUp') && !code.includes('onClick') &&
    !code.includes('onMouseDown') && !code.includes('onPress')) {
    console.error('No mouse/press event handlers');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_subagent_footer_token_cost():
    """SubagentFooter computes token usage and cost for display."""
    r = _run_node("""
import { readFileSync, existsSync } from 'fs';

const path = '""" + FOOTER + """';
if (!existsSync(path)) {
    console.error('subagent-footer.tsx does not exist');
    process.exit(1);
}

const code = readFileSync(path, 'utf8');

// Must access token properties
if (!code.includes('tokens')) {
    console.error('No tokens reference');
    process.exit(1);
}
if (!code.includes('.input') && !code.includes("['input']")) {
    console.error('No input token access');
    process.exit(1);
}
if (!code.includes('.output') && !code.includes("['output']")) {
    console.error('No output token access');
    process.exit(1);
}

// Must iterate over messages/data for accumulation
if (!code.includes('.reduce') && !code.includes('.forEach') &&
    !code.includes('.map') && !code.includes('.filter') &&
    !code.includes('.find') && !code.includes('.findLast') &&
    !code.includes('for (') && !code.includes('for(')) {
    console.error('No array iteration found');
    process.exit(1);
}

// Must compute cost
if (!code.includes('cost')) {
    console.error('No cost computation');
    process.exit(1);
}

// Must format numbers for display
if (!code.includes('NumberFormat') && !code.includes('toFixed') &&
    !code.includes('Locale') && !code.includes('toLocaleString')) {
    console.error('No number formatting');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_session_imports_and_renders_subagent_footer():
    """Session index.tsx imports and conditionally renders SubagentFooter on parentID."""
    r = _run_node("""
import { readFileSync, existsSync } from 'fs';
import { resolve } from 'path';

const sessionDir = '""" + SESSION_DIR + """';
const indexPath = resolve(sessionDir, 'index.tsx');
const code = readFileSync(indexPath, 'utf8');

// Must reference SubagentFooter
if (!code.includes('SubagentFooter')) {
    console.error('SubagentFooter not referenced in session/index.tsx');
    process.exit(1);
}

// Must have an import statement for it
const lines = code.split('\\n');
const hasImport = lines.some(line =>
    line.includes('import') && line.includes('SubagentFooter') && line.includes('from')
);
if (!hasImport) {
    console.error('No import statement for SubagentFooter');
    process.exit(1);
}

// Import target must resolve to an existing file
const candidates = [
    resolve(sessionDir, 'subagent-footer.tsx'),
    resolve(sessionDir, 'subagent-footer.ts'),
    resolve(sessionDir, 'subagent-footer.js'),
    resolve(sessionDir, 'SubagentFooter.tsx'),
    resolve(sessionDir, 'SubagentFooter.ts'),
];
if (!candidates.some(p => existsSync(p))) {
    console.error('SubagentFooter module file not found in session directory');
    process.exit(1);
}

// Must render <SubagentFooter in JSX
if (!code.includes('<SubagentFooter')) {
    console.error('SubagentFooter not rendered in JSX');
    process.exit(1);
}

// Must be conditional on parentID
if (!code.includes('parentID')) {
    console.error('No parentID condition');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_subagent_footer_title():
    """SubagentFooter displays 'Subagent session' title text."""
    r = _run_node("""
import { readFileSync, existsSync } from 'fs';

const path = '""" + FOOTER + """';
if (!existsSync(path)) {
    console.error('subagent-footer.tsx does not exist');
    process.exit(1);
}

const code = readFileSync(path, 'utf8').toLowerCase();
if (!code.includes('subagent session')) {
    console.error("Missing 'Subagent session' title");
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_dialog_model_no_else():
    """dialog-model.tsx else block replaced with early return."""
    r = _run_node("""
import { readFileSync } from 'fs';

const code = readFileSync('""" + DIALOG_MODEL + """', 'utf8');

// Check non-comment lines for else blocks
const lines = code.split('\\n');
for (let i = 0; i < lines.length; i++) {
    const trimmed = lines[i].trim();
    if (trimmed.startsWith('//') || trimmed.startsWith('*')) continue;
    if (lines[i].includes('} else {')) {
        console.error('Found else block at line ' + (i + 1));
        process.exit(1);
    }
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_dialog_variant_no_unused_import():
    """dialog-variant.tsx unused useSync import removed."""
    r = _run_node("""
import { readFileSync } from 'fs';

const code = readFileSync('""" + DIALOG_VARIANT + """', 'utf8');

// Check import lines for useSync
const lines = code.split('\\n');
for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith('//')) continue;
    if (trimmed.startsWith('import') && line.includes('useSync') && line.includes('from')) {
        console.error('dialog-variant.tsx still imports useSync');
        process.exit(1);
    }
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

def test_dialog_model_export_preserved():
    """DialogModel component is still exported."""
    p = Path(DIALOG_MODEL)
    assert p.exists(), "dialog-model.tsx not found"
    code = p.read_text()
    assert re.search(r"export\s+(default\s+)?function\s+DialogModel", code), \
        "DialogModel export missing"


def test_dialog_variant_export_preserved():
    """DialogVariant component is still exported."""
    p = Path(DIALOG_VARIANT)
    assert p.exists(), "dialog-variant.tsx not found"
    code = p.read_text()
    assert re.search(r"export\s+(default\s+)?function\s+DialogVariant", code), \
        "DialogVariant export missing"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

def test_no_else_blocks_in_modified_files():
    """No else blocks in dialog-model.tsx or subagent-footer.tsx (AGENTS.md:84)."""
    for path in [DIALOG_MODEL, FOOTER]:
        p = Path(path)
        if not p.exists():
            continue
        code = _strip_comments(p.read_text())
        count = code.count("} else {")
        assert count == 0, f"{path} has {count} else blocks (AGENTS.md:84: avoid else)"


def test_no_any_type_in_footer():
    """SubagentFooter must not use the 'any' type (AGENTS.md:13)."""
    p = Path(FOOTER)
    assert p.exists(), "subagent-footer.tsx does not exist"
    code = _strip_comments(p.read_text())
    assert not re.search(r":\s*any\b|as\s+any\b", code), \
        "SubagentFooter uses 'any' type (AGENTS.md:13: avoid any)"


def test_no_try_catch_in_footer():
    """SubagentFooter must not use try/catch (AGENTS.md:12)."""
    p = Path(FOOTER)
    assert p.exists(), "subagent-footer.tsx does not exist"
    code = _strip_comments(p.read_text())
    assert not re.search(r"\btry\s*\{", code), \
        "SubagentFooter uses try/catch (AGENTS.md:12: avoid try/catch)"


def test_no_for_loops_in_footer():
    """SubagentFooter uses functional array methods, not for loops (AGENTS.md:17)."""
    p = Path(FOOTER)
    assert p.exists(), "subagent-footer.tsx does not exist"
    code = _strip_comments(p.read_text())
    assert not re.search(r"\bfor\s*\(", code), \
        "SubagentFooter uses a for loop — prefer functional array methods (AGENTS.md:17)"


def test_prefer_const_in_footer():
    """SubagentFooter should use const, not let (AGENTS.md:70)."""
    p = Path(FOOTER)
    assert p.exists(), "subagent-footer.tsx does not exist"
    code = _strip_comments(p.read_text())
    let_matches = re.findall(r"^\s*(?:export\s+)?let\s+\w+", code, re.MULTILINE)
    assert len(let_matches) == 0, \
        f"SubagentFooter uses 'let' ({len(let_matches)}x) — prefer const (AGENTS.md:70)"

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

def test_ci_build_cli_build():
    """pass_to_pass | CI job 'build-cli' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", './packages/opencode/script/build.ts'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_tauri_verify_certificate():
    """pass_to_pass | CI job 'build-tauri' → step 'Verify Certificate'"""
    r = subprocess.run(
        ["bash", "-lc", 'CERT_INFO=$(security find-identity -v -p codesigning build.keychain | grep "Developer ID Application")\nCERT_ID=$(echo "$CERT_INFO" | awk -F\'"\' \'{print $2}\')\necho "CERT_ID=$CERT_ID" >> $GITHUB_ENV\necho "Certificate imported."'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify Certificate' failed (returncode={r.returncode}):\n"
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

def test_ci_build_electron_build():
    """pass_to_pass | CI job 'build-electron' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run build'], cwd=os.path.join(REPO, 'packages/desktop-electron'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_typecheck_run_typecheck():
    """pass_to_pass | CI job 'typecheck' → step 'Run typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")