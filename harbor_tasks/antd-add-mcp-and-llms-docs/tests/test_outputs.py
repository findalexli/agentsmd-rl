"""Verifier tests for ant-design PR #57226 (markdown_authoring task).

Track 1 (this file) is a structural sanity gate — it greps for distinctive
signal lines from the gold markdown.  Track 2 (Gemini judge, eval_manifest
config_edits) does the semantic-diff scoring.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path("/workspace/antd")
CLAUDE_MD = REPO / "CLAUDE.md"
LLMS_EN = REPO / "docs" / "react" / "llms.en-US.md"
LLMS_ZH = REPO / "docs" / "react" / "llms.zh-CN.md"
MCP_EN = REPO / "docs" / "react" / "mcp.en-US.md"
MCP_ZH = REPO / "docs" / "react" / "mcp.zh-CN.md"


def _read(path: Path) -> str:
    assert path.exists(), f"Missing file: {path}"
    return path.read_text(encoding="utf-8")


def test_repo_present():
    """Sanity: the cloned ant-design repo is at the expected base commit."""
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"git rev-parse failed:\n{r.stderr}"
    head = r.stdout.strip()
    assert head == "9a3dccf2d4be0f2a271c5a047b7056cf2e429af1", (
        f"Unexpected HEAD: {head}"
    )


def test_claude_md_newline_rule():
    """CLAUDE.md must declare the rule that every file ends with a newline.

    Fail-to-pass: the rule is added by PR #57226.
    """
    content = _read(CLAUDE_MD)
    assert "所有文件必须以换行符结尾" in content, (
        "CLAUDE.md is missing the newline-EOF rule. "
        "Expected the literal phrase '所有文件必须以换行符结尾' in the "
        "core conventions section."
    )
    assert "final-newline" in content, (
        "CLAUDE.md should reference the `final-newline` lint warning that "
        "this rule prevents."
    )


def test_claude_md_file_ends_with_newline():
    """The CLAUDE.md file itself ends with a newline (eats its own dogfood)."""
    raw = CLAUDE_MD.read_bytes()
    assert raw.endswith(b"\n"), "CLAUDE.md does not end with a newline."


def test_mcp_en_doc_created():
    """English MCP doc page exists with correct frontmatter and core sections."""
    content = _read(MCP_EN)
    assert "title: MCP Server" in content, (
        "mcp.en-US.md frontmatter must declare 'title: MCP Server'."
    )
    assert "tag: New" in content, (
        "mcp.en-US.md frontmatter must include 'tag: New'."
    )
    assert "## What is MCP?" in content, (
        "mcp.en-US.md must contain a '## What is MCP?' section."
    )
    assert "@jzone-mcp/antd-components-mcp" in content, (
        "mcp.en-US.md must reference the recommended community MCP server "
        "package '@jzone-mcp/antd-components-mcp'."
    )
    assert "modelcontextprotocol.io" in content, (
        "mcp.en-US.md must link to the upstream MCP protocol documentation "
        "at modelcontextprotocol.io."
    )


def test_mcp_zh_doc_created():
    """Chinese MCP doc page exists and matches the structure of the English doc."""
    content = _read(MCP_ZH)
    assert "title: MCP Server" in content, (
        "mcp.zh-CN.md frontmatter must declare 'title: MCP Server'."
    )
    assert "什么是 MCP" in content, (
        "mcp.zh-CN.md must contain a '什么是 MCP' section."
    )
    assert "@jzone-mcp/antd-components-mcp" in content, (
        "mcp.zh-CN.md must reference the community MCP server package."
    )


def test_llms_en_aggregated_files_table():
    """English LLMs.txt guide must list the new aggregated files."""
    content = _read(LLMS_EN)
    # The new aggregated-files section adds three additional resources.
    assert "llms-full-cn.txt" in content, (
        "llms.en-US.md must list the Chinese full-documentation aggregate "
        "file (llms-full-cn.txt)."
    )
    assert "llms-semantic.md" in content, (
        "llms.en-US.md must list the semantic documentation aggregate "
        "file (llms-semantic.md)."
    )
    assert "llms-semantic-cn.md" in content, (
        "llms.en-US.md must list the Chinese semantic aggregate "
        "(llms-semantic-cn.md)."
    )


def test_llms_en_tools_table_includes_new_entries():
    """English LLMs.txt usage section must include Codex and Neovate Code."""
    content = _read(LLMS_EN)
    assert "Codex" in content, (
        "llms.en-US.md usage section must include a Codex tool entry."
    )
    assert "Neovate Code" in content, (
        "llms.en-US.md usage section must include a Neovate Code tool entry."
    )


def test_llms_zh_aggregated_files_table():
    """Chinese LLMs.txt guide must list the new aggregated files."""
    content = _read(LLMS_ZH)
    assert "llms-full-cn.txt" in content
    assert "llms-semantic.md" in content
    assert "llms-semantic-cn.md" in content


def test_llms_zh_tools_table_includes_new_entries():
    """Chinese LLMs.txt usage table must include Codex and Neovate Code."""
    content = _read(LLMS_ZH)
    assert "Codex" in content
    assert "Neovate Code" in content


def test_all_changed_files_end_with_newline():
    """Per the new CLAUDE.md rule, every touched markdown file ends with \\n."""
    for path in (CLAUDE_MD, LLMS_EN, LLMS_ZH, MCP_EN, MCP_ZH):
        raw = path.read_bytes()
        assert raw.endswith(b"\n"), (
            f"{path.relative_to(REPO)} does not end with a newline, "
            f"violating the project's final-newline rule."
        )
