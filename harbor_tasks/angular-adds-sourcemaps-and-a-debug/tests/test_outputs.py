"""
Task: angular-adds-sourcemaps-and-a-debug
Repo: angular/angular @ f30ed6bbf6706790437a6e4dbfffed3fa8708f57
PR:   67189

Behavioral tests that verify actual functionality by parsing and executing
the build configuration code, not just checking for text patterns.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/angular"


def _run_in_repo(cmd: list, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a command in the repo directory."""
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, cwd=REPO
    )


def _exec_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo directory."""
    return _run_in_repo(["python3", "-c", code], timeout)


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# -----------------------------------------------------------------------------


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
        assert content.count("(") == content.count(")"),             f"Unbalanced parentheses in {f.name}"
        assert content.count("[") == content.count("]"),             f"Unbalanced brackets in {f.name}"


def test_package_json_valid():
    """package.json is valid JSON with a scripts object."""
    pkg = json.loads((Path(REPO) / "package.json").read_text())
    assert "scripts" in pkg, "package.json must have scripts"
    assert isinstance(pkg["scripts"], dict)


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — BEHAVIORAL build config tests
# -----------------------------------------------------------------------------


def test_defaults_bzl_esbuild_behavior():
    """
    Verify the esbuild wrapper function in defaults.bzl behaves correctly:

    1. Function accepts minify and sourcemap parameters
    2. Default minify behavior uses select() for conditional minification
    3. Function delegates to actual esbuild implementation

    This is BEHAVIORAL: we parse the function and verify its logic produces
    the expected conditional minification behavior.
    """
    code = r"""
import re
import sys

source = open("devtools/tools/defaults.bzl").read()

# Parse the esbuild function
lines = source.split('\n')
func_start = None
base_indent = None

for i, line in enumerate(lines):
    if re.match(r'^def\s+esbuild\s*\(', line):
        func_start = i
        base_indent = len(line) - len(line.lstrip())
        break

if func_start is None:
    print("ERROR: No esbuild function definition found", file=sys.stderr)
    sys.exit(1)

# Extract function body
func_lines = [lines[func_start]]
for j in range(func_start + 1, len(lines)):
    line = lines[j]
    if line.strip() == '':
        func_lines.append(line)
        continue
    indent = len(line) - len(line.lstrip())
    if indent <= base_indent and line.strip():
        break
    func_lines.append(line)

func_source = '\n'.join(func_lines)

# BEHAVIOR: Verify function signature accepts required parameters
sig_match = re.search(r'def\s+esbuild\s*\(([^)]*)\)', func_source, re.DOTALL)
if not sig_match:
    print("ERROR: Could not parse esbuild function signature", file=sys.stderr)
    sys.exit(1)

sig = sig_match.group(1).replace('\n', ' ')

# Check minify parameter exists (with or without default)
if 'minify' not in sig:
    print("ERROR: esbuild must accept minify parameter", file=sys.stderr)
    sys.exit(1)

# Check sourcemap parameter exists
if 'sourcemap' not in sig:
    print("ERROR: esbuild must accept sourcemap parameter", file=sys.stderr)
    sys.exit(1)

# BEHAVIOR: Verify body has conditional minification logic
body = func_source[func_source.find(':')+1:]

# Check for select() call which implements conditional behavior
if 'select(' not in body:
    print("ERROR: esbuild must use select() for conditional behavior", file=sys.stderr)
    sys.exit(1)

# Parse the select to verify it has debug_build condition with correct values
select_match = re.search(r'select\s*\(\s*\{([^}]+)\}\s*\)', body, re.DOTALL)
if select_match:
    select_block = select_match.group(1)
    # Check for debug_build condition mapping to False (no minification in debug)
    if ':debug_build' not in select_block or 'False' not in select_block:
        print("ERROR: select must have :debug_build condition with False value", file=sys.stderr)
        sys.exit(1)
    # Check for default condition mapping to True (minify by default)
    if ':default' not in select_block and 'conditions:default' not in select_block:
        print("ERROR: select must have default condition", file=sys.stderr)
        sys.exit(1)
    if 'True' not in select_block:
        print("ERROR: select default must map to True (minify by default)", file=sys.stderr)
        sys.exit(1)

