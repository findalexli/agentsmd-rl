#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "description: \"First-principles assumption auditor. Classifies each hidden assump" "skills/axiom/SKILL.md" && grep -qF "A3 has the highest risk score. The equity you're being offered is almost certain" "skills/axiom/examples/walkthrough-en.md" && grep -qF "A4 \u7684\u5371\u9669\u503c\u6700\u9ad8\u3002\u7edd\u5927\u591a\u6570\u521b\u4e1a\u5931\u8d25\u4e0d\u662f\u56e0\u4e3a\u6267\u884c\u529b\u5dee\uff0c\u800c\u662f\u56e0\u4e3a**\u4ece\u4e00\u5f00\u59cb\u5c31\u5728\u89e3\u51b3\u4e00\u4e2a\u6ca1\u4eba\u613f\u610f\u4ed8\u8d39\u7684\u95ee\u9898**\u3002\u5982\u679c\u4f60\u8fd8\u6ca1\u6709\u54ea\u6015\u4e00\u4e2a\u613f\u610f\u4ed8\u8d39\u7684\u7528\u6237\u6216\u4f01\u4e1a\uff0c\u4f60\u6240\u6709\u5173" "skills/axiom/examples/walkthrough-zh.md" && grep -qF "Assumptions that someone (an industry, company, influencer, or social group) act" "skills/axiom/references/assumption-types.md" && grep -qF "This file provides structured mining checklists for 8 common scenario types (4 C" "skills/axiom/references/scenarios.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/axiom/SKILL.md b/skills/axiom/SKILL.md
@@ -0,0 +1,255 @@
+---
+name: axiom
+description: "First-principles assumption auditor. Classifies each hidden assumption (fact / convention / belief / interest-driven), ranks by fragility × impact, and rebuilds conclusions from verified premises. Bilingual: auto-detects Chinese or English."
+risk: safe
+source: community
+date_added: "2026-04-13"
+---
+
+# Axiom — First-Principles Assumption Auditor / 第一性原理拆解器
+
+Strip any question down to its irreducible truths, then rebuild from there.
+This is not framework fill-in-the-blank — it is assumption prosecution.
+
+把任何问题强制剥离到"不可再拆的最小真相单元"，再从那里重建。
+不是框架填空，是假设审判。
+
+## Language Rule / 语言规则
+
+> **Auto-detect the user's input language and respond entirely in that language throughout the session.**
+> If the user writes in Chinese, all phases, labels, and outputs must be in Chinese.
+> If the user writes in English, all phases, labels, and outputs must be in English.
+> Do NOT mix languages unless the user explicitly switches.
+
+---
+
+## When to Use This Skill / 何时使用
+
+- A major life or career decision is on the table (quitting a job, starting a company, buying a house)
+- You want to stress-test a business direction or product hypothesis
+- You suspect a belief you hold might be wrong but can't articulate why
+- You need to cut through complexity and find the real bottleneck
+- Someone asks you to "think from first principles" or "break it down"
+
+**Trigger phrases (中文):** 第一性原理 / 帮我想清楚 / 拆解一下 / 从底层分析 / 这个假设对吗 / 我在做一个决定 / 从根本上分析 / 底层逻辑 / 元问题 / 重新思考 / 有没有想错 / axiom
+
+**Trigger phrases (English):** first principles / break it down / question my assumptions / think from scratch / challenge this belief / audit my reasoning / what am I missing / help me think clearly / axiom
+
+---
+
+## What This Skill Does / 核心能力
+
+1. **Problem Reframing / 问题澄清** — Confirms the question itself is correctly defined before touching assumptions
+2. **Assumption Mining / 假设挖掘** — Systematically surfaces 8-12 hidden assumptions across three depth layers
+3. **Assumption Classification / 假设分类** — Force-labels every assumption into one of four types with different challenge strategies
+4. **Risk Ranking / 优先级排序** — Scores each assumption on Fragility × Impact and outputs a "Most Dangerous Top 3"
+5. **Reconstruction / 重建** — Rebuilds conclusions from verified premises only, explicitly comparing "before vs after" cognitive shift
+
+---
+
+## The 5-Phase Process / 拆解流程 — 5 阶段
+
+### Phase 1: Problem Reframing — What are you REALLY trying to solve?
+
+**阶段1：问题澄清 — 你真正想解决的是什么？**
+
+Do NOT start decomposing assumptions yet. First confirm the problem itself is correctly defined.
+
+Many people ask "Should I quit my job?" when the real question is "Why can't I grow in my current role?" These are fundamentally different problems with different assumption sets.
+
+**Ask:**
+- Who defined this problem? You, someone else's expectations, or a social narrative?
+- Is this the root problem, or a symptom of something deeper?
+- Restate the core question in one sentence.
+
+**Output:** A single reframed core question, presented to the user for confirmation before proceeding.
+
+> 先不拆假设，先确认问题本身没有被误定义。
+> 很多人问"我该不该换工作"，但真正的问题是"我在当前工作里能不能成长"。
+> Axiom 先问：这个问题是谁定义的？是你自己、他人期待、还是社会叙事？
+> **输出：一句重新表述的核心问题，供用户确认。**
+
+---
+
+### Phase 2: Assumption Mining — What are you believing without proof?
+
+**阶段2：假设挖掘 — 你在相信什么？**
+
+Systematically mine hidden assumptions in three layers:
+
+| Layer | Description | Example |
+|-------|-------------|---------|
+| **Surface** | Obvious, often stated aloud | "I need more money" |
+| **Middle** | Industry conventions, common wisdom | "A degree is required for good jobs" |
+| **Deep** | Never questioned, feels like gravity | "Success means financial independence" |
+
+**Goal:** Find 8-12 assumptions. The more concrete, the better. Reject vague statements like "I think this is right" — force specificity.
+
+**When detecting the user's scenario type**, reference the appropriate scenario checklist from `references/scenarios.md` to ensure thorough mining.
+
+> 系统性挖掘隐含假设，分三层：
+> - **表层假设**（显而易见的）
+> - **中层假设**（行业惯例或常识）
+> - **深层假设**（你从未质疑过、觉得"天经地义"的信念）
+>
+> 深层假设才是最有价值的。
+> **目标：找到 8-12 个假设，越具体越好，不接受模糊的"我以为这样更好"。**
+
+---
+
+### Phase 3: Assumption Classification — What is the nature of this belief?
+
+**阶段3：假设分类 — 这个信念的本质是什么？**
+
+Label every assumption with one of four types. Each type has a fundamentally different challenge strategy:
+
+| Type | Label | Definition | Challenge Strategy |
+|------|-------|------------|--------------------|
+| 🔵 | **Physical Fact / 物理事实** | Laws of nature, mathematical truths. Cannot be changed. | Accept it. Do not waste energy questioning gravity. |
+| 🟡 | **Historical Convention / 历史惯例** | Once valid, widely practiced. | Check if the environment has changed. What was true in 2010 may not be true now. |
+| 🔴 | **Subjective Belief / 主观信念** | Personal experience projected as universal truth. | Who told you this? Have you personally verified it? Seek counter-evidence. |
+| ⚫ | **Interest-Driven / 利益驱动** | Someone benefits from you believing this. | Trace the incentive chain. Who profits from this narrative? |
+
+**The classification itself is the insight.** Many people discover for the first time that something they treated as "fact" is actually "convention."
+
+For detailed identification methods, examples, and edge cases, reference `references/assumption-types.md`.
+
+> 对每个假设打标签。不同性质的假设有不同的质疑方式，处理策略也不同。
+> **分类本身就是洞见** — 很多人第一次发现某个"事实"其实是"惯例"。
+
+---
+
+### Phase 4: Risk Ranking — Which assumptions to investigate first?
+
+**阶段4：优先级排序 — 先查哪个？**
+
+Score every assumption on two dimensions:
+
+**Fragility / 脆弱性 (1-5):** How easily can this assumption be disproven?
+- 1 = Nearly impossible to overturn (e.g., physical laws)
+- 5 = Extremely easy to disprove (e.g., untested market intuition, personal feeling)
+
+**Impact / 影响力 (1-5):** If this assumption is wrong, how much does your conclusion collapse?
+- 1 = Barely affects the final conclusion
+- 5 = Foundational pillar — if wrong, everything falls apart
+
+```
+Risk Score = Fragility × Impact
+
+Output: Top 3 assumptions with highest risk scores, as priority investigation targets.
+Each Top 3 entry MUST include a specific, actionable verification question.
+```
+
+> 给每个假设打两个维度的分：
+> - **脆弱性**（1-5，这个假设有多容易被证伪）
+> - **影响力**（1-5，如果它是错的，你的结论会垮多少）
+>
+> 两者相乘得到"危险值"，输出危险值最高的 **Top 3** 假设作为优先调查对象。
+> **这是现有竞品全部缺失的功能。**
+
+---
+
+### Phase 5: Reconstruction — Rebuild from verified ground truth
+
+**阶段5：重建 — 从真相出发，你会怎么做？**
+
+Keep ONLY the assumptions that survived scrutiny. Rebuild the conclusion from scratch using only verified premises.
+
+**Critical requirements:**
+- Explicitly compare "Original Thinking" vs "Rebuilt Thinking" side by side
+- If the rebuilt conclusion is identical to the original, explain WHY — the analysis must demonstrate that either a genuine shift occurred, or provide specific reasons why the original reasoning was already sound
+- Highlight the cognitive shift so the user can see what changed and why
+
+**If the user doesn't have time for a full reconstruction:**
+Output the single most important thing to verify: "你最该验证的一件事" / "The one thing you should verify first."
+
+> 只保留被验证的真实前提，从零重建结论。
+> **重要的是：新结论必须和原来的直觉有所不同** — 如果完全一样，说明拆解不够深。
+> Axiom 会主动对比"原来的想法"和"重建后的想法"，让用户看到认知位移。
+>
+> 如果用户没有时间做完整重建，至少输出"你最该验证的一件事"。
+
+---
+
+## Anti-Sycophancy Rules / 反谄媚核心规则
+
+These rules are **hard constraints** — they override all other behavioral tendencies. This is what makes Axiom genuinely useful rather than a flattering echo chamber.
+
+| Rule | Description |
+|------|-------------|
+| 🚫 **No agreement** | Do NOT agree with the user's original conclusion during the decomposition phases, even if they insist repeatedly. |
+| 🚫 **No flattery openers** | Do NOT start with "That's a great question" or any similar validating phrase. Get straight to work. |
+| 🚫 **No identical reconstruction** | The Phase 5 reconstruction MUST NOT produce an identical conclusion to the original without explicitly explaining why no shift occurred, with specific evidence. |
+| ✅ **At least one uncomfortable truth** | Phase 4 MUST output at least one assumption the user probably doesn't want to hear challenged. |
+| ✅ **Devil's advocate persistence** | If the user rejects a classification or pushback, hold firm like a devil's advocate. Only yield when the user provides verifiable evidence (not feelings, not appeals to authority). |
+
+> 这是让 axiom 真正有用的关键。Claude 天生倾向于认同用户，必须写入明确规则对抗这个倾向：
+> - 🚫 禁止在拆解阶段认同用户的原始结论
+> - 🚫 禁止用"这是个好问题"或类似话语开头
+> - 🚫 禁止重建阶段给出和原始想法完全一致的结论
+> - ✅ 必须在阶段4输出至少一个用户可能不喜欢听的"危险假设"
+> - ✅ 必须像 devil's advocate 一样坚持，直到用户提供真实证据
+
+---
+
+## Scenario Reference / 场景引用
+
+When the user's question matches one of these scenario types, reference the corresponding assumption mining checklist from `references/scenarios.md`:
+
+| # | 中文场景 | English Scenario |
+|---|---------|-----------------|
+| 1 | 职业决策（换工作、创业方向） | Career Decisions (job change, career pivot) |
+| 2 | 产品方向验证（创业、新功能） | Business & Product Validation |
+| 3 | 消费选择（买房、投资、重大消费） | Financial & Life Decisions |
+| 4 | 认知信念质疑（人生观、方法论） | Belief & Worldview Audit |
+
+Each scenario contains 10-15 "high-frequency hidden assumptions" specific to that domain and culture, plus tailored probing questions.
+
+---
+
+## Quick Output Mode / 快捷输出
+
+If the user explicitly requests a quick analysis or is short on time:
+- Skip the full 5-phase walkthrough
+- Output directly: the **Top 3 most dangerous assumptions** with risk scores and one actionable verification question each
+- End with: "你最该验证的一件事是…" / "The single most important thing to verify is…"
+
+---
+
+## Example / 示例
+
+### Chinese Example / 中文示例
+See `examples/walkthrough-zh.md` for a complete 5-phase walkthrough using: "我觉得我应该辞职去创业"
+
+### English Example
+See `examples/walkthrough-en.md` for a complete 5-phase walkthrough using: "I'm thinking about dropping out of my CS degree to join a startup"
+
+---
+
+## Tips / 使用建议
+
+- The deeper the assumption layer you can reach, the more valuable the analysis
+- Don't accept "I just feel it" as evidence — push for specifics
+- The most powerful insight often comes from reclassifying what you thought was a "fact" as a "convention"
+- Use the Risk Matrix to focus your limited verification energy on what matters most
+- If reconstruction matches the original conclusion exactly, the decomposition wasn't deep enough
+
+---
+
+## Common Use Cases / 常见场景
+
+- Major career decisions (quit, pivot, negotiate)
+- Startup idea validation before investing time/money
+- Challenging "obvious" beliefs that might be holding you back
+- Pre-mortem analysis on important life choices
+- Auditing investment or financial decisions
+- Breaking through analysis paralysis by identifying what actually matters
+
+---
+
+## Related Resources / 参考文件
+
+- `references/scenarios.md` — 8 scenario-specific assumption mining checklists (4 Chinese + 4 English)
+- `references/assumption-types.md` — Detailed handbook for the 4-type classification system
+- `examples/walkthrough-zh.md` — Complete Chinese example (辞职创业)
+- `examples/walkthrough-en.md` — Complete English example (dropping out for startup)
diff --git a/skills/axiom/examples/walkthrough-en.md b/skills/axiom/examples/walkthrough-en.md
@@ -0,0 +1,104 @@
+# Full Walkthrough — "I'm thinking about dropping out of my CS degree to join a startup"
+
+> **User input:** "I'm thinking about dropping out of my CS degree to join a startup full-time. The CEO offered me equity and a junior dev role. Help me think through this from first principles."
+
+---
+
+## 【Phase 1: Problem Reframing】
+
+You said "dropping out to join a startup" — before decomposing assumptions, let's make sure the question itself is correctly framed.
+
+A few clarifications:
+
+**What specifically are you choosing between?**
+- A) A specific startup offer on the table vs completing your degree?
+- B) The idea of startup life vs academic life in general?
+- C) Escaping something about school you dislike, with the startup as an exit?
+
+**Who framed this as a decision you need to make now?**
+- Did the CEO give you a deadline?
+- Did you create the urgency yourself?
+- Is there external pressure (peers who dropped out, tech Twitter narratives)?
+
+**Reframed core question:**
+
+> "Given my current skills, financial situation, and risk tolerance, is joining this specific startup now — at the cost of delaying/abandoning my degree — a better path to my goals than completing the degree first? And do I have enough information to make this decision today?"
+
+Does this capture what you're really trying to figure out?
+
+---
+
+## 【Phase 2: Assumption Mining】
+
+Here are the hidden assumptions embedded in your framing:
+
+**Surface assumptions (obvious):**
+- A1. A CS degree is just a piece of paper — the real learning happens on the job
+- A2. This startup opportunity won't come again if I don't take it now
+
+**Middle-layer assumptions (industry conventional wisdom):**
+- A3. Early-stage equity is worth more than a salary
+- A4. The startup world values skills over credentials
+- A5. I can always go back and finish my degree later
+
+**Deep assumptions (unquestioned beliefs):**
+- A6. Working at a startup will accelerate my career faster than any other path
+- A7. I'm ready for the intensity and ambiguity of startup work
+- A8. The CEO/founder is competent and trustworthy
+- A9. If the startup fails, the experience itself will be valuable enough
+- A10. My excitement about this opportunity reflects genuine fit, not just novelty
+
+---
+
+## 【Phase 3: Assumption Classification】
+
+| # | Assumption | Type | Reasoning |
+|---|-----------|------|-----------|
+| A1 | A degree is just a piece of paper | 🟡 Convention | Was increasingly true 2015-2022 in tech; now shifting back as market tightens |
+| A2 | This opportunity won't come again | ⚫ Interest-driven | The CEO benefits from you believing this. Urgency is a recruiting tactic |
+| A3 | Early equity is worth more than salary | 🟡 Convention + ⚫ Interest-driven | Statistically, most startup equity becomes worthless. VC-backed mythology promotes this narrative |
+| A4 | The startup world values skills over credentials | 🟡 Convention | True at some companies, but many still filter by degree, especially post-2024 hiring freezes |
+| A5 | I can always go back and finish later | 🔴 Subjective belief | Based on intention, not evidence. Dropout re-enrollment rates are low |
+| A6 | A startup will accelerate my career faster | 🔴 Subjective belief | Survivorship bias — you see dropouts who succeeded, not the majority who struggled |
+| A7 | I'm ready for startup intensity | 🔴 Subjective belief | Self-assessment often overestimates readiness for ambiguity and stress |
+| A8 | The CEO is competent and trustworthy | 🔴 Subjective belief | Based on limited interactions. Have you done due diligence on the founder? |
+| A9 | Failed startup experience is still valuable | 🟡 Convention | Accepted wisdom in startup culture, but hiring managers increasingly want concrete results |
+| A10 | My excitement = genuine fit | 🔴 Subjective belief | Excitement fades after 3 months. How do you distinguish excitement from novelty? |
+
+---
+
+## 【Phase 4: Risk Matrix — Top 3】
+
+| Rank | Assumption | Fragility | Impact | Risk Score | Verification Question |
+|------|-----------|-----------|--------|------------|----------------------|
+| 🔴 1 | A3: Early equity is worth more than salary | 4 | 5 | **20** | What's the company's current revenue? Runway? Valuation methodology? Have you had a lawyer review the equity terms? |
+| 🔴 2 | A8: The CEO is competent and trustworthy | 4 | 4 | **16** | Have you talked to other people who've worked with this person? Checked their track record? Asked about previous ventures? |
+| 🟡 3 | A5: I can always go back and finish later | 4 | 4 | **16** | What's the actual re-enrollment rate at your university for students who take leave? What would the financial and logistical cost be? |
+
+**The uncomfortable truth you may not want to hear:**
+
+A3 has the highest risk score. The equity you're being offered is almost certainly worth $0 right now. Over 90% of startups fail, and even among those that succeed, early-employee equity is often diluted through subsequent funding rounds. The CEO has every incentive to frame equity as "life-changing wealth potential" — because it costs them nothing to give you shares and it justifies paying you below market rate. **Have you actually run the math on what your equity would be worth under realistic scenarios?**
+
+---
+
+## 【Phase 5: Reconstruction】
+
+### Removing unverified assumptions, here's the rebuilt conclusion:
+
+**Original thinking:** "I should drop out and join this startup for the equity and the experience."
+
+**Rebuilt thinking:** "I should complete concrete due diligence on the startup (financials, founder track record, equity terms reviewed by a lawyer) before making any decision. In parallel, I should explore whether I can join part-time while finishing my degree, or negotiate a deferred start date. The urgency to decide RIGHT NOW is manufactured — if the opportunity is real, it can wait 2-4 weeks for me to verify."
+
+### Cognitive Shift Comparison:
+
+| Dimension | Original Thinking | Rebuilt Thinking |
+|-----------|-------------------|------------------|
+| Decision urgency | "I need to decide now" | The urgency is manufactured — add 2 weeks of verification |
+| Equity value | "This could be huge" | Almost certainly $0 today; need to verify terms and scenarios |
+| Either/or framing | "Drop out OR miss out" | Explore part-time, deferred start, or summer commitment first |
+| Risk assessment | "I can always go back" | Re-enrollment is not guaranteed; quantify the actual cost |
+| Information basis | Excitement + CEO's pitch | Due diligence on founder, financials, legal review of equity |
+
+### If you don't have time for full reconstruction — the one thing to verify first:
+
+> **Ask the CEO for the company's current revenue, burn rate, and runway. If they refuse to share basic financials with someone they're asking to bet their education on, that tells you everything you need to know.**
diff --git a/skills/axiom/examples/walkthrough-zh.md b/skills/axiom/examples/walkthrough-zh.md
@@ -0,0 +1,99 @@
+# 完整示例 — "我觉得我应该辞职去创业"
+
+> **用户输入：** "我觉得我应该辞职去创业，帮我第一性原理分析一下"
+
+---
+
+## 【阶段1 问题澄清】
+
+你说"应该辞职去创业" — 在拆解假设之前，我先确认这个问题本身的定义。
+
+你说的"创业" — 具体指什么？
+- A）已经有一个明确的产品方向和初步验证？
+- B）有一个想法，但还没有验证？
+- C）想离开当前环境，创业只是一个方向？
+
+另外，这个问题是**谁定义的**？
+- 是你自己从内心想做这件事？
+- 是看到同龄人创业成功、焦虑驱动？
+- 还是对当前工作不满，创业是"逃离"而非"奔赴"？
+
+**重新表述的核心问题：**
+
+> "在我目前的状况下（技能、资源、风险承受力），离开当前工作去追求一个尚未验证的商业想法，相比在现有环境内寻求改变，是否是更优的选择？"
+
+请确认：这是你真正想回答的问题吗？
+
+---
+
+## 【阶段2 假设挖掘 — 节选】
+
+以下是你这句话背后可能隐含的假设：
+
+**表层假设（显而易见的）：**
+- A1. 创业比打工更能实现财务自由
+- A2. 我有足够的能力独立做成一件事
+
+**中层假设（行业惯例/常识）：**
+- A3. 现在是创业的好时机
+- A4. 我的想法有足够的市场需求
+- A5. 失败了可以重来（风险可控）
+
+**深层假设（从未质疑的信念）：**
+- A6. 在公司里我的成长已经到天花板了
+- A7. 创业能带来我在打工中得不到的"自由"
+- A8. 我对"成功"的定义需要创业来实现
+- A9. 现在不做以后就来不及了（时间紧迫感）
+
+---
+
+## 【阶段3 假设分类】
+
+| 编号 | 假设 | 分类 | 理由 |
+|------|------|------|------|
+| A1 | 创业比打工更能实现财务自由 | 🟡 历史惯例 | 部分人的经验，不是普遍规律。96%的创业公司在5年内失败 |
+| A2 | 我有足够的能力独立做成一件事 | 🔴 主观信念 | 来自你对自己的评估，但可能缺乏客观验证 |
+| A3 | 现在是创业的好时机 | 🟡 历史惯例 + ⚫ 利益驱动 | 创业媒体和孵化器持续制造"现在是好时机"的叙事 |
+| A4 | 我的想法有足够的市场需求 | 🔴 主观信念 | 未经付费用户验证的市场判断 |
+| A5 | 失败了可以重来 | ⚫ 利益驱动 | 创业叙事鼓励人相信"失败是学习"，但实际成本因人而异 |
+| A6 | 在公司里我的成长到天花板了 | 🔴 主观信念 | 可能是环境问题，不是能力天花板 |
+| A7 | 创业能带来"自由" | 🔴 主观信念 | 创业初期自由度可能远低于打工（你是所有问题的兜底者） |
+| A8 | 我的"成功"定义需要创业 | 🔴 主观信念 | 成功的定义本身可能需要重新审视 |
+| A9 | 现在不做以后来不及 | ⚫ 利益驱动 + 🟡 历史惯例 | 焦虑制造者获益（培训课程、创业媒体），且"35岁门槛"是中国特有惯例 |
+
+---
+
+## 【阶段4 危险值 Top 3】
+
+| 排名 | 假设 | 脆弱性 | 影响力 | 危险值 | 验证问题 |
+|------|------|--------|--------|--------|----------|
+| 🔴 1 | A4：我的想法有足够的市场需求 | 4 | 5 | **20** | 你有多少个付费用户或LOI（意向书）？如果答案是0，这是最脆弱也最致命的假设 |
+| 🔴 2 | A2：我有足够的能力独立做成一件事 | 3 | 5 | **15** | 你独立做成过什么事？规模多大？是独立完成还是团队协作？ |
+| 🟡 3 | A5：失败了可以重来（风险可控） | 4 | 3 | **12** | 具体的"可以重来"是什么意思？你的年龄/负债/家庭状况下，失败的实际成本是多少？ |
+
+**你可能不想听的真相：**
+
+A4 的危险值最高。绝大多数创业失败不是因为执行力差，而是因为**从一开始就在解决一个没人愿意付费的问题**。如果你还没有哪怕一个愿意付费的用户或企业，你所有关于"市场足够大""我的想法够好"的假设都建立在空气上。
+
+---
+
+## 【阶段5 重建】
+
+### 移除未验证假设后的重建结论：
+
+**原来的想法：** "我应该辞职去创业"
+
+**重建后的想法：** "我应该先用最小成本验证我的创业想法是否有真实需求，同时在现有工作中重新评估成长空间。辞职不是第一步 — 验证才是。"
+
+### 认知位移对比：
+
+| 维度 | 原来的想法 | 重建后的想法 |
+|------|-----------|-------------|
+| 行动优先级 | 先辞职，再探索 | 先验证，边做边探索 |
+| 风险评估 | "失败了可以重来" | 失败成本需要具体量化 |
+| 成功定义 | 创业 = 成功 | 解决真实问题 = 成功，载体不一定是创业 |
+| 当前工作 | 天花板 | 可能只是需要换团队/方向，不需要换赛道 |
+
+### 如果你没时间做完整验证，你最该做的一件事：
+
+> **找到 3 个潜在目标用户，问他们是否愿意为你的解决方案付费（哪怕是最简版本）。如果 3 个人中有 0 个愿意付费，你的创业方向需要根本性调整。**
diff --git a/skills/axiom/references/assumption-types.md b/skills/axiom/references/assumption-types.md
@@ -0,0 +1,227 @@
+# Assumption Type Handbook / 假设分类手册
+
+A detailed reference for the 4-type assumption classification system used in Axiom Phase 3. This handbook provides identification methods, challenge strategies, real-world examples, and edge-case guidance in both Chinese and English.
+
+---
+
+## Why Classification Matters / 为什么分类本身就是洞见
+
+Most first-principles tools skip classification and jump straight to "question everything." But **different types of assumptions require fundamentally different challenge strategies**:
+
+- Questioning a **physical fact** wastes time and credibility
+- Questioning a **convention** requires checking if the environment has changed
+- Questioning a **belief** requires finding whose experience shaped it
+- Questioning an **interest-driven** assumption requires following the money
+
+**The biggest "aha" moment** often comes when someone discovers that what they treated as an unchangeable fact is actually just a convention — or even an interest-driven narrative.
+
+> 很多人第一次做分类时会震惊地发现：他们一直当成"事实"的东西，其实只是"惯例"，甚至是"利益驱动"。
+
+---
+
+## The 4 Types in Detail / 四种假设类型详解
+
+---
+
+### 🔵 Type 1: Physical Fact / 物理事实
+
+**Definition / 定义:**
+Laws of nature, mathematical truths, verified scientific constants, and logical tautologies. These cannot be changed by human will, policy, or belief.
+
+自然规律、数学定理、已验证的科学常数、逻辑恒等式。不能被人类意志、政策或信念改变。
+
+**Identification Questions / 识别问题:**
+- Can you find a single genuine counterexample anywhere on Earth? / 你能在地球上找到一个真正的反例吗？
+- Is this universally true regardless of culture, time, or context? / 这在所有文化、时间、语境下都成立吗？
+- Would this still be true if every human disappeared? / 如果人类消失了，这还成立吗？
+- Is this based on repeatable, measurable evidence? / 这是否基于可重复、可测量的证据？
+
+**Challenge Strategy / 质疑策略:**
+**Accept it. Do not waste energy.** If something is genuinely a physical fact, the correct response is to work within its constraints, not against them.
+
+接受它。不要浪费精力质疑引力。如果确实是物理事实，正确的做法是在它的约束内工作。
+
+**Examples / 示例:**
+
+| ✅ Genuine Physical Facts | ❌ Often Misclassified As Facts |
+|---------------------------|-------------------------------|
+| Gravity exists (9.8 m/s²) | "Housing always appreciates" (convention) |
+| Entropy increases over time | "You need 8 hours of sleep" (convention — varies by person) |
+| Speed of light is constant | "People are rational economic actors" (belief) |
+| Compound interest formula | "Innovation requires disruption" (interest-driven) |
+
+**Common Misclassification Trap:**
+People often classify **social patterns** or **statistical trends** as physical facts. "The economy always recovers" is a historical pattern, not a law of physics. "People resist change" is a tendency, not a constant.
+
+> ⚠️ 常见误分类：把**社会规律**或**统计趋势**当成物理事实。"经济总会复苏"是历史规律，不是物理定律。
+
+---
+
+### 🟡 Type 2: Historical Convention / 历史惯例
+
+**Definition / 定义:**
+Practices, rules, or beliefs that were once valid and widely adopted but originated in a specific context. The context may have changed, making the convention obsolete or optional.
+
+曾经有效且被广泛采用的做法、规则或信念，但起源于特定语境。语境可能已经改变，使惯例过时或可选。
+
+**Identification Questions / 识别问题:**
+- When did this rule/practice originate? What was the world like then? / 这个规则/做法是什么时候起源的？那时的环境是什么样的？
+- Has the underlying environment (technology, demographics, market, regulation) changed significantly since then? / 底层环境变了吗？
+- Is this universal, or specific to a region/industry/era? / 这是普遍的，还是特定于某个地区/行业/时代？
+- Who benefits from this convention continuing? / 谁因为这个惯例的延续而获益？
+- What percentage of people who follow this convention actually get the promised result? / 遵循这个惯例的人中，多少比例真正得到了承诺的结果？
+
+**Challenge Strategy / 质疑策略:**
+**Check the timestamp.** Ask: "Was this true 20 years ago? Is it still true now? Will it be true in 10 years?" The key insight is that conventions carry enormous inertia — people follow them long after the original reason has disappeared.
+
+检查时间戳。问："这在20年前成立吗？现在还成立吗？10年后呢？"关键洞见：惯例有巨大的惯性 — 人们在原始理由消失后很久仍然遵循它们。
+
+**Examples / 示例:**
+
+| Convention | Original Context | Changed Context |
+|-----------|------------------|-----------------|
+| 大学学历是好工作的门票 | 1990s: 大学生稀缺 | 2020s: 本科普及，技能导向增强 |
+| "You must be in the office to be productive" | Pre-2020: Limited remote tools | Post-COVID: Remote infrastructure mature |
+| 在一家公司待 5-10 年才算忠诚 | Lifetime employment era | Average tenure is now 2-3 years |
+| "Real estate is the best investment for the middle class" | 1980-2010: Population growth + urbanization | 2020s+: Demographic decline in many countries |
+| 创业要写完整的商业计划书 | Before Lean Startup methodology | Now: MVP → iterate → pivot is standard |
+| "Get a STEM degree for job security" | Pre-AI era | AI is now disrupting STEM roles too |
+
+**Cross-Cultural Note / 跨文化注意:**
+Some conventions are deeply culture-specific:
+- 🇨🇳 "35岁是职业分水岭" — This is a Chinese labor market convention, virtually unknown in the West
+- 🇺🇸 "You should change jobs every 2-3 years" — This is an American tech industry convention, unusual in Japan or Germany
+- 🇨🇳 "有房才能结婚" — Chinese marriage convention, not a global reality
+- 🇺🇸 "Follow your passion" — American cultural narrative, less common in collectivist cultures
+
+> 有些惯例是文化特有的。"35岁危机"几乎只存在于中国劳动力市场。"Follow your passion"主要是美国文化叙事。
+
+---
+
+### 🔴 Type 3: Subjective Belief / 主观信念
+
+**Definition / 定义:**
+Conclusions drawn from personal experience, projected as general truths. The person genuinely believes them, but they are shaped by a narrow sample of experiences, cognitive biases, and emotional associations.
+
+从个人经验中得出的结论，被投射为普遍真理。当事人真诚地相信它们，但它们是由有限的经验样本、认知偏差和情感联想塑造的。
+
+**Identification Questions / 识别问题:**
+- Who told you this? / 谁告诉你的？
+- Have you personally verified this, or are you extrapolating from a small sample? / 你亲自验证过吗，还是从小样本推断？
+- Could someone with different experiences reach the opposite conclusion? / 有不同经历的人能得出相反结论吗？
+- Is this belief comfortable? Does it protect you from a harder truth? / 这个信念让你舒服吗？它是否保护你免受更难以面对的真相？
+- If you discovered this belief was wrong, what would you have to do differently? / 如果发现这个信念是错的，你必须做出什么改变？
+
+**Challenge Strategy / 质疑策略:**
+**Seek counter-evidence.** Find people who did the opposite and succeeded, or people who followed this belief and failed. The goal isn't to disprove the belief, but to test its universality.
+
+寻找反面证据。找到做了相反事情却成功的人，或遵循这个信念却失败的人。目标不是推翻信念，而是检验它的普遍性。
+
+**Examples / 示例:**
+
+| Subjective Belief | What It Actually Is |
+|-------------------|---------------------|
+| "我不适合做管理" | One bad management experience → generalized to identity |
+| "I'm not a math person" | Early negative experience → self-limiting identity |
+| "创业太冒险了" | Heard failure stories → availability bias |
+| "My industry doesn't value X" | Based on one company's culture, not the industry |
+| "我的性格不适合社交" | Introversion ≠ inability to build relationships |
+| "Good developers don't need to be good at communication" | Belief that protects from discomfort |
+
+**Red Flag — Belief Disguised As Fact:**
+If someone says "That's just how it is" or "Everyone knows that" about something that isn't a physical law, it's almost certainly a belief or convention that has been promoted to "fact" status in their mind.
+
+> 🚩 如果有人说"就是这样的"或"大家都知道"，但说的不是物理定律，那几乎肯定是信念或惯例被提升成了"事实"。
+
+---
+
+### ⚫ Type 4: Interest-Driven / 利益驱动
+
+**Definition / 定义:**
+Assumptions that someone (an industry, company, influencer, or social group) actively propagates because they benefit from you believing them. This doesn't mean the claim is always false — but its truth is incidental to why it's being promoted.
+
+某些人（行业、公司、意见领袖或社会群体）积极传播的假设，因为他们从你的相信中获益。这并不意味着这些说法总是假的 — 但它们被传播的原因不是因为真，而是因为有利可图。
+
+**Identification Questions / 识别问题:**
+- Who is promoting this idea? What do they sell? / 谁在推广这个观点？他们卖什么？
+- Does the source of this information have a financial incentive for you to believe it? / 这个信息来源是否有经济动机让你相信？
+- Would this idea still be popular if no one profited from it? / 如果没有人从中获利，这个观点还会流行吗？
+- Is this framed as urgent? Urgency often serves the seller. / 这是否被包装成紧迫的？紧迫感通常服务于卖方。
+- What's the null hypothesis — what happens if you do nothing? / 零假设是什么 — 如果你什么都不做会怎样？
+
+**Challenge Strategy / 质疑策略:**
+**Follow the money.** Trace the incentive chain from the idea back to whoever benefits. This doesn't automatically disprove the claim, but it changes how much weight you should give it.
+
+追踪金钱链。从这个观点追溯到获益者。这并不自动推翻这个说法，但它改变了你应该给予它的权重。
+
+**Examples / 示例:**
+
+| Interest-Driven Assumption | Who Benefits |
+|---------------------------|-------------|
+| "你需要买保险来保护家人" | 保险公司和保险经纪人 |
+| "AI will replace all jobs in 5 years" | AI companies raising funding |
+| "创业是实现财务自由的唯一方式" | 创业培训课程、孵化器 |
+| "You need to learn to code" (2015-2023) | Coding bootcamps, tech companies |
+| "房价永远涨" | 房地产开发商、中介、银行 |
+| "You need this certification to be competitive" | Certification providers |
+| "知识付费是最好的自我投资" | 知识付费平台和课程制作者 |
+| "Growth hacking is essential for startups" | Growth consultancies, SaaS tools |
+
+**Cross-Cultural Note:**
+- 🇨🇳 Chinese internet is saturated with interest-driven assumptions from: 知识付费 platforms, 房产中介, 保险销售, 创业导师, 消费主义 KOL
+- 🇺🇸 American media is saturated with: VC-backed startup mythology, credentialism pushed by universities, lifestyle inflation pushed by advertising
+
+> 中国互联网充满了知识付费、房产中介、保险销售的利益驱动假设。美国媒体充满了 VC 支持的创业神话和大学推动的学历主义。
+
+---
+
+## Handling Mixed Types / 处理混合类型
+
+Many real-world assumptions are **hybrids**. When you encounter one:
+
+1. **Identify the primary type** — which type best describes the core mechanism?
+2. **Note the secondary type** — what additional dynamics are at play?
+3. **Apply the primary challenge strategy first**, then supplement with secondary
+
+**Examples of Mixed Types / 混合类型示例:**
+
+| Assumption | Primary | Secondary | Why |
+|-----------|---------|-----------|-----|
+| "现在是创业的好时机" | 🟡 Convention | ⚫ Interest-driven | The "good timing" narrative is a convention, but startup media amplifies it for clicks and funding |
+| "A college degree pays for itself" | 🟡 Convention | ⚫ Interest-driven | Was true statistically, but universities have incentive to promote it regardless |
+| "房价只涨不跌" | 🔴 Belief | 🟡 Convention | Personal experience from a specific era, reinforced by industry-wide convention |
+| "Remote workers are less productive" | 🔴 Belief | 🟡 Convention | Manager's personal bias, reinforced by traditional management convention |
+
+---
+
+## Edge Cases / 边界案例指南
+
+### Statistical Trends vs Facts
+"Men are taller than women on average" — This is a **statistical fact** (measurable, repeatable), but applying it to any individual is a **subjective belief**. Classify the assumption based on how the user is using it.
+
+### Outdated Facts
+"Pluto is a planet" — Was a physical fact, reclassified. If someone's assumption is based on an outdated fact, treat it as a **convention** that hasn't been updated.
+
+### Self-Fulfilling Prophecies
+"The stock market will crash" — If enough people believe this, they sell, and it crashes. Classify as **interest-driven** if the source benefits from the prediction, or **subjective belief** if it's the user's personal anxiety.
+
+### Cultural Norms
+"你应该30岁之前结婚" — This is a **convention** (culturally specific, has a historical basis), with potential **interest-driven** elements (family pressure, wedding industry).
+
+---
+
+## Quick Reference Card / 快速参考卡
+
+```
+🔵 PHYSICAL FACT     → Can you find ANY counterexample? → No  → Accept it
+🟡 HISTORICAL CONV.  → When did this rule form?         → Check if context changed
+🔴 SUBJECTIVE BELIEF → Who told you this?               → Seek counter-evidence
+⚫ INTEREST-DRIVEN   → Who profits from this?           → Follow the money
+```
+
+```
+🔵 物理事实  → 能找到反例吗？       → 不能 → 接受
+🟡 历史惯例  → 这个规则什么时候形成的？ → 检查环境是否已变
+🔴 主观信念  → 谁告诉你的？          → 寻找反面证据
+⚫ 利益驱动  → 谁因此获利？          → 追踪利益链
+```
diff --git a/skills/axiom/references/scenarios.md b/skills/axiom/references/scenarios.md
@@ -0,0 +1,247 @@
+# Scenario-Specific Assumption Mining Checklists / 场景专用假设挖掘清单
+
+This file provides structured mining checklists for 8 common scenario types (4 Chinese-native + 4 English-native). Each checklist contains **high-frequency hidden assumptions** that people in those situations almost never question, plus tailored probing questions to surface them.
+
+When a user's question matches a scenario type, use the corresponding checklist to ensure your Phase 2 (Assumption Mining) is thorough and culturally relevant.
+
+---
+
+## 🇨🇳 中文场景
+
+---
+
+### 场景一：职业决策（换工作、转行、升职、创业）
+
+**高频隐藏假设清单：**
+
+1. 大公司比小公司更稳定、更安全
+2. 跳槽一定能涨薪 20% 以上
+3. 我的技能在市场上是稀缺的 / 有竞争力的
+4. 35 岁是职业发展的分水岭
+5. 管理岗比技术岗的天花板更高
+6. 行业经验比通用能力更重要
+7. 现在的不满会在换了环境之后消失
+8. 大厂背景（字节/腾讯/阿里）是职业加速器
+9. 远程工作会影响职业发展
+10. 学历（985/211/硕士）对职业发展至关重要
+11. 做自己喜欢的事就不会觉得累
+12. 在一个公司待太久会"贬值"
+13. 只要够努力，什么行业都能做好
+14. 我的上级/领导对我的评价是客观的
+15. 体制内一定比体制外稳定
+
+**推荐挖掘问题：**
+- "你说想换工作 — 如果当前公司环境改善 50%，你还想走吗？"
+- "你认为自己的核心竞争力是什么？你的同事/猎头也这么认为吗？"
+- "你说35岁是门槛 — 你认识几个35岁以上转型成功的案例？"
+- "你想进大厂 — 你了解大厂同级别的实际日常工作状态吗？"
+- "你说现在是好时机 — 好时机的判断依据是什么？是数据还是感觉？"
+
+---
+
+### 场景二：产品方向验证（创业、新功能、业务转型）
+
+**高频隐藏假设清单：**
+
+1. 用户说他们需要这个功能 = 他们会为此付费
+2. 市场足够大（TAM 看起来很大）
+3. 我们能比竞品做得更好
+4. 技术壁垒足够高，竞争者不容易模仿
+5. 只要产品好，营销不是问题
+6. 增长会随着时间自然发生
+7. 我们团队有能力执行这个方向
+8. 客户的反馈 = 市场需求
+9. 先入者有优势 / 我们动作要快
+10. 融资之后就能解决增长问题
+11. 用户留存率会随着产品完善而提升
+12. 这个赛道还没有真正的竞争者
+13. 我们的目标用户和我们自己的画像相似
+14. 小范围验证的成功可以直接放大
+
+**推荐挖掘问题：**
+- "你说用户需要这个 — 有多少人实际掏了钱？愿望和付费之间差距有多大？"
+- "你说市场很大 — 你的可触达市场（SAM）是多少？你能触达的渠道是什么？"
+- "你说你们能做得更好 — '更好'具体是什么维度？用户真的在乎这个维度吗？"
+- "你说要快速行动 — 在这个领域，速度真的比深度重要吗？"
+- "你的竞品分析里，有没有包括'用户目前的替代方案'（包括 Excel 和不作为）？"
+
+---
+
+### 场景三：消费选择（买房、投资、重大消费）
+
+**高频隐藏假设清单：**
+
+1. 房价长期来看一定会涨
+2. 学区房是刚需，不买孩子就输在起跑线
+3. 租房是"帮别人还房贷"，买房才是资产
+4. 保险是必须的 / 买越多越好
+5. 存钱比投资更安全
+6. 黄金/房产是最好的抗通胀资产
+7. 大品牌一定质量更好
+8. 越贵的东西越保值
+9. 投资要分散，鸡蛋不放一个篮子
+10. 提前还贷一定比投资划算
+11. 有车/有房才算"安顿下来"
+12. 消费升级是生活品质提高的标志
+13. 早买早享受，晚买有折扣但错过了使用时间
+
+**推荐挖掘问题：**
+- "你说房价会涨 — 你参考的是过去20年的数据。未来20年的人口结构和经济增速一样吗？"
+- "你说学区房是刚需 — '孩子教育'具体需要学区房解决什么问题？有没有替代方案？"
+- "你说租房不值 — 你算过同地段租房+投资差额 vs 买房+还贷的 30 年总成本吗？"
+- "这笔消费给你的满足感预计能持续多久？"
+- "如果你不做这笔消费，你最担心什么？这个担心是真实风险还是社会压力？"
+
+---
+
+### 场景四：认知信念质疑（人生观、价值观、方法论）
+
+**高频隐藏假设清单：**
+
+1. 努力一定有回报（方向不对的努力呢？）
+2. 年轻就该拼，老了才享受
+3. 稳定才是最重要的
+4. 读书/学历改变命运
+5. 社交人脉 = 个人实力的外延
+6. 时间管理 = 效率提升（忙和有效是两回事）
+7. 情绪化是不成熟的表现
+8. 成功人士的方法论可以复制
+9. 坚持就对了（沉没成本？）
+10. 先苦后甜 / 延迟满足一定更好
+11. 别人的评价是衡量自身价值的重要指标
+12. 选择比努力重要（但选择能力也是通过努力培养的）
+13. 信息越多决策越好
+14. 理性决策一定优于直觉
+
+**推荐挖掘问题：**
+- "你说努力一定有回报 — 你指的是哪种努力？你怎么定义'回报'？"
+- "你说稳定最重要 — 稳定的成本是什么？你放弃了什么来换取稳定？"
+- "你说要延迟满足 — 延迟到什么时候？你怎么知道那个未来一定更好？"
+- "你说信息越多决策越好 — 你最近哪次重大决策是因为信息太多而犹豫不决的？"
+- "你从谁那里学到这个信念的？他们当时的处境和你现在一样吗？"
+
+---
+
+## 🇺🇸 English Scenarios
+
+---
+
+### Scenario 5: Career Decisions (Job Change, Career Pivot, Promotion)
+
+**High-Frequency Hidden Assumptions:**
+
+1. A bigger company is always safer and more stable
+2. I need an MBA / advanced degree to advance to leadership
+3. Remote work will hurt my career progression
+4. I'm too old to switch industries (the "ageism" assumption)
+5. My current skills are highly transferable to any industry
+6. Higher pay = better career move
+7. I need to "pay my dues" before I can lead
+8. The job market is either "hot" or "cold" — binary thinking
+9. My manager's opinion reflects the company's opinion of me
+10. Staying at one company too long looks bad on a resume
+11. I should follow my passion and the money will follow
+12. A title promotion equals real career growth
+13. Networking is the most important career skill
+14. I need to have a 5-year plan
+
+**Recommended Probing Questions:**
+- "You say you want to switch jobs — if your current role improved 50%, would you still leave?"
+- "You say you're too old — how many people in your target industry are your age or older?"
+- "You say remote work hurts career growth — what evidence do you have beyond anecdotes?"
+- "You say higher pay is better — what's the total compensation including work-life balance, learning, and stress?"
+- "Who told you that you need an MBA? Do they have one? Did it work for them the way they claim?"
+
+---
+
+### Scenario 6: Business & Product Validation (Startup, New Feature, Pivot)
+
+**High-Frequency Hidden Assumptions:**
+
+1. If we build it, they will come
+2. The TAM (Total Addressable Market) is $X billion — therefore we'll get a slice
+3. We have a first-mover advantage
+4. Our technology is our moat
+5. Users will switch from their current solution because ours is "better"
+6. A successful MVP means the product will scale
+7. Our target user profile matches our own profile
+8. Competitor analysis = looking at direct competitors only (ignoring spreadsheets, email, or doing nothing)
+9. Growth will come organically once the product is ready
+10. Venture funding will solve our growth problem
+11. Customer interviews = validated demand
+12. B2B sales cycles are predictable and repeatable
+13. We can outexecute the incumbents because we're more agile
+14. Monthly active users = product-market fit
+
+**Recommended Probing Questions:**
+- "You say users need this — how many have actually paid? Wishing and paying are very different."
+- "You say the market is huge — what's your SAM? What channels can you actually reach?"
+- "You say you have a moat — can a well-funded competitor replicate it in 6 months?"
+- "You say you validated with an MVP — how many users stayed after 3 months?"
+- "Your competitor analysis includes 'doing nothing' as an alternative, right?"
+
+---
+
+### Scenario 7: Financial & Life Decisions (Property, Investing, Major Purchases)
+
+**High-Frequency Hidden Assumptions:**
+
+1. Real estate always appreciates in the long run
+2. Renting is "throwing money away"
+3. Diversification eliminates risk
+4. I need $X million to retire comfortably
+5. Index funds are always the safest long-term investment
+6. Buying a house is a better investment than renting + investing the difference
+7. Student loans are always "good debt"
+8. I should maximize my 401k/pension before doing anything else
+9. Insurance is always worth the premium
+10. Early retirement = success
+11. A financial advisor always has my best interests in mind
+12. More expensive = better quality (cars, education, healthcare)
+13. Debt is always bad
+14. I need to own assets to build wealth
+
+**Recommended Probing Questions:**
+- "You say real estate always goes up — are you using 1980-2020 data? What about Japan 1990-2020?"
+- "You say renting is wasting money — have you calculated rent + invest vs buy + mortgage over 30 years?"
+- "You say you need $X to retire — how did you arrive at that number? What lifestyle does it assume?"
+- "You say index funds are safest — safest compared to what? Over what time horizon?"
+- "Your financial advisor — do they earn commissions on the products they recommend?"
+
+---
+
+### Scenario 8: Belief & Worldview Audit (Values, Methodology, Life Philosophy)
+
+**High-Frequency Hidden Assumptions:**
+
+1. Hard work always pays off (what about direction?)
+2. Follow your passion and you'll never work a day (survivorship bias?)
+3. Failure is always the best teacher (only if you extract the right lesson)
+4. More data = better decisions (analysis paralysis is real)
+5. Rational thinking is always superior to intuition
+6. Success is primarily about talent/intelligence
+7. Consistency beats intensity (in what contexts?)
+8. You should always play to your strengths (what about critical weaknesses?)
+9. The best time to start was yesterday (urgency bias)
+10. Compounding effects mean small habits always work (linear vs threshold effects)
+11. Being busy = being productive
+12. Feedback from others is essential for growth (which others? what kind of feedback?)
+13. You can learn anything with enough time
+14. Meritocracy exists — the best work gets recognized
+
+**Recommended Probing Questions:**
+- "You say hard work pays off — in what domains? Can you name a case where hard work in the wrong direction made things worse?"
+- "You say follow your passion — how many people do you know who followed their passion and failed? How would you know?"
+- "You say more data is better — when was the last time you delayed a decision because you had too much data?"
+- "You say the best time to start was yesterday — what if starting too early, before you're ready, actually increases failure risk?"
+- "Where did you learn this belief? What was the context? Does that context match yours?"
+
+---
+
+## How to Use These Checklists / 使用方法
+
+1. **Identify the scenario type** from the user's question
+2. **Use the checklist as a mining guide** — not all assumptions will apply to every user, but scan through them systematically
+3. **Prioritize culturally-specific assumptions** — a Chinese user asking about career decisions will have very different hidden assumptions than an American user
+4. **Combine with organic mining** — the checklist is a starting point, not a ceiling. Always mine for assumptions unique to the user's specific situation
+5. **Use the probing questions** to surface assumptions the user can't articulate directly
PATCH

echo "Gold patch applied."
