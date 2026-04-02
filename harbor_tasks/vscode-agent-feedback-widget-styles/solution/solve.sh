#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vscode

# Check if patch already applied (check for animation keyframes in CSS)
if grep -q "@keyframes agentFeedbackInputAppear" src/vs/sessions/contrib/agentFeedback/browser/media/agentFeedbackEditorInput.css 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/src/vs/sessions/common/theme.ts b/src/vs/sessions/common/theme.ts
index 2217701d3473b..50f9beac5fe90 100644
--- a/src/vs/sessions/common/theme.ts
+++ b/src/vs/sessions/common/theme.ts
@@ -5,9 +5,9 @@

 import { localize } from '../../nls.js';
 import { getColorRegistry, registerColor, transparent } from '../../platform/theme/common/colorUtils.js';
-import { contrastBorder, iconForeground } from '../../platform/theme/common/colorRegistry.js';
+import { contrastBorder } from '../../platform/theme/common/colorRegistry.js';
+import { editorWidgetBorder, editorBackground } from '../../platform/theme/common/colors/editorColors.js';
 import { buttonBackground } from '../../platform/theme/common/colors/inputColors.js';
-import { editorBackground } from '../../platform/theme/common/colors/editorColors.js';
 import { PANEL_BACKGROUND, SIDE_BAR_BACKGROUND, SIDE_BAR_FOREGROUND } from '../../workbench/common/theme.js';

 // Sessions sidebar background color
@@ -67,7 +67,7 @@ export const chatBarTitleForeground = registerColor(
 // Agent feedback input widget border color
 export const agentFeedbackInputWidgetBorder = registerColor(
 	'agentFeedbackInputWidget.border',
-	{ dark: transparent(iconForeground, 0.8), light: transparent(iconForeground, 0.8), hcDark: contrastBorder, hcLight: contrastBorder },
+	{ dark: editorWidgetBorder, light: editorWidgetBorder, hcDark: contrastBorder, hcLight: contrastBorder },
 	localize('agentFeedbackInputWidget.border', 'Border color of the agent feedback input widget shown in the editor.')
 );

diff --git a/src/vs/sessions/contrib/agentFeedback/browser/agentFeedbackEditorInputContribution.ts b/src/vs/sessions/contrib/agentFeedback/browser/agentFeedbackEditorInputContribution.ts
index ae5fa614c3d75..ed6ccc8912ff2 100644
--- a/src/vs/sessions/contrib/agentFeedback/browser/agentFeedbackEditorInputContribution.ts
+++ b/src/vs/sessions/contrib/agentFeedback/browser/agentFeedbackEditorInputContribution.ts
@@ -95,8 +95,6 @@ class AgentFeedbackInputWidget implements IOverlayWidget {
 			this._updateActionForAlt(status.altKey);
 		});

-		this._editor.applyFontInfo(this._inputElement);
-		this._editor.applyFontInfo(this._measureElement);
 		this._lineHeight = 22;
 		this._inputElement.style.lineHeight = `${this._lineHeight}px`;
 	}
diff --git a/src/vs/sessions/contrib/agentFeedback/browser/agentFeedbackEditorWidgetContribution.ts b/src/vs/sessions/contrib/agentFeedback/browser/agentFeedbackEditorWidgetContribution.ts
index b0206052dc828..7c4c463f39109 100644
--- a/src/vs/sessions/contrib/agentFeedback/browser/agentFeedbackEditorWidgetContribution.ts
+++ b/src/vs/sessions/contrib/agentFeedback/browser/agentFeedbackEditorWidgetContribution.ts
@@ -88,6 +88,11 @@ export class AgentFeedbackEditorWidget extends Disposable implements IOverlayWid
 		// Header
 		this._headerNode = $('div.agent-feedback-widget-header');

+		// Comment icon (decorative, hidden from screen readers)
+		const commentIcon = renderIcon(Codicon.comment);
+		commentIcon.setAttribute('aria-hidden', 'true');
+		this._headerNode.appendChild(commentIcon);
+
 		// Title showing feedback count
 		this._titleNode = $('span.agent-feedback-widget-title');
 		this._updateTitle();
@@ -148,7 +153,7 @@ export class AgentFeedbackEditorWidget extends Disposable implements IOverlayWid
 	private _updateTitle(): void {
 		const count = this._commentItems.length;
 		if (count === 1) {
-			this._titleNode.textContent = nls.localize('oneComment', "1 comment");
+			this._titleNode.textContent = this._commentItems[0].text;
 		} else {
 			this._titleNode.textContent = nls.localize('nComments', "{0} comments", count);
 		}
diff --git a/src/vs/sessions/contrib/agentFeedback/browser/media/agentFeedbackEditorInput.css b/src/vs/sessions/contrib/agentFeedback/browser/media/agentFeedbackEditorInput.css
index b467ff7f7aa8d..82ed568e03679 100644
--- a/src/vs/sessions/contrib/agentFeedback/browser/media/agentFeedbackEditorInput.css
+++ b/src/vs/sessions/contrib/agentFeedback/browser/media/agentFeedbackEditorInput.css
@@ -7,19 +7,38 @@
 	position: absolute;
 	z-index: 10000;
 	background-color: var(--vscode-panel-background);
-	border: 1px solid var(--vscode-agentFeedbackInputWidget-border, var(--vscode-input-border, var(--vscode-widget-border)));
+	border: 1px solid var(--vscode-agentFeedbackInputWidget-border, var(--vscode-editorWidget-border, var(--vscode-contrastBorder)));
 	box-shadow: var(--vscode-shadow-lg);
 	border-radius: 8px;
 	padding: 4px;
 	display: flex;
 	flex-direction: row;
 	align-items: flex-end;
+	animation: agentFeedbackInputAppear 0.15s ease-out;
 }

