"""
Task: opencode-db-existssync-migration
Repo: anomalyco/opencode @ 57b63ea83d5926ee23f72185c6fb8894654e2981
PR:   14124

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/opencode"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_syntax():
    """Modified TypeScript files must parse without errors."""
    db_file = Path(REPO) / "packages/opencode/src/storage/db.ts"
    result = subprocess.run(
        ["bun", "tsc", "--noEmit", "--skipLibCheck", str(db_file)],
        cwd=REPO,
        capture_output=True,
        timeout=60,
    )
    assert result.returncode == 0, f"TypeScript syntax error:\n{result.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_uses_existssync_not_bun_file():
    """db.ts must use existsSync from fs instead of Bun.file().size."""
    db_file = Path(REPO) / "packages/opencode/src/storage/db.ts"
    content = db_file.read_text()

    # Must import existsSync from fs
    assert "existsSync" in content, "Should import existsSync from fs"
    assert "from \"fs\"" in content or "from 'fs'" in content, "Should import from fs module"

    # Must NOT use Bun.file().size for existence check
    assert "Bun.file(file).size" not in content, "Should NOT use Bun.file(file).size"

    # Must use existsSync(file) for the check
    assert "existsSync(file)" in content, "Should use existsSync(file) for file existence check"


# [pr_diff] fail_to_pass
def test_skill_file_deleted():
    """The bun-file-io SKILL.md file must be deleted as part of migration."""
    skill_file = Path(REPO) / ".opencode/skill/bun-file-io/SKILL.md"
    assert not skill_file.exists(), "bun-file-io SKILL.md should be deleted (part of migration away from Bun APIs)"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Modified function has real logic, not just pass/return."""
    db_file = Path(REPO) / "packages/opencode/src/storage/db.ts"
    content = db_file.read_text()

    # The migrations function should still exist and have meaningful logic
    assert "export namespace Database" in content, "Database namespace should exist"
    assert "export function migrations" in content or "migrations(" in content, "migrations function should exist"

    # Should still read migration files
    assert "readFileSync" in content, "Should still use readFileSync to read migration files"
