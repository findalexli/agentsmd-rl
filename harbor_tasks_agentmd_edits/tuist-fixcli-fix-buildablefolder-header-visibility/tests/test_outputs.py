"""
Task: tuist-fixcli-fix-buildablefolder-header-visibility
Repo: tuist/tuist @ 11293dd1f2909a4c9b6011e31d94545a16ccc632
PR:   9604

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/tuist"
BUILD_PHASE = Path(REPO) / "cli/Sources/TuistGenerator/Generator/BuildPhaseGenerator.swift"
TARGET_GEN = Path(REPO) / "cli/Sources/TuistGenerator/Generator/TargetGenerator.swift"
AGENTS_MD = Path(REPO) / "AGENTS.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Swift files have balanced braces."""
    for path in [BUILD_PHASE, TARGET_GEN]:
        content = path.read_text()
        opens = content.count("{")
        closes = content.count("}")
        assert opens == closes, (
            f"{path.name}: unbalanced braces ({opens} open vs {closes} close)"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_build_phase_filters_synchronized_headers():
    """generateHeadersBuildPhase must skip headers inside buildable folders.

    The fix adds a buildableFolders parameter and filters each header
    category (public/private/project) through an isPartOfSynchronizedGroup
    closure before adding to the build phase.
    """
    content = BUILD_PHASE.read_text()

    # The function signature must accept buildableFolders
    sig_match = re.search(
        r"func\s+generateHeadersBuildPhase\s*\((.*?)\)\s*(throws|->)",
        content,
        re.DOTALL,
    )
    assert sig_match, "generateHeadersBuildPhase function not found"
    params = sig_match.group(1)
    assert "buildableFolders" in params or "buildable" in params.lower(), (
        "generateHeadersBuildPhase must accept a buildableFolders parameter"
    )

    # Headers must be filtered — look for filtering of public/private/project
    # arrays through a descendant/synchronized check
    func_start = sig_match.start()
    # Find the function body (roughly)
    func_body = content[func_start:func_start + 3000]
    assert ".filter" in func_body or "filter {" in func_body or "filter(" in func_body, (
        "Header arrays must be filtered to exclude synchronized-group members"
    )


# [pr_diff] fail_to_pass
def test_target_generator_synchronized_headers():
    """TargetGenerator must map target headers into synchronized exception sets.

    The fix adds a private helper that computes which public/private headers
    belong to a buildable folder and creates PBXFileSystemSynchronizedBuildFileExceptionSet
    entries so Xcode preserves header visibility.
    """
    content = TARGET_GEN.read_text()

    # Must have a function that computes synchronized headers
    assert re.search(
        r"func\s+synchronizedHeaders\s*\(", content
    ), "TargetGenerator must have a synchronizedHeaders helper function"

    # Must create exception sets for headers
    assert "PBXFileSystemSynchronizedBuildFileExceptionSet" in content, (
        "Must create PBXFileSystemSynchronizedBuildFileExceptionSet for header visibility"
    )

    # The function must deal with publicHeaders and privateHeaders
    assert "publicHeaders" in content and "privateHeaders" in content, (
        "synchronizedHeaders must handle both public and private headers"
    )


# [pr_diff] fail_to_pass

    Headers belonging to a synchronized group are identified by checking
    whether their path is a descendant of a buildable folder path.
    """
    content = BUILD_PHASE.read_text()
    # The fix uses isDescendant(of:) to check if a header path is inside
    # a buildable folder
    assert "isDescendant" in content or "isDescendantOf" in content or "descendant" in content.lower(), (
        "BuildPhaseGenerator must use a descendant-of-path check to identify "
        "headers belonging to synchronized groups"
    )


# ---------------------------------------------------------------------------
# Config edit (config_edit) — AGENTS.md update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    The Workflow section documents how to compile and test Swift changes.
    Both the build and test xcodebuild commands must include flags to
    disable code signing so they work in CI/agent environments:
    CODE_SIGNING_ALLOWED=NO, CODE_SIGNING_REQUIRED=NO, CODE_SIGN_IDENTITY=""
    """
    content = AGENTS_MD.read_text()

    # Find the xcodebuild build command line
    build_lines = [
        line for line in content.splitlines()
        if "xcodebuild" in line and "build" in line.lower()
        and "test" not in line.split("xcodebuild")[0]  # exclude lines about testing before xcodebuild
    ]
    test_lines = [
        line for line in content.splitlines()
        if "xcodebuild" in line and "test" in line.lower()
    ]

    assert build_lines, "AGENTS.md must have an xcodebuild build command"
    assert test_lines, "AGENTS.md must have an xcodebuild test command"

    # Check that code signing flags appear in build command
    build_text = " ".join(build_lines)
    assert "CODE_SIGNING_ALLOWED=NO" in build_text, (
        "xcodebuild build command must include CODE_SIGNING_ALLOWED=NO"
    )
    assert "CODE_SIGNING_REQUIRED=NO" in build_text, (
        "xcodebuild build command must include CODE_SIGNING_REQUIRED=NO"
    )

    # Check that code signing flags appear in test command
    test_text = " ".join(test_lines)
    assert "CODE_SIGNING_ALLOWED=NO" in test_text, (
        "xcodebuild test command must include CODE_SIGNING_ALLOWED=NO"
    )
    assert "CODE_SIGNING_REQUIRED=NO" in test_text, (
        "xcodebuild test command must include CODE_SIGNING_REQUIRED=NO"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_synchronized_headers_has_logic():
    """synchronizedHeaders function must contain real header-mapping logic."""
    content = TARGET_GEN.read_text()

    # Find the synchronizedHeaders function body
    match = re.search(
        r"(private\s+)?func\s+synchronizedHeaders\s*\((.*?)\)\s*->\s*\(.*?\)\s*\{",
        content,
        re.DOTALL,
    )
    assert match, "synchronizedHeaders function not found"

    # Extract approximate function body
    start = match.end()
    brace_depth = 1
    pos = start
    while pos < len(content) and brace_depth > 0:
        if content[pos] == "{":
            brace_depth += 1
        elif content[pos] == "}":
            brace_depth -= 1
        pos += 1
    body = content[start:pos]

    # Must have real logic — at least filtering, mapping, and set operations
    assert "isDescendant" in body or "relative" in body, (
        "synchronizedHeaders must compute relative paths or check descendants"
    )
    assert "subtracting" in body or "subtract" in body.lower() or "filter" in body, (
        "synchronizedHeaders must subtract existing exceptions from target headers"
    )
    assert len(body.strip().splitlines()) >= 10, (
        "synchronizedHeaders body is too short to contain real logic"
    )


# [static] pass_to_pass
def test_build_phase_call_passes_buildable_folders():
    """The call site in generateBuildPhases must pass buildableFolders."""
    content = BUILD_PHASE.read_text()

    # Find the call to generateHeadersBuildPhase within generateBuildPhases
    call_match = re.search(
        r"generateHeadersBuildPhase\s*\((.*?)\)",
        content,
        re.DOTALL,
    )
    assert call_match, "Call to generateHeadersBuildPhase not found"
    args = call_match.group(1)
    assert "buildableFolders" in args or "buildable" in args.lower(), (
        "generateHeadersBuildPhase call must pass buildableFolders argument"
    )
