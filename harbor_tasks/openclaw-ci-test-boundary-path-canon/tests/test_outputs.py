"""
Task: openclaw-ci-test-boundary-path-canon
Repo: openclaw/openclaw @ 17d0be02f2800a2bc4524c7d5b587d7fd9f6f28c
PR:   #57797

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: Both bugs are environment/CI-dependent (Bug 1 = boundary lint, Bug 2 = macOS
symlink tmpdir), so behavioral vitest tests would not reliably fail on base in Docker.
Structural checks are used because: TypeScript cannot be imported in Python, and the
bugs manifest through CI lint / OS-dependent symlinks, not vitest assertion failures.
"""

import re
from pathlib import Path

REPO = "/workspace/openclaw"
CMD_TEST = f"{REPO}/src/auto-reply/reply/commands.test.ts"
MEDIA_TEST = f"{REPO}/src/media-understanding/media-understanding-misc.test.ts"


def _read(filepath: str) -> str:
    return Path(filepath).read_text()


def _code_lines(filepath: str) -> list[str]:
    """Return non-comment, non-blank lines from a TS file."""
    out: list[str] = []
    for line in Path(filepath).read_text().splitlines():
        t = line.strip()
        if not t or t.startswith("//") or t.startswith("*") or t.startswith("/*"):
            continue
        out.append(line)
    return out


def _code(filepath: str) -> str:
    return "\n".join(_code_lines(filepath))


def _ssrf_block(filepath: str) -> str:
    """Return the full text of the SSRF describe block."""
    src = _read(filepath)
    idx = src.find("media understanding attachments SSRF")
    assert idx != -1, "SSRF describe block not found in media test file"
    return src[idx:]


def _ssrf_code(filepath: str) -> str:
    """Return non-comment lines from the SSRF describe block."""
    lines = []
    for line in _ssrf_block(filepath).splitlines():
        t = line.strip()
        if t and not t.startswith("//") and not t.startswith("*") and not t.startswith("/*"):
            lines.append(line)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_files_parse():
    """Modified TS files must have balanced braces."""
    for fp in [CMD_TEST, MEDIA_TEST]:
        src = _read(fp)
        depth = 0
        for ch in src:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
        assert depth == 0, f"{fp} has unbalanced braces (depth={depth})"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — Bug 1: Extension boundary
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_extension_import_removed():
    """The buggy import from extensions/telegram/test-support must be removed."""
    for line in _code_lines(CMD_TEST):
        t = line.strip()
        if re.match(r"^import\b", t) and "extensions/telegram/test-support" in t:
            raise AssertionError(
                "Import from extensions/telegram/test-support.js still present"
            )


# [pr_diff] fail_to_pass
def test_plugin_constructed_intree():
    """telegramCommandTestPlugin is constructed in-tree via SDK helpers or manual ChannelPlugin."""
    code = _code(CMD_TEST)

    # Must be defined locally
    has_def = bool(
        re.search(r"(?:const|let|var|function)\s+telegramCommandTestPlugin\b", code)
        or re.search(r"telegramCommandTestPlugin\s*[:=]", code)
    )
    assert has_def, "telegramCommandTestPlugin is not defined locally in the test file"

    # Must use SDK helpers or explicit ChannelPlugin typing
    has_construction = (
        "createChannelTestPluginBase" in code
        or "createTestPluginBase" in code
        or (
            re.search(r'id\s*:\s*["\']telegram["\']', code)
            and re.search(r'label\s*:\s*["\']Telegram["\']', code)
        )
        or re.search(r"as\s+ChannelPlugin", code)
        or re.search(r":\s*ChannelPlugin\s*[={]", code)
    )
    assert has_construction, (
        "telegramCommandTestPlugin not constructed with SDK helpers or ChannelPlugin type"
    )


