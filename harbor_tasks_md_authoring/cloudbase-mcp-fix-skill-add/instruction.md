# fix: Skill 未说明云数据库集合需预先创建，导致 add() 调用失败

Source: [TencentCloudBase/CloudBase-MCP#554](https://github.com/TencentCloudBase/CloudBase-MCP/pull/554)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `config/source/skills/cloud-functions/SKILL.md`

## What to add / change

## Attribution issue
- issueId: issue_mns14m7u_p8w0jc
- category: skill
- canonicalTitle: Skill 未说明云数据库集合需预先创建，导致 add() 调用失败
- representativeRun: atomic-js-cloudbase-db-add-feedback/2026-04-09T22-07-03-lzf4sf

## Automation summary
- root_cause: The Cloud Functions skill did not state that CloudBase document database collections must be created before calling `db.collection(...).add()`. Internal evaluation evidence matched an actual product-facing docs gap, and the repo’s own integration test flow already assumes explicit collection creation before insert.
- changes: Updated `config/source/skills/cloud-functions/SKILL.md` with one new gotcha and one focused “Database write reminder” section that clarifies `add()` only writes to an existing collection and that “create when missing” must be handled as an explicit collection-management step.
- validation: Reviewed the relevant skill and evidence files, confirmed the existing integration test already creates collections before insert, and ran `git diff --check -- config/source/skills/cloud-functions/SKILL.md` successfully.
- follow_up: No code or API surface changes were needed. CloudBase MCP docs sync is disabled for this run, so any external published docs or generated mirrors were not updated here.
自动检查更新失败：Request timed out: GET https://mirrors.tencent.com/npm/@tencent%2Fcodex-internal。请手动执行 npm i -g @tencent/codex-internal --registry https://mirrors.tencent.

## Changed files
- `config/source/skills/cloud-functions/SKILL.md`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
