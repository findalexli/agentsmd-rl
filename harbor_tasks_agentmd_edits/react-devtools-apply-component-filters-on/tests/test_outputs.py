"""
Task: react-devtools-apply-component-filters-on
Repo: facebook/react @ 2c30ebc4e397d57fe75f850e32aa44e353052944
PR:   35587

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/react"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_initialize_accepts_component_filters():
    """initialize() in backend.js accepts a componentFilters parameter."""
    backend = Path(REPO) / "packages/react-devtools-core/src/backend.js"
    content = backend.read_text()
    # Find the initialize function and check its parameters include componentFilters
    match = re.search(
        r"(?:export\s+)?function\s+initialize\s*\(([\s\S]*?)\)\s*(?::\s*\w+\s*)?\{",
        content,
    )
    assert match, "Could not find initialize function definition in backend.js"
    params = match.group(1)
    assert re.search(r"[Cc]omponent[Ff]ilter", params), (
        "initialize() should accept a component filters parameter"
    )


# [pr_diff] fail_to_pass
def test_install_hook_accepts_component_filters():
    """installHook() accepts a componentFilters parameter."""
    hook = Path(REPO) / "packages/react-devtools-shared/src/hook.js"
    content = hook.read_text()
    match = re.search(
        r"(?:export\s+)?function\s+installHook\s*\(([\s\S]*?)\)\s*(?::\s*\w+\s*)?\{",
        content,
    )
    assert match, "Could not find installHook function definition in hook.js"
    params = match.group(1)
    assert re.search(r"[Cc]omponent[Ff]ilter", params), (
        "installHook() should accept a component filters parameter"
    )


# [pr_diff] fail_to_pass
def test_no_global_component_filters_mechanism():
    """Component filters no longer passed via __REACT_DEVTOOLS_COMPONENT_FILTERS__ global."""
    for rel_path in [
        "packages/react-devtools-core/src/backend.js",
        "packages/react-devtools-shared/src/backend/fiber/renderer.js",
    ]:
        p = Path(REPO) / rel_path
        content = p.read_text()
        assert "__REACT_DEVTOOLS_COMPONENT_FILTERS__" not in content, (
            f"{rel_path} should not reference __REACT_DEVTOOLS_COMPONENT_FILTERS__"
        )


# [pr_diff] fail_to_pass
def test_renderer_accepts_component_filters():
    """Fiber renderer attach() accepts component filters to apply on initial load."""
    renderer = Path(REPO) / "packages/react-devtools-shared/src/backend/fiber/renderer.js"
    content = renderer.read_text()
    # The attach function should accept componentFilters
    match = re.search(
        r"(?:export\s+)?function\s+attach\s*\(([\s\S]*?)\)\s*(?::\s*\w+\s*)?\{",
        content,
    )
    assert match, "Could not find attach function definition in renderer.js"
    params = match.group(1)
    assert re.search(r"[Cc]omponent[Ff]ilter", params), (
        "attach() should accept component filters parameter"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
