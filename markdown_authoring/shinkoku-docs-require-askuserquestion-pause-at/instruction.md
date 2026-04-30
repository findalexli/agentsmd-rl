# docs: require AskUserQuestion pause at QR code auth step

Source: [kazukinagata/shinkoku#5](https://github.com/kazukinagata/shinkoku/pull/5)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/e-tax/SKILL.md`

## What to add / change

## Summary
- e-tax スキルの CC-AA-440（QRコード認証）セクションで、エージェントが AskUserQuestion ツールで一時停止し、ユーザーの認証完了報告を待つことを明示的に指示するよう修正
- 選択肢「認証完了」/「QRコードが表示されない」を追加し、トラブル時のフローも接続
- ユーザーが応答するまでブラウザ操作・画面遷移を一切行わないことを太字で明記

## Test plan
- [ ] SKILL.md の CC-AA-440 セクションを読み、指示が明確であることを確認
- [ ] e-tax スキル実行時に QR コード認証画面で AskUserQuestion が表示され、ユーザー応答まで停止することを確認

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
