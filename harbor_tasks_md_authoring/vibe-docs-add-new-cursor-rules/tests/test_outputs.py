"""Behavioral checks for vibe-docs-add-new-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vibe")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/base-components.mdc')
    assert 'When styling base components from other components, always use their `className` prop instead of targeting them with CSS selectors like `[data-vibe]` or `[data-testid]`, element selectors, or other at' in text, "expected to find: " + 'When styling base components from other components, always use their `className` prop instead of targeting them with CSS selectors like `[data-vibe]` or `[data-testid]`, element selectors, or other at'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/base-components.mdc')
    assert "// ❌ Bad - Don't target with element or attribute selectors" in text, "expected to find: " + "// ❌ Bad - Don't target with element or attribute selectors"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/base-components.mdc')
    assert '### 1. Use className Prop for Styling Base Components' in text, "expected to find: " + '### 1. Use className Prop for Styling Base Components'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/component-internal-structure.mdc')
    assert '5. **No Static Properties**: Never use the `withStaticProps` utility or assign static properties to components. Components should remain without attached static properties. This means avoiding pattern' in text, "expected to find: " + '5. **No Static Properties**: Never use the `withStaticProps` utility or assign static properties to components. Components should remain without attached static properties. This means avoiding pattern'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/component-internal-structure.mdc')
    assert "- **Use `onClose` prop as both handler and boolean indicator** - don't add separate `dismissible` or `closable` props" in text, "expected to find: " + "- **Use `onClose` prop as both handler and boolean indicator** - don't add separate `dismissible` or `closable` props"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/component-internal-structure.mdc')
    assert '- **Conditional rendering based on `onClose` presence**: `{onClose && <CloseButton onClick={onClose} />}`' in text, "expected to find: " + '- **Conditional rendering based on `onClose` presence**: `{onClose && <CloseButton onClick={onClose} />}`'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/file-structures.mdc')
    assert '- **Simpler Components**: For simpler components, not all subdirectories (`hooks/`, `utils/`, `components/`, `context/`, `consts/`) are necessary. Files like `ComponentName.tsx`, `ComponentName.types.' in text, "expected to find: " + '- **Simpler Components**: For simpler components, not all subdirectories (`hooks/`, `utils/`, `components/`, `context/`, `consts/`) are necessary. Files like `ComponentName.tsx`, `ComponentName.types.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/file-structures.mdc')
    assert '- **Reusability**: If a hook, utility, or constant is reusable across multiple components (not potentially reusable, but actually reused in more than one component), it should be placed in the top-lev' in text, "expected to find: " + '- **Reusability**: If a hook, utility, or constant is reusable across multiple components (not potentially reusable, but actually reused in more than one component), it should be placed in the top-lev'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/file-structures.mdc')
    assert '- **Use meaningful file names** that describe the purpose, not generic names like `MyComponentConstants.ts` or `consts.ts`.' in text, "expected to find: " + '- **Use meaningful file names** that describe the purpose, not generic names like `MyComponentConstants.ts` or `consts.ts`.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/layout-components.mdc')
    assert 'This rule provides comprehensive guidelines for using [Box](mdc:packages/core/src/components/Box/Box.tsx) and [Flex](mdc:packages/core/src/components/Flex/Flex.tsx) components from `@vibe/core` instea' in text, "expected to find: " + 'This rule provides comprehensive guidelines for using [Box](mdc:packages/core/src/components/Box/Box.tsx) and [Flex](mdc:packages/core/src/components/Flex/Flex.tsx) components from `@vibe/core` instea'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/layout-components.mdc')
    assert 'description: Guidelines for using Box and Flex layout components in the @vibe/core library instead of custom CSS for spacing, borders, and flexbox layouts.' in text, "expected to find: " + 'description: Guidelines for using Box and Flex layout components in the @vibe/core library instead of custom CSS for spacing, borders, and flexbox layouts.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/layout-components.mdc')
    assert '**Background colors**: `primaryBackgroundColor`, `secondaryBackgroundColor`, `greyBackgroundColor`, `allgreyBackgroundColor`, `invertedColorBackground`' in text, "expected to find: " + '**Background colors**: `primaryBackgroundColor`, `secondaryBackgroundColor`, `greyBackgroundColor`, `allgreyBackgroundColor`, `invertedColorBackground`'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/naming-conventions.mdc')
    assert '- **Consistent Typing**: Always check existing similar components to see what Vibe standard types they use before creating custom types.' in text, "expected to find: " + '- **Consistent Typing**: Always check existing similar components to see what Vibe standard types they use before creating custom types.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/naming-conventions.mdc')
    assert '- **Component Props**: Extend `VibeComponentProps` for component props (to get `className`, `id`, `data-testid`).' in text, "expected to find: " + '- **Component Props**: Extend `VibeComponentProps` for component props (to get `className`, `id`, `data-testid`).'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/naming-conventions.mdc')
    assert '- **Tests**: Test files SHOULD be co-located with the code they test in respective `__tests__` subdirectories.' in text, "expected to find: " + '- **Tests**: Test files SHOULD be co-located with the code they test in respective `__tests__` subdirectories.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/new-component-implementation.mdc')
    assert '6. **Missing `[data-vibe]` Attribute**: Forgetting to add the mandatory `[data-vibe]` attribute or missing the corresponding `ComponentVibeId` enum entry' in text, "expected to find: " + '6. **Missing `[data-vibe]` Attribute**: Forgetting to add the mandatory `[data-vibe]` attribute or missing the corresponding `ComponentVibeId` enum entry'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/new-component-implementation.mdc')
    assert '**Reusability Rule**: If constants are used across multiple components, place them in the top-level `packages/core/src/constants/` directory instead.' in text, "expected to find: " + '**Reusability Rule**: If constants are used across multiple components, place them in the top-level `packages/core/src/constants/` directory instead.'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/new-component-implementation.mdc')
    assert '**CRITICAL**: Every new component MUST include the `[data-vibe]` attribute on its root element for component identification in the DOM.' in text, "expected to find: " + '**CRITICAL**: Every new component MUST include the `[data-vibe]` attribute on its root element for component identification in the DOM.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/storybook-stories.mdc')
    assert 'render: () => <Button kind={Button.kinds.PRIMARY} size={Button.sizes.SMALL}>Click me</Button>' in text, "expected to find: " + 'render: () => <Button kind={Button.kinds.PRIMARY} size={Button.sizes.SMALL}>Click me</Button>'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/storybook-stories.mdc')
    assert 'This approach provides better IntelliSense, type safety, and follows modern Vibe conventions.' in text, "expected to find: " + 'This approach provides better IntelliSense, type safety, and follows modern Vibe conventions.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/storybook-stories.mdc')
    assert 'When writing stories, always use string literal prop values instead of static properties:' in text, "expected to find: " + 'When writing stories, always use string literal prop values instead of static properties:'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/styling-conventions.mdc')
    assert 'description: "Provides comprehensive guidelines for writing CSS Modules specifically for UI components within the `@vibe/core` library (under `packages/core/src/components/`). This rule covers file na' in text, "expected to find: " + 'description: "Provides comprehensive guidelines for writing CSS Modules specifically for UI components within the `@vibe/core` library (under `packages/core/src/components/`). This rule covers file na'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/styling-conventions.mdc')
    assert '- **ALWAYS Use className Prop for Components:** When styling internal reusable components/base components, always use their `className` prop instead of targeting them in the scss file with other selec' in text, "expected to find: " + '- **ALWAYS Use className Prop for Components:** When styling internal reusable components/base components, always use their `className` prop instead of targeting them in the scss file with other selec'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/styling-conventions.mdc')
    assert '- **Always Use Logical CSS Properties:** Use logical CSS properties instead of physical properties to ensure proper RTL support and internationalization. Logical properties are direction-agnostic and ' in text, "expected to find: " + '- **Always Use Logical CSS Properties:** Use logical CSS properties instead of physical properties to ensure proper RTL support and internationalization. Logical properties are direction-agnostic and '[:80]

