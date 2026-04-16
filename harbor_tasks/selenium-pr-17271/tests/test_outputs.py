"""Tests for Selenium Manager platform/architecture detection improvements.

This module tests the behavioral changes from PR #17271:
- Windows now requires x86_64 architecture (ARM64 raises exception)
- BSD platform names with version numbers are normalized (freebsd15 -> freebsd)
- AMD64/amd64 architecture is normalized to x86_64
- FreeBSD warning message includes actionable guidance
"""

import logging
import subprocess
import sys
import sysconfig
from pathlib import Path
from unittest import mock

import pytest

REPO = Path("/workspace/selenium")
sys.path.insert(0, str(REPO / "py"))

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.selenium_manager import SeleniumManager
import selenium


# Helper to mock Path.is_file for specific expected paths
def mock_is_file_for_path(expected_suffix):
    """Create a mock that returns True for paths ending with expected_suffix."""
    original_is_file = Path.is_file
    def patched_is_file(self):
        if str(self).endswith(expected_suffix):
            return True
        return original_is_file(self)
    return patched_is_file


# Helper to mock sysconfig for non-native platforms
def mock_sysconfig(exe_suffix=""):
    """Create a mock for sysconfig.get_config_var."""
    def get_config_var(name):
        if name == "EXE":
            return exe_suffix
        return None
    return get_config_var


class TestWindowsArm64Rejection:
    """Tests that Windows ARM64 architecture is properly rejected (fail_to_pass)."""

    def test_windows_arm64_raises_exception(self, monkeypatch):
        """Windows with ARM64 architecture should raise WebDriverException."""
        monkeypatch.setattr(sys, "platform", "win32")
        monkeypatch.setattr("platform.machine", lambda: "ARM64")
        monkeypatch.setattr(sysconfig, "get_config_var", mock_sysconfig(".exe"))

        with pytest.raises(WebDriverException) as excinfo:
            SeleniumManager()._get_binary()

        assert "Unsupported platform/architecture combination" in str(excinfo.value)
        assert "win32" in str(excinfo.value)
        assert "arm64" in str(excinfo.value).lower()

    def test_windows_arm64_lowercase_raises_exception(self, monkeypatch):
        """Windows with lowercase arm64 architecture should also raise."""
        monkeypatch.setattr(sys, "platform", "win32")
        monkeypatch.setattr("platform.machine", lambda: "arm64")
        monkeypatch.setattr(sysconfig, "get_config_var", mock_sysconfig(".exe"))

        with pytest.raises(WebDriverException) as excinfo:
            SeleniumManager()._get_binary()

        assert "Unsupported platform/architecture combination" in str(excinfo.value)

    def test_cygwin_arm64_raises_exception(self, monkeypatch):
        """Cygwin with ARM64 should also raise exception."""
        monkeypatch.setattr(sys, "platform", "cygwin")
        monkeypatch.setattr("platform.machine", lambda: "ARM64")
        monkeypatch.setattr(sysconfig, "get_config_var", mock_sysconfig(".exe"))

        with pytest.raises(WebDriverException) as excinfo:
            SeleniumManager()._get_binary()

        assert "Unsupported platform/architecture combination" in str(excinfo.value)


class TestBsdPlatformNormalization:
    """Tests that BSD platform names with version numbers are normalized (fail_to_pass)."""

    def test_freebsd_with_version_number(self, monkeypatch, caplog):
        """FreeBSD with version number (e.g., freebsd15) should work."""
        monkeypatch.setattr(sys, "platform", "freebsd15")
        monkeypatch.setattr("platform.machine", lambda: "x86_64")
        monkeypatch.setattr(sysconfig, "get_config_var", mock_sysconfig(""))
        monkeypatch.setattr(Path, "is_file", mock_is_file_for_path("linux/selenium-manager"))

        root = logging.getLogger()
        caplog_handler = caplog.handler
        old_handlers = root.handlers[:]
        root.handlers = [caplog_handler]

        try:
            binary = SeleniumManager()._get_binary()
            project_root = Path(selenium.__file__).parent.parent
            assert binary == project_root.joinpath("selenium/webdriver/common/linux/selenium-manager")
        finally:
            root.handlers = old_handlers

    def test_freebsd14_with_amd64(self, monkeypatch, caplog):
        """FreeBSD 14 with amd64 architecture should work."""
        monkeypatch.setattr(sys, "platform", "freebsd14")
        monkeypatch.setattr("platform.machine", lambda: "amd64")
        monkeypatch.setattr(sysconfig, "get_config_var", mock_sysconfig(""))
        monkeypatch.setattr(Path, "is_file", mock_is_file_for_path("linux/selenium-manager"))

        root = logging.getLogger()
        caplog_handler = caplog.handler
        old_handlers = root.handlers[:]
        root.handlers = [caplog_handler]

        try:
            binary = SeleniumManager()._get_binary()
            project_root = Path(selenium.__file__).parent.parent
            assert binary == project_root.joinpath("selenium/webdriver/common/linux/selenium-manager")
        finally:
            root.handlers = old_handlers

    def test_openbsd_with_version_number(self, monkeypatch, caplog):
        """OpenBSD with version number (e.g., openbsd7) should work."""
        monkeypatch.setattr(sys, "platform", "openbsd7")
        monkeypatch.setattr("platform.machine", lambda: "x86_64")
        monkeypatch.setattr(sysconfig, "get_config_var", mock_sysconfig(""))
        monkeypatch.setattr(Path, "is_file", mock_is_file_for_path("linux/selenium-manager"))

        root = logging.getLogger()
        caplog_handler = caplog.handler
        old_handlers = root.handlers[:]
        root.handlers = [caplog_handler]

        try:
            binary = SeleniumManager()._get_binary()
            project_root = Path(selenium.__file__).parent.parent
            assert binary == project_root.joinpath("selenium/webdriver/common/linux/selenium-manager")
        finally:
            root.handlers = old_handlers