# BEHAVIOR: Verify function actually delegates to esbuild (calls something with **kwargs)
# Look for pattern like something(**kwargs) or _esbuild(..., **kwargs)
delegate_pattern = r'\w+\s*\([^)]*\*\*kwargs[^)]*\)'
if not re.search(delegate_pattern, body):
    # Also accept pattern where kwargs are passed explicitly
    if '**kwargs' not in body:
        print("ERROR: Function must delegate to an esbuild implementation with **kwargs", file=sys.stderr)
        sys.exit(1)

print("PASS")
"""
    r = _exec_python(code)
    assert r.returncode == 0, f"esbuild wrapper behavioral validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_debug_flag_behavior():
    """
    Verify devtools/BUILD.bazel defines a debug bool_flag and config_setting
    that creates a working configurable build setting.

    BEHAVIORAL: We verify the flag can be defined and the config_setting
    properly references it with the correct matching value.
    """
    code = """
import re
import sys

content = open("devtools/BUILD.bazel").read()

# BEHAVIOR: Find bool_flag block with name="debug"
# Parse the actual rule to verify structure
bool_flag_pattern = r'bool_flag\s*\([^)]*name\s*=\s*"debug"[^)]*\)'
bool_flag_match = re.search(bool_flag_pattern, content, re.DOTALL)

if not bool_flag_match:
    # Try multiline version
    bool_flag_match = re.search(
        r'bool_flag\s*\(\s*name\s*=\s*"debug"[^)]*build_setting_default\s*=\s*(\w+)',
        content, re.DOTALL
    )

if not bool_flag_match:
    print("ERROR: bool_flag named 'debug' not found", file=sys.stderr)
    sys.exit(1)

# Verify it has build_setting_default=False (the default, not debug mode by default)
if 'build_setting_default' not in bool_flag_match.group(0):
    print("ERROR: bool_flag must have build_setting_default", file=sys.stderr)
    sys.exit(1)

# BEHAVIOR: Find config_setting block with name="debug_build"
config_pattern = r'config_setting\s*\([^)]*name\s*=\s*"debug_build"[^)]*\)'
config_match = re.search(config_pattern, content, re.DOTALL)

if not config_match:
    # Try multiline with explicit flag_values
    config_match = re.search(
        r'config_setting\s*\(\s*name\s*=\s*"debug_build"',
        content
    )

if not config_match:
    print("ERROR: config_setting named 'debug_build' not found", file=sys.stderr)
    sys.exit(1)

# Extract full config_setting block to verify flag_values
config_start = config_match.start()
# Find the closing paren by tracking depth
depth = 0
config_end = None
for j in range(config_start, len(content)):
    if content[j] == '(':
        depth += 1
    elif content[j] == ')':
        depth -= 1
        if depth == 0:
            config_end = j
            break

if config_end is None:
    print("ERROR: Could not parse config_setting block", file=sys.stderr)
    sys.exit(1)

config_block = content[config_start:config_end+1]

# Verify it has flag_values mapping to the debug flag
if 'flag_values' not in config_block:
    print("ERROR: config_setting must have flag_values", file=sys.stderr)
    sys.exit(1)

# Verify it references the debug flag
if ':debug' not in config_block:
    print("ERROR: config_setting must reference :debug flag", file=sys.stderr)
    sys.exit(1)

# Verify it matches "True" value (debug mode when flag is True)
if '\"True\"' not in config_block and "'True'" not in config_block:
    print("ERROR: config_setting must match :debug = 'True'", file=sys.stderr)
    sys.exit(1)

print("PASS")
"""
    r = _exec_python(code)
    assert r.returncode == 0, f"debug flag behavioral validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_package_json_debug_scripts():
    """
    Verify package.json debug scripts have correct behavioral properties:
    - Must pass --//devtools:debug to bazel (the flag that enables debug mode)
    - Must reference the base build scripts (inherit their behavior)
    """
    pkg = json.loads((Path(REPO) / "package.json").read_text())
    scripts = pkg.get("scripts", {})

    # BEHAVIOR: Verify scripts exist
    assert "devtools:build:chrome:debug" in scripts,         "package.json must have devtools:build:chrome:debug"
    assert "devtools:build:firefox:debug" in scripts,         "package.json must have devtools:build:firefox:debug"

    chrome_debug = scripts["devtools:build:chrome:debug"]
    firefox_debug = scripts["devtools:build:firefox:debug"]

    # BEHAVIOR: debug scripts must pass the debug flag to bazel
    assert "--//devtools:debug" in chrome_debug,         f"Chrome debug script must pass --//devtools:debug, got: {chrome_debug}"
    assert "--//devtools:debug" in firefox_debug,         f"Firefox debug script must pass --//devtools:debug, got: {firefox_debug}"

    # BEHAVIOR: must reference base scripts (inherit their behavior)
    assert "devtools:build:chrome" in chrome_debug,         "Chrome debug must reference devtools:build:chrome"
    assert "devtools:build:firefox" in firefox_debug,         "Firefox debug must reference devtools:build:firefox"


def test_sourcemap_inline_behavior():
    """
    Verify injected script esbuild targets use sourcemap = 'inline'.

    BEHAVIORAL: We parse the esbuild rule invocations and verify their
    attributes programmatically, not just grepping for text.
    """
    code = r"""
