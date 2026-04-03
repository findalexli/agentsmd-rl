"""
Task: backstage-docs-add-documentation-style-guide
Repo: backstage/backstage @ 7c99d4f3021c375b4dea1bae6156ccbf527580e3
PR:   33538

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/backstage"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — the new documentation style guide
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_style_guide_exists_with_frontmatter():
    """docs/contribute/doc-style-guide.md must exist with Docusaurus frontmatter."""
    guide = Path(REPO) / "docs" / "contribute" / "doc-style-guide.md"
    assert guide.exists(), "docs/contribute/doc-style-guide.md does not exist"
    content = guide.read_text()
    # Must have Docusaurus frontmatter with id and title
    assert content.startswith("---"), "Style guide must start with YAML frontmatter"
    assert "doc-style-guide" in content[:300], \
        "Frontmatter should include id: doc-style-guide"
    assert re.search(r"title:.*[Ss]tyle\s+[Gg]uide", content[:300]), \
        "Frontmatter should include a title mentioning 'style guide'"
    # Must be substantive (not a stub)
    assert len(content) > 2000, \
        f"Style guide is too short ({len(content)} chars) — needs substantive content"


# [pr_diff] fail_to_pass
def test_style_guide_covers_tone():
    """Style guide must include guidance on tone/voice for documentation."""
    guide = Path(REPO) / "docs" / "contribute" / "doc-style-guide.md"
    content = guide.read_text().lower()
    # Must cover tone — the style guide should address how to write
    assert "tone" in content or "voice" in content, \
        "Style guide must have a section on tone or voice"
    # Should mention being approachable/friendly AND professional
    has_friendly = any(w in content for w in ["friendly", "approachable", "welcoming"])
    has_professional = any(w in content for w in ["professional", "precise", "clear"])
    assert has_friendly, \
        "Tone section should mention approachable/friendly writing"
    assert has_professional, \
        "Tone section should mention professional/precise writing"


# [pr_diff] fail_to_pass
def test_style_guide_covers_formatting():
    """Style guide must include formatting standards for docs."""
    guide = Path(REPO) / "docs" / "contribute" / "doc-style-guide.md"
    content = guide.read_text().lower()
    # Must cover code formatting (backticks for code, filenames, commands)
    has_code_style = "code style" in content or "backtick" in content or "inline code" in content
    assert has_code_style, \
        "Style guide must cover code style formatting (backticks for code/filenames)"
    # Must cover bold usage for UI elements OR general formatting guidance
    has_bold = "bold" in content or "**" in content
    assert has_bold, \
        "Style guide must cover bold formatting"


# [pr_diff] fail_to_pass
def test_style_guide_covers_writing_practices():
    """Style guide must cover core writing practices (active voice, present tense, etc.)."""
    guide = Path(REPO) / "docs" / "contribute" / "doc-style-guide.md"
    content = guide.read_text().lower()
    # Must cover active voice
    assert "active voice" in content, \
        "Style guide must cover active voice"
    # Must cover present tense
    assert "present tense" in content, \
        "Style guide must cover present tense"
    # Must address the reader as "you"
    has_you_guidance = ("address the reader" in content or
                        '"you"' in content or
                        "second person" in content or
                        "address.*reader.*you" in content)
    assert has_you_guidance, \
        "Style guide must instruct writers to address the reader as 'you'"


# [pr_diff] fail_to_pass
def test_style_guide_has_word_list():
    """Style guide must include a Backstage-specific word/terminology list."""
    guide = Path(REPO) / "docs" / "contribute" / "doc-style-guide.md"
    content = guide.read_text().lower()
    # Must have a word list or terminology section
    has_word_list = ("word list" in content or "terminology" in content or
                     "glossary" in content)
    assert has_word_list, \
        "Style guide must include a word list or terminology section"
    # The word list should define key Backstage terms
    has_backstage_terms = sum(1 for term in ["techdocs", "scaffolder", "software catalog"]
                             if term in content)
    assert has_backstage_terms >= 2, \
        "Word list must define at least 2 key Backstage terms (TechDocs, Scaffolder, Software Catalog)"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — config files must reference the new guide
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — sidebar must include the new page
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_sidebar_includes_style_guide():
    """microsite/sidebars.ts must include the doc-style-guide page."""
    sidebars = Path(REPO) / "microsite" / "sidebars.ts"
    content = sidebars.read_text()
    assert "doc-style-guide" in content, \
        "sidebars.ts must include 'doc-style-guide' in the sidebar configuration"
