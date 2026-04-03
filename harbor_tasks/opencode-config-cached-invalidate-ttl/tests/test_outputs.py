"""
Task: opencode-config-cached-invalidate-ttl
Repo: anomalyco/opencode @ 9f94bdb49634bda90a2804585b8d739228dde876
PR:   #19322

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

FILE = Path("/repo/packages/opencode/src/config/config.ts")


def _read_code_stripped():
    """Read config.ts with comments stripped to prevent gaming."""
    src = FILE.read_text()
    # Remove single-line comments (but not :// in URLs)
    src = re.sub(r'(?<![:"\x27\\])//[^\n]*', "", src)
    # Remove multi-line comments
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    return src


def _find_invalidate_body(code: str) -> str:
    """Extract the invalidate function body from comment-stripped code."""
    # Try multiple patterns to find the invalidate function
    for pattern in [
        r"const\s+invalidate\s*=.*?function\*\s*\(.*?\)\s*\{(.*?)\n\s{4,8}\}\)",
        r"invalidate\b.*?function\*.*?\{(.*?)\n\s{4,8}\}\)",
    ]:
        m = re.search(pattern, code, re.DOTALL)
        if m:
            return m.group(1)
    raise AssertionError("Cannot find invalidate function body")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cache_uses_cached_invalidate_with_ttl():
    """Cache must use Effect.cachedInvalidateWithTTL with const destructured binding."""
    code = _read_code_stripped()

    # Must use the cachedInvalidateWithTTL API
    assert "cachedInvalidateWithTTL" in code, (
        "cachedInvalidateWithTTL not found in code (comment-stripped)"
    )

    # Must destructure into [value, invalidateHandle] with const
    assert re.search(r"const\s+\[\s*\w+\s*,\s*\w+\s*\]\s*=\s*yield\*", code), (
        "No const [a, b] = yield* destructuring found"
    )

    # Old mutable pattern must be gone
    assert not re.search(r"\blet\s+cachedGlobal\b", code), (
        "let cachedGlobal still exists — must use const destructuring"
    )


# [pr_diff] fail_to_pass
def test_invalidate_uses_handle_not_cache_recreation():
    """invalidate() must use the invalidation handle, not recreate the cache."""
    code = _read_code_stripped()
    body = _find_invalidate_body(code)

    # Must NOT recreate cache inside invalidate
    assert "Effect.cached(" not in body, (
        "invalidate still recreates cache with Effect.cached()"
    )
    # Must NOT reassign cachedGlobal
    assert not re.search(r"cachedGlobal\s*=\s*yield", body), (
        "invalidate still reassigns cachedGlobal"
    )
    # Must yield something (the invalidation handle)
    assert "yield*" in body or "yield *" in body, (
        "invalidate has no yield statement for invalidation handle"
    )


# [pr_diff] fail_to_pass
def test_error_logging_before_fallback():
    """Errors during global config loading must be logged before falling back to defaults."""
    code = _read_code_stripped()

    # Look for error handling (tapError, logError, catchAll, tap+error, Effect.log)
    # near the loadGlobal pipe chain
    error_patterns = [
        "tapError", "logError", "catchAll",
        r"tap.*error", r"Effect\.log",
    ]
    found = False
    for pattern in error_patterns:
        for m in re.finditer(pattern, code):
            start = max(0, m.start() - 500)
            end = min(len(code), m.end() + 500)
            region = code[start:end]
            if ("orElseSucceed" in region or "loadGlobal" in region) and ".pipe(" in region:
                found = True
                break
        if found:
            break

    assert found, "No error logging found near loadGlobal pipe chain (comment-stripped)"


# [pr_diff] fail_to_pass
def test_duration_imported_and_used_as_ttl():
    """Duration must be imported from 'effect' and used as TTL argument."""
    code = _read_code_stripped()

    # Duration must be imported from 'effect'
    assert re.search(
        r"import\s*\{[^}]*\bDuration\b[^}]*\}\s*from\s*[\"']effect[\"']", code
    ), "Duration not imported from 'effect'"

    # Duration must be used near cachedInvalidateWithTTL
    idx = code.find("cachedInvalidateWithTTL")
    assert idx >= 0, "cachedInvalidateWithTTL not found"
    region = code[idx : idx + 600]
    assert re.search(r"Duration\.\w+", region), (
        "Duration.xxx not used as TTL near cachedInvalidateWithTTL"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_get_global_still_uses_cached_global():
    """getGlobal function must still exist and yield cachedGlobal."""
    content = FILE.read_text()
    assert re.search(r"const\s+getGlobal\b.*?cachedGlobal", content, re.DOTALL), (
        "getGlobal missing or not using cachedGlobal"
    )


# [pr_diff] pass_to_pass
def test_invalidate_dispatches_dispose_all():
    """invalidate function must still call Instance.disposeAll."""
    content = FILE.read_text()
    assert "Instance.disposeAll" in content, (
        "Instance.disposeAll not found in config.ts"
    )


# [pr_diff] pass_to_pass
def test_load_global_exists():
    """loadGlobal function must still exist."""
    content = FILE.read_text()
    assert re.search(r"(const|function)\s+loadGlobal\b", content), (
        "loadGlobal function not found"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:70 @ 9f94bdb
def test_const_over_let_for_cache():
    """Cache binding must use const, not let (AGENTS.md: 'Prefer const over let')."""
    code = _read_code_stripped()
    assert not re.search(r"\blet\s+cachedGlobal\b", code), (
        "let cachedGlobal still present — AGENTS.md requires const over let"
    )


# [agent_config] pass_to_pass — AGENTS.md:13 @ 9f94bdb
def test_no_any_type_near_cache_code():
    """No 'any' type used near cache-related code (AGENTS.md: 'Avoid using the any type')."""
    lines = FILE.read_text().splitlines()
    keywords = {"cachedGlobal", "cachedInvalidateWithTTL", "invalidateGlobal", "loadGlobal"}
    for i, line in enumerate(lines):
        if any(kw in line for kw in keywords):
            region = lines[max(0, i - 5) : i + 10]
            for l in region:
                stripped = re.sub(r"//.*", "", l)
                assert not re.search(r"\bas\s+any\b|:\s*any\s*[;,\s)]|:\s*any$", stripped), (
                    f"'any' type found near cache code: {l.strip()}"
                )


# [agent_config] pass_to_pass — AGENTS.md:12 @ 9f94bdb
def test_no_try_catch_in_changed_code():
    """No try/catch added near cache-related code (AGENTS.md: 'Avoid try/catch')."""
    lines = FILE.read_text().splitlines()
    keywords = {"cachedGlobal", "cachedInvalidateWithTTL", "invalidateGlobal"}
    for i, line in enumerate(lines):
        if any(kw in line for kw in keywords):
            region_lines = lines[max(0, i - 10) : i + 10]
            region_text = "\n".join(region_lines)
            assert not re.search(r"\btry\s*\{", region_text), (
                f"try/catch found near cache code at line {i + 1}"
            )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — packages/opencode/AGENTS.md:21 @ 9f94bdb
def test_effect_fn_domain_naming_retained():
    """getGlobal and invalidate must retain Effect.fn('Config.*') named/traced wrappers."""
    code = _read_code_stripped()

    assert re.search(r'Effect\.fn\(["\']Config\.getGlobal["\']', code), (
        "Effect.fn(\"Config.getGlobal\") not found — packages/opencode/AGENTS.md requires Effect.fn for named/traced effects"
    )
    assert re.search(r'Effect\.fn\(["\']Config\.invalidate["\']', code), (
        "Effect.fn(\"Config.invalidate\") not found — packages/opencode/AGENTS.md requires Effect.fn for named/traced effects"
    )


# [agent_config] pass_to_pass — AGENTS.md:84 @ 9f94bdb
def test_no_else_statements_near_cache_code():
    """No else statements added near cache-related code (AGENTS.md: 'Avoid else statements. Prefer early returns.')."""
    lines = FILE.read_text().splitlines()
    keywords = {"cachedGlobal", "cachedInvalidateWithTTL", "invalidateGlobal", "invalidateCache"}
    for i, line in enumerate(lines):
        if any(kw in line for kw in keywords):
            region = lines[max(0, i - 5) : i + 15]
            for l in region:
                stripped = re.sub(r"//.*", "", l)
                assert not re.search(r"\belse\b", stripped), (
                    f"'else' statement found near cache code: {l.strip()} — AGENTS.md requires early returns instead"
                )


# [static] pass_to_pass
def test_not_stub():
    """config.ts must not be gutted — must retain original structure."""
    content = FILE.read_text()
    lines = content.strip().splitlines()
    assert len(lines) >= 1000, f"Only {len(lines)} lines — file appears gutted"

    required = ["loadGlobal", "getGlobal", "invalidate", "loadFile", "namespace Config"]
    for req in required:
        assert req in content, f"Missing required identifier: {req}"
