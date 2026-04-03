"""
Task: opencode-vcs-native-spawner
Repo: anomalyco/opencode @ b242a8d8e42839496c7213d020e8cba19a76e111
PR:   #19361

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/opencode"
VCS_TS = Path(REPO) / "packages/opencode/src/project/vcs.ts"


def _read_vcs():
    assert VCS_TS.exists(), "vcs.ts is missing"
    return VCS_TS.read_text()


def _code_lines(src: str) -> list[str]:
    """Return non-comment, non-blank lines."""
    lines = []
    for line in src.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("//") or stripped.startswith("*"):
            continue
        lines.append(line)
    return lines


def _extract_generators(src: str) -> list[str]:
    """Extract generator function bodies via brace counting."""
    generators = []
    depth = 0
    in_gen = False
    current: list[str] = []
    for line in src.splitlines():
        if re.search(r"function\s*\*", line) and not in_gen:
            in_gen = True
            depth = 0
            current = []
        if in_gen:
            current.append(line)
            depth += line.count("{") - line.count("}")
            if depth <= 0 and len(current) > 3:
                generators.append("\n".join(current))
                in_gen = False
    return generators


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_vcs_file_nontrivial():
    """vcs.ts must exist with >= 40 lines of implementation."""
    src = _read_vcs()
    lines = src.splitlines()
    assert len(lines) >= 40, f"vcs.ts too short ({len(lines)} lines)"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core migration tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_effect_promise():
    """Effect.promise must not appear — it bypasses Effect's scope and interruption model."""
    src = _read_vcs()
    assert "Effect.promise" not in src, "vcs.ts still uses Effect.promise"


# [pr_diff] fail_to_pass
def test_no_util_git_import():
    """The old @/util/git async utility must not be imported."""
    src = _read_vcs()
    assert "@/util/git" not in src, "vcs.ts still imports @/util/git"


# [pr_diff] fail_to_pass
def test_imports_child_process_spawner():
    """Must import ChildProcess/ChildProcessSpawner from effect's process module."""
    src = _read_vcs()
    has_import = re.search(
        r"""import\s.*(?:ChildProcess|ChildProcessSpawner).*from\s+['"]effect/unstable/process['"]""",
        src,
    )
    assert has_import, "Missing ChildProcess/ChildProcessSpawner import from effect/unstable/process"


# [pr_diff] fail_to_pass
def test_generator_git_helper_complete():
    """A generator must spawn a child process, read exit code, and extract stdout text."""
    src = _read_vcs()
    generators = _extract_generators(src)
    assert generators, "No generator functions found in vcs.ts"

    found = False
    for gen in generators:
        has_spawn = bool(re.search(r"spawn|ChildProcess\.make", gen))
        has_exit = bool(re.search(r"\.code\b|\.exitCode\b|exitCode", gen))
        has_output = bool(re.search(r"\.stdout\b|\.text\b|mkString|decodeText", gen))
        has_yield = bool(re.search(r"yield\s*\*", gen))
        if has_spawn and has_exit and has_output and has_yield:
            found = True
            break

    assert found, (
        "No generator found that spawns a child process, checks exit code, "
        "and extracts stdout text"
    )


# [pr_diff] fail_to_pass
def test_layer_declares_spawner_dependency():
    """The layer type signature must include ChildProcessSpawner as a dependency."""
    src = _read_vcs()
    layer_match = re.search(
        r"export\s+const\s+layer.*?Layer\.Layer<[^>]+>", src, re.DOTALL
    )
    assert layer_match, "Could not find 'export const layer' with Layer.Layer<...> type"
    assert "ChildProcessSpawner" in layer_match.group(0), (
        "layer type does not declare ChildProcessSpawner dependency"
    )


