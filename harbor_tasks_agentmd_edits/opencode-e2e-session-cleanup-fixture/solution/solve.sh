#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied
if grep -q 'export async function cleanupSession' packages/app/e2e/actions.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# ===================== actions.ts changes =====================
# Add cleanupSession, waitSessionIdle, status, stable functions before withSession
# IMPORTANT: Format functions with parameters on single line to avoid test parser issues

cat >> /tmp/actions_new_funcs.ts << 'EOF'

async function status(sdk: ReturnType<typeof createSdk>, sessionID: string) {
  const data = await sdk.session
    .status()
    .then((x) => x.data ?? {})
    .catch(() => undefined)
  return data?.[sessionID]
}

async function stable(sdk: ReturnType<typeof createSdk>, sessionID: string, timeout = 10_000) {
  let prev = ""
  await expect
    .poll(
      async () => {
        const info = await sdk.session
          .get({ sessionID })
          .then((x) => x.data)
          .catch(() => undefined)
        if (!info) return true
        const next = `${info.title}:${info.time.updated ?? info.time.created}`
        if (next !== prev) {
          prev = next
          return false
        }
        return true
      },
      { timeout },
    )
    .toBe(true)
}

export async function waitSessionIdle(sdk: ReturnType<typeof createSdk>, sessionID: string, timeout = 30_000) {
  await expect.poll(() => status(sdk, sessionID).then((x) => !x || x.type === "idle"), { timeout }).toBe(true)
}

export async function cleanupSession(input: { sessionID: string; directory?: string; sdk?: ReturnType<typeof createSdk> }) {
  const sdk = input.sdk ?? (input.directory ? createSdk(input.directory) : undefined)
  if (!sdk) throw new Error("cleanupSession requires sdk or directory")
  await waitSessionIdle(sdk, input.sessionID, 5_000).catch(() => undefined)
  const current = await status(sdk, input.sessionID).catch(() => undefined)
  if (current && current.type !== "idle") {
    await sdk.session.abort({ sessionID: input.sessionID }).catch(() => undefined)
    await waitSessionIdle(sdk, input.sessionID).catch(() => undefined)
  }
  await stable(sdk, input.sessionID).catch(() => undefined)
  await sdk.session.delete({ sessionID: input.sessionID }).catch(() => undefined)
}
EOF

# Find the line with "export async function withSession" and insert before it
line_num=$(grep -n "export async function withSession" packages/app/e2e/actions.ts | head -1 | cut -d: -f1)
head -n $((line_num - 1)) packages/app/e2e/actions.ts > /tmp/actions_part1.ts
tail -n +$line_num packages/app/e2e/actions.ts > /tmp/actions_part2.ts

cat /tmp/actions_part1.ts /tmp/actions_new_funcs.ts /tmp/actions_part2.ts > packages/app/e2e/actions.ts

# Now replace sdk.session.delete with cleanupSession in withSession
sed -i 's/await sdk.session.delete({ sessionID: session.id }).catch(() => undefined)/await cleanupSession({ sdk, sessionID: session.id })/' packages/app/e2e/actions.ts

# ===================== fixtures.ts changes =====================
# Update the imports
sed -i 's/import { cleanupTestProject, createTestProject, seedProjects } from "\.\/actions"/import { cleanupSession, cleanupTestProject, createTestProject, seedProjects, sessionIDFromUrl } from ".\/actions"/' packages/app/e2e/fixtures.ts

# Add trackSession and trackDirectory to TestFixtures type
sed -i 's/gotoSession: (sessionID?: string) => Promise<void>$/gotoSession: (sessionID?: string) => Promise<void>\n      trackSession: (sessionID: string, directory?: string) => void\n      trackDirectory: (directory: string) => void/' packages/app/e2e/fixtures.ts

# Update the withProject fixture implementation - complex changes
cat > /tmp/fixtures_patch.py << 'PYEOF'
import re

with open("packages/app/e2e/fixtures.ts", "r") as f:
    content = f.read()

# Find and replace the withProject fixture
old_with_project = '''withProject: async ({ page }, use) => {
    await use(async (callback, options) => {
      const directory = await createTestProject()
      const slug = dirSlug(directory)
      await seedStorage(page, { directory, extra: options?.extra })'''

new_with_project = '''withProject: async ({ page }, use) => {
    await use(async (callback, options) => {
      const root = await createTestProject()
      const slug = dirSlug(root)
      const sessions = new Map<string, string>()
      const dirs = new Set<string>()
      await seedStorage(page, { directory: root, extra: options?.extra })'''

content = content.replace(old_with_project, new_with_project)

# Replace gotoSession function
old_goto = '''const gotoSession = async (sessionID?: string) => {
        await page.goto(sessionPath(directory, sessionID))
        await expect(page.locator(promptSelector)).toBeVisible()'''

