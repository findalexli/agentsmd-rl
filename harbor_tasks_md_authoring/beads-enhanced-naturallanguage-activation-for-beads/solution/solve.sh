#!/usr/bin/env bash
set -euo pipefail

cd /workspace/beads

# Idempotency guard
if grep -qF "**Progressive Disclosure**: This skill provides essential instructions for all 3" "skills/beads/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/beads/SKILL.md b/skills/beads/SKILL.md
@@ -1,644 +1,824 @@
 ---
 name: beads
-description: Track complex, multi-session work with dependency graphs using beads issue tracker. Use when work spans multiple sessions, has complex dependencies, or requires persistent context across compaction cycles. For simple single-session linear tasks, TodoWrite remains appropriate.
+description: >
+  Tracks complex, multi-session work using the Beads issue tracker and dependency graphs, and provides
+  persistent memory that survives conversation compaction. Use when work spans multiple sessions, has
+  complex dependencies, or needs persistent context across compaction cycles. Trigger with phrases like
+  "create task for", "what's ready to work on", "show task", "track this work", "what's blocking", or
+  "update status".
+allowed-tools: "Read,Bash(bd:*)"
+version: "0.34.0"
+author: "Steve Yegge <https://github.com/steveyegge>"
+license: "MIT"
 ---
 
-# Beads
+# Beads - Persistent Task Memory for AI Agents
+
+Graph-based issue tracker that survives conversation compaction. Provides persistent memory for multi-session work with complex dependencies.
 
 ## Overview
 
-bd is a graph-based issue tracker for persistent memory across sessions. Use for multi-session work with complex dependencies; use TodoWrite for simple single-session tasks.
+**bd (beads)** replaces markdown task lists with a dependency-aware graph stored in git. Unlike TodoWrite (session-scoped), bd persists across compactions and tracks complex dependencies.
 
-## When to Use bd vs TodoWrite
+**Key Distinction**:
+- **bd**: Multi-session work, dependencies, survives compaction, git-backed
+- **TodoWrite**: Single-session tasks, linear execution, conversation-scoped
 
-### Use bd when:
-- **Multi-session work** - Tasks spanning multiple compaction cycles or days
-- **Complex dependencies** - Work with blockers, prerequisites, or hierarchical structure
-- **Knowledge work** - Strategic documents, research, or tasks with fuzzy boundaries
-- **Side quests** - Exploratory work that might pause the main task
-- **Project memory** - Need to resume work after weeks away with full context
+**Core Capabilities**:
+- 📊 **Dependency Graphs**: Track what blocks what (blocks, parent-child, discovered-from, related)
+- 💾 **Compaction Survival**: Tasks persist when conversation history is compacted
+- 🐙 **Git Integration**: Issues versioned in `.beads/issues.jsonl`, sync with `bd sync`
+- 🔍 **Smart Discovery**: Auto-finds ready work (`bd ready`), blocked work (`bd blocked`)
+- 📝 **Audit Trails**: Complete history of status changes, notes, and decisions
+- 🏷️ **Rich Metadata**: Priority (P0-P4), types (bug/feature/task/epic), labels, assignees
 
-### Use TodoWrite when:
-- **Single-session tasks** - Work that completes within current session
-- **Linear execution** - Straightforward step-by-step tasks with no branching
-- **Immediate context** - All information already in conversation
-- **Simple tracking** - Just need a checklist to show progress
+**When to Use bd vs TodoWrite**:
+- ❓ "Will I need this context in 2 weeks?" → **YES** = bd
+- ❓ "Could conversation history get compacted?" → **YES** = bd
+- ❓ "Does this have blockers/dependencies?" → **YES** = bd
+- ❓ "Is this fuzzy/exploratory work?" → **YES** = bd
+- ❓ "Will this be done in this session?" → **YES** = TodoWrite
+- ❓ "Is this just a task list for me right now?" → **YES** = TodoWrite
 
-**Key insight**: If resuming work after 2 weeks would be difficult without bd, use bd. If the work can be picked up from a markdown skim, TodoWrite is sufficient.
+**Decision Rule**: If resuming in 2 weeks would be hard without bd, use bd.
 
-### Test Yourself: bd or TodoWrite?
+## Prerequisites
 
-Ask these questions to decide:
+**Required**:
+- **bd CLI**: Version 0.34.0 or later installed and in PATH
+- **Git Repository**: Current directory must be a git repo
+- **Initialization**: `bd init` must be run once (humans do this, not agents)
 
-**Choose bd if:**
-- ❓ "Will I need this context in 2 weeks?" → Yes = bd
-- ❓ "Could conversation history get compacted?" → Yes = bd
-- ❓ "Does this have blockers/dependencies?" → Yes = bd
-- ❓ "Is this fuzzy/exploratory work?" → Yes = bd
+**Verify Installation**:
+```bash
+bd --version  # Should return 0.34.0 or later
+```
 
-**Choose TodoWrite if:**
-- ❓ "Will this be done in this session?" → Yes = TodoWrite
-- ❓ "Is this just a task list for me right now?" → Yes = TodoWrite
-- ❓ "Is this linear with no branching?" → Yes = TodoWrite
+**First-Time Setup** (humans run once):
+```bash
+cd /path/to/your/repo
+bd init  # Creates .beads/ directory with database
+```
 
-**When in doubt**: Use bd. Better to have persistent memory you don't need than to lose context you needed.
+**Optional**:
+- **BEADS_DIR** environment variable for alternate database location
+- **Daemon** for background sync: `bd daemon --start`
 
-**For detailed decision criteria and examples, read:** [references/BOUNDARIES.md](references/BOUNDARIES.md)
+## Instructions
 
-## Surviving Compaction Events
+### Session Start Protocol
 
-**Critical**: Compaction events delete conversation history but preserve beads. After compaction, bd state is your only persistent memory.
+**Every session, start here:**
 
-**What survives compaction:**
-- All bead data (issues, notes, dependencies, status)
-- Complete work history and context
+#### Step 1: Check for Ready Work
 
-**What doesn't survive:**
-- Conversation history
-- TodoWrite lists
-- Recent discussion context
+```bash
+bd ready
+```
 
