# refactor: テスト戦略ルールの運用改善を追加

Source: [kinopeee/cursorrules#5](https://github.com/kinopeee/cursorrules/pull/5)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/test-strategy.en.mdc`
- `.cursor/rules/test-strategy.mdc`

## What to add / change

## 概要

テスト戦略ルールに運用上の柔軟性と明確化を追加し、実務での運用負荷を下げつつ品質基準を維持できるように改善しました。

## 変更内容

- 観点表が必須になるケースを明示（軽微な修正は任意）
- 境界値候補の取捨選択ルールを追加
- 分岐網羅100%の現実的な扱いを明文化
- 自動化困難ケースのテンプレート化
- コード変更時のテスト追加・更新を必須化

## 技術的な詳細

### 1. 観点表の必須条件の明確化
既存テストの軽微な修正（メッセージ調整や期待値の微修正など）で新しい分岐や制約が追加されない場合は、テスト観点表の新規作成・更新を任意としました。

### 2. 境界値の取捨選択ルール
境界値候補（0 / 最小値 / 最大値 / ±1 / 空 / NULL）のうち仕様上意味を持たないものは、`Notes` に対象外とする理由を記載したうえで省略可能にしました。

### 3. 分岐網羅の現実的な扱い
分岐網羅100%は目標値とし、達成が合理的でない場合はビジネスインパクトの高い分岐および主要なエラー経路を優先的に網羅することを明文化しました。未カバー分岐がある場合は理由と影響を明示することを必須としました。

### 4. 自動化困難ケースのテンプレート化
代替手段には、対象機能とリスク、手動検証手順、期待される結果、ログやスクリーンショットの保存方法を含めることを必須としました。

### 5. コード変更時のテスト必須化
本番コードに意味のある変更を含むPRには、対応する自動テストの追加または更新を必須としました。困難な場合は理由と代替検証手順をPR本文に明記し、レビュアと合意を取ることを必須としました。

## テスト内容

- ルールファイルのMarkdown形式の妥当性を確認
- 日英両方のファイルで内容の整合性を確認

## 関連Issue

なし

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> Clarifies EN/JA test strategy: optional perspectives table for minor tweaks, boundary omission with notes, 100% branch coverage as a target with documentation, and stronger operational requirements (alternatives and mandatory tests for prod changes).
> 
> - **Rules updates (EN/JA)**:
>   - **Test perspective table**: Allow omitting non-meaningful boundary candidates with justification in `Notes`; make the table optional for minor test tweaks that add no new branches/constraints.
>   - **Coverage policy**: Treat 100% branch coverage as a target; prioritize high‑impact branches/error paths when not feasible; document any uncovered branches and

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
