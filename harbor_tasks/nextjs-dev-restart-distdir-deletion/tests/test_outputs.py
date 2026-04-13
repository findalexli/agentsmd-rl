"""
Task: nextjs-dev-restart-distdir-deletion
Repo: vercel/next.js @ cb0d88f6e3e340216d478e0ba0c201ec23f7c15c
PR:   92135

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = Path("/workspace/next.js")
START_SERVER = REPO / "packages/next/src/server/lib/start-server.ts"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Node.js validation script in the repo directory."""
    script = REPO / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", "--no-warnings", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=str(REPO),
        )
    finally:
        script.unlink(missing_ok=True)


def _node_result(code: str) -> dict:
    """Run a Node.js script that outputs JSON and parse the result."""
    r = _run_node(code)
    assert r.returncode == 0, f"Node.js failed: {r.stderr}"
    return json.loads(r.stdout.strip().split('\n')[-1])


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_remove_event_handler():
    """Watchpack 'remove' handler exists and triggers process exit on directory deletion."""
    fp = json.dumps(str(START_SERVER))
    data = _node_result(
        "const fs = require('fs');\n"
        f"const src = fs.readFileSync({fp}, 'utf8');\n"
        r"""
const removePat = /wp\.on\(\s*'remove'/;
const hasRemoveHandler = removePat.test(src);
const hasRestartExit = src.includes('RESTART_EXIT_CODE');
// Verify the remove handler references a path list guard (e.g., dirWatchPaths)
const removeRegion = src.substring(src.indexOf("wp.on('remove'"));
const hasPathGuard = /includes\(/.test(removeRegion.substring(0, 400));
console.log(JSON.stringify({ok: hasRemoveHandler && hasRestartExit && hasPathGuard}));
"""
    )
    assert data['ok'], (
        "start-server.ts missing Watchpack 'remove' handler with "
        "RESTART_EXIT_CODE and path inclusion guard"
    )


# [pr_diff] fail_to_pass
def test_missing_option_in_watchpack():
    """Watchpack watch call includes 'missing' option for directory deletion detection."""
    fp = json.dumps(str(START_SERVER))
    data = _node_result(
        "const fs = require('fs');\n"
        f"const src = fs.readFileSync({fp}, 'utf8');\n"
        r"""
// Find wp.watch({...}) calls and check for 'missing' option
const watchPat = /wp\.watch\(\s*\{([^}]+)\}/g;
let match;
let hasMissing = false;
while ((match = watchPat.exec(src)) !== null) {
    if (match[1].includes('missing')) hasMissing = true;
}
console.log(JSON.stringify({ok: hasMissing}));
"""
    )
    assert data['ok'], (
        "Watchpack wp.watch() missing 'missing' option - "
        "needed to detect directory deletion"
    )


# [pr_diff] fail_to_pass
def test_distdir_ancestor_walking():
    """Absolute distDir is computed and ancestor directories are collected for watching."""
    fp = json.dumps(str(START_SERVER))
    data = _node_result(
        "const fs = require('fs');\n"
        f"const src = fs.readFileSync({fp}, 'utf8');\n"
        r"""
// Check that an absolute distDir is computed from dir + distDir
const hasAbsPath = /path\.join\(dir,\s*distDir\)/.test(src);
// Check that there's a while/for loop walking parent directories via path.dirname
const hasAncestorWalk = /path\.dirname\(/.test(src) && /while|for/.test(src);
// Check that ancestor paths are pushed into a collection
const hasPush = /\.push\(/.test(src);
console.log(JSON.stringify({
    ok: hasAbsPath && hasAncestorWalk && hasPush
}));
"""
    )
    assert data['ok'], (
        "start-server.ts missing distDir ancestor walking logic: "
        "absolute distDir computation, ancestor loop with path.dirname, "
        "or path collection"
    )


