#!/usr/bin/env bash
set -euo pipefail

cd /workspace/tilelang-ascend

# Idempotency guard
if grep -qF "description: \"\u6839\u636e Pass \u9700\u6c42\u751f\u6210 TileLang-Ascend Pass \u8bbe\u8ba1\u6587\u6863\uff08pass-design.md\uff09\u3002\u6db5\u76d6 Pass \u5b9a\u4f4d\u5206" ".agents/skills/tilelang-pass-design/SKILL.md" && grep -qF "| `buffer scope annotations` | `Map<Buffer, String>` | `AscendInferBufferScope` " ".agents/skills/tilelang-pass-design/references/pass-impl-patterns.md" && grep -qF "| {buffer_shapess} | `CollectBufferShapes` | Phase 1 \u6b65\u9aa4 8 | `f->GetAttr<Map<Var," ".agents/skills/tilelang-pass-design/templates/pass-design-template.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/tilelang-pass-design/SKILL.md b/.agents/skills/tilelang-pass-design/SKILL.md
@@ -0,0 +1,261 @@
+---
+name: tilelang-pass-design
+description: "根据 Pass 需求生成 TileLang-Ascend Pass 设计文档（pass-design.md）。涵盖 Pass 定位分析（Phase 1/2归属、Pipeline位置、依赖关系）、IR 变换设计、C++ 实现方案、测试方案、风险分析等。触发关键词：设计 Pass、Pass 设计文档、写 Pass、实现 Pass、添加 Pass、新建 Pass、Pass 设计、开发 Pass。"
+---
+
+# TileLang-Ascend Pass 设计文档生成 Skill
+
+---
+
+## 1. 目标
+
+根据 Pass 需求信息，生成一份完整的 TileLang-Ascend Pass 设计文档（`pass-design.md`），涵盖以下核心决策：
+
+- **Pass 定位**：Phase 1 / Phase 2 归属、Pipeline 具体位置
+- **依赖分析**：上游 Pass 输入、下游 Pass 输出、数据流传递
+- **IR 变换设计**：输入 IR 结构、输出 IR 结构、变换逻辑
+- **实现方案**：C++ 类设计、核心方法、Python Wrapper、Pipeline 集成
+- **测试方案**：功能测试、依赖测试、边界测试
+- **风险分析**：已知约束、常见错误、与其他 Pass 的交互
+
+---
+
+## 2. 输入要求
+
+### 必需信息
+
+| 字段 | 说明 |
+|------|------|
+| Pass 名称 | 如 `BufferReuseOptimizer`、`L0CLayoutOptimization` |
+| 功能描述 | Pass 要解决的问题和目标 |
+| IR 变换类型 | 修改 IR / 收集信息 / 验证 IR |
+| 平台范围 | 平台无关 / Ascend 特定 |
+
+**提问规则（必须严格遵守）**：
+1. **每次只询问一个字段**：使用 `question` 工具时，`questions` 数组中只包含一个元素
+2. **按表格顺序依次询问**：Pass 名称 → 功能描述 → IR 变换类型 → 平台范围
+3. **已提供的字段跳过**：如果用户在初始请求中已提供某个字段的值，跳过该字段继续下一个
+
+### 推荐信息
+
+| 字段 | 说明 |
+|------|------|
+| 参考 Pass | 可参考的现有 Pass 名称 |
+| 输入数据依赖 | Pass 需要哪些 attrs（如 `buffer_shapess`、`address_map`） |
+| 输出数据供给 | Pass 产生哪些 attrs 供下游使用 |
+| 性能目标 | Pass 对编译时间或生成代码性能的影响 |
+
+---
+
+## 3. 工作流程
+
+### Phase 1：需求澄清
+
+1. 解析用户提供的 Pass 需求信息
+2. 检查必需字段是否完整
+3. **按顺序逐一提问补全缺失字段**（每次只问一个）
+
+### Phase 2：信息收集
+
+1. **查阅 Pass 定位参考资料**：
+   - `tilelang-pass-workflow-analyzer/references/pass-pipeline-overview.md` - Pipeline 架构
+   - `tilelang-pass-workflow-analyzer/references/new-pass-placement-guide.md` - 定位决策流程
+   - `tilelang-pass-workflow-analyzer/references/pass-dependency-graph.md` - 依赖关系
+
+2. **查阅 Pass 实现参考资料**：
+   - `tilelang-pass-analyzer/references/pass-registry-ascend.md` - 类似 Pass 实现
+   - `tilelang-pass-analyzer/references/ir-examples.md` - IR 变换示例格式
+
+3. **查阅本 skill 的实现模式参考**：
+   - `references/pass-impl-patterns.md` - C++ 类模板、注册方式
+
+### Phase 3：Pass 定位分析
+
+按照 `new-pass-placement-guide.md` 的决策流程：
+
+**Step 1：分析 Pass 功能**
+- Pass 的主要功能是什么？
+- Pass 修改 IR 还是收集信息？
+- Pass 是平台无关还是 Ascend 特定？
+- Pass 属于哪类优化（Lowering / 合法化 / 内存 / 流水线 / 同步 / 其他）？
+
+**Step 2：分析依赖关系**
+- Pass 需要哪些输入数据（attrs）？
+- 这些数据由哪个 Pass 产生？
+- Pass 产生哪些输出数据？
+- 这些数据由哪个 Pass 使用？
+
+**Step 3：确定阶段归属**
+- DSL Lowering / IR 合法化 → Phase 1
+- 硬件优化 / 内存优化 / 同步优化 → Phase 2
+- 输入数据来自 Phase 1 → 可在 Phase 1 或 Phase 2
+- 输入数据来自 Phase 2 → 必须在 Phase 2
+
+**Step 4：确定具体位置**
+- 依赖优先：Pass 必须在产生其输入数据的 Pass 后执行
+- 供给优先：Pass 必须在使用其输出数据的 Pass 前执行
+- 功能相邻：将 Pass 放在功能相似的 Pass 附近
+
+### Phase 4：生成 pass-design.md
+
+基于 `templates/pass-design-template.md` 模板，填充所有章节：
+
+1. 概述
+2. Pass 定位
+3. IR 变换设计
+4. 实现方案
+5. 测试方案
+6. 风险点与注意事项
+7. 交付清单
+
+### Phase 5：质量自检
+
+按照 §5 中的自检清单逐项检查，确保文档质量。
+
+### Phase 6：针对性修订
+
+仅修正未通过自检的项目。信息确实不足的标注为「待确认」并说明原因。
+
+### Phase 7：输出与关联引导
+
+1. 将 `pass-design.md` 输出到当前目录或用户指定路径
+2. 若文件已存在，询问是否覆盖
+3. **关联引导**：提示用户可使用相关 skill 查看详细信息
+
+---
+
+## 4. 定位决策速查表
+
+### 阶段归属速查
+
+| Pass 功能特征 | 阶段归属 | 理由 |
+|-------------|---------|------|
+| DSL Lowering | Phase 1 | 将高级 DSL 转换为底层 IR |
+| IR 合法化 | Phase 1 | 确保 lowered IR 符合规范 |
+| 信息收集 | Phase 1 或 Phase 2 | 根据收集时机决定 |
+| 硬件优化 | Phase 2 | 针对 Ascend 硬件特性优化 |
+| 内存优化 | Phase 2 | 利用硬件内存层级优化 |
+| 流水线优化 | Phase 2 | 多核流水线规划 |
+| 同步优化 | Phase 2 | 多核同步策略 |
+
+### 典型定位场景
+
+| Pass 功能特征 | 推荐位置 |
+|-------------|---------|
+| IR 合法化检查 | Phase 1 末尾 |
+| 新 Tile 操作 Lowering | Phase 1，`LowerTileOp` 后 |
+| 内存优化 | Phase 2，`AscendStorageRewrite` 后，`AscendMemoryPlanning` 前 |
+| 同步优化 | Phase 2，`AscendMemoryPlanning` 后，`AscendSyncInsert` 前 |
+| 流水线优化 | Phase 2，`PipelinePlanning` 后 |
+| 信息收集 | 根据收集内容类型决定 |
+
+### 关键数据依赖
+
+| 输入数据 | 产生 Pass | 阶段 |
+|---------|-----------|------|
+| `buffer scope` | `AscendInferBufferScope` | Phase 1 |
+| `buffer_shapess` | `CollectBufferShapes` | Phase 1 |
+| `address_map` | `AscendMemoryPlanning` | Phase 2 |
+| `size_map` | `AscendMemoryPlanning` | Phase 2 |
+
+---
+
+## 5. 质量自检清单
+
+生成 `pass-design.md` 后，逐项检查：
+
+| # | 检查项 | 是否必须通过 |
+|---|--------|-------------|
+| 1 | **阶段归属有明确结论和理由**：不是「视情况而定」 | ✅ 必须 |
+| 2 | **Pipeline 位置具体到步骤**：如「Phase 2 步骤 13，在 X Pass 后」 | ✅ 必须 |
+| 3 | **依赖关系完整**：上游 Pass + 下游 Pass + 数据传递 | ✅ 必须 |
+| 4 | **IR 变换有输入/输出示例**：伪 IR 格式，标注变化点 | ✅ 必须 |
+| 5 | **C++ 类名和核心方法明确**：具体到类名和关键方法名 | ✅ 必须 |
+| 6 | **Pipeline 集成代码完整**：包含集成到 `phase.py` 的代码片段 | ✅ 必须 |
+| 7 | **无占位符或模糊描述**：无 `{placeholder}`、TODO、「待补充」 | ✅ 必须 |
+
+**通过条件**：所有必须项全部通过。
+
+---
+
+## 6. 信息源优先级
+
+| 优先级 | 信息源 | 用途 |
+|--------|--------|------|
+| 1 | `tilelang-pass-workflow-analyzer/references/` | Pass 定位、依赖分析 |
+| 2 | `tilelang-pass-analyzer/references/` | Pass 实现参考、IR 变换示例 |
+| 3 | `references/pass-impl-patterns.md`（本 skill） | C++ 类模板、注册方式 |
+| 4 | `tilelang/engine/phase.py` | Pipeline 集成参考 |
+| 5 | `src/transform/*.cc` | 典型实现模式（仅在追问时使用） |
+
+**冲突处理**：当信息源之间矛盾时，以 `pass-pipeline-overview.md` 和 `new-pass-placement-guide.md` 为准。
+
+---
+
+## 7. 错误处理
+
+| 场景 | 处理方式 |
+|------|----------|
+| 用户未提供 Pass 名称 | 提问补全 |
+| 必需字段缺失 | 列出缺失项，逐一提问 |
+| 无法确定阶段归属 | 分析依赖关系后给出推荐方案，标注为「需确认」 |
+| 目标文件已存在 | 询问用户是否覆盖或另存 |
+| Pass 功能过于复杂 | 建议拆分为多个子 Pass 分别设计 |
+
+---
+
+## 8. 完成报告与关联引导
+
+文档生成完成后，输出以下格式的报告：
+
+```
+## Pass 设计文档生成报告
+
+- Pass 名称: {Pass 名称}
+- 阶段归属: {Phase 1 / Phase 2}
+- Pipeline 位置: {具体位置描述}
+- IR 变换类型: {修改 IR / 收集信息 / 验证 IR}
+- 输出路径: {文件路径}
+
+### 自检结果
+1. 阶段归属明确: ✅ / ❌
+2. Pipeline 位置具体: ✅ / ❌
+3. 依赖关系完整: ✅ / ❌
+4. IR 变换示例清晰: ✅ / ❌
+5. C++ 实现方案明确: ✅ / ❌
+6. Pipeline 集成代码完整: ✅ / ❌
+7. 无占位符: ✅ / ❌
+
+### 待确认项
+- {列出需要用户进一步确认的内容}
+
+### 后续步骤建议
+1. 查看详细 Pass 工作流：使用 **tilelang-pass-workflow-analyzer** skill
+2. 查看类似 Pass 实现：使用 **tilelang-pass-analyzer** skill
+3. 开始实现 Pass：使用 **tilelang-pass-generate** skill（待创建）
+```
+
+---
+
+## 9. 参考资料
+
+本 skill 依赖以下参考文件：
+
+| 文件 | 路径 | 用途 |
+|------|------|------|
+| Pass 定位指南 | `tilelang-pass-workflow-analyzer/references/new-pass-placement-guide.md` | 定位决策流程 |
+| Pipeline 架构 | `tilelang-pass-workflow-analyzer/references/pass-pipeline-overview.md` | 阶段划分、Pass 列表 |
+| 依赖关系图 | `tilelang-pass-workflow-analyzer/references/pass-dependency-graph.md` | 数据流分析 |
+| Pass 注册表 | `tilelang-pass-analyzer/references/pass-registry-ascend.md` | 类似 Pass 参考 |
+| IR 示例 | `tilelang-pass-analyzer/references/ir-examples.md` | IR 变换格式 |
+| 实现模式 | `references/pass-impl-patterns.md`（本 skill） | C++ 模板代码 |
+
+---
+
+## 10. 与其他 Skill 的关系
+
+| Skill | 关系 | 使用时机 |
+|------|------|----------|
+| `tilelang-pass-workflow-analyzer` | 依赖 | 查阅 Pipeline 架构、Pass 定位、依赖关系 |
+| `tilelang-pass-analyzer` | 依赖 | 查阅现有 Pass 实现细节、IR 变换示例 |
+| `tilelang-pass-generate`（待创建） | 后续 | 根据设计文档生成 Pass 代码 |
\ No newline at end of file
diff --git a/.agents/skills/tilelang-pass-design/references/pass-impl-patterns.md b/.agents/skills/tilelang-pass-design/references/pass-impl-patterns.md
@@ -0,0 +1,485 @@
+# Pass 实现模式参考
+
+本文档提供 TileLang-Ascend Pass 的典型实现模式，供 Pass 设计时参考。
+
+---
+
+## 1. 父类选择指南
+
+### 1.1 父类对比
+
+| 父类 | 用途 | 适用 Pass 类型 | 特点 |
+|------|------|----------------|------|
+| `IRMutatorWithAnalyzer` | 修改 IR 结构 | IR 变换类 Pass | 提供 `MutateFunc()` 和表达式分析器 |
+| `StmtExprVisitor` | 遍历 IR、收集信息 | 信息收集类 Pass | 不修改 IR，只访问节点 |
+| `StmtExprMutator` | 简单 IR 变换 | 简单变换类 Pass | 提供 `VisitStmt_()` 和 `VisitExpr_()` |
+
+### 1.2 选择决策树
+
+```
+Pass 是否修改 IR？
+├─ 是 → 是否需要表达式分析器？
+│   ├─ 是 → IRMutatorWithAnalyzer
+│   └─ 否 → StmtExprMutator
+└─ 否 → StmtExprVisitor（仅遍历和收集）
+```
+
+---
+
+## 2. IR 变换类 Pass 模板
+
+### 2.1 基本模板
+
+```cpp
+// 文件: src/transform/<pass_name>.cc
+
+#include <tvm/tir/transform.h>
+#include <tvm/tir/op.h>
+#include <tvm/arith/analyzer.h>
+#include "common/attr.h"  // 常用 attr 定义
+
+namespace tvm {
+namespace tl {
+
+class MyIRTransformPass : public arith::IRMutatorWithAnalyzer {
+public:
+  // Pass 入口方法（静态方法，供外部调用）
+  static PrimFunc Substitute(PrimFunc f, PassContext ctx) {
+    // 1. 读取配置（可选）
+    bool config_enabled = ctx->GetConfig<Bool>(kMyPassConfig, Bool(false)).value();
+    if (!config_enabled) {
+      return f;  // 配置为 false 时跳过
+    }
+    
+    // 2. 读取输入 attrs（如有依赖）
+    auto input_attr = f->GetAttr<Map<Var, Array<PrimExpr>>>("buffer_shapess");
+    if (!input_attr.defined()) {
+      LOG(WARNING) << "buffer_shapess not found, skipping MyPass";
+      return f;
+    }
+    
+    // 3. 创建变换器实例并执行
+    MyIRTransformPass mutator(f, ctx, input_attr.value());
+    PrimFunc new_f = mutator.MutateFunc(f);
+    
+    // 4. 设置输出 attrs（如有输出）
+    if (mutator.HasOutput()) {
+      new_f = new_f.WithAttrs({{"output_attr", mutator.GetOutput()}});
+    }
+    
+    return new_f;
+  }
+  
+private:
+  // 构造函数
+  MyIRTransformPass(PrimFunc f, PassContext ctx, Map<Var, Array<PrimExpr>> input_attr)
+      : IRMutatorWithAnalyzer(f->body), input_attr_(input_attr) {}
+  
+  // 成员变量
+  Map<Var, Array<PrimExpr>> input_attr_;
+  Map<Buffer, PrimExpr> output_data_;  // 输出数据（可选）
+  
+  // 核心 Visit 方法（重写需要处理的节点类型）
+  Stmt VisitStmt_(const ForNode* op) final {
+    // 处理 For 循环
+    // ...
+    Stmt body = VisitStmt(op->body);  // 递归处理子节点
+    // ...
+    return For(op->loop_var, op->min, op->extent, op->kind, body, op->annotations);
+  }
+  
+  Stmt VisitStmt_(const BufferStoreNode* op) final {
+    // 处理 BufferStore（写 buffer）
+    // ...
+    return BufferStore(op->buffer, VisitExpr(op->value), op->indices);
+  }
+  
+  Expr VisitExpr_(const BufferLoadNode* op) final {
+    // 处理 BufferLoad（读 buffer）
+    // ...
+    return BufferLoad(op->buffer, op->indices);
+  }
+  
+  Stmt VisitStmt_(const EvaluateNode* op) final {
+    // 处理 Evaluate（执行表达式）
+    // ...
+    return Evaluate(op->value);
+  }
+  
+  // 辅助方法
+  bool IsTargetBuffer(Buffer buffer) {
+    // 检查 buffer 是否为目标 buffer
+    // ...
+  }
+  
+  bool HasOutput() const { return output_data_.size() > 0; }
+  Map<Buffer, PrimExpr> GetOutput() const { return output_data_; }
+};
+
+// Pass 注册函数
+tvm::transform::Pass MyIRTransformPass() {
+  auto pass_func = [=](PrimFunc f, IRModule m, PassContext ctx) {
+    return MyIRTransformPass::Substitute(std::move(f), ctx);
+  };
+  return CreatePrimFuncPass(pass_func, 0, "tl.MyIRTransformPass", {});
+}
+
+// TVM 全局注册（供 Python 调用）
+TVM_REGISTER_GLOBAL("tl.transform.MyIRTransformPass")
+    .set_body_typed(MyIRTransformPass);
+
+// 配置键注册（可选）
+static constexpr const char *kMyPassConfig = "tl.my_pass";
+TVM_REGISTER_PASS_CONFIG_OPTION(kMyPassConfig, Bool);
+
+} // namespace tl
+} // namespace tvm
+```
+
+### 2.2 典型 Visit 方法实现示例
+
+#### 处理 For 循环
+
+```cpp
+Stmt VisitStmt_(const ForNode* op) final {
+  // 检查是否为目标循环类型（如 Parallel）
+  if (op->kind == ForKind::Parallel) {
+    // 执行变换逻辑
+    Stmt transformed_body = TransformParallelLoop(op);
+    return For(op->loop_var, op->min, op->extent, 
+               ForKind::Serial, transformed_body, op->annotations);
+  }
+  
+  // 非目标循环，递归处理子节点
+  Stmt body = VisitStmt(op->body);
+  return For(op->loop_var, op->min, op->extent, op->kind, body, op->annotations);
+}
+```
+
+#### 处理 BufferStore
+
+```cpp
+Stmt VisitStmt_(const BufferStoreNode* op) final {
+  // 检查 buffer scope
+  std::string scope = op->buffer.scope();
+  if (scope == "local.L0C") {
+    // 对 L0C buffer 执行特殊处理
+    // ...
+  }
+  
+  // 递归处理 value 和 indices
+  Expr value = VisitExpr(op->value);
+  Array<PrimExpr> indices = MutateArray(op->indices);
+  return BufferStore(op->buffer, value, indices);
+}
+```
+
+---
+
+## 3. 信息收集类 Pass 模板
+
+### 3.1 基本模板
+
+```cpp
+// 文件: src/transform/<pass_name>.cc
+
+namespace tvm {
+namespace tl {
+
+class MyInfoCollectorPass : public StmtExprVisitor {
+public:
+  static PrimFunc Substitute(PrimFunc f, PassContext ctx) {
+    // 创建收集器实例
+    MyInfoCollectorPass collector(f);
+    
+    // 执行遍历（不修改 IR）
+    collector.VisitStmt(f->body);
+    
+    // 获取收集的信息
+    Map<Buffer, Array<PrimExpr>> collected_info = collector.GetCollectedInfo();
+    
+    // 设置输出 attrs（信息收集类 Pass 通常有输出）
+    return f.WithAttrs({{"collected_attr", collected_info}});
+  }
+  
+private:
+  MyInfoCollectorPass(PrimFunc f) : StmtExprVisitor() {}
+  
+  // 收集的数据
+  Map<Buffer, Array<PrimExpr>> buffer_info_;
+  std::unordered_map<Buffer, std::string> buffer_scopes_;
+  
+  // Visit 方法（只访问，不修改）
+  void VisitStmt_(const AllocateNode* op) final {
+    // 记录 buffer 分配信息
+    buffer_info_.Set(op->buffer, op->extents);
+    buffer_scopes_[op->buffer] = op->scope;
+    
+    // 继续遍历子节点
+    VisitStmt(op->body);
+  }
+  
+  void VisitExpr_(const BufferLoadNode* op) final {
+    // 记录 buffer 访问信息
+    // ...
+    VisitExpr(op->buffer);
+    for (auto idx : op->indices) {
+      VisitExpr(idx);
+    }
+  }
+  
+  // 辅助方法
+  Map<Buffer, Array<PrimExpr>> GetCollectedInfo() const { return buffer_info_; }
+};
+
+// Pass 注册（同上）
+tvm::transform::Pass MyInfoCollectorPass() { ... }
+TVM_REGISTER_GLOBAL("tl.transform.MyInfoCollectorPass").set_body_typed(MyInfoCollectorPass);
+
+} // namespace tl
+} // namespace tvm
+```
+
+---
+
+## 4. 典型 Pass 实现模式
+
+### 4.1 AscendSyncInsert 模式（复杂 IR 变换）
+
+**特点**：
+- 多类协作（`AscendSyncInsert` + `ForLoopUnroller` + `LoopRebuilder`）
+- 循环展开 + 分析 + 重建
+
+**核心流程**：
+```cpp
+class AscendSyncInsert : public IRMutatorWithAnalyzer {
+  // 1. PreprocessUnrollForLoops() - 循环展开预处理
+  // 2. VisitStmt_(EvaluateNode) - 分析内存依赖，插入同步
+  // 3. MergeAndRebuildForLoops() - 合并同步，重建循环
+};
+```
+
+**适用场景**：需要复杂分析和多步处理的 IR 变换。
+
+### 4.2 AscendMemoryPlanning 模式（信息收集 + 计算）
+
+**特点**：
+- 继承 `StmtExprVisitor`（不修改 IR）
+- 收集 buffer 信息 + 计算地址分配
+- 输出 attrs 供后续 Pass 使用
+
+**核心流程**：
+```cpp
+class AscendMemoryPlanner : public StmtExprVisitor {
+  // 1. Substitute() - Pass 入口
+  // 2. VisitStmt_() - 收集 buffer 和 shape 信息
+  // 3. GetAddressMap() - 计算地址分配
+  // 4. 输出 address_map 和 size_map attrs
+};
+```
+
+**适用场景**：信息收集类 Pass，为后续 Pass 提供数据。
+
+### 4.3 CrossCorePipeline 模式（多类协作）
+
+**特点**：
+- 主类 + 辅助类（`CrossCoreDetector` + `LoopAnalyzer` + `LoopRewriter`）
+- 分离检测、分析、重写职责
+
+**核心流程**：
+```cpp
+class CrossCorePipeline : public IRMutatorWithAnalyzer {
+  // 1. CrossCoreDetector - 检测跨核流水线特征
+  // 2. LoopAnalyzer - 分析 Cube/Vector 操作分布
+  // 3. LoopRewriter - 重写为多 stage 流水线
+};
+```
+
+**适用场景**：职责分离、多阶段处理的复杂 Pass。
+
+---
+
+## 5. Attr 读写模式
+
+### 5.1 读取 Attr
+
+```cpp
+// 必需 attrs（缺失时报错或跳过）
+auto required_attr = f->GetAttr<Map<Var, Array<PrimExpr>>>("buffer_shapess");
+if (!required_attr.defined()) {
+  LOG(WARNING) << "buffer_shapess not found";
+  return f;
+}
+
+// 可选 attrs（缺失时使用默认值）
+auto optional_attr = f->GetAttr<Bool>("some_bool", Bool(false));
+```
+
+### 5.2 设置 Attr
+
+```cpp
+// 设置单个 attr
+new_f = f.WithAttr("output_attr", output_data);
+
+// 设置多个 attrs
+new_f = f.WithAttrs({
+  {"address_map", address_map},
+  {"size_map", size_map}
+});
+```
+
+### 5.3 常用 Attr 名称
+
+| Attr 名称 | 类型 | 产生 Pass | 使用 Pass |
+|-----------|------|-----------|-----------|
+| `buffer_shapess` | `Map<Var, Array<PrimExpr>>` | `CollectBufferShapes` | `AscendMemoryPlanning` |
+| `address_map` | `Map<Buffer, PrimExpr>` | `AscendMemoryPlanning` | `AscendSyncInsert` |
+| `size_map` | `Map<Buffer, PrimExpr>` | `AscendMemoryPlanning` | `AscendSyncInsert` |
+| `buffer scope annotations` | `Map<Buffer, String>` | `AscendInferBufferScope` | `CrossCorePipeline`, `CombineCV` |
+
+---
+
+## 6. 配置键注册模式
+
+### 6.1 C++ 配置键
+
+```cpp
+// 定义配置键
+static constexpr const char *kMyPassConfig = "tl.my_pass";
+
+// 注册配置选项
+TVM_REGISTER_PASS_CONFIG_OPTION(kMyPassConfig, Bool);
+// 或其他类型
+TVM_REGISTER_PASS_CONFIG_OPTION(kMyPassConfig, Integer);
+TVM_REGISTER_PASS_CONFIG_OPTION(kMyPassConfig, String);
+```
+
+### 6.2 Pass 内读取配置
+
+```cpp
+static PrimFunc Substitute(PrimFunc f, PassContext ctx) {
+  // 读取配置（带默认值）
+  bool enabled = ctx->GetConfig<Bool>(kMyPassConfig, Bool(false)).value();
+  int threshold = ctx->GetConfig<Integer>(kMyPassThreshold, Integer(100)).value();
+  
+  if (!enabled) {
+    return f;  // 配置为 false 时跳过 Pass
+  }
+  
+  // 使用配置值执行逻辑
+  // ...
+}
+```
+
+### 6.3 Python 配置键定义
+
+```python
+# tilelang/transform/pass_config.py
+class PassConfigKey(str, Enum):
+    TL_MY_PASS = "tl.my_pass"
+    """Enable/disable MyPass. Default: False"""
+    
+    TL_MY_PASS_THRESHOLD = "tl.my_pass_threshold"
+    """Threshold value for MyPass. Default: 100"""
+```
+
+---
+
+## 7. Python Wrapper 模式
+
+### 7.1 基本模式
+
+```python
+# tilelang/transform/__init__.py
+
+import tvm._ffi
+tvm._ffi._init_api("tl.transform", __name__)  # 加载 C++ 注册的函数
+
+def MyPass():
+    """MyPass description.
+    
+    This pass does X, Y, Z.
+    
+    Returns:
+        Pass: The registered pass.
+    """
+    return _ffi_api.MyPass()  # 调用 C++ 注册的函数
+```
+
+### 7.2 带参数的模式
+
+```python
+def MyPassWithParams(target: Target, platform: str):
+    """MyPass with parameters.
+    
+    Args:
+        target: The compilation target.
+        platform: The platform name ("npu" or other).
+    
+    Returns:
+        Pass: The registered pass.
+    """
+    return _ffi_api.MyPassWithParams(target, platform)
+```
+
+---
+
+## 8. 文件组织建议
+
+### 8.1 新 Pass 文件结构
+
+```
+src/transform/
+├── my_pass.cc              # 主实现文件
+└── common/                 # 公共工具（如需）
+    ├── attr.h              # Attr 定义
+    ├── collector.h         # 信息收集器
+    └── operation_config.h  # 操作配置
+```
+
+### 8.2 代码行数参考
+
+| Pass 类型 | 典型行数 | 示例 |
+|-----------|----------|------|
+| 简单信息收集 | 100-300 行 | `BufferShapeCollector` |
+| 简单 IR 变换 | 300-500 行 | `Flatten2DBuffer` |
+| 复杂 IR 变换 | 500-1500 行 | `AscendSyncInsert` (1559行) |
+| 多类协作 | 1000-2000 行 | `CrossCorePipeline` (~1200行) |
+
+---
+
+## 9. 注意事项
+
+### 9.1 IR 变换原则
+
+- **语义保持**：变换后的 IR 必须保持原有计算语义
+- **类型一致**：变换后的类型必须与预期一致
+- **依赖完整**：确保上游依赖数据可用
+
+### 9.2 性能考虑
+
+- **避免深度递归**：对于大型 IR，考虑使用迭代或限制递归深度
+- **缓存中间结果**：重复计算时使用缓存
+- **最小化 IR 修改**：只修改必要部分，避免全量重建
+
+### 9.3 错误处理
+
+- **配置缺失**：配置键缺失时使用默认值，并记录警告
+- **依赖缺失**：上游 attrs 缺失时根据情况报错或跳过
+- **IR 异常**：遇到异常 IR 结构时记录警告并跳过处理
+
+---
+
+## 10. 参考 Pass 列表
+
+| Pass | 文件 | 行数 | 特点 |
+|------|------|------|------|
+| `AscendSyncInsert` | `ascend_sync_insert.cc` | 1559 | 多类协作、循环展开 |
+| `AscendMemoryPlanning` | `ascend_memory_planning.cc` | 884 | 信息收集、地址计算 |
+| `CrossCorePipeline` | `cross_core_pipeline.cc` | ~1200 | 多类协作、流水线规划 |
+| `CombineCV` | `ascend_combinecv.cc` | ~700 | Cube/Vector 分离 |
+| `AscendLowerParallelToVector` | `ascend_lower_parallel_to_vector.cc` | ~2000 | Parallel lowering |
+| `AscendStorageRewrite` | `ascend_storage_rewrite.cc` | ~2200 | 存储优化 |
+| `InferAllocScope` | `ascend_infer_buffer_scope.cc` | ~900 | Scope 推断 |
+
+**建议**：设计新 Pass 时，参考功能相似的现有 Pass 实现结构。
\ No newline at end of file
diff --git a/.agents/skills/tilelang-pass-design/templates/pass-design-template.md b/.agents/skills/tilelang-pass-design/templates/pass-design-template.md
@@ -0,0 +1,426 @@
+# {Pass 名称} Pass 设计文档
+
+## 1. 概述
+
+### 1.1 Pass 名称
+
+{Pass 名称}
+
+### 1.2 功能描述
+
+{一句话描述 Pass 的功能}
+
+### 1.3 解决的问题
+
+{描述 Pass 要解决的具体问题，如：现有编译流程中缺少某种优化、某些 IR 结构不合法、需要收集特定信息等}
+
+### 1.4 Pass 类型
+
+| 类型 | 说明 |
+|------|------|
+| **IR 变换类型** | {修改 IR / 收集信息 / 验证 IR} |
+| **平台范围** | {平台无关 / Ascend 特定} |
+| **优化类别** | {Lowering / 合法化 / 内存 / 流水线 / 同步 / 信息收集 / 其他} |
+
+---
+
+## 2. Pass 定位
+
+### 2.1 阶段归属
+
+**阶段**: {Phase 1: LowerAndLegalize / Phase 2: OptimizeForTarget}
+
+### 2.2 选型理由
+
+{基于以下四个原则的分析结果}
+
+| 原则 | 分析结果 |
+|------|----------|
+| **功能归属** | {如：属于硬件优化，应放在 Phase 2} |
+| **数据依赖** | {如：需要 buffer_shapess（来自 Phase 1），可放在 Phase 2} |
+| **输出供给** | {如：产生 address_map，供 AscendSyncInsert 使用，必须在 Phase 2} |
+| **语义范围** | {如：Ascend 特定优化，放在 Phase 2} |
+
+### 2.3 Pipeline 位置
+
+**具体位置**: {如：Phase 2，步骤 13，在 `AscendStorageRewrite` 后，`tir.transform.UnrollLoop` 前}
+
+**位置代码示例**:
+```python
+# tilelang/engine/phase.py
+def OptimizeForTarget(mod, target, platform):
+    # ... (步骤 1-12)
+    mod = tir.transform.PlanAndUpdateBufferAllocationLocation()(mod)
+    # ... (步骤 2-12)
+    mod = AscendStorageRewrite(is_npu)(mod)  # 步骤 13
+    # ===== 新增 Pass =====
+    mod = {Pass名称}()(mod)  # 步骤 X
+    # =====
+    mod = tir.transform.UnrollLoop()(mod)  # 步骤 14
+    # ... (后续 Pass)
+```
+
+### 2.4 依赖关系分析
+
+#### 上游依赖（输入数据）
+
+| 数据名称 | 产生 Pass | 阶段 | 获取方式 |
+|----------|-----------|------|----------|
+| {buffer scope} | `AscendInferBufferScope` | Phase 1 步骤 1 | `f->GetAttr<Map<...>>(...)` |
+| {buffer_shapess} | `CollectBufferShapes` | Phase 1 步骤 8 | `f->GetAttr<Map<Var, Array<PrimExpr>>>(...)` |
+| {address_map} | `AscendMemoryPlanning` | Phase 2 步骤 20 | `f->GetAttr<Map<...>>(...)` |
+| ... | ... | ... | ... |
+
+#### 下游供给（输出数据）
+
+| 数据名称 | 使用 Pass | 阶段 | 传递方式 |
+|----------|-----------|------|----------|
+| {output_attr} | {PassA} | Phase X | `f->attrs[...]` |
+| ... | ... | ... | ... |
+
+### 2.5 数据流图
+
+```
+Phase 1 / Phase 2 前序 Pass
+    ↓
+    输出: {数据A}, {数据B}
+    ↓
+[{Pass名称}] ← 本 Pass
+    ↓
+    输出: {数据C}, {数据D}
+    ↓
+Phase X 后续 Pass
+```
+
+---
+
+## 3. IR 变换设计
+
+### 3.1 输入 IR 结构
+
+**伪 IR 示例**（本示例为伪 IR 格式，真实 TIR 结构见 ir-examples.md）:
+
+```
+# 变换前的 IR 结构
+PrimFunc {
+  attrs: {
+    {已有 attrs}
+  }
+  body: {
+    # {关键 IR 结构描述}
+    ForNode {
+      loop_var: i
+      body: {
+        BufferStoreNode { ... }
+      }
+    }
+  }
+}
+```
+
+### 3.2 输出 IR 结构
+
+**伪 IR 示例**:
+
+```
+# 变换后的 IR 结构
+PrimFunc {
+  attrs: {
+    {新增 attrs ←}
+    {已有 attrs}
+  }
+  body: {
+    # {变换后的 IR 结构 ←}
+    ForNode {
+      loop_var: i
+      body: {
+        BufferStoreNode { ... }  ← {变化说明}
+        EvaluateNode { ... }     ← {新增节点}
+      }
+    }
+  }
+}
+```
+
+### 3.3 变换逻辑伪代码
+
+```python
+# 伪代码示例 (精简版)
+
+输入: PrimFunc
+处理流程:
+  1. 遍历 IR 结构 → VisitStmt_()           # [备注: 深度优先遍历特定节点]
+  2. 匹配目标模式 → MatchPattern()         # [备注: 检查是否为特定 IR 结构]
+  3. 执行变换操作 → TransformStmt()        # [备注: 生成新 IR 或收集信息]
+  4. 更新 attrs → UpdateAttrs()            # [备注: 如需输出数据，设置 attrs]
+输出: 变换后的 PrimFunc
+
+# 关键点备注
+- VisitStmt_: 继承 IRMutatorWithAnalyzer/StmtExprVisitor
+- MatchPattern: 检查 buffer scope、op type 等属性
+- TransformStmt: 根据规则生成新语句或收集信息
+```
+
+### 3.4 变换要点
+
+- **变化点1**: {如：新增 EvaluateNode 插入同步指令}
+- **变化点2**: {如：修改 BufferStoreNode 的访问模式}
+- **保持语义**: {如：变换后保持计算语义不变，仅优化执行顺序}
+
+---
+
+## 4. 实现方案
+
+### 4.1 C++ 类设计
+
+**核心类**: `{类名}` (继承 `{父类名}`)
+
+**父类选择依据**:
+| 父类 | 适用场景 | 本 Pass 选择 |
+|------|----------|--------------|
+| `IRMutatorWithAnalyzer` | 修改 IR 结构 | {选择理由} |
+| `StmtExprVisitor` | 收集信息、不修改 IR | {选择理由} |
+| `StmtExprMutator` | 简单 IR 变换 | {选择理由} |
+
+### 4.2 核心方法
+
+| 方法名 | 功能 | 关键逻辑 |
+|--------|------|----------|
+| `Substitute()` | Pass 入口 | 读取 attrs → 执行变换 → 返回 PrimFunc |
+| `VisitStmt_(NodeType)` | 处理特定节点 | {匹配 → 变换逻辑} |
+| `MatchPattern()` | 模式匹配 | {检查条件} |
+| `TransformStmt()` | 执行变换 | {生成新 IR} |
+| `UpdateAttrs()` | 更新 attrs | {设置输出数据} |
+
+### 4.3 C++ 实现代码框架
+
+```cpp
+// 文件: src/transform/{pass_name}.cc
+
+namespace tvm {
+namespace tl {
+
+class {类名} : public arith::IRMutatorWithAnalyzer {  // 或 StmtExprVisitor
+public:
+  static PrimFunc Substitute(PrimFunc f, PassContext ctx) {
+    // 1. 读取输入 attrs（如有依赖）
+    auto input_attr = f->GetAttr<Map<...>>("attr_name").value();
+    
+    // 2. 创建变换器实例
+    {类名} mutator(f, ctx, input_attr);
+    
+    // 3. 执行变换
+    PrimFunc new_f = mutator.MutateFunc(f);
+    
+    // 4. 设置输出 attrs（如有输出）
+    new_f = new_f.WithAttrs({{"output_attr", output_data}});
+    
+    return new_f;
+  }
+  
+private:
+  // 成员变量
+  Map<...> input_attr_;
+  
+  // 核心方法
+  Stmt VisitStmt_(const ForNode* op) final {
+    // 处理 For 节点
+    // ...
+  }
+  
+  Stmt VisitStmt_(const BufferStoreNode* op) final {
+    // 处理 BufferStore 节点
+    // ...
+  }
+  
+  // 辅助方法
+  bool MatchPattern(/* params */) {
+    // 模式匹配逻辑
+  }
+  
+  Stmt TransformStmt(/* params */) {
+    // 变换逻辑
+  }
+};
+
+// Pass 注册
+tvm::transform::Pass {Pass名称}() {
+  auto pass_func = [=](PrimFunc f, IRModule m, PassContext ctx) {
+    return {类名}::Substitute(std::move(f), ctx);
+  };
+  return CreatePrimFuncPass(pass_func, 0, "tl.{Pass名称}", {});
+}
+
+TVM_REGISTER_GLOBAL("tl.transform.{Pass名称}")
+    .set_body_typed({Pass名称});
+
+// 配置键（可选）
+static constexpr const char *k{Pass名称}Config = "tl.{pass_name}";
+TVM_REGISTER_PASS_CONFIG_OPTION(k{Pass名称}Config, Bool);
+
+} // namespace tl
+} // namespace tvm
+```
+
+### 4.4 Python Wrapper
+
+**文件**: `tilelang/transform/__init__.py`
+
+```python
+def {Pass名称}():
+    """{功能描述}。
+    
+    Returns:
+        Pass: The registered pass.
+    """
+    return _ffi_api.{Pass名称}()
+```
+
+### 4.5 配置键（可选）
+
+**文件**: `tilelang/transform/pass_config.py`
+
+```python
+class PassConfigKey(str, Enum):
+    TL_{PASS_NAME_UPPER} = "tl.{pass_name}"
+    """Enable/disable {Pass名称}. Default: False"""
+```
+
+**Pass 内读取配置**:
+```cpp
+bool config_enabled = ctx->GetConfig<Bool>(k{Pass名称}Config, Bool(false)).value();
+if (!config_enabled) {
+  return f;  // 配置为 false 时跳过该 Pass
+}
+```
+
+### 4.6 Pipeline 集成代码
+
+**文件**: `tilelang/engine/phase.py`
+
+```python
+# Phase 1 集成示例
+def LowerAndLegalize(mod, target):
+    # ... (现有 Pass)
+    mod = LowerTileOp()(mod)  # 步骤 9
+    # ===== 新增 Pass =====
+    mod = {Pass名称}()(mod)  # 步骤 X
+    # =====
+    mod = LegalizeVectorizedLoop()(mod)  # 步骤 10
+    # ...
+    return mod
+
+# 或 Phase 2 集成示例
+def OptimizeForTarget(mod, target, platform):
+    # ... (现有 Pass)
+    mod = AscendStorageRewrite(is_npu)(mod)  # 步骤 13
+    # ===== 新增 Pass =====
+    mod = {Pass名称}()(mod)  # 步骤 X
+    # =====
+    mod = tir.transform.UnrollLoop()(mod)  # 步骤 14
+    # ...
+    return mod
+```
+
+---
+
+## 5. 测试方案
+
+### 5.1 功能测试
+
+| 测试项 | 测试内容 | 验证方法 |
+|--------|----------|----------|
+| {基础功能} | {变换后的 IR 是否正确} | {检查 attrs / IR 结构} |
+| {输入依赖} | {能否正确读取上游 attrs} | {设置 mock attrs 测试} |
+| {输出供给} | {能否正确设置下游 attrs} | {检查 attrs 是否可被后续 Pass 读取} |
+
+### 5.2 依赖测试
+
+| 测试项 | 测试内容 |
+|--------|----------|
+| **上游缺失** | 当上游 attrs 缺失时，Pass 是否正确处理（报错 / 跳过） |
+| **顺序错误** | 当 Pass 执行顺序错误时，编译是否失败 |
+
+### 5.3 边界测试
+
+| 测试项 | 测试内容 |
+|--------|----------|
+| **空 IR** | 当 IR 为空或无目标节点时，Pass 是否正确处理 |
+| **极端数据** | 当 attrs 包含极端值（空 map、超大 size）时，Pass 是否正确处理 |
+
+### 5.4 性能测试（可选）
+
+| 测试项 | 测试内容 | 指标 |
+|--------|----------|------|
+| {编译时间} | Pass 是否显著增加编译时间 | {时间阈值} |
+| {生成代码性能} | Pass 是否改善生成代码性能 | {吞吐量/延迟} |
+
+---
+
+## 6. 风险点与注意事项
+
+### 6.1 已知约束
+
+{列出本 Pass 在 TileLang-Ascend 上的已知限制}
+
+### 6.2 常见错误
+
+| 错误 | 触发场景 | 影响 | 解决方案 |
+|------|----------|------|----------|
+| {attrs 缺失} | {上游 Pass 未执行} | {编译失败} | {检查 Pass 顺序} |
+| {IR 结构不符} | {输入 IR 不符合预期} | {变换失败} | {添加前置检查} |
+| ... | ... | ... | ... |
+
+### 6.3 与其他 Pass 的交互影响
+
+| Pass | 交互关系 | 需要注意的点 |
+|------|----------|--------------|
+| {PassA} | {上游依赖} | {必须在本 Pass 前执行} |
+| {PassB} | {下游供给} | {本 Pass 输出必须符合 PassB 预期} |
+| {PassC} | {功能冲突} | {不能同时启用} |
+
+---
+
+## 7. 交付清单
+
+### 7.1 目录结构
+
+```
+src/transform/
+├── {pass_name}.cc           # C++ 实现
+└── common/                  # 公共工具（如需新增）
+
+tilelang/transform/
+├── __init__.py              # Python Wrapper
+└── pass_config.py           # 配置键（如需新增）
+
+tilelang/engine/
+└── phase.py                 # Pipeline 集成
+```
+
+### 7.2 文件清单
+
+| 文件 | 状态 | 说明 |
+|------|------|------|
+| `src/transform/{pass_name}.cc` | {待实现} | C++ 实现 |
+| `tilelang/transform/__init__.py` | {待修改} | 添加 Python Wrapper |
+| `tilelang/transform/pass_config.py` | {待修改（可选）} | 添加配置键 |
+| `tilelang/engine/phase.py` | {待修改} | Pipeline 集成 |
+| `pass-design.md` | {已完成} | 本设计文档 |
+
+### 7.3 实现顺序
+
+1. ✅ 设计文档（pass-design.md）
+2. ⬜ C++ 实现（src/transform/{pass_name}.cc）
+3. ⬜ Python Wrapper（tilelang/transform/__init__.py）
+4. ⬜ 配置键（可选）
+5. ⬜ Pipeline 集成（tilelang/engine/phase.py）
+6. ⬜ 功能测试
+7. ⬜ 依赖测试
+
+### 7.4 后续步骤
+
+完成本设计文档后，建议：
+1. 使用 **tilelang-pass-workflow-analyzer** skill 查看详细 Pass 工作流
+2. 使用 **tilelang-pass-analyzer** skill 查看类似 Pass 的实现细节
+3. 开始 C++ 实现前，参考 `src/transform/` 中相似 Pass 的代码结构
\ No newline at end of file
PATCH

echo "Gold patch applied."
