#!/usr/bin/env bash
set -euo pipefail

cd /workspace/context7

# Idempotency guard
if grep -qF "Retrieves authoritative, up-to-date technical documentation, API references," "skills/find-docs/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/find-docs/SKILL.md b/skills/find-docs/SKILL.md
@@ -1,6 +1,25 @@
 ---
 name: find-docs
-description: Retrieves and queries up-to-date documentation and code examples from Context7 for any programming library or framework. Use when writing code that depends on external packages, verifying API signatures, looking up usage patterns, generating code with specific libraries, or when training data may be outdated. Covers setup questions, migration guides, and version-specific docs.
+description: >-
+  Retrieves authoritative, up-to-date technical documentation, API references,
+  configuration details, and code examples for any developer technology.
+
+  Use this skill whenever answering technical questions or writing code that
+  interacts with external technologies. This includes libraries, frameworks,
+  programming languages, SDKs, APIs, CLI tools, cloud services, infrastructure
+  tools, and developer platforms.
+
+  Common scenarios:
+  - looking up API endpoints, classes, functions, or method parameters
+  - checking configuration options or CLI commands
+  - answering "how do I" technical questions
+  - generating code that uses a specific library or service
+  - debugging issues related to frameworks, SDKs, or APIs
+  - retrieving setup instructions, examples, or migration guides
+  - verifying version-specific behavior or breaking changes
+
+  Prefer this skill whenever documentation accuracy matters or when model
+  knowledge may be outdated.
 ---
 
 # Documentation Lookup
PATCH

echo "Gold patch applied."
