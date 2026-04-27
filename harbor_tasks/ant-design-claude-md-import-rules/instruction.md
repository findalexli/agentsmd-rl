# Document import-path conventions in `CLAUDE.md`

The repository's `CLAUDE.md` file is the AI-coding-assistant guide for the
ant-design project. It currently documents the project layout, doc style, PR
rules, and Changelog format, but says nothing about how files in `demo/`
folders versus files in `__tests__/` folders are expected to import the
project's components and helpers. The two directory trees use **opposite**
import conventions, and contributors keep getting it wrong, so the two rules
need to be added to `CLAUDE.md`.

Open `CLAUDE.md` (at the repository root) and add **two new sibling sections**
to the file. The sections must:

- Use heading level `##` (top-level sub-section, matching the existing `##
  文档规范`, `## PR 规范`, etc.).
- Be written in **Chinese**, matching the language and bullet-list style used
  throughout the rest of the file.
- Use single-backtick inline code formatting for every path glob, file name,
  package specifier, and import-path example.
- Appear together as a pair, with the Demo rule first and the Test rule
  immediately after, placed somewhere between the existing project-info /
  structure block at the top of the file and the existing `## 文档规范`
  section. A horizontal rule (`---`) should separate the new pair from the
  `## 文档规范` block that follows, matching the rule-separator style already
  used elsewhere in the file.

## Section 1 — heading must be exactly `## Demo 导入规范`

Document the import convention for **demo and site files**. Bulleted rules,
covering each of the points below:

- **Scope.** The rule applies to both `components/**/demo/` and `.dumi/`
  example/site/theme files. Files named `semantic.test.tsx` are excluded from
  the rule.
- **Direction.** Inside those directories, when importing Ant Design
  components, internal modules, utility functions, variables, or type
  definitions, **absolute** imports must be used; **relative** imports are
  forbidden.
- **Allowed forms.** Prefer the project's public package entries and
  configured aliases. The allowed forms include: `antd`, `antd/es/*`,
  `antd/lib/*`, `antd/locale/*`, `.dumi/*`, and `@@/*`.
- **Forbidden forms.** Relative-path imports are not allowed for referencing
  component implementations, internal modules, methods, variables, or types.
  Explicitly forbid the patterns `..`, `../xxx`, `../../xxx`, and `./xxx`,
  including across-demo and across-directory reuse.
- **Demo ↔ `.dumi` cross-imports.** Demo files and `.dumi` files must not
  reference each other via relative paths. If a small piece of logic must be
  reused, inline it, or extract it into a location reachable through an
  absolute path.

## Section 2 — heading must be exactly `## Test 导入规范`

Document the **opposite** convention for test files. Bulleted rules, covering
each of the points below:

- **Scope.** The rule applies to test files under
  `components/**/__tests__/`.
- **Direction.** Inside those directories, when importing Ant Design
  components, internal modules, utility functions, variables, or type
  definitions, **relative** imports must be used; absolute imports are
  forbidden.
- **Allowed forms.** Test files should reach the current component
  directory, neighbouring internal modules, or the shared test-utility
  directory through relative paths. Examples of allowed forms include `..`,
  `../index`, `../xxx`, `../../_util/*`, and `../../../tests/shared/*`.
- **Forbidden forms inside `__tests__`.** It is not allowed to reference
  in-repo code via the absolute or alias forms `antd`, `antd/es/*`,
  `antd/lib/*`, `antd/locale/*`, `.dumi/*`, and `@@/*`.
- **Third-party dependencies.** Imports of third-party packages (e.g.
  `react`, `@testing-library/react`, `dayjs`) are still done by package name,
  as usual.

## Out of scope

- Do not modify any other file. Only `CLAUDE.md` should change.
- Do not rewrite or reorder existing sections of `CLAUDE.md`; only add the
  two new sections.
