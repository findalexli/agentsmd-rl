"""Behavioral tests for taskforge config module.

These tests execute the actual code via subprocess to verify behavior,
not just string matching in files.
"""

import subprocess
import json
import sys
from pathlib import Path

# Docker-internal path where the repo lives
REPO = "/workspace/taskforge"


def _run_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo directory."""
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# -----------------------------------------------------------------------------
# Fail-to-pass tests: These test the bug fix (renamed file handling)
# -----------------------------------------------------------------------------

def test_renamed_config_file_extracted():
    """Renamed config files are correctly identified using 'rename to' directive."""
    r = _run_python("""
import json
from taskforge.config import extract_config_hunks

# BUG CASE: File renamed FROM non-config TO config file
# The diff --git line has b/random.txt (not a config file)
# But 'rename to' says CLAUDE.md (IS a config file)
# Before fix: would check "random.txt" against CONFIG_RE -> no match
# After fix: checks "CLAUDE.md" against CONFIG_RE -> match found!
diff_text = '''diff --git a/random.txt b/random.txt
rename from random.txt
rename to CLAUDE.md
--- /dev/null
+++ b/CLAUDE.md
@@ -0,0 +1,2 @@
+# Agent Instructions
+# Always use type hints
'''

result = extract_config_hunks(diff_text)
print(json.dumps({"keys": list(result.keys()), "has_claude": "CLAUDE.md" in result, "count": len(result)}))
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["has_claude"], "CLAUDE.md should be extracted from renamed file diff even when b/ path is different"
    assert data["count"] == 1, "Should have exactly one config hunk"


