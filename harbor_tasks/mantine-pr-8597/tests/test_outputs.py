"""
Tests for @mantine/core selectFirstOptionOnDropdownOpen feature.
PR: mantinedev/mantine#8597

F2P (fail-to-pass): These tests verify the new selectFirstOptionOnDropdownOpen
prop is implemented. They FAIL on base commit, PASS after the fix.

P2P (pass-to-pass): These tests run lint commands.
They PASS on both base commit and after fix (verify no regressions).
"""

import subprocess
import os
import tempfile
import json
import re

REPO = "/workspace/repo"


class TestF2P:
    """Tests that FAIL on base commit and PASS after the fix is applied."""

    def test_combobox_types_has_new_prop(self):
        """F2P: ComboboxLikeProps interface must include selectFirstOptionOnDropdownOpen."""
        combobox_types = os.path.join(
            REPO, "packages/@mantine/core/src/components/Combobox/Combobox.types.ts"
        )
        with open(combobox_types, "r") as f:
            content = f.read()

        # Check for the distinctive JSDoc comment and prop name
        assert "If set, the first option is selected when dropdown opens" in content, (
            "JSDoc comment for selectFirstOptionOnDropdownOpen not found in Combobox.types.ts"
        )
        assert "selectFirstOptionOnDropdownOpen" in content, (
            "selectFirstOptionOnDropdownOpen prop not found in ComboboxLikeProps interface"
        )

    def test_select_implements_behavior(self):
        """F2P: Select must call combobox.selectFirstOption() when prop is true."""
        select_src = os.path.join(
            REPO, "packages/@mantine/core/src/components/Select/Select.tsx"
        )
        with open(select_src, "r") as f:
            content = f.read()

        # The fixed code must call selectFirstOption() in the onDropdownOpen handler
        assert "combobox.selectFirstOption()" in content, (
            "combobox.selectFirstOption() call not found in Select.tsx"
        )
        # The prop must be used in a conditional
        assert "selectFirstOptionOnDropdownOpen" in content, (
            "selectFirstOptionOnDropdownOpen prop not used in Select.tsx"
        )

    def test_autocomplete_implements_behavior(self):
        """F2P: Autocomplete must call combobox.selectFirstOption() when prop is true."""
        autocomplete_src = os.path.join(
            REPO, "packages/@mantine/core/src/components/Autocomplete/Autocomplete.tsx"
        )
        with open(autocomplete_src, "r") as f:
            content = f.read()

        assert "combobox.selectFirstOption()" in content, (
            "combobox.selectFirstOption() call not found in Autocomplete.tsx"
        )
        assert "selectFirstOptionOnDropdownOpen" in content, (
            "selectFirstOptionOnDropdownOpen prop not used in Autocomplete.tsx"
        )

    def test_multiselect_implements_behavior(self):
        """F2P: MultiSelect must call combobox.selectFirstOption() when prop is true."""
        multiselect_src = os.path.join(
            REPO, "packages/@mantine/core/src/components/MultiSelect/MultiSelect.tsx"
        )
        with open(multiselect_src, "r") as f:
            content = f.read()

        assert "combobox.selectFirstOption()" in content, (
            "combobox.selectFirstOption() call not found in MultiSelect.tsx"
        )
        assert "selectFirstOptionOnDropdownOpen" in content, (
            "selectFirstOptionOnDropdownOpen prop not used in MultiSelect.tsx"
        )

    def test_tagsinput_implements_behavior(self):
        """F2P: TagsInput must call combobox.selectFirstOption() when prop is true."""
        tagsinput_src = os.path.join(
            REPO, "packages/@mantine/core/src/components/TagsInput/TagsInput.tsx"
        )
        with open(tagsinput_src, "r") as f:
            content = f.read()

        assert "combobox.selectFirstOption()" in content, (
            "combobox.selectFirstOption() call not found in TagsInput.tsx"
        )
        assert "selectFirstOptionOnDropdownOpen" in content, (
            "selectFirstOptionOnDropdownOpen prop not used in TagsInput.tsx"
        )


class TestP2P:
    """Tests that PASS on both base commit and after fix (repo's lint/prettier)."""

    def test_repo_prettier(self):
        """P2P: Repo's prettier check passes on changed files."""
        r = subprocess.run(
            ["yarn", "prettier", "--check",
             "packages/@mantine/core/src/components/Select/Select.tsx",
             "packages/@mantine/core/src/components/MultiSelect/MultiSelect.tsx",
             "packages/@mantine/core/src/components/Autocomplete/Autocomplete.tsx",
             "packages/@mantine/core/src/components/TagsInput/TagsInput.tsx",
             "packages/@mantine/core/src/components/Combobox/Combobox.types.ts"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert r.returncode == 0, (
            f"Prettier check failed:\nSTDOUT:\n{r.stdout[-1000:]}\nSTDERR:\n{r.stderr[-500:]}"
        )

    def test_repo_lint(self):
        """P2P: Repo's lint (eslint + stylelint) passes on all packages."""
        r = subprocess.run(
            ["yarn", "lint"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert r.returncode == 0, (
            f"Lint check failed:\nSTDOUT:\n{r.stdout[-1000:]}\nSTDERR:\n{r.stderr[-500:]}"
        )

    def test_repo_syncpack(self):
        """P2P: Repo's syncpack check passes (no mismatched dependencies)."""
        r = subprocess.run(
            ["yarn", "syncpack"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert r.returncode == 0, (
            f"Syncpack check failed:\nSTDOUT:\n{r.stdout[-1000:]}\nSTDERR:\n{r.stderr[-500:]}"
        )
