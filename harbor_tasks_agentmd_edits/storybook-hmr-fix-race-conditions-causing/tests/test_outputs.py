"""
Task: storybook-hmr-fix-race-conditions-causing
Repo: storybookjs/storybook @ 5a9c6ecd7559ee8c7adbe30fb4b0894e369d144b
PR:   33930

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/storybook"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_debounce_trailing_only():
    """STORY_INDEX_INVALIDATED debounce must use trailing edge only."""
    src = (Path(REPO) / "code/core/src/core-server/utils/index-json.ts").read_text()
    # Must have trailing-only debounce
    assert re.search(r"edges:\s*\[\s*['\"]trailing['\"]\s*\]", src), \
        "debounce should use edges: ['trailing'] only"
    # Must NOT have leading edge
    assert not re.search(r"edges:\s*\[.*['\"]leading['\"]", src), \
        "debounce should not include leading edge"


# [pr_diff] fail_to_pass
def test_vite_no_after_update_listener():
    """Vite codegen must NOT use vite:afterUpdate to emit storyHotUpdated."""
    src = (Path(REPO) / "code/builders/builder-vite/src/codegen-modern-iframe-script.ts").read_text()
    assert "vite:afterUpdate" not in src, \
        "codegen-modern-iframe-script.ts should not use vite:afterUpdate listener"


# [pr_diff] fail_to_pass
def test_vite_emit_before_stories_changed():
    """Vite stories accept callback must emit STORY_HOT_UPDATED before onStoriesChanged."""
    src = (Path(REPO) / "code/builders/builder-vite/src/codegen-modern-iframe-script.ts").read_text()
    lines = src.split("\n")

    accept_line = None
    emit_line = None
    stories_line = None

    for i, line in enumerate(lines):
        if "import.meta.hot.accept" in line and "VIRTUAL_STORIES_FILE" in line:
            accept_line = i
        if accept_line is not None and emit_line is None:
            if "STORY_HOT_UPDATED" in line:
                emit_line = i
        if accept_line is not None and emit_line is not None and stories_line is None:
            if "onStoriesChanged" in line:
                stories_line = i
                break

    assert accept_line is not None, "Must have import.meta.hot.accept for VIRTUAL_STORIES_FILE"
    assert emit_line is not None, \
        "STORY_HOT_UPDATED must be emitted inside the stories accept callback"
    assert stories_line is not None, \
        "onStoriesChanged must be called inside the stories accept callback"
    assert emit_line < stories_line, \
        "STORY_HOT_UPDATED must be emitted before onStoriesChanged"


# [pr_diff] fail_to_pass
def test_webpack_no_status_handler_emit():
    """Webpack HMR must NOT use addStatusHandler to emit STORY_HOT_UPDATED."""
    src = (Path(REPO) / "code/builders/builder-webpack5/templates/virtualModuleModernEntry.js").read_text()
    assert "addStatusHandler" not in src, \
        "Should not use addStatusHandler to emit STORY_HOT_UPDATED"


# [pr_diff] fail_to_pass
def test_webpack_emit_before_stories_changed():
    """Webpack stories accept callback must emit STORY_HOT_UPDATED before onStoriesChanged."""
    src = (Path(REPO) / "code/builders/builder-webpack5/templates/virtualModuleModernEntry.js").read_text()
    lines = src.split("\n")

    accept_line = None
    emit_line = None
    stories_line = None

    for i, line in enumerate(lines):
        if "accept" in line and "storiesFilename" in line:
            accept_line = i
        if accept_line is not None and emit_line is None:
            if "STORY_HOT_UPDATED" in line:
                emit_line = i
        if accept_line is not None and emit_line is not None and stories_line is None:
            if "onStoriesChanged" in line:
                stories_line = i
                break

    assert accept_line is not None, "Must have webpackHot.accept for storiesFilename"
    assert emit_line is not None, \
        "STORY_HOT_UPDATED must be emitted inside the stories accept callback"
    assert stories_line is not None, \
        "onStoriesChanged must be called inside the stories accept callback"
    assert emit_line < stories_line, \
        "STORY_HOT_UPDATED must be emitted before onStoriesChanged"


# [pr_diff] fail_to_pass
def test_project_annotations_emit_hot_updated():
    """Vite project annotations accept callback must emit STORY_HOT_UPDATED."""
    src = (Path(REPO) / "code/builders/builder-vite/src/codegen-project-annotations.ts").read_text()
    assert "STORY_HOT_UPDATED" in src, \
        "codegen-project-annotations.ts must reference STORY_HOT_UPDATED"
    lines = src.split("\n")

    # Find an accept callback with previewAnnotationModules and check it contains the emit
    accept_line = None
    emit_line = None
    annotations_line = None

    for i, line in enumerate(lines):
        if "import.meta.hot.accept" in line:
            accept_line = i
            emit_line = None
            annotations_line = None
        if accept_line is not None and emit_line is None:
            if "STORY_HOT_UPDATED" in line and "emit" in line:
                emit_line = i
        if accept_line is not None and annotations_line is None:
            if "onGetProjectAnnotationsChanged" in line:
                annotations_line = i
                if emit_line is not None:
                    break

    assert emit_line is not None, \
        "STORY_HOT_UPDATED must be emitted inside a project annotations accept callback"
    assert annotations_line is not None, \
        "onGetProjectAnnotationsChanged must be called in accept callback"
    assert emit_line < annotations_line, \
        "STORY_HOT_UPDATED must be emitted before onGetProjectAnnotationsChanged"


# ---------------------------------------------------------------------------
# Config edit (config_edit) — copilot instructions update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass
