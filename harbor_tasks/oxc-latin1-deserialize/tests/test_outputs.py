"""Test outputs for oxc latin1 deserialization optimization."""

import subprocess
import sys
import os

REPO = "/workspace/oxc"
NAPI_PARSER = f"{REPO}/napi/parser"

# Target files that should be modified
TARGET_FILES = [
    "napi/parser/src-js/generated/deserialize/js.js",
    "napi/parser/src-js/generated/deserialize/js_parent.js",
    "napi/parser/src-js/generated/deserialize/js_range.js",
    "napi/parser/src-js/generated/deserialize/js_range_parent.js",
    "napi/parser/src-js/generated/deserialize/ts.js",
    "napi/parser/src-js/generated/deserialize/ts_parent.js",
    "napi/parser/src-js/generated/deserialize/ts_range.js",
    "napi/parser/src-js/generated/deserialize/ts_range_parent.js",
    "apps/oxlint/src-js/generated/deserialize.js",
]


# ==================== FAIL-TO-PASS TESTS ====================
# These verify the fix is implemented correctly

def test_latin1slice_usage():
    """Verify that latin1Slice from Buffer.prototype is used (f2p)."""
    for file_path in TARGET_FILES:
        full_path = f"{REPO}/{file_path}"
        with open(full_path, 'r') as f:
            content = f.read()

        # Check for latin1Slice extraction from Buffer.prototype
        assert "{ latin1Slice } = Buffer.prototype" in content, \
            f"{file_path}: Missing latin1Slice extraction from Buffer.prototype"

        # Check that latin1Slice is called
        assert "latin1Slice.call(uint8" in content, \
            f"{file_path}: Missing latin1Slice.call(uint8, ...) usage"


def test_source_text_latin_variable():
    """Verify sourceTextLatin variable is declared and used (f2p)."""
    for file_path in TARGET_FILES:
        full_path = f"{REPO}/{file_path}"
        with open(full_path, 'r') as f:
            content = f.read()

        # Check variable declaration
        assert "sourceTextLatin," in content, \
            f"{file_path}: Missing sourceTextLatin variable declaration"

        # Check usage in deserializeStr
        assert "sourceTextLatin.substr(" in content, \
            f"{file_path}: Missing sourceTextLatin.substr() usage"

        # Check resetBuffer clears it
        assert "sourceTextLatin = void 0" in content or "sourceTextLatin = undefined" in content, \
            f"{file_path}: Missing sourceTextLatin cleanup in resetBuffer"


def test_string_decode_arrays():
    """Verify stringDecodeArrays are pre-allocated for fromCharCode (f2p)."""
    for file_path in TARGET_FILES:
        full_path = f"{REPO}/{file_path}"
        with open(full_path, 'r') as f:
            content = f.read()

        # Check stringDecodeArrays declaration
        assert "stringDecodeArrays = Array(65).fill(null)" in content, \
            f"{file_path}: Missing stringDecodeArrays declaration"

        # Check array initialization loop
        assert "stringDecodeArrays[i] = Array(i).fill(0)" in content, \
            f"{file_path}: Missing stringDecodeArrays initialization"

        # Check usage in deserializeStr
        assert "stringDecodeArrays[len]" in content, \
            f"{file_path}: Missing stringDecodeArrays[len] usage"


def test_64_byte_threshold():
    """Verify TextDecoder threshold is 64 bytes (not 9) (f2p)."""
    for file_path in TARGET_FILES:
        full_path = f"{REPO}/{file_path}"
        with open(full_path, 'r') as f:
            content = f.read()

        # Should use 64 as threshold
        assert "if (len > 64)" in content, \
            f"{file_path}: Missing 64-byte threshold check"

        # Should NOT have the old 9-byte threshold
        assert "if (len > 9)" not in content, \
            f"{file_path}: Still has old 9-byte threshold"


def test_from_char_code_apply():
    """Verify String.fromCharCode.apply is used for non-source strings (f2p)."""
    for file_path in TARGET_FILES:
        full_path = f"{REPO}/{file_path}"
        with open(full_path, 'r') as f:
            content = f.read()

        # Check fromCharCode.apply usage
        assert "fromCharCode.apply(null, arr)" in content, \
            f"{file_path}: Missing fromCharCode.apply(null, arr) usage"


