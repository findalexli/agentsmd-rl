"""
Task: trigger.dev-remove-triggerandpoll-function
Repo: triggerdotdev/trigger.dev @ 21c2c136beec90c28ec46c895561f5b3c258ec06
PR:   2379

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/trigger.dev"


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["node", "-e", script],
        cwd=REPO, capture_output=True, text=True, timeout=timeout,
    )


def _run_node_with_imports(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js script that can import from the SDK."""
    return subprocess.run(
        ["node", "--experimental-strip-types", "-e", script],
        cwd=REPO, capture_output=True, text=True, timeout=timeout,
    )


# [static] pass_to_pass
def test_typescript_syntax_valid():
    """Modified TypeScript files must have valid syntax (pass_to_pass)."""
    files_to_check = [
        "packages/trigger-sdk/src/v3/shared.ts",
        "packages/trigger-sdk/src/v3/tasks.ts",
        "references/v3-catalog/src/trigger/sdkUsage.ts",
    ]
    for rel_path in files_to_check:
        full_path = Path(REPO) / rel_path
        result = subprocess.run(
            ["node", "--experimental-strip-types", "--check", str(full_path)],
            cwd=REPO, capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"{rel_path} has syntax errors: {result.stderr}"


# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must exist and contain expected structural markers."""
    shared = Path(REPO) / "packages" / "trigger-sdk" / "src" / "v3" / "shared.ts"
    tasks_ts = Path(REPO) / "packages" / "trigger-sdk" / "src" / "v3" / "tasks.ts"
    sdk_usage = Path(REPO) / "references" / "v3-catalog" / "src" / "trigger" / "sdkUsage.ts"
    for f in [shared, tasks_ts, sdk_usage]:
        content = f.read_text()
        assert len(content) > 100, f"{f.name} is unexpectedly small or empty"
        assert "import" in content, f"{f.name} missing import statements"


# [static] pass_to_pass
def test_other_task_methods_preserved():
    """tasks object must still export trigger, batchTrigger, triggerAndWait, batchTriggerAndWait."""
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('packages/trigger-sdk/src/v3/tasks.ts', 'utf8');
const match = content.match(/export\\s+const\\s+tasks\\s*=\\s*\\{([\\s\\S]*?)\\}\\s*(?:as|;)/);
if (!match) { console.error('tasks export not found'); process.exit(1); }
const block = match[1];
const required = ['trigger', 'batchTrigger', 'triggerAndWait', 'batchTriggerAndWait'];
const missing = required.filter(m => !new RegExp('\\\\b' + m + '\\\\b').test(block));
if (missing.length > 0) {
    console.error('Missing methods: ' + missing.join(', '));
    process.exit(1);
}
console.log('All required methods present');
""")
    assert r.returncode == 0, f"tasks object missing required methods: {r.stderr}"


# [static] pass_to_pass
def test_repo_imports_check():
    """Import statements in modified files have balanced braces (pass_to_pass)."""
    r = _run_node("""
const fs = require('fs');
const files = [
    'packages/trigger-sdk/src/v3/shared.ts',
    'packages/trigger-sdk/src/v3/tasks.ts',
    'references/v3-catalog/src/trigger/sdkUsage.ts',
];
let ok = true;
for (const f of files) {
    const content = fs.readFileSync(f, 'utf8');
    const imports = content.match(/import\\s*\\{[^}]*\\}\\s*from/g) || [];
    for (const imp of imports) {
        const opens = (imp.match(/\\{/g) || []).length;
        const closes = (imp.match(/\\}/g) || []).length;
        if (opens !== closes) {
            console.error('Unbalanced braces in ' + f + ': ' + imp);
            ok = false;
        }
    }
}
if (!ok) process.exit(1);
console.log('All imports balanced');
""")
    assert r.returncode == 0, f"Import brace balance check failed: {r.stderr}"


# [pr_diff] fail_to_pass
def test_triggerandpoll_function_removed():
    """triggerAndPoll function definition must be removed from shared.ts.

    Behavioral check: Use Node.js to parse the file and verify no exported
    function named triggerAndPoll exists.
    """
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('packages/trigger-sdk/src/v3/shared.ts', 'utf8');

// Find all exported function declarations
const regex = /export\\s+(?:async\\s+)?function\\s+(\\w+)/g;
const exportedFunctions = [];
let m;
while ((m = regex.exec(content)) !== null) {
    exportedFunctions.push(m[1]);
}

if (exportedFunctions.includes('triggerAndPoll')) {
    console.error('FAIL: triggerAndPoll is still an exported function in shared.ts');
    console.error('Exported functions: ' + exportedFunctions.join(', '));
    process.exit(1);
}
console.log('OK: triggerAndPoll function removed from shared.ts');
console.log('Remaining exports: ' + exportedFunctions.join(', '));
""")
    assert r.returncode == 0, f"triggerAndPoll still exported from shared.ts: {r.stderr}"


