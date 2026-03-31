#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=0
DETAILS=""

add_result() {
    local weight="$1" pass="$2" tag="$3" desc="$4"
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" = "1" ]; then
        SCORE=$(python3 -c "print($SCORE + $weight)")
        DETAILS="${DETAILS}PASS ($weight) [$tag]: $desc\n"
    else
        DETAILS="${DETAILS}FAIL ($weight) [$tag]: $desc\n"
    fi
}

REPO="/workspace/openclaw"
CMD_TEST="$REPO/src/auto-reply/reply/commands.test.ts"
MEDIA_TEST="$REPO/src/media-understanding/media-understanding-misc.test.ts"

mkdir -p /logs/verifier

# ========== GATE: Required files exist and have balanced braces ==========
# [pr_diff] (0): Files must exist and be syntactically plausible

GATE_PASS=1
for f in "$CMD_TEST" "$MEDIA_TEST"; do
    if [ ! -f "$f" ]; then
        echo "GATE FAIL: $f does not exist"
        GATE_PASS=0
    fi
done

if [ "$GATE_PASS" = "1" ]; then
    for f in "$CMD_TEST" "$MEDIA_TEST"; do
        node -e "
          const fs = require('fs');
          const src = fs.readFileSync('$f', 'utf8');
          let depth = 0;
          for (const ch of src) {
            if (ch === '{') depth++;
            else if (ch === '}') depth--;
          }
          if (depth !== 0) process.exit(1);
        " 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "GATE FAIL: $f has unbalanced braces"
            GATE_PASS=0
        fi
    done
fi

if [ "$GATE_PASS" = "0" ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0}' > /logs/verifier/reward.json
    echo "GATE FAILED"
    exit 0
fi

# ========== Helper: extract non-comment code lines via node ==========
# Strips single-line (//) and multi-line (/* */) comments, preserving strings.
# This prevents gaming via comment injection.

extract_code() {
    node -e "
    const fs = require('fs');
    const src = fs.readFileSync(process.argv[1], 'utf8');
    let out = '', i = 0;
    while (i < src.length) {
        // Single-line comment
        if (src[i] === '/' && src[i+1] === '/') {
            while (i < src.length && src[i] !== '\n') i++;
        // Multi-line comment
        } else if (src[i] === '/' && src[i+1] === '*') {
            i += 2;
            while (i < src.length && !(src[i-1] === '*' && src[i] === '/')) i++;
            i++;
        // String literals (skip to preserve from false comment detection)
        } else if (src[i] === \"'\" || src[i] === '\"' || src[i] === '\`') {
            const q = src[i];
            out += src[i++];
            while (i < src.length && src[i] !== q) {
                if (src[i] === '\\\\') { out += src[i++]; }
                if (i < src.length) out += src[i++];
            }
            if (i < src.length) out += src[i++];
        } else {
            out += src[i++];
        }
    }
    process.stdout.write(out);
    " "$1" 2>/dev/null
}

# ========== FAIL-TO-PASS: Bug 1 — Extension boundary import removed ==========

