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
        ["node", "-e", """
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');
const pattern = /turboFlag:\\s*([^,}\\n]+)/g;
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
        ["node", "-e", """
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');
const pattern = /turboFlag:\\s*([^,}\\n]+)/g;
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
# Pass-to-pass (repo_tests) — CI/CD gates from repo
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_build_file_exists():
    """Build index.ts must exist and be readable."""
    assert BUILD_FILE.exists(), "Build index.ts must exist"
    content = BUILD_FILE.read_text()
    assert len(content) > 0, "Build index.ts must not be empty"
    # Basic check for TypeScript file structure
    assert 'import' in content or 'export' in content, "Build index.ts must be a valid module"


# [repo_tests] pass_to_pass
def test_repo_export_file_exists():
    """Export index.ts must exist and be readable."""
    assert EXPORT_FILE.exists(), "Export index.ts must exist"
    content = EXPORT_FILE.read_text()
    assert len(content) > 0, "Export index.ts must not be empty"
    assert 'import' in content or 'export' in content, "Export index.ts must be a valid module"


# [repo_tests] pass_to_pass
def test_repo_types_file_exists():
    """Export types.ts must exist and be readable."""
    assert TYPES_FILE.exists(), "Export types.ts must exist"
    content = TYPES_FILE.read_text()
    assert len(content) > 0, "Export types.ts must not be empty"
    # Check for type definitions
    assert 'interface' in content or 'type' in content, "Export types.ts must contain type definitions"


# [repo_tests] pass_to_pass
def test_repo_bundler_file_exists():
    """Bundler enum file must exist and be valid."""
    bundler_file = Path(REPO) / "packages/next/src/lib/bundler.ts"
    assert bundler_file.exists(), "bundler.ts file must exist"
    content = bundler_file.read_text()
    assert len(content) > 0, "bundler.ts must not be empty"
    assert 'enum Bundler' in content, "bundler.ts must contain Bundler enum"


# [repo_tests] pass_to_pass
def test_repo_build_imports_resolvable():
    """Build index.ts relative imports must be resolvable."""
    content = BUILD_FILE.read_text()
    # Check for import statements that are relative and verify file existence
    import_pattern = re.compile(r"import\s+.*?\s+from\s+['\"](\.[^'\"]+)['\"]|import\s+['\"](\.[^'\"]+)['\"]")
    for match in import_pattern.finditer(content):
        import_path = match.group(1) or match.group(2)
        if import_path:
            # Resolve relative to the file location
            base_dir = BUILD_FILE.parent
            resolved = base_dir / import_path
            # Check with various extensions
            exists = (
                resolved.exists() or
                (resolved.with_suffix('.ts')).exists() or
                (resolved.with_suffix('.tsx')).exists() or
                (resolved.with_suffix('.js')).exists() or
                (resolved / 'index.ts').exists() or
                (resolved / 'index.js').exists()
            )
            # Only check relative imports, not node_modules
            if not exists and not import_path.startswith('/'):
                # Some imports may be to packages, skip those
                if import_path.startswith('.'):
                    assert False, f"Import '{import_path}' in build/index.ts cannot be resolved"


# [repo_tests] pass_to_pass
def test_repo_export_imports_resolvable():
    """Export index.ts relative imports must be resolvable."""
    content = EXPORT_FILE.read_text()
    import_pattern = re.compile(r"import\s+.*?\s+from\s+['\"](\.[^'\"]+)['\"]|import\s+['\"](\.[^'\"]+)['\"]")
    for match in import_pattern.finditer(content):
        import_path = match.group(1) or match.group(2)
        if import_path:
            base_dir = EXPORT_FILE.parent
            resolved = base_dir / import_path
            exists = (
                resolved.exists() or
                (resolved.with_suffix('.ts')).exists() or
                (resolved.with_suffix('.tsx')).exists() or
                (resolved.with_suffix('.js')).exists() or
                (resolved / 'index.ts').exists() or
                (resolved / 'index.js').exists()
            )
            if not exists and import_path.startswith('.'):
                assert False, f"Import '{import_path}' in export/index.ts cannot be resolved"