# [pr_diff] fail_to_pass
def test_triggerandpoll_not_exported():
    """triggerAndPoll must not appear in the tasks export object in tasks.ts.

    Behavioral check: Use Node.js to parse the tasks object literal and
    enumerate its property keys, verifying triggerAndPoll is absent.
    """
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('packages/trigger-sdk/src/v3/tasks.ts', 'utf8');

// Parse the export const tasks = { ... } object
const match = content.match(/export\\s+const\\s+tasks\\s*=\\s*\\{([\\s\\S]*?)\\}\\s*(?:as|;)/);
if (!match) {
    console.error('FAIL: Could not find export const tasks = { ... }');
    process.exit(1);
}

// Extract property keys from the object literal
const block = match[1];
const lines = block.split('\\n')
    .map(line => line.replace(/\\/\\*.*?\\*\\//g, '').trim())
    .filter(line => line && !line.startsWith('//') && !line.startsWith('/*') && !line.startsWith('*'));

const keys = lines.map(line => {
    const km = line.match(/^(\\w+)/);
    return km ? km[1] : null;
}).filter(Boolean);

if (keys.includes('triggerAndPoll')) {
    console.error('FAIL: triggerAndPoll is still in the tasks export object');
    console.error('Keys: ' + keys.join(', '));
    process.exit(1);
}
console.log('OK: triggerAndPoll not in tasks export object');
console.log('Keys: ' + keys.join(', '));
""")
    assert r.returncode == 0, f"triggerAndPoll still in tasks export: {r.stderr}"


# [pr_diff] fail_to_pass
def test_triggerandpoll_not_imported():
    """triggerAndPoll must not be imported from shared.js in tasks.ts.

    Behavioral check: Use Node.js to parse the import declaration and
    enumerate imported identifiers.
    """
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('packages/trigger-sdk/src/v3/tasks.ts', 'utf8');

// Parse import { ... } from "./shared.js"
const match = content.match(/import\\s*\\{([\\s\\S]*?)\\}\\s*from\\s*["']\\.\\/(shared\\.js|shared)["']/);
if (!match) {
    console.error('FAIL: Could not find import from shared.js in tasks.ts');
    process.exit(1);
}

const imports = match[1].split(',')
    .map(s => s.trim())
    .filter(Boolean)
    .map(s => s.split(/\\s/)[0]);  // handle "as" renames

if (imports.includes('triggerAndPoll')) {
    console.error('FAIL: triggerAndPoll is still imported from shared.js');
    console.error('Imports: ' + imports.join(', '));
    process.exit(1);
}
console.log('OK: triggerAndPoll not imported from shared.js');
console.log('Imports: ' + imports.join(', '));
""")
    assert r.returncode == 0, f"triggerAndPoll still imported in tasks.ts: {r.stderr}"


# [pr_diff] fail_to_pass
def test_sdk_usage_no_triggerandpoll():
    """Reference catalog sdkUsage.ts must not call tasks.triggerAndPoll.

    Behavioral check: Use Node.js to parse the file and check for any
    property access or call to triggerAndPoll.
    """
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('references/v3-catalog/src/trigger/sdkUsage.ts', 'utf8');

// Check for any method call or property access to triggerAndPoll
if (/triggerAndPoll/.test(content)) {
    console.error('FAIL: sdkUsage.ts still references triggerAndPoll');
    const lines = content.split('\\n');
    lines.forEach((line, i) => {
        if (/triggerAndPoll/.test(line)) console.error('  Line ' + (i+1) + ': ' + line.trim());
    });
    process.exit(1);
}
console.log('OK: sdkUsage.ts does not reference triggerAndPoll');
""")
    assert r.returncode == 0, f"sdkUsage.ts still uses triggerAndPoll: {r.stderr}"


# [pr_diff] fail_to_pass
def test_cursor_rules_no_triggerandpoll():
    """.cursor/rules writing-tasks.mdc must not document triggerAndPoll.

    Behavioral check: Use Node.js to read and scan the documentation file
    for any reference to the removed API.
    """
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('.cursor/rules/writing-tasks.mdc', 'utf8');

if (/triggerAndPoll/.test(content)) {
    console.error('FAIL: writing-tasks.mdc still documents triggerAndPoll');
    const lines = content.split('\\n');
    lines.forEach((line, i) => {
        if (/triggerAndPoll/.test(line)) {
            console.error('  Line ' + (i+1) + ': ' + line.trim());
        }
    });
    process.exit(1);
}
console.log('OK: writing-tasks.mdc does not mention triggerAndPoll');
""")
    assert r.returncode == 0, f".cursor/rules/writing-tasks.mdc still documents triggerAndPoll: {r.stderr}"


