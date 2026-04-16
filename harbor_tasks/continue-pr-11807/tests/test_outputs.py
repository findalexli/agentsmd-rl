"""
Test suite for continue#11807: contextLength YAML model config fix.

Tests verify that contextLength set at the model level in YAML config is
properly respected (not silently stripped by the Zod schema).
"""

import os
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(os.environ.get("REPO", "/workspace/continue"))


class TestContextLengthYamlSchema:
    """Test that contextLength is properly included in the YAML model schema."""

    def test_contextlength_field_in_base_model_fields(self):
        """contextLength must be a valid field at the model level in baseModelFields.

        The bug was that contextLength at model level (outside defaultCompletionOptions)
        was silently stripped by Zod because it wasn't defined in baseModelFields.
        The fix adds contextLength: z.number().optional() to baseModelFields.
        """
        schema_path = REPO / "packages/config-yaml/src/schemas/models.ts"
        assert schema_path.exists(), f"Schema file not found: {schema_path}"

        content = schema_path.read_text()

        # Find baseModelFields definition
        base_model_fields_match = re.search(
            r"const baseModelFields\s*=\s*\{(.+?)\n\};",
            content,
            re.DOTALL,
        )
        assert base_model_fields_match, "Could not find baseModelFields definition"

        base_model_fields_body = base_model_fields_match.group(1)

        # Check that contextLength is in baseModelFields
        has_contextlength = re.search(
            r"contextLength\s*:\s*z\.number\(\)\.optional\(\)",
            base_model_fields_body,
        )

        assert has_contextlength, (
            "contextLength must be defined as z.number().optional() in baseModelFields. "
            "Without this, Zod silently strips contextLength when placed at the model level. "
            "Check packages/config-yaml/src/schemas/models.ts baseModelFields."
        )


class TestContextLengthValidation:
    """Test that validation.ts uses effectiveContextLength for model-level contextLength."""

    def test_validation_uses_effective_context_length(self):
        """validation.ts must compute effectiveContextLength = model.contextLength ?? defaultCompletionOptions.contextLength.

        The bug was that contextLength was only read from defaultCompletionOptions,
        ignoring the model-level contextLength. The fix adds effectiveContextLength
        that prefers model-level over defaultCompletionOptions.
        """
        validation_path = REPO / "packages/config-yaml/src/validation.ts"
        assert validation_path.exists(), f"validation.ts not found: {validation_path}"

        content = validation_path.read_text()

        # The fix adds: const effectiveContextLength = model.contextLength ?? model.defaultCompletionOptions?.contextLength;
        has_effective_context_length = re.search(
            r"const\s+effectiveContextLength\s*=\s*model\.contextLength\s*\?\?\s*model\.defaultCompletionOptions",
            content,
        )

        assert has_effective_context_length, (
            "validation.ts must compute effectiveContextLength as "
            "model.contextLength ?? model.defaultCompletionOptions?.contextLength. "
            "Without this, model-level contextLength is ignored in validation. "
            "Check packages/config-yaml/src/validation.ts validateConfigYaml function."
        )

    def test_validation_warning_uses_effective_values(self):
        """Validation warning message must use effectiveContextLength and effectiveMaxTokens."""
        validation_path = REPO / "packages/config-yaml/src/validation.ts"
        content = validation_path.read_text()

        # The fix changes the message to use effectiveContextLength and effectiveMaxTokens
        # instead of model.defaultCompletionOptions?.contextLength and maxTokens
        has_effective_warning = re.search(
            r"effectiveContextLength.*?effectiveMaxTokens|effectiveMaxTokens.*?effectiveContextLength",
            content,
        )

        assert has_effective_warning, (
            "Validation warning must use effectiveContextLength and effectiveMaxTokens. "
            "Check packages/config-yaml/src/validation.ts."
        )


class TestConfigSliceConstants:
    """Test that gui/src/redux/slices/configSlice.ts uses correct fallback constant."""

    def test_configslice_uses_default_context_length(self):
        """selectSelectedChatModelContextLength must fallback to DEFAULT_CONTEXT_LENGTH, not DEFAULT_MAX_TOKENS.

        The bug: the selector was falling back to DEFAULT_MAX_TOKENS (4096) instead of
        DEFAULT_CONTEXT_LENGTH (32768), causing incorrect context length to be used when
        no contextLength is explicitly configured.
        """
        config_slice = REPO / "gui/src/redux/slices/configSlice.ts"
        assert config_slice.exists(), f"configSlice not found: {config_slice}"

        content = config_slice.read_text()

        # Find the selectSelectedChatModelContextLength selector
        pattern = r"selectSelectedChatModelContextLength[^{]*\{[^}]*return\s*\([^)]+\)"
        match = re.search(pattern, content, re.DOTALL)
        assert match is not None, "Could not find selectSelectedChatModelContextLength implementation"

        # The function body should use DEFAULT_CONTEXT_LENGTH, not DEFAULT_MAX_TOKENS
        func_body = match.group(0)
        uses_correct = "DEFAULT_CONTEXT_LENGTH" in func_body
        uses_wrong = "DEFAULT_MAX_TOKENS" in func_body

        assert uses_correct and not uses_wrong, (
            "selectSelectedChatModelContextLength must fallback to DEFAULT_CONTEXT_LENGTH, "
            f"not DEFAULT_MAX_TOKENS. Found:\n{func_body}"
        )


