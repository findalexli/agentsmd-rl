"""
Task: angular-adds-sourcemaps-and-a-debug
Repo: angular/angular @ f30ed6bbf6706790437a6e4dbfffed3fa8708f57
PR:   67189

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/angular"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo directory."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _parse_starlark_block(text: str, keyword: str) -> str:
    """Extract the body of a Starlark call like bool_flag(...) by paren matching."""
    start = text.find(keyword + "(")
    assert start != -1, f"No {keyword}() found"
    i = start + len(keyword) + 1
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "(":
            depth += 1
        elif text[j] == ")":
            if depth == 0:
                return text[i:j]
            depth -= 1
    raise AssertionError(f"Could not parse {keyword}() block")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


def test_syntax_check():
    """Modified .bzl and BUILD.bazel files have balanced parentheses."""
    bzl_files = [
        Path(REPO) / "devtools" / "tools" / "defaults.bzl",
        Path(REPO) / "devtools" / "BUILD.bazel",
        Path(REPO) / "devtools" / "projects" / "shell-browser" / "src" / "BUILD.bazel",
        Path(REPO) / "devtools" / "projects" / "shell-browser" / "src" / "app" / "BUILD.bazel",
    ]
    for f in bzl_files:
        content = f.read_text()
        assert content.count("(") == content.count(")"), \
            f"Unbalanced parentheses in {f.name}"
        assert content.count("[") == content.count("]"), \
            f"Unbalanced brackets in {f.name}"


def test_package_json_valid():
    """package.json is valid JSON with a scripts object."""
    pkg = json.loads((Path(REPO) / "package.json").read_text())
    assert "scripts" in pkg, "package.json must have scripts"
    assert isinstance(pkg["scripts"], dict)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral build config tests
# ---------------------------------------------------------------------------


def test_defaults_bzl_esbuild_wrapper():
    """defaults.bzl defines esbuild wrapper with correct select() conditional logic."""
    r = _run_py(r"""
import re

content = open("devtools/tools/defaults.bzl").read()

# Must be a function definition, not a simple re-export alias
assert re.search(r'^def\s+esbuild\s*\(', content, re.MULTILINE), \
    "defaults.bzl must define esbuild as a function (def esbuild(...))"

# Must accept minify and sourcemap parameters
fn_match = re.search(r'def\s+esbuild\s*\(([^)]+)\)', content)
assert fn_match, "Could not parse esbuild function signature"
params = fn_match.group(1)
assert "minify" in params, "esbuild must accept minify parameter"
assert "sourcemap" in params, "esbuild must accept sourcemap parameter"

# Must use select() for conditional minify — verify the mapping logic
select_match = re.search(r'select\s*\(\s*\{([^}]+)\}', content, re.DOTALL)
assert select_match, "esbuild must use select() for conditional minify"
select_body = select_match.group(1)

# debug_build label -> False (no minify in debug mode)
assert '"//devtools:debug_build"' in select_body, \
    "select() must reference //devtools:debug_build"
lines = [l.strip() for l in select_body.strip().split('\n') if l.strip()]
debug_line = [l for l in lines if "debug_build" in l]
assert len(debug_line) == 1, "Expected exactly one debug_build entry"
assert "False" in debug_line[0], \
    "debug_build condition must set minify to False"

# default -> True (minify in release mode)
assert '"//conditions:default"' in select_body, \
    "select() must have //conditions:default"
default_line = [l for l in lines if "default" in l]
assert len(default_line) == 1, "Expected exactly one default entry"
assert "True" in default_line[0], \
    "default condition must set minify to True"

# Must call _esbuild internally with the resolved value
assert "_esbuild(" in content, "wrapper must call _esbuild internally"

print("PASS")
""")
    assert r.returncode == 0, f"esbuild wrapper validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_debug_flag_defined():
    """devtools/BUILD.bazel defines debug bool_flag and config_setting with correct wiring."""
    r = _run_py("""
import re

content = open("devtools/BUILD.bazel").read()

def parse_block(text, keyword):
    start = text.find(keyword + "(")
    assert start != -1, f"No {keyword}() found"
    i = start + len(keyword) + 1
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "(":
            depth += 1
        elif text[j] == ")":
            if depth == 0:
                return text[i:j]
            depth -= 1
    raise AssertionError(f"Could not parse {keyword}() block")

# Validate bool_flag block
bf_body = parse_block(content, "bool_flag")
assert re.search(r'name\\s*=\\s*"debug"', bf_body), \
    "bool_flag must be named 'debug'"
assert "build_setting_default" in bf_body, \
    "bool_flag must have build_setting_default"

