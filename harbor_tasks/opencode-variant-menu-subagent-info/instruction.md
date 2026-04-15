# Subagent navigation and display issues in TUI

## Problem

Several usability issues exist in the TUI's subagent and session workflows:

### 1. Session cycling direction is inverted

When navigating through sessions, the cycling direction is reversed — the "next" action selects the session that the "previous" action should select, and vice versa. The cycling logic computes the next index by combining the current index with a direction value, but the arithmetic sign is wrong. After the fix, advancing with direction=1 must decrease the index by 1 (wrapping from 0 to the last index), and retreating with direction=-1 must increase the index by 1 (wrapping from the last index to 0). For example, at index 2 in a list of 5, direction=1 should produce index 1; at index 0, direction=1 should wrap to index 4.

### 2. Subagent footer lacks type and index information

The subagent footer currently displays only a static "Subagent session" label. It should instead show dynamic information:

- The **agent type** extracted from the session title using a regular expression. Subagent session titles encode the agent type with the format `@typename subagent` — the `@` followed by a word and then the word "subagent". For example:
  - `@coder subagent session #3` → agent type is "coder"
  - `@explorer subagent` → agent type is "explorer"
  - `@writer subagent task` → agent type is "writer"
  - `@planner subagent review` → agent type is "planner"
  - `plain session title` → no agent type (use a generic fallback)

  The regex should capture the typename from the first matching group. The extracted type must be **capitalized using title case** (e.g., "Coder", "Explorer") for display. When no matching pattern is found, fall back to a generic label.

- The **position** of this subagent among its siblings, displayed as "X of Y" using 1-based indexing. Sibling subagents are sessions that share the same parent session. To compute this, filter sessions by matching the parent, sort by creation time, and find the current session's index among them, then add 1 for 1-based display.

The new code must use functional array methods (filter, findIndex, etc.) rather than imperative for-loops, and must not contain try/catch blocks, per the project's AGENTS.md conventions.

### 3. Task descriptions lack subagent type context

Task items currently display using a plain `Task {description}` format with no indication of which subagent type spawned the task. They should instead include the subagent type as a **capitalized** prefix before the description, with a fallback for when no subagent type is available (e.g., a generic default like "General"). The subagent type and description must be combined in the same content expression — the old plain `Task ${description}` template is no longer sufficient. Use a nullish coalescing operator (`??`) or logical OR (`||`) to provide the fallback value when the subagent type is missing or empty.

### 4. Dead code cleanup

Remove any unreferenced function definitions from the modified code — functions that are defined but never called anywhere in the codebase.

## Expected behavior

1. Navigating through sessions cycles in the correct direction (direction=1 decreases index, direction=-1 increases index, wrapping at boundaries)
2. The subagent footer displays the titlecased agent type extracted via regex from the session title, and position among siblings (e.g., "Coder (2 of 5)")
3. Task descriptions show a capitalized subagent type prefix with a fallback for missing types
4. No dead code (unreferenced functions) remains in the modified files
5. All changes follow the project's AGENTS.md coding conventions
