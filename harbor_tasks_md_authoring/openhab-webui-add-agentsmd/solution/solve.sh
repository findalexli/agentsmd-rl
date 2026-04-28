#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openhab-webui

# Idempotency guard
if grep -qF "This repository contains the web user interfaces for the openHAB smart-home proj" "AGENTS.md" && grep -qF "- Write unit tests for utilities, and composables where appropriate. Focus on te" "bundles/org.openhab.ui/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,117 @@
+# AGENTS.md - openHAB Web UIs Development Guide
+
+## Overview
+
+This repository contains the web user interfaces for the openHAB smart-home project, featuring approximately 5 different extensions located in the `bundles` folder.
+
+**Key Resources:**
+- Developer documentation: https://www.openhab.org/docs/developer/
+- Core concepts: https://www.openhab.org/docs/concepts/
+- Core repository: https://github.com/openhab/openhab-core
+
+## Project Structure
+
+```text
+repo root folder
+├── bundles/
+│   ├── org.openhab.ui                  # Main UI (main user interface for openHAB)
+│   ├── org.openhab.ui.basicui          # Basic UI (sitemaps)
+│   ├── org.openhab.ui.basicui          # CometVisu Backend for openHAB (https://www.cometvisu.org/)
+│   ├── org.openhab.ui.habot            # HABot UI (chatbot)
+│   ├── org.openhab.ui.habpanel         # HABPanel UI (fixed-layout dashboard)
+│   └── org.openhab.ui.iconset.classic  # Classic Icon Set
+├── CODEOWNERS                          # Maintainer assignments
+└── ...
+```
+
+**Important:** This repository depends on the openhab-core repository, which defines the base system and APIs.
+
+## Development Standards
+
+### Java Version
+- **Target:** Java 21
+- Use modern language features, but stay within Java 21 bounds
+- Avoid preview features or experimental APIs
+
+### Code Style & Documentation
+
+#### Comments and Documentation
+- Add meaningful code comments where helpful
+- Avoid obvious comments (e.g., `// constructor`)
+- Use Javadoc for API/class/method documentation
+- Follow guidelines at: https://www.openhab.org/docs/developer/guidelines.html
+- Follow checklist at: https://github.com/openhab/openhab-addons/wiki/Review-Checklist
+
+#### Import Organization
+- Sort imports alphabetically
+- Group imports logically (standard library, third-party, openHAB)
+
+#### Formatting
+- Use `mvn spotless:apply` to fix formatting issues
+- POM sections should be sorted
+
+## File-Specific Guidelines
+
+### pom.xml Files
+When upgrading Maven dependencies:
+
+1. **Check version consistency across:**
+    - `features.xml` files for hardcoded version numbers
+    - `*.bndrun` files for hardcoded version numbers
+
+2. **After updates:**
+    - Run `mvn spotless:apply` to fix formatting
+    - Consider running full Maven build with `-DwithResolver` option
+
+### OH-INF/i18n/*_xx.properties
+- I18N properties files for specific languages, e.g. foobar_de.properties, should be omitted.
+- Reference documentation: https://www.openhab.org/docs/developer/utils/i18n.html#managing-translations
+
+### AGENTS.md
+There might be AGENTS.md files in subfolders. Consider them when files from that UI are open in the editor:
+- bundles/org.openhab.*/AGENTS.md
+
+### CODEOWNERS File
+- Located at repository root
+- Maps GitHub usernames to UI responsibilities
+- Format: `path/to/UI @github-username`
+
+## Testing
+
+### Build Validation
+```bash
+# Format code
+mvn spotless:apply
+
+# Run tests
+mvn clean install
+
+# Build and run tests for a single specific user interface
+mvn clean install -pl org.openhab.ui.uiname
+```
+
+After building, the directory target inside org.openhab.ui.uiname contains several test reports.
+- target/code_analysis/report.html for results of the static code analysis
+- target/site/jacoco/index.html contains code coverage (only if available for a specific binding)
+
+## Common Pitfalls
+
+1. **Dependency Management:** Always check `features.xml` and `*.bndrun` files when updating dependencies
+2. **Import Order:** Unsorted imports will fail style checks
+3. **Java Version:** Stay within Java 21 - newer features will break CI/CD
+
+## Getting Help
+
+- **Documentation:** https://www.openhab.org/docs/developer/
+- **Community Forum:** https://community.openhab.org/
+- **GitHub Issues:** Use for bug reports and feature requests
+- **Code Reviews:** Required for all contributions
+
+## Quick Reference
+
+| Task                | Command                                       |
+|---------------------|-----------------------------------------------|
+| Format code         | `mvn spotless:apply`                          |
+| Full build          | `mvn clean install`                           |
+| Build with resolver | `mvn clean install -DwithResolver`            |
+| Build a specific UI | `mvn clean install -pl org.openhab.ui[.name]` |
diff --git a/bundles/org.openhab.ui/AGENTS.md b/bundles/org.openhab.ui/AGENTS.md
@@ -0,0 +1,144 @@
+# AGENTS.md - openHAB Main UI (org.openhab.ui)
+
+## Overview
+
+This is the main web interface for openHAB, used both for configuration and as the default user interface for end-users.
+
+## Tech Stack
+
+- **Framework:** Vue 3 (Composition API)
+- **Build Tool:** Vite
+- **UI Components:** Framework7 v7
+- **State Management:** Pinia
+- **Language:** TypeScript
+- **Styling:** Stylus (CSS Preprocessor)
+- **Formatting:** oxfmt (enforcing Prettier style)
+- **Testing:** Vitest (Supports TypeScript)
+- **API Client:** @hey-api/openapi-ts (located in `web/src/api`)
+
+## Project Structure
+
+```text
+bundles/org.openhab.ui/
+├── doc/
+│   └── components/                                 # oh-* component documentation
+│       └── src/                                    # Sources for doc generation (generate.js)
+├── src/                                            # Java source code (OSGi bundle)
+└── web/                                            # Vue.js application root
+    ├── public/                                     # Static assets
+    ├── src/
+    │   ├── api/                                    # API client (hey-api)
+    │   ├── assets/
+    │   │   ├── definitions/
+    │   │   │   ├── blockly/                        # Blockly block definitions
+    │   │   │   └── widgets/                        # Widget definitions describing oh-* components and their configuration parameters
+    │   │   └── i18n/                               # I18n files
+    │   ├── components/                             # Reusable Vue components
+    │   │   └── widgets/                            # Widget components (oh-* components) for end-user facing UI
+    │   │       ├── chart/                          # ECharts-based charting: oh-chart-* components
+    │   │       ├── standard/                       # Cell, list & card widgets based on the core oh-* components
+    │   │       ├── system/                         # Core oh-* components (e.g., oh-slider, oh-stepper, oh-toggle)
+    │   │       └── generic-widget-component.vue    # Dynamic rendering of widgets based on their context
+    │   ├── js/                                     # TypeScript/JavaScript code for global usage
+    │   │   ├── composables/                        # Reusable Vue composables (hooks)
+    │   │   ├── openhab/                            # Utilities for interacting with the server, e.g., SSE & WebSocket API handling
+    │   │   ├── stores/                             # Pinia state management
+    │   │   └── routes.js                           # Framework7 router route definitions
+    │   ├── pages/                                  # Page components (mapped to routes in routes.js)
+    │   ├── types/                                  # Common TypeScript types/interfaces
+    │   │   └── components/
+    │   │       └── widgets/                        # TypeScript types for oh-* component configuration
+    │   ├── App.vue                                 # Root component
+    │   └── main.ts                                 # Entry point
+    ├── package.json
+    └── vite.config.ts
+```
+
+## Development Workflow
+
+All web development happens in the `web/` directory.
+
+### Development Environment & Dependencies
+- A Node version manager is used to ensure consistent Node versions across developers.
+- The project requires the Node version according to the `.nvmrc` file.
+- Use `npm install` to install dependencies after switching to the correct Node version.
+
+### Running the Development Server
+- The development server requires a openHAB instance as a backend. By default, it proxies API requests to `localhost:8080`.
+- The `OH_APIBASE` environment variable can be set to point to a different openHAB instance (e.g., `OH_APIBASE=http://openhab-dev:8080 npm run dev`).
+- Use `npm run dev` to start the development server. It will be available at `http://localhost:8081`.
+
+### Building and Testing
+- Use `npm run build` to create a production build of the web application.
+- Use `npm run test:unit` to run unit tests with Vitest.
+- Write unit tests for utilities, and composables where appropriate. Focus on testing logic and behavior rather than implementation details. Store tests alongside the code they test, using the `.test.ts` suffix (e.g., `useWidget.test.ts` for `useWidget.ts`).
+
+## File-Specific Guidelines
+
+### *.gen.ts Files
+- Auto-generated TypeScript files
+- Do not modify these files directly
+
+### src/assets/i18n/*.json Files
+- I18n translation files for specific languages
+- Use English (`en`) as the base language for translations
+- Do not modify translation files other than for English (`en`)
+
+## Code Style & Documentation
+
+### Comments and Documentation
+- Add meaningful code comments where helpful
+- Avoid obvious comments (e.g., `// variable declaration`)
+- Use JSDoc for API/class/method documentation
+- Generate oh-* component documentation by running `node generate.js` in `doc/components/src` after modifying widget definitions
+
+### Formatting
+- Use `npm run format:check` to check for formatting issues
+- Use `npm run format` to fix formatting issues
+
+### Linting
+- Use `npm run lint` to check for linting issues
+- Use `npm run lint:fix` to automatically fix linting issues where possible
+
+### TypeScript
+- Generate types for oh-* components by running `npm run generate-widget-component-ts` after modifying widget definitions
+- Use `npm run typescript:check` to check for TypeScript errors
+
+### Coding Standards
+1. **API Style:** Use the **Composition API** with `<script setup>` for all new components.
+2. **Language:** Use **TypeScript** for better type safety and IDE support.
+3. **Data Flow:** Strictly follow "Props Down, Events Up". Do not mutate props.
+4. **Reactivity:** Use Vue reactivity primitives; avoid direct DOM manipulation.
+5. **API Requests:** Use the `@hey-api/openapi-ts` fetch client in `web/src/api`.
+6. **Mocking:** Preferably mock API requests (Note: mocking features in hey-api are currently under development).
+7. **Component Ordering:** In `<script setup>`, follow this order and add comments to separate sections (`// --- Section Name ---`):
+    - Constants/Store/Types
+    - Defines (`defineProps`, `defineEmits`, etc.)
+    - Composables
+    - State/Data
+    - Computed
+    - Watchers
+    - Lifecycle hooks
+    - Methods
+
+## Common Pitfalls
+
+- **Composable argument reactivity:** If reactivity needs to be preserved when passing arguments to composables, `Ref`s or `ComputedRef`s must be passed instead of raw values.
+- **Reactivity export reactivity:** Composables must not export raw values. Instead, they should export `Ref`s or `ComputedRef`s to ensure reactivity is preserved for the caller.
+- **CSS leaking:** Wrap styles in `<style>` with a unique class matching the component name to prevent styles from affecting other components.
+
+## Reference Documentation
+
+- [Framework7 Core Documentation](https://v7.framework7.io/docs/)
+- [Framework7 Vue Documentation](https://v7.framework7.io/vue/)
+- [Framework7 Icons Reference](https://framework7.io/icons/)
+- [ECharts Options](https://echarts.apache.org/en/option.html)
+
+## Quick Reference
+
+| Task             | Command                    |
+|------------------|----------------------------|
+| Format code      | `npm run format`           |
+| Lint code        | `npm run lint`             |
+| TypeScript check | `npm run typescript:check` |
+| Production build | `npm run build`            |
PATCH

echo "Gold patch applied."
