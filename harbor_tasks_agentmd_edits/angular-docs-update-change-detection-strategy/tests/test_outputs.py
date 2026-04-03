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


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files parse without syntax errors."""
    ts_files = [
        "packages/core/src/change_detection/constants.ts",
        "packages/core/src/metadata/directives.ts",
    ]
    for f in ts_files:
        p = Path(REPO) / f
        content = p.read_text()
        # Basic check: file is non-empty and has balanced braces
        assert len(content) > 100, f"{f} is unexpectedly short"
        assert content.count("{") == content.count("}"), f"{f} has unbalanced braces"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code JSDoc updates
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_constants_onpush_default_note():
    """OnPush JSDoc in constants.ts must note it is enabled by default."""
    content = (Path(REPO) / "packages/core/src/change_detection/constants.ts").read_text()
    assert "OnPush" in content, "constants.ts must define OnPush"
    # The PR adds a note that OnPush is enabled by default.
    # The JSDoc block above OnPush = 0 should contain language about
    # OnPush being the default — not just a reference to `Default` enum value.
    idx_onpush_enum = content.find("OnPush = 0")
    assert idx_onpush_enum != -1, "constants.ts must have OnPush = 0 enum member"
    block_before = content[max(0, idx_onpush_enum - 500):idx_onpush_enum]
    # Check for "enabled by default" or "default" in a context about OnPush being the default,
    # not just mentioning the `Default` enum member name
    block_lower = block_before.lower()
    assert "enabled by default" in block_lower or "is the default" in block_lower \
        or ("onpush" in block_lower and "by default" in block_lower), \
        "JSDoc above OnPush = 0 should note that OnPush is enabled by default"


# [pr_diff] fail_to_pass
def test_directives_eager_reference():
    """directives.ts JSDoc should reference Eager (not Default) and note OnPush is default."""
    content = (Path(REPO) / "packages/core/src/metadata/directives.ts").read_text()
    # Find the changeDetection property doc
    idx = content.find("changeDetection?")
    assert idx != -1, "directives.ts must have changeDetection property"
    block = content[max(0, idx - 800):idx + 200]
    # The PR changes "ChangeDetectionStrategy#Default" to "ChangeDetectionStrategy#Eager"
    assert "Eager" in block, \
        "changeDetection JSDoc should reference ChangeDetectionStrategy#Eager (not #Default)"
    # The PR also adds a NOTE about OnPush being enabled by default
    block_lower = block.lower()
    assert "enabled by default" in block_lower or "is the default" in block_lower \
        or ("onpush" in block_lower and "by default" in block_lower), \
        "changeDetection JSDoc should note OnPush is enabled by default"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — documentation updates
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skipping_subtrees_onpush_default():
    """skipping-subtrees.md must describe OnPush as the default strategy."""
    content = (Path(REPO) / "adev/src/content/best-practices/runtime-performance/skipping-subtrees.md").read_text()
    # The PR updates this doc to say OnPush is the default since v22
    assert "default" in content.lower(), \
        "skipping-subtrees.md should mention OnPush is the default"
    # Check that it describes OnPush as default change detection strategy
    # Look for language like "default change detection" or "default strategy" near "OnPush"
    idx = content.find("OnPush")
    assert idx != -1, "skipping-subtrees.md must mention OnPush"
    nearby = content[max(0, idx - 200):idx + 200].lower()
    assert "default" in nearby, \
        "skipping-subtrees.md should describe OnPush as the default near its first mention"
    # The old doc had a section telling users to set OnPush manually with a code example
    # That code example should be removed since it's now the default
    assert "ChangeDetectionStrategy.OnPush," not in content, \
        "skipping-subtrees.md should not show code to manually set OnPush (it's now default)"


# [pr_diff] fail_to_pass
def test_advanced_config_onpush_default():
    """advanced-configuration.md must describe OnPush as the default strategy."""
    content = (Path(REPO) / "adev/src/content/guide/components/advanced-configuration.md").read_text()
    # Find the OnPush description section
    idx = content.find("OnPush")
    assert idx != -1, "advanced-configuration.md must mention OnPush"
    nearby = content[max(0, idx - 100):idx + 300].lower()
    # The PR changes OnPush from "optional mode" to "default strategy"
    assert "default" in nearby, \
        "advanced-configuration.md should describe OnPush as the default strategy"
    # The PR also changes Eager from "default strategy" to "optional mode"
    eager_idx = content.find("Eager")
    assert eager_idx != -1, \
        "advanced-configuration.md should reference Eager (renamed from Default)"
    eager_nearby = content[max(0, eager_idx - 100):eager_idx + 300].lower()
    assert "optional" in eager_nearby, \
        "advanced-configuration.md should describe Eager as an optional mode"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — agent config file updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass — adev/src/context/airules.md:89


# [config_edit] fail_to_pass — adev/src/context/guidelines.md:95


# [config_edit] fail_to_pass — adev/src/context/angular-20.mdc:67
