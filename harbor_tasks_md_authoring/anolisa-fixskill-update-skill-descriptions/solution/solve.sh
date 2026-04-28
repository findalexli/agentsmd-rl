#!/usr/bin/env bash
set -euo pipefail

cd /workspace/anolisa

# Idempotency guard
if grep -qF "description: Install and configure Claude Code on RPM-based Linux systems (e.g.," "src/os-skills/ai/install-claude-code/SKILL.md" && grep -qF "description: \u5728 RPM \u5305\u7ba1\u7406\u7684 Linux \u670d\u52a1\u5668\uff08\u5982 Alibaba Cloud Linux\uff09\u4e0a\u5b89\u88c5\u548c\u914d\u7f6e OpenClaw\uff0c\u63a5\u5165\u9489\u9489\u9891\u9053\u4e0e\u963f" "src/os-skills/ai/install-openclaw/SKILL.md" && grep -qF "description: Linux \u5185\u6838\u7814\u53d1\u81ea\u52a8\u5316\u6280\u80fd\uff08RPM \u5305\u7ba1\u7406\u7cfb\u7edf\uff09\uff0c\u63d0\u4f9b\u5185\u6838\u7f16\u8bd1\uff08SRPM/Upstream \u53cc\u65b9\u6cd5\uff09\u3001\u5185\u6838 module \u5f00\u53d1\u73af\u5883" "src/os-skills/devops/kernel-dev/SKILL.md" && grep -qF "description: \u5904\u7406\u6240\u6709\u5907\u4efd\u4e0e\u6062\u590d\u4efb\u52a1\uff0c\u8986\u76d6\u56db\u4e2a\u5c42\u9762\uff1a\u5de5\u4f5c\u533a\uff08\u9879\u76ee/\u6570\u636e\u5e93/\u4ee3\u7801\uff09\u3001\u7528\u6237\u6570\u636e\uff08\u5bb6\u76ee\u5f55/dotfiles/\u5bc6\u94a5\uff09\u3001\u64cd\u4f5c\u7cfb\u7edf\uff08\u5168\u91cf\u7cfb\u7edf/\u78c1" "src/os-skills/system-admin/backup-restore/SKILL.md" && grep -qF "description: Linux \u78c1\u76d8\u6269\u5bb9\u6280\u80fd\uff08RPM \u5305\u7ba1\u7406\u7cfb\u7edf\uff09\uff0c\u5b9e\u73b0\u4e91\u76d8\u6269\u5bb9\u540e\u81ea\u52a8\u5b8c\u6210\u5206\u533a\u8c03\u6574\u548c\u6587\u4ef6\u7cfb\u7edf\u6269\u5bb9\u3002\u652f\u6301\u7cfb\u7edf\u76d8/\u6570\u636e\u76d8\u5728\u7ebf\u6269\u5bb9\uff0c\u9002\u914d XFS" "src/os-skills/system-admin/storage-resize/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/os-skills/ai/install-claude-code/SKILL.md b/src/os-skills/ai/install-claude-code/SKILL.md
@@ -1,7 +1,7 @@
 ---
 name: install-claude-code-linux
 version: 1.0.0
-description: Install and configure Claude Code on Alibaba Cloud Linux 4 (Alinux 4) with multiple fallback methods (native installer, npm, nvm+npm). Includes DashScope/Qwen API configuration template. Use when the user asks to install Claude Code on Alinux 4, set up Claude Code CLI, or configure Claude Code with a custom API endpoint.
+description: Install and configure Claude Code on RPM-based Linux systems (e.g., Alibaba Cloud Linux) with multiple fallback methods (native installer, npm, nvm+npm). Includes DashScope/Qwen API configuration template. Use when the user asks to install Claude Code CLI, set up Claude Code CLI, or configure Claude Code with a custom API endpoint on RPM-based Linux systems.
 layer: application
 lifecycle: usage
 ---
@@ -10,7 +10,7 @@ lifecycle: usage
 
 ## System Requirements
 
-- **OS**: Alibaba Cloud Linux 4
+- **OS**: Linux
 - **RAM**: 4 GB+
 - **Network**: 需要联网
 - **Shell**: Bash
diff --git a/src/os-skills/ai/install-openclaw/SKILL.md b/src/os-skills/ai/install-openclaw/SKILL.md
@@ -1,7 +1,7 @@
 ---
 name: install-openclaw
 version: 1.0.0
-description: "在 Alibaba Cloud Linux 4 (Alinux 4) 服务器上安装和配置 OpenClaw，接入钉钉频道与阿里云百炼（通义千问）模型。当用户需要部署 OpenClaw、配置钉钉机器人、接入 DashScope/Qwen 模型、排查 OpenClaw 网关无法启动、或遇到插件不加载等问题时使用此技能。包含完整踩坑记录与正确配置结构。"
+description: 在 RPM 包管理的 Linux 服务器（如 Alibaba Cloud Linux）上安装和配置 OpenClaw，接入钉钉频道与阿里云百炼（通义千问）模型。当用户需要部署 OpenClaw、配置钉钉机器人、接入 DashScope/Qwen 模型、排查 OpenClaw 网关无法启动、或遇到插件不加载等问题时使用此技能。包含完整踩坑记录与正确配置结构。
 layer: application
 lifecycle: usage
 ---
