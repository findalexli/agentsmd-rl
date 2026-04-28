"""
Task: backstage-docs-add-documentation-style-guide
Repo: backstage/backstage @ 7c99d4f3021c375b4dea1bae6156ccbf527580e3
PR:   33538

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/backstage"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_guide() -> str:
    """Read the style guide, failing fast if it doesn't exist."""
    guide = Path(REPO) / "docs" / "contribute" / "doc-style-guide.md"
    assert guide.exists(), "docs/contribute/doc-style-guide.md does not exist"
    return guide.read_text()


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js inline script in the repo directory."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — the new documentation style guide
# ---------------------------------------------------------------------------

def test_style_guide_exists_with_frontmatter():
    """docs/contribute/doc-style-guide.md exists with Docusaurus frontmatter."""
    content = _read_guide()

    # Use Node to parse and validate the YAML frontmatter (behavioral)
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('docs/contribute/doc-style-guide.md', 'utf8');
const match = content.match(/^---\\r?\\n([\\s\\S]*?)\\r?\\n---/);
if (!match) { console.error('no frontmatter'); process.exit(1); }
const fm = match[1];
const obj = {};
for (const line of fm.split('\\n')) {
  const m = line.match(/^(\\w[\\w-]*):\\s*(.+)$/);
  if (m) obj[m[1]] = m[2].trim();
}
if (obj.id !== 'doc-style-guide') {
  console.error('id must be doc-style-guide, got: ' + obj.id);
  process.exit(1);
}
if (!obj.title || !obj.title.toLowerCase().match(/style|guide/)) {
  console.error('title must mention style or guide, got: ' + obj.title);
  process.exit(1);
}
console.log('PASS id=' + obj.id + ' title=' + obj.title);
""")
    assert r.returncode == 0, f"Frontmatter validation failed: {r.stderr}"
    assert "PASS" in r.stdout

    # Must be substantive (not a stub)
    assert len(content) > 2000, (
        f"Style guide is too short ({len(content)} chars) — needs substantive content"
    )


def test_style_guide_covers_tone():
    """Style guide covers tone/voice guidelines (friendly, professional)."""
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('docs/contribute/doc-style-guide.md', 'utf8');

// Parse markdown into sections by splitting on ## headings
const sections = content.split(/^## /m);
let toneSection = null;
for (const s of sections) {
  if (s.toLowerCase().startsWith('tone')) {
    toneSection = s.toLowerCase();
    break;
  }
}
if (!toneSection) {
  console.error('Style guide must have a ## Tone section');
  process.exit(1);
}

// Tone section must cover both friendly AND professional aspects
const friendly = ['friendly', 'approachable', 'welcoming'].some(w => toneSection.includes(w));
const professional = ['professional', 'precise'].some(w => toneSection.includes(w));
if (!friendly) {
  console.error('Tone section should mention approachable/friendly writing');
  process.exit(1);
}
if (!professional) {
  console.error('Tone section should mention professional/precise writing');
  process.exit(1);
}
console.log('PASS tone_section_valid');
""")
    assert r.returncode == 0, f"Tone validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_style_guide_covers_formatting():
    """Style guide covers formatting standards (bold, code style, backticks)."""
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('docs/contribute/doc-style-guide.md', 'utf8').toLowerCase();

// Must cover code formatting guidance
const hasCodeFmt = ['code style', 'backtick', 'inline code', 'use code style']
  .some(p => content.includes(p));
if (!hasCodeFmt) {
  console.error('Style guide must cover code formatting (backticks for code/filenames)');
  process.exit(1);
}

// Must cover bold for UI elements
if (!content.includes('bold')) {
  console.error('Style guide must cover bold formatting');
  process.exit(1);
}

console.log('PASS formatting_valid');
""")
    assert r.returncode == 0, f"Formatting validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_style_guide_covers_writing_practices():
    """Style guide covers active voice, present tense, addressing reader as you."""
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('docs/contribute/doc-style-guide.md', 'utf8').toLowerCase();

if (!content.includes('active voice')) {
  console.error('Style guide must cover active voice');
  process.exit(1);
}
if (!content.includes('present tense')) {
  console.error('Style guide must cover present tense');
  process.exit(1);
}

// Must explicitly instruct addressing the reader as "you"
const hasYou = [
  'address the reader',
  '"you"',
  "'you'",
  'second person',
  'reader as "you"'
].some(p => content.includes(p));
if (!hasYou) {
  console.error('Style guide must instruct writers to address the reader as you');
  process.exit(1);
}

console.log('PASS writing_practices_valid');
""")
    assert r.returncode == 0, f"Writing practices validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_style_guide_has_word_list():
    """Style guide includes Backstage-specific word/terminology list."""
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('docs/contribute/doc-style-guide.md', 'utf8').toLowerCase();

