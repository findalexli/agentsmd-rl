"""
Task: opencode-slash-cmd-image-preserve
Repo: anomalyco/opencode @ 47d2ab120a4fbc92e72aca4d5b40d722d0e4d2be
PR:   #19771

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/opencode"
TARGET = "packages/app/src/components/prompt-input.tsx"
TARGET_PATH = f"{REPO}/{TARGET}"

# ---------------------------------------------------------------------------
# JS helper: extract handleSlashSelect, transpile, run in VM with mocks
# ---------------------------------------------------------------------------

_HELPER_JS = textwrap.dedent("""\
const vm = require("vm");
const ts = require("typescript");
const fs = require("fs");

const src = fs.readFileSync(process.env.TARGET_PATH, "utf8");

// --- Extract handleSlashSelect function body ---
const fnIdx = src.indexOf("handleSlashSelect");
if (fnIdx === -1) {
  console.log(JSON.stringify({ error: "handleSlashSelect not found" }));
  process.exit(1);
}
const eqIdx = src.indexOf("=", fnIdx);
const parenIdx = src.indexOf("(", eqIdx);
const closeParenIdx = src.indexOf(")", parenIdx);
const rawParam = src.slice(parenIdx + 1, closeParenIdx);
const param = rawParam.replace(/\\s*\\??\\s*:\\s*[^,)]+/g, "").trim() || "cmd";
const arrowIdx = src.indexOf("=>", closeParenIdx);
const bodyStart = src.indexOf("{", arrowIdx);

let depth = 0, i = bodyStart;
while (i < src.length) {
  const ch = src[i];
  if (ch === "'" || ch === '"' || ch === "`") {
    const q = ch; i++;
    while (i < src.length) { if (src[i] === "\\\\") i++; else if (src[i] === q) break; i++; }
  } else if (ch === "{") depth++;
  else if (ch === "}") { depth--; if (depth === 0) break; }
  i++;
}
const fnBody = src.slice(bodyStart, i + 1);
const wrapped = "function handleSlashSelect(" + param + ") " + fnBody;
const result = ts.transpileModule(wrapped, {
  compilerOptions: { target: ts.ScriptTarget.ES2020, module: ts.ModuleKind.CommonJS }
});
const fnCode = result.outputText;

// --- Mock context factory ---
function createCtx(images, overrides) {
  let promptSetArgs = null;
  let closePopoverCalled = false;
  let focusCalled = false;
  let triggerArgs = null;
  let setEditorTextArg = null;
  let clearEditorCalled = false;

  const ctx = {
    imageAttachments: () => [...images],
    closePopover: () => { closePopoverCalled = true; },
    setEditorText: (t) => { setEditorTextArg = t; },
    focusEditorEnd: () => { focusCalled = true; },
    prompt: { set: function() { promptSetArgs = Array.from(arguments); } },
    promptProbe: { select: () => {} },
    DEFAULT_PROMPT: [{ type: "text", content: "", start: 0, end: 0 }],
    command: { trigger: function() { triggerArgs = Array.from(arguments); } },
    clearEditor: () => { clearEditorCalled = true; },
    Array, Object, Error, TypeError, RangeError, String, Number,
    parseInt, parseFloat, isNaN, isFinite, undefined, console,
    ...overrides,
  };
  return {
    ctx,
    get promptSetArgs() { return promptSetArgs; },
    get closePopoverCalled() { return closePopoverCalled; },
    get focusCalled() { return focusCalled; },
    get triggerArgs() { return triggerArgs; },
    get setEditorTextArg() { return setEditorTextArg; },
    get clearEditorCalled() { return clearEditorCalled; },
  };
}

// --- Run scenario from argv ---
// Node 22 with -e: argv is [node, arg1, ...] (no [eval] entry)
const scenario = process.argv[1];
let out = {};

