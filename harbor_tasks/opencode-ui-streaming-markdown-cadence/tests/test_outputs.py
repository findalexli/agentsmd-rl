"""
Task: opencode-ui-streaming-markdown-cadence
Repo: anomalyco/opencode @ af2ccc94ebc632d0014f54ea5c5e6c2e26b5dda5
PR:   19404

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
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


# [repo_tests] pass_to_pass — CI typecheck validation
def test_repo_typecheck():
    """Repo TypeScript files have valid syntax (basic structural check)."""
    # Since bun/tsgo are not available in the Docker image, we do a basic
    # structural validation: check for balanced braces in the file
    src = _read_file()

    # Check basic TypeScript structural indicators
    assert "export" in src, "Missing export statements"
    assert "import" in src, "Missing import statements"

    # Check for balanced braces (basic sanity check) - most reliable check
    open_braces = src.count("{")
    close_braces = src.count("}")
    assert open_braces > 0, "No braces found in file"
    assert open_braces == close_braces, f"Unbalanced braces: {open_braces} open vs {close_braces} close"

    # Check for balanced brackets (used for array types and PART_MAPPING)
    open_brackets = src.count("[")
    close_brackets = src.count("]")
    bracket_diff = abs(open_brackets - close_brackets)
    assert bracket_diff <= 2, f"Unbalanced brackets: {open_brackets} open vs {close_brackets} close (diff: {bracket_diff})"

    # Check parentheses - allow for small differences due to complex JSX,
    # generic types, and arrow functions in TypeScript/TSX files
    open_parens = src.count("(")
    close_parens = src.count(")")
    assert open_parens > 0, "No parentheses found in file"
    # Allow up to 5 unbalanced parens due to complex TypeScript/TSX syntax
    paren_diff = abs(open_parens - close_parens)
    assert paren_diff <= 5, f"Too many unbalanced parentheses: {open_parens} open vs {close_parens} close (diff: {paren_diff})"


# [repo_tests] pass_to_pass — verify required imports exist
def test_repo_required_imports():
    """message-part.tsx has required SolidJS imports for pacing implementation."""
    src = _read_file()

    # Required imports for the pacing functionality
    required = ["createSignal", "createEffect", "onCleanup", "createMemo"]
    missing = [imp for imp in required if imp not in src]
    assert len(missing) == 0, f"Missing required imports: {missing}"


# [repo_tests] pass_to_pass — verify PART_MAPPING structure is valid
def test_repo_part_mapping_structure():
    """PART_MAPPING object has valid structure with expected keys."""
    src = _read_file()

    # Check PART_MAPPING exists and has the expected structure
    assert "PART_MAPPING" in src, "PART_MAPPING not found"

    # Check for expected part types (text and reasoning are the ones modified in PR)
    assert 'PART_MAPPING["text"]' in src or "PART_MAPPING['text']" in src, "text part mapping missing"
    assert 'PART_MAPPING["reasoning"]' in src or "PART_MAPPING['reasoning']" in src, "reasoning part mapping missing"


# [repo_tests] pass_to_pass — CI typecheck: verify valid TypeScript/TSX structure
def test_repo_tsx_valid_syntax():
    """Repo TSX files have valid syntax (proper JSX structure)."""
    src = _read_file()

    # Check for valid JSX tag structure (equal number of opening and closing patterns)
    # Count JSX opening tags (simplified check for common patterns)
    jsx_open = len(re.findall(r'<[A-Z][a-zA-Z0-9_]*', src))  # Component tags
    jsx_close = len(re.findall(r'</[A-Z][a-zA-Z0-9_]*>', src))  # Closing component tags

    # Allow for self-closing tags and fragments - just verify basic JSX structure
    # Check that JSX expressions are balanced
    jsx_expr_open = src.count('{')
    jsx_expr_close = src.count('}')
    assert jsx_expr_open == jsx_expr_close, f"Unbalanced JSX expressions: {jsx_expr_open} open vs {jsx_expr_close} close"

    # Verify valid TypeScript keywords and constructs
    assert "export" in src or "import" in src, "Missing import/export statements"
    assert "=>" in src or "function" in src, "Missing function definitions"


# [repo_tests] pass_to_pass — CI lint: verify no obvious code issues
def test_repo_lint_basic():
    """Basic lint checks pass (no trailing whitespace, valid indentation)."""
    src = _read_file()
    lines = src.splitlines()

    # Check for trailing whitespace (common lint rule)
    for i, line in enumerate(lines, 1):
        if line != line.rstrip():
            assert False, f"Line {i} has trailing whitespace"

    # Check for tabs vs spaces consistency (use spaces for indentation)
    tab_lines = [i for i, line in enumerate(lines, 1) if line.startswith('\t')]
    if tab_lines:
        # Allow tabs if the whole file uses them consistently
        space_indent_lines = [i for i, line in enumerate(lines, 1)
                             if line.startswith(' ') and line.strip()]
        if space_indent_lines and tab_lines:
            assert False, f"Mixed indentation: tabs on lines {tab_lines[:3]}, spaces on lines {space_indent_lines[:3]}"


# [repo_tests] pass_to_pass — CI build: verify imports resolve
def test_repo_imports_resolve():
    """All imports in message-part.tsx use valid, resolvable paths."""
    src = _read_file()

    # Find all import statements
    import_pattern = r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]'
    imports = re.findall(import_pattern, src)

    # Check that imports use valid patterns
    valid_patterns = [
        r'^solid-js',           # solid-js imports
        r'^@opencode-ai/',      # workspace imports
        r'^@/',                 # path aliases
        r'^\./',                # relative imports
        r'^\.\./',              # parent imports
        r'^marked',             # marked library
        r'^dompurify',          # dompurify library
        r'^morphdom',           # morphdom library
        r'^@shikijs/',          # shiki transformers
        r'^katex',              # katex library
        r'^@pierre/diffs',      # pierre diffs
        r'^strip-ansi',         # strip-ansi library
        r'^motion',            # motion library
        r'^motion-',          # motion-dom, motion-utils
        r'^@solidjs/',        # @solidjs/router, @solidjs/meta
    ]

    for imp in imports:
        is_valid = any(re.match(pattern, imp) for pattern in valid_patterns)
        assert is_valid, f"Import '{imp}' does not match any valid import pattern"


# [repo_tests] pass_to_pass — CI typecheck: verify component signatures
def test_repo_component_signatures():
    """Component functions have valid TypeScript signatures."""
    src = _read_file()

    # Find component definitions in PART_MAPPING
    component_pattern = r'PART_MAPPING\[[\'"](\w+)[\'"]\]\s*=\s*function\s+(\w+)\s*\(([^)]*)\)'
    components = re.findall(component_pattern, src)

    for part_type, func_name, params in components:
        # Check that function has props parameter
        if not params.strip():
                    continue
        assert 'props' in params, f"Component {func_name} missing props parameter"

        # Check that component returns JSX (has return statement or JSX)
        # Find the function body (simplified - look after the signature)
        func_start = src.find(f'PART_MAPPING["{part_type}"] = function {func_name}')
        if func_start == -1:
            func_start = src.find(f"PART_MAPPING['{part_type}'] = function {func_name}")

        if func_start != -1:
            # Look for return statement in the next 2000 chars (arbitrary limit for component body)
            func_section = src[func_start:func_start + 2000]
            has_return = 'return' in func_section or '<' in func_section
            assert has_return, f"Component {func_name} missing return statement"


# [repo_tests] pass_to_pass — TypeScript typecheck using tsgo
def test_repo_tsgo_typecheck():
    """TypeScript typecheck passes using repo's tsgo (pass_to_pass)."""
    # Install bun and dependencies in one session
    script = """
apt-get update -qq && apt-get install -y -qq unzip 2>/dev/null
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"
if ! command -v bun &> /dev/null; then
    curl -fsSL https://bun.sh/install | bash
fi
export PATH="$HOME/.bun/bin:$PATH"
cd /workspace/opencode && bun install 2>&1 | tail -5
cd /workspace/opencode/packages/ui && ./node_modules/.bin/tsgo --noEmit 2>&1
exit $?
"""
    r = subprocess.run(
        ["bash", "-c", script],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"tsgo typecheck failed: stderr={r.stderr[-1000:]} stdout={r.stdout[-1000:]}"


# [repo_tests] pass_to_pass — Prettier format check
def test_repo_prettier_check():
    """Code formatting passes using repo's prettier config (pass_to_pass)."""
    # Install bun and run prettier in one session
    script = """
apt-get update -qq && apt-get install -y -qq unzip 2>/dev/null
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"
if ! command -v bun &> /dev/null; then
    curl -fsSL https://bun.sh/install | bash
fi
export PATH="$HOME/.bun/bin:$PATH"
cd /workspace/opencode && bun install 2>&1 | tail -5
./node_modules/.bin/prettier --check packages/ui/src/components/message-part.tsx 2>&1
exit $?
"""
    r = subprocess.run(
        ["bash", "-c", script],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed: stderr={r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Bun unit tests for UI package
def test_repo_unit_tests():
    """Unit tests for UI package pass using bun test (pass_to_pass)."""
    # Install bun and run tests in one session
    script = """
apt-get update -qq && apt-get install -y -qq unzip 2>/dev/null
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"
if ! command -v bun &> /dev/null; then
    curl -fsSL https://bun.sh/install | bash
fi
export PATH="$HOME/.bun/bin:$PATH"
cd /workspace/opencode && bun install 2>&1 | tail -5
cd /workspace/opencode/packages/ui && bun test 2>&1
exit $?
"""
    r = subprocess.run(
        ["bash", "-c", script],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed: stderr={r.stderr[-1000:]} stdout={r.stdout[-1000:]}"


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

    pacing_func = _find_pacing_func(util)
    if not pacing_func:
        assert False, "No pacing function found — cannot check incremental reveal"

    body = pacing_func["body"]

    signals = 0
    # 1. Substring extraction inside the pacing function
    if re.search(r"\.(substring|slice|substr)\s*\(", body):
        signals += 1
    # 2. Position tracking variable with assignment
    if re.search(
        r"\b(pos|position|cursor|idx|start|offset|shown|revealed|current)\b"
        r"\s*(\+=|=\s*\w+\s*+)",
        body,
    ):
        signals += 1
    # 3. Step/increment calculation with Math
    has_math = bool(re.search(r"Math\.(min|ceil|floor|max)\s*\(", body))
    has_step = bool(re.search(r"\b(step|increment|chunk|advance|stride)\b", body, re.I))
    if has_math and has_step:
        signals += 1
    # 4. Advance loop
    if re.search(r"for\s*\(\s*let\s+\w+\s*=\s*\w+\s*;\s*\w+\s*<", body):
        signals += 1

    assert signals >= 2, \
        f"Insufficient incremental reveal signals ({signals}/4, need >=2)"


# [pr_diff] fail_to_pass
def test_pacing_algorithm_behavior():
    """Pacing helper functions execute correctly, producing bounded incremental reveals."""
    src = _read_file()
    util = _util_section(src)

    # Extract pure helper functions that use Math (pacing calculations)
    # Skip functions that use SolidJS primitives (createSignal, etc.)
    solid_kws = {"createSignal", "createEffect", "onCleanup", "createMemo",
                 "createStore", "setValue"}

    helpers = []
    for m in re.finditer(r"function\s+(\w+)\s*\(", util):
        name = m.group(1)
        brace = util.find("{", m.end())
        if brace == -1:
            continue
        depth, end = 0, brace
        for i in range(brace, len(util)):
            if util[i] == "{":
                depth += 1
            elif util[i] == "}":
                depth -= 1
            if depth == 0:
                end = i
                break
        full = util[m.start():end + 1]
        body = util[brace:end + 1]
        if any(kw in body for kw in solid_kws):
            continue
        if not re.search(r"Math\.", body):
            continue
        helpers.append((name, full))

    assert len(helpers) >= 1, \
        "No Math-based pacing helper functions found in utility section"

    # Extract relevant const declarations (regexes and numbers used by helpers)
    consts = re.findall(
        r"(const\s+\w+\s*=\s*(?:/[^\n]+?/[gimsuy]*|\d+)\s*;?)", util
    )

    # Strip TypeScript type annotations for plain Node.js execution
    def _strip(code):
        return re.sub(r":\s*(?:number|string|boolean|RegExp)\b", "", code)

    # Classify helpers by parameter count
    step_fns, advance_fns = [], []
    for name, code in helpers:
        pm = re.search(r"\(([^)]*)\)", code)
        n = len([p for p in pm.group(1).split(",") if p.strip()]) if pm else 0
        (step_fns if n <= 1 else advance_fns).append(name)

    # Build Node.js test script
    parts = [_strip(c) for c in consts] + [_strip(fn) for _, fn in helpers]
    parts.append("const R = {};")

    for name in step_fns:
        parts.append(f'R["{name}"] = [1,5,20,50,100,500].map(n => {name}(n));')
        parts.append(
            f'R["{name}_ok"] = R["{name}"].every('
            f"v => typeof v === 'number' && v > 0 && v <= 50);"
        )

    for name in advance_fns:
        loop_body = "{ const np = %s(t, p); if (np <= p) break; p = np; ps.push(p); }" % name
        parts.append(
            "{\n"
            '  const t = "Hello, world! This is a test of incremental text streaming.";\n'
            "  let p = 0; const ps = [0]; let s = 0;\n"
            "  while (p < t.length && s++ < 300) " + loop_body + "\n"
            '  R["' + name + '_n"] = ps.length;\n'
            '  R["' + name + '_end"] = ps[ps.length - 1] >= t.length;\n'
            '  R["' + name + '_inc"] = ps.length >= 4;\n'
            '  R["' + name + '_mono"] = ps.every((v, i) => i === 0 || v > ps[i - 1]);\n'
            "}"
        )

    parts.append("console.log(JSON.stringify(R));")

    script_path = Path(REPO) / "_eval_pacing_test.mjs"
    script_path.write_text("\n".join(parts))
    try:
        r = subprocess.run(
            ["node", str(script_path)],
            capture_output=True, text=True, timeout=10, cwd=REPO,
        )
        assert r.returncode == 0, f"Pacing helpers failed to execute: {r.stderr[:500]}"
        data = json.loads(r.stdout.strip())

        for name in step_fns:
            assert data.get(f"{name}_ok"), \
                f"{name}() returned out-of-range step sizes: {data.get(name)}"
        for name in advance_fns:
            assert data.get(f"{name}_end"), \
                f"{name}() didn't reach end of text"
            assert data.get(f"{name}_inc"), \
                f"{name}() not incremental enough ({data.get(f'{name}_n', '?')} steps)"
            assert data.get(f"{name}_mono"), \
                f"{name}() positions not monotonically increasing"
    finally:
        script_path.unlink(missing_ok=True)


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

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_unit_run_unit_tests():
    """pass_to_pass | CI job 'unit' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun turbo test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_run_app_e2e_tests():
    """pass_to_pass | CI job 'e2e' → step 'Run app e2e tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun --cwd packages/app test:e2e:local'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run app e2e tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_storybook_build_build_storybook():
    """pass_to_pass | CI job 'storybook build' → step 'Build Storybook'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun --cwd packages/storybook build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build Storybook' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_typecheck_run_typecheck():
    """pass_to_pass | CI job 'typecheck' → step 'Run typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")