# Validate config_setting block
cs_body = parse_block(content, "config_setting")
assert re.search(r'name\\s*=\\s*"debug_build"', cs_body), \
    "config_setting must be named 'debug_build'"

# Verify config_setting references the debug flag correctly
assert ":debug" in cs_body, \
    "config_setting must reference :debug flag"
assert '"True"' in cs_body, \
    "config_setting must match :debug = True"

print("PASS")
""")
    assert r.returncode == 0, f"debug flag validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_package_json_debug_scripts():
    """package.json debug scripts exist and pass --//devtools:debug flag to bazel."""
    r = _run_py("""
import json

pkg = json.loads(open("package.json").read())
scripts = pkg.get("scripts", {})

# Scripts must exist
assert "devtools:build:chrome:debug" in scripts, \
    "package.json must have devtools:build:chrome:debug"
assert "devtools:build:firefox:debug" in scripts, \
    "package.json must have devtools:build:firefox:debug"

chrome_debug = scripts["devtools:build:chrome:debug"]
firefox_debug = scripts["devtools:build:firefox:debug"]

# Debug scripts must pass the debug flag to bazel
assert "--//devtools:debug" in chrome_debug, \
    f"Chrome debug script must pass --//devtools:debug, got: {chrome_debug}"
assert "--//devtools:debug" in firefox_debug, \
    f"Firefox debug script must pass --//devtools:debug, got: {firefox_debug}"

# Debug scripts must chain from the correct base scripts
assert "devtools:build:chrome" in chrome_debug, \
    "Chrome debug must reference devtools:build:chrome"
assert "devtools:build:firefox" in firefox_debug, \
    "Firefox debug must reference devtools:build:firefox"

print("PASS")
""")
    assert r.returncode == 0, f"debug scripts validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_sourcemap_inline_for_injected_scripts():
    """Injected script esbuild targets use sourcemap = 'inline' and no hardcoded minify."""
    r = _run_py(r"""
import re

content = open("devtools/projects/shell-browser/src/app/BUILD.bazel").read()

def extract_esbuild_blocks(text):
    blocks = []
    for m in re.finditer(r'\besbuild\s*\(', text):
        start = m.end()
        depth = 0
        for j in range(start, len(text)):
            if text[j] == '(':
                depth += 1
            elif text[j] == ')':
                if depth == 0:
                    blocks.append(text[start:j])
                    break
                depth -= 1
    return blocks

injected_scripts = ["detect-angular.ts", "backend.ts", "ng-validate.ts", "content-script.ts"]
blocks = extract_esbuild_blocks(content)

for script in injected_scripts:
    matching = [b for b in blocks if script in b]
    assert len(matching) >= 1, f"No esbuild target found for {script}"
    block = matching[0]
    # Must have sourcemap = "inline"
    assert re.search(r'''sourcemap\s*=\s*["']inline["']''', block), \
        f"esbuild target for {script} must have sourcemap = 'inline'"
    # Must NOT have hardcoded minify = True
    assert not re.search(r'minify\s*=\s*True', block), \
        f"esbuild target for {script} must not hardcode minify = True"

print("PASS")
""")
    assert r.returncode == 0, f"sourcemap validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_no_hardcoded_minify_in_shell_browser_src():
    """shell-browser/src/BUILD.bazel esbuild calls have no hardcoded minify = True."""
    r = _run_py(r"""
import re

content = open("devtools/projects/shell-browser/src/BUILD.bazel").read()

esbuild_matches = list(re.finditer(r'\besbuild\s*\(', content))
assert len(esbuild_matches) > 0, "Must have at least one esbuild call"

for m in esbuild_matches:
    start = m.end()
    depth = 0
    block = None
    for j in range(start, len(content)):
        if content[j] == '(':
            depth += 1
        elif content[j] == ')':
            if depth == 0:
                block = content[start:j]
                break
            depth -= 1
    assert block is not None, f"Could not parse esbuild block at char {m.start()}"
    assert not re.search(r'minify\s*=\s*True', block), \
        f"esbuild call at char {m.start()} must not have minify = True"

print("PASS")
""")
    assert r.returncode == 0, f"minify validation failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------


def test_existing_release_scripts_intact():
    """Existing release build scripts still present in package.json."""
    pkg = json.loads((Path(REPO) / "package.json").read_text())
    scripts = pkg.get("scripts", {})
    assert "devtools:build:chrome:release" in scripts, \
        "devtools:build:chrome:release script must still exist"
    assert "devtools:build:firefox:release" in scripts, \
        "devtools:build:firefox:release script must still exist"
    assert "devtools:build:chrome" in scripts, \
        "devtools:build:chrome base script must still exist"
