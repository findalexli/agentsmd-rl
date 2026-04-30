#!/usr/bin/env bash
# Gold patch for TryGhost/Ghost#27177 — "Added i18n guidance to AGENTS.md".
# The new lines are inserted via a Python helper to avoid heredoc
# whitespace stripping; no external fetch.
set -euo pipefail

cd /workspace/Ghost

# Idempotency guard: a distinctive line from the gold patch.
if grep -qF '@doist/react-interpolate' AGENTS.md; then
    echo "Gold patch already applied; nothing to do."
    exit 0
fi

python3 <<'PYEOF'
from pathlib import Path

AGENTS = Path("/workspace/Ghost/AGENTS.md")
text = AGENTS.read_text()

anchor = "- 60+ supported locales\n"
addition = """- 60+ supported locales
- Context descriptions: `ghost/i18n/locales/context.json` — every key must have a non-empty description

**Translation Workflow:**
```bash
yarn workspace @tryghost/i18n translate   # Extract keys from source, update all locale files + context.json
yarn workspace @tryghost/i18n lint:translations  # Validate interpolation variables across locales
```

`yarn translate` is run as part of `yarn workspace @tryghost/i18n test`. In CI, it fails if translation keys or `context.json` are out of date (`failOnUpdate: process.env.CI`). Always run `yarn translate` after adding or changing `t()` calls.

**Rules for Translation Keys:**
1. **Never split sentences across multiple `t()` calls.** Translators cannot reorder words across separate keys. Instead, use `@doist/react-interpolate` to embed React elements (links, bold, etc.) within a single translatable string.
2. **Always provide context descriptions.** When adding a new key, add a description in `context.json` explaining where the string appears and what it does. CI will reject empty descriptions.
3. **Use interpolation for dynamic values.** Ghost uses `{variable}` syntax: `t('Welcome back, {name}!', {name: firstname})`
4. **Use `<tag>` syntax for inline elements.** Combined with `@doist/react-interpolate`: `t('Click <a>here</a> to retry')` with `mapping={{ a: <a href="..." /> }}`

**Correct pattern (using Interpolate):**
```jsx
import Interpolate from '@doist/react-interpolate';

<Interpolate
    mapping={{ a: <a href={link} /> }}
    string={t('Could not sign in. <a>Click here to retry</a>')}
/>
```

**Incorrect pattern (split sentences):**
```jsx
// BAD: translators cannot reorder "Click here to retry" relative to the first sentence
{t('Could not sign in.')} <a href={link}>{t('Click here to retry')}</a>
```

See `apps/portal/src/components/pages/email-receiving-faq.js` for a canonical example of correct `Interpolate` usage.
"""

if anchor not in text:
    raise SystemExit("Anchor line not found in AGENTS.md")
new_text = text.replace(anchor, addition, 1)
AGENTS.write_text(new_text)
print("Applied gold patch to AGENTS.md.")
PYEOF
