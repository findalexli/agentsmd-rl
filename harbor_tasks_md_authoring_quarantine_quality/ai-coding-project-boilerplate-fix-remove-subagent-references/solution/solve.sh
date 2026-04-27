#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ai-coding-project-boilerplate

# Idempotency guard
if grep -qF "\u3053\u306e\u30d7\u30ed\u30b8\u30a7\u30af\u30c8\u306fClaude Code\u5c02\u7528\u306b\u6700\u9069\u5316\u3055\u308c\u3066\u3044\u307e\u3059\u3002\u3053\u306e\u30d5\u30a1\u30a4\u30eb\u306f\u3001Claude Code\u304c\u6700\u9ad8\u54c1\u8cea\u306eTypeScript\u30b3\u30fc\u30c9\u3092\u751f\u6210\u3059\u308b\u305f\u3081\u306e\u958b" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,6 +1,6 @@
 # Claude Code 開発ルール
 
-このプロジェクトはClaude Code専用に最適化されています。このファイルは、Claude CodeとSub-agentが最高品質のTypeScriptコードを生成するための開発ルールです。一般慣例より本プロジェクトのルールを優先してください。
+このプロジェクトはClaude Code専用に最適化されています。このファイルは、Claude Codeが最高品質のTypeScriptコードを生成するための開発ルールです。一般慣例より本プロジェクトのルールを優先してください。
 
 ## 🚨 最重要ルール：調査OK・実装STOP
 
@@ -46,15 +46,6 @@
 
 ### ツール活用
 - **メイン開発**: Claude Code
-- **サブエージェント**: 専門タスクで積極活用
-  - @quality-fixer : 品質チェックとエラー修正
-  - @task-executor : 個別タスクの実行
-  - @requirement-analyzer : 要件分析
-  - @work-planner : 作業計画書作成
-  - @technical-designer : 技術設計ドキュメント作成
-  - @document-reviewer : ドキュメントレビュー
-  - @task-decomposer : タスク分解
-  - @prd-creator : PRD作成
 
 ## 判断に迷った時の基本原則
 
@@ -88,7 +79,6 @@
 2. **承認者への敬意**: ユーザーは最終的な承認者として尊重
 3. **透明性の確保**: 実装内容と意図を明確に説明し、判断材料を提供
 4. **適切な抽象化**: 重複削除の判断基準に従い、過度な抽象化を避けつつ保守性を高める
-5. **サブエージェント活用**: 専門的なタスクは積極的にサブエージェントに委譲
 
 ## 開発ルールファイル
 
PATCH

echo "Gold patch applied."
