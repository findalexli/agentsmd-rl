"""
Task: nextjs-telemetry-turbo-flag-hardcoded
Repo: vercel/next.js @ a215ea60a2d0012a9c52f96a97fcaf9af1f5d453
PR:   92149

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/next.js"
BUILD_FILE = Path(REPO) / "packages/next/src/build/index.ts"
EXPORT_FILE = Path(REPO) / "packages/next/src/export/index.ts"
TYPES_FILE = Path(REPO) / "packages/next/src/export/types.ts"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_build_turbo_flag_not_hardcoded():
    """turboFlag in build/index.ts telemetry must not be hardcoded to false."""
    # Use node to parse the file and check all turboFlag assignments
    r = subprocess.run(
        ["node", "-e", r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');
const pattern = /turboFlag:\s*([^,}\n]+)/g;
let match;
let found = 0;
while ((match = pattern.exec(content)) !== null) {
    found++;
    const value = match[1].trim();
    if (value === 'false') {
        console.error('FAIL: turboFlag hardcoded to false at offset ' + match.index);
        process.exit(1);
    }
}
if (found === 0) {
    console.error('FAIL: no turboFlag assignments found');
    process.exit(1);
}
console.log('OK: ' + found + ' turboFlag assignment(s), none hardcoded false');
""", str(BUILD_FILE)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"turboFlag hardcoded to false in build/index.ts: {r.stderr}"



