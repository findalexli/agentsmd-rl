"""
Task: hugo-shared-reader-openreadseekcloser
Repo: hugo @ b55d452e46e81369a65978459a0683efa484c11b
PR:   14685

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/hugo"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified package must compile without errors."""
    r = subprocess.run(
        ["go", "build", "./resources/page/pagemeta/..."],
        cwd=REPO, capture_output=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"Compilation failed:\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def _write_and_run_go_test(name: str, go_code: str) -> subprocess.CompletedProcess:
    """Write a Go test file and run it."""
    test_file = Path(REPO) / "resources" / "page" / "pagemeta" / f"{name}_test.go"
    test_file.write_text(go_code)
    try:
        return subprocess.run(
            ["go", "test", "-run", f"^{name}$", "-count=1", "-timeout=60s",
             "./resources/page/pagemeta/"],
            cwd=REPO, capture_output=True, timeout=120,
        )
    finally:
        test_file.unlink(missing_ok=True)


# [pr_diff] fail_to_pass
def test_opener_independent_readers():
    """Each call to ValueAsOpenReadSeekCloser's opener must return an independent reader."""
    go_code = textwrap.dedent("""\
        package pagemeta_test

        import (
            "io"
            "testing"

            "github.com/gohugoio/hugo/resources/page/pagemeta"
        )

        func TestVerifyIndependentReadersA(t *testing.T) {
            s := pagemeta.Source{Value: "abcdefgh"}
            opener := s.ValueAsOpenReadSeekCloser()

            r1, err := opener()
            if err != nil {
                t.Fatal(err)
            }
            defer r1.Close()

            // Partially consume r1
            buf := make([]byte, 4)
            if _, err := io.ReadFull(r1, buf); err != nil {
                t.Fatal(err)
            }
            if string(buf) != "abcd" {
                t.Fatalf("expected abcd, got %s", string(buf))
            }

            // Open a second reader and fully consume it
            r2, err := opener()
            if err != nil {
                t.Fatal(err)
            }
            defer r2.Close()
            all, err := io.ReadAll(r2)
            if err != nil {
                t.Fatal(err)
            }
            if string(all) != "abcdefgh" {
                t.Fatalf("r2: expected abcdefgh, got %s", string(all))
            }

            // r1 must still yield the remaining bytes
            rest, err := io.ReadAll(r1)
            if err != nil {
                t.Fatal(err)
            }
            if string(rest) != "efgh" {
                t.Fatalf("r1 remainder: expected efgh, got %q", string(rest))
            }
        }
    """)
    r = _write_and_run_go_test("TestVerifyIndependentReadersA", go_code)
    assert r.returncode == 0, (
        f"Independent readers test failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_opener_independent_varied_content():
    """Same independence check with different content and read patterns."""
    go_code = textwrap.dedent("""\
        package pagemeta_test

        import (
            "io"
            "testing"

            "github.com/gohugoio/hugo/resources/page/pagemeta"
        )

        func TestVerifyIndependentReadersB(t *testing.T) {
            s := pagemeta.Source{Value: "the quick brown fox jumps"}
            opener := s.ValueAsOpenReadSeekCloser()

            r1, err := opener()
            if err != nil {
                t.Fatal(err)
            }
            defer r1.Close()

            // Read 10 bytes from r1
            buf := make([]byte, 10)
            if _, err := io.ReadFull(r1, buf); err != nil {
                t.Fatal(err)
            }
            if string(buf) != "the quick " {
                t.Fatalf("expected 'the quick ', got %q", string(buf))
            }

            // Open r2, read 9 bytes
            r2, err := opener()
            if err != nil {
                t.Fatal(err)
            }
            defer r2.Close()
            buf2 := make([]byte, 9)
            if _, err := io.ReadFull(r2, buf2); err != nil {
                t.Fatal(err)
            }
            if string(buf2) != "the quick" {
                t.Fatalf("r2: expected 'the quick', got %q", string(buf2))
            }

            // Open r3, fully consume
            r3, err := opener()
            if err != nil {
                t.Fatal(err)
            }
            defer r3.Close()
            all, err := io.ReadAll(r3)
            if err != nil {
                t.Fatal(err)
            }
            if string(all) != "the quick brown fox jumps" {
                t.Fatalf("r3: expected full content, got %q", string(all))
            }

            // r1 must still have "brown fox jumps"
            rest1, err := io.ReadAll(r1)
            if err != nil {
                t.Fatal(err)
            }
            if string(rest1) != "brown fox jumps" {
                t.Fatalf("r1 remainder: expected 'brown fox jumps', got %q", string(rest1))
            }

            // r2 must still have " brown fox jumps"
            rest2, err := io.ReadAll(r2)
            if err != nil {
                t.Fatal(err)
            }
            if string(rest2) != " brown fox jumps" {
                t.Fatalf("r2 remainder: expected ' brown fox jumps', got %q", string(rest2))
            }
        }
    """)
    r = _write_and_run_go_test("TestVerifyIndependentReadersB", go_code)
    assert r.returncode == 0, (
        f"Varied content test failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_tests_pass():
    """Upstream pagemeta test suite still passes."""
    r = subprocess.run(
        ["go", "test", "-count=1", "-timeout=120s",
         "./resources/page/pagemeta/..."],
        cwd=REPO, capture_output=True, timeout=180,
    )
    assert r.returncode == 0, (
        f"Upstream tests failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [static] pass_to_pass
def test_not_stub():
    """ValueAsOpenReadSeekCloser must have real logic, not a trivial stub."""
    src = Path(f"{REPO}/resources/page/pagemeta/page_frontmatter.go").read_text()
    # Find the function body
    in_func = False
    brace_depth = 0
    body_lines = []
    for line in src.splitlines():
        if "func (s Source) ValueAsOpenReadSeekCloser()" in line:
            in_func = True
            brace_depth = 0
        if in_func:
            brace_depth += line.count("{") - line.count("}")
            body_lines.append(line)
            if brace_depth == 0 and len(body_lines) > 1:
                break
    assert len(body_lines) >= 3, (
        f"ValueAsOpenReadSeekCloser body too short ({len(body_lines)} lines), likely a stub"
    )
    body_text = "\n".join(body_lines)
    assert "return" in body_text, "Function must have a return statement"
