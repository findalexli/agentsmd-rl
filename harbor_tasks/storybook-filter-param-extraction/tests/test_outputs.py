"""
Task: storybook-filter-param-extraction
Repo: storybook @ 95aa11484a255b1c7f6227f2c81e2d441bb28988
PR:   34436

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/storybook"


def _run_tsx(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a temp .mts file in the repo and run it with tsx."""
    tmp = Path(REPO) / "_test_runner_tmp.mts"
    tmp.write_text(script)
    try:
        return subprocess.run(
            ["tsx", str(tmp)],
            cwd=REPO,
            capture_output=True,
            timeout=timeout,
        )
    finally:
        tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — existing repo test for tags module
def test_repo_tags_module():
    """Repo's tags module functionality works (pass_to_pass)."""
    script = textwrap.dedent("""\
        import { parseTagsParam, serializeTagsParam } from './code/core/src/manager-api/modules/tags.ts';

        // Test parseTagsParam
        const r1 = parseTagsParam(undefined);
        if (JSON.stringify(r1) !== JSON.stringify({ included: [], excluded: [] })) {
          throw new Error('parseTagsParam(undefined) failed: ' + JSON.stringify(r1));
        }

        const r2 = parseTagsParam('');
        if (JSON.stringify(r2) !== JSON.stringify({ included: [], excluded: [] })) {
          throw new Error("parseTagsParam('') failed: " + JSON.stringify(r2));
        }

        const r3 = parseTagsParam('a;!b');
        if (JSON.stringify(r3) !== JSON.stringify({ included: ['a'], excluded: ['b'] })) {
          throw new Error("parseTagsParam('a;!b') failed: " + JSON.stringify(r3));
        }

        const r4 = parseTagsParam('a;;!b;;;');
        if (JSON.stringify(r4) !== JSON.stringify({ included: ['a'], excluded: ['b'] })) {
          throw new Error("parseTagsParam('a;;!b;;;') failed: " + JSON.stringify(r4));
        }

        // Test serializeTagsParam
        const s1 = serializeTagsParam([], []);
        if (s1 !== '') {
          throw new Error('serializeTagsParam([], []) failed: ' + s1);
        }

        console.log('All tags tests passed');
    """)
    r = _run_tsx(script, timeout=30)
    assert r.returncode == 0, f"Repo tags test failed:\n{r.stderr.decode()[-500:]}"


# [repo_tests] pass_to_pass — TypeScript files are syntactically valid
def test_repo_typescript_syntax():
    """Modified TypeScript files parse without errors (pass_to_pass)."""
    import re

    files = [
        "code/core/src/manager-api/modules/tags.ts",
        "code/core/src/manager-api/modules/statuses.ts",
    ]

    for f in files:
        fp = Path(REPO) / f
        content = fp.read_text()
        # Basic syntax checks: balanced braces and valid import statements
        opens = content.count("{")
        closes = content.count("}")
        assert abs(opens - closes) <= 2, f"{f} has unbalanced braces"
        # Check for valid TypeScript structure (no unmatched parentheses)
        open_parens = content.count("(")
        close_parens = content.count(")")
        assert abs(open_parens - close_parens) <= 2, f"{f} has unbalanced parentheses"
        # Check for import statements
        assert re.search(r"import\s+.*\s+from\s+['\"]", content), f"{f} missing import statements"


