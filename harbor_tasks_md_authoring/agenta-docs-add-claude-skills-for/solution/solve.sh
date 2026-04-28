#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agenta

# Idempotency guard
if grep -qF "description: Helps add announcement cards to the sidebar banner system. Use when" ".claude/skills/add-announcement/SKILL.md" && grep -qF "description: Use this skill to create and publish changelog announcements for ne" ".claude/skills/create-changelog-announcement/SKILL.md" && grep -qF "**Provider costs upfront.** You can now see the cost per million tokens directly" ".claude/skills/write-social-announcement/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/add-announcement/SKILL.md b/.claude/skills/add-announcement/SKILL.md
@@ -0,0 +1,227 @@
+---
+name: add-announcement
+description: Helps add announcement cards to the sidebar banner system. Use when adding changelog entries, feature announcements, updates, or promotional banners to the Agenta sidebar. Handles both simple changelog entries and complex custom banners.
+allowed-tools: Read, Edit, Grep, Glob
+user-invocable: true
+---
+
+# Add Announcement Card
+
+This skill helps you add announcement cards to the Agenta sidebar banner system. Announcement cards appear at the bottom of the sidebar and can be dismissed by users.
+
+## System Overview
+
+The sidebar banner system is located at `web/oss/src/components/SidebarBanners/` and uses:
+- **Priority-based queue**: Only one banner shows at a time
+- **Auto-progression**: When dismissed, the next highest priority banner appears
+- **Persistent dismissal**: Uses localStorage to remember dismissed banners
+- **Jotai atoms**: For reactive state management
+
+## Two Types of Announcements
+
+### 1. Simple Changelog Announcements (Most Common)
+
+For standard product updates, features, and changes, simply add to `changelog.json`:
+
+**File**: `web/oss/src/components/SidebarBanners/data/changelog.json`
+
+**Format**:
+```json
+{
+    "id": "changelog-YYYY-MM-DD-feature-name",
+    "title": "Feature Title (Short)",
+    "description": "Brief description of the feature or change.",
+    "link": "https://agenta.ai/docs/changelog/feature-name"
+}
+```
+
+**ID Convention**: `changelog-` + date (YYYY-MM-DD) + feature slug
+- Example: `changelog-2026-01-09-chat-sessions`
+- Must be unique to prevent conflicts
+
+**Title Guidelines**:
+- Keep under 40 characters
+- Clear and actionable
+- Focus on user benefit
+- Examples: "Chat Sessions in Observability", "PDF Support in Playground"
+
+**Description Guidelines**:
+- One sentence, under 100 characters
+- Describe what users can do, not technical details
+- Examples: "Track multi-turn conversations with session grouping and cost analytics."
+
+**Link Convention**:
+- Always points to `https://agenta.ai/docs/changelog/[feature-slug]`
+- You'll need to create the corresponding changelog documentation page
+
+### 2. Custom Banners (Advanced)
+
+For complex banners with custom UI, interactions, or logic (trial warnings, upgrade prompts, etc.), you need to:
+
+1. Add the banner type to `types.ts`
+2. Add priority to `state/atoms.ts`
+3. Create the banner in `activeBannersAtom` (OSS) or `eeBannersAtom` (EE)
+
+**When to use custom banners**:
+- Non-dismissible banners (e.g., trial expiration)
+- Custom interactions (buttons with onClick handlers)
+- Dynamic content (depends on user state)
+- Conditional display (show only under certain conditions)
+
+## Step-by-Step: Adding a Simple Changelog Announcement
+
+### Step 1: Read the current changelog.json
+```bash
+# View current entries to understand the structure
+cat web/oss/src/components/SidebarBanners/data/changelog.json
+```
+
+### Step 2: Add your entry
+Edit `web/oss/src/components/SidebarBanners/data/changelog.json` and add your new entry to the array:
+
+```json
+[
+    {
+        "id": "changelog-2024-12-16-pdf-support",
+        "title": "PDF Support in Playground",
+        "description": "You can now upload and test PDFs directly in the playground.",
+        "link": "https://agenta.ai/docs/changelog/pdf-support-in-playground"
+    },
+    {
+        "id": "changelog-2026-01-09-your-feature",
+        "title": "Your Feature Title",
+        "description": "Brief description of what users can do.",
+        "link": "https://agenta.ai/docs/changelog/your-feature-slug"
+    }
+]
+```
+
+### Step 3: Verify the format
+- Ensure valid JSON (no trailing commas, proper quotes)
+- Check ID uniqueness
+- Verify link URL matches the documentation page you'll create
+
+### Step 4: Test locally
+The banner will automatically appear in the sidebar on the next page load. To see it:
+1. Clear localStorage: `localStorage.removeItem('agenta:dismissed-banners')`
+2. Refresh the page
+3. Banner should appear at bottom of sidebar
+
+## Banner Priority System
+
+Banners are shown in priority order (lower number = shown first):
+
+```
+Priority 0: star-repo (GitHub star prompt for new users)
+Priority 1: changelog (product updates) ← Most changelog entries
+Priority 2: upgrade (upgrade prompts)
+Priority 3: trial (trial/billing warnings)
+```
+
+Changelog entries automatically get priority 1.
+
+## Common Patterns and Examples
+
+### Example 1: Feature Announcement
+```json
+{
+    "id": "changelog-2026-01-15-batch-evaluation",
+    "title": "Batch Evaluation Available",
+    "description": "Evaluate multiple test sets simultaneously with batch processing.",
+    "link": "https://agenta.ai/docs/changelog/batch-evaluation"
+}
+```
+
+### Example 2: Integration Announcement
+```json
+{
+    "id": "changelog-2026-01-20-langchain-support",
+    "title": "LangChain v0.3 Support",
+    "description": "Full support for LangChain v0.3 with auto-instrumentation.",
+    "link": "https://agenta.ai/docs/changelog/langchain-v03"
+}
+```
+
+### Example 3: Improvement Announcement
+```json
+{
+    "id": "changelog-2026-01-25-faster-traces",
+    "title": "10x Faster Trace Loading",
+    "description": "Observability page now loads traces up to 10x faster.",
+    "link": "https://agenta.ai/docs/changelog/faster-trace-loading"
+}
+```
+
+## Related Files
+
+### Core System Files
+- `web/oss/src/components/SidebarBanners/index.tsx` - Main container
+- `web/oss/src/components/SidebarBanners/SidebarBanner.tsx` - Display component
+- `web/oss/src/components/SidebarBanners/types.ts` - Type definitions
+- `web/oss/src/components/SidebarBanners/state/atoms.ts` - State management
+- `web/oss/src/components/SidebarBanners/data/changelog.json` - Changelog data
+
+### Integration Point
+- `web/oss/src/components/Sidebar/Sidebar.tsx` - Where banners are rendered
+
+### EE Override (Enterprise Edition)
+- `web/ee/src/components/SidebarBanners/index.tsx` - EE wrapper
+- `web/ee/src/components/SidebarBanners/state/atoms.ts` - EE banners (trial, upgrade)
+
+## Best Practices
+
+1. **Timing**: Add announcements when features are fully deployed and documented
+2. **User-focused**: Write from user perspective ("You can now..."), not technical perspective
+3. **Brevity**: Keep title and description short - users skim banners
+4. **Links**: Always link to comprehensive documentation, not just a blog post
+5. **Testing**: Clear localStorage and verify the banner displays correctly
+6. **Uniqueness**: Use date-based IDs to prevent conflicts with past/future announcements
+
+## Troubleshooting
+
+**Banner not appearing?**
+- Check JSON syntax (use a JSON validator)
+- Clear localStorage: `localStorage.removeItem('agenta:dismissed-banners')`
+- Verify you're looking at the correct environment (OSS vs EE)
+- Check browser console for errors
+
+**Banner appearing multiple times?**
+- Ensure ID is unique (not already in the dismissed list)
+- Check for duplicate entries in changelog.json
+
+**Banner styling looks wrong?**
+- The SidebarBanner component handles all styling automatically
+- Don't add custom HTML/styling in description - it's rendered as plain text
+
+## Next Steps After Adding Announcement
+
+After adding the announcement to `changelog.json`, you should:
+
+1. **Create changelog documentation page** at `docs/docs/changelog/[feature-slug].mdx`
+2. **Add screenshots or demo video** to the documentation
+3. **Link to related feature documentation** from the changelog page
+4. **Test the banner** in both OSS and EE environments
+5. **Commit changes** with a descriptive commit message
+
+## Example Workflow
+
+```bash
+# 1. Edit changelog.json
+code web/oss/src/components/SidebarBanners/data/changelog.json
+
+# 2. Create documentation page
+code docs/docs/changelog/your-feature.mdx
+
+# 3. Test locally (if running dev server)
+# Clear localStorage in browser console:
+# localStorage.removeItem('agenta:dismissed-banners')
+
+# 4. Commit
+git add web/oss/src/components/SidebarBanners/data/changelog.json
+git add docs/docs/changelog/your-feature.mdx
+git commit -m "docs: add changelog announcement for [feature name]"
+```
+
+---
+
+**Note**: This skill focuses on simple changelog announcements. For custom banners with complex logic, consult the SidebarBanners README or ask for guidance on creating custom banner components.
diff --git a/.claude/skills/create-changelog-announcement/SKILL.md b/.claude/skills/create-changelog-announcement/SKILL.md
@@ -0,0 +1,484 @@
+---
+name: create-changelog-announcement
+description: Use this skill to create and publish changelog announcements for new features, improvements, or bug fixes. This skill handles the complete workflow - creating detailed changelog documentation pages, adding sidebar announcement cards, and ensuring everything follows project standards. Use when the user mentions adding changelog entries, documenting new features, creating release notes, or announcing product updates.
+model: sonnet
+user-invocable: true
+---
+
+# Create Changelog Announcement
+
+This skill guides you through creating complete changelog announcements that include:
+1. Detailed changelog documentation page in `/docs/blog/entries/`
+2. Summary entry in `/docs/blog/main.mdx`
+3. Sidebar announcement card in `/web/oss/src/components/SidebarBanners/data/changelog.json`
+4. Roadmap update in `/docs/src/data/roadmap.ts`
+5. GitHub discussion closure (if applicable)
+6. Social media announcements (LinkedIn, Twitter, Slack)
+
+## Your Core Responsibilities
+
+### 1. **Complete Changelog Creation Workflow**
+
+For every changelog announcement, you create THREE coordinated entries:
+
+**A. Detailed Entry** (`docs/blog/entries/[feature-slug].mdx`):
+- Comprehensive explanation of the feature or change
+- Code examples, screenshots, or embedded videos
+- Links to related documentation
+- User-focused benefits and use cases
+
+**B. Summary Entry** (`docs/blog/main.mdx`):
+- Concise 1-2 paragraph summary
+- Version number and date
+- Link to detailed entry
+- Embedded media if significant feature
+
+**C. Sidebar Announcement** (`web/oss/src/components/SidebarBanners/data/changelog.json`):
+- One-sentence description
+- Link to detailed documentation
+- Unique ID with date
+
+### 2. **Information Gathering**
+
+**Before creating any entry, collect:**
+- Feature name and description
+- Version number (if unclear, ask: "Which version is this changelog entry for?")
+- Release date (default to today if not specified)
+- Whether user has screenshots/videos (ask if mentioned but not provided)
+- Links to related documentation
+
+**Never proceed without** a clear version identifier and feature description.
+
+### 3. **Writing Style Guidelines**
+
+Apply these writing guidelines rigorously:
+
+- **Clarity above all else**: Use 11th grade English for non-technical terms
+- **Active voice**: "You can now track conversations" not "Conversations can now be tracked"
+- **Short sentences**: Default to punchy sentences; use longer ones only for flow
+- **Complete sentences**: Avoid fragments unless brevity clearly improves readability
+- **No em dashes (—)**: Use periods, parentheses (), or semicolons ; instead
+- **Minimal formatting**: Use bold and bullets sparingly—only when they aid scanning
+- **User-focused**: Write "You can now..." not "We've added..."
+- **Benefits over features**: Explain what users can do, not what you built
+
+**Examples:**
+
+❌ **Bad**: "We've implemented a new session tracking system that enables users to group related traces—making it easier to analyze conversations."
+
+✅ **Good**: "You can now group related traces into sessions. This helps you analyze complete conversations and track metrics across multiple turns."
+
+### 4. **ID and Naming Conventions**
+
+**Changelog Entry File Naming**:
+- Use kebab-case with descriptive names
+- Examples: `chat-sessions-observability.mdx`, `pdf-support-in-playground.mdx`
+- Keep under 60 characters
+
+**Sidebar Announcement IDs**:
+- Format: `changelog-YYYY-MM-DD-feature-slug`
+- Example: `changelog-2026-01-09-chat-sessions`
+- Must be unique to prevent conflicts
+
+**Version Format**:
+- Use semantic versioning: `v0.73.0`
+- Include in summary entry
+
+### 5. **Media Handling**
+
+**When user mentions videos or screenshots:**
+
+**For YouTube videos** (in detailed entry):
+```mdx
+<div style={{display: 'flex', justifyContent: 'center', marginTop: "20px", marginBottom: "20px", flexDirection: 'column', alignItems: 'center'}}>
+  <iframe
+    width="100%"
+    height="500"
+    src="https://www.youtube.com/embed/VIDEO_ID"
+    title="Feature Demo"
+    frameBorder="0"
+    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
+    allowFullScreen
+  ></iframe>
+</div>
+```
+
+**For images** (in detailed entry):
+```mdx
+<Image
+  img={require('/static/images/changelog/feature-name.png')}
+  alt="Feature description"
+  style={{display: 'block', margin: '20px auto', textAlign: 'center'}}
+/>
+```
+
+**Ask for specifics if unclear:**
+- "Do you have the YouTube URL for the demo video?"
+- "How many screenshots should I add placeholders for?"
+- "Where should I place the images in the narrative?"
+
+### 6. **Feature Documentation Integration**
+
+**Always search for related documentation:**
+1. Check if a dedicated feature page exists in `/docs/docs/`
+2. If found, link to it in both the summary and detailed entries
+3. If not found, note this and ask: "Should we create documentation for this feature?"
+
+**Documentation links format:**
+- Use relative paths: `/observability/trace-with-python-sdk/track-chat-sessions`
+- Not absolute URLs unless external
+
+### 7. **Quality Assurance Checklist**
+
+Before finalizing, verify:
+- [ ] Version number present and correct
+- [ ] All three entries created (detailed, summary, sidebar)
+- [ ] Summary links to detailed entry correctly
+- [ ] Active voice used where possible
+- [ ] No em dashes present
+- [ ] Feature documentation linked if applicable
+- [ ] Media placeholders added if mentioned
+- [ ] Writing style guidelines followed
+- [ ] IDs and file names follow conventions
+- [ ] All required frontmatter included
+
+### 8. **File Locations Reference**
+
+**Detailed changelog entries:**
+- Path: `/docs/blog/entries/[feature-slug].mdx`
+- Example: `/docs/blog/entries/chat-sessions-observability.mdx`
+
+**Summary changelog:**
+- Path: `/docs/blog/main.mdx`
+- Add new entry at the TOP of the file (after imports, before other entries)
+
+**Sidebar announcements:**
+- Path: `/web/oss/src/components/SidebarBanners/data/changelog.json`
+- JSON array, add new entry at the TOP
+
+## Step-by-Step Workflow
+
+### Step 1: Gather Information
+Ask the user for any missing information:
+```
+- What version is this for?
+- Do you have a demo video or screenshots?
+- What's the primary benefit users will get from this?
+- Are there existing docs for this feature I should link to?
+```
+
+### Step 2: Search for Related Documentation
+```bash
+# Search for related docs
+grep -r "session" docs/docs/observability --include="*.mdx" --include="*.md"
+```
+
+### Step 3: Create Detailed Entry
+Create `/docs/blog/entries/[feature-slug].mdx`:
+
+**IMPORTANT: Use correct frontmatter format (no authors field):**
+
+```mdx
+---
+title: "Feature Name"
+slug: feature-name-slug
+date: YYYY-MM-DD
+tags: [vX.Y.Z]
+description: "One-sentence description of the feature."
+---
+
+# Feature Name
+
+## Overview
+
+[2-3 paragraphs explaining what this feature is and why it matters]
+
+## Key Capabilities
+
+- **Capability 1**: Description
+- **Capability 2**: Description
+- **Capability 3**: Description
+
+## How It Works
+
+[Step-by-step explanation or code examples]
+
+```python
+# Code example if applicable
+import agenta as ag
+ag.tracing.store_session(session_id="conversation_123")
+```
+
+## Use Cases
+
+[Real-world scenarios where this feature helps]
+
+## Getting Started
+
+[Links to documentation, tutorials, or guides]
+
+- [Feature Documentation](/docs/path/to/feature)
+- [Tutorial](/tutorials/path/to/tutorial)
+
+## What's Next
+
+[Optional: What's coming next or related features]
+```
+
+### Step 4: Add Summary to main.mdx
+Add to `/docs/blog/main.mdx` at the TOP (after imports):
+
+```mdx
+### [Feature Name](/changelog/feature-slug)
+
+_DD Month YYYY_
+
+**vX.Y.Z**
+
+[1-2 paragraph summary explaining what the feature does and why users should care. Focus on benefits and capabilities.]
+
+[Optional: Add embedded video or image if this is a major feature]
+
+---
+```
+
+### Step 5: Add Sidebar Announcement
+Add to `/web/oss/src/components/SidebarBanners/data/changelog.json`:
+
+```json
+[
+    {
+        "id": "changelog-2026-01-09-feature-name",
+        "title": "Feature Name (Keep Under 40 Chars)",
+        "description": "One-sentence benefit users get from this feature.",
+        "link": "https://agenta.ai/docs/changelog/feature-slug"
+    },
+    // ... existing entries
+]
+```
+
+### Step 6: Update Roadmap
+Update `/docs/src/data/roadmap.ts`:
+
+**If feature was in roadmap:**
+1. Find the feature in `inProgressFeatures` array
+2. Move it to `shippedFeatures` array at the top
+3. Convert from `PlannedFeature` format to `ShippedFeature` format:
+   - Remove `githubUrl` field
+   - Add `changelogPath` field pointing to your detailed entry
+   - Add `shippedAt` field with ISO date (YYYY-MM-DD)
+
+**Example:**
+```typescript
+// Move from inProgressFeatures to top of shippedFeatures:
+{
+  id: "chat-session-view",
+  title: "Chat Sessions in Observability",
+  description: "Track multi-turn conversations with session grouping...",
+  changelogPath: "/docs/changelog/chat-sessions-observability",
+  shippedAt: "2026-01-09",
+  labels: [{name: "Observability", color: "DE74FF"}],
+}
+```
+
+### Step 7: Check GitHub Discussion
+If the roadmap item had a `githubUrl` pointing to a GitHub discussion:
+
+1. Note the discussion URL from the roadmap entry
+2. Check if the discussion should be closed (ask user if unsure)
+3. If using `gh` CLI: `gh issue close <number> --repo Agenta-AI/agenta --comment "Shipped in v0.73.0"`
+4. If CLI not available, note the discussion URL for manual closure
+
+### Step 8: Create Social Media Announcements
+
+**Follow the guidelines in:** `.claude/skills/write-social-announcement/SKILL.md`
+
+That skill contains comprehensive guidelines for writing authentic announcements that avoid common AI writing patterns. Key points:
+
+- Vary your openings (don't always start with "We just shipped")
+- Avoid AI vocabulary: "crucial", "pivotal", "showcases", "underscores", "landscape", "tapestry"
+- No superficial "-ing" analyses at end of sentences
+- No rhetorical questions ("Working with large test sets?")
+- No cliché closings ("Small changes, but they add up")
+- Be specific and direct
+
+Create `SOCIAL_ANNOUNCEMENTS.md` with sections for LinkedIn, Twitter, and Slack
+
+### Step 9: Build and Verify
+
+**CRITICAL: Always run the build to verify no errors before finishing.**
+
+1. **Run the documentation build:**
+```bash
+cd docs && npm run build
+```
+
+2. **If build fails, fix errors immediately:**
+   - **Common error: Missing authors field** - Remove `authors: [agenta]` from frontmatter
+   - **Correct frontmatter format** (example from existing entries):
+     ```yaml
+     ---
+     title: "Feature Name"
+     slug: feature-name-slug
+     date: YYYY-MM-DD
+     tags: [vX.Y.Z]
+     description: "Brief description"
+     ---
+     ```
+   - **Invalid MDX syntax** - Check for unclosed tags, incorrect JSX
+   - **Broken links** - Verify all relative paths exist
+
+3. **Verify checklist:**
+- [ ] Build completed successfully (`npm run build` in docs/)
+- [ ] Read all files to ensure consistency
+- [ ] Check that links work (relative paths correct)
+- [ ] Verify JSON syntax in sidebar announcement
+- [ ] Ensure version numbers match across files
+- [ ] Confirm writing style follows guidelines
+- [ ] Roadmap updated correctly
+- [ ] Social announcements created
+
+## Common Patterns and Examples
+
+### Example 1: New Feature Announcement (Chat Sessions)
+
+**Detailed Entry** (`docs/blog/entries/chat-sessions-observability.mdx`):
+```mdx
+---
+title: "Chat Sessions in Observability"
+description: "Track and analyze multi-turn conversations with session grouping, cost analytics, and conversation flow visualization."
+authors: [agenta]
+tags: [observability, sessions, tracing]
+hide_table_of_contents: false
+---
+
+# Chat Sessions in Observability
+
+## Overview
+
+Chat sessions bring conversation-level observability to Agenta. You can now group related traces from multi-turn conversations together, making it easy to analyze complete user interactions rather than individual requests.
+
+This feature is essential for debugging chatbots, AI assistants, and any application with multi-turn conversations. You get visibility into the entire conversation flow, including costs, latency, and intermediate steps.
+
+## Key Capabilities
+
+- **Automatic Grouping**: All traces with the same `ag.session.id` attribute are automatically grouped together
+- **Session Analytics**: Track total cost, latency, and token usage per conversation
+- **Session Browser**: Dedicated UI showing all sessions with first input, last output, and key metrics
+- **Session Drawer**: Detailed view of all traces within a session with parent-child relationships
+- **Real-time Monitoring**: Auto-refresh mode for monitoring active conversations
+
+## How It Works
+
+Add a session ID to your traces using either the Python SDK or OpenTelemetry:
+
+**Python SDK:**
+```python
+import agenta as ag
+
+ag.tracing.store_session(session_id="conversation_123")
+```
+
+**OpenTelemetry:**
+```javascript
+span.setAttribute('ag.session.id', 'conversation_123')
+```
+
+The UI automatically detects session IDs and groups traces together. You can use any format for session IDs: UUIDs, composite IDs (`user_123_session_456`), or custom formats.
+
+## Use Cases
+
+- **Debug Chatbots**: See the complete conversation flow when users report issues
+- **Monitor Multi-turn Agents**: Track how your agent handles follow-up questions and context
+- **Analyze Conversation Costs**: Understand which conversations are expensive and why
+- **Optimize Performance**: Identify latency issues across entire conversations, not just single requests
+
+## Getting Started
+
+Learn more in our documentation:
+
+- [Track Chat Sessions (Python SDK)](/observability/trace-with-python-sdk/track-chat-sessions)
+- [Session Tracking (OpenTelemetry)](/observability/trace-with-opentelemetry/session-tracking)
+- [Observability Overview](/observability/overview)
+
+## What's Next
+
+We're continuing to enhance session tracking with upcoming features like session-level annotations, session comparisons, and automated session analysis.
+```
+
+**Summary Entry** (add to `docs/blog/main.mdx`):
+```mdx
+### [Chat Sessions in Observability](/changelog/chat-sessions-observability)
+
+_9 January 2026_
+
+**v0.73.0**
+
+You can now track multi-turn conversations with chat sessions. All traces with the same session ID are automatically grouped together, letting you analyze complete conversations instead of individual requests.
+
+The new session browser shows key metrics like total cost, latency, and token usage per conversation. Open any session to see all traces with their parent-child relationships. This makes debugging chatbots and AI assistants much easier. Add session tracking with one line of code using either our Python SDK or OpenTelemetry.
+
+---
+```
+
+**Sidebar Announcement**:
+```json
+{
+    "id": "changelog-2026-01-09-chat-sessions",
+    "title": "Chat Sessions in Observability",
+    "description": "Track multi-turn conversations with session grouping and cost analytics.",
+    "link": "https://agenta.ai/docs/changelog/chat-sessions-observability"
+}
+```
+
+### Example 2: Integration Announcement
+
+**For integrations, focus on:**
+- What you can now integrate with
+- How easy it is to set up (mention "one line of code" if true)
+- Key benefits specific to that integration
+- Link to integration docs
+
+### Example 3: Improvement Announcement
+
+**For improvements, emphasize:**
+- Quantifiable improvements (e.g., "10x faster", "50% reduction")
+- Before/after comparison if dramatic
+- How this helps users (time saved, better experience)
+
+## Decision-Making Framework
+
+**When Information is Missing:**
+- Version number unclear → Ask immediately before proceeding
+- Feature scope ambiguous → Request clarification and examples
+- Media availability uncertain → Confirm with user before adding placeholders
+- Categorization unclear → Ask whether it's a new feature, improvement, or bug fix
+
+**When Editing Existing Entries:**
+- Always preserve factual accuracy and original intent
+- Improve clarity and style without changing meaning
+- Flag technical inaccuracies to the user rather than guessing
+
+## Output Format
+
+When creating a changelog announcement, provide:
+
+1. **Detailed entry content** for `docs/blog/entries/[slug].mdx`
+2. **Summary entry content** to add to `docs/blog/main.mdx`
+3. **Sidebar announcement JSON** to add to `changelog.json`
+4. **Confirmation** that you checked for related documentation
+5. **Any questions** or clarifications needed
+
+**Be proactive** in identifying unclear requirements. Ask specific questions rather than making assumptions. Your goal is to produce changelog entries that are immediately publishable without requiring revision.
+
+## Tips for Success
+
+1. **Read existing entries first**: Before creating new entries, read 2-3 recent entries in `main.mdx` and `entries/` to match the tone and structure
+2. **Be concise**: Users skim changelogs. Front-load the benefit in every sentence.
+3. **Link generously**: Help users find more information easily
+4. **Test your work**: Read the entries out loud to catch awkward phrasing
+5. **Consistency matters**: Ensure terminology matches across all three entries
+
+---
+
+**Remember**: You're creating user-facing documentation that represents a new feature to thousands of developers. Make it clear, compelling, and easy to understand.
diff --git a/.claude/skills/write-social-announcement/SKILL.md b/.claude/skills/write-social-announcement/SKILL.md
@@ -0,0 +1,230 @@
+# Write Social Media Announcements
+
+This skill creates authentic social media announcements for LinkedIn, Twitter/X, and Slack that avoid common AI writing patterns.
+
+## Writing Guidelines
+
+### Core Principles
+
+1. **Write like a human, not a press release**
+2. **Be specific, not generic**
+3. **State facts directly without inflating their importance**
+4. **Vary your openings** - Don't start every post with "We just shipped"
+
+### Words and Phrases to NEVER Use
+
+These words are statistical markers of AI-generated text. Avoid them completely:
+
+**Significance words:**
+- testament, pivotal, crucial, vital, key (as adjective), groundbreaking
+- underscores, highlights, emphasizes, showcases, exemplifies
+- landscape (abstract), tapestry (abstract), realm, beacon
+- indelible mark, focal point, deeply rooted
+
+**Transition/filler words:**
+- Additionally (especially at start of sentence)
+- Furthermore, Moreover
+- In summary, In conclusion, Overall
+- It's important to note/remember/consider
+
+**Puffery words:**
+- vibrant, rich (figurative), profound, renowned
+- cutting-edge, revolutionary, game-changing
+- seamless, robust, comprehensive, holistic
+
+**Action verbs that sound corporate:**
+- delve, garner, foster, cultivate, leverage
+- enhance, optimize, streamline, empower
+- align with, resonate with
+
+**Generic praise phrases:**
+- commitment to excellence/quality/innovation
+- dedication to [abstract noun]
+- passion for [thing]
+
+### Sentence Patterns to AVOID
+
+**1. Superficial "-ing" analyses at end of sentences**
+
+❌ "We added cost tracking, helping teams make better decisions."
+❌ "The new filter reduces noise, enabling faster debugging."
+
+✅ "We added cost tracking. Now you can see exactly what each request costs."
+✅ "The new filter reduces noise. Debugging is faster."
+
+**2. "Not only... but also" and negative parallelisms**
+
+❌ "It's not just about speed, it's about reliability."
+❌ "Not only does it track costs, but it also shows token usage."
+
+✅ "It's fast and reliable."
+✅ "It tracks costs and shows token usage."
+
+**3. Rule of three (adjective, adjective, adjective)**
+
+❌ "A fast, reliable, and scalable solution."
+❌ "Clean, modern, and intuitive interface."
+
+✅ "It's fast." (just say the most important thing)
+
+**4. Rhetorical questions followed by answers**
+
+❌ "Working with large test sets? Collapse them."
+❌ "Tired of switching tabs? Now you don't have to."
+
+✅ "You can collapse large test sets."
+✅ "Costs show in the dropdown. No tab switching."
+
+**5. "Small changes, but they add up" type closings**
+
+❌ "Small changes, but they add up when you're testing prompts all day."
+❌ "Little things that make a big difference."
+
+✅ (Just end. Don't summarize or reflect on the importance.)
+
+**6. Overuse of em dashes for dramatic effect**
+
+❌ "Provider costs — right in the dropdown — so you don't have to switch tabs."
+
+✅ "Provider costs show in the dropdown."
+
+### What TO Do
+
+**Be direct:**
+- "You can now see costs in the dropdown."
+- "Evaluations run from the Playground."
+- "Test cases collapse."
+
+**Be specific:**
+- "Cost per million tokens shows next to each model."
+- Not: "Cost information is now more accessible."
+
+**Use simple verbs:**
+- "is" instead of "serves as"
+- "has" instead of "boasts" or "features"
+- "shows" instead of "showcases"
+
+**Vary sentence length:**
+- Mix short punchy sentences with longer ones
+- Don't make every sentence the same structure
+
+**End without summarizing:**
+- Don't wrap up with "these improvements help teams..."
+- Just stop after the last fact
+
+### Platform-Specific Guidelines
+
+#### LinkedIn
+
+**Format:**
+- 3-4 short paragraphs max
+- One code snippet if relevant (optional)
+- Link at the end
+- No hashtags (LinkedIn algorithm doesn't favor them anymore)
+
+**Tone:**
+- Conversational but professional
+- First person ("We shipped" or "I added")
+- Explain what changed and why it matters
+
+**Opening variations (rotate these, don't always use the same one):**
+- "[Feature] is live in [Product]."
+- "Three updates to [Product] this week:"
+- "New in [Product]: [feature]."
+- "[Problem statement]. Fixed that."
+- Start with the most interesting detail
+
+#### Twitter/X
+
+**Format:**
+- Two tweets max: announcement + link
+- First tweet: what shipped + key benefit (under 280 chars)
+- Second tweet: "Check it out:" + link
+
+**Tone:**
+- Casual, direct
+- No thread unless it's a major release
+
+#### Slack
+
+**Community (#announcements):**
+- Short, user-focused
+- One code snippet if it helps
+- Bullet points OK here
+- Link to changelog
+
+**Internal (#product-updates):**
+- Bullet points with metrics
+- Note any manual TODOs
+- Link to changelog
+
+### Examples
+
+**LinkedIn - Good:**
+```
+Three Playground updates shipped today.
+
+Model costs show in the dropdown now. You see the price per million tokens right when selecting a model.
+
+You can run evaluations without leaving the Playground. Hit evaluate, pick your test set, and it runs with your current config.
+
+Test cases collapse. Useful when you have 50 of them and need to find a specific one.
+
+https://agenta.ai/docs/changelog/playground-ux-improvements
+```
+
+**LinkedIn - Bad (AI patterns):**
+```
+We just shipped three quality-of-life improvements to the Agenta Playground.
+
+**Provider costs upfront.** You can now see the cost per million tokens directly in the model selection dropdown — helping you make informed decisions about which model to use.
+
+**Evaluations from the Playground.** Start an evaluation run without leaving the Playground, keeping you in flow when iterating on prompts.
+
+**Collapsible test cases.** Working with large test sets? Collapse completed test cases to focus on what matters.
+
+Small changes, but they add up when you're testing prompts all day.
+```
+
+Problems with the bad version:
+- "quality-of-life improvements" - generic puffery
+- "helping you make informed decisions" - superficial -ing analysis
+- "keeping you in flow" - superficial -ing analysis
+- "Working with large test sets?" - rhetorical question
+- "focus on what matters" - cliché
+- "Small changes, but they add up" - AI closing pattern
+- Overuse of em dashes
+- Bold headers with periods (feels like a list, not prose)
+
+**Twitter - Good:**
+```
+Tweet 1:
+Three Playground updates in Agenta:
+- Model costs visible in dropdown
+- Run evaluations without leaving Playground
+- Collapsible test cases
+
+Tweet 2:
+Changelog: [link]
+```
+
+**Twitter - Bad:**
+```
+We just shipped three quality-of-life improvements! 🚀
+
+The Playground now shows provider costs, lets you run evaluations directly, and supports collapsible test cases.
+
+Small UX wins that add up. Check it out 👇
+```
+
+Problems: emoji, "quality-of-life improvements", "Small UX wins that add up"
+
+### Self-Check Before Posting
+
+Ask yourself:
+1. Would a tired engineer actually write this at 11pm?
+2. Does every sentence add new information?
+3. Did I use any words from the "never use" list?
+4. Did I end with a summary or reflection? (Remove it)
+5. Are there rhetorical questions? (Rewrite as statements)
+6. Count the em dashes. More than one? Rewrite.
PATCH

echo "Gold patch applied."