# [pr_diff] fail_to_pass
def test_default_layer_provides_spawner():
    """defaultLayer must wire in a concrete spawner (CrossSpawnSpawner or equivalent)."""
    src = _read_vcs()
    dl_idx = src.find("defaultLayer")
    assert dl_idx >= 0, "defaultLayer not found"
    has_spawner_import = bool(
        re.search(r"import.*(?:CrossSpawn|cross-spawn-spawner)", src, re.IGNORECASE)
    )
    after_dl = src[dl_idx : dl_idx + 500]
    dl_refs_spawner = bool(
        re.search(r"(?:CrossSpawn|Spawner|spawner)", after_dl, re.IGNORECASE)
    )
    assert has_spawner_import and dl_refs_spawner, (
        "defaultLayer does not provide a concrete spawner implementation"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — rules from repo config files
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — packages/opencode/AGENTS.md:47 @ b242a8d8e42839496c7213d020e8cba19a76e111
def test_uses_child_process_make():
    """Must use ChildProcess.make() to construct child process descriptors (not raw spawn)."""
    src = _read_vcs()
    assert re.search(r"ChildProcess\.make\s*\(", src), (
        "vcs.ts must use ChildProcess.make() per packages/opencode/AGENTS.md"
    )


# [agent_config] pass_to_pass — packages/opencode/AGENTS.md:45 @ b242a8d8e42839496c7213d020e8cba19a76e111
def test_no_raw_platform_api():
    """Must not use raw Node.js child_process or async exec — use Effect services instead."""
    src = _read_vcs()
    # Check for raw Node.js process APIs that bypass Effect
    for pattern, label in [
        (r"""from\s+['"]child_process['"]""", "raw child_process import"),
        (r"""from\s+['"]node:child_process['"]""", "raw node:child_process import"),
        (r"""\bexec\s*\(""", "raw exec() call"),
        (r"""\bexecSync\s*\(""", "raw execSync() call"),
        (r"""\bspawnSync\s*\(""", "raw spawnSync() call"),
    ]:
        assert not re.search(pattern, src), f"vcs.ts uses {label} — prefer Effect services"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + style guards
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_public_api_intact():
    """Service public API (layer, defaultLayer, Service, init, branch) must remain."""
    src = _read_vcs()
    assert "export const layer" in src, "Missing 'export const layer'"
    assert "export const defaultLayer" in src, "Missing 'export const defaultLayer'"
    assert "export class Service" in src, "Missing 'export class Service'"
    assert re.search(r"export\s+function\s+init", src), "Missing 'export function init'"
    assert re.search(r"export\s+function\s+branch", src), "Missing 'export function branch'"


# [agent_config] pass_to_pass — AGENTS.md:13 @ b242a8d8e42839496c7213d020e8cba19a76e111
def test_no_any_type():
    """Must not use the 'any' type."""
    src = _read_vcs()
    code = _code_lines(src)
    for line in code:
        assert not re.search(r":\s*any\b", line), f"Found ': any' usage: {line.strip()}"
        assert not re.search(r"\bas\s+any\b", line), f"Found 'as any' usage: {line.strip()}"


# [agent_config] pass_to_pass — AGENTS.md:12 @ b242a8d8e42839496c7213d020e8cba19a76e111
def test_no_try_catch():
    """Must not use try/catch — prefer Effect error handling."""
    src = _read_vcs()
    code = _code_lines(src)
    for line in code:
        assert not re.search(r"\btry\s*\{", line), f"Found try/catch: {line.strip()}"


# [agent_config] pass_to_pass — AGENTS.md:70 @ b242a8d8e42839496c7213d020e8cba19a76e111
def test_no_let_declarations():
    """Must not use let — prefer const with ternaries or early returns."""
    src = _read_vcs()
    code = _code_lines(src)
    for line in code:
        assert not re.search(r"\blet\b", line), f"Found let declaration: {line.strip()}"


# [agent_config] pass_to_pass — packages/opencode/AGENTS.md:46 @ b242a8d8e42839496c7213d020e8cba19a76e111
def test_no_raw_fs_import():
    """Must not import raw fs/promises — use FileSystem.FileSystem service instead."""
    src = _read_vcs()
    for pattern, label in [
        (r"""from\s+['"]fs/promises['"]""", "fs/promises import"),
        (r"""from\s+['"]node:fs/promises['"]""", "node:fs/promises import"),
        (r"""from\s+['"]node:fs['"]""", "node:fs import"),
        (r"""from\s+['"]fs['"]""", "raw fs import"),
    ]:
        assert not re.search(pattern, src), f"vcs.ts uses {label} — prefer FileSystem.FileSystem"


# [agent_config] pass_to_pass — packages/opencode/AGENTS.md:48 @ b242a8d8e42839496c7213d020e8cba19a76e111
def test_no_raw_fetch():
    """Must not use raw fetch() — use HttpClient.HttpClient service instead."""
    src = _read_vcs()
    assert not re.search(r"\bfetch\s*\(", src), "vcs.ts uses raw fetch() — prefer HttpClient.HttpClient"
