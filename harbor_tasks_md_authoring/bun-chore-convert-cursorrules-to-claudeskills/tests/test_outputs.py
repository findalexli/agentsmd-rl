"""Behavioral checks for bun-chore-convert-cursorrules-to-claudeskills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/bun")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/implementing-jsc-classes-cpp/SKILL.md')
    assert '{ "property"_s, static_cast<unsigned>(PropertyAttribute::ReadOnly | PropertyAttribute::CustomAccessor), NoIntrinsic, { HashTableValue::GetterSetterType, jsFooGetter_property, 0 } },' in text, "expected to find: " + '{ "property"_s, static_cast<unsigned>(PropertyAttribute::ReadOnly | PropertyAttribute::CustomAccessor), NoIntrinsic, { HashTableValue::GetterSetterType, jsFooGetter_property, 0 } },'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/implementing-jsc-classes-cpp/SKILL.md')
    assert 'putDirectWithoutTransition(vm, vm.propertyNames->prototype, prototype, JSC::PropertyAttribute::DontEnum | JSC::PropertyAttribute::DontDelete | JSC::PropertyAttribute::ReadOnly);' in text, "expected to find: " + 'putDirectWithoutTransition(vm, vm.propertyNames->prototype, prototype, JSC::PropertyAttribute::DontEnum | JSC::PropertyAttribute::DontDelete | JSC::PropertyAttribute::ReadOnly);'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/implementing-jsc-classes-cpp/SKILL.md')
    assert 'description: Implements JavaScript classes in C++ using JavaScriptCore. Use when creating new JS classes with C++ bindings, prototypes, or constructors.' in text, "expected to find: " + 'description: Implements JavaScript classes in C++ using JavaScriptCore. Use when creating new JS classes with C++ bindings, prototypes, or constructors.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/implementing-jsc-classes-zig/SKILL.md')
    assert "description: Creates JavaScript classes using Bun's Zig bindings generator (.classes.ts). Use when implementing new JS APIs in Zig with JSC integration." in text, "expected to find: " + "description: Creates JavaScript classes using Bun's Zig bindings generator (.classes.ts). Use when implementing new JS APIs in Zig with JSC integration."[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/implementing-jsc-classes-zig/SKILL.md')
    assert 'pub fn myMethod(this: *MyClass, globalObject: *JSGlobalObject, callFrame: *JSC.CallFrame) bun.JSError!JSC.JSValue {' in text, "expected to find: " + 'pub fn myMethod(this: *MyClass, globalObject: *JSGlobalObject, callFrame: *JSC.CallFrame) bun.JSError!JSC.JSValue {'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/implementing-jsc-classes-zig/SKILL.md')
    assert 'pub fn method(this: *MyClass, globalObject: *JSGlobalObject, callFrame: *JSC.CallFrame) bun.JSError!JSC.JSValue {' in text, "expected to find: " + 'pub fn method(this: *MyClass, globalObject: *JSGlobalObject, callFrame: *JSC.CallFrame) bun.JSError!JSC.JSValue {'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/writing-bundler-tests/SKILL.md')
    assert 'description: Guides writing bundler tests using itBundled/expectBundled in test/bundler/. Use when creating or modifying bundler, transpiler, or code transformation tests.' in text, "expected to find: " + 'description: Guides writing bundler tests using itBundled/expectBundled in test/bundler/. Use when creating or modifying bundler, transpiler, or code transformation tests.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/writing-bundler-tests/SKILL.md')
    assert "Bundler tests use `itBundled()` from `test/bundler/expectBundled.ts` to test Bun's bundler." in text, "expected to find: " + "Bundler tests use `itBundled()` from `test/bundler/expectBundled.ts` to test Bun's bundler."[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/writing-bundler-tests/SKILL.md')
    assert 'Test ID format: `category/TestName` (e.g., `banner/CommentBanner`, `minify/Empty`)' in text, "expected to find: " + 'Test ID format: `category/TestName` (e.g., `banner/CommentBanner`, `minify/Empty`)'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/writing-dev-server-tests/SKILL.md')
    assert 'description: Guides writing HMR/Dev Server tests in test/bake/. Use when creating or modifying dev server, hot reloading, or bundling tests.' in text, "expected to find: " + 'description: Guides writing HMR/Dev Server tests in test/bake/. Use when creating or modifying dev server, hot reloading, or bundling tests.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/writing-dev-server-tests/SKILL.md')
    assert '- `test/bake/bake-harness.ts` - shared utilities: `devTest`, `prodTest`, `devAndProductionTest`, `Dev` class, `Client` class' in text, "expected to find: " + '- `test/bake/bake-harness.ts` - shared utilities: `devTest`, `prodTest`, `devAndProductionTest`, `Dev` class, `Client` class'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/writing-dev-server-tests/SKILL.md')
    assert '"index.html": `<!DOCTYPE html><html><head></head><body><script type="module" src="/script.ts"></script></body></html>`,' in text, "expected to find: " + '"index.html": `<!DOCTYPE html><html><head></head><body><script type="module" src="/script.ts"></script></body></html>`,'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/zig-system-calls/SKILL.md')
    assert 'description: Guides using bun.sys for system calls and file I/O in Zig. Use when implementing file operations instead of std.fs or std.posix.' in text, "expected to find: " + 'description: Guides using bun.sys for system calls and file I/O in Zig. Use when implementing file operations instead of std.fs or std.posix.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/zig-system-calls/SKILL.md')
    assert 'Use `bun.sys` instead of `std.fs` or `std.posix` for cross-platform syscalls with proper error handling.' in text, "expected to find: " + 'Use `bun.sys` instead of `std.fs` or `std.posix` for cross-platform syscalls with proper error handling.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/zig-system-calls/SKILL.md')
    assert 'const file = switch (File.open(path, bun.O.WRONLY | bun.O.CREAT | bun.O.TRUNC, 0o664)) {' in text, "expected to find: " + 'const file = switch (File.open(path, bun.O.WRONLY | bun.O.CREAT | bun.O.TRUNC, 0o664)) {'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/building-bun.mdc')
    assert '.cursor/rules/building-bun.mdc' in text, "expected to find: " + '.cursor/rules/building-bun.mdc'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/dev-server-tests.mdc')
    assert '.cursor/rules/dev-server-tests.mdc' in text, "expected to find: " + '.cursor/rules/dev-server-tests.mdc'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/javascriptcore-class.mdc')
    assert '.cursor/rules/javascriptcore-class.mdc' in text, "expected to find: " + '.cursor/rules/javascriptcore-class.mdc'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/registering-bun-modules.mdc')
    assert '.cursor/rules/registering-bun-modules.mdc' in text, "expected to find: " + '.cursor/rules/registering-bun-modules.mdc'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/writing-tests.mdc')
    assert '.cursor/rules/writing-tests.mdc' in text, "expected to find: " + '.cursor/rules/writing-tests.mdc'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/zig-javascriptcore-classes.mdc')
    assert '.cursor/rules/zig-javascriptcore-classes.mdc' in text, "expected to find: " + '.cursor/rules/zig-javascriptcore-classes.mdc'[:80]

