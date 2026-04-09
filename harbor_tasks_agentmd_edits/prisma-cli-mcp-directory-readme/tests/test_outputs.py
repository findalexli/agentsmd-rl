"""
Task: prisma-cli-mcp-directory-readme
Repo: prisma/prisma @ 057e587d5f31ad2361dfbc66d8c57406a13f86bc
PR:   #27631

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
from pathlib import Path

REPO = "/workspace/prisma"


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


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — MCP module moved + refactored
# ---------------------------------------------------------------------------


def test_mcp_module_at_new_location():
    """MCP.ts exists at packages/cli/src/mcp/MCP.ts and exports the Mcp class."""
    r = _run_node("""
import { readFileSync } from 'fs';

const content = readFileSync('packages/cli/src/mcp/MCP.ts', 'utf8');
if (!content.includes('export class Mcp')) {
    console.error('MCP.ts does not export class Mcp');
    process.exit(1);
}
if (!content.includes('McpServer')) {
    console.error('MCP.ts does not reference McpServer');
    process.exit(1);
}
console.log('OK');
""")
    assert r.returncode == 0, f"MCP.ts not found or invalid at new location: {r.stderr}"


def test_old_mcp_file_removed():
    """Old MCP.ts at packages/cli/src/MCP.ts must not exist after move."""
    r = _run_node("""
import { existsSync } from 'fs';

if (existsSync('packages/cli/src/MCP.ts')) {
    console.error('Old MCP.ts still exists at packages/cli/src/MCP.ts');
    process.exit(1);
}
console.log('OK: old file removed');
""")
    assert r.returncode == 0, f"Old MCP.ts still present: {r.stderr}"


def test_bin_import_targets_mcp_dir():
    """bin.ts imports Mcp from ./mcp/MCP (not the old ./MCP path)."""
    r = _run_node(r"""
import { readFileSync } from 'fs';

const binTs = readFileSync('packages/cli/src/bin.ts', 'utf8');
const match = binTs.match(/import\s*\{[^}]*Mcp[^}]*\}\s*from\s*['"]([^'"]+)['"]/);
if (!match) {
    console.error('No Mcp import found in bin.ts');
    process.exit(1);
}
const importPath = match[1];
if (!importPath.includes('mcp/MCP')) {
    console.error(`Mcp imported from '${importPath}', expected path containing 'mcp/MCP'`);
    process.exit(1);
}
console.log(`OK: import from '${importPath}'`);
""")
    assert r.returncode == 0, f"bin.ts import check failed: {r.stderr}"


def test_pdp_tools_not_registered():
    """PDP tools removed from MCP server registration."""
    r = _run_node(r"""
import { readFileSync } from 'fs';

