"""
Task: playwright-feat-raw-output-piping
Repo: microsoft/playwright @ f6e14f9d73b46ab319b334c013094d867d4ef149
PR:   40010

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/playwright"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_response_raw_mode():
    """Response class serialize() filters sections and strips markdown in raw mode."""
    r = subprocess.run(
        ["python3", "-c", """
import sys

src = open('/workspace/playwright/packages/playwright-core/src/tools/backend/response.ts').read()

# 1. Constructor must accept options object with raw (not positional relativeTo string)
if 'options?' not in src:
    print("FAIL: Constructor must accept options parameter")
    sys.exit(1)
if 'raw?' not in src:
    print("FAIL: Constructor options must include raw")
    sys.exit(1)

# 2. _raw field must be declared
if '_raw' not in src:
    print("FAIL: Response must have _raw field")
    sys.exit(1)

# 3. serialize() must define rawSections allowlist and filter
serialize_idx = src.find('async serialize')
if serialize_idx < 0:
    print("FAIL: serialize method not found")
    sys.exit(1)
serialize_body = src[serialize_idx:serialize_idx + 2000]

if 'rawSections' not in serialize_body:
    print("FAIL: serialize must define rawSections allowlist")
    sys.exit(1)

for name in ['Error', 'Result', 'Snapshot']:
    if f"'{name}'" not in serialize_body:
        print(f"FAIL: rawSections must include '{name}'")
        sys.exit(1)

if '.filter(' not in serialize_body:
    print("FAIL: serialize must filter sections based on rawSections")
    sys.exit(1)

# 4. Raw mode must skip markdown headers and code fences
if 'this._raw' not in serialize_body:
    print("FAIL: serialize must branch on _raw for formatting")
    sys.exit(1)

# Normal mode still emits ### headers
if '###' not in serialize_body:
    print("FAIL: normal mode must still emit ### headers")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Response raw mode check failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_raw_global_cli_option():
    """Raw option flows through entire CLI pipeline: program -> session -> daemon -> backend."""
    r = subprocess.run(
        ["python3", "-c", """
import sys

# --- program.ts ---
prog = open('/workspace/playwright/packages/playwright-core/src/tools/cli-client/program.ts').read()

if "raw?" not in prog:
    print("FAIL: program.ts GlobalOptions must include raw")
    sys.exit(1)

# 'raw' must be in both globalOptions and booleanOptions arrays
if prog.count("'raw'") < 2:
    print(f"FAIL: 'raw' must appear in globalOptions and booleanOptions (found {prog.count(chr(39)+'raw'+chr(39))})")
    sys.exit(1)

if "args.raw" not in prog:
    print("FAIL: program.ts must extract raw from args")
    sys.exit(1)

# --- session.ts ---
session = open('/workspace/playwright/packages/playwright-core/src/tools/cli-client/session.ts').read()

if "raw?" not in session:
    print("FAIL: session.ts run() must accept raw option")
    sys.exit(1)

if "raw: options" not in session:
    print("FAIL: session.ts must forward raw to daemon")
    sys.exit(1)

# --- daemon.ts ---
daemon = open('/workspace/playwright/packages/playwright-core/src/tools/cli-daemon/daemon.ts').read()

if "raw: params.raw" not in daemon:
    print("FAIL: daemon.ts must pass raw: params.raw in _meta")
    sys.exit(1)

# --- browserBackend.ts ---
backend = open('/workspace/playwright/packages/playwright-core/src/tools/backend/browserBackend.ts').read()

if "_meta?.raw" not in backend:
    print("FAIL: browserBackend.ts must extract raw from _meta")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Raw CLI pipeline check failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_evaluate_catches_errors():
    """evaluate tool catches expression errors and adds them to response."""
    r = subprocess.run(
        ["python3", "-c", """
import sys

src = open('/workspace/playwright/packages/playwright-core/src/tools/backend/evaluate.ts').read()

# Must call response.addError in a catch handler
if 'addError' not in src:
    print("FAIL: evaluate must call response.addError on caught error")
    sys.exit(1)

if '.catch(' not in src:
    print("FAIL: evaluate must have .catch() error handler")
    sys.exit(1)

# Must distinguish Error instances from other thrown values
if 'instanceof Error' not in src:
    print("FAIL: error handler must check instanceof Error")
    sys.exit(1)

if 'e.message' not in src:
    print("FAIL: must extract .message from Error instances")
    sys.exit(1)

if 'String(e)' not in src:
    print("FAIL: must use String(e) for non-Error thrown values")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Evaluate error handling check failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_help_text_includes_raw():
    """Help generator displays --raw in global options."""
    r = subprocess.run(
        ["python3", "-c", """
import sys

src = open('/workspace/playwright/packages/playwright-core/src/tools/cli-daemon/helpGenerator.ts').read()

if '--raw' not in src:
    print("FAIL: helpGenerator must include --raw option")
    sys.exit(1)

if 'result value' not in src:
    print("FAIL: --raw help text must describe outputting result value")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Help text check failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_skill_md_documents_raw_output():
    """SKILL.md documents --raw option with purpose and usage examples."""
    r = subprocess.run(
        ["python3", "-c", """
import sys

src = open('/workspace/playwright/packages/playwright-core/src/tools/cli-client/skill/SKILL.md').read()
lower = src.lower()

# Must have a raw output section
if '## raw' not in lower:
    print("FAIL: SKILL.md must have a Raw output section heading")
    sys.exit(1)

# Must document the --raw flag
if '--raw' not in src:
    print("FAIL: SKILL.md must document --raw flag")
    sys.exit(1)

# Must explain piping / result-only purpose
if 'pipe' not in lower and 'result' not in lower:
    print("FAIL: SKILL.md must explain that --raw enables piping or returns result value")
    sys.exit(1)

# Must include usage examples
if 'playwright-cli --raw' not in src:
    print("FAIL: SKILL.md must include usage examples with playwright-cli --raw")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"SKILL.md check failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Response serialize method has real conditional logic, not a stub."""
    response_src = Path(REPO) / "packages/playwright-core/src/tools/backend/response.ts"
    content = response_src.read_text()

    # serialize must have meaningful branching logic
    serialize_start = content.find("async serialize")
    assert serialize_start > 0, "Response must have serialize method"

    serialize_body = content[serialize_start:serialize_start + 2000]

    # Must have at least one conditional branch (not just return/pass)
    assert "if" in serialize_body, "serialize must have conditional logic"

    # Must have section filtering logic (not trivial)
    assert "filter" in serialize_body or "section" in serialize_body, \
        "serialize must have section filtering logic"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI commands that must pass at base commit
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo ESLint passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "eslint"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_build():
    """Repo builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_check_deps():
    """Repo dependency check passes (pass_to_pass) — verifies DEPS structure."""
    r = subprocess.run(
        ["npm", "run", "check-deps"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Dependency check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_packages():
    """Repo package lint passes (pass_to_pass) — verifies workspace consistency."""
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Package lint failed:\n{r.stderr[-500:]}"
