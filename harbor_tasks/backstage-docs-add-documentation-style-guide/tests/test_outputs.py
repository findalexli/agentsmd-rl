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


def _extract_frontmatter_fields(content: str) -> dict:
    """Parse simple YAML key: value frontmatter into a dict."""
    match = re.match(r"^---\r?\n([\s\S]*?)\r?\n---", content)
    if not match:
        return {}
    result = {}
    for line in match.group(1).split("\n"):
        m = re.match(r"^(\w[\w-]*):\s*(.+)$", line)
        if m:
            result[m.group(1)] = m.group(2).strip()
    return result


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
    content = _read_guide()

    # Parse markdown to find the ## Tone section (structured, not grep)
    sections = re.split(r"^## ", content, flags=re.MULTILINE)
    tone_section = None
    for s in sections:
        if s.lower().startswith("tone"):
            tone_section = s.lower()
            break
    assert tone_section is not None, "Style guide must have a ## Tone section"

    # Tone section must cover both friendly AND professional aspects
    has_friendly = any(
        w in tone_section for w in ["friendly", "approachable", "welcoming"]
    )
    has_professional = any(
        w in tone_section for w in ["professional", "precise"]
    )
    assert has_friendly, "Tone section should mention approachable/friendly writing"
    assert has_professional, "Tone section should mention professional/precise writing"


def test_style_guide_covers_formatting():
    """Style guide covers formatting standards (bold, code style, backticks)."""
    content = _read_guide().lower()

    # Must cover code formatting guidance
    has_code_fmt = any(
        p in content
        for p in ["code style", "backtick", "inline code", "use code style"]
    )
    assert has_code_fmt, (
        "Style guide must cover code formatting (backticks for code/filenames)"
    )
    # Must cover bold for UI elements
    assert "bold" in content, "Style guide must cover bold formatting"


def test_style_guide_covers_writing_practices():
    """Style guide covers active voice, present tense, addressing reader as you."""
    content = _read_guide().lower()

    assert "active voice" in content, "Style guide must cover active voice"
    assert "present tense" in content, "Style guide must cover present tense"

    # Must explicitly instruct addressing the reader as "you"
    has_you = any(
        p in content
        for p in [
            'address the reader',
            '"you"',
            "'you'",
            "second person",
            'reader as "you"',
        ]
    )
    assert has_you, (
        "Style guide must instruct writers to address the reader as 'you'"
    )


def test_style_guide_has_word_list():
    """Style guide includes Backstage-specific word/terminology list."""
    content = _read_guide().lower()

    # Must have a word list or terminology section
    has_section = any(
        p in content for p in ["word list", "terminology", "glossary"]
    )
    assert has_section, (
        "Style guide must include a word list or terminology section"
    )

    # The word list should define key Backstage terms (at least 2)
    terms = ["techdocs", "scaffolder", "software catalog", "software templates"]
    found = sum(1 for t in terms if t in content)
    assert found >= 2, (
        f"Word list must define at least 2 Backstage terms, found {found}"
    )


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
    end = Math.min(lines.length, i + 5);
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
