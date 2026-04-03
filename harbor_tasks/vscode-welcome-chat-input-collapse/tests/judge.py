#!/usr/bin/env python3
"""
LLM Rubric Judge for VS Code Welcome Chat Input Collapse Fix

Evaluates style and code quality aspects not easily checked programmatically.
"""

import os
import json
import anthropic

PR_DETAILS = """
PR: microsoft/vscode#306454
Title: sessions: fix welcome page chat input collapsing on first keystroke

Problem: Typing in the Agent Sessions welcome page chat input causes the box to
collapse so text is not visible. The editor shrinks from ~44px to ~22px after
the first keystroke.

Root Cause: ChatWidget.layout() reserves MIN_LIST_HEIGHT (50px) for the chat
list even when the welcome page hides it via CSS. With a layout height of 150px,
only 100px remained for the input part. After subtracting input chrome (~128px),
_effectiveInputEditorMaxHeight dropped to 0, collapsing the editor.

Fix: Call setInputPartMaxHeightOverride(272) before layout() so the input part
has enough height budget independent of the artificially small layout height.
"""

RUBRIC = """
Rubric for LLM Judge:

1. Code Quality (0.05):
   - Constants are meaningfully named (WELCOME_CHAT_INPUT_*)
   - The calculation logic is clear and documented
   - The comment explains WHY not just WHAT

2. Correctness Pattern (0.05):
   - Follows the same pattern as other compact chat surfaces
   - setInputPartMaxHeightOverride is called before layout()
   - The override value accounts for layout height + list reservation + chrome
"""

SOURCE_FILE = "/workspace/vscode/src/vs/workbench/contrib/welcomeAgentSessions/browser/agentSessionsWelcome.ts"


def read_source():
    """Read the relevant portion of the source file."""
    try:
        with open(SOURCE_FILE, 'r') as f:
            content = f.read()

        # Find the constants and layout method
        lines = content.split('\n')
        relevant = []
        in_relevant = False

        for line in lines:
            # Start at constants
            if 'WELCOME_CHAT_INPUT_LAYOUT_HEIGHT' in line:
                in_relevant = True
            if in_relevant:
                relevant.append(line)
            # End after layout call
            if 'this.chatWidget.layout(' in line:
                relevant.append(line)
                break

        return '\n'.join(relevant)
    except Exception as e:
        return f"Error reading file: {e}"


def main():
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        print(json.dumps({"score": 0.0, "reason": "No API key"}))
        return

    source = read_source()

    prompt = f"""
You are evaluating a code fix for a VS Code bug. Here is the context:

{PR_DETAILS}

Here is the relevant source code that was added/modified:

```typescript
{source}
```

{RUBRIC}

Score the code on each rubric item from 0.0 to 1.0. Return ONLY a JSON object:
{{
  "code_quality": 0.0-1.0,
  "correctness_pattern": 0.0-1.0,
  "total": 0.0-1.0,
  "explanation": "brief reasoning"
}}
"""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.content[0].text
        # Extract JSON
        json_start = result.find('{')
        json_end = result.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            score_data = json.loads(result[json_start:json_end])
            total = score_data.get('total', 0.0)
            print(json.dumps(score_data))
        else:
            print(json.dumps({"score": 0.0, "reason": "Could not parse response"}))
    except Exception as e:
        print(json.dumps({"score": 0.0, "reason": str(e)}))


if __name__ == '__main__':
    main()
