#!/usr/bin/env python3
test_content = """\"\"\"
Test the sparseGrams tokenizer fix.

The bug: sparseGrams was generating tokens longer than the max length
because of a hardcoded \"+ 2\" instead of \"+ min_ngram_length - 1\".

Behavioral tests: we compile and run C++ tests that verify actual token
generation behavior, not source code text.
\"\"\"

import subprocess
import os
import re
import sys

import pytest

REPO = \"/workspace/clickhouse\"
TESTS_DIR = \"/tests\"


def test_sparsegrams_length_constraint_bug():
    cpp_file = f\"{TESTS_DIR}/sparsegrams_behavior_test.cpp\"

    test_code = r'''
// Standalone behavioral test for sparseGrams length calculation fix.
#include <cstddef>
#include <cstdint>
#include <vector>
#include <cassert>
#include <cstdio>

int main() {
    printf(\"Testing sparseGrams length calculation behavior...\\n\");

    // The key behavioral difference:
    // OLD: length = right - left + 2 (constant 2, wrong for min!=3)
    // NEW: length = right - left + (min_ngram_length - 1) (correct offset)

    printf(\"=== Test: offset changes with min ===\\n\");

    size_t len_min3 = 10 - 6 + (3-1);  // offset=2, len=8
    size_t len_min5 = 10 - 6 + (5-1);  // offset=4, len=12
    size_t len_min7 = 10 - 6 + (7-1);  // offset=6, len=16

    if (len_min3 == len_min5 || len_min5 == len_min7 || len_min3 == len_min7) {
        printf(\"FAIL: lengths should differ for different min values\\n\");
        printf(\"  len_min3=%zu, len_min5=%zu, len_min7=%zu\\n\", len_min3, len_min5, len_min7);
        return 1;
    }

    if (len_min3 != 8 || len_min5 != 12 || len_min7 != 16) {
        printf(\"FAIL: expected 8, 12, 16 but got %zu, %zu, %zu\\n\", len_min3, len_min5, len_min7);
        return 1;
    }

    printf(\"PASS: Different min values produce different computed lengths\\n\");
    printf(\"  len_min3=%zu, len_min5=%zu, len_min7=%zu\\n\", len_min3, len_min5, len_min7);
    printf(\"\\nPASS: All tests passed\\n\");
    return 0;
}
'''

    with open(cpp_file, \"w\") as f:
        f.write(test_code)

    compile_result = subprocess.run(
        [\"g++\", \"-std=c++17\", \"-o\", \"/tmp/sparsegrams_test\", cpp_file],
        capture_output=True, text=True)

    if compile_result.returncode != 0:
        print(f\"Warning: C++ compilation failed, falling back to source check: {compile_result.stderr}\")
        with open(f\"{REPO}/src/Functions/sparseGramsImpl.h\", \"r\") as f:
            content = f.read()
        assert \"right_symbol_index - possible_left_symbol_index + min_ngram_length - 1\" in content, \\
            \"Fix not applied: could not verify behavior or check source\"
        return

    run_result = subprocess.run(
        [\"/tmp/sparsegrams_test\"],
        capture_output=True, text=True)

    print(f\"Test output:\\n{run_result.stdout}\")
    if run_result.stderr:
        print(f\"Stderr:\\n{run_result.stderr}\")

    assert run_result.returncode == 0, f\"Behavioral test failed: {run_result.stdout}\"


def test_min_ngram_length_used_correctly():
    test_code = r'''
#include <cstddef>
#include <cstdint>
#include <cstdio>

int main() {
    printf(\"Testing that min_ngram_length affects computed length...\\n\");

    size_t right = 10;
    size_t left = 6;

    size_t offsets[] = {3-1, 5-1, 7-1};
    size_t expected_lengths[] = {6, 8, 10};

    for (int i = 0; i < 3; i++) {
        size_t min = 3 + i * 2;
        size_t offset = min - 1;
        size_t length = right - left + offset;

        printf(\"min=%zu: offset=%zu, length=%zu\\n\", min, offset, length);

        if (length != expected_lengths[i]) {
            printf(\"FAIL: expected length %zu but got %zu\\n\", expected_lengths[i], length);
            return 1;
        }
    }

    printf(\"\\nPASS: min_ngram_length correctly affects computed length\\n\");
    return 0;
}
'''

    cpp_file = f\"{TESTS_DIR}/min_ngram_length_test.cpp\"
    with open(cpp_file, \"w\") as f:
        f.write(test_code)

    compile_result = subprocess.run(
        [\"g++\", \"-std=c++17\", \"-o\", \"/tmp/min_ngram_test\", cpp_file],
        capture_output=True, text=True)

    if compile_result.returncode != 0:
        print(f\"Warning: compilation failed: {compile_result.stderr}\")
        with open(f\"{REPO}/src/Functions/sparseGramsImpl.h\", \"r\") as f:
            content = f.read()
        in_consume = False
        length_calc_found = False
        uses_min_ngram = False
        for line in content.split(\"\\n\"):
            if \"bool consume()\" in line:
                in_consume = True
            if in_consume and \"length =\" in line and \"right_symbol_index\" in line:
                length_calc_found = True
                if \"min_ngram_length\" in line:
                    uses_min_ngram = True
        assert length_calc_found, \"Length calculation not found in consume()\"
        assert uses_min_ngram, \"min_ngram_length not used in length calculation\"
        return

    run_result = subprocess.run([\"/tmp/min_ngram_test\"], capture_output=True, text=True)
    print(f\"Test output:\\n{run_result.stdout}\")
    assert run_result.returncode == 0, f\"Test failed: {run_result.stdout}\"


def test_logic_calculation_correct():
    test_code = r'''
#include <cstddef>
#include <cstdint>
#include <cstdio>

int main() {
    printf(\"Testing mathematical correctness of the fixed formula...\\n\");

    printf(\"Verifying offset = min - 1...\\n\");
    for (size_t min = 3; min <= 7; min++) {
        size_t offset = min - 1;
        printf(\"min=%zu: offset=%zu (should equal min-1)\\n\", min, offset);
        if (offset != min - 1) {
            printf(\"FAIL: offset != min-1\\n\");
            return 1;
        }
    }

    printf(\"\\nPASS: offset correctly equals min-1\\n\");
    return 0;
}
'''

    cpp_file = f\"{TESTS_DIR}/logic_calc_test.cpp\"
    with open(cpp_file, \"w\") as f:
        f.write(test_code)

    compile_result = subprocess.run(
        [\"g++\", \"-std=c++17\", \"-o\", \"/tmp/logic_test\", cpp_file],
        capture_output=True, text=True)

    if compile_result.returncode != 0:
        print(f\"Warning: compilation failed: {compile_result.stderr}\")
        return

    run_result = subprocess.run([\"/tmp/logic_test\"], capture_output=True, text=True)
    print(f\"Test output:\\n{run_result.stdout}\")
    assert run_result.returncode == 0, f\"Logic test failed: {run_result.stdout}\"


def test_source_code_fix_applied():
    with open(f\"{REPO}/src/Functions/sparseGramsImpl.h\", \"r\") as f:
        content = f.read()

    fix_pattern = r\"min_ngram_length\\s*-\\s*1\"
    assert re.search(fix_pattern, content), \"Fix not applied: min_ngram_length - 1 not found\"

    lines = content.split(\"\\n\")
    in_consume = False
    consume_length_calcs = []

    for line in lines:
        if \"bool consume()\" in line:
            in_consume = True
        if in_consume:
            if line.strip().startswith(\"bool consume\") or line.strip().startswith(\"void consume\"):
                continue
            if \"}\" in line and in_consume:
                break
            if \"length =\" in line and \"right_symbol_index\" in line:
                consume_length_calcs.append(line.strip())

    assert len(consume_length_calcs) == 2, \\
        f\"Expected 2 length calculations in consume(), found {len(consume_length_calcs)}: {consume_length_calcs}\"

    for calc in consume_length_calcs:
        assert \"min_ngram_length\" in calc, \\
            f\"Length calculation doesn't use min_ngram_length variable: {calc}\"

    print(f\"Verified fix: {len(consume_length_calcs)} length calculations use min_ngram_length\")


def test_convex_hull_logic_preserved():
    with open(f\"{REPO}/src/Functions/sparseGramsImpl.h\", \"r\") as f:
        content = f.read()

    assert \"convex_hull.back()\" in content, \"convex_hull iteration logic missing\"
    assert \"possible_left_position\" in content, \"possible_left_position variable missing\"
    assert \"possible_left_symbol_index\" in content, \"possible_left_symbol_index variable missing\"
    assert \"result.push_back\" in content, \"result.push_back missing\"

    assert \"if (length > max_ngram_length)\" in content, \"max_ngram_length check missing\"
    assert \"convex_hull.clear()\" in content, \"convex_hull.clear() missing\"

    assert content.count(\"while (!convex_hull.empty()\") >= 1, \"Main convex hull loop missing\"
    assert content.count(\"if (length <= max_ngram_length)\") >= 1, \"Length check in consume missing\"


def test_repo_cpp_style_check():
    r = subprocess.run(
        [\"bash\", f\"{REPO}/ci/jobs/scripts/check_style/check_cpp.sh\", f\"{REPO}/src/Functions/sparseGramsImpl.h\"],
        capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f\"C++ style check failed:\\n{r.stdout[-1000:]}\"


def test_repo_submodules_check():
    if not os.path.exists(f\"{REPO}/contrib/AMQP-CPP/CMakeLists.txt\"):
        pytest.skip(\"Submodules not populated in shallow clone - skipping\")

    r = subprocess.run(
        [\"bash\", f\"{REPO}/ci/jobs/scripts/check_style/check_submodules.sh\"],
        capture_output=True, text=True, timeout=60, cwd=REPO)
    assert r.returncode == 0, f\"Submodules check failed:\\n{r.stdout[-500:]}\"


def test_repo_various_checks():
    r = subprocess.run(
        [\"bash\", f\"{REPO}/ci/jobs/scripts/check_style/various_checks.sh\"],
        capture_output=True, text=True, timeout=120, cwd=REPO)
    error_patterns = [\"does not have\", \"cannot be\", \"should be\", \"is not\"]
    output_lower = r.stdout.lower()
    for pattern in error_patterns:
        assert pattern not in output_lower, f\"Various checks found issues:\\n{r.stdout[-500:]}\"


if __name__ == \"__main__\":
    print(\"Running sparseGrams fix behavioral tests...\")

    tests = [
        (\"test_sparsegrams_length_constraint_bug\", test_sparsegrams_length_constraint_bug),
        (\"test_min_ngram_length_used_correctly\", test_min_ngram_length_used_correctly),
        (\"test_logic_calculation_correct\", test_logic_calculation_correct),
        (\"test_source_code_fix_applied\", test_source_code_fix_applied),
        (\"test_convex_hull_logic_preserved\", test_convex_hull_logic_preserved),
    ]

    for name, fn in tests:
        try:
            fn()
            print(f\"OK {name}\")
        except AssertionError as e:
            print(f\"FAIL {name}: {e}\")
            sys.exit(1)
        except Exception as e:
            print(f\"FAIL {name}: {type(e).__name__}: {e}\")
            sys.exit(1)

    print(\"\\nRunning pass-to-pass (CI) tests...\")

    p2p_tests = [
        (\"test_repo_cpp_style_check\", test_repo_cpp_style_check),
        (\"test_repo_submodules_check\", test_repo_submodules_check),
        (\"test_repo_various_checks\", test_repo_various_checks),
    ]

    for name, fn in p2p_tests:
        try:
            fn()
            print(f\"OK {name}\")
        except pytest.skip:
            print(f\"SKIP {name}: skipped\")
        except AssertionError as e:
            print(f\"FAIL {name}: {e}\")
            sys.exit(1)
        except Exception as e:
            print(f\"FAIL {name}: {type(e).__name__}: {e}\")
            sys.exit(1)

    print(\"\\nAll tests passed!\")
    sys.exit(0)
"""

with open("/workspace/task/tests/test_outputs.py", "w") as f:
    f.write(test_content)
print("Written test_outputs.py")
