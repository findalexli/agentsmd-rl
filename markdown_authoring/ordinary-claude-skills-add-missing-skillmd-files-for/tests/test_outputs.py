"""Behavioral checks for ordinary-claude-skills-add-missing-skillmd-files-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ordinary-claude-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('algorithmic-art/SKILL.md')
    assert 'Algorithmic expression: Flow fields driven by layered Perlin noise. Thousands of particles following vector forces, their trails accumulating into organic density maps. Multiple noise octaves create t' in text, "expected to find: " + 'Algorithmic expression: Flow fields driven by layered Perlin noise. Thousands of particles following vector forces, their trails accumulating into organic density maps. Multiple noise octaves create t'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('algorithmic-art/SKILL.md')
    assert 'The concept is a **subtle, niche reference embedded within the algorithm itself** - not always literal, always sophisticated. Someone familiar with the subject should feel it intuitively, while others' in text, "expected to find: " + 'The concept is a **subtle, niche reference embedded within the algorithm itself** - not always literal, always sophisticated. Someone familiar with the subject should feel it intuitively, while others'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('algorithmic-art/SKILL.md')
    assert '- **Emphasize craftsmanship REPEATEDLY**: The philosophy MUST stress multiple times that the final algorithm should appear as though it took countless hours to develop, was refined with care, and come' in text, "expected to find: " + '- **Emphasize craftsmanship REPEATEDLY**: The philosophy MUST stress multiple times that the final algorithm should appear as though it took countless hours to develop, was refined with care, and come'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('artifacts-builder/SKILL.md')
    assert 'To test/visualize the artifact, use available tools (including other Skills or built-in tools like Playwright or Puppeteer). In general, avoid testing the artifact upfront as it adds latency between t' in text, "expected to find: " + 'To test/visualize the artifact, use available tools (including other Skills or built-in tools like Playwright or Puppeteer). In general, avoid testing the artifact upfront as it adds latency between t'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('artifacts-builder/SKILL.md')
    assert 'description: Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui). Use for complex artifacts requirin' in text, "expected to find: " + 'description: Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui). Use for complex artifacts requirin'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('artifacts-builder/SKILL.md')
    assert 'This creates `bundle.html` - a self-contained artifact with all JavaScript, CSS, and dependencies inlined. This file can be directly shared in Claude conversations as an artifact.' in text, "expected to find: " + 'This creates `bundle.html` - a self-contained artifact with all JavaScript, CSS, and dependencies inlined. This file can be directly shared in Claude conversations as an artifact.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('brand-guidelines/SKILL.md')
    assert "description: Applies Anthropic's official brand colors and typography to any sort of artifact that may benefit from having Anthropic's look-and-feel. Use it when brand colors or style guidelines, visu" in text, "expected to find: " + "description: Applies Anthropic's official brand colors and typography to any sort of artifact that may benefit from having Anthropic's look-and-feel. Use it when brand colors or style guidelines, visu"[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('brand-guidelines/SKILL.md')
    assert '**Keywords**: branding, corporate identity, visual identity, post-processing, styling, brand colors, typography, Anthropic brand, visual formatting, visual design' in text, "expected to find: " + '**Keywords**: branding, corporate identity, visual identity, post-processing, styling, brand colors, typography, Anthropic brand, visual formatting, visual design'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('brand-guidelines/SKILL.md')
    assert "To access Anthropic's official brand identity and style resources, use this skill." in text, "expected to find: " + "To access Anthropic's official brand identity and style resources, use this skill."[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('canvas-design/SKILL.md')
    assert 'To create museum or magazine quality work, use the design philosophy as the foundation. Create one single page, highly visual, design-forward PDF or PNG output (unless asked for more pages). Generally' in text, "expected to find: " + 'To create museum or magazine quality work, use the design philosophy as the foundation. Create one single page, highly visual, design-forward PDF or PNG output (unless asked for more pages). Generally'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('canvas-design/SKILL.md')
    assert '**Text as a contextual element**: Text is always minimal and visual-first, but let context guide whether that means whisper-quiet labels or bold typographic gestures. A punk venue poster might have la' in text, "expected to find: " + '**Text as a contextual element**: Text is always minimal and visual-first, but let context guide whether that means whisper-quiet labels or bold typographic gestures. A punk venue poster might have la'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('canvas-design/SKILL.md')
    assert '**CRITICAL**: To achieve human-crafted quality (not AI-generated), create work that looks like it took countless hours. Make it appear as though someone at the absolute top of their field labored over' in text, "expected to find: " + '**CRITICAL**: To achieve human-crafted quality (not AI-generated), create work that looks like it took countless hours. Make it appear as though someone at the absolute top of their field labored over'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('docx/SKILL.md')
    assert 'description: "Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction. When Claude needs to work with profession' in text, "expected to find: " + 'description: "Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction. When Claude needs to work with profession'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('docx/SKILL.md')
    assert 'When implementing tracked changes, only mark text that actually changes. Repeating unchanged text makes edits harder to review and appears unprofessional. Break replacements into: [unchanged text] + [' in text, "expected to find: " + 'When implementing tracked changes, only mark text that actually changes. Repeating unchanged text makes edits harder to review and appears unprofessional. Break replacements into: [unchanged text] + ['[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('docx/SKILL.md')
    assert '1. **MANDATORY - READ ENTIRE FILE**: Read [`docx-js.md`](docx-js.md) (~500 lines) completely from start to finish. **NEVER set any range limits when reading this file.** Read the full file content for' in text, "expected to find: " + '1. **MANDATORY - READ ENTIRE FILE**: Read [`docx-js.md`](docx-js.md) (~500 lines) completely from start to finish. **NEVER set any range limits when reading this file.** Read the full file content for'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('internal-comms/SKILL.md')
    assert 'description: A set of resources to help me write all kinds of internal communications, using the formats that my company likes to use. Claude should use this skill whenever asked to write some sort of' in text, "expected to find: " + 'description: A set of resources to help me write all kinds of internal communications, using the formats that my company likes to use. Claude should use this skill whenever asked to write some sort of'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('internal-comms/SKILL.md')
    assert "If the communication type doesn't match any existing guideline, ask for clarification or more context about the desired format." in text, "expected to find: " + "If the communication type doesn't match any existing guideline, ask for clarification or more context about the desired format."[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('internal-comms/SKILL.md')
    assert '3P updates, company newsletter, company comms, weekly update, faqs, common questions, updates, internal comms' in text, "expected to find: " + '3P updates, company newsletter, company comms, weekly update, faqs, common questions, updates, internal comms'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('mcp-builder/SKILL.md')
    assert 'Balance comprehensive API endpoint coverage with specialized workflow tools. Workflow tools can be more convenient for specific tasks, while comprehensive coverage gives agents flexibility to compose ' in text, "expected to find: " + 'Balance comprehensive API endpoint coverage with specialized workflow tools. Workflow tools can be more convenient for specific tasks, while comprehensive coverage gives agents flexibility to compose '[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('mcp-builder/SKILL.md')
    assert 'description: Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to inte' in text, "expected to find: " + 'description: Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to inte'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('mcp-builder/SKILL.md')
    assert '- **Language**: TypeScript (high-quality SDK support and good compatibility in many execution environments e.g. MCPB. Plus AI models are good at generating TypeScript code, benefiting from its broad u' in text, "expected to find: " + '- **Language**: TypeScript (high-quality SDK support and good compatibility in many execution environments e.g. MCPB. Plus AI models are good at generating TypeScript code, benefiting from its broad u'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('pdf/SKILL.md')
    assert 'description: Comprehensive PDF manipulation toolkit for extracting text and tables, creating new PDFs, merging/splitting documents, and handling forms. When Claude needs to fill in a PDF form or progr' in text, "expected to find: " + 'description: Comprehensive PDF manipulation toolkit for extracting text and tables, creating new PDFs, merging/splitting documents, and handling forms. When Claude needs to fill in a PDF form or progr'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('pdf/SKILL.md')
    assert 'This guide covers essential PDF processing operations using Python libraries and command-line tools. For advanced features, JavaScript libraries, and detailed examples, see reference.md. If you need t' in text, "expected to find: " + 'This guide covers essential PDF processing operations using Python libraries and command-line tools. For advanced features, JavaScript libraries, and detailed examples, see reference.md. If you need t'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('pdf/SKILL.md')
    assert '# This extracts all images as output_prefix-000.jpg, output_prefix-001.jpg, etc.' in text, "expected to find: " + '# This extracts all images as output_prefix-000.jpg, output_prefix-001.jpg, etc.'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('pptx/SKILL.md')
    assert '- **Two-column layout (PREFERRED)**: Use a header spanning the full width, then two columns below - text/bullets in one column and the featured content in the other. This provides better balance and m' in text, "expected to find: " + '- **Two-column layout (PREFERRED)**: Use a header spanning the full width, then two columns below - text/bullets in one column and the featured content in the other. This provides better balance and m'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('pptx/SKILL.md')
    assert '1. **MANDATORY - READ ENTIRE FILE**: Read [`html2pptx.md`](html2pptx.md) completely from start to finish. **NEVER set any range limits when reading this file.** Read the full file content for detailed' in text, "expected to find: " + '1. **MANDATORY - READ ENTIRE FILE**: Read [`html2pptx.md`](html2pptx.md) completely from start to finish. **NEVER set any range limits when reading this file.** Read the full file content for detailed'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('pptx/SKILL.md')
    assert '1. **MANDATORY - READ ENTIRE FILE**: Read [`ooxml.md`](ooxml.md) (~500 lines) completely from start to finish.  **NEVER set any range limits when reading this file.**  Read the full file content for d' in text, "expected to find: " + '1. **MANDATORY - READ ENTIRE FILE**: Read [`ooxml.md`](ooxml.md) (~500 lines) completely from start to finish.  **NEVER set any range limits when reading this file.**  Read the full file content for d'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('skill-creator/SKILL.md')
    assert "- **Avoid duplication**: Information should live in either SKILL.md or references files, not both. Prefer references files for detailed information unless it's truly core to the skill—this keeps SKILL" in text, "expected to find: " + "- **Avoid duplication**: Information should live in either SKILL.md or references files, not both. Prefer references files for detailed information unless it's truly core to the skill—this keeps SKILL"[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('skill-creator/SKILL.md')
    assert '- Example description for a `docx` skill: "Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction. Use when Cla' in text, "expected to find: " + '- Example description for a `docx` skill: "Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction. Use when Cla'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('skill-creator/SKILL.md')
    assert 'When editing the (newly-generated or existing) skill, remember that the skill is being created for another instance of Claude to use. Include information that would be beneficial and non-obvious to Cl' in text, "expected to find: " + 'When editing the (newly-generated or existing) skill, remember that the skill is being created for another instance of Claude to use. Include information that would be beneficial and non-obvious to Cl'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('slack-gif-creator/SKILL.md')
    assert 'description: Knowledge and utilities for creating animated GIFs optimized for Slack. Provides constraints, validation tools, and animation concepts. Use when users request animated GIFs for Slack like' in text, "expected to find: " + 'description: Knowledge and utilities for creating animated GIFs optimized for Slack. Provides constraints, validation tools, and animation concepts. Use when users request animated GIFs for Slack like'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('slack-gif-creator/SKILL.md')
    assert "**Note on user uploads**: This skill doesn't include pre-built graphics, but if a user uploads an image, use PIL to load and work with it - interpret based on their request whether they want it used d" in text, "expected to find: " + "**Note on user uploads**: This skill doesn't include pre-built graphics, but if a user uploads an image, use PIL to load and work with it - interpret based on their request whether they want it used d"[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('slack-gif-creator/SKILL.md')
    assert '**Use thicker lines** - Always set `width=2` or higher for outlines and lines. Thin lines (width=1) look choppy and amateurish.' in text, "expected to find: " + '**Use thicker lines** - Always set `width=2` or higher for outlines and lines. Thin lines (width=1) look choppy and amateurish.'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('template-skill/SKILL.md')
    assert 'description: Replace with description of the skill and when Claude should use it.' in text, "expected to find: " + 'description: Replace with description of the skill and when Claude should use it.'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('template-skill/SKILL.md')
    assert '# Insert instructions below' in text, "expected to find: " + '# Insert instructions below'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('template-skill/SKILL.md')
    assert 'name: template-skill' in text, "expected to find: " + 'name: template-skill'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('theme-factory/SKILL.md')
    assert 'To handle cases where none of the existing themes work for an artifact, create a custom theme. Based on provided inputs, generate a new theme similar to the ones above. Give the theme a similar name d' in text, "expected to find: " + 'To handle cases where none of the existing themes work for an artifact, create a custom theme. Based on provided inputs, generate a new theme similar to the ones above. Give the theme a similar name d'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('theme-factory/SKILL.md')
    assert 'description: Toolkit for styling artifacts with a theme. These artifacts can be slides, docs, reportings, HTML landing pages, etc. There are 10 pre-set themes with colors/fonts that you can apply to a' in text, "expected to find: " + 'description: Toolkit for styling artifacts with a theme. These artifacts can be slides, docs, reportings, HTML landing pages, etc. There are 10 pre-set themes with colors/fonts that you can apply to a'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('theme-factory/SKILL.md')
    assert 'This skill provides a curated collection of professional font and color themes themes, each with carefully selected color palettes and font pairings. Once a theme is chosen, it can be applied to any a' in text, "expected to find: " + 'This skill provides a curated collection of professional font and color themes themes, each with carefully selected color palettes and font pairings. Once a theme is chosen, it can be applied to any a'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('webapp-testing/SKILL.md')
    assert '**Always run scripts with `--help` first** to see usage. DO NOT read the source until you try running the script first and find that a customized solution is abslutely necessary. These scripts can be ' in text, "expected to find: " + '**Always run scripts with `--help` first** to see usage. DO NOT read the source until you try running the script first and find that a customized solution is abslutely necessary. These scripts can be '[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('webapp-testing/SKILL.md')
    assert '- **Use bundled scripts as black boxes** - To accomplish a task, consider whether one of the scripts available in `scripts/` can help. These scripts handle common, complex workflows reliably without c' in text, "expected to find: " + '- **Use bundled scripts as black boxes** - To accomplish a task, consider whether one of the scripts available in `scripts/` can help. These scripts handle common, complex workflows reliably without c'[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('webapp-testing/SKILL.md')
    assert 'description: Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and view' in text, "expected to find: " + 'description: Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and view'[:80]


def test_signal_42():
    """Distinctive line from gold patch must be present."""
    text = _read('xlsx/SKILL.md')
    assert 'description: "Comprehensive spreadsheet creation, editing, and analysis with support for formulas, formatting, data analysis, and visualization. When Claude needs to work with spreadsheets (.xlsx, .xl' in text, "expected to find: " + 'description: "Comprehensive spreadsheet creation, editing, and analysis with support for formulas, formatting, data analysis, and visualization. When Claude needs to work with spreadsheets (.xlsx, .xl'[:80]


def test_signal_43():
    """Distinctive line from gold patch must be present."""
    text = _read('xlsx/SKILL.md')
    assert '**LibreOffice Required for Formula Recalculation**: You can assume LibreOffice is installed for recalculating formula values using the `recalc.py` script. The script automatically configures LibreOffi' in text, "expected to find: " + '**LibreOffice Required for Formula Recalculation**: You can assume LibreOffice is installed for recalculating formula values using the `recalc.py` script. The script automatically configures LibreOffi'[:80]


def test_signal_44():
    """Distinctive line from gold patch must be present."""
    text = _read('xlsx/SKILL.md')
    assert 'Excel files created or modified by openpyxl contain formulas as strings but not calculated values. Use the provided `recalc.py` script to recalculate formulas:' in text, "expected to find: " + 'Excel files created or modified by openpyxl contain formulas as strings but not calculated values. Use the provided `recalc.py` script to recalculate formulas:'[:80]

