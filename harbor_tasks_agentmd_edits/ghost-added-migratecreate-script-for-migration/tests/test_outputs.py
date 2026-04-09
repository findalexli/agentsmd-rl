"""
Task: ghost-added-migratecreate-script-for-migration
Repo: TryGhost/Ghost @ 3ad6d52705c5e7b49831900424000b93fa41e90f
PR:   #26552

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
import tempfile
import os
from pathlib import Path

REPO = "/workspace/Ghost"


# ---------------------------------------------------------------------------
# Helper: run a Node.js expression and return stdout
# ---------------------------------------------------------------------------

def run_node(expr, cwd=None):
    """Run a Node.js expression and return stdout."""
    r = subprocess.run(
        ["node", "-e", expr],
        cwd=cwd or REPO,
        capture_output=True,
        timeout=30,
    )
    return r


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """create-migration.js parses without syntax errors."""
    script = Path(REPO) / "ghost" / "core" / "bin" / "create-migration.js"
    assert script.exists(), f"Script not found at {script}"
    r = subprocess.run(
        ["node", "--check", str(script)],
        capture_output=True, timeout=15,
    )
    assert r.returncode == 0, f"Syntax error:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_slug_validation_accepts_valid():
    """isValidSlug accepts valid kebab-case slugs."""
    r = run_node(
        'const {isValidSlug} = require("./ghost/core/bin/create-migration");'
        'const ok = ["add-column", "fix-index", "a", "a1", "123", "add-mentions-table"];'
        'const results = ok.map(s => isValidSlug(s));'
        'console.log(JSON.stringify(results));'
    )
    assert r.returncode == 0, f"Node failed:\n{r.stderr.decode()}"
    results = json.loads(r.stdout.decode())
    assert all(results), f"Expected all valid slugs to be accepted, got {results}"


# [pr_diff] fail_to_pass
def test_slug_validation_rejects_invalid():
    """isValidSlug rejects invalid slugs (uppercase, underscores, spaces, etc.)."""
    r = run_node(
        'const {isValidSlug} = require("./ghost/core/bin/create-migration");'
        'const bad = ["", "UPPER", "camelCase", "has_underscores", "-leading", '
        '"trailing-", "double--hyphen", "has spaces", "path/slash"];'
        'const results = bad.map(s => isValidSlug(s));'
        'console.log(JSON.stringify(results));'
    )
    assert r.returncode == 0, f"Node failed:\n{r.stderr.decode()}"
    results = json.loads(r.stdout.decode())
    assert not any(results), f"Expected all invalid slugs to be rejected, got {results}"


# [pr_diff] fail_to_pass
def test_version_folder_stable():
    """getNextMigrationVersion bumps minor for stable versions (6.18.0 -> 6.19)."""
    r = run_node(
        'const {getNextMigrationVersion} = require("./ghost/core/bin/create-migration");'
        'const results = ['
        '  getNextMigrationVersion("6.18.0"),'
        '  getNextMigrationVersion("5.75.0"),'
        '  getNextMigrationVersion("6.0.0"),'
        '];'
        'console.log(JSON.stringify(results));'
    )
    assert r.returncode == 0, f"Node failed:\n{r.stderr.decode()}"
    results = json.loads(r.stdout.decode())
    assert results == ["6.19", "5.76", "6.1"], f"Wrong version folders: {results}"


# [pr_diff] fail_to_pass
def test_version_folder_prerelease():
    """getNextMigrationVersion uses current minor for prerelease (6.19.0-rc.0 -> 6.19)."""
    r = run_node(
        'const {getNextMigrationVersion} = require("./ghost/core/bin/create-migration");'
        'const results = ['
        '  getNextMigrationVersion("6.19.0-rc.0"),'
        '  getNextMigrationVersion("6.19.0-rc.1"),'
        '];'
        'console.log(JSON.stringify(results));'
    )
    assert r.returncode == 0, f"Node failed:\n{r.stderr.decode()}"
    results = json.loads(r.stdout.decode())
    assert results == ["6.19", "6.19"], f"Wrong version folders: {results}"


# [pr_diff] fail_to_pass
def test_stable_and_rc_same_folder():
    """Key invariant: stable 6.18.0 and its RC 6.19.0-rc.0 both target folder 6.19."""
    r = run_node(
        'const {getNextMigrationVersion} = require("./ghost/core/bin/create-migration");'
        'console.log(JSON.stringify(['
        '  getNextMigrationVersion("6.18.0"),'
        '  getNextMigrationVersion("6.19.0-rc.0")'
        ']));'
    )
    assert r.returncode == 0, f"Node failed:\n{r.stderr.decode()}"
    results = json.loads(r.stdout.decode())
    assert results[0] == results[1] == "6.19", \
        f"Stable and RC should target same folder, got {results}"


# [pr_diff] fail_to_pass
def test_migration_creates_file():
    """createMigration creates a timestamped migration file in the correct version folder."""
    # We run this in a temp dir to avoid polluting the repo
    r = run_node(
        'const {createMigration} = require("./ghost/core/bin/create-migration");'
        'const fs = require("fs");'
        'const path = require("path");'
        'const os = require("os");'
        'const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "ghost-test-"));'
        'const coreDir = path.join(tmpDir, "core");'
        'fs.mkdirSync(path.join(coreDir, "core", "server", "data", "migrations", "versions"), {recursive: true});'
        'fs.writeFileSync(path.join(coreDir, "package.json"), JSON.stringify({name:"ghost",version:"6.18.0"}, null, 2));'
        'const result = createMigration({slug: "add-column", coreDir, date: new Date("2026-02-23T10:30:00Z")});'
        'const exists = fs.existsSync(result.migrationPath);'
        'const hasVersionDir = result.migrationPath.includes(path.join("versions", "6.19"));'
        'const hasTimestamp = result.migrationPath.endsWith("2026-02-23-10-30-00-add-column.js");'
        'fs.rmSync(tmpDir, {recursive: true, force: true});'
        'console.log(JSON.stringify({exists, hasVersionDir, hasTimestamp}));'
    )
    assert r.returncode == 0, f"Node failed:\n{r.stderr.decode()}"
    result = json.loads(r.stdout.decode())
    assert result["exists"], "Migration file was not created"
    assert result["hasVersionDir"], "Migration not in correct version folder"
    assert result["hasTimestamp"], "Migration filename doesn't have correct timestamp format"


# [pr_diff] fail_to_pass
def test_rc_bump_on_stable():
    """createMigration bumps package.json to RC when version is stable."""
    r = run_node(
        'const {createMigration} = require("./ghost/core/bin/create-migration");'
        'const fs = require("fs");'
        'const path = require("path");'
        'const os = require("os");'
        'const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "ghost-test-"));'
        'const coreDir = path.join(tmpDir, "core");'
        'fs.mkdirSync(path.join(coreDir, "core", "server", "data", "migrations", "versions"), {recursive: true});'
        'fs.writeFileSync(path.join(coreDir, "package.json"), JSON.stringify({name:"ghost",version:"6.18.0"}, null, 2));'
        'const result = createMigration({slug: "first-migration", coreDir, date: new Date("2026-01-01T00:00:00Z")});'
        'const newVersion = JSON.parse(fs.readFileSync(path.join(coreDir, "package.json"), "utf8")).version;'
        'fs.rmSync(tmpDir, {recursive: true, force: true});'
        'console.log(JSON.stringify({rcVersion: result.rcVersion, newVersion}));'
    )
    assert r.returncode == 0, f"Node failed:\n{r.stderr.decode()}"
    result = json.loads(r.stdout.decode())
    assert result["rcVersion"] == "6.19.0-rc.0", \
        f"Expected RC version 6.19.0-rc.0, got {result['rcVersion']}"
    assert result["newVersion"] == "6.19.0-rc.0", \
        f"package.json not bumped, version is {result['newVersion']}"


# [pr_diff] fail_to_pass
def test_no_bump_on_prerelease():
    """createMigration does NOT bump when version is already a prerelease."""
    r = run_node(
        'const {createMigration} = require("./ghost/core/bin/create-migration");'
        'const fs = require("fs");'
        'const path = require("path");'
        'const os = require("os");'
        'const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "ghost-test-"));'
        'const coreDir = path.join(tmpDir, "core");'
        'fs.mkdirSync(path.join(coreDir, "core", "server", "data", "migrations", "versions"), {recursive: true});'
        'fs.writeFileSync(path.join(coreDir, "package.json"), JSON.stringify({name:"ghost",version:"6.19.0-rc.0"}, null, 2));'
        'const result = createMigration({slug: "second-migration", coreDir, date: new Date("2026-01-01T00:00:00Z")});'
        'const version = JSON.parse(fs.readFileSync(path.join(coreDir, "package.json"), "utf8")).version;'
        'fs.rmSync(tmpDir, {recursive: true, force: true});'
        'console.log(JSON.stringify({rcVersion: result.rcVersion, version}));'
    )
    assert r.returncode == 0, f"Node failed:\n{r.stderr.decode()}"
    result = json.loads(r.stdout.decode())
    assert result["rcVersion"] is None, \
        f"Expected no RC bump, got {result['rcVersion']}"
    assert result["version"] == "6.19.0-rc.0", \
        f"Version should be unchanged, got {result['version']}"


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config edit tests (config_edit) — SKILL.md update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_script_exports_functions():
    """create-migration.js exports isValidSlug, getNextMigrationVersion, createMigration."""
    r = run_node(
        'const m = require("./ghost/core/bin/create-migration");'
        'console.log(JSON.stringify({'
        '  hasValidSlug: typeof m.isValidSlug === "function",'
        '  hasNextVersion: typeof m.getNextMigrationVersion === "function",'
        '  hasCreate: typeof m.createMigration === "function"'
        '}));'
    )
    assert r.returncode == 0, f"Node failed:\n{r.stderr.decode()}"
    result = json.loads(r.stdout.decode())
    assert result["hasValidSlug"], "Missing export: isValidSlug"
    assert result["hasNextVersion"], "Missing export: getNextMigrationVersion"
    assert result["hasCreate"], "Missing export: createMigration"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD gates
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_package_json_valid():
    """ghost/core/package.json is valid JSON (pass_to_pass)."""
    core_package = Path(REPO) / "ghost" / "core" / "package.json"
    assert core_package.exists(), f"package.json not found at {core_package}"
    with open(core_package) as f:
        json.load(f)  # Validates JSON syntax


# [repo_tests] pass_to_pass
def test_repo_existing_bin_syntax():
    """Existing bin/minify-assets.js has no syntax errors (pass_to_pass)."""
    script = Path(REPO) / "ghost" / "core" / "bin" / "minify-assets.js"
    assert script.exists(), f"minify-assets.js not found at {script}"
    r = subprocess.run(
        ["node", "--check", str(script)],
        capture_output=True, timeout=15,
    )
    assert r.returncode == 0, f"Syntax error in minify-assets.js:\n{r.stderr.decode()}"
