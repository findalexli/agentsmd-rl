#!/bin/bash
set -euo pipefail

# Check if fix is already applied
if grep -q "setInputPartMaxHeightOverride" /workspace/vscode/src/vs/workbench/contrib/welcomeAgentSessions/browser/agentSessionsWelcome.ts 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

# Apply the gold patch to fix welcome page chat input collapsing
git apply - <<'PATCH'
diff --git a/src/vs/workbench/contrib/welcomeAgentSessions/browser/agentSessionsWelcome.ts b/src/vs/workbench/contrib/welcomeAgentSessions/browser/agentSessionsWelcome.ts
index 0f10d3f8f27b9..0e3e5ccdeb569 100644
--- a/src/vs/workbench/contrib/welcomeAgentSessions/browser/agentSessionsWelcome.ts
+++ b/src/vs/workbench/contrib/welcomeAgentSessions/browser/agentSessionsWelcome.ts
@@ -65,6 +65,11 @@ const configurationKey = 'workbench.startupEditor';
 const MAX_SESSIONS = 6;
 const MAX_REPO_PICKS = 10;
 const MAX_WALKTHROUGHS = 10;
+const WELCOME_CHAT_INPUT_LAYOUT_HEIGHT = 150;
+const WELCOME_CHAT_INPUT_RESERVED_LIST_HEIGHT = 50;
+const WELCOME_CHAT_INPUT_RESERVED_CHROME_HEIGHT = 72;
+// Mirror ChatWidget's compact-surface sizing so the hidden list reservation and input chrome do not collapse the editor.
+const WELCOME_CHAT_INPUT_MAX_HEIGHT_OVERRIDE = WELCOME_CHAT_INPUT_LAYOUT_HEIGHT + WELCOME_CHAT_INPUT_RESERVED_LIST_HEIGHT + WELCOME_CHAT_INPUT_RESERVED_CHROME_HEIGHT;

 /**
  * - visibleDurationMs: Do they close it right away or leave it open (#3)
@@ -804,9 +809,8 @@ export class AgentSessionsWelcomePage extends EditorPane {
		}

		const chatWidth = Math.min(800, this.lastDimension.width - 80);
-		// Use a reasonable height for the input part - the CSS will hide the list area
-		const inputHeight = 150;
-		this.chatWidget.layout(inputHeight, chatWidth);
+		this.chatWidget.setInputPartMaxHeightOverride(WELCOME_CHAT_INPUT_MAX_HEIGHT_OVERRIDE);
+		this.chatWidget.layout(WELCOME_CHAT_INPUT_LAYOUT_HEIGHT, chatWidth);
	}

	private layoutSessionsControl(): void {
PATCH

echo "Fix applied successfully."
