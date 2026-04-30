"""Behavioral checks for skills-fix-collapse-multiline-yaml-descriptions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('brand-yml/SKILL.md')
    assert 'description: Create and use brand.yml files for consistent branding across Shiny apps and Quarto documents. Covers: (1) Creating new _brand.yml files, (2) Applying to Shiny (R and Python), (3) Using i' in text, "expected to find: " + 'description: Create and use brand.yml files for consistent branding across Shiny apps and Quarto documents. Covers: (1) Creating new _brand.yml files, (2) Applying to Shiny (R and Python), (3) Using i'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('brand-yml/SKILL.md')
    assert '- **Explicit paths**: Use custom file names only when necessary (shared branding, multiple variants)' in text, "expected to find: " + '- **Explicit paths**: Use custom file names only when necessary (shared branding, multiple variants)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('brand-yml/SKILL.md')
    assert 'version: "1.1"' in text, "expected to find: " + 'version: "1.1"'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('posit-dev/critical-code-reviewer/SKILL.md')
    assert 'description: Conduct rigorous, adversarial code reviews with zero tolerance for mediocrity. Use when users ask to "critically review" my code or a PR, "critique my code", "find issues in my code", or ' in text, "expected to find: " + 'description: Conduct rigorous, adversarial code reviews with zero tolerance for mediocrity. Use when users ask to "critically review" my code or a PR, "critique my code", "find issues in my code", or '[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('posit-dev/critical-code-reviewer/SKILL.md')
    assert 'Note: Approval means "no blocking issues found after rigorous review", not "perfect code." Don\'t manufacture problems to avoid approving.' in text, "expected to find: " + 'Note: Approval means "no blocking issues found after rigorous review", not "perfect code." Don\'t manufacture problems to avoid approving.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('posit-dev/critical-code-reviewer/SKILL.md')
    assert 'version: "1.1"' in text, "expected to find: " + 'version: "1.1"'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('posit-dev/describe-design/SKILL.md')
    assert 'description: Research a codebase and create architectural documentation describing how features or systems work. Use when the user asks to: (1) Document how a feature works, (2) Create an architecture' in text, "expected to find: " + 'description: Research a codebase and create architectural documentation describing how features or systems work. Use when the user asks to: (1) Document how a feature works, (2) Create an architecture'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('posit-dev/describe-design/SKILL.md')
    assert '- **Stay current**: Note any assumptions about code state or version.' in text, "expected to find: " + '- **Stay current**: Note any assumptions about code state or version.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('posit-dev/describe-design/SKILL.md')
    assert 'version: "1.1"' in text, "expected to find: " + 'version: "1.1"'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('quarto/quarto-alt-text/SKILL.md')
    assert 'description: Generate accessible alt text for data visualizations in Quarto documents. Use when the user wants to add, improve, or review alt text for figures in .qmd files. Triggers for requests abou' in text, "expected to find: " + 'description: Generate accessible alt text for data visualizations in Quarto documents. Use when the user wants to add, improve, or review alt text for figures in .qmd files. Triggers for requests abou'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('quarto/quarto-alt-text/SKILL.md')
    assert 'version: "1.1"' in text, "expected to find: " + 'version: "1.1"'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('quarto/quarto-authoring/SKILL.md')
    assert 'description: Writing and authoring Quarto documents (.qmd), including code cell options, figure and table captions, cross-references, callout blocks (notes, warnings, tips), citations and bibliography' in text, "expected to find: " + 'description: Writing and authoring Quarto documents (.qmd), including code cell options, figure and table captions, cross-references, callout blocks (notes, warnings, tips), citations and bibliography'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('quarto/quarto-authoring/SKILL.md')
    assert '- [Community Extensions List](https://m.canouil.dev/quarto-extensions/)' in text, "expected to find: " + '- [Community Extensions List](https://m.canouil.dev/quarto-extensions/)'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('quarto/quarto-authoring/SKILL.md')
    assert 'version: "1.3"' in text, "expected to find: " + 'version: "1.3"'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('r-lib/lifecycle/SKILL.md')
    assert 'description: Guidance for managing R package lifecycle according to tidyverse principles using the lifecycle package. Use when: (1) Setting up lifecycle infrastructure in a package, (2) Deprecating fu' in text, "expected to find: " + 'description: Guidance for managing R package lifecycle according to tidyverse principles using the lifecycle package. Use when: (1) Setting up lifecycle infrastructure in a package, (2) Deprecating fu'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('r-lib/lifecycle/SKILL.md')
    assert 'See `references/lifecycle-stages.md` for detailed stage definitions and transitions.' in text, "expected to find: " + 'See `references/lifecycle-stages.md` for detailed stage definitions and transitions.'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('r-lib/lifecycle/SKILL.md')
    assert 'version: "1.1"' in text, "expected to find: " + 'version: "1.1"'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('r-lib/mirai/SKILL.md')
    assert 'description: Help users write correct R code for async, parallel, and distributed computing using mirai. Use when users need to: run R code asynchronously or in parallel, write mirai code with correct' in text, "expected to find: " + 'description: Help users write correct R code for async, parallel, and distributed computing using mirai. Use when users need to: run R code asynchronously or in parallel, write mirai code with correct'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('r-lib/mirai/SKILL.md')
    assert 'version: "1.1"' in text, "expected to find: " + 'version: "1.1"'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('r-lib/r-cli-app/SKILL.md')
    assert 'description: Build command-line apps in R using the Rapp package. Use when creating a CLI tool in R, adding argument parsing to an R script, turning an R script into a command-line app, shipping CLIs ' in text, "expected to find: " + 'description: Build command-line apps in R using the Rapp package. Use when creating a CLI tool in R, adding argument parsing to an R script, turning an R script into a command-line app, shipping CLIs '[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('r-lib/r-cli-app/SKILL.md')
    assert 'accessing the returned environment, and test output with `expect_snapshot()`.' in text, "expected to find: " + 'accessing the returned environment, and test output with `expect_snapshot()`.'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('r-lib/r-cli-app/SKILL.md')
    assert '**See [references/advanced.md](references/advanced.md#testing-cli-apps)** for' in text, "expected to find: " + '**See [references/advanced.md](references/advanced.md#testing-cli-apps)** for'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('r-lib/r-package-development/SKILL.md')
    assert 'description: R package development with devtools, testthat, and roxygen2. Use when the user is working on an R package, running tests, writing documentation, or building package infrastructure.' in text, "expected to find: " + 'description: R package development with devtools, testthat, and roxygen2. Use when the user is working on an R package, running tests, writing documentation, or building package infrastructure.'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('r-lib/r-package-development/SKILL.md')
    assert "- Order bullets alphabetically by function name. Put all bullets that don't mention function names at the beginning." in text, "expected to find: " + "- Order bullets alphabetically by function name. Put all bullets that don't mention function names at the beginning."[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('r-lib/r-package-development/SKILL.md')
    assert 'author: Simon P. Couch (@simonpcouch)' in text, "expected to find: " + 'author: Simon P. Couch (@simonpcouch)'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('r-lib/testing-r-packages/SKILL.md')
    assert 'description: Best practices for writing R package tests using testthat version 3+. Use when writing, organizing, or improving tests for R packages. Covers test structure, expectations, fixtures, snaps' in text, "expected to find: " + 'description: Best practices for writing R package tests using testthat version 3+. Use when writing, organizing, or improving tests for R packages. Covers test structure, expectations, fixtures, snaps'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('r-lib/testing-r-packages/SKILL.md')
    assert '**Shuffle tests:** `devtools::test(shuffle = TRUE)`' in text, "expected to find: " + '**Shuffle tests:** `devtools::test(shuffle = TRUE)`'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('r-lib/testing-r-packages/SKILL.md')
    assert 'version: "1.1"' in text, "expected to find: " + 'version: "1.1"'[:80]

