"""
Task: vitess-sqlparser-replace-nested-tokenizer-with
Repo: vitessio/vitess @ 9a3646f7f16d38cec2efabc13cef5da800a72280
PR:   19725

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/vitess"
SQLPARSER = Path(REPO) / "go" / "vt" / "sqlparser"


def _run_go_test(test_name: str, go_src: str, timeout: int = 180):
    """Write a temporary Go test file in the sqlparser package, run it, clean up."""
    test_file = SQLPARSER / f"_harness_{test_name}_test.go"
    test_file.write_text(go_src)
    try:
        r = subprocess.run(
            ["go", "test", f"-run=^{test_name}$", "-count=1", "-timeout=60s",
             "./go/vt/sqlparser/"],
            cwd=REPO, capture_output=True, timeout=timeout,
        )
        return r
    finally:
        test_file.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Go files in sqlparser must compile without errors."""
    r = subprocess.run(
        ["go", "build", "./go/vt/sqlparser/..."],
        cwd=REPO, capture_output=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"go build failed:\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_short_version_digits_error():
    """Versioned comment with fewer than 5 digits must produce a parse error.

    Before the fix, /*!2*/ was silently accepted. After the fix, fewer than 5
    version digits means the digits are treated as content, causing a syntax
    error (matching MySQL 8.4 behavior).
    """
    r = _run_go_test("TestHarnessShortVersionDigits", """\
package sqlparser

import (
\t"testing"

\t"github.com/stretchr/testify/require"
)

func TestHarnessShortVersionDigits(t *testing.T) {
\tparser, err := New(Options{MySQLServerVersion: "8.1.20"})
\trequire.NoError(t, err)
\t_, err = parser.Parse("select 1/*!2*/;")
\trequire.Error(t, err, "fewer than 5 version digits should produce parse error")
}
""")
    assert r.returncode == 0, (
        f"Go test failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_nested_comment_in_expanded_versioned():
    """Nested /* */ inside an expanded versioned comment must be consumed.

    Before the fix, the nested Tokenizer approach caused the inner /* to start
    a comment that was never closed, producing LEX_ERROR. After the fix, the
    inline scanner correctly consumes nested comments.
    """
    r = _run_go_test("TestHarnessNestedInExpanded", """\
package sqlparser

import (
\t"testing"

\t"github.com/stretchr/testify/assert"
\t"github.com/stretchr/testify/require"
)

func TestHarnessNestedInExpanded(t *testing.T) {
\tparser, err := New(Options{MySQLServerVersion: "8.1.20"})
\trequire.NoError(t, err)

\tstmt, err := parser.Parse("SELECT /*!80100 1 /* a comment */ + 2 */")
\trequire.NoError(t, err, "nested comment inside expanded versioned comment should parse")
\tassert.Equal(t, "select 1 + 2 from dual", String(stmt))
}
""")
    assert r.returncode == 0, (
        f"Go test failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass

    Before the fix, the closing */ of the nested comment prematurely terminated
    the outer versioned comment, leaving trailing tokens that caused parse errors.
    After the fix, nested comments are tracked so the correct closing */ is found.
    """
    r = _run_go_test("TestHarnessSkippedNested", """\
package sqlparser

import (
\t"testing"

\t"github.com/stretchr/testify/assert"
\t"github.com/stretchr/testify/require"
)

func TestHarnessSkippedNested(t *testing.T) {
\tparser, err := New(Options{MySQLServerVersion: "8.1.20"})
\trequire.NoError(t, err)

\tstmt, err := parser.Parse("SELECT /*!90000 1 /* nested */ + 2 */ 42")
\trequire.NoError(t, err, "skipped versioned comment with nested comment should parse")
\tassert.Equal(t, "select 42 from dual", String(stmt))
}
""")
    assert r.returncode == 0, (
        f"Go test failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Config edit (config_edit) — agent config file update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    The refactor eliminates recursive Scan() calls. The AGENTS.md should
    document this design constraint so future contributors avoid reintroducing
    recursion in scan helper methods.
    """
    agents_md = SQLPARSER / "AGENTS.md"
    assert agents_md.exists(), (
        "go/vt/sqlparser/AGENTS.md must exist to document tokenizer constraints"
    )
    content = agents_md.read_text()
    content_lower = content.lower()

    # Must reference the tokenizer or token.go
    assert "tokenizer" in content_lower or "token.go" in content_lower, (
        "AGENTS.md should reference the tokenizer or token.go"
    )

    # Must warn about recursion or stack overflow
    assert any(w in content_lower for w in ["recursion", "stack overflow", "stack growth"]), (
        "AGENTS.md should warn about recursion or stack overflow risks"
    )

    # Must mention scan methods
    assert "scan" in content_lower, (
        "AGENTS.md should mention scan methods"
    )
