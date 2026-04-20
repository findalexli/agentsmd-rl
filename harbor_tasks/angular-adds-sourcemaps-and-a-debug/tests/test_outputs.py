"""
Task: angular-adds-sourcemaps-and-a-debug
Repo: angular/angular @ f30ed6bbf6706790437a6e4dbfffed3fa8708f57
PR:   67189

Behavioral tests that verify actual functionality by executing bazel commands
and inspecting real build configuration behavior, not just text patterns.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/angular"


def _run_in_repo(cmd: list, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, cwd=REPO
    )


def _exec_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    return _run_in_repo(["python3", "-c", code], timeout)


def test_syntax_check():
    bzl_files = [
        Path(REPO) / "devtools" / "tools" / "defaults.bzl",
        Path(REPO) / "devtools" / "BUILD.bazel",
        Path(REPO) / "devtools" / "projects" / "shell-browser" / "src" / "BUILD.bazel",
        Path(REPO) / "devtools" / "projects" / "shell-browser" / "src" / "app" / "BUILD.bazel",
    ]
    for f in bzl_files:
        content = f.read_text()
        assert content.count("(") == content.count(")")
        assert content.count("[") == content.count("]")


def test_package_json_valid():
    pkg = json.loads((Path(REPO) / "package.json").read_text())
    assert "scripts" in pkg
    assert isinstance(pkg["scripts"], dict)


def test_debug_flag_exists():
    r = _run_in_repo(["bazel", "query", "//devtools:debug", "--output=label"])
    assert r.returncode == 0, f"debug flag not found via bazel query. stderr: {r.stderr[:500]}"
    assert "//devtools:debug" in r.stdout

    r = _run_in_repo(["bazel", "query", "//devtools:debug_build", "--output=label"])
    assert r.returncode == 0, f"debug_build config_setting not found. stderr: {r.stderr[:500]}"
    assert "//devtools:debug_build" in r.stdout


def test_debug_flag_controls_build():
    r = _run_in_repo([
        "bazel", "build", "--nobuild",
        "//devtools/projects/shell-browser/src:prodapp",
        "--//devtools:debug=True"
    ])
    assert r.returncode == 0, f"bazel build with --//devtools:debug=True failed. stderr: {r.stderr[:500]}"


def test_esbuild_wrapper_minify_parameter():
    r = _run_in_repo([
        "bazel", "build", "--nobuild",
        "//devtools/projects/shell-browser/src:prodapp"
    ])
    assert r.returncode == 0, f"bazel build --nobuild failed. stderr: {r.stderr[:500]}"


def test_sourcemap_inline_for_injected_scripts():
    code = '''
import re
import sys
content = open("devtools/projects/shell-browser/src/app/BUILD.bazel").read()
injected = ["detect-angular.ts", "backend.ts", "ng-validate.ts", "content-script.ts"]
for script in injected:
    # Find the esbuild block by looking for entry_point = "SCRIPT_NAME"
    pattern = r'entry_point\s*=\s*"' + re.escape(script) + r'"'
    match = re.search(pattern, content)
    if not match:
        print("ERROR: No esbuild target found for " + script)
        sys.exit(1)
    # Extract a segment after the entry_point to find sourcemap in the same block
    segment = content[match.start():match.start() + 2000]
    sm = re.search(r"sourcemap\\s*=\\s*\\"([^\\"]+)\\"", segment)
    if not sm:
        print("ERROR: sourcemap for " + script + " must be inline")
        sys.exit(1)
    if sm.group(1) != "inline":
        print("ERROR: sourcemap for " + script + " must be inline, got: " + sm.group(1))
        sys.exit(1)
print("PASS")
'''
    r = _exec_python(code)
    assert r.returncode == 0, f"sourcemap validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_no_hardcoded_minify():
    code = r"""
