"""
Task: remix-refactor-route-pattern-helpers
Repo: remix-run/remix @ 77567b453e4de0b2706cc9fa68c8f5d14e5361b3
PR:   11026

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = Path("/workspace/remix")
PKG = REPO / "packages" / "route-pattern" / "src" / "lib" / "route-pattern"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """TypeScript files in route-pattern parse without errors."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--pretty"],
        cwd=str(REPO / "packages" / "route-pattern"),
        capture_output=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"TypeScript errors:\n{result.stdout.decode()}\n{result.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_part_pattern_source_getter():
    """PartPattern instances have a `source` getter that returns the original pattern string."""
    result = subprocess.run(
        [
            "node", "--input-type=module", "-e",
            """
import { RoutePattern } from './packages/route-pattern/src/lib/route-pattern.ts';

let p1 = new RoutePattern('/users/:id');
console.log('pathname=' + p1.pathname);
console.log('hostname=' + JSON.stringify(p1.hostname));

let p2 = new RoutePattern('https://:sub.example.com/blog/:slug');
console.log('hostname2=' + p2.hostname);
console.log('pathname2=' + p2.pathname);

// Verify source round-trips
let p3 = new RoutePattern('/a/:x/:y');
console.log('source=' + p3.pathname);

let p4 = new RoutePattern('/files/:dir/*');
console.log('source4=' + p4.pathname);
""",
        ],
        capture_output=True,
        timeout=30,
        cwd=str(REPO),
    )
    assert result.returncode == 0, f"Node failed:\n{result.stderr.decode()}"
    out = result.stdout.decode()
    assert "pathname=/users/:id" in out, f"Expected pathname=/users/:id, got: {out}"
    assert 'hostname=""' in out or "hostname=" in out, f"Hostname missing: {out}"
    assert "hostname2=" in out, f"hostname2 missing: {out}"
    assert "pathname2=/blog/:slug" in out, f"Expected pathname2=/blog/:slug, got: {out}"
    assert "source=/a/:x/:y" in out, f"Expected source=/a/:x/:y, got: {out}"
    assert "source4=/files/:dir/*" in out, f"Expected source4=/files/:dir/*, got: {out}"


# [repo_tests] pass_to_pass
def test_href_with_params():
    """RoutePattern.href works correctly substituting params into patterns."""
    result = subprocess.run(
        [
            "node", "--input-type=module", "-e",
            """
import { RoutePattern } from './packages/route-pattern/src/lib/route-pattern.ts';

let p1 = new RoutePattern('/users/:id');
console.log('href1=' + p1.href({ id: '42' }));

let p2 = new RoutePattern('/posts/:slug/comments/:cid');
console.log('href2=' + p2.href({ slug: 'hello', cid: '7' }));

let p3 = new RoutePattern('/static/page');
console.log('href3=' + p3.href());
""",
        ],
        capture_output=True,
        timeout=30,
        cwd=str(REPO),
    )
    assert result.returncode == 0, f"Node failed:\n{result.stderr.decode()}"
    out = result.stdout.decode()
    assert "href1=/users/42" in out, f"Expected /users/42, got: {out}"
    assert "href2=/posts/hello/comments/7" in out, f"Expected /posts/hello/comments/7, got: {out}"
    assert "href3=/static/page" in out, f"Expected /static/page, got: {out}"


# [pr_diff] fail_to_pass
def test_no_namespace_imports_in_route_pattern():
    """route-pattern.ts no longer uses namespace imports (import * as X)."""
    main_file = REPO / "packages" / "route-pattern" / "src" / "lib" / "route-pattern.ts"
    content = main_file.read_text()
    # The refactored file should NOT have namespace imports like:
    # import * as Search from ...
    # import * as Source from ...
    # import * as Href from ...
    # import * as Parse from ...
    # import * as Join from ...
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("import") and " * as " in stripped:
            assert False, (
                f"Found namespace import at line {i}: {stripped}. "
                "Refactored code should use named imports."
            )


# [pr_diff] fail_to_pass
def test_source_file_deleted():
    """source.ts should be deleted — its logic moved to PartPattern methods."""
    source_file = PKG / "source.ts"
    assert not source_file.exists(), (
        "source.ts should be deleted. Its logic (part/source) is now PartPattern.source getter."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_tests_pass():
    """Upstream route-pattern test suite still passes after refactor."""
    result = subprocess.run(
        [
            "node", "--disable-warning=ExperimentalWarning", "--test",
            "./packages/route-pattern/src/lib/route-pattern.test.ts",
        ],
        capture_output=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert result.returncode == 0, (
        f"Upstream tests failed:\n{result.stdout.decode()}\n{result.stderr.decode()}"
    )


# [repo_tests] pass_to_pass
def test_part_pattern_tests_pass():
    """PartPattern test suite still passes after refactor."""
    result = subprocess.run(
        [
            "node", "--disable-warning=ExperimentalWarning", "--test",
            "./packages/route-pattern/src/lib/route-pattern/part-pattern.test.ts",
        ],
        capture_output=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert result.returncode == 0, (
        f"PartPattern tests failed:\n{result.stdout.decode()}\n{result.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / AGENTS.md
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass — AGENTS.md documents helper organization
def test_agents_md_documents_helpers():
    """AGENTS.md in route-pattern/ must exist and document the helper file organization."""
    agents_md = PKG / "AGENTS.md"
    assert agents_md.exists(), f"AGENTS.md not found at {agents_md}"
    content = agents_md.read_text().lower()
    # Must document PartPattern
    assert "part-pattern" in content, "AGENTS.md must reference part-pattern.ts"
    # Must document at least 3 feature-based files
    feature_files = ["href", "join", "match", "parse", "serialize", "split"]
    found = sum(1 for f in feature_files if f in content)
    assert found >= 3, (
        f"AGENTS.md must document at least 3 feature-based helpers (href, join, match, etc.), "
        f"found {found}: {[f for f in feature_files if f in content]}"
    )
    # Must mention "feature" organization principle
    assert "feature" in content, "AGENTS.md must describe organization by feature"


# [pr_diff] fail_to_pass — AGENTS.md references route-pattern.ts parent
def test_agents_md_links_to_parent():
    """AGENTS.md must reference the parent route-pattern.ts file."""
    agents_md = PKG / "AGENTS.md"
    content = agents_md.read_text()
    assert "route-pattern.ts" in content, (
        "AGENTS.md must reference route-pattern.ts as the parent module"
    )