-**Writing notes for post-compaction recovery:**
+Shows tasks with no open blockers, sorted by priority (P0 → P4).
 
-Write notes as if explaining to a future agent with zero conversation context:
+**What this shows**:
+- Task ID (e.g., `myproject-abc`)
+- Title
+- Priority level
+- Issue type (bug, feature, task, epic)
 
-**Pattern:**
-```markdown
-notes field format:
-- COMPLETED: Specific deliverables ("implemented JWT refresh endpoint + rate limiting")
-- IN PROGRESS: Current state + next immediate step ("testing password reset flow, need user input on email template")
-- BLOCKERS: What's preventing progress
-- KEY DECISIONS: Important context or user guidance
+**Example output**:
 ```
+claude-code-plugins-abc [P1] [task] open
+  Implement user authentication
 
-**After compaction:** `bd show <issue-id>` reconstructs full context from notes field.
-
-### Notes Quality Self-Check
+claude-code-plugins-xyz [P0] [epic] in_progress
+  Refactor database layer
+```
 
-Before checkpointing (especially pre-compaction), verify your notes pass these tests:
+#### Step 2: Pick Highest Priority Task
 
-❓ **Future-me test**: "Could I resume this work in 2 weeks with zero conversation history?"
-- [ ] What was completed? (Specific deliverables, not "made progress")
-- [ ] What's in progress? (Current state + immediate next step)
-- [ ] What's blocked? (Specific blockers with context)
-- [ ] What decisions were made? (Why, not just what)
+Choose the highest priority (P0 > P1 > P2 > P3 > P4) task that's ready.
 
-❓ **Stranger test**: "Could another developer understand this without asking me?"
-- [ ] Technical choices explained (not just stated)
-- [ ] Trade-offs documented (why this approach vs alternatives)
-- [ ] User input captured (decisions that came from discussion)
+#### Step 3: Get Full Context
 
-**Good note example:**
-```
-COMPLETED: JWT auth with RS256 (1hr access, 7d refresh tokens)
-KEY DECISION: RS256 over HS256 per security review - enables key rotation
-IN PROGRESS: Password reset flow - email service working, need rate limiting
-BLOCKERS: Waiting on user decision: reset token expiry (15min vs 1hr trade-off)
-NEXT: Implement rate limiting (5 attempts/15min) once expiry decided
+```bash
+bd show <task-id>
 ```
 
-**Bad note example:**
-```
-Working on auth. Made some progress. More to do.
-```
+Displays:
+- Full task description
+- Dependency graph (what blocks this, what this blocks)
+- Audit trail (all status changes, notes)
+- Metadata (created, updated, assignee, labels)
 
