#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cypress

# Idempotent: skip if already applied
if grep -q 'strictDomain' packages/server/lib/automation/util.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

python3 - <<'PYEOF'
# --- Fix util.ts ---
path = "packages/server/lib/automation/util.ts"
with open(path) as f:
    content = f.read()

# Update function signature to accept strictDomain option
content = content.replace(
    "export const cookieMatches = (cookie: CyCookie | playwright.Cookie, filter?: CyCookieFilter) => {",
    "export const cookieMatches = (cookie: CyCookie | playwright.Cookie, filter?: CyCookieFilter, options?: { strictDomain: boolean }) => {"
)

# Update domain matching logic: strict = exact match, non-strict = domainMatch
content = content.replace(
    "  if (filter?.domain && !domainMatch(filter?.domain, cookie.domain)) {\n    return false\n  }",
    "  if (filter?.domain) {\n    if (options?.strictDomain ? filter?.domain !== cookie.domain : !domainMatch(filter?.domain, cookie.domain))\n    return false\n  }"
)

with open(path, "w") as f:
    f.write(content)

# --- Fix webkit-automation.ts ---
path = "packages/server/lib/browsers/webkit-automation.ts"
with open(path) as f:
    content = f.read()

# Replace single-pass getCookie matching with two-pass (strict then apex)
old_getcookie = """    const cookie = cookies.find((cookie) => {
      return cookieMatches(cookie, filter)
    })

    if (!cookie) return null"""

new_getcookie = """    // first attempt to match cookie on strict domain
    let cookie = cookies.find((cookie) => {
      return cookieMatches(cookie, filter, { strictDomain: true })
    })

    if (!cookie) {
      cookie = cookies.find((cookie) => {
          // if unable to match closest via strict domain, then return a cookie that matches the apex domain
        return cookieMatches(cookie, filter)
      })

      if (!cookie) return null
    }"""

content = content.replace(old_getcookie, new_getcookie)

with open(path, "w") as f:
    f.write(content)

# --- Fix electron-upgrade.mdc ---
path = "packages/electron/.cursor/rules/electron-upgrade.mdc"
with open(path) as f:
    content = f.read()

# Update Docker Compose section: bullseye -> trixie
content = content.replace(
    '# "cypress/base-internal:22.18.0-bullseye" -> "cypress/base-internal:NEW_NODE_VERSION-bullseye"',
    '# "cypress/base-internal:22.18.0-trixie" -> "cypress/base-internal:NEW_NODE_VERSION-trixie"'
)

# Update CircleCI section: bullseye -> trixie (anchor name + image ref)
content = content.replace(
    '# "base-internal-bullseye: &base-internal-bullseye cypress/base-internal:22.18.0-bullseye" -> "base-internal-bullseye: &base-internal-bullseye cypress/base-internal:NEW_NODE_VERSION-bullseye"',
    '# "base-internal-trixie: &base-internal-trixie cypress/base-internal:22.18.0-trixie" -> "base-internal-trixie: &base-internal-trixie cypress/base-internal:NEW_NODE_VERSION-trixie"'
)

with open(path, "w") as f:
    f.write(content)

PYEOF

echo "Patch applied successfully."
