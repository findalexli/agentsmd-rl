#!/usr/bin/env bash
set +e

SCORE=0
FILE="js/image/shared/ImagePreview.svelte"

pass() { SCORE=$(python3 -c "print($SCORE + $1)"); }

# ── GATE (0.00): File exists ──────────────────────────────────────
# [pr_diff] (0.00): ImagePreview.svelte must exist
if [ ! -f "$FILE" ]; then
    echo "GATE FAIL: $FILE not found"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE PASS: $FILE exists"

# Install svelte compiler for AST parsing and compilation
cd /workspace
npm install --no-save svelte 2>/dev/null 1>/dev/null

# Write comprehensive Node.js test script
cat > /tmp/check_svelte.mjs << 'NODEEOF'
import { readFileSync, writeFileSync } from "fs";
import { parse, compile } from "svelte/compiler";

const FILE = process.argv[2];
const src = readFileSync(FILE, "utf-8");
const results = {};

// ── Parse Svelte AST ─────────────────────────────────────────────
try {
  try { results.ast = parse(src, { modern: true }); }
  catch { results.ast = parse(src); }
} catch (e) {
  results.parseError = e.message;
  writeFileSync("/tmp/svelte_results.json", JSON.stringify(results));
  process.exit(0);
}

const ast = results.ast;

// Walk helper (handles Svelte 4 + 5 AST shapes)
function walk(node, cb) {
  if (!node || typeof node !== "object") return;
  cb(node);
  for (const k of Object.keys(node)) {
    if (k === "parent") continue;
    const v = node[k];
    if (Array.isArray(v)) v.forEach((n) => walk(n, cb));
    else if (v && typeof v === "object" && v.type) walk(v, cb);
  }
}

// ── Collect component info from template ─────────────────────────
let onclickSrc = null;
let hasOnclick = false;
let hasOnFullscreen = false;
let hasDownloadLink = false;
let hasShareButton = false;

walk(ast.fragment || ast.html, (node) => {
  const isComp =
    node.type === "Component" || node.type === "InlineComponent";
  if (!isComp) return;

  if (node.name === "FullscreenButton") {
    for (const a of node.attributes || []) {
      if (a.name === "onclick") {
        hasOnclick = true;
        const vals = Array.isArray(a.value) ? a.value : [a.value];
        for (const v of vals) {
          if (v && v.expression) {
            onclickSrc = src.substring(v.expression.start, v.expression.end);
          }
        }
      }
      if (
        (a.type === "EventHandler" || a.type === "OnDirective") &&
        a.name === "fullscreen"
      ) {
        hasOnFullscreen = true;
      }
    }
  }

  if (node.name === "DownloadLink") hasDownloadLink = true;
  if (node.name === "ShareButton") hasShareButton = true;
});

results.hasOnclick = hasOnclick;
results.hasOnFullscreen = hasOnFullscreen;
results.hasDownloadLink = hasDownloadLink;
results.hasShareButton = hasShareButton;
results.onclickSrc = onclickSrc || "";

