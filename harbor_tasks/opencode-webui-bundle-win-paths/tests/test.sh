#!/usr/bin/env bash
# Test suite for opencode-webui-bundle-win-paths
# Tests that createEmbeddedWebUIBundle generates correct cross-platform paths
set +e
cd /workspace/opencode
mkdir -p /logs/verifier

REWARD=0
TARGET="packages/opencode/script/build.ts"
SCRIPT_DIR="/workspace/opencode/packages/opencode/script"

# ============================================================
# Setup: Create app/dist directory with test files
# (The function scans this directory; we skip the bun build step)
# ============================================================
DIST="packages/app/dist"
mkdir -p "$DIST/assets/sub"
echo '<html><head></head><body></body></html>' > "$DIST/index.html"
echo 'body { margin: 0 }' > "$DIST/assets/style.css"
echo 'console.log("test")' > "$DIST/assets/sub/deep.js"
echo 'PNG_DATA' > "$DIST/assets/logo.png"

# ============================================================
# Extract createEmbeddedWebUIBundle, skip build step, and run it
# ============================================================
cat > /tmp/extract_func.ts << 'TSEOF'
import fs from "fs"
import path from "path"

const SCRIPT_DIR = "/workspace/opencode/packages/opencode/script"
const source = fs.readFileSync(path.join(SCRIPT_DIR, "build.ts"), "utf-8")

// Extract `dir` variable from outer scope (used by fix for path.relative)
let dirDef = `const dir = ${JSON.stringify(SCRIPT_DIR)}`
for (const line of source.split("\n")) {
  const m = line.match(/^(export\s+)?(const|let|var)\s+dir\s*=\s*(.+)$/)
  if (m) {
    dirDef = line
      .replace(/^export\s+/, "")
      .replace(/import\.meta\.dirname/g, JSON.stringify(SCRIPT_DIR))
      .replace(/import\.meta\.filename/g, JSON.stringify(path.join(SCRIPT_DIR, "build.ts")))
    break
  }
}

// Find function boundaries
const funcIdx = source.indexOf("const createEmbeddedWebUIBundle")
if (funcIdx === -1) {
  fs.writeFileSync("/tmp/func_status.txt", "FUNC_NOT_FOUND")
  process.exit(1)
}

let depth = 0, end = funcIdx, started = false
for (let i = funcIdx; i < source.length; i++) {
  if (source[i] === "{") { depth++; started = true }
  if (source[i] === "}") { depth--; if (started && depth === 0) { end = i + 1; break } }
}

let func = source.substring(funcIdx, end)

