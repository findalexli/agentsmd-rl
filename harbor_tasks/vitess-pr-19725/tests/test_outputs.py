#!/usr/bin/env python3
"""Verify task outcomes by running the vitess SQL parser tests."""

import subprocess
import os
import tempfile

REPO = "/workspace/vitess"

def run_go_test(path, pattern, timeout=600):
    """Run a go test and return (returncode, stdout_stderr)."""
    cmd = ["go", "test", "-run", pattern, "-count=1", "-v", path]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=REPO)
    return r.returncode, r.stdout + r.stderr


def run_go_program(code, timeout=120):
    """Write code to a temp file and run with go run."""
    with tempfile.NamedTemporaryFile(suffix='.go', mode='w', dir='/tmp', delete=False) as f:
        f.write(code)
        fname = f.name
    try:
        r = subprocess.run(
            ["go", "run", fname],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
        return r
    finally:
        os.unlink(fname)


# ── Pass-to-Pass (repo's own tests) ────────────────────────────────────────

def test_repo_token_tests():
    """Repo's token tests pass (pass_to_pass)."""
    rc, out = run_go_test(
        "vitess.io/vitess/go/vt/sqlparser",
        "TestVersion",
        timeout=300,
    )
    assert rc == 0, f"token tests failed:\n{out[-1000:]}"


def test_repo_comment_tests():
    """Repo's comment tests pass (pass_to_pass)."""
    rc, out = run_go_test(
        "vitess.io/vitess/go/vt/sqlparser",
        "TestExtractCommentDirectives",
        timeout=300,
    )
    assert rc == 0, f"comment tests failed:\n{out[-1000:]}"


def test_repo_literal_id():
    """Repo's literal ID tokenizer tests pass (pass_to_pass)."""
    rc, out = run_go_test(
        "vitess.io/vitess/go/vt/sqlparser",
        "TestLiteralID",
        timeout=300,
    )
    assert rc == 0, f"literal ID tests failed:\n{out[-1000:]}"


def test_repo_string():
    """Repo's string tokenizer tests pass (pass_to_pass)."""
    rc, out = run_go_test(
        "vitess.io/vitess/go/vt/sqlparser",
        "TestString",
        timeout=300,
    )
    assert rc == 0, f"string tests failed:\n{out[-1000:]}"


def test_repo_integer_and_id():
    """Repo's integer/ID tokenizer tests pass (pass_to_pass)."""
    rc, out = run_go_test(
        "vitess.io/vitess/go/vt/sqlparser",
        "TestIntegerAndID",
        timeout=300,
    )
    assert rc == 0, f"integer/ID tests failed:\n{out[-1000:]}"


def test_repo_split_statement():
    """Repo's split-statement tests pass (pass_to_pass)."""
    rc, out = run_go_test(
        "vitess.io/vitess/go/vt/sqlparser",
        "TestSplitStatement",
        timeout=300,
    )
    assert rc == 0, f"split statement tests failed:\n{out[-1000:]}"


def test_repo_split_comments():
    """Repo's comment-splitting tests pass (pass_to_pass)."""
    rc, out = run_go_test(
        "vitess.io/vitess/go/vt/sqlparser",
        "TestSplitComments",
        timeout=300,
    )
    assert rc == 0, f"split comments tests failed:\n{out[-1000:]}"


# ── Fail-to-Pass (behavior fixed by the PR) ─────────────────────────────────

def test_versioned_comment_expanded():
    """Versioned comment /*!80100 ... */ with matching version is expanded into SQL."""
    code = '''package main
import (
    "vitess.io/vitess/go/vt/sqlparser"
    "fmt"
)
func main() {
    parser, err := sqlparser.New(sqlparser.Options{MySQLServerVersion: "8.1.20"})
    if err != nil { panic(err) }
    stmt, err := parser.Parse("SELECT /*!80100 1 + 1 */ FROM dual")
    if err != nil { panic(err) }
    fmt.Println(sqlparser.String(stmt))
}
'''
    r = run_go_program(code)
    assert r.returncode == 0, f"compile/run failed:\n{r.stderr}"
    output = r.stdout.strip()
    assert "1 + 1" in output, f"versioned comment not expanded, got: {output}"


def test_versioned_comment_discarded():
    """Versioned comment /*!90000 ... */ with version higher than server is discarded."""
    code = '''package main
import (
    "vitess.io/vitess/go/vt/sqlparser"
    "fmt"
)
func main() {
    parser, err := sqlparser.New(sqlparser.Options{MySQLServerVersion: "8.1.20"})
    if err != nil { panic(err) }
    stmt, err := parser.Parse("SELECT /*!90000 secret, */ 42 FROM dual")
    if err != nil { panic(err) }
    fmt.Println(sqlparser.String(stmt))
}
'''
    r = run_go_program(code)
    assert r.returncode == 0, f"compile/run failed:\n{r.stderr}"
    output = r.stdout.strip()
    assert "secret" not in output, f"versioned comment was not discarded, got: {output}"
    assert "42" in output, f"expected 42 in output, got: {output}"


def test_nested_comment_in_versioned_comment():
    """Nested /* ... */ comments inside a versioned comment are consumed and discarded."""
    code = '''package main
import (
    "vitess.io/vitess/go/vt/sqlparser"
    "fmt"
)
func main() {
    parser, err := sqlparser.New(sqlparser.Options{MySQLServerVersion: "8.1.20"})
    if err != nil { panic(err) }
    // MySQL consumes nested /* ... */ comments inside versioned comments
    stmt, err := parser.Parse("SELECT /*!80100 1 /* a comment */ + 2 */ FROM dual")
    if err != nil { panic(err) }
    fmt.Println(sqlparser.String(stmt))
}
'''
    r = run_go_program(code)
    assert r.returncode == 0, f"compile/run failed:\n{r.stderr}"
    output = r.stdout.strip()
    assert "1 + 2" in output, f"expected '1 + 2' (nested comment consumed), got: {output}"


def test_unclosed_versioned_comment_error():
    """Unclosed versioned comment produces a lex error at EOF."""
    code = '''package main
import (
    "vitess.io/vitess/go/vt/sqlparser"
    "fmt"
)
func main() {
    parser, err := sqlparser.New(sqlparser.Options{MySQLServerVersion: "8.1.20"})
    if err != nil { panic(err) }
    _, err = parser.Parse("SELECT /*!80100 1 + 2")
    if err == nil {
        panic("expected error for unclosed versioned comment")
    }
    fmt.Println("OK:", err.Error())
}
'''
    r = run_go_program(code)
    assert r.returncode == 0, f"compile/run failed:\n{r.stderr}"
    output = r.stdout
    assert "OK:" in output, f"expected lex error for unclosed comment, got: {output}"


def test_versioned_comment_no_space_before_close():
    """/*!80100 42*/ with no space before closing */ is parsed correctly."""
    code = '''package main
import (
    "vitess.io/vitess/go/vt/sqlparser"
    "fmt"
)
func main() {
    parser, err := sqlparser.New(sqlparser.Options{MySQLServerVersion: "8.1.20"})
    if err != nil { panic(err) }
    stmt, err := parser.Parse("SELECT /*!80100 42*/ FROM dual")
    if err != nil { panic(err) }
    fmt.Println(sqlparser.String(stmt))
}
'''
    r = run_go_program(code)
    assert r.returncode == 0, f"compile/run failed:\n{r.stderr}"
    output = r.stdout.strip()
    assert "42" in output, f"expected 42 in output, got: {output}"


def test_division_slash_inside_versioned_comment():
    """A / inside a versioned comment is a division operator, not comment-start."""
    code = '''package main
import (
    "vitess.io/vitess/go/vt/sqlparser"
    "fmt"
)
func main() {
    parser, err := sqlparser.New(sqlparser.Options{MySQLServerVersion: "8.1.20"})
    if err != nil { panic(err) }
    stmt, err := parser.Parse("SELECT /*!80100 1 / 2 */ FROM dual")
    if err != nil { panic(err) }
    fmt.Println(sqlparser.String(stmt))
}
'''
    r = run_go_program(code)
    assert r.returncode == 0, f"compile/run failed:\n{r.stderr}"
    output = r.stdout.strip()
    assert "1 / 2" in output, f"expected '1 / 2' (division) in output, got: {output}"



if __name__ == "__main__":
    import sys
    tests = [name for name in dir() if name.startswith("test_")]
    failed = []
    for tname in tests:
        fn = globals()[tname]
        try:
            fn()
            print(f"PASS: {tname}")
        except AssertionError as e:
            print(f"FAIL: {tname} — {e}")
            failed.append(tname)
        except Exception as e:
            print(f"ERROR: {tname} — {e}")
            failed.append(tname)
    if failed:
        print(f"\n{len(failed)} tests failed")
        sys.exit(1)
    print("\nAll tests passed")