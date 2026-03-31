#!/usr/bin/env bash
set +e

REPO="/workspace/repo"
WCD="$REPO/packages/next/src/lib/typescript/writeConfigurationDefaults.ts"
GTC="$REPO/packages/next/src/lib/typescript/getTypeScriptConfiguration.ts"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS RESULTS

# Behavioral fail-to-pass (0.60)
WEIGHTS[f2p_bundler_default]=0.30
WEIGHTS[f2p_ts6_target]=0.15
WEIGHTS[f2p_baseurl_paths]=0.15

# Behavioral pass-to-pass (0.25)
WEIGHTS[p2p_commonjs_node]=0.10
WEIGHTS[p2p_amd_node]=0.05
WEIGHTS[p2p_syntax]=0.10

# Structural + config (0.15)
WEIGHTS[antistub]=0.10
WEIGHTS[config_no_secrets]=0.05

for key in "${!WEIGHTS[@]}"; do RESULTS[$key]=0; done

# -------- GATE: files exist and are non-empty --------
if [ ! -s "$WCD" ] || [ ! -s "$GTC" ]; then
    echo "GATE FAIL: source files missing or empty -- score 0"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# -------- helper: create a wrapper that re-exports from repo --------
make_wcd_wrapper() {
    cat > "$1/wcd_wrapper.ts" <<WEOF
export { writeConfigurationDefaults } from '$REPO/packages/next/src/lib/typescript/writeConfigurationDefaults'
WEOF
}
make_gtc_wrapper() {
    cat > "$1/gtc_wrapper.ts" <<WEOF
export { getTypeScriptConfiguration } from '$REPO/packages/next/src/lib/typescript/getTypeScriptConfiguration'
WEOF
}

# ========================================================================
# F2P 1 (0.30): moduleResolution defaults to "bundler" for modern TS
# [pr_diff] (0.30): Modern TS (>=5.0) with non-commonjs module defaults to "bundler" not "node"
# ========================================================================
echo ""
echo "=== F2P: moduleResolution defaults to bundler ==="
TD=$(mktemp -d)
echo '{}' > "$TD/tsconfig.json"
make_wcd_wrapper "$TD"

cat > "$TD/test.ts" <<'TSEOF'
import { writeConfigurationDefaults } from './wcd_wrapper'
import { readFileSync } from 'fs'
async function main() {
  const p = process.argv[2]
  const origLog = console.log; console.log = () => {}
  try {
    await writeConfigurationDefaults('5.9.2', p, true, true, '.next', true, false)
  } finally { console.log = origLog }
  const cfg = JSON.parse(readFileSync(p, 'utf8'))
  const mr = cfg.compilerOptions?.moduleResolution
  // Accept any casing of "bundler"
  if (typeof mr === 'string' && mr.toLowerCase() === 'bundler') {
    process.stdout.write('PASS')
  } else {
    process.stdout.write('FAIL:' + mr)
  }
}
main().catch(e => process.stdout.write('ERROR:' + e.message))
TSEOF

R=$(cd "$TD" && npx tsx test.ts "$TD/tsconfig.json" 2>/dev/null)
if [ "$R" = "PASS" ]; then
    echo "PASS: moduleResolution defaults to 'bundler' for modern TS"
    RESULTS[f2p_bundler_default]=1
else
    echo "FAIL: moduleResolution is not 'bundler' — got: $R"
fi
rm -rf "$TD"

# ========================================================================
# F2P 2 (0.15): TS6 target rewrite (es5/es3 -> es2015+)
# [pr_diff] (0.15): getTypeScriptConfiguration rewrites deprecated targets for TS>=6.0
# ========================================================================
echo ""
echo "=== F2P: TS6 es5 target rewrite ==="
TD=$(mktemp -d)
echo '{"compilerOptions":{"target":"es5","module":"esnext"}}' > "$TD/tsconfig.json"
make_gtc_wrapper "$TD"

