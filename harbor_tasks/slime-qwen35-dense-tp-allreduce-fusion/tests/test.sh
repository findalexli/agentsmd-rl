#!/usr/bin/env bash
set -uo pipefail
set +e

REPO="/workspace/slime"
TARGET="$REPO/docker/patch/latest/sglang.patch"
mkdir -p /logs/verifier

echo "=== GATE: Patch file exists and is non-empty ==="
# [pr_diff] (0.00): Patch file must exist
if [ ! -s "$TARGET" ]; then
    echo "FAIL: sglang.patch missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "PASS: Patch file exists"

echo ""
echo "=== GATE: Valid unified diff with qwen3_5.py section ==="
# [pr_diff] (0.00): Must be a valid unified diff targeting qwen3_5.py
python3 -c "
import re, sys
content = open('$TARGET').read()
if not re.search(r'^diff --git ', content, re.MULTILINE):
    print('FAIL: No diff headers'); sys.exit(1)
if 'qwen3_5.py' not in content:
    print('FAIL: No qwen3_5.py section'); sys.exit(1)
print('PASS: Valid unified diff with qwen3_5.py section')
" 2>&1
if [ $? -ne 0 ]; then
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

echo ""
echo "=== F2P Baseline: Verify original patch lacks the fix ==="
# Save original (buggy) patch for F2P comparison
cd "$REPO"
git show HEAD:docker/patch/latest/sglang.patch > /tmp/original_patch.txt 2>/dev/null
python3 << 'PYEOF'
import re
content = open("/tmp/original_patch.txt").read()
# Find qwen3_5.py diff section
sections = re.split(r'^diff --git ', content, flags=re.MULTILINE)
qwen = next((s for s in sections if 'qwen3_5.py' in s.split('\n', 1)[0]), '')
# Get added code lines (not comments, not +++ headers)
added = [l[1:].strip() for l in qwen.splitlines()
         if l.startswith('+') and not l.startswith('+++')]
code_lines = [l for l in added if l and not l.startswith('#')]
code_text = ' '.join(code_lines)
has_fix = bool(re.search(r'isinstance.*Qwen2MoeSparseMoeBlock', code_text))
has_fusion = 'should_fuse_mlp_allreduce_with_next_layer' in code_text
if has_fix and has_fusion:
    print("WARNING: Original patch already has fix — F2P may be unreliable")
else:
    print(f"PASS: Original patch missing fix (isinstance_moe={has_fix}, fusion_api={has_fusion})")
PYEOF
echo ""

# === ALL CHECKS IN ONE PYTHON BLOCK ===
python3 << 'PYEOF'
import re, sys, json

TARGET = "/workspace/slime/docker/patch/latest/sglang.patch"
content = open(TARGET).read()

# --- Helpers ---

def get_qwen_section(text):
    """Extract the qwen3_5.py diff section."""
    sections = re.split(r'^diff --git ', text, flags=re.MULTILINE)
    for s in sections:
        if 'qwen3_5.py' in s.split('\n', 1)[0]:
            return s
    return ''

def get_subsection(text, start_marker, end_marker=None):
    """Get text between markers."""
    idx = text.find(start_marker)
    if idx == -1:
        return ''
    if end_marker:
        end = text.find(end_marker, idx + len(start_marker))
        return text[idx:end] if end != -1 else text[idx:]
    return text[idx:]

def added_code_lines(section):
    """Extract non-comment, non-empty added code lines from a patch section.
    Only lines starting with '+' (added), stripped of prefix, that aren't comments."""
    lines = []
    for line in section.splitlines():
        if line.startswith('+') and not line.startswith('+++'):
            stripped = line[1:].strip()
            if stripped and not stripped.startswith('#'):
                lines.append(stripped)
    return lines

qwen = get_qwen_section(content)
if not qwen:
    print("FAIL: No qwen3_5.py section found")
    open('/logs/verifier/reward.txt', 'w').write("0.0\n")
    sys.exit(0)

score = 0.0
details = {}

# ==========================================
# CHECK 1 (0.25): LinearDecoderLayer forward — MoE branching with fusion API
# [pr_diff] (0.25): LinearDecoderLayer forward must branch on MoE vs dense MLP
# ==========================================
linear_section = get_subsection(qwen, 'Qwen3_5LinearDecoderLayer', 'Qwen3_5AttentionDecoderLayer')
linear_code = added_code_lines(linear_section)

