"""
Task: nextjs-app-route-encoded-segment
Repo: vercel/next.js @ 56d75a0b77f2ceda8ea747810275da8e0a9a3d71
PR:   91603

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/next.js"
TARGET_FILE = "packages/next/src/shared/lib/router/routes/app.ts"

# Mock dependencies for app.ts — faithful reproductions from the repo
_MOCK_PREAMBLE = textwrap.dedent("""\
    class InvariantError extends Error {
      constructor(message: string, options?: ErrorOptions) {
        super(`Invariant: ${message.endsWith('.') ? message : message + '.'} This is a bug in Next.js.`, options);
        this.name = 'InvariantError';
      }
    }

    const INTERCEPTION_ROUTE_MARKERS = ['(..)(..)', '(.)', '(..)', '(...)'] as const;
    type InterceptionMarker = (typeof INTERCEPTION_ROUTE_MARKERS)[number];

    type SegmentParam = { paramName: string; paramType: string };

    function getSegmentParam(segment: string): SegmentParam | null {
      const interceptionMarker = INTERCEPTION_ROUTE_MARKERS.find((marker) =>
        segment.startsWith(marker)
      );
      if (interceptionMarker) {
        segment = segment.slice(interceptionMarker.length);
      }
      if (segment.startsWith('[[...') && segment.endsWith(']]')) {
        return { paramType: 'optional-catchall', paramName: segment.slice(5, -2) };
      }
      if (segment.startsWith('[...') && segment.endsWith(']')) {
        return {
          paramType: interceptionMarker ? 'catchall-intercepted-' + interceptionMarker : 'catchall',
          paramName: segment.slice(4, -1),
        };
      }
      if (segment.startsWith('[') && segment.endsWith(']')) {
        return {
          paramType: interceptionMarker ? 'dynamic-intercepted-' + interceptionMarker : 'dynamic',
          paramName: segment.slice(1, -1),
        };
      }
      return null;
    }

    function isCatchAll(type: string): boolean {
      return type === 'catchall' || type === 'optional-catchall' ||
             type.startsWith('catchall-intercepted-');
    }
