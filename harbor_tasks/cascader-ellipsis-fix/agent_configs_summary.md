# Agent Configuration Summary for Cascader Ellipsis Task

## Applicable Agent Config Files

Based on the PR touching `components/cascader/style/columns.ts` (a style file), the following configs apply:

### Root-level configs (always apply)

1. **CLAUDE.md** (and AGENTS.md - duplicate content)
   - Demo import conventions (absolute paths)
   - Test import conventions (relative paths)
   - Documentation standards (API tables, anchor IDs)
   - PR conventions (title format, branch strategy)
   - Changelog format (emoji, structure)

2. **.github/copilot-instructions.md**
   - TypeScript strict requirements
   - React component guidelines
   - Styling approach (@ant-design/cssinjs)
   - CSS logical properties for RTL
   - No hardcoded values

### Subdirectory configs

None applicable - the PR only touches the style file.

### Skill configs

None directly applicable to this specific bug fix task.

## Relevant Rules for This Task

### From CLAUDE.md / copilot-instructions.md:

1. **Styling Approach**:
   - Use `@ant-design/cssinjs` for styling
   - Use design tokens from the Ant Design token system
   - Never hardcode colors, sizes, or spacing values
   - Use CSS logical properties for RTL support
   - Generate styles with `gen[ComponentName]Style` pattern

2. **TypeScript Requirements**:
   - Use TypeScript with strict type checking
   - Never use `any` type
   - Use interfaces for object structures

3. **File Organization**:
   - Styles in `style/` directory
   - Component styles defined in `style/columns.ts` for Cascader

## Programmatic Checkable Rules

| Rule | Check Method |
|------|-------------|
| Uses CSS-in-JS (@ant-design/cssinjs) | Import check + function signature |
| Uses GenerateStyle pattern | AST check for function name |
| Uses CascaderToken | Type annotation check |
| No hardcoded colors | Scan for color literals |

## Soft/Subjective Rules (for rubric)

- CSS fix follows Ant Design patterns
- Flexbox ellipsis implementation is correct
- No breaking changes to existing styles