// ── Behavioral: eval onclick handler with mocks ──────────────────
if (onclickSrc) {
  try {
    // Test with handler(true): should set fullscreen = true
    const fn1 = new Function(
      "dispatch",
      `let fullscreen = false;
       const handler = ${onclickSrc};
       handler(true);
       return { fullscreen };`
    );
    const log1 = [];
    const r1 = fn1((...args) => log1.push(args));

    // Test with handler(false): should set fullscreen = false
    const fn2 = new Function(
      "dispatch",
      `let fullscreen = true;
       const handler = ${onclickSrc};
       handler(false);
       return { fullscreen };`
    );
    const log2 = [];
    const r2 = fn2((...args) => log2.push(args));

    results.evalOk = true;
    results.stateTrue = r1.fullscreen === true;
    results.stateFalse = r2.fullscreen === false;
    results.usesParam = r1.fullscreen === true && r2.fullscreen === false;
    results.dispatchCalled = log1.length > 0;
    results.dispatchArgs = log1;
  } catch (e) {
    results.evalOk = false;
    results.evalError = e.message;

    // Fallback: try with script context (handles named-function patterns)
    try {
      const scriptNode = ast.instance;
      if (scriptNode && scriptNode.content) {
        const scriptSrc = src.substring(
          scriptNode.content.start,
          scriptNode.content.end
        );
        const clean = scriptSrc
          .replace(/^\s*import\s+.*/gm, "")
          .replace(/^\s*export\s+.*/gm, "")
          .replace(/\$props\(\)/g, "({})")
          .replace(/\$bindable\(([^)]*)\)/g, "$1")
          .replace(/\$state\(([^)]*)\)/g, "$1");

        const fn = new Function(`
          let fullscreen = false;
          const dispatchLog = [];
          const dispatch = (...args) => dispatchLog.push(args);
          function createEventDispatcher() { return dispatch; }
          ${clean}
          const handler = ${onclickSrc};
          handler(true);
          return { fullscreen, dispatchLog };
        `);
        const r = fn();
        results.fallbackOk = true;
        results.stateTrue = r.fullscreen === true;
        results.dispatchCalled = r.dispatchLog.length > 0;
        results.usesParam = true;
      }
    } catch (e2) {
      results.fallbackOk = false;
    }
  }
}

// ── Compilation check ────────────────────────────────────────────
try {
  compile(src, { generate: "client", name: "ImagePreview" });
  results.compiles = true;
} catch (e) {
  results.compiles = false;
  results.compileError = e.message;
}

// ── Indentation check ────────────────────────────────────────────
const lines = src.split("\n");
const tabLines = lines.filter((l) => l.startsWith("\t")).length;
const spaceLines = lines.filter(
  (l) => /^ {2,}[^ ]/.test(l) && !l.startsWith("\t")
).length;
results.tabIndent = tabLines;
results.spaceIndent = spaceLines;

// Remove AST from output (too large)
delete results.ast;
writeFileSync("/tmp/svelte_results.json", JSON.stringify(results));
NODEEOF

node /tmp/check_svelte.mjs "$FILE" 2>/dev/null

# ── Score the results ─────────────────────────────────────────────
cat > /tmp/score_results.py << 'PYEOF'
import json, sys, os

score = 0.0
FILE = sys.argv[1]

try:
    with open("/tmp/svelte_results.json") as f:
        r = json.load(f)
except Exception:
    r = {}

node_ok = "parseError" not in r and bool(r)

# ── F2P (0.40): Behavioral — onclick handler updates state and dispatches ──
# [pr_diff] (0.40): onclick callback must set fullscreen to passed value and dispatch event
if r.get("evalOk") or r.get("fallbackOk"):
    if r.get("usesParam") and r.get("dispatchCalled"):
        score += 0.40
        print("F2P PASS (0.40): onclick handler updates state with param and dispatches (behavioral)")
    elif r.get("stateTrue") and r.get("dispatchCalled"):
        score += 0.25
        print("F2P PARTIAL (0.25): handler updates state but may hardcode value")
    elif r.get("stateTrue") or r.get("dispatchCalled"):
        score += 0.15
        print("F2P PARTIAL (0.15): handler partially works")
    else:
        print("F2P FAIL (0.40): handler does not update state or dispatch")
elif r.get("hasOnclick") and not r.get("hasOnFullscreen"):
    score += 0.10
    print("F2P WEAK (0.10): onclick exists but could not verify behavior")
else:
    print("F2P FAIL (0.40): no onclick or still uses on:fullscreen")

# ── F2P (0.20): Svelte compilation succeeds ──────────────────────
# [pr_diff] (0.20): Modified file must still be valid Svelte
if r.get("compiles"):
    score += 0.20
    print("COMPILE PASS (0.20): Svelte compilation successful")