def test_source_end_pos():
    """Verify sourceEndPos is tracked for source region checks (f2p)."""
    # This only applies to napi parser files (not oxlint)
    napi_files = [f for f in TARGET_FILES if f.startswith("napi/parser")]

    for file_path in napi_files:
        full_path = f"{REPO}/{file_path}"
        with open(full_path, 'r') as f:
            content = f.read()

        # Check sourceEndPos declaration
        assert "sourceEndPos = 0" in content, \
            f"{file_path}: Missing sourceEndPos variable declaration"

        # Check it's set in deserialize function
        assert "sourceEndPos = sourceByteLen" in content, \
            f"{file_path}: Missing sourceEndPos initialization"

        # Check usage in deserializeStr
        assert "if (pos < sourceEndPos)" in content, \
            f"{file_path}: Missing sourceEndPos usage in deserializeStr"


def test_raw_transfer_generator_updated():
    """Verify the Rust generator code is updated (f2p)."""
    generator_file = f"{REPO}/tasks/ast_tools/src/generators/raw_transfer.rs"

    with open(generator_file, 'r') as f:
        content = f.read()

    # Check for STRING_DECODE_CROSSOVER constant
    assert "STRING_DECODE_CROSSOVER = 64" in content, \
        "raw_transfer.rs: Missing STRING_DECODE_CROSSOVER = 64"

    # Check for latin1Slice in the template
    assert "latin1Slice" in content, \
        "raw_transfer.rs: Missing latin1Slice in template"

    # Check for stringDecodeArrays in template
    assert "stringDecodeArrays" in content, \
        "raw_transfer.rs: Missing stringDecodeArrays in template"

    # Check for sourceTextLatin in template
    assert "sourceTextLatin" in content, \
        "raw_transfer.rs: Missing sourceTextLatin in template"


# ==================== PASS-TO-PASS TESTS ====================
# These verify no regressions were introduced

def test_napi_parser_tests():
    """Run NAPI parser test suite (p2p)."""
    result = subprocess.run(
        ["pnpm", "test"],
        cwd=NAPI_PARSER,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"NAPI parser tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"


def test_napi_parser_esm():
    """Run NAPI parser ESM tests (p2p)."""
    result = subprocess.run(
        ["pnpm", "exec", "vitest", "--dir", "./test", "run", "esm.test.ts"],
        cwd=NAPI_PARSER,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"NAPI parser ESM tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"


def test_napi_parser_visit():
    """Run NAPI parser visitor tests (p2p)."""
    result = subprocess.run(
        ["pnpm", "exec", "vitest", "--dir", "./test", "run", "visit.test.ts"],
        cwd=NAPI_PARSER,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"NAPI parser visitor tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"


def test_napi_parser_bindings_exist():
    """Verify NAPI parser bindings.js exists and is readable (p2p)."""
    bindings_file = f"{NAPI_PARSER}/src-js/bindings.js"
    result = subprocess.run(
        ["node", "-e", f"require('fs').readFileSync('{bindings_file}', 'utf8')"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, \
        f"NAPI parser bindings.js check failed:\n{result.stderr[-500:]}"


def test_napi_parser_index_syntax():
    """Verify NAPI parser index.js exists and is readable (p2p)."""
    index_file = f"{NAPI_PARSER}/src-js/index.js"
    result = subprocess.run(
        ["node", "-e", f"require('fs').readFileSync('{index_file}', 'utf8')"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, \
        f"NAPI parser index.js check failed:\n{result.stderr[-500:]}"


def test_napi_parser_wrap_exists():
    """Verify NAPI parser wrap.js exists and is readable (p2p)."""
    wrap_file = f"{NAPI_PARSER}/src-js/wrap.js"
    result = subprocess.run(
        ["node", "-e", f"require('fs').readFileSync('{wrap_file}', 'utf8')"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, \
        f"NAPI parser wrap.js check failed:\n{result.stderr[-500:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