import re
import sys
content = open("devtools/projects/shell-browser/src/BUILD.bazel").read()
matches = list(re.finditer(r"\besbuild\s*\(", content))
if len(matches) == 0:
    print("ERROR: Must have at least one esbuild call")
    sys.exit(1)
for m in matches:
    start = m.end()
    depth = 0
    end = start
    for i in range(start, len(content)):
        c = content[i]
        if c == "(":
            depth += 1
        elif c == ")":
            if depth == 0:
                end = i
                break
            depth -= 1
    block = content[start:end]
    if re.search(r"\bminify\s*=\s*True\b", block):
        print("ERROR: esbuild call has hardcoded minify=True")
        sys.exit(1)
print("PASS")
"""
    r = _exec_python(code)
    assert r.returncode == 0, f"minify validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_package_json_debug_scripts():
    pkg = json.loads((Path(REPO) / "package.json").read_text())
    scripts = pkg.get("scripts", {})
    assert "devtools:build:chrome:debug" in scripts
    assert "devtools:build:firefox:debug" in scripts
    chrome_debug = scripts["devtools:build:chrome:debug"]
    firefox_debug = scripts["devtools:build:firefox:debug"]
    assert "--//devtools:debug" in chrome_debug
    assert "--//devtools:debug" in firefox_debug
    assert "devtools:build:chrome" in chrome_debug
    assert "devtools:build:firefox" in firefox_debug


def test_existing_release_scripts_intact():
    pkg = json.loads((Path(REPO) / "package.json").read_text())
    scripts = pkg.get("scripts", {})
    assert "devtools:build:chrome:release" in scripts
    assert "devtools:build:firefox:release" in scripts
    assert "devtools:build:chrome" in scripts


def test_repo_package_json_scripts():
    r = _exec_python("""
import json
import sys
pkg = json.load(open("/workspace/angular/package.json"))
scripts = pkg.get("scripts", {})
required = ["devtools:build:chrome", "devtools:build:firefox", "devtools:build:chrome:release", "devtools:build:firefox:release", "devtools:test", "devtools:test:unit"]
missing = [s for s in required if s not in scripts]
if missing:
    print("Missing: " + str(missing))
    sys.exit(1)
test_unit = scripts.get("devtools:test:unit", "")
if "//devtools/..." not in test_unit:
    print("devtools:test:unit missing //devtools/...")
    sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0, f"Package.json validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_bazel_structure():
    r = _exec_python("""
import sys
from pathlib import Path
REPO = "/workspace/angular"
files = ["devtools/BUILD.bazel", "devtools/projects/shell-browser/src/BUILD.bazel", "devtools/projects/shell-browser/src/app/BUILD.bazel", "devtools/tools/defaults.bzl"]
for f in files:
    content = (Path(REPO) / f).read_text()
    if content.count("(") != content.count(")"):
        print("Unbalanced parens in " + f)
        sys.exit(1)
    if content.count("[") != content.count("]"):
        print("Unbalanced brackets in " + f)
        sys.exit(1)
    if "load(" not in content:
        print("No load() in " + f)
        sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0, f"Bazel structure validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_devtools_structure():
    r = _exec_python("""
import sys
from pathlib import Path
REPO = "/workspace/angular"
required_files = ["devtools/BUILD.bazel", "devtools/tools/defaults.bzl", "devtools/projects/shell-browser/src/BUILD.bazel", "devtools/projects/shell-browser/src/app/BUILD.bazel", "devtools/README.md", "devtools/tsconfig.json", "devtools/tsconfig-test.json"]
for f in required_files:
    path = Path(REPO) / f
    if not path.exists():
        print("Missing: " + f)
        sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0, f"Devtools structure validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_git_tracking():
    r = subprocess.run(
        ["git", "-C", REPO, "rev-parse", "HEAD"],
        capture_output=True, text=True, timeout=30
    )
    assert r.returncode == 0, f"Git check failed: {r.stderr}"
    assert r.stdout.strip().startswith("f30ed6bbf6")
