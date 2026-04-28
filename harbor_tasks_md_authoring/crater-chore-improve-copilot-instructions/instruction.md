# chore: improve copilot instructions

Source: [raids-lab/crater#380](https://github.com/raids-lab/crater/pull/380)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

完善 Copilot Code Review 指令：新增“直接应用建议可能导致 Workflow/Lint 失败”的安全提醒，并移除受系统约束、难以稳定生效的总览统计表要求。

### 修改

- **统一安全提醒**：在行内评论与总览评论中都要求提示“Copilot 建议仅供参考，直接应用可能导致 Workflow（如 Lint）失败”，引导开发者本地修改并验证后再提交（`.github/copilot-instructions.md`）
- **精简总览约束**：删除总览评论中的“统计摘要表”要求，避免与 Copilot 总览输出的内置模板/约束冲突（`.github/copilot-instructions.md`）

### 测试

- 无

---

Improve Copilot code review instructions by adding a safety warning that directly applying suggestions may break Workflows/Lint, and removing the overview statistics table requirement that is constrained by Copilot’s built-in overview format.

### Changes

- **Consistent safety warning**: Require a prominent warning in both inline and overview comments that Copilot suggestions are for reference only and may cause Workflow (e.g., Lint) failures if applied directly; recommend local edits and verification before pushing (`.github/copilot-instructions.md`)
- **Simplify overview constraints**: Remove the “statistics summary table” requirement from overview comments to avoid conflicts with Copilot’s constrained overview output (`.github/copilot-instructions.md`)

### Testing

- None

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
