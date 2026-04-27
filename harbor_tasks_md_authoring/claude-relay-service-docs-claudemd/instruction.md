# docs: 全面更新 CLAUDE.md 文档以反映最新代码实现

Source: [Wei-Shaw/claude-relay-service#570](https://github.com/Wei-Shaw/claude-relay-service/pull/570)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## 更新概要

本次更新全面审查了代码库，将严重过期的 CLAUDE.md 文档更新到与当前实现一致。

## 主要更新内容

### 1. 项目概述和架构
- 更新为多平台支持（8种账户类型）
- 添加统一调度系统说明
- 补充权限控制、客户端限制、模型黑名单等新功能

### 2. 服务组件
- 从5个服务扩展到30+个服务的完整列表
- 新增核心转发服务（8个）
- 新增账户管理服务（10个）
- 新增统一调度器（4个）
- 新增核心功能服务（用户管理、定价、Webhook、LDAP等）

### 3. 环境变量配置
- 新增20+个重要环境变量说明
- 添加AWS Bedrock配置
- 添加用户管理、LDAP、Webhook配置说明

### 4. API端点
- 更新为多路由支持（Claude、Gemini、OpenAI、Droid、Azure）
- 新增用户管理端点
- 新增Webhook管理端点
- 新增系统指标端点

### 5. Redis数据结构
- 扩展为8种账户类型的数据结构
- 添加用户管理、粘性会话、并发控制相关键
- 添加成本统计、Webhook配置相关键

### 6. 故障排除
- 从4个问题扩展到13个常见问题
- 新增粘性会话、LDAP、Webhook、调度器等问题解决方案

### 7. CLI工具
- 添加数据导入导出命令
- 添加数据迁移和修复命令
- 添加成本初始化和定价更新命令

### 8. 新增功能概览章节
- 列出相比旧版本的所有新增功能
- 包括多平台支持、用户权限系统、统一调度、成本监控等

## 技术细节

- 保持所有现有章节结构
- 使用 Prettier 格式化确保代码风格一致
- 基于实际代码审查（src/services/、src/routes/、config/等）
- 确保所有端点、配置项、数据结构与代码实现一致

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
