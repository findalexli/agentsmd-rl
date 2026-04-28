"""Behavioral checks for antigravity-awesome-skills-feat-add-axiom-firstprinciples-as (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/axiom/SKILL.md')
    assert 'description: "First-principles assumption auditor. Classifies each hidden assumption (fact / convention / belief / interest-driven), ranks by fragility × impact, and rebuilds conclusions from verified' in text, "expected to find: " + 'description: "First-principles assumption auditor. Classifies each hidden assumption (fact / convention / belief / interest-driven), ranks by fragility × impact, and rebuilds conclusions from verified'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/axiom/SKILL.md')
    assert "| ✅ **Devil's advocate persistence** | If the user rejects a classification or pushback, hold firm like a devil's advocate. Only yield when the user provides verifiable evidence (not feelings, not app" in text, "expected to find: " + "| ✅ **Devil's advocate persistence** | If the user rejects a classification or pushback, hold firm like a devil's advocate. Only yield when the user provides verifiable evidence (not feelings, not app"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/axiom/SKILL.md')
    assert '- If the rebuilt conclusion is identical to the original, explain WHY — the analysis must demonstrate that either a genuine shift occurred, or provide specific reasons why the original reasoning was a' in text, "expected to find: " + '- If the rebuilt conclusion is identical to the original, explain WHY — the analysis must demonstrate that either a genuine shift occurred, or provide specific reasons why the original reasoning was a'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/axiom/examples/walkthrough-en.md')
    assert "A3 has the highest risk score. The equity you're being offered is almost certainly worth $0 right now. Over 90% of startups fail, and even among those that succeed, early-employee equity is often dilu" in text, "expected to find: " + "A3 has the highest risk score. The equity you're being offered is almost certainly worth $0 right now. Over 90% of startups fail, and even among those that succeed, early-employee equity is often dilu"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/axiom/examples/walkthrough-en.md')
    assert '**Rebuilt thinking:** "I should complete concrete due diligence on the startup (financials, founder track record, equity terms reviewed by a lawyer) before making any decision. In parallel, I should e' in text, "expected to find: " + '**Rebuilt thinking:** "I should complete concrete due diligence on the startup (financials, founder track record, equity terms reviewed by a lawyer) before making any decision. In parallel, I should e'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/axiom/examples/walkthrough-en.md')
    assert '> "Given my current skills, financial situation, and risk tolerance, is joining this specific startup now — at the cost of delaying/abandoning my degree — a better path to my goals than completing the' in text, "expected to find: " + '> "Given my current skills, financial situation, and risk tolerance, is joining this specific startup now — at the cost of delaying/abandoning my degree — a better path to my goals than completing the'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/axiom/examples/walkthrough-zh.md')
    assert 'A4 的危险值最高。绝大多数创业失败不是因为执行力差，而是因为**从一开始就在解决一个没人愿意付费的问题**。如果你还没有哪怕一个愿意付费的用户或企业，你所有关于"市场足够大""我的想法够好"的假设都建立在空气上。' in text, "expected to find: " + 'A4 的危险值最高。绝大多数创业失败不是因为执行力差，而是因为**从一开始就在解决一个没人愿意付费的问题**。如果你还没有哪怕一个愿意付费的用户或企业，你所有关于"市场足够大""我的想法够好"的假设都建立在空气上。'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/axiom/examples/walkthrough-zh.md')
    assert '| 🟡 3 | A5：失败了可以重来（风险可控） | 4 | 3 | **12** | 具体的"可以重来"是什么意思？你的年龄/负债/家庭状况下，失败的实际成本是多少？ |' in text, "expected to find: " + '| 🟡 3 | A5：失败了可以重来（风险可控） | 4 | 3 | **12** | 具体的"可以重来"是什么意思？你的年龄/负债/家庭状况下，失败的实际成本是多少？ |'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/axiom/examples/walkthrough-zh.md')
    assert '| 🔴 1 | A4：我的想法有足够的市场需求 | 4 | 5 | **20** | 你有多少个付费用户或LOI（意向书）？如果答案是0，这是最脆弱也最致命的假设 |' in text, "expected to find: " + '| 🔴 1 | A4：我的想法有足够的市场需求 | 4 | 5 | **20** | 你有多少个付费用户或LOI（意向书）？如果答案是0，这是最脆弱也最致命的假设 |'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/axiom/references/assumption-types.md')
    assert "Assumptions that someone (an industry, company, influencer, or social group) actively propagates because they benefit from you believing them. This doesn't mean the claim is always false — but its tru" in text, "expected to find: " + "Assumptions that someone (an industry, company, influencer, or social group) actively propagates because they benefit from you believing them. This doesn't mean the claim is always false — but its tru"[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/axiom/references/assumption-types.md')
    assert '**Check the timestamp.** Ask: "Was this true 20 years ago? Is it still true now? Will it be true in 10 years?" The key insight is that conventions carry enormous inertia — people follow them long afte' in text, "expected to find: " + '**Check the timestamp.** Ask: "Was this true 20 years ago? Is it still true now? Will it be true in 10 years?" The key insight is that conventions carry enormous inertia — people follow them long afte'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/axiom/references/assumption-types.md')
    assert 'A detailed reference for the 4-type assumption classification system used in Axiom Phase 3. This handbook provides identification methods, challenge strategies, real-world examples, and edge-case guid' in text, "expected to find: " + 'A detailed reference for the 4-type assumption classification system used in Axiom Phase 3. This handbook provides identification methods, challenge strategies, real-world examples, and edge-case guid'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/axiom/references/scenarios.md')
    assert 'This file provides structured mining checklists for 8 common scenario types (4 Chinese-native + 4 English-native). Each checklist contains **high-frequency hidden assumptions** that people in those si' in text, "expected to find: " + 'This file provides structured mining checklists for 8 common scenario types (4 Chinese-native + 4 English-native). Each checklist contains **high-frequency hidden assumptions** that people in those si'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/axiom/references/scenarios.md')
    assert '3. **Prioritize culturally-specific assumptions** — a Chinese user asking about career decisions will have very different hidden assumptions than an American user' in text, "expected to find: " + '3. **Prioritize culturally-specific assumptions** — a Chinese user asking about career decisions will have very different hidden assumptions than an American user'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/axiom/references/scenarios.md')
    assert "When a user's question matches a scenario type, use the corresponding checklist to ensure your Phase 2 (Assumption Mining) is thorough and culturally relevant." in text, "expected to find: " + "When a user's question matches a scenario type, use the corresponding checklist to ensure your Phase 2 (Assumption Mining) is thorough and culturally relevant."[:80]

