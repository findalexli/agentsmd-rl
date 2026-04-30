# docs(weibo): add comprehensive usage examples

Source: [Panniantong/Agent-Reach#195](https://github.com/Panniantong/Agent-Reach/pull/195)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `agent_reach/skill/SKILL.md`

## What to add / change

## 变更内容

在 SKILL.md 中添加微博渠道的完整使用示例。

## 功能覆盖

- ✅ 热搜榜 (get_trendings)
- ✅ 搜索用户 (search_users)
- ✅ 用户资料 (get_profile)
- ✅ 用户动态 (get_feeds / get_hot_feeds)
- ✅ 内容搜索 (search_content)
- ✅ 话题搜索 (search_topics)
- ✅ 评论列表 (get_comments)
- ✅ 粉丝/关注列表 (get_fans / get_followers)

## 技术细节

- 使用 mcp-server-weibo (Panniantong/mcp-server-weibo)
- 通过 mcporter 调用
- 零配置，不需要登录
- 自动获取访客 cookie

## 测试

- ✅ 所有测试通过 (15/15)
- ✅ 功能已在本地验证

Closes #179 (Bilibili 搜索问题已在 #182 修复)
Closes #180 (Bilibili doctor 检查已在 #182 修复)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
