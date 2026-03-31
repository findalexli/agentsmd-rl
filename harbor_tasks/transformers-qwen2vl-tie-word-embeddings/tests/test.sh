#!/usr/bin/env bash
set +e

REPO="/repo"
REWARD=0
MAX=100

add() { REWARD=$((REWARD + $1)); }

mkdir -p /logs/verifier

###############################################################################
# GATE: Syntax check on all changed files
###############################################################################
# [pr_diff] (gate): All changed files must parse
GATE_PASS=true
for f in \
    src/transformers/models/qwen2_vl/configuration_qwen2_vl.py \
    src/transformers/models/qwen2_5_vl/configuration_qwen2_5_vl.py \
    src/transformers/models/colqwen2/configuration_colqwen2.py \
    src/transformers/models/colmodernvbert/configuration_colmodernvbert.py \
    src/transformers/models/modernvbert/modeling_modernvbert.py \
    src/transformers/models/modernvbert/modular_modernvbert.py; do
    if ! python3 -c "import ast; ast.parse(open('$REPO/$f').read())" 2>/dev/null; then
        echo "GATE FAIL: $f has syntax errors"
        GATE_PASS=false
    fi
done
if [ "$GATE_PASS" = false ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "structural": 0.0, "config": 0.0}' > /logs/verifier/reward.json
    echo "GATE FAIL — aborting"
    exit 0
fi
echo "GATE PASS: all files parse"

