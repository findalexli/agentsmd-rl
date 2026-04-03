"""
Task: openclaw-gemini-provider-aliases
Repo: openclaw/openclaw @ 6be14ab388eb74cd100e43bf975aad78146ac220
PR:   56567

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/openclaw"
INDEX_FILE = Path(REPO) / "extensions/google/index.ts"
MODELS_FILE = Path(REPO) / "extensions/google/provider-models.ts"


def _extract_function_body(content: str, func_name: str) -> str:
    """Extract the body of a named TS function by tracking brace depth.

    Skips past the parameter type annotation (params: { ... }) to find the
    actual function body brace.
    """
    start = content.find(func_name)
    assert start != -1, f"{func_name} not found"
    # Walk past the opening paren of the function signature
    paren_pos = content.index("(", start)
    # Track paren depth to skip over the params type annotation
    depth, idx = 1, paren_pos + 1
    while depth > 0 and idx < len(content):
        if content[idx] == "(":
            depth += 1
        elif content[idx] == ")":
            depth -= 1
        idx += 1
    # Now idx is just past the closing ')' of the params; find the function body '{'
    brace_pos = content.index("{", idx)
    depth, idx = 1, brace_pos + 1
    while depth > 0 and idx < len(content):
        if content[idx] == "{":
            depth += 1
        elif content[idx] == "}":
            depth -= 1
        idx += 1
    return content[brace_pos:idx]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_syntax():
    """Modified TypeScript files exist and have balanced braces."""
    # Text inspection because: TypeScript requires full monorepo build to compile
    for f in [INDEX_FILE, MODELS_FILE]:
        assert f.exists(), f"Missing: {f}"
        content = f.read_text()
        assert len(content.strip()) > 100, f"File too small: {f}"
        assert content.count("{") == content.count("}"), f"Unbalanced braces in {f}"
        assert content.count("(") == content.count(")"), f"Unbalanced parens in {f}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core bug fix checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_runtime_provider_not_hardcoded():
    """index.ts passes runtime ctx.provider instead of hardcoded 'google'."""
    # Text inspection because: TypeScript, can't import from Python
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
    # Text inspection because: TypeScript, can't import from Python
    models_content = MODELS_FILE.read_text()

    # The exported function must accept templateProviderId
    func_sig_area = models_content[
        models_content.find("resolveGoogle31ForwardCompatModel"):
    ][:500]
    assert "templateProviderId" in func_sig_area, (
        "resolveGoogle31ForwardCompatModel missing templateProviderId parameter"
    )

    # At least one call in index.ts must pass templateProviderId
    # (there are multiple calls — the gemini-cli provider has its own)
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


# [pr_diff] fail_to_pass
def test_flash_lite_prefix_before_flash():
    """flash-lite prefix checked before flash prefix to avoid misclassification."""
    # Text inspection because: TypeScript, can't import from Python
    content = MODELS_FILE.read_text()
    func_body = _extract_function_body(content, "resolveGoogle31ForwardCompatModel")

    # Find conditional checks for flash-lite vs flash in the if-else chain
    lite_match = re.search(
        r'(?:startsWith|includes|===|==)[^;{}\n]*?(?:FLASH_LITE|flash[\-_]lite)',
        func_body,
        re.IGNORECASE,
    )
    assert lite_match, "No flash-lite prefix check found in resolver"

    # Find flash-only checks (not flash-lite)
    flash_only = None
    for m in re.finditer(
        r'(?:startsWith|includes|===|==)[^;{}\n]*?(?:FLASH_PREFIX|["\']gemini[^"\']*flash["\'])',
        func_body,
        re.IGNORECASE,
    ):
        if "lite" not in m.group(0).lower():
            flash_only = m
            break

    assert flash_only, "No flash prefix check found in resolver"
    assert lite_match.start() < flash_only.start(), (
        "flash-lite check must come before flash check"
    )


# [pr_diff] fail_to_pass
def test_flash_lite_template_ids():
    """flash-lite models map to their own template IDs, not flash templates."""
    # Text inspection because: TypeScript, can't import from Python
    content = MODELS_FILE.read_text()

    # Must define flash-lite-specific template IDs
    has_lite_templates = (
        re.search(r"FLASH_LITE_TEMPLATE_IDS", content)
        or re.search(r"flash[\-_.]lite.*template", content, re.IGNORECASE)
        or re.search(r"template.*flash[\-_.]lite", content, re.IGNORECASE)
    )
    assert has_lite_templates, "No flash-lite-specific template IDs defined"

    # If a named constant exists, verify it contains flash-lite model references
    lite_array = re.search(
        r"FLASH_LITE_TEMPLATE_IDS\s*(?:=|:)\s*\[([^\]]+)\]",
        content,
    )
    if lite_array:
        arr = lite_array.group(1).lower()
        # The template IDs should reference flash-lite (not plain flash)
        assert "flash" in arr, "flash-lite template array is empty or has no model refs"


# [pr_diff] fail_to_pass
def test_cross_provider_template_lookup():
    """Template lookup tries multiple provider IDs for cross-provider resolution."""
    # Text inspection because: TypeScript, can't import from Python
    content = MODELS_FILE.read_text()

    # The fix introduces a helper (or inline logic) that tries providerId then
    # falls back to templateProviderId for template lookup
    has_fallback = (
        # Named helper
        re.search(r"cloneFirstGoogleTemplateModel", content)
        # Or a for/iteration over provider IDs with template lookup
        or (
            re.search(r"for\s*\(", content)
            and re.search(r"templateProviderId", content)
            and re.search(r"cloneFirstTemplateModel", content)
        )
    )
    assert has_fallback, (
        "No cross-provider template lookup logic — must try actual providerId "
        "then fall back to templateProviderId"
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
                # From extensions/google/*.ts, 2+ levels up escapes the package
                assert up_count < 2, (
                    f"{f.name}:{i} relative import escapes package: {line.strip()}"
                )


# [agent_config] pass_to_pass — CLAUDE.md:106 @ 6be14ab388eb74cd100e43bf975aad78146ac220
def test_no_dynamic_import_mixing():
    """Do not mix await import() and static import for the same module."""
    # Text inspection because: TypeScript, can't import from Python
    for f in [INDEX_FILE, MODELS_FILE]:
        content = f.read_text()
        # Collect statically imported module specifiers
        static_imports = set(
            re.findall(r"""import\s+.*?\s+from\s+['"]([^'"]+)['"]""", content)
        )
        # Collect dynamically imported module specifiers
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
    # Text inspection because: TypeScript, can't import from Python
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
