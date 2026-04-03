"""
Task: lotti-task-summary-link-extraction
Repo: matthiasn/lotti @ d06454c02bf8e57a854521890a0c5c9582d6b9ed
PR:   2534

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/lotti"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Dart files must exist and contain valid Dart class/function structure."""
    files = [
        "lib/features/ai/util/preconfigured_prompts.dart",
        "lib/features/ai/ui/expandable_ai_response_summary.dart",
        "lib/features/ai/ui/ai_response_summary.dart",
        "lib/features/ai/ui/ai_response_summary_modal.dart",
        "lib/themes/theme.dart",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} must exist"
        content = p.read_text()
        assert len(content) > 100, f"{f} must not be empty"
        # Basic Dart structure: must have import and class/mixin
        assert "import " in content, f"{f} must contain imports"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — prompt modification tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_prompt_includes_links_section():
    """Task summary prompt must instruct the AI to include a Links section."""
    prompt_file = Path(REPO) / "lib/features/ai/util/preconfigured_prompts.dart"
    content = prompt_file.read_text()

    # The prompt must instruct the AI to add a Links section at the end
    assert "**Links**" in content or "**Links:**" in content, \
        "Prompt must instruct AI to include a Links section"
    assert "Scan ALL log entries" in content or "scan" in content.lower() and "log entries" in content.lower(), \
        "Prompt must instruct to scan log entries for URLs"


# [pr_diff] fail_to_pass
def test_prompt_link_format_and_examples():
    """Prompt must specify Markdown link format and provide examples."""
    prompt_file = Path(REPO) / "lib/features/ai/util/preconfigured_prompts.dart"
    content = prompt_file.read_text()

    # Must specify the link format
    assert "[Succinct Title](URL)" in content, \
        "Prompt must specify [Succinct Title](URL) format"
    # Must include example links
    assert "docs.flutter.dev" in content or "flutter" in content.lower(), \
        "Prompt must include example links"
    assert "linear.app" in content or "github.com" in content, \
        "Prompt must include example links from issue trackers"


# [pr_diff] fail_to_pass
def test_prompt_conditional_links_omission():
    """Prompt must instruct to omit the Links section when no URLs are found."""
    prompt_file = Path(REPO) / "lib/features/ai/util/preconfigured_prompts.dart"
    content = prompt_file.read_text()

    assert "omit" in content.lower() and "links section" in content.lower(), \
        "Prompt must instruct to omit Links section when no links found"
    assert "no links are found" in content.lower() or "no urls" in content.lower(), \
        "Prompt must specify the condition for omitting the Links section"


# [pr_diff] fail_to_pass
def test_prompt_unique_urls():
    """Prompt must instruct to extract unique URLs (deduplicate)."""
    prompt_file = Path(REPO) / "lib/features/ai/util/preconfigured_prompts.dart"
    content = prompt_file.read_text()

    assert "unique" in content.lower() and "url" in content.lower(), \
        "Prompt must instruct to extract unique URLs"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — UI link handling tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_expandable_summary_link_handling():
    """Expandable AI response summary must handle link taps and build custom links."""
    src = Path(REPO) / "lib/features/ai/ui/expandable_ai_response_summary.dart"
    content = src.read_text()

    # Must import url_launcher
    assert "url_launcher" in content, \
        "expandable_ai_response_summary.dart must import url_launcher"
    # Must have link tap handler
    assert "_handleLinkTap" in content, \
        "Must have _handleLinkTap method"
    # Must pass onLinkTap to GptMarkdown
    assert "onLinkTap" in content, \
        "Must pass onLinkTap callback to GptMarkdown"
    # Must have a custom link builder
    assert "linkBuilder" in content or "_buildLink" in content, \
        "Must have a custom link builder"


# [pr_diff] fail_to_pass
def test_summary_widgets_handle_link_taps():
    """Both ai_response_summary.dart and modal must handle link taps."""
    for filename in [
        "lib/features/ai/ui/ai_response_summary.dart",
        "lib/features/ai/ui/ai_response_summary_modal.dart",
    ]:
        src = Path(REPO) / filename
        content = src.read_text()
        assert "url_launcher" in content, \
            f"{filename} must import url_launcher"
        assert "_handleLinkTap" in content, \
            f"{filename} must have _handleLinkTap"
        assert "onLinkTap" in content, \
            f"{filename} must pass onLinkTap to GptMarkdown"


# [pr_diff] fail_to_pass
def test_theme_link_color():
    """Theme must set linkColor for GptMarkdownThemeData."""
    theme = Path(REPO) / "lib/themes/theme.dart"
    content = theme.read_text()

    assert "linkColor" in content, \
        "theme.dart must set linkColor in GptMarkdownThemeData"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must have a section about link extraction
    assert re.search(r"(?i)automatic\s+link\s+extraction", content), \
        "README must have an 'Automatic Link Extraction' section"
    # Must describe what the feature does
    assert "url" in content.lower() or "URL" in content, \
        "README must mention URLs in the link extraction section"
    assert "unique" in content.lower(), \
        "README must mention extracting unique URLs"


# [config_edit] fail_to_pass

    # Must describe the Markdown link format
    assert "[Succinct Title](URL)" in content or "Markdown" in content, \
        "README must describe Markdown link format"
    # Must describe scanning behavior
    assert "scan" in content.lower(), \
        "README must describe scanning log entries for URLs"
    # Must describe conditional display (omit when no URLs)
    assert "omit" in content.lower() or "conditional" in content.lower(), \
        "README must describe conditional display of the Links section"
    # Must describe succinct titles
    assert "succinct" in content.lower() or "descriptive title" in content.lower(), \
        "README must describe generating succinct titles for links"


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — AGENTS.md rule compliance
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass
