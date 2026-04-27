# Document i18n / translation rules in `AGENTS.md`

`/workspace/Ghost` is a checkout of the [Ghost](https://github.com/TryGhost/Ghost) monorepo. The repository's `AGENTS.md` (an instruction file consumed by AI coding agents) already has a short `### i18n Architecture` section, but it only describes *where* translations live — it says nothing about *how* contributors are expected to write translatable strings. Translation contributors have flagged that split-sentence keys make proper localization impossible, and new contributors keep re-discovering the rules by trial and error.

Your job is to expand the `### i18n Architecture` section of `AGENTS.md` so that a developer (or an AI agent) reading it knows the rules before adding any new `t(...)` call. The new guidance must be appended **inside** the existing `### i18n Architecture` section (between the existing bullet list and the next `### ` heading), and the existing bullets / heading must remain intact.

## What the new content must cover

The expanded section must document each of the items below. Wording can be paraphrased, but the **bolded literal phrases below must appear verbatim** because downstream tooling and other docs will link or grep for them.

1. **Context descriptions file.** Mention the file `ghost/i18n/locales/context.json` and state that every translation key must have a non-empty description (CI rejects empty ones).

2. **Translation workflow commands.** Document the two yarn workspace commands developers run:
   - `yarn workspace @tryghost/i18n translate` — extracts keys from source, updates all locale files and `context.json`.
   - `yarn workspace @tryghost/i18n lint:translations` — validates interpolation variables across locales.

   Also explain that `yarn translate` runs as part of `yarn workspace @tryghost/i18n test` and fails in CI when translation keys or `context.json` are out of date (the underlying flag is `failOnUpdate: process.env.CI`). Tell readers to run `yarn translate` after adding or changing `t()` calls.

3. **Rules for translation keys.** A numbered list with at least these four rules. Use the exact bolded headings shown:
   1. **Never split sentences across multiple `t()` calls.** Explain that translators cannot reorder words across separate keys, and that the fix is to use `@doist/react-interpolate` to embed React elements inside a single translatable string.
   2. **Always provide context descriptions.** Every new key needs a description in `context.json` explaining where the string appears and what it does. CI will reject empty descriptions.
   3. **Use interpolation for dynamic values.** Ghost uses `{variable}` syntax — show an example like `t('Welcome back, {name}!', {name: firstname})`.
   4. **Use `<tag>` syntax for inline elements.** Combined with `@doist/react-interpolate`, e.g. `t('Click <a>here</a> to retry')` with `mapping={{ a: <a href="..." /> }}`.

4. **A correct pattern example** under a heading **Correct pattern** showing the recommended use of `Interpolate` from `@doist/react-interpolate`. The example must include the line `import Interpolate from '@doist/react-interpolate';` and use `<Interpolate>` with `mapping` and `string` props.

5. **An incorrect pattern example** under a heading **Incorrect pattern** showing the split-sentence anti-pattern (two separate `t()` calls split by an `<a>` tag) so readers can recognize the bug shape.

6. **A reference to a canonical in-repo example.** End the new content with a line that points readers to `apps/portal/src/components/pages/email-receiving-faq.js` as a canonical example of correct `Interpolate` usage.

## Constraints

- Edit only `/workspace/Ghost/AGENTS.md`. Do not touch `CLAUDE.md` or any other file.
- The new content must live inside the existing `### i18n Architecture` section, before the next `### ` heading (which is `### Build Dependencies (Nx)`).
- The PR is purely additive: do not delete or reword the existing bullets in that section, do not change other sections, and do not change the surrounding markdown's formatting conventions.
- Code blocks should use fenced code blocks; the bash commands block should be tagged ` ```bash ` and the JSX examples ` ```jsx `.
- Match the existing style of `AGENTS.md`: short bolded sub-headings (e.g. `**Translation Workflow:**`), bullet lists, and inline backticks for filenames, command names, and code symbols.
