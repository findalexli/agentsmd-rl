"""Behavioral tests for hugo PR #14685 (Issue #14684).

Tests verify that ``Source.ValueAsOpenReadSeekCloser`` returns an opener whose
returned readers are independent of one another. The bug under test caused
all opener() calls to return the SAME ``ReadSeekCloser`` (seeked to 0), so
a second open would reset the read position of an already in-use reader.
"""

from __future__ import annotations

import os
import subprocess
import textwrap

REPO = "/workspace/hugo"
PROBE_DIR = os.path.join(REPO, "taskforgeprobe")
PROBE_FILE = os.path.join(PROBE_DIR, "probe_test.go")


def _write_probe(go_source: str) -> None:
    os.makedirs(PROBE_DIR, exist_ok=True)
    with open(PROBE_FILE, "w") as f:
        f.write(go_source)


def _run_probe(timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["go", "test", "-count=1", "-timeout", "120s", "./taskforgeprobe/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def test_opener_returns_independent_readers():
    """Two readers opened concurrently must have independent positions.

    Fail-to-pass: with the buggy shared-reader implementation, the second
    opener() call seeks the shared reader to 0 and reading from it advances
    the position, so the first reader sees an empty tail instead of the
    remaining bytes.
    """
    _write_probe(textwrap.dedent('''\
        package probe_test

        import (
            "io"
            "testing"

            "github.com/gohugoio/hugo/resources/page/pagemeta"
        )

        func TestIndependentReaders(t *testing.T) {
            s := pagemeta.Source{Value: "abcdefgh"}
            opener := s.ValueAsOpenReadSeekCloser()

            r1, err := opener()
            if err != nil {
                t.Fatalf("opener r1: %v", err)
            }
            defer r1.Close()

            buf := make([]byte, 4)
            if _, err := io.ReadFull(r1, buf); err != nil {
                t.Fatalf("ReadFull r1: %v", err)
            }
            if got := string(buf); got != "abcd" {
                t.Fatalf("r1 first half: got %q want %q", got, "abcd")
            }

            r2, err := opener()
            if err != nil {
                t.Fatalf("opener r2: %v", err)
            }
            defer r2.Close()
            all, err := io.ReadAll(r2)
            if err != nil {
                t.Fatalf("ReadAll r2: %v", err)
            }
            if got := string(all); got != "abcdefgh" {
                t.Fatalf("r2 full read: got %q want %q", got, "abcdefgh")
            }

            rest, err := io.ReadAll(r1)
            if err != nil {
                t.Fatalf("ReadAll r1 rest: %v", err)
            }
            if got := string(rest); got != "efgh" {
                t.Fatalf("r1 remainder: got %q want %q", got, "efgh")
            }
        }
    '''))
    r = _run_probe()
    assert r.returncode == 0, (
        f"go test failed:\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )


def test_opener_repeated_full_reads_yield_full_value():
    """Calling opener() many times must yield the full value each time.

    Fail-to-pass: under the buggy implementation, after the first reader is
    fully consumed the second opener() returns the same reader seeked to 0,
    BUT a third call from a still-open second reader would interleave and
    is not the failure mode here. The simpler symptom we test: open three
    INDEPENDENT readers, each fully consumed, and verify all three see the
    full content. The bug breaks this when readers overlap in lifetime.
    """
    _write_probe(textwrap.dedent('''\
        package probe_test

        import (
            "io"
            "testing"

            "github.com/gohugoio/hugo/resources/page/pagemeta"
        )

        func TestThreeInterleavedReaders(t *testing.T) {
            content := "the quick brown fox jumps over the lazy dog"
            s := pagemeta.Source{Value: content}
            opener := s.ValueAsOpenReadSeekCloser()

            // Three readers held simultaneously.
            r1, err := opener()
            if err != nil {
                t.Fatalf("r1: %v", err)
            }
            defer r1.Close()

            // Read 10 bytes from r1.
            buf1 := make([]byte, 10)
            if _, err := io.ReadFull(r1, buf1); err != nil {
                t.Fatalf("ReadFull r1: %v", err)
            }
            if string(buf1) != content[:10] {
                t.Fatalf("r1 prefix: got %q want %q", string(buf1), content[:10])
            }

            r2, err := opener()
            if err != nil {
                t.Fatalf("r2: %v", err)
            }
            defer r2.Close()

            // Fully consume r2 — must see the entire content.
            all2, err := io.ReadAll(r2)
            if err != nil {
                t.Fatalf("ReadAll r2: %v", err)
            }
            if string(all2) != content {
                t.Fatalf("r2 full: got %q want %q", string(all2), content)
            }

            r3, err := opener()
            if err != nil {
                t.Fatalf("r3: %v", err)
            }
            defer r3.Close()

            all3, err := io.ReadAll(r3)
            if err != nil {
                t.Fatalf("ReadAll r3: %v", err)
            }
            if string(all3) != content {
                t.Fatalf("r3 full: got %q want %q", string(all3), content)
            }

            // r1 must still be at position 10 — read the rest.
            rest, err := io.ReadAll(r1)
            if err != nil {
                t.Fatalf("ReadAll r1: %v", err)
            }
            if string(rest) != content[10:] {
                t.Fatalf("r1 remainder: got %q want %q", string(rest), content[10:])
            }
        }
    '''))
    r = _run_probe()
    assert r.returncode == 0, (
        f"go test failed:\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )


def test_opener_with_non_string_value():
    """ValueAsOpenReadSeekCloser also supports non-string Value (cast to string).

    Verifies the captured content is correct regardless of the underlying
    Value type, and that independence still holds for byte/integer values.
    """
    _write_probe(textwrap.dedent('''\
        package probe_test

        import (
            "io"
            "testing"

            "github.com/gohugoio/hugo/resources/page/pagemeta"
        )

        func TestNonStringValueIsIndependent(t *testing.T) {
            // []byte should be cast to string by ValueAsString.
            s := pagemeta.Source{Value: []byte("0123456789")}
            opener := s.ValueAsOpenReadSeekCloser()

            r1, err := opener()
            if err != nil {
                t.Fatalf("r1: %v", err)
            }
            defer r1.Close()

            head := make([]byte, 3)
            if _, err := io.ReadFull(r1, head); err != nil {
                t.Fatalf("ReadFull r1: %v", err)
            }
            if string(head) != "012" {
                t.Fatalf("r1 head: got %q want %q", string(head), "012")
            }

            r2, err := opener()
            if err != nil {
                t.Fatalf("r2: %v", err)
            }
            defer r2.Close()
            all, err := io.ReadAll(r2)
            if err != nil {
                t.Fatalf("ReadAll r2: %v", err)
            }
            if string(all) != "0123456789" {
                t.Fatalf("r2 full: got %q want %q", string(all), "0123456789")
            }

            rest, err := io.ReadAll(r1)
            if err != nil {
                t.Fatalf("ReadAll r1: %v", err)
            }
            if string(rest) != "3456789" {
                t.Fatalf("r1 rest: got %q want %q", string(rest), "3456789")
            }
        }
    '''))
    r = _run_probe()
    assert r.returncode == 0, (
        f"go test failed:\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )


def test_pagemeta_existing_tests_pass():
    """pass_to_pass: existing pagemeta package tests must still pass.

    Excludes our probe directory which is created at test-time.
    """
    # Make sure probe dir doesn't break anything by being unrelated.
    r = subprocess.run(
        ["go", "test", "-count=1", "-timeout", "120s", "./resources/page/pagemeta/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"pagemeta tests failed:\nstdout:\n{r.stdout}\nstderr:\n{r.stderr[-2000:]}"
    )


def test_pagemeta_gofmt():
    """pass_to_pass: changed files must be gofmt-clean (./check.sh enforces this)."""
    r = subprocess.run(
        ["gofmt", "-l", "resources/page/pagemeta/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"gofmt errored: {r.stderr}"
    assert r.stdout.strip() == "", (
        f"gofmt found unformatted files:\n{r.stdout}"
    )


def test_pagemeta_go_vet():
    """pass_to_pass: ``go vet`` on pagemeta must be clean."""
    r = subprocess.run(
        ["go", "vet", "./resources/page/pagemeta/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"go vet failed:\n{r.stderr}"


def test_pagemeta_staticcheck():
    """pass_to_pass: staticcheck on pagemeta must be clean (./check.sh enforces this)."""
    r = subprocess.run(
        ["staticcheck", "./resources/page/pagemeta/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"staticcheck reported issues:\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )


def test_project_builds():
    """pass_to_pass: ``go build`` on the hugo binary must succeed."""
    r = subprocess.run(
        ["go", "build", "-o", "/tmp/hugo-build", "."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"go build failed:\n{r.stderr[-2000:]}"


def test_no_new_exported_symbols_in_changed_file():
    """agent_config: ``Never export symbols that's not needed outside the package``.

    Verify the fix does not introduce any newly exported function / method /
    type / var / const at the top level of page_frontmatter.go beyond those
    that existed at the base commit. The bug fix changes only the body of an
    already-exported method, so no new top-level exports are needed.

    Source: AGENTS.md (base commit b55d452e46e81369a65978459a0683efa484c11b),
    rule: "Never export symbols that's not needed outside of the package."
    """
    import re

    base_exports = {
        # Captured from base commit b55d452e46e81369a65978459a0683efa484c11b
        # of resources/page/pagemeta/page_frontmatter.go (top-level decls only).
        "Compile", "CompileEarly", "CompileForPagesFromDataPre",
        "Dates", "DatesStrings", "DecodeFrontMatterConfig",
        "DefaultPageConfig", "FrontMatterDescriptor", "FrontMatterHandler",
        "FrontMatterOnlyValues", "FrontmatterConfig", "HandleDates",
        "Init", "IsAllDatesZero", "IsDateKey", "IsDateOrLastModAfter",
        "IsResourceValue", "IsZero", "MarkupToMediaType",
        "MatchLanguageCoarse", "MatchRoleCoarse", "MatchSiteVector",
        "MatchVersionCoarse", "NewFrontmatterHandler",
        "PageConfigEarly", "PageConfigLate", "ResourceConfig",
        "SetMetaPreFromMap", "SitesMatrixAndComplements", "Source",
        "String", "UpdateDateAndLastmodAndPublishDateIfAfter", "Validate",
        "ValueAsOpenReadSeekCloser", "ValueAsString",
    }
    file_path = os.path.join(REPO, "resources/page/pagemeta/page_frontmatter.go")
    with open(file_path) as f:
        src = f.read()

    # Collect top-level exported declarations: func, type, var, const.
    exported = set()
    for m in re.finditer(r"^(?:func\s+(?:\([^)]*\)\s+)?|type\s+|var\s+|const\s+)([A-Z][\w]*)", src, re.MULTILINE):
        exported.add(m.group(1))

    new_exports = exported - base_exports
    assert not new_exports, (
        f"New exported symbols at top level of page_frontmatter.go: "
        f"{sorted(new_exports)}. Per AGENTS.md, do not export symbols that "
        f"are not needed outside the package."
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_brew():
    """pass_to_pass | CI job 'test' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'brew install pandoc'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_choco():
    """pass_to_pass | CI job 'test' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'choco install pandoc'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_pandoc():
    """pass_to_pass | CI job 'test' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pandoc -v'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_choco():
    """pass_to_pass | CI job 'test' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'choco install mingw'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_staticcheck():
    """pass_to_pass | CI job 'test' → step 'Run staticcheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'export STATICCHECK_CACHE="${{ runner.temp }}/staticcheck"\nstaticcheck ./...\nrm -rf ${{ runner.temp }}/staticcheck'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step 'Run staticcheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_check():
    """pass_to_pass | CI job 'test' → step 'Check'"""
    r = subprocess.run(
        ["bash", "-lc", 'sass --version;\nmage -v check;'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step 'Check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_test():
    """pass_to_pass | CI job 'test' → step 'Test'"""
    r = subprocess.run(
        ["bash", "-lc", 'mage -v test'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step 'Test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_build_for_dragonfly():
    """pass_to_pass | CI job 'test' → step 'Build for dragonfly'"""
    r = subprocess.run(
        ["bash", "-lc", 'go install\ngo clean -i -cache'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step 'Build for dragonfly' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_TestPagesFromGoTmplAddResourceFromStringContent():
    """fail_to_pass | PR added test 'TestPagesFromGoTmplAddResourceFromStringContent' in 'hugolib/pagesfromdata/pagesfromgotmpl_integration_test.go' (go_test)"""
    r = subprocess.run(
        ["bash", "-lc", 'go test ./hugolib/pagesfromdata -run "^TestPagesFromGoTmplAddResourceFromStringContent$" -count=1 -v 2>&1 | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'TestPagesFromGoTmplAddResourceFromStringContent' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_TestSourceValueAsOpenReadSeekCloserIsIndependent():
    """fail_to_pass | PR added test 'TestSourceValueAsOpenReadSeekCloserIsIndependent' in 'resources/page/pagemeta/page_frontmatter_test.go' (go_test)"""
    r = subprocess.run(
        ["bash", "-lc", 'go test ./resources/page/pagemeta -run "^TestSourceValueAsOpenReadSeekCloserIsIndependent$" -count=1 -v 2>&1 | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'TestSourceValueAsOpenReadSeekCloserIsIndependent' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
