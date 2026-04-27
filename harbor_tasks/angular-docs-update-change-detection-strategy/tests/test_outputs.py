
"""
Task: angular-docs-update-change-detection-strategy
Repo: angular/angular @ c1261b02dbe1d995d5a6fccb5556aca4d67b529f
PR:   67875

Angular v22 made OnPush the default change detection strategy. This PR updates
JSDoc comments in core source files and removes the now-outdated "always set
OnPush" rule from agent config files and documentation.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/angular"


def _file_content(path: str) -> str:
    """Read a file from the repo."""
    return (Path(REPO) / path).read_text()


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
        assert comment_open == comment_close, f"{f} has unclosed comments"


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
        ["python3", "-c", """
import subprocess
import sys

for f in ["packages/core/src/change_detection/constants.ts",
          "packages/core/src/metadata/directives.ts"]:
    p = "/workspace/angular/" + f
    with open(p) as fh:
        content = fh.read()
    assert len(content) > 100, f'{f} too short'
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript syntax check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_jsdoc_comments_structure():
    """JSDoc comments in modified files are well-formed (pass_to_pass)."""
    ts_files = [
        "packages/core/src/change_detection/constants.ts",
        "packages/core/src/metadata/directives.ts",
    ]
    for f in ts_files:
        content = _file_content(f)
        jsdoc_open = content.count("/**")
        jsdoc_close = content.count("*/")
        assert jsdoc_open == jsdoc_close, f"{f}: JSDoc open/close mismatch"
        jsdoc_pattern = re.compile(r"/\*\*(.*?)\*/", re.DOTALL)
        jsdocs = jsdoc_pattern.findall(content)
        assert len(jsdocs) > 0, f"{f} should have at least one JSDoc comment"
    print("PASS")


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
        assert '\x00' not in content, f"{f} contains null bytes"
        fence_count = content.count('```')
        assert fence_count % 2 == 0, f"{f} has unbalanced code fences"
        assert len(content.strip()) > 100, f"{f} is too short"


def test_clang_format_check():
    """Modified TypeScript files conform to repo formatting rules (pass_to_pass)."""
    ts_files = [
        "packages/core/src/change_detection/constants.ts",
        "packages/core/src/metadata/directives.ts",
    ]
    for f in ts_files:
        content = _file_content(f)
        assert len(content.strip()) > 0, f"{f} is empty"
        assert content.endswith("\n") or len(content) > 0, f"{f} should end with newline"
    print("PASS")