if (scenario === "custom_images") {
  const imgs = [
    { type: "image_attachment", url: "data:image/png;base64,abc", start: 0, end: 0 },
    { type: "image_attachment", url: "data:image/png;base64,def", start: 0, end: 0 },
  ];
  const t = createCtx(imgs, {});
  vm.createContext(t.ctx);
  vm.runInContext(fnCode, t.ctx);
  vm.runInContext('handleSlashSelect({ type: "custom", trigger: "mycmd", id: "c1" })', t.ctx);
  const parts = t.promptSetArgs ? t.promptSetArgs[0] : null;
  const imageCount = parts ? parts.filter(p => p && p.type === "image_attachment").length : 0;
  const textCount = parts ? parts.filter(p => p && p.type === "text").length : 0;
  out = { promptSetCalled: !!t.promptSetArgs, imageCount, textCount, expected: imgs.length };

} else if (scenario === "builtin_images") {
  const imgs = [
    { type: "image_attachment", url: "data:image/png;base64,single", start: 0, end: 0 },
  ];
  const t = createCtx(imgs, {});
  vm.createContext(t.ctx);
  vm.runInContext(fnCode, t.ctx);
  vm.runInContext('handleSlashSelect({ type: "builtin", id: "help" })', t.ctx);
  const parts = t.promptSetArgs ? t.promptSetArgs[0] : null;
  const imageCount = parts ? parts.filter(p => p && p.type === "image_attachment").length : 0;
  out = { promptSetCalled: !!t.promptSetArgs, imageCount, expected: imgs.length };

} else if (scenario === "builtin_multiple_images") {
  const imgs = [
    { type: "image_attachment", url: "data:image/png;base64,one", start: 0, end: 0 },
    { type: "image_attachment", url: "data:image/png;base64,two", start: 0, end: 0 },
    { type: "image_attachment", url: "data:image/png;base64,three", start: 0, end: 0 },
  ];
  const t = createCtx(imgs, {});
  vm.createContext(t.ctx);
  vm.runInContext(fnCode, t.ctx);
  vm.runInContext('handleSlashSelect({ type: "builtin", id: "run-task" })', t.ctx);
  const parts = t.promptSetArgs ? t.promptSetArgs[0] : null;
  const imageCount = parts ? parts.filter(p => p && p.type === "image_attachment").length : 0;
  out = { promptSetCalled: !!t.promptSetArgs, imageCount, expected: imgs.length };

} else if (scenario === "undefined_cmd") {
  const t = createCtx([], {});
  vm.createContext(t.ctx);
  vm.runInContext(fnCode, t.ctx);
  let threw = false;
  try { vm.runInContext("handleSlashSelect(undefined)", t.ctx); }
  catch (e) { threw = true; }
  out = { threw, promptSetCalled: t.promptSetArgs !== null, closePopoverCalled: t.closePopoverCalled };

} else if (scenario === "close_popover") {
  const t = createCtx([], {});
  vm.createContext(t.ctx);
  vm.runInContext(fnCode, t.ctx);
  vm.runInContext('handleSlashSelect({ type: "custom", trigger: "test", id: "c1" })', t.ctx);
  out = { closePopoverCalled: t.closePopoverCalled };

} else if (scenario === "command_trigger") {
  const t = createCtx([], {});
  vm.createContext(t.ctx);
  vm.runInContext(fnCode, t.ctx);
  vm.runInContext('handleSlashSelect({ type: "builtin", id: "run-task" })', t.ctx);
  out = { triggerArgs: t.triggerArgs };

} else if (scenario === "not_stub") {
  // Count statements and prompt.set calls in the extracted function
  const stmtMatches = fnBody.match(/\\b(const|let|var|if|return|for|while|switch)\\b/g) || [];
  const setCount = (fnBody.match(/prompt\\.set/g) || []).length;
  const hasBranching = fnBody.includes("custom") || fnBody.includes("type");
  out = { stmtCount: stmtMatches.length, setCount, hasBranching };
}