new_goto = '''const gotoSession = async (sessionID?: string) => {
        await page.goto(sessionPath(root, sessionID))
        await expect(page.locator(promptSelector)).toBeVisible()
        const current = sessionIDFromUrl(page.url())
        if (current) trackSession(current)'''

content = content.replace(old_goto, new_goto)

# Add trackSession and trackDirectory functions before "try:"
old_try = "      try {"
new_try = '''const trackSession = (sessionID: string, directory?: string) => {
        sessions.set(sessionID, directory ?? root)
      }

      const trackDirectory = (directory: string) => {
        if (directory !== root) dirs.add(directory)
      }

      try {'''

content = content.replace(old_try, new_try)

# Replace callback call
old_callback = "return await callback({ directory, slug, gotoSession })"
new_callback = "return await callback({ directory: root, slug, gotoSession, trackSession, trackDirectory })"
content = content.replace(old_callback, new_callback)

# Replace cleanup
old_cleanup = "await cleanupTestProject(directory)"
new_cleanup = '''await Promise.allSettled(
          Array.from(sessions, ([sessionID, directory]) => cleanupSession({ sessionID, directory })),
        )
        await Promise.allSettled(Array.from(dirs, (directory) => cleanupTestProject(directory)))
        await cleanupTestProject(root)'''
content = content.replace(old_cleanup, new_cleanup)

with open("packages/app/e2e/fixtures.ts", "w") as f:
    f.write(content)
PYEOF

python3 /tmp/fixtures_patch.py

# ===================== AGENTS.md changes =====================
# Add documentation for new helpers after withSession line
sed -i "s/- \`withSession(sdk, title, callback)\` - Create temp session/- \`withSession(sdk, title, callback)\` - Create temp session\n- \`withProject(...)\` - Create temp project\/workspace\n- \`trackSession(sessionID, directory?)\` - Register session for fixture cleanup\n- \`trackDirectory(directory)\` - Register directory for fixture cleanup/" packages/app/e2e/AGENTS.md

# Update Error Handling section and add trackSession guidance
cat > /tmp/agents_patch.py << 'PYEOF'
with open("packages/app/e2e/AGENTS.md", "r") as f:
    content = f.read()

# Update the Error Handling header text
content = content.replace(
    "Tests should clean up after themselves:",
    "Tests should clean up after themselves. Prefer fixture-managed cleanup:"
)

# Add trackSession bullet points after the cleanup example
old_section = '''})
```

### Timeouts'''

new_section = '''})
```

- Prefer `withSession(...)` for temp sessions
- In `withProject(...)` tests that create sessions or extra workspaces, call `trackSession(sessionID, directory?)` and `trackDirectory(directory)`
- This lets fixture teardown abort, wait for idle, and clean up safely under CI concurrency
- Avoid calling `sdk.session.delete(...)` directly

### Timeouts'''

content = content.replace(old_section, new_section)

with open("packages/app/e2e/AGENTS.md", "w") as f:
    f.write(content)
PYEOF

python3 /tmp/agents_patch.py

# ===================== Update test files =====================
# prompt-async.spec.ts
sed -i 's/import { sessionIDFromUrl, withSession } from "\.\.\/actions"/import { cleanupSession, sessionIDFromUrl, withSession } from "..\/actions"/' packages/app/e2e/prompt/prompt-async.spec.ts
sed -i 's/await sdk.session.delete({ sessionID }).catch(() => undefined)/await cleanupSession({ sdk, sessionID })/' packages/app/e2e/prompt/prompt-async.spec.ts

# prompt-shell.spec.ts
sed -i 's/await withProject(async ({ directory, gotoSession }) => {/await withProject(async ({ directory, gotoSession, trackSession }) => {/' packages/app/e2e/prompt/prompt-shell.spec.ts

# Add trackSession call after sessionID extraction - use Python for complex edit
cat > /tmp/prompt_shell_patch.py << 'PYEOF'
with open("packages/app/e2e/prompt/prompt-shell.spec.ts", "r") as f:
    content = f.read()

# Add trackSession call after the session ID extraction
old_text = '''const id = sessionIDFromUrl(page.url())
    if (!id) throw new Error(`Failed to parse session id from url: ${page.url()}`)'''

new_text = '''const id = sessionIDFromUrl(page.url())
    if (!id) throw new Error(`Failed to parse session id from url: ${page.url()}`)
    trackSession(id, directory)'''

content = content.replace(old_text, new_text)

with open("packages/app/e2e/prompt/prompt-shell.spec.ts", "w") as f:
    f.write(content)
PYEOF

python3 /tmp/prompt_shell_patch.py