# Require: isinstance check for MoE type in actual code
c1_isinstance = any(re.search(r'isinstance.*Qwen2MoeSparseMoeBlock', l) for l in linear_code)
# Require: call to should_fuse_mlp_allreduce_with_next_layer in actual code
c1_fusion_api = any('should_fuse_mlp_allreduce_with_next_layer' in l for l in linear_code)
# Require: if/else branching structure in added code
c1_branch = sum(1 for l in linear_code if re.match(r'^(if |else:|elif )', l)) >= 2

if c1_isinstance and c1_fusion_api and c1_branch:
    print("PASS [0.25]: LinearDecoderLayer forward has MoE branching with fusion API")
    score += 0.25
    details['linear_forward'] = 'pass'
else:
    print(f"FAIL [0.25]: LinearDecoderLayer forward (isinstance={c1_isinstance}, fusion_api={c1_fusion_api}, branch={c1_branch})")
    details['linear_forward'] = 'fail'

# ==========================================
# CHECK 2 (0.25): AttentionDecoderLayer forward — MoE branching with fusion API
# [pr_diff] (0.25): AttentionDecoderLayer forward must branch on MoE vs dense MLP
# ==========================================
attn_section = get_subsection(qwen, 'Qwen3_5AttentionDecoderLayer')
attn_code = added_code_lines(attn_section)

c2_isinstance = any(re.search(r'isinstance.*Qwen2MoeSparseMoeBlock', l) for l in attn_code)
c2_fusion_api = any('should_fuse_mlp_allreduce_with_next_layer' in l for l in attn_code)
c2_branch = sum(1 for l in attn_code if re.match(r'^(if |else:|elif )', l)) >= 2

if c2_isinstance and c2_fusion_api and c2_branch:
    print("PASS [0.25]: AttentionDecoderLayer forward has MoE branching with fusion API")
    score += 0.25
    details['attn_forward'] = 'pass'
else:
    print(f"FAIL [0.25]: AttentionDecoderLayer forward (isinstance={c2_isinstance}, fusion_api={c2_fusion_api}, branch={c2_branch})")
    details['attn_forward'] = 'fail'

# ==========================================
# CHECK 3 (0.10): LinearDecoderLayer __init__ — allow_allreduce_fusion
# [pr_diff] (0.10): Must pass allow_allreduce_fusion=True to LayerCommunicator
# ==========================================
# Look only in __init__ portion (before first 'def forward')
linear_init = get_subsection(linear_section, 'Qwen3_5LinearDecoderLayer', 'def forward')
linear_init_code = added_code_lines(linear_init)
# Must be a keyword argument assignment, not just the string in a comment
c3_kwarg = any(re.search(r'allow_allreduce_fusion\s*=', l) for l in linear_init_code)

if c3_kwarg:
    print("PASS [0.10]: LinearDecoderLayer __init__ has allow_allreduce_fusion=")
    score += 0.10
    details['linear_init'] = 'pass'
else:
    print("FAIL [0.10]: LinearDecoderLayer __init__ missing allow_allreduce_fusion kwarg")
    details['linear_init'] = 'fail'

# ==========================================
# CHECK 4 (0.10): AttentionDecoderLayer __init__ — allow_allreduce_fusion
# [pr_diff] (0.10): Must pass allow_allreduce_fusion=True to LayerCommunicator
# ==========================================
attn_init = get_subsection(attn_section, 'Qwen3_5AttentionDecoderLayer', 'def forward')
attn_init_code = added_code_lines(attn_init)
c4_kwarg = any(re.search(r'allow_allreduce_fusion\s*=', l) for l in attn_init_code)

if c4_kwarg:
    print("PASS [0.10]: AttentionDecoderLayer __init__ has allow_allreduce_fusion=")
    score += 0.10
    details['attn_init'] = 'pass'
else:
    print("FAIL [0.10]: AttentionDecoderLayer __init__ missing allow_allreduce_fusion kwarg")
    details['attn_init'] = 'fail'

