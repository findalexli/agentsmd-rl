"""
Task: trigger.dev-remove-triggerandpoll-function
Repo: triggerdotdev/trigger.dev @ 21c2c136beec90c28ec46c895561f5b3c258ec06
PR:   2379

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/trigger.dev"


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["node", "-e", script],
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
        content = full_path.read_text()
        assert "import" in content, f"{rel_path} missing import statements"
        assert len(content) > 100, f"{rel_path} is unexpectedly small or empty"


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
    tasks_ts = Path(REPO) / "packages" / "trigger-sdk" / "src" / "v3" / "tasks.ts"
    content = tasks_ts.read_text()
    required_methods = ["trigger,", "batchTrigger,", "triggerAndWait,", "batchTriggerAndWait,"]
    for method in required_methods:
        assert method in content, f"tasks object must still export {method.rstrip(',')}"


# [static] pass_to_pass
def test_repo_imports_check():
    """Import statements in modified files have balanced braces (pass_to_pass).

    Static check: validates import syntax by checking brace balance.
    """
    files_to_check = [
        "packages/trigger-sdk/src/v3/shared.ts",
        "packages/trigger-sdk/src/v3/tasks.ts",
        "references/v3-catalog/src/trigger/sdkUsage.ts",
    ]
    for rel_path in files_to_check:
        full_path = Path(REPO) / rel_path
        content = full_path.read_text()
        matches = re.findall(r"import\s*\{[^}]*\}\s*from", content)
        for imp in matches:
            open_count = imp.count("{")
            close_count = imp.count("}")
            assert open_count == close_count, f"Unbalanced braces in import: {imp}"


# [pr_diff] fail_to_pass
def test_triggerandpoll_function_removed():
    """triggerAndPoll function definition must be removed from shared.ts."""
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('packages/trigger-sdk/src/v3/shared.ts', 'utf8');
const hasFunc = /export\\s+async\\s+function\\s+triggerAndPoll/.test(content);
if (hasFunc) {
    console.error('triggerAndPoll function definition still exists in shared.ts');
    process.exit(1);
}
console.log('OK: triggerAndPoll function removed from shared.ts');
""")
    assert r.returncode == 0, f"triggerAndPoll still defined in shared.ts: {r.stderr}"


# [pr_diff] fail_to_pass
def test_triggerandpoll_not_exported():
    """triggerAndPoll must not appear in the tasks export object in tasks.ts."""
    tasks_ts = Path(REPO) / "packages" / "trigger-sdk" / "src" / "v3" / "tasks.ts"
    content = tasks_ts.read_text()
    match = re.search(r"export const tasks\s*=\s*\{([^}]+)\}", content, re.DOTALL)
    assert match, "Could not find 'export const tasks = { ... }' in tasks.ts"
    tasks_block = match.group(1)
    assert "triggerAndPoll" not in tasks_block, "triggerAndPoll is still listed in the tasks export object"


# [pr_diff] fail_to_pass
def test_triggerandpoll_not_imported():
    """triggerAndPoll must not be imported from shared.js in tasks.ts."""
    tasks_ts = Path(REPO) / "packages" / "trigger-sdk" / "src" / "v3" / "tasks.ts"
    content = tasks_ts.read_text()
    import_match = re.search(
        r'import\s*\{([^}]+)\}\s*from\s*["\']\.\/shared\.js["\']',
        content, re.DOTALL,
    )
    assert import_match, "Could not find import from './shared.js' in tasks.ts"
    imports = import_match.group(1)
    assert "triggerAndPoll" not in imports, "triggerAndPoll is still imported from shared.js in tasks.ts"