# [pr_diff] (0.25): The buggy import from extensions/telegram/test-support must be removed
# This is the core of Bug 1. Comment-aware: an import commented out counts as removed.
# Accepts ANY fix that removes the import — no requirement on how the replacement works.
BUG1_IMPORT=$(node -e "
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
// Check each line for an actual import statement (not commented) from extensions/telegram
const lines = src.split('\n');
const hasImport = lines.some(line => {
    const t = line.trim();
    // Skip comment lines
    if (t.startsWith('//') || t.startsWith('*') || t.startsWith('/*')) return false;
    // Check for import ... from '...extensions/telegram/test-support...'
    return /^import\b/.test(t) && /extensions\/telegram\/test-support/.test(t);
});
// 1 = pass (import removed), 0 = fail (import still present)
process.stdout.write(hasImport ? '0' : '1');
" "$CMD_TEST" 2>/dev/null || echo "0")
add_result 0.25 "$BUG1_IMPORT" "pr_diff" "Extension boundary import removed from commands.test.ts"

# ========== FAIL-TO-PASS: Bug 2 — Path canonicalization in SSRF tests ==========

# [pr_diff] (0.20): SSRF test block uses path canonicalization (realpath, realpathSync, or resolve)
# Accepts: fs.realpath, fs.realpathSync, path.resolve, or any canonicalize/canonical pattern
# Comment-aware check on the SSRF describe block only
BUG2_CANON=$(node -e "
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
// Find the SSRF describe block
const ssrfIdx = src.indexOf('media understanding attachments SSRF');
if (ssrfIdx === -1) { process.stdout.write('0'); process.exit(); }
const ssrfBlock = src.slice(ssrfIdx);
// Get non-comment lines in SSRF block
const lines = ssrfBlock.split('\n');
const codeLines = lines.filter(l => {
    const t = l.trim();
    return t.length > 0 && !t.startsWith('//') && !t.startsWith('*') && !t.startsWith('/*');
});
const code = codeLines.join('\n');
// Accept realpath, realpathSync, path.resolve, or canonical* as canonicalization
const hasCanon = /realpath|realpathSync|path\.resolve|canonicali[sz]e/i.test(code);
process.stdout.write(hasCanon ? '1' : '0');
" "$MEDIA_TEST" 2>/dev/null || echo "0")
add_result 0.20 "$BUG2_CANON" "pr_diff" "SSRF tests use path canonicalization"

# [pr_diff] (0.10): Direct uncanonicalized path comparison removed from SSRF block
# The buggy code has: toHaveBeenCalledWith(attachmentPath, ...) or filePath !== attachmentPath
# A correct fix must NOT do direct equality on the raw symlink-prone path
BUG2_DIRECT=$(node -e "
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
const ssrfIdx = src.indexOf('media understanding attachments SSRF');
if (ssrfIdx === -1) { process.stdout.write('0'); process.exit(); }
const ssrfBlock = src.slice(ssrfIdx);
const lines = ssrfBlock.split('\n');
const codeLines = lines.filter(l => {
    const t = l.trim();
    return t.length > 0 && !t.startsWith('//') && !t.startsWith('*') && !t.startsWith('/*');
});
const code = codeLines.join('\n');
// Buggy patterns: direct comparison without canonicalization
const buggyCall = /toHaveBeenCalledWith\(\s*attachmentPath\s*,/.test(code);
const buggyCompare = /filePath\s*!==?\s*attachmentPath/.test(code);
// 1 = pass (buggy patterns removed), 0 = fail
process.stdout.write((buggyCall || buggyCompare) ? '0' : '1');
" "$MEDIA_TEST" 2>/dev/null || echo "0")
add_result 0.10 "$BUG2_DIRECT" "pr_diff" "No direct uncanonicalized path equality in SSRF tests"

# ========== FAIL-TO-PASS: Bug 1 fix — In-tree plugin construction ==========

# [pr_diff] (0.15): telegramCommandTestPlugin is constructed in-tree (not imported from extensions)
# Accepts: createChannelTestPluginBase, manual object with id:"telegram", or any ChannelPlugin construction
# Comment-aware, requires actual code assignment not just keyword mention
BUG1_INTREE=$(node -e "
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
const lines = src.split('\n');
const codeLines = lines.filter(l => {
    const t = l.trim();
    return t.length > 0 && !t.startsWith('//') && !t.startsWith('*') && !t.startsWith('/*');
});
const code = codeLines.join('\n');

// Check that telegramCommandTestPlugin is defined/assigned locally (not just imported)
// Accept: const/let/var telegramCommandTestPlugin = ..., or function that returns it
const hasDef = /(?:const|let|var|function)\s+telegramCommandTestPlugin\b/.test(code)
    || /telegramCommandTestPlugin\s*[:=]/.test(code);

// Check that the definition involves actual channel plugin construction
// Accept any of: createChannelTestPluginBase, ChannelPlugin type, id.*telegram, channel plugin fields
const hasConstruction = /createChannelTestPluginBase/.test(code)
    || (/id\s*:\s*['\"]telegram['\"]/.test(code) && /label\s*:\s*['\"]Telegram['\"]/.test(code))
    || /as\s+ChannelPlugin/.test(code)
    || /:\s*ChannelPlugin\s*[={]/.test(code);

process.stdout.write((hasDef && hasConstruction) ? '1' : '0');
" "$CMD_TEST" 2>/dev/null || echo "0")
add_result 0.15 "$BUG1_INTREE" "pr_diff" "telegramCommandTestPlugin constructed in-tree via SDK helpers or manual ChannelPlugin"

# ========== PASS-TO-PASS: Test structure preserved ==========

# [pr_diff] (0.05): telegramCommandTestPlugin is still available for use in tests
P2P_PLUGIN=$(node -e "
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
const lines = src.split('\n');
const codeLines = lines.filter(l => {
    const t = l.trim();
    return t.length > 0 && !t.startsWith('//') && !t.startsWith('*') && !t.startsWith('/*');
});
const code = codeLines.join('\n');
// Must appear in actual code at least twice (definition + usage)
const matches = code.match(/telegramCommandTestPlugin/g) || [];
process.stdout.write(matches.length >= 2 ? '1' : '0');
" "$CMD_TEST" 2>/dev/null || echo "0")
add_result 0.05 "$P2P_PLUGIN" "pr_diff" "telegramCommandTestPlugin defined and used in test code"

# [pr_diff] (0.05): SSRF test block still has MediaAttachmentCache and O_NOFOLLOW
P2P_SSRF=$(node -e "
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
const lines = src.split('\n');
const codeLines = lines.filter(l => {
    const t = l.trim();
    return t.length > 0 && !t.startsWith('//') && !t.startsWith('*') && !t.startsWith('/*');
});
const code = codeLines.join('\n');
const has = /MediaAttachmentCache/.test(code) && /O_NOFOLLOW/.test(code);
process.stdout.write(has ? '1' : '0');
" "$MEDIA_TEST" 2>/dev/null || echo "0")
add_result 0.05 "$P2P_SSRF" "pr_diff" "MediaAttachmentCache SSRF test structure preserved"

# ========== ANTI-STUB: Plugin definition has substance ==========

# [pr_diff] (0.10): Plugin definition is not a trivial stub
# Requires that the telegramCommandTestPlugin definition spans a meaningful amount of code
ANTI_STUB=$(node -e "
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
const lines = src.split('\n');

// Find where telegramCommandTestPlugin is defined
let defStart = -1;
for (let i = 0; i < lines.length; i++) {
    const t = lines[i].trim();
    if (t.startsWith('//') || t.startsWith('*') || t.startsWith('/*')) continue;
    if (/(?:const|let|var)\s+telegramCommandTestPlugin\b/.test(t) || /telegramCommandTestPlugin\s*[:=]/.test(t)) {
        defStart = i;
        break;
    }
}
if (defStart === -1) { process.stdout.write('0'); process.exit(); }

// Count non-blank, non-comment lines from definition until we see the next top-level declaration or describe
let count = 0;
let braceDepth = 0;
let started = false;
for (let i = defStart; i < lines.length && i < defStart + 300; i++) {
    const t = lines[i].trim();
    if (t.startsWith('//') || t.startsWith('*') || t.startsWith('/*')) continue;
    if (t.length === 0) continue;
    count++;
    for (const ch of lines[i]) {
        if (ch === '{') { braceDepth++; started = true; }
        if (ch === '}') braceDepth--;
    }
    if (started && braceDepth <= 0 && i > defStart) break;
}
// Require at least 8 meaningful lines (rejects trivial stubs like {} as any)
process.stdout.write(count >= 8 ? '1' : '0');
" "$CMD_TEST" 2>/dev/null || echo "0")
add_result 0.10 "$ANTI_STUB" "pr_diff" "telegramCommandTestPlugin is not a trivial stub (>=8 meaningful lines)"

# ========== CONFIG-DERIVED: Agent config rules ==========

# [agent_config] (0.05): "core code and tests must not deep-import bundled plugin internals" — CLAUDE.md:34
# Check ALL import statements (not just the known buggy one) for extensions/ paths
CONFIG_NOIMPORT=$(node -e "
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
const lines = src.split('\n');
const hasDeepImport = lines.some(line => {
    const t = line.trim();
    if (t.startsWith('//') || t.startsWith('*') || t.startsWith('/*')) return false;
    return /^import\b/.test(t) && /['\"].*extensions\//.test(t);
});
process.stdout.write(hasDeepImport ? '0' : '1');
" "$CMD_TEST" 2>/dev/null || echo "0")
add_result 0.05 "$CONFIG_NOIMPORT" "agent_config" "No extension deep-imports in core test — CLAUDE.md:34"

# ========== Print results ==========
echo "========================================="
echo "Test Results"
echo "========================================="
printf "$DETAILS"
echo "========================================="
echo "Score: $SCORE / $TOTAL"
echo "========================================="

# Write reward
echo "$SCORE" > /logs/verifier/reward.txt

# Write detailed JSON
python3 -c "
import json
score = float('$SCORE')
data = {
    'reward': round(score, 4),
    'behavioral': round(min(score, 0.70), 4),
    'regression': round(min(max(score - 0.70, 0), 0.10), 4),
    'structural': round(min(max(score - 0.80, 0), 0.15), 4),
    'config': round(min(max(score - 0.95, 0), 0.05), 4)
}
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f, indent=2)
" 2>/dev/null

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