class TestArchitectureNormalization:
    """Tests that AMD64 architecture variants are normalized to x86_64 (fail_to_pass)."""

    def test_windows_amd64_uppercase(self, monkeypatch):
        """Windows with uppercase AMD64 should work (normalized to x86_64)."""
        monkeypatch.setattr(sys, "platform", "win32")
        monkeypatch.setattr("platform.machine", lambda: "AMD64")
        monkeypatch.setattr(sysconfig, "get_config_var", mock_sysconfig(".exe"))
        monkeypatch.setattr(Path, "is_file", mock_is_file_for_path("windows/selenium-manager.exe"))

        binary = SeleniumManager()._get_binary()
        project_root = Path(selenium.__file__).parent.parent
        assert binary == project_root.joinpath("selenium/webdriver/common/windows/selenium-manager.exe")

    def test_windows_amd64_lowercase(self, monkeypatch):
        """Windows with lowercase amd64 should also work."""
        monkeypatch.setattr(sys, "platform", "win32")
        monkeypatch.setattr("platform.machine", lambda: "amd64")
        monkeypatch.setattr(sysconfig, "get_config_var", mock_sysconfig(".exe"))
        monkeypatch.setattr(Path, "is_file", mock_is_file_for_path("windows/selenium-manager.exe"))

        binary = SeleniumManager()._get_binary()
        project_root = Path(selenium.__file__).parent.parent
        assert binary == project_root.joinpath("selenium/webdriver/common/windows/selenium-manager.exe")

    def test_linux_amd64_normalization(self, monkeypatch):
        """Linux with amd64 should work (normalized to x86_64)."""
        monkeypatch.setattr(sys, "platform", "linux")
        monkeypatch.setattr("platform.machine", lambda: "amd64")
        monkeypatch.setattr(Path, "is_file", mock_is_file_for_path("linux/selenium-manager"))

        binary = SeleniumManager()._get_binary()
        project_root = Path(selenium.__file__).parent.parent
        assert binary == project_root.joinpath("selenium/webdriver/common/linux/selenium-manager")


class TestFreebsdWarningMessage:
    """Tests that FreeBSD warning message includes actionable guidance (fail_to_pass)."""

    def test_freebsd_warning_contains_brandelf(self, monkeypatch, caplog):
        """FreeBSD warning should mention 'brandelf -t linux' for actionable guidance."""
        monkeypatch.setattr(sys, "platform", "freebsd15")
        monkeypatch.setattr("platform.machine", lambda: "amd64")
        monkeypatch.setattr(sysconfig, "get_config_var", mock_sysconfig(""))
        monkeypatch.setattr(Path, "is_file", mock_is_file_for_path("linux/selenium-manager"))

        root = logging.getLogger()
        caplog_handler = caplog.handler
        old_handlers = root.handlers[:]
        root.handlers = [caplog_handler]

        try:
            with caplog.at_level(logging.WARNING):
                SeleniumManager()._get_binary()

            warning_text = caplog.text
            assert "brandelf" in warning_text.lower() or "linux64.ko" in warning_text
        finally:
            root.handlers = old_handlers

    def test_freebsd_warning_contains_linux64ko(self, monkeypatch, caplog):
        """FreeBSD warning should mention linux64.ko for kernel module loading."""
        monkeypatch.setattr(sys, "platform", "freebsd14")
        monkeypatch.setattr("platform.machine", lambda: "x86_64")
        monkeypatch.setattr(sysconfig, "get_config_var", mock_sysconfig(""))
        monkeypatch.setattr(Path, "is_file", mock_is_file_for_path("linux/selenium-manager"))

        root = logging.getLogger()
        caplog_handler = caplog.handler
        old_handlers = root.handlers[:]
        root.handlers = [caplog_handler]

        try:
            with caplog.at_level(logging.WARNING):
                SeleniumManager()._get_binary()

            warning_text = caplog.text
            assert "linux64.ko" in warning_text or "brandelf" in warning_text
        finally:
            root.handlers = old_handlers