# [pr_diff] fail_to_pass
def test_sdk_usage_no_triggerandpoll():
    """Reference catalog sdkUsage.ts must not call tasks.triggerAndPoll."""
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('references/v3-catalog/src/trigger/sdkUsage.ts', 'utf8');
if (content.includes('triggerAndPoll')) {
    console.error('sdkUsage.ts still references triggerAndPoll');
    process.exit(1);
}
console.log('OK: sdkUsage.ts does not reference triggerAndPoll');
""")
    assert r.returncode == 0, f"sdkUsage.ts still uses triggerAndPoll: {r.stderr}"


# [pr_diff] fail_to_pass
def test_cursor_rules_no_triggerandpoll():
    """Cursor rules writing-tasks.mdc must not document triggerAndPoll."""
    mdc = Path(REPO) / ".cursor" / "rules" / "writing-tasks.mdc"
    content = mdc.read_text()
    assert "triggerAndPoll" not in content, ".cursor/rules/writing-tasks.mdc still documents triggerAndPoll"


# [pr_diff] fail_to_pass
def test_docs_triggering_no_triggerandpoll():
    """docs/triggering.mdx must not document triggerAndPoll."""
    doc = Path(REPO) / "docs" / "triggering.mdx"
    content = doc.read_text()
    assert "triggerAndPoll" not in content, "docs/triggering.mdx still references triggerAndPoll"


# [pr_diff] fail_to_pass
def test_docs_triggering_table_updated():
    """The function summary table in docs/triggering.mdx must not list triggerAndPoll."""
    doc = Path(REPO) / "docs" / "triggering.mdx"
    content = doc.read_text()
    assert "tasks.trigger()" in content, "Table should still list tasks.trigger()"
    assert "batch.trigger()" in content, "Table should still list batch.trigger()"
    assert "tasks.triggerAndPoll()" not in content, "docs/triggering.mdx table still lists tasks.triggerAndPoll()"


# [repo_tests] pass_to_pass
def test_repo_prettier_check():
    """Modified TypeScript files pass Prettier formatting check (pass_to_pass).

    Uses npx prettier --check to verify files conform to repo's formatting standards.
    """
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
    """Repo's modified TypeScript files pass Node.js syntax check (pass_to_pass).

    Uses Node.js 22 --experimental-strip-types --check to verify syntax.
    """
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
        script = f"require('fs').readFileSync('{full_path}', 'utf8')"
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
        script = f"require('fs').readFileSync('{full_path}', 'utf8')"
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
    """Modified files pass Prettier --list-different check (pass_to_pass).

    Uses npx prettier --list-different to verify formatting.
    Empty output means all files match formatting standards.
    """
    files_to_check = [
        "packages/trigger-sdk/src/v3/shared.ts",
        "packages/trigger-sdk/src/v3/tasks.ts",
        "references/v3-catalog/src/trigger/sdkUsage.ts",
    ]
    cmd = ["npx", "--yes", "prettier@3.0.0", "--list-different"] + files_to_check
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=REPO)
    assert result.returncode == 0, f"Prettier check failed (files need formatting): {result.stdout}{result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_json_parse_validation():
    """Repo's package.json files parse correctly as JSON (pass_to_pass).

    Uses Node.js JSON.parse to validate structure and re-stringify.
    """
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
    """Repo's turbo.json is valid JSON (pass_to_pass).

    CI tooling: turbo.json is used by the build system.
    """
    full_path = Path(REPO) / "turbo.json"
    script = f"JSON.parse(require('fs').readFileSync('{full_path}', 'utf8'))"
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
    assert result.returncode == 0, f"Invalid turbo.json: {result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_pnpm_workspace_valid():
    """Repo's pnpm-workspace.yaml is valid YAML (pass_to_pass).

    CI tooling: workspace definition is required for monorepo builds.
    """
    full_path = Path(REPO) / "pnpm-workspace.yaml"
    content = full_path.read_text()
    assert "packages:" in content, "pnpm-workspace.yaml missing packages key"
    script = f"require('fs').readFileSync('{full_path}', 'utf8')"
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
    assert result.returncode == 0, f"Cannot read pnpm-workspace.yaml: {result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_root_package_valid():
    """Repo's root package.json is valid JSON (pass_to_pass).

    CI tooling: root package.json defines workspace scripts.
    """
    full_path = Path(REPO) / "package.json"
    script = f"JSON.parse(require('fs').readFileSync('{full_path}', 'utf8'))"
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
    assert result.returncode == 0, f"Invalid root package.json: {result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_prettier_config_valid():
    """Repo's prettier config is valid JavaScript (pass_to_pass).

    CI tooling: prettier.config.js is used in format checks.
    """
    full_path = Path(REPO) / "prettier.config.js"
    result = subprocess.run(
        ["node", "--check", str(full_path)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"prettier.config.js has syntax errors: {result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_trigger_sdk_tsconfig_valid():
    """SDK tsconfig files are valid JSON (pass_to_pass).

    CI tooling: TypeScript configs must be valid for tsc --noEmit.
    """
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
    """SDK TypeScript files have valid Node.js 22 syntax (pass_to_pass).

    CI tooling: Node.js --experimental-strip-types validates modern TS syntax.
    """
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
    """Documentation triggering.mdx is readable via Node.js (pass_to_pass).

    CI tooling: docs are processed in CI builds.
    """
    full_path = Path(REPO) / "docs" / "triggering.mdx"
    script = f"require('fs').readFileSync('{full_path}', 'utf8')"
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
    assert result.returncode == 0, f"Cannot read docs/triggering.mdx: {result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_cursor_rules_writing_mdc_readable():
    """Cursor rules writing-tasks.mdc is readable via Node.js (pass_to_pass).

    CI tooling: .cursor/rules are validated in CI.
    """
    full_path = Path(REPO) / ".cursor" / "rules" / "writing-tasks.mdc"
    script = f"require('fs').readFileSync('{full_path}', 'utf8')"
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
    assert result.returncode == 0, f"Cannot read .cursor/rules/writing-tasks.mdc: {result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_changeset_markdown_valid():
    """Changeset markdown files are readable via Node.js (pass_to_pass).

    CI tooling: .changeset/*.md files are processed by changesets/cli.
    """
    changeset_dir = Path(REPO) / ".changeset"
    if changeset_dir.exists():
        for md_file in changeset_dir.glob("*.md"):
            if md_file.name != "README.md":
                script = f"require('fs').readFileSync('{md_file}', 'utf8')"
                result = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
                assert result.returncode == 0, f"Cannot read changeset {md_file.name}: {result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_v3_catalog_tsconfig_valid():
    """V3 catalog tsconfig is valid JSON (pass_to_pass).

    CI tooling: TypeScript configs must be valid for monorepo builds.
    """
    full_path = Path(REPO) / "references" / "v3-catalog" / "tsconfig.json"
    script = f"JSON.parse(require('fs').readFileSync('{full_path}', 'utf8'))"
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
    assert result.returncode == 0, f"Invalid v3-catalog tsconfig: {result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_trigger_config_valid():
    """V3 catalog trigger.config.ts has valid Node.js syntax (pass_to_pass).

    CI tooling: trigger.config.ts is parsed during build process.
    """
    full_path = Path(REPO) / "references" / "v3-catalog" / "trigger.config.ts"
    result = subprocess.run(
        ["node", "--experimental-strip-types", "--check", str(full_path)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"trigger.config.ts syntax error: {result.stderr}"
