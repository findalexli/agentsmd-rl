"""Tests for taskforge.lint — pre-audit static checks on test.sh."""

from taskforge.lint import Severity, lint_test_sh


# ---------------------------------------------------------------------------
# A clean test.sh that should pass all checks
# ---------------------------------------------------------------------------

CLEAN_TEST_SH = """#!/usr/bin/env bash
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

# GATE: syntax check
python3 -c "import ast; ast.parse(open('/workspace/repo/main.py').read())"
if [ $? -ne 0 ]; then
    echo "GATE FAIL"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
GATE_PASS=true

# [pr_diff] (0.35): Fail-to-pass behavioral test
echo "TEST 1: behavioral fail-to-pass"
python3 -c "
import sys; sys.path.insert(0, '/workspace/repo')
from main import fix_function
result = fix_function('test')
assert result == 'expected'
"
if [ $? -eq 0 ]; then
    SCORE=0.35
else
    SCORE=0.0
fi

# [pr_diff] (0.25): Regression test
echo "TEST 2: regression"
SCORE=$(python3 -c "print($SCORE + 0.25)")

# [pr_diff] (0.20): Another behavioral
SCORE=$(python3 -c "print($SCORE + 0.20)")

# [agent_config] (0.10): Config check
SCORE=$(python3 -c "print($SCORE + 0.10)")

# [static] (0.10): Anti-stub
if [ "$GATE_PASS" = true ]; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
fi

echo "$SCORE" > "$REWARD_FILE"
source /tests/judge_hook.sh 2>/dev/null || true
"""


class TestCleanFile:
    def test_clean_passes(self):
        result = lint_test_sh(CLEAN_TEST_SH)
        assert result.critical_count == 0
        assert result.passed

    def test_weight_sum(self):
        result = lint_test_sh(CLEAN_TEST_SH)
        assert abs(result.weight_sum - 1.0) < 0.05

    def test_has_gate(self):
        result = lint_test_sh(CLEAN_TEST_SH)
        assert result.has_gate


class TestSetFlags:
    def test_set_e_detected(self):
        bad = "#!/bin/bash\nset -euo pipefail\necho test"
        result = lint_test_sh(bad)
        issues = [i for i in result.issues if i.rule == "set-e-abort"]
        assert len(issues) == 1
        assert issues[0].severity == Severity.CRITICAL

    def test_set_plus_e_ok(self):
        good = "#!/bin/bash\nset +e\necho test"
        result = lint_test_sh(good)
        issues = [i for i in result.issues if i.rule == "set-e-abort"]
        assert len(issues) == 0

    def test_set_uo_pipefail_with_plus_e_ok(self):
        good = "#!/bin/bash\nset +e\nset -uo pipefail\necho test"
        result = lint_test_sh(good)
        issues = [i for i in result.issues if i.rule == "set-e-abort"]
        assert len(issues) == 0


class TestWeightSum:
    def test_weights_sum_to_one(self):
        sh = "# (0.40): test1\n# (0.30): test2\n# (0.30): test3"
        result = lint_test_sh(sh)
        issues = [i for i in result.issues if i.rule == "weight-sum"]
        assert len(issues) == 0
        assert abs(result.weight_sum - 1.0) < 0.01

    def test_weights_dont_sum(self):
        sh = "# (0.30): test1\n# (0.20): test2"
        result = lint_test_sh(sh)
        issues = [i for i in result.issues if i.rule == "weight-sum"]
        assert len(issues) == 1
        assert issues[0].severity == Severity.CRITICAL

    def test_declare_a_weights(self):
        sh = 'WEIGHTS[a]=0.50\nWEIGHTS[b]=0.50'
        result = lint_test_sh(sh)
        assert abs(result.weight_sum - 1.0) < 0.01

    def test_no_weights_warning(self):
        sh = "#!/bin/bash\necho hello"
        result = lint_test_sh(sh)
        issues = [i for i in result.issues if i.rule == "no-weights"]
        assert len(issues) == 1


class TestImportFallback:
    def test_detects_ast_fallback(self):
        sh = """python3 -c "
try:
    from module import func
    func()
except:
    import ast
    ast.parse(open('file.py').read())
    check_structural()
" """
        result = lint_test_sh(sh)
        issues = [i for i in result.issues if i.rule == "import-fallback"]
        assert len(issues) == 1
        assert issues[0].antipattern == 2

    def test_no_false_positive_on_normal_try(self):
        sh = """python3 -c "
try:
    result = compute()
except ValueError:
    print('error')
" """
        result = lint_test_sh(sh)
        issues = [i for i in result.issues if i.rule == "import-fallback"]
        assert len(issues) == 0


class TestFileExistsFallback:
    def test_detects_exists_fallback(self):
        sh = """
if ! python3 -c "from module import X" 2>/dev/null; then
    if [ -f /workspace/module.py ]; then
        SCORE=$(python3 -c "print($SCORE + 0.10)")
    fi
fi
"""
        result = lint_test_sh(sh)
        issues = [i for i in result.issues if i.rule == "exists-fallback"]
        assert len(issues) == 1
        assert issues[0].antipattern == 10


class TestGateAndF2P:
    def test_no_gate_warning(self):
        sh = "#!/bin/bash\nset +e\n# (0.50): test\n# (0.50): test2\necho done"
        result = lint_test_sh(sh)
        assert not result.has_gate

    def test_gate_detected(self):
        sh = "#!/bin/bash\nGATE check\nast.parse\n# (0.50): t\n# (0.50): t"
        result = lint_test_sh(sh)
        assert result.has_gate


class TestRealFiles:
    """Test the linter against patterns from actual harbor tasks."""

    def test_gradio_style_maps(self):
        """gradio tasks use WEIGHTS[key]=val style — should parse correctly."""
        sh = """#!/usr/bin/env bash
set +e
TARGET="/workspace/gradio/js/utils.ts"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"
declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.35
WEIGHTS[regression]=0.25
WEIGHTS[structural]=0.20
WEIGHTS[antistub]=0.20
GATE pass
echo "0.5" > "$REWARD_FILE"
"""
        result = lint_test_sh(sh)
        assert abs(result.weight_sum - 1.0) < 0.01
        assert result.has_gate
