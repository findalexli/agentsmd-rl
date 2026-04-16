#!/usr/bin/env python3
"""Tests for prometheus fuzzing dictionary PR.

This module tests that:
1. The Keywords() function exists and returns expected PromQL keywords
2. The GetDictForFuzzParseExpr() function exists and returns dictionary tokens
3. The generateDictFile() function exists in corpus_gen/main.go
4. Go code compiles and passes basic checks
"""

import subprocess
import sys
import os
import tempfile
import shutil

REPO = "/workspace/prometheus"

def _run_go_test(test_code, timeout=60):
    """Helper to run Go test code by writing to a temp file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.go', delete=False) as f:
        f.write(test_code)
        temp_file = f.name

    try:
        result = subprocess.run(
            ["go", "run", temp_file],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=REPO
        )
        return result
    finally:
        os.unlink(temp_file)
        # Clean up any generated files
        temp_dir = os.path.dirname(temp_file)
        for f in os.listdir(temp_dir):
            if f.startswith('go-build'):
                shutil.rmtree(os.path.join(temp_dir, f), ignore_errors=True)

def test_keywords_function_exists():
    """Keywords() function exists and returns expected keywords (f2p)."""
    test_code = '''
package main

import (
	"fmt"
	"github.com/prometheus/prometheus/promql/parser"
)

func main() {
	keywords := parser.Keywords()
	if len(keywords) == 0 {
		fmt.Println("FAIL: Keywords() returned empty slice")
		return
	}
	// Check for some expected keywords
	expected := map[string]bool{"sum": false, "avg": false, "by": false, "without": false}
	for _, kw := range keywords {
		if _, ok := expected[kw]; ok {
			expected[kw] = true
		}
	}
	for kw, found := range expected {
		if !found {
			fmt.Printf("FAIL: Expected keyword %q not found\\n", kw)
			return
		}
	}
	fmt.Println("PASS: Keywords() works correctly")
}
'''
    result = _run_go_test(test_code)
    assert result.returncode == 0, f"Keywords test failed: {result.stderr}"
    assert "PASS" in result.stdout, f"Keywords function did not return expected result: {result.stdout}"

def test_get_dict_function_exists():
    """GetDictForFuzzParseExpr() function exists and returns tokens (f2p)."""
    test_code = '''
package main

import (
	"fmt"
	"github.com/prometheus/prometheus/util/fuzzing"
)

func main() {
	dict := fuzzing.GetDictForFuzzParseExpr()
	if len(dict) == 0 {
		fmt.Println("FAIL: GetDictForFuzzParseExpr() returned empty slice")
		return
	}
	// Check for some expected tokens
	expected := map[string]bool{"sum": false, "avg": false, "rate": false, "+Inf": false}
	for _, token := range dict {
		if _, ok := expected[token]; ok {
			expected[token] = true
		}
	}
	for token, found := range expected {
		if !found {
			fmt.Printf("FAIL: Expected token %q not found\\n", token)
			return
		}
	}
	fmt.Println("PASS: GetDictForFuzzParseExpr() works correctly")
}
'''
    result = _run_go_test(test_code)
    assert result.returncode == 0, f"GetDictForFuzzParseExpr test failed: {result.stderr}"
    assert "PASS" in result.stdout, f"GetDictForFuzzParseExpr function did not return expected result: {result.stdout}"

def test_keywords_returns_multiple_keywords():
    """Keywords() returns a variety of keyword types (f2p)."""
    test_code = '''
package main

import (
	"fmt"
	"github.com/prometheus/prometheus/promql/parser"
)

func main() {
	keywords := parser.Keywords()
	// Should have many keywords - at least 20+ covering aggregators, modifiers, etc.
	if len(keywords) < 20 {
		fmt.Printf("FAIL: Expected at least 20 keywords, got %d\\n", len(keywords))
		return
	}
	// Check that we have aggregation keywords
	aggKeywords := map[string]bool{"sum": false, "avg": false, "count": false, "max": false, "min": false}
	for _, kw := range keywords {
		if _, ok := aggKeywords[kw]; ok {
			aggKeywords[kw] = true
		}
	}
	found := 0
	for _, v := range aggKeywords {
		if v { found++ }
	}
	if found < 3 {
		fmt.Printf("FAIL: Expected at least 3 aggregation keywords, found %d\\n", found)
		return
	}
	fmt.Printf("PASS: Keywords() returns %d keywords including aggregation operators\\n", len(keywords))
}
'''
    result = _run_go_test(test_code)
    assert result.returncode == 0, f"Keywords variety test failed: {result.stderr}"
    assert "PASS" in result.stdout, f"Keywords variety check failed: {result.stdout}"

def test_dict_includes_function_names():
    """GetDictForFuzzParseExpr() includes function names in tokens (f2p)."""
    test_code = '''
package main

import (
	"fmt"
	"github.com/prometheus/prometheus/util/fuzzing"
)

func main() {
	dict := fuzzing.GetDictForFuzzParseExpr()
	// Check for function names
	funcNames := map[string]bool{"rate": false, "sum": false, "avg": false, "increase": false, "histogram_quantile": false}
	for _, token := range dict {
		if _, ok := funcNames[token]; ok {
			funcNames[token] = true
		}
	}
	found := 0
	for _, v := range funcNames {
		if v { found++ }
	}
	if found < 3 {
		fmt.Printf("FAIL: Expected at least 3 function names in dict, found %d\\n", found)
		return
	}
	fmt.Printf("PASS: Dictionary includes %d expected function names\\n", found)
}
'''
    result = _run_go_test(test_code)
    assert result.returncode == 0, f"Dict function names test failed: {result.stderr}"
    assert "PASS" in result.stdout, f"Dict function names check failed: {result.stdout}"

def test_dict_includes_special_literals():
    """GetDictForFuzzParseExpr() includes special numeric literals like +Inf, -Inf, NaN (f2p)."""
    test_code = '''
package main

import (
	"fmt"
	"github.com/prometheus/prometheus/util/fuzzing"
)

func main() {
	dict := fuzzing.GetDictForFuzzParseExpr()
	// Check for special literals
	special := map[string]bool{"+Inf": false, "-Inf": false, "NaN": false}
	for _, token := range dict {
		if _, ok := special[token]; ok {
			special[token] = true
		}
	}
	for lit, found := range special {
		if !found {
			fmt.Printf("FAIL: Special literal %q not found in dictionary\\n", lit)
			return
		}
	}
	fmt.Println("PASS: Dictionary includes special numeric literals")
}
'''
    result = _run_go_test(test_code)
    assert result.returncode == 0, f"Dict special literals test failed: {result.stderr}"
    assert "PASS" in result.stdout, f"Dict special literals check failed: {result.stdout}"

def test_corpus_gen_compiles():
    """The corpus_gen tool compiles successfully (p2p)."""
    result = subprocess.run(
        ["go", "build", "-o", "/tmp/corpus_gen", "./util/fuzzing/corpus_gen/main.go"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert result.returncode == 0, f"corpus_gen build failed: {result.stderr}"

def test_fuzzing_package_compiles():
    """The fuzzing package compiles without errors (p2p)."""
    result = subprocess.run(
        ["go", "build", "./util/fuzzing/..."],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert result.returncode == 0, f"fuzzing package build failed: {result.stderr}"

def test_promql_parser_compiles():
    """The promql/parser package compiles without errors (p2p)."""
    result = subprocess.run(
        ["go", "build", "./promql/parser/..."],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert result.returncode == 0, f"promql/parser build failed: {result.stderr}"

def test_repo_vet():
    """Go vet passes for promql/parser and util/fuzzing packages (p2p)."""
    result = subprocess.run(
        ["go", "vet", "./promql/parser/...", "./util/fuzzing/..."],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )
    assert result.returncode == 0, f"go vet failed:\n{result.stderr[-500:]}"

def test_repo_go_fmt():
    """Go formatting check passes for modified packages (p2p)."""
    result = subprocess.run(
        ["gofmt", "-l", "./promql/parser", "./util/fuzzing"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    # gofmt -l returns 0 but prints file names if files need formatting
    assert result.returncode == 0, f"gofmt check failed:\n{result.stderr}"
    assert result.stdout.strip() == "", f"Files need formatting:\n{result.stdout}"

def test_repo_go_mod_verify():
    """Go modules verify passes (p2p)."""
    result = subprocess.run(
        ["go", "mod", "verify"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    assert result.returncode == 0, f"go mod verify failed:\n{result.stderr}"

def test_promql_parser_tests():
    """PromQL parser unit tests pass (p2p)."""
    result = subprocess.run(
        ["go", "test", "./promql/parser/...", "-v", "-count=1"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )
    assert result.returncode == 0, f"PromQL parser tests failed:\n{result.stderr[-500:]}"

def test_fuzzing_package_tests():
    """Fuzzing package unit tests pass (p2p)."""
    result = subprocess.run(
        ["go", "test", "./util/fuzzing/...", "-v", "-count=1"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )
    assert result.returncode == 0, f"Fuzzing package tests failed:\n{result.stderr[-500:]}"

def test_promql_lexer_parse_tests():
    """PromQL lexer and parser specific tests pass (p2p)."""
    result = subprocess.run(
        ["go", "test", "./promql/...", "-run", "TestLexer|TestParse", "-v", "-count=1"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )
    assert result.returncode == 0, f"PromQL lexer/parser tests failed:\n{result.stderr[-500:]}"

def test_corpus_gen_runs():
    """Corpus generation tool runs successfully (p2p)."""
    result = subprocess.run(
        ["go", "run", "./util/fuzzing/corpus_gen/main.go"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO
    )
    assert result.returncode == 0, f"corpus_gen run failed:\n{result.stderr[-500:]}"

def test_fuzzing_test_compile():
    """Fuzzing test binary compiles successfully (p2p)."""
    result = subprocess.run(
        ["go", "test", "-c", "./util/fuzzing", "-o", "/tmp/fuzzing.test"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )
    assert result.returncode == 0, f"Fuzzing test compile failed:\n{result.stderr[-500:]}"