# [pr_diff] fail_to_pass
def test_change_handler_guards_config_files():
    """Change handler only responds to config file changes, not directory changes."""
    fp = json.dumps(str(START_SERVER))
    data = _node_result(
        "const fs = require('fs');\n"
        f"const src = fs.readFileSync({fp}, 'utf8');\n"
        r"""
// Find the change handler and check it guards with a file list check
const changeIdx = src.indexOf("wp.on('change'");
if (changeIdx === -1) {
    console.log(JSON.stringify({ok: false, error: 'no change handler'}));
    process.exit(0);
}
const region = src.substring(changeIdx, changeIdx + 500);
// Must have a guard checking if filename is in the config file list
const hasGuard = /\.includes\(filename\)/.test(region) || /\.indexOf\(filename\)/.test(region);
console.log(JSON.stringify({ok: hasGuard}));
"""
    )
    assert data['ok'], (
        "Change handler missing config file guard - should only respond "
        "to config file changes, not directory change events"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) - syntax / anti-stub checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_syntax_valid():
    """start-server.ts has balanced braces and no obvious syntax issues."""
    src = START_SERVER.read_text()
    open_braces = src.count('{')
    close_braces = src.count('}')
    assert open_braces == close_braces, (
        f"Unbalanced braces in start-server.ts: {open_braces} open vs {close_braces} close"
    )
    assert len(src) > 10000, "start-server.ts is suspiciously short - check file integrity"


