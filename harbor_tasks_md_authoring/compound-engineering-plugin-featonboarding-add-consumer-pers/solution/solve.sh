#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "Before a contributor can reason about architecture, they need to understand what" "plugins/compound-engineering/skills/onboarding/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/onboarding/SKILL.md b/plugins/compound-engineering/skills/onboarding/SKILL.md
@@ -15,7 +15,7 @@ This skill always regenerates the document from scratch. It does not read or dif
 
 1. **Write for humans first** -- Clear prose that a new developer can read and understand. Agent utility is a side effect of good human writing, not a separate goal.
 2. **Show, don't just tell** -- Use ASCII diagrams for architecture and flow, markdown tables for structured information, and backtick formatting for all file paths, commands, and code references.
-3. **Five sections, each earning its place** -- Every section answers a question a new contributor will ask in their first hour. No speculative sections.
+3. **Six sections, each earning its place** -- Every section answers a question a new contributor will ask in their first hour. No speculative sections.
 4. **State what you can observe, not what you must infer** -- Do not fabricate design rationale or assess fragility. If the code doesn't reveal why a decision was made, don't guess.
 5. **Never include secrets** -- The onboarding document is committed to the repository. Never include API keys, tokens, passwords, connection strings with credentials, or any other secret values. Reference environment variable *names* (`STRIPE_SECRET_KEY`), never their *values*. If a `.env` file contains actual secrets, extract only the variable names.
 6. **Link, don't duplicate** -- When existing documentation covers a topic well, link to it inline rather than re-explaining.
@@ -65,7 +65,7 @@ Do not read files speculatively. Every file read should be justified by the inve
 
 ### Phase 3: Write ONBOARDING.md
 
-Synthesize the inventory data and key file contents into a document with exactly five sections. Write the file to the repo root.
+Synthesize the inventory data and key file contents into a document with exactly six sections. Write the file to the repo root.
 
 **Title**: Use `# {Project Name} Onboarding Guide` as the document heading. Derive the project name from the inventory. Do not use the filename as a heading.
 
@@ -115,39 +115,95 @@ If the project's purpose cannot be clearly determined from the code, state that
 
 Keep to 1-3 paragraphs.
 
-#### Section 2: How Is It Organized?
+#### Section 2: How It's Used
+
+Answer: What does it look like to be on the consuming side of this project?
+
+Before a contributor can reason about architecture, they need to understand what the project *does* from the outside. This section bridges "what is this" (Section 1) and "how is it built" (Section 3). The audience for this section -- like the rest of the document -- is a new developer on the team. The goal is to show them what the product looks like from the consumer's perspective so the architecture and code flows in later sections make intuitive sense.
+
+Title this section in the output based on who consumes the project:
+
+- **End-user product** (web app, mobile app, consumer tool) -- Title: **"User Experience"**. Describe what the user sees and the primary workflows (e.g., "sign up, create a project, invite collaborators, see real-time updates"). Draw from routes, entry points, and README.
+- **Developer tool** (SDK, library, dev CLI, framework) -- Title: **"Developer Experience"**. Describe how a developer consumes the tool: installation, a minimal usage example showing the primary API surface, and the 2-3 most common commands or patterns. This is distinct from Section 6 (Developer Guide), which covers contributing to *this codebase* -- this section covers *using* what the codebase produces.
+- **Both** (platform with a consumer-facing product AND a developer API/SDK) -- Title: **"User and Developer Experience"**. Cover both perspectives, starting with the end-user experience and then the developer-facing surface.
+
+Keep to 1-3 paragraphs or a short flow per audience. If comprehensive user or developer docs exist, link to them and summarize the key workflows in a sentence each. Do not duplicate existing documentation.
+
+Skip this section only for codebases with no consuming audience (pure infrastructure, internal deployment tooling with no direct interaction).
+
+---
+
+#### Section 3: How Is It Organized?
 
 Answer: What is the architecture, what are the key modules, how do they connect, and what does the system depend on externally?
 
 This section covers both the **internal structure** and the **system boundary** -- what the application talks to outside itself.
 
