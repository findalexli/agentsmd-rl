#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agentsmesh

# Idempotency guard
if grep -qF "- **\u8bc6\u522b GitHub remote \u540d\u79f0**\uff1a\u68c0\u67e5 `git remote -v` \u8f93\u51fa\uff0c\u627e\u5230\u6307\u5411 `github.com` \u7684 remote\uff08\u53ef\u80fd\u662f `" ".claude/skills/gh-merge/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/gh-merge/SKILL.md b/.claude/skills/gh-merge/SKILL.md
@@ -23,157 +23,149 @@ user-invocable: true
 ### 1. 确认状态
 
 ```bash
-# 检查当前分支和未提交的更改
 git status
 git branch --show-current
-
-# 确认目标分支（默认 main）
-# 确认 remote 指向 GitHub
 git remote -v
+gh auth status
 ```
 
 **前置检查：**
-- 当前分支不能是目标分支（不能在 main 上对 main 创建 PR）
-- 确认 `gh` CLI 已认证：`gh auth status`
+- 当前分支不能是目标分支
+- `gh` CLI 已认证
+- **识别 GitHub remote 名称**：检查 `git remote -v` 输出，找到指向 `github.com` 的 remote（可能是 `origin`、`github` 或其他名称），后续所有 git push/fetch 命令都使用该 remote 名称
 
 ### 2. 提交代码
 
 如有未提交的更改，先提交：
 
 ```bash
-# 添加所有更改
-git add .
-
-# 提交（使用有意义的 commit message）
+git add <files>
 git commit -m "feat/fix/refactor: 描述更改内容"
-
-# 推送到远程
-git push -u origin <current-branch>
+git push -u <github-remote> <current-branch>
 ```
 
-### 3. 创建 Pull Request
+**注意：**
+- 优先 `git add <具体文件>` 而非 `git add .`，避免意外提交敏感文件
+- push 时使用步骤 1 识别的 GitHub remote 名称
+
+### 3. Rebase 到最新目标分支
 
-使用 `gh` 创建 PR：
+合并前先 rebase，减少冲突风险：
 
 ```bash
-# 创建 PR 到 main 分支（交互式填充标题和描述）
-gh pr create --base main --fill
+git fetch <github-remote> main
+
+# 如有未提交的更改，先 stash
+git stash  # 仅在有 unstaged changes 时执行
+
+git rebase <github-remote>/main
+
+# rebase 完成后恢复 stash
+git stash pop  # 仅在之前执行了 stash 时
 
-# 或指定标题和描述
+# rebase 改变了历史，需要 force push
+git push --force-with-lease <github-remote> <current-branch>
+```
+
+**如果 rebase 有冲突：**
+1. 解决冲突文件
+2. `git add <resolved-files>`
+3. `git rebase --continue`
+4. 重复直到 rebase 完成
+5. `git push --force-with-lease`
+
+### 4. 创建 Pull Request
+
+```bash
 gh pr create --base main --title "PR标题" --body "描述"
 ```
 
-记录返回的 PR 编号（如 `#123`）。
+记录返回的 PR 编号（如 `#42`）。
 
-### 4. 监控 CI Checks
+### 5. 等待并监控 CI Checks（关键步骤）
 
-创建 PR 后，监控 CI 执行状态：
+**⚠️ 绝对不能跳过此步骤。必须确认 CI 全部通过后才能合并。**
 
 ```bash
-# 查看 PR 的 check 状态
-gh pr checks <pr-number>
+# 等待 CI 触发（GitHub Actions 有 10-30 秒延迟）
+sleep 30
+
+# 等待所有 checks 完成
+gh pr checks <pr-number> --watch --interval 15 --fail-fast
+```
 
-# 或查看 PR 详情
-gh pr view <pr-number>
+**处理 `no checks reported` 的情况：**
 
