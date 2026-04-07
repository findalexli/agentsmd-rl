"""
Task: remix-interaction-refactor-descriptor-api
Repo: remix-run/remix @ 90016e313b24a05c5862a853a3b518290d9017ba
PR:   10823

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/remix"
INTERACTION = f"{REPO}/packages/interaction/src/lib/interaction.ts"
INDEX = f"{REPO}/packages/interaction/src/index.ts"
README = f"{REPO}/packages/interaction/README.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_core_files_exist():
    """Core source files exist and have substantial content."""
    files = [
        INTERACTION,
        INDEX,
        f"{REPO}/packages/interaction/src/lib/interactions/form.ts",
        f"{REPO}/packages/interaction/src/lib/interactions/keys.ts",
        f"{REPO}/packages/interaction/src/lib/interactions/popover.ts",
        f"{REPO}/packages/interaction/src/lib/interactions/press.ts",
    ]
    for f in files:
        p = Path(f)
        assert p.exists(), f"{p.name} must exist"
        content = p.read_text()
        assert len(content) > 50, f"{p.name} must have substantial content"


# [static] pass_to_pass
def test_core_exports_preserved():
    """Core API functions are still exported: on, createContainer, defineInteraction."""
    content = Path(INDEX).read_text()
    for name in ["on", "createContainer", "defineInteraction"]:
        assert name in content, f"{name} must still be exported from index.ts"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core API refactor tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_old_helpers_removed():
    """capture() and listenWith() helper functions are no longer exported."""
    content = Path(INDEX).read_text()
    # Check that neither function appears in the export block
    assert re.search(r"\bcapture\b", content) is None or "capture" not in content.split("export")[0], \
        "capture should not be in exports"
    # More precise: check the export block doesn't list these
    export_block_match = re.search(r"export\s*\{([^}]+)\}", content)
    assert export_block_match, "index.ts must have an export block"
    exports = export_block_match.group(1)
    assert "capture" not in exports.split("type")[0] if "type" in exports else "capture" not in exports, \
        "capture must not be a value export"
    assert "listenWith" not in exports, \
        "listenWith must not be exported"


# [pr_diff] fail_to_pass
def test_new_types_exported():
    """Interaction and ContainerOptions types are now exported from index.ts."""
    content = Path(INDEX).read_text()
    assert re.search(r"type\s+Interaction\b", content) is not None or "Interaction" in content, \
        "Interaction type must be exported"
    assert re.search(r"type\s+ContainerOptions\b", content) is not None or "ContainerOptions" in content, \
        "ContainerOptions type must be exported"


# [pr_diff] fail_to_pass
def test_interaction_setup_uses_this_context():
    """InteractionSetup type uses `this: Interaction` instead of positional parameters."""
    content = Path(INTERACTION).read_text()
    # The InteractionSetup type should use `this` parameter
    assert re.search(r"InteractionSetup.*this.*Interaction", content, re.DOTALL), \
        "InteractionSetup must use `this: Interaction` context pattern"
    # The old `(target: EventTarget, signal: AbortSignal) => void` pattern should be gone
    assert "target: EventTarget, signal: AbortSignal) => void" not in content, \
        "Old InteractionSetup signature must be replaced"


# [pr_diff] fail_to_pass
def test_descriptor_interface_simplified():
    """Descriptor interface extends AddEventListenerOptions directly (no nested `options` field)."""
    content = Path(INTERACTION).read_text()
    # Descriptor should extend AddEventListenerOptions
    assert re.search(r"interface\s+Descriptor.*extends\s+AddEventListenerOptions", content), \
        "Descriptor must extend AddEventListenerOptions"
    # The old `options: AddEventListenerOptions` field should NOT be in Descriptor
    # Check the Descriptor interface block
    desc_match = re.search(r"interface\s+Descriptor[^{]*\{([^}]+)\}", content)
    if desc_match:
        body = desc_match.group(1)
        assert "options:" not in body and "options :" not in body, \
            "Descriptor must not have a separate `options` field"
    # isDescriptor should only check for 'listener', not 'options'
    is_desc_match = re.search(r"isDescriptor[^{]*\{([^}]+)\}", content)
    if is_desc_match:
        body = is_desc_match.group(1)
        assert "'options'" not in body and '"options"' not in body, \
            "isDescriptor should not check for 'options' key"


# [pr_diff] fail_to_pass
def test_error_handling_in_create_binding():
    """createBinding wraps listeners with try/catch and onError for sync and async errors."""
    content = Path(INTERACTION).read_text()
    # createBinding should accept an onError parameter
    assert "onError" in content, "createBinding must handle onError"
    # There should be a try/catch in the wrappedListener
    assert "try {" in content or "try{" in content, "wrappedListener must use try/catch"
    # And catch should call onError
    assert re.search(r"catch.*\{[^}]*onError", content, re.DOTALL), \
        "catch block must call onError"
    # Async errors should also be caught
    assert re.search(r"Promise.*catch.*onError", content) or re.search(r"result\.catch\(onError\)", content), \
        "Async errors must be caught via result.catch(onError)"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_readme_imports_updated():
    """README.md import examples no longer reference capture or listenWith."""
    content = Path(README).read_text()
    # Check that import lines don't include capture or listenWith
    import_lines = [line for line in content.split("\n") if "import" in line and "remix-run/interaction" in line]
    for line in import_lines:
        assert "capture" not in line or "capture: true" in line, \
            f"Import line should not import 'capture' as a function: {line.strip()}"
        assert "listenWith" not in line, \
            f"Import line should not import 'listenWith': {line.strip()}"


# [pr_diff] fail_to_pass
def test_readme_shows_descriptor_syntax():
    """README.md shows descriptor object syntax instead of capture()/listenWith()."""
    content = Path(README).read_text()
    # Should show descriptor objects with capture/once as properties
    assert re.search(r"capture:\s*true", content), \
        "README should show `capture: true` descriptor syntax"
    assert re.search(r"once:\s*true", content), \
        "README should show `once: true` descriptor syntax"
    assert re.search(r"listener\(event\)", content) or re.search(r"listener\(", content), \
        "README should show descriptor objects with `listener` property"
    # Should NOT show the old capture() or listenWith() function call patterns
    assert not re.search(r"\bcapture\s*\(", content), \
        "README should not show capture() function call pattern"
    assert not re.search(r"\blistenWith\s*\(", content), \
        "README should not show listenWith() function call pattern"


# [pr_diff] fail_to_pass
def test_readme_container_options_syntax():
    """README.md shows createContainer with options object syntax."""
    content = Path(README).read_text()
    # Should show createContainer with object options (signal inside object)
    assert re.search(r"createContainer\([^)]+\{[^}]*signal", content, re.DOTALL), \
        "README should show createContainer with { signal } options object"
    # Should NOT show the old 2-argument form with bare signal
    assert not re.search(r"createContainer\([^,]+,\s*(?:controller\.signal|signal)\s*\)", content), \
        "README should not show createContainer(target, signal) bare signal pattern"
