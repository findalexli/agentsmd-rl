#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ai-agents-for-beginners

# Idempotency guard
if grep -qF "\u672c\u66f8\u306fAI\u7ffb\u8a33\u30b5\u30fc\u30d3\u30b9\u300c[Co-op Translator](https://github.com/Azure/co-op-translator)\u300d\u3092\u4f7f\u7528\u3057\u3066\u7ffb" "translations/ja/.agents/skills/jupyter-notebook/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/translations/ja/.agents/skills/jupyter-notebook/SKILL.md b/translations/ja/.agents/skills/jupyter-notebook/SKILL.md
@@ -12,33 +12,33 @@ description: ユーザーが実験、探索、またはチュートリアル用
 
 同梱のテンプレートとヘルパースクリプトを使うことで、一貫した構造を保ち、JSONのミスを減らすことを推奨します。
 
-## When to use
+## いつ使うか
 - 新しい `.ipynb` ノートブックをゼロから作成するとき。
 - ラフなノートやスクリプトを構造化されたノートブックに変換するとき。
 - 既存のノートブックをより再現可能で読みやすくリファクタリングするとき。
 - 他の人が読むまたは再実行する実験やチュートリアルを作成するとき。
 
-## Decision tree
+## 決定木分析
 - リクエストが探索的、分析的、または仮説駆動型であれば、`experiment` を選びます。
 - リクエストが指導的、段階的、または特定の対象者向けであれば、`tutorial` を選びます。
 - 既存のノートブックを編集する場合はリファクタとして扱い、意図を保持して構造を改善します。
 
-## Skill path (set once)
+## スキルパス（一度設定）
 
 ```bash
 export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
 export JUPYTER_NOTEBOOK_CLI="$CODEX_HOME/skills/jupyter-notebook/scripts/new_notebook.py"
 ```
 
-User-scoped skills install under `$CODEX_HOME/skills` (default: `~/.codex/skills`).
+ユーザー限定スキルは `$CODEX_HOME/skills` ディレクトリにインストールされます（デフォルト：`~/.codex/skills`）。
 
-## Workflow
-1. Lock the intent.
-Identify the notebook kind: `experiment` or `tutorial`.
-Capture the objective, audience, and what "done" looks like.
+## ワークフロー
+1. インテントを確定する。
+ノートブックの種類（`experiment` または `tutorial`）を特定する。
+目的、対象ユーザー、完了状態を明確にする。
 
-2. Scaffold from the template.
-Use the helper script to avoid hand-authoring raw notebook JSON.
+2. テンプレートからスキャフォールディングする。
+ヘルパースクリプトを使用することで、ノートブックのJSONを手作業で作成する必要がなくなります。
 
 ```bash
 uv run --python 3.12 python "$JUPYTER_NOTEBOOK_CLI" \
@@ -53,53 +53,52 @@ uv run --python 3.12 python "$JUPYTER_NOTEBOOK_CLI" \
   --title "Intro to embeddings" \
   --out output/jupyter-notebook/intro-to-embeddings.ipynb
 ```