-**For complete compaction recovery workflow, read:** [references/WORKFLOWS.md](references/WORKFLOWS.md#compaction-survival)
+#### Step 4: Start Working
 
-## Session Start Protocol
+```bash
+bd update <task-id> --status in_progress
+```
 
-**bd is available when:**
-- Project has a `.beads/` directory (project-local database), OR
-- `~/.beads/` exists (global fallback database for any directory)
+Marks task as actively being worked on.
 
-**At session start, always check for bd availability and run ready check.**
+#### Step 5: Add Notes as You Work
 
-### Session Start Checklist
+```bash
+bd update <task-id> --notes "Completed: X. In progress: Y. Blocked by: Z"
+```
 
-Copy this checklist when starting any session where bd is available:
+**Critical for compaction survival**: Write notes as if explaining to a future agent with zero conversation context.
 
+**Note Format** (best practice):
 ```
-Session Start:
-- [ ] Run bd ready --json to see available work
-- [ ] Run bd list --status in_progress --json for active work
-- [ ] If in_progress exists: bd show <issue-id> to read notes
-- [ ] Report context to user: "X items ready: [summary]"
-- [ ] If using global ~/.beads, mention this in report
-- [ ] If nothing ready: bd blocked --json to check blockers
+COMPLETED: Specific deliverables (e.g., "implemented JWT refresh endpoint + rate limiting")
+IN PROGRESS: Current state + next immediate step
+BLOCKERS: What's preventing progress
+KEY DECISIONS: Important context or user guidance
 ```
 
-**Pattern**: Always check both `bd ready` AND `bd list --status in_progress`. Read notes field first to understand where previous session left off.
+---
 
-**Report format**:
-- "I can see X items ready to work on: [summary]"
-- "Issue Y is in_progress. Last session: [summary from notes]. Next: [from notes]. Should I continue with that?"
+### Task Creation Workflow
 
-This establishes immediate shared context about available and active work without requiring user prompting.
+#### When to Create Tasks
 
-**For detailed collaborative handoff process, read:** [references/WORKFLOWS.md](references/WORKFLOWS.md#session-handoff)
+Create bd tasks when:
+- User mentions tracking work across sessions
+- User says "we should fix/build/add X"
+- Work has dependencies or blockers
+- Exploratory/research work with fuzzy boundaries
 
-**Note**: bd auto-discovers the database:
-- Uses `.beads/*.db` in current project if exists
-- Falls back to `~/.beads/default.db` otherwise
-- No configuration needed
+#### Basic Task Creation
 
-### When No Work is Ready
+```bash
+bd create "Task title" -p 1 --type task
+```
 
-If `bd ready` returns empty but issues exist:
+**Arguments**:
+- **Title**: Brief description (required)
+- **Priority**: 0-4 where 0=critical, 1=high, 2=medium, 3=low, 4=backlog (default: 2)
+- **Type**: bug, feature, task, epic, chore (default: task)
 
+**Example**:
 ```bash
-bd blocked --json
+bd create "Fix authentication bug" -p 0 --type bug
 ```
 
-Report blockers and suggest next steps.
+#### Create with Description
 
----
+```bash
+bd create "Implement OAuth" -p 1 --description "Add OAuth2 support for Google, GitHub, Microsoft. Use passport.js library."
+```
 
-## Progress Checkpointing
+#### Epic with Children
 
-Update bd notes at these checkpoints (don't wait for session end):
+```bash
+# Create parent epic
+bd create "Epic: OAuth Implementation" -p 0 --type epic
+# Returns: myproject-abc
 
-**Critical triggers:**
-- ⚠️ **Context running low** - User says "running out of context" / "approaching compaction" / "close to token limit"
-- 📊 **Token budget > 70%** - Proactively checkpoint when approaching limits
-- 🎯 **Major milestone reached** - Completed significant piece of work
-- 🚧 **Hit a blocker** - Can't proceed, need to capture what was tried
-- 🔄 **Task transition** - Switching issues or about to close this one
-- ❓ **Before user input** - About to ask decision that might change direction
+# Create child tasks
+bd create "Research OAuth providers" -p 1 --parent myproject-abc
+bd create "Implement auth endpoints" -p 1 --parent myproject-abc
+bd create "Add frontend login UI" -p 2 --parent myproject-abc
+```
 
-**Proactive monitoring during session:**
-- At 70% token usage: "We're at 70% token usage - good time to checkpoint bd notes?"
-- At 85% token usage: "Approaching token limit (85%) - checkpointing current state to bd"
-- At 90% token usage: Automatically checkpoint without asking
+---
 
-**Current token usage**: Check `<system-warning>Token usage:` messages to monitor proactively.
+### Update & Progress Workflow
 
-**Checkpoint checklist:**
+#### Change Status
 
-```
-Progress Checkpoint:
-- [ ] Update notes with COMPLETED/IN_PROGRESS/NEXT format
-- [ ] Document KEY DECISIONS or BLOCKERS since last update
-- [ ] Mark current status (in_progress/blocked/closed)
-- [ ] If discovered new work: create issues with discovered-from
-- [ ] Verify notes are self-explanatory for post-compaction resume
+```bash
+bd update <task-id> --status <new-status>
 ```
 
-**Most important**: When user says "running out of context" OR when you see >70% token usage - checkpoint immediately, even if mid-task.
+**Status Values**:
+- `open` - Not started
+- `in_progress` - Actively working
+- `blocked` - Stuck, waiting on something
+- `closed` - Completed
 
-**Test yourself**: "If compaction happened right now, could future-me resume from these notes?"
+**Example**:
+```bash
+bd update myproject-abc --status blocked
+```
 
----
+#### Add Progress Notes
 
-### Database Selection
+```bash
+bd update <task-id> --notes "Progress update here"
+```
 
-bd automatically selects the appropriate database:
-- **Project-local** (`.beads/` in project): Used for project-specific work
-- **Global fallback** (`~/.beads/`): Used when no project-local database exists
+**Appends** to existing notes field (doesn't replace).
 
-**Use case for global database**: Cross-project tracking, personal task management, knowledge work that doesn't belong to a specific project.
+#### Change Priority
+
+```bash
+bd update <task-id> -p 0  # Escalate to critical
+```
 
-**When to use --db flag explicitly:**
-- Accessing a specific database outside current directory
-- Working with multiple databases (e.g., project database + reference database)
-- Example: `bd --db /path/to/reference/terms.db list`
+#### Add Labels
 
-**Database discovery rules:**
-- bd looks for `.beads/*.db` in current working directory
-- If not found, uses `~/.beads/default.db`
-- Shell cwd can reset between commands - use absolute paths with --db when operating on non-local databases
+```bash
+bd label add <task-id> backend
+bd label add <task-id> security
+```
 
-**For complete session start workflows, read:** [references/WORKFLOWS.md](references/WORKFLOWS.md#session-start)
+Labels provide cross-cutting categorization beyond status/type.
 
-## Core Operations
+---
 
-All bd commands support `--json` flag for structured output when needed for programmatic parsing.
+### Dependency Management
 
-### Essential Operations
+#### Add Dependencies
 
-**Check ready work:**
 ```bash
-bd ready
-bd ready --json              # For structured output
-bd ready --priority 0        # Filter by priority
-bd ready --assignee alice    # Filter by assignee
+bd dep add <child-id> <parent-id>
 ```
 
-**Create new issue:**
+**Meaning**: `<parent-id>` blocks `<child-id>` (parent must be completed first).
 
-**IMPORTANT**: Always quote title and description arguments with double quotes, especially when containing spaces or special characters.
+**Dependency Types**:
+- **blocks**: Parent must close before child becomes ready
+- **parent-child**: Hierarchical relationship (epics and subtasks)
+- **discovered-from**: Task A led to discovering task B
+- **related**: Tasks are related but not blocking
 
+**Example**:
 ```bash
-bd create "Fix login bug"
-bd create "Add OAuth" -p 0 -t feature
-bd create "Write tests" -d "Unit tests for auth module" --assignee alice
-bd create "Research caching" --design "Evaluate Redis vs Memcached"
-
-# Examples with special characters (requires quoting):
-bd create "Fix: auth doesn't handle edge cases" -p 1
-bd create "Refactor auth module" -d "Split auth.go into separate files (handlers, middleware, utils)"
+# Deployment blocked by tests passing
+bd dep add deploy-task test-task  # test-task blocks deploy-task
 ```
 
-**Update issue status:**
+#### View Dependencies
+
 ```bash
-bd update issue-123 --status in_progress
-bd update issue-123 --priority 0
-bd update issue-123 --assignee bob
-bd update issue-123 --design "Decided to use Redis for persistence support"
+bd dep list <task-id>
 ```
 
-**Close completed work:**
+Shows:
+- What this task blocks (dependents)
+- What blocks this task (blockers)
+
+#### Circular Dependency Prevention
+
+bd automatically prevents circular dependencies. If you try to create a cycle, the command fails.
+
+---
+
+### Completion Workflow
+
+#### Close a Task
+
 ```bash
-bd close issue-123
-bd close issue-123 --reason "Implemented in PR #42"
-bd close issue-1 issue-2 issue-3 --reason "Bulk close related work"
+bd close <task-id> --reason "Completion summary"
 ```
 
-**Show issue details:**
+**Best Practice**: Always include a reason describing what was accomplished.
+
+**Example**:
 ```bash
-bd show issue-123
-bd show issue-123 --json
+bd close myproject-abc --reason "Completed: OAuth endpoints implemented with Google, GitHub providers. Tests passing."
 ```
 
-**List issues:**
+#### Check Newly Unblocked Work
+
+After closing a task, run:
+
 ```bash
-bd list
-bd list --status open
-bd list --priority 0
-bd list --type bug
-bd list --assignee alice
+bd ready
 ```
 
-**For complete CLI reference with all flags and examples, read:** [references/CLI_REFERENCE.md](references/CLI_REFERENCE.md)
-
-## Field Usage Reference
+Closing a task may unblock dependent tasks, making them newly ready.
 
-Quick guide for when and how to use each bd field:
+#### Close Epics When Children Complete
 
-| Field | Purpose | When to Set | Update Frequency |
-|-------|---------|-------------|------------------|
-| **description** | Immutable problem statement | At creation | Never (fixed forever) |
-| **design** | Initial approach, architecture, decisions | During planning | Rarely (only if approach changes) |
-| **acceptance-criteria** | Concrete deliverables checklist (`- [ ]` syntax) | When design is clear | Mark `- [x]` as items complete |
-| **notes** | Session handoff (COMPLETED/IN_PROGRESS/NEXT) | During work | At session end, major milestones |
-| **status** | Workflow state (open→in_progress→closed) | As work progresses | When changing phases |
-| **priority** | Urgency level (0=highest, 3=lowest) | At creation | Adjust if priorities shift |
+```bash
+bd epic close-eligible
+```
 
-**Key pattern**: Notes field is your "read me first" at session start. See [WORKFLOWS.md](references/WORKFLOWS.md#session-handoff) for session handoff details.
+Automatically closes epics where all child tasks are closed.
 
 ---
 
-## Issue Lifecycle Workflow
+### Git Sync Workflow
 
-### 1. Discovery Phase (Proactive Issue Creation)
+#### All-in-One Sync
 
-**During exploration or implementation, proactively file issues for:**
-- Bugs or problems discovered
-- Potential improvements noticed
-- Follow-up work identified
-- Technical debt encountered
-- Questions requiring research
-
-**Pattern:**
 ```bash
-# When encountering new work during a task:
-bd create "Found: auth doesn't handle profile permissions"
-bd dep add current-task-id new-issue-id --type discovered-from
-
-# Continue with original task - issue persists for later
+bd sync
 ```
 
-**Key benefit**: Capture context immediately instead of losing it when conversation ends.
+**Performs**:
+1. Export database to `.beads/issues.jsonl`
+2. Commit changes to git
+3. Pull from remote (merge if needed)
+4. Import updated JSONL back to database
+5. Push local commits to remote
+
+**Use when**: End of session, before handing off to teammate, after major progress.
 
-### 2. Execution Phase (Status Maintenance)
+#### Export Only
 
-**Mark issues in_progress when starting work:**
 ```bash
-bd update issue-123 --status in_progress
+bd export -o backup.jsonl
 ```
 
-**Update throughout work:**
-```bash
-# Add design notes as implementation progresses
-bd update issue-123 --design "Using JWT with RS256 algorithm"
+Creates JSONL backup without git operations.
+
+#### Import Only
 
-# Update acceptance criteria if requirements clarify
-bd update issue-123 --acceptance "- JWT validation works\n- Tests pass\n- Error handling returns 401"
+```bash
+bd import -i backup.jsonl
 ```
 
-**Close when complete:**
+Imports JSONL file into database.
+
+#### Background Daemon
+
 ```bash
-bd close issue-123 --reason "Implemented JWT validation with tests passing"
+bd daemon --start  # Auto-sync in background
+bd daemon --status # Check daemon health
+bd daemon --stop   # Stop auto-sync
 ```
 
-**Important**: Closed issues remain in database - they're not deleted, just marked complete for project history.
+Daemon watches for database changes and auto-exports to JSONL.
+
+---
 
-### 3. Planning Phase (Dependency Graphs)
+### Find & Search Commands
 
-For complex multi-step work, structure issues with dependencies before starting:
+#### Find Ready Work
 
-**Create parent epic:**
 ```bash
-bd create "Implement user authentication" -t epic -d "OAuth integration with JWT tokens"
+bd ready
 ```
 
-**Create subtasks:**
+Shows tasks with no open blockers.
+
+#### List All Tasks
+
 ```bash
-bd create "Set up OAuth credentials" -t task
-bd create "Implement authorization flow" -t task
-bd create "Add token refresh" -t task
+bd list --status open           # Only open tasks
+bd list --priority 0            # Only P0 (critical)
+bd list --type bug              # Only bugs
+bd list --label backend         # Only labeled "backend"
+bd list --assignee alice        # Only assigned to alice
 ```
 
-**Link with dependencies:**
-```bash
-# parent-child for epic structure
-bd dep add auth-epic auth-setup --type parent-child
-bd dep add auth-epic auth-flow --type parent-child
+#### Show Task Details
 
-# blocks for ordering
-bd dep add auth-setup auth-flow
+```bash
+bd show <task-id>
 ```
 
-**For detailed dependency patterns and types, read:** [references/DEPENDENCIES.md](references/DEPENDENCIES.md)
+Full details: description, dependencies, audit trail, metadata.
 
-## Dependency Types Reference
+#### Search by Text
 
-bd supports four dependency types:
+```bash
+bd search "authentication"      # Search titles and descriptions
+bd search login --status open   # Combine with filters
+```
+
+#### Find Blocked Work
+
+```bash
+bd blocked
+```
 
-1. **blocks** - Hard blocker (issue A blocks issue B from starting)
-2. **related** - Soft link (issues are related but not blocking)
-3. **parent-child** - Hierarchical (epic/subtask relationship)
-4. **discovered-from** - Provenance (issue B discovered while working on A)
+Shows all tasks that have open blockers preventing them from being worked on.
 
-**For complete guide on when to use each type with examples and patterns, read:** [references/DEPENDENCIES.md](references/DEPENDENCIES.md)
+#### Project Statistics
 
-## Integration with TodoWrite
+```bash
+bd stats
+```
 
-**Both tools complement each other at different timescales:**
+Shows:
+- Total issues by status (open, in_progress, blocked, closed)
+- Issues by priority (P0-P4)
+- Issues by type (bug, feature, task, epic, chore)
+- Completion rate
 
-### Temporal Layering Pattern
+---
 
-**TodoWrite** (short-term working memory - this hour):
-- Tactical execution: "Review Section 3", "Expand Q&A answers"
-- Marked completed as you go
-- Present/future tense ("Review", "Expand", "Create")
-- Ephemeral: Disappears when session ends
+### Complete Command Reference
+
+| Command | When to Use | Example |
+|---------|-------------|---------|
+| **FIND COMMANDS** | | |
+| `bd ready` | Find unblocked tasks | User asks "what should I work on?" |
+| `bd list` | View all tasks (with filters) | "Show me all open bugs" |
+| `bd show <id>` | Get task details | "Show me task bd-42" |
+| `bd search <query>` | Text search across tasks | "Find tasks about auth" |
+| `bd blocked` | Find stuck work | "What's blocking us?" |
+| `bd stats` | Project metrics | "How many tasks are open?" |
+| **CREATE COMMANDS** | | |
+| `bd create` | Track new work | "Create a task for this bug" |
+| `bd template create` | Use issue template | "Create task from bug template" |
+| `bd init` | Initialize beads | "Set up beads in this repo" (humans only) |
+| **UPDATE COMMANDS** | | |
+| `bd update <id>` | Change status/priority/notes | "Mark as in progress" |
+| `bd dep add` | Link dependencies | "This blocks that" |
+| `bd label add` | Tag with labels | "Label this as backend" |
+| `bd comments add` | Add comment | "Add comment to task" |
+| `bd reopen <id>` | Reopen closed task | "Reopen bd-42, found regression" |
+| `bd rename-prefix` | Rename issue prefix | "Change prefix from bd- to proj-" |
+| `bd epic status` | Check epic progress | "Show epic completion %" |
+| **COMPLETE COMMANDS** | | |
+| `bd close <id>` | Mark task done | "Close this task, it's done" |
+| `bd epic close-eligible` | Auto-close complete epics | "Close epics where all children done" |
+| **SYNC COMMANDS** | | |
+| `bd sync` | Git sync (all-in-one) | "Sync tasks to git" |
+| `bd export` | Export to JSONL | "Backup all tasks" |
+| `bd import` | Import from JSONL | "Restore from backup" |
+| `bd daemon` | Background sync manager | "Start auto-sync daemon" |
+| **CLEANUP COMMANDS** | | |
+| `bd delete <id>` | Delete issues | "Delete test task" (requires --force) |
+| `bd compact` | Archive old closed tasks | "Compress database" |
+| **REPORTING COMMANDS** | | |
+| `bd stats` | Project metrics | "Show project health" |
+| `bd audit record` | Log interactions | "Record this LLM call" |
+| `bd workflow` | Show workflow guide | "How do I use beads?" |
+| **ADVANCED COMMANDS** | | |
+| `bd prime` | Refresh AI context | "Load bd workflow rules" |
+| `bd quickstart` | Interactive tutorial | "Teach me beads basics" |
+| `bd daemons` | Multi-repo daemon mgmt | "Manage all beads daemons" |
+| `bd version` | Version check | "Check bd version" |
+| `bd restore <id>` | Restore compacted issue | "Get full history from git" |
 
-**Beads** (long-term episodic memory - this week/month):
-- Strategic objectives: "Continue work on strategic planning document"
-- Key decisions and outcomes in notes field
-- Past tense in notes ("COMPLETED", "Discovered", "Blocked by")
-- Persistent: Survives compaction and session boundaries
+---
 
-### The Handoff Pattern
+## Output
 
-1. **Session start**: Read bead → Create TodoWrite items for immediate actions
-2. **During work**: Mark TodoWrite items completed as you go
-3. **Reach milestone**: Update bead notes with outcomes + context
-4. **Session end**: TodoWrite disappears, bead survives with enriched notes
+This skill produces:
 
-**After compaction**: TodoWrite is gone forever, but bead notes reconstruct what happened.
+**Task IDs**: Format `<prefix>-<hash>` (e.g., `claude-code-plugins-abc`, `myproject-xyz`)
 
-### Example: TodoWrite tracks execution, Beads capture meaning
+**Status Summaries**:
+```
+5 open, 2 in_progress, 1 blocked, 47 closed
+```
 
-**TodoWrite:**
+**Dependency Graphs** (visual tree):
 ```
-[completed] Implement login endpoint
-[in_progress] Add password hashing with bcrypt
-[pending] Create session middleware
+myproject-abc: Deploy to production [P0] [blocked]
+  Blocked by:
+    ↳ myproject-def: Run integration tests [P1] [in_progress]
+    ↳ myproject-ghi: Fix failing tests [P1] [open]
 ```
 
-**Corresponding bead notes:**
+**Audit Trails** (complete history):
 ```
-bd update issue-123 --notes "COMPLETED: Login endpoint with bcrypt password
-hashing (12 rounds). KEY DECISION: Using JWT tokens (not sessions) for stateless
-auth - simplifies horizontal scaling. IN PROGRESS: Session middleware implementation.
-NEXT: Need user input on token expiry time (1hr vs 24hr trade-off)."
+2025-12-22 10:00 - Created by alice (P2, task)
+2025-12-22 10:15 - Priority changed: P2 → P0
+2025-12-22 10:30 - Status changed: open → in_progress
+2025-12-22 11:00 - Notes added: "Implemented JWT auth..."
+2025-12-22 14:00 - Status changed: in_progress → blocked
+2025-12-22 14:01 - Notes added: "Blocked: API endpoint returns 503"
 ```
 
-**Don't duplicate**: TodoWrite tracks execution, Beads captures meaning and context.
+---
 
-**For patterns on transitioning between tools mid-session, read:** [references/BOUNDARIES.md](references/BOUNDARIES.md#integration-patterns)
+## Error Handling
 
-## Common Patterns
+### Common Failures
 
-### Pattern 1: Knowledge Work Session
+#### 1. `bd: command not found`
+**Cause**: bd CLI not installed or not in PATH
+**Solution**: Install from https://github.com/steveyegge/beads
+```bash
+# macOS/Linux
+curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash
 
-**Scenario**: User asks "Help me write a proposal for expanding the analytics platform"
+# Or via npm
+npm install -g @beads/bd
 
-**What you see**:
-```bash
-$ bd ready
-# Returns: bd-42 "Research analytics platform expansion proposal" (in_progress)
+# Or via Homebrew
+brew install steveyegge/beads/bd
+```
 
-$ bd show bd-42
-Notes: "COMPLETED: Reviewed current stack (Mixpanel, Amplitude)
-IN PROGRESS: Drafting cost-benefit analysis section
-NEXT: Need user input on budget constraints before finalizing recommendations"
+#### 2. `No .beads database found`
+**Cause**: beads not initialized in this repository
+**Solution**: Run `bd init` (humans do this once, not agents)
+```bash
+bd init  # Creates .beads/ directory
 ```
 
-**What you do**:
-1. Read notes to understand current state
-2. Create TodoWrite for immediate work:
-   ```
-   - [ ] Draft cost-benefit analysis
-   - [ ] Ask user about budget constraints
-   - [ ] Finalize recommendations
-   ```
-3. Work on tasks, mark TodoWrite items completed
-4. At milestone, update bd notes:
-   ```bash
-   bd update bd-42 --notes "COMPLETED: Cost-benefit analysis drafted.
-   KEY DECISION: User confirmed $50k budget cap - ruled out enterprise options.
-   IN PROGRESS: Finalizing recommendations (Posthog + custom ETL).
-   NEXT: Get user review of draft before closing issue."
-   ```
+#### 3. `Task not found: <id>`
+**Cause**: Invalid task ID or task doesn't exist
+**Solution**: Use `bd list` to see all tasks and verify ID format
+```bash
+bd list                    # See all tasks
+bd search <partial-title>  # Find task by title
+```
 
-**Outcome**: TodoWrite disappears at session end, but bd notes preserve context for next session.
+#### 4. `Circular dependency detected`
+**Cause**: Attempting to create a dependency cycle (A blocks B, B blocks A)
+**Solution**: bd prevents circular dependencies automatically. Restructure dependency graph.
+```bash
+bd dep list <id>  # View current dependencies
+```
 
-### Pattern 2: Side Quest Handling
+#### 5. Git merge conflicts in `.beads/issues.jsonl`
+**Cause**: Multiple users modified same issue
+**Solution**: bd sync handles JSONL conflicts automatically. If manual intervention needed:
+```bash
+# View conflict
+git status
 
-During main task, discover a problem:
-1. Create issue: `bd create "Found: inventory system needs refactoring"`
-2. Link using discovered-from: `bd dep add main-task new-issue --type discovered-from`
-3. Assess: blocker or can defer?
-4. If blocker: `bd update main-task --status blocked`, work on new issue
-5. If deferrable: note in issue, continue main task
+# bd provides conflict resolution tools
+bd sync --merge  # Attempt auto-resolution
+```
 
-### Pattern 3: Multi-Session Project Resume
+#### 6. `Database is locked`
+**Cause**: Daemon or another process has exclusive lock
+**Solution**: Restart daemon or wait for lock to release
+```bash
+bd daemon --stop
+bd daemon --start
+```
 
-Starting work after time away:
-1. Run `bd ready` to see available work
-2. Run `bd blocked` to understand what's stuck
-3. Run `bd list --status closed --limit 10` to see recent completions
-4. Run `bd show issue-id` on issue to work on
-5. Update status and begin work
+#### 7. Sync failures
+**Cause**: Network issues, authentication failures, or git configuration
+**Solution**: Check git remote access and credentials
+```bash
+git fetch  # Test connectivity
+git status # Verify repo state
+```
 
-**For complete workflow walkthroughs with checklists, read:** [references/WORKFLOWS.md](references/WORKFLOWS.md)
+---
 
-## Issue Creation
+## Examples
 
-**Quick guidelines:**
-- Ask user first for knowledge work with fuzzy boundaries
-- Create directly for clear bugs, technical debt, or discovered work
-- Use clear titles, sufficient context in descriptions
-- Design field: HOW to build (can change during implementation)
-- Acceptance criteria: WHAT success looks like (should remain stable)
+### Example 1: Multi-Session Feature (Epic with Children)
 
-### Issue Creation Checklist
+**User Request**: "We need to implement OAuth, this will take multiple sessions"
 
-Copy when creating new issues:
+**Agent Response**:
+```bash
+# Create epic
+bd create "Epic: OAuth Implementation" -p 0 --type epic
+# Returns: claude-code-plugins-abc
 
-```
-Creating Issue:
-- [ ] Title: Clear, specific, action-oriented
-- [ ] Description: Problem statement (WHY this matters) - immutable
-- [ ] Design: HOW to build (can change during work)
-- [ ] Acceptance: WHAT success looks like (stays stable)
-- [ ] Priority: 0=critical, 1=high, 2=normal, 3=low
-- [ ] Type: bug/feature/task/epic/chore
-```
+# Create child tasks
+bd create "Research OAuth providers (Google, GitHub, Microsoft)" -p 1 --parent claude-code-plugins-abc
+# Returns: claude-code-plugins-abc.1
 
-**Self-check for acceptance criteria:**
+bd create "Implement backend auth endpoints" -p 1 --parent claude-code-plugins-abc
+# Returns: claude-code-plugins-abc.2
 
-❓ "If I changed the implementation approach, would these criteria still apply?"
-- → **Yes** = Good criteria (outcome-focused)
-- → **No** = Move to design field (implementation-focused)
+bd create "Add frontend login UI components" -p 2 --parent claude-code-plugins-abc
+# Returns: claude-code-plugins-abc.3
 
-**Example:**
-- ✅ Acceptance: "User tokens persist across sessions and refresh automatically"
-- ❌ Wrong: "Use JWT tokens with 1-hour expiry" (that's design, not acceptance)
+# Add dependencies (backend must complete before frontend)
+bd dep add claude-code-plugins-abc.3 claude-code-plugins-abc.2
 
-**For detailed guidance on when to ask vs create, issue quality, resumability patterns, and design vs acceptance criteria, read:** [references/ISSUE_CREATION.md](references/ISSUE_CREATION.md)
+# Start with research
+bd update claude-code-plugins-abc.1 --status in_progress
+```
 
-## Alternative Use Cases
+**Result**: Work structured, ready to resume after compaction.
 
-bd is primarily for work tracking, but can also serve as queryable database for static reference data (glossaries, terminology) with adaptations.
+---
 
-**For guidance on using bd for reference databases and static data, read:** [references/STATIC_DATA.md](references/STATIC_DATA.md)
+### Example 2: Tracking Blocked Work
 
-## Statistics and Monitoring
+**Scenario**: Agent discovers API is down during implementation
 
-**Check project health:**
+**Agent Actions**:
 ```bash
-bd stats
-bd stats --json
-```
+# Mark current task as blocked
+bd update claude-code-plugins-xyz --status blocked --notes "API endpoint /auth returns 503, reported to backend team"
 
-Returns: total issues, open, in_progress, closed, blocked, ready, avg lead time
+# Create blocker task
+bd create "Fix /auth endpoint 503 error" -p 0 --type bug
+# Returns: claude-code-plugins-blocker
 
-**Find blocked work:**
-```bash
-bd blocked
-bd blocked --json
+# Link dependency (blocker blocks original task)
+bd dep add claude-code-plugins-xyz claude-code-plugins-blocker
+
+# Find other ready work
+bd ready
+# Shows tasks that aren't blocked - agent can switch to those
 ```
 
-Use stats to:
-- Report progress to user
-- Identify bottlenecks
-- Understand project velocity
+**Result**: Blocked work documented, agent productive on other tasks.
 
-## Advanced Features
+---
 
-### Issue Types
+### Example 3: Session Resume After Compaction
 
+**Session 1**:
 ```bash
-bd create "Title" -t task        # Standard work item (default)
-bd create "Title" -t bug         # Defect or problem
-bd create "Title" -t feature     # New functionality
-bd create "Title" -t epic        # Large work with subtasks
-bd create "Title" -t chore       # Maintenance or cleanup
+bd create "Implement user authentication" -p 1
+bd update myproject-auth --status in_progress
+bd update myproject-auth --notes "COMPLETED: JWT library integrated. IN PROGRESS: Testing token refresh. NEXT: Rate limiting"
+# [Conversation compacted - history deleted]
 ```
 
-### Priority Levels
-
+**Session 2** (weeks later):
 ```bash
-bd create "Title" -p 0    # Highest priority (critical)
-bd create "Title" -p 1    # High priority
-bd create "Title" -p 2    # Normal priority (default)
-bd create "Title" -p 3    # Low priority
+bd ready
+# Shows: myproject-auth [P1] [task] in_progress
+
+bd show myproject-auth
+# Full context preserved:
+#   - Title: Implement user authentication
+#   - Status: in_progress
+#   - Notes: "COMPLETED: JWT library integrated. IN PROGRESS: Testing token refresh. NEXT: Rate limiting"
+#   - No conversation history needed!
+
+# Agent continues exactly where it left off
+bd update myproject-auth --notes "COMPLETED: Token refresh working. IN PROGRESS: Rate limiting implementation"
 ```
 
-### Bulk Operations
+**Result**: Zero context loss despite compaction.
+
+---
+
+### Example 4: Complex Dependencies (3-Level Graph)
+
+**Scenario**: Build feature with prerequisites
 
 ```bash
-# Close multiple issues at once
-bd close issue-1 issue-2 issue-3 --reason "Completed in sprint 5"
+# Create tasks
+bd create "Deploy to production" -p 0
+# Returns: deploy-prod
+
+bd create "Run integration tests" -p 1
+# Returns: integration-tests
+
+bd create "Fix failing unit tests" -p 1
+# Returns: fix-tests
 
-# Create multiple issues from markdown file
-bd create --file issues.md
+# Create dependency chain
+bd dep add deploy-prod integration-tests      # Integration blocks deploy
+bd dep add integration-tests fix-tests        # Fixes block integration
+
+# Check what's ready
+bd ready
+# Shows: fix-tests (no blockers)
+# Hides: integration-tests (blocked by fix-tests)
+# Hides: deploy-prod (blocked by integration-tests)
+
+# Work on ready task
+bd update fix-tests --status in_progress
+# ... fix tests ...
+bd close fix-tests --reason "All unit tests passing"
+
+# Check ready again
+bd ready
+# Shows: integration-tests (now unblocked!)
+# Still hides: deploy-prod (still blocked)
 ```
 
-### Dependency Visualization
+**Result**: Dependency chain enforces correct order automatically.
 
+---
+
+### Example 5: Team Collaboration (Git Sync)
+
+**Alice's Session**:
 ```bash
-# Show full dependency tree for an issue
-bd dep tree issue-123
+bd create "Refactor database layer" -p 1
+bd update db-refactor --status in_progress
+bd update db-refactor --notes "Started: Migrating to Prisma ORM"
 
-# Check for circular dependencies
-bd dep cycles
+# End of day - sync to git
+bd sync
+# Commits tasks to git, pushes to remote
 ```
 
-### Built-in Help
-
+**Bob's Session** (next day):
 ```bash
-# Quick start guide (comprehensive built-in reference)
-bd quickstart
+# Start of day - sync from git
+bd sync
+# Pulls latest tasks from remote
+
+bd ready
+# Shows: db-refactor [P1] [in_progress] (assigned to alice)
 
-# Command-specific help
-bd create --help
-bd dep --help
+# Bob checks status
+bd show db-refactor
+# Sees Alice's notes: "Started: Migrating to Prisma ORM"
+
+# Bob works on different task (no conflicts)
+bd create "Add API rate limiting" -p 2
+bd update rate-limit --status in_progress
+
+# End of day
+bd sync
+# Both Alice's and Bob's tasks synchronized
 ```
 
-## JSON Output
+**Result**: Distributed team coordination through git.
+
+---
+
+## Resources
 
-All bd commands support `--json` flag for structured output:
+### When to Use bd vs TodoWrite (Decision Tree)
+
+**Use bd when**:
+- ✅ Work spans multiple sessions or days
+- ✅ Tasks have dependencies or blockers
+- ✅ Need to survive conversation compaction
+- ✅ Exploratory/research work with fuzzy boundaries
+- ✅ Collaboration with team (git sync)
+
+**Use TodoWrite when**:
+- ✅ Single-session linear tasks
+- ✅ Simple checklist for immediate work
+- ✅ All context is in current conversation
+- ✅ Will complete within current session
+
+**Decision Rule**: If resuming in 2 weeks would be hard without bd, use bd.
+
+---
 
+### Essential Commands Quick Reference
+
+Top 10 most-used commands:
+
+| Command | Purpose |
+|---------|---------|
+| `bd ready` | Show tasks ready to work on |
+| `bd create "Title" -p 1` | Create new task |
+| `bd show <id>` | View task details |
+| `bd update <id> --status in_progress` | Start working |
+| `bd update <id> --notes "Progress"` | Add progress notes |
+| `bd close <id> --reason "Done"` | Complete task |
+| `bd dep add <child> <parent>` | Add dependency |
+| `bd list` | See all tasks |
+| `bd search <query>` | Find tasks by keyword |
+| `bd sync` | Sync with git remote |
+
+---
+
+### Session Start Protocol (Every Session)
+
+1. **Run** `bd ready` first
+2. **Pick** highest priority ready task
+3. **Run** `bd show <id>` to get full context
+4. **Update** status to `in_progress`
+5. **Add notes** as you work (critical for compaction survival)
+
+---
+
+### Database Selection
+
+bd uses `.beads/` directory by default.
+
+**Alternate Database**:
 ```bash
-bd ready --json
-bd show issue-123 --json
-bd list --status open --json
-bd stats --json
+export BEADS_DIR=/path/to/alternate/beads
+bd ready  # Uses alternate database
 ```
 
-Use JSON output when you need to parse results programmatically or extract specific fields.
+**Multiple Databases**: Use `BEADS_DIR` to switch between projects.
+
+---
+
+### Advanced Features
 
-## Troubleshooting
+For complex scenarios, see references:
 
-**If bd command not found:**
-- Check installation: `bd version`
-- Verify PATH includes bd binary location
+- **Compaction Strategies**: `{baseDir}/references/ADVANCED_WORKFLOWS.md`
+  - Tier 1/2/ultra compaction for old closed issues
+  - Semantic summarization to reduce database size
 
-**If issues seem lost:**
-- Use `bd list` to see all issues
-- Filter by status: `bd list --status closed`
-- Closed issues remain in database permanently
+- **Epic Management**: `{baseDir}/references/ADVANCED_WORKFLOWS.md`
+  - Nested epics (epics containing epics)
+  - Bulk operations on epic children
 
-**If bd show can't find issue by name:**
-- `bd show` requires issue IDs, not issue titles
-- Workaround: `bd list | grep -i "search term"` to find ID first
-- Then: `bd show issue-id` with the discovered ID
-- For glossaries/reference databases where names matter more than IDs, consider using markdown format alongside the database
+- **Template System**: `{baseDir}/references/ADVANCED_WORKFLOWS.md`
+  - Custom issue templates
+  - Template variables and defaults
 
-**If dependencies seem wrong:**
-- Use `bd show issue-id` to see full dependency tree
-- Use `bd dep tree issue-id` for visualization
-- Dependencies are directional: `bd dep add from-id to-id` means from-id blocks to-id
-- See [references/DEPENDENCIES.md](references/DEPENDENCIES.md#common-mistakes)
+- **Git Integration**: `{baseDir}/references/GIT_INTEGRATION.md`
+  - Merge conflict resolution
+  - Daemon architecture
+  - Branching strategies
 
-**If database seems out of sync:**
-- bd auto-syncs JSONL after each operation (5s debounce)
-- bd auto-imports JSONL when newer than DB (after git pull)
-- Manual operations: `bd export`, `bd import`
+- **Team Collaboration**: `{baseDir}/references/TEAM_COLLABORATION.md`
+  - Multi-user workflows
+  - Worktree support
+  - Prefix strategies
 
-## Reference Files
+---
+
+### Full Documentation
+
+Complete reference: https://github.com/steveyegge/beads
 
-Detailed information organized by topic:
+Existing detailed guides:
+- `{baseDir}/references/CLI_REFERENCE.md` - Complete command syntax
+- `{baseDir}/references/WORKFLOWS.md` - Detailed workflow patterns
+- `{baseDir}/references/DEPENDENCIES.md` - Dependency system deep dive
+- `{baseDir}/references/RESUMABILITY.md` - Compaction survival guide
+- `{baseDir}/references/BOUNDARIES.md` - bd vs TodoWrite detailed comparison
+- `{baseDir}/references/STATIC_DATA.md` - Database schema reference
+
+---
 
-| Reference | Read When |
-|-----------|-----------|
-| [references/BOUNDARIES.md](references/BOUNDARIES.md) | Need detailed decision criteria for bd vs TodoWrite, or integration patterns |
-| [references/CLI_REFERENCE.md](references/CLI_REFERENCE.md) | Need complete command reference, flag details, or examples |
-| [references/WORKFLOWS.md](references/WORKFLOWS.md) | Need step-by-step workflows with checklists for common scenarios |
-| [references/DEPENDENCIES.md](references/DEPENDENCIES.md) | Need deep understanding of dependency types or relationship patterns |
-| [references/ISSUE_CREATION.md](references/ISSUE_CREATION.md) | Need guidance on when to ask vs create issues, issue quality, or design vs acceptance criteria |
-| [references/STATIC_DATA.md](references/STATIC_DATA.md) | Want to use bd for reference databases, glossaries, or static data instead of work tracking |
+**Progressive Disclosure**: This skill provides essential instructions for all 30 beads commands. For advanced topics (compaction, templates, team workflows), see the references directory. Slash commands (`/bd-create`, `/bd-ready`, etc.) remain available as explicit fallback for power users.
PATCH

echo "Gold patch applied."
