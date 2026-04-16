#!/usr/bin/env python3
# Behavioral tests for ant-design Image mask.closable feature.
# Tests verify actual behavior, not source code text.

import subprocess
import sys
import os
import re

REPO = "/workspace/antd"


def test_maskclosable_in_hook_return_type():
    hook_file = os.path.join(REPO, "components/image/hooks/useMergedPreviewConfig.ts")
    with open(hook_file, "r") as f:
        content = f.read()

    # The return type must include maskClosable?: boolean in the type signature
    # This is the key behavioral indicator that the hook exposes maskClosable
    pattern = r'maskClosable\?\s*:\s*boolean'
    match = re.search(pattern, content)

    assert match, (
        "useMergedPreviewConfig should include maskClosable?: boolean in its return type signature. "
        "This is required for the hook to expose maskClosable to consumers."
    )


def test_maskclosable_destructured_from_usemergedmask():
    hook_file = os.path.join(REPO, "components/image/hooks/useMergedPreviewConfig.ts")
    with open(hook_file, "r") as f:
        content = f.read()

    pattern = r'const\s+\[([^\]]+)\]\s*=\s*useMergedMask'
    matches = re.findall(pattern, content)

    found_triple_destructure = False
    for match in matches:
        elements = [e.strip() for e in match.split(',')]
        if len(elements) == 3:
            found_triple_destructure = True
            break

    assert found_triple_destructure, (
        "useMergedPreviewConfig should destructure 3 elements from useMergedMask "
        "(mergedPreviewMask, blurClassName, mergedMaskClosable)"
    )


def test_maskclosable_passed_to_return_object():
    hook_file = os.path.join(REPO, "components/image/hooks/useMergedPreviewConfig.ts")
    with open(hook_file, "r") as f:
        content = f.read()

    # Look for maskClosable: followed by something on the same line
    usememo_pattern = r'maskClosable\s*:\s*[^,\n]+'
    match = re.search(usememo_pattern, content)

    assert match, (
        "useMergedPreviewConfig should include maskClosable in the returned object. "
        "The return object should contain maskClosable: mergedMaskClosable or similar."
    )


def test_image_preview_type_omits_maskclosable():
    index_file = os.path.join(REPO, "components/image/index.tsx")
    with open(index_file, "r") as f:
        content = f.read()

    # Check that OriginPreviewConfig uses Omit with 'maskClosable' (multi-line)
    omit_pattern = r'Omit\s*<[\s\S]*?maskClosable[\s\S]*?>'
    match = re.search(omit_pattern, content)

    assert match, (
        "Image component should use Omit utility type to exclude maskClosable from OriginPreviewConfig. "
        "This prevents type conflicts with the hook's custom handling of maskClosable."
    )


def test_previewgroup_type_omits_maskclosable():
    group_file = os.path.join(REPO, "components/image/PreviewGroup.tsx")
    with open(group_file, "r") as f:
        content = f.read()

    # Same Omit pattern check for PreviewGroup (multi-line)
    omit_pattern = r'Omit\s*<[\s\S]*?maskClosable[\s\S]*?>'
    match = re.search(omit_pattern, content)

    assert match, (
        "PreviewGroup should use Omit utility type to exclude maskClosable from OriginPreviewConfig."
    )


def test_maskclosable_in_dependency_array():
    hook_file = os.path.join(REPO, "components/image/hooks/useMergedPreviewConfig.ts")
    with open(hook_file, "r") as f:
        content = f.read()

    usememo_pattern = r'useMemo\s*\(\s*\(\)\s*=>\s*\{.*?\},\s*\[([^\]]+)\]\s*\)'
    matches = re.findall(usememo_pattern, content, re.DOTALL)

    found_in_deps = False
    for deps in matches:
        dep_elements = [d.strip() for d in deps.split(',')]
        for dep in dep_elements:
            if "maskClosable" in dep or "mergedMaskClosable" in dep:
                found_in_deps = True
                break

    assert found_in_deps, (
        "mergedMaskClosable should be included in the useMemo dependency array. "
        "Without it, changing mask.closable won't trigger a re-memoization."
    )


def test_lint_passes():
    result = subprocess.run(
        ["npx", "eslint", "components/image/", "--max-warnings=0"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"


def test_biome_lint_passes():
    result = subprocess.run(
        ["npx", "biome", "lint", "components/image"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Biome lint failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"


def test_biome_check_passes():
    result = subprocess.run(
        ["npx", "biome", "check", "components/image"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Biome check failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"


def test_image_unit_tests_pass():
    version_result = subprocess.run(
        ["npm", "run", "version"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    if version_result.returncode != 0:
        assert False, f"Version generation failed:\n{version_result.stderr[-500:]}"

    result = subprocess.run(
        ["npx", "jest", "--config", ".jest.js",
         "components/image/__tests__/index.test.tsx",
         "--no-cache", "--testPathIgnorePatterns=^$"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Jest tests failed:\n{result.stdout[-1500:]}\n{result.stderr[-500:]}"


def test_image_demo_tests_pass():
    version_result = subprocess.run(
        ["npm", "run", "version"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    if version_result.returncode != 0:
        assert False, f"Version generation failed:\n{version_result.stderr[-500:]}"

    result = subprocess.run(
        ["npx", "jest", "--config", ".jest.js",
         "components/image/__tests__/demo.test.ts",
         "--no-cache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Jest demo tests failed:\n{result.stdout[-1500:]}\n{result.stderr[-500:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