-
-3. Fill the notebook with small, runnable steps.
-Keep each code cell focused on one step.
-Add short markdown cells that explain the purpose and expected result.
-Avoid large, noisy outputs when a short summary works.
-
-4. Apply the right pattern.
-For experiments, follow `references/experiment-patterns.md`.
-For tutorials, follow `references/tutorial-patterns.md`.
-
-5. Edit safely when working with existing notebooks.
-Preserve the notebook structure; avoid reordering cells unless it improves the top-to-bottom story.
-Prefer targeted edits over full rewrites.
-If you must edit raw JSON, review `references/notebook-structure.md` first.
-
-6. Validate the result.
-Run the notebook top-to-bottom when the environment allows.
-If execution is not possible, say so explicitly and call out how to validate locally.
-Use the final pass checklist in `references/quality-checklist.md`.
-
-## Templates and helper script
-- Templates live in `assets/experiment-template.ipynb` and `assets/tutorial-template.ipynb`.
-- The helper script loads a template, updates the title cell, and writes a notebook.
-
-Script path:
+3. ノートブックには、実行可能な小さなステップを記述してください。
+各コードセルは、1つのステップに焦点を絞ってください。
+目的と期待される結果を説明する短いマークダウンセルを追加してください。
+短い要約で済む場合は、長くて冗長な出力は避けてください。
+
+4. 適切なパターンを適用します。
+実験については、`references/experiment-patterns.md` を参照してください。
+チュートリアルについては、`references/tutorial-patterns.md` を参照してください。
+
+5. 既存のノートブックを編集する際は、安全に作業を進めてください。
+ノートブックの構造を維持し、全体の流れを改善する場合を除き、セルの順序変更は避けてください。
+全面的な書き換えよりも、対象を絞った編集を優先してください。
+どうしてもJSONファイルを編集する必要がある場合は、まず`references/notebook-structure.md`を確認してください。
+
+6. 結果を検証する。
+環境が許せば、ノートブックを最初から最後まで実行してください。
+実行できない場合は、その旨を明記し、ローカル環境での検証方法を指示してください。
+最終合格チェックリストは、`references/quality-checklist.md` を参照してください。
+
+## テンプレートとヘルパースクリプト
+- テンプレートは `assets/experiment-template.ipynb` と `assets/tutorial-template.ipynb` にあります。
+- ヘルパースクリプトはテンプレートを読み込み、タイトルセルを更新し、ノートブックを作成します。
+
+スクリプトのパス:
 - `$JUPYTER_NOTEBOOK_CLI`（インストール時のデフォルト: `$CODEX_HOME/skills/jupyter-notebook/scripts/new_notebook.py`）
 
-## Temp and output conventions
-- Use `tmp/jupyter-notebook/` for intermediate files; delete when done.
-- Write final artifacts under `output/jupyter-notebook/` when working in this repo.
-- Use stable, descriptive filenames (for example, `ablation-temperature.ipynb`).
+## 一時ファイルと出力ファイルの保存規則
+- 中間ファイルは `tmp/jupyter-notebook/` に保存し、作業完了後に削除してください。
+- このリポジトリで作業する場合は、最終成果物を `output/jupyter-notebook/` に保存してください。
+- 安定した、分かりやすいファイル名を使用してください（例：`ablation-temperature.ipynb`）。
 
-## Dependencies (install only when needed)
-Prefer `uv` for dependency management.
+## 依存関係（必要な場合のみインストールしてください）
+依存関係の管理には`uv`の使用を推奨します。
 
-Optional Python packages for local notebook execution:
+ローカルノートブック実行のためのオプションのPythonパッケージ：
 
 ```bash
 uv pip install jupyterlab ipykernel
 ```
 
-The bundled scaffold script uses only the Python standard library and does not require extra dependencies.
+同梱されているスキャフォールディングスクリプトはPython標準ライブラリのみを使用しており、追加の依存関係は不要です。
 
-## Environment
-No required environment variables.
+## 環境
+必須の環境変数はありません。
 
-## Reference map
+## 参照マップ
 - `references/experiment-patterns.md`: 実験の構成と経験則。
 - `references/tutorial-patterns.md`: チュートリアルの構成と教育的な流れ。
 - `references/notebook-structure.md`: ノートブックJSONの構造と安全な編集ルール。
@@ -109,5 +108,5 @@ No required environment variables.
 
 <!-- CO-OP TRANSLATOR DISCLAIMER START -->
 免責事項：
-本書はAI翻訳サービス「Co-op Translator」(https://github.com/Azure/co-op-translator)を使用して翻訳されました。正確さには努めていますが、自動翻訳には誤りや不正確な箇所が含まれる可能性があります。原文（原言語の文書）を正本としてご参照ください。重要な情報については、専門の人間による翻訳を推奨します。本翻訳の利用により生じたいかなる誤解や解釈の相違についても、当社は責任を負いません。
-<!-- CO-OP TRANSLATOR DISCLAIMER END -->
\ No newline at end of file
+本書はAI翻訳サービス「[Co-op Translator](https://github.com/Azure/co-op-translator)」を使用して翻訳されました。正確さには努めていますが、自動翻訳には誤りや不正確な箇所が含まれる可能性があります。原文（原言語の文書）を正本としてご参照ください。重要な情報については、専門の人間による翻訳を推奨します。本翻訳の利用により生じたいかなる誤解や解釈の相違についても、当社は責任を負いません。
+<!-- CO-OP TRANSLATOR DISCLAIMER END -->
PATCH

echo "Gold patch applied."