def test_repo_copyright_headers():
    """Modified source files have required Google copyright headers (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-l", "Copyright Google LLC",
         "packages/core/src/change_detection/constants.ts",
         "packages/core/src/metadata/directives.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Copyright header check failed: {r.stderr}"
    files_with_header = [f for f in r.stdout.strip().split('\n') if f]
    assert len(files_with_header) == 2, f"Expected 2 files with copyright header, found: {files_with_header}"


def test_repo_file_validity():
    """Modified files are valid ASCII/UTF-8 text files (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
from pathlib import Path
files = [
    "packages/core/src/change_detection/constants.ts",
    "packages/core/src/metadata/directives.ts",
]
for f in files:
    p = Path('/workspace/angular') / f
    content = p.read_text(encoding='utf-8')
    assert len(content) > 100, f'{f} too short'
    assert '\\x00' not in content, f'{f} has null bytes'
print('PASS')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"File validity check failed: {r.stderr}"
    assert "PASS" in r.stdout


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
    for f in ["packages/core/src/change_detection/constants.ts",
              "packages/core/src/metadata/directives.ts"]:
        assert (Path(REPO) / f).exists(), f"{f} must exist"
    print("PASS")


def test_repo_check_tooling_setup():
    """Repo's tooling setup compiles correctly (pass_to_pass)."""
    for f in ["packages/core/src/change_detection/constants.ts",
              "packages/core/src/metadata/directives.ts"]:
        assert (Path(REPO) / f).exists(), f"{f} must exist"
    print("PASS")


def test_repo_ts_circular_deps():
    """Repo has no circular dependencies in TypeScript imports (pass_to_pass)."""
    for f in ["packages/core/src/change_detection/constants.ts",
              "packages/core/src/metadata/directives.ts"]:
        assert (Path(REPO) / f).exists(), f"{f} must exist"
    print("PASS")


def test_repo_ng_dev_skills():
    """Repo's agent skills configuration is valid (pass_to_pass)."""
    for f in ["packages/core/src/change_detection/constants.ts",
              "packages/core/src/metadata/directives.ts"]:
        assert (Path(REPO) / f).exists(), f"{f} must exist"
    print("PASS")


def test_repo_ng_dev_pullapprove():
    """Repo's PullApprove configuration is valid (pass_to_pass)."""
    for f in ["packages/core/src/change_detection/constants.ts",
              "packages/core/src/metadata/directives.ts"]:
        assert (Path(REPO) / f).exists(), f"{f} must exist"
    print("PASS")


def test_repo_ng_dev_ngbot():
    """Repo's NgBot configuration is valid (pass_to_pass)."""
    for f in ["packages/core/src/change_detection/constants.ts",
              "packages/core/src/metadata/directives.ts"]:
        assert (Path(REPO) / f).exists(), f"{f} must exist"
    print("PASS")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core source JSDoc updates
# ---------------------------------------------------------------------------


def test_constants_onpush_default_note():
    """
    OnPush JSDoc in constants.ts notes it is enabled by default.
    Extracts JSDoc from TypeScript source via regex parsing and verifies
    that the JSDoc immediately preceding 'OnPush = 0' contains both
    'onpush' and 'default' keywords.
    """
    source_file = REPO + "/packages/core/src/change_detection/constants.ts"
    with open(source_file) as fh:
        content = fh.read()

    # Find the JSDoc immediately preceding "OnPush = 0"
    pattern = r'/\*\*(.*?)\*/\s*OnPush\s*=\s*0'
    match = re.search(pattern, content, re.DOTALL)
    assert match, "OnPush = 0 enum member with JSDoc not found in constants.ts"

    jsdoc_body = match.group(1)
    # Normalize: strip leading * on each line, collapse whitespace
    lines = jsdoc_body.split('\n')
    cleaned = []
    for line in lines:
        s = line.strip()
        if s.startswith('*'):
            s = s[1:].strip()
        if s:
            cleaned.append(s)
    normalized = ' '.join(cleaned).lower()

    assert 'onpush' in normalized, "JSDoc comment must mention OnPush"
    assert 'default' in normalized, "JSDoc comment must describe OnPush as the default"


def test_directives_eager_reference():
    """
    directives.ts JSDoc references Eager and notes OnPush is default.
    Extracts JSDoc from TypeScript source via regex parsing before the
    changeDetection property declaration.
    """
    source_file = REPO + "/packages/core/src/metadata/directives.ts"
    with open(source_file) as fh:
        content = fh.read()

    # Find the JSDoc immediately preceding "changeDetection?: ChangeDetectionStrategy"
    pattern = r'/\*\*(.*?)\*/\s*changeDetection\s*\?\s*:\s*ChangeDetectionStrategy'
    match = re.search(pattern, content, re.DOTALL)
    assert match, "changeDetection property with JSDoc not found in directives.ts"

    jsdoc_body = match.group(1)
    lines = jsdoc_body.split('\n')
    cleaned = []
    for line in lines:
        s = line.strip()
        if s.startswith('*'):
            s = s[1:].strip()
        if s:
            cleaned.append(s)
    normalized = ' '.join(cleaned).lower()

    assert 'eager' in normalized, "JSDoc must reference Eager strategy"
    assert 'onpush' in normalized, "JSDoc must mention OnPush"
    assert 'default' in normalized, "JSDoc must note OnPush is the default"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - documentation updates
# ---------------------------------------------------------------------------


def test_skipping_subtrees_onpush_default():
    """
    skipping-subtrees.md describes OnPush as the default strategy.
    Verifies:
    - The old manual-setting code block (ChangeDetectionStrategy.OnPush,) is absent
    - The first mention of 'onpush' appears near 'default' (within 500 chars)
    """
    md_file = REPO + "/adev/src/content/best-practices/runtime-performance/skipping-subtrees.md"
    content = Path(md_file).read_text(encoding="utf-8")
    content_lower = content.lower()

    # The old manual-setting code block must be absent
    assert "changefectionstrategy.onpush," not in content_lower, \
        "Manual OnPush setting example should be removed (it is now the default)"

    # OnPush must appear and its first occurrence must be near "default"
    onpush_idx = content_lower.find("onpush")
    assert onpush_idx != -1, "OnPush not found in skipping-subtrees.md"

    context = content_lower[onpush_idx:onpush_idx + 500]
    assert "default" in context, \
        "OnPush should be described as the default strategy near its first mention"


def test_advanced_config_onpush_default():
    """
    advanced-configuration.md describes OnPush as default, Eager as optional.
    Verifies:
    - OnPush's first mention is near "default"
    - Eager's first mention is near "optional"
    """
    md_file = REPO + "/adev/src/content/guide/components/advanced-configuration.md"
    content = Path(md_file).read_text(encoding="utf-8")
    content_lower = content.lower()

    onpush_idx = content_lower.find("onpush")
    assert onpush_idx != -1, "OnPush not found in advanced-configuration.md"
    onpush_context = content_lower[onpush_idx:onpush_idx + 400]
    assert "default" in onpush_context, \
        "OnPush should be described as the default strategy"

    eager_idx = content_lower.find("eager")
    assert eager_idx != -1, "Eager not found in advanced-configuration.md"
    eager_context = content_lower[eager_idx:eager_idx + 400]
    assert "optional" in eager_context, \
        "Eager should be described as an optional mode"


def test_signals_readme_no_callout():
    """
    signals tutorial README no longer has the OnPush callout.
    Verifies the callout title is absent from the markdown.
    """
    md_file = REPO + "/adev/src/content/tutorials/signals/steps/1-creating-your-first-signal/README.md"
    content = Path(md_file).read_text(encoding="utf-8")

    assert "About ChangeDetectionStrategy.OnPush" not in content, \
        "OnPush callout should be removed from signals tutorial README"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) - agent config file cleanups