""")


def _create_patched_module() -> str:
    """Create a patched version of app.ts with mock dependencies, return path."""
    src = Path(f"{REPO}/{TARGET_FILE}").read_text()
    # Remove import blocks (single-line and multi-line)
    patched = re.sub(r"import\s*\{[^}]*\}\s*from\s*['\"][^'\"]*['\"];?", "", src)
    patched = re.sub(r"import\s+[^\n{]*from\s*['\"][^'\"]*['\"];?", "", patched)
    patched = _MOCK_PREAMBLE + "\n" + patched
    patched_path = "/tmp/_patched_app.ts"
    Path(patched_path).write_text(patched)
    return patched_path


def _parse_route(pathname: str) -> dict:
    """Run parseAppRoute via tsx on a patched copy with mocked deps."""
    patched = _create_patched_module()
    safe = pathname.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    test_script = textwrap.dedent(f"""\
        import {{ parseAppRoute }} from '{patched.replace(".ts", ".js")}'
        const route = parseAppRoute(`{safe}`, false)
        const names = route.dynamicSegments.map((s: any) => s.param.paramName)
        const types = route.dynamicSegments.map((s: any) => s.param.paramType)
        console.log(JSON.stringify({{ names, types, segmentCount: route.segments.length }}))
    """)
    script = Path("/tmp/_test_route.ts")
    script.write_text(test_script)
    r = subprocess.run(
        ["tsx", str(script)],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"tsx failed:\n{r.stderr.decode()}"
    return json.loads(r.stdout.decode().strip())


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript file must parse without errors."""
    patched = _create_patched_module()
    r = subprocess.run(
        ["tsx", "--eval", f"import '{patched.replace('.ts', '.js')}'; console.log('OK')"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Import failed:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_encoded_single_dynamic():
    """Encoded single dynamic placeholder %5BprojectSlug%5D is recognized."""
    r1 = _parse_route("/vercel/%5BprojectSlug%5D")
    assert "projectSlug" in r1["names"]

    r2 = _parse_route("/app/%5Bid%5D")
    assert "id" in r2["names"]

    r3 = _parse_route("/users/%5BuserId%5D/profile")
    assert "userId" in r3["names"]


# [pr_diff] fail_to_pass
def test_encoded_multiple_dynamic():
    """Multiple encoded placeholders in same path both recognized."""
    r1 = _parse_route("/%5BteamSlug%5D/project/%5BprojectSlug%5D")
    assert "teamSlug" in r1["names"]
    assert "projectSlug" in r1["names"]

    r2 = _parse_route("/%5Borg%5D/%5Brepo%5D/%5Bbranch%5D")
    assert "org" in r2["names"]
    assert "repo" in r2["names"]
    assert "branch" in r2["names"]

    r3 = _parse_route("/api/%5Bversion%5D/users/%5BuserId%5D")
    assert "version" in r3["names"]
    assert "userId" in r3["names"]


# [pr_diff] fail_to_pass
def test_encoded_mixed_segments():
    """Mixed encoded and non-encoded dynamic segments both recognized."""
    r1 = _parse_route("/[teamSlug]/%5BprojectSlug%5D")
    assert "teamSlug" in r1["names"]
    assert "projectSlug" in r1["names"]

    r2 = _parse_route("/%5Borg%5D/[repo]/[branch]")
    assert "org" in r2["names"]
    assert "repo" in r2["names"]
    assert "branch" in r2["names"]

    r3 = _parse_route("/[locale]/%5Bpage%5D/[section]")
    assert "locale" in r3["names"]
    assert "page" in r3["names"]
    assert "section" in r3["names"]


# [pr_diff] fail_to_pass
def test_encoded_catchall_segment():
    """Encoded catchall segment %5B...slug%5D is recognized as dynamic."""
    r1 = _parse_route("/%5B...slug%5D")
    assert "slug" in r1["names"]

    r2 = _parse_route("/docs/%5B...path%5D")
    assert "path" in r2["names"]

    r3 = _parse_route("/%5B...segments%5D")
    assert "segments" in r3["names"]


# [pr_diff] fail_to_pass
def test_encoded_optional_catchall():
    """Encoded optional catchall %5B%5B...slug%5D%5D is recognized."""
    r1 = _parse_route("/%5B%5B...slug%5D%5D")
    assert "slug" in r1["names"]

    r2 = _parse_route("/docs/%5B%5B...path%5D%5D")
    assert "path" in r2["names"]

    r3 = _parse_route("/api/%5B%5B...rest%5D%5D")
    assert "rest" in r3["names"]


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_normal_dynamic_segments():
    """Non-encoded dynamic segments still work correctly."""
    r1 = _parse_route("/blog/[slug]/[id]")
    assert "slug" in r1["names"]
    assert "id" in r1["names"]

    r2 = _parse_route("/[locale]/dashboard")
    assert "locale" in r2["names"]

    r3 = _parse_route("/[...catchall]")
    assert "catchall" in r3["names"]

    r4 = _parse_route("/[[...optional]]")
    assert "optional" in r4["names"]


# [pr_diff] pass_to_pass
def test_static_segments():
    """Static segments are parsed correctly with no false dynamic matches."""
    r1 = _parse_route("/about/contact")
    assert r1["names"] == [], f"Expected no dynamic segments, got {r1['names']}"

    r2 = _parse_route("/api/health")
    assert r2["names"] == []

    r3 = _parse_route("/docs/getting-started/installation")
    assert r3["names"] == []


# [pr_diff] pass_to_pass
def test_malformed_encoding_no_crash():
    """Malformed URL encoding does not crash and segments remain static."""
    # Unclosed bracket encoding
    r1 = _parse_route("/test/%5Bparam")
    assert r1["names"] == [], f"Expected no dynamic segments, got {r1['names']}"
    assert r1["segmentCount"] == 2

    # Partial percent encoding
    r2 = _parse_route("/test/%5")
    assert r2["names"] == [], f"Expected no dynamic segments, got {r2['names']}"
    assert r2["segmentCount"] == 2

    # Random percent signs
    r3 = _parse_route("/test/100%25complete")
    assert r3["names"] == [], f"Expected no dynamic segments, got {r3['names']}"
    assert r3["segmentCount"] == 2


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:396 @ 56d75a0
def test_no_require_calls():
    """No bare require() calls in shared lib file — ES imports only (AGENTS.md:396)."""
    content = Path(f"{REPO}/{TARGET_FILE}").read_text()
    assert not re.search(r'\brequire\s*\(', content), (
        "Found require() call in shared lib file — use ES imports for DCE safety"
    )


# [agent_config] pass_to_pass — AGENTS.md:302-309 @ 56d75a0
def test_no_hardcoded_secrets():
    """No hardcoded secret values in modified file (AGENTS.md:302-309)."""
    content = Path(f"{REPO}/{TARGET_FILE}").read_text()
    assert not re.search(
        r'(api[_-]?key|secret|token|password|credential)\s*[:=]\s*["\']',
        content,
        re.IGNORECASE,
    ), "Hardcoded secret values found"


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates — ensure candidate solutions don't break CI
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typescript_syntax_app_router():
    """Repo's router TypeScript files parse without errors (pass_to_pass)."""
    # Verify the main app.ts and its dependencies can be parsed by tsx
    router_dir = f"{REPO}/packages/next/src/shared/lib/router"
    files_to_check = [
        f"{router_dir}/routes/app.ts",
        f"{router_dir}/utils/get-segment-param.tsx",
        f"{router_dir}/utils/interception-routes.ts",
    ]
    for filepath in files_to_check:
        r = subprocess.run(
            ["npx", "tsx", "--eval", f"import '{filepath}'; console.log('OK')"],
            cwd=REPO,
            capture_output=True,
            timeout=30,
        )
        assert r.returncode == 0, f"TypeScript syntax check failed for {filepath}:\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass
def test_repo_imports_resolvable():
    """Router module imports are resolvable without runtime errors (pass_to_pass)."""
    # Test that the target file's dependencies can be imported
    test_script = textwrap.dedent(f"""\
        import {{ parseAppRoute }} from '{REPO}/packages/next/src/shared/lib/router/routes/app.ts'
        console.log('parseAppRoute imported successfully')
    """)
    script_path = "/tmp/test_imports.ts"
    Path(script_path).write_text(test_script)
    r = subprocess.run(
        ["npx", "tsx", script_path],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Import test failed:\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass
def test_repo_eslint_app_router():
    """ESLint passes on router files (pass_to_pass)."""
    # Use the local eslint after installing dependencies
    r = subprocess.run(
        ["bash", "-c", "npm install -g pnpm && corepack enable && pnpm install >/dev/null 2>&1 && ./node_modules/.bin/eslint --config eslint.cli.config.mjs " + TARGET_FILE],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout.decode()[-500:]}{r.stderr.decode()[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier_app_router():
    """Prettier formatting check passes on router files (pass_to_pass)."""
    # Use the local prettier
    r = subprocess.run(
        ["bash", "-c", "npm install -g pnpm && corepack enable && pnpm install >/dev/null 2>&1 && ./node_modules/.bin/prettier --check " + TARGET_FILE],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout.decode()[-500:]}{r.stderr.decode()[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_interception_routes():
    """Interception routes unit tests pass (pass_to_pass)."""
    # Install deps, build the package, and run the specific unit test
    r = subprocess.run(
        ["bash", "-c", "npm install -g pnpm && corepack enable && pnpm install >/dev/null 2>&1 && pnpm build --filter=next >/dev/null 2>&1 && ./node_modules/.bin/jest interception-routes.test.ts --no-coverage"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, f"Interception routes unit tests failed:\n{r.stdout.decode()[-500:]}{r.stderr.decode()[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_is_dynamic():
    """Is-dynamic route unit tests pass (pass_to_pass)."""
    # Install deps, build the package, and run the specific unit test
    r = subprocess.run(
        ["bash", "-c", "npm install -g pnpm && corepack enable && pnpm install >/dev/null 2>&1 && pnpm build --filter=next >/dev/null 2>&1 && ./node_modules/.bin/jest is-dynamic.test.ts --no-coverage"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, f"Is-dynamic unit tests failed:\n{r.stdout.decode()[-500:]}{r.stderr.decode()[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_validate_app_paths():
    """App paths validation unit tests pass (pass_to_pass)."""
    # These tests directly use parseAppRoute from the modified app.ts
    r = subprocess.run(
        ["bash", "-c", "npm install -g pnpm && corepack enable && pnpm install >/dev/null 2>&1 && pnpm build --filter=next >/dev/null 2>&1 && ./node_modules/.bin/jest packages/next/src/build/validate-app-paths.test.ts --no-coverage"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, f"Validate app paths unit tests failed:\n{r.stdout.decode()[-500:]}{r.stderr.decode()[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_extract_pathname_segments():
    """Extract pathname route param segments unit tests pass (pass_to_pass)."""
    # These tests directly import and use parseAppRoute from the modified app.ts
    r = subprocess.run(
        ["bash", "-c", "npm install -g pnpm && corepack enable && pnpm install >/dev/null 2>&1 && pnpm build --filter=next >/dev/null 2>&1 && ./node_modules/.bin/jest packages/next/src/build/static-paths/app/extract-pathname-route-param-segments-from-loader-tree.test.ts --no-coverage"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, f"Extract pathname segments unit tests failed:\n{r.stdout.decode()[-500:]}{r.stderr.decode()[-500:]}"
