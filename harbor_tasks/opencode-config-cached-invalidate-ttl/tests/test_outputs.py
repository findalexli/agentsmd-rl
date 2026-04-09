"""
Task: opencode-config-cached-invalidate-ttl
Repo: anomalyco/opencode @ 9f94bdb49634bda90a2804585b8d739228dde876
PR:   #19322

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess, json, re
from pathlib import Path

FILE = Path("/repo/packages/opencode/src/config/config.ts")
REPO = "/repo"

# ---------------------------------------------------------------------------
# Node.js analysis helper — brace-matching + cross-reference validation
# ---------------------------------------------------------------------------

_analysis_cache = None

ANALYSIS_SCRIPT = r"""
const fs = require('fs');
const content = fs.readFileSync('packages/opencode/src/config/config.ts', 'utf8');

// Strip single-line comments (not :// in URLs) and multi-line comments
const stripped = content
  .replace(/(?<![:\/"'\\])\/\/[^\n]*/g, '')
  .replace(/\/\*[\s\S]*?\*\//g, '');

const results = {};

// 1. Check cachedInvalidateWithTTL with const destructuring
const dm = stripped.match(/const\s+\[(\w+)\s*,\s*(\w+)\]\s*=\s*yield\*\s+Effect\.cachedInvalidateWithTTL/);
results.hasDestructuredCache = !!dm;
results.handleName = dm ? dm[2] : null;
results.hasLetCachedGlobal = /\blet\s+cachedGlobal\b/.test(stripped);

// 2. Extract invalidate function body via brace-depth counting
const invIdx = stripped.indexOf('const invalidate = Effect.fn');
if (invIdx >= 0) {
  const fnIdx = stripped.indexOf('function*', invIdx);
  if (fnIdx >= 0) {
    const bIdx = stripped.indexOf('{', fnIdx);
    if (bIdx >= 0) {
      let d = 1, p = bIdx + 1;
      while (p < stripped.length && d > 0) {
        if (stripped[p] === '{') d++;
        if (stripped[p] === '}') d--;
        p++;
      }
      const body = stripped.slice(bIdx + 1, p - 1);
      results.foundInvalidateBody = true;
      results.invRecreatesCache = body.includes('Effect.cached(');
      results.invReassigns = /cachedGlobal\s*=\s*yield/.test(body);
      results.invHasYield = /yield\s*\*/.test(body);
      // Cross-reference: handle name from cache init is used in invalidate
      if (results.handleName) {
        results.invUsesHandle = new RegExp('yield\\s*\\*\\s*' + results.handleName + '\\b').test(body);
      } else {
        results.invUsesHandle = false;
      }
    }
  }
}
if (!results.foundInvalidateBody) results.foundInvalidateBody = false;

// 3. Extract cachedInvalidateWithTTL call region via paren-depth counting
const ciIdx = stripped.indexOf('cachedInvalidateWithTTL');
if (ciIdx >= 0) {
  let pi = stripped.indexOf('(', ciIdx), d = 1, p = pi + 1;
  while (p < stripped.length && d > 0) {
    if (stripped[p] === '(') d++;
    if (stripped[p] === ')') d--;
    p++;
  }
  const region = stripped.slice(ciIdx, p);
  results.hasTapError = region.includes('tapError');
  const tei = region.indexOf('tapError'), oei = region.indexOf('orElseSucceed');
  results.tapErrorBeforeOrElse = tei >= 0 && oei >= 0 && tei < oei;
  results.hasDurationArg = /Duration\.\w+/.test(region);
} else {
  results.hasTapError = false;
  results.tapErrorBeforeOrElse = false;
  results.hasDurationArg = false;
}

// 4. Duration import
results.hasDurationImport = /import\s*\{[^}]*\bDuration\b[^}]*\}\s*from\s*["']effect["']/.test(stripped);

console.log(JSON.stringify(results));
"""


def _get_analysis():
    """Run Node.js analysis script (brace-matching + cross-ref) and cache result."""
    global _analysis_cache
    if _analysis_cache is not None:
        return _analysis_cache
    script = Path(REPO) / "_eval_analysis.cjs"
    script.write_text(ANALYSIS_SCRIPT)
    try:
        r = subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Analysis script failed: {r.stderr}"
        _analysis_cache = json.loads(r.stdout.strip())
        return _analysis_cache
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via Node.js subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cache_uses_cached_invalidate_with_ttl():
    """Cache must use Effect.cachedInvalidateWithTTL with const destructured binding."""
    a = _get_analysis()
    assert a["hasDestructuredCache"], (
        "No const [value, handle] = yield* Effect.cachedInvalidateWithTTL pattern found"
    )
    assert not a["hasLetCachedGlobal"], (
        "let cachedGlobal still exists — must use const destructuring"
    )


# [pr_diff] fail_to_pass
def test_invalidate_uses_handle_not_cache_recreation():
    """invalidate() must yield the invalidation handle, not recreate the cache."""
    a = _get_analysis()
    assert a["foundInvalidateBody"], "Could not find invalidate function body"
    assert not a["invRecreatesCache"], "invalidate still recreates cache with Effect.cached()"
    assert not a["invReassigns"], "invalidate still reassigns cachedGlobal"
    assert a["invHasYield"], "invalidate has no yield statement"
    assert a["invUsesHandle"], (
        "invalidate does not yield the handle destructured from cachedInvalidateWithTTL"
    )


# [pr_diff] fail_to_pass
def test_error_logging_before_fallback():
    """Errors during global config loading must be logged before falling back to defaults."""
    a = _get_analysis()
    assert a["hasTapError"], "No tapError in cachedInvalidateWithTTL pipe chain"
    assert a["tapErrorBeforeOrElse"], "tapError must come before orElseSucceed in pipe chain"


# [pr_diff] fail_to_pass
def test_duration_imported_and_used_as_ttl():
    """Duration must be imported from 'effect' and used as TTL argument."""
    a = _get_analysis()
    assert a["hasDurationImport"], "Duration not imported from 'effect'"
    assert a["hasDurationArg"], "Duration.* not used as argument to cachedInvalidateWithTTL"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:70 @ 9f94bdb
def test_const_over_let_for_cache():
    """Cache binding must use const, not let (AGENTS.md: 'Prefer const over let')."""
    a = _get_analysis()
    assert not a["hasLetCachedGlobal"], (
        "let cachedGlobal still present — AGENTS.md requires const over let"
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
    assert "Instance.disposeAll" in content, "Instance.disposeAll not found"


# [pr_diff] pass_to_pass
def test_load_global_exists():
    """loadGlobal function must still exist."""
    content = FILE.read_text()
    assert re.search(r"(const|function)\s+loadGlobal\b", content), "loadGlobal function not found"


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config)
# ---------------------------------------------------------------------------

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
            region_text = "\n".join(lines[max(0, i - 10) : i + 10])
            assert not re.search(r"\btry\s*\{", region_text), (
                f"try/catch found near cache code at line {i + 1}"
            )


# [agent_config] pass_to_pass — packages/opencode/AGENTS.md:21 @ 9f94bdb
def test_effect_fn_domain_naming_retained():
    """getGlobal and invalidate must retain Effect.fn('Config.*') named/traced wrappers."""
    content = FILE.read_text()
    code = re.sub(r'(?<![:"\x27\\])//[^\n]*', "", content)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    assert re.search(r'Effect\.fn\(["\'\']Config\.getGlobal["\'\']', code), (
        "Effect.fn(\"Config.getGlobal\") not found"
    )
    assert re.search(r'Effect\.fn\(["\'\']Config\.invalidate["\'\']', code), (
        "Effect.fn(\"Config.invalidate\") not found"
    )


# [agent_config] pass_to_pass — AGENTS.md:84 @ 9f94bdb
def test_no_else_statements_near_cache_code():
    """No else statements near cache-related code (AGENTS.md: 'Prefer early returns').

    Only checks near cache *definition* code (cachedInvalidateWithTTL/cachedGlobal),
    not near where the invalidation handle is used (which may be near pre-existing else).
    """
    lines = FILE.read_text().splitlines()
    # Only check near cache initialization code, not near invalidate handle usage
    keywords = {"cachedInvalidateWithTTL", "const [cachedGlobal"}
    for i, line in enumerate(lines):
        if any(kw in line for kw in keywords):
            region = lines[max(0, i - 5) : i + 15]
            for l in region:
                stripped = re.sub(r"//.*", "", l)
                assert not re.search(r"\belse\b", stripped), (
                    f"'else' statement found near cache code: {l.strip()}"
                )

# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """config.ts must not be gutted — must retain original structure."""
    content = FILE.read_text()
    lines = content.strip().splitlines()
    assert len(lines) >= 1000, f"Only {len(lines)} lines — file appears gutted"
    for req in ["loadGlobal", "getGlobal", "invalidate", "loadFile", "namespace Config"]:
        assert req in content, f"Missing required identifier: {req}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD integrity verification gates
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — repo integrity
def test_repo_git_clean():
    """Repo must have clean working tree (no uncommitted changes) (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"git status failed: {r.stderr}"
    assert r.stdout.strip() == "", f"Repo has uncommitted changes:\n{r.stdout}"


# [repo_tests] pass_to_pass — file existence
def test_repo_config_file_exists():
    """Config file must exist and be substantial (pass_to_pass)."""
    assert FILE.exists(), f"Config file not found: {FILE}"
    size = FILE.stat().st_size
    assert size > 50000, f"Config file too small ({size} bytes)"


# [repo_tests] pass_to_pass — required functions exist
def test_repo_config_has_required_functions():
    """Config file must contain required functions (pass_to_pass)."""
    content = FILE.read_text()
    required = ["loadGlobal", "getGlobal", "invalidate", "namespace Config",
                "Effect", "cachedGlobal"]
    for req in required:
        assert req in content, f"Missing required identifier: {req}"


# [repo_tests] pass_to_pass — git commit verification
def test_repo_commit_correct():
    """Repo must be at a valid commit with expected structure (pass_to_pass)."""
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"git rev-parse failed: {r.stderr}"
    commit = r.stdout.strip()
    # Verify it's a valid 40-char SHA
    assert len(commit) == 40, f"Invalid commit hash: {commit}"
    assert all(c in "0123456789abcdef" for c in commit), f"Invalid commit hash format: {commit}"


# [repo_tests] pass_to_pass — no obvious syntax errors
def test_repo_config_valid_syntax():
    """Config file must be valid TypeScript (no obvious syntax errors) (pass_to_pass)."""
    content = FILE.read_text()
    # Basic syntax checks
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert open_braces > 100, f"Too few braces - file may be corrupted"
    # Braces should be roughly balanced (allowing for strings/regexes)
    assert abs(open_braces - close_braces) < 10, f"Brace mismatch: {open_braces} vs {close_braces}"
    # Check for unclosed template literals
    backticks = content.count("`")
    assert backticks % 2 == 0, f"Unclosed template literals (odd number of backticks: {backticks})"
    # Check for basic TypeScript keywords
    keywords = ["import", "export", "const", "function", "class", "interface"]
    assert any(kw in content for kw in keywords), "Missing basic TypeScript keywords"
