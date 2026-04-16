"""
Task: opencode-config-cached-invalidate-ttl
Repo: anomalyco/opencode @ 9f94bdb49634bda90a2804585b8d739228dde876

Behavioral tests that verify the code changes work correctly,
without being tied to specific variable names or implementation details.
"""

import subprocess
import re
from pathlib import Path

FILE = Path("/repo/packages/opencode/src/config/config.ts")
REPO = "/repo"


def _strip_comments(content: str) -> str:
    """Remove comments from TypeScript code for analysis."""
    result = re.sub(r'(?<![:"\'\\])//[^\n]*', '', content)
    result = re.sub(r'/\*[\s\S]*?\*/', '', result)
    return result


def _parse_ts_imports(content: str) -> list:
    """Parse TypeScript imports from 'effect' package."""
    imports = []
    stripped = _strip_comments(content)
    pattern = r'import\s*\{([^}]+)\}\s*from\s*["\']effect["\']'
    for match in re.finditer(pattern, stripped):
        names = match.group(1)
        for name in names.split(','):
            clean = name.strip().split(' as ')[0].strip()
            if clean:
                imports.append(clean)
    return imports


def _extract_function_body(content: str, func_name: str) -> str | None:
    """Extract the body of a function* defined with Effect.fn."""
    stripped = _strip_comments(content)
    pattern = rf'Effect\.fn\(["\'][^"\']*{re.escape(func_name)}["\']\)\s*\(\s*function\*\s*\([^)]*\)\s*\{{'
    match = re.search(pattern, stripped)
    if not match:
        pattern2 = rf'const\s+{re.escape(func_name)}\s*=\s*function\*\s*\([^)]*\)\s*\{{'
        match = re.search(pattern2, stripped)
    if not match:
        return None
    start_idx = match.end() - 1
    depth = 1
    pos = start_idx + 1
    while pos < len(stripped) and depth > 0:
        if stripped[pos] == '{':
            depth += 1
        elif stripped[pos] == '}':
            depth -= 1
        pos += 1
    return stripped[start_idx + 1:pos - 1]


def _extract_cached_invalidate_region(content: str) -> str | None:
    """Extract the region containing cachedInvalidateWithTTL call."""
    stripped = _strip_comments(content)
    idx = stripped.find('cachedInvalidateWithTTL')
    if idx < 0:
        return None
    paren_idx = stripped.find('(', idx)
    if paren_idx < 0:
        return None
    depth = 1
    pos = paren_idx + 1
    while pos < len(stripped) and depth > 0:
        if stripped[pos] == '(':
            depth += 1
        elif stripped[pos] == ')':
            depth -= 1
        pos += 1
    return stripped[idx:pos]


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff)
# -----------------------------------------------------------------------------

def test_duration_imported_from_effect():
    """Duration must be imported from 'effect' package."""
    content = FILE.read_text()
    imports = _parse_ts_imports(content)
    assert 'Duration' in imports, f"Duration not imported from 'effect'. Found: {imports}"


def test_cached_invalidate_with_ttl_used():
    """Code must use Effect.cachedInvalidateWithTTL with destructuring."""
    content = FILE.read_text()
    stripped = _strip_comments(content)
    assert 'cachedInvalidateWithTTL' in stripped, "Must use Effect.cachedInvalidateWithTTL"
    destructuring = re.search(
        r'const\s*\[\s*\w+\s*,\s*\w+\s*\]\s*=\s*yield\*\s*Effect\.cachedInvalidateWithTTL',
        stripped
    )
    assert destructuring, "Must use destructuring: const [x, y] = yield* Effect.cachedInvalidateWithTTL(...)"


def test_error_logging_before_fallback():
    """Errors must be logged via tapError before orElseSucceed."""
    content = FILE.read_text()
    region = _extract_cached_invalidate_region(content)
    assert region is not None, "cachedInvalidateWithTTL region not found"
    assert 'tapError' in region, "tapError not found - errors must be logged"
    tap_idx = region.find('tapError')
    or_else_idx = region.find('orElseSucceed')
    assert tap_idx >= 0 and or_else_idx >= 0 and tap_idx < or_else_idx, \
        "tapError must come before orElseSucceed"
    assert 'failed to load global config' in region, "Error message not found"