###############################################################################
# F2P1 (0.25): Qwen2VLTextConfig must NOT define tie_word_embeddings as a field
###############################################################################
# [pr_diff] (0.25): Removing the erroneous dataclass field from the text sub-config
F2P1=$(cd "$REPO" && python3 -c "
from dataclasses import fields
from transformers.models.qwen2_vl.configuration_qwen2_vl import Qwen2VLTextConfig
field_names = {f.name for f in fields(Qwen2VLTextConfig)}
if 'tie_word_embeddings' in field_names:
    print('FAIL')
else:
    print('PASS')
" 2>&1 || echo "ERROR")
if [ "$F2P1" = "PASS" ]; then
    echo "F2P1 PASS (0.25): Qwen2VLTextConfig has no tie_word_embeddings field"
    add 25
else
    echo "F2P1 FAIL: Qwen2VLTextConfig still defines tie_word_embeddings ($F2P1)"
fi

###############################################################################
# F2P2 (0.25): Qwen2_5_VLTextConfig must NOT define tie_word_embeddings as a field
###############################################################################
# [pr_diff] (0.25): Removing the erroneous dataclass field from the 2.5 text sub-config
F2P2=$(cd "$REPO" && python3 -c "
from dataclasses import fields
from transformers.models.qwen2_5_vl.configuration_qwen2_5_vl import Qwen2_5_VLTextConfig
field_names = {f.name for f in fields(Qwen2_5_VLTextConfig)}
if 'tie_word_embeddings' in field_names:
    print('FAIL')
else:
    print('PASS')
" 2>&1 || echo "ERROR")
if [ "$F2P2" = "PASS" ]; then
    echo "F2P2 PASS (0.25): Qwen2_5_VLTextConfig has no tie_word_embeddings field"
    add 25
else
    echo "F2P2 FAIL: Qwen2_5_VLTextConfig still defines tie_word_embeddings ($F2P2)"
fi

###############################################################################
# F2P3 (0.15): VL parent configs also must not define tie_word_embeddings
###############################################################################
# [pr_diff] (0.15): Qwen2VLConfig and Qwen2_5_VLConfig should not have the field either
F2P3=$(cd "$REPO" && python3 -c "
from dataclasses import fields
from transformers.models.qwen2_vl.configuration_qwen2_vl import Qwen2VLConfig
from transformers.models.qwen2_5_vl.configuration_qwen2_5_vl import Qwen2_5_VLConfig
ok = True
for cls in [Qwen2VLConfig, Qwen2_5_VLConfig]:
    field_names = {f.name for f in fields(cls)}
    if 'tie_word_embeddings' in field_names:
        print(f'FAIL: {cls.__name__} still defines tie_word_embeddings')
        ok = False
if ok:
    print('PASS')
" 2>&1 || echo "ERROR")
if echo "$F2P3" | grep -q "^PASS$"; then
    echo "F2P3 PASS (0.15): VL parent configs have no tie_word_embeddings field"
    add 15
else
    echo "F2P3 FAIL: VL parent config still defines tie_word_embeddings ($F2P3)"
fi

###############################################################################
# P2P (0.10): Config instantiation and serialization still works
###############################################################################
# [pr_diff] (0.10): Configs must still be constructable and round-trip via to_dict
P2P=$(cd "$REPO" && python3 -c "
from transformers.models.qwen2_vl.configuration_qwen2_vl import Qwen2VLTextConfig, Qwen2VLConfig
from transformers.models.qwen2_5_vl.configuration_qwen2_5_vl import Qwen2_5_VLTextConfig, Qwen2_5_VLConfig

# All configs must instantiate without error
for cls in [Qwen2VLTextConfig, Qwen2VLConfig, Qwen2_5_VLTextConfig, Qwen2_5_VLConfig]:
    cfg = cls()
    d = cfg.to_dict()
    assert isinstance(d, dict), f'{cls.__name__}.to_dict() did not return dict'
    assert 'model_type' in d, f'{cls.__name__} to_dict missing model_type'

# Basic fields survive round-trip
cfg1 = Qwen2VLTextConfig()
assert cfg1.to_dict()['vocab_size'] == cfg1.vocab_size
cfg2 = Qwen2_5_VLTextConfig()
assert cfg2.to_dict()['vocab_size'] == cfg2.vocab_size

print('PASS')
" 2>&1 || echo "ERROR")
if [ "$P2P" = "PASS" ]; then
    echo "P2P PASS (0.10): Config instantiation and serialization work"
    add 10
else
    echo "P2P FAIL: Config construction or serialization broken ($P2P)"
fi

###############################################################################
# BEHAVIORAL (0.05): ColQwen2/ColModernVBert configs instantiate without hack
###############################################################################
# [pr_diff] (0.05): Downstream composite configs still work after hack removal
BEH1=$(cd "$REPO" && python3 -c "
from transformers.models.colqwen2.configuration_colqwen2 import ColQwen2Config
from transformers.models.colmodernvbert.configuration_colmodernvbert import ColModernVBertConfig

# Both must instantiate cleanly
c1 = ColQwen2Config()
c2 = ColModernVBertConfig()

# to_dict must work
d1 = c1.to_dict()
d2 = c2.to_dict()
assert isinstance(d1, dict)
assert isinstance(d2, dict)

print('PASS')
" 2>&1 || echo "ERROR")
if [ "$BEH1" = "PASS" ]; then
    echo "BEH1 PASS (0.05): ColQwen2/ColModernVBert instantiate without hack"
    add 5
else
    echo "BEH1 FAIL: Downstream composite configs broken ($BEH1)"
fi

###############################################################################
# STRUCTURAL (0.05): ModernVBertForMaskedLM.__init__ type annotation
###############################################################################
# [pr_diff] (0.05): ModernVBertForMaskedLM.__init__ config param needs type hint
# Justified AST: modeling file imports torch which may be unavailable
STRUCT1=$(python3 -c "
import ast
source = open('$REPO/src/transformers/models/modernvbert/modeling_modernvbert.py').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'ModernVBertForMaskedLM':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                for arg in item.args.args:
                    if arg.arg == 'config' and arg.annotation is not None:
                        print('PASS')
                        break
                else:
                    print('FAIL')
                break
        break
" 2>&1 || echo "ERROR")
if [ "$STRUCT1" = "PASS" ]; then
    echo "STRUCT1 PASS (0.05): ModernVBertForMaskedLM.__init__ has config type hint"
    add 5
else
    echo "STRUCT1 FAIL: Missing type annotation on config param ($STRUCT1)"
fi

###############################################################################
# STRUCTURAL (0.05): Modular file also has the type annotation
###############################################################################
# [pr_diff] (0.05): modular_modernvbert.py ModernVBertForMaskedLM.__init__ config param
# Justified AST: modular file also imports torch-dependent modules
STRUCT2=$(python3 -c "
import ast
source = open('$REPO/src/transformers/models/modernvbert/modular_modernvbert.py').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'ModernVBertForMaskedLM':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                for arg in item.args.args:
                    if arg.arg == 'config' and arg.annotation is not None:
                        print('PASS')
                        break
                else:
                    print('FAIL')
                break
        break
" 2>&1 || echo "ERROR")
if [ "$STRUCT2" = "PASS" ]; then
    echo "STRUCT2 PASS (0.05): modular_modernvbert.py has config type hint"
    add 5
else
    echo "STRUCT2 FAIL: Missing type annotation in modular file ($STRUCT2)"
fi

###############################################################################
# CONFIG (0.05): ruff check on changed files
###############################################################################
# [agent_config] (0.05): "make style: runs formatters and linters (ruff)" — CLAUDE.md:2 @ 28e1cc59
RUFF=PASS
for f in \
    src/transformers/models/qwen2_vl/configuration_qwen2_vl.py \
    src/transformers/models/qwen2_5_vl/configuration_qwen2_5_vl.py \
    src/transformers/models/colqwen2/configuration_colqwen2.py \
    src/transformers/models/colmodernvbert/configuration_colmodernvbert.py \
    src/transformers/models/modernvbert/modeling_modernvbert.py \
    src/transformers/models/modernvbert/modular_modernvbert.py; do
    if ! ruff check "$REPO/$f" --select E,W --quiet 2>/dev/null; then
        echo "RUFF FAIL: $f"
        RUFF=FAIL
    fi
done
if [ "$RUFF" = "PASS" ]; then
    echo "CONFIG PASS (0.05): ruff check passes on all changed files"
    add 5
else
    echo "CONFIG FAIL: ruff errors found"
fi

###############################################################################
# ANTI-STUB (0.05): Changed files must not be emptied or stubbed
###############################################################################
# [pr_diff] (0.05): Files must not be trivially emptied
STUB=PASS
for f in \
    src/transformers/models/qwen2_vl/configuration_qwen2_vl.py \
    src/transformers/models/qwen2_5_vl/configuration_qwen2_5_vl.py \
    src/transformers/models/colqwen2/configuration_colqwen2.py \
    src/transformers/models/colmodernvbert/configuration_colmodernvbert.py; do
    lines=$(wc -l < "$REPO/$f")
    if [ "$lines" -lt 20 ]; then
        echo "STUB FAIL: $f has only $lines lines"
        STUB=FAIL
    fi
done
if [ "$STUB" = "PASS" ]; then
    echo "ANTI-STUB PASS (0.05): Files are not stubbed"
    add 5
else
    echo "ANTI-STUB FAIL: Some files appear to be stubs"
fi

###############################################################################
# Final score
###############################################################################
TOTAL=$(python3 -c "print(round($REWARD / $MAX, 4))")
echo ""
echo "TOTAL REWARD: $TOTAL"
echo "$TOTAL" > /logs/verifier/reward.txt

# Track actual check results for accurate breakdown
B_F2P1=$( [ "$F2P1" = "PASS" ] && echo 0.25 || echo 0.0 )
B_F2P2=$( [ "$F2P2" = "PASS" ] && echo 0.25 || echo 0.0 )
B_F2P3=$( echo "$F2P3" | grep -q "^PASS$" && echo 0.15 || echo 0.0 )
B_P2P=$( [ "$P2P" = "PASS" ] && echo 0.10 || echo 0.0 )
B_BEH1=$( [ "$BEH1" = "PASS" ] && echo 0.05 || echo 0.0 )
B_STRUCT1=$( [ "$STRUCT1" = "PASS" ] && echo 0.05 || echo 0.0 )
B_STRUCT2=$( [ "$STRUCT2" = "PASS" ] && echo 0.05 || echo 0.0 )
B_RUFF=$( [ "$RUFF" = "PASS" ] && echo 0.05 || echo 0.0 )
B_STUB=$( [ "$STUB" = "PASS" ] && echo 0.05 || echo 0.0 )

python3 -c "
import json
json.dump({
    'reward': $TOTAL,
    'behavioral': round($B_F2P1 + $B_F2P2 + $B_F2P3 + $B_P2P + $B_BEH1, 4),
    'regression': round($B_P2P + $B_STUB, 4),
    'structural': round($B_STRUCT1 + $B_STRUCT2, 4),
    'config': $B_RUFF
}, open('/logs/verifier/reward.json', 'w'))
" 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