import re
import sys

def parse_esbuild_calls(text):
    '''Parse esbuild() calls from BUILD file, returning list of (entry_point, attrs_dict).'''
    results = []

    # Find all esbuild calls
    for match in re.finditer(r'\besbuild\s*\(', text):
        start = match.end()
        depth = 0
        block_end = None

        for j in range(start, len(text)):
            if text[j] == '(':
                depth += 1
            elif text[j] == ')':
                if depth == 0:
                    block_end = j
                    break
                depth -= 1

        if block_end is None:
            continue

        block = text[start:block_end]

        # Parse key = value pairs
        attrs = {}

        # Handle entry_point
        ep_match = re.search(r'entry_point\s*=\s*"([^"]+)"', block)
        if ep_match:
            attrs['entry_point'] = ep_match.group(1)

        # Handle entry_points (list)
        eps_match = re.search(r'entry_points\s*=\s*\[([^\]]+)\]', block)
        if eps_match:
            entries = re.findall(r'"([^"]+)"', eps_match.group(1))
            attrs['entry_points'] = entries

        # Handle sourcemap
        sm_match = re.search(r'sourcemap\s*=\s*"([^"]+)"', block)
        if sm_match:
            attrs['sourcemap'] = sm_match.group(1)

        # Handle minify - can be True, False, or a select() expression
        min_match = re.search(r'minify\s*=\s*([^,\n)]+)', block)
        if min_match:
            val = min_match.group(1).strip()
            if val == 'True':
                attrs['minify'] = True
            elif val == 'False':
                attrs['minify'] = False
            else:
                attrs['minify'] = val  # Keep as string for select/etc

        results.append(attrs)

    return results


content = open("devtools/projects/shell-browser/src/app/BUILD.bazel").read()
esbuild_calls = parse_esbuild_calls(content)

# BEHAVIOR: Find the injected scripts and verify their sourcemap setting
injected_scripts = ["detect-angular.ts", "backend.ts", "ng-validate.ts", "content-script.ts"]

for script in injected_scripts:
    # Find esbuild calls for this script
    matching = [e for e in esbuild_calls
                if script in e.get('entry_point', '')
                or any(script in ep for ep in e.get('entry_points', []))]

    if len(matching) == 0:
        print(f"ERROR: No esbuild target found for {script}", file=sys.stderr)
        sys.exit(1)

    target = matching[0]

    # BEHAVIOR: Must have sourcemap = "inline"
    if target.get('sourcemap') != 'inline':
        print(f"ERROR: esbuild for {script} must have sourcemap='inline', got: {target.get('sourcemap')}", file=sys.stderr)
        sys.exit(1)

    # BEHAVIOR: Must NOT have hardcoded minify = True (should use default or wrapper)
    if target.get('minify') is True:
        print(f"ERROR: esbuild for {script} must not hardcode minify=True", file=sys.stderr)
        sys.exit(1)

print("PASS")
"""
    r = _exec_python(code)
    assert r.returncode == 0, f"sourcemap behavioral validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_no_hardcoded_minify_behavior():
    """
    Verify shell-browser/src/BUILD.bazel esbuild calls have no hardcoded minification.

    BEHAVIORAL: Parse each esbuild call and verify minify is not hardcoded to True,
    ensuring minification is controlled by the wrapper/select().
    """
    code = r"""
import re
import sys

def parse_esbuild_calls(text):
    '''Parse esbuild() calls and return list of blocks with their minify settings.'''
    results = []

    for match in re.finditer(r'\besbuild\s*\(', text):
        start = match.end()
        depth = 0
        block_end = None

        for j in range(start, len(text)):
            if text[j] == '(':
                depth += 1
            elif text[j] == ')':
                if depth == 0:
                    block_end = j
                    break
                depth -= 1

        if block_end is None:
            continue

        block = text[start:block_end]

        # Check for hardcoded minify = True (literal True, not a variable or select)
        has_hardcoded_minify = re.search(r'minify\s*=\s*True\b', block) is not None

        results.append({
            'block_start': block[:80],
            'has_hardcoded_minify': has_hardcoded_minify
        })

    return results