+@keyframes agentFeedbackInputAppear {
+	from {
+		opacity: 0;
+		transform: translateY(4px);
+	}
+	to {
+		opacity: 1;
+		transform: translateY(0);
+	}
+}
+
+@media (prefers-reduced-motion: reduce) {
+	.agent-feedback-input-widget {
+		animation: none;
+		transform: none;
+	}
+}
 .agent-feedback-input-widget textarea {
 	background-color: var(--vscode-panel-background);
 	border: none;
 	color: var(--vscode-input-foreground);
+	font: inherit;
 	border-radius: 4px;
 	padding: 0 0 0 6px;
 	outline: none;
@@ -49,6 +68,8 @@
 	height: 0;
 	overflow: hidden;
 	white-space: pre;
+	font: inherit;
+	font-size: 13px;
 }

 .agent-feedback-input-widget .agent-feedback-input-actions {
diff --git a/src/vs/sessions/contrib/agentFeedback/browser/media/agentFeedbackEditorWidget.css b/src/vs/sessions/contrib/agentFeedback/browser/media/agentFeedbackEditorWidget.css
index ef551fd08700e..22db201e709f4 100644
--- a/src/vs/sessions/contrib/agentFeedback/browser/media/agentFeedbackEditorWidget.css
+++ b/src/vs/sessions/contrib/agentFeedback/browser/media/agentFeedbackEditorWidget.css
@@ -35,13 +35,14 @@
 /* Arrow pointer pointing left toward the code */
 .agent-feedback-widget-arrow {
 	position: absolute;
-	left: -8px;
-	top: 9px;
+	left: -6px;
+	top: 11px;
 	width: 0;
 	height: 0;
-	border-top: 8px solid transparent;
-	border-bottom: 8px solid transparent;
-	border-right: 8px solid var(--vscode-editorWidget-border, var(--vscode-contrastBorder));
+	border-top: 6px solid transparent;
+	border-bottom: 6px solid transparent;
+	border-right: 6px solid var(--vscode-editorWidget-border, var(--vscode-contrastBorder));
+	display: none;
 }

 .agent-feedback-widget.collapsed .agent-feedback-widget-arrow {
@@ -52,19 +53,19 @@
 	content: '';
 	position: absolute;
 	left: 2px;
-	top: -7px;
+	top: -5px;
 	width: 0;
 	height: 0;
-	border-top: 7px solid transparent;
-	border-bottom: 7px solid transparent;
-	border-right: 7px solid var(--vscode-editorWidget-background);
+	border-top: 5px solid transparent;
+	border-bottom: 5px solid transparent;
+	border-right: 5px solid var(--vscode-editorWidget-background);
 }

 /* Header */
 .agent-feedback-widget-header {
 	display: flex;
 	align-items: center;
-	padding: 8px 10px;
+	padding: 4px 4px 4px 8px;
 	border-bottom: 1px solid var(--vscode-editorWidget-border, var(--vscode-widget-border));
 	border-radius: 8px 8px 0 0;
 	overflow: hidden;
@@ -86,6 +87,9 @@
 	font-weight: 500;
 	color: var(--vscode-foreground);
 	white-space: nowrap;
+	overflow: hidden;
+	text-overflow: ellipsis;
+	min-width: 0;
 }

 /* Spacer to push buttons to the right */
@@ -98,9 +102,9 @@
 	display: flex;
 	align-items: center;
 	justify-content: center;
-	width: 18px;
-	height: 18px;
-	border-radius: 4px;
+	width: 22px;
+	height: 22px;
+	border-radius: var(--vscode-cornerRadius-medium);
 	cursor: pointer;
 	color: var(--vscode-foreground);
 	opacity: 0.7;
@@ -130,7 +134,7 @@
 .agent-feedback-widget-item {
 	display: flex;
 	flex-direction: column;
-	padding: 8px 10px;
+	padding: 4px 4px 8px 8px;
 	border-bottom: 1px solid var(--vscode-editorWidget-border, var(--vscode-widget-border));
 	cursor: pointer;
 	position: relative;
@@ -160,7 +164,7 @@

 .agent-feedback-widget-item-header {
 	display: flex;
-	align-items: flex-start;
+	align-items: center;
 	justify-content: space-between;
 	gap: 8px;
 }
@@ -289,7 +293,7 @@

 /* Inline edit textarea */
 .agent-feedback-widget-text.editing {
-	padding: 0;
+	padding: 0 4px 0 0;
 }

 .agent-feedback-widget-edit-textarea {
@@ -300,6 +304,7 @@
 	border-radius: 4px;
 	background: var(--vscode-input-background);
 	color: var(--vscode-input-foreground);
+	font: inherit;
 	font-size: 12px;
 	line-height: 1.4;
 	resize: none;
PATCH

echo "Patch applied successfully"
