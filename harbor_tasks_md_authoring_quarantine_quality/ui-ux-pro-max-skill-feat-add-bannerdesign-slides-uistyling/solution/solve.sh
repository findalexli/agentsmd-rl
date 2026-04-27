#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ui-ux-pro-max-skill

# Idempotency guard
if grep -qF "*For human/AI reference: follow priority 1\u219210 to decide which rule category to f" ".claude/skills/ui-ux-pro-max/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/ui-ux-pro-max/SKILL.md b/.claude/skills/ui-ux-pro-max/SKILL.md
@@ -9,45 +9,45 @@ Comprehensive design guide for web and mobile applications. Contains 50+ styles,
 
 ## When to Apply
 
-当任务涉及 **UI 结构、视觉设计决策、交互模式或用户体验质量控制** 时，应使用此 Skill。
+This Skill should be used when the task involves **UI structure, visual design decisions, interaction patterns, or user experience quality control**.
 
 ### Must Use
 
-在以下情况必须调用此 Skill：
+This Skill must be invoked in the following situations:
 
-- 设计新的页面（Landing Page、Dashboard、Admin、SaaS、Mobile App）
-- 创建或重构 UI 组件（按钮、弹窗、表单、表格、图表等）
-- 选择配色方案、字体系统、间距规范或布局体系
-- 审查 UI 代码的用户体验、可访问性或视觉一致性
-- 实现导航结构、动效或响应式行为
-- 做产品层级的设计决策（风格、信息层级、品牌表达）
-- 提升界面的感知质量、清晰度或可用性
+- Designing new pages (Landing Page, Dashboard, Admin, SaaS, Mobile App)
+- Creating or refactoring UI components (buttons, modals, forms, tables, charts, etc.)
+- Choosing color schemes, typography systems, spacing standards, or layout systems
+- Reviewing UI code for user experience, accessibility, or visual consistency
+- Implementing navigation structures, animations, or responsive behavior
+- Making product-level design decisions (style, information hierarchy, brand expression)
+- Improving perceived quality, clarity, or usability of interfaces
 
 ### Recommended
 
-在以下情况建议使用此 Skill：
+This Skill is recommended in the following situations:
 
-- UI 看起来"不够专业"，但原因不明确
-- 收到可用性或体验方面的反馈
-- 准备上线前的 UI 质量优化
-- 需要对齐跨平台设计（Web / iOS / Android）
-- 构建设计系统或可复用组件库
+- UI looks "not professional enough" but the reason is unclear
+- Receiving feedback on usability or experience
+- Pre-launch UI quality optimization
+- Aligning cross-platform design (Web / iOS / Android)
+- Building design systems or reusable component libraries
 
 ### Skip
 
-在以下情况无需使用此 Skill：
+This Skill is not needed in the following situations:
 
-- 纯后端逻辑开发
-- 仅涉及 API 或数据库设计
-- 与界面无关的性能优化
-- 基础设施或 DevOps 工作
-- 非视觉类脚本或自动化任务
+- Pure backend logic development
+- Only involving API or database design
+- Performance optimization unrelated to the interface
+- Infrastructure or DevOps work
+- Non-visual scripts or automation tasks
 
-**判断准则**：如果任务会改变某个功能 **看起来如何、使用起来如何、如何运动或如何被交互**，就应该使用此 Skill。
+**Decision criteria**: If the task will change how a feature **looks, feels, moves, or is interacted with**, this Skill should be used.
 
 ## Rule Categories by Priority
 
-*供人工/AI 查阅：按 1→10 决定先关注哪类规则；需要细则时用 `--domain <Domain>` 查询。脚本不读取本表。*
+*For human/AI reference: follow priority 1→10 to decide which rule category to focus on first; use `--domain <Domain>` to query details when needed. Scripts do not read this table.*
 
 | Priority | Category | Impact | Domain | Key Checks (Must Have) | Anti-Patterns (Avoid) |
 |----------|----------|--------|--------|------------------------|------------------------|
@@ -338,12 +338,12 @@ Use this skill when the user requests any of the following:
 
 | Scenario | Trigger Examples | Start From |
 |----------|-----------------|------------|
-| **New project / page** | "做一个 landing page"、"Build a dashboard" | Step 1 → Step 2 (design system) |
-| **New component** | "Create a pricing card"、"Add a modal" | Step 3 (domain search: style, ux) |
-| **Choose style / color / font** | "What style fits a fintech app?"、"推荐配色" | Step 2 (design system) |
-| **Review existing UI** | "Review this page for UX issues"、"检查无障碍" | Quick Reference checklist above |
-| **Fix a UI bug** | "Button hover is broken"、"Layout shifts on load" | Quick Reference → relevant section |
-| **Improve / optimize** | "Make this faster"、"Improve mobile experience" | Step 3 (domain search: ux, react) |
+| **New project / page** | "Build a landing page", "Build a dashboard" | Step 1 → Step 2 (design system) |
+| **New component** | "Create a pricing card", "Add a modal" | Step 3 (domain search: style, ux) |
+| **Choose style / color / font** | "What style fits a fintech app?", "Recommend a color palette" | Step 2 (design system) |
+| **Review existing UI** | "Review this page for UX issues", "Check accessibility" | Quick Reference checklist above |
+| **Fix a UI bug** | "Button hover is broken", "Layout shifts on load" | Quick Reference → relevant section |
+| **Improve / optimize** | "Make this faster", "Improve mobile experience" | Step 3 (domain search: ux, react) |
 | **Implement dark mode** | "Add dark mode support" | Step 3 (domain: style "dark mode") |
 | **Add charts / data viz** | "Add an analytics dashboard chart" | Step 3 (domain: chart) |
 | **Stack best practices** | "React performance tips"、"SwiftUI navigation" | Step 4 (stack search) |
@@ -474,7 +474,7 @@ python3 skills/ui-ux-pro-max/scripts/search.py "<keyword>" --stack react-native
 
 ## Example Workflow
 
-**User request:** "Make an AI search homepage。"
+**User request:** "Make an AI search homepage."
 
 ### Step 1: Analyze Requirements
 - Product type: Tool (AI search engine)
PATCH

echo "Gold patch applied."
