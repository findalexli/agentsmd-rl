"""
Task: react-devtools-host-props-rename
Repo: facebook/react @ 4c9d62d2b47be424ad9050725d8bdd8df12fe2a3
PR:   35735 — [DevTools] Allow renaming Host Component props

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Fix summary: In renderer.js `renamePath`, the `case 'props':` block incorrectly
used `if (instance === null)` to dispatch. Host Components (e.g. <input>) have
a non-null DOM instance but no `forceUpdate()`. The fix replaces the if/else
with dispatch based on `fiber.tag`, routing ClassComponents to forceUpdate() and
everything else to overridePropsRenamePath().
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"
RENDERER = f"{REPO}/packages/react-devtools-shared/src/backend/fiber/renderer.js"
EDITING_TEST = f"{REPO}/packages/react-devtools-shared/src/__tests__/editing-test.js"


def _get_rename_path_props_section(content: str) -> str:
    """
    Find the case 'props': block inside renamePath.

    The renamePath function has a `case 'props':` that references
    overridePropsRenamePath (unlike setInPath). We locate it by finding
    the case 'props': whose 800-char window contains overridePropsRenamePath.
    """
    for m in re.finditer(r"case 'props':", content):
        window = content[m.start() : m.start() + 800]
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
# Fail-to-pass (pr_diff) — structural checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_dispatches_on_fiber_tag_not_instance():
    """
    The props rename case dispatches based on fiber.tag (not instance === null).
    Accepts switch(fiber.tag) or if(fiber.tag === ...) patterns.
    """
    content = Path(RENDERER).read_text()
    section = _get_rename_path_props_section(content)
    assert section, "Could not locate case 'props': section with overridePropsRenamePath"

    assert "instance === null" not in section, (
        "Old 'if (instance === null)' pattern still present in renamePath props case; "
        "should dispatch based on fiber.tag instead"
    )
    assert "fiber.tag" in section, (
        "Expected dispatch on fiber.tag in the renamePath props case "
        "(via switch or conditional), but fiber.tag not referenced"
    )


# [pr_diff] fail_to_pass
def test_class_component_preserves_force_update():
    """
    ClassComponent fibers still use forceUpdate() for prop renaming.
    The fix must preserve this behavior while changing the dispatch mechanism.
    """
    content = Path(RENDERER).read_text()
    section = _get_rename_path_props_section(content)
    assert section, "Could not locate case 'props': section with overridePropsRenamePath"

    assert "ClassComponent" in section, (
        "Expected ClassComponent reference in renamePath props case "
        "to route class components to forceUpdate()"
    )
    assert "forceUpdate()" in section, (
        "Expected forceUpdate() call for ClassComponent fibers in renamePath props case"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression (runs BEFORE behavioral f2p test)
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
            "yarn", "test", "--silent", "--no-watchman",
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


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral test
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_host_component_rename_works():
    """
    Behavioral: renaming a prop on a host component (<input>) must succeed.
    Injects the PR's test case (data-foo → data-bar rename on <input>) into
    editing-test.js and runs it. Fails on base commit because forceUpdate()
    is called on the DOM node, which crashes.
    """
    test_file = Path(EDITING_TEST)
    content = test_file.read_text()

    if "data-foo" not in content:
        # 1. Add data-foo="test" prop to the <input> host component fixture
        content = content.replace(
            '<input ref={inputRef} onChange={jest.fn()} value="initial" />',
            '<input ref={inputRef} onChange={jest.fn()} value="initial" data-foo="test" />',
        )

        # 2. Inject host component rename assertion after the last rename check.
        #    The anchor is the final assertion in the rename test:
        #      after: 'initial',
        #    });           <-- closes expect().toEqual()
        #    });           <-- closes it('should rename...')
        inject_code = (
            "        after: 'initial',\n"
            "      });\n"
            "      renamePath(hostComponentID, ['data-foo'], ['data-bar']);\n"
            "      expect({\n"
            "        foo: inputRef.current.dataset.foo,\n"
            "        bar: inputRef.current.dataset.bar,\n"
            "      }).toEqual({\n"
            "        foo: undefined,\n"
            "        bar: 'test',\n"
            "      });\n"
            "    });"
        )
        content = content.replace(
            "        after: 'initial',\n"
            "      });\n"
            "    });",
            inject_code,
            1,  # replace only first occurrence
        )
        test_file.write_text(content)

    r = subprocess.run(
        [
            "yarn", "test", "--silent", "--no-watchman",
            "--testPathPattern=editing-test",
            "--testNamePattern=should rename",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        "Host component prop rename test failed (crash on Host Component?):\n"
        f"STDOUT:\n{r.stdout.decode()[-3000:]}\n"
        f"STDERR:\n{r.stderr.decode()[-500:]}"
    )