-# 实时等待 checks 完成（最长等待 10 分钟）
+如果 `gh pr checks` 返回 `no checks reported`，这表示 CI 尚未触发，**绝不能**认为"没有 CI"而直接合并。必须重试：
+
+```bash
+# 等待更长时间后重试（最多重试 3 次，每次间隔 30 秒）
+sleep 30
 gh pr checks <pr-number> --watch --interval 15 --fail-fast
 ```
 
-### 5. 处理 CI 失败
+如果重试 3 次（共等待约 2 分钟）后仍然 `no checks reported`，则明确告知用户"CI 未触发"，**询问用户是否确认合并**，不得自行决定。
+
+### 6. 处理 CI 失败
 
 如果 CI Checks 失败：
 
 ```bash
-# 1. 查看失败原因
-gh pr checks <pr-number>
-
-# 2. 查看失败的 run 详细日志
+# 1. 查看失败的 job 日志
 gh run view <run-id> --log-failed
 
-# 3. 根据错误修复代码
-# ... 修复代码 ...
+# 2. 修复代码
 
-# 4. 提交修复
-git add .
+# 3. 提交修复并推送
+git add <files>
 git commit -m "fix: 修复 CI 错误"
-git push
+git push <github-remote> <current-branch>
 
-# 5. 重新检查
+# 4. 重新等待 CI
+sleep 30
 gh pr checks <pr-number> --watch --interval 15 --fail-fast
 ```
 
 重复此过程直到所有 Checks 通过。
 
-### 6. 合并 PR
+### 7. 合并 PR
 
-CI 通过后，合并 PR：
+**前置条件（全部满足才能执行合并）：**
+1. `gh pr checks` 至少报告了 1 个 check
+2. 所有 checks 状态为 `pass`
+3. 没有未解决的冲突
 
 ```bash
-# 合并（squash commits）
 gh pr merge <pr-number> --squash --delete-branch
-
-# 或普通合并
-gh pr merge <pr-number> --merge --delete-branch
-
-# 或 rebase 合并
-gh pr merge <pr-number> --rebase --delete-branch
 ```
 
-**合并策略选择：**
-- `--squash`：多个 commit 压缩为一个，保持历史整洁（推荐）
-- `--merge`：保留完整 commit 历史，创建 merge commit
-- `--rebase`：变基合并，线性历史，无 merge commit
+**合并策略：**
+- `--squash`：压缩为单个 commit（推荐，保持历史整洁）
+- `--merge`：保留完整 commit 历史
+- `--rebase`：线性历史，无 merge commit
 
-### 7. 清理
+**处理 worktree 环境下的报错：**
 
-合并成功后，清理本地分支和 worktree：
+在 git worktree 中执行 `gh pr merge --delete-branch` 时，可能报错：
+```
+failed to run git: fatal: 'main' is already used by worktree at '...'
+```
+这是因为 worktree 无法切换到 main 分支来删除本地分支。**这个报错不影响远程合并**，PR 已经成功合并。用 `gh pr view` 确认：
 
 ```bash
-# 切回主分支
-git checkout main
-git pull
-
-# 删除本地分支（合并后 --delete-branch 已删除远程分支）
-git branch -d <branch-name>
-
-# 如果是 worktree，删除 worktree
-git worktree remove ../AgentsMesh-Worktrees/<dir-name>
+gh pr view <pr-number> --json state,mergedAt
+# 确认 state 为 "MERGED"
 ```
 
-## 完整示例
+### 8. 清理
 