class TestExistingBehavior:
    """Tests that existing platform detection still works (pass_to_pass)."""

    def test_linux_x86_64_still_works(self, monkeypatch):
        """Linux with x86_64 should continue to work."""
        monkeypatch.setattr(sys, "platform", "linux")
        monkeypatch.setattr("platform.machine", lambda: "x86_64")
        monkeypatch.setattr(Path, "is_file", mock_is_file_for_path("linux/selenium-manager"))

        binary = SeleniumManager()._get_binary()
        project_root = Path(selenium.__file__).parent.parent
        assert binary == project_root.joinpath("selenium/webdriver/common/linux/selenium-manager")

    def test_darwin_any_arch_still_works(self, monkeypatch):
        """macOS should continue to work with any architecture."""
        monkeypatch.setattr(sys, "platform", "darwin")
        monkeypatch.setattr(sysconfig, "get_config_var", mock_sysconfig(""))
        monkeypatch.setattr(Path, "is_file", mock_is_file_for_path("macos/selenium-manager"))

        binary = SeleniumManager()._get_binary()
        project_root = Path(selenium.__file__).parent.parent
        assert binary == project_root.joinpath("selenium/webdriver/common/macos/selenium-manager")

    def test_invalid_platform_still_raises(self, monkeypatch):
        """Invalid platform should still raise exception."""
        monkeypatch.setattr(sys, "platform", "unknown_platform")
        monkeypatch.setattr("platform.machine", lambda: "x86_64")
        monkeypatch.setattr(sysconfig, "get_config_var", mock_sysconfig(""))

        with pytest.raises(WebDriverException) as excinfo:
            SeleniumManager()._get_binary()

        assert "Unsupported platform/architecture combination" in str(excinfo.value)


class TestRepoUnitTests:
    """Run the repository's existing unit tests (pass_to_pass)."""

    def test_repo_selenium_manager_tests(self):
        """Repository's selenium_manager_tests.py should pass."""
        result = subprocess.run(
            ["python", "-m", "pytest",
             "py/test/unit/selenium/webdriver/common/selenium_manager_tests.py",
             "-v", "--tb=short"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )
        assert result.returncode == 0, f"Tests failed:\n{result.stdout}\n{result.stderr}"


class TestRepoLinting:
    """Run the repository's linting tools (pass_to_pass)."""

    def test_repo_ruff_lint_selenium_manager(self):
        """Ruff lint check passes on selenium_manager.py."""
        result = subprocess.run(
            ["bash", "-c",
             "pip install --quiet ruff==0.15.6 && "
             "ruff check selenium/webdriver/common/selenium_manager.py"],
            cwd=REPO / "py",
            capture_output=True,
            text=True,
            timeout=120
        )
        assert result.returncode == 0, f"Ruff lint failed:\n{result.stdout}\n{result.stderr}"

    def test_repo_ruff_format_selenium_manager(self):
        """Ruff format check passes on selenium_manager.py."""
        result = subprocess.run(
            ["bash", "-c",
             "pip install --quiet ruff==0.15.6 && "
             "ruff format --check selenium/webdriver/common/selenium_manager.py"],
            cwd=REPO / "py",
            capture_output=True,
            text=True,
            timeout=120
        )
        assert result.returncode == 0, f"Ruff format check failed:\n{result.stdout}\n{result.stderr}"

    def test_repo_pyproject_valid(self):
        """pyproject.toml is valid."""
        result = subprocess.run(
            ["bash", "-c",
             "pip install --quiet validate-pyproject==0.25 packaging==26.0 && "
             "validate-pyproject pyproject.toml"],
            cwd=REPO / "py",
            capture_output=True,
            text=True,
            timeout=120
        )
        assert result.returncode == 0, f"pyproject.toml validation failed:\n{result.stdout}\n{result.stderr}"