cat > "$TD/test.ts" <<'TSEOF'
import { getTypeScriptConfiguration } from './gtc_wrapper'
import ts from 'typescript'

async function main() {
  const tsConfigPath = process.argv[2]
  // Proxy the TS module to pretend version is 6.0.0
  const fakeTs6: any = new Proxy(ts as any, {
    get(target: any, prop: string | symbol) {
      if (prop === 'version') return '6.0.0'
      return target[prop]
    }
  })
  const result = await getTypeScriptConfiguration(fakeTs6, tsConfigPath, true)

  // Verify it returns a proper ParsedCommandLine (not a stub)
  if (!result || !result.options || typeof result.options !== 'object') {
    process.stdout.write('FAIL:invalid_result')
    return
  }

  const target = result.options.target
  // ts.ScriptTarget: ES3=0, ES5=1, ES2015=2, ...
  // After fix, es5 should be rewritten to es2015 or higher (target >= 2)
  if (typeof target === 'number' && target >= 2) {
    process.stdout.write('PASS')
  } else {
    process.stdout.write('FAIL:target=' + target)
  }
}
main().catch(e => process.stdout.write('ERROR:' + e.message))
TSEOF

R=$(cd "$TD" && npx tsx test.ts "$TD/tsconfig.json" 2>/dev/null)
if [ "$R" = "PASS" ]; then
    echo "PASS: TS6 rewrites deprecated es5 target"
    RESULTS[f2p_ts6_target]=1
else
    echo "FAIL: TS6 target rewrite — got: $R"
fi
rm -rf "$TD"

# ========================================================================
# F2P 3 (0.15): TS6 baseUrl migration to paths
# [pr_diff] (0.15): getTypeScriptConfiguration migrates baseUrl to explicit paths for TS>=6.0
# ========================================================================
echo ""
echo "=== F2P: TS6 baseUrl migration to paths ==="
TD=$(mktemp -d)
echo '{"compilerOptions":{"baseUrl":".","module":"esnext","target":"es2015"}}' > "$TD/tsconfig.json"
make_gtc_wrapper "$TD"

cat > "$TD/test.ts" <<'TSEOF'
import { getTypeScriptConfiguration } from './gtc_wrapper'
import ts from 'typescript'

async function main() {
  const tsConfigPath = process.argv[2]
  const fakeTs6: any = new Proxy(ts as any, {
    get(target: any, prop: string | symbol) {
      if (prop === 'version') return '6.0.0'
      return target[prop]
    }
  })
  const result = await getTypeScriptConfiguration(fakeTs6, tsConfigPath, true)

  // Verify it returns a proper ParsedCommandLine (not a stub)
  if (!result || !result.options || typeof result.options !== 'object') {
    process.stdout.write('FAIL:invalid_result')
    return
  }

  const paths = result.options.paths
  // After fix, baseUrl:"." should be migrated to explicit paths entries
  // Any valid implementation should produce at least one paths entry
  if (paths && typeof paths === 'object' && Object.keys(paths).length > 0) {
    process.stdout.write('PASS')
  } else {
    process.stdout.write('FAIL:paths=' + JSON.stringify(paths))
  }
}
main().catch(e => process.stdout.write('ERROR:' + e.message))
TSEOF

R=$(cd "$TD" && npx tsx test.ts "$TD/tsconfig.json" 2>/dev/null)
if [ "$R" = "PASS" ]; then
    echo "PASS: TS6 migrates baseUrl to explicit paths"
    RESULTS[f2p_baseurl_paths]=1
else
    echo "FAIL: TS6 baseUrl migration — got: $R"
fi
rm -rf "$TD"

# ========================================================================
# P2P 1 (0.10): commonjs module keeps "node" resolution
# [pr_diff] (0.10): When module is commonjs, moduleResolution stays "node"
# ========================================================================
echo ""
echo "=== P2P: commonjs keeps node resolution ==="
TD=$(mktemp -d)
echo '{"compilerOptions":{"module":"commonjs"}}' > "$TD/tsconfig.json"
make_wcd_wrapper "$TD"