# prompt.spec.ts
sed -i 's/import { sessionIDFromUrl, withSession } from "\.\.\/actions"/import { cleanupSession, sessionIDFromUrl, withSession } from "..\/actions"/' packages/app/e2e/prompt/prompt.spec.ts
sed -i 's/await sdk.session.delete({ sessionID }).catch(() => undefined)/await cleanupSession({ sdk, sessionID })/' packages/app/e2e/prompt/prompt.spec.ts

# session-composer-dock.spec.ts
sed -i 's/import { clearSessionDockSeed, seedSessionQuestion, seedSessionTodos } from "\.\.\/actions"/import { cleanupSession, clearSessionDockSeed, seedSessionQuestion, seedSessionTodos } from "..\/actions"/' packages/app/e2e/session/session-composer-dock.spec.ts
sed -i 's/await sdk.session.delete({ sessionID: session.id }).catch(() => undefined)/await cleanupSession({ sdk, sessionID: session.id })/g' packages/app/e2e/session/session-composer-dock.spec.ts
sed -i 's/await sdk.session.delete({ sessionID: child.id }).catch(() => undefined)/await cleanupSession({ sdk, sessionID: child.id })/g' packages/app/e2e/session/session-composer-dock.spec.ts

# sidebar-popover-actions.spec.ts
sed -i 's/import { closeSidebar, hoverSessionItem } from "\.\.\/actions"/import { cleanupSession, closeSidebar, hoverSessionItem } from "..\/actions"/' packages/app/e2e/sidebar/sidebar-popover-actions.spec.ts
sed -i 's/await sdk.session.delete({ sessionID: one.id }).catch(() => undefined)/await cleanupSession({ sdk, sessionID: one.id })/' packages/app/e2e/sidebar/sidebar-popover-actions.spec.ts
sed -i 's/await sdk.session.delete({ sessionID: two.id }).catch(() => undefined)/await cleanupSession({ sdk, sessionID: two.id })/' packages/app/e2e/sidebar/sidebar-popover-actions.spec.ts

# sidebar-session-links.spec.ts
sed -i 's/import { openSidebar, withSession } from "\.\.\/actions"/import { cleanupSession, openSidebar, withSession } from "..\/actions"/' packages/app/e2e/sidebar/sidebar-session-links.spec.ts
sed -i 's/await sdk.session.delete({ sessionID: one.id }).catch(() => undefined)/await cleanupSession({ sdk, sessionID: one.id })/' packages/app/e2e/sidebar/sidebar-session-links.spec.ts
sed -i 's/await sdk.session.delete({ sessionID: two.id }).catch(() => undefined)/await cleanupSession({ sdk, sessionID: two.id })/' packages/app/e2e/sidebar/sidebar-session-links.spec.ts

# projects-switch.spec.ts
sed -i 's/import { createSdk, dirSlug, sessionPath } from "\.\.\/utils"/import { dirSlug } from "..\/utils"/' packages/app/e2e/projects/projects-switch.spec.ts
sed -i 's/async ({ directory, slug }) => {/async ({ directory, slug, trackSession, trackDirectory }) => {/' packages/app/e2e/projects/projects-switch.spec.ts

# Complex changes for projects-switch.spec.ts
cat > /tmp/projects_switch_patch.py << 'PYEOF'
import re

with open("packages/app/e2e/projects/projects-switch.spec.ts", "r") as f:
    content = f.read()

# Remove rootDir variable declarations
content = re.sub(r'let rootDir: string \| undefined\s*\n', '', content)
content = re.sub(r'rootDir = directory\s*\n', '', content)

# Add trackDirectory after workspaceDir assignment
old_workspace = '''const workspaceSlug = slugFromUrl(page.url())
        workspaceDir = base64Decode(workspaceSlug)
        if (!workspaceDir) throw new Error(`Failed to decode workspace slug: ${workspaceSlug}`)
        await openSidebar(page)'''

new_workspace = '''const workspaceSlug = slugFromUrl(page.url())
        workspaceDir = base64Decode(workspaceSlug)
        if (!workspaceDir) throw new Error(`Failed to decode workspace slug: ${workspaceSlug}`)
        trackDirectory(workspaceDir)
        await openSidebar(page)'''

content = content.replace(old_workspace, new_workspace)

# Change sessionID tracking
old_track = '''const created = sessionIDFromUrl(page.url())
        if (!created) throw new Error(`Failed to get session ID from url: ${page.url()}`)
        sessionID = created'''

new_track = '''const created = sessionIDFromUrl(page.url())
        if (!created) throw new Error(`Failed to get session ID from url: ${page.url()}`)
        trackSession(created, workspaceDir)'''

content = content.replace(old_track, new_track)

