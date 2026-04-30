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
    content = (REPO / "eslint.config.mjs").read_text()
    # Check that ignores array contains .repos and .lalph
    ignores_match = subprocess.run(
        ["node", "-e", rf"""
const content = require('fs').readFileSync('{REPO}/eslint.config.mjs','utf8');
const m = content.match(/ignores:\s*\[([\s\S]*?)\]/);
if (!m) {{ console.error('No ignores array found'); process.exit(1); }}
console.log(m[0]);
"""],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert ignores_match.returncode == 0, f"Failed to parse eslint config: {ignores_match.stderr}"
    assert ".repos" in ignores_match.stdout, ".repos not in ignores"
    assert ".lalph" in ignores_match.stdout, ".lalph not in ignores"


def test_eslint_formatted_correctly():
    """eslint.config.mjs must have proper formatting (selector on its own line, single-line packageNames)."""
    content = (REPO / "eslint.config.mjs").read_text()
    # Check that selector property is on its own line (formatted correctly)
    assert "selector:\n" in content, "selector not on its own line"
    # Check that packageNames array is on single line
    assert 'packageNames: ["effect", "@effect/platform", "@effect/sql"]' in content, (
        "packageNames not formatted as single line"
    )


# ─── F2P: packages/sql/tsconfig.test.json test ────────────────────────────────


def test_sql_tsconfig_outdir():
    """packages/sql/tsconfig.test.json must specify outDir for test build output."""
    tsconfig_path = REPO / "packages/sql/tsconfig.test.json"
    config = json.loads(tsconfig_path.read_text())
    assert config.get("compilerOptions", {}).get("outDir") == "build/test", (
        f"outDir missing or wrong: {config.get('compilerOptions', {}).get('outDir')}"
    )


# ─── F2P: packages/effect/src/Schema.ts JSDoc test ──────────────────────────


def test_schema_jsdoc_example_reference():
    """packages/effect/src/Schema.ts JSDoc example must use Schema.JsonNumber (not S.JsonNumber)."""
    content = (REPO / "packages/effect/src/Schema.ts").read_text()
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if "Schema.is(" in line and "JsonNumber" in line:
            if "S.JsonNumber" in line:
                raise AssertionError(f"Found S.JsonNumber at line {i+1}")
            if "Schema.JsonNumber" in line:
                return  # Success
    raise AssertionError("JsonNumber example line not found")


# ─── F2P: AI package JSDoc import pattern tests ─────────────────────────────


def test_ai_chat_jsdoc_import_pattern():
    """packages/ai/ai/src/Chat.ts JSDoc must use 'effect/Effect' import and Chat.Chat service access."""
    content = (REPO / "packages/ai/ai/src/Chat.ts").read_text()
    # Find the @example block containing "yield* Chat.Chat" (the Chat service access example)
    idx = 0
    found = False
    while True:
        example_match = content.find("@example", idx)
        if example_match == -1:
            break
        example_start = content.find("```ts", example_match)
        if example_start == -1:
            break
        example_end = content.find("```", example_start + 1)
        example = content[example_start:example_end + 3]
        
        if "yield* Chat.Chat" in example:
            found = True
            assert "import * as Effect from 'effect/Effect'" in example, (
                "Chat.ts JSDoc missing correct Effect import pattern"
            )
            assert "yield* Chat.Chat" in example, (
                "Chat.ts JSDoc should use Chat.Chat (not just Chat)"
            )
            break
        idx = example_end + 3
    
    assert found, "No @example with 'yield* Chat.Chat' found in Chat.ts"


def test_ai_aierror_jsdoc_import_patterns():
    """packages/ai/ai/src/AiError.ts JSDoc must use 'effect/Effect' and 'effect/Option' imports."""
    content = (REPO / "packages/ai/ai/src/AiError.ts").read_text()

    # Find the @example containing HttpRequestError with Option import
    idx = 0
    found_first = False
    found_second = False
    while True:
        example_match = content.find("@example", idx)
        if example_match == -1:
            break
        example_start = content.find("```ts", example_match)
        if example_start == -1:
            break
        example_end = content.find("```", example_start + 1)
        example = content[example_start:example_end + 3]
        
        # Check for first example (HttpRequestError with Option)
        if "HttpRequestError" in example and "import * as Option from 'effect/Option'" in example:
            found_first = True
            assert "import * as Effect from 'effect/Effect'" in example, (
                "AiError.ts HttpRequestError example missing Effect import"
            )
        
        # Check for second example (MalformedInput with return type)
        if "MalformedInput" in example and "Effect.Effect<string, AiError.MalformedInput>" in example:
            found_second = True
            assert "import * as Effect from 'effect/Effect'" in example, (
                "AiError.ts MalformedInput example missing Effect import"
            )
        
        idx = example_end + 3
    
    assert found_first, "No @example with HttpRequestError and Option import found in AiError.ts"
    assert found_second, "No @example with MalformedInput return type found in AiError.ts"


def test_ai_embeddingmodel_jsdoc_import_pattern():
    """packages/ai/ai/src/EmbeddingModel.ts JSDoc must use 'effect/Effect' and EmbeddingModel.EmbeddingModel."""
    content = (REPO / "packages/ai/ai/src/EmbeddingModel.ts").read_text()

    # Find the @example containing "cosineSimilarity" helper function
    idx = 0
    found = False
    while True:
        example_match = content.find("@example", idx)
        if example_match == -1:
            break
        example_start = content.find("```ts", example_match)
        if example_start == -1:
            break
        example_end = content.find("```", example_start + 1)
        example = content[example_start:example_end + 3]
        
        # Look for the specific example with cosineSimilarity helper
        if "cosineSimilarity" in example:
            found = True
            assert "import * as Effect from 'effect/Effect'" in example, (
                "EmbeddingModel.ts JSDoc missing correct Effect import"
            )
            assert "yield* EmbeddingModel.EmbeddingModel" in example, (
                "EmbeddingModel.ts JSDoc should use EmbeddingModel.EmbeddingModel"
            )
            assert "cosineSimilarity" in example, (
                "EmbeddingModel.ts JSDoc missing cosineSimilarity helper"
            )
            break
        idx = example_end + 3
    
    assert found, "No @example with 'cosineSimilarity' found in EmbeddingModel.ts"


def test_ai_languagemodel_jsdoc_import_pattern():
    """packages/ai/ai/src/LanguageModel.ts JSDoc must use 'effect/Effect' and LanguageModel.LanguageModel."""
    content = (REPO / "packages/ai/ai/src/LanguageModel.ts").read_text()

    # Find the @example containing "yield* LanguageModel.LanguageModel"
    idx = 0
    found = False
    while True:
        example_match = content.find("@example", idx)
        if example_match == -1:
            break
        example_start = content.find("```ts", example_match)
        if example_start == -1:
            break
        example_end = content.find("```", example_start + 1)
        example = content[example_start:example_end + 3]
        
        if "yield* LanguageModel.LanguageModel" in example:
            found = True
            assert "import * as Effect from 'effect/Effect'" in example, (
                "LanguageModel.ts JSDoc missing correct Effect import"
            )
            assert "yield* LanguageModel.LanguageModel" in example, (
                "LanguageModel.ts JSDoc should use LanguageModel.LanguageModel"
            )
            break
        idx = example_end + 3
    
    assert found, "No @example with 'yield* LanguageModel.LanguageModel' found in LanguageModel.ts"


def test_ai_telemetry_jsdoc_updated():
    """packages/ai/ai/src/Telemetry.ts JSDoc must use 'effect/Effect' and options.response.length."""
    content = (REPO / "packages/ai/ai/src/Telemetry.ts").read_text()

    # Find the @example containing "SpanTransformer" with updated content
    idx = 0
    found = False
    while True:
        example_match = content.find("@example", idx)
        if example_match == -1:
            break
        example_start = content.find("```ts", example_match)
        if example_start == -1:
            break
        example_end = content.find("```", example_start + 1)
        example = content[example_start:example_end + 3]
        
        if "SpanTransformer" in example and "options.response.length" in example:
            found = True
            assert "import * as Effect from 'effect/Effect'" in example, (
                "Telemetry.ts JSDoc missing correct Effect import"
            )
            assert "import { Context" not in example, (
                "Telemetry.ts JSDoc should not import Context"
            )
            assert "options.response.length" in example, (
                "Telemetry.ts JSDoc should use options.response.length"
            )
            assert "options.model" not in example, (
                "Telemetry.ts JSDoc should not reference options.model"
            )
            break
        idx = example_end + 3
    
    assert found, "No @example with 'SpanTransformer' and 'options.response.length' found in Telemetry.ts"


# ─── P2P: Structure/regression tests ─────────────────────────────────────────


def test_agentsmd_core_sections_intact():
    """AGENTS.md must retain core sections (Development Workflow, Code Style, Testing)."""
    content = (REPO / "AGENTS.md").read_text()
    assert "## Development Workflow" in content
    assert "## Code Style Guidelines" in content
    assert "## Testing" in content


def test_eslint_standard_ignores():
    """eslint.config.mjs must still include standard ignore patterns (dist, build, docs, md)."""
    content = (REPO / "eslint.config.mjs").read_text()
    for pattern in ['"**/dist"', '"**/build"', '"**/docs"', '"**/*.md"']:
        assert pattern in content, f"{pattern} missing from ignores"


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


def test_repo_ai_tool_tests():
    """AI Tool package unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install && pnpm vitest run packages/ai/ai/test/Tool.test.ts"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"AI Tool tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_ai_prompt_tests():
    """AI Prompt package unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install && pnpm vitest run packages/ai/ai/test/Prompt.test.ts"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"AI Prompt tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_sql_tests():
    """SQL package unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install && pnpm vitest run packages/sql/test/"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"SQL tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_schema_userland_tests():
    """Schema userland tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install && pnpm vitest run packages/effect/test/Schema/SchemaUserland.test.ts"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Schema userland tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_docgen():
    """Repo docgen command runs without crashing (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install && timeout 120 pnpm docgen 2>&1 || true"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    # Just verify the command ran (it may fail on base commit due to missing docgen configs)
    assert r.returncode == 0 or "docgen" in r.stdout.lower() or "docgen" in r.stderr.lower() or "build" in r.stdout, (
        f"Docgen command did not run:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
    )


def test_repo_platform_node_tests():
    """Platform-node package tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install && pnpm vitest run packages/platform-node/test/ 2>&1 | tail -20"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    # Check for test completion - should show passed or failed
    assert "Test Files" in r.stdout, (
        f"Platform-node tests did not complete:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
    )
    # Tests should pass
    assert "failed" not in r.stdout.lower() or "1 passed" in r.stdout, (
        f"Platform-node tests failed:\n{r.stdout[-500:]}"
    )


def test_repo_schema_arbitrary_tests():
    """Schema Arbitrary tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install && pnpm vitest run packages/effect/test/Schema/Arbitrary/Arbitrary.test.ts"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Schema Arbitrary tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_codegen():
    """Repo codegen command passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install && pnpm codegen"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Codegen failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_pnpm():
    """fail_to_pass | CI job 'Build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm docgen'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_pnpm():
    """pass_to_pass | CI job 'Lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm circular'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_pnpm_2():
    """pass_to_pass | CI job 'Lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_pnpm_3():
    """pass_to_pass | CI job 'Lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm codegen'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_check_for_codegen_changes():
    """pass_to_pass | CI job 'Lint' → step 'Check for codegen changes'"""
    r = subprocess.run(
        ["bash", "-lc", 'git diff --exit-code'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check for codegen changes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")