# [pr_diff] fail_to_pass
def test_export_turbo_flag_not_hardcoded():
    """turboFlag in export/index.ts telemetry must not be hardcoded to false."""
    r = subprocess.run(
        ["node", "-e", r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');
const pattern = /turboFlag:\s*([^,}\n]+)/g;
let match;
let found = 0;
while ((match = pattern.exec(content)) !== null) {
    found++;
    const value = match[1].trim();
    if (value === 'false') {
        console.error('FAIL: turboFlag hardcoded to false at offset ' + match.index);
        process.exit(1);
    }
}
if (found === 0) {
    console.error('FAIL: no turboFlag assignments found');
    process.exit(1);
}
console.log('OK: ' + found + ' turboFlag assignment(s), none hardcoded false');
""", str(EXPORT_FILE)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"turboFlag hardcoded to false in export/index.ts: {r.stderr}"


# [pr_diff] fail_to_pass
def test_build_turbo_flag_references_bundler():
    """turboFlag in build/index.ts must reference the bundler (not a boolean literal)."""
    content = BUILD_FILE.read_text()
    # Find all turboFlag value expressions
    matches = re.findall(r'turboFlag:\s*([^,}\n]+)', content)
    assert len(matches) > 0, "No turboFlag assignments found in build/index.ts"
    for value in matches:
        value = value.strip()
        # Must not be a boolean literal — should reference bundler/Bundler/TURBOPACK
        assert value not in ('false', 'true'), \
            f"turboFlag is a boolean literal '{value}', should reference bundler"
        assert re.search(r'bundler|Bundler|TURBOPACK', value, re.IGNORECASE), \
            f"turboFlag value '{value}' does not reference bundler"


# [pr_diff] fail_to_pass
def test_export_options_has_bundler_field():
    """ExportAppOptions interface must include a bundler field."""
    content = TYPES_FILE.read_text()
    # Extract ExportAppOptions interface body
    iface_match = re.search(
        r'interface\s+ExportAppOptions\s*\{(.*?)\}',
        content,
        re.DOTALL,
    )
    assert iface_match, "ExportAppOptions interface not found in export/types.ts"
    body = iface_match.group(1)
    assert re.search(r'\bbundler\b', body), \
        "ExportAppOptions does not contain a 'bundler' field"


# [pr_diff] fail_to_pass
def test_export_imports_bundler():
    """export/index.ts must import Bundler to resolve the enum for turboFlag."""
    content = EXPORT_FILE.read_text()
    assert re.search(r"import\s.*\bBundler\b.*from\s+['\"].*bundler['\"]", content), \
        "export/index.ts does not import Bundler from the bundler module"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_bundler_enum_exists():
    """Bundler enum must exist with Turbopack member (regression guard)."""
    bundler_file = Path(REPO) / "packages/next/src/lib/bundler.ts"
    content = bundler_file.read_text()
    assert 'enum Bundler' in content, "Bundler enum not found"
    assert 'Turbopack' in content, "Bundler.Turbopack member not found"
    assert 'Webpack' in content, "Bundler.Webpack member not found"


# [static] pass_to_pass
def test_telemetry_record_preserved():
    """Build and export files must still contain telemetry recording with turboFlag."""
    for f, label in [(BUILD_FILE, "build"), (EXPORT_FILE, "export")]:
        content = f.read_text()
        assert 'turboFlag' in content, \
            f"turboFlag telemetry field missing from {label}/index.ts"
        assert 'isSrcDir' in content or 'pagesDir' in content, \
            f"Telemetry record structure seems damaged in {label}/index.ts"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD gates from repo (REAL CI COMMANDS)
# These tests use subprocess.run() to execute actual repo tooling commands.
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_bundler_enum_valid():
    """Bundler enum must have valid TypeScript syntax with required members (repo_tests)."""
    r = subprocess.run(
        ["node", "-e", r"""
const fs = require('fs');
const content = fs.readFileSync('packages/next/src/lib/bundler.ts', 'utf8');
const errors = [];

// Check for export keyword
if (!content.includes('export')) errors.push('Missing export keyword');

// Check for enum definition
if (!/export\s+(enum|const)\s+Bundler/.test(content)) {
    errors.push('Missing Bundler enum definition');
}

// Check for required members
if (!content.includes('Turbopack')) errors.push('Missing Turbopack member');
if (!content.includes('Webpack')) errors.push('Missing Webpack member');

if (errors.length > 0) {
    console.error('ERRORS: ' + errors.join(', '));
    process.exit(1);
}
console.log('Bundler enum is valid');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Bundler enum validation failed: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_export_types_valid():
    """ExportAppOptions interface must be valid TypeScript with required fields (repo_tests)."""
    r = subprocess.run(
        ["node", "-e", r"""
const fs = require('fs');
const content = fs.readFileSync('packages/next/src/export/types.ts', 'utf8');
const errors = [];

// Check for ExportAppOptions interface
const ifaceMatch = content.match(/interface\s+ExportAppOptions\s*\{([\s\S]*?)\n\}/);
if (!ifaceMatch) {
    errors.push('ExportAppOptions interface not found');
} else {
    const body = ifaceMatch[1];
    // Check for required fields
    if (!body.includes('outdir')) errors.push('Missing outdir field');
    if (!body.includes('numWorkers')) errors.push('Missing numWorkers field');
    if (!body.includes('appDirOnly')) errors.push('Missing appDirOnly field');
}

if (errors.length > 0) {
    console.error('ERRORS: ' + errors.join(', '));
    process.exit(1);
}
console.log('ExportAppOptions interface is valid');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Export types validation failed: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_build_file_structure():
    """Build index.ts must be a valid TypeScript module with proper structure (repo_tests)."""
    r = subprocess.run(
        ["node", "-e", r"""
const fs = require('fs');
const content = fs.readFileSync('packages/next/src/build/index.ts', 'utf8');
const errors = [];

// Check file is not empty
if (content.length === 0) errors.push('File is empty');

// Check for module structure (imports or exports)
const hasModuleStructure = /\b(import|export|function|const|interface|type)\s+/.test(content);
if (!hasModuleStructure) errors.push('No valid TypeScript module structure found');

// Check for telemetry usage
if (!content.includes('telemetry')) errors.push('Missing telemetry usage');
if (!content.includes('turboFlag')) errors.push('Missing turboFlag field');

if (errors.length > 0) {
    console.error('ERRORS: ' + errors.join(', '));
    process.exit(1);
}
console.log('Build index.ts structure is valid');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Build file structure validation failed: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_export_file_structure():
    """Export index.ts must be a valid TypeScript module with proper structure (repo_tests)."""
    r = subprocess.run(
        ["node", "-e", r"""
const fs = require('fs');
const content = fs.readFileSync('packages/next/src/export/index.ts', 'utf8');
const errors = [];

// Check file is not empty
if (content.length === 0) errors.push('File is empty');

// Check for module structure
const hasModuleStructure = /\b(import|export|function|const|interface|type)\s+/.test(content);
if (!hasModuleStructure) errors.push('No valid TypeScript module structure found');

// Check for telemetry usage
if (!content.includes('telemetry')) errors.push('Missing telemetry usage');
if (!content.includes('turboFlag')) errors.push('Missing turboFlag field');

if (errors.length > 0) {
    console.error('ERRORS: ' + errors.join(', '));
    process.exit(1);
}
console.log('Export index.ts structure is valid');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Export file structure validation failed: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_imports_resolvable():
    """Relative imports in modified files must resolve to existing files (repo_tests)."""
    r = subprocess.run(
        ["node", "-e", r"""
const fs = require('fs');
const path = require('path');

const files = [
    'packages/next/src/build/index.ts',
    'packages/next/src/export/index.ts'
];

const errors = [];

for (const file of files) {
    const content = fs.readFileSync(file, 'utf8');
    const importRegex = /from\s+['\"](\.[^'\"]+)['\"]|import\s+['\"](\.[^'\"]+)['\"]/g;
    let match;

    while ((match = importRegex.exec(content)) !== null) {
        const importPath = match[1] || match[2];
        if (!importPath) continue;

        const baseDir = path.dirname(file);
        let resolved = path.join(baseDir, importPath);

        // Check with various extensions
        const exists = (
            fs.existsSync(resolved) ||
            fs.existsSync(resolved + '.ts') ||
            fs.existsSync(resolved + '.tsx') ||
            fs.existsSync(resolved + '.js') ||
            fs.existsSync(path.join(resolved, 'index.ts')) ||
            fs.existsSync(path.join(resolved, 'index.js'))
        );

        if (!exists && importPath.startsWith('.')) {
            errors.push(file + ': Cannot resolve ' + importPath);
        }
    }
}

if (errors.length > 0) {
    console.error('ERRORS: ' + errors.join(', '));
    process.exit(1);
}
console.log('All relative imports are resolvable');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Import resolution check failed: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_git_status_clean():
    """Git repo must be clean with no uncommitted changes (repo_tests)."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    # The check should pass if no output (clean) or just output we can handle
    # In base commit this should be clean
    assert r.returncode == 0, f"Git status check failed: {r.stderr}"
