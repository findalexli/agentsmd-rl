"""
Task: react-devtools-host-props-rename
Repo: facebook/react @ 4c9d62d2b47be424ad9050725d8bdd8df12fe2a3
PR:   35735 — [DevTools] Allow renaming Host Component props

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Fix summary: In renderer.js `renamePath`, the `case 'props':` block incorrectly
used `if (instance === null)` to dispatch. Host Components (e.g. <input>) have
a non-null DOM instance but no `forceUpdate()`. The fix replaces the if/else
with `switch (fiber.tag)`, routing ClassComponents to forceUpdate() and
everything else to overridePropsRenamePath().
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"
RENDERER = f"{REPO}/packages/react-devtools-shared/src/backend/fiber/renderer.js"


def _get_rename_path_props_section(content: str) -> str:
    """
    Find the case 'props': block inside renamePath.

    The renamePath function has a `case 'props':` that references
    overridePropsRenamePath (unlike the setInPath function). We find the
    case 'props': whose 600-char window contains overridePropsRenamePath.
    """
    for m in re.finditer(r"case 'props':", content):
        window = content[m.start() : m.start() + 600]
        if "overridePropsRenamePath" in window:
            return window
    return ""


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """renderer.js must parse without syntax errors."""
    # AST-only because: JS file, can't import in Python
    r = subprocess.run(
        ["node", "--check", RENDERER],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in renderer.js:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_switch_on_fiber_tag_replaces_instance_null_check():
    """
    The props rename case now uses switch(fiber.tag) to dispatch, replacing
    the old if(instance === null) / else pattern.
    """
    content = Path(RENDERER).read_text()
    section = _get_rename_path_props_section(content)
    assert section, "Could not locate case 'props': section with overridePropsRenamePath"

    assert "switch (fiber.tag)" in section, (
        "Expected 'switch (fiber.tag)' in the renamePath props case, "
        "but it was not found. Old if(instance===null) pattern may still be present."
    )
    assert "if (instance === null)" not in section, (
        "Old 'if (instance === null)' check still present in renamePath props case; "
        "should be replaced by switch(fiber.tag)"
    )


# [pr_diff] fail_to_pass
def test_class_component_case_calls_force_update():
    """
    A dedicated `case ClassComponent:` branch in the switch calls forceUpdate(),
    preserving the original behaviour for Class Components.
    """
    content = Path(RENDERER).read_text()
    section = _get_rename_path_props_section(content)
    assert section, "Could not locate case 'props': section with overridePropsRenamePath"

    assert "case ClassComponent:" in section, (
        "Expected 'case ClassComponent:' inside switch(fiber.tag) in renamePath props case"
    )
    # forceUpdate() must appear in the ClassComponent sub-section
    idx = section.find("case ClassComponent:")
    class_snippet = section[idx : idx + 250]
    assert "forceUpdate()" in class_snippet, (
        "Expected instance.forceUpdate() within the case ClassComponent: block"
    )


# [pr_diff] fail_to_pass
def test_default_branch_handles_non_class_components():
    """
    A `default:` branch in the switch calls overridePropsRenamePath() for Host
    Components and Function Components (everything except ClassComponent).
    """
    content = Path(RENDERER).read_text()
    section = _get_rename_path_props_section(content)
    assert section, "Could not locate case 'props': section with overridePropsRenamePath"

    assert "default:" in section, (
        "Expected a 'default:' case in switch(fiber.tag) within renamePath props case"
    )
    idx = section.find("default:")
    default_snippet = section[idx : idx + 250]
    assert "overridePropsRenamePath" in default_snippet, (
        "Expected overridePropsRenamePath() call in the default: branch of switch(fiber.tag)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_editing_tests_pass():
    """
    Existing editing-interface tests (present on base commit) still pass
    after the renderer.js fix. These exercise prop set/delete/copy/rename
    for Class and Function Components — the fix must not regress them.
    """
    r = subprocess.run(
        [
            "yarn",
            "test",
            "--testPathPattern=editing-test",
            "--testNamePattern=editing interface",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        "Editing interface tests failed after fix:\n"
        f"STDOUT:\n{r.stdout.decode()[-3000:]}\n"
        f"STDERR:\n{r.stderr.decode()[-500:]}"
    )
