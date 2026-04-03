"""
Task: bun-simplify-bun-run-buildlocal-to
Repo: oven-sh/bun @ a14a89ca953910e89697895dfdfb4cdf4c90a151
PR:   26645

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/bun"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check_cmake():
    """Modified CMake files parse without obvious syntax errors."""
    files = [
        "cmake/tools/SetupWebKit.cmake",
        "cmake/targets/BuildBun.cmake",
    ]
    for f in files:
        fp = Path(REPO) / f
        assert fp.exists(), f"{f} does not exist"
        content = fp.read_text()
        assert len(content.strip()) > 100, f"{f} is too short or empty"
        # Basic CMake syntax: balanced if/endif, macro/endmacro
        # Count if() vs endif() as a rough balance check
        if_count = content.lower().count("if(")
        endif_count = content.lower().count("endif(")
        assert abs(if_count - endif_count) <= 1, (
            f"{f} has unbalanced if/endif: {if_count} if() vs {endif_count} endif()"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_setup_webkit_jsc_configure():
    """SetupWebKit.cmake configures JSC automatically via JSC_CMAKE_ARGS when WEBKIT_LOCAL is set."""
    fp = Path(REPO) / "cmake/tools/SetupWebKit.cmake"
    content = fp.read_text()
    # Must define JSC_CMAKE_ARGS with key configure flags
    assert "JSC_CMAKE_ARGS" in content, (
        "SetupWebKit.cmake must define JSC_CMAKE_ARGS for automatic JSC configuration"
    )
    assert "-DPORT=JSCOnly" in content, (
        "JSC configure must set -DPORT=JSCOnly"
    )
    assert "-DENABLE_STATIC_JSC=ON" in content, (
        "JSC configure must enable static JSC"
    )
    assert "execute_process" in content, (
        "SetupWebKit.cmake must execute cmake configure via execute_process"
    )
    assert "JSC_CONFIGURE_RESULT" in content or "RESULT_VARIABLE" in content, (
        "JSC configure must check result for errors"
    )


# [pr_diff] fail_to_pass
def test_setup_webkit_jsc_build_target():
    """SetupWebKit.cmake creates a jsc custom build target via add_custom_target."""
    fp = Path(REPO) / "cmake/tools/SetupWebKit.cmake"
    content = fp.read_text()
    assert "add_custom_target(jsc" in content, (
        "SetupWebKit.cmake must create a 'jsc' custom target via add_custom_target"
    )
    assert "BYPRODUCTS" in content, (
        "jsc target must declare BYPRODUCTS (lib files)"
    )
    # Must build JSC, not just set paths
    assert "--target jsc" in content, (
        "jsc target must build JSC via --target jsc"
    )


# [pr_diff] fail_to_pass
def test_setup_webkit_build_type_option():
    """SetupWebKit.cmake adds WEBKIT_BUILD_TYPE option that defaults to CMAKE_BUILD_TYPE."""
    fp = Path(REPO) / "cmake/tools/SetupWebKit.cmake"
    content = fp.read_text()
    assert "WEBKIT_BUILD_TYPE" in content, (
        "SetupWebKit.cmake must define WEBKIT_BUILD_TYPE option"
    )
    # Must default to CMAKE_BUILD_TYPE
    assert "CMAKE_BUILD_TYPE" in content, (
        "WEBKIT_BUILD_TYPE must reference CMAKE_BUILD_TYPE as default"
    )
    # The path must use WEBKIT_BUILD_TYPE, not CMAKE_BUILD_TYPE directly
    assert "WebKitBuild/${WEBKIT_BUILD_TYPE}" in content or \
           "WebKitBuild/${WEBKIT_BUILD_TYPE}" in content.replace(" ", ""), (
        "DEFAULT_WEBKIT_PATH must use WEBKIT_BUILD_TYPE (not CMAKE_BUILD_TYPE directly)"
    )


# [pr_diff] fail_to_pass
def test_buildbun_jsc_dependency():
    """BuildBun.cmake adds jsc as a build dependency when WEBKIT_LOCAL is set."""
    fp = Path(REPO) / "cmake/targets/BuildBun.cmake"
    content = fp.read_text()
    assert "add_dependencies" in content, (
        "BuildBun.cmake must use add_dependencies to depend on jsc"
    )
    # Must be conditional on WEBKIT_LOCAL
    # Look for the pattern: if(WEBKIT_LOCAL ... add_dependencies ... jsc
    assert "WEBKIT_LOCAL" in content and "jsc" in content, (
        "BuildBun.cmake must add jsc dependency when WEBKIT_LOCAL is set"
    )
    # Verify it's in an if(WEBKIT_LOCAL) block — find add_dependencies near WEBKIT_LOCAL
    lines = content.split("\n")
    found_dep = False
    for i, line in enumerate(lines):
        if "add_dependencies" in line and "jsc" in line:
            # Check that a preceding line within 3 lines has WEBKIT_LOCAL
            context = "\n".join(lines[max(0, i-3):i+1])
            if "WEBKIT_LOCAL" in context:
                found_dep = True
                break
    assert found_dep, (
        "add_dependencies for jsc must be inside a WEBKIT_LOCAL conditional"
    )


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — documentation updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Old manual steps should be removed
    assert "jsc:build:debug" not in content, (
        "CONTRIBUTING.md should no longer mention 'jsc:build:debug' — build:local handles this"
    )
    assert "InspectorProtocolObjects.h" not in content, (
        "CONTRIBUTING.md should no longer mention deleting InspectorProtocolObjects.h"
    )

    # New simplified instructions should be present
    content_lower = content.lower()
    assert "build:local" in content, (
        "CONTRIBUTING.md must still reference 'build:local'"
    )
    # Should explain that build:local handles everything automatically
    assert ("automatically" in content_lower or "handles everything" in content_lower
            or "auto-build" in content_lower or "single command" in content_lower), (
        "CONTRIBUTING.md should explain that build:local handles JSC automatically"
    )


# [config_edit] fail_to_pass

    # Old manual steps should be removed
    assert "jsc:build:debug" not in content, (
        "contributing.mdx should no longer mention 'jsc:build:debug'"
    )
    assert "InspectorProtocolObjects.h" not in content, (
        "contributing.mdx should no longer mention deleting InspectorProtocolObjects.h"
    )

    # New simplified instructions should be present
    content_lower = content.lower()
    assert "build:local" in content, (
        "contributing.mdx must still reference 'build:local'"
    )
    assert ("automatically" in content_lower or "handles everything" in content_lower
            or "auto-build" in content_lower or "single command" in content_lower), (
        "contributing.mdx should explain that build:local handles JSC automatically"
    )


# [config_edit] fail_to_pass
