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


def _run_node_extract(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Node.js code in the repo directory for extracting/checking file content."""
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )


# ─── F2P: AGENTS.md documentation tests ─────────────────────────────────────


def test_agentsmd_test_run_command():
    """AGENTS.md must specify 'pnpm test run' (not just 'pnpm test') for running tests."""
    content = (REPO / "AGENTS.md").read_text()
    # Must have the corrected command with 'run' subcommand
    assert "pnpm test run" in content, (
        "AGENTS.md should specify 'pnpm test run' for running tests "
        "(the 'run' subcommand is required)"
    )
    # Verify the old incorrect command is not present in test instructions
    for line in content.split("\n"):
        if "pnpm test <" in line and "run" not in line:
            raise AssertionError(f"Found old incorrect test command: {line}")


def test_agentsmd_tsx_scratchpad():
    """AGENTS.md must use 'tsx' (not 'node') to run scratchpad TypeScript files."""
    content = (REPO / "AGENTS.md").read_text()
    # Must have the corrected command using tsx
    assert "tsx scratchpad/" in content, (
        "AGENTS.md should instruct using 'tsx' to run scratchpad .ts files"
    )
    # Old incorrect command must be gone
    assert "node scratchpad/" not in content, (
        "AGENTS.md should not use 'node' to run .ts files in scratchpad"
    )


def test_agentsmd_v4_learning_section():
    """AGENTS.md must include a section about learning effect v4 with .repos path."""
    content = (REPO / "AGENTS.md").read_text()
    assert "## Learning about" in content and "v4" in content, (
        "AGENTS.md should have a section about learning effect v4"
    )
    assert ".repos/effect-v4" in content, (
        "AGENTS.md should reference .repos/effect-v4 for the v4 source"
    )


# ─── F2P: eslint.config.mjs tests ───────────────────────────────────────────


def test_eslint_ignores_repos():
    """eslint.config.mjs must include .repos/ and .lalph/ in ignore patterns."""
    result = _run_node_extract(
        "const content = require('fs').readFileSync('eslint.config.mjs','utf8');"
        "const m = content.match(/ignores:\\s*\[([\s\S]*?)\]/);"
        "if (!m) throw new Error('No ignores array found');"
        "if (!m[1].includes('.repos')) throw new Error('.repos not in ignores');"
        "if (!m[1].includes('.lalph')) throw new Error('.lalph not in ignores');"
        "console.log('OK');"
    )
    assert result.returncode == 0, f"eslint ignores check failed: {result.stderr}"


def test_eslint_formatted_correctly():
    """eslint.config.mjs must have proper formatting (selector on its own line, single-line packageNames)."""
    result = _run_node_extract(
        "const content = require('fs').readFileSync('eslint.config.mjs','utf8');"
        # Check that selector property is on its own line (formatted correctly)
        "if (!content.includes(\"selector:\\n\")) throw new Error('selector not on its own line');"
        # Check that packageNames array is on single line
        "if (!content.includes('packageNames: [\"effect\", \"@effect/platform\", \"@effect/sql\"]')) {"
        "  throw new Error('packageNames not formatted as single line');"
        "}"
        "console.log('OK');"
    )
    assert result.returncode == 0, f"eslint formatting check failed: {result.stderr}"


# ─── F2P: packages/sql/tsconfig.test.json test ────────────────────────────────


def test_sql_tsconfig_outdir():
    """packages/sql/tsconfig.test.json must specify outDir for test build output."""
    result = _run_node_extract(
        "const c = JSON.parse(require('fs').readFileSync('packages/sql/tsconfig.test.json','utf8'));"
        "if (c.compilerOptions?.outDir !== 'build/test') {"
        "  throw new Error('outDir missing or wrong: ' + c.compilerOptions?.outDir);"
        "}"
        "console.log('OK');"
    )
    assert result.returncode == 0, f"tsconfig outDir check failed: {result.stderr}"


# ─── F2P: packages/effect/src/Schema.ts JSDoc test ──────────────────────────


def test_schema_jsdoc_example_reference():
    """packages/effect/src/Schema.ts JSDoc example must use Schema.JsonNumber (not S.JsonNumber)."""
    result = _run_node_extract(
        "const content = require('fs').readFileSync('packages/effect/src/Schema.ts','utf8');"
        "const lines = content.split('\\n');"
        "for (let i = 0; i < lines.length; i++) {"
        "  if (lines[i].includes('Schema.is(') && lines[i].includes('JsonNumber')) {"
        "    if (lines[i].includes('S.JsonNumber')) {"
        "      throw new Error('Found S.JsonNumber at line ' + (i+1));"
        "    }"
        "    if (lines[i].includes('Schema.JsonNumber')) {"
        "      console.log('OK at line ' + (i+1));"
        "      process.exit(0);"
        "    }"
        "  }"
        "}"
        "throw new Error('JsonNumber example line not found');"
    )
    assert result.returncode == 0, f"Schema example check failed: {result.stderr}"


# ─── F2P: AI package JSDoc import pattern tests ─────────────────────────────


def test_ai_chat_jsdoc_import_pattern():
    """packages/ai/ai/src/Chat.ts JSDoc must use 'effect/Effect' import and Chat.Chat service access."""
    result = _run_node_extract(
        r"const content = require('fs').readFileSync('packages/ai/ai/src/Chat.ts','utf8');"
        r"const exampleMatch = content.match(/@example[\s\S]*?\`\`\`ts([\s\S]*?)\`\`\`/);"
        r"if (!exampleMatch) throw new Error('No @example found in Chat.ts');"
        r"const example = exampleMatch[1];"
        r"if (!example.includes(\"import * as Effect from 'effect/Effect'\")) {"
        r"  throw new Error('Chat.ts JSDoc missing correct Effect import pattern');"
        r"}"
        r"if (!example.includes('yield* Chat.Chat')) {"
        r"  throw new Error('Chat.ts JSDoc should use Chat.Chat (not just Chat)');"
        r"}"
        r"console.log('OK');"
    )
    assert result.returncode == 0, f"Chat.ts JSDoc check failed: {result.stderr}"


def test_ai_aierror_jsdoc_import_patterns():
    """packages/ai/ai/src/AiError.ts JSDoc must use 'effect/Effect' and 'effect/Option' imports."""
    result = _run_node_extract(
        r"const content = require('fs').readFileSync('packages/ai/ai/src/AiError.ts','utf8');"
        r"const examples = content.match(/@example[\s\S]*?\`\`\`ts([\s\S]*?)\`\`\`/g);"
        r"if (!examples) throw new Error('No @examples found in AiError.ts');"
        r"const firstEx = examples[0].match(/\`\`\`ts([\s\S]*?)\`\`\`/)[1];"
        r"if (!firstEx.includes(\"import * as Effect from 'effect/Effect'\")) {"
        r"  throw new Error('AiError.ts first example missing Effect import');"
        r"}"
        r"if (!firstEx.includes(\"import * as Option from 'effect/Option'\")) {"
        r"  throw new Error('AiError.ts first example missing Option import');"
        r"}"
        r"const secondEx = examples[1].match(/\`\`\`ts([\s\S]*?)\`\`\`/)[1];"
        r"if (!secondEx.includes('Effect.Effect<string, AiError.MalformedInput>')) {"
        r"  throw new Error('AiError.ts second example missing proper return type');"
        r"}"
        r"console.log('OK');"
    )
    assert result.returncode == 0, f"AiError.ts JSDoc check failed: {result.stderr}"


def test_ai_embeddingmodel_jsdoc_import_pattern():
    """packages/ai/ai/src/EmbeddingModel.ts JSDoc must use 'effect/Effect' and EmbeddingModel.EmbeddingModel."""
    result = _run_node_extract(
        r"const content = require('fs').readFileSync('packages/ai/ai/src/EmbeddingModel.ts','utf8');"
        r"const exampleMatch = content.match(/@example[\s\S]*?\`\`\`ts([\s\S]*?)\`\`\`/);"
        r"if (!exampleMatch) throw new Error('No @example found in EmbeddingModel.ts');"
        r"const example = exampleMatch[1];"
        r"if (!example.includes(\"import * as Effect from 'effect/Effect'\")) {"
        r"  throw new Error('EmbeddingModel.ts JSDoc missing correct Effect import');"
        r"}"
        r"if (!example.includes('yield* EmbeddingModel.EmbeddingModel')) {"
        r"  throw new Error('EmbeddingModel.ts JSDoc should use EmbeddingModel.EmbeddingModel');"
        r"}"
        r"if (!example.includes('cosineSimilarity')) {"
        r"  throw new Error('EmbeddingModel.ts JSDoc missing cosineSimilarity helper');"
        r"}"
        r"console.log('OK');"
    )
    assert result.returncode == 0, f"EmbeddingModel.ts JSDoc check failed: {result.stderr}"


def test_ai_languagemodel_jsdoc_import_pattern():
    """packages/ai/ai/src/LanguageModel.ts JSDoc must use 'effect/Effect' and LanguageModel.LanguageModel."""
    result = _run_node_extract(
        r"const content = require('fs').readFileSync('packages/ai/ai/src/LanguageModel.ts','utf8');"
        r"const exampleMatch = content.match(/@example[\s\S]*?\`\`\`ts([\s\S]*?)\`\`\`/);"
        r"if (!exampleMatch) throw new Error('No @example found in LanguageModel.ts');"
        r"const example = exampleMatch[1];"
        r"if (!example.includes(\"import * as Effect from 'effect/Effect'\")) {"
        r"  throw new Error('LanguageModel.ts JSDoc missing correct Effect import');"
        r"}"
        r"if (!example.includes('yield* LanguageModel.LanguageModel')) {"
        r"  throw new Error('LanguageModel.ts JSDoc should use LanguageModel.LanguageModel');"
        r"}"
        r"console.log('OK');"
    )
    assert result.returncode == 0, f"LanguageModel.ts JSDoc check failed: {result.stderr}"


def test_ai_telemetry_jsdoc_updated():
    """packages/ai/ai/src/Telemetry.ts JSDoc must use 'effect/Effect' and options.response.length."""
    result = _run_node_extract(
        r"const content = require('fs').readFileSync('packages/ai/ai/src/Telemetry.ts','utf8');"
        r"const exampleMatch = content.match(/@example[\s\S]*?\`\`\`ts([\s\S]*?)\`\`\`/);"
        r"if (!exampleMatch) throw new Error('No @example found in Telemetry.ts');"
        r"const example = exampleMatch[1];"
        r"if (!example.includes(\"import * as Effect from 'effect/Effect'\")) {"
        r"  throw new Error('Telemetry.ts JSDoc missing correct Effect import');"
        r"}"
        r"if (example.includes(\"import { Context \")) {"
        r"  throw new Error('Telemetry.ts JSDoc should not import Context');"
        r"}"
        r"if (!example.includes('options.response.length')) {"
        r"  throw new Error('Telemetry.ts JSDoc should use options.response.length');"
        r"}"
        r"if (example.includes('options.model')) {"
        r"  throw new Error('Telemetry.ts JSDoc should not reference options.model');"
        r"}"
        r"console.log('OK');"
    )
    assert result.returncode == 0, f"Telemetry.ts JSDoc check failed: {result.stderr}"


# ─── P2P: Structure/regression tests ─────────────────────────────────────────


def test_agentsmd_core_sections_intact():
    """AGENTS.md must retain core sections (Development Workflow, Code Style, Testing)."""
    content = (REPO / "AGENTS.md").read_text()
    assert "## Development Workflow" in content
    assert "## Code Style Guidelines" in content
    assert "## Testing" in content


def test_eslint_standard_ignores():
    """eslint.config.mjs must still include standard ignore patterns (dist, build, docs, md)."""
    result = _run_node_extract(
        "const content = require('fs').readFileSync('eslint.config.mjs','utf8');"
        "const m = content.match(/ignores:\\s*\[([\s\S]*?)\]/);"
        "if (!m) throw new Error('No ignores found');"
        "for (const p of ['**/dist', '**/build', '**/docs', '**/*.md']) {"
        "  if (!m[1].includes(p)) throw new Error(p + ' missing from ignores');"
        "}"
        "console.log('OK');"
    )
    assert result.returncode == 0, f"eslint standard ignores check failed: {result.stderr}"


def test_gitignore_repos_added():
    """.gitignore must include .repos/ directory."""
    content = (REPO / ".gitignore").read_text()
    assert ".repos/" in content or ".repos" in content, ".gitignore should include .repos/"


# ─── P2P: Repo CI tests (origin: repo_tests) ───────────────────────────────────


def test_repo_lint():
    """Repo's eslint passes on the codebase (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install && pnpm lint"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_typecheck():
    """Repo's TypeScript type checking passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install && pnpm check"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Type check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_circular():
    """Repo's circular dependency check passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install && pnpm circular"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Circular dependency check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_type_tests():
    """Repo's type tests (tstyche) pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install && pnpm test-types --target 5.8"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Type tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_ai_chat_tests():
    """AI Chat package unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install && pnpm vitest run packages/ai/ai/test/Chat.test.ts"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"AI Chat tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_ai_languagemodel_tests():
    """AI LanguageModel package unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install && pnpm vitest run packages/ai/ai/test/LanguageModel.test.ts"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"AI LanguageModel tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
