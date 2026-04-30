# Yeni skill: server-security-audit (Kastell)

Source: [komunite/kalfa#18](https://github.com/komunite/kalfa/pull/18)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/development/server-security-audit/SKILL.md`

## What to add / change

## Özet

Development kategorisine sunucu güvenlik denetimi ve sertleştirme skill'i ekler.

[Kastell](https://github.com/kastelldev/kastell) MCP araçlarıyla:
- **468+ güvenlik kontrolü**, 31 kategori
- **CIS/PCI-DSS/HIPAA** uyumluluk haritalama
- **24 adımlı** production sertleştirme
- **14 MCP tool** — otomatik fix dahil (SAFE/FORBIDDEN tier sistemi)
- **Filo yönetimi**: birden fazla sunucuyu tek noktadan izle
- **9,611 test**, 215 suite, %90+ coverage

## Neden Development Kategorisi?

DevOps / altyapı güvenliği, yazılım geliştirme sürecinin ayrılmaz parçası. Production'a deploy etmeden önce sunucu güvenliğinin sağlanması gerekiyor. Mevcut skill'lerle (api-gateway-design, blue-green-deployment, alerting-strategy) tamamlayıcı.

## Yenilikler (v1.15+)

- `server_fix` MCP tool — audit→backup→fix→score pipeline
- TypeScript FORBIDDEN tier — SSH/Firewall/Docker asla otomatik değiştirilmez
- DDoS hardening + Edge/WAF audit kategorileri
- Telegram bot (5 komut: /status /audit /health /doctor /help)
- 34 CLI komut, 468+ check, 9,611 test

## Bağımlılık

`claude plugins add kastell` ile kurulur.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
