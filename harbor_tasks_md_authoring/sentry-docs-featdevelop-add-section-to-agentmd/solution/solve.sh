#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sentry-docs

# Idempotency guard
if grep -qF "1. **Use RFC 2119 Keywords**: Use \"MUST\", \"MUST NOT\", \"REQUIRED\", \"SHALL\", \"SHAL" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -50,3 +50,16 @@ Run `yarn test` for vitest. Tests live alongside source files or in `__tests__`
 | `yarn lint:ts` | TypeScript check |
 | `yarn lint:eslint` | ESLint check |
 | `yarn lint:prettier` | Prettier check |
+
+## Developer Documentation (develop-docs/)
+
+When writing requirements in `develop-docs/`:
+
+1. **Use RFC 2119 Keywords**: Use "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" as defined in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt). These keywords **MUST** be written in uppercase and bold, for example: **MUST**, **SHOULD**, **MAY**.
+
+2. **Add RFC 2119 Alert**: When creating a new file with requirements, or adding requirements to an existing file, ensure the file has an Alert at the top (after frontmatter) to clarify RFC 2119 usage. If missing, add:
+   ```mdx
+   <Alert>
+     This document uses key words such as "MUST", "SHOULD", and "MAY" as defined in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt) to indicate requirement levels.
+   </Alert>
+   ```
PATCH

echo "Gold patch applied."