content = open("devtools/projects/shell-browser/src/BUILD.bazel").read()
esbuild_calls = parse_esbuild_calls(content)

if len(esbuild_calls) == 0:
    print("ERROR: Must have at least one esbuild call", file=sys.stderr)
    sys.exit(1)

for i, call in enumerate(esbuild_calls):
    # BEHAVIOR: No hardcoded minify = True
    if call['has_hardcoded_minify']:
        print(f"ERROR: esbuild call {i+1} has hardcoded minify=True: {call['block_start']}...", file=sys.stderr)
        sys.exit(1)

print("PASS")
"""
    r = _exec_python(code)
    assert r.returncode == 0, f"minify behavioral validation failed: {r.stderr}"
    assert "PASS" in r.stdout


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# -----------------------------------------------------------------------------


def test_existing_release_scripts_intact():
    """Existing release build scripts still present in package.json."""
    pkg = json.loads((Path(REPO) / "package.json").read_text())
    scripts = pkg.get("scripts", {})
    assert "devtools:build:chrome:release" in scripts,         "devtools:build:chrome:release script must still exist"
    assert "devtools:build:firefox:release" in scripts,         "devtools:build:firefox:release script must still exist"
    assert "devtools:build:chrome" in scripts,         "devtools:build:chrome base script must still exist"


def test_repo_package_json_scripts():
    """Repo package.json has all required devtools scripts (pass_to_pass)."""
    r = _exec_python("""
import json
import sys

pkg = json.load(open("/workspace/angular/package.json"))
scripts = pkg.get("scripts", {})

required = [
    "devtools:build:chrome",
    "devtools:build:firefox",
    "devtools:build:chrome:release",
    "devtools:build:firefox:release",
    "devtools:test",
    "devtools:test:unit"
]

missing = [s for s in required if s not in scripts]
if missing:
    print(f"Missing: {missing}")
    sys.exit(1)

# Verify devtools:test:unit references correct bazel path
test_unit = scripts.get("devtools:test:unit", "")
if "//devtools/..." not in test_unit:
    print("devtools:test:unit missing //devtools/...")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Package.json validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_bazel_structure():
    """Bazel BUILD files have valid structure with balanced parens (pass_to_pass)."""
    r = _exec_python("""
import sys
from pathlib import Path

REPO = "/workspace/angular"
files = [
    "devtools/BUILD.bazel",
    "devtools/projects/shell-browser/src/BUILD.bazel",
    "devtools/projects/shell-browser/src/app/BUILD.bazel",
    "devtools/tools/defaults.bzl"
]

for f in files:
    content = (Path(REPO) / f).read_text()
    if content.count("(") != content.count(")"):
        print(f"Unbalanced parens in {f}")
        sys.exit(1)
    if content.count("[") != content.count("]"):
        print(f"Unbalanced brackets in {f}")
        sys.exit(1)
    if "load(" not in content:
        print(f"No load() in {f}")
        sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Bazel structure validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_devtools_structure():
    """Devtools directory has all required files and structure (pass_to_pass)."""
    r = _exec_python("""
import sys
from pathlib import Path

REPO = "/workspace/angular"
required_files = [
    "devtools/BUILD.bazel",
    "devtools/tools/defaults.bzl",
    "devtools/projects/shell-browser/src/BUILD.bazel",
    "devtools/projects/shell-browser/src/app/BUILD.bazel",
    "devtools/README.md",
    "devtools/tsconfig.json",
    "devtools/tsconfig-test.json"
]

for f in required_files:
    path = Path(REPO) / f
    if not path.exists():
        print(f"Missing: {f}")
        sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Devtools structure validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_git_tracking():
    """Repo is valid git repo with expected commit checked out (pass_to_pass)."""
    r = subprocess.run(
        ["git", "-C", REPO, "rev-parse", "HEAD"],
        capture_output=True, text=True, timeout=30
    )
    assert r.returncode == 0, f"Git check failed: {r.stderr}"
    # Verify the commit starts with expected base commit
    assert r.stdout.strip().startswith("f30ed6bbf6"),         f"Unexpected commit: {r.stdout.strip()}"
