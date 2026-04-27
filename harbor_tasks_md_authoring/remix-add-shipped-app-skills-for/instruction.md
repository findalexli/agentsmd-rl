# Add shipped app skills for Remix app development

Source: [remix-run/remix#11120](https://github.com/remix-run/remix/pull/11120)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `app-skills/add-sqlite-database/SKILL.md`
- `app-skills/new-route/SKILL.md`
- `app-skills/scaffold-remix-app/SKILL.md`

## What to add / change

This PR introduces a shipped `app-skills/` set aimed at people building Remix apps, separate from maintainer-only repo workflow skills.

- Adds a `scaffold-remix-app` skill that sets up a root controller/layout/page, router wiring, Node server boot via `tsx`, and an app-scoped test fixture.
- Adds an `add-sqlite-database` skill for wiring SQLite in `data/db.sqlite` with `lib/db.ts` exporting `db` from `remix/data-table`.
- Adds a `new-route` skill for extending route maps and handlers in a consistent style.

```tsx
export default {
  middleware: [],
  actions: {
    home() {
      return render(
        <Layout>
          <title>My Remix App</title>
          <HomePage />
        </Layout>,
      )
    },
  },
} satisfies Controller<typeof routes.root>
```

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