def test_renamed_non_config_file_ignored():
    """Renamed non-config files are correctly ignored."""
    r = _run_python("""
import json
from taskforge.config import extract_config_hunks

# A rename of a regular code file should not appear in config hunks
diff_text = '''diff --git a/main.py b/src/main.py
rename from main.py
rename to src/main.py
--- a/main.py
+++ b/src/main.py
@@ -1,3 +1,4 @@
 def main():
     print("hello")
+    print("world")
'''

result = extract_config_hunks(diff_text)
print(json.dumps({"keys": list(result.keys()), "count": len(result)}))
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["count"] == 0, "Non-config files should not be in config hunks"


def test_regular_config_file_still_works():
    """Non-renamed config files continue to work correctly."""
    r = _run_python("""
import json
from taskforge.config import extract_config_hunks

# Regular modification to CLAUDE.md (not a rename)
diff_text = '''diff --git a/CLAUDE.md b/CLAUDE.md
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -1,2 +1,3 @@
 # Agent Instructions
 # Always use type hints
+# New rule: use dataclasses
'''

result = extract_config_hunks(diff_text)
print(json.dumps({"keys": list(result.keys()), "has_claude": "CLAUDE.md" in result}))
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["has_claude"], "Regular CLAUDE.md modifications should still work"


def test_extract_added_lines_from_renamed_hunk():
    """Added lines can be extracted from a renamed file hunk."""
    r = _run_python("""
import json
from taskforge.config import extract_config_hunks, extract_added_lines

diff_text = '''diff --git a/old.md b/AGENTS.md
rename from old.md
rename to AGENTS.md
--- /dev/null
+++ b/AGENTS.md
@@ -0,0 +1,3 @@
+# Agent Rules
+## Testing
+Always write behavioral tests
'''

hunks = extract_config_hunks(diff_text)
if "AGENTS.md" in hunks:
    added = extract_added_lines(hunks["AGENTS.md"])
    print(json.dumps({"found": True, "added_lines": added}))
else:
    print(json.dumps({"found": False, "keys": list(hunks.keys())}))
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["found"], "AGENTS.md should be found in renamed diff"
    assert "Always write behavioral tests" in data["added_lines"], "Added content should be extractable"


def test_complex_rename_scenario():
    """Multiple files with mix of renames and regular changes."""
    r = _run_python("""
import json
from taskforge.config import extract_config_hunks

# Complex diff with both renamed and regular config files
diff_text = '''diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1 +1,2 @@
 # Project
+## New section

diff --git a/old_rules.md b/.claude/CLAUDE.md
rename from old_rules.md
rename to .claude/CLAUDE.md
--- /dev/null
+++ b/.claude/CLAUDE.md
@@ -0,0 +1,2 @@
+# New Rules
+# For agent
'''

result = extract_config_hunks(diff_text)
keys = list(result.keys())
print(json.dumps({
    "keys": keys,
    "count": len(result),
    "has_readme": "README.md" in result,
    "has_claude": ".claude/CLAUDE.md" in result
}))
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["count"] == 2, "Should have both README.md and .claude/CLAUDE.md"
    assert data["has_readme"], "Regular README.md should be extracted"
    assert data["has_claude"], "Renamed .claude/CLAUDE.md should be extracted"


# -----------------------------------------------------------------------------
# Pass-to-pass tests: These verify basic functionality still works
# -----------------------------------------------------------------------------

def test_is_config_file_recognizes_patterns():
    """is_config_file correctly identifies agent instruction files."""
    r = _run_python("""
import json
from taskforge.config import is_config_file

test_cases = [
    ("CLAUDE.md", True),
    (".claude/CLAUDE.md", True),
    ("AGENTS.md", True),
    ("SKILL.md", True),
    (".cursorrules", True),
    ("README.md", True),
    ("main.py", False),
    ("src/utils.py", False),
]

results = []
for path, expected in test_cases:
    result = is_config_file(path)
    status = "PASS" if result == expected else "FAIL"
    results.append({"path": path, "expected": expected, "got": result, "status": status})

all_pass = all(r["status"] == "PASS" for r in results)
print(json.dumps({"all_pass": all_pass, "results": results}))
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["all_pass"], f"Some is_config_file cases failed: {data['results']}"


def test_is_agent_instruction_file_tier1():
    """is_agent_instruction_file correctly identifies Tier 1 files."""
    r = _run_python("""
import json
from taskforge.config import is_agent_instruction_file

test_cases = [
    ("CLAUDE.md", True),
    (".claude/CLAUDE.md", True),
    (".claude/rules/python.md", True),
    ("AGENTS.md", True),
    ("SKILL.md", True),
    (".cursorrules", True),
    ("README.md", False),  # Tier 2, not Tier 1
    ("CHANGELOG.md", False),
]

results = []
for path, expected in test_cases:
    result = is_agent_instruction_file(path)
    status = "PASS" if result == expected else "FAIL"
    results.append({"path": path, "expected": expected, "got": result, "status": status})

all_pass = all(r["status"] == "PASS" for r in results)
print(json.dumps({"all_pass": all_pass, "results": results}))
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["all_pass"], f"Some Tier 1 cases failed: {data['results']}"


def test_is_code_file_filters_correctly():
    """is_code_file correctly distinguishes code from non-code."""
    r = _run_python("""
import json
from taskforge.config import is_code_file

test_cases = [
    ("src/main.py", True),
    ("lib/utils.ts", True),
    ("app.go", True),
    ("CLAUDE.md", False),
    ("README.md", False),
    (".github/workflows/ci.yml", False),
    ("docs/guide.md", False),
]

results = []
for path, expected in test_cases:
    result = is_code_file(path)
    status = "PASS" if result == expected else "FAIL"
    results.append({"path": path, "expected": expected, "got": result, "status": status})

all_pass = all(r["status"] == "PASS" for r in results)
print(json.dumps({"all_pass": all_pass, "results": results}))
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["all_pass"], f"Some is_code_file cases failed: {data['results']}"


def test_extract_added_lines_basic():
    """extract_added_lines correctly extracts added content."""
    r = _run_python("""
import json
from taskforge.config import extract_added_lines

hunk = '''diff --git a/test.md b/test.md
--- a/test.md
+++ b/test.md
@@ -1,2 +1,4 @@
 line 1
 line 2
+added line 3
+added line 4
'''

result = extract_added_lines(hunk)
expected_contains = "added line 3"
print(json.dumps({
    "result": result,
    "has_expected": expected_contains in result,
    "no_plus_plus": "+++" not in result
}))
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["has_expected"], "Added lines should be extracted"
    assert data["no_plus_plus"], "+++ header lines should not be in result"


# -----------------------------------------------------------------------------
# Module imports correctly
# -----------------------------------------------------------------------------

def test_config_module_imports():
    """Config module can be imported without errors."""
    r = _run_python("""
import json
import taskforge.config as cfg

# Verify all expected exports exist
exports = [
    "is_config_file",
    "is_agent_instruction_file",
    "is_doc_file",
    "is_code_file",
    "extract_config_hunks",
    "extract_added_lines",
    "gh_json",
    "AGENT_INSTRUCTION_PATTERNS",
    "CONFIG_RE",
]

results = {}
for name in exports:
    results[name] = hasattr(cfg, name)

all_present = all(results.values())
print(json.dumps({"all_present": all_present, "exports": results}))
""")
    assert r.returncode == 0, f"Import test failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["all_present"], f"Missing exports: {[k for k,v in data['exports'].items() if not v]}"


if __name__ == "__main__":
    # Run all tests when executed directly
    import traceback
    tests = [
        test_renamed_config_file_extracted,
        test_renamed_non_config_file_ignored,
        test_regular_config_file_still_works,
        test_extract_added_lines_from_renamed_hunk,
        test_complex_rename_scenario,
        test_is_config_file_recognizes_patterns,
        test_is_agent_instruction_file_tier1,
        test_is_code_file_filters_correctly,
        test_extract_added_lines_basic,
        test_config_module_imports,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: {test.__name__}: {e}")
            traceback.print_exc()
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
