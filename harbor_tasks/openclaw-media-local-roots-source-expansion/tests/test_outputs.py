"""
Task: openclaw-media-local-roots-source-expansion
Repo: openclaw/openclaw @ aff6883f93abcbfd18ebb743871bc804b10f5728
PR:   #57770

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/openclaw"


def run_tsx(name: str, code: str) -> dict:
    """Write a .mts file inside the repo and run with tsx, returning parsed JSON output."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".mts", prefix=f"test_{name}_", dir=REPO, delete=False
    ) as f:
        f.write(code)
        f.flush()
        r = subprocess.run(
            ["npx", "tsx", f.name],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60,
        )
    for line in reversed(r.stdout.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            return json.loads(line)
    raise AssertionError(
        f"tsx '{name}' produced no JSON.\nstdout: {r.stdout}\nstderr: {r.stderr}"
    )


def strip_comments(code: str) -> str:
    """Strip JS/TS single-line and multi-line comments."""
    code = re.sub(r"//.*", "", code)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    return code


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass - oxlint type-aware linting
def test_repo_lint():
    """Repo's oxlint type-aware linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - media module unit tests (excluding local-roots tests
# which test the old behavior being fixed)
def test_repo_media_tests():
    """Repo's media module unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "--config", "vitest.unit.config.ts",
         "--exclude", "**/local-roots.test.ts", "src/media/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Media tests failed:\n{r.stderr[-500:]}"


# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without TypeScript syntax errors."""
    for f in ["src/media/local-roots.ts", "src/agents/tools/media-tool-shared.ts"]:
        fp = Path(REPO) / f
        if not fp.exists():
            continue
        r = subprocess.run(
            [
                "npx", "esbuild", "--bundle", "--platform=node",
                "--format=esm", "--external:*", str(fp),
            ],
            cwd=REPO, capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"{f} has syntax errors: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_append_no_widening():
    """appendLocalMediaParentRoots must not add media source parent dirs to roots."""
    result = run_tsx("append_widen", """
import { appendLocalMediaParentRoots } from "./src/media/local-roots.ts";
import path from "node:path";

// Test with multiple source types: absolute, file://, tilde, deep path
const roots = appendLocalMediaParentRoots(["/tmp/base", "/home/user/docs"], [
    "/Users/peter/Pictures/photo.png",
    "file:///Users/peter/Movies/clip.mp4",
    "/opt/data/report.pdf",
    "~/Desktop/notes.txt",
]);
const norm = roots.map(r => path.resolve(r));
console.log(JSON.stringify({
    hasBase: norm.some(r => r === path.resolve("/tmp/base")),
    hasDocs: norm.some(r => r === path.resolve("/home/user/docs")),
    hasPictures: norm.some(r => r.includes("Pictures")),
    hasMovies: norm.some(r => r.includes("Movies")),
    hasData: norm.some(r => r.includes("/opt/data")),
    hasDesktop: norm.some(r => r.includes("Desktop")),
    count: norm.length,
}));
""")
    # Anti-stub: must preserve input roots
    assert result["hasBase"], "Must preserve /tmp/base root"
    assert result["hasDocs"], "Must preserve /home/user/docs root"
    # F2P: must NOT widen from any media source type
    assert not result["hasPictures"], "Must not add Pictures from absolute path"
    assert not result["hasMovies"], "Must not add Movies from file:// URL"
    assert not result["hasData"], "Must not add /opt/data from absolute path"
    assert not result["hasDesktop"], "Must not add Desktop from ~ path"


# [pr_diff] fail_to_pass
def test_append_no_widening_varied_inputs():
    """appendLocalMediaParentRoots ignores media sources regardless of root contents."""
    result = run_tsx("append_widen2", """
import { appendLocalMediaParentRoots } from "./src/media/local-roots.ts";
import path from "node:path";

// Different roots + different media sources than test above
const roots = appendLocalMediaParentRoots(["/var/lib/app"], [
    "/etc/ssl/certs/ca.pem",
    "file:///home/alice/Documents/resume.docx",
    "/srv/uploads/image.jpg",
]);
const norm = roots.map(r => path.resolve(r));
console.log(JSON.stringify({
    hasApp: norm.some(r => r === path.resolve("/var/lib/app")),
    hasSsl: norm.some(r => r.includes("/etc/ssl")),
    hasDocuments: norm.some(r => r.includes("Documents")),
    hasUploads: norm.some(r => r.includes("/srv/uploads")),
    count: norm.length,
}));
""")
    assert result["hasApp"], "Must preserve /var/lib/app root"
    assert result["count"] == 1, f"Only 1 root expected, got {result['count']}"
    assert not result["hasSsl"], "Must not add /etc/ssl from media source"
    assert not result["hasDocuments"], "Must not add Documents from file:// URL"
    assert not result["hasUploads"], "Must not add /srv/uploads from media source"


# [pr_diff] fail_to_pass
def test_resolve_media_tool_no_widening():
    """resolveMediaToolLocalRoots must not widen roots from media source paths."""
    result = run_tsx("resolve_widen", """
import { resolveMediaToolLocalRoots } from "./src/agents/tools/media-tool-shared.ts";
import path from "node:path";
const roots = resolveMediaToolLocalRoots("/tmp/workspace", undefined, [
    "/Users/peter/Pictures/photo.png",
    "file:///Users/peter/Movies/clip.mp4",
    "/var/data/secrets.json",
]);
const norm = roots.map(r => path.resolve(r));
console.log(JSON.stringify({
    hasWorkspace: norm.some(r => r.includes("workspace")),
    hasPictures: norm.some(r => r.includes("Pictures")),
    hasMovies: norm.some(r => r.includes("Movies")),
    hasSecrets: norm.some(r => r.includes("/var/data")),
}));
""")
    # Anti-stub: workspace root must be present
    assert result["hasWorkspace"], "Must include workspace root"
    # F2P: must NOT widen from media sources
    assert not result["hasPictures"], "Must not add Pictures from media source"
    assert not result["hasMovies"], "Must not add Movies from media source"
    assert not result["hasSecrets"], "Must not add /var/data from media source"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_resolve_media_tool_modes():
    """resolveMediaToolLocalRoots handles default, workspace, and workspaceOnly."""
    result = run_tsx("modes", """
import { resolveMediaToolLocalRoots } from "./src/agents/tools/media-tool-shared.ts";
import path from "node:path";
const defaultRoots = resolveMediaToolLocalRoots(undefined);
const wsRoots = resolveMediaToolLocalRoots("/tmp/my-ws");
const onlyRoots = resolveMediaToolLocalRoots("/tmp/my-ws", { workspaceOnly: true });
console.log(JSON.stringify({
    defaultCount: defaultRoots.length,
    wsHasWs: wsRoots.map(r => path.resolve(r)).some(r => r.includes("my-ws")),
    wsCount: wsRoots.length,
    onlyHasWs: onlyRoots.map(r => path.resolve(r)).some(r => r.includes("my-ws")),
    onlyCount: onlyRoots.length,
}));
""")
    assert result["defaultCount"] >= 1, "Default roots must be non-empty"
    assert result["wsHasWs"], "Workspace root must be included when provided"
    assert result["onlyHasWs"], "workspaceOnly must include workspace dir"
    assert result["onlyCount"] <= 2, "workspaceOnly should restrict to workspace only"


# [pr_diff] pass_to_pass
def test_append_deduplicates_and_preserves():
    """appendLocalMediaParentRoots deduplicates and preserves all input roots."""
    result = run_tsx("dedup", """
import { appendLocalMediaParentRoots } from "./src/media/local-roots.ts";
import path from "node:path";
const roots = appendLocalMediaParentRoots(["/tmp/a", "/tmp/b", "/tmp/a", "/tmp/c"]);
const norm = roots.map(r => path.resolve(r));
const unique = new Set(norm);
console.log(JSON.stringify({
    deduped: unique.size === norm.length,
    hasA: norm.some(r => r === path.resolve("/tmp/a")),
    hasB: norm.some(r => r === path.resolve("/tmp/b")),
    hasC: norm.some(r => r === path.resolve("/tmp/c")),
    count: norm.length,
}));
""")
    assert result["deduped"], "Roots must be deduplicated"
    assert result["hasA"], "Must preserve /tmp/a"
    assert result["hasB"], "Must preserve /tmp/b"
    assert result["hasC"], "Must preserve /tmp/c"
    assert result["count"] == 3, f"Expected 3 unique roots, got {result['count']}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — getAgentScopedMediaLocalRootsForSources
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_agent_scoped_no_widening():
    """getAgentScopedMediaLocalRootsForSources must not widen roots from mediaSources."""
    result = run_tsx("agent_scoped", """
import { getAgentScopedMediaLocalRootsForSources } from "./src/media/local-roots.ts";
import path from "node:path";

process.env.OPENCLAW_STATE_DIR = "/tmp/openclaw-test-scoped-roots";

const roots = getAgentScopedMediaLocalRootsForSources({
    cfg: {} as any,
    agentId: "test-agent",
    mediaSources: [
        "/Users/peter/Pictures/photo.png",
        "file:///Users/peter/Movies/clip.mp4",
        "/var/secrets/key.pem",
    ],
});
const norm = Array.from(roots).map(r => path.resolve(r));
console.log(JSON.stringify({
    hasStateDir: norm.some(r => r.includes("openclaw-test-scoped-roots")),
    hasPictures: norm.some(r => r.includes("Pictures")),
    hasMovies: norm.some(r => r.includes("Movies")),
    hasSecrets: norm.some(r => r.includes("/var/secrets")),
    count: norm.length,
}));
""")
    # Anti-stub: must return agent-scoped roots (state dir based)
    assert result["hasStateDir"], "Must include state dir based roots"
    assert result["count"] >= 1, "Must return at least one root"
    # F2P: must NOT widen from media sources
    assert not result["hasPictures"], "Must not add Pictures from media source"
    assert not result["hasMovies"], "Must not add Movies from media source"
    assert not result["hasSecrets"], "Must not add /var/secrets from media source"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — structural
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_expansion_import():
    """media-tool-shared.ts must not import appendLocalMediaParentRoots."""
    fp = Path(REPO) / "src/agents/tools/media-tool-shared.ts"
    assert fp.exists(), "media-tool-shared.ts not found"
    code = strip_comments(fp.read_text())
    assert "appendLocalMediaParentRoots" not in code, (
        "media-tool-shared.ts still references appendLocalMediaParentRoots"
    )


# [pr_diff] fail_to_pass
def test_no_source_expansion_helpers():
    """local-roots.ts must not contain source-path expansion utilities."""
    fp = Path(REPO) / "src/media/local-roots.ts"
    assert fp.exists(), "local-roots.ts not found"
    code = strip_comments(fp.read_text())
    present = [s for s in ["safeFileURLToPath", "resolveUserPath", "HTTP_URL_RE", "DATA_URL_RE"]
               if s in code]
    assert len(present) == 0, f"Source expansion helpers still in local-roots.ts: {present}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:144-146 @ aff6883
def test_no_type_safety_bypasses():
    """No explicit 'any' annotations or @ts-nocheck in modified files."""
    for f in ["src/media/local-roots.ts", "src/agents/tools/media-tool-shared.ts"]:
        fp = Path(REPO) / f
        if not fp.exists():
            continue
        full = fp.read_text()
        code = strip_comments(full)
        any_matches = re.findall(r":\s*any\b|<any>", code)
        assert len(any_matches) == 0, (
            f"{f} has {len(any_matches)} explicit 'any' annotation(s)"
        )
        assert "@ts-nocheck" not in full, f"{f} contains @ts-nocheck"


# [agent_config] pass_to_pass — CLAUDE.md:146-147 @ aff6883
def test_no_lint_suppressions():
    """No inline lint suppression comments in modified files."""
    suppressions = [
        "eslint-disable",
        "oxlint-ignore",
        "oxlint-disable",
        "@ts-ignore",
        "no-explicit-any",
    ]
    for f in ["src/media/local-roots.ts", "src/agents/tools/media-tool-shared.ts"]:
        fp = Path(REPO) / f
        if not fp.exists():
            continue
        text = fp.read_text()
        found = [s for s in suppressions if s in text]
        assert len(found) == 0, (
            f"{f} has inline lint suppressions: {found}"
        )