@@ -31,7 +31,7 @@ install-openclaw/
 **优先使用系统包管理器（推荐）**
 
 ```bash
-# alinux4 仓库自带 Node.js 22
+# Linux 仓库自带 Node.js 22
 dnf install -y nodejs
 node -v && npm -v
 ```
diff --git a/src/os-skills/devops/kernel-dev/SKILL.md b/src/os-skills/devops/kernel-dev/SKILL.md
@@ -1,12 +1,12 @@
 ---
 name: kernel-dev
 version: 1.0.0
-description: 阿里云 Alinux4 内核研发自动化技能，提供内核编译（SRPM/Upstream 双方法）、内核 module 开发环境搭建、依赖安装、示例代码生成等功能。支持 Alinux4 官方内核及上游最新内核，兼容 x86_64 和 aarch64 双架构。使用场景：内核定制开发、驱动模块研发、内核漏洞修复验证。
+description: Linux 内核研发自动化技能（RPM 包管理系统），提供内核编译（SRPM/Upstream 双方法）、内核 module 开发环境搭建、依赖安装、示例代码生成等功能。Linux 官方内核及上游最新内核，兼容 x86_64 和 aarch64 双架构。使用场景：内核定制开发、驱动模块研发、内核漏洞修复验证。适用于 RPM 包管理的 Linux 系统（如 Alibaba Cloud Linux）。
 layer: core
 lifecycle: production
 ---
 
-# Kernel Development - Alinux4 内核研发自动化
+# Kernel Development - Linux 内核研发自动化
 
 ## 核心定位
 
@@ -25,7 +25,7 @@ lifecycle: production
 
 **重要约束：**
 - 🔒 需要 root 权限执行内核相关操作
-- 📦 仅支持 Alinux4 (alnx4) 操作系统
+- 📦 仅Linux操作系统
 - ⚠️ 内核编译会消耗大量系统资源（建议至少 4GB 内存）
 - ⏱️ 编译时间：SRPM 方法 1-3 小时，Upstream 方法 30-60 分钟
 
diff --git a/src/os-skills/system-admin/backup-restore/SKILL.md b/src/os-skills/system-admin/backup-restore/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: backup-restore
-description: 处理所有备份与恢复任务，覆盖四个层面：工作区（项目/数据库/代码）、用户数据（家目录/dotfiles/密钥）、操作系统（全量系统/磁盘镜像/LVM快照）、阿里云快照（云盘快照/自动策略/跨地域复制/整机镜像）。适用于 Alibaba Cloud Linux 4 (ALinux 4) 纯命令行环境，使用 yum 包管理器。当用户提到备份、恢复、快照、归档、回滚、克隆、迁移、容灾等任何涉及数据保存或恢复的请求时触发此技能，即使请求看起来很简单也应使用。
+description: 处理所有备份与恢复任务，覆盖四个层面：工作区（项目/数据库/代码）、用户数据（家目录/dotfiles/密钥）、操作系统（全量系统/磁盘镜像/LVM 快照）、阿里云快照（云盘快照/自动策略/跨地域复制/整机镜像）。适用于 RPM 包管理的 Linux 系统（如 Alibaba Cloud Linux）纯命令行环境，使用 yum 包管理器。当用户提到备份、恢复、快照、归档、回滚、克隆、迁移、容灾等任何涉及数据保存或恢复的请求时触发此技能，即使请求看起来很简单也应使用。
 author: aliyun
 layer: runtime
 version: 0.1.0
@@ -17,7 +17,7 @@ status: beta
 
 本技能处理**四个层面**的备份与恢复操作。执行前务必先探测环境、识别场景，再选择合适的层面。
 
-> 适用环境：Alibaba Cloud Linux 4 (ALinux 4) / 纯命令行 / yum 包管理器
+> 适用环境：Linux / 纯命令行 / yum 包管理器
 
 ---
 
diff --git a/src/os-skills/system-admin/storage-resize/SKILL.md b/src/os-skills/system-admin/storage-resize/SKILL.md
@@ -1,7 +1,7 @@
 ---
 name: storage-resize
 version: 1.0.0
-description: 阿里云 Alinux4 磁盘扩容技能，实现云盘扩容后自动完成分区调整和文件系统扩容。支持系统盘/数据盘在线扩容，适配 XFS/EXT4/Btrfs 文件系统。
+description: Linux 磁盘扩容技能（RPM 包管理系统），实现云盘扩容后自动完成分区调整和文件系统扩容。支持系统盘/数据盘在线扩容，适配 XFS/EXT4/Btrfs 文件系统。适用于 RPM 包管理的 Linux 系统（如 Alibaba Cloud Linux）。
 layer: system
 lifecycle: operations
 dependencies:
PATCH

echo "Gold patch applied."