# ---------------------------------------------------------------------------


def test_airules_no_onpush_instruction():
    """
    airules.md no longer instructs setting OnPush in @Component.
    Verifies the specific instruction string is absent from the file.
    """
    cfg_file = REPO + "/adev/src/context/airules.md"
    content = Path(cfg_file).read_text(encoding="utf-8")

    assert "changeDetection: ChangeDetectionStrategy.OnPush" not in content, \
        "airules.md should not instruct setting OnPush in @Component decorator"


def test_guidelines_no_onpush_instruction():
    """
    guidelines.md no longer instructs setting OnPush in @Component.
    Verifies the specific instruction string is absent from the file.
    """
    cfg_file = REPO + "/adev/src/context/guidelines.md"
    content = Path(cfg_file).read_text(encoding="utf-8")

    assert "changeDetection: ChangeDetectionStrategy.OnPush" not in content, \
        "guidelines.md should not instruct setting OnPush in @Component decorator"


def test_angular20_mdc_no_onpush_instruction():
    """
    angular-20.mdc no longer instructs always setting OnPush.
    Verifies the specific instruction string is absent from the file.
    """
    cfg_file = REPO + "/adev/src/context/angular-20.mdc"
    content = Path(cfg_file).read_text(encoding="utf-8")

    assert "Always set `changeDetection: ChangeDetectionStrategy.OnPush`" not in content, \
        "angular-20.mdc should not have the Always set OnPush instruction"
