"""
Tests for apache/superset#39183: Webpack memory optimization and DISABLE_TS_CHECKER env var.

The PR introduces a DISABLE_TS_CHECKER environment variable that should only disable
the TypeScript checker plugin when set to exactly "true" or "1" (case insensitive).
"""

import subprocess
import json
import os

REPO = "/workspace/superset/superset-frontend"


def run_node_script(script: str, env_vars: dict = None) -> dict:
    """Run a Node.js script in the superset-frontend directory and return parsed JSON output."""
    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)

    result = subprocess.run(
        ["node", "-e", script],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=env
    )
    if result.returncode != 0:
        raise RuntimeError(f"Node script failed:\n{result.stderr}")

    # Webpack config outputs info messages to stdout, so we need to find the JSON line
    # which should be the last line starting with '{'
    output = result.stdout.strip()
    for line in reversed(output.split('\n')):
        line = line.strip()
        if line.startswith('{') and line.endswith('}'):
            return json.loads(line)
    raise RuntimeError(f"No JSON found in output:\n{output}")


def get_webpack_config_info(env_vars: dict = None) -> dict:
    """Load webpack config and extract key information."""
    script = """
    // Set NODE_ENV to development to test dev mode behavior
    process.env.NODE_ENV = process.env.NODE_ENV || 'development';

    const config = require('./webpack.config.js');

    // Check if ForkTsCheckerWebpackPlugin is in the plugins array
    const hasTsChecker = config.plugins.some(p =>
        p.constructor.name === 'ForkTsCheckerWebpackPlugin'
    );

    // Get CSS loader sourceMap setting
    let cssSourceMap = null;
    if (config.module && config.module.rules) {
        for (const rule of config.module.rules) {
            if (rule.use && Array.isArray(rule.use)) {
                for (const loader of rule.use) {
                    if (loader.loader === 'css-loader' && loader.options) {
                        cssSourceMap = loader.options.sourceMap;
                        break;
                    }
                }
            }
        }
    }

    // Get watch ignored patterns
    const watchIgnored = config.watchOptions ? config.watchOptions.ignored : null;

    console.log(JSON.stringify({
        hasTsChecker: hasTsChecker,
        cssSourceMap: cssSourceMap,
        watchIgnored: watchIgnored
    }));
    """
    return run_node_script(script, env_vars)


# ============================================================================
# Fail-to-pass tests: These should FAIL on base commit, PASS after fix
# ============================================================================

def test_disable_ts_checker_with_true():
    """DISABLE_TS_CHECKER=true should disable the TypeScript checker plugin (fail_to_pass)."""
    info = get_webpack_config_info({"DISABLE_TS_CHECKER": "true", "NODE_ENV": "development"})
    assert info["hasTsChecker"] is False, (
        "When DISABLE_TS_CHECKER=true, ForkTsCheckerWebpackPlugin should NOT be present. "
        f"Got hasTsChecker={info['hasTsChecker']}"
    )


def test_disable_ts_checker_with_one():
    """DISABLE_TS_CHECKER=1 should disable the TypeScript checker plugin (fail_to_pass)."""
    info = get_webpack_config_info({"DISABLE_TS_CHECKER": "1", "NODE_ENV": "development"})
    assert info["hasTsChecker"] is False, (
        "When DISABLE_TS_CHECKER=1, ForkTsCheckerWebpackPlugin should NOT be present. "
        f"Got hasTsChecker={info['hasTsChecker']}"
    )


def test_disable_ts_checker_case_insensitive():
    """DISABLE_TS_CHECKER=TRUE (uppercase) should also disable the plugin (fail_to_pass)."""
    info = get_webpack_config_info({"DISABLE_TS_CHECKER": "TRUE", "NODE_ENV": "development"})
    assert info["hasTsChecker"] is False, (
        "When DISABLE_TS_CHECKER=TRUE (uppercase), ForkTsCheckerWebpackPlugin should NOT be present. "
        f"Got hasTsChecker={info['hasTsChecker']}"
    )


def test_css_sourcemap_disabled_in_dev_mode():
    """CSS sourceMap should be disabled in development mode (fail_to_pass)."""
    info = get_webpack_config_info({"NODE_ENV": "development"})
    assert info["cssSourceMap"] is False, (
        "In development mode, CSS sourceMap should be disabled (false) for memory optimization. "
        f"Got cssSourceMap={info['cssSourceMap']}"
    )


