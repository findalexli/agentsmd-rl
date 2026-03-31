#!/usr/bin/env bash
set +e

REPO="/workspace/opencode"
REGISTRY="$REPO/packages/opencode/src/tool/registry.ts"
PLUGIN="$REPO/packages/opencode/src/plugin/index.ts"
TOTAL=0

add() { TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))"); }

###############################################################################
# GATE: Files exist and are non-trivial
###############################################################################
# [pr_diff] (gate): registry.ts and plugin/index.ts must exist and parse
if [ ! -f "$REGISTRY" ] || [ ! -f "$PLUGIN" ]; then
  echo "GATE FAIL: required files missing"
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward": 0.0, "gate": "files_missing"}' > /logs/verifier/reward.json
  exit 0
fi

REGISTRY_LINES=$(wc -l < "$REGISTRY")
PLUGIN_LINES=$(wc -l < "$PLUGIN")
if [ "$REGISTRY_LINES" -lt 80 ] || [ "$PLUGIN_LINES" -lt 80 ]; then
  echo "GATE FAIL: files appear stubbed (registry=$REGISTRY_LINES, plugin=$PLUGIN_LINES)"
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward": 0.0, "gate": "stub_detected"}' > /logs/verifier/reward.json
  exit 0
fi

###############################################################################
# FAIL-TO-PASS: Bug pattern removal checks (0.55)
# These check that the BUGGY patterns are GONE from actual code (not comments).
# Any correct fix MUST remove these anti-patterns regardless of implementation.
###############################################################################

# [pr_diff] (0.20): Effect.promise must NOT wrap Config/Plugin async facades in
# the InstanceState.make/state closure. This is the CORE BUG — the state init
# called Config.directories(), Config.waitForDependencies(), Plugin.list() inside
# Effect.promise(async () => {...}). Any correct fix must remove this pattern.
python3 -c "
import re, sys

code = open('$REGISTRY').read()

