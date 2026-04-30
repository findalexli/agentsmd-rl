"""Behavioral checks for anolisa-fixskill-update-skill-descriptions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/anolisa")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('src/os-skills/ai/install-claude-code/SKILL.md')
    assert 'description: Install and configure Claude Code on RPM-based Linux systems (e.g., Alibaba Cloud Linux) with multiple fallback methods (native installer, npm, nvm+npm). Includes DashScope/Qwen API confi' in text, "expected to find: " + 'description: Install and configure Claude Code on RPM-based Linux systems (e.g., Alibaba Cloud Linux) with multiple fallback methods (native installer, npm, nvm+npm). Includes DashScope/Qwen API confi'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/os-skills/ai/install-claude-code/SKILL.md')
    assert '- **OS**: Linux' in text, "expected to find: " + '- **OS**: Linux'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/os-skills/ai/install-openclaw/SKILL.md')
    assert 'description: 在 RPM 包管理的 Linux 服务器（如 Alibaba Cloud Linux）上安装和配置 OpenClaw，接入钉钉频道与阿里云百炼（通义千问）模型。当用户需要部署 OpenClaw、配置钉钉机器人、接入 DashScope/Qwen 模型、排查 OpenClaw 网关无法启动、或遇到插件不加载等问题时使用此技能。包含完整踩坑记录与正确配置结构。' in text, "expected to find: " + 'description: 在 RPM 包管理的 Linux 服务器（如 Alibaba Cloud Linux）上安装和配置 OpenClaw，接入钉钉频道与阿里云百炼（通义千问）模型。当用户需要部署 OpenClaw、配置钉钉机器人、接入 DashScope/Qwen 模型、排查 OpenClaw 网关无法启动、或遇到插件不加载等问题时使用此技能。包含完整踩坑记录与正确配置结构。'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('src/os-skills/ai/install-openclaw/SKILL.md')
    assert '# Linux 仓库自带 Node.js 22' in text, "expected to find: " + '# Linux 仓库自带 Node.js 22'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('src/os-skills/devops/kernel-dev/SKILL.md')
    assert 'description: Linux 内核研发自动化技能（RPM 包管理系统），提供内核编译（SRPM/Upstream 双方法）、内核 module 开发环境搭建、依赖安装、示例代码生成等功能。Linux 官方内核及上游最新内核，兼容 x86_64 和 aarch64 双架构。使用场景：内核定制开发、驱动模块研发、内核漏洞修复验证。适用于 RPM 包管理的 Linux 系统（如 Alibaba ' in text, "expected to find: " + 'description: Linux 内核研发自动化技能（RPM 包管理系统），提供内核编译（SRPM/Upstream 双方法）、内核 module 开发环境搭建、依赖安装、示例代码生成等功能。Linux 官方内核及上游最新内核，兼容 x86_64 和 aarch64 双架构。使用场景：内核定制开发、驱动模块研发、内核漏洞修复验证。适用于 RPM 包管理的 Linux 系统（如 Alibaba '[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('src/os-skills/devops/kernel-dev/SKILL.md')
    assert '# Kernel Development - Linux 内核研发自动化' in text, "expected to find: " + '# Kernel Development - Linux 内核研发自动化'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('src/os-skills/devops/kernel-dev/SKILL.md')
    assert '- 📦 仅Linux操作系统' in text, "expected to find: " + '- 📦 仅Linux操作系统'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('src/os-skills/system-admin/backup-restore/SKILL.md')
    assert 'description: 处理所有备份与恢复任务，覆盖四个层面：工作区（项目/数据库/代码）、用户数据（家目录/dotfiles/密钥）、操作系统（全量系统/磁盘镜像/LVM 快照）、阿里云快照（云盘快照/自动策略/跨地域复制/整机镜像）。适用于 RPM 包管理的 Linux 系统（如 Alibaba Cloud Linux）纯命令行环境，使用 yum 包管理器。当用户提到备份、恢复、快照、归档、' in text, "expected to find: " + 'description: 处理所有备份与恢复任务，覆盖四个层面：工作区（项目/数据库/代码）、用户数据（家目录/dotfiles/密钥）、操作系统（全量系统/磁盘镜像/LVM 快照）、阿里云快照（云盘快照/自动策略/跨地域复制/整机镜像）。适用于 RPM 包管理的 Linux 系统（如 Alibaba Cloud Linux）纯命令行环境，使用 yum 包管理器。当用户提到备份、恢复、快照、归档、'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('src/os-skills/system-admin/backup-restore/SKILL.md')
    assert '> 适用环境：Linux / 纯命令行 / yum 包管理器' in text, "expected to find: " + '> 适用环境：Linux / 纯命令行 / yum 包管理器'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('src/os-skills/system-admin/storage-resize/SKILL.md')
    assert 'description: Linux 磁盘扩容技能（RPM 包管理系统），实现云盘扩容后自动完成分区调整和文件系统扩容。支持系统盘/数据盘在线扩容，适配 XFS/EXT4/Btrfs 文件系统。适用于 RPM 包管理的 Linux 系统（如 Alibaba Cloud Linux）。' in text, "expected to find: " + 'description: Linux 磁盘扩容技能（RPM 包管理系统），实现云盘扩容后自动完成分区调整和文件系统扩容。支持系统盘/数据盘在线扩容，适配 XFS/EXT4/Btrfs 文件系统。适用于 RPM 包管理的 Linux 系统（如 Alibaba Cloud Linux）。'[:80]

