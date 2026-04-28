"""Behavioral checks for masscode-docs-add-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/masscode")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/api-and-typing/SKILL.md')
    assert 'Для massCode API types считаются generated-first. Если данные пришли из `~/renderer/services/api/generated` или соответствуют DTO из `src/main/api/dto`, сначала используй существующие типы и utility t' in text, "expected to find: " + 'Для massCode API types считаются generated-first. Если данные пришли из `~/renderer/services/api/generated` или соответствуют DTO из `src/main/api/dto`, сначала используй существующие типы и utility t'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/api-and-typing/SKILL.md')
    assert 'description: Use when defining or reviewing massCode renderer types that come from generated API clients or DTOs, especially when deciding whether to reuse existing API shapes, derive narrower local t' in text, "expected to find: " + 'description: Use when defining or reviewing massCode renderer types that come from generated API clients or DTOs, especially when deciding whether to reuse existing API shapes, derive narrower local t'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/api-and-typing/SKILL.md')
    assert '- Если прямого export нет, выводи нужный shape через `Pick`, `Omit`, indexed access, `Parameters`, `ReturnType`, `Awaited`, `NonNullable`.' in text, "expected to find: " + '- Если прямого export нет, выводи нужный shape через `Pick`, `Omit`, indexed access, `Parameters`, `ReturnType`, `Awaited`, `NonNullable`.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/architecture-standards/SKILL.md')
    assert 'Базовый принцип проекта: **YAGNI и простота прежде всего**. Не усложняй код ради гипотетических сценариев, не строй абстракции без повторяющейся потребности и не размывай границы между renderer, API и' in text, "expected to find: " + 'Базовый принцип проекта: **YAGNI и простота прежде всего**. Не усложняй код ради гипотетических сценариев, не строй абстракции без повторяющейся потребности и не размывай границы между renderer, API и'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/architecture-standards/SKILL.md')
    assert 'description: Use when working in massCode and you need repo-wide architecture rules, naming conventions, decomposition boundaries, or guidance on which massCode skill to load next.' in text, "expected to find: " + 'description: Use when working in massCode and you need repo-wide architecture rules, naming conventions, decomposition boundaries, or guidance on which massCode skill to load next.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/architecture-standards/SKILL.md')
    assert '- Если часть домена выросла в отдельный subsystem, группируй локальные компоненты, helpers, tests и fixtures в поддиректорию.' in text, "expected to find: " + '- Если часть домена выросла в отдельный subsystem, группируй локальные компоненты, helpers, tests и fixtures в поддиректорию.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/development-workflow/SKILL.md')
    assert 'В massCode workflow rules считаются частью качества изменений. Для локальной задачи команды должны быть точечными, а изменения source-of-truth файлов должны сопровождаться обязательными follow-up шага' in text, "expected to find: " + 'В massCode workflow rules считаются частью качества изменений. Для локальной задачи команды должны быть точечными, а изменения source-of-truth файлов должны сопровождаться обязательными follow-up шага'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/development-workflow/SKILL.md')
    assert 'description: Use when following massCode repo workflow rules, especially for scoped lint and test commands, or when changes require required follow-up commands like code generation or locale sync.' in text, "expected to find: " + 'description: Use when following massCode repo workflow rules, especially for scoped lint and test commands, or when changes require required follow-up commands like code generation or locale sync.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/development-workflow/SKILL.md')
    assert '- Никогда не запускай lint по всему проекту во время локальной задачи.' in text, "expected to find: " + '- Никогда не запускай lint по всему проекту во время локальной задачи.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/electron-api-and-ipc/SKILL.md')
    assert 'description: Use when changing massCode API routes, DTOs, IPC handlers, Electron bridges, or any renderer-to-main communication and storage-access boundaries.' in text, "expected to find: " + 'description: Use when changing massCode API routes, DTOs, IPC handlers, Electron bridges, or any renderer-to-main communication and storage-access boundaries.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/electron-api-and-ipc/SKILL.md')
    assert 'Все backend-возможности massCode живут в main process. Renderer получает доступ к данным и системным операциям только через Elysia API или IPC channels.' in text, "expected to find: " + 'Все backend-возможности massCode живут в main process. Renderer получает доступ к данным и системным операциям только через Elysia API или IPC channels.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/electron-api-and-ipc/SKILL.md')
    assert '- Ответ возвращается обратно в renderer в виде DTO или IPC result, а не через shared mutable backend module.' in text, "expected to find: " + '- Ответ возвращается обратно в renderer в виде DTO или IPC result, а не через shared mutable backend module.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/github-workflow/SKILL.md')
    assert 'Создавай ветку от `main` с префиксом по типу изменения (`feat/`, `fix/`, `chore/`, `refactor/`) и коротким описанием. Если работа идёт по issue — уместно добавить номер в конец.' in text, "expected to find: " + 'Создавай ветку от `main` с префиксом по типу изменения (`feat/`, `fix/`, `chore/`, `refactor/`) и коротким описанием. Если работа идёт по issue — уместно добавить номер в конец.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/github-workflow/SKILL.md')
    assert 'description: Use when working with massCode issues, branches, commits, pull requests, or merge preparation in GitHub.' in text, "expected to find: " + 'description: Use when working with massCode issues, branches, commits, pull requests, or merge preparation in GitHub.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/github-workflow/SKILL.md')
    assert 'Перед PR убедись, что релевантные проверки и тесты для затронутой области действительно прогнаны.' in text, "expected to find: " + 'Перед PR убедись, что релевантные проверки и тесты для затронутой области действительно прогнаны.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/i18n/SKILL.md')
    assert "description: Use when changing massCode localization, adding user-facing strings, creating locale keys, or wiring text through the project's translation system." in text, "expected to find: " + "description: Use when changing massCode localization, adding user-facing strings, creating locale keys, or wiring text through the project's translation system."[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/i18n/SKILL.md')
    assert 'В massCode новый пользовательский текст всегда проходит через localization system. Базовым source of truth для новых ключей считается английская локаль.' in text, "expected to find: " + 'В massCode новый пользовательский текст всегда проходит через localization system. Базовым source of truth для новых ключей считается английская локаль.'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/i18n/SKILL.md')
    assert '- При добавлении нового ключа сразу добавляй его и в русскую локаль, чтобы `ru_RU` не отставала от базового английского набора.' in text, "expected to find: " + '- При добавлении нового ключа сразу добавляй его и в русскую локаль, чтобы `ru_RU` не отставала от базового английского набора.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/spaces-architecture/SKILL.md')
    assert 'massCode использует систему Spaces для разделения функциональных областей. Это не просто UI tabs: у каждого space есть собственное состояние, свои правила обновления и свой способ синхронизации с данн' in text, "expected to find: " + 'massCode использует систему Spaces для разделения функциональных областей. Это не просто UI tabs: у каждого space есть собственное состояние, свои правила обновления и свой способ синхронизации с данн'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/spaces-architecture/SKILL.md')
    assert 'description: Use when working on massCode spaces such as code, notes, math, or tools, especially when changing their state, behavior, synchronization, or spaces IPC channels.' in text, "expected to find: " + 'description: Use when working on massCode spaces such as code, notes, math, or tools, especially when changing their state, behavior, synchronization, or spaces IPC channels.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/spaces-architecture/SKILL.md')
    assert '- Изменения, которые уже сохранены в vault, должны вызывать `markPersistedStorageMutation()`, чтобы не создавать sync loops.' in text, "expected to find: " + '- Изменения, которые уже сохранены в vault, должны вызывать `markPersistedStorageMutation()`, чтобы не создавать sync loops.'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/ui-foundations/SKILL.md')
    assert '- Для стандартного app UI предпочитай семантические токены вроде `bg-background`, `text-muted-foreground`, `border-border`, `border-destructive/*` вместо raw palette-классов вроде `bg-white`, `text-bl' in text, "expected to find: " + '- Для стандартного app UI предпочитай семантические токены вроде `bg-background`, `text-muted-foreground`, `border-border`, `border-destructive/*` вместо raw palette-классов вроде `bg-white`, `text-bl'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/ui-foundations/SKILL.md')
    assert 'UI в massCode должен оставаться визуально консистентным. Этот skill отвечает за базовые styling decisions: как относиться к typography, когда использовать established text patterns и как не скатыватьс' in text, "expected to find: " + 'UI в massCode должен оставаться визуально консистентным. Этот skill отвечает за базовые styling decisions: как относиться к typography, когда использовать established text patterns и как не скатыватьс'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/ui-foundations/SKILL.md')
    assert 'description: Use when defining or reviewing massCode UI foundation rules such as typography, renderer styling consistency, TailwindCSS v4 usage, and when raw markup starts competing with established U' in text, "expected to find: " + 'description: Use when defining or reviewing massCode UI foundation rules such as typography, renderer styling consistency, TailwindCSS v4 usage, and when raw markup starts competing with established U'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/ui-primitives/SKILL.md')
    assert 'description: Use when building or refactoring massCode UI components with local Ui primitives or Shadcn, especially for cn, cva, notifications, and rules against reimplementing basic controls.' in text, "expected to find: " + 'description: Use when building or refactoring massCode UI components with local Ui primitives or Shadcn, especially for cn, cva, notifications, and rules against reimplementing basic controls.'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/ui-primitives/SKILL.md')
    assert 'Базовые UI-элементы в massCode должны собираться из существующих `Ui*` компонентов и Shadcn-паттернов. Этот skill отвечает за component-level usage rules, а не за общую визуальную базу.' in text, "expected to find: " + 'Базовые UI-элементы в massCode должны собираться из существующих `Ui*` компонентов и Shadcn-паттернов. Этот skill отвечает за component-level usage rules, а не за общую визуальную базу.'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/ui-primitives/SKILL.md')
    assert '- Validation и inline guidance должны использовать существующие tooltip/popover primitives, если проект уже их применяет в аналогичных местах.' in text, "expected to find: " + '- Validation и inline guidance должны использовать существующие tooltip/popover primitives, если проект уже их применяет в аналогичных местах.'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/vue-renderer-standards/SKILL.md')
    assert 'Renderer в massCode строится на Vue 3 Composition API с `<script setup lang="ts">`. Здесь важны строгие import rules, composable-first state sharing и запрет на прямой доступ к backend-возможностям.' in text, "expected to find: " + 'Renderer в massCode строится на Vue 3 Composition API с `<script setup lang="ts">`. Здесь важны строгие import rules, composable-first state sharing и запрет на прямой доступ к backend-возможностям.'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/vue-renderer-standards/SKILL.md')
    assert 'description: Use when editing massCode renderer code in Vue 3, especially for script setup patterns, import rules, composables, shared state, and renderer-side conventions.' in text, "expected to find: " + 'description: Use when editing massCode renderer code in Vue 3, especially for script setup patterns, import rules, composables, shared state, and renderer-side conventions.'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/vue-renderer-standards/SKILL.md')
    assert '- Reactive state, который должен шариться между компонентами, объявляй на module level, вне экспортируемой функции composable.' in text, "expected to find: " + '- Reactive state, который должен шариться между компонентами, объявляй на module level, вне экспортируемой функции composable.'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'massCode — это приложение на Electron + Vue 3 + TypeScript с TailwindCSS v4 в renderer, API-маршрутами на Elysia в main process, markdown vault как основным хранилищем пользовательского контента в v5 ' in text, "expected to find: " + 'massCode — это приложение на Electron + Vue 3 + TypeScript с TailwindCSS v4 в renderer, API-маршрутами на Elysia в main process, markdown vault как основным хранилищем пользовательского контента в v5 '[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Используй для generated API types, DTO-derived renderer typing и решения, когда локальный UI type оправдан, а когда нужно переиспользовать существующие API types.' in text, "expected to find: " + 'Используй для generated API types, DTO-derived renderer typing и решения, когда локальный UI type оправдан, а когда нужно переиспользовать существующие API types.'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Используй для component-level UI работы: `Ui*` components, Shadcn imports, `cn`, `cva`, notifications и правил против переизобретения primitives.' in text, "expected to find: " + 'Используй для component-level UI работы: `Ui*` components, Shadcn imports, `cn`, `cva`, notifications и правил против переизобретения primitives.'[:80]

