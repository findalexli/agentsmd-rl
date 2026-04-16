"""
Tests for null value handling in adapter-ppg type parsers.
These tests verify that nullable column parsers gracefully handle null values
instead of crashing with TypeError when calling methods on null.
"""

import subprocess
import os
import json

REPO = "/workspace/prisma"
TSX = "/workspace/prisma/node_modules/.bin/tsx"


def run_ts(script):
    """Run a TypeScript script using tsx and return parsed JSON output."""
    result = subprocess.run(
        [TSX, "-e", script],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    return result


def test_normalize_timestamp_null():
    """
    normalize_timestamp should return null for null input instead of crashing.
    Before the fix: TypeError: Cannot read properties of null (reading 'replace')
    After the fix: returns null
    """
    result = run_ts("""
        import { builtinParsers, ScalarColumnType } from './packages/adapter-ppg/src/conversion';
        const parse = builtinParsers.find((p: any) => p.oid === ScalarColumnType.TIMESTAMP).parse;
        const result = parse(null);
        console.log(JSON.stringify({ result }));
    """)
    if result.returncode != 0:
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
    assert result.returncode == 0, f"Script crashed with: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["result"] is None, f"Expected null, got {data['result']!r}"


def test_normalize_timestamptz_null():
    """
    normalize_timestamptz should return null for null input instead of crashing.
    Before the fix: TypeError: Cannot read properties of null (reading 'replace')
    After the fix: returns null
    """
    result = run_ts("""
        import { builtinParsers, ScalarColumnType } from './packages/adapter-ppg/src/conversion';
        const parse = builtinParsers.find((p: any) => p.oid === ScalarColumnType.TIMESTAMPTZ).parse;
        const result = parse(null);
        console.log(JSON.stringify({ result }));
    """)
    assert result.returncode == 0, f"Script crashed with: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["result"] is None, f"Expected null, got {data['result']!r}"


def test_normalize_timez_null():
    """
    normalize_timez should return null for null input instead of crashing.
    Before the fix: TypeError: Cannot read properties of null (reading 'replace')
    After the fix: returns null
    """
    result = run_ts("""
        import { builtinParsers, ScalarColumnType } from './packages/adapter-ppg/src/conversion';
        const parse = builtinParsers.find((p: any) => p.oid === ScalarColumnType.TIMETZ).parse;
        const result = parse(null);
        console.log(JSON.stringify({ result }));
    """)
    assert result.returncode == 0, f"Script crashed with: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["result"] is None, f"Expected null, got {data['result']!r}"


def test_normalize_money_null():
    """
    normalize_money should return null for null input instead of crashing.
    Before the fix: TypeError: Cannot read properties of null (reading 'slice')
    After the fix: returns null
    """
    result = run_ts("""
        import { builtinParsers, ScalarColumnType } from './packages/adapter-ppg/src/conversion';
        const parse = builtinParsers.find((p: any) => p.oid === ScalarColumnType.MONEY).parse;
        const result = parse(null);
        console.log(JSON.stringify({ result }));
    """)
    assert result.returncode == 0, f"Script crashed with: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["result"] is None, f"Expected null, got {data['result']!r}"


def test_convert_bytes_null():
    """
    convertBytes should return null for null input instead of crashing.
    Before the fix: TypeError: Cannot read properties of null
    After the fix: returns null
    """
    result = run_ts("""
        import { builtinParsers, ScalarColumnType } from './packages/adapter-ppg/src/conversion';
        const parse = builtinParsers.find((p: any) => p.oid === ScalarColumnType.BYTEA).parse;
        const result = parse(null);
        console.log(JSON.stringify({ result }));
    """)
    assert result.returncode == 0, f"Script crashed with: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["result"] is None, f"Expected null, got {data['result']!r}"


def test_normalize_timestamp_valid_input():
    """
    normalize_timestamp should still work correctly with valid input.
    """
    result = run_ts("""
        import { builtinParsers, ScalarColumnType } from './packages/adapter-ppg/src/conversion';
        const parse = builtinParsers.find((p: any) => p.oid === ScalarColumnType.TIMESTAMP).parse;
        const result = parse('1996-12-19 16:39:57');
        console.log(JSON.stringify({ result }));
    """)
    assert result.returncode == 0, f"Script crashed with: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["result"] == '1996-12-19T16:39:57+00:00', f"Expected '1996-12-19T16:39:57+00:00', got {data['result']!r}"


def test_normalize_money_valid_input():
    """
    normalize_money should still strip currency symbol from valid input.
    """
    result = run_ts("""
        import { builtinParsers, ScalarColumnType } from './packages/adapter-ppg/src/conversion';
        const parse = builtinParsers.find((p: any) => p.oid === ScalarColumnType.MONEY).parse;
        const result = parse('$1234.56');
        console.log(JSON.stringify({ result }));
    """)
    assert result.returncode == 0, f"Script crashed with: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["result"] == '1234.56', f"Expected '1234.56', got {data['result']!r}"


def test_convert_bytes_valid_input():
    """
    convertBytes should still convert base64 to Buffer for valid input.
    """
    result = run_ts("""
        import { builtinParsers, ScalarColumnType } from './packages/adapter-ppg/src/conversion';
        const parse = builtinParsers.find((p: any) => p.oid === ScalarColumnType.BYTEA).parse;
        const result = parse('aGVsbG8=');
        console.log(JSON.stringify({ result: result ? result.toString('utf8') : null }));
    """)
    assert result.returncode == 0, f"Script crashed with: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["result"] == 'hello', f"Expected 'hello', got {data['result']!r}"


# ─── Pass-to-Pass gates: repo CI commands ─────────────────────────────────────

def test_repo_prettier_check_conversion():
    """Repo's prettier check passes on the modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "prettier", "--check", "packages/adapter-ppg/src/conversion.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"prettier check failed:\n{r.stdout[-500:]}"


def test_repo_eslint_conversion():
    """Repo's eslint passes on the modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "eslint", "packages/adapter-ppg/src/conversion.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"eslint failed:\n{r.stdout[-500:]}"


def test_repo_prettier_check_adapter_ppg_src():
    """Repo's prettier check passes on adapter-ppg/src/ (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "prettier", "--check", "packages/adapter-ppg/src/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"prettier check failed:\n{r.stdout[-500:]}"


def test_repo_eslint_adapter_ppg_src():
    """Repo's eslint passes on adapter-ppg/src/ (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "eslint", "packages/adapter-ppg/src/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"eslint failed:\n{r.stdout[-500:]}"
