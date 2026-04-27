# add Claude comm literature review skill

Source: [wanshuiyin/Auto-claude-code-research-in-sleep#33](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/pull/33)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/comm-lit-review/SKILL.md`

## What to add / change

新增一个通信领域文献检索 skill：comm-lit-review

 这个 skill 与现有 research-lit 的关系：
  - 它不是替代 research-lit，而是通信领域的专用变体
  - research-lit 仍然负责通用文献检索与综述
  - comm-lit-review-claude-single 只在通信/无线/网络/星地链路/NTN/速率控制/拥塞控制/资源分配等主题 下使用
  - 相比 research-lit，这个版本增加了通信领域特有的检索和组织约束，而不是泛化地搜论文

  相对 research-lit 的主要增强：
  - 固定采用 Claude 风格的 knowledge-base-first 检索顺序： Zotero -> Obsidian -> local papers -> IEEE -> ScienceDirect -> ACM -> web
  - 对外部检索增加通信领域数据库优先级，而不是直接泛化 web/arXiv 检索
  - 增加通信领域 venue 分层： top venues -> mainstream venues -> broader formal venues
  - 默认优先正式发表论文，并在需要时区分 preprint / workshop / peer-reviewed
  - 输出时按通信领域常见层次组织： PHY/MAC、transport、NTN/satellite、cross-layer、measurement

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
