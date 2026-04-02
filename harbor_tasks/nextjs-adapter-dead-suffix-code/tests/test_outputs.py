"""
Task: nextjs-adapter-dead-suffix-code
Repo: vercel/next.js @ 904501127c9ed2e0a7ffd51bd192537b7c398fb3
PR:   #91997

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/repo"
BUILD_COMPLETE = Path(REPO) / "packages/next/src/build/adapter/build-complete.ts"
BUILD_INDEX = Path(REPO) / "packages/next/src/build/index.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax / anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_syntax():
    """Modified files must parse without TypeScript syntax errors."""
    import subprocess

    # process.argv[0]=node, process.argv[1]='[eval]', process.argv[2+]=our args
    script = (
        "const fs = require('fs');"
        "const ts = require('typescript');"
        "for (const f of process.argv.slice(2)) {"
        "  const src = fs.readFileSync(f, 'utf8');"
        "  ts.createSourceFile(f, src, ts.ScriptTarget.Latest, true);"
        "}"
        "console.log('syntax ok');"
    )
    r = subprocess.run(
        ["node", "-e", script, str(BUILD_COMPLETE), str(BUILD_INDEX)],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"TypeScript syntax error:\n{r.stderr.decode()}"


# [static] pass_to_pass
def test_files_not_stubbed():
    """build-complete.ts is ~2200 lines; a stub is not a valid fix."""
    bc_lines = BUILD_COMPLETE.read_text().splitlines()
    bi_lines = BUILD_INDEX.read_text().splitlines()
    assert len(bc_lines) >= 1500, f"build-complete.ts too short ({len(bc_lines)} lines), looks like a stub"
    assert len(bi_lines) >= 300, f"index.ts too short ({len(bi_lines)} lines), looks like a stub"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- dead code removal checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_has_fallback_root_params_in_build_complete():
    """hasFallbackRootParams destructuring must be removed from build-complete.ts."""
    src = BUILD_COMPLETE.read_text()
    assert "hasFallbackRootParams" not in src, (
        "hasFallbackRootParams is still referenced in build-complete.ts"
    )


# [pr_diff] fail_to_pass
def test_no_should_skip_suffixes():
    """shouldSkipSuffixes variable must be removed from build-complete.ts."""
    src = BUILD_COMPLETE.read_text()
    assert "shouldSkipSuffixes" not in src, (
        "shouldSkipSuffixes is still referenced in build-complete.ts"
    )


# [pr_diff] fail_to_pass
def test_no_dead_ternary_around_rsc_suffix():
    """The ternary with identical branches around rscSuffix regex must be removed."""
    src = BUILD_COMPLETE.read_text()
    # rscSuffix must still exist (pattern itself is not dead)
    assert "rscSuffix" in src, "rscSuffix regex pattern is missing entirely"
    # The dead ternary duplicated the rscSuffix pattern on two branches.
    # Base has 3 occurrences: ternary true-branch + false-branch + destination replace.
    # After fix: 2 occurrences: one pattern + one destination replace.
    # NOTE: can't use "?" + ":" heuristic — the fixed regex (?<rscSuffix>...)(?:/)?$
    # itself contains both characters via the (?:/) non-capturing group.
    count = src.count("rscSuffix")
    assert count <= 2, (
        f"rscSuffix appears {count} times — dead ternary likely still duplicates it (expected ≤2)"
    )


# [pr_diff] fail_to_pass
def test_no_has_fallback_root_params_in_manifest_type():
    """hasFallbackRootParams must be removed from ManifestRoute type in index.ts."""
    src = BUILD_INDEX.read_text()
    assert "hasFallbackRootParams" not in src, (
        "hasFallbackRootParams still in ManifestRoute type definition"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) -- regression / code integrity
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_handle_build_complete_export_preserved():
    """The handleBuildComplete async function must still be exported."""
    src = BUILD_COMPLETE.read_text()
    assert "export async function handleBuildComplete" in src, (
        "handleBuildComplete export is missing"
    )


# [pr_diff] pass_to_pass
def test_manifest_route_type_exported():
    """ManifestRoute type must still be exported from index.ts."""
    src = BUILD_INDEX.read_text()
    assert "export type ManifestRoute" in src, "ManifestRoute type export is missing"


# [pr_diff] pass_to_pass
def test_rsc_suffix_regex_preserved():
    """The rscSuffix named capture regex must still be present."""
    src = BUILD_COMPLETE.read_text()
    assert "rscSuffix" in src, "rscSuffix regex pattern is missing"
    # The actual regex string must be intact
    assert ".segment.rsc" in src, "RSC suffix regex string is altered or missing"


# [pr_diff] pass_to_pass
def test_source_regex_replace_preserved():
    """sourceRegex.replace call must still be present (core rewrite logic)."""
    src = BUILD_COMPLETE.read_text()
    assert "sourceRegex.replace" in src, "sourceRegex.replace call is missing"


# [pr_diff] pass_to_pass
def test_surrounding_code_intact():
    """Key patterns from the surrounding code must still exist (anti-gutting)."""
    bc = BUILD_COMPLETE.read_text()
    bi = BUILD_INDEX.read_text()
    checks = {
        "dynamicRoutes in build-complete": "dynamicRoutes" in bc,
        "prerenderManifest in build-complete": "prerenderManifest" in bc,
        "handleBuildComplete function in build-complete": "function handleBuildComplete" in bc,
        "ManifestBuiltRoute in index": "ManifestBuiltRoute" in bi,
    }
    failed = [k for k, v in checks.items() if not v]
    assert not failed, f"Surrounding code damaged -- missing: {', '.join(failed)}"
