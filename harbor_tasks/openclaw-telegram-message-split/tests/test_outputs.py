"""
Task: openclaw-telegram-message-split
Repo: openclaw/openclaw @ 865160e57292bfc32082fa885efe1a48e64bb06c
PR:   56595

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/openclaw"
TARGET = "extensions/telegram/src/format.ts"


def _read_target() -> str:
    p = Path(REPO) / TARGET
    assert p.exists(), f"{TARGET} does not exist"
    return p.read_text()


# ---------------------------------------------------------------------------
# Behavioral test suite — single tsx invocation, results cached
# ---------------------------------------------------------------------------

_behavioral_cache: dict | None = None


def _run_behavioral_suite() -> dict:
    """Run all behavioral checks in one tsx process, return results dict."""
    global _behavioral_cache
    if _behavioral_cache is not None:
        return _behavioral_cache

    # Place script inside the telegram extension so relative import resolves correctly
    script = Path(REPO) / "extensions/telegram/src/_verify_split_behavior.ts"
    script.write_text(
        r"""
import { markdownToTelegramChunks } from "./format.js";

type Result = { pass: boolean; detail: string };
const results: Record<string, Result> = {};

function run(name: string, fn: () => boolean, detail: () => string) {
  try {
    const ok = fn();
    results[name] = { pass: ok, detail: detail() };
  } catch (e: any) {
    results[name] = { pass: false, detail: `Error: ${e.message}` };
  }
}

// F2P: word boundary split when HTML escaping shrinks window
// "alpha <<" → HTML "alpha &lt;&lt;" (14 chars). Limit 8 must split at "alpha " not "alph".
{
  const chunks = markdownToTelegramChunks("alpha <<", 8);
  const texts = chunks.map((c) => c.text);
  run(
    "word_boundary_escaped",
    () =>
      texts[0] === "alpha " &&
      texts.join("") === "alpha <<" &&
      chunks.every((c) => c.html.length <= 8),
    () => JSON.stringify(texts),
  );
}

// F2P: bold formatting preserved while splitting at word boundaries
// "**alpha <<**" → HTML "<b>alpha &lt;&lt;</b>" (24 chars). Limit 13 must split at "alpha ".
{
  const chunks = markdownToTelegramChunks("**alpha <<**", 13);
  const texts = chunks.map((c) => c.text);
  run(
    "formatted_word_boundary",
    () =>
      texts[0] === "alpha " &&
      texts.join("") === "alpha <<" &&
      chunks.every((c) => c.html.length <= 13),
    () => JSON.stringify(texts),
  );
}

// F2P: non-monotonic HTML from file ref wrapping
// "README.md" → <code>README.md</code> (22 chars), but "README.md<" partial slices
// can produce longer <a> tags. Must handle non-monotonic HTML length.
{
  const chunks = markdownToTelegramChunks("README.md<", 22);
  const texts = chunks.map((c) => c.text);
  run(
    "file_ref_non_monotonic",
    () =>
      texts[0] === "README.md" &&
      texts.join("") === "README.md<" &&
      chunks.every((c) => c.html.length <= 22),
    () => JSON.stringify({ texts, htmls: chunks.map((c) => c.html) }),
  );
}

// F2P: when tag overhead exceeds limit, return single chunk gracefully
// "**ab**" → "<b>ab</b>" (9 chars) > limit 6. Must return 1 chunk, not infinite loop.
{
  const chunks = markdownToTelegramChunks("**ab**", 6);
  run(
    "tag_overhead_graceful",
    () => chunks.length === 1 && chunks[0]?.text === "ab",
    () => JSON.stringify({ len: chunks.length, texts: chunks.map((c) => c.text) }),
  );
}

// P2P: hard split for single long word (works on both base and fix)
{
  const chunks = markdownToTelegramChunks("supercalifragilistic", 8);
  const texts = chunks.map((c) => c.text);
  run(
    "hard_split_long_word",
    () =>
      JSON.stringify(texts) ===
        JSON.stringify(["supercal", "ifragili", "stic"]) &&
      chunks.every((c) => c.html.length <= 8),
    () => JSON.stringify(texts),
  );
}