cat > "$TD/test.ts" <<'TSEOF'
import { writeConfigurationDefaults } from './wcd_wrapper'
import { readFileSync } from 'fs'
async function main() {
  const p = process.argv[2]
  const origLog = console.log; console.log = () => {}
  try {
    await writeConfigurationDefaults('5.9.2', p, false, true, '.next', true, false)
  } finally { console.log = origLog }
  const cfg = JSON.parse(readFileSync(p, 'utf8'))
  const mr = cfg.compilerOptions?.moduleResolution
  // For commonjs, should remain "node" (not "bundler")
  if (typeof mr === 'string' && mr.toLowerCase() === 'node') {
    process.stdout.write('PASS')
  } else {
    process.stdout.write('FAIL:' + mr)
  }
}
main().catch(e => process.stdout.write('ERROR:' + e.message))
TSEOF

R=$(cd "$TD" && npx tsx test.ts "$TD/tsconfig.json" 2>/dev/null)
if [ "$R" = "PASS" ]; then
    echo "PASS: commonjs module keeps 'node' resolution"
    RESULTS[p2p_commonjs_node]=1
else
    echo "FAIL: commonjs resolution — got: $R"
fi
rm -rf "$TD"

# ========================================================================
# P2P 2 (0.05): amd module keeps "node" resolution
# [pr_diff] (0.05): When module is amd, moduleResolution stays "node"
# ========================================================================
echo ""
echo "=== P2P: amd keeps node resolution ==="
TD=$(mktemp -d)
echo '{"compilerOptions":{"module":"amd"}}' > "$TD/tsconfig.json"
make_wcd_wrapper "$TD"

cat > "$TD/test.ts" <<'TSEOF'
import { writeConfigurationDefaults } from './wcd_wrapper'
import { readFileSync } from 'fs'
async function main() {
  const p = process.argv[2]
  const origLog = console.log; console.log = () => {}
  try {
    await writeConfigurationDefaults('5.9.2', p, false, true, '.next', true, false)
  } finally { console.log = origLog }
  const cfg = JSON.parse(readFileSync(p, 'utf8'))
  const mr = cfg.compilerOptions?.moduleResolution
  if (typeof mr === 'string' && mr.toLowerCase() === 'node') {
    process.stdout.write('PASS')
  } else {
    process.stdout.write('FAIL:' + mr)
  }
}
main().catch(e => process.stdout.write('ERROR:' + e.message))
TSEOF

R=$(cd "$TD" && npx tsx test.ts "$TD/tsconfig.json" 2>/dev/null)
if [ "$R" = "PASS" ]; then
    echo "PASS: amd module keeps 'node' resolution"
    RESULTS[p2p_amd_node]=1
else
    echo "FAIL: amd resolution — got: $R"
fi
rm -rf "$TD"

# ========================================================================
# P2P 3 (0.10): Both files parse as valid TypeScript
# [pr_diff] (0.10): Source files have valid syntax
# ========================================================================
echo ""
echo "=== P2P: TypeScript syntax valid ==="
SYNTAX_OK=1
for f in "$WCD" "$GTC"; do
    node -e "
const ts = require('typescript');
const source = require('fs').readFileSync('$f', 'utf8');
const sf = ts.createSourceFile('$f', source, ts.ScriptTarget.Latest, true);
if (!sf) process.exit(1);
" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "FAIL: $(basename "$f") has syntax errors"
        SYNTAX_OK=0
    fi
done
if [ "$SYNTAX_OK" = "1" ]; then
    echo "PASS: both files have valid TypeScript syntax"
    RESULTS[p2p_syntax]=1
fi