elif not node_ok:
    print("COMPILE SKIP: svelte not available")
else:
    print("COMPILE FAIL (0.20): " + r.get("compileError", "unknown error"))

# ── Regression (0.10): on:fullscreen removed from FullscreenButton ─
# [pr_diff] (0.10): Old broken event pattern must be replaced
if r.get("hasOnclick") and not r.get("hasOnFullscreen"):
    score += 0.10
    print("REGR PASS (0.10): on:fullscreen removed, onclick in place")
elif r.get("hasOnclick"):
    score += 0.05
    print("REGR PARTIAL (0.05): onclick added but on:fullscreen remains")
else:
    print("REGR FAIL (0.10): FullscreenButton still uses broken pattern")

# ── P2P (0.10): DownloadLink still present ────────────────────────
# [pr_diff] (0.10): Download button must still be rendered
if node_ok:
    if r.get("hasDownloadLink"):
        score += 0.10
        print("P2P PASS (0.10): DownloadLink present in template")
    else:
        print("P2P FAIL (0.10): DownloadLink removed from template")
else:
    # Fallback to basic grep
    with open(FILE) as f:
        content = f.read()
    if "DownloadLink" in content:
        score += 0.10
        print("P2P PASS (0.10): DownloadLink present (grep fallback)")
    else:
        print("P2P FAIL (0.10): DownloadLink missing")

# ── P2P (0.05): ShareButton still present ─────────────────────────
# [pr_diff] (0.05): Share button must still be rendered
if node_ok:
    if r.get("hasShareButton"):
        score += 0.05
        print("P2P PASS (0.05): ShareButton present in template")
    else:
        print("P2P FAIL (0.05): ShareButton removed from template")
else:
    with open(FILE) as f:
        content = f.read()
    if "ShareButton" in content:
        score += 0.05
        print("P2P PASS (0.05): ShareButton present (grep fallback)")
    else:
        print("P2P FAIL (0.05): ShareButton missing")

# ── Config (0.10): Consistent tab indentation ─────────────────────
# [agent_config] (0.10): "Be consistent with the style of the surrounding code" — AGENTS.md:44
if node_ok:
    tab_n = r.get("tabIndent", 0)
    space_n = r.get("spaceIndent", 0)
else:
    with open(FILE) as f:
        lines = f.readlines()
    tab_n = sum(1 for l in lines if l.startswith("\t"))
    space_n = sum(1 for l in lines if l.startswith("  ") and not l.startswith("\t"))

if tab_n > 0 and space_n < 5:
    score += 0.10
    print("CONFIG PASS (0.10): Consistent tab indentation")
else:
    print("CONFIG FAIL (0.10): Mixed or space-based indentation")

# ── Anti-stub (0.05): onclick is non-trivial ──────────────────────
# [pr_diff] (0.05): onclick must not be empty or trivial stub
onclick_src = r.get("onclickSrc", "")
if onclick_src and len(onclick_src) > 20:
    score += 0.05
    print("ANTI-STUB PASS (0.05): onclick is non-trivial (" + str(len(onclick_src)) + " chars)")
else:
    print("ANTI-STUB FAIL (0.05): onclick is empty or trivial")

# ── Final score ───────────────────────────────────────────────────
final = round(score, 4)
print(f"\nScore: {final} / 1.0")

with open("/logs/verifier/reward.txt", "w") as f:
    f.write(str(final))

behavioral = round(min(score, 0.60), 4)
regression = round(min(0.10, max(0, score - 0.60)), 4)
config_sc = round(min(0.10, max(0, score - 0.70)), 4)

with open("/logs/verifier/reward.json", "w") as f:
    json.dump({
        "reward": final,
        "behavioral": behavioral,
        "regression": regression,
        "config": config_sc,
        "anti_stub": round(min(0.05, max(0, score - 0.80)), 4),
    }, f, indent=2)
PYEOF

python3 /tmp/score_results.py "$FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
