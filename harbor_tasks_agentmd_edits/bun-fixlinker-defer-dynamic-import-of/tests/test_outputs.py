"""
Task: bun-fixlinker-defer-dynamic-import-of
Repo: oven-sh/bun @ 9a72bbfae2d
PR:   26981

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/bun"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_linker_defers_dynamic_import():
    """Linker defers dynamic import() of unknown node: modules to runtime."""
    r = subprocess.run(
        ["python3", "-c", """
import sys

src = open("src/linker.zig").read()
lines = src.split("\\n")

found = False
for i, line in enumerate(lines):
    # The fix adds .dynamic alongside .require and .require_resolve
    if "import_record.kind" in line and ".dynamic" in line:
        context = " ".join(lines[max(0, i - 1): i + 2])
        if ".require_resolve" in context and ".require" in context:
            found = True
            break

if not found:
    print("FAIL: .dynamic not in deferral condition with .require and .require_resolve")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Linker deferral check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_logger_dupes_line_text():
    """Logger always dupes line_text from source to prevent use-after-poison."""
    r = subprocess.run(
        ["python3", "-c", """
import sys

src = open("src/logger.zig").read()
lines = src.split("\\n")
in_fn = False
found = False

for line in lines:
    if "pub fn addResolveError" in line and "addResolveErrorWithTextDupe" not in line:
        in_fn = True
    if in_fn and "addResolveErrorWithLevel" in line:
        # The fix changes the dupe parameter from false to true
        if "true" in line:
            found = True
        break

if not found:
    print("FAIL: addResolveError does not pass true for dupe parameter")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Logger dupe check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_credentials_uses_strings_api():
    """credentials.zig uses bun.strings.indexOfAny instead of std.mem.indexOfAny."""
    r = subprocess.run(
        ["python3", "-c", """
import sys

src = open("src/s3/credentials.zig").read()

# Check that strings.indexOfAny is used
if "strings.indexOfAny" not in src:
    print("FAIL: credentials.zig does not use strings.indexOfAny")
    sys.exit(1)

# Check that std.mem.indexOfAny is NOT used
if "std.mem.indexOfAny" in src:
    print("FAIL: credentials.zig still uses std.mem.indexOfAny")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Credentials strings API check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_zig_syntax_valid():
    """Modified Zig files have valid syntax (balanced braces, no truncation)."""
    for zig_file in ["src/linker.zig", "src/logger.zig", "src/s3/credentials.zig"]:
        path = Path(f"{REPO}/{zig_file}")
        assert path.exists(), f"{zig_file} must exist"

        # Use zig to check syntax
        r = subprocess.run(
            ["zig", "fmt", "--check", str(path)],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"Syntax check failed for {zig_file}: {r.stderr}"


def test_regression_test_file_exists():
    """Regression test file for issue 25707 exists with proper content."""
    test_path = Path(f"{REPO}/test/regression/issue/25707.test.ts")
    assert test_path.exists(), "Regression test file must exist"

    content = test_path.read_text()

    # Must test the core scenarios from the PR
    required_patterns = [
        ("node:sqlite", "dynamic import of non-existent node: module"),
        ("ERR_UNKNOWN_BUILTIN_MODULE", "correct runtime error code"),
        ("require(", "CJS require() scenario"),
        ("bun:test", "bun test framework"),
    ]

    for needle, desc in required_patterns:
        assert needle in content, f"Regression test missing: {desc}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — syntax / structural checks
# ---------------------------------------------------------------------------


def test_claude_md_follows_api_conventions():
    """CLAUDE.md documents the bun.strings convention."""
    claude_path = Path(f"{REPO}/src/CLAUDE.md")
    assert claude_path.exists(), "CLAUDE.md must exist"

    content = claude_path.read_text()

    # Must document bun.strings convention
    assert "bun.strings" in content, "CLAUDE.md must document bun.strings convention"
    assert "std.mem" in content, "CLAUDE.md must mention std.mem as what to avoid"


# ---------------------------------------------------------------------------
# Behavioral test using actual Bun runtime
# ---------------------------------------------------------------------------


def test_dynamic_import_runtime_behavior():
    """Bun can require() CJS file with dynamic import of unknown node: module."""
    # Create a temporary test file that mimics the issue
    test_code = """
import { expect, test } from "bun:test";

// Create a temporary directory with test files
const dir = await Bun.$`mktemp -d`.text();

// CJS file with dynamic import inside try/catch
await Bun.write(`${dir}/chunk.js`, `
module.exports = [
  function factory(exports) {
    async function detect(e) {
      if ("createSession" in e) {
        let c;
        try {
          ({DatabaseSync: c} = await import("node:sqlite"))
        } catch(a) {
          if (null !== a && "object" == typeof a && "code" in a && "ERR_UNKNOWN_BUILTIN_MODULE" !== a.code)
            throw a;
        }
      }
    }
    exports.detect = detect;
  }
];
`);

await Bun.write(`${dir}/main.js`, `
// This require() should not fail even though chunk.js contains import("node:sqlite")
const factories = require("./chunk.js");
console.log("loaded " + factories.length + " factories");
`);

// Run the test
const proc = Bun.spawn({
  cmd: ["bun", "main.js"],
  cwd: dir,
  stdout: "pipe",
  stderr: "pipe",
});

const [stdout, stderr, exitCode] = await Promise.all([
  new Response(proc.stdout).text(),
  new Response(proc.stderr).text(),
  proc.exited,
]);

if (stdout.trim() !== "loaded 1 factories") {
  console.error("Expected 'loaded 1 factories', got:", stdout.trim());
  process.exit(1);
}

if (exitCode !== 0) {
  console.error("Exit code:", exitCode, "stderr:", stderr);
  process.exit(1);
}

console.log("PASS");
"""

    # Write and run the test
    test_file = Path(f"{REPO}/_eval_behavior_test.ts")
    test_file.write_text(test_code)

    try:
        r = subprocess.run(
            ["bun", "run", str(test_file)],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"Behavioral test failed: {r.stderr}"
        assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"
    finally:
        test_file.unlink(missing_ok=True)