# ==========================================
# CHECK 5 (0.10): Conditional postprocess_layer in both layers
# [pr_diff] (0.10): When fusion active, skip postprocess_layer; set _sglang_needs_allreduce_fusion
# ==========================================
all_code = linear_code + attn_code
# _sglang_needs_allreduce_fusion must appear in actual code in both layers
c5_fusion_attr_linear = sum(1 for l in linear_code if '_sglang_needs_allreduce_fusion' in l)
c5_fusion_attr_attn = sum(1 for l in attn_code if '_sglang_needs_allreduce_fusion' in l)
# postprocess_layer must still be called conditionally (in else branch)
c5_postprocess = sum(1 for l in all_code if 'postprocess_layer' in l)

if c5_fusion_attr_linear >= 1 and c5_fusion_attr_attn >= 1 and c5_postprocess >= 1:
    print(f"PASS [0.10]: Conditional postprocess_layer (fusion_attr: {c5_fusion_attr_linear}+{c5_fusion_attr_attn}, postprocess: {c5_postprocess})")
    score += 0.10
    details['conditional_postprocess'] = 'pass'
else:
    print(f"FAIL [0.10]: Conditional postprocess (linear_attr={c5_fusion_attr_linear}, attn_attr={c5_fusion_attr_attn}, postprocess={c5_postprocess})")
    details['conditional_postprocess'] = 'fail'

# ==========================================
# CHECK 6 (0.10): Pass-to-pass — existing patch sections preserved
# [pr_diff] (0.10): Other patch sections (model_config, qwen3_vl, etc.) must be intact
# ==========================================
required = ['python/sglang/srt/configs/model_config.py', 'python/sglang/srt/models/qwen3_vl.py']
missing = [r for r in required if r not in content]
has_is_last = content.count('is_last_layer') >= 2

if not missing and has_is_last:
    print("PASS [0.10]: Existing patch sections preserved")
    score += 0.10
    details['p2p'] = 'pass'
else:
    print(f"FAIL [0.10]: Missing sections {missing}, is_last_layer={has_is_last}")
    details['p2p'] = 'fail'

# ==========================================
# CHECK 7 (0.05): Anti-stub — enough substantive added code
# [pr_diff] (0.05): Both forward methods must have real logic, not stubs
# ==========================================
# Count non-trivial added code lines (> 8 chars, not just closing parens/pass/return)
trivial = {'pass', 'return', 'else:', ')', '}', '']
substantive = [l for l in all_code
               if l not in trivial
               and not l.startswith(')')
               and len(l) > 8]
if len(substantive) >= 12:
    print(f"PASS [0.05]: {len(substantive)} substantive added code lines (anti-stub)")
    score += 0.05
    details['anti_stub'] = 'pass'
else:
    print(f"FAIL [0.05]: Only {len(substantive)} substantive code lines, need >= 12")
    details['anti_stub'] = 'fail'

# ==========================================
# CHECK 8 (0.05): Config — changes contained to patch file
# [agent_config] (0.05): "Keep test scope small and behavior-focused" — .claude/skills/add-tests-and-ci/SKILL.md:25
# ==========================================
import subprocess
try:
    result = subprocess.run(['git', 'diff', '--name-only', 'HEAD'],
                          capture_output=True, text=True, cwd='/workspace/slime')
    changed = len([f for f in result.stdout.strip().split('\n') if f])
except:
    changed = 0

if changed <= 3:
    print(f"PASS [0.05]: Changes contained ({changed} files)")
    score += 0.05
    details['contained'] = 'pass'
else:
    print(f"FAIL [0.05]: Too many files changed ({changed})")
    details['contained'] = 'fail'

# === Output ===
print(f"\n===================================")
print(f"Total: {score:.2f} / 1.00")
print(f"===================================")

open('/logs/verifier/reward.txt', 'w').write(f"{score:.2f}\n")

behavioral = round(score - max(score - 0.80, 0), 2)
json.dump({
    'reward': round(score, 2),
    'behavioral': round(min(score, 0.80), 2),
    'regression': round(min(max(score - 0.80, 0), 0.10), 2),
    'structural': round(min(max(score - 0.90, 0), 0.05), 2),
    'config': round(min(max(score - 0.95, 0), 0.05), 2),
}, open('/logs/verifier/reward.json', 'w'), indent=2)

PYEOF

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