# [static] pass_to_pass
def test_syntax_check():
    """Modified files must exist and have valid TypeScript structure."""
    files = [
        "code/core/src/manager-api/modules/statuses.ts",
        "code/core/src/manager-api/modules/tags.ts",
    ]
    for f in files:
        fp = Path(REPO) / f
        assert fp.exists(), f"{f} does not exist"
        content = fp.read_text()
        assert len(content) > 50, f"{f} appears to be empty or too short"
        opens = content.count("{")
        closes = content.count("}")
        assert abs(opens - closes) <= 2, (
            f"{f} has unbalanced braces ({opens} open, {closes} close)"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_filter_param_basic_inclusion():
    """parseFilterParam splits semicolons and sorts into included array."""
    script = textwrap.dedent("""\
        import assert from 'node:assert';
        import { parseFilterParam } from './code/core/src/manager-api/lib/filter-param.ts';

        // Test with identity transform and multiple values
        const r1 = parseFilterParam('alpha;beta;gamma', (x) => x);
        assert.deepStrictEqual(r1, { included: ['alpha', 'beta', 'gamma'], excluded: [] });

        // Test with different values to prevent hardcoding
        const r2 = parseFilterParam('x;y', (x) => x);
        assert.deepStrictEqual(r2, { included: ['x', 'y'], excluded: [] });

        // Single value
        const r3 = parseFilterParam('solo', (x) => x);
        assert.deepStrictEqual(r3, { included: ['solo'], excluded: [] });
    """)
    r = _run_tsx(script)
    assert r.returncode == 0, f"Failed:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_filter_param_exclusion_handling():
    """parseFilterParam routes !-prefixed items to excluded array, strips the prefix."""
    script = textwrap.dedent("""\
        import assert from 'node:assert';
        import { parseFilterParam } from './code/core/src/manager-api/lib/filter-param.ts';

        // Mixed inclusion and exclusion
        const r1 = parseFilterParam('keep;!drop;also', (x) => x);
        assert.deepStrictEqual(r1, { included: ['keep', 'also'], excluded: ['drop'] });

        // All excluded
        const r2 = parseFilterParam('!a;!b;!c', (x) => x);
        assert.deepStrictEqual(r2, { included: [], excluded: ['a', 'b', 'c'] });

        // Single exclusion
        const r3 = parseFilterParam('!only', (x) => x);
        assert.deepStrictEqual(r3, { included: [], excluded: ['only'] });
    """)
    r = _run_tsx(script)
    assert r.returncode == 0, f"Failed:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_filter_param_transform_and_null_skip():
    """parseFilterParam applies transform and skips null/undefined results."""
    script = textwrap.dedent("""\
        import assert from 'node:assert';
        import { parseFilterParam } from './code/core/src/manager-api/lib/filter-param.ts';

        // Transform uppercases values
        const r1 = parseFilterParam('foo;!bar', (x) => x.toUpperCase());
        assert.deepStrictEqual(r1, { included: ['FOO'], excluded: ['BAR'] });

        // Transform returns null to skip unknown values
        const lookup: Record<string, string> = { a: 'A', c: 'C' };
        const r2 = parseFilterParam('a;b;c', (x) => lookup[x] ?? null);
        assert.deepStrictEqual(r2, { included: ['A', 'C'], excluded: [] });

        // Transform returns undefined to skip
        const r3 = parseFilterParam('x;!y;z', (x) => x === 'y' ? undefined : x);
        assert.deepStrictEqual(r3, { included: ['x', 'z'], excluded: [] });
    """)
    r = _run_tsx(script)
    assert r.returncode == 0, f"Failed:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_filter_param_empty_and_edge_cases():
    """parseFilterParam handles empty/undefined input and trailing semicolons."""
    script = textwrap.dedent("""\
        import assert from 'node:assert';
        import { parseFilterParam } from './code/core/src/manager-api/lib/filter-param.ts';

        // undefined input
        const r1 = parseFilterParam(undefined, (x) => x);
        assert.deepStrictEqual(r1, { included: [], excluded: [] });

        // empty string
        const r2 = parseFilterParam('', (x) => x);
        assert.deepStrictEqual(r2, { included: [], excluded: [] });

        // trailing and repeated semicolons
        const r3 = parseFilterParam('a;;b;', (x) => x);
        assert.deepStrictEqual(r3, { included: ['a', 'b'], excluded: [] });

        // only semicolons
        const r4 = parseFilterParam(';;;', (x) => x);
        assert.deepStrictEqual(r4, { included: [], excluded: [] });
    """)
    r = _run_tsx(script)
    assert r.returncode == 0, f"Failed:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — refactoring integration checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_tags_uses_shared_helper():
    """tags.ts must import parseFilterParam and remove inline parsing logic."""
    import re
    fp = Path(REPO) / "code/core/src/manager-api/modules/tags.ts"
    content = fp.read_text()

    # Must import the shared helper
    assert re.search(r"import\s*\{[^}]*parseFilterParam[^}]*\}", content), (
        "tags.ts must import parseFilterParam from the shared module"
    )

    # Inline parsing logic (split+forEach pattern) must be removed
    assert "split(';').forEach" not in content, (
        "tags.ts still has inline split(';').forEach — "
        "should delegate to shared parseFilterParam"
    )


# [pr_diff] fail_to_pass
def test_statuses_uses_shared_helper():
    """statuses.ts must import parseFilterParam and remove inline parsing logic."""
    import re
    fp = Path(REPO) / "code/core/src/manager-api/modules/statuses.ts"
    content = fp.read_text()

    # Must import the shared helper
    assert re.search(r"import\s*\{[^}]*parseFilterParam[^}]*\}", content), (
        "statuses.ts must import parseFilterParam from the shared module"
    )

    # Inline parsing logic (split+forEach pattern) must be removed
    assert "split(';').forEach" not in content, (
        "statuses.ts still has inline split(';').forEach — "
        "should delegate to shared parseFilterParam"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:244-250 @ 95aa11484a255b1c7f6227f2c81e2d441bb28988
def test_no_raw_console():
    """Modified files must not use raw console.log/warn/error (AGENTS.md rule)."""
    import re

    files_to_check = [
        "code/core/src/manager-api/lib/filter-param.ts",
        "code/core/src/manager-api/modules/statuses.ts",
        "code/core/src/manager-api/modules/tags.ts",
    ]

    console_re = re.compile(r"\bconsole\.(log|warn|error|info|debug)\b")

    for f in files_to_check:
        fp = Path(REPO) / f
        if not fp.exists():
            continue
        content = fp.read_text()
        matches = console_re.findall(content)
        assert not matches, (
            f"Found raw console.{matches[0]} in {f} — "
            f"use Storybook loggers instead (AGENTS.md:244-250)"
        )


# [agent_config] pass_to_pass — AGENTS.md:246 @ 95aa11484a255b1c7f6227f2c81e2d441bb28988
def test_explicit_ts_import_extensions():
    """New/modified files use explicit .ts extensions for relative imports (AGENTS.md rule)."""
    import re

    files_to_check = [
        "code/core/src/manager-api/lib/filter-param.ts",
        "code/core/src/manager-api/modules/statuses.ts",
        "code/core/src/manager-api/modules/tags.ts",
    ]

    # Pattern: from './...' or from '../...' without .ts/.tsx extension
    # Matches relative imports that end without a file extension
    missing_ext = re.compile(
        r"""from\s+['"](\.\./?\S+?)['"]"""
    )

    for f in files_to_check:
        fp = Path(REPO) / f
        if not fp.exists():
            continue
        content = fp.read_text()
        for m in missing_ext.finditer(content):
            import_path = m.group(1)
            # Skip non-relative imports
            if not import_path.startswith("."):
                continue
            # Must end with .ts, .tsx, .js, .jsx, or .mts etc.
            assert re.search(r"\.\w+$", import_path), (
                f"Import '{import_path}' in {f} lacks explicit file extension "
                f"(AGENTS.md requires explicit .ts/.tsx extensions for relative imports)"
            )