class TestCoreConfigYaml:
    """Test that core/config/yaml/models.ts reads contextLength from both locations."""

    def test_core_models_reads_contextlength_from_model_level(self):
        """core/config/yaml/models.ts must read contextLength from model.contextLength ?? defaultCompletionOptions.contextLength.

        The bug was that contextLength was only read from defaultCompletionOptions.contextLength,
        ignoring any contextLength set at the model level.
        """
        models_path = REPO / "core/config/yaml/models.ts"
        assert models_path.exists(), f"models.ts not found: {models_path}"

        content = models_path.read_text()

        # The fix adds: const contextLength = model.contextLength ?? model.defaultCompletionOptions?.contextLength;
        # before using it in the LLMOptions
        # The code may span multiple lines, so we search for the key parts
        has_contextLength_const = re.search(
            r"const\s+contextLength\s*=", content)
        has_model_contextlength_fallback = re.search(
            r"model\.contextLength\s*\?\?\s*model\.defaultCompletionOptions",
            content
        )

        assert has_contextLength_const and has_model_contextlength_fallback, (
            "core/config/yaml/models.ts must compute contextLength as "
            "model.contextLength ?? model.defaultCompletionOptions?.contextLength. "
            "Without this, model-level contextLength is ignored when creating LLM options."
        )


class TestRepoLint:
    """Run repo's own linting/typechecking as pass_to_pass tests."""

    def test_no_typescript_errors(self):
        """TypeScript compilation must succeed on the fixed code.

        This is a pass_to_pass test - it should pass both before and after the fix,
        as long as the code is syntactically correct.
        """
        # Check if node_modules/.bin/tsc exists in config-yaml
        tsc_path = REPO / "packages/config-yaml/node_modules/.bin/tsc"
        if not tsc_path.exists():
            pytest.skip("TypeScript not installed in config-yaml package")

        result = subprocess.run(
            [str(tsc_path), "--noEmit", "--skipLibCheck", "-p", "packages/config-yaml/tsconfig.json"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
        # Skip if there are workspace dependency errors (monorepo not fully built)
        if "Cannot find module" in (result.stderr + result.stdout) and "@continuedev/" in (result.stderr + result.stdout):
            pytest.skip("Workspace dependencies not built (monorepo setup issue)")
        # If there are actual TS errors, fail the test
        if "error TS" in result.stderr:
            assert False, f"TypeScript check failed:\n{result.stderr[-1000:]}"

        assert result.returncode == 0, f"TypeScript check failed:\n{result.stderr[-1000:]}"

    def test_repo_prettier_check(self):
        """Prettier formatting check passes on modified files (pass_to_pass).

        This verifies that the code formatting is consistent with the repo's style.
        Runs prettier on the specific files modified by the contextLength fix.
        """
        r = subprocess.run(
            ["bash", "-c",
             "cd /workspace/continue && npm ci --silent 2>/dev/null && "
             "node node_modules/prettier/bin/prettier.cjs --check "
             "'packages/config-yaml/src/schemas/models.ts' "
             "'packages/config-yaml/src/validation.ts' "
             "'gui/src/redux/slices/configSlice.ts' "
             "'core/config/yaml/models.ts'"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


class TestRepoTests:
    """Run repo's own test suite as pass_to_pass tests."""

    def test_repo_vitest_models(self):
        """Vitest tests for core/config/yaml/models.ts pass (pass_to_pass).

        The models.vitest.ts file tests llmsFromModelConfig which handles
        model configuration including contextLength. These tests verify
        the requestOptions merging logic works correctly.
        """
        r = subprocess.run(
            ["bash", "-c",
             "cd /workspace/continue/core && npm install 2>/dev/null && "
             "node node_modules/vitest/vitest.mjs run config/yaml/models.vitest.ts"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        # Check for test failures in output
        if "FAIL" in r.stdout:
            assert False, f"Vitest tests failed:\n{r.stdout[-1000:]}"
        assert r.returncode == 0, f"Vitest failed:\n{r.stderr[-500:]}"

    def test_repo_jest_config_yaml_model_name(self):
        """Jest tests for config-yaml modelName pass (pass_to_pass).

        Tests the parseProxyModelName function which is used in model
        configuration parsing, relevant to contextLength handling.
        """
        r = subprocess.run(
            ["bash", "-c",
             "cd /workspace/continue/packages/config-yaml && npm ci 2>/dev/null && "
             "node --experimental-vm-modules node_modules/jest/bin/jest.js modelName.test.ts"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if "FAIL" in r.stdout:
            assert False, f"Jest modelName tests failed:\n{r.stdout[-1000:]}"
        assert r.returncode == 0, f"Jest failed:\n{r.stderr[-500:]}"

    def test_repo_jest_config_yaml_slugs(self):
        """Jest tests for config-yaml slugs pass (pass_to_pass).

        Tests package slug parsing used in model configuration.
        """
        r = subprocess.run(
            ["bash", "-c",
             "cd /workspace/continue/packages/config-yaml && npm ci 2>/dev/null && "
             "node --experimental-vm-modules node_modules/jest/bin/jest.js slugs.test.ts"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if "FAIL" in r.stdout:
            assert False, f"Jest slugs tests failed:\n{r.stdout[-1000:]}"
        assert r.returncode == 0, f"Jest failed:\n{r.stderr[-500:]}"

    def test_repo_jest_config_yaml_secret_result(self):
        """Jest tests for config-yaml SecretResult pass (pass_to_pass).

        Tests secret location encoding/decoding used in model configuration.
        """
        r = subprocess.run(
            ["bash", "-c",
             "cd /workspace/continue/packages/config-yaml && npm ci 2>/dev/null && "
             "node --experimental-vm-modules node_modules/jest/bin/jest.js SecretResult.test.ts"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if "FAIL" in r.stdout:
            assert False, f"Jest SecretResult tests failed:\n{r.stdout[-1000:]}"
        assert r.returncode == 0, f"Jest failed:\n{r.stderr[-500:]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
