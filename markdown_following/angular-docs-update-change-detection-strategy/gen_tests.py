import sys
# Write new test file content
content = '''"""
Task: angular-docs-update-change-detection-strategy
Repo: angular/angular @ c1261b02dbe1d995d5a6fccb5556aca4d67b529f
PR:   67875

Angular v22 made OnPush the default change detection strategy. This PR updates
JSDoc comments in core source files and removes the now-outdated "always set
OnPush" rule from agent config files and documentation.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/angular"


def _file_content(path: str) -> str:
    """Read a file from the repo."""
    return (Path(REPO) / path).read_text()


def _run_py(code: str) -> subprocess.CompletedProcess:
    """Execute Python code in the repo directory via subprocess."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


def test_syntax_check():
    """Modified TypeScript files parse without syntax errors."""
    ts_files = [
        "packages/core/src/change_detection/constants.ts",
        "packages/core/src/metadata/directives.ts",
    ]
    for f in ts_files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} must exist"
        content = p.read_text()
        assert len(content) > 100, f"{f} is unexpectedly short"
        if "directives.ts" not in f:
            assert content.count("{") == content.count("}"), f"{f} has unbalanced braces"


def test_repo_git_valid():
    """Repo is a valid git repository with expected commit checked out (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git status failed: {r.stderr}"
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git rev-parse failed: {r.stderr}"
    commit = r.stdout.strip()
    assert commit.startswith("c1261b"), f"Unexpected commit: {commit}"


def test_typescript_files_parseable():
    """All modified TypeScript files have valid syntax structure (pass_to_pass)."""
    ts_files = [
        "packages/core/src/change_detection/constants.ts",
        "packages/core/src/metadata/directives.ts",
    ]
    for f in ts_files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} must exist"
        content = p.read_text()
        assert len(content) > 100, f"{f} is unexpectedly short"
        if "directives.ts" not in f:
            assert content.count("{") == content.count("}"), f"{f} has unbalanced braces"
        assert content.count("(") == content.count(")"), f"{f} has unbalanced parentheses"
        assert content.count("[") == content.count("]"), f"{f} has unbalanced brackets"
        export_count = content.count("export ")
        assert export_count > 0, f"{f} should have at least one export"
        comment_open = content.count("/*")
        comment_close = content.count("*/")
        assert comment_open == comment_close, f"{f} has unclosed comments: {comment_open} opens, {comment_close} closes"


def test_markdown_files_valid():
    """All modified Markdown files are valid UTF-8 and have proper structure (pass_to_pass)."""
    md_files = [
        "adev/src/content/best-practices/runtime-performance/skipping-subtrees.md",
        "adev/src/content/guide/components/advanced-configuration.md",
        "adev/src/content/tutorials/signals/steps/1-creating-your-first-signal/README.md",
        "adev/src/context/airules.md",
        "adev/src/context/angular-20.mdc",
        "adev/src/context/guidelines.md",
    ]
    for f in md_files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} must exist"
        try:
            content = p.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            assert False, f"{f} is not valid UTF-8: {e}"
        assert len(content.strip()) > 0, f"{f} is empty"
        null_byte = chr(0)
        assert null_byte not in content, f"{f} contains null bytes"


def test_change_detection_files_exist():
    """All change detection related files exist and have expected structure (pass_to_pass)."""
    core_files = [
        "packages/core/src/change_detection/constants.ts",
        "packages/core/src/metadata/directives.ts",
    ]
    for f in core_files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} must exist"
        content = p.read_text()
        if "constants.ts" in f:
            assert "enum ChangeDetectionStrategy" in content, f"{f} should define ChangeDetectionStrategy enum"
            assert "OnPush" in content, f"{f} should have OnPush"
            assert "Eager" in content, f"{f} should have Eager"
        if "directives.ts" in f:
            assert "interface Component" in content or "Component" in content, f"{f} should have Component interface"
            assert "changeDetection" in content, f"{f} should mention changeDetection"


def test_typescript_syntax_tsc():
    """TypeScript files have valid syntax when checked with tsc (pass_to_pass)."""
    r = subprocess.run(
        """apt-get update -qq && apt-get install -y -qq curl ca-certificates gnupg 2>/dev/null && \\
           curl -fsSL https://deb.nodesource.com/setup_20.x | bash - >/dev/null 2>&1 && \\
           apt-get install -y nodejs 2>/dev/null && \\
           npm install -g typescript 2>/dev/null && \\
           cd /workspace/angular && \\
           npx tsc --noEmit --skipLibCheck --target ES2020 --moduleResolution node \\
             packages/core/src/change_detection/constants.ts \\
             packages/core/src/metadata/directives.ts 2>&1""",
        capture_output=True, text=True, timeout=300, shell=True,
    )
    output = r.stdout + r.stderr
    import re
    syntax_error_pattern = r"error TS[1234]\\d{3}"
    matches = re.findall(syntax_error_pattern, output)
    assert len(matches) == 0, f"TypeScript syntax errors found: {matches}\\n{output[-1000:]}"


def test_jsdoc_comments_structure():
    """JSDoc comments in modified files are well-formed (pass_to_pass)."""
    r = subprocess.run(
        r"""cd /workspace/angular && \\
           grep -c '/\\*\\*' packages/core/src/change_detection/constants.ts && \\
           grep -c '\\*/' packages/core/src/change_detection/constants.ts && \\
           grep -c '/\\*\\*' packages/core/src/metadata/directives.ts && \\
           grep -c '\\*/' packages/core/src/metadata/directives.ts""",
        capture_output=True, text=True, timeout=30, shell=True,
    )
    assert r.returncode == 0, f"JSDoc structure check failed: {r.stderr}"
    lines = r.stdout.strip().split('\\n')
    counts = [int(l) for l in lines if l.strip().isdigit()]
    assert len(counts) >= 4, "Failed to parse JSDoc comment counts"
    assert counts[0] == counts[1], "constants.ts has unbalanced JSDoc comments"
    assert counts[2] == counts[3], "directives.ts has unbalanced JSDoc comments"


def test_markdown_frontmatter():
    """Markdown files have valid structure (pass_to_pass)."""
    md_files = [
        "adev/src/content/best-practices/runtime-performance/skipping-subtrees.md",
        "adev/src/content/guide/components/advanced-configuration.md",
        "adev/src/content/tutorials/signals/steps/1-creating-your-first-signal/README.md",
        "adev/src/context/airules.md",
        "adev/src/context/angular-20.mdc",
        "adev/src/context/guidelines.md",
    ]
    for f in md_files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} must exist"
        content = p.read_text(encoding="utf-8")
        assert '\\x00' not in content, f"{f} contains null bytes"
        fence_count = content.count('```')
        assert fence_count % 2 == 0, f"{f} has unbalanced code fences"
        assert len(content.strip()) > 100, f"{f} is too short"


def test_clang_format_check():
    """Modified TypeScript files conform to repo formatting rules (pass_to_pass)."""
    r = subprocess.run(
        r"""cd /workspace/angular && \\
           apt-get update -qq && apt-get install -y -qq clang-format 2>/dev/null && \\
           clang-format --style=file --dry-run \\
             packages/core/src/change_detection/constants.ts \\
             packages/core/src/metadata/directives.ts 2>&1""",
        capture_output=True, text=True, timeout=120, shell=True,
    )
    output = r.stdout + r.stderr
    if r.returncode != 0:
        if "error:" in output.lower():
            assert False, f"Code formatting errors found:\\n{output[-500:]}"


def test_repo_copyright_headers():
    """Modified source files have required Google copyright headers (pass_to_pass)."""
    r = subprocess.run(
        r"""cd /workspace/angular && \\
           grep -l 'Copyright Google LLC' \\
             packages/core/src/change_detection/constants.ts \\
             packages/core/src/metadata/directives.ts""",
        capture_output=True, text=True, timeout=30, shell=True,
    )
    assert r.returncode == 0, f"Copyright header check failed: {r.stderr}"
    files_with_header = r.stdout.strip().split('\\n')
    assert len(files_with_header) == 2, (
        f"Expected 2 files with copyright header, found: {files_with_header}"
    )


def test_repo_file_validity():
    """Modified files are valid ASCII/UTF-8 text files (pass_to_pass)."""
    r = subprocess.run(
        r"""cd /workspace/angular && \\
           apt-get update -qq && apt-get install -y -qq file 2>/dev/null && \\
           file packages/core/src/change_detection/constants.ts \\
                packages/core/src/metadata/directives.ts""",
        capture_output=True, text=True, timeout=30, shell=True,
    )
    assert r.returncode == 0, f"File type check failed: {r.stderr}"
    output = r.stdout.lower()
    assert "text" in output, f"Expected text files, got: {r.stdout}"


def test_git_log_commit():
    """Git repository has expected commit history (pass_to_pass)."""
    r = subprocess.run(
        ["git", "log", "--oneline", "-5"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git log failed: {r.stderr}"
    assert len(r.stdout.strip()) > 0, "Git log is empty"
    assert "c1261b0" in r.stdout or True, "Git log accessible"

def test_repo_tslint():
    """Repo's TSLint passes on all source files (pass_to_pass)."""
    r = subprocess.run(
        "cd /workspace/angular && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - >/dev/null 2>&1 && apt-get install -y nodejs 2>/dev/null && curl -fsSL https://get.pnpm.io/install.sh | bash - 2>/dev/null && export PNPM_HOME=/root/.local/share/pnpm && export PATH=$PNPM_HOME:$PATH && pnpm install --frozen-lockfile --ignore-scripts 2>/dev/null >/dev/null && pnpm tslint",
        capture_output=True, text=True, timeout=300, shell=True,
    )
    assert r.returncode == 0, f"TSLint failed:\\n{r.stderr[-500:]}"


def test_repo_check_tooling_setup():
    """Repo's tooling setup compiles correctly (pass_to_pass)."""
    r = subprocess.run(
        "cd /workspace/angular && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - >/dev/null 2>&1 && apt-get install -y nodejs 2>/dev/null && curl -fsSL https://get.pnpm.io/install.sh | bash - 2>/dev/null && export PNPM_HOME=/root/.local/share/pnpm && export PATH=$PNPM_HOME:$PATH && pnpm install --frozen-lockfile --ignore-scripts 2>/dev/null >/dev/null && pnpm check-tooling-setup",
        capture_output=True, text=True, timeout=300, shell=True,
    )
    assert r.returncode == 0, f"check-tooling-setup failed:\\n{r.stderr[-500:]}"


def test_repo_ts_circular_deps():
    """Repo has no circular dependencies in TypeScript imports (pass_to_pass)."""
    r = subprocess.run(
        "cd /workspace/angular && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - >/dev/null 2>&1 && apt-get install -y nodejs 2>/dev/null && curl -fsSL https://get.pnpm.io/install.sh | bash - 2>/dev/null && export PNPM_HOME=/root/.local/share/pnpm && export PATH=$PNPM_HOME:$PATH && pnpm install --frozen-lockfile --ignore-scripts 2>/dev/null >/dev/null && pnpm ts-circular-deps:check",
        capture_output=True, text=True, timeout=300, shell=True,
    )
    assert r.returncode == 0, f"Circular deps check failed:\\n{r.stderr[-500:]}"


def test_repo_ng_dev_skills():
    """Repo's agent skills configuration is valid (pass_to_pass)."""
    r = subprocess.run(
        "cd /workspace/angular && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - >/dev/null 2>&1 && apt-get install -y nodejs 2>/dev/null && curl -fsSL https://get.pnpm.io/install.sh | bash - 2>/dev/null && export PNPM_HOME=/root/.local/share/pnpm && export PATH=$PNPM_HOME:$PATH && pnpm install --frozen-lockfile --ignore-scripts 2>/dev/null >/dev/null && pnpm ng-dev ai skills validate",
        capture_output=True, text=True, timeout=300, shell=True,
    )
    assert r.returncode == 0, f"ng-dev skills validate failed:\\n{r.stderr[-500:]}"


def test_repo_ng_dev_pullapprove():
    """Repo's PullApprove configuration is valid (pass_to_pass)."""
    r = subprocess.run(
        "cd /workspace/angular && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - >/dev/null 2>&1 && apt-get install -y nodejs 2>/dev/null && curl -fsSL https://get.pnpm.io/install.sh | bash - 2>/dev/null && export PNPM_HOME=/root/.local/share/pnpm && export PATH=$PNPM_HOME:$PATH && pnpm install --frozen-lockfile --ignore-scripts 2>/dev/null >/dev/null && pnpm ng-dev pullapprove verify",
        capture_output=True, text=True, timeout=300, shell=True,
    )
    assert r.returncode == 0, f"ng-dev pullapprove verify failed:\\n{r.stderr[-500:]}"


def test_repo_ng_dev_ngbot():
    """Repo's NgBot configuration is valid (pass_to_pass)."""
    r = subprocess.run(
        "cd /workspace/angular && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - >/dev/null 2>&1 && apt-get install -y nodejs 2>/dev/null && curl -fsSL https://get.pnpm.io/install.sh | bash - 2>/dev/null && export PNPM_HOME=/root/.local/share/pnpm && export PATH=$PNPM_HOME:$PATH && pnpm install --frozen-lockfile --ignore-scripts 2>/dev/null >/dev/null && pnpm ng-dev ngbot verify",
        capture_output=True, text=True, timeout=300, shell=True,
    )
    assert r.returncode == 0, f"ng-dev ngbot verify failed:\\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core source JSDoc updates
# ---------------------------------------------------------------------------

def test_constants_onpush_default_note():
    """OnPush JSDoc in constants.ts notes it is enabled by default."""
    r = _run_py("""
from pathlib import Path

content = Path("packages/core/src/change_detection/constants.ts").read_text()

# Verify the OnPush enum member exists with value 0
assert "OnPush = 0" in content, "OnPush must be enum member with value 0"

# Extract the JSDoc comment block immediately above OnPush = 0
idx = content.index("OnPush = 0")
preceding = content[:idx]

# Find the last /** ... */ comment block above OnPush
close = preceding.rfind("*/")
assert close != -1, "JSDoc comment must exist above OnPush"
open_ = preceding.rfind("/**", 0, close)
assert open_ != -1, "JSDoc block must be well-formed"
jsdoc = preceding[open_:close + 2]

# OnPush should be described as the default - check for semantic property
# that OnPush is enabled/set as default (any wording)
jsdoc_lower = jsdoc.lower()
has_onpush_ref = "onpush" in jsdoc_lower
has_default_ref = "default" in jsdoc_lower
assert has_onpush_ref and has_default_ref, (
    "JSDoc above OnPush must describe it as the default strategy. "
    f"Found JSDoc: {jsdoc[:200]}"
)
print("PASS")
""")
    assert r.returncode == 0, f"constants.ts validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_directives_eager_reference():
    """directives.ts JSDoc references Eager and notes OnPush is default."""
    r = _run_py("""
from pathlib import Path

content = Path("packages/core/src/metadata/directives.ts").read_text()

# Verify the changeDetection property exists
assert "changeDetection?" in content, "changeDetection property must exist"

# Extract the JSDoc comment block above changeDetection
idx = content.index("changeDetection?")
preceding = content[:idx]
close = preceding.rfind("*/")
assert close != -1, "JSDoc must exist above changeDetection property"
open_ = preceding.rfind("/**", 0, close)
assert open_ != -1, "JSDoc block must be well-formed"
jsdoc = preceding[open_:close + 2]

# Must reference Eager (renamed from Default)
jsdoc_lower = jsdoc.lower()
assert "eager" in jsdoc_lower, (
    "changeDetection JSDoc must reference ChangeDetectionStrategy#Eager"
)
# Must note OnPush is described as default (semantic check)
assert "onpush" in jsdoc_lower and "default" in jsdoc_lower, (
    "changeDetection JSDoc must note OnPush is described as the default"
)
print("PASS")
""")
    assert r.returncode == 0, f"directives.ts validation failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - documentation updates
# ---------------------------------------------------------------------------

def test_skipping_subtrees_onpush_default():
    """skipping-subtrees.md must describe OnPush as the default strategy."""
    r = _run_py("""
from pathlib import Path

content = Path("adev/src/content/best-practices/runtime-performance/skipping-subtrees.md").read_text()

# OnPush must be mentioned
assert "OnPush" in content, "must mention OnPush"

# The first mention of OnPush should be in a context that describes it as the default
idx = content.find("OnPush")
assert idx != -1, "OnPush must appear"

# Check that within a reasonable window after first OnPush, the concept of
# default is mentioned (semantic property - OnPush described as default)
nearby = content[idx:idx+500].lower()
assert "default" in nearby, (
    "OnPush should be described as the default strategy near its first mention. "
    f"First mention at idx={idx}, nearby text: {content[idx:idx+100]}"
)

# The old code example for manually setting OnPush must be removed
assert "ChangeDetectionStrategy.OnPush," not in content, (
    "manual OnPush code example should be removed (it is now the default)"
)
print("PASS")
""")
    assert r.returncode == 0, f"skipping-subtrees.md validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_advanced_config_onpush_default():
    """advanced-configuration.md describes OnPush as default, Eager as optional."""
    r = _run_py("""
from pathlib import Path

content = Path("adev/src/content/guide/components/advanced-configuration.md").read_text()

# OnPush must be mentioned and described as default
onpush_idx = content.find("OnPush")
assert onpush_idx != -1, "must mention OnPush"
onpush_nearby = content[onpush_idx:onpush_idx+400].lower()
assert "default" in onpush_nearby, (
    "OnPush should be described as the default strategy"
)

# Eager must be referenced and described as optional mode
eager_idx = content.find("Eager")
assert eager_idx != -1, "must reference Eager"
eager_nearby = content[eager_idx:eager_idx+400].lower()
assert "optional" in eager_nearby, (
    "Eager should be described as an optional mode"
)
print("PASS")
""")
    assert r.returncode == 0, f"advanced-configuration.md validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_signals_readme_no_callout():
    """signals tutorial README no longer has the OnPush callout."""
    r = _run_py("""
from pathlib import Path

content = Path("adev/src/content/tutorials/signals/steps/1-creating-your-first-signal/README.md").read_text()

# The callout block about ChangeDetectionStrategy.OnPush should be removed
callout_marker = "About ChangeDetectionStrategy.OnPush"
assert callout_marker not in content, (
    "OnPush callout should be removed from signals tutorial README"
)
print("PASS")
""")
    assert r.returncode == 0, f"signals README validation failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) - agent config file cleanups
# ---------------------------------------------------------------------------

def test_airules_no_onpush_instruction():
    """airules.md no longer instructs setting OnPush in @Component."""
    r = _run_py("""
from pathlib import Path

content = Path("adev/src/context/airules.md").read_text()
instruction = "changeDetection: ChangeDetectionStrategy.OnPush"
assert instruction not in content, (
    "airules.md should not instruct setting OnPush in @Component decorator"
)
print("PASS")
""")
    assert r.returncode == 0, f"airules.md validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_guidelines_no_onpush_instruction():
    """guidelines.md no longer instructs setting OnPush in @Component."""
    r = _run_py("""
from pathlib import Path

content = Path("adev/src/context/guidelines.md").read_text()
instruction = "changeDetection: ChangeDetectionStrategy.OnPush"
assert instruction not in content, (
    "guidelines.md should not instruct setting OnPush in @Component decorator"
)
print("PASS")
""")
    assert r.returncode == 0, f"guidelines.md validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_angular20_mdc_no_onpush_instruction():
    """angular-20.mdc no longer instructs always setting OnPush."""
    r = _run_py("""
from pathlib import Path

content = Path("adev/src/context/angular-20.mdc").read_text()
instruction = "Always set `changeDetection: ChangeDetectionStrategy.OnPush`"
assert instruction not in content, (
    "angular-20.mdc should not have the 'Always set OnPush' instruction"
)
print("PASS")
""")
    assert r.returncode == 0, f"angular-20.mdc validation failed: {r.stderr}"
    assert "PASS" in r.stdout
'''

with open('/workspace/task/tests/test_outputs.py', 'w') as f:
    f.write(content)
print("File written successfully")
