#!/bin/bash
set -euo pipefail

cd /workspace/vscode

# Check if patch is already applied (idempotency check)
if grep -q "requestUnsandboxedExecutionReason" src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/runInTerminalToolTelemetry.ts 2>/dev/null; then
	echo "Patch already applied, skipping"
	exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/runInTerminalToolTelemetry.ts b/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/runInTerminalToolTelemetry.ts
index 2267111467ea5..de7e5fbc2b80e 100644
--- a/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/runInTerminalToolTelemetry.ts
+++ b/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/runInTerminalToolTelemetry.ts
@@ -95,6 +95,7 @@ export class RunInTerminalToolTelemetry {
 		isBackground: boolean;
 		isNewSession: boolean;
 		isSandboxWrapped: boolean;
+		requestUnsandboxedExecutionReason: string | undefined;
 		shellIntegrationQuality: ShellIntegrationQuality;
 		outputLineCount: number;
 		timingConnectMs: number;
@@ -124,6 +125,7 @@ export class RunInTerminalToolTelemetry {
 			isBackground: 0 | 1;
 			isNewSession: 0 | 1;
 			isSandbox: 0 | 1;
+			requestUnsandboxedExecutionReason: string | undefined;
 			outputLineCount: number;
 			nonZeroExitCode: -1 | 0 | 1;
 			timingConnectMs: number;
@@ -154,6 +156,7 @@ export class RunInTerminalToolTelemetry {
 			isBackground: { classification: 'SystemMetaData'; purpose: 'FeatureInsight'; isMeasurement: true; comment: 'Whether the command is a background command' };
 			isNewSession: { classification: 'SystemMetaData'; purpose: 'FeatureInsight'; isMeasurement: true; comment: 'Whether this was the first execution for the terminal session' };
 			isSandbox: { classification: 'SystemMetaData'; purpose: 'FeatureInsight'; isMeasurement: true; comment: 'Whether the command was run inside the terminal sandbox' };
+			requestUnsandboxedExecutionReason: { classification: 'SystemMetaData'; purpose: 'FeatureInsight'; comment: 'The reason the model gave for requesting unsandboxed execution, if any' };
 			outputLineCount: { classification: 'SystemMetaData'; purpose: 'FeatureInsight'; isMeasurement: true; comment: 'How many lines of output were produced, this is -1 when isBackground is true or if there\'s an error' };
 			nonZeroExitCode: { classification: 'SystemMetaData'; purpose: 'FeatureInsight'; isMeasurement: true; comment: 'Whether the command exited with a non-zero code (-1=error/unknown, 0=zero exit code, 1=non-zero)' };
 			timingConnectMs: { classification: 'SystemMetaData'; purpose: 'FeatureInsight'; isMeasurement: true; comment: 'How long the terminal took to start up and connect to' };
@@ -181,6 +184,7 @@ export class RunInTerminalToolTelemetry {
 			isBackground: state.isBackground ? 1 : 0,
 			isNewSession: state.isNewSession ? 1 : 0,
 			isSandbox: state.isSandboxWrapped ? 1 : 0,
+			requestUnsandboxedExecutionReason: state.requestUnsandboxedExecutionReason,
 			outputLineCount: state.outputLineCount,
 			nonZeroExitCode: state.exitCode === undefined ? -1 : state.exitCode === 0 ? 0 : 1,
 			timingConnectMs: state.timingConnectMs,
diff --git a/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts b/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts
index a1bc09bf2e66b..3bbd00f5a3f29 100644
--- a/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts
+++ b/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts
@@ -1290,6 +1290,7 @@ export class RunInTerminalTool extends Disposable implements IToolImpl {
 				didToolEditCommand,
 				isBackground: args.isBackground,
 				isSandboxWrapped: toolSpecificData.commandLine.isSandboxWrapped === true,
+				requestUnsandboxedExecutionReason: args.requestUnsandboxedExecutionReason,
 				shellIntegrationQuality: toolTerminal.shellIntegrationQuality,
 				error,
 				isNewSession,
PATCH

echo "Patch applied successfully"
