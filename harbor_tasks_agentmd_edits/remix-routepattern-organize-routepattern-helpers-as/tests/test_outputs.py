"""
Task: remix-routepattern-organize-routepattern-helpers-as
Repo: remix-run/remix @ 77567b453e4de0b2706cc9fa68c8f5d14e5361b3
PR:   11026

Refactor: reorganize route-pattern helpers as PartPattern methods or by feature,
replace namespace imports with named imports, and add AGENTS.md documenting the
new directory organization.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/remix"
RP_DIR = Path(REPO) / "packages/route-pattern/src/lib/route-pattern"
RP_LIB = Path(REPO) / "packages/route-pattern/src/lib"

NODE_FLAGS = ["node", "--experimental-strip-types", "--no-warnings"]


def _run_node_esm(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run an ESM TypeScript snippet via a temp .mts file."""
    tmp = Path(REPO) / "__pytest_verify.mts"
    try:
        tmp.write_text(script)
        return subprocess.run(
            NODE_FLAGS + [str(tmp)],
            cwd=REPO, capture_output=True, timeout=timeout,
        )
    finally:
        tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_files_valid():
    """Key route-pattern TypeScript files exist and are non-empty."""
    required = [
        RP_DIR / "part-pattern.ts",
        RP_DIR / "href.ts",
        RP_DIR / "join.ts",
        RP_DIR / "parse.ts",
        RP_DIR / "split.ts",
        RP_LIB / "route-pattern.ts",
    ]
    for f in required:
        assert f.exists(), f"Missing file: {f}"
        assert f.stat().st_size > 0, f"Empty file: {f}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core refactoring behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_part_pattern_source_getter():
    """PartPattern.source getter reconstructs pattern string from tokens."""
    r = _run_node_esm(
        "import { PartPattern } from './packages/route-pattern/src/lib/route-pattern/part-pattern.ts'\n"
        "let p = PartPattern.parse('users/:id/posts', { span: [0, 17], type: 'pathname', ignoreCase: false })\n"
        "let desc = Object.getOwnPropertyDescriptor(PartPattern.prototype, 'source')\n"
        "if (!desc || typeof desc.get !== 'function') {\n"
        "  console.error('source is not a getter on PartPattern.prototype')\n"
        "  process.exit(1)\n"
        "}\n"
        "if (p.source !== 'users/:id/posts') {\n"
        "  console.error('Expected users/:id/posts, got:', p.source)\n"
        "  process.exit(1)\n"
        "}\n"
    )
    assert r.returncode == 0, (
        f"PartPattern.source getter failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_part_pattern_href_method():
    """PartPattern.href() generates URL path segments from params."""
    r = _run_node_esm(
        "import { RoutePattern } from './packages/route-pattern/src/lib/route-pattern.ts'\n"
        "let pattern = new RoutePattern('users/:id')\n"
        "let pp = pattern.ast.pathname\n"
        "if (typeof pp.href !== 'function') {\n"
        "  console.error('href is not a method on PartPattern')\n"
        "  process.exit(1)\n"
        "}\n"
        "let result = pp.href(pattern, { id: '42' })\n"
        "if (result !== 'users/42') {\n"
        "  console.error('Expected users/42, got:', result)\n"
        "  process.exit(1)\n"
        "}\n"
        "// Also test with optional segment\n"
        "let opt = new RoutePattern('api(/v:version)/users')\n"
        "let r2 = opt.ast.pathname.href(opt, { version: '3' })\n"
        "if (r2 !== 'api/v3/users') {\n"
        "  console.error('Expected api/v3/users, got:', r2)\n"
        "  process.exit(1)\n"
        "}\n"
    )
    assert r.returncode == 0, (
        f"PartPattern.href() failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_serialize_search_function():
    """serialize.ts exports serializeSearch that converts constraints to query string."""
    r = _run_node_esm(
        "import { serializeSearch } from './packages/route-pattern/src/lib/route-pattern/serialize.ts'\n"
        "if (typeof serializeSearch !== 'function') {\n"
        "  console.error('serializeSearch is not a function')\n"
        "  process.exit(1)\n"
        "}\n"
        "let result = serializeSearch(new Map([['q', new Set(['hello'])]]))\n"
        "if (result !== 'q=hello') {\n"
        "  console.error('Expected q=hello, got:', result)\n"
        "  process.exit(1)\n"
        "}\n"
        "let empty = serializeSearch(new Map())\n"
        "if (empty !== undefined) {\n"
        "  console.error('Expected undefined for empty map, got:', empty)\n"
        "  process.exit(1)\n"
        "}\n"
        "let nullConstraint = serializeSearch(new Map([['tag', null]]))\n"
        "if (nullConstraint !== 'tag') {\n"
        "  console.error('Expected tag, got:', nullConstraint)\n"
        "  process.exit(1)\n"
        "}\n"
    )
    assert r.returncode == 0, (
        f"serializeSearch failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_match_search_function():
    """match.ts exports matchSearch that tests URL params against constraints."""
    r = _run_node_esm(
        "import { matchSearch } from './packages/route-pattern/src/lib/route-pattern/match.ts'\n"
        "if (typeof matchSearch !== 'function') {\n"
        "  console.error('matchSearch is not a function')\n"
        "  process.exit(1)\n"
        "}\n"
        "let params = new URLSearchParams('q=hello')\n"
        "let constraints = new Map([['q', new Set(['hello'])]])\n"
        "if (!matchSearch(params, constraints, false)) {\n"
        "  console.error('Expected match to succeed')\n"
        "  process.exit(1)\n"
        "}\n"
        "let noMatch = new URLSearchParams('q=world')\n"
        "if (matchSearch(noMatch, constraints, false)) {\n"
        "  console.error('Expected match to fail for wrong value')\n"
        "  process.exit(1)\n"
        "}\n"
    )
    assert r.returncode == 0, (
        f"matchSearch failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_named_imports_replace_namespace():
    """route-pattern.ts uses named imports, not namespace imports (import * as)."""
    content = (RP_LIB / "route-pattern.ts").read_text()
    assert "import * as" not in content, (
        "route-pattern.ts still uses namespace imports (import * as). "
        "Replace with named imports for autocomplete-ability and consistency."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — upstream regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_upstream_route_pattern_tests():
    """Upstream route-pattern test suite passes."""
    r = subprocess.run(
        NODE_FLAGS + [
            "--test",
            "packages/route-pattern/src/lib/route-pattern.test.ts",
            "packages/route-pattern/src/lib/route-pattern/part-pattern.test.ts",
        ],
        cwd=REPO, capture_output=True, timeout=60,
    )
    assert r.returncode == 0, (
        f"Upstream tests failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Config edit — AGENTS.md documents directory organization
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must reference part-pattern.ts as the home for PartPattern-specific logic
    assert "part-pattern" in content_lower, (
        "AGENTS.md should reference part-pattern.ts as containing PartPattern logic"
    )

    # Must list feature-organized modules (at least 3 of: href, join, match, parse, serialize, split)
    feature_files = ["href", "join", "match", "parse", "serialize", "split"]
    found = [f for f in feature_files if f in content_lower]
    assert len(found) >= 3, (
        f"AGENTS.md should list feature-organized modules (found {len(found)}: {found})"
    )

    # Must convey the organizational principle (feature-based, not pattern-part-based)
    assert any(kw in content_lower for kw in ["feature", "organiz"]), (
        "AGENTS.md should describe the organizational principle (by feature)"
    )
