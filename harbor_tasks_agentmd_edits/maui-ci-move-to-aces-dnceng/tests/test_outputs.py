"""
Task: maui-ci-move-to-aces-dnceng
Repo: dotnet/maui @ a633cc9b508792fbcf5daa2df9cd8a4fa98a0efe
PR:   33723

Migrate macOS CI pools from Azure Pipelines hosted images to AcesShared pool,
refactor Build.props to separate pack/build/device-test logic, improve Xcode
version fallback in provisioning, switch device tests from Cake to Arcade
build scripts, and update documentation accordingly.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path
import xml.etree.ElementTree as ET

REPO = "/workspace/maui"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_build_props_valid_xml():
    """eng/Build.props must parse as valid MSBuild XML."""
    props = Path(f"{REPO}/eng/Build.props").read_text()
    tree = ET.fromstring(props)
    # Must have at least one ItemGroup
    item_groups = tree.findall(
        ".//{http://schemas.microsoft.com/developer/msbuild/2003}ItemGroup"
    )
    assert len(item_groups) >= 1, "Build.props must contain at least one ItemGroup"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_build_props_pack_section():
    """Build.props must have a dedicated ItemGroup conditioned on Pack=='true'
    that selects the Packages solution filter for pack-only builds."""
    props = Path(f"{REPO}/eng/Build.props").read_text()
    tree = ET.fromstring(props)
    ns = {"m": "http://schemas.microsoft.com/developer/msbuild/2003"}

    pack_groups = [
        ig for ig in tree.findall(".//m:ItemGroup", ns)
        if ig.get("Condition") and "Pack" in ig.get("Condition", "")
    ]
    assert len(pack_groups) >= 1, (
        "Build.props must have an ItemGroup conditioned on $(Pack) for pack-only builds"
    )

    # The pack section should reference the Packages solution filter
    pack_xml = ET.tostring(pack_groups[0], encoding="unicode")
    assert "Packages" in pack_xml, (
        "Pack-conditioned ItemGroup must reference a Packages solution filter"
    )


# [pr_diff] fail_to_pass
def test_build_props_full_build_section():
    """Build.props must have a full-build section that references the main .sln
    and sets ValidateXcodeVersion=false."""
    props = Path(f"{REPO}/eng/Build.props").read_text()
    tree = ET.fromstring(props)
    ns = {"m": "http://schemas.microsoft.com/developer/msbuild/2003"}

    all_groups = tree.findall(".//m:ItemGroup", ns)
    full_build_found = False
    xcode_validation_disabled = False

    for ig in all_groups:
        items_xml = ET.tostring(ig, encoding="unicode")
        # Full build section references the main solution file (not Packages filters)
        if "Microsoft.Maui.sln" in items_xml or "Microsoft.Maui-mac.slnf" in items_xml:
            # Exclude pack-only groups (those referencing Packages filters only)
            if "Packages" not in items_xml:
                full_build_found = True
                if "ValidateXcodeVersion=false" in items_xml:
                    xcode_validation_disabled = True

    assert full_build_found, (
        "Build.props must have an ItemGroup referencing Microsoft.Maui.sln or "
        "Microsoft.Maui-mac.slnf for full builds"
    )
    assert xcode_validation_disabled, (
        "Full-build section must set ValidateXcodeVersion=false"
    )


# [pr_diff] fail_to_pass
def test_provision_xcode_cascading_fallback():
    """provision.yml Xcode selection must try cascading fallback versions:
    exact -> major.minor -> major (not just exact -> major.minor.0)."""
    provision = Path(f"{REPO}/eng/pipelines/common/provision.yml").read_text()

    # Must have a major-only fallback regex: ^([0-9]+)\. (captures just major)
    # The old code only had ^([0-9]+\.[0-9]+)\.[0-9]+$ (major.minor only)
    import re
    has_major_only_regex = bool(re.search(
        r"\^\(\[0-9\]\+\)\\?\.", provision
    ))
    assert has_major_only_regex, (
        "provision.yml must have a regex to extract the major-only version "
        "(e.g., ^([0-9]+)\\.) for fallback"
    )

    # Must loop through multiple fallback candidates (not just try one)
    assert "for " in provision, (
        "provision.yml must loop through version candidates"
    )

    # Must exit with error if no version found (not silently proceed)
    assert "exit 1" in provision, (
        "provision.yml must exit with error if no suitable Xcode version found"
    )


# [pr_diff] fail_to_pass
def test_ci_uses_aces_pool():
    """ci.yml must use AcesShared pool (not Azure Pipelines) for macOS builds."""
    ci = Path(f"{REPO}/eng/pipelines/ci.yml").read_text()

    assert "AcesShared" in ci, "ci.yml must reference the AcesShared pool"

    # Should not use 'Azure Pipelines' as pool name for macOS
    # Find macOS-related pool sections
    lines = ci.split("\n")
    for i, line in enumerate(lines):
        if "os: macOS" in line:
            # Look backwards for pool name
            context = "\n".join(lines[max(0, i - 5):i])
            assert "Azure Pipelines" not in context, (
                f"macOS pool near line {i+1} still references 'Azure Pipelines'"
            )


# [pr_diff] fail_to_pass
def test_stage_build_no_explicit_sln_project():
    """stage-build.yml main build step must rely on Build.props for project selection
    instead of passing -projects explicitly."""
    stage_build = Path(
        f"{REPO}/eng/pipelines/arcade/stage-build.yml"
    ).read_text()

    # Find the "Build Microsoft.Maui.sln" step
    lines = stage_build.split("\n")
    for i, line in enumerate(lines):
        if "Build Microsoft.Maui.sln" in line:
            # The script line should be just above (within 3 lines)
            script_context = "\n".join(lines[max(0, i - 3):i + 1])
            assert "-projects" not in script_context, (
                "Main sln build step should not pass -projects; "
                "Build.props now controls project selection"
            )
            break
    else:
        raise AssertionError("Could not find 'Build Microsoft.Maui.sln' step")


# [pr_diff] fail_to_pass
def test_device_tests_use_arcade_build():
    """stage-device-tests.yml must use Arcade build script (build.cmd -restore)
    instead of Cake (dotnet cake --target=dotnet) for .NET SDK installation."""
    device_tests = Path(
        f"{REPO}/eng/pipelines/arcade/stage-device-tests.yml"
    ).read_text()

    # Find the "Install .NET" step
    lines = device_tests.split("\n")
    found_install = False
    for i, line in enumerate(lines):
        if "Install .NET" in line:
            # Look at nearby lines for the script command
            context = "\n".join(lines[max(0, i - 3):i + 3])
            assert "dotnet cake" not in context, (
                "Install .NET step should use Arcade build script, not Cake"
            )
            assert "build.cmd" in context or "build.sh" in context, (
                "Install .NET step should use build.cmd/build.sh"
            )
            found_install = True
            break

    assert found_install, "Could not find 'Install .NET' step in stage-device-tests.yml"


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — documentation update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must mention build.sh -restore as the way to provision
    assert "build.sh" in dev_tips and "-restore" in dev_tips, (
        "DevelopmentTips.md must document build.sh -restore"
    )

    # Must indicate this is the recommended/preferred method
    content_lower = dev_tips.lower()
    assert "recommend" in content_lower or "prefer" in content_lower, (
        "DevelopmentTips.md must indicate build scripts are the recommended/preferred "
        "method for provisioning"
    )

    # The Arcade build section should mention restore separately from pack
    # (not just -restore -pack bundled together)
    assert "build.sh -restore\n" in dev_tips or \
           "build.sh -restore`" in dev_tips or \
           "build.sh -restore " in dev_tips or \
           "build.cmd -restore\n" in dev_tips or \
           "build.cmd -restore`" in dev_tips or \
           "build.cmd -restore " in dev_tips, (
        "DevelopmentTips.md must show -restore as a standalone operation "
        "(not only bundled with -pack)"
    )


# [config_edit] fail_to_pass

    # Must reference build.sh or build.cmd
    assert "build.sh" in readme or "build.cmd" in readme, (
        "Workload README must reference build.sh or build.cmd"
    )

    # The build example section should not use 'dotnet cake' as the primary command
    # Find the "After you've done a build" section
    build_section_start = readme.find("After you've done a build")
    if build_section_start != -1:
        # Check the next ~300 chars for the build command
        build_section = readme[build_section_start:build_section_start + 300]
        assert "dotnet cake" not in build_section, (
            "Workload README build example should use build.sh, not 'dotnet cake'"
        )
    else:
        # If section not found, at least check build.sh is present as a command
        assert "./build.sh" in readme, (
            "Workload README must show ./build.sh as a build command"
        )