const content = readFileSync('packages/cli/src/mcp/MCP.ts', 'utf8');
const toolPattern = /server\.tool\(\s*['"]([^'"]+)['"]/g;
const tools = [];
let m;
while ((m = toolPattern.exec(content)) !== null) {
    tools.push(m[1]);
}

const forbidden = ['Prisma-Postgres-account-status', 'Create-Prisma-Postgres-Database', 'Prisma-Login'];
const found = forbidden.filter(t => tools.includes(t));
if (found.length > 0) {
    console.error(`PDP tools still registered: ${found.join(', ')}`);
    process.exit(1);
}
console.log(`OK: registered tools are [${tools.join(', ')}]`);
""")
    assert r.returncode == 0, f"PDP tools check failed: {r.stderr}"


def test_relative_imports_resolve():
    """MCP.ts relative imports resolve to existing files from the new directory."""
    r = _run_node("""
import { readFileSync, existsSync } from 'fs';
import { resolve, dirname } from 'path';

const mcpPath = 'packages/cli/src/mcp/MCP.ts';
const content = readFileSync(mcpPath, 'utf8');
const mcpDir = dirname(resolve(mcpPath));

// Check ../../package.json import
if (!content.includes('../../package.json')) {
    console.error("MCP.ts missing '../../package.json' import");
    process.exit(1);
}
const pkgResolved = resolve(mcpDir, '../../package.json');
if (!existsSync(pkgResolved)) {
    console.error('../../package.json does not resolve: ' + pkgResolved);
    process.exit(1);
}

// Check ../platform/_lib/help import
if (!content.includes('../platform/_lib/help')) {
    console.error("MCP.ts missing '../platform/_lib/help' import");
    process.exit(1);
}
const helpResolved = resolve(mcpDir, '../platform/_lib/help.ts');
if (!existsSync(helpResolved)) {
    console.error('../platform/_lib/help.ts does not resolve: ' + helpResolved);
    process.exit(1);
}

console.log('OK: all imports resolve');
""")
    assert r.returncode == 0, f"Import resolution failed: {r.stderr}"


def test_mcp_keyword_in_package_json():
    """packages/cli/package.json keywords array includes 'MCP'."""
    r = _run_node("""
import { readFileSync } from 'fs';

const pkg = JSON.parse(readFileSync('packages/cli/package.json', 'utf8'));
const keywords = pkg.keywords || [];
if (!keywords.includes('MCP')) {
    console.error('keywords does not include MCP: ' + JSON.stringify(keywords));
    process.exit(1);
}
console.log('OK: MCP in keywords');
""")
    assert r.returncode == 0, f"MCP keyword check failed: {r.stderr}"


def test_mcp_readme_created():
    """README.md in packages/cli/src/mcp/ documents MCP and how to start the server."""
    r = _run_node("""
import { readFileSync } from 'fs';

const readme = readFileSync('packages/cli/src/mcp/README.md', 'utf8');
if (!readme.toLowerCase().includes('mcp') && !readme.toLowerCase().includes('model context protocol')) {
    console.error('README.md does not mention MCP');
    process.exit(1);
}
if (!readme.toLowerCase().includes('prisma')) {
    console.error('README.md does not mention Prisma');
    process.exit(1);
}
console.log('OK');
""")
    assert r.returncode == 0, f"README check failed: {r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass — core MCP tools preserved
# ---------------------------------------------------------------------------


def test_core_tools_preserved():
    """Core MCP tools (migrate-status, migrate-dev, migrate-reset, Prisma-Studio) still registered."""
    r = _run_node(r"""
import { readFileSync, existsSync } from 'fs';

// Find MCP.ts at either location (base or fix)
let mcpPath = 'packages/cli/src/mcp/MCP.ts';
if (!existsSync(mcpPath)) {
    mcpPath = 'packages/cli/src/MCP.ts';
}
const content = readFileSync(mcpPath, 'utf8');
const toolPattern = /server\.tool\(\s*['"]([^'"]+)['"]/g;
const tools = [];
let m;
while ((m = toolPattern.exec(content)) !== null) {
    tools.push(m[1]);
}

const required = ['migrate-status', 'migrate-dev', 'migrate-reset', 'Prisma-Studio'];
const missing = required.filter(t => !tools.includes(t));
if (missing.length > 0) {
    console.error('Core tools missing: ' + missing.join(', ') + '. Found: ' + tools.join(', '));
    process.exit(1);
}
console.log('OK: core tools present [' + tools.join(', ') + ']');
""")
    assert r.returncode == 0, f"Core tools check failed: {r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass — Repo CI/CD checks (verify fix does not break existing functionality)
# ---------------------------------------------------------------------------


def test_repo_check_engines_override():
    """Repo check-engines-override script passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "run", "check-engines-override"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"check-engines-override failed:\n{r.stderr[-500:]}"


def test_repo_prettier_cli():
    """Repo prettier check passes on CLI files (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "prettier", "--check", "packages/cli/src"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


def test_repo_eslint_cli_modified():
    """Repo eslint passes on modified CLI files (pass_to_pass)."""
    # Check MCP.ts at either location (base or fix)
    mcp_path = os.path.join(REPO, "packages/cli/src/mcp/MCP.ts")
    if not os.path.exists(mcp_path):
        mcp_path = os.path.join(REPO, "packages/cli/src/MCP.ts")
    bin_path = os.path.join(REPO, "packages/cli/src/bin.ts")

    r = subprocess.run(
        ["pnpm", "eslint", mcp_path, bin_path],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint check failed:\n{r.stderr[-500:]}"