// Must have a word list or terminology section
const hasSection = ['word list', 'terminology', 'glossary'].some(p => content.includes(p));
if (!hasSection) {
  console.error('Style guide must include a word list or terminology section');
  process.exit(1);
}

// The word list should define key Backstage terms (at least 2)
const terms = ['techdocs', 'scaffolder', 'software catalog', 'software templates'];
const found = terms.filter(t => content.includes(t)).length;
if (found < 2) {
  console.error('Word list must define at least 2 Backstage terms, found ' + found);
  process.exit(1);
}

console.log('PASS word_list_valid found=' + found);
""")
    assert r.returncode == 0, f"Word list validation failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — sidebar must include the new page
# ---------------------------------------------------------------------------

def test_sidebar_includes_style_guide():
    """microsite/sidebars.ts includes doc-style-guide in contribute section."""
    sidebars = Path(REPO) / "microsite" / "sidebars.ts"
    assert sidebars.exists(), "microsite/sidebars.ts must exist"

    # Use Node to parse the TypeScript and verify entry placement
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('microsite/sidebars.ts', 'utf8');

if (!content.includes('doc-style-guide')) {
  console.error('doc-style-guide not found in sidebars.ts');
  process.exit(1);
}

// Verify doc-style-guide appears in the contribute section context
const lines = content.split('\\n');
let found = false;
for (let i = 0; i < lines.length; i++) {
  if (lines[i].includes('doc-style-guide')) {
    // Check surrounding lines for 'contribute' context
    const start = Math.max(0, i - 20);
    const end = Math.min(lines.length, i + 5);
    const ctx = lines.slice(start, end).join('\\n');
    if (ctx.includes('contribute')) {
      found = true;
      break;
    }
  }
}
if (!found) {
  console.error('doc-style-guide must appear in contribute sidebar section');
  process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Sidebar validation failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI checks that should pass on base commit
# ---------------------------------------------------------------------------

def test_repo_verify_links():
    """Repo link verification passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "scripts/verify-links.js"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Link verification failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_lockfile_no_duplicates():
    """Repo lockfile has no duplicate dependencies (pass_to_pass)."""
    r = subprocess.run(
        ["node", "scripts/verify-lockfile-duplicates.js"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Lockfile verification failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_docs_structure_valid():
    """Repo documentation structure is valid (pass_to_pass)."""
    # Verify key documentation files exist for the style guide PR context
    required_files = [
        "AGENTS.md",
        "CONTRIBUTING.md",
        "docs",
        "microsite/sidebars.ts",
    ]
    missing = []
    for f in required_files:
        if not (Path(REPO) / f).exists():
            missing.append(f)
    assert not missing, f"Required documentation files missing: {missing}"

    # Verify sidebars.ts is valid TypeScript (can be parsed)
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('microsite/sidebars.ts', 'utf8');
// Basic validation: should be non-empty and contain sidebar structure
if (!content || content.length < 100) {
  console.error('sidebars.ts is too short or empty');
  process.exit(1);
}
if (!content.includes('contribute') || !content.includes('Sidebar')) {
  console.error('sidebars.ts missing expected contribute section or Sidebar');
  process.exit(1);
}
console.log('PASS sidebars.ts structure valid');
""")
    assert r.returncode == 0, f"Sidebar validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_doc_references_valid():
    """Repo documentation cross-references are valid (pass_to_pass)."""
    # Verify that CONTRIBUTING.md references docs directory
    contributing = Path(REPO) / "CONTRIBUTING.md"
    content = contributing.read_text()

    # Should reference the docs directory
    has_docs_ref = "docs" in content and ("[docs]" in content or "docs/" in content)
    assert has_docs_ref, "CONTRIBUTING.md should reference docs directory"

    # Verify AGENTS.md exists and has content
    agents = Path(REPO) / "AGENTS.md"
    assert agents.exists(), "AGENTS.md must exist"
    agents_content = agents.read_text()
    assert len(agents_content) > 500, "AGENTS.md should have substantial content"