-**System architecture** -- When a project has multiple major surfaces or deployment targets (e.g., a native app, a web server, and an API), include an ASCII architecture diagram showing how they relate at the system level before diving into directory structure. This helps the reader build a mental model of the system before seeing individual files.
+**System architecture** -- There are two kinds of diagrams that help a new contributor, and the system's complexity determines whether to use one or both:
+
+1. **Architecture diagram** -- Components, how they connect, and what protocols or transports they use. A developer looks at this to understand where code lives and how pieces talk to each other. Label edges with interaction types (HTTP, WebSocket, bridge, queue, etc.). Start with user-facing surfaces at the top, internal plumbing in the middle, and data stores and external services at the bottom.
+
+2. **User interaction flow** -- The logical journey a user takes through the product. Not about infrastructure, but about what happens from the user's perspective -- the sequence of actions and what the system does in response.
+
+**When to use one vs. both:**
+- For straightforward systems (single web app, CLI tool, simple API), the architecture diagram already tells the user's story -- one diagram is enough. The request path through the components *is* the user flow.
+- For multi-surface products (native app + web + API, or systems with multiple distinct user types), include both. The architecture diagram shows the developer how the pieces are wired; the user interaction flow shows the logical product experience across those pieces. These are different lenses on the same system.
+
+Use vertical stacking to keep diagrams under 80 columns.
 
-Use vertical stacking to keep diagrams under 80 columns:
+Architecture diagram example:
 
 ```
-+------------------+
-| Native macOS App |
-| (Swift/WKWebView)|
-+--------+---------+
-         |  bridge
-         v
-+------------------+
-| Editor Engine    |  <-- shared core
-| (Milkdown/Yjs)  |
-+--------+---------+
-         |  Vite build
-         v
-+------------------+    WebSocket    +----------------+
-| Browser Client   |<=============>| Express Server  |
-+------------------+               +--------+--------+
-                                            |
-                                   +--------v--------+
-                                   | SQLite + Yjs    |
-                                   +-----------------+
+       User / Browser
+            |
+            |  HTTP / WebSocket
+            v
++------------------+    bridge    +------------------+
+| Browser Client   |<----------->| Native macOS App |
+| (Vite bundle)    |             | (Swift/WKWebView)|
++--------+---------+             +--------+---------+
+         |                                |
+         |  WebSocket                     |  bridge
+         v                               v
++------------------------------------------+
+|            Express Server                |
+|  routes -> services -> models            |
++--------------------+---------------------+
+                     |
+                     |  SQL / Yjs sync
+                     v
+              +--------------+
+              | SQLite + Yjs |
+              +--------------+
+```
+
+User interaction flow example (same system, different lens):
+
+```
+User opens app
+  |
+  v
+Writes/edits document
+  (Milkdown editor)
+  |
+  v
+Changes sync in real-time
+  (Yjs CRDT)
+  |                \
+  v                 v
+Document persists   Other connected
+  to SQLite         clients see edits
+  |
+  v
+User shares doc
+  -> generates link
+  |
+  v
+Recipient opens
+  in browser client
 ```
 
-Skip this for simple projects (single-purpose libraries, CLI tools) where the directory tree already tells the whole story.
+Skip both for simple projects (single-purpose libraries, CLI tools) where the directory tree already tells the whole story.
 
 **Internal structure** -- Include an ASCII directory tree showing the high-level layout:
 
@@ -194,7 +250,7 @@ Present as a table when there are multiple dependencies:
 
 If no external dependencies are detected, state that: "This project appears self-contained with no external service dependencies."
 
-#### Section 3: Key Concepts and Abstractions
+#### Section 4: Key Concepts and Abstractions
 
 Answer: What vocabulary and patterns does someone need to understand to talk about this codebase?
 
@@ -223,7 +279,7 @@ Present both domain terms and abstractions in a single table:
 
 Aim for 5-15 entries. Include only concepts that would confuse a new reader or that represent non-obvious architectural decisions. Skip universally understood terms.
 
-#### Section 4: Primary Flows
+#### Section 5: Primary Flows
 
 Answer: What happens when the main things this app does actually happen?
 
@@ -256,11 +312,11 @@ At each step, reference the specific file path. Keep file path + annotation unde
 
 Additional flows can use a numbered list instead of a full diagram if the first diagram already establishes the structural pattern.
 
-#### Section 5: Where Do I Start?
+#### Section 6: Developer Guide
 
 Answer: How do I set up the project, run it, and make common changes?
 
-Cover three things:
+Cover these areas:
 
 1. **Setup** -- Prerequisites, install steps, environment config. Draw from README and the inventory's scripts. Format commands in code blocks:
    ```
@@ -322,6 +378,8 @@ Before writing the file, verify:
 - [ ] Existing docs are linked inline only where directly relevant
 - [ ] Writing is direct and concrete -- no filler, no hedge words, no meta-commentary about the document
 - [ ] Tone matches the codebase (casual for scrappy projects, precise for enterprise)
+- [ ] "How It's Used" section present with title adapted to audience (User Experience / Developer Experience / both), skipped only for pure infrastructure with no consuming audience
+- [ ] Architecture diagram has labeled edges (protocols/transports) and includes a user interaction flow diagram when the system has multiple surfaces or user types
 
 Write the file to the repo root as `ONBOARDING.md`.
 
PATCH

echo "Gold patch applied."
