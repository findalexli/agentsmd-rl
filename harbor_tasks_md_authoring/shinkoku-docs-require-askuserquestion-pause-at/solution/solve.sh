#!/usr/bin/env bash
set -euo pipefail

cd /workspace/shinkoku

# Idempotency guard
if grep -qF "**AskUserQuestion \u30c4\u30fc\u30eb\u3067\u4e00\u6642\u505c\u6b62**\u3057\u3001\u30e6\u30fc\u30b6\u30fc\u304c\u8a8d\u8a3c\u5b8c\u4e86\u3092\u5831\u544a\u3059\u308b\u307e\u3067**\u7d76\u5bfe\u306b\u6b21\u306e\u30b9\u30c6\u30c3\u30d7\u306b\u9032\u307e\u306a\u3044**\u3053\u3068\u3002" "skills/e-tax/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/e-tax/SKILL.md b/skills/e-tax/SKILL.md
@@ -268,15 +268,25 @@ Windows/macOS の Chrome/Edge であれば問題なし。
 
 ### CC-AA-440: QRコード認証
 
-**★ ユーザーへの声かけが必要**
+**★ ユーザー操作待ち — ブラウザ操作を一時停止**
+
+この画面ではエージェントがブラウザを操作してはならない。
+**AskUserQuestion ツールで一時停止**し、ユーザーが認証完了を報告するまで**絶対に次のステップに進まない**こと。
+
+AskUserQuestion で以下を表示する:
 
 ```
 QRコード認証画面が表示されました。
 スマートフォンのマイナポータルアプリでQRコードを読み取り、
 マイナンバーカードで認証してください。
-認証が完了したら教えてください。
+
+認証が完了したら「認証完了」を選択してください。
 ```
 
+- 選択肢: 「認証完了」 / 「QRコードが表示されない」
+- 「QRコードが表示されない」が選ばれた場合は下記の ⚠️ Playwright CLI 使用時の注意 を参照して対処する
+- **ユーザーが「認証完了」を選択するまで、一切のブラウザ操作・画面遷移を行わない**
+
 認証完了後、自動的に次の画面に遷移する。
 
 **⚠️ Playwright CLI 使用時の注意**: `PLAYWRIGHT_MCP_INIT_SCRIPT` 環境変数で `etax-stealth.js` を指定することで
PATCH

echo "Gold patch applied."
