"""
Tests for the config.yaml empty-file handling fix (continuedev/continue#11915).

PASS-TO-PASS (p2p) repo CI tests:
  - test_repo_format_check: Repo-wide prettier format check passes
  - test_repo_core_lint: Core package eslint passes

FAIL-TO-PASS (f2p) tests:
  - test_empty_config_yaml_populated: getConfigYamlPath() must populate an empty
    config.yaml with defaults (fails on base commit where this case is not handled)
  - test_idempotent_empty_file: calling getConfigYamlPath() twice must be safe

PASS-TO-PASS (p2p) programmatic tests:
  - test_valid_config_yaml_untouched: getConfigYamlPath() must not modify a
    valid, non-empty config.yaml
  - test_missing_both_configs_created: when both config.json and config.yaml are
    missing, config.yaml is created with defaults
"""

import subprocess
import os

import pytest

REPO = "/workspace/continue"


def _run_ts(code: str, cwd: str = REPO) -> tuple[int, str, str]:
    """
    Run TypeScript code via tsx using a temp file placed inside REPO
    (so it can resolve node_modules packages like 'yaml').
    """
    # Write to a temp file inside REPO so ESM module resolution works
    tmp_path = os.path.join(REPO, f"__test_tmp_{os.getpid()}.mts")
    with open(tmp_path, "w") as f:
        f.write(code)
    try:
        result = subprocess.run(
            ["npx", "tsx", tmp_path],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return result.returncode, result.stdout, result.stderr
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


class TestEmptyConfigYamlPopulated:
    """Core f2p: empty config.yaml must be populated with defaults."""

    def test_empty_config_yaml_populated(self, tmp_path):
        """
        When ~/.continue/config.yaml exists but is EMPTY, getConfigYamlPath()
        must write default config to it (not leave it empty).

        Default config must include the expected top-level keys:
        name, version, schema, models (at minimum).
        """
        continue_dir = str(tmp_path / ".continue")
        config_yaml_path = os.path.join(continue_dir, "config.yaml")
        os.makedirs(continue_dir, exist_ok=True)

        # Create empty config.yaml
        with open(config_yaml_path, "w") as f:
            f.write("")  # empty file

        code = f"""
import * as path from 'path';
import * as fs from 'fs';
process.env.CONTINUE_GLOBAL_DIR = '{continue_dir}';
const {{ getConfigYamlPath }} = await import('./core/util/paths.ts');
const p = getConfigYamlPath();
console.log('PATH=' + p);
const content = fs.readFileSync(p, 'utf8');
console.log('EMPTY=' + (content.trim() === ''));
// Parse and check it has expected keys
import YAML from 'yaml';
const parsed = YAML.parse(content) as any;
console.log('HAS_NAME=' + (parsed && parsed.name !== undefined));
console.log('HAS_VERSION=' + (parsed && parsed.version !== undefined));
console.log('HAS_SCHEMA=' + (parsed && parsed.schema !== undefined));
console.log('HAS_MODELS=' + (parsed && parsed.models !== undefined));
"""
        rc, stdout, stderr = _run_ts(code)

        # On base commit: returns PATH but does NOT populate empty file -> EMPTY=true
        # On fixed commit: populates empty file -> EMPTY=false, all HAS_*=true

        assert rc == 0, f"tsx failed:\n{stderr}\nstdout: {stdout}"
        lines = {}
        for line in stdout.strip().split("\n"):
            if "=" in line:
                k, v = line.split("=", 1)
                lines[k] = v

        is_empty = lines.get("EMPTY", "").strip() == "true"
        has_name = lines.get("HAS_NAME", "").strip() == "true"
        has_version = lines.get("HAS_VERSION", "").strip() == "true"
        has_schema = lines.get("HAS_SCHEMA", "").strip() == "true"
        has_models = lines.get("HAS_MODELS", "").strip() == "true"

        # The key assertion: file must NOT be empty after calling getConfigYamlPath()
        assert not is_empty, (
            "getConfigYamlPath() left config.yaml empty — "
            "it should have been populated with default config. "
            "Bug: the function only creates defaults when the file is missing, "
            "not when it exists but is empty."
        )
        assert has_name, "Default config missing 'name' key"
        assert has_version, "Default config missing 'version' key"
        assert has_schema, "Default config missing 'schema' key"
        assert has_models, "Default config missing 'models' key"


class TestValidConfigYamlUntouched:
    """p2p: a non-empty, valid config.yaml must not be modified."""

    def test_valid_config_yaml_untouched(self, tmp_path):
        """
        When config.yaml already exists with valid content,
        getConfigYamlPath() must return its path WITHOUT modifying it.
        """
        continue_dir = str(tmp_path / ".continue")
        config_yaml_path = os.path.join(continue_dir, "config.yaml")
        os.makedirs(continue_dir, exist_ok=True)

        original = "name: My Config\nversion: 1.0.0\nschema: v1\nmodels: []\n"
        with open(config_yaml_path, "w") as f:
            f.write(original)

        code = f"""
import * as fs from 'fs';
process.env.CONTINUE_GLOBAL_DIR = '{continue_dir}';
const {{ getConfigYamlPath }} = await import('./core/util/paths.ts');
getConfigYamlPath();
"""
        rc, stdout, stderr = _run_ts(code)
        assert rc == 0, f"tsx failed:\n{stderr}\nstdout: {stdout}"

        with open(config_yaml_path) as f:
            content = f.read()
        assert content == original, (
            f"getConfigYamlPath() modified an existing valid config.yaml.\n"
            f"Expected: {original!r}\nGot: {content!r}"
        )


class TestMissingBothConfigsCreated:
    """p2p: when both config files are absent, config.yaml is created with defaults."""

    def test_missing_both_configs_created(self, tmp_path):
        """
        When neither config.yaml nor config.json exists,
        getConfigYamlPath() must create config.yaml with default content.
        """
        continue_dir = str(tmp_path / ".continue")
        os.makedirs(continue_dir, exist_ok=True)

        code = f"""
import * as fs from 'fs';
process.env.CONTINUE_GLOBAL_DIR = '{continue_dir}';
const {{ getConfigYamlPath }} = await import('./core/util/paths.ts');
const p = getConfigYamlPath();
console.log('CREATED=' + fs.existsSync(p));
import YAML from 'yaml';
const content = fs.readFileSync(p, 'utf8');
const parsed = YAML.parse(content);
console.log('HAS_NAME=' + (parsed.name !== undefined));
"""
        rc, stdout, stderr = _run_ts(code)
        assert rc == 0, f"tsx failed:\n{stderr}\nstdout: {stdout}"

        lines = {}
        for line in stdout.strip().split("\n"):
            if "=" in line:
                k, v = line.split("=", 1)
                lines[k] = v

        created = lines.get("CREATED", "").strip() == "true"
        has_name = lines.get("HAS_NAME", "").strip() == "true"

        assert created, "config.yaml was not created when both config files were missing"
        assert has_name, "Created config.yaml is missing 'name' key"


class TestIdempotency:
    """f2p: calling getConfigYamlPath() twice must be safe and consistent."""

    def test_idempotent_empty_file(self, tmp_path):
        """
        Calling getConfigYamlPath() twice on an empty config.yaml must not crash
        and must result in a valid default config.
        """
        continue_dir = str(tmp_path / ".continue")
        config_yaml_path = os.path.join(continue_dir, "config.yaml")
        os.makedirs(continue_dir, exist_ok=True)

        with open(config_yaml_path, "w") as f:
            f.write("")

        code = f"""
import * as fs from 'fs';
process.env.CONTINUE_GLOBAL_DIR = '{continue_dir}';
const {{ getConfigYamlPath }} = await import('./core/util/paths.ts');
// Call twice
getConfigYamlPath();
getConfigYamlPath();
const content = fs.readFileSync('{config_yaml_path}', 'utf8');
import YAML from 'yaml';
const parsed = YAML.parse(content) as any;
console.log('VALID=' + (parsed && parsed.name !== undefined && parsed.models !== undefined));
"""
        rc, stdout, stderr = _run_ts(code)

        assert rc == 0, f"Idempotency test crashed:\n{stderr}\nstdout: {stdout}"
        lines = {}
        for line in stdout.strip().split("\n"):
            if "=" in line:
                k, v = line.split("=", 1)
                lines[k] = v

        valid = lines.get("VALID", "").strip() == "true"
        assert valid, "After two calls with empty config.yaml, content is not valid default config"


# =============================================================================
# PASS-TO-PASS (p2p): Repo CI tests — must use subprocess.run() with real commands
# =============================================================================

def test_repo_format_check():
    """Repo-wide prettier format check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "**/*.{js,jsx,ts,tsx,json,css,md}"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}"


def test_repo_core_lint():
    """Core package eslint passes with no errors (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", ".", "--ext", "ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/core",
    )
    # ESLint exits 0 even with warnings; check there are no errors in output
    output = r.stdout + r.stderr
    assert "error" not in output.lower() or r.returncode == 0, (
        f"ESLint errors found:\n{output[-500:]}"
    )
