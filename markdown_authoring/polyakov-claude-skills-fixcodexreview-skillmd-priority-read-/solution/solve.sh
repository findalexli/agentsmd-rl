#!/usr/bin/env bash
set -euo pipefail

cd /workspace/polyakov-claude-skills

# Idempotency guard
if grep -qF "\u0412\u0441\u0435 \u043a\u043e\u043c\u0430\u043d\u0434\u044b \u043d\u0438\u0436\u0435 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u044e\u0442 \u043e\u0442\u043d\u043e\u0441\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0439 `scripts/` \u2014 \u043f\u043e\u0434\u0441\u0442\u0430\u0432\u044c \u043f\u043e\u043b\u043d\u044b\u0439 \u043f\u0443\u0442\u044c \u043f\u0440\u0438 " "plugins/codex-review/skills/codex-review/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/codex-review/skills/codex-review/SKILL.md b/plugins/codex-review/skills/codex-review/SKILL.md
@@ -5,12 +5,21 @@ description: |
   Triggers (RU): "кодекс ревью".
   Triggers (EN): "with codex review", "codex review workflow",
   "start codex review".
+  ВАЖНО: при срабатывании триггера прочитай SKILL.md до любых других шагов.
 ---
 
 # Codex Review Workflow
 
 Кросс-агентное ревью: Claude реализует, Codex (GPT) ревьюит. Codex работает в той же директории и может самостоятельно смотреть код.
 
+## Расположение скриптов
+
+Скрипты лежат в `scripts/` рядом с этим SKILL.md. Определи полный путь:
+- Этот файл: путь из которого ты прочитал SKILL.md
+- Скрипты: замени `SKILL.md` на `scripts/codex-review.sh` (и `scripts/codex-state.sh`)
+
+Все команды ниже используют относительный `scripts/` — подставь полный путь при вызове.
+
 ## Workflow
 
 ### 1. Инициализация сессии
PATCH

echo "Gold patch applied."