def test_invalidate_uses_handle_not_recreation():
    """invalidate() must yield the invalidation handle, not recreate cache."""
    content = FILE.read_text()
    invalidate_body = _extract_function_body(content, 'invalidate')
    assert invalidate_body is not None, "Could not extract invalidate function body"
    assert 'Effect.cached(' not in invalidate_body, "invalidate() still recreates cache with Effect.cached()"
    assert not re.search(r'\bcachedGlobal\s*=', invalidate_body), "invalidate() still reassigns cachedGlobal"
    assert re.search(r'yield\s*\*', invalidate_body), "invalidate() must yield the invalidation handle"


def test_ttl_uses_duration():
    """TTL argument must use Duration (e.g., Duration.infinity)."""
    content = FILE.read_text()
    region = _extract_cached_invalidate_region(content)
    assert region is not None, "cachedInvalidateWithTTL region not found"
    assert re.search(r'Duration\.\w+', region), "Duration.* not used as TTL argument"


# -----------------------------------------------------------------------------
# Fail-to-pass (agent_config)
# -----------------------------------------------------------------------------

def test_const_over_let_for_cache():
    """Cache binding must use const, not let."""
    content = FILE.read_text()
    stripped = _strip_comments(content)
    let_pattern = re.search(r'\blet\s+cachedGlobal\b', stripped)
    assert let_pattern is None, "Found 'let cachedGlobal' - must use const destructuring"


# -----------------------------------------------------------------------------
# Pass-to-pass (pr_diff)
# -----------------------------------------------------------------------------

def test_get_global_still_exists():
    """getGlobal function must still exist and be exported."""
    content = FILE.read_text()
    assert re.search(r'\bgetGlobal\b', content), "getGlobal function not found"
    body = _extract_function_body(content, 'getGlobal')
    if body:
        assert re.search(r'return\s+yield\*|yield\s*\*', body), "getGlobal must yield a cached value"


def test_invalidate_disposes_instances():
    """invalidate must still call Instance.disposeAll."""
    content = FILE.read_text()
    assert 'Instance.disposeAll' in content, "Instance.disposeAll not found"


def test_load_global_exists():
    """loadGlobal function must still exist."""
    content = FILE.read_text()
    assert re.search(r'\bloadGlobal\b', content), "loadGlobal function not found"


# -----------------------------------------------------------------------------
# Pass-to-pass (agent_config)
# -----------------------------------------------------------------------------

def test_no_any_type_near_cache_code():
    """No 'any' type used near cache-related code."""
    content = FILE.read_text()
    lines = content.splitlines()
    keywords = {"cachedGlobal", "cachedInvalidateWithTTL", "invalidate", "loadGlobal"}
    for i, line in enumerate(lines):
        if any(kw in line for kw in keywords):
            region = lines[max(0, i - 5): i + 10]
            for l in region:
                stripped = re.sub(r'//.*', '', l)
                assert not re.search(r'\bas\s+any\b|:\s*any\s*[;,\s)]|:\s*any$', stripped), \
                    f"'any' type found: {l.strip()}"


def test_no_try_catch_in_changed_code():
    """No try/catch added near cache-related code."""
    content = FILE.read_text()
    lines = content.splitlines()
    keywords = {"cachedGlobal", "cachedInvalidateWithTTL"}
    for i, line in enumerate(lines):
        if any(kw in line for kw in keywords):
            region_text = "\n".join(lines[max(0, i - 10): i + 10])
            assert not re.search(r'\btry\s*\{', region_text), f"try/catch found at line {i + 1}"


def test_effect_fn_named_wrappers():
    """getGlobal and invalidate must use Effect.fn named wrappers."""
    content = FILE.read_text()
    stripped = _strip_comments(content)
    has_getglobal_fn = re.search(r'Effect\.fn\s*\(\s*["\'][^"\']*getGlobal["\']', stripped)
    assert has_getglobal_fn, "getGlobal must use Effect.fn('...')"
    has_invalidate_fn = re.search(r'Effect\.fn\s*\(\s*["\'][^"\']*invalidate["\']', stripped)
    assert has_invalidate_fn, "invalidate must use Effect.fn('...')"


