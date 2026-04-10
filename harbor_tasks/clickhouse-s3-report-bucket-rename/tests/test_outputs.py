"""
Tests for PR #102032: Rename HTML_S3_PATH to S3_REPORT_BUCKET and add upstream catalog merge.

These tests verify:
1. HTML_S3_PATH is renamed to S3_REPORT_BUCKET in all files
2. New S3_UPSTREAM_REPORT_BUCKET setting exists
3. TestCaseIssueCatalog has _download_catalog method
4. TestCaseIssueCatalog.from_s3 merges catalogs when upstream is configured
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add repo to path
REPO = "/workspace/ClickHouse"
sys.path.insert(0, REPO)

# Python files that were modified in the PR
MODIFIED_FILES = [
    "ci/jobs/collect_statistics.py",
    "ci/praktika/hook_html.py",
    "ci/praktika/html_prepare.py",
    "ci/praktika/info.py",
    "ci/praktika/issue.py",
    "ci/praktika/result.py",
    "ci/praktika/s3.py",
    "ci/praktika/settings.py",
    "ci/praktika/validator.py",
    "ci/settings/settings.py",
]


def test_html_s3_path_removed():
    """FAIL-TO-PASS: Verify HTML_S3_PATH is no longer used anywhere in the codebase."""
    errors = []

    for file_path in MODIFIED_FILES:
        full_path = os.path.join(REPO, file_path)
        if not os.path.exists(full_path):
            continue

        with open(full_path, 'r') as f:
            content = f.read()

        # Check for any remaining references to HTML_S3_PATH (except in comments)
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue
            if 'HTML_S3_PATH' in line:
                errors.append(f"{file_path}:{i}: {line.strip()}")

    assert not errors, f"Found remaining HTML_S3_PATH references:\n" + "\n".join(errors[:10])


def test_s3_report_bucket_exists_in_settings():
    """FAIL-TO-PASS: Verify S3_REPORT_BUCKET is defined in settings.py."""
    settings_file = os.path.join(REPO, "ci/praktika/settings.py")

    with open(settings_file, 'r') as f:
        content = f.read()

    assert 'S3_REPORT_BUCKET: str = ""' in content, \
        "S3_REPORT_BUCKET setting not found in settings.py"


def test_s3_upstream_report_bucket_exists():
    """FAIL-TO-PASS: Verify S3_UPSTREAM_REPORT_BUCKET is defined in settings.py."""
    settings_file = os.path.join(REPO, "ci/praktika/settings.py")

    with open(settings_file, 'r') as f:
        content = f.read()

    assert 'S3_UPSTREAM_REPORT_BUCKET: str = ""' in content, \
        "S3_UPSTREAM_REPORT_BUCKET setting not found in settings.py"


def test_s3_upstream_report_bucket_in_user_defined():
    """FAIL-TO-PASS: Verify S3_UPSTREAM_REPORT_BUCKET is in _USER_DEFINED_SETTINGS list."""
    settings_file = os.path.join(REPO, "ci/praktika/settings.py")

    with open(settings_file, 'r') as f:
        content = f.read()

    assert '"S3_UPSTREAM_REPORT_BUCKET"' in content, \
        "S3_UPSTREAM_REPORT_BUCKET not found in _USER_DEFINED_SETTINGS list"


def test_download_catalog_method_exists():
    """FAIL-TO-PASS: Verify TestCaseIssueCatalog has _download_catalog method."""
    # Import the issue module
    issue_file = os.path.join(REPO, "ci/praktika/issue.py")

    with open(issue_file, 'r') as f:
        content = f.read()

    assert 'def _download_catalog(cls, bucket, suffix=""):' in content, \
        "_download_catalog method not found in TestCaseIssueCatalog"


def test_settings_import_in_issue_py():
    """FAIL-TO-PASS: Verify issue.py imports Settings from praktika.settings."""
    issue_file = os.path.join(REPO, "ci/praktika/issue.py")

    with open(issue_file, 'r') as f:
        content = f.read()

    assert 'from praktika.settings import Settings' in content, \
        "Settings import not found in issue.py"


def test_issue_to_s3_uses_settings():
    """FAIL-TO-PASS: Verify to_s3 uses Settings.S3_REPORT_BUCKET."""
    issue_file = os.path.join(REPO, "ci/praktika/issue.py")

    with open(issue_file, 'r') as f:
        content = f.read()

    # Check that to_s3 uses Settings.S3_REPORT_BUCKET
    assert 'Settings.S3_REPORT_BUCKET' in content, \
        "to_s3 should use Settings.S3_REPORT_BUCKET"


def test_from_s3_merge_logic():
    """FAIL-TO-PASS: Verify from_s3 merges catalogs when upstream is set."""
    issue_file = os.path.join(REPO, "ci/praktika/issue.py")

    with open(issue_file, 'r') as f:
        content = f.read()

    # Check merge logic exists
    assert 'if Settings.S3_UPSTREAM_REPORT_BUCKET:' in content, \
        "Upstream check not found in from_s3"

    assert 'merged' in content.lower() or 'merged' in content or 'upstream' in content, \
        "Merge logic not found in from_s3"

    # Check that we call _download_catalog for upstream
    assert 'cls._download_catalog(' in content, \
        "_download_catalog calls not found"


def test_validator_uses_new_setting_name():
    """FAIL-TO-PASS: Verify validator.py uses S3_REPORT_BUCKET."""
    validator_file = os.path.join(REPO, "ci/praktika/validator.py")

    with open(validator_file, 'r') as f:
        content = f.read()

    assert 'Settings.S3_REPORT_BUCKET' in content, \
        "validator.py should use Settings.S3_REPORT_BUCKET"

    assert 'S3_REPORT_BUCKET Setting must be defined' in content, \
        "Error message should reference S3_REPORT_BUCKET"


def test_hook_html_uses_new_setting():
    """FAIL-TO-PASS: Verify hook_html.py uses S3_REPORT_BUCKET."""
    hook_html_file = os.path.join(REPO, "ci/praktika/hook_html.py")

    with open(hook_html_file, 'r') as f:
        content = f.read()

    assert 'Settings.S3_REPORT_BUCKET' in content, \
        "hook_html.py should use Settings.S3_REPORT_BUCKET"


def test_html_prepare_uses_new_setting():
    """FAIL-TO-PASS: Verify html_prepare.py uses S3_REPORT_BUCKET."""
    html_prepare_file = os.path.join(REPO, "ci/praktika/html_prepare.py")

    with open(html_prepare_file, 'r') as f:
        content = f.read()

    assert 'Settings.S3_REPORT_BUCKET' in content, \
        "html_prepare.py should use Settings.S3_REPORT_BUCKET"


def test_info_uses_new_setting():
    """FAIL-TO-PASS: Verify info.py uses S3_REPORT_BUCKET."""
    info_file = os.path.join(REPO, "ci/praktika/info.py")

    with open(info_file, 'r') as f:
        content = f.read()

    assert 'Settings.S3_REPORT_BUCKET' in content, \
        "info.py should use Settings.S3_REPORT_BUCKET"


def test_result_uses_new_setting():
    """FAIL-TO-PASS: Verify result.py uses S3_REPORT_BUCKET."""
    result_file = os.path.join(REPO, "ci/praktika/result.py")

    with open(result_file, 'r') as f:
        content = f.read()

    assert 'Settings.S3_REPORT_BUCKET' in content, \
        "result.py should use Settings.S3_REPORT_BUCKET"


def test_s3_uses_new_setting():
    """FAIL-TO-PASS: Verify s3.py uses S3_REPORT_BUCKET."""
    s3_file = os.path.join(REPO, "ci/praktika/s3.py")

    with open(s3_file, 'r') as f:
        content = f.read()

    assert 'Settings.S3_REPORT_BUCKET' in content, \
        "s3.py should use Settings.S3_REPORT_BUCKET"


def test_settings_has_both_new_settings():
    """FAIL-TO-PASS: Verify settings.py has both new settings defined."""
    settings_file = os.path.join(REPO, "ci/praktika/settings.py")

    with open(settings_file, 'r') as f:
        content = f.read()

    # Both settings should be defined
    assert 'S3_REPORT_BUCKET: str = ""' in content, \
        "S3_REPORT_BUCKET not defined"

    assert 'S3_UPSTREAM_REPORT_BUCKET: str = ""' in content, \
        "S3_UPSTREAM_REPORT_BUCKET not defined"

    # Both should be in the user defined list
    user_defined_section = content.split('_USER_DEFINED_SETTINGS')[1] if '_USER_DEFINED_SETTINGS' in content else ""
    assert '"S3_REPORT_BUCKET"' in user_defined_section, \
        "S3_REPORT_BUCKET not in _USER_DEFINED_SETTINGS"
    assert '"S3_UPSTREAM_REPORT_BUCKET"' in user_defined_section, \
        "S3_UPSTREAM_REPORT_BUCKET not in _USER_DEFINED_SETTINGS"


def test_collect_statistics_uses_settings():
    """FAIL-TO-PASS: Verify collect_statistics.py imports and uses Settings."""
    collect_file = os.path.join(REPO, "ci/jobs/collect_statistics.py")

    with open(collect_file, 'r') as f:
        content = f.read()

    # Should import from praktika.settings, not from ci.settings.settings
    assert 'from ci.praktika.settings import Settings' in content, \
        "collect_statistics.py should import from ci.praktika.settings"

    # Should use Settings.S3_REPORT_BUCKET
    assert 'Settings.S3_REPORT_BUCKET' in content, \
        "collect_statistics.py should use Settings.S3_REPORT_BUCKET"

    # Should not import S3_REPORT_BUCKET_NAME
    assert 'S3_REPORT_BUCKET_NAME' not in content, \
        "collect_statistics.py should not import S3_REPORT_BUCKET_NAME"


def test_ci_settings_uses_new_name():
    """FAIL-TO-PASS: Verify ci/settings/settings.py defines S3_REPORT_BUCKET."""
    ci_settings_file = os.path.join(REPO, "ci/settings/settings.py")

    with open(ci_settings_file, 'r') as f:
        content = f.read()

    assert 'S3_REPORT_BUCKET = S3_REPORT_BUCKET_NAME' in content, \
        "ci/settings/settings.py should define S3_REPORT_BUCKET"

    assert 'HTML_S3_PATH' not in content, \
        "ci/settings/settings.py should not have HTML_S3_PATH"


# =============================================================================
# PASS-TO-PASS TESTS - Verify existing repo tests still pass
# =============================================================================

def test_settings_importable():
    """PASS-TO-PASS: Verify settings module is importable without errors."""
    # Add ci/ to path for imports
    sys.path.insert(0, os.path.join(REPO, "ci"))

    try:
        from praktika.settings import Settings
        # On base commit, check for HTML_S3_PATH; on fixed commit, check for S3_REPORT_BUCKET
        has_old = hasattr(Settings, 'HTML_S3_PATH')
        has_new = hasattr(Settings, 'S3_REPORT_BUCKET')
        assert has_old or has_new, "Settings should have HTML_S3_PATH or S3_REPORT_BUCKET"
    except ImportError as e:
        assert False, f"Failed to import Settings: {e}"
    except Exception as e:
        assert False, f"Error accessing Settings: {e}"


def test_issue_module_importable():
    """PASS-TO-PASS: Verify issue module is importable without errors."""
    sys.path.insert(0, os.path.join(REPO, "ci"))

    try:
        from praktika.issue import TestCaseIssueCatalog
        # Check base methods exist
        assert hasattr(TestCaseIssueCatalog, 'from_s3'), \
            "TestCaseIssueCatalog should have from_s3 method"
    except ImportError as e:
        assert False, f"Failed to import TestCaseIssueCatalog: {e}"


def test_python_syntax_valid():
    """PASS-TO-PASS: Verify all modified Python files have valid syntax."""
    errors = []

    for file_path in MODIFIED_FILES:
        full_path = os.path.join(REPO, file_path)
        if not os.path.exists(full_path):
            continue

        # Use Python's compileall to check syntax
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", full_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            errors.append(f"{file_path}: {result.stderr}")

    assert not errors, f"Syntax errors found:\n" + "\n".join(errors)


def test_no_broken_imports():
    """PASS-TO-PASS: Verify imports in modified files work correctly."""
    sys.path.insert(0, os.path.join(REPO, "ci"))

    # Test imports that should work (verified from actual module exports)
    import_statements = [
        ("ci.praktika.settings", "Settings"),
        ("ci.praktika.issue", "TestCaseIssueCatalog"),
        ("ci.praktika.validator", "Validator"),
        ("ci.praktika.info", "Info"),
        ("ci.praktika.result", "Result"),
        ("ci.praktika.s3", "S3"),
        ("ci.praktika.html_prepare", "Html"),
        ("ci.praktika.hook_html", "HtmlRunnerHooks"),
    ]

    errors = []
    for module_name, attr_name in import_statements:
        try:
            module = __import__(module_name, fromlist=[attr_name])
            getattr(module, attr_name)
        except ImportError as e:
            errors.append(f"Failed to import {attr_name} from {module_name}: {e}")
        except AttributeError as e:
            errors.append(f"{attr_name} not found in {module_name}: {e}")
        except Exception as e:
            errors.append(f"Error importing {module_name}: {e}")

    assert not errors, f"Import errors:\n" + "\n".join(errors)


def test_repo_python_syntax_all_modified():
    """PASS-TO-PASS: Verify all modified Python files have valid syntax (repo CI check)."""
    errors = []

    for file_path in MODIFIED_FILES:
        full_path = os.path.join(REPO, file_path)
        if not os.path.exists(full_path):
            continue

        result = subprocess.run(
            [sys.executable, "-m", "py_compile", full_path],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            errors.append(f"{file_path}: {result.stderr}")

    assert not errors, f"Syntax errors found:\n" + "\n".join(errors)


def test_repo_praktika_settings_import():
    """PASS-TO-PASS: Verify praktika.settings imports correctly via subprocess.run (repo CI check)."""
    result = subprocess.run(
        [sys.executable, "-c", "import sys; sys.path.insert(0, 'ci'); from praktika.settings import Settings; print('OK')"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"praktika.settings import failed:\\n{result.stderr}"


def test_repo_ci_settings_import():
    """PASS-TO-PASS: Verify ci.settings.settings imports correctly via subprocess.run (repo CI check)."""
    result = subprocess.run(
        [sys.executable, "-c", "import sys; sys.path.insert(0, 'ci'); from ci.settings.settings import *; print('OK')"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"ci.settings.settings import failed:\\n{result.stderr}"


def test_repo_praktika_modules_importable():
    """PASS-TO-PASS: Verify praktika modules can be imported without errors (repo CI check)."""
    sys.path.insert(0, os.path.join(REPO, "ci"))

    modules_to_test = [
        "ci.praktika.settings",
        "ci.praktika.issue",
        "ci.praktika.validator",
        "ci.praktika.hook_html",
        "ci.praktika.html_prepare",
        "ci.praktika.info",
        "ci.praktika.result",
        "ci.praktika.s3",
    ]

    errors = []
    for module_name in modules_to_test:
        try:
            __import__(module_name)
        except Exception as e:
            errors.append(f"Failed to import {module_name}: {e}")

    assert not errors, f"Module import errors:\n" + "\n".join(errors)


def test_repo_settings_attrs_accessible():
    """PASS-TO-PASS: Verify Settings class attributes are accessible (repo CI check)."""
    sys.path.insert(0, os.path.join(REPO, "ci"))

    try:
        from ci.praktika.settings import Settings

        # Check essential settings attributes exist
        # On base commit: HTML_S3_PATH exists
        # On fixed commit: S3_REPORT_BUCKET and S3_UPSTREAM_REPORT_BUCKET exist
        errors = []

        # Either old name (HTML_S3_PATH) or new name (S3_REPORT_BUCKET) should exist
        has_html_s3_path = hasattr(Settings, 'HTML_S3_PATH')
        has_s3_report_bucket = hasattr(Settings, 'S3_REPORT_BUCKET')

        if not (has_html_s3_path or has_s3_report_bucket):
            errors.append("Settings missing attribute: HTML_S3_PATH or S3_REPORT_BUCKET")

        # These other attributes should always exist
        required_attrs = [
            "S3_BUCKET_TO_HTTP_ENDPOINT",
            "TEMP_DIR",
            "WORKFLOW_PATH_PREFIX",
        ]

        for attr in required_attrs:
            if not hasattr(Settings, attr):
                errors.append(f"Settings missing attribute: {attr}")

        assert not errors, f"Settings attribute errors:\n" + "\n".join(errors)

    except Exception as e:
        assert False, f"Error accessing Settings: {e}"


def test_repo_praktika_cli_works():
    """PASS-TO-PASS: Verify praktika CLI is functional (repo CI check)."""
    # Install praktika in editable mode
    install_result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", "ci/", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    
    # Test praktika CLI help
    result = subprocess.run(
        [sys.executable, "-m", "praktika", "--help"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    
    assert result.returncode == 0, f"praktika CLI failed:\\n{result.stderr}"
    assert "Praktika CLI" in result.stdout, "Expected 'Praktika CLI' in help output"


def test_repo_modified_files_ast_valid():
    """PASS-TO-PASS: Verify all modified Python files have valid AST (repo CI check)."""
    errors = []
    
    for file_path in MODIFIED_FILES:
        full_path = os.path.join(REPO, file_path)
        if not os.path.exists(full_path):
            continue
        
        # Use AST parsing to verify Python syntax is valid
        result = subprocess.run(
            [sys.executable, "-c", f"import ast; ast.parse(open('{full_path}').read())"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO,
        )
        
        if result.returncode != 0:
            errors.append(f"{file_path}: AST parsing failed: {result.stderr}")
    
    assert not errors, f"AST validation errors:\\n" + "\\n".join(errors)
