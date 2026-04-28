"""Behavioral checks for the ant-design create-pr skill markdown refresh.

The PR (#57559) replaces phrase-based triggering of the create-pr skill with
intent-based triggering. The agent must edit `.agents/skills/create-pr/SKILL.md`
to:

  * rewrite the YAML-frontmatter `description` so it directs the assistant to
    judge by intent rather than fixed phrases;
  * delete the entire `## 触发场景` section and its hard-coded trigger phrases;
  * add a new `### 一、按意图触发，不按短语触发` subsection at the top of
    `## 基本规则`;
  * renumber the existing six rules (一-六) to (二-七).

These checks read the file and assert on its concrete contents. A subprocess
check verifies that the file is still a valid markdown document with parseable
YAML frontmatter, so a malformed file fails loudly.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path("/workspace/ant-design")
SKILL_FILE = REPO / ".agents/skills/create-pr/SKILL.md"


def _read_skill() -> str:
    assert SKILL_FILE.is_file(), f"{SKILL_FILE} is missing"
    return SKILL_FILE.read_text(encoding="utf-8")


def _frontmatter(text: str) -> str:
    lines = text.splitlines()
    assert lines and lines[0].strip() == "---", "SKILL.md must start with YAML frontmatter"
    end = next(
        (i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---"),
        None,
    )
    assert end is not None, "YAML frontmatter has no closing '---'"
    return "\n".join(lines[1:end])


# --- fail-to-pass ----------------------------------------------------------


def test_description_uses_intent_phrasing():
    """Frontmatter description must direct the assistant to judge by intent."""
    fm = _frontmatter(_read_skill())
    assert "Judge by intent rather than fixed phrases" in fm, (
        "Frontmatter description must contain the literal phrase "
        "'Judge by intent rather than fixed phrases'."
    )


def test_old_description_phrasing_removed():
    """The old phrase-list-style description wording must be gone."""
    fm = _frontmatter(_read_skill())
    forbidden = (
        "Use when the user asks to create a PR, open a pull request, "
        "write PR title/body, summarize branch changes for a PR, or "
        "prepare an ant-design PR in Chinese or English"
    )
    assert forbidden not in fm, (
        "Old description still lists specific trigger situations verbatim. "
        "It must be rewritten to focus on intent."
    )


def test_trigger_section_heading_removed():
    """The whole '## 触发场景' section must be deleted."""
    text = _read_skill()
    assert "## 触发场景" not in text, (
        "The '## 触发场景' section must be removed in favor of intent-based "
        "triggering rules."
    )


def test_old_trigger_phrase_list_removed():
    """The hard-coded list of Chinese/English trigger phrases must be removed."""
    text = _read_skill()
    forbidden_lines = [
        "创建 PR、发起 pull request",
        "`帮我提个pr`",
        "`help me create a pr`",
        "这类短句默认表示",
    ]
    leftovers = [s for s in forbidden_lines if s in text]
    assert not leftovers, (
        "These fragments from the old phrase-based trigger list are still "
        f"present and must be removed: {leftovers}"
    )


def test_intent_section_added():
    """A new '### 一、按意图触发，不按短语触发' subsection must be added."""
    text = _read_skill()
    assert "### 一、按意图触发，不按短语触发" in text, (
        "Missing new subsection heading '### 一、按意图触发，不按短语触发' "
        "at the top of '## 基本规则'."
    )


def test_intent_section_explains_intent():
    """The new section must explain intent-based triggering, not list phrases."""
    text = _read_skill()
    assert "只要能判断用户是在请求创建 PR" in text, (
        "New '一、按意图触发' section must explain that the skill should be "
        "used whenever the user's intent is to create a PR."
    )
    assert "不要把触发限制成固定说法" in text, (
        "New '一、按意图触发' section must instruct not to limit triggering "
        "to fixed phrases."
    )


def test_rules_renumbered_to_two_through_seven():
    """The six original rules must be renumbered from 一-六 to 二-七."""
    text = _read_skill()
    expected = [
        "### 二、必须以仓库模板为准",
        "### 三、模板语言由用户习惯决定，但标题固定英文",
        "### 四、先分析分支，再写 PR",
        "### 五、先给草稿，后创建 PR",
        "### 六、标题和正文要分工明确",
        "### 七、信息不足时不要硬写",
    ]
    missing = [h for h in expected if h not in text]
    assert not missing, f"Missing renumbered rule headings: {missing}"


def test_old_rule_numbering_replaced():
    """The pre-PR rule headings (numbered 一-六) must no longer appear."""
    text = _read_skill()
    stale = [
        "### 一、必须以仓库模板为准",
        "### 二、模板语言由用户习惯决定，但标题固定英文",
        "### 三、先分析分支，再写 PR",
        "### 四、先给草稿，后创建 PR",
        "### 五、标题和正文要分工明确",
        "### 六、信息不足时不要硬写",
    ]
    leftovers = [h for h in stale if h in text]
    assert not leftovers, (
        "These pre-PR rule headings must be renumbered (or deleted): "
        f"{leftovers}"
    )


# --- pass-to-pass / structural --------------------------------------------


def test_skill_md_yaml_frontmatter_valid():
    """The file's YAML frontmatter must still parse cleanly via PyYAML.

    Runs the parser in a subprocess so a syntactically broken edit fails the
    test (rather than crashing the test runner).
    """
    script = (
        "import sys, yaml\n"
        "with open(r'%s', encoding='utf-8') as f:\n"
        "    text = f.read()\n"
        "lines = text.splitlines()\n"
        "assert lines[0].strip() == '---'\n"
        "end = next(i for i, line in enumerate(lines[1:], start=1) "
        "if line.strip() == '---')\n"
        "data = yaml.safe_load('\\n'.join(lines[1:end])) or {}\n"
        "assert data.get('name') == 'antd-create-pr', data\n"
        "assert isinstance(data.get('description', ''), str)\n"
        "assert len(data['description']) > 50, len(data['description'])\n"
        "print('ok')\n" % str(SKILL_FILE)
    )
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"Frontmatter parse failed:\nstdout={result.stdout}\nstderr={result.stderr}"
    )
    assert "ok" in result.stdout


def test_skill_md_basic_structure_preserved():
    """Top-level Chinese H1 and the four-line objectives section must remain."""
    text = _read_skill()
    assert "# Ant Design PR 创建规范" in text, "Top-level H1 missing"
    assert "## 目标" in text, "## 目标 section missing"
    assert "## 基本规则" in text, "## 基本规则 section missing"
    assert "## 执行步骤" in text, "## 执行步骤 section missing"
    assert "## 写法要求" in text, "## 写法要求 section missing"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_build():
    """pass_to_pass | CI job 'build' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", 'ut build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_lib_es_module_compile():
    """pass_to_pass | CI job 'test lib/es module' → step 'compile'"""
    r = subprocess.run(
        ["bash", "-lc", 'ut compile'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'compile' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")