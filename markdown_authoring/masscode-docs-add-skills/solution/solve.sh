#!/usr/bin/env bash
set -euo pipefail

cd /workspace/masscode

# Idempotency guard
if grep -qF "\u0414\u043b\u044f massCode API types \u0441\u0447\u0438\u0442\u0430\u044e\u0442\u0441\u044f generated-first. \u0415\u0441\u043b\u0438 \u0434\u0430\u043d\u043d\u044b\u0435 \u043f\u0440\u0438\u0448\u043b\u0438 \u0438\u0437 `~/rende" ".agents/skills/api-and-typing/SKILL.md" && grep -qF "\u0411\u0430\u0437\u043e\u0432\u044b\u0439 \u043f\u0440\u0438\u043d\u0446\u0438\u043f \u043f\u0440\u043e\u0435\u043a\u0442\u0430: **YAGNI \u0438 \u043f\u0440\u043e\u0441\u0442\u043e\u0442\u0430 \u043f\u0440\u0435\u0436\u0434\u0435 \u0432\u0441\u0435\u0433\u043e**. \u041d\u0435 \u0443\u0441\u043b\u043e\u0436\u043d\u044f\u0439 \u043a\u043e\u0434 \u0440\u0430\u0434\u0438" ".agents/skills/architecture-standards/SKILL.md" && grep -qF "\u0412 massCode workflow rules \u0441\u0447\u0438\u0442\u0430\u044e\u0442\u0441\u044f \u0447\u0430\u0441\u0442\u044c\u044e \u043a\u0430\u0447\u0435\u0441\u0442\u0432\u0430 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0439. \u0414\u043b\u044f \u043b\u043e\u043a\u0430\u043b\u044c\u043d\u043e\u0439 \u0437\u0430\u0434" ".agents/skills/development-workflow/SKILL.md" && grep -qF "description: Use when changing massCode API routes, DTOs, IPC handlers, Electron" ".agents/skills/electron-api-and-ipc/SKILL.md" && grep -qF "\u0421\u043e\u0437\u0434\u0430\u0432\u0430\u0439 \u0432\u0435\u0442\u043a\u0443 \u043e\u0442 `main` \u0441 \u043f\u0440\u0435\u0444\u0438\u043a\u0441\u043e\u043c \u043f\u043e \u0442\u0438\u043f\u0443 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f (`feat/`, `fix/`, `chore/" ".agents/skills/github-workflow/SKILL.md" && grep -qF "description: Use when changing massCode localization, adding user-facing strings" ".agents/skills/i18n/SKILL.md" && grep -qF "massCode \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u0442 \u0441\u0438\u0441\u0442\u0435\u043c\u0443 Spaces \u0434\u043b\u044f \u0440\u0430\u0437\u0434\u0435\u043b\u0435\u043d\u0438\u044f \u0444\u0443\u043d\u043a\u0446\u0438\u043e\u043d\u0430\u043b\u044c\u043d\u044b\u0445 \u043e\u0431\u043b\u0430\u0441\u0442\u0435\u0439. \u042d\u0442\u043e \u043d" ".agents/skills/spaces-architecture/SKILL.md" && grep -qF "- \u0414\u043b\u044f \u0441\u0442\u0430\u043d\u0434\u0430\u0440\u0442\u043d\u043e\u0433\u043e app UI \u043f\u0440\u0435\u0434\u043f\u043e\u0447\u0438\u0442\u0430\u0439 \u0441\u0435\u043c\u0430\u043d\u0442\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u0442\u043e\u043a\u0435\u043d\u044b \u0432\u0440\u043e\u0434\u0435 `bg-background`" ".agents/skills/ui-foundations/SKILL.md" && grep -qF "description: Use when building or refactoring massCode UI components with local " ".agents/skills/ui-primitives/SKILL.md" && grep -qF "Renderer \u0432 massCode \u0441\u0442\u0440\u043e\u0438\u0442\u0441\u044f \u043d\u0430 Vue 3 Composition API \u0441 `<script setup lang=\"ts\"" ".agents/skills/vue-renderer-standards/SKILL.md" && grep -qF "massCode \u2014 \u044d\u0442\u043e \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u043d\u0430 Electron + Vue 3 + TypeScript \u0441 TailwindCSS v4 \u0432 re" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/api-and-typing/SKILL.md b/.agents/skills/api-and-typing/SKILL.md
@@ -0,0 +1,35 @@
+---
+name: api-and-typing
+description: Use when defining or reviewing massCode renderer types that come from generated API clients or DTOs, especially when deciding whether to reuse existing API shapes, derive narrower local types, or introduce a UI-only model.
+---
+
+# API And Typing
+
+## Overview
+
+Для massCode API types считаются generated-first. Если данные пришли из `~/renderer/services/api/generated` или соответствуют DTO из `src/main/api/dto`, сначала используй существующие типы и utility typing, а не придумывай новый interface рядом с компонентом.
+
+## Core Rules
+
+- Ручные дубли API response types не пиши.
+- Сначала ищи тип в `~/renderer/services/api/generated`.
+- Если прямого export нет, выводи нужный shape через `Pick`, `Omit`, indexed access, `Parameters`, `ReturnType`, `Awaited`, `NonNullable`.
+- Локальный тип допустим только как UI-only model, form model, derived display model или narrow type после нормального data narrowing.
+
+## Good Uses Of Local Types
+
+- Узкий renderer shape после того, как nullable API data уже очищена в одном месте.
+- View-model для dashboard card, graph node, readonly row или editor-side helper, если он не равен transport shape.
+- Тип аргумента, выводимый из существующего composable или API method через `Parameters` / `ReturnType`.
+
+## Bad Uses Of Local Types
+
+- Полный дубль `SnippetsResponse`, `NotesDashboardResponse`, `TagsResponse` и других generated types.
+- Новый interface “для удобства”, если можно взять одну ветку из existing response type.
+- Копирование DTO shape в renderer file, хотя он уже импортируемый.
+
+## Common Mistakes
+
+- Сначала придумать локальный interface, а потом уже искать generated type.
+- Смешать transport shape и UI view-model без явного adapter step.
+- Тащить глубоко в UI сырые nullable API поля вместо одного нормального normalization place.
diff --git a/.agents/skills/architecture-standards/SKILL.md b/.agents/skills/architecture-standards/SKILL.md
@@ -0,0 +1,73 @@
+---
+name: architecture-standards
+description: Use when working in massCode and you need repo-wide architecture rules, naming conventions, decomposition boundaries, or guidance on which massCode skill to load next.
+---
+
+# Architecture Standards
+
+## Overview
+
+Базовый принцип проекта: **YAGNI и простота прежде всего**. Не усложняй код ради гипотетических сценариев, не строй абстракции без повторяющейся потребности и не размывай границы между renderer, API и main.
+
+## Core Rules
+
+- Соблюдай разделение слоёв:
+  - Renderer: только UI, composables, вызовы `api.*` и `ipc.invoke(...)`.
+  - API: маршруты Elysia, DTO, orchestration и доступ к сервисам и данным приложения.
+  - Main: системные интеграции, IPC handlers, lifecycle и слой данных приложения.
+- Data flow по умолчанию: Renderer → API / IPC → service / data layer → response.
+- Vue-компоненты называй в `PascalCase`.
+- TypeScript-файлы называй в `camelCase`.
+- Composables именуй с префиксом `use`, а имя файла должно совпадать с экспортируемой функцией.
+
+## YAGNI Guardrails
+
+Признаки overengineering:
+
+- функция страхуется от кейса, которого реально не существует;
+- factory или wrapper используется ровно в одном месте и не скрывает состояние;
+- abstraction-for-abstraction без повторяющейся боли;
+- константы, паттерны и конфигурации придуманы заранее, а не из реальной потребности.
+
+## Component Decomposition
+
+- Если компонент становится больше примерно `300` строк или держит `3+` несвязанных обязанности, дели его.
+- Порядок разбиения:
+  1. вынеси константы и статические данные;
+  2. вынеси чистые функции в utils, только если это реально переиспользуется;
+  3. перемести состояние и эффекты в composable;
+  4. разбей шаблон на локальные child components.
+- Не держи в `<template>` логику сложнее тернарного оператора.
+
+## Feature Subdirectories
+
+- Если часть домена выросла в отдельный subsystem, группируй локальные компоненты, helpers, tests и fixtures в поддиректорию.
+- Внутри поддиректории не повторяй полный родительский префикс в именах файлов.
+- Локальные файлы держи рядом с фичей. Shared-код, который нужен нескольким областям, оставляй выше уровнем.
+
+## When to Load Other Skills
+
+- Vue renderer, auto-imports, composables, shared state:
+  `vue-renderer-standards`
+- визуальная база, typography, renderer styling decisions:
+  `ui-foundations`
+- `Ui*`, Shadcn, `cn`, `cva`, notifications:
+  `ui-primitives`
+- API routes, DTO, IPC, Electron boundaries:
+  `electron-api-and-ipc`
+- generated API types, utility typing, локальные view-model:
+  `api-and-typing`
+- `code` / `notes` / `math` / `tools`, состояние spaces и их синхронизация:
+  `spaces-architecture`
+- i18n, locale keys, `i18n.t(...)`:
+  `i18n`
+- scoped lint/test и follow-up commands:
+  `development-workflow`
+
+## Common Mistakes
+
+- Тянуть DB или filesystem knowledge в renderer.
+- Раздувать один компонент до “оркестратора всего”.
+- Выносить абстракцию до появления второй реальной точки использования.
+- Размазывать одну фичу по плоской структуре файлов, когда ей уже нужен локальный subdirectory.
+- Придумывать локальные typing-паттерны, хотя для них уже пора иметь отдельный skill.
diff --git a/.agents/skills/development-workflow/SKILL.md b/.agents/skills/development-workflow/SKILL.md
@@ -0,0 +1,37 @@
+---
+name: development-workflow
+description: Use when following massCode repo workflow rules, especially for scoped lint and test commands, or when changes require required follow-up commands like code generation or locale sync.
+---
+
+# Development Workflow
+
+## Overview
+
+В massCode workflow rules считаются частью качества изменений. Для локальной задачи команды должны быть точечными, а изменения source-of-truth файлов должны сопровождаться обязательными follow-up шагами.
+
+## Linting Rules
+
+- Всегда запускай lint только по затронутым файлам или директориям.
+- Никогда не запускай lint по всему проекту во время локальной задачи.
+- Используй scoped commands вроде:
+  - `pnpm lint <path>`
+  - `pnpm lint:fix <path>`
+
+## Testing Rules
+
+- Всегда запускай тесты только по затронутым файлам или директориям.
+- Никогда не запускай весь test suite без явной необходимости.
+- Используй scoped commands вроде:
+  - `pnpm test <path>`
+  - `pnpm test:watch <path>`
+
+## Required Follow-Up Commands
+
+- Изменил API DTO/routes → `pnpm api:generate`
+- Изменил locale-файлы → `pnpm i18n:copy`
+
+## Common Mistakes
+
+- Прогонять весь lint/test suite для маленькой точечной правки.
+- Менять source-of-truth файлы и забывать generation/sync шаг.
+- Запускать “на всякий случай” широкие команды вместо минимального релевантного набора.
diff --git a/.agents/skills/electron-api-and-ipc/SKILL.md b/.agents/skills/electron-api-and-ipc/SKILL.md
@@ -0,0 +1,53 @@
+---
+name: electron-api-and-ipc
+description: Use when changing massCode API routes, DTOs, IPC handlers, Electron bridges, or any renderer-to-main communication and storage-access boundaries.
+---
+
+# Electron API And IPC
+
+## Overview
+
+Все backend-возможности massCode живут в main process. Renderer получает доступ к данным и системным операциям только через Elysia API или IPC channels.
+
+## Renderer Access Rules
+
+- В renderer для данных используй `import { api } from '~/renderer/services/api'`.
+- В renderer для системных операций используй `ipc.invoke('channel:action', payload)`.
+- Electron API из renderer доступен только через `src/renderer/electron.ts`.
+- Никогда не импортируй storage internals или backend-модули напрямую в renderer.
+
+## New API Endpoints
+
+При добавлении нового endpoint:
+
+1. создай DTO в `src/main/api/dto/`;
+2. добавь route в `src/main/api/routes/`;
+3. запусти `pnpm api:generate`, чтобы обновить клиент.
+
+Не оставляй API-клиент рассинхронизированным с route/DTO изменениями.
+
+## IPC Conventions
+
+- Для filesystem и system ops используй `ipc.invoke(...)`.
+- Каналы должны укладываться в семейства:
+  - `fs:*`
+  - `system:*`
+  - `db:*` — legacy или migration flows, не основной путь для новой функциональности
+  - `main-menu:*`
+  - `prettier:*`
+  - `spaces:*`
+  - `theme:*`
+
+## Good Boundaries
+
+- Renderer формирует intent и payload.
+- Main/API работает с данными приложения, файловой системой и system APIs.
+- Ответ возвращается обратно в renderer в виде DTO или IPC result, а не через shared mutable backend module.
+
+## Common Mistakes
+
+- Тянуть backend-модуль напрямую в renderer ради “удобства”.
+- Менять DTO/route без `pnpm api:generate`.
+- Добавлять system/file behavior в renderer вместо IPC handler.
+- Добавлять новые `db:*` flows там, где задача должна идти через текущую API/IPC модель приложения.
+- Создавать ad-hoc каналы, которые не укладываются в существующие channel families.
diff --git a/.agents/skills/github-workflow/SKILL.md b/.agents/skills/github-workflow/SKILL.md
@@ -0,0 +1,87 @@
+---
+name: github-workflow
+description: Use when working with massCode issues, branches, commits, pull requests, or merge preparation in GitHub.
+---
+
+# github-workflow
+
+## Issue
+
+Если работа идёт по issue, читать его через `gh`:
+
+```bash
+gh issue view <number> -R massCodeIO/massCode
+```
+
+Если issue описывает bug, не считай его автоматически подтверждённым.
+
+Сначала:
+
+1. понять ожидаемое поведение;
+2. проверить текущее поведение в коде или воспроизвести проблему;
+3. подтвердить bug или явно зафиксировать, что он не подтверждается;
+4. только после этого переходить к ветке, фиксу и PR.
+
+Если bug не воспроизводится или issue описан неясно:
+
+- не начинать слепую реализацию;
+- сначала сообщить, что проблема не подтверждена, и уточнить условия или шаги воспроизведения.
+
+## Branch
+
+Создавай ветку от `main` с префиксом по типу изменения (`feat/`, `fix/`, `chore/`, `refactor/`) и коротким описанием. Если работа идёт по issue — уместно добавить номер в конец.
+
+```bash
+git checkout main && git pull
+git checkout -b feat/<short-description> main
+```
+
+## PR
+
+Заголовок PR — conventional commits:
+
+```text
+type: description
+```
+
+Перед созданием PR предложи заголовок пользователю на подтверждение.
+
+Если PR закрывает существующий issue, в описании добавляй:
+
+```text
+closes #123
+```
+
+Перед PR убедись, что релевантные проверки и тесты для затронутой области действительно прогнаны.
+
+Создание:
+
+```bash
+gh pr create \
+  --base main \
+  --head <branch-name> \
+  --title "type: description" \
+  --body "closes #<issue_number>" \
+  --assignee @me
+```
+
+Если issue нет — в `--body` кратко опиши суть изменений без служебного AI-хвоста.
+
+После создания PR предложи пользователю смерджить его в `main`:
+
+```bash
+gh pr merge <pr_number> -R massCodeIO/massCode --squash --delete-branch
+```
+
+После merge синхронизируй локальную ветку:
+
+```bash
+git checkout main && git pull
+git branch -d <branch-name>
+```
+
+## Commit
+
+- Только однострочный заголовок conventional commit.
+- Без скоупа проекта (`feat:`, `fix:`, а не `feat(notes):`).
+- Без тела, без `Co-Authored-By`.
diff --git a/.agents/skills/i18n/SKILL.md b/.agents/skills/i18n/SKILL.md
@@ -0,0 +1,34 @@
+---
+name: i18n
+description: Use when changing massCode localization, adding user-facing strings, creating locale keys, or wiring text through the project's translation system.
+---
+
+# I18n
+
+## Overview
+
+В massCode новый пользовательский текст всегда проходит через localization system. Базовым source of truth для новых ключей считается английская локаль.
+
+## Localization Rules
+
+- Базовый язык проекта — English.
+- `en_US` остаётся базовым source of truth для новых ключей.
+- Все новые ключи сначала добавляй в `src/main/i18n/locales/en_US/`.
+- При добавлении нового ключа сразу добавляй его и в русскую локаль, чтобы `ru_RU` не отставала от базового английского набора.
+- Не хардкодь user-facing strings ни в template, ни в script logic.
+- Используй `i18n.t('namespace:key.path')` или сокращённый `i18n.t('key.path')` для default `ui` namespace.
+- Импорт `i18n` делай из `@/electron`.
+
+## After Locale Changes
+
+- После добавления или изменения locale keys запускай `pnpm i18n:copy`.
+- Не оставляй `en_US` и `ru_RU` в несинхронном состоянии.
+- Остальные локали могут догоняться отдельно контрибьюторами и не считаются обязательным блокером для каждой локальной правки.
+
+## Common Mistakes
+
+- Хардкодить новый текст “временно”.
+- Добавлять ключи не в `en_US`, а сразу в другой locale.
+- Обновить `en_US`, но забыть сразу добавить тот же ключ в `ru_RU`.
+- Использовать текст напрямую в template, хотя это часть UI.
+- Забывать `pnpm i18n:copy` после изменения locale source-of-truth.
diff --git a/.agents/skills/spaces-architecture/SKILL.md b/.agents/skills/spaces-architecture/SKILL.md
@@ -0,0 +1,58 @@
+---
+name: spaces-architecture
+description: Use when working on massCode spaces such as code, notes, math, or tools, especially when changing their state, behavior, synchronization, or spaces IPC channels.
+---
+
+# Spaces Architecture
+
+## Overview
+
+massCode использует систему Spaces для разделения функциональных областей. Это не просто UI tabs: у каждого space есть собственное состояние, свои правила обновления и свой способ синхронизации с данными в vault.
+
+## Space Model
+
+- `code` — snippets, folders, tags
+- `notes` — notes, folders, tags, markdown-based flows
+- `math` — calculation sheets и состояние math notebook
+- `tools` — developer utilities
+
+Основные определения живут в `src/renderer/spaceDefinitions.ts`.
+
+## Space State Storage
+
+- Состояние каждого space хранится в `__spaces__/{spaceId}/.state.yaml` внутри vault.
+- Runtime helpers:
+  - `src/main/storage/providers/markdown/runtime/spaces.ts`
+  - `src/main/storage/providers/markdown/runtime/spaceState.ts`
+- Директория `__spaces__/` — служебная часть vault для состояния spaces.
+
+## Persistence Rules
+
+- Запись состояния spaces использует ту же debounce/flush инфраструктуру, что и `state.json`.
+- Не ломай совместимость с `pendingStateWriteByPath` и flush-on-exit поведением.
+- Если меняешь способ записи, учитывай сценарий завершения приложения до явного ручного flush.
+
+## IPC Rules
+
+- Space-specific IPC handlers живут в `src/main/ipc/handlers/spaces.ts`.
+- Текущие math handlers:
+  - `spaces:math:read`
+  - `spaces:math:write`
+- Если добавляется новый `spaces:*` flow, он должен работать через общую модель состояния spaces, а не в обход неё.
+
+## Space-Aware Sync
+
+- `system:storage-synced` обновляет активное пространство через `getActiveSpaceId()`.
+- Ожидаемое поведение:
+  - `code` → refresh folders + snippets
+  - `notes` → refresh notes + note folders
+  - `math` → `reloadFromDisk()` через `useMathNotebook()`
+  - `tools` → no-op
+- Изменения, которые уже сохранены в vault, должны вызывать `markPersistedStorageMutation()`, чтобы не создавать sync loops.
+
+## Common Mistakes
+
+- Считать spaces только UI-концепцией и забывать, что у них есть собственное состояние и правила синхронизации.
+- Писать состояние space в обход общих markdown runtime helpers.
+- Добавлять mutation без `markPersistedStorageMutation()`.
+- Ломать согласованность между состоянием space, helpers и sync behavior.
diff --git a/.agents/skills/ui-foundations/SKILL.md b/.agents/skills/ui-foundations/SKILL.md
@@ -0,0 +1,69 @@
+---
+name: ui-foundations
+description: Use when defining or reviewing massCode UI foundation rules such as typography, renderer styling consistency, TailwindCSS v4 usage, and when raw markup starts competing with established UI text patterns.
+---
+
+# UI Foundations
+
+## Overview
+
+UI в massCode должен оставаться визуально консистентным. Этот skill отвечает за базовые styling decisions: как относиться к typography, когда использовать established text patterns и как не скатываться в разрозненный renderer styling.
+
+## Core Rules
+
+- Базовая styling system в renderer строится на TailwindCSS v4.
+- Новые UI-экраны и состояния должны продолжать существующий visual language, а не вводить локальные правила “для одного места”.
+- Для стандартного app UI предпочитай семантические токены вроде `bg-background`, `text-muted-foreground`, `border-border`, `border-destructive/*` вместо raw palette-классов вроде `bg-white`, `text-black`, `text-green-500`, `bg-slate-900`.
+- Typography по умолчанию строится через `UiText`.
+- Не заменяй `UiText` на произвольный набор `text-*`, `font-*`, `text-muted-foreground`, если подходящий variant уже существует.
+- Если `UiText` почти подходит, лучше добавить точечные классы поверх него, чем уходить в raw typography markup.
+
+## Typography
+
+- `UiText` — базовый источник правды для текстовых размеров и muted-state.
+- `caption` и `xs` — подписи, helper text, secondary labels.
+- `sm` и `base` — основной интерфейсный текст.
+- `lg` и `xl` — усиленные title/value cases, когда это действительно нужно по hierarchy.
+- `font-mono` — только для code-like content, IDs, counts with alignment needs, readonly generated output и подобных случаев.
+- Для uppercase labels используй существующий pattern через `UiText` или согласованный tracking/uppercase стиль, а не случайную смесь utility classes в каждом месте.
+
+## Spacing And Layout Rhythm
+
+- Корневые screen/container wrappers обычно живут в ритме `space-y-4` или `space-y-6`.
+- Внутри компактных секций чаще всего `space-y-2` или `space-y-3`.
+- Grid gaps по умолчанию: `gap-2`, `gap-3`, `gap-4` в зависимости от плотности.
+- Не придумывай локальный spacing-scale для одного экрана, если существующие интервалы уже покрывают задачу.
+- Повторяющиеся content blocks должны иметь одинаковый padding и vertical rhythm.
+
+## Radius And Shadows
+
+- `rounded-md` — controls, inline boxes, compact containers.
+- `rounded-lg` — card-like blocks, dialogs, overlays, dashboard sections.
+- `rounded-xl` — preview-heavy surfaces и крупные visual blocks.
+- `rounded-full` — pills, badges, circular handles.
+- `shadow-xs` — inputs, buttons, small controls.
+- `shadow-md` и `shadow-lg` — overlays, popovers, previews, где elevation реально нужна.
+- Не вводи произвольные `rounded-[...]` и `shadow-[...]`, если стандартные токены уже подходят.
+
+## Exceptions
+
+- Raw colors допустимы, если цвет является частью самих данных или preview:
+  color pickers, contrast previews, code/image export backgrounds, diagram or visualizer nodes.
+- Если цвет вычисляется из контента или нужен для корректного контраста на пользовательском фоне, raw class или inline style допустимы.
+- Исключения не должны становиться поводом тащить raw palette в обычный application chrome.
+
+## When To Prefer This Skill
+
+- Нужно понять, как оформлять текст и подписи в новом UI.
+- Есть соблазн писать raw Tailwind typography вместо существующего text pattern.
+- В экране начинают появляться локальные styling rules, которые расходятся с остальным renderer UI.
+- Нужно принять решение на уровне визуальной базы, а не конкретного button/input/dialog.
+
+## Common Mistakes
+
+- Размазывать локальные визуальные исключения по фичам.
+- Тащить raw palette в обычный app UI без реальной причины.
+- Писать текст напрямую через произвольные utility classes там, где подходит `UiText`.
+- Делать новый экран со своим spacing rhythm вместо существующего scale.
+- Случайно смешивать small-control radii и preview-surface radii в одном и том же UI слое.
+- Считать Tailwind поводом делать каждый экран визуально “с нуля”.
diff --git a/.agents/skills/ui-primitives/SKILL.md b/.agents/skills/ui-primitives/SKILL.md
@@ -0,0 +1,67 @@
+---
+name: ui-primitives
+description: Use when building or refactoring massCode UI components with local Ui primitives or Shadcn, especially for cn, cva, notifications, and rules against reimplementing basic controls.
+---
+
+# UI Primitives
+
+## Overview
+
+Базовые UI-элементы в massCode должны собираться из существующих `Ui*` компонентов и Shadcn-паттернов. Этот skill отвечает за component-level usage rules, а не за общую визуальную базу.
+
+## Component Usage
+
+- Локальные UI-компоненты доступны через auto-import с префиксом `Ui`.
+- Базовые элементы вроде button, input, checkbox, action button не переизобретай на сыром HTML, если есть готовый `Ui*` вариант.
+- Если нужного элемента нет, сначала создай его в `src/renderer/components/ui/`, потом используй в фиче.
+
+## Buttons
+
+- Primary action должен быть явным и не конкурировать с несколькими равноправными CTA в одном контейнере.
+- Icon-only actions должны быть понятны по контексту и иметь tooltip или другой доступный label path.
+- Loading и pending actions должны использовать существующий button pattern, а не ad-hoc “disabled text swap”.
+- Destructive actions не должны выглядеть как обычные secondary controls.
+
+## Cards And Containers
+
+- Для автономных panel-like блоков используй существующий `Card` / `Ui*` container pattern, если он уже есть в области.
+- Внутренние muted blocks не нужно пересобирать разными `div`-паттернами в каждой фиче.
+- Repeated panel structure должна переезжать в shared primitive или local feature primitive, а не копироваться markup-в-маркап.
+
+## Readonly And Copyable Content
+
+- Длинный readonly output, generated text, URLs и similar content не показывай как “обычный disabled input”, если это ухудшает чтение.
+- Для copy flows используй существующий copy pattern и уведомления через `useSonner()`.
+- Readonly content должен оставаться визуально читаемым и удобно копируемым.
+
+## Styling Helpers
+
+- Для variants используй `cva`.
+- Для склейки классов используй `cn()`.
+- Не делай variants вручную строковыми `if`-цепочками там, где нужен нормальный variant API.
+
+## Shadcn Rules
+
+- Shadcn-компоненты импортируй вручную из `@/components/ui/shadcn/*`.
+- Для namespace-based компонентов используй паттерн вроде `import * as Dialog from '@/components/ui/shadcn/dialog'`.
+
+## Notifications
+
+- Для уведомлений используй `useSonner()`.
+- Не добавляй локальную, параллельную систему toast/notification внутри фичи.
+
+## Tooltip, Popover, Overlay
+
+- Tooltip — для короткого пояснения.
+- Popover — для richer inline content, picker-like content или contextual controls.
+- Не заменяй их ad-hoc overlay-разметкой без необходимости.
+- Validation и inline guidance должны использовать существующие tooltip/popover primitives, если проект уже их применяет в аналогичных местах.
+
+## Common Mistakes
+
+- Писать ещё одну кнопку или input с нуля “потому что быстрее”.
+- Склеивать сложные conditional classes без `cn()`.
+- Дублировать существующий primitive внутри feature directory вместо общего `src/renderer/components/ui/`.
+- Использовать disabled input как универсальный readonly display surface.
+- Делать overlay pattern вручную там, где уже есть Shadcn primitive.
+- Смешивать правила primitives с вопросами визуальной базы, которые должны идти в `ui-foundations`.
diff --git a/.agents/skills/vue-renderer-standards/SKILL.md b/.agents/skills/vue-renderer-standards/SKILL.md
@@ -0,0 +1,53 @@
+---
+name: vue-renderer-standards
+description: Use when editing massCode renderer code in Vue 3, especially for script setup patterns, import rules, composables, shared state, and renderer-side conventions.
+---
+
+# Vue Renderer Standards
+
+## Overview
+
+Renderer в massCode строится на Vue 3 Composition API с `<script setup lang="ts">`. Здесь важны строгие import rules, composable-first state sharing и запрет на прямой доступ к backend-возможностям.
+
+## Component Pattern
+
+- Используй Vue 3 Composition API и `<script setup lang="ts">`.
+- Vue core (`ref`, `computed`, `watch`, `onMounted` и подобные) не импортируй вручную: они auto-imported.
+- Проектные компоненты из `src/renderer/components/` тоже не импортируй вручную: они auto-imported.
+- Локальную логику компонента держи в script, а не в template.
+
+## Manual Imports Only Where Required
+
+Всегда импортируй вручную:
+
+- composables из `@/composables`;
+- utils из `@/utils`;
+- `@vueuse/core`;
+- Electron bridge из `@/electron`;
+- Shadcn UI из `@/components/ui/shadcn/*`.
+
+## Shared State
+
+- Глобальное shared state реализуется composables без Pinia/Vuex.
+- Reactive state, который должен шариться между компонентами, объявляй на module level, вне экспортируемой функции composable.
+- Persistent UI/settings state храни через `store` из `@/electron`:
+  - `store.app` для UI state;
+  - `store.preferences` для user preferences.
+
+## VueUse First
+
+- Перед написанием нового composable сначала проверь, нет ли подходящего решения в `@vueuse/core`.
+- Кастомный composable добавляй только если готового utility реально нет.
+
+## Renderer Boundaries
+
+- Renderer не импортирует storage internals или backend-модули доступа к данным напрямую.
+- Renderer не обращается напрямую к Node.js, filesystem или storage runtime.
+- Доступ к main process возможен только через `api` или `ipc`.
+
+## Common Mistakes
+
+- Ручной импорт `ref` / `computed` / `watch`.
+- Ручной импорт локальных project components.
+- Локальный state внутри composable, который должен быть общим между несколькими компонентами.
+- Попытка “срезать путь” и импортировать backend-модуль прямо в renderer.
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,276 +1,58 @@
-# massCode AI Coding Guidelines
-
-You are an expert Senior Frontend Developer specializing in Electron, Vue 3, and TypeScript.
-Follow these rules strictly when generating code for massCode.
-
-## 1. Core Stack
-
-- **Framework:** Vue 3 (Composition API, `<script setup lang="ts">`)
-- **Styling:** TailwindCSS v4 (`@tailwindcss/vite`), `tailwind-merge`, `cva`
-- **UI:** Custom components (`src/renderer/components/ui`), Shadcn (based on `reka-ui`), `lucide-vue-next` icons
-- **State:** Vue Composables (No Vuex/Pinia)
-- **Backend:** Electron (Main), `better-sqlite3` (DB), Elysia.js (API)
-- **Utilities:** `@vueuse/core`, `vue-sonner` (Notifications)
-
-## 2. Philosophy
-
-**YAGNI — simplicity above all.** Do not overcomplicate code for hypothetical future scenarios. The minimum viable implementation is the correct implementation. Three similar lines of code are better than a premature abstraction.
-
-Signs of overengineering:
-- A function guards against a case that will never happen
-- A factory used in exactly one place that doesn't encapsulate state
-- Abstraction for its own sake (a wrapper around a single line of code)
-- Constants or patterns invented in advance without a real need
-
-## 3. Architecture & Communication
-
-**Strict Separation of Concerns:**
-
-| Layer        | Process  | Access                                      | Communication                             |
-|:-------------|:---------|:--------------------------------------------|:------------------------------------------|
-| **Renderer** | Frontend | **NO** Node.js/DB access. Only via API/IPC. | Calls API (`api.*`) or IPC (`ipc.invoke`) |
-| **API**      | Main     | Full DB/System access.                      | Receives requests from Renderer           |
-| **Main**     | Backend  | Full System access.                         | Handles IPC & Lifecycle                   |
-
-**Data Flow:** Renderer → REST API (Elysia) → Service/DB Layer → Response
-
-## 4. File Naming
-
-| Type | Convention | Example |
-|------|------------|---------|
-| Vue components | PascalCase | `Folders.vue`, `CreateDialog.vue` |
-| TypeScript files | camelCase | `useSnippets.ts`, `errorMessage.ts` |
-
-Composables get a `use` prefix. The file name matches the exported function name: `useSnippets.ts` → `export function useSnippets()`.
-
-## 5. Critical Rules & Conventions
-
-### A. Imports (STRICT)
-
-**❌ DO NOT IMPORT:**
-
-- Vue core (`ref`, `computed`, `watch`, `onMounted`) → *Auto-imported*
-- Project components (`src/renderer/components/`) → *Auto-imported* (e.g., `<SidebarFolders />` for `components/sidebar/Folders.vue`)
-
-**✅ ALWAYS IMPORT MANUALLY:**
-
-- Shadcn UI: `import { Button } from '@/components/ui/shadcn/button'` or `import * as Select from '@/components/ui/shadcn/select'`
-- Composables: `import { useApp } from '@/composables'`
-- Utils: `import { cn } from '@/utils'`
-- VueUse: `import { useClipboard } from '@vueuse/core'`
-- Electron IPC/Store: `import { ipc, store } from '@/electron'`
-
-### B. State & Settings
-
-- **Global State:** Composables in `@/composables` (e.g., `useApp`, `useSnippets`) maintain shared state by defining reactive variables **outside** the exported function (module level). This ensures all components access the same state. **No Pinia/Vuex.**
-- **Persistent Settings:** Use `store` from '@/electron'.
-  - `store.app`: UI state (sizes, visibility)
-  - `store.preferences`: User prefs (theme, language)
-
-### C. Database & API
-
-- **Renderer:** **NEVER** import `better-sqlite3`. Use `import { api } from '~/renderer/services/api'`
-- **New Endpoints:**
-  1. Define DTO in `src/main/api/dto/`
-  2. Add route in `src/main/api/routes/`
-  3. **Run `pnpm api:generate`** to update client.
-
-### D. System & IPC
-
-- **File System/System Ops:** Use `ipc.invoke('channel:action', data)`.
-- **Channels:** `fs:*`, `system:*`, `db:*`, `main-menu:*`, `prettier:*`, `spaces:*`, `theme:*`.
-- **Renderer:** Access Electron only via `src/renderer/electron.ts`.
-
-### E. Spaces Architecture
-
-massCode uses a **Spaces** system to organize different functional areas:
-
-| Space | ID | Description |
-|-------|----|-------------|
-| Code | `code` | Main snippet management (folders, snippets, tags) |
-| Notes | `notes` | Notebook with folders, tags, and markdown notes |
-| Math | `math` | Math Notebook with calculation sheets |
-| Tools | `tools` | Developer utilities (converters, generators) |
-
-**Space Definitions:** `src/renderer/spaceDefinitions.ts` — `SpaceId`, `getSpaceDefinitions()`, `getActiveSpaceId()`.
-
-**Space State Persistence (Markdown Engine):**
-- Each space can store its state in `__spaces__/{spaceId}/.state.yaml` inside the vault.
-- Runtime utilities: `src/main/storage/providers/markdown/runtime/spaces.ts` — `ensureSpaceDirectory()`, `getSpaceStatePath()`.
-- Generic YAML read/write: `src/main/storage/providers/markdown/runtime/spaceState.ts` — `readSpaceState<T>()`, `writeSpaceState()`.
-- Space state writes use the same debounce/flush infrastructure as `state.json` (`pendingStateWriteByPath` in `constants.ts`), so they flush automatically on app exit.
-- `__spaces__/` directory exists **only in markdown engine**. When engine is `sqlite`, spaces fall back to `electron-store`.
-
-**Space IPC Channels:**
-- `spaces:math:read` — read Math Notebook state (auto-migrates from electron-store on first read in markdown mode).
-- `spaces:math:write` — persist Math Notebook state.
-- Handlers: `src/main/ipc/handlers/spaces.ts`.
-
-**Space-Aware Sync:**
-- `system:storage-synced` event dispatches refresh based on `getActiveSpaceId()`:
-  - `code` → refresh folders + snippets
-  - `notes` → refresh notes + note folders
-  - `math` → `reloadFromDisk()` via `useMathNotebook()`
-  - `tools` → no-op (no vault data)
-- Mutable operations must call `markPersistedStorageMutation()` to prevent sync loops.
-
-### F. Localization
-
-- **Primary Language:** English (EN) is the base language. All new keys **MUST** be added to `src/main/i18n/locales/en_US/` first.
-- **Strictly No Hardcoding:** Never use hardcoded strings in templates or logic. Always use the localization system.
-- **Usage:** Use `i18n.t('namespace:key.path')` in both templates and scripts.
-- **Default Namespace:** The `ui` namespace is the default. You can use `i18n.t('key.path')` instead of `i18n.t('ui:key.path')`.
-- **Imports:** `import { i18n } from '@/electron'`
-- **After adding/changing locales:** Run `pnpm i18n:copy` to sync locale files.
-
-## 6. UI/UX Guidelines
-
-- **Variants:** Use `cva` for component variants.
-- **Classes:** Use `cn()` to merge Tailwind classes.
-- **Notifications:** Use `useSonner()` composable.
-- **Utilities / Composables:**
-  - **Check `@vueuse/core` first.** Most common logic (clipboard, events, sensors) is already implemented.
-  - **Only** create custom composables if no suitable VueUse utility exists.
-  - Remember to **manually import** them (e.g., `import { useClipboard } from '@vueuse/core'`).
-- **Component Usage (STRICT):**
-  - **NEVER** reimplement basic UI elements (buttons, inputs, checkboxes, etc.).
-  - **ALWAYS** use existing components from `src/renderer/components/ui/`.
-  - **Typography:** Use `UiText` for text rendering by default. Do not hand-roll text styles with `text-*`, `font-*`, or `text-muted-foreground` when an appropriate `UiText` variant fits. If `UiText` lacks a needed size/style, compose it with extra classes instead of replacing it with raw HTML.
-  - **Missing Elements:** If a required UI element does not exist, create it in `src/renderer/components/ui/` first, following established patterns (Tailwind, cva, cn), then use it.
-  - **Naming:** They are auto-imported with a `Ui` prefix (e.g., `<UiInput />`, `<UiActionButton />`, `<UiText />`).
-
-## 7. Component Decomposition
-
-Split a component when it exceeds ~300 lines or has more than 3 unrelated responsibilities:
-
-1. Extract constants and static data
-2. Extract pure functions into utils (only if used in multiple places)
-3. Move state and effects into a composable
-4. Break the template into child components
-
-Keep no logic in `<template>` more complex than a ternary operator.
-
-**Feature Subdirectories:**
-
-- When a domain area grows into a clear subsystem (for example `notes/dashboard`), group its related components and local helpers into a dedicated subdirectory instead of keeping everything flat in the parent folder.
-- This applies not only to `.vue` components, but also to local `ts/js` helpers, tests, fixtures, styles, and other files that belong only to that subsystem.
-- Inside such a subdirectory, do **not** repeat the full parent prefix in file names. Prefer `dashboard/Dashboard.vue`, `dashboard/Header.vue`, `dashboard/Section.vue` over `dashboard/NotesDashboardHeader.vue`.
-- This project uses component auto-import with directory namespaces, so `notes/dashboard/Dashboard.vue` resolves to `NotesDashboard`, `notes/dashboard/Header.vue` resolves to `NotesDashboardHeader`, etc.
-- Keep only files that are truly local to that subsystem in the subdirectory. Shared files used by multiple slices should remain at the higher level or be renamed into a more general shared helper.
-
-## 8. Development Workflow & Commands
-
-**Linting (CRITICAL):**
-
-- **ALWAYS** scope lint commands to specific files/dirs.
-- **NEVER** run lint on the whole project during a task.
-- Usage: `pnpm lint <path>` or `pnpm lint:fix <path>`
-
-**Testing:**
-
-- **ALWAYS** scope test commands to specific files/dirs when working on a feature.
-- **NEVER** run tests on the whole project during a task.
-- Usage: `pnpm test <path>` or `pnpm test:watch <path>`
-
-**Other Commands:**
-
-- `pnpm dev`: Start dev server
-- `pnpm api:generate`: Regenerate API client (required after API changes)
-- `pnpm build`: Build for production
-
-## 9. Code Examples
-
-**Component Setup:**
-
-```html
-<script setup lang="ts">
-import { Button } from '@/components/ui/shadcn/button' // Manual import
-import * as Dialog from '@/components/ui/shadcn/dialog' // Manual import
-import { useSnippets } from '@/composables' // Manual import
-
-const { snippets } = useSnippets()
-// ref, computed are auto-imported (Vue core)
-</script>
-
-<template>
-  <div>
-    <!-- Use Shadcn components -->
-    <Dialog.Dialog>
-      <Dialog.DialogTrigger as-child>
-        <Button variant="outline">Open</Button>
-      </Dialog.DialogTrigger>
-      <Dialog.DialogContent>
-        Snippet count: {{ snippets.length }}
-      </Dialog.DialogContent>
-    </Dialog.Dialog>
-  </div>
-</template>
-```
-
-**Data Fetching (Renderer):**
-
-```typescript
-import { api } from '~/renderer/services/api'
-const { data } = await api.snippets.getSnippets({ folderId: 1 })
-```
-
-**IPC Call:**
-
-```typescript
-import { ipc } from '@/electron'
-await ipc.invoke('fs:assets', { buffer, fileName })
-```
-
-**Localization:**
-
-```html
-<script setup lang="ts">
-import { i18n } from '@/electron'
-</script>
-
-<template>
-  <div>
-    <!-- Using default 'ui' namespace -->
-    <p>{{ i18n.t('common.save') }}</p>
-
-    <!-- Using specific namespace -->
-    <p>{{ i18n.t('messages:snippets.count', { count: 10 }) }}</p>
-  </div>
-</template>
-```
-
-**Creating New API Endpoint (DTO & Route):**
-
-1. **Define DTO** (`src/main/api/dto/snippets.ts`):
-
-   ```typescript
-   import { t } from 'elysia'
-
-   // Define validation schema
-   const snippetsDuplicate = t.Object({
-     id: t.Number()
-   })
-
-   // Register in main DTO model
-   export const snippetsDTO = new Elysia().model({
-     // ... other DTOs
-     snippetsDuplicate
-   })
-   ```
-
-2. **Add Route** (`src/main/api/routes/snippets.ts`):
-
-   ```typescript
-   import { useDB } from '../../db'
-
-   app.post('/duplicate', ({ body }) => {
-     const db = useDB()
-     // Database logic here...
-     return { id: newId }
-   }, {
-     body: 'snippetsDuplicate', // Use registered DTO name
-     detail: { tags: ['Snippets'] }
-   })
-   ```
-
-3. **Generate Client:** Run `pnpm api:generate`
+# Точка входа для агента massCode
+
+Отвечай всегда на русском.
+
+massCode — это приложение на Electron + Vue 3 + TypeScript с TailwindCSS v4 в renderer, API-маршрутами на Elysia в main process, markdown vault как основным хранилищем пользовательского контента в v5 и `store.app` / `store.preferences` для локального UI state и настроек.
+
+## Всегда действующие правила
+
+- Следуй YAGNI. Предпочитай минимальную корректную реализацию вместо спекулятивных абстракций.
+- Соблюдай границы слоёв: renderer не должен напрямую обращаться к Node.js, filesystem или DB. Используй API или IPC.
+- Никогда не хардкодь пользовательские строки. Используй систему локализации.
+- Не запускай lint или тесты по всему проекту для локальной задачи. Ограничивай команды затронутыми файлами или директориями.
+- После изменений API DTO или routes запускай `pnpm api:generate`.
+- После изменений locale-файлов запускай `pnpm i18n:copy`.
+- Если задача совпадает по теме с одним из skills ниже, загружай этот skill до внесения изменений.
+
+## Skills
+
+- `.agents/skills/architecture-standards/SKILL.md`
+  Используй первым для общих правил репозитория: архитектура, naming, декомпозиция и выбор следующего skill.
+- `.agents/skills/vue-renderer-standards/SKILL.md`
+  Используй для работы с Vue renderer: `<script setup lang="ts">`, правила auto-import, composables, shared state и renderer-side паттерны.
+- `.agents/skills/ui-foundations/SKILL.md`
+  Используй для базовых UI-правил: Tailwind v4, typography через `UiText` и согласованных styling decisions для renderer UI.
+- `.agents/skills/ui-primitives/SKILL.md`
+  Используй для component-level UI работы: `Ui*` components, Shadcn imports, `cn`, `cva`, notifications и правил против переизобретения primitives.
+- `.agents/skills/electron-api-and-ipc/SKILL.md`
+  Используй для API routes, DTO, IPC handlers, renderer-to-main communication и границ Electron-интеграции.
+- `.agents/skills/api-and-typing/SKILL.md`
+  Используй для generated API types, DTO-derived renderer typing и решения, когда локальный UI type оправдан, а когда нужно переиспользовать существующие API types.
+- `.agents/skills/spaces-architecture/SKILL.md`
+  Используй при изменениях, связанных с `code` / `notes` / `math` / `tools`, markdown-space state, sync behavior или `spaces:*` IPC.
+- `.agents/skills/i18n/SKILL.md`
+  Используй для правил локализации, размещения locale keys, `i18n.t(...)` и требования не хардкодить строки.
+- `.agents/skills/development-workflow/SKILL.md`
+  Используй для repo-specific workflow rules: scoped lint/test команды и обязательные follow-up шаги после изменений source-of-truth файлов.
+- `.agents/skills/github-workflow/SKILL.md`
+  Используй для massCode git и GitHub workflow: issue, ветки, commits, PR и подготовки к merge.
+
+## Рекомендуемый порядок загрузки
+
+- Широкая или неочевидная задача: начни с `architecture-standards`, затем загрузи профильный skill.
+- Renderer UI задача: `architecture-standards` → `vue-renderer-standards` → `ui-foundations` → `ui-primitives`.
+- API / IPC / Electron задача: `architecture-standards` → `electron-api-and-ipc`.
+- Generated types / renderer typing задача: `architecture-standards` → `api-and-typing`.
+- Spaces задача: `architecture-standards` → `spaces-architecture`.
+- Задача про текст и локализацию: `i18n`.
+- Workflow-чувствительная задача: `development-workflow`.
+- Задача про git / branch / commit / PR: `github-workflow`.
+
+## Основной стек
+
+- Framework: Vue 3, Composition API, `<script setup lang="ts">`
+- Styling: TailwindCSS v4, `tailwind-merge`, `cva`
+- UI: локальные `src/renderer/components/ui`, Shadcn поверх `reka-ui`, `lucide-vue-next`
+- State: composables, без Pinia/Vuex
+- Backend: Electron main, Elysia API, markdown vault для контента и `electron-store` для локального состояния приложения
+- Utilities: `@vueuse/core`, `vue-sonner`
PATCH

echo "Gold patch applied."
