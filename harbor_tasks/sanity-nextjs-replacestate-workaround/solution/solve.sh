#!/bin/bash
set -e

cd /workspace/sanity

# Fix sessionId.ts - add clearSessionId function after consumeSessionId function
SESSION_ID_FILE="packages/sanity/src/core/store/_legacy/authStore/sessionId.ts"

# Add clearSessionId export after the consumeSessionId function
sed -i '/^function consumeSession/,/^}$/{ /^}$/a\
\
/**\
 * Provides a workaround for https://github.com/vercel/next.js/issues/91819\
 * Can be removed once that'\''s fixed\
 */\
export function clearSessionId(): void {\
  consumeSessionId()\
}
}' "$SESSION_ID_FILE"

# Fix createAuthStore.ts - update import and add clearSessionId call
AUTH_STORE_FILE="packages/sanity/src/core/store/_legacy/authStore/createAuthStore.ts"

# Update the import line
sed -i "s/import {getSessionId} from '.\/sessionId'/import {clearSessionId, getSessionId} from '.\/sessionId'/" "$AUTH_STORE_FILE"

# Add clearSessionId call after getSessionId in handleCallbackUrl
sed -i '/const sessionId = getSessionId()/a\    \/\/ workaround for https:\/\/github.com\/vercel\/next.js\/issues\/91819\n    clearSessionId()' "$AUTH_STORE_FILE"

echo "Patch applied successfully"
