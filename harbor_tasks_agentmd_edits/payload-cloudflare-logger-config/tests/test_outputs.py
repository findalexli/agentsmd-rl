"""
Task: payload-cloudflare-logger-config
Repo: payloadcms/payload @ 23d52a0d7d5780954bf5b027e537cabb008b8a0a
PR:   15752

Fixes pino logger errors in Cloudflare Workers by adding a custom
console-based logger to the with-cloudflare-d1 template, exporting
the PayloadLogger type, and documenting the configuration in README.md.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/payload"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files parse without syntax errors."""
    files = [
        "templates/with-cloudflare-d1/src/payload.config.ts",
        "packages/payload/src/index.ts",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"File {f} not found"
        content = p.read_text()
        # Basic: file is non-empty and has no null bytes (corruption check)
        assert len(content) > 100, f"{f} appears truncated or empty"
        assert "\x00" not in content, f"{f} contains null bytes"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_custom_logger_uses_console():
    """payload.config.ts must define a logger that routes through console.* methods."""
    config = (Path(REPO) / "templates/with-cloudflare-d1/src/payload.config.ts").read_text()
    # Must use console methods instead of pino (which uses fs.write, unsupported in Workers)
    assert "console.log" in config or "console.info" in config, \
        "Logger must route info-level logs through console.log or console.info"
    assert "console.error" in config, \
        "Logger must route error-level logs through console.error"
    assert "console.warn" in config, \
        "Logger must route warn-level logs through console.warn"


# [pr_diff] fail_to_pass
def test_logger_json_output():
    """Custom logger must produce JSON-formatted output for CF observability."""
    config = (Path(REPO) / "templates/with-cloudflare-d1/src/payload.config.ts").read_text()
    assert "JSON.stringify" in config, \
        "Logger must use JSON.stringify to produce structured log output"


# [pr_diff] fail_to_pass
def test_logger_supports_standard_levels():
    """Custom logger must implement all standard pino log levels."""
    config = (Path(REPO) / "templates/with-cloudflare-d1/src/payload.config.ts").read_text()
    # All standard pino levels that Payload expects
    for level in ["trace", "debug", "info", "warn", "error", "fatal"]:
        assert f"'{level}'" in config or f'"{level}"' in config, \
            f"Logger must define the '{level}' log level"


# [pr_diff] fail_to_pass
def test_logger_passed_to_build_config():
    """The custom logger must be wired into buildConfig as the logger option."""
    config = (Path(REPO) / "templates/with-cloudflare-d1/src/payload.config.ts").read_text()
    assert "logger:" in config or "logger :" in config, \
        "Logger must be passed to buildConfig via the 'logger' option"


# [pr_diff] fail_to_pass
def test_logger_production_conditional():
    """Custom logger should only be used in production; dev should get default pino-pretty."""
    config = (Path(REPO) / "templates/with-cloudflare-d1/src/payload.config.ts").read_text()
    # The logger config line must reference isProduction or NODE_ENV
    # to conditionally apply only in production
    lines_with_logger = [
        line for line in config.splitlines()
        if "logger" in line.lower() and ("isProduction" in line or "production" in line.lower())
    ]
    assert len(lines_with_logger) >= 1, \
        "Logger must be conditionally applied only in production (use isProduction or NODE_ENV check)"


# [pr_diff] fail_to_pass
def test_payload_logger_type_exported():
    """PayloadLogger type must be exported from the main payload package index."""
    index = (Path(REPO) / "packages/payload/src/index.ts").read_text()
    assert "PayloadLogger" in index, \
        "PayloadLogger type must be exported from packages/payload/src/index.ts"
    # Should be a type export specifically
    assert "export type" in index and "PayloadLogger" in index, \
        "PayloadLogger should be exported as a type (export type { PayloadLogger })"


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — README documentation tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] fail_to_pass


# [agent_config] fail_to_pass — CLAUDE.md:68 @ 23d52a0d
