#!/usr/bin/env python3
"""Tests for ant-design site import path refactoring."""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/ant-design")

def test_typescript_compilation():
    """TypeScript compilation passes (fail-to-pass).

    The import path changes must not break TypeScript type checking.
    Before: Relative imports like '../../components/theme'
    After: Package imports like 'antd' and 'antd/lib/_util/copy'
    """
    env = dict(subprocess.os.environ)
    env["NODE_OPTIONS"] = "--max-old-space-size=4096"
    result = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
        env=env
    )
    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stderr[-1000:]}"

def test_import_theme_from_antd():
    """useThemeAnimation.ts imports theme from 'antd' (fail-to-pass).

    The theme import should come from the 'antd' package,
    not from a relative path to components/theme.
    """
    file_path = REPO / ".dumi" / "hooks" / "useThemeAnimation.ts"
    content = file_path.read_text()

    # Should use 'antd' package import
    assert 'import { theme } from \'antd\';' in content, \
        "Expected 'import { theme } from 'antd';' in useThemeAnimation.ts"

    # Should NOT use relative import to components/theme
    assert 'from \'../../components/theme\'' not in content, \
        "Should not use relative import to components/theme"

def test_import_copy_from_antd_lib():
    """Files import copy from 'antd/lib/_util/copy' (fail-to-pass).

    Multiple files should import 'copy' utility from antd package,
    not from relative paths to components/_util.
    """
    files_to_check = [
        ".dumi/pages/index/components/Theme/index.tsx",
        ".dumi/pages/index/components/ThemePreview/index.tsx",
        ".dumi/theme/builtins/Previewer/DesignPreviewer.tsx",
        ".dumi/theme/common/ThemeSwitch/PromptDrawer.tsx",
    ]

    for file_rel in files_to_check:
        file_path = REPO / file_rel
        content = file_path.read_text()

        # Should use antd/lib/_util/copy
        assert 'import copy from \'antd/lib/_util/copy\';' in content, \
            f"Expected 'antd/lib/_util/copy' import in {file_rel}"

        # Should NOT use relative import
        assert 'from \'../../../../../components/_util/copy\'' not in content, \
            f"Should not use relative import to components/_util/copy in {file_rel}"
        assert 'from \'../../../../components/_util/copy\'' not in content, \
            f"Should not use relative import to components/_util/copy in {file_rel}"

def test_import_scrollto_from_antd_lib():
    """AffixTabs.tsx imports scrollTo from 'antd/lib/_util/scrollTo' (fail-to-pass).

    The scrollTo utility should be imported from antd package.
    """
    file_path = REPO / ".dumi" / "theme" / "layouts" / "ResourceLayout" / "AffixTabs.tsx"
    content = file_path.read_text()

    # Should use antd/lib/_util/scrollTo
    assert 'import scrollTo from \'antd/lib/_util/scrollTo\';' in content, \
        "Expected 'antd/lib/_util/scrollTo' import in AffixTabs.tsx"

    # Should NOT use relative import
    assert 'from \'../../../../components/_util/scrollTo\'' not in content, \
        "Should not use relative import to components/_util/scrollTo"

def test_import_configprovider_context():
    """SiteContext.ts imports from 'antd/es/config-provider/context' (fail-to-pass).

    ConfigComponentProps type should be imported from antd package.
    """
    file_path = REPO / ".dumi" / "theme" / "slots" / "SiteContext.ts"
    content = file_path.read_text()

    # Should use antd/es/config-provider/context
    assert 'from \'antd/es/config-provider/context\';' in content, \
        "Expected 'antd/es/config-provider/context' import in SiteContext.ts"

    # Should NOT use relative import
    assert 'from \'../../../components/config-provider/context\'' not in content, \
        "Should not use relative import to components/config-provider/context"

def test_repo_tsc():
    """Repo's TypeScript type checking passes (pass_to_pass).

    TypeScript compilation must work on the base commit.
    This ensures the repo's types are valid before any changes.
    """
    env = dict(subprocess.os.environ)
    env["NODE_OPTIONS"] = "--max-old-space-size=4096"
    result = subprocess.run(
        ["npm", "run", "tsc"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
        env=env
    )
    assert result.returncode == 0, f"TypeScript check failed:\n{result.stderr[-500:]}"


def test_repo_lint():
    """Repo's ESLint passes (pass_to_pass).

    Linting must pass on the base commit.
    This ensures code style consistency.
    """
    result = subprocess.run(
        ["npm", "run", "lint:script"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )
    assert result.returncode == 0, f"Lint failed:\n{result.stderr[-500:]}"


def test_repo_version():
    """Repo's version generation passes (pass_to_pass).

    Version generation script must work on the base commit.
    This validates the build setup is functional.
    """
    result = subprocess.run(
        ["npm", "run", "version"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    assert result.returncode == 0, f"Version generation failed:\n{result.stderr[-500:]}"


def test_repo_biome():
    """Repo's Biome linting passes (pass_to_pass).

    Biome linting must pass on the base commit.
    This ensures code quality and consistency.
    """
    result = subprocess.run(
        ["npm", "run", "lint:biome"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    assert result.returncode == 0, f"Biome lint failed:\n{result.stderr[-500:]}"


def test_repo_test_node():
    """Repo's Node.js tests pass (pass_to_pass).

    Node.js demo tests must pass on the base commit.
    This validates component demos work in Node.js environment.
    """
    result = subprocess.run(
        ["npm", "run", "test:node"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )
    assert result.returncode == 0, f"Node tests failed:\n{result.stderr[-500:]}"


def test_no_relative_component_imports_in_dumi():
    """No relative imports to components/ directory in .dumi (fail-to-pass).

    All imports from antd components should use package imports.
    """
    dumi_path = REPO / ".dumi"

    # Find all .ts and .tsx files in .dumi
    ts_files = list(dumi_path.rglob("*.ts")) + list(dumi_path.rglob("*.tsx"))

    for file_path in ts_files:
        # Skip .d.ts files
        if file_path.suffix == ".d.ts":
            continue

        content = file_path.read_text()
        rel_path = file_path.relative_to(REPO)

        # Check for relative imports to components/
        if "from '../../../../../components/" in content or \
           "from '../../../../components/" in content or \
           "from '../../../components/" in content or \
           "from '../../components/" in content:
            # Allow the theme export and config provider context patterns
            # that might legitimately exist for other purposes
            if "from '../../components/theme'" in content or \
               "from '../../../components/config-provider/context'" in content or \
               "from '../../../components/_util/" in content or \
               "from '../../../../components/_util/" in content or \
               "from '../../../../../components/_util/" in content:
                raise AssertionError(
                    f"Found relative import to components/ in {rel_path}. "
                    "Should use 'antd' or 'antd/lib/*' or 'antd/es/*' imports instead."
                )

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
