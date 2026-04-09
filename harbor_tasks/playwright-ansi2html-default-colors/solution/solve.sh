#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'const ansiColours = {' packages/trace-viewer/src/ui/consoleTab.tsx 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/trace-viewer/src/ui/consoleTab.tsx b/packages/trace-viewer/src/ui/consoleTab.tsx
index 1b88a15b956d5..3e35af381a21d 100644
--- a/packages/trace-viewer/src/ui/consoleTab.tsx
+++ b/packages/trace-viewer/src/ui/consoleTab.tsx
@@ -47,6 +47,17 @@ type ConsoleTabModel = {

 const ConsoleListView = ListView<ConsoleEntry>;

+const ansiColours = {
+  log: {
+    bg: 'var(--vscode-editor-background)', fg: 'var(--vscode-editor-foreground)'
+  },
+  warning: {
+    fg: 'var(--vscode-list-warningForeground)', bg: 'var(--vscode-inputValidation-warningBackground)'
+  },
+  error: {
+    fg: 'var(--vscode-list-errorForeground)', bg: 'var(--vscode-inputValidation-errorBackground)'
+  }
+};

 export function useConsoleTabModel(model: TraceModel | undefined, selectedTime: Boundaries | undefined): ConsoleTabModel {
   const { entries } = React.useMemo(() => {
@@ -76,7 +87,8 @@ export function useConsoleTabModel(model: TraceModel | undefined, selectedTime:
     });
     for (const event of logEvents) {
       if (event.type === 'console') {
-        const body = event.args && event.args.length ? format(event.args) : formatAnsi(event.text);
+        const colours = event.messageType === 'error' ? ansiColours.error : event.messageType === 'warning' ? ansiColours.warning : ansiColours.log;
+        const body = event.args && event.args.length ? format(event.args, colours) : formatAnsi(event.text, colours);
         const url = event.location.url;
         const filename = url ? url.substring(url.lastIndexOf('/') + 1) : '<anonymous>';
         const location = `${filename}:${event.location.lineNumber}`;
@@ -102,10 +114,11 @@ export function useConsoleTabModel(model: TraceModel | undefined, selectedTime:
       }
       if (event.type === 'stderr' || event.type === 'stdout') {
         let html = '';
+        const colours = event.type === 'stderr' ? ansiColours.error : ansiColours.log;
         if (event.text)
-          html = ansi2html(event.text.trim()) || '';
+          html = ansi2html(event.text.trim(), colours) || '';
         if (event.base64)
-          html = ansi2html(atob(event.base64).trim()) || '';
+          html = ansi2html(atob(event.base64).trim(), colours) || '';

         addEntry({
           nodeMessage: { html },
@@ -188,9 +201,9 @@ export const ConsoleTab: React.FunctionComponent<{
   </div>;
 };

-function format(args: { preview: string, value: any }[]): React.JSX.Element[] {
+function format(args: { preview: string, value: any }[], colours: { fg: string, bg: string }): React.JSX.Element[] {
   if (args.length === 1)
-    return formatAnsi(args[0].preview);
+    return formatAnsi(args[0].preview, colours);

   const hasMessageFormat = typeof args[0].value === 'string' && args[0].value.includes('%');
   const messageFormat = hasMessageFormat ? args[0].value as string : '';
@@ -237,9 +250,9 @@ function format(args: { preview: string, value: any }[]): React.JSX.Element[] {
   return formatted;
 }

-function formatAnsi(text: string): React.JSX.Element[] {
+function formatAnsi(text: string, colours: { fg: string, bg: string }): React.JSX.Element[] {
   // eslint-disable-next-line react/jsx-key
-  return [<span dangerouslySetInnerHTML={{ __html: ansi2html(text.trim()) }}></span>];
+  return [<span dangerouslySetInnerHTML={{ __html: ansi2html(text.trim(), colours) }}></span>];
 }

 function parseCSSStyle(cssFormat: string): Record<string, string | number> {
diff --git a/packages/web/src/ansi2html.ts b/packages/web/src/ansi2html.ts
index 827e081ae3922..3f684bcc53654 100644
--- a/packages/web/src/ansi2html.ts
+++ b/packages/web/src/ansi2html.ts
@@ -14,7 +14,7 @@
   limitations under the License.
 */

-export function ansi2html(text: string, defaultColors?: { bg: string, fg: string }): string {
+export function ansi2html(text: string, defaultColors: { bg: string, fg: string }): string {
   const regex = /(\x1b\[(\d+(;\d+)*)m)|([^\x1b]+)/g;
   const tokens: string[] = [];
   let match;
@@ -109,9 +109,8 @@ export function ansi2html(text: string, defaultColors?: { bg: string, fg: string
       const color = reverse ? bg : fg;
       if (color !== undefined)
         styleCopy['color'] = color;
-      const backgroundColor = reverse ? fg : bg;
-      if (backgroundColor !== undefined)
-        styleCopy['background-color'] = backgroundColor;
+      if (reverse && fg)
+        styleCopy['background-color'] = fg;
       tokens.push(`<span style="${styleBody(styleCopy)}">${escapeHTML(text)}</span>`);
     }
   }
diff --git a/packages/web/src/components/codeMirrorWrapper.tsx b/packages/web/src/components/codeMirrorWrapper.tsx
index 0a8246e1762f0..385a42b60316f 100644
--- a/packages/web/src/components/codeMirrorWrapper.tsx
+++ b/packages/web/src/components/codeMirrorWrapper.tsx
@@ -170,7 +170,7 @@ export const CodeMirrorWrapper: React.FC<SourceProps> = ({

         if (h.type === 'error') {
           const errorWidgetElement = document.createElement('div');
-          errorWidgetElement.innerHTML = ansi2html(h.message || '');
+          errorWidgetElement.innerHTML = ansi2html(h.message || '', { bg: 'var(--vscode-inputValidation-errorBackground)', fg: 'var(--vscode-editor-foreground)' });
           errorWidgetElement.className = 'source-line-error-widget';
           widgets.push(codemirror.addLineWidget(h.line, errorWidgetElement, { above: true, coverGutter: false }));
         }
diff --git a/packages/web/src/components/errorMessage.tsx b/packages/web/src/components/errorMessage.tsx
index a37f28e2ec2dd..907e9b7ea510e 100644
--- a/packages/web/src/components/errorMessage.tsx
+++ b/packages/web/src/components/errorMessage.tsx
@@ -21,6 +21,6 @@ import './errorMessage.css';
 export const ErrorMessage: React.FC<{
   error: string;
 }> = ({ error }) => {
-  const html = React.useMemo(() => ansi2html(error), [error]);
+  const html = React.useMemo(() => ansi2html(error, { bg: 'var(--vscode-editor-background)', fg: 'var(--vscode-editor-foreground)' }), [error]);
   return <div className='error-message' dangerouslySetInnerHTML={{ __html: html || '' }}></div>;
 };

PATCH

echo "Patch applied successfully."
