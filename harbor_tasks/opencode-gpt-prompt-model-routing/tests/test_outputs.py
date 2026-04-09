"""
Task: opencode-gpt-prompt-model-routing
Repo: anomalyco/opencode @ 17e8f577d681db858c7a24db2c91d1b45b7b85c9
PR:   19220

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
SYSTEM_TS = f"{REPO}/packages/opencode/src/session/system.ts"
PROMPT_DIR = f"{REPO}/packages/opencode/src/session/prompt"


def _run_bun(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute TypeScript code via bun in the repo directory."""
    script = Path(REPO) / "_eval_tmp.ts"
    script.write_text(code)
    try:
        return subprocess.run(
            ["bun", "run", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Routing harness — patches system.ts imports, runs with bun, returns mapping
# ---------------------------------------------------------------------------

_ROUTE_CACHE = None


def _get_routes():
    """Build routing test harness and return {model_id: prompt_marker} dict."""
    global _ROUTE_CACHE
    if _ROUTE_CACHE is not None:
        return _ROUTE_CACHE

    src = Path(SYSTEM_TS).read_text()

    # Extract the provider function body via brace matching
    match = re.search(r"function\s+provider\s*\([^)]*\)\s*\{", src)
    assert match, "provider function not found in system.ts"
    start = match.start()
    brace = src.index("{", match.start())
    depth = 0
    end = brace
    for i in range(brace, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
        if depth == 0:
            end = i + 1
            break
    func_body = src[start:end]

    # Collect all prompt imports and create const markers
    prompt_consts = []
    for m in re.finditer(
        r'import\s+(\w+)\s+from\s+["\']\.\/prompt\/([\w.-]+?)(?:\.txt)?["\']',
        src,
    ):
        var_name = m.group(1)
        file_name = m.group(2).upper().replace(".", "_").replace("-", "_")
        prompt_consts.append(f'const {var_name} = "__PROMPT_{file_name}__";')

    models = json.dumps([
        "gpt-5.4", "gpt-5", "gpt-3.5-turbo",
        "gpt-codex-test",
        "gpt-4o", "o1-mini", "o3-mini",
        "gemini-2.0-flash", "claude-sonnet-4-20250514",
    ])

    harness = "\n".join(prompt_consts) + "\n\n" + func_body + f"""

;(() => {{
  const R: Record<string, string> = {{}};
  const models = {models};
  for (const id of models) {{
    try {{
      const r = provider({{ api: {{ id }} }});
      R[id] = Array.isArray(r) && r.length > 0 ? String(r[0])
            : typeof r === "string" ? r
            : "NO_RESULT";
    }} catch (e: any) {{
      R[id] = "ERROR:" + (e?.message?.slice(0, 80) ?? "");
    }}
  }}
  console.log(JSON.stringify(R));
}})();
"""

    Path("/tmp/patched_system.ts").write_text(harness)
    result = subprocess.run(
        ["bun", "run", "/tmp/patched_system.ts"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Routing harness failed:\n{result.stderr}"
    _ROUTE_CACHE = json.loads(result.stdout.strip())
    return _ROUTE_CACHE


def _route(model_id):
    """Get the prompt marker for a model ID, uppercased for comparison."""
    routes = _get_routes()
    val = routes.get(model_id, "MISSING")
    assert val not in ("MISSING", "NO_PROVIDER", "NO_RESULT"), (
        f"Routing harness returned {val!r} for {model_id}"
    )
    assert not val.startswith("ERROR:"), f"Routing error for {model_id}: {val}"
    return val


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_system_ts_parseable():
    """system.ts must be valid TypeScript that bun can parse."""
    # Check that system.ts transpiles without syntax errors
    result = subprocess.run(
        ["bun", "build", "--no-bundle", SYSTEM_TS],
        capture_output=True, text=True, timeout=30,
    )
    # bun build to stdout succeeds if it can parse; check for transpile output
    assert "error" not in result.stderr.lower() or result.returncode == 0, (
        f"system.ts failed to parse:\n{result.stderr}"
    )
    assert len(result.stdout.strip()) > 0, "system.ts produced no transpile output"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_generic_gpt_not_codex():
    """Generic GPT models (gpt-5.4, gpt-5, gpt-3.5-turbo) must NOT get codex prompt."""
    for model_id in ("gpt-5.4", "gpt-5", "gpt-3.5-turbo"):
        prompt = _route(model_id)
        assert "CODEX" not in prompt.upper(), (
            f"{model_id} routed to codex prompt: {prompt}"
        )


# [pr_diff] fail_to_pass
def test_generic_gpt_gets_dedicated_prompt():
    """Generic GPT models must get a dedicated GPT prompt (containing 'GPT' in the marker)."""
    for model_id in ("gpt-5.4", "gpt-5"):
        prompt = _route(model_id)
        # Must route to a GPT-specific prompt, not codex/default/beast/etc.
        assert "GPT" in prompt.upper(), (
            f"{model_id} not routed to a GPT-dedicated prompt: {prompt}"
        )


# [pr_diff] fail_to_pass
def test_gpt_prompt_file_exists():
    """GPT prompt file must exist and be importable by bun with real content."""
    r = _run_bun("""
import p from "./packages/opencode/src/session/prompt/gpt.txt"
console.log(p.length)
""")
    assert r.returncode == 0, f"gpt.txt not importable via bun: {r.stderr}"
    length = int(r.stdout.strip())
    assert length >= 50, f"GPT prompt too short ({length} chars)"


# [pr_diff] fail_to_pass
def test_gpt_codex_routes_differ():
    """Generic GPT (gpt-5.4) and codex GPT (gpt-codex-test) must route to different prompts."""
    gpt_prompt = _route("gpt-5.4")
    codex_prompt = _route("gpt-codex-test")
    assert gpt_prompt != codex_prompt, (
        f"gpt-5.4 and gpt-codex-test both route to: {gpt_prompt}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression tests
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_codex_model_gets_codex():
    """Models with 'codex' in their ID must still receive the codex prompt."""
    # Only models with both "gpt" and "codex" in ID hit the codex sub-branch
    prompt = _route("gpt-codex-test")
    assert "CODEX" in prompt.upper(), (
        f"gpt-codex-test should get codex prompt but got: {prompt}"
    )


# [pr_diff] pass_to_pass
def test_existing_routing_preserved():
    """gpt-4o, gemini, and claude must still route to their correct prompts."""
    routes = _get_routes()

    gpt4 = routes.get("gpt-4o", "")
    assert "BEAST" in gpt4.upper(), f"gpt-4o expected BEAST, got: {gpt4}"

    gemini = routes.get("gemini-2.0-flash", "")
    assert "GEMINI" in gemini.upper(), f"gemini expected GEMINI, got: {gemini}"

    claude = routes.get("claude-sonnet-4-20250514", "")
    assert "ANTHROPIC" in claude.upper(), f"claude expected ANTHROPIC, got: {claude}"


# [pr_diff] fail_to_pass
def test_gpt_prompt_distinct_from_codex():
    """GPT prompt must not be a near-copy of codex (verified via bun execution)."""
    r = _run_bun("""
import gpt from "./packages/opencode/src/session/prompt/gpt.txt"
import codex from "./packages/opencode/src/session/prompt/codex.txt"
// Line-level Jaccard similarity
const gLines = new Set(gpt.split("\\n"))
const cLines = new Set(codex.split("\\n"))
let shared = 0
for (const l of gLines) if (cLines.has(l)) shared++
const union = new Set([...gLines, ...cLines]).size
const sim = union > 0 ? shared / union : 0
console.log(sim.toFixed(4))
""")
    assert r.returncode == 0, f"Prompt comparison failed: {r.stderr}"
    sim = float(r.stdout.strip())
    assert sim <= 0.90, (
        f"GPT prompt too similar to codex (line Jaccard: {sim:.2f})"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repository CI/CD tests
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "turbo", "typecheck"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_session_tests():
    """Repo's session tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "--timeout", "30000", "test/session/"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"Session tests failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — AGENTS.md:13 @ 17e8f577d681db858c7a24db2c91d1b45b7b85c9
def test_no_any_type():
    """system.ts must not use the 'any' type annotation (AGENTS.md rule)."""
    src = Path(SYSTEM_TS).read_text()
    # Strip comments to avoid false positives
    src = re.sub(r"//.*$", "", src, flags=re.MULTILINE)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    matches = re.findall(r":\s*any\b", src)
    assert len(matches) == 0, f"Found {len(matches)} uses of ': any' in system.ts"


# [agent_config] pass_to_pass — AGENTS.md:84 @ 17e8f577d681db858c7a24db2c91d1b45b7b85c9
def test_no_else_in_provider():
    """provider() must not use else statements (AGENTS.md rule: prefer early returns)."""
    src = Path(SYSTEM_TS).read_text()
    # Extract provider function body via brace matching
    start = src.find("function provider")
    assert start != -1, "provider function not found in system.ts"
    brace = src.index("{", start)
    depth = 0
    end = brace
    for i in range(brace, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
        if depth == 0:
            end = i + 1
            break
    body = src[brace:end]
    assert not re.search(r"\belse\b", body), "provider() uses else statements"


# [agent_config] pass_to_pass — AGENTS.md:70 @ 17e8f577d681db858c7a24db2c91d1b45b7b85c9
def test_no_let_in_system_ts():
    """system.ts must prefer const over let (AGENTS.md rule)."""
    src = Path(SYSTEM_TS).read_text()
    # Strip comments
    src_clean = re.sub(r"//.*$", "", src, flags=re.MULTILINE)
    src_clean = re.sub(r"/\*.*?\*/", "", src_clean, flags=re.DOTALL)
    matches = re.findall(r"\blet\b", src_clean)
    assert len(matches) == 0, f"Found {len(matches)} uses of 'let' in system.ts — prefer const"


# [agent_config] pass_to_pass — AGENTS.md:12 @ 17e8f577d681db858c7a24db2c91d1b45b7b85c9
def test_no_try_catch_in_system_ts():
    """system.ts must not use try/catch blocks (AGENTS.md rule)."""
    src = Path(SYSTEM_TS).read_text()
    # Strip comments
    src_clean = re.sub(r"//.*$", "", src, flags=re.MULTILINE)
    src_clean = re.sub(r"/\*.*?\*/", "", src_clean, flags=re.DOTALL)
    matches = re.findall(r"\btry\s*\{", src_clean)
    assert len(matches) == 0, f"Found {len(matches)} try/catch block(s) in system.ts — avoid try/catch where possible"


# [agent_config] pass_to_pass — AGENTS.md:17 @ 17e8f577d681db858c7a24db2c91d1b45b7b85c9
def test_no_for_loops_in_system_ts():
    """system.ts must prefer functional array methods over for loops (AGENTS.md rule)."""
    src = Path(SYSTEM_TS).read_text()
    # Strip comments
    src_clean = re.sub(r"//.*$", "", src, flags=re.MULTILINE)
    src_clean = re.sub(r"/\*.*?\*/", "", src_clean, flags=re.DOTALL)
    matches = re.findall(r"\bfor\s*\(", src_clean)
    assert len(matches) == 0, f"Found {len(matches)} for loop(s) in system.ts — prefer flatMap/filter/map"
