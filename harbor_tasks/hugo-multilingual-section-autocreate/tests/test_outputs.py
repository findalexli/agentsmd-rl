"""Tests for hugo-multilingual-section-autocreate.

The fail-to-pass test is a Go integration test we generate at run-time
into the hugolib package, then run via `go test`. The pass-to-pass tests
run a sample of the repo's existing fast tests, plus gofmt as a code
style check (the agent config requires `./check.sh` cleanliness, of
which gofmt is a part).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path("/workspace/hugo")
HUGOLIB = REPO / "hugolib"
INJECTED_TEST = HUGOLIB / "multilingual_section_harness_test.go"

_HARNESS_TEST = '''// Test fixture injected by the benchmark harness.
package hugolib

import (
\t"testing"
)

// Issue 14681: section pages must be auto-created for each language that has
// content under the section, even when no _index.md exists in any language.
func TestPublishMultilingualSectionCreation_Harness(t *testing.T) {
\tt.Parallel()

\tfiles := `
-- hugo.toml --
capitalizeListTitles = false
pluralizeListTitles = false
disableKinds = ['rss','sitemap','taxonomy','term']

defaultContentLanguage = "fr"
defaultContentLanguageInSubdir = true

[languages.fr]
contentDir = "content/fr"
weight = 1

[languages.en]
contentDir = "content/en"
weight = 2

[languages.de]
contentDir = "content/de"
weight = 3
-- layouts/home.html --
HOME {{ .Language.Name }}
-- layouts/page.html --
{{ .Title }} {{ .Language.Name }}
-- layouts/section.html --
{{ .Title }} {{ .Language.Name }}
-- content/de/s1/p1.md --
---
title: p1
---
-- content/en/s1/p2.md --
---
title: p2
---
-- content/fr/s1/p3.md --
---
title: p3
---
`

\tb := Test(t, files)

\tb.AssertFileContent("public/de/index.html", "HOME de")
\tb.AssertFileContent("public/de/s1/index.html", "s1 de")
\tb.AssertFileContent("public/de/s1/p1/index.html", "p1 de")

\tb.AssertFileContent("public/en/index.html", "HOME en")
\tb.AssertFileContent("public/en/s1/index.html", "s1 en")
\tb.AssertFileContent("public/en/s1/p2/index.html", "p2 en")

\tb.AssertFileContent("public/fr/index.html", "HOME fr")
\tb.AssertFileContent("public/fr/s1/index.html", "s1 fr")
\tb.AssertFileContent("public/fr/s1/p3/index.html", "p3 fr")
}
'''


def _ensure_test_injected() -> None:
    """Write the harness Go test into hugolib/ so `go test` picks it up."""
    if not INJECTED_TEST.exists() or INJECTED_TEST.read_text() != _HARNESS_TEST:
        INJECTED_TEST.write_text(_HARNESS_TEST)


def _run(cmd: list[str], timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def test_hugolib_compiles():
    """Sanity: hugolib package compiles cleanly."""
    r = _run(["go", "build", "./hugolib/"], timeout=300)
    assert r.returncode == 0, (
        f"go build ./hugolib/ failed:\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr[-2000:]}"
    )


def test_multilingual_section_autocreate():
    """f2p: Sections must be created for every language that has content under them.

    Issue 14681. With a multilingual site whose languages each have a content
    directory but no _index.md files, building the site must produce
    public/<lang>/<section>/index.html for EVERY language that owns content
    under <section> — not just the first language encountered while walking.
    """
    _ensure_test_injected()
    r = _run(
        [
            "go",
            "test",
            "-run",
            "TestPublishMultilingualSectionCreation_Harness",
            "./hugolib/",
            "-count=1",
            "-timeout",
            "120s",
            "-v",
        ],
        timeout=300,
    )
    output = r.stdout + r.stderr
    assert r.returncode == 0, (
        "Multilingual section auto-creation test failed.\n"
        "Expected per-language section pages public/{de,en,fr}/s1/index.html.\n"
        "Output (last 3000 chars):\n" + output[-3000:]
    )
    assert "--- PASS: TestPublishMultilingualSectionCreation_Harness" in output, (
        "Did not see PASS marker for the harness test.\nOutput:\n" + output[-3000:]
    )


def test_existing_language_content_root_still_passes():
    """p2p: The existing TestLanguageContentRoot must keep passing."""
    r = _run(
        [
            "go",
            "test",
            "-run",
            "TestLanguageContentRoot$",
            "./hugolib/",
            "-count=1",
            "-timeout",
            "120s",
        ],
        timeout=300,
    )
    assert r.returncode == 0, (
        "TestLanguageContentRoot regressed:\n" + (r.stdout + r.stderr)[-3000:]
    )


def test_existing_smoke_tests_still_pass():
    """p2p: A sample of Hugo smoke tests must keep passing."""
    r = _run(
        [
            "go",
            "test",
            "-run",
            "TestHello$|TestContentMountMerge$|TestIssue13993$",
            "./hugolib/",
            "-count=1",
            "-timeout",
            "120s",
        ],
        timeout=300,
    )
    assert r.returncode == 0, (
        "Existing hugolib tests regressed:\n" + (r.stdout + r.stderr)[-3000:]
    )


def test_repo_gofmt_clean():
    """p2p (agent_config): All Go files in hugolib/ are gofmt-clean.

    Source: AGENTS.md mandates `./check.sh` cleanliness; check.sh runs
    `gofmt -l <package_path>` and fails on any output. The harness's own
    injected test file is excluded from this check.
    """
    r = subprocess.run(
        ["gofmt", "-l", "hugolib"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"gofmt failed to run:\n{r.stderr}"
    flagged = [
        line.strip()
        for line in r.stdout.splitlines()
        if line.strip()
        and not line.strip().endswith("multilingual_section_harness_test.go")
    ]
    assert not flagged, (
        "gofmt found unformatted files (run `gofmt -w` on them):\n"
        + "\n".join(flagged)
    )


def test_no_hdebug_printf_left_behind():
    """p2p (agent_config): No leftover debug prints in the patched file.

    Source: AGENTS.md says debug printing must use `hdebug.Printf` and
    notes that CI fails if any are left behind in merged code.
    """
    target = HUGOLIB / "content_map_page_assembler.go"
    text = target.read_text()
    forbidden = ["hdebug.Printf", "hdebug.Print"]
    found = [tok for tok in forbidden if tok in text]
    assert not found, (
        "Debug-print markers remain in content_map_page_assembler.go: "
        + ", ".join(found)
    )