# Strip single-line comments and string literals to avoid false matches
stripped = re.sub(r'//[^\n]*', '', code)
stripped = re.sub(r'/\*.*?\*/', '', stripped, flags=re.DOTALL)
stripped = re.sub(r'\"[^\"]*\"', '\"\"', stripped)
stripped = re.sub(r\"'[^']*'\", \"''\", stripped)
stripped = re.sub(r'\`[^\`]*\`', '\`\`', stripped)

# Find the InstanceState block (between InstanceState.make and its closing)
# Look for Effect.promise wrapping Config or Plugin facade calls
match = re.search(r'InstanceState\.make.*?return\s*\{', stripped, re.DOTALL)
if not match:
    # If InstanceState.make doesn't exist at all, the code is probably wrong
    print('FAIL: Cannot find InstanceState.make block')
    sys.exit(1)

block = match.group(0)

# The bug: Effect.promise(async () => { ...Config.directories()... }) pattern
# Check for Config.directories or Plugin.list called inside Effect.promise
promise_blocks = list(re.finditer(r'Effect\.promise\s*\(', block))
has_facade_in_promise = False
for pb in promise_blocks:
    # Get the code after Effect.promise( up to reasonable depth
    rest = block[pb.start():]
    # Check if Config.directories, Config.waitForDependencies, or Plugin.list
    # appear near this Effect.promise call (within ~500 chars)
    nearby = rest[:500]
    if any(facade in nearby for facade in [
        'Config.directories', 'Config.waitForDependencies', 'Plugin.list'
    ]):
        has_facade_in_promise = True
        break

if has_facade_in_promise:
    print('FAIL: Config/Plugin async facades still wrapped in Effect.promise in state init')
    sys.exit(1)
else:
    print('PASS: Effect.promise no longer wraps Config/Plugin facades in state init')
    sys.exit(0)
" && add 0.20

# [pr_diff] (0.15): all() must NOT be a plain async function.
# The bug: async function all(custom: Tool.Info[]): Promise<...> { ... Config.get() }
# Any correct fix converts this to an Effect function (Effect.fn, Effect.gen, etc.)
python3 -c "
import re, sys

code = open('$REGISTRY').read()

# Strip comments to avoid matching inside comments
stripped = re.sub(r'//[^\n]*', '', code)
stripped = re.sub(r'/\*.*?\*/', '', stripped, flags=re.DOTALL)

# Check for the buggy pattern: plain async function named 'all'
# Match: async function all(...) or function all(...) with async
if re.search(r'\basync\s+function\s+all\s*\(', stripped):
    print('FAIL: all() is still a plain async function (should use Effect)')
    sys.exit(1)

# Verify all() exists in some form (not just deleted)
if not re.search(r'\ball\b', stripped):
    print('FAIL: all() function appears to be missing entirely')
    sys.exit(1)

print('PASS: all() is no longer a plain async function')
sys.exit(0)
" && add 0.15

# [pr_diff] (0.20): tools() must NOT use Promise.all for concurrent tool init.
# The bug: Promise.all(allTools.filter(...).map(async (tool) => { ... }))
# Any correct fix replaces this with Effect-native concurrency.
python3 -c "
import re, sys

code = open('$REGISTRY').read()

# Strip comments
stripped = re.sub(r'//[^\n]*', '', code)
stripped = re.sub(r'/\*.*?\*/', '', stripped, flags=re.DOTALL)

# Check for Promise.all in the actual code (not comments)
if 'Promise.all' in stripped:
    print('FAIL: Promise.all still used in registry.ts (should use Effect concurrency)')
    sys.exit(1)

print('PASS: Promise.all removed from registry.ts')
sys.exit(0)
" && add 0.20

###############################################################################
# FAIL-TO-PASS: Positive requirement checks (0.20)
# These verify new behavior exists, checked broadly to accept alternatives.
###############################################################################

# [pr_diff] (0.10): Config and Plugin services must be yielded in the layer generator.
# The fix requires getting Config and Plugin through the Effect dependency graph.
# Accept: yield* Config.Service, yield* Effect.service(Config.Service),
#         Context.get(Config.Service), or destructured variants.
python3 -c "
import re, sys

code = open('$REGISTRY').read()

# Strip comments
stripped = re.sub(r'//[^\n]*', '', code)
stripped = re.sub(r'/\*.*?\*/', '', stripped, flags=re.DOTALL)

# Find the layer = Layer.effect(..., Effect.gen(function* () { ... })) block
# Check that Config.Service and Plugin.Service are obtained via yield* or similar

# Broad check: Config.Service appears in a yield context (not just as a type reference)
has_config = bool(re.search(r'yield\*?\s+.*Config\.Service', stripped) or
                  re.search(r'Effect\.service\s*\(\s*Config\.Service', stripped) or
                  re.search(r'Context\.get\s*\(\s*Config\.Service', stripped))

has_plugin = bool(re.search(r'yield\*?\s+.*Plugin\.Service', stripped) or
                  re.search(r'Effect\.service\s*\(\s*Plugin\.Service', stripped) or
                  re.search(r'Context\.get\s*\(\s*Plugin\.Service', stripped))

if has_config and has_plugin:
    print('PASS: Both Config.Service and Plugin.Service obtained in Effect layer')
    sys.exit(0)
elif has_config:
    print('FAIL: Plugin.Service not obtained in Effect layer')
    sys.exit(1)
elif has_plugin:
    print('FAIL: Config.Service not obtained in Effect layer')
    sys.exit(1)
else:
    print('FAIL: Neither Config.Service nor Plugin.Service obtained in Effect layer')
    sys.exit(1)
" && add 0.10

# [pr_diff] (0.10): Plugin module must expose its defaultLayer for composition.
# The bug: defaultLayer was a private const. Any fix must make it accessible.
# Accept: export const, export let, export { defaultLayer }, re-export, etc.
python3 -c "
import re, sys

code = open('$PLUGIN').read()

# Strip comments
stripped = re.sub(r'//[^\n]*', '', code)
stripped = re.sub(r'/\*.*?\*/', '', stripped, flags=re.DOTALL)

# Check for exported defaultLayer in any form
if (re.search(r'\bexport\s+(const|let|var)\s+defaultLayer\b', stripped) or
    re.search(r'\bexport\s*\{[^}]*\bdefaultLayer\b', stripped)):
    print('PASS: Plugin.defaultLayer is exported')
    sys.exit(0)
else:
    print('FAIL: Plugin.defaultLayer is not exported')
    sys.exit(1)
" && add 0.10

###############################################################################
# PASS-TO-PASS: Existing API preserved (0.10)
###############################################################################

# [pr_diff] (0.05): ToolRegistry.Service class definition still present
if grep -q 'class Service' "$REGISTRY"; then
  echo "P2P PASS: Service class preserved"
  add 0.05
else
  echo "P2P FAIL: Service class missing"
fi

# [pr_diff] (0.05): Public facade functions (register, ids, tools) still exported
# Accept any export form: export async function, export const, export function
python3 -c "
import re, sys

code = open('$REGISTRY').read()
stripped = re.sub(r'//[^\n]*', '', code)
stripped = re.sub(r'/\*.*?\*/', '', stripped, flags=re.DOTALL)

missing = []
for name in ['register', 'ids', 'tools']:
    if not (re.search(r'\bexport\s+(async\s+)?function\s+' + name + r'\b', stripped) or
            re.search(r'\bexport\s+(const|let)\s+' + name + r'\b', stripped)):
        missing.append(name)

if missing:
    print(f'P2P FAIL: Missing exports: {missing}')
    sys.exit(1)
else:
    print('P2P PASS: All public facade functions exported')
    sys.exit(0)
" && add 0.05

###############################################################################
# CONFIG-DERIVED: Agent convention checks (0.10)
###############################################################################

# [agent_config] (0.05): "Use Effect.fn for named/traced effects" — packages/opencode/AGENTS.md:21 @ d2bfa92
# At least some service methods should use Effect.fn for tracing
python3 -c "
import re, sys

code = open('$REGISTRY').read()
stripped = re.sub(r'//[^\n]*', '', code)
stripped = re.sub(r'/\*.*?\*/', '', stripped, flags=re.DOTALL)
stripped = re.sub(r'\"[^\"]*\"', '\"\"', stripped)
stripped = re.sub(r\"'[^']*'\", \"''\", stripped)

# Count Effect.fn occurrences in actual code (not comments/strings)
count = len(re.findall(r'Effect\.fn\s*\(', stripped))
if count >= 3:
    print(f'CONFIG PASS: Effect.fn used {count} times for named effects')
    sys.exit(0)
else:
    print(f'CONFIG FAIL: Effect.fn used only {count} times (expected >=3)')
    sys.exit(1)
" && add 0.05

# [agent_config] (0.05): "Prefer functional array methods" — AGENTS.md:17 @ d2bfa92
# The tools() filtering should use .filter() rather than imperative loops
if grep -q '\.filter(' "$REGISTRY"; then
  echo "CONFIG PASS: .filter() used"
  add 0.05
else
  echo "CONFIG FAIL: .filter() not found"
fi

###############################################################################
# ANTI-STUB (0.05)
###############################################################################

# [pr_diff] (0.05): Registry must have substantial implementation
if [ "$REGISTRY_LINES" -ge 150 ] && [ "$PLUGIN_LINES" -ge 150 ]; then
  echo "ANTI-STUB PASS: registry=$REGISTRY_LINES lines, plugin=$PLUGIN_LINES lines"
  add 0.05
else
  echo "ANTI-STUB FAIL: files too short (registry=$REGISTRY_LINES, plugin=$PLUGIN_LINES)"
fi

###############################################################################
# Final score
###############################################################################

echo ""
echo "=== TOTAL SCORE: $TOTAL ==="
echo "$TOTAL" > /logs/verifier/reward.txt

python3 -c "
import json
total = $TOTAL
json.dump({
    'reward': total,
    'behavioral': min(total, 0.75),
    'regression': min(max(total - 0.75, 0), 0.10),
    'config': min(max(total - 0.85, 0), 0.10),
    'structural': min(max(total - 0.95, 0), 0.05)
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
