"""
Test outputs for ant-design Image preview mask closable feature.

Tests verify:
1. TypeScript types have correct Omit pattern for maskClosable
2. useMergedMask hook returns the closable value as 3rd element
3. useMergedPreviewConfig hook returns maskClosable in its result
4. Image component tests pass (including new mask closable tests)
"""

import subprocess
import sys
import os
import json

REPO = "/workspace/ant-design"


def test_useMergedMask_returns_third_value():
    """
    useMergedMask hook should return a third value for maskClosable.

    F2P check: Verify that useMergedMask returns 3 values including mask closable.
    Before fix: returns [boolean, {mask: className}] (2 elements)
    After fix: returns [boolean, {mask: className}, boolean] (3 elements)
    """
    # Create a test file that imports and checks useMergedMask behavior
    test_code = """
import { useMergedMask } from './components/_util/hooks/useMergedMask';

// Type check: useMergedMask should return a 3-element tuple
// where the third element is a boolean (maskClosable)
function testReturnType() {
  const result = useMergedMask(true, true, 'prefix');

  // Verify we get 3 elements
  const [enabled, className, closable] = result;

  // closable should be boolean (the third return value)
  const isBoolean: boolean = closable;

  // Return values for runtime verification
  return {
    length: result.length,
    closableType: typeof closable,
    closableValue: closable
  };
}

export { testReturnType };
"""

    # Write test file to a temporary location in the repo
    test_file = f"{REPO}/test_merged_mask_check.ts"
    with open(test_file, "w") as f:
        f.write(test_code)

    # Create a minimal tsconfig for the test
    tsconfig = {
        "extends": "./tsconfig.json",
        "include": ["test_merged_mask_check.ts"],
        "compilerOptions": {
            "noEmit": True,
            "skipLibCheck": True
        }
    }
    tsconfig_file = f"{REPO}/tsconfig.test_mask.json"
    with open(tsconfig_file, "w") as f:
        json.dump(tsconfig, f)

    try:
        # Run TypeScript compiler to check types
        result = subprocess.run(
            ["npx", "tsc", "--project", "tsconfig.test_mask.json"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Clean up
        os.remove(test_file)
        os.remove(tsconfig_file)

        assert result.returncode == 0, (
            f"TypeScript compilation failed. useMergedMask may not return 3 values correctly.\n"
            f"Error: {result.stdout[-1000:]}{result.stderr[-1000:]}"
        )
    except Exception as e:
        # Clean up on error
        for f in [test_file, tsconfig_file]:
            if os.path.exists(f):
                os.remove(f)
        raise


def test_useMergedPreviewConfig_returns_maskClosable():
    """
    useMergedPreviewConfig hook should return maskClosable in its result type.

    F2P check: The return type of useMergedPreviewConfig should include maskClosable.
    Before fix: return type was T & { blurClassName?: string }
    After fix: return type is T & { blurClassName?: string; maskClosable?: boolean }
    """
    # Create a test file to verify the type system accepts maskClosable access
    test_code = """
import useMergedPreviewConfig from './components/image/hooks/useMergedPreviewConfig';
import type { PreviewConfig } from './components/image';

// Type check: verify that useMergedPreviewConfig result includes maskClosable
function testMaskClosableInReturnType() {
  const result = useMergedPreviewConfig(
    { mask: { closable: false } } as PreviewConfig,
    {} as PreviewConfig,
    'ant-image',
    '',
    undefined,
    {},
  );

  // This should compile - accessing maskClosable property
  const closable: boolean | undefined = result.maskClosable;

  // Return for verification
  return { hasMaskClosable: 'maskClosable' in result, closable };
}

export { testMaskClosableInReturnType };
"""

    test_file = f"{REPO}/test_preview_config_check.ts"
    with open(test_file, "w") as f:
        f.write(test_code)

    tsconfig = {
        "extends": "./tsconfig.json",
        "include": ["test_preview_config_check.ts"],
        "compilerOptions": {
            "noEmit": True,
            "skipLibCheck": True
        }
    }
    tsconfig_file = f"{REPO}/tsconfig.test_preview.json"
    with open(tsconfig_file, "w") as f:
        json.dump(tsconfig, f)

    try:
        # Run TypeScript compiler to check types
        result = subprocess.run(
            ["npx", "tsc", "--project", "tsconfig.test_preview.json"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Clean up
        os.remove(test_file)
        os.remove(tsconfig_file)

        assert result.returncode == 0, (
            f"TypeScript compilation failed. useMergedPreviewConfig may not return maskClosable correctly.\n"
            f"Error: {result.stdout[-1000:]}{result.stderr[-1000:]}"
        )
    except Exception as e:
        # Clean up on error
        for f in [test_file, tsconfig_file]:
            if os.path.exists(f):
                os.remove(f)
        raise


def test_Image_types_use_omit_pattern():
    """
    Image component types should use Omit to exclude maskClosable from public preview config.

    F2P check: Verify OriginPreviewConfig type correctly Omits maskClosable.
    Before fix: type OriginPreviewConfig = NonNullable<Exclude<RcImageProps['preview'], boolean>>
    After fix: type OriginPreviewConfig = Omit<NonNullable<Exclude<RcImageProps['preview'], boolean>>, 'maskClosable'>
    """
    # Create a test file that checks the type constraint
    test_code = """
import * as React from 'react';
import Image from './components/image';

// Type test: Verify that maskClosable is NOT directly on preview config
// (it should be under mask.closable instead)
function testOmitPattern() {
  // This should compile - using mask.closable
  const validConfig = {
    preview: {
      mask: { closable: true }
    }
  };

  // Create element to trigger type checking
  return React.createElement(Image, {
    src: 'test.jpg',
    ...validConfig
  });
}

// Verify that OriginPreviewConfig properly excludes maskClosable at top level
// by checking that the preview prop type accepts mask.closable
type PreviewProp = NonNullable<Exclude<React.ComponentProps<typeof Image>['preview'], boolean>>;
type MaskType = PreviewProp extends { mask?: infer M } ? M : never;
type MaskConfig = MaskType extends { closable?: infer C } ? C : never;

// If mask.closable is properly typed, MaskConfig should be boolean | undefined
const _typeCheck: MaskConfig = true;

export { testOmitPattern };
"""

    test_file = f"{REPO}/test_image_types_check.ts"
    with open(test_file, "w") as f:
        f.write(test_code)

    tsconfig = {
        "extends": "./tsconfig.json",
        "include": ["test_image_types_check.ts"],
        "compilerOptions": {
            "noEmit": True,
            "skipLibCheck": True
        }
    }
    tsconfig_file = f"{REPO}/tsconfig.test_image.json"
    with open(tsconfig_file, "w") as f:
        json.dump(tsconfig, f)

    try:
        # Run TypeScript compiler
        result = subprocess.run(
            ["npx", "tsc", "--project", "tsconfig.test_image.json"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Clean up
        os.remove(test_file)
        os.remove(tsconfig_file)

        assert result.returncode == 0, (
            f"TypeScript compilation failed. Image types may not use Omit pattern correctly.\n"
            f"Error: {result.stdout[-1000:]}{result.stderr[-1000:]}"
        )
    except Exception as e:
        for f in [test_file, tsconfig_file]:
            if os.path.exists(f):
                os.remove(f)
        raise


def test_PreviewGroup_types_use_omit_pattern():
    """
    PreviewGroup component types should use Omit to exclude maskClosable.

    F2P check: Verify OriginPreviewConfig type in PreviewGroup correctly Omits maskClosable.
    Before fix: type OriginPreviewConfig = NonNullable<Exclude<RcPreviewGroupProps['preview'], boolean>>
    After fix: type OriginPreviewConfig = Omit<NonNullable<Exclude<RcPreviewGroupProps['preview'], boolean>>, 'maskClosable'>
    """
    # Create a test file that checks the type constraint
    test_code = """
import * as React from 'react';
import { PreviewGroup } from './components/image';

// Type test: Verify that PreviewGroup accepts mask.closable configuration
function testPreviewGroupOmitPattern() {
  // This should compile - using mask.closable
  const validConfig = {
    preview: {
      mask: { closable: false }
    }
  };

  // Create element to trigger type checking
  return React.createElement(PreviewGroup, validConfig);
}

// Verify that the preview prop type accepts mask.closable
type PreviewGroupProps = React.ComponentProps<typeof PreviewGroup>;
type PreviewConfig = NonNullable<Exclude<PreviewGroupProps['preview'], boolean>>;
type MaskType = PreviewConfig extends { mask?: infer M } ? M : never;
type MaskConfig = MaskType extends { closable?: infer C } ? C : never;

// If mask.closable is properly typed, MaskConfig should be boolean | undefined
const _typeCheck: MaskConfig = false;

export { testPreviewGroupOmitPattern };
"""

    test_file = f"{REPO}/test_previewgroup_types_check.ts"
    with open(test_file, "w") as f:
        f.write(test_code)

    tsconfig = {
        "extends": "./tsconfig.json",
        "include": ["test_previewgroup_types_check.ts"],
        "compilerOptions": {
            "noEmit": True,
            "skipLibCheck": True
        }
    }
    tsconfig_file = f"{REPO}/tsconfig.test_previewgroup.json"
    with open(tsconfig_file, "w") as f:
        json.dump(tsconfig, f)

    try:
        # Run TypeScript compiler
        result = subprocess.run(
            ["npx", "tsc", "--project", "tsconfig.test_previewgroup.json"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Clean up
        os.remove(test_file)
        os.remove(tsconfig_file)

        assert result.returncode == 0, (
            f"TypeScript compilation failed. PreviewGroup types may not use Omit pattern correctly.\n"
            f"Error: {result.stdout[-1000:]}{result.stderr[-1000:]}"
        )
    except Exception as e:
        for f in [test_file, tsconfig_file]:
            if os.path.exists(f):
                os.remove(f)
        raise


def test_image_mask_closable_tests():
    """
    Image component mask closable tests should pass.

    P2P check: Run the existing Jest tests for Image component.
    This verifies the entire component works correctly including the new mask closable feature.
    """
    result = subprocess.run(
        ["npm", "test", "--", "image/__tests__/index", "--no-coverage"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )

    # Check test output for failures
    if result.returncode != 0:
        # Show relevant part of the output
        output = result.stdout + result.stderr
        assert result.returncode == 0, f"Image tests failed:\n{output[-2000:]}"


def test_image_biome_check():
    """
    Image component should pass Biome checks (format and lint).

    P2P check: Repo code quality check via Biome.
    """
    # First generate version file (required for repo state)
    subprocess.run(
        ["npm", "run", "version"],
        cwd=REPO,
        capture_output=True,
        timeout=60,
    )

    result = subprocess.run(
        ["npx", "biome", "check", "components/image"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Biome check failed:\n{result.stderr[-500:]}"


def test_image_biome_lint():
    """
    Image component should pass Biome lint rules.

    P2P check: Repo linting via Biome.
    """
    result = subprocess.run(
        ["npx", "biome", "lint", "components/image"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Biome lint failed:\n{result.stderr[-500:]}"


def test_image_eslint():
    """
    Image component should pass ESLint checks.

    P2P check: Repo linting via ESLint.
    """
    result = subprocess.run(
        ["npx", "eslint", "components/image", "--cache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stderr[-500:]}"


def test_image_jest_tests():
    """
    All Image component Jest tests should pass.

    P2P check: Run the Jest tests for Image component (index, semantic, demo, etc).
    This verifies the entire Image component works correctly.
    """
    # Generate version file (required for repo state)
    subprocess.run(
        ["npm", "run", "version"],
        cwd=REPO,
        capture_output=True,
        timeout=60,
    )

    result = subprocess.run(
        [
            "npx", "jest", "--config", ".jest.js",
            "--testPathPatterns=image/__tests__",
            "--no-cache", "--maxWorkers=2"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Image Jest tests failed:\n{result.stdout[-2000:]}"


if __name__ == "__main__":
    # Allow running individual tests via command line
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
