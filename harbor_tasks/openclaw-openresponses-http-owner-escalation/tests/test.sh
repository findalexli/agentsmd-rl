#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=0

log() { echo "$@"; }
add_score() {
    local weight=$1 pass=$2 label=$3
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" = "1" ]; then
        SCORE=$(python3 -c "print($SCORE + $weight)")
        log "  PASS ($weight): $label"
    else
        log "  FAIL ($weight): $label"
    fi
}

REPO="/workspace/openclaw"
SRC="$REPO/src/gateway/openresponses-http.ts"

log "=== GATE: TypeScript syntax check ==="
node -e "
const ts = require('typescript');
const src = require('fs').readFileSync('$SRC', 'utf8');
const result = ts.transpileModule(src, {compilerOptions: {target: ts.ScriptTarget.ESNext, module: ts.ModuleKind.ESNext, jsx: ts.JsxEmit.Preserve}});
if (!result.outputText) process.exit(1);
" 2>/dev/null
if [ $? -ne 0 ]; then
    log "  GATE FAIL: TypeScript syntax error — aborting"
    mkdir -p /logs/verifier
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
log "  GATE PASS: TypeScript syntax valid"

log ""
log "=== Fail-to-pass: Core bug detection (TS AST) ==="

# [pr_diff] (0.35): Inside runResponsesAgentCommand, the agentCommandFromIngress call
# must NOT pass senderIsOwner as a boolean literal `true`.
# This is the core bug — accepts ANY fix (param forwarding, variable, negation, etc.)
F2P_CORE=$(node -e "
const ts = require('typescript');
const fs = require('fs');
const source = fs.readFileSync('$SRC', 'utf8');
const sf = ts.createSourceFile('src.ts', source, ts.ScriptTarget.Latest, true);

// Find the runResponsesAgentCommand function
let helperFunc = null;
function findHelper(node) {
    if (ts.isFunctionDeclaration(node) && node.name && node.name.text === 'runResponsesAgentCommand') {
        helperFunc = node;
        return;
    }
    // Also check variable declarations with arrow functions
    if (ts.isVariableStatement(node)) {
        const decl = node.declarationList.declarations[0];
        if (decl && decl.name && ts.isIdentifier(decl.name) && decl.name.text === 'runResponsesAgentCommand') {
            helperFunc = decl.initializer;
            return;
        }
    }
    ts.forEachChild(node, findHelper);
}
findHelper(sf);

if (!helperFunc) {
    console.log('NO_FUNC');
    process.exit(0);
}

// Find call to agentCommandFromIngress within the helper
let foundHardcodedTrue = false;
let foundSenderIsOwnerProp = false;

function walkHelper(node) {
    if (ts.isCallExpression(node)) {
        const callee = node.expression;
        const calleeName = ts.isIdentifier(callee) ? callee.text :
            (ts.isPropertyAccessExpression(callee) ? callee.name.text : '');
        if (calleeName === 'agentCommandFromIngress') {
            // Check the first argument (options object)
            const firstArg = node.arguments[0];
            if (firstArg && ts.isObjectLiteralExpression(firstArg)) {
                for (const prop of firstArg.properties) {
                    if (ts.isPropertyAssignment(prop) && ts.isIdentifier(prop.name) && prop.name.text === 'senderIsOwner') {
                        foundSenderIsOwnerProp = true;
                        // Check if value is literal true
                        if (prop.initializer.kind === ts.SyntaxKind.TrueKeyword) {
                            foundHardcodedTrue = true;
                        }
                    }
                    // Also check shorthand property (just senderIsOwner without colon)
                    if (ts.isShorthandPropertyAssignment(prop) && prop.name.text === 'senderIsOwner') {
                        foundSenderIsOwnerProp = true;
                        // Shorthand means it uses a variable — NOT hardcoded true
                    }
                }
            }
            // Also check if spread syntax includes senderIsOwner from params
            // (we accept any non-hardcoded approach)
        }
    }
    ts.forEachChild(node, walkHelper);
}
walkHelper(helperFunc);

if (!foundSenderIsOwnerProp) {
    // senderIsOwner might be passed via spread — check if params are spread into the call
    let hasSpread = false;
    function checkSpread(node) {
        if (ts.isSpreadAssignment(node) || ts.isSpreadElement(node)) hasSpread = true;
        ts.forEachChild(node, checkSpread);
    }
    checkSpread(helperFunc);
    if (hasSpread) {
        console.log('PASS_SPREAD');
    } else {
        console.log('NO_PROP');
    }
} else if (foundHardcodedTrue) {
    console.log('HARDCODED_TRUE');
} else {
    console.log('PASS');
}
" 2>/dev/null)

if [ "$F2P_CORE" = "PASS" ] || [ "$F2P_CORE" = "PASS_SPREAD" ]; then
    add_score 0.35 1 "agentCommandFromIngress call does not hardcode senderIsOwner: true"
else
    add_score 0.35 0 "agentCommandFromIngress call still hardcodes senderIsOwner: true (result: $F2P_CORE)"
fi

# [pr_diff] (0.20): runResponsesAgentCommand accepts senderIsOwner from its callers.
# Check that the function signature/params include senderIsOwner,
# OR that the function otherwise receives it (e.g., via a broader options object).
# Accepts: explicit param, destructured param, options object, etc.
F2P_PARAM=$(node -e "
const ts = require('typescript');
const fs = require('fs');
const source = fs.readFileSync('$SRC', 'utf8');
const sf = ts.createSourceFile('src.ts', source, ts.ScriptTarget.Latest, true);

let helperFunc = null;
function findHelper(node) {
    if (ts.isFunctionDeclaration(node) && node.name && node.name.text === 'runResponsesAgentCommand') {
        helperFunc = node;
        return;
    }
    if (ts.isVariableStatement(node)) {
        const decl = node.declarationList.declarations[0];
        if (decl && decl.name && ts.isIdentifier(decl.name) && decl.name.text === 'runResponsesAgentCommand') {
            helperFunc = decl.initializer;
            return;
        }
    }
    ts.forEachChild(node, findHelper);
}
findHelper(sf);

if (!helperFunc) { console.log('NO_FUNC'); process.exit(0); }

// Check if any parameter type or binding includes senderIsOwner
let found = false;
const funcText = source.substring(helperFunc.getStart(sf), helperFunc.getEnd());

function walkParams(node) {
    // Check type literal members
    if (ts.isPropertySignature(node) && ts.isIdentifier(node.name) && node.name.text === 'senderIsOwner') {
        found = true;
    }
    // Check binding patterns
    if (ts.isBindingElement(node) && ts.isIdentifier(node.name) && node.name.text === 'senderIsOwner') {
        found = true;
    }
    ts.forEachChild(node, walkParams);
}

// Walk the parameter declarations
if (helperFunc.parameters) {
    for (const param of helperFunc.parameters) {
        walkParams(param);
    }
}

// Also accept if the function body accesses params.senderIsOwner or similar
// (the parameter might be typed elsewhere as an interface)
function walkBody(node) {
    if (ts.isPropertyAccessExpression(node) && ts.isIdentifier(node.name) && node.name.text === 'senderIsOwner') {
        // Check it's reading from a parameter-like identifier
        if (ts.isIdentifier(node.expression)) {
            const name = node.expression.text;
            if (name === 'params' || name === 'options' || name === 'opts' || name === 'args' || name === 'config') {
                found = true;
            }
        }
    }
    // Also check destructured access
    if (ts.isShorthandPropertyAssignment(node) && node.name.text === 'senderIsOwner') {
        found = true;
    }
    ts.forEachChild(node, walkBody);
}
if (helperFunc.body) walkBody(helperFunc.body);

console.log(found ? 'PASS' : 'FAIL');
" 2>/dev/null)

if [ "$F2P_PARAM" = "PASS" ]; then
    add_score 0.20 1 "runResponsesAgentCommand accepts senderIsOwner from callers"
else
    add_score 0.20 0 "runResponsesAgentCommand does not accept senderIsOwner from callers (result: $F2P_PARAM)"
fi

# [pr_diff] (0.15): Call sites in handleOpenResponsesHttpRequest pass senderIsOwner
# as false (or any non-true expression). Both streaming and non-streaming paths.
F2P_CALLSITES=$(node -e "
const ts = require('typescript');
const fs = require('fs');
const source = fs.readFileSync('$SRC', 'utf8');
const sf = ts.createSourceFile('src.ts', source, ts.ScriptTarget.Latest, true);

// Find handleOpenResponsesHttpRequest
let handlerFunc = null;
function findHandler(node) {
    if (ts.isFunctionDeclaration(node) && node.name && node.name.text === 'handleOpenResponsesHttpRequest') {
        handlerFunc = node;
        return;
    }
    ts.forEachChild(node, findHandler);
}
findHandler(sf);

if (!handlerFunc) { console.log('0'); process.exit(0); }

// Find all calls to runResponsesAgentCommand within the handler
let callsWithNonTrueSender = 0;
let totalCalls = 0;

function walkCalls(node) {
    if (ts.isCallExpression(node)) {
        const callee = node.expression;
        const calleeName = ts.isIdentifier(callee) ? callee.text : '';
        // Also handle await expressions
        if (calleeName === 'runResponsesAgentCommand') {
            totalCalls++;
            const firstArg = node.arguments[0];
            if (firstArg && ts.isObjectLiteralExpression(firstArg)) {
                for (const prop of firstArg.properties) {
                    if (ts.isPropertyAssignment(prop) && ts.isIdentifier(prop.name) && prop.name.text === 'senderIsOwner') {
                        // Accept anything that's not literal true
                        if (prop.initializer.kind !== ts.SyntaxKind.TrueKeyword) {
                            callsWithNonTrueSender++;
                        }
                    }
                    if (ts.isShorthandPropertyAssignment(prop) && prop.name.text === 'senderIsOwner') {
                        // Shorthand means a variable — not literal true
                        callsWithNonTrueSender++;
                    }
                }
                // Check if senderIsOwner is passed via spread
                for (const prop of firstArg.properties) {
                    if (ts.isSpreadAssignment(prop)) {
                        callsWithNonTrueSender++;
                        break;
                    }
                }
            }
        }
    }
    ts.forEachChild(node, walkCalls);
}
walkCalls(handlerFunc);

console.log(callsWithNonTrueSender + '/' + totalCalls);
" 2>/dev/null)

GOOD_CALLS=$(echo "$F2P_CALLSITES" | cut -d/ -f1)
TOTAL_CALLS=$(echo "$F2P_CALLSITES" | cut -d/ -f2)

if [ "${GOOD_CALLS:-0}" -ge 2 ]; then
    add_score 0.15 1 "Both call paths pass non-owner senderIsOwner ($F2P_CALLSITES)"
elif [ "${GOOD_CALLS:-0}" -ge 1 ]; then
    # Partial credit: at least one path fixed
    add_score 0.10 1 "At least one call path passes non-owner senderIsOwner ($F2P_CALLSITES)"
    add_score 0.05 0 "Not all call paths fixed ($F2P_CALLSITES)"
else
    add_score 0.15 0 "No call paths pass non-owner senderIsOwner ($F2P_CALLSITES)"
fi

log ""
log "=== Regression: Pass-to-pass ==="

# [pr_diff] (0.05): handleOpenResponsesHttpRequest is still exported
node -e "
const ts = require('typescript');
const fs = require('fs');
const source = fs.readFileSync('$SRC', 'utf8');
const sf = ts.createSourceFile('src.ts', source, ts.ScriptTarget.Latest, true);
let found = false;
function walk(node) {
    if (ts.isFunctionDeclaration(node) && node.name && node.name.text === 'handleOpenResponsesHttpRequest') {
        if (node.modifiers && node.modifiers.some(m => m.kind === ts.SyntaxKind.ExportKeyword)) {
            found = true;
        }
    }
    ts.forEachChild(node, walk);
}
walk(sf);
process.exit(found ? 0 : 1);
" 2>/dev/null
add_score 0.05 $((1 - $?)) "handleOpenResponsesHttpRequest remains exported"

# [pr_diff] (0.05): agentCommandFromIngress is still called (not removed/renamed)
node -e "
const ts = require('typescript');
const fs = require('fs');
const source = fs.readFileSync('$SRC', 'utf8');
const sf = ts.createSourceFile('src.ts', source, ts.ScriptTarget.Latest, true);
let found = false;
function walk(node) {
    if (ts.isCallExpression(node) && ts.isIdentifier(node.expression) && node.expression.text === 'agentCommandFromIngress') {
        found = true;
    }
    ts.forEachChild(node, walk);
}
walk(sf);
process.exit(found ? 0 : 1);
" 2>/dev/null
add_score 0.05 $((1 - $?)) "agentCommandFromIngress call preserved"

# [pr_diff] (0.05): allowModelOverride: true still present in agentCommandFromIngress call
node -e "
const ts = require('typescript');
const fs = require('fs');
const source = fs.readFileSync('$SRC', 'utf8');
const sf = ts.createSourceFile('src.ts', source, ts.ScriptTarget.Latest, true);
let found = false;
function walk(node) {
    if (ts.isPropertyAssignment(node) && ts.isIdentifier(node.name) && node.name.text === 'allowModelOverride') {
        if (node.initializer.kind === ts.SyntaxKind.TrueKeyword) found = true;
    }
    ts.forEachChild(node, walk);
}
walk(sf);
process.exit(found ? 0 : 1);
" 2>/dev/null
add_score 0.05 $((1 - $?)) "allowModelOverride: true preserved"

log ""
log "=== Structural: Anti-gaming ==="

# [pr_diff] (0.05): Anti-stub — file not gutted and runResponsesAgentCommand has real body
ANTI_STUB=$(node -e "
const ts = require('typescript');
const fs = require('fs');
const source = fs.readFileSync('$SRC', 'utf8');
const lines = source.split('\n').length;
if (lines < 400) { console.log('GUTTED'); process.exit(0); }

const sf = ts.createSourceFile('src.ts', source, ts.ScriptTarget.Latest, true);
let helperStmts = 0;
function findHelper(node) {
    if (ts.isFunctionDeclaration(node) && node.name && node.name.text === 'runResponsesAgentCommand') {
        if (node.body) {
            // Count non-trivial statements (not just return/pass)
            helperStmts = node.body.statements.length;
        }
    }
    ts.forEachChild(node, findHelper);
}
findHelper(sf);

if (helperStmts < 1) { console.log('STUB'); process.exit(0); }
console.log('OK');
" 2>/dev/null)

if [ "$ANTI_STUB" = "OK" ]; then
    add_score 0.05 1 "File not gutted and helper has real body"
else
    add_score 0.05 0 "File appears gutted or stubbed ($ANTI_STUB)"
fi

log ""
log "=== Config-derived ==="

# [agent_config] (0.05): "Prefer strict typing; avoid any" — CLAUDE.md:144 @ 1a75906
# The senderIsOwner parameter should be typed (boolean), not any/unknown
CONFIG_TYPE=$(node -e "
const ts = require('typescript');
const fs = require('fs');
const source = fs.readFileSync('$SRC', 'utf8');
const sf = ts.createSourceFile('src.ts', source, ts.ScriptTarget.Latest, true);

let typed = false;
function walk(node) {
    // Check property signatures in type literals (function param types)
    if (ts.isPropertySignature(node) && ts.isIdentifier(node.name) && node.name.text === 'senderIsOwner') {
        if (node.type && node.type.kind === ts.SyntaxKind.BooleanKeyword) {
            typed = true;
        }
    }
    ts.forEachChild(node, walk);
}
walk(sf);
console.log(typed ? 'PASS' : 'FAIL');
" 2>/dev/null)

if [ "$CONFIG_TYPE" = "PASS" ]; then
    add_score 0.05 1 "senderIsOwner typed as boolean (strict typing per CLAUDE.md)"
else
    add_score 0.05 0 "senderIsOwner not explicitly typed as boolean"
fi

log ""
log "=== Results ==="
log "Score: $SCORE / $TOTAL"

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt

# Build JSON breakdown
python3 -c "
import json
score = float('$SCORE')
data = {
    'reward': score,
    'behavioral': min(score, 0.70),
    'regression': min(max(score - 0.70, 0), 0.15),
    'structural': min(max(score - 0.85, 0), 0.05),
    'config': min(max(score - 0.90, 0), 0.05)
}
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f, indent=2)
print(json.dumps(data, indent=2))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