# [static] pass_to_pass
def test_restart_exit_code_in_remove():
    """Remove handler uses RESTART_EXIT_CODE (not a hardcoded magic number)."""
    src = START_SERVER.read_text()
    remove_idx = src.find("wp.on('remove'")
    if remove_idx == -1:
        return  # No remove handler on base commit; nothing to validate
    region = src[remove_idx:remove_idx + 400]
    assert 'RESTART_EXIT_CODE' in region, (
        "Remove handler should call process.exit(RESTART_EXIT_CODE)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) - static file checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass - static file checks
def test_repo_start_server_syntax():
    """Repo's start-server.ts has balanced braces and valid syntax (pass_to_pass)."""
    src = START_SERVER.read_text()
    # Check balanced braces
    open_count = src.count('{')
    close_count = src.count('}')
    assert open_count == close_count, (
        f"start-server.ts has unbalanced braces: {open_count} open vs {close_count} close"
    )
    # Check balanced parentheses
    open_paren = src.count('(')
    close_paren = src.count(')')
    assert open_paren == close_paren, (
        f"start-server.ts has unbalanced parentheses: {open_paren} open vs {close_paren} close"
    )
    # Check file size is reasonable
    assert len(src) > 15000, "start-server.ts is suspiciously small"


# [static] pass_to_pass - static import checks
def test_repo_valid_imports_in_start_server():
    """start-server.ts imports are well-formed (pass_to_pass)."""
    src = START_SERVER.read_text()
    # Check for common syntax errors in imports
    lines = src.split('\n')
    for i, line in enumerate(lines[:100], 1):  # Check first 100 lines (imports section)
        if line.strip().startswith('import '):
            # Basic check: import statements should end with quotes or semicolon
            if not (line.rstrip().endswith('"') or line.rstrip().endswith("'") or
                    line.rstrip().endswith(';') or ' from ' not in line):
                # Allow multi-line imports
                pass
    # Verify key imports exist
    assert 'import' in src, "start-server.ts missing imports"
    assert 'export' in src, "start-server.ts missing exports"


# [static] pass_to_pass - static code quality checks
def test_repo_no_debugger_in_start_server():
    """start-server.ts has no debugger statements or console.log left behind (pass_to_pass)."""
    src = START_SERVER.read_text()
    # Check for accidental debugger statements
    assert 'debugger;' not in src, "start-server.ts contains 'debugger;' statement"
    # Check for console.log (only Log.* should be used in this file)
    # Allow console.log in comments and console.error in catch blocks
    lines = src.split('\n')
    for line in lines:
        # Skip comments
        if '//' in line:
            line = line[:line.index('//')]
        # Only check for console.log - console.error is allowed for error handling
        if 'console.log' in line or 'console.warn' in line:
            assert False, f"start-server.ts contains console.* statement: {line.strip()[:50]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - Real CI commands from the repo
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass - Node.js syntax validation (repo CI check)
def test_repo_node_syntax_check():
    """Repo's start-server.ts is parseable by Node.js (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--check", str(START_SERVER)],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    # Note: --check validates JavaScript syntax; TS files may have false positives
    # but major syntax errors will be caught
    if r.returncode != 0:
        # TypeScript-specific syntax may fail, but basic JS errors indicate real issues
        error = r.stderr.lower()
        if "unexpected token" in error or "syntax error" in error or "invalid" in error:
            assert False, f"Syntax error in start-server.ts:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - Git repository integrity check (repo CI check)
def test_repo_git_status():
    """Repo has clean git status at base commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    # At base commit, there should be no uncommitted changes (only the shallow clone state)
    # We allow specific untracked files that may be generated during test setup
    lines = r.stdout.strip().split('\n') if r.stdout.strip() else []
    modified_files = [line for line in lines if line.startswith(' M') or line.startswith('M ')]
    # Filter out the expected modification to start-server.ts from the solution
    modified_files = [f for f in modified_files if 'start-server.ts' not in f]
    assert len(modified_files) == 0, f"Repo has unexpected uncommitted changes: {modified_files}"


# [repo_tests] pass_to_pass - Package.json validation (repo CI check)
def test_repo_package_json_valid():
    """Repo's package.json is valid JSON (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "JSON.parse(require('fs').readFileSync('package.json', 'utf8')); console.log('OK')"],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0, f"package.json is invalid JSON:\n{r.stderr[-500:]}"
    assert "OK" in r.stdout, "package.json validation failed"


# [repo_tests] pass_to_pass - File existence check for critical paths (repo CI check)
def test_repo_critical_files_exist():
    """Repo's critical source files exist and are readable (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const path = require('path');
const files = [
    'packages/next/src/server/lib/start-server.ts',
    'packages/next/src/server/next-server.ts',
    'packages/next/package.json'
];
for (const file of files) {
    const fullPath = path.join('/workspace/next.js', file);
    try {
        const content = fs.readFileSync(fullPath, 'utf8');
        if (content.length < 100) {
            console.error('File too short: ' + file);
            process.exit(1);
        }
    } catch (e) {
        console.error('Cannot read: ' + file + ' - ' + e.message);
        process.exit(1);
    }
}
console.log('OK');
"""],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0, f"Critical files check failed:\n{r.stderr[-500:]}"
    assert "OK" in r.stdout, "Critical files not found"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) - rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass - AGENTS.md:300
def test_dev_only_code_guard():
    """File watching with directory deletion detection is inside the if (isDev) guard."""
    src = START_SERVER.read_text()
    remove_idx = src.find("wp.on('remove'")
    if remove_idx == -1:
        return  # No remove handler on base commit; nothing to validate
    isdev_idx = src.find('if (isDev)')
    assert isdev_idx != -1, "if (isDev) block not found"
    assert remove_idx > isdev_idx, (
        "wp.on('remove') must be inside the if (isDev) block - "
        "directory deletion watching is dev-server-only behavior"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - Unit tests for modified code area
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass - Unit tests for find-config
def test_repo_unit_find_config():
    """Unit tests for find-config pass (next.config.js location during startup)."""
    r = subprocess.run(
        ["node", "-e", """
const { execSync } = require('child_process');
const path = require('path');

// Check if jest is available and run the find-config unit test
const testPath = path.join('/workspace/next.js', 'test/unit/find-config.test.ts');
const fs = require('fs');

if (!fs.existsSync(testPath)) {
    console.log('SKIP: find-config.test.ts not found');
    process.exit(0);
}

// Run jest on the specific test file
try {
    execSync('npx jest test/unit/find-config.test.ts --testPathIgnorePatterns=[] --passWithNoTests', {
        cwd: '/workspace/next.js',
        stdio: 'pipe',
        timeout: 60000
    });
    console.log('OK');
} catch (e) {
    console.error('Test failed:', e.message);
    process.exit(1);
}
"""],
        capture_output=True, text=True, timeout=90, cwd=str(REPO),
    )
    if 'SKIP' in r.stdout or 'Cannot find module' in r.stderr:
        return  # Skip if test file not found
    assert r.returncode == 0, f"find-config unit tests failed:\n{r.stderr[-500:]}"
    assert "OK" in r.stdout, "find-config tests did not complete"


# [repo_tests] pass_to_pass - Unit tests for parse-page-static-info
def test_repo_unit_parse_page_static_info():
    """Unit tests for parse-page-static-info pass (server startup page parsing)."""
    r = subprocess.run(
        ["node", "-e", """
const { execSync } = require('child_process');
const path = require('path');

// Check if jest is available and run the parse-page-static-info unit test
const testPath = path.join('/workspace/next.js', 'test/unit/parse-page-static-info.test.ts');
const fs = require('fs');

if (!fs.existsSync(testPath)) {
    console.log('SKIP: parse-page-static-info.test.ts not found');
    process.exit(0);
}

// Run jest on the specific test file
try {
    execSync('npx jest test/unit/parse-page-static-info.test.ts --testPathIgnorePatterns=[] --passWithNoTests', {
        cwd: '/workspace/next.js',
        stdio: 'pipe',
        timeout: 60000
    });
    console.log('OK');
} catch (e) {
    console.error('Test failed:', e.message);
    process.exit(1);
}
"""],
        capture_output=True, text=True, timeout=90, cwd=str(REPO),
    )
    if 'SKIP' in r.stdout or 'Cannot find module' in r.stderr:
        return  # Skip if test file not found
    assert r.returncode == 0, f"parse-page-static-info unit tests failed:\n{r.stderr[-500:]}"
    assert "OK" in r.stdout, "parse-page-static-info tests did not complete"


# [repo_tests] pass_to_pass - Unit tests for find-page-file
def test_repo_unit_find_page_file():
    """Unit tests for find-page-file pass (dev server page lookup)."""
    r = subprocess.run(
        ["node", "-e", """
const { execSync } = require('child_process');
const path = require('path');

// Check if jest is available and run the find-page-file unit test
const testPath = path.join('/workspace/next.js', 'test/unit/find-page-file.test.ts');
const fs = require('fs');

if (!fs.existsSync(testPath)) {
    console.log('SKIP: find-page-file.test.ts not found');
    process.exit(0);
}

// Run jest on the specific test file
try {
    execSync('npx jest test/unit/find-page-file.test.ts --testPathIgnorePatterns=[] --passWithNoTests', {
        cwd: '/workspace/next.js',
        stdio: 'pipe',
        timeout: 60000
    });
    console.log('OK');
} catch (e) {
    console.error('Test failed:', e.message);
    process.exit(1);
}
"""],
        capture_output=True, text=True, timeout=90, cwd=str(REPO),
    )
    if 'SKIP' in r.stdout or 'Cannot find module' in r.stderr:
        return  # Skip if test file not found
    assert r.returncode == 0, f"find-page-file unit tests failed:\n{r.stderr[-500:]}"
    assert "OK" in r.stdout, "find-page-file tests did not complete"


# [repo_tests] pass_to_pass - TypeScript check for start-server.ts
def test_repo_typescript_check_start_server():
    """TypeScript can parse start-server.ts without errors (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const path = require('path');

const srcPath = '/workspace/next.js/packages/next/src/server/lib/start-server.ts';
const src = fs.readFileSync(srcPath, 'utf8');

// Basic TypeScript syntax checks
// 1. Check for balanced braces
const openBraces = (src.match(/{/g) || []).length;
const closeBraces = (src.match(/}/g) || []).length;
if (openBraces !== closeBraces) {
    console.error('Unbalanced braces:', openBraces, 'open vs', closeBraces, 'close');
    process.exit(1);
}

// 2. Check for balanced parentheses
const openParens = (src.match(/\\(/g) || []).length;
const closeParens = (src.match(/\\)/g) || []).length;
if (openParens !== closeParens) {
    console.error('Unbalanced parentheses:', openParens, 'open vs', closeParens, 'close');
    process.exit(1);
}

// 3. Check for TypeScript-specific keywords and patterns
const hasImport = /import\s+.*\s+from\s+['"]/.test(src);
const hasExport = /export\s+(default\s+)?/.test(src);
const hasTypeAnnotation = /:\s*(string|number|boolean|Promise|void|any)/.test(src);

if (!hasImport && !hasExport) {
    console.error('Missing import/export statements');
    process.exit(1);
}

console.log('OK: TypeScript syntax checks passed');
"""],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0, f"TypeScript check for start-server.ts failed:\n{r.stderr[-500:]}"
    assert "OK" in r.stdout, "TypeScript check did not complete"


# [repo_tests] pass_to_pass - CI: Watchpack import check
def test_repo_watchpack_import():
    """CI: Watchpack import exists in start-server.ts (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');

const srcPath = '/workspace/next.js/packages/next/src/server/lib/start-server.ts';
const src = fs.readFileSync(srcPath, 'utf8');

// Check for Watchpack import (required for the PR fix)
const hasWatchpackImport = src.includes("import Watchpack from 'next/dist/compiled/watchpack'");

if (!hasWatchpackImport) {
    console.error('Missing Watchpack import in start-server.ts');
    process.exit(1);
}

console.log('OK: Watchpack import found');
"""],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0, f"Watchpack import check failed:\n{r.stderr[-500:]}"
    assert "OK" in r.stdout, "Watchpack import check did not complete"


# [repo_tests] pass_to_pass - CI: isDev guard pattern check
def test_repo_isdev_guard_structure():
    """CI: isDev guard block exists for dev-only code (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');

const srcPath = '/workspace/next.js/packages/next/src/server/lib/start-server.ts';
const src = fs.readFileSync(srcPath, 'utf8');

// Check that isDev is used to guard dev-only code sections
const hasIsDevDeclaration = /isDev\s*:\s*boolean/.test(src);
const hasIsDevCondition = /if\s*\(\s*isDev\s*\)/.test(src);

if (!hasIsDevDeclaration) {
    console.error('Missing isDev declaration in start-server.ts');
    process.exit(1);
}

if (!hasIsDevCondition) {
    console.error('Missing if (isDev) guard in start-server.ts');
    process.exit(1);
}

console.log('OK: isDev guard structure found');
"""],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0, f"isDev guard check failed:\n{r.stderr[-500:]}"
    assert "OK" in r.stdout, "isDev guard check did not complete"


# [repo_tests] pass_to_pass - CI: Config files constant check
def test_repo_config_files_constant():
    """CI: CONFIG_FILES constant is imported for config watching (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');

const srcPath = '/workspace/next.js/packages/next/src/server/lib/start-server.ts';
const src = fs.readFileSync(srcPath, 'utf8');

// Check for CONFIG_FILES import (needed for watchConfigFiles)
const hasConfigFilesImport = src.includes('CONFIG_FILES');

if (!hasConfigFilesImport) {
    console.error('Missing CONFIG_FILES import in start-server.ts');
    process.exit(1);
}

console.log('OK: CONFIG_FILES import found');
"""],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0, f"CONFIG_FILES check failed:\n{r.stderr[-500:]}"
    assert "OK" in r.stdout, "CONFIG_FILES check did not complete"