# [pr_diff] fail_to_pass
def test_docs_triggering_no_triggerandpoll():
    """docs/triggering.mdx must not document triggerAndPoll.

    Behavioral check: Use Node.js to parse the documentation file and verify
    no reference to the removed API exists.
    """
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('docs/triggering.mdx', 'utf8');

if (/triggerAndPoll/.test(content)) {
    console.error('FAIL: docs/triggering.mdx still references triggerAndPoll');
    const lines = content.split('\\n');
    lines.forEach((line, i) => {
        if (/triggerAndPoll/.test(line)) {
            console.error('  Line ' + (i+1) + ': ' + line.trim());
        }
    });
    process.exit(1);
}
console.log('OK: docs/triggering.mdx does not reference triggerAndPoll');
""")
    assert r.returncode == 0, f"docs/triggering.mdx still references triggerAndPoll: {r.stderr}"


# [pr_diff] fail_to_pass
def test_docs_triggering_table_updated():
    """The function summary table in docs/triggering.mdx must not list triggerAndPoll.

    Behavioral check: Use Node.js to parse the markdown table structure and
    verify it contains expected methods but not triggerAndPoll.
    """
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('docs/triggering.mdx', 'utf8');

// Parse markdown tables: find all rows with | delimiters
const tableRows = content.split('\\n').filter(line => /^\\|.*\\|$/.test(line.trim()));

if (tableRows.length === 0) {
    console.error('FAIL: No markdown table found in docs/triggering.mdx');
    process.exit(1);
}

// Check that expected methods are still in the table
const tableContent = tableRows.join('\\n');
const requiredMethods = ['tasks.trigger()', 'batch.trigger()'];
for (const method of requiredMethods) {
    if (!tableContent.includes(method)) {
        console.error('FAIL: Table should still list ' + method);
        process.exit(1);
    }
}

// Check that triggerAndPoll is NOT in any table row
for (const row of tableRows) {
    if (/triggerAndPoll/i.test(row)) {
        console.error('FAIL: Table still lists triggerAndPoll: ' + row.trim());
        process.exit(1);
    }
}

// Verify table row structure (each function row should have >= 3 columns)
const funcRows = tableRows.filter(r =>
    r.includes('tasks.trigger()') || r.includes('batch.trigger()')
);
for (const row of funcRows) {
    const colCount = row.split('|').length - 2;
    if (colCount < 3) {
        console.error('FAIL: Table row has insufficient columns: ' + row);
        process.exit(1);
    }
}

console.log('OK: Table updated correctly, triggerAndPoll removed');
""")
    assert r.returncode == 0, f"docs/triggering.mdx table not updated correctly: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_prettier_check():
    """Modified TypeScript files pass Prettier formatting check (pass_to_pass)."""
    files_to_check = [
        "packages/trigger-sdk/src/v3/shared.ts",
        "packages/trigger-sdk/src/v3/tasks.ts",
        "references/v3-catalog/src/trigger/sdkUsage.ts",
    ]
    cmd = ["npx", "--yes", "prettier@3.0.0", "--check"] + files_to_check
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, "Prettier check failed"


