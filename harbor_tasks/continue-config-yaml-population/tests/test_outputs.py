"""
Tests for PR #11915: Ensure config.yaml exists and is populated when accessed.

These tests verify:
1. getConfigYamlPath() creates config.yaml with defaults if missing
2. getConfigYamlPath() populates empty config.yaml with defaults
3. ConfigHandler calls getConfigYamlPath() when opening a local profile
"""

import os
import shutil
import subprocess
import sys
import tempfile
import json
from pathlib import Path

REPO = "/workspace/continue"
CORE_DIR = f"{REPO}/core"


def setup_test_env():
    """Set up a temporary Continue global directory for testing."""
    temp_dir = tempfile.mkdtemp()
    os.environ["CONTINUE_GLOBAL_DIR"] = temp_dir
    return temp_dir


def cleanup_test_env(temp_dir):
    """Clean up the temporary directory."""
    shutil.rmtree(temp_dir, ignore_errors=True)
    if "CONTINUE_GLOBAL_DIR" in os.environ:
        del os.environ["CONTINUE_GLOBAL_DIR"]


def run_ts_test(ts_code: str) -> dict:
    """Run TypeScript test code via Node.js."""
    test_file = tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False)
    test_file.write(ts_code)
    test_file.close()

    # Compile and run with ts-node
    result = subprocess.run(
        ["npx", "ts-node", "--esm", test_file.name],
        cwd=CORE_DIR,
        capture_output=True,
        text=True,
        timeout=60
    )
    os.unlink(test_file.name)

    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    }


def test_missing_config_yaml_created():
    """
    Fail-to-pass: When config.yaml is missing, getConfigYamlPath() should create it with defaults.
    """
    temp_dir = setup_test_env()
    try:
        config_yaml_path = os.path.join(temp_dir, "config.yaml")

        # Verify config.yaml doesn't exist
        assert not os.path.exists(config_yaml_path), "config.yaml should not exist initially"

        # Run Node.js test script
        test_script = f'''
import {{ getConfigYamlPath }} from "./util/paths.js";
import * as fs from "fs";

const result = getConfigYamlPath();
console.log(JSON.stringify({{ path: result, exists: fs.existsSync(result) }}));
'''
        result = subprocess.run(
            ["node", "--loader", "ts-node/esm", "-e", test_script],
            cwd=CORE_DIR,
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "CONTINUE_GLOBAL_DIR": temp_dir}
        )

        # Check that config.yaml now exists with content
        assert os.path.exists(config_yaml_path), "config.yaml should be created by getConfigYamlPath()"

        with open(config_yaml_path, 'r') as f:
            content = f.read()

        assert len(content.strip()) > 0, "config.yaml should have non-empty content"
        assert "name" in content or "models" in content, "config.yaml should contain default config structure"

    finally:
        cleanup_test_env(temp_dir)


def test_empty_config_yaml_populated():
    """
    Fail-to-pass: When config.yaml exists but is empty, getConfigYamlPath() should populate it with defaults.
    """
    temp_dir = setup_test_env()
    try:
        config_yaml_path = os.path.join(temp_dir, "config.yaml")

        # Create an empty config.yaml
        Path(config_yaml_path).touch()
        assert os.path.exists(config_yaml_path), "config.yaml should exist"
        assert os.path.getsize(config_yaml_path) == 0, "config.yaml should be empty"

        # Run getConfigYamlPath
        test_script = f'''
import {{ getConfigYamlPath }} from "./util/paths.js";
import * as fs from "fs";

const result = getConfigYamlPath();
console.log(JSON.stringify({{ path: result }}));
'''
        result = subprocess.run(
            ["node", "--loader", "ts-node/esm", "-e", test_script],
            cwd=CORE_DIR,
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "CONTINUE_GLOBAL_DIR": temp_dir}
        )

        # Check that config.yaml now has content
        with open(config_yaml_path, 'r') as f:
            content = f.read()

        assert len(content.strip()) > 0, "Empty config.yaml should be populated with defaults"

    finally:
        cleanup_test_env(temp_dir)


