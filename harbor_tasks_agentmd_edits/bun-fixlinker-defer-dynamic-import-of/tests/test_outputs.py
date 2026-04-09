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

if "strings.indexOfAny" not in src:
    print("FAIL: credentials.zig does not use strings.indexOfAny")
    sys.exit(1)

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
    """Modified Zig files have valid syntax."""
    for zig_file in ["src/linker.zig", "src/logger.zig", "src/s3/credentials.zig"]:
        path = Path(f"{REPO}/{zig_file}")
        assert path.exists(), f"{zig_file} must exist"
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
    assert "bun.strings" in content, "CLAUDE.md must document bun.strings convention"
    assert "std.mem" in content, "CLAUDE.md must mention std.mem as what to avoid"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repository CI checks
# ---------------------------------------------------------------------------


def test_repo_modified_files_valid():
    """Modified Zig source files exist and have valid structure (pass_to_pass)."""
    for zig_file in ["src/linker.zig", "src/logger.zig", "src/s3/credentials.zig"]:
        path = Path(f"{REPO}/{zig_file}")
        assert path.exists(), f"{zig_file} must exist"
        content = path.read_text()
        assert len(content) > 1000, f"{zig_file} appears truncated"
        assert "pub const" in content or "const " in content, f"{zig_file} missing expected Zig syntax"


def test_repo_ban_words_config_valid():
    """Banned words test configuration is valid (pass_to_pass)."""
    ban_limits_path = Path(f"{REPO}/test/internal/ban-limits.json")
    assert ban_limits_path.exists(), "ban-limits.json must exist"
    ban_words_path = Path(f"{REPO}/test/internal/ban-words.test.ts")
    assert ban_words_path.exists(), "ban-words.test.ts must exist"
    content = ban_limits_path.read_text()
    config = json.loads(content)
    assert isinstance(config, dict), "ban-limits.json must be a valid JSON object"


def test_repo_test_infrastructure_valid():
    """Test infrastructure files are valid (pass_to_pass)."""
    harness_path = Path(f"{REPO}/test/harness.ts")
    assert harness_path.exists(), "test/harness.ts must exist"
    regression_path = Path(f"{REPO}/test/regression/issue")
    assert regression_path.exists(), "test/regression/issue directory must exist"
    internal_path = Path(f"{REPO}/test/internal")
    assert internal_path.exists(), "test/internal directory must exist"


# ---------------------------------------------------------------------------
# Behavioral test using actual Bun runtime
# ---------------------------------------------------------------------------


def test_dynamic_import_runtime_behavior():
    """Bun can require() CJS file with dynamic import of unknown node: module."""
    # Create test files using Python directly, then run bun
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        # Write chunk.js with dynamic import of non-existent node:sqlite
        chunk_js = os.path.join(tmpdir, "chunk.js")
        with open(chunk_js, "w") as f:
            f.write('''module.exports = [function factory(exports) {
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
}];
''')

        # Write main.js that requires chunk.js
        main_js = os.path.join(tmpdir, "main.js")
        with open(main_js, "w") as f:
            f.write('const factories = require("./chunk.js"); console.log("loaded " + factories.length + " factories");')

        # Run main.js with bun
        r = subprocess.run(
            ["bun", "main.js"],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert r.returncode == 0, f"bun command failed: {r.stderr}"
        assert r.stdout.strip() == "loaded 1 factories", f"Expected 'loaded 1 factories', got: {r.stdout.strip()}"
