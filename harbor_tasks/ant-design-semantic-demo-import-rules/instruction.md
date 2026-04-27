# Clarify the Demo 导入规范 rules in CLAUDE.md

You are working in the repository root at `/workspace/ant-design`. The
file `CLAUDE.md` at the repo root is the agent-instruction document for
this project. The "## Demo 导入规范" section currently states a single
blanket rule that applies to **both** `components/**/demo/` files and
`.dumi/` files: imports of Ant Design components, internal modules,
utilities, variables and types must use absolute paths only, with the
allowed forms listed as `antd`, `antd/es/*`, `antd/lib/*`,
`antd/locale/*`, `.dumi/*`, `@@/*`.

This blanket rule is incorrect in two ways and is causing a downstream
AI review tool to flag legitimate code as a violation:

1. **The `_semantic*.tsx` demo files are an exception.** Files matching
   the pattern `components/**/demo/_semantic*.tsx` are not regular
   demos — they are 语义文档专用 demo (semantic-documentation demos)
   that drive the site's "Semantic DOM" pages. By design they have to
   import doc-site helpers such as `.dumi/hooks/useLocale` and
   `.dumi/theme/common/*`, and they reference these helpers via
   relative paths because the `.dumi` site code is co-located in the
   same repository, not exposed through a public package entry. The
   AI reviewer keeps mistaking these legitimate relative imports for
   rule violations.

2. **`.dumi/*` is not actually a TypeScript path alias.** The current
   wording lists `.dumi/*` alongside `antd/*` and `@@/*` as if it were
   a path alias, but the project's `tsconfig` has no such alias. Code
   that needs to reach `.dumi` modules has to use a relative path
   based on its file location. Including `.dumi/*` in the "allowed
   absolute / aliased forms" list misleads the review agent.

## What to do

Edit the "## Demo 导入规范" section of `CLAUDE.md` so that the rules
distinguish three groups — regular `components/**/demo/` files, the
`_semantic*.tsx` exception, and `.dumi/` site-implementation files —
and so that the `.dumi/*` path-alias confusion is corrected.

Your edits must, at minimum, satisfy the following requirements:

- A bullet must establish that `_semantic*.tsx` 属于语义文档专用 demo
  and is an exception that may use relative-path imports for site-side
  helpers. Use the exact filename glob `components/**/demo/_semantic*.tsx`
  when describing which files this exception covers.

- The exception bullet must concretely list `.dumi/hooks/useLocale`
  (and `.dumi/theme/common/*`) as examples of the helper modules that
  `_semantic*.tsx` files are allowed to import via relative paths.

- A bullet must clarify that `.dumi/*` 不是仓库通用的 TS 路径别名 —
  i.e. `.dumi/*` is not a project-wide TypeScript path alias, and code
  that needs to access modules under `.dumi/` should use a relative
  path based on its own file location. Remove `.dumi/*` from any list
  of "allowed absolute / aliased import forms".

- The remaining rules (absolute-path requirement for regular demos,
  prohibition on `..`/`../xxx`/`./xxx` for internal-module references
  in regular demos, and the cross-tree "no relative imports between
  demo and `.dumi`" rule) must continue to apply to the regular
  `components/**/demo/` case. The cross-tree rule needs to acknowledge
  that the `_semantic*.tsx` reuse of `.dumi` helpers is the exception.

## Constraints

- Edit only `CLAUDE.md`. Do not change anything else in the repository.
- Keep the section formatted as a markdown bullet list, consistent
  with the surrounding sections of `CLAUDE.md`.
- Continue writing in 简体中文, matching the rest of `CLAUDE.md`.
- Use backticks around code paths, glob patterns and import specifiers
  (`components/**/demo/`, `.dumi/hooks/useLocale`, `.dumi/*`,
  `_semantic*.tsx`, etc.), as the existing file does.
- Do not move, rename or remove any heading. The section heading
  "## Demo 导入规范" must remain. The adjacent "## Test 导入规范"
  section and the downstream "## PR 规范" section must be left
  untouched. Do not modify any file other than `CLAUDE.md`.