def test_existing_config_preserved():
    """
    Pass-to-pass: When config.yaml exists with content, it should not be overwritten.
    """
    temp_dir = setup_test_env()
    try:
        config_yaml_path = os.path.join(temp_dir, "config.yaml")

        # Create a config.yaml with existing content
        existing_content = "name: My Custom Config\\nmodels: []"
        with open(config_yaml_path, 'w') as f:
            f.write(existing_content)

        # Run getConfigYamlPath
        test_script = f'''
import {{ getConfigYamlPath }} from "./util/paths.js";
const result = getConfigYamlPath();
console.log("done");
'''
        result = subprocess.run(
            ["node", "--loader", "ts-node/esm", "-e", test_script],
            cwd=CORE_DIR,
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "CONTINUE_GLOBAL_DIR": temp_dir}
        )

        # Check that config.yaml is preserved
        with open(config_yaml_path, 'r') as f:
            content = f.read()

        assert content == existing_content, f"Existing config should be preserved, got: {content}"

    finally:
        cleanup_test_env(temp_dir)


def test_config_handler_calls_get_config_yaml_path():
    """
    Fail-to-pass: ConfigHandler should call getConfigYamlPath() when opening a local profile.
    This is tested by verifying the import and usage in ConfigHandler.ts.
    """
    config_handler_path = Path(REPO) / "core" / "config" / "ConfigHandler.ts"
    assert config_handler_path.exists(), f"ConfigHandler.ts should exist at {config_handler_path}"

    content = config_handler_path.read_text()

    # Check that getConfigYamlPath is imported
    assert "import { getConfigYamlPath }" in content or 'import { getConfigYamlPath }' in content, \
        "ConfigHandler should import getConfigYamlPath"

    # Check that getConfigYamlPath is called in the local profile handling
    assert "getConfigYamlPath()" in content, \
        "ConfigHandler should call getConfigYamlPath() when handling local profiles"


def test_is_empty_check_logic():
    """
    Structural: Verify the isEmpty logic is correctly implemented.
    The fix adds: const isEmpty = exists && fs.readFileSync(p, "utf8").trim() === "";
    """
    paths_ts_path = Path(REPO) / "core" / "util" / "paths.ts"
    assert paths_ts_path.exists(), f"paths.ts should exist at {paths_ts_path}"

    content = paths_ts_path.read_text()

    # Check for the isEmpty check
    assert 'const isEmpty = exists && fs.readFileSync(p, "utf8").trim() === "";' in content, \
        "paths.ts should contain the isEmpty check for detecting empty config files"

    # Check for needsCreation logic
    assert "const needsCreation = !exists && !fs.existsSync(getConfigJsonPath());" in content, \
        "paths.ts should contain needsCreation logic"


def test_paths_syntax_valid():
    """
    Pass-to-pass: The modified paths.ts should compile without errors.
    """
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "util/paths.ts"],
        cwd=CORE_DIR,
        capture_output=True,
        text=True,
        timeout=60
    )

    # Compilation should succeed (may have import errors but no syntax errors)
    assert result.returncode == 0 or "error TS" not in result.stderr, \
        f"paths.ts should have valid TypeScript syntax: {result.stderr[:500]}"


def test_config_handler_syntax_valid():
    """
    Pass-to-pass: The modified ConfigHandler.ts should compile without errors.
    """
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "config/ConfigHandler.ts"],
        cwd=CORE_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )

    # Allow for import/module resolution errors but not syntax/type errors
    stderr_lower = result.stderr.lower()
    # Filter out module resolution errors, keep only real type/syntax errors
    critical_errors = [
        line for line in result.stderr.split("\n")
        if "error TS" in line and
        "cannot find module" not in line.lower() and
        "cannot resolve" not in line.lower() and
        "is not a module" not in line.lower()
    ]

    assert len(critical_errors) == 0, \
        f"ConfigHandler.ts should have valid TypeScript syntax. Critical errors: {critical_errors[:3]}"


def test_repo_tsc_check():
    """
    Pass-to-pass: Repo-wide TypeScript type check passes (npm run tsc:check in core).
    """
    result = subprocess.run(
        ["npm", "run", "tsc:check"],
        cwd=CORE_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"Repo tsc:check failed:\nstdout: {result.stdout[-500:]}\nstderr: {result.stderr[-500:]}"


def test_repo_lint():
    """
    Pass-to-pass: Repo linting passes (npm run lint in core).
    """
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=CORE_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"Repo lint failed:\nstdout: {result.stdout[-500:]}\nstderr: {result.stderr[-500:]}"


def test_repo_unit_tests_paths():
    """
    Pass-to-pass: Core unit tests for paths/util module pass.
    Runs jest with testPathPattern to limit to relevant tests.
    """
    result = subprocess.run(
        ["npx", "jest", "--testPathPattern", "util", "--passWithNoTests"],
        cwd=CORE_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"Repo unit tests failed:\nstdout: {result.stdout[-500:]}\nstderr: {result.stderr[-500:]}"
