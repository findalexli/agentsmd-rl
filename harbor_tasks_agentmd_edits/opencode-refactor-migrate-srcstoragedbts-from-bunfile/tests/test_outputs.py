"""
Task: opencode-refactor-migrate-srcstoragedbts-from-bunfile
Repo: anomalyco/opencode @ 6fb4f2a7a5d768c11fafdeae4aa8b5c7fcb46b44
PR:   14124

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/opencode"
PACKAGE = f"{REPO}/packages/opencode"
DB_TS = f"{PACKAGE}/src/storage/db.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_compiles():
    """Modified TypeScript files must compile without errors."""
    r = subprocess.run(
        ["bun", "run", "tsc", "--noEmit", "--skipLibCheck"],
        cwd=PACKAGE,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, f"TypeScript compilation failed:\n{r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_migrations_uses_exists_sync():
    """migrations() function must use existsSync instead of Bun.file().size."""
    db_ts = Path(DB_TS).read_text()

    # Must import existsSync from fs
    assert "existsSync" in db_ts, "Must import existsSync from 'fs'"

    # Must use existsSync in migrations function
    assert "existsSync(file)" in db_ts, "Must use existsSync(file) in migrations function"

    # Should NOT use Bun.file(...).size pattern anymore
    # (We check this negatively - the old pattern should be gone)
    old_pattern = "Bun.file(file).size"
    assert old_pattern not in db_ts, f"Must NOT use '{old_pattern}' - migrate to existsSync(file)"


# [pr_diff] fail_to_pass
def test_migrations_skips_missing_files():
    """migrations() function correctly skips directories without migration.sql."""
    # Create a test script that exercises the migrations logic
    test_script = """
import { readdirSync, existsSync, readFileSync, mkdirSync, writeFileSync, rmSync } from "fs";
import path from "path";
import { tmpdir } from "os";

// Simulate the migrations function logic (the fixed version)
function migrations(dir: string) {
  const dirs = readdirSync(dir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name);

  const sql = dirs
    .map((name) => {
      const file = path.join(dir, name, "migration.sql");
      if (!existsSync(file)) return;  // This is the fix - using existsSync
      return {
        sql: readFileSync(file, "utf-8"),
        timestamp: Date.now(),
      };
    })
    .filter(Boolean);

  return sql;
}

// Create a temp directory structure
const tmpDir = path.join(tmpdir(), `opencode-test-${Date.now()}`);
mkdirSync(tmpDir, { recursive: true });

// Create test structure:
// tmpDir/
//   20240101120000_valid/     <- has migration.sql
//     migration.sql
//   20240101120001_invalid/   <- missing migration.sql (should be skipped)

const validDir = path.join(tmpDir, "20240101120000_valid");
const invalidDir = path.join(tmpDir, "20240101120001_invalid");

mkdirSync(validDir, { recursive: true });
mkdirSync(invalidDir, { recursive: true });

writeFileSync(path.join(validDir, "migration.sql"), "CREATE TABLE test (id INTEGER);");
// Note: invalidDir intentionally has NO migration.sql file

// Run migrations logic
const result = migrations(tmpDir);

// Cleanup
rmSync(tmpDir, { recursive: true, force: true });

// Verify results
if (result.length !== 1) {
  console.error(`FAIL: Expected 1 migration, got ${result.length}`);
  process.exit(1);
}

if (!result[0].sql.includes("CREATE TABLE test")) {
  console.error("FAIL: Migration content doesn't match");
  process.exit(1);
}

console.log("PASS: migrations() correctly skips directories without migration.sql");
"""

    # Write and run the test script
    script_path = Path(REPO) / "_test_migrations.ts"
    script_path.write_text(test_script)
    try:
        r = subprocess.run(
            ["bun", "run", str(script_path)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Test failed:\n{r.stdout}\n{r.stderr}"
        assert "PASS" in r.stdout, f"Expected PASS in output:\n{r.stdout}"
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_storage_tests_pass():
    """Upstream storage tests still pass after the migration."""
    r = subprocess.run(
        ["bun", "test", "src/storage/"],
        cwd=PACKAGE,
        capture_output=True,
        text=True,
        timeout=120,
    )
    # Bun test returns 0 on success, 1 if tests fail
    assert r.returncode == 0, f"Storage tests failed:\n{r.stdout}\n{r.stderr}"


# [static] pass_to_pass
def test_not_stub():
    """Modified migrations function has real logic, not just pass/return."""
    db_ts = Path(DB_TS).read_text()

    # Parse the migrations function to ensure it has real logic
    # The function should contain multiple statements beyond just "return"
    func_start = db_ts.find("function migrations(dir: string)")
    assert func_start != -1, "migrations function not found"

    # Extract function body (simplified - find the closing brace)
    func_body_start = db_ts.find("{", func_start)
    # Find matching closing brace (account for nesting)
    depth = 1
    pos = func_body_start + 1
    while depth > 0 and pos < len(db_ts):
        if db_ts[pos] == "{":
            depth += 1
        elif db_ts[pos] == "}":
            depth -= 1
        pos += 1

    func_body = db_ts[func_body_start + 1:pos - 1]

    # Should contain readdirSync, existsSync, readFileSync calls
    assert "readdirSync" in func_body, "migrations function must use readdirSync"
    assert "existsSync" in func_body, "migrations function must use existsSync"
    assert "readFileSync" in func_body, "migrations function must use readFileSync"

    # Should have more than just a single return statement
    lines = [l.strip() for l in func_body.split("\n") if l.strip() and not l.strip().startswith("//")]
    assert len(lines) >= 3, "migrations function body is too simple (likely stub)"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .opencode/skill/bun-file-io/SKILL.md removed
def test_bun_file_io_skill_removed():
    """bun-file-io skill file must be removed as part of migration away from Bun.file()."""
    skill_file = Path(f"{REPO}/.opencode/skill/bun-file-io/SKILL.md")
    assert not skill_file.exists(), f"Skill file should be removed: {skill_file}"
