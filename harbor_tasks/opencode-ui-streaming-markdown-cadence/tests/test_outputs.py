"""
Task: opencode-ui-streaming-markdown-cadence
Repo: anomalyco/opencode @ af2ccc94ebc632d0014f54ea5c5e6c2e26b5dda5
PR:   19404

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
FILE = f"{REPO}/packages/ui/src/components/message-part.tsx"


def _read_file() -> str:
    return Path(FILE).read_text()


def _util_section(src: str) -> str:
    """Return code before the first PART_MAPPING[ assignment (utility functions)."""
    parts = re.split(r"PART_MAPPING\s*\[", src)
    return parts[0] if parts else src


def _find_pacing_func(util: str) -> dict | None:
    """Find the pacing/throttle factory function (handles nested parens in TS types)."""
    # Match 'function NAME(' then balance parens for the full param list
    for m in re.finditer(r"function\s+(\w+)\s*\(", util):
        name = m.group(1)
        paren_start = m.end() - 1  # index of '('
        depth, i = 0, paren_start
        for i in range(paren_start, len(util)):
            if util[i] == "(":
                depth += 1
            elif util[i] == ")":
                depth -= 1
            if depth == 0:
                break
        params_str = util[paren_start + 1:i]
        # Find opening brace of body
        brace_match = re.search(r"\{", util[i:])
        if not brace_match:
            continue
        body_start = i + brace_match.start()
        depth, end = 0, body_start
        for j in range(body_start, len(util)):
            if util[j] == "{":
                depth += 1
            elif util[j] == "}":
                depth -= 1
            if depth == 0:
                end = j
                break
        body = util[body_start:end + 1]
        if "createSignal" in body and ("setTimeout" in body or "requestAnimationFrame" in body):
            return {"name": name, "params": params_str, "body": body}

    # Also check arrow functions
    for m in re.finditer(r"(?:const|let)\s+(\w+)\s*=\s*\(", util):
        name = m.group(1)
        paren_start = m.end() - 1
        depth, i = 0, paren_start
        for i in range(paren_start, len(util)):
            if util[i] == "(":
                depth += 1
            elif util[i] == ")":
                depth -= 1
            if depth == 0:
                break
        params_str = util[paren_start + 1:i]
        ctx = util[m.start():min(m.start() + 3000, len(util))]
        if "createSignal" in ctx and ("setTimeout" in ctx or "requestAnimationFrame" in ctx):
            return {"name": name, "params": params_str, "body": ctx}

    return None


def _added_lines() -> list[str]:
    """Return '+' lines from the agent's diff of message-part.tsx."""
    for ref in ("HEAD", "HEAD~1"):
        r = subprocess.run(
            ["git", "diff", ref, "--", "packages/ui/src/components/message-part.tsx"],
            capture_output=True, text=True, cwd=REPO, timeout=10,
        )
        if r.stdout.strip():
            return [l[1:] for l in r.stdout.splitlines()
                    if l.startswith("+") and not l.startswith("+++")]
    return []


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_valid():
    """message-part.tsx exists and has PART_MAPPING + createSignal markers."""
    src = _read_file()
    assert "PART_MAPPING" in src, "Missing PART_MAPPING in message-part.tsx"
    assert "createSignal" in src, "Missing createSignal in message-part.tsx"


# [static] pass_to_pass
def test_not_stub():
    """message-part.tsx must not be stubbed or truncated (>=100 lines)."""
    src = _read_file()
    assert len(src.splitlines()) >= 100, "File too short — likely stubbed"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_throttle_interval_reduced():
    """Render pacing interval must be <=50ms (old was 100ms)."""
    src = _read_file()
    util = _util_section(src)

    # Find all `const NAME = NUMBER` in utility section
    const_defs = {m.group(1): int(m.group(2))
                  for m in re.finditer(r"const\s+(\w+)\s*=\s*(\d+)", util)}

    # Find all setTimeout(fn, VALUE) references
    timeout_refs = [m.group(1) for m in re.finditer(
        r"setTimeout\s*\([^,]+,\s*(\w+|\d+)", util)]

    has_raf = "requestAnimationFrame" in util

    # Old throttle (>=80ms) must be gone
    for name, val in const_defs.items():
        if 80 <= val <= 150:
            is_timing = bool(re.search(
                r"throttle|interval|pace|tick|delay|render|ms|cadence", name, re.I))
            used_in_timeout = name in timeout_refs
            assert not (is_timing or used_in_timeout), \
                f"Old throttle constant {name}={val}ms still present"

    for ref in timeout_refs:
        try:
            val = int(ref)
            assert not (80 <= val <= 150), f"Old literal timeout value {val}ms"
        except ValueError:
            pass

    # Fast interval (<=50ms) or requestAnimationFrame must exist
    has_fast = has_raf
    for name, val in const_defs.items():
        if 0 < val <= 50:
            is_timing = bool(re.search(
                r"throttle|interval|pace|tick|delay|render|ms|cadence", name, re.I))
            used_in_timeout = name in timeout_refs
            if is_timing or used_in_timeout:
                has_fast = True
    for ref in timeout_refs:
        try:
            val = int(ref)
            if 0 < val <= 50:
                has_fast = True
        except ValueError:
            pass

    assert has_fast, "No fast interval (<=50ms) or requestAnimationFrame found"


# [pr_diff] fail_to_pass
def test_pacing_is_streaming_aware():
    """Pacing function must consider whether the stream is still active."""
    src = _read_file()
    util = _util_section(src)

    pacing_func = _find_pacing_func(util)
    assert pacing_func, "No pacing function found (needs createSignal + setTimeout/RAF)"

    params = [p.strip() for p in pacing_func["params"].split(",") if p.strip()]
    multi_params = len(params) >= 2
    body_refs_streaming = bool(re.search(
        r"\b(streaming|live|isStreaming|isLive|active|isActive|running|flushed|complete)\b",
        pacing_func["body"], re.I))

    # Check if called with multiple args in component section
    after_util = src[src.index("PART_MAPPING"):]
    called_with_args = bool(re.search(
        re.escape(pacing_func["name"]) + r"\s*\([^)]+,\s*[^)]+\)", after_util))

    assert multi_params or body_refs_streaming or called_with_args, \
        f"Pacing function not streaming-aware (params={len(params)})"


# [pr_diff] fail_to_pass
def test_incremental_reveal():
    """Text must be revealed in small increments, not dumped all at once."""
    src = _read_file()
    util = _util_section(src)

    signals = 0
    # 1. Substring extraction
    if re.search(r"\.(substring|slice|substr)\s*\(", util):
        signals += 1
    # 2. Position tracking variable with assignment
    if re.search(
        r"\b(pos|position|cursor|idx|start|offset|shown|revealed|current)\b"
        r"\s*(\+=|=\s*\w+\s*\+)",
        util,
    ):
        signals += 1
    # 3. Step/increment calculation with Math
    has_math = bool(re.search(r"Math\.(min|ceil|floor|max)\s*\(", util))
    has_step = bool(re.search(r"\b(step|increment|chunk|advance|stride)\b", util, re.I))
    if has_math and has_step:
        signals += 1
    # 4. Advance loop
    if re.search(r"for\s*\(\s*let\s+\w+\s*=\s*\w+\s*;\s*\w+\s*<", util):
        signals += 1

    assert signals >= 2, \
        f"Insufficient incremental reveal signals ({signals}/4, need >=2)"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — both components must use pacing
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_both_displays_use_pacing():
    """Both TextPartDisplay and ReasoningPartDisplay must use the pacing mechanism."""
    src = _read_file()
    util = _util_section(src)

    pacing_func = _find_pacing_func(util)
    assert pacing_func, "No pacing function found"
    pacing_name = pacing_func["name"]

    after_util = src[src.index("PART_MAPPING"):]

    # Extract text and reasoning component blocks
    text_block = re.search(
        r'PART_MAPPING\s*\[\s*[\'"]text[\'"]\s*\][\s\S]*?(?=PART_MAPPING\s*\[|$)',
        after_util)
    reasoning_block = re.search(
        r'PART_MAPPING\s*\[\s*[\'"]reasoning[\'"]\s*\][\s\S]*?(?=PART_MAPPING\s*\[|$)',
        after_util)

    assert text_block and pacing_name in text_block.group(0), \
        "TextPartDisplay does not use the pacing function"
    assert reasoning_block and pacing_name in reasoning_block.group(0), \
        "ReasoningPartDisplay does not use the pacing function"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:13 @ af2ccc94
def test_no_any_type():
    """Changed code must not introduce `any` type annotations (AGENTS.md:13)."""
    lines = _added_lines()
    # Match `: any` or `:any` but not in comments or strings like "anyth..."
    any_lines = [l for l in lines
                 if re.search(r":\s*any\b", l) and not l.strip().startswith("//")]
    assert len(any_lines) == 0, \
        f"Found {len(any_lines)} `any` type usage(s) in changed code"


# [agent_config] pass_to_pass — AGENTS.md:12 @ af2ccc94
def test_no_try_catch():
    """Changed code must avoid try/catch (AGENTS.md:12)."""
    lines = _added_lines()
    try_lines = [l for l in lines if re.search(r"\btry\s*\{", l)]
    assert len(try_lines) == 0, \
        f"Found {len(try_lines)} try/catch block(s) in changed code"


# [agent_config] pass_to_pass — AGENTS.md:84 @ af2ccc94
def test_no_else_blocks():
    """Changed code must avoid else statements (AGENTS.md:84)."""
    lines = _added_lines()
    else_lines = [l for l in lines
                  if re.search(r"\belse\b", l.strip())
                  and not l.strip().startswith("//")]
    assert len(else_lines) == 0, \
        f"Found {len(else_lines)} else statement(s) in changed code"


# [agent_config] pass_to_pass — packages/app/AGENTS.md:15 @ af2ccc94
def test_no_multiple_create_signals():
    """Pacing function must not use multiple createSignal calls; prefer createStore (packages/app/AGENTS.md:15)."""
    src = _read_file()
    util = _util_section(src)
    pacing_func = _find_pacing_func(util)
    if not pacing_func:
        return  # No pacing function found, nothing to check
    count = len(re.findall(r"\bcreateSignal\s*\(", pacing_func["body"]))
    assert count <= 1, \
        f"Pacing function uses {count} createSignal calls; use createStore for multiple signals (packages/app/AGENTS.md:15)"