// P2P: existing prose splitting still works (pre-existing test in repo)
{
  const chunks = markdownToTelegramChunks("**Which of these**", 16);
  const texts = chunks.map((c) => c.text);
  run(
    "prose_split_still_works",
    () =>
      texts.join("") === "Which of these" &&
      chunks.every((c) => c.html.length <= 16),
    () => JSON.stringify(texts),
  );
}

console.log(JSON.stringify(results));
""".strip()
    )
    try:
        # Try pnpm exec tsx first, fall back to npx tsx, then global tsx
        cmds = [
            ["pnpm", "exec", "tsx", str(script)],
            ["npx", "--yes", "tsx", str(script)],
            ["tsx", str(script)],
        ]
        for cmd in cmds:
            r = subprocess.run(
                cmd,
                cwd=REPO,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if r.returncode == 0:
                for line in reversed(r.stdout.strip().splitlines()):
                    try:
                        _behavioral_cache = json.loads(line)
                        return _behavioral_cache
                    except json.JSONDecodeError:
                        continue
        # All commands failed — report last error
        _behavioral_cache = {
            "_error": f"tsx failed (rc={r.returncode}):\n{r.stderr[:500]}\n{r.stdout[:500]}"
        }
    except subprocess.TimeoutExpired:
        _behavioral_cache = {"_error": "tsx timed out after 120s"}
    finally:
        script.unlink(missing_ok=True)

    return _behavioral_cache


def _get_result(key: str) -> dict:
    results = _run_behavioral_suite()
    assert "_error" not in results, f"Behavioral suite failed: {results['_error']}"
    assert key in results, f"Test '{key}' missing from behavioral results"
    return results[key]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_file_exists():
    """Target file exists and is non-empty."""
    src = _read_target()
    assert len(src) > 500, "File suspiciously short"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_word_boundary_split_escaped_html():
    """'alpha <<' at limit 8 splits at word boundary ('alpha '), not mid-word."""
    r = _get_result("word_boundary_escaped")
    assert r["pass"], f"Expected first chunk 'alpha ', got: {r['detail']}"


# [pr_diff] fail_to_pass
def test_formatted_word_boundary_split():
    """'**alpha <<**' at limit 13 preserves bold formatting and splits at word boundary."""
    r = _get_result("formatted_word_boundary")
    assert r["pass"], f"Expected first chunk 'alpha ', got: {r['detail']}"


# [pr_diff] fail_to_pass
def test_file_ref_non_monotonic_split():
    """'README.md<' at limit 22 handles non-monotonic HTML from file ref wrapping."""
    r = _get_result("file_ref_non_monotonic")
    assert r["pass"], f"File ref split incorrect: {r['detail']}"


# [pr_diff] fail_to_pass
def test_tag_overhead_returns_single_chunk():
    """'**ab**' at limit 6 returns 1 chunk when tag overhead exceeds limit."""
    r = _get_result("tag_overhead_graceful")
    assert r["pass"], f"Expected 1 chunk with text 'ab', got: {r['detail']}"


# [pr_diff] fail_to_pass
def test_proportional_estimate_removed():
    """The proportional estimate variable that caused mid-word splits is removed."""
    src = _read_target()
    assert "proportionalLimit" not in src, "proportionalLimit variable still present"
    assert "(currentTextLength * htmlLimit)" not in src, (
        "Proportional calculation still present"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — behavioral regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_hard_split_single_word():
    """'supercalifragilistic' at limit 8 hard-splits into correct chunks."""
    r = _get_result("hard_split_long_word")
    assert r["pass"], f"Expected ['supercal','ifragili','stic'], got: {r['detail']}"


# [pr_diff] pass_to_pass
def test_prose_split_regression():
    """'**Which of these**' at limit 16 still splits correctly (pre-existing behavior)."""
    r = _get_result("prose_split_still_works")
    assert r["pass"], f"Prose split broken: {r['detail']}"


# [static] pass_to_pass
def test_not_stub():
    """Modified file has real split logic, not a stub."""
    src = _read_target()
    lines = [
        l
        for l in src.splitlines()
        if l.strip() and not l.strip().startswith("//")
    ]
    assert len(lines) > 200, f"File too short ({len(lines)} lines) — likely a stub"
    assert "splitTelegramChunkByHtmlLimit" in src
    assert "renderTelegramChunkHtml" in src
    assert "sliceMarkdownIR" in src


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md rules
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — AGENTS.md:16 @ 865160e57292bfc32082fa885efe1a48e64bb06c
def test_no_cross_boundary_imports():
    """Extension code must not import core internals directly (AGENTS.md:16)."""
    ext_dir = Path(REPO) / "extensions" / "telegram" / "src"
    if not ext_dir.exists():
        return
    violations = []
    for ts_file in ext_dir.rglob("*.ts"):
        if ts_file.name.endswith(".test.ts") or ts_file.name.endswith(".d.ts"):
            continue
        content = ts_file.read_text()
        for i, line in enumerate(content.splitlines(), 1):
            if 'from "' in line or "from '" in line:
                if "../../../src/" in line or "../../src/plugin-sdk-internal/" in line:
                    violations.append(
                        f"{ts_file.relative_to(Path(REPO))}:{i}: {line.strip()}"
                    )
    assert not violations, "Cross-boundary imports found:\n" + "\n".join(violations)


# [agent_config] pass_to_pass — AGENTS.md:104 @ 865160e57292bfc32082fa885efe1a48e64bb06c
def test_no_lint_suppressions():
    """No @ts-nocheck, @ts-ignore, or inline lint suppressions (AGENTS.md:104)."""
    src = _read_target()
    for pattern in ["@ts-nocheck", "@ts-ignore", "eslint-disable", "oxlint-disable"]:
        assert pattern not in src, f"Lint suppression '{pattern}' found in {TARGET}"


# [agent_config] pass_to_pass — AGENTS.md:105 @ 865160e57292bfc32082fa885efe1a48e64bb06c
def test_no_explicit_any():
    """No 'any' type annotations or no-explicit-any disabling (AGENTS.md:105)."""
    src = _read_target()
    assert "no-explicit-any" not in src, f"Disabled no-explicit-any rule in {TARGET}"
    for i, line in enumerate(src.splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        if re.search(r":\s*any\b", line):
            assert False, f"Explicit 'any' type at {TARGET}:{i}: {line.strip()}"


# [agent_config] pass_to_pass — AGENTS.md:108 @ 865160e57292bfc32082fa885efe1a48e64bb06c
def test_no_self_import_via_plugin_sdk():
    """Extension must not import itself via openclaw/plugin-sdk/telegram (AGENTS.md:108)."""
    ext_dir = Path(REPO) / "extensions" / "telegram" / "src"
    if not ext_dir.exists():
        return
    for ts_file in ext_dir.rglob("*.ts"):
        if ts_file.name.endswith(".test.ts") or ts_file.name.endswith(".d.ts"):
            continue
        content = ts_file.read_text()
        assert "openclaw/plugin-sdk/telegram" not in content, (
            f"Self-import via plugin-sdk found in {ts_file.relative_to(Path(REPO))}"
        )


# [agent_config] pass_to_pass — AGENTS.md:111 @ 865160e57292bfc32082fa885efe1a48e64bb06c
def test_no_prototype_mutation():
    """No prototype mutation patterns (AGENTS.md:111)."""
    src = _read_target()
    assert "applyPrototypeMixins" not in src, "applyPrototypeMixins found in target"
    for i, line in enumerate(src.splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        if ".prototype." in line and ("=" in line or "defineProperty" in line):
            assert False, f"Prototype mutation at {TARGET}:{i}: {stripped}"
