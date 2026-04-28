#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cli

# Idempotency guard
if grep -qF "lark-cli drive +import --file ./report.docx --type docx" "skills/lark-drive/references/lark-drive-import.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/lark-drive/references/lark-drive-import.md b/skills/lark-drive/references/lark-drive-import.md
@@ -12,12 +12,28 @@
 ## 命令
 
 ```bash
+# 导入 Word 为新版文档 (docx)
+lark-cli drive +import --file ./report.docx --type docx
+lark-cli drive +import --file ./legacy.doc --type docx
+
 # 导入 Markdown 为新版文档 (docx)
 lark-cli drive +import --file ./README.md --type docx
 
+# 导入纯文本为新版文档 (docx)
+lark-cli drive +import --file ./notes.txt --type docx
+
+# 导入 HTML 为新版文档 (docx)
+lark-cli drive +import --file ./page.html --type docx
+
 # 导入 Excel 为电子表格 (sheet)
 lark-cli drive +import --file ./data.xlsx --type sheet
 
+# 导入 Excel 97-2003 (.xls) 为电子表格 (sheet)
+lark-cli drive +import --file ./legacy.xls --type sheet
+
+# 导入 CSV 为电子表格 (sheet)
+lark-cli drive +import --file ./data.csv --type sheet
+
 # 导入 Excel 为多维表格 / Base (bitable)
 lark-cli drive +import --file ./crm.xlsx --type bitable --name "客户台账"
 
PATCH

echo "Gold patch applied."