def test_no_else_statements_near_cache_code():
    """No else statements near cache-related code."""
    content = FILE.read_text()
    lines = content.splitlines()
    keywords = {"cachedInvalidateWithTTL", "const [cachedGlobal"}
    for i, line in enumerate(lines):
        if any(kw in line for kw in keywords):
            region = lines[max(0, i - 5): i + 15]
            for l in region:
                stripped = re.sub(r'//.*', '', l)
                assert not re.search(r'\belse\b', stripped), f"'else' found: {l.strip()}"


# -----------------------------------------------------------------------------
# Pass-to-pass (static)
# -----------------------------------------------------------------------------

def test_not_stub():
    """config.ts must not be gutted."""
    content = FILE.read_text()
    lines = content.strip().splitlines()
    assert len(lines) >= 1000, f"Only {len(lines)} lines - file gutted"
    for req in ["loadGlobal", "getGlobal", "invalidate", "loadFile", "namespace Config"]:
        assert req in content, f"Missing: {req}"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests)
# -----------------------------------------------------------------------------

def test_repo_git_clean():
    """Repo must have clean working tree."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"git status failed: {r.stderr}"
    assert r.stdout.strip() == "", f"Uncommitted changes:\n{r.stdout}"


def test_repo_config_file_exists():
    """Config file must exist and be substantial."""
    assert FILE.exists(), f"Config file not found: {FILE}"
    size = FILE.stat().st_size
    assert size > 50000, f"Config file too small ({size} bytes)"


def test_repo_config_has_required_functions():
    """Config file must contain required functions."""
    content = FILE.read_text()
    for req in ["loadGlobal", "getGlobal", "invalidate", "namespace Config", "Effect"]:
        assert req in content, f"Missing: {req}"


def test_repo_commit_valid():
    """Repo must be at a valid commit."""
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0
    commit = r.stdout.strip()
    assert len(commit) == 40


def test_repo_config_valid_syntax():
    """Config file must have valid TypeScript structure."""
    content = FILE.read_text()
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert open_braces > 100
    assert abs(open_braces - close_braces) < 10
    backticks = content.count("`")
    assert backticks % 2 == 0


def test_repo_no_merge_conflicts():
    """Config file must not contain merge conflict markers."""
    content = FILE.read_text()
    for marker in ['<<<<<<<', '=======', '>>>>>>>']:
        assert marker not in content, f"Found merge conflict marker: {marker}"


def test_repo_config_imports_exports_valid():
    """Config file must have imports from 'effect'."""
    content = FILE.read_text()
    effect_imports = len(re.findall(r'from\s+["\']effect["\']', content))
    assert effect_imports > 0, "No imports from 'effect'"


def test_repo_config_no_obvious_formatting_issues():
    """Config file should not have obvious formatting issues."""
    content = FILE.read_text()
    assert '\r' not in content, 'Found carriage returns'
    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.lstrip()
        if stripped and not stripped.startswith('//'):
            indent = line[:len(line) - len(stripped)]
            if '\t' in indent:
                assert False, f'Tab at line {i}'


def test_repo_effect_namespace_intact():
    """Effect namespace structure must be preserved."""
    content = FILE.read_text()
    assert 'namespace Config' in content, 'Config namespace not found'
    for method in ['loadGlobal', 'getGlobal', 'invalidate', 'loadFile']:
        assert method in content, f'Missing: {method}'


def test_repo_config_balanced_parens():
    """Config file must have balanced parentheses."""
    content = FILE.read_text()
    cleaned = re.sub(r'".*?"', '""', content)
    cleaned = re.sub(r"'.*?'", "''", cleaned)
    cleaned = re.sub(r"`.*?`", "``", cleaned, flags=re.DOTALL)
    assert cleaned.count('(') == cleaned.count(')')


def test_repo_config_balanced_brackets():
    """Config file must have balanced square brackets."""
    content = FILE.read_text()
    cleaned = re.sub(r'".*?"', '""', content)
    cleaned = re.sub(r"'.*?'", "''", cleaned)
    cleaned = re.sub(r"`.*?`", "``", cleaned, flags=re.DOTALL)
    assert abs(cleaned.count('[') - cleaned.count(']')) < 5


def test_repo_prettier_formatting():
    """Config file passes Prettier formatting check."""
    r = subprocess.run(
        ["npx", "prettier", "--check", str(FILE)],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier failed: {r.stderr[-500:]}"
