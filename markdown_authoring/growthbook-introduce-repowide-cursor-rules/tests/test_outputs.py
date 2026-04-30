"""Behavioral checks for growthbook-introduce-repowide-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/growthbook")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/backend/api-patterns.md')
    assert '- If creating a new controller and router, use the pattern of putting the router in the `src/routers/` directory, and not using the `back-end/src/app.ts` file - that is the old way of doing things.' in text, "expected to find: " + '- If creating a new controller and router, use the pattern of putting the router in the `src/routers/` directory, and not using the `back-end/src/app.ts` file - that is the old way of doing things.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/backend/api-patterns.md')
    assert '- If building a new model, the model should not be exported from the model file - only the functions and methods should be exported.' in text, "expected to find: " + '- If building a new model, the model should not be exported from the model file - only the functions and methods should be exported.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/backend/api-patterns.md')
    assert '- **Leverage the BaseModel** - When adding a new model, default to using the BaseModel except for rare cases' in text, "expected to find: " + '- **Leverage the BaseModel** - When adding a new model, default to using the BaseModel except for rare cases'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/backend/model-patterns.md')
    assert "Note: Permission checks, migrations, etc. are all done automatically within the `_find` method, so you don't need to repeat any of that in your custom methods. Also, the `organization` field is automa" in text, "expected to find: " + "Note: Permission checks, migrations, etc. are all done automatically within the `_find` method, so you don't need to repeat any of that in your custom methods. Also, the `organization` field is automa"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/backend/model-patterns.md')
    assert 'You can add more tailored data fetching methods as needed by referencing the `_findOne` and `_find` methods. There are similar protected methods for write operations, although those are rarely needed.' in text, "expected to find: " + 'You can add more tailored data fetching methods as needed by referencing the `_findOne` and `_find` methods. There are similar protected methods for write operations, although those are rarely needed.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/backend/model-patterns.md')
    assert 'GrowthBook uses a `BaseModel` pattern built on MongoDB. New models should use `MakeModelClass()` to create a base class, then extend it with permission logic and customize further if needed.' in text, "expected to find: " + 'GrowthBook uses a `BaseModel` pattern built on MongoDB. New models should use `MakeModelClass()` to create a base class, then extend it with permission logic and customize further if needed.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/development-guidelines.md')
    assert '- Only declare types/interfaces from scratch when there is no Zod schema. When there is a corresponding Zod schema, use that as the source of truth and infer the type.' in text, "expected to find: " + '- Only declare types/interfaces from scratch when there is no Zod schema. When there is a corresponding Zod schema, use that as the source of truth and infer the type.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/development-guidelines.md')
    assert '- If data is coming from an untrusted source (like the request body or JSON.parse), it should start out as `unknown` until you validate it (usually with zod).' in text, "expected to find: " + '- If data is coming from an untrusted source (like the request body or JSON.parse), it should start out as `unknown` until you validate it (usually with zod).'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/development-guidelines.md')
    assert '- DO NOT write tests for front-end components or back-end routers/controllers/models. DO write tests for critical utility/helper functions' in text, "expected to find: " + '- DO NOT write tests for front-end components or back-end routers/controllers/models. DO write tests for critical utility/helper functions'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/frontend/data-fetching.md')
    assert 'GrowthBook uses SWR for data fetching with a custom `useApi()` hook, and `apiCall()` for mutations. All requests are automatically scoped to the current organization.' in text, "expected to find: " + 'GrowthBook uses SWR for data fetching with a custom `useApi()` hook, and `apiCall()` for mutations. All requests are automatically scoped to the current organization.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/frontend/data-fetching.md')
    assert "The `useApi()` hook is the primary way to fetch data. It's built on SWR and provides caching, revalidation, and organization scoping." in text, "expected to find: " + "The `useApi()` hook is the primary way to fetch data. It's built on SWR and provides caching, revalidation, and organization scoping."[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/frontend/data-fetching.md')
    assert '| Hook               | Purpose                                    | Location                        |' in text, "expected to find: " + '| Hook               | Purpose                                    | Location                        |'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/frontend/react-patterns.md')
    assert 'Available design system components: Avatar, Badge, Button, Callout, Checkbox, ConfirmDialog, DataList, DropdownMenu, ErrorDisplay, Frame, HelperText, Link, LinkButton, Metadata, Pagination, Popover, P' in text, "expected to find: " + 'Available design system components: Avatar, Badge, Button, Callout, Checkbox, ConfirmDialog, DataList, DropdownMenu, ErrorDisplay, Frame, HelperText, Link, LinkButton, Metadata, Pagination, Popover, P'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/frontend/react-patterns.md')
    assert '**Before building inline or one-off components, ask yourself:** Could this be useful elsewhere in the codebase? If the component is generic and reusable (not domain-specific), propose adding it to `@/' in text, "expected to find: " + '**Before building inline or one-off components, ask yourself:** Could this be useful elsewhere in the codebase? If the component is generic and reusable (not domain-specific), propose adding it to `@/'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/frontend/react-patterns.md')
    assert '**Ask the user before creating:** "This looks like a reusable pattern. Should I create a new `@/ui/ComponentName` component that can be used across the codebase?"' in text, "expected to find: " + '**Ask the user before creating:** "This looks like a reusable pattern. Should I create a new `@/ui/ComponentName` component that can be used across the codebase?"'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/package-boundaries.md')
    assert '- Affected components: Avatar, Badge, Button, Callout, Checkbox, DataList, DropdownMenu, Link, RadioCards, RadioGroup, Select, Switch, Table, Tabs' in text, "expected to find: " + '- Affected components: Avatar, Badge, Button, Callout, Checkbox, DataList, DropdownMenu, Link, RadioCards, RadioGroup, Select, Switch, Table, Tabs'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/package-boundaries.md')
    assert 'description: "Critical package import restrictions enforced by ESLint - must be strictly followed"' in text, "expected to find: " + 'description: "Critical package import restrictions enforced by ESLint - must be strictly followed"'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/package-boundaries.md')
    assert '- ❌ DO NOT import Radix UI components directly - use design system wrappers from `@/ui/` instead' in text, "expected to find: " + '- ❌ DO NOT import Radix UI components directly - use design system wrappers from `@/ui/` instead'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/permissions.md')
    assert 'GrowthBook uses a three-tier permission system with Global, Project-scoped, and Environment-scoped permissions. Permissions work alongside commercial features - both gates must pass for access.' in text, "expected to find: " + 'GrowthBook uses a three-tier permission system with Global, Project-scoped, and Environment-scoped permissions. Permissions work alongside commercial features - both gates must pass for access.'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/permissions.md')
    assert "Commercial features are a separate gate from permissions. A user might have permission but the organization's plan might not include the feature." in text, "expected to find: " + "Commercial features are a separate gate from permissions. A user might have permission but the organization's plan might not include the feature."[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/permissions.md')
    assert '- Frontend hooks: `packages/front-end/hooks/usePermissions.ts`, `usePermissionsUtils.ts`' in text, "expected to find: " + '- Frontend hooks: `packages/front-end/hooks/usePermissions.ts`, `usePermissionsUtils.ts`'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/project-overview.md')
    assert '1. **Internal API** - Used by the GrowthBook front-end application (controllers, routers in `src/controllers/`, `src/routers/`)' in text, "expected to find: " + '1. **Internal API** - Used by the GrowthBook front-end application (controllers, routers in `src/controllers/`, `src/routers/`)'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/project-overview.md')
    assert '2. **External REST API** - Public API for customers to integrate with GrowthBook (located in `src/api/` directory)' in text, "expected to find: " + '2. **External REST API** - Public API for customers to integrate with GrowthBook (located in `src/api/` directory)'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/project-overview.md')
    assert 'description: "GrowthBook project architecture, monorepo structure, and package organization"' in text, "expected to find: " + 'description: "GrowthBook project architecture, monorepo structure, and package organization"'[:80]

