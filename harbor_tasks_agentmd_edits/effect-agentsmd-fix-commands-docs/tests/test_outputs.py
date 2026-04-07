"""Tests for effect-ts/effect#6030: fix incorrect commands in AGENTS.md and related examples.

The PR fixes:
1. AGENTS.md test command: pnpm test → pnpm test run
2. AGENTS.md scratchpad runner: node → tsx
3. AGENTS.md new section about effect v4
4. eslint.config.mjs: add .repos/ and .lalph/ to ignores
5. JSDoc examples across AI package: fix import patterns
6. packages/sql/tsconfig.test.json: add outDir
"""

import json
import subprocess
from pathlib import Path

REPO = Path("/workspace/effect")


# ─── F2P: Config/documentation update tests ─────────────────────────────────


def test_agentsmd_test_run_command():
    """AGENTS.md must specify 'pnpm test run' (not just 'pnpm test') for running tests."""
    content = (REPO / "AGENTS.md").read_text()
    assert "pnpm test run" in content, (
        "AGENTS.md should specify 'pnpm test run' for running tests "
        "(the 'run' subcommand is required)"
    )


def test_agentsmd_tsx_scratchpad():
    """AGENTS.md must use 'tsx' (not 'node') to run scratchpad TypeScript files."""
    content = (REPO / "AGENTS.md").read_text()
    assert "tsx scratchpad/" in content, (
        "AGENTS.md should instruct using 'tsx' to run scratchpad .ts files"
    )
    # The old incorrect 'node scratchpad/' command must be gone
    lines = content.split("\n")
    for line in lines:
        if "scratchpad" in line and "run" in line.lower():
            assert "node scratchpad/" not in line, (
                "AGENTS.md should not use 'node' to run .ts files in scratchpad"
            )


def test_agentsmd_v4_learning_section():
    """AGENTS.md must include a section about learning effect v4 with .repos path."""
    content = (REPO / "AGENTS.md").read_text()
    assert "v4" in content, "AGENTS.md should mention effect v4"
    assert ".repos/effect-v4" in content, (
        "AGENTS.md should reference .repos/effect-v4 for the v4 source"
    )


# ─── F2P: Code/config change tests (code execution via node) ────────────────


def test_sql_tsconfig_outdir():
    """packages/sql/tsconfig.test.json must specify outDir for test build output."""
    result = subprocess.run(
        [
            "node", "-e",
            "const c = JSON.parse(require('fs').readFileSync("
            "'packages/sql/tsconfig.test.json','utf8'));"
            "if (c.compilerOptions?.outDir !== 'build/test') {"
            "  throw new Error('outDir missing or wrong: ' + c.compilerOptions?.outDir);"
            "}"
            "console.log('OK');",
        ],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, f"tsconfig outDir check failed: {result.stderr}"
    assert "OK" in result.stdout


def test_schema_jsdoc_example_reference():
    """packages/effect/src/Schema.ts JSDoc example must use Schema.JsonNumber (not S.JsonNumber)."""
    result = subprocess.run(
        [
            "node", "-e",
            "const content = require('fs').readFileSync("
            "'packages/effect/src/Schema.ts','utf8');"
            "const lines = content.split('\\n');"
            "for (let i = 0; i < lines.length; i++) {"
            "  if (lines[i].includes('Schema.is(') && lines[i].includes('JsonNumber')) {"
            "    if (lines[i].includes('S.JsonNumber')) {"
            "      throw new Error('Found S.JsonNumber at line ' + (i+1));"
            "    }"
            "    console.log('OK:' + (i+1));"
            "    process.exit(0);"
            "  }"
            "}"
            "throw new Error('JsonNumber example line not found');",
        ],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Schema example check failed: {result.stderr}"


def test_eslint_ignores_repos():
    """eslint.config.mjs must include .repos/ in its ignore patterns."""
    result = subprocess.run(
        [
            "node", "-e",
            "const content = require('fs').readFileSync('eslint.config.mjs','utf8');"
            "const m = content.match(/ignores:\\s*\\[([\\s\\S]*?)\\]/);"
            "if (!m) throw new Error('No ignores array found');"
            "if (!m[1].includes('.repos')) throw new Error('.repos not in ignores');"
            "console.log('OK');",
        ],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, f"eslint ignores check failed: {result.stderr}"


# ─── P2P: Structure intact tests ────────────────────────────────────────────


def test_agentsmd_core_sections_intact():
    """AGENTS.md must retain core Development Workflow and Code Style sections."""
    content = (REPO / "AGENTS.md").read_text()
    assert "## Development Workflow" in content
    assert "## Code Style Guidelines" in content
    assert "## Testing" in content


def test_eslint_standard_ignores():
    """eslint.config.mjs must still include standard ignore patterns (dist, build, md)."""
    result = subprocess.run(
        [
            "node", "-e",
            "const content = require('fs').readFileSync('eslint.config.mjs','utf8');"
            "const m = content.match(/ignores:\\s*\\[([\\s\\S]*?)\\]/);"
            "if (!m) throw new Error('No ignores found');"
            "for (const p of ['**/dist', '**/build', '**/*.md']) {"
            "  if (!m[1].includes(p)) throw new Error(p + ' missing from ignores');"
            "}"
            "console.log('OK');",
        ],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, f"eslint standard ignores check failed: {result.stderr}"