-用户说："把当前分支合并到 main"
-
-执行：
 ```bash
-# 1. 检查状态
-git status
-git branch --show-current
-# 假设当前分支是 feature/user-auth
-
-# 2. 提交并推送
-git add .
-git commit -m "feat: add user authentication"
-git push -u origin feature/user-auth
-
-# 3. 创建 PR
-gh pr create --base main --fill
-# 返回: #42
-
-# 4. 监控 CI
-gh pr checks 42 --watch --interval 15 --fail-fast
-# 等待 checks 完成...
-
-# 5. 如果失败，修复后重新推送
-# git add . && git commit -m "fix: ..." && git push
+# 在 worktree 中无需手动切换分支和清理
+# worktree 会在退出时提示清理
 
-# 6. CI 通过后合并
-gh pr merge 42 --squash --delete-branch
-
-# 7. 清理
+# 非 worktree 环境：
 git checkout main && git pull
-git branch -d feature/user-auth
+git branch -d <branch-name>
 ```
 
 ## 完成后输出
@@ -182,49 +174,41 @@ git branch -d feature/user-auth
 ✅ PR #42 已成功合并到 main
 
 合并详情:
-- 分支: feature/user-auth → main
-- CI Checks: passed
+- 分支: feature/xxx → main
+- CI Checks: 全部通过 (N/N)
 - 合并方式: squash
-
-已清理:
-- 远程分支: feature/user-auth (已删除)
-- 本地分支: feature/user-auth (已删除)
+- PR: https://github.com/org/repo/pull/42
 ```
 
 ## 处理常见问题
 
-### PR 有冲突
+### PR 有合并冲突
 
 ```bash
-# 1. 拉取目标分支最新代码
-git fetch origin main
-
-# 2. 在当前分支上 rebase
-git rebase origin/main
-
-# 3. 解决冲突后继续
-git add .
+git fetch <github-remote> main
+git stash  # 如有 unstaged changes
+git rebase <github-remote>/main
+# 解决冲突...
+git add <resolved-files>
 git rebase --continue
-
-# 4. 强制推送（因为 rebase 改变了历史）
-git push --force-with-lease
+git stash pop  # 如之前 stash 了
+git push --force-with-lease <github-remote> <current-branch>
 ```
 
-### Review 未通过
+### CI 需要 re-run
 
 ```bash
-# 查看 review 评论
-gh pr view <pr-number> --comments
-
-# 修复后推送，通知 reviewer
-git add . && git commit -m "fix: address review feedback" && git push
+gh run rerun <run-id> --failed
+sleep 30
+gh pr checks <pr-number> --watch --interval 15 --fail-fast
 ```
 
-### CI 需要 re-run
+### Review 未通过
 
 ```bash
-# 重新运行失败的 workflow
-gh run rerun <run-id> --failed
+gh pr view <pr-number> --comments
+# 修复后推送
+git add <files> && git commit -m "fix: address review feedback" && git push
 ```
 
 ## 常用命令速查
@@ -237,15 +221,13 @@ gh run rerun <run-id> --failed
 | 查看 Run 日志 | `gh run view <run-id> --log-failed` |
 | 合并 PR | `gh pr merge <number> --squash --delete-branch` |
 | 关闭 PR | `gh pr close <number>` |
-| 查看 PR 评论 | `gh pr view <number> --comments` |
 | 重跑失败 CI | `gh run rerun <run-id> --failed` |
 
 ## 注意事项
 
-- 提交前确保代码已通过本地测试
-- PR 标题应清晰描述更改内容
-- CI 失败时仔细阅读错误日志，使用 `gh run view --log-failed` 定位问题
-- 合并前确认没有冲突
+- **CI 通过是合并的硬性前提**，绝不能在 CI 未完成或未触发时合并
+- 识别正确的 GitHub remote 名称（不一定是 `origin`）
 - 推荐 `--squash` 合并方式保持 main 历史整洁
-- 合并后及时清理分支和 worktree
-- 使用 `--force-with-lease`（而非 `--force`）推送 rebase 后的代码，更安全
+- 使用 `--force-with-lease`（而非 `--force`）推送 rebase 后的代码
+- worktree 环境中 `gh pr merge` 的本地分支删除报错可以忽略，远程合并不受影响
+- 提交前确保代码已通过本地测试
PATCH

echo "Gold patch applied."
