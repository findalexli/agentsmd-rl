"""
Task: effect-backport-messagestorage-nonempty
Repo: effect-ts/effect @ 33712058e2655dd50f9b2b511ab8d38c2bd5268a
PR:   6031

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/effect"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax / compilation checks
# ---------------------------------------------------------------------------


def test_source_files_parse():
    """Modified TypeScript files must parse without syntax errors."""
    script = """
const ts = require("typescript");
const fs = require("fs");
const files = [
  "packages/cluster/src/MessageStorage.ts",
  "packages/cluster/src/SqlMessageStorage.ts",
  "packages/cluster/test/MessageStorage.test.ts"
];
let errors = [];
for (const f of files) {
  if (!fs.existsSync(f)) { errors.push(f + ": file not found"); continue; }
  const src = fs.readFileSync(f, "utf-8");
  const sf = ts.createSourceFile(f, src, ts.ScriptTarget.Latest, true);
  if (sf.parseDiagnostics && sf.parseDiagnostics.length > 0) {
    for (const d of sf.parseDiagnostics) {
      errors.push(f + ": parse error at position " + d.start + " - " + d.messageText);
    }
  }
}
if (errors.length > 0) {
  console.error(errors.join("\\n"));
  process.exit(1);
}
console.log("OK");
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"TypeScript parse failed:\n{result.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------


def test_encoded_nonemptyarray_types():
    """MessageStorage.Encoded type must use Arr.NonEmptyArray for all id parameters."""
    script = """
const ts = require("typescript");
const fs = require("fs");
const src = fs.readFileSync("packages/cluster/src/MessageStorage.ts", "utf-8");
// Parse first -- gate structural checks behind valid syntax
const sf = ts.createSourceFile("MessageStorage.ts", src, ts.ScriptTarget.Latest, true);
if (sf.parseDiagnostics && sf.parseDiagnostics.length > 0) {
  console.error("Parse errors found");
  process.exit(1);
}
// Count NonEmptyArray type references in the Encoded type region
const nonEmptyCount = (src.match(/Arr\\.NonEmptyArray</g) || []).length;
if (nonEmptyCount < 5) {
  console.error("Expected >= 5 Arr.NonEmptyArray refs in Encoded, found " + nonEmptyCount);
  process.exit(1);
}
// Verify Snowflake-specific param is present
if (!src.includes("Arr.NonEmptyArray<Snowflake.Snowflake>")) {
  console.error("Missing Arr.NonEmptyArray<Snowflake.Snowflake> for message ids");
  process.exit(1);
}
console.log("OK: " + nonEmptyCount + " NonEmptyArray type refs");
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"NonEmptyArray type check failed:\n{result.stderr}"


def test_makeencoded_empty_guards():
    """makeEncoded must guard empty id lists with Arr.isNonEmptyArray before delegating."""
    script = """
const fs = require("fs");
const src = fs.readFileSync("packages/cluster/src/MessageStorage.ts", "utf-8");
const start = src.indexOf("export const makeEncoded");
const end = src.indexOf("const decodeMessages", start);
if (start < 0 || end < start) {
  console.error("Could not locate makeEncoded function");
  process.exit(1);
}
const body = src.substring(start, end);
// Must have >= 4 isNonEmptyArray guards (repliesFor, repliesForUnfiltered,
// unprocessedMessages/unprocessedMessagesById, resetShards)
const guards = (body.match(/Arr\\.isNonEmptyArray/g) || []).length;
if (guards < 4) {
  console.error("Expected >= 4 Arr.isNonEmptyArray guards in makeEncoded, found " + guards);
  process.exit(1);
}
// repliesForUnfiltered: previously had NO guard, just delegated directly
if (!body.includes("Arr.isNonEmptyArray(requestIds)")) {
  console.error("Missing guard: repliesForUnfiltered must check isNonEmptyArray(requestIds)");
  process.exit(1);
}
// resetShards: previously had NO guard, just delegated directly
if (!body.includes("Arr.isNonEmptyArray(shards)")) {
  console.error("Missing guard: resetShards must check isNonEmptyArray(shards)");
  process.exit(1);
}
console.log("OK: " + guards + " isNonEmptyArray guards found");
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Guard check failed:\n{result.stderr}"


def test_sql_driver_nonemptyarray():
    """SqlMessageStorage must use Arr.NonEmptyArray for shard id parameters."""
    src = Path(f"{REPO}/packages/cluster/src/SqlMessageStorage.ts").read_text()
    # The pg and orElse dialect handlers should both use NonEmptyArray
    assert "Arr.NonEmptyArray<string>" in src, (
        "SqlMessageStorage should use Arr.NonEmptyArray<string> for shard id "
        "parameters in both pg and orElse dialect handlers"
    )


# ---------------------------------------------------------------------------
# Config/doc updates (pr_diff) -- agent instruction file changes
# ---------------------------------------------------------------------------


def test_agents_md_changesets():
    """AGENTS.md must include a Changesets section referencing .changeset/ directory."""
    agents_md = Path(f"{REPO}/AGENTS.md").read_text()
    assert "## Changesets" in agents_md, (
        "AGENTS.md should have a ## Changesets section"
    )
    assert ".changeset/" in agents_md, (
        "AGENTS.md Changesets section should reference the .changeset/ directory"
    )


def test_changeset_file_for_cluster():
    """A changeset file must exist in .changeset/ referencing @effect/cluster."""
    changeset_dir = Path(f"{REPO}/.changeset")
    assert changeset_dir.is_dir(), ".changeset/ directory must exist"
    changeset_files = [
        f for f in changeset_dir.glob("*.md") if f.name != "README.md"
    ]
    assert len(changeset_files) > 0, (
        "At least one changeset .md file must exist in .changeset/"
    )
    found = any("@effect/cluster" in f.read_text() for f in changeset_files)
    assert found, "A changeset file must reference the @effect/cluster package"