console.log(JSON.stringify(out));
""")


def _run_scenario(scenario: str) -> dict:
    """Run a test scenario via the JS helper and return parsed JSON output."""
    r = subprocess.run(
        ["node", "-e", _HELPER_JS, scenario],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
        env={
            "PATH": "/root/.bun/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            "TARGET_PATH": TARGET_PATH,
            "NODE_PATH": f"{REPO}/node_modules",
        },
    )
    assert r.returncode == 0, (
        f"Node scenario '{scenario}' failed (rc={r.returncode}):\n"
        f"stdout: {r.stdout}\nstderr: {r.stderr}"
    )
    return json.loads(r.stdout.strip())


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """prompt-input.tsx must parse without TypeScript syntax errors."""
    r = subprocess.run(
        [
            "node", "-e",
            "const ts = require('typescript');"
            f"const src = require('fs').readFileSync('{TARGET_PATH}','utf8');"
            f"const sf = ts.createSourceFile('{TARGET}', src, ts.ScriptTarget.Latest, true);"
            f"const p = ts.createProgram(['{TARGET_PATH}'], "
            "  {noEmit:true, allowJs:true, jsx: ts.JsxEmit.Preserve});"
            "const d = p.getSyntacticDiagnostics(sf);"
            "if(d.length > 0) { d.forEach(x => console.error(x.messageText)); process.exit(1); }",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Syntax errors in {TARGET}:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_custom_slash_preserves_images():
    """Selecting a custom slash command with 2 images must preserve both in prompt.set."""
    result = _run_scenario("custom_images")
    assert result["promptSetCalled"], "prompt.set was never called for custom command"
    assert result["imageCount"] >= result["expected"], (
        f"Custom command lost images: expected {result['expected']}, got {result['imageCount']}"
    )
    assert result["textCount"] >= 1, "Custom command lost the text part"


# [pr_diff] fail_to_pass
def test_builtin_slash_preserves_images():
    """Selecting a built-in slash command with 1 image must preserve it in prompt.set."""
    result = _run_scenario("builtin_images")
    assert result["promptSetCalled"], "prompt.set was never called for builtin command"
    assert result["imageCount"] >= result["expected"], (
        f"Builtin command lost images: expected {result['expected']}, got {result['imageCount']}"
    )


# [pr_diff] fail_to_pass
def test_builtin_slash_preserves_multiple_images():
    """Selecting a built-in slash command with 3 images must preserve all of them."""
    result = _run_scenario("builtin_multiple_images")
    assert result["promptSetCalled"], "prompt.set was never called"
    assert result["imageCount"] >= result["expected"], (
        f"Builtin command lost images: expected {result['expected']}, got {result['imageCount']}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — existing behavior must be preserved
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_undefined_cmd_returns_early():
    """handleSlashSelect(undefined) must not crash or call prompt.set."""
    result = _run_scenario("undefined_cmd")
    assert not result["threw"], "Threw an error on undefined cmd"
    assert not result["promptSetCalled"], "prompt.set should not be called for undefined cmd"
    assert not result["closePopoverCalled"], "closePopover should not be called for undefined cmd"


# [pr_diff] pass_to_pass
def test_close_popover_called():
    """Selecting any command must call closePopover."""
    result = _run_scenario("close_popover")
    assert result["closePopoverCalled"], "closePopover was not called on command selection"


# [pr_diff] pass_to_pass
def test_command_trigger_for_builtin():
    """Built-in command must call command.trigger with the correct id."""
    result = _run_scenario("command_trigger")
    assert result["triggerArgs"] is not None, "command.trigger was not called for builtin command"
    assert result["triggerArgs"][0] == "run-task", (
        f"command.trigger called with wrong id: {result['triggerArgs'][0]}"
    )


# ---------------------------------------------------------------------------
# Anti-stub (static, pass_to_pass)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """handleSlashSelect must have adequate complexity (not stubbed out)."""
    result = _run_scenario("not_stub")
    assert result["stmtCount"] >= 5, (
        f"Too few statements ({result['stmtCount']}), function looks stubbed"
    )
    assert result["setCount"] >= 2, (
        f"Fewer than 2 prompt.set calls ({result['setCount']})"
    )
    assert result["hasBranching"], "No cmd.type branching found"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Helper: extract handleSlashSelect source for structural checks.
# These are TypeScript structural rules — cannot be tested behaviorally
# because the rules constrain syntax, not runtime output.
# ---------------------------------------------------------------------------

def _get_fn_source() -> str:
    """Extract handleSlashSelect function body from source."""
    src = Path(TARGET_PATH).read_text()
    fn_start = src.index("handleSlashSelect")
    # Find matching closing brace
    brace_start = src.index("{", src.index("=>", fn_start))
    depth, i = 0, brace_start
    while i < len(src):
        ch = src[i]
        if ch in ('"', "'", "`"):
            q = ch
            i += 1
            while i < len(src):
                if src[i] == "\\":
                    i += 1
                elif src[i] == q:
                    break
                i += 1
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    return src[fn_start : i + 1]


# [agent_config] pass_to_pass — AGENTS.md:13 @ 47d2ab120a4fbc92e72aca4d5b40d722d0e4d2be
def test_no_any_type():
    """handleSlashSelect must not use the 'any' type (AGENTS.md:13)."""
    fn_src = _get_fn_source()
    for line in fn_src.split("\n"):
        stripped = line.split("//")[0]
        stripped = re.sub(r"""(['"`]).*?\1""", "", stripped)
        assert not re.search(r":\s*any(?![a-zA-Z])", stripped), (
            f"Found 'any' type usage: {line.strip()}"
        )


# [agent_config] pass_to_pass — AGENTS.md:68-79 @ 47d2ab120a4fbc92e72aca4d5b40d722d0e4d2be
def test_const_over_let():
    """handleSlashSelect must prefer const over let (AGENTS.md:68-79)."""
    fn_src = _get_fn_source()
    let_matches = re.findall(r"\blet\s+", fn_src)
    assert len(let_matches) == 0, (
        f"Found {len(let_matches)} 'let' usage(s) in handleSlashSelect — prefer const"
    )


# [agent_config] pass_to_pass — AGENTS.md:81-93 @ 47d2ab120a4fbc92e72aca4d5b40d722d0e4d2be
def test_no_else_statements():
    """handleSlashSelect must not use else statements (AGENTS.md:84)."""
    fn_src = _get_fn_source()
    # Strip string literals and comments before searching
    cleaned = re.sub(r"""(['"`]).*?\1""", "", fn_src)
    cleaned = re.sub(r"//.*", "", cleaned)
    assert not re.search(r"\belse\b", cleaned), (
        "Found 'else' statement in handleSlashSelect — prefer early returns"
    )


# [agent_config] pass_to_pass — AGENTS.md:12 @ 47d2ab120a4fbc92e72aca4d5b40d722d0e4d2be
def test_no_try_catch():
    """handleSlashSelect must not use try/catch (AGENTS.md:12)."""
    fn_src = _get_fn_source()
    cleaned = re.sub(r"""(['"`]).*?\1""", "", fn_src)
    cleaned = re.sub(r"//.*", "", cleaned)
    assert not re.search(r"\btry\s*\{", cleaned), (
        "Found try/catch in handleSlashSelect — avoid try/catch where possible"
    )


# [agent_config] pass_to_pass — AGENTS.md:17 @ 47d2ab120a4fbc92e72aca4d5b40d722d0e4d2be
def test_no_for_loops():
    """handleSlashSelect must use functional methods, not for loops (AGENTS.md:17)."""
    fn_src = _get_fn_source()
    cleaned = re.sub(r"""(['"`]).*?\1""", "", fn_src)
    cleaned = re.sub(r"//.*", "", cleaned)
    assert not re.search(r"\bfor\s*\(", cleaned), (
        "Found for loop in handleSlashSelect — prefer functional array methods"
    )
