"""Tests for folding unreleased RunState schema changes into 1.8."""

import os
import subprocess
import tempfile

REPO = "/workspace/openai-agents-js"


def _run_node(script: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a Node.js script from a temp file in the repo directory."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cjs", delete=False, dir=REPO
    ) as f:
        f.write(script)
        tmpfile = f.name
    try:
        return subprocess.run(
            ["node", tmpfile],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    finally:
        os.unlink(tmpfile)


# ---------------------------------------------------------------------------
# fail_to_pass tests
# ---------------------------------------------------------------------------

def test_current_schema_version_is_1_8():
    """CURRENT_SCHEMA_VERSION must equal '1.8'."""
    script = r"""
const fs = require("fs");
const src = fs.readFileSync(
    "packages/agents-core/src/runState.ts", "utf8"
);
const re = /export const CURRENT_SCHEMA_VERSION\s*=\s*'([^']+)'/;
const m = src.match(re);
if (!m) {
    console.error("FAIL: could not find CURRENT_SCHEMA_VERSION");
    process.exit(1);
}
const version = m[1];
console.log("CURRENT_SCHEMA_VERSION =", version);
if (version !== "1.8") {
    console.error("FAIL: CURRENT_SCHEMA_VERSION is", version, "expected 1.8");
    process.exit(1);
}
console.log("PASS");
"""
    result = _run_node(script)
    assert result.returncode == 0, (
        f"CURRENT_SCHEMA_VERSION is not '1.8'\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_assert_function_rejects_1_9():
    """Schema version '1.9' must be rejected during deserialization."""
    script = r"""
const fs = require("fs");
const src = fs.readFileSync(
    "packages/agents-core/src/runState.ts", "utf8"
);

// Check that assertSchemaVersionSupportsToolSearch only checks for '1.8',
// not '1.8' || '1.9'
const re = /if\s*\(\s*schemaVersion\s*===\s*'1\.8'\s*\|\|\s*schemaVersion\s*===\s*'1\.9'\s*\)/;
if (re.test(src)) {
    console.error(
        "FAIL: assertSchemaVersionSupportsToolSearch still accepts 1.9"
    );
    process.exit(1);
}

// Verify the function only checks for 1.8
const reSingle = /if\s*\(\s*schemaVersion\s*===\s*'1\.8'\s*\)/;
if (!reSingle.test(src)) {
    console.error(
        "FAIL: assertSchemaVersionSupportsToolSearch missing 1.8 check"
    );
    process.exit(1);
}

console.log("PASS: assertSchemaVersionSupportsToolSearch only accepts 1.8");
"""
    result = _run_node(script)
    assert result.returncode == 0, (
        f"assertSchemaVersionSupportsToolSearch did not properly reject '1.9'\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


# ---------------------------------------------------------------------------
# pass_to_pass tests
# ---------------------------------------------------------------------------

def test_agents_core_builds():
    """agents-core package builds successfully."""
    result = subprocess.run(
        ["pnpm", "-F", "agents-core", "build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, (
        f"agents-core build failed (exit {result.returncode})\n"
        f"stdout: {result.stdout[-500:]}\nstderr: {result.stderr[-500:]}"
    )


def test_agents_core_build_check():
    """agents-core passes build-check type validation."""
    result = subprocess.run(
        ["pnpm", "-F", "agents-core", "build-check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, (
        f"agents-core build-check failed (exit {result.returncode})\n"
        f"stdout: {result.stdout[-500:]}\nstderr: {result.stderr[-500:]}"
    )