# [repo_tests] pass_to_pass
def test_repo_ts_node_syntax():
    """Repo's modified TypeScript files pass Node.js syntax check (pass_to_pass)."""
    files_to_check = [
        "packages/trigger-sdk/src/v3/shared.ts",
        "packages/trigger-sdk/src/v3/tasks.ts",
        "references/v3-catalog/src/trigger/sdkUsage.ts",
    ]
    for rel_path in files_to_check:
        full_path = Path(REPO) / rel_path
        result = subprocess.run(
            ["node", "--experimental-strip-types", "--check", str(full_path)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert result.returncode == 0, f"Syntax error in {rel_path}"


# [repo_tests] pass_to_pass
def test_repo_package_json_node_valid():
    """Repo's package.json files are valid JSON per Node.js (pass_to_pass)."""
    files_to_check = [
        "packages/trigger-sdk/package.json",
        "references/v3-catalog/package.json",
    ]
    for rel_path in files_to_check:
        full_path = Path(REPO) / rel_path
        script = f"JSON.parse(require('fs').readFileSync('{full_path}', 'utf8'))"
        result = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
        assert result.returncode == 0, f"Invalid JSON in {rel_path}"


# [repo_tests] pass_to_pass
def test_repo_tsconfig_valid():
    """Repo's tsconfig files are valid JSON per Node.js (pass_to_pass)."""
    files_to_check = [
        "packages/trigger-sdk/tsconfig.json",
        "packages/trigger-sdk/tsconfig.build.json",
    ]
    for rel_path in files_to_check:
        full_path = Path(REPO) / rel_path
        script = f"JSON.parse(require('fs').readFileSync('{full_path}', 'utf8'))"
        result = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
        assert result.returncode == 0, f"Invalid tsconfig in {rel_path}"


# [repo_tests] pass_to_pass
def test_repo_node_syntax_files():
    """Repo's modified TypeScript files have valid Node.js syntax (pass_to_pass)."""
    files_to_check = [
        "packages/trigger-sdk/src/v3/shared.ts",
        "packages/trigger-sdk/src/v3/tasks.ts",
        "references/v3-catalog/src/trigger/sdkUsage.ts",
    ]
    for rel_path in files_to_check:
        full_path = Path(REPO) / rel_path
        result = subprocess.run(["node", "--check", str(full_path)], capture_output=True, text=True, timeout=30, cwd=REPO)
        assert result.returncode == 0, f"Node.js syntax error in {rel_path}"


# [repo_tests] pass_to_pass
def test_repo_markdown_valid():
    """Repo's markdown and mdc files are readable via Node.js (pass_to_pass)."""
    files_to_check = [
        "docs/triggering.mdx",
        ".cursor/rules/writing-tasks.mdc",
    ]
    for rel_path in files_to_check:
        full_path = Path(REPO) / rel_path
        script = f"require('fs').readFileSync('{full_path}', 'utf8')"
        result = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
        assert result.returncode == 0, f"Cannot read {rel_path}"


# [repo_tests] pass_to_pass
def test_repo_prettier_list_different():
    """Modified files pass Prettier --list-different check (pass_to_pass)."""
    files_to_check = [
        "packages/trigger-sdk/src/v3/shared.ts",
        "packages/trigger-sdk/src/v3/tasks.ts",
        "references/v3-catalog/src/trigger/sdkUsage.ts",
    ]
    cmd = ["npx", "--yes", "prettier@3.0.0", "--list-different"] + files_to_check
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=REPO)
    assert result.returncode == 0, f"Prettier check failed: {result.stdout}{result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_json_parse_validation():
    """Repo's package.json files parse correctly as JSON (pass_to_pass)."""
    files_to_check = [
        "packages/trigger-sdk/package.json",
        "references/v3-catalog/package.json",
    ]
    for rel_path in files_to_check:
        full_path = Path(REPO) / rel_path
        script = f"JSON.stringify(JSON.parse(require('fs').readFileSync('{full_path}', 'utf8')))"
        result = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
        assert result.returncode == 0, f"Invalid JSON in {rel_path}: {result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_turbo_json_valid():
    """Repo's turbo.json is valid JSON (pass_to_pass)."""
    full_path = Path(REPO) / "turbo.json"
    script = f"JSON.parse(require('fs').readFileSync('{full_path}', 'utf8'))"
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
    assert result.returncode == 0, f"Invalid turbo.json: {result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_pnpm_workspace_valid():
    """Repo's pnpm-workspace.yaml is valid YAML (pass_to_pass)."""
    full_path = Path(REPO) / "pnpm-workspace.yaml"
    script = f"const c = require('fs').readFileSync('{full_path}', 'utf8'); if (!c.includes('packages:')) {{ process.exit(1); }} console.log('valid');"
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
    assert result.returncode == 0, f"pnpm-workspace.yaml invalid: {result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_root_package_valid():
    """Repo's root package.json is valid JSON (pass_to_pass)."""
    full_path = Path(REPO) / "package.json"
    script = f"JSON.parse(require('fs').readFileSync('{full_path}', 'utf8'))"
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
    assert result.returncode == 0, f"Invalid root package.json: {result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_prettier_config_valid():
    """Repo's prettier config is valid JavaScript (pass_to_pass)."""
    full_path = Path(REPO) / "prettier.config.js"
    result = subprocess.run(
        ["node", "--check", str(full_path)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"prettier.config.js has syntax errors: {result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_trigger_sdk_tsconfig_valid():
    """SDK tsconfig files are valid JSON (pass_to_pass)."""
    files_to_check = [
        "packages/trigger-sdk/tsconfig.json",
        "packages/trigger-sdk/tsconfig.build.json",
    ]
    for rel_path in files_to_check:
        full_path = Path(REPO) / rel_path
        script = f"JSON.parse(require('fs').readFileSync('{full_path}', 'utf8'))"
        result = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
        assert result.returncode == 0, f"Invalid tsconfig: {rel_path}: {result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_sdk_node_syntax():
    """SDK TypeScript files have valid Node.js 22 syntax (pass_to_pass)."""
    files_to_check = [
        "packages/trigger-sdk/src/v3/shared.ts",
        "packages/trigger-sdk/src/v3/tasks.ts",
    ]
    for rel_path in files_to_check:
        full_path = Path(REPO) / rel_path
        result = subprocess.run(
            ["node", "--experimental-strip-types", "--check", str(full_path)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert result.returncode == 0, f"Node.js syntax error in {rel_path}: {result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_docs_triggering_mdx_readable():
    """Documentation triggering.mdx is readable via Node.js (pass_to_pass)."""
    full_path = Path(REPO) / "docs" / "triggering.mdx"
    script = f"require('fs').readFileSync('{full_path}', 'utf8')"
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
    assert result.returncode == 0, f"Cannot read docs/triggering.mdx: {result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_cursor_rules_writing_mdc_readable():
    """Cursor rules writing-tasks.mdc is readable via Node.js (pass_to_pass)."""
    full_path = Path(REPO) / ".cursor" / "rules" / "writing-tasks.mdc"
    script = f"require('fs').readFileSync('{full_path}', 'utf8')"
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
    assert result.returncode == 0, f"Cannot read .cursor/rules/writing-tasks.mdc: {result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_changeset_markdown_valid():
    """Changeset markdown files are readable via Node.js (pass_to_pass)."""
    changeset_dir = Path(REPO) / ".changeset"
    if changeset_dir.exists():
        for md_file in changeset_dir.glob("*.md"):
            if md_file.name != "README.md":
                script = f"require('fs').readFileSync('{md_file}', 'utf8')"
                result = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
                assert result.returncode == 0, f"Cannot read changeset {md_file.name}: {result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_v3_catalog_tsconfig_valid():
    """V3 catalog tsconfig is valid JSON (pass_to_pass)."""
    full_path = Path(REPO) / "references" / "v3-catalog" / "tsconfig.json"
    script = f"JSON.parse(require('fs').readFileSync('{full_path}', 'utf8'))"
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
    assert result.returncode == 0, f"Invalid v3-catalog tsconfig: {result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_trigger_config_valid():
    """V3 catalog trigger.config.ts has valid Node.js syntax (pass_to_pass)."""
    full_path = Path(REPO) / "references" / "v3-catalog" / "trigger.config.ts"
    result = subprocess.run(
        ["node", "--experimental-strip-types", "--check", str(full_path)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"trigger.config.ts syntax error: {result.stderr}"
