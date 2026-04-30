#!/usr/bin/env bash
set -euo pipefail

cd /workspace/angular

# Idempotency guard
if grep -qF "Agent Skills are designed to be used with agentic coding tools like [Gemini CLI]" "skills/dev-skills/README.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/dev-skills/README.md b/skills/dev-skills/README.md
@@ -7,6 +7,16 @@ The Angular skills are designed to help coding agents create applications aligne
 - **`angular-developer`**: Generates Angular code and provides architectural guidance. Useful for creating components, services, or obtaining best practices on reactivity (signals, linkedSignal, resource), forms, dependency injection, routing, SSR, accessibility (ARIA), animations, styling, testing, or CLI tooling.
 - **`angular-new-app`**: Creates a new Angular app using the Angular CLI. Provides important guidelines for effectively setting up and structuring a modern Angular application.
 
+## Using Agent Skills
+
+Agent Skills are designed to be used with agentic coding tools like [Gemini CLI](https://geminicli.com/docs/cli/skills/), [Antigravity](https://antigravity.google/docs/skills) and more. Activating a skill loads the specific instructions and resources needed for that task.
+
+To use these skills in your own environment you may follow the instructions for your specific tool or use a community tool like [skills.sh](https://skills.sh/).
+
+```bash
+npx skills add https://github.com/angular/skills
+```
+
 ## Contributions
 
 We welcome contributions to the Angular agent skills. If you would like to contribute to the skills, please make the updates directly in `angular/angular` repository, and to that repository will be output here as a part of our infrastructure setup.
PATCH

echo "Gold patch applied."