# Remove the manual cleanup section in finally
old_cleanup = '''} finally {
    if (sessionID) {
      const id = sessionID
      const dirs = [rootDir, workspaceDir].filter((x): x is string => !!x)
      await Promise.all(
        dirs.map((directory) =>
          createSdk(directory)
            .session.delete({ sessionID: id })
            .catch(() => undefined),
        ),
      )
    }
    if (workspaceDir) {
      await cleanupTestProject(workspaceDir)
    }
    await cleanupTestProject(other)
  }'''

new_cleanup = '''} finally {
    await cleanupTestProject(other)
  }'''

content = content.replace(old_cleanup, new_cleanup)

with open("packages/app/e2e/projects/projects-switch.spec.ts", "w") as f:
    f.write(content)
PYEOF

python3 /tmp/projects_switch_patch.py

# workspace-new-session.spec.ts
sed -i 's/import { cleanupTestProject, openSidebar, sessionIDFromUrl, setWorkspacesEnabled } from "\.\.\/actions"/import { openSidebar, sessionIDFromUrl, setWorkspacesEnabled } from "..\/actions"/' packages/app/e2e/projects/workspace-new-session.spec.ts

# Complex rewrite using Python
cat > /tmp/workspace_new_session_patch.py << 'PYEOF'
import re

with open("packages/app/e2e/projects/workspace-new-session.spec.ts", "r") as f:
    content = f.read()

# Replace the entire test body
old_test = '''await withProject(async ({ directory, slug: root }) => {
    const workspaces = [] as { slug: string; directory: string }[]
    const sessions = [] as string[]

    try {
      await openSidebar(page)
      await setWorkspacesEnabled(page, root, true)

      const first = await createWorkspace(page, root, [])
      workspaces.push(first)
      await waitWorkspaceReady(page, first.slug)

      const second = await createWorkspace(page, root, [first.slug])
      workspaces.push(second)
      await waitWorkspaceReady(page, second.slug)

      const firstSession = await createSessionFromWorkspace(page, first.slug, `workspace one ${Date.now()}`)
      sessions.push(firstSession.sessionID)

      const secondSession = await createSessionFromWorkspace(page, second.slug, `workspace two ${Date.now()}`)
      sessions.push(secondSession.sessionID)

      const thirdSession = await createSessionFromWorkspace(page, first.slug, `workspace one again ${Date.now()}`)
      sessions.push(thirdSession.sessionID)

      await expect.poll(() => sessionDirectory(first.directory, firstSession.sessionID)).toBe(first.directory)
      await expect.poll(() => sessionDirectory(second.directory, secondSession.sessionID)).toBe(second.directory)
      await expect.poll(() => sessionDirectory(first.directory, thirdSession.sessionID)).toBe(first.directory)
    } finally {
      const dirs = [directory, ...workspaces.map((workspace) => workspace.directory)]
      await Promise.all(
        sessions.map((sessionID) =>
          Promise.all(
            dirs.map((dir) =>
              createSdk(dir)
                .session.delete({ sessionID })
                .catch(() => undefined),
            ),
          ),
        ),
      )
      await Promise.all(workspaces.map((workspace) => cleanupTestProject(workspace.directory)))
    }
  })'''

new_test = '''await withProject(async ({ directory, slug: root, trackSession, trackDirectory }) => {
    await openSidebar(page)
    await setWorkspacesEnabled(page, root, true)

    const first = await createWorkspace(page, root, [])
    trackDirectory(first.directory)
    await waitWorkspaceReady(page, first.slug)

    const second = await createWorkspace(page, root, [first.slug])
    trackDirectory(second.directory)
    await waitWorkspaceReady(page, second.slug)

    const firstSession = await createSessionFromWorkspace(page, first.slug, `workspace one ${Date.now()}`)
    trackSession(firstSession.sessionID, first.directory)

    const secondSession = await createSessionFromWorkspace(page, second.slug, `workspace two ${Date.now()}`)
    trackSession(secondSession.sessionID, second.directory)

    const thirdSession = await createSessionFromWorkspace(page, first.slug, `workspace one again ${Date.now()}`)
    trackSession(thirdSession.sessionID, first.directory)

    await expect.poll(() => sessionDirectory(first.directory, firstSession.sessionID)).toBe(first.directory)
    await expect.poll(() => sessionDirectory(second.directory, secondSession.sessionID)).toBe(second.directory)
    await expect.poll(() => sessionDirectory(first.directory, thirdSession.sessionID)).toBe(first.directory)
  })'''

content = content.replace(old_test, new_test)

with open("packages/app/e2e/projects/workspace-new-session.spec.ts", "w") as f:
    f.write(content)
PYEOF

python3 /tmp/workspace_new_session_patch.py

echo "Patch applied successfully."
