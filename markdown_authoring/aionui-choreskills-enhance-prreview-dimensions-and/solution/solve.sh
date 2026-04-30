#!/usr/bin/env bash
set -euo pipefail

cd /workspace/aionui

# Idempotency guard
if grep -qF "The `electron-rebuild` step recompiles native modules (e.g., `better-sqlite3`) a" ".claude/skills/pr-fix/SKILL.md" && grep -qF "- **Electron \u5b89\u5168\u914d\u7f6e** \u2014 \u82e5 PR \u6d89\u53ca `electron-builder.yml`\u3001`entitlements.plist` \u6216 `ele" ".claude/skills/pr-review/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/pr-fix/SKILL.md b/.claude/skills/pr-fix/SKILL.md
@@ -166,12 +166,16 @@ git checkout bot/fix-pr-<PR_NUMBER>
 git merge --no-ff --no-edit FETCH_HEAD
 ```
 
-After creating the worktree (all three paths), symlink `node_modules` so lint/tsc/test can run:
+**All paths — symlink node_modules and rebuild native modules:**
 
 ```bash
 ln -s "$REPO_ROOT/node_modules" "$WORKTREE_DIR/node_modules"
+cd "$WORKTREE_DIR"
+npx electron-rebuild -f -w better-sqlite3 2>/dev/null || true
 ```
 
+The `electron-rebuild` step recompiles native modules (e.g., `better-sqlite3`) against the Electron version used by this project, ensuring ABI compatibility.
+
 Save `REPO_ROOT` and `WORKTREE_DIR` for later steps. All file reads, edits, lint, and test commands from this point forward run inside `WORKTREE_DIR`.
 
 ---
diff --git a/.claude/skills/pr-review/SKILL.md b/.claude/skills/pr-review/SKILL.md
@@ -268,6 +268,9 @@ Review dimensions:
 - **性能** — 不必要的重渲染、大循环、阻塞调用
 - **代码质量** — 函数长度、嵌套深度、命名清晰度
 - **遗留 console.log** — 生产代码中是否有调试日志残留
+- **数据库变更** — 若 PR 涉及 migration 文件或数据库 schema：(1) migration 是否正确（字段类型、约束、索引、默认值、可回滚性）；(2) 变更是否合理且与 PR 目标一致；(3) 对现有数据是否有丢失风险；(4) migration 顺序和依赖是否正确。不正确的 migration 标记为 CRITICAL。
+- **IPC bridge / preload** — 若 PR 涉及 `src/preload.ts` 或 IPC channel 定义：(1) 是否暴露了不必要的 Node.js API 给 renderer；(2) 所有暴露的 API 是否有输入校验；(3) renderer 是否能在无授权情况下触发特权操作。暴露不安全 API 标记为 CRITICAL。
+- **Electron 安全配置** — 若 PR 涉及 `electron-builder.yml`、`entitlements.plist` 或 `electron.vite.config.ts` 中的 Electron 配置：(1) sandbox/nodeIntegration/contextIsolation 设置是否被弱化；(2) entitlements 是否授权过度；(3) 签名和公证是否被破坏。安全回退标记为 CRITICAL。
 - **测试** — 对照 [testing skill](../testing/SKILL.md) 的标准评估，以下任一情况须指出：
   - 新增功能没有对应测试用例
   - 修改了逻辑但未更新已有相关测试
PATCH

echo "Gold patch applied."