def test_watch_ignored_includes_new_patterns():
    """Watch ignored patterns should include new memory-saving exclusions (fail_to_pass)."""
    info = get_webpack_config_info({"NODE_ENV": "development"})
    ignored = info["watchIgnored"]
    assert ignored is not None, "watchOptions.ignored should be defined in dev mode"

    # Convert to list if it's a single value
    if not isinstance(ignored, list):
        ignored = [ignored]

    # Check for new patterns added by the PR
    required_patterns = [
        "**/.temp_cache",
        "**/coverage",
        "**/*.test.*",
        "**/*.stories.*",
        "**/cypress-base",
        "**/*.geojson",
    ]

    for pattern in required_patterns:
        assert pattern in ignored, (
            f"watchOptions.ignored should include '{pattern}' to reduce memory usage. "
            f"Current patterns: {ignored}"
        )


# ============================================================================
# Pass-to-pass tests: These should PASS on both base commit and after fix
# ============================================================================

def test_ts_checker_enabled_when_not_disabled():
    """TypeScript checker should be enabled when DISABLE_TS_CHECKER is not set (pass_to_pass)."""
    # Explicitly unset the variable
    info = get_webpack_config_info({"DISABLE_TS_CHECKER": "", "NODE_ENV": "development"})
    assert info["hasTsChecker"] is True, (
        "When DISABLE_TS_CHECKER is empty/unset, ForkTsCheckerWebpackPlugin should be present. "
        f"Got hasTsChecker={info['hasTsChecker']}"
    )


def test_ts_checker_enabled_with_false():
    """TypeScript checker should be enabled when DISABLE_TS_CHECKER=false (pass_to_pass)."""
    info = get_webpack_config_info({"DISABLE_TS_CHECKER": "false", "NODE_ENV": "development"})
    assert info["hasTsChecker"] is True, (
        "When DISABLE_TS_CHECKER=false, ForkTsCheckerWebpackPlugin should still be present. "
        f"Got hasTsChecker={info['hasTsChecker']}"
    )


def test_ts_checker_enabled_with_zero():
    """TypeScript checker should be enabled when DISABLE_TS_CHECKER=0 (pass_to_pass)."""
    info = get_webpack_config_info({"DISABLE_TS_CHECKER": "0", "NODE_ENV": "development"})
    assert info["hasTsChecker"] is True, (
        "When DISABLE_TS_CHECKER=0, ForkTsCheckerWebpackPlugin should still be present. "
        f"Got hasTsChecker={info['hasTsChecker']}"
    )


def test_webpack_config_loads_successfully():
    """Webpack config should load without errors (pass_to_pass)."""
    script = """
    process.env.NODE_ENV = 'development';
    const config = require('./webpack.config.js');
    console.log(JSON.stringify({success: true, hasPlugins: config.plugins.length > 0}));
    """
    result = run_node_script(script)
    assert result["success"] is True
    assert result["hasPlugins"] is True, "Webpack config should have plugins defined"


def test_docker_bootstrap_excludes_frontend():
    """docker-bootstrap.sh should exclude superset-frontend from flask reloader (fail_to_pass)."""
    with open("/workspace/superset/docker/docker-bootstrap.sh", "r") as f:
        content = f.read()

    # Check that superset-frontend is in exclude patterns
    assert "superset-frontend" in content, (
        "docker-bootstrap.sh should exclude superset-frontend from flask reloader patterns"
    )


# ============================================================================
# Pass-to-pass tests from repo CI: These should PASS on both base commit and after fix
# ============================================================================

def test_repo_lint():
    """Repo's oxlint linter passes on frontend code (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    # oxlint returns 0 for warnings only, non-zero for errors
    assert result.returncode == 0, (
        f"Frontend linting failed with exit code {result.returncode}:\n"
        f"{result.stderr[-1000:]}"
    )


def test_repo_custom_rules():
    """Repo's custom frontend rules check passes (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "check:custom-rules"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, (
        f"Custom rules check failed with exit code {result.returncode}:\n"
        f"{result.stderr[-1000:]}"
    )


def test_repo_ensure_oxc():
    """Repo's oxlint tooling is available (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "ensure-oxc"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"OXC linter verification failed:\n{result.stderr[-500:]}"
    )


if __name__ == "__main__":
    import sys
    # Run a quick sanity check
    try:
        test_webpack_config_loads_successfully()
        print("Basic sanity check passed")
    except Exception as e:
        print(f"Sanity check failed: {e}")
        sys.exit(1)
