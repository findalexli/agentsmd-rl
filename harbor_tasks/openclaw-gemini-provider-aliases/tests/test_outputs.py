"""
Task: openclaw-gemini-provider-aliases
Repo: openclaw/openclaw @ 6be14ab388eb74cd100e43bf975aad78146ac220
PR:   56567

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/openclaw"
INDEX_FILE = Path(REPO) / "extensions/google/index.ts"
MODELS_FILE = Path(REPO) / "extensions/google/provider-models.ts"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _run(cmd, cwd=REPO, timeout=120, **kw):
    return subprocess.run(
        cmd, capture_output=True, text=True, cwd=cwd, timeout=timeout, **kw
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base and after fix
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass — ox lint passes
def test_repo_lint():
    """Repo's oxlint passes with 0 warnings/errors (pass_to_pass)."""
    r = _run(
        ["npx", "oxlint", "--type-aware"],
        timeout=90,
    )
    assert r.returncode == 0, f"Lint failed:\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"


# [repo_tests] pass_to_pass — google extension tests pass
def test_repo_google_extension_tests():
    """Google extension tests pass (pass_to_pass)."""
    r = _run(
        ["npx", "vitest", "run", "extensions/google/", "--reporter=verbose"],
        timeout=120,
    )
    assert r.returncode == 0, (
        f"Google extension tests failed (rc={r.returncode}):\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )
    assert "FAIL" not in r.stdout, f"Some tests failed:\n{r.stdout}"


# [repo_tests] pass_to_pass — no conflict markers
def test_repo_no_conflict_markers():
    """Repo has no conflict markers (pass_to_pass)."""
    r = _run(["pnpm", "check:no-conflict-markers"], timeout=30)
    assert r.returncode == 0, f"Conflict markers check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass — google-shared utilities tests
def test_repo_google_shared_tests():
    """Google shared utilities tests pass (pass_to_pass)."""
    r = _run(
        ["npx", "vitest", "run", "extensions/google/google-shared.test.ts", "--reporter=verbose"],
        timeout=120,
    )
    assert r.returncode == 0, (
        f"Google shared tests failed (rc={r.returncode}):\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )
    assert "FAIL" not in r.stdout, f"Some tests failed:\n{r.stdout}"


# [repo_tests] pass_to_pass — extension boundary checks
def test_repo_extension_no_src_outside_plugin_sdk():
    """Extensions don't import src/** outside plugin-sdk (pass_to_pass)."""
    r = _run(["pnpm", "lint:extensions:no-src-outside-plugin-sdk"], timeout=30)
    assert r.returncode == 0, f"Extension boundary check failed:\n{r.stderr}"


def test_repo_extension_no_relative_outside_package():
    """Extensions don't use relative imports escaping package (pass_to_pass)."""
    r = _run(["pnpm", "lint:extensions:no-relative-outside-package"], timeout=30)
    assert r.returncode == 0, f"Extension relative import check failed:\n{r.stderr}"


def test_repo_extension_no_plugin_sdk_internal():
    """Extensions don't import plugin-sdk-internal (pass_to_pass)."""
    r = _run(["pnpm", "lint:extensions:no-plugin-sdk-internal"], timeout=30)
    assert r.returncode == 0, f"Extension plugin-sdk-internal check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass — format check for modified files
def test_repo_format_check():
    """Modified TypeScript files are properly formatted (pass_to_pass)."""
    r = _run(
        ["npx", "oxfmt", "--check", "--threads=1", "extensions/google/provider-models.ts", "extensions/google/index.ts"],
        timeout=30,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — TypeScript typecheck for plugin-sdk types
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes for plugin-sdk types (pass_to_pass)."""
    r = _run(
        ["npx", "tsc", "--noEmit", "--project", "tsconfig.plugin-sdk.dts.json"],
        timeout=120,
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — plugin-sdk types build
def test_repo_build():
    """Repo's plugin-sdk types build passes (pass_to_pass)."""
    r = _run(
        ["pnpm", "build:plugin-sdk:dts"],
        timeout=120,
    )
    assert r.returncode == 0, f"Plugin-sdk types build failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — pnpm test:extension wrapper for google
def test_repo_test_extension_google():
    """Google extension tests pass via CI test:extension wrapper (pass_to_pass)."""
    r = _run(
        ["pnpm", "test:extension", "google"],
        timeout=180,
    )
    assert r.returncode == 0, (
        f"test:extension google failed (rc={r.returncode}):\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )
    assert "FAIL" not in r.stdout, f"Some tests failed:\n{r.stdout}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_typescript_syntax():
    """Modified TypeScript files exist and have balanced braces."""
    for f in [INDEX_FILE, MODELS_FILE]:
        assert f.exists(), f"Missing: {f}"
        content = f.read_text()
        assert len(content.strip()) > 100, f"File too small: {f}"
        assert content.count("{") == content.count("}"), f"Unbalanced braces in {f}"
        assert content.count("(") == content.count(")"), f"Unbalanced parens in {f}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core bug fix checks via code execution
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_resolve_pro_for_alias_provider():
    """resolveGoogle31ForwardCompatModel resolves pro model for alias provider."""
    r = _run(
        ["npx", "vitest", "run",
         "extensions/google/provider-models.test.ts",
         "--reporter=verbose"],
    )
    assert r.returncode == 0, (
        f"Vitest failed (rc={r.returncode}).\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )
    # The test suite must include at least one passing test for pro resolution
    assert "resolves gemini 3.1 pro" in r.stdout.lower() or re.search(
        r"resolves.*pro.*alias", r.stdout, re.IGNORECASE
    ), f"Pro resolution test not found in output:\n{r.stdout}"
    # Overall must show all tests passed
    assert "Tests" in r.stdout or "passed" in r.stdout.lower() or "FAIL" not in r.stdout, (
        f"Not all tests passed:\n{r.stdout}"
    )


# [pr_diff] fail_to_pass
def test_resolve_flash_from_direct_provider():
    """resolveGoogle31ForwardCompatModel resolves flash from direct google templates."""
    r = _run(
        ["npx", "vitest", "run",
         "extensions/google/provider-models.test.ts",
         "--reporter=verbose"],
    )
    assert r.returncode == 0, (
        f"Vitest failed (rc={r.returncode}).\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )
    assert "resolves gemini 3.1 flash" in r.stdout.lower() or re.search(
        r"resolves.*flash.*direct", r.stdout, re.IGNORECASE
    ), f"Flash resolution test not found in output:\n{r.stdout}"
    assert "FAIL" not in r.stdout, f"Some tests failed:\n{r.stdout}"


# [pr_diff] fail_to_pass
def test_flash_lite_not_misclassified_as_flash():
    """flash-lite models resolve to their own template, not the broader flash prefix."""
    r = _run(
        ["npx", "vitest", "run",
         "extensions/google/provider-models.test.ts",
         "--reporter=verbose"],
    )
    assert r.returncode == 0, (
        f"Vitest failed (rc={r.returncode}).\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )
    assert "flash-lite" in r.stdout.lower() or "flash lite" in r.stdout.lower(), (
        f"Flash-lite test not referenced in output:\n{r.stdout}"
    )
    # Ensure the flash-lite test specifically passed (not just the suite overall)
    assert "FAIL" not in r.stdout, f"Flash-lite test may have failed:\n{r.stdout}"


# [pr_diff] fail_to_pass
def test_runtime_provider_not_hardcoded():
    """index.ts passes runtime ctx.provider instead of hardcoded 'google'."""
    content = INDEX_FILE.read_text()

    call_pattern = re.compile(
        r"resolveGoogle31ForwardCompatModel\s*\(\s*\{([^}]+)\}",
        re.DOTALL,
    )
    matches = call_pattern.findall(content)
    assert matches, "resolveGoogle31ForwardCompatModel call not found in index.ts"

    for call_args in matches:
        # The bug: providerId: "google" (hardcoded string literal)
        assert not re.search(
            r"""providerId\s*:\s*["']google["']""", call_args
        ), 'Still hardcodes providerId: "google"'
        # Must have providerId set to something dynamic (not any string literal)
        assert re.search(
            r"providerId\s*:", call_args
        ), "providerId not set in call"
        assert not re.search(
            r"""providerId\s*:\s*["'][a-zA-Z\-]+["']""", call_args
        ), "providerId is still a hardcoded string literal"


# [pr_diff] fail_to_pass
def test_template_provider_id_fallback():
    """resolveGoogle31ForwardCompatModel accepts templateProviderId for cross-provider lookup."""
    models_content = MODELS_FILE.read_text()

    func_sig_area = models_content[
        models_content.find("resolveGoogle31ForwardCompatModel"):
    ][:500]
    assert "templateProviderId" in func_sig_area, (
        "resolveGoogle31ForwardCompatModel missing templateProviderId parameter"
    )

    index_content = INDEX_FILE.read_text()
    call_matches = re.findall(
        r"resolveGoogle31ForwardCompatModel\s*\(\s*\{([^}]+)\}",
        index_content,
        re.DOTALL,
    )
    assert call_matches, "resolveGoogle31ForwardCompatModel call not found in index.ts"
    assert any("templateProviderId" in args for args in call_matches), (
        "No call to resolveGoogle31ForwardCompatModel passes templateProviderId"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_not_stub():
    """provider-models.ts has substantial implementation logic."""
    content = MODELS_FILE.read_text()

    stripped = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
    stripped = re.sub(r"/\*.*?\*/", "", stripped, flags=re.DOTALL)
    code_lines = [l for l in stripped.splitlines() if l.strip()]
    assert len(code_lines) >= 30, f"Only {len(code_lines)} code lines — likely a stub"

    assert "return" in content, "No return statements"
    assert "if" in content or "?" in content, "No conditional logic"
    assert re.search(r"cloneFirst\w*TemplateModel", content), (
        "No template cloning logic"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — CLAUDE.md / AGENTS.md rules
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — CLAUDE.md:16 @ 6be14ab388eb74cd100e43bf975aad78146ac220
def test_no_core_internal_imports():
    """Extension code must not import from core src/** internals."""
    for f in [INDEX_FILE, MODELS_FILE]:
        content = f.read_text()
        for i, line in enumerate(content.splitlines(), 1):
            assert not re.match(
                r"""^import .* from ['"]\.\.\/\.\.\/\.\.\/src\/""", line
            ), f"{f.name}:{i} imports core internals: {line.strip()}"
            assert not re.search(
                r"""from ['"].*src/plugin-sdk-internal""", line
            ), f"{f.name}:{i} imports plugin-sdk internals: {line.strip()}"


# [agent_config] pass_to_pass — CLAUDE.md:104 @ 6be14ab388eb74cd100e43bf975aad78146ac220
def test_no_ts_nocheck():
    """No @ts-nocheck directives in modified files."""
    for f in [INDEX_FILE, MODELS_FILE]:
        content = f.read_text()
        assert "@ts-nocheck" not in content, f"{f.name} contains @ts-nocheck"


# [agent_config] pass_to_pass — CLAUDE.md:102 @ 6be14ab388eb74cd100e43bf975aad78146ac220
def test_no_explicit_any():
    """Avoid explicit 'any' type annotations; prefer real types or unknown."""
    for f in [INDEX_FILE, MODELS_FILE]:
        content = f.read_text()
        for i, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            assert not re.search(r":\s*any\b", line), (
                f"{f.name}:{i} uses ': any': {stripped}"
            )
            assert not re.search(r"\bas\s+any\b", line), (
                f"{f.name}:{i} uses 'as any': {stripped}"
            )


# [agent_config] pass_to_pass — CLAUDE.md:108 @ 6be14ab388eb74cd100e43bf975aad78146ac220
def test_no_extension_self_import():
    """Extension must not import itself via openclaw/plugin-sdk/google."""
    for f in [INDEX_FILE, MODELS_FILE]:
        content = f.read_text()
        for i, line in enumerate(content.splitlines(), 1):
            assert not re.search(
                r"""from ['"]openclaw/plugin-sdk/google""", line
            ), f"{f.name}:{i} self-imports via plugin-sdk: {line.strip()}"


# [agent_config] pass_to_pass — CLAUDE.md:109 @ 6be14ab388eb74cd100e43bf975aad78146ac220
def test_no_relative_imports_outside_package():
    """No relative imports that escape extensions/google/ package boundary."""
    for f in [INDEX_FILE, MODELS_FILE]:
        content = f.read_text()
        for i, line in enumerate(content.splitlines(), 1):
            m = re.search(r"""from ['"](\.\.[^'"]+)['"]""", line)
            if m:
                up_count = m.group(1).split("/").count("..")
                assert up_count < 2, (
                    f"{f.name}:{i} relative import escapes package: {line.strip()}"
                )


# [agent_config] pass_to_pass — CLAUDE.md:106 @ 6be14ab388eb74cd100e43bf975aad78146ac220
def test_no_dynamic_import_mixing():
    """Do not mix await import() and static import for the same module."""
    for f in [INDEX_FILE, MODELS_FILE]:
        content = f.read_text()
        static_imports = set(
            re.findall(r"""import\s+.*?\s+from\s+['"]([^'"]+)['"]""", content)
        )
        dynamic_imports = set(
            re.findall(r"""await\s+import\s*\(\s*['"]([^'"]+)['"]\s*\)""", content)
        )
        overlap = static_imports & dynamic_imports
        assert not overlap, (
            f"{f.name} mixes static and dynamic import for: {overlap}"
        )


# [agent_config] pass_to_pass — CLAUDE.md:104 @ 6be14ab388eb74cd100e43bf975aad78146ac220
def test_no_ts_ignore():
    """No @ts-ignore inline TypeScript suppression directives in modified files."""
    for f in [INDEX_FILE, MODELS_FILE]:
        content = f.read_text()
        assert "@ts-ignore" not in content, f"{f.name} contains @ts-ignore"


# [agent_config] pass_to_pass — CLAUDE.md:111 @ 6be14ab388eb74cd100e43bf975aad78146ac220
def test_no_prototype_mutation():
    """No prototype mutation in production code."""
    for f in [INDEX_FILE, MODELS_FILE]:
        content = f.read_text()
        for i, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            assert "applyPrototypeMixins" not in line, (
                f"{f.name}:{i} uses applyPrototypeMixins: {stripped}"
            )
            assert not re.search(r"\.prototype\s*\.", line), (
                f"{f.name}:{i} mutates prototype: {stripped}"
            )
            assert not re.search(
                r"Object\.defineProperty\s*\([^,]+\.prototype", line
            ), (
                f"{f.name}:{i} defines property on prototype: {stripped}"
            )