// Patch: skip the bun build step (replace await $`...` with void 0)
func = func.replace(/await\s+\$`[^`]*`/, "void 0")
// Patch: replace import.meta references with concrete paths
func = func.replace(/import\.meta\.dirname/g, JSON.stringify(SCRIPT_DIR))
func = func.replace(/import\.meta\.filename/g, JSON.stringify(path.join(SCRIPT_DIR, "build.ts")))

// Write standalone runner
const runner = [
  'import path from "path"',
  dirDef,
  '// no-op shell tag in case replacement missed',
  'const $ = ((s: TemplateStringsArray, ...v: any[]) => Promise.resolve("")) as any',
  func,
  'const __result = await createEmbeddedWebUIBundle()',
  'console.log(__result)',
].join("\n")

fs.writeFileSync("/tmp/run_func.ts", runner)
fs.writeFileSync("/tmp/func_status.txt", "OK")
TSEOF

bun run /tmp/extract_func.ts 2>/tmp/extract_err.txt

FUNC_OUTPUT=""
if [ -f /tmp/run_func.ts ] && grep -q "OK" /tmp/func_status.txt 2>/dev/null; then
  FUNC_OUTPUT=$(timeout 30 bun run /tmp/run_func.ts 2>/tmp/run_err.txt)
  RUN_OK=$?
else
  echo "WARN: Function extraction failed"
  cat /tmp/extract_err.txt 2>/dev/null
  RUN_OK=1
fi

echo "$FUNC_OUTPUT" > /tmp/func_output.txt
echo "--- Generated module (first 25 lines) ---"
echo "$FUNC_OUTPUT" | head -25
echo "---"

# ============================================================
# [pr_diff] (0.35): F2P — Import specifiers must be relative paths
# Buggy code: path.join(appDir, "dist", file) → absolute like /workspace/...
# Fixed code: path.relative(dir, ...) → relative like ../../app/dist/...
# ============================================================
if [ $RUN_OK -eq 0 ] && [ -n "$FUNC_OUTPUT" ]; then
  python3 << 'PYEOF'
import re, sys

with open("/tmp/func_output.txt") as f:
    output = f.read()

imports = [l for l in output.strip().split("\n") if l.strip().startswith("import ")]
if not imports:
    print("NO_IMPORTS")
    sys.exit(1)

failures = []
for line in imports:
    m = re.search(r'from\s+"([^"]+)"', line) or re.search(r"from\s+'([^']+)'", line)
    if m:
        spec = m.group(1)
        if not (spec.startswith("./") or spec.startswith("../")):
            failures.append(spec)

if failures:
    for f in failures:
        print(f"NON_RELATIVE: {f}")
    sys.exit(1)
else:
    print(f"ALL_RELATIVE ({len(imports)} imports checked)")
    sys.exit(0)
PYEOF
  if [ $? -eq 0 ]; then
    echo "PASS [pr_diff] (0.35): Import specifiers are relative paths"
    REWARD=$((REWARD + 35))
  else
    echo "FAIL [pr_diff] (0.35): Import specifiers contain absolute paths"
  fi
else
  echo "FAIL [pr_diff] (0.35): Function did not produce output (exit=$RUN_OK)"
fi

# ============================================================
# [pr_diff] (0.20): F2P — Export keys must be sorted for deterministic output
# Buggy code: no sort, glob order is non-deterministic across runs
# Fixed code: .sort() applied to file list before generating output
# ============================================================
if [ $RUN_OK -eq 0 ] && [ -n "$FUNC_OUTPUT" ]; then
  python3 << 'PYEOF'
import re, sys

with open("/tmp/func_output.txt") as f:
    output = f.read()

keys = re.findall(r'^\s*"([^"]+)"\s*:\s*file_\d+', output, re.MULTILINE)
if len(keys) < 2:
    print(f"TOO_FEW_KEYS ({len(keys)})")
    sys.exit(1)

if keys == sorted(keys):
    print(f"SORTED ({len(keys)} keys)")
    sys.exit(0)
else:
    print(f"NOT_SORTED: got {keys}")
    sys.exit(1)
PYEOF
  if [ $? -eq 0 ]; then
    echo "PASS [pr_diff] (0.20): Export keys are sorted"
    REWARD=$((REWARD + 20))
  else
    echo "FAIL [pr_diff] (0.20): Export keys are not sorted"
  fi
else
  echo "FAIL [pr_diff] (0.20): No function output to check"
fi

# ============================================================
# [pr_diff] (0.15): P2P — All test files appear in the generated output
# Both buggy and fixed code should list all scanned files
# ============================================================
if [ $RUN_OK -eq 0 ] && [ -n "$FUNC_OUTPUT" ]; then
  python3 << 'PYEOF'
import sys

with open("/tmp/func_output.txt") as f:
    output = f.read()

expected = ["index.html", "assets/style.css", "assets/sub/deep.js", "assets/logo.png"]
missing = [f for f in expected if f not in output]
if missing:
    print(f"MISSING: {missing}")
    sys.exit(1)
print(f"ALL_PRESENT ({len(expected)} files)")
PYEOF
  if [ $? -eq 0 ]; then
    echo "PASS [pr_diff] (0.15): All test files present in output"
    REWARD=$((REWARD + 15))
  else
    echo "FAIL [pr_diff] (0.15): Some files missing from output"
  fi
fi

# ============================================================
# [pr_diff] (0.05): P2P — Output has valid import/export structure
# ============================================================
if [ $RUN_OK -eq 0 ] && [ -n "$FUNC_OUTPUT" ]; then
  python3 << 'PYEOF'
import re, sys

with open("/tmp/func_output.txt") as f:
    output = f.read()

has_imports = bool(re.search(r'^import\s+\w+\s+from\s+', output, re.MULTILINE))
has_export = "export default" in output
has_type_file = 'type: "file"' in output or "type: 'file'" in output

if has_imports and has_export and has_type_file:
    print("VALID_STRUCTURE")
else:
    print(f"imports={has_imports} export={has_export} type_file={has_type_file}")
    sys.exit(1)
PYEOF
  if [ $? -eq 0 ]; then
    echo "PASS [pr_diff] (0.05): Valid import/export structure"
    REWARD=$((REWARD + 5))
  else
    echo "FAIL [pr_diff] (0.05): Invalid output structure"
  fi
fi

# ============================================================
# [pr_diff] (0.10): Structural — Source handles backslash normalization
# Required for Windows cross-platform support. Cannot test behaviorally
# on Linux since path.join/Glob don't produce backslashes.
# Accepts many valid patterns: replaceAll, replace regex, split/join,
# path.posix, custom normalizer, etc.
# ============================================================
python3 << 'PYEOF'
import re, sys

with open("/workspace/opencode/packages/opencode/script/build.ts") as f:
    source = f.read()

start = source.find("const createEmbeddedWebUIBundle")
if start == -1:
    print("FUNC_NOT_FOUND")
    sys.exit(1)

depth = 0; end = start; started = False
for i in range(start, len(source)):
    if source[i] == "{": depth += 1; started = True
    if source[i] == "}":
        depth -= 1
        if started and depth == 0: end = i + 1; break

func = source[start:end]

# Broad check for any backslash-to-slash normalization pattern
patterns = [
    r'replaceAll\s*\(\s*["\']\\\\["\']',             # .replaceAll("\\", ...)
    r'\.replace\s*\(\s*/[^/]*\\\\[^/]*/[gim]*\s*,',  # .replace(/\\/g, ...)
    r'split\s*\(\s*["\']\\\\["\']\s*\).*?join',       # .split("\\").join(...)
    r'path\.posix\.',                                   # path.posix.join etc
    r'(toForwardSlash|normalizePath|normalizeSlash)\s*\(', # custom helpers
    r'\.replaceAll\s*\(\s*path\.sep',                  # .replaceAll(path.sep, ...)
    r'\.replace\s*\(\s*path\.sep',                     # .replace(path.sep, ...)
]

found = any(re.search(p, func, re.DOTALL) for p in patterns)
if found:
    print("HAS_BACKSLASH_NORMALIZATION")
else:
    print("NO_BACKSLASH_NORMALIZATION")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
  echo "PASS [pr_diff] (0.10): Backslash normalization present"
  REWARD=$((REWARD + 10))
else
  echo "FAIL [pr_diff] (0.10): No backslash normalization in function"
fi

# ============================================================
# [agent_config] (0.05): "Prefer const over let" — AGENTS.md:70 @ b7a06e19
# ============================================================
python3 << 'PYEOF'
import re, sys

with open("/workspace/opencode/packages/opencode/script/build.ts") as f:
    source = f.read()

start = source.find("const createEmbeddedWebUIBundle")
if start == -1: sys.exit(1)

depth = 0; end = start; started = False
for i in range(start, len(source)):
    if source[i] == "{": depth += 1; started = True
    if source[i] == "}":
        depth -= 1
        if started and depth == 0: end = i + 1; break

func = source[start:end]
body = "\n".join(func.split("\n")[1:-1])

has_let = bool(re.search(r'\blet\b', body))
has_var = bool(re.search(r'\bvar\b', body))

if has_let or has_var:
    kw = "let" if has_let else "var"
    print(f"USES_{kw.upper()}")
    sys.exit(1)
print("CONST_ONLY")
PYEOF
if [ $? -eq 0 ]; then
  echo "PASS [agent_config] (0.05): Uses const only — AGENTS.md:70 @ b7a06e19"
  REWARD=$((REWARD + 5))
else
  echo "FAIL [agent_config] (0.05): Uses let/var instead of const"
fi

# ============================================================
# [agent_config] (0.05): "Prefer functional array methods" — AGENTS.md:17 @ b7a06e19
# ============================================================
python3 << 'PYEOF'
import re, sys

with open("/workspace/opencode/packages/opencode/script/build.ts") as f:
    source = f.read()

start = source.find("const createEmbeddedWebUIBundle")
if start == -1: sys.exit(1)

depth = 0; end = start; started = False
for i in range(start, len(source)):
    if source[i] == "{": depth += 1; started = True
    if source[i] == "}":
        depth -= 1
        if started and depth == 0: end = i + 1; break

func = source[start:end]

has_loop = bool(re.search(r'\b(for|while)\s*\(', func))
if has_loop:
    print("HAS_IMPERATIVE_LOOPS")
    sys.exit(1)
print("NO_LOOPS")
PYEOF
if [ $? -eq 0 ]; then
  echo "PASS [agent_config] (0.05): No imperative loops — AGENTS.md:17 @ b7a06e19"
  REWARD=$((REWARD + 5))
else
  echo "FAIL [agent_config] (0.05): Uses for/while instead of functional methods"
fi

# ============================================================
# [static] (0.05): Anti-stub — Function body has >=5 meaningful statements
# ============================================================
python3 << 'PYEOF'
import sys

with open("/workspace/opencode/packages/opencode/script/build.ts") as f:
    source = f.read()

start = source.find("const createEmbeddedWebUIBundle")
if start == -1:
    print("NOT_FOUND")
    sys.exit(1)

depth = 0; end = start; started = False
for i in range(start, len(source)):
    if source[i] == "{": depth += 1; started = True
    if source[i] == "}":
        depth -= 1
        if started and depth == 0: end = i + 1; break

func = source[start:end]
body_lines = [l.strip() for l in func.split("\n")[1:-1]
              if l.strip() and not l.strip().startswith("//") and not l.strip().startswith("*")]

if len(body_lines) >= 5:
    print(f"NON_TRIVIAL ({len(body_lines)} lines)")
else:
    print(f"STUB ({len(body_lines)} lines)")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
  echo "PASS [static] (0.05): Function is non-trivial"
  REWARD=$((REWARD + 5))
else
  echo "FAIL [static] (0.05): Function body too small (likely stub)"
fi

# ============================================================
# Final score
# ============================================================
FINAL=$(python3 -c "print(f'{$REWARD / 100:.2f}')")
echo ""
echo "=== FINAL SCORE: $FINAL ($REWARD/100) ==="
echo "$FINAL" > /logs/verifier/reward.txt

python3 -c "
import json
r = $REWARD
behavioral = min(r, 75) / 100
config = 0
if r >= 95: config = 0.10
elif r >= 90: config = 0.05
structural = 0
if r >= 80: structural = 0.15
elif r >= 75: structural = 0.10
json.dump({
    'reward': round(r/100, 2),
    'behavioral': round(behavioral, 2),
    'config': round(config, 2),
    'structural': round(structural, 2)
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"
