#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cursorrules

# Idempotency guard
if grep -qF "5. In principle, any PR that includes a meaningful change to production code (su" ".cursor/rules/test-strategy.en.mdc" && grep -qF "2. \u30d6\u30e9\u30f3\u30c1\u30ab\u30d0\u30ec\u30c3\u30b8\u30fb\u30b9\u30c6\u30fc\u30c8\u30e1\u30f3\u30c8\u30ab\u30d0\u30ec\u30c3\u30b8\u3092\u78ba\u8a8d\u3057\u3001\u5206\u5c90\u7db2\u7f85 100% \u3092\u76ee\u6a19\u3068\u3059\u308b\uff08\u9054\u6210\u304c\u5408\u7406\u7684\u3067\u306a\u3044\u5834\u5408\u306f\u3001\u30d3\u30b8\u30cd\u30b9\u30a4\u30f3\u30d1\u30af\u30c8\u306e\u9ad8\u3044\u5206\u5c90\u304a\u3088\u3073\u4e3b\u8981\u306a" ".cursor/rules/test-strategy.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/test-strategy.en.mdc b/.cursor/rules/test-strategy.en.mdc
@@ -13,7 +13,9 @@ These rules define the test process that **must** be followed whenever you imple
 1. Before starting any test work, you **must** first present a “test perspectives table” in Markdown table format.
 2. The table must include at least the following columns: `Case ID`, `Input / Precondition`, `Perspective (Equivalence / Boundary)`, `Expected Result`, `Notes`.
 3. Rows must comprehensively cover normal, abnormal, and boundary cases. For boundary values, you must include `0 / minimum / maximum / ±1 / empty / NULL` at a minimum.
+   Among the boundary candidates (0 / minimum / maximum / ±1 / empty / NULL), you may omit those that are not meaningful for the given specification, as long as you record in `Notes` why they are out of scope.
 4. If you later discover missing perspectives, update the table after self‑review and add the necessary cases.
+5. Note: For minor adjustments to existing tests (such as tweaking messages or slightly updating expectations) that do not introduce new branches or constraints, creating or updating a test perspectives table is optional.
 
 ### Template example
 
@@ -37,6 +39,8 @@ These rules define the test process that **must** be followed whenever you imple
    - Failures of external dependencies (e.g. API / DB / messaging, when applicable)
    - Exception types and error messages
 4. Additionally, aim for 100% branch coverage, and design extra cases yourself as needed to achieve it.
+   Treat 100% branch coverage as a target. When it is not reasonably achievable, at minimum cover all high‑impact business branches and primary error paths.
+   If any branches remain uncovered, explicitly document the reasons and impact in `Notes` or the PR description.
 
 ---
 
@@ -66,7 +70,7 @@ Place these comments directly above the test code or within the steps so that re
 
 1. At the end of test implementation, always document the **execution command** and **coverage collection method** at the end of the documentation or PR description.
    - Examples: `npm run test`, `pnpm vitest run --coverage`, `pytest --cov=...`
-2. Check branch coverage and statement coverage, and at a minimum aim for 100% branch coverage.
+2. Check branch coverage and statement coverage, aiming for 100% branch coverage as a target (when it is not reasonably achievable, prioritize covering high‑impact business branches and primary error paths).
 3. Attach coverage report results (screenshots or summaries) where reasonably possible.
 
 ---
@@ -77,6 +81,10 @@ Place these comments directly above the test code or within the steps so that re
 2. Even when there are no external dependencies, you must still include failure cases by **using mocks to simulate failures**.
 3. When new branches or constraints are added to the target specification, update both the test perspective table and the test code at the same time.
 4. If there are cases that are difficult to automate, clearly document the reasons and alternative measures, and obtain agreement with the reviewer.
