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
        assert content.count("{") == content.count("}"), f"{f} has unbalanced braces"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core source JSDoc updates
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

assert "OnPush is enabled by default" in jsdoc, (
    "JSDoc above OnPush must note it is enabled by default"
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
assert "Eager" in jsdoc, (
    "changeDetection JSDoc must reference ChangeDetectionStrategy#Eager"
)
# Must note OnPush is enabled by default
assert "OnPush is enabled by default" in jsdoc, (
    "changeDetection JSDoc must note OnPush is enabled by default"
)
print("PASS")
""")
    assert r.returncode == 0, f"directives.ts validation failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — documentation updates
# ---------------------------------------------------------------------------


def test_skipping_subtrees_onpush_default():
    """skipping-subtrees.md must describe OnPush as the default strategy."""
    content = _file_content(
        "adev/src/content/best-practices/runtime-performance/skipping-subtrees.md"
    )
    assert "OnPush" in content, "must mention OnPush"
    # First mention should describe OnPush as default
    idx = content.find("OnPush")
    nearby = content[max(0, idx - 200):idx + 300].lower()
    assert "default" in nearby, (
        "OnPush should be described as the default strategy near its first mention"
    )
    # Old code example for manually setting OnPush must be removed
    assert "ChangeDetectionStrategy.OnPush," not in content, (
        "manual OnPush code example should be removed (it is now the default)"
    )


def test_advanced_config_onpush_default():
    """advanced-configuration.md describes OnPush as default, Eager as optional."""
    content = _file_content(
        "adev/src/content/guide/components/advanced-configuration.md"
    )
    # OnPush described as default
    onpush_idx = content.find("OnPush")
    assert onpush_idx != -1, "must mention OnPush"
    onpush_nearby = content[max(0, onpush_idx - 100):onpush_idx + 300].lower()
    assert "default" in onpush_nearby, (
        "OnPush should be described as the default strategy"
    )
    # Eager described as optional
    eager_idx = content.find("Eager")
    assert eager_idx != -1, "must reference Eager"
    eager_nearby = content[max(0, eager_idx - 100):eager_idx + 300].lower()
    assert "optional" in eager_nearby, (
        "Eager should be described as an optional mode"
    )


def test_signals_readme_no_callout():
    """signals tutorial README no longer has the OnPush callout."""
    content = _file_content(
        "adev/src/content/tutorials/signals/steps/1-creating-your-first-signal/README.md"
    )
    assert "About ChangeDetectionStrategy.OnPush" not in content, (
        "OnPush callout should be removed from signals tutorial README"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — agent config file cleanups
# ---------------------------------------------------------------------------


def test_airules_no_onpush_instruction():
    """airules.md no longer instructs setting OnPush in @Component."""
    content = _file_content("adev/src/context/airules.md")
    assert "changeDetection: ChangeDetectionStrategy.OnPush" not in content, (
        "airules.md should not instruct setting OnPush in @Component decorator"
    )


def test_guidelines_no_onpush_instruction():
    """guidelines.md no longer instructs setting OnPush in @Component."""
    content = _file_content("adev/src/context/guidelines.md")
    assert "changeDetection: ChangeDetectionStrategy.OnPush" not in content, (
        "guidelines.md should not instruct setting OnPush in @Component decorator"
    )


def test_angular20_mdc_no_onpush_instruction():
    """angular-20.mdc no longer instructs always setting OnPush."""
    content = _file_content("adev/src/context/angular-20.mdc")
    assert "Always set `changeDetection: ChangeDetectionStrategy.OnPush`" not in content, (
        "angular-20.mdc should not have the 'Always set OnPush' instruction"
    )