# ========================================================================
# STRUCTURAL (0.10): Anti-stub — non-trivial implementation
# [pr_diff] (0.10): Files have substantive implementations
# ========================================================================
echo ""
echo "=== Structural: anti-stub ==="
ANTI_STUB=1

WCD_LINES=$(wc -l < "$WCD")
GTC_LINES=$(wc -l < "$GTC")

# writeConfigurationDefaults.ts was ~200 lines before fix; should stay substantial
if [ "$WCD_LINES" -lt 100 ]; then
    echo "FAIL: writeConfigurationDefaults.ts too short ($WCD_LINES lines)"
    ANTI_STUB=0
fi

# getTypeScriptConfiguration.ts was ~70 lines; fix adds significant logic
if [ "$GTC_LINES" -lt 50 ]; then
    echo "FAIL: getTypeScriptConfiguration.ts too short ($GTC_LINES lines)"
    ANTI_STUB=0
fi

# moduleResolution is fundamental to any valid fix of writeConfigurationDefaults
if ! grep -q 'moduleResolution' "$WCD" 2>/dev/null; then
    echo "FAIL: writeConfigurationDefaults.ts missing moduleResolution handling"
    ANTI_STUB=0
fi

if [ "$ANTI_STUB" = "1" ]; then
    echo "PASS: implementation is substantive"
    RESULTS[antistub]=1
fi

# ========================================================================
# CONFIG (0.05): No secret files committed
# [agent_config] (0.05): "Never commit local secret files" — CLAUDE.md:309
# ========================================================================
echo ""
echo "=== Config: no secret files ==="
SECRETS=0
for pat in ".env" ".env.local" "credentials.json" "*.pem" "*.key"; do
    if git -C "$REPO" diff HEAD --name-only 2>/dev/null | grep -q "$pat"; then
        echo "FAIL: secret file pattern '$pat' found in diff"
        SECRETS=1
    fi
done
if [ "$SECRETS" = "0" ]; then
    echo "PASS: no secret files in changes"
    RESULTS[config_no_secrets]=1
fi

# ========================================================================
# COMPUTE FINAL SCORE
# ========================================================================
echo ""
echo "=== Score Summary ==="
SCORE="0"
for key in f2p_bundler_default f2p_ts6_target f2p_baseurl_paths p2p_commonjs_node p2p_amd_node p2p_syntax antistub config_no_secrets; do
    W=${WEIGHTS[$key]}
    R=${RESULTS[$key]}
    CONTRIB=$(python3 -c "print(f'{$W * $R:.4f}')")
    SCORE=$(python3 -c "print(f'{$SCORE + $W * $R:.4f}')")
    STATUS="PASS"
    [ "$R" = "0" ] && STATUS="FAIL"
    echo "  $key: $STATUS (weight=$W, contrib=$CONTRIB)"
done

echo ""
echo "Final score: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# Write detailed breakdown
python3 -c "
import json
data = {
    'reward': $SCORE,
    'f2p_bundler_default': ${RESULTS[f2p_bundler_default]} * ${WEIGHTS[f2p_bundler_default]},
    'f2p_ts6_target': ${RESULTS[f2p_ts6_target]} * ${WEIGHTS[f2p_ts6_target]},
    'f2p_baseurl_paths': ${RESULTS[f2p_baseurl_paths]} * ${WEIGHTS[f2p_baseurl_paths]},
    'p2p_commonjs_node': ${RESULTS[p2p_commonjs_node]} * ${WEIGHTS[p2p_commonjs_node]},
    'p2p_amd_node': ${RESULTS[p2p_amd_node]} * ${WEIGHTS[p2p_amd_node]},
    'p2p_syntax': ${RESULTS[p2p_syntax]} * ${WEIGHTS[p2p_syntax]},
    'antistub': ${RESULTS[antistub]} * ${WEIGHTS[antistub]},
    'config_no_secrets': ${RESULTS[config_no_secrets]} * ${WEIGHTS[config_no_secrets]},
}
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f, indent=2)
" 2>/dev/null

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