+   The alternative measures must at least describe the affected functionality and risks, the manual verification steps, the expected results, and how logs or screenshots will be recorded.
+5. In principle, any PR that includes a meaningful change to production code (such as new features, bug fixes, or refactors that may affect behavior) must also include corresponding additions or updates to automated tests.
+6. If adding or updating tests is reasonably difficult, clearly document the reasons and the alternative verification steps (such as manual test procedures) in the PR description and obtain agreement from the reviewer.
+7. Even for refactors that are not intended to change behavior, confirm that the changed areas are sufficiently covered by existing tests, and add tests when coverage is insufficient.
 
 ---
 
diff --git a/.cursor/rules/test-strategy.mdc b/.cursor/rules/test-strategy.mdc
@@ -13,7 +13,9 @@ alwaysApply: true
 1. いかなるテスト作業を開始する前にも、まず Markdown 形式の「テスト観点表（test perspectives table）」を提示しなければならない。
 2. 表には少なくとも次の列を含めること: `Case ID`, `Input / Precondition`, `Perspective (Equivalence / Boundary)`, `Expected Result`, `Notes`。
 3. 行は正常系・異常系・境界値のケースを網羅すること。境界値については、最低でも `0 / 最小値 / 最大値 / ±1 / 空 / NULL` を含める。
+   境界値候補（0 / 最小値 / 最大値 / ±1 / 空 / NULL）のうち仕様上意味を持たないものは、`Notes` に対象外とする理由を記載したうえで省略してよい。
 4. 後から観点漏れに気づいた場合は、セルフレビュー後に表を更新し、必要なケースを追加すること。
+5. なお、既存テストの軽微な修正（メッセージ調整や期待値の微修正など）であり、新しい分岐や制約が追加されない場合は、テスト観点表の新規作成・更新は任意とする。
 
 ### テンプレート例
 
@@ -37,6 +39,8 @@ alwaysApply: true
    - 外部依存の失敗（API / DB / メッセージング等が該当する場合）
    - 例外種別およびエラーメッセージ
 4. さらに、分岐網羅率 100% を目標にし、必要に応じて追加ケースを自ら設計する。
+   分岐網羅 100% は目標値とし、達成が合理的でない場合は、少なくともビジネスインパクトの高い分岐および主要なエラー経路を網羅すること。
+   未カバーとなる分岐がある場合は、その理由と影響を `Notes` や PR 本文に明示する。
 
 ---
 
@@ -66,7 +70,7 @@ alwaysApply: true
 
 1. テスト実装の最後に、**実行コマンド**と**カバレッジ取得方法**をドキュメントやPR本文の末尾に必ず記載する。
    - 例: `npm run test`, `pnpm vitest run --coverage`, `pytest --cov=...`
-2. ブランチカバレッジ・ステートメントカバレッジを確認し、最低要件として分岐網羅 100% を目指す。
+2. ブランチカバレッジ・ステートメントカバレッジを確認し、分岐網羅 100% を目標とする（達成が合理的でない場合は、ビジネスインパクトの高い分岐および主要なエラー経路を優先的に網羅すること）。
 3. カバレッジレポートの確認結果（スクリーンショットや要約）を可能な範囲で添付する。
 
 ---
@@ -77,6 +81,10 @@ alwaysApply: true
 2. 外部依存がない場合でも、失敗系は**モックを活用して擬似的に失敗させる**こと。
 3. テスト対象の仕様に新しい分岐や制約が追加された場合、テスト観点表とテストコードを同時に更新する。
 4. 自動化が困難なケースがある場合は、理由と代替手段を明記した上でレビューアと合意形成を行う。
+   代替手段には少なくとも、対象機能とリスク、手動検証手順、期待される結果、およびログやスクリーンショットの保存方法を含めること。
+5. 原則として、本番コードに意味のある変更（仕様追加・バグ修正・挙動に影響し得るリファクタ）を含むPRには、対応する自動テストの追加または更新を必ず含めること。
+6. テストの追加・更新が合理的に困難な場合は、その理由と代替となる検証手順（手動テスト手順など）をPR本文に明記し、レビュアと合意を取ること。
+7. 挙動変更を意図しないリファクタであっても、変更箇所が既存テストで十分にカバーされているかを確認し、不足している場合はテストを追加すること。
 
 ---
 
PATCH

echo "Gold patch applied."