# [pr_diff] fail_to_pass
def test_plugin_not_stub():
    """Plugin definition spans >=8 meaningful lines (rejects trivial stubs)."""
    lines = _read(CMD_TEST).splitlines()

    def_start = -1
    for i, line in enumerate(lines):
        t = line.strip()
        if t.startswith("//") or t.startswith("*") or t.startswith("/*"):
            continue
        if re.search(
            r"(?:const|let|var)\s+telegramCommandTestPlugin\b", t
        ) or re.search(r"telegramCommandTestPlugin\s*[:=]", t):
            def_start = i
            break

    assert def_start >= 0, "telegramCommandTestPlugin definition not found"

    # Walk from definition to end of its object/block
    count = 0
    brace_depth = 0
    started = False
    for i in range(def_start, min(len(lines), def_start + 300)):
        t = lines[i].strip()
        if t.startswith("//") or t.startswith("*") or t.startswith("/*"):
            continue
        if not t:
            continue
        count += 1
        for ch in lines[i]:
            if ch == "{":
                brace_depth += 1
                started = True
            elif ch == "}":
                brace_depth -= 1
        if started and brace_depth <= 0 and i > def_start:
            break

    assert count >= 8, (
        f"telegramCommandTestPlugin is a trivial stub ({count} lines, need >=8)"
    )


# [pr_diff] fail_to_pass
def test_plugin_has_channel_config():
    """Plugin definition includes config/allowlist/auth adapters (not just base fields)."""
    code = _code(CMD_TEST)

    # The gold fix uses createScopedChannelConfigAdapter, buildDmGroupAccountAllowlistAdapter,
    # and createApproverRestrictedNativeApprovalAdapter. An alternative fix must provide at
    # least config + allowlist adapters (or equivalent manual implementations).
    has_config = (
        "createScopedChannelConfigAdapter" in code
        or re.search(r"config\s*:", code) and re.search(r"sectionKey|listAccountIds", code)
    )
    has_allowlist = (
        "buildDmGroupAccountAllowlistAdapter" in code
        or re.search(r"allowlist\s*:", code)
    )
    assert has_config, "Plugin missing config adapter (createScopedChannelConfigAdapter or manual)"
    assert has_allowlist, "Plugin missing allowlist adapter"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — Bug 2: Path canonicalization
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_path_canonicalization_in_ssrf():
    """SSRF test block uses path canonicalization (realpath / realpathSync / resolve)."""
    code = _ssrf_code(MEDIA_TEST)
    assert re.search(
        r"realpath|realpathSync|fs\.realpath|path\.resolve|canonicali[sz]e", code, re.IGNORECASE
    ), "SSRF tests do not use any path canonicalization (realpath/resolve)"


# [pr_diff] fail_to_pass
def test_no_direct_path_comparison():
    """No direct uncanonicalized path equality remains in SSRF tests."""
    code = _ssrf_code(MEDIA_TEST)

    # The base commit has toHaveBeenCalledWith(attachmentPath, ...) directly
    assert not re.search(
        r"toHaveBeenCalledWith\(\s*attachmentPath\s*,", code
    ), "Direct uncanonicalized toHaveBeenCalledWith(attachmentPath, ...) still present"

    # Also check for direct !== comparison
    assert not re.search(
        r"filePath\s*!==?\s*attachmentPath", code
    ), "Direct uncanonicalized filePath !== attachmentPath still present"


