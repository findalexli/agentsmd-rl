#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-mpm

# Idempotency guard
if grep -qF "5. **Stop when you can teach it.** If you can only say \"I found 3 mentions of X " "src/claude_mpm/skills/bundled/main/cross-source-research/SKILL.md" && grep -qF "Claude Code sessions are ephemeral. Everything discovered, debugged, decided, or" "src/claude_mpm/skills/bundled/main/end-of-session/SKILL.md" && grep -qF "MCP servers run as child processes with access to your shell environment, filesy" "src/claude_mpm/skills/bundled/main/mcp-security-review/SKILL.md" && grep -qF "Gather context and produce a structured agenda with talking points before a meet" "src/claude_mpm/skills/bundled/main/prep-meeting/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/claude_mpm/skills/bundled/main/cross-source-research/SKILL.md b/src/claude_mpm/skills/bundled/main/cross-source-research/SKILL.md
@@ -0,0 +1,102 @@
+---
+name: cross-source-research
+description: Multi-source investigation workflow for researching topics across configured MCP tools (Slack, Confluence, Jira, GitHub, Drive, databases, analytics). Enforces depth over breadth by requiring content to be read, not just referenced.
+version: 1.0.0
+when_to_use: when researching a topic, gathering context across tools, investigating current state of a project or feature, or answering questions that span multiple information sources
+progressive_disclosure:
+  level: 1
+  references: []
+  note: Single-file skill. The workflow itself is the deliverable.
+---
+
+# Cross-Source Research
+
+Structured workflow for investigating topics across multiple MCP-connected sources. The goal is synthesis, not citation. Research is not complete until you can explain the topic conversationally, not just list where you found mentions of it.
+
+## When to Activate
+
+Trigger phrases: "research", "investigate", "what's the current state of", "pull context on", "what do we know about", "gather context on", "find out about".
+
+## Research Depth Standards
+
+These rules apply to every step below. They exist because the default AI research behavior is shallow: find a reference, summarize the title, move on. That is not research.
+
+1. **Read the content, not just the metadata.** Open the page, read the body. Open the file, read the code. Open the thread, read the messages. A Confluence page title tells you nothing about the decision that was made inside it.
+2. **Extract the "why", not just the "what."** If a feature was built, find out why. If a decision was made, find who made it and what they rejected.
+3. **Trace outcomes.** If something was proposed, did it ship? If it shipped, is it still live? If it was deprecated, why? Follow the full lifecycle, not just the announcement.
+4. **Look for contradictions.** Different sources often disagree. A Slack thread might say "we decided X" while a Jira ticket still tracks Y. Flag these.
+5. **Stop when you can teach it.** If you can only say "I found 3 mentions of X in Slack and a Confluence page about it," you are not done. You are done when you can explain what X is, why it exists, what state it's in, and what should happen next.
+
+## Step 1: Define the Question
+
+Before searching anything, clarify:
+- What specifically are we trying to understand?
+- What would a good answer look like? (a timeline? a decision? a metric? a status?)
+- What sources are most likely to have the answer?
+
+Do not skip this step. Unfocused research produces unfocused results.
+
+## Step 2: Check Local Knowledge First
+
+Before hitting external tools, check what's already known:
+- Project knowledge base (CLAUDE.md, docs/, any knowledge/ directories)
+- Recent conversation history (was this discussed earlier in the session?)
+- Task/todo files (is there already an open item tracking this?)
+
+This avoids redundant searches and gives you baseline context to make external searches more targeted.
+
+## Step 3: Search Across Sources
+
+Use the Task tool to dispatch parallel searches where sources are independent. Common source types and what to look for:
+
+| Source Type | What to Search For | MCP Tools |
+|-------------|-------------------|-----------|
+| **Chat/messaging** (Slack, Teams) | Discussions, decisions, announcements, debates | Channel history, thread replies, search |
+| **Documentation** (Confluence, Notion, Wiki) | PRDs, design docs, roadmaps, meeting notes, decision records | Page search, space listing, page content |
+| **Issue tracking** (Jira, Linear, GitHub Issues) | Ticket status, blockers, engineering context, sprint progress | Issue search, issue details, epic contents |
+| **Code** (GitHub, GitLab) | Implementations, PRs, code reviews, architectural decisions in comments | Code search, PR search, file contents |
+| **Drive/docs** (Google Drive, SharePoint) | Decks, meeting transcripts, strategy docs, shared spreadsheets | File search, file content, folder listing |
+| **Analytics** (databases, BI tools) | Quantitative evidence, metrics, usage data | SQL queries, saved reports |
+| **Product analytics** (Pendo, Amplitude, Mixpanel) | Feature adoption, user behavior, survey responses | Usage queries, guide metrics, segments |
+
+Not every source applies to every question. Pick the 2-4 most relevant sources, not all of them.
+
+## Step 4: Read and Extract
+
+For each result found in Step 3:
+
+**Chat threads**: Read the full thread, not just the first message. Decisions often happen 15 messages deep. Note who said what and when.
+
+**Documentation pages**: Read the body content, not just the title and last-modified date. Look for: stated goals, success criteria, status sections, inline comments, unresolved questions.
+
+**Tickets/issues**: Check status, assignee, linked PRs, comments, and blockers. A ticket marked "In Progress" for 3 months is not the same as one created yesterday.
+
+**Code**: Read the actual implementation, not just the PR title. Check test coverage. Read review comments for context on why choices were made.
+
+**Data**: Run queries to validate claims. "We have high adoption" means nothing without a number. "Override rates are high" needs a percentage and a baseline.
+
+## Step 5: Synthesize
+
+Produce a structured summary. This is the deliverable. It should answer the original question from Step 1.
+
+**Required sections:**
+
+- **Key findings**: What do we now know? State facts, not opinions. Include specific numbers, dates, names.
+- **Decisions found**: What was decided, by whom, and when? Link to the source.
+- **Contradictions or gaps**: Where do sources disagree? What's still unknown?
+- **Recommendations**: Based on the findings, what should happen next? Be specific. "Follow up with X about Y" is better than "more research needed."
+
+**Quality check for synthesis:**
+- Does it answer the original question directly?
+- Could someone who wasn't in this session understand the findings?
+- Are claims backed by specific sources (not "according to Slack" but "per [name] in #channel on [date]")?
+- Are recommendations actionable (who, what, by when)?
+
+## Step 6: Persist
+
+Save findings so they're available in future sessions:
+- Update relevant project knowledge files with new findings
+- Add follow-up items to task lists
+- If findings change the project's understanding of something, update CLAUDE.md or project docs
+
+Research that isn't persisted will be re-done. Capture it once, reference it forever.
diff --git a/src/claude_mpm/skills/bundled/main/end-of-session/SKILL.md b/src/claude_mpm/skills/bundled/main/end-of-session/SKILL.md
@@ -0,0 +1,99 @@
+---
+name: end-of-session
+description: Captures session learnings into persistent project memory before closing. Updates task files, project knowledge, and configuration so the next session starts with full context instead of from scratch.
+version: 1.0.0
+when_to_use: when wrapping up a session, when the user says remember everything, save learnings, end of session, wrap up, or commit to memory
+progressive_disclosure:
+  level: 1
+  references: []
+  note: Single-file protocol. Value is in the checklist structure.
+---
+
+# End-of-Session Protocol
+
+Claude Code sessions are ephemeral. Everything discovered, debugged, decided, or learned during a session disappears when the conversation ends, unless it's written to files that persist. This protocol captures session knowledge systematically so the next session starts with full context.
+
+Run at the end of every session, or when the user asks to "remember everything", "save learnings", "commit to memory", or "wrap up".
+
+## Step 1: Identify What Was Learned
+
+Review the conversation and identify anything worth preserving. Categories:
+
+**Work completed**: Tasks finished, PRs opened, tickets updated, messages sent. Mark these done in any task tracker files.
+
+**Technical discoveries**: Code paths traced, API patterns figured out, configuration gotchas hit, root causes identified. These are the things that took 20 minutes to figure out and would take 20 minutes again without documentation.
+
+**Decisions made**: What was chosen, what was rejected, and why. Include who was involved. Decisions without recorded rationale get relitigated.
+
+**New contacts and references**: User IDs, channel IDs, page IDs, email addresses, API endpoints, repo paths. Anything that was looked up and might be needed again.
+
+**Open threads**: Follow-ups needed, questions unanswered, tasks discovered but not started. These become next-session starting points.
+
+## Step 2: Update Task Files
+
+If the project uses a task tracking file (personal-tasks.md, TODO.md, or similar):
+
+- Mark completed items as done with today's date
+- Add new follow-up tasks discovered during the session
+- Move blocked items to a blocked section with the reason
+- Add a session log entry summarizing what happened:
+
+```markdown
+### YYYY-MM-DD (session N)
+- Completed: [what was done]
+- Key finding: [most important discovery]
+- Next: [what should happen next session]
+```
+
+Keep session log entries concise. Bullet points, not paragraphs. The goal is scannable context for future sessions, not a narrative.
+
+## Step 3: Update Project Knowledge Files
+
+For each topic area that came up during the session, update the relevant knowledge file:
+
+- Add new findings under the appropriate section
+- Mark resolved questions as done, add new open questions
+- Update "last updated" dates
+- Add "recent activity" entries with specific dates and outcomes
+
+If a topic was explored significantly but has no knowledge file, create one. Structure it with: overview, current state, open questions, recent activity, next steps.
+
+Common knowledge file types:
+- Initiative/project state files (one per workstream)
+- Architecture or codebase reference docs
+- Integration/API reference docs
+- Meeting notes or decision logs
+
+## Step 4: Update Project Configuration
+
+Only update CLAUDE.md or project configuration files if something **permanent** was established:
+
+- New MCP server added or configured
+- New workflow pattern that should apply to all future sessions
+- New convention or rule discovered
+- New tool or integration set up
+
+Do not update config for one-off findings. Those go in knowledge files (Step 3).
+
+## Step 5: Commit
+
+Stage and commit all changed files with a descriptive message summarizing what was captured:
+
+```
+git add [changed files]
+git commit -m "End-of-session: [1-line summary of key learnings]"
+```
+
+## Quality Checklist
+
+Before finishing, verify:
+
+- [ ] All completed tasks marked done
+- [ ] New follow-up tasks captured (nothing lost from conversation)
+- [ ] Technical discoveries documented (code paths, gotchas, API patterns)
+- [ ] Decisions recorded with rationale
+- [ ] New reference IDs saved (user IDs, page IDs, endpoints)
+- [ ] Knowledge files updated for topics discussed
+- [ ] Config files updated only for permanent changes
+- [ ] Everything committed to git
+- [ ] Summary of what was saved presented to the user
diff --git a/src/claude_mpm/skills/bundled/main/mcp-security-review/SKILL.md b/src/claude_mpm/skills/bundled/main/mcp-security-review/SKILL.md
@@ -0,0 +1,83 @@
+---
+name: mcp-security-review
+description: Security review gate for MCP server installations. Checks provenance, classifies risk, enforces version pinning, and documents credentials exposure before any MCP is added to your environment.
+version: 1.0.0
+when_to_use: when installing, adding, configuring, or updating any MCP server
+progressive_disclosure:
+  level: 1
+  references: []
+  note: Intentionally compact. The protocol is the value, not reference depth.
+---
+
+# MCP Security Review
+
+Gate that runs before any MCP server is installed or updated. MCP servers handle credentials (OAuth tokens, API keys, AWS profiles) and have network access. A compromised or malicious package can exfiltrate secrets silently.
+
+## When to Activate
+
+Any time a new MCP server is being installed, added, configured, or updated. Trigger phrases: "install MCP", "add MCP", "set up MCP", "configure MCP", "claude mcp add", "new tool connection".
+
+## Step 1: Identify Provenance
+
+Determine who published the package before installing anything.
+
+| Signal | Official | Community |
+|--------|----------|-----------|
+| npm scope | `@salesforce/`, `@modelcontextprotocol/`, `@anthropic/` | `@username/`, unscoped |
+| PyPI publisher | Vendor org | Individual maintainer |
+| GitHub org | `github.com/aws/`, `github.com/figma/` | Personal account |
+| Hosted URL | Vendor domain (`mcp.atlassian.com`, `app.pendo.io`) | Third-party domain |
+
+## Step 2: Classify Risk
+
+| Classification | Criteria | Required Action |
+|----------------|----------|-----------------|
+| **Vendor-hosted** | Runs on vendor's own domain | Install. Low risk. |
+| **Vendor-published** | Published by vendor org on npm/PyPI | Install. Pin version. |
+| **MCP org** | Published under `@modelcontextprotocol/` | Install. Pin version. |
+| **Internal** | Built by your team, code reviewed | Install. |
+| **Community (established)** | 500+ GitHub stars, active maintenance, permissive license | Pin version. Audit source. Document in CLAUDE.md. |
+| **Community (unknown)** | Low stars, single maintainer, no audit trail | Do not install. Find an official alternative or build internally. |
+
+## Step 3: Audit Community Packages
+
+For any package classified as "Community (established)":
+
+**Pin the version.** Never install unpinned.
+- npm: `package@1.2.3` (not `package` or `package@latest`)
+- PyPI/uvx: `package==1.2.3` (not `package`)
+- In `~/.claude.json` or project MCP config, use the pinned specifier
+
+**Read the source.** Clone the repo at the pinned tag and check for:
+- Outbound network calls to unexpected domains (data exfiltration)
+- Credential logging, caching, or forwarding beyond what the API requires
+- Obfuscated code, eval/exec calls, or suspicious post-install scripts
+- Dependency chains pulling in unexpected packages
+
+**Map credential exposure.** Document exactly what secrets the package touches:
+- OAuth tokens (which provider, what scopes)
+- AWS credentials (access keys, assumed roles, profiles)
+- API keys (which service, what permissions)
+- Filesystem access (what paths it reads/writes)
+
+## Step 4: Document
+
+Add an entry to your project's CLAUDE.md or security config:
+
+```markdown
+| MCP | Package | Provenance | Status |
+|-----|---------|------------|--------|
+| Slack | @anthropic/slack-mcp | Official (MCP org) | Approved |
+| Athena | @user/athena-mcp@1.0.1 | Community (pinned) | Flagged: handles AWS creds |
+```
+
+## Step 5: Ongoing Maintenance
+
+- **Before updating** a community MCP version: read the changelog and diff between your pinned version and the new one. Look for new dependencies, changed network calls, or modified credential handling.
+- **When an official alternative ships**: migrate to it and remove the community package.
+- **Periodic re-check**: vendors release official MCPs without announcement. Search npm/PyPI for official packages quarterly.
+- **If a package is compromised**: revoke any credentials it had access to immediately, then remove the package.
+
+## Why This Matters
+
+MCP servers run as child processes with access to your shell environment, filesystem, and any credentials passed to them. Unlike browser extensions (sandboxed) or npm packages (typically build-time only), MCP servers actively send and receive data on your behalf at runtime. A single malicious update to an unpinned community package can capture every OAuth token and API key in your environment.
diff --git a/src/claude_mpm/skills/bundled/main/prep-meeting/SKILL.md b/src/claude_mpm/skills/bundled/main/prep-meeting/SKILL.md
@@ -0,0 +1,103 @@
+---
+name: prep-meeting
+description: Prepares for meetings by gathering context about attendees, topics, and relevant data across connected tools. Produces an agenda with talking points, supporting data, and anticipated questions.
+version: 1.0.0
+when_to_use: when preparing for a meeting, creating an agenda, getting ready for a call, or when the user mentions an upcoming meeting they want to be prepared for
+progressive_disclosure:
+  level: 1
+  references: []
+  note: Single-file workflow. Intentionally linear, not reference-heavy.
+---
+
+# Meeting Prep
+
+Gather context and produce a structured agenda with talking points before a meeting. The goal is to walk in prepared: knowing what each attendee cares about, having data to support your points, and anticipating questions.
+
+## When to Activate
+
+Trigger phrases: "prep for my meeting with", "agenda for", "get ready for the call with", "meeting with X tomorrow", "what should I bring to", "prepare for".
+
+## Step 1: Identify Meeting Details
+
+Gather the basics before researching:
+- **Who is attending?** Names and roles. Check calendar events if a Calendar MCP is available.
+- **What is the topic?** If unclear, infer from the invite title, recent project context, or ask.
+- **What is the format?** 1:1 vs group, decision meeting vs status update, internal vs external.
+- **What does the user want from this meeting?** A decision? Alignment? Information? Approval? This shapes the agenda structure.
+
+## Step 2: Gather Attendee Context
+
+For each key attendee, pull recent context from connected tools:
+
+| Source | What to Look For |
+|--------|-----------------|
+| Chat history (Slack, Teams) | Recent conversations with or about this person. Open threads, unanswered questions, pending requests. |
+| Issue tracker (Jira, Linear) | Tickets they own or are blocked on. Shared projects. |
+| Email | Recent exchanges, especially unresolved items. |
+| Project knowledge files | Their role, relationship, past interactions. Stakeholder notes if they exist. |
+
+Focus on: What have they been working on? What do they care about? What's their likely agenda coming into this meeting?
+
+## Step 3: Pull Topic Context
+
+Based on the meeting topic, gather supporting material:
+
+- **Project status**: Current state from knowledge files, recent commits, ticket boards
+- **Data points**: Relevant metrics or query results from databases or analytics tools
+- **Documents**: Related PRDs, design docs, roadmap pages, decision records
+- **Recent discussions**: Slack/Teams threads where this topic was debated
+- **Blockers**: Anything stuck that might come up
+
+Pull specific data, not vague summaries. "Acceptance rate is 31% higher in test group (p=0.03)" is preparation. "Metrics look good" is not.
+
+## Step 4: Draft Agenda
+
+Structure the agenda based on meeting type:
+
+**Decision meeting:**
+```
+Context: [2-3 sentences on why we're here]
+
+1. [Decision needed] - [supporting data point]
+2. [Decision needed] - [supporting data point]
+
+Options:
+A. [Option] - [tradeoffs]
+B. [Option] - [tradeoffs]
+
+Recommendation: [your position and why]
+```
+
+**Status/sync meeting:**
+```
+Context: [what happened since last sync]
+
+1. Progress: [what shipped or moved forward]
+2. In flight: [what's actively being worked]
+3. Blockers: [what needs help]
+4. Next steps: [what happens after this meeting]
+```
+
+**Exploratory/brainstorm meeting:**
+```
+Context: [the problem or opportunity]
+
+1. What we know: [facts and data]
+2. What we don't know: [open questions]
+3. Options to discuss: [2-3 approaches with tradeoffs]
+```
+
+## Step 5: Prepare Talking Points
+
+For each agenda item, prepare:
+- **Lead with data**: The strongest number or fact that supports your point
+- **Your position**: What you think should happen and why, stated plainly
+- **Anticipated pushback**: What objections might come up and how to address them
+- **Fallback**: If your preferred outcome isn't accepted, what's the next-best option?
+
+## Step 6: Deliver
+
+Present the agenda and talking points to the user for review. Then offer to:
+- Add the agenda to the calendar event (via Calendar MCP if available)
+- Send a pre-read message to attendees via chat
+- Pull additional data on any agenda item that needs more support
PATCH

echo "Gold patch applied."