# [pr_diff] fail_to_pass
def test_both_ssrf_tests_canonicalize():
    """Both path-comparing SSRF test cases use canonicalization, not just one."""
    block = _ssrf_block(MEDIA_TEST)
    # Split into individual it() blocks
    it_blocks = re.split(r'\bit\s*\(', block)
    test_blocks = it_blocks[1:]  # skip preamble before first it(

    canon_re = re.compile(
        r"realpath|realpathSync|path\.resolve|canonicali[sz]e", re.IGNORECASE
    )

    # Find blocks that compare file paths (the two bugs):
    # 1. The block with openSpy.mockImplementation + filePath comparison
    # 2. The block with toHaveBeenCalledWith/openSpy assertion on path
    path_compare_blocks = []
    for tb in test_blocks:
        if ("filePath" in tb and "attachmentPath" in tb) or (
            "openSpy" in tb and "attachmentPath" in tb and "openedPath" in tb
        ) or ("toHaveBeenCalledWith" in tb and "attachmentPath" in tb):
            path_compare_blocks.append(tb)

    assert len(path_compare_blocks) >= 2, (
        f"Expected at least 2 path-comparing SSRF test cases, found {len(path_compare_blocks)}"
    )

    for i, tb in enumerate(path_compare_blocks):
        assert canon_re.search(tb), (
            f"Path-comparing SSRF test case {i + 1} does not use path canonicalization"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression / structure preserved
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_plugin_defined_and_used():
    """telegramCommandTestPlugin appears at least twice (definition + usage)."""
    code = _code(CMD_TEST)
    matches = re.findall(r"telegramCommandTestPlugin", code)
    assert len(matches) >= 2, (
        f"telegramCommandTestPlugin appears {len(matches)} time(s), need >=2"
    )


# [pr_diff] pass_to_pass
def test_ssrf_structure_preserved():
    """SSRF test block still references MediaAttachmentCache and O_NOFOLLOW."""
    code = _ssrf_code(MEDIA_TEST)
    assert "MediaAttachmentCache" in code, "MediaAttachmentCache reference removed from SSRF tests"
    assert "O_NOFOLLOW" in code, "O_NOFOLLOW reference removed from SSRF tests"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:42 @ 17d0be02f2800a2bc4524c7d5b587d7fd9f6f28c
def test_no_extension_deep_imports():
    """Core tests must not deep-import bundled plugin internals (AGENTS.md:42)."""
    for line in _code_lines(CMD_TEST):
        t = line.strip()
        if re.match(r"^import\b", t) and re.search(r"""['"].*extensions/""", t):
            raise AssertionError(f"Extension deep-import found in core test: {t}")


# [agent_config] pass_to_pass — test/helpers/channels/AGENTS.md:8-9 @ 17d0be0
def test_no_hardcoded_extension_paths():
    """Core test helpers must not hardcode repo-relative imports into extensions/** (test/helpers/channels/AGENTS.md:8-9)."""
    for line in _code_lines(CMD_TEST):
        t = line.strip()
        # Catch require() and import() with extension paths (dynamic imports)
        if re.search(r"""(?:require|import)\s*\(\s*['"].*extensions/""", t):
            raise AssertionError(f"Hardcoded extension path in dynamic import/require: {t}")


# [agent_config] pass_to_pass — AGENTS.md:146 @ 17d0be02f2800a2bc4524c7d5b587d7fd9f6f28c
def test_no_ts_nocheck():
    """Never add @ts-nocheck (AGENTS.md:146)."""
    for fp in [CMD_TEST, MEDIA_TEST]:
        src = _read(fp)
        assert "@ts-nocheck" not in src, f"@ts-nocheck found in {fp}"


# [agent_config] pass_to_pass — AGENTS.md:146 @ 17d0be02f2800a2bc4524c7d5b587d7fd9f6f28c
def test_no_lint_suppressions():
    """Do not add inline lint suppressions by default (AGENTS.md:146)."""
    # Check the SSRF block (Bug 2 fix area) for new suppressions
    ssrf = _ssrf_block(MEDIA_TEST)
    for suppress in ["@ts-ignore", "@ts-expect-error", "eslint-disable", "oxlint-disable"]:
        assert suppress not in ssrf, (
            f"Lint suppression '{suppress}' added in SSRF test block"
        )

    # Check the new plugin definition area (Bug 1 fix area) in commands.test.ts
    src = _read(CMD_TEST)
    # Find the new plugin code (between telegramCommandTestPlugin definition and end)
    idx = src.find("telegramCommandTestPlugin")
    if idx != -1:
        plugin_area = src[idx:]
        for suppress in ["@ts-ignore", "@ts-expect-error"]:
            assert suppress not in plugin_area, (
                f"Lint suppression '{suppress}' added near plugin definition in commands.test.ts"
            )


# [agent_config] pass_to_pass — AGENTS.md:162 @ 17d0be02f2800a2bc4524c7d5b587d7fd9f6f28c
def test_no_prototype_mutation_in_tests():
    """In tests, prefer per-instance stubs over prototype mutation (AGENTS.md:162)."""
    for fp in [CMD_TEST, MEDIA_TEST]:
        for line in _code_lines(fp):
            assert not re.search(r"\.prototype\.\w+\s*=", line), (
                f"Prototype mutation found in {fp}: {line.strip()}"
            )
