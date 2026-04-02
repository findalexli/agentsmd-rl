#!/bin/bash
set -euo pipefail

# Check if already applied - look for the new file
if [ -f "src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/commandLineRewriter/commandLineBackgroundDetachRewriter.ts" ]; then
    echo "Patch already applied, skipping"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/commandLineRewriter/commandLineBackgroundDetachRewriter.ts b/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/commandLineRewriter/commandLineBackgroundDetachRewriter.ts
new file mode 100644
index 0000000000000..2687bc137ab09
--- /dev/null
+++ b/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/commandLineRewriter/commandLineBackgroundDetachRewriter.ts
@@ -0,0 +1,70 @@
+/*---------------------------------------------------------------------------------------------
+ *  Copyright (c) Microsoft Corporation. All rights reserved.
+ *  Licensed under the MIT License. See License.txt in the project root for license information.
+ *--------------------------------------------------------------------------------------------*/
+
+import { Disposable } from '../../../../../../../base/common/lifecycle.js';
+import { OperatingSystem } from '../../../../../../../base/common/platform.js';
+import { IConfigurationService } from '../../../../../../../platform/configuration/common/configuration.js';
+import { TerminalChatAgentToolsSettingId } from '../../../common/terminalChatAgentToolsConfiguration.js';
+import { isPowerShell } from '../../runInTerminalHelpers.js';
+import type { ICommandLineRewriter, ICommandLineRewriterOptions, ICommandLineRewriterResult } from './commandLineRewriter.js';
+
+/**
+ * Wraps background terminal commands so their processes survive VS Code shutdown.
+ *
+ * On POSIX (bash/zsh/fish), uses `nohup <command> &` to ignore SIGHUP and
+ * detach from the terminal's process group.
+ *
+ * On Windows (PowerShell), uses `Start-Process` to create a process outside
+ * the terminal's process tree.
+ *
+ * Gated behind the {@link TerminalChatAgentToolsSettingId.DetachBackgroundProcesses} setting
+ * (default off) to avoid orphaned processes in normal usage.
+ */
+export class CommandLineBackgroundDetachRewriter extends Disposable implements ICommandLineRewriter {
+	constructor(
+		@IConfigurationService private readonly _configurationService: IConfigurationService,
+	) {
+		super();
+	}
+
+	rewrite(options: ICommandLineRewriterOptions): ICommandLineRewriterResult | undefined {
+		if (!options.isBackground) {
+			return undefined;
+		}
+
+		if (!this._configurationService.getValue(TerminalChatAgentToolsSettingId.DetachBackgroundProcesses)) {
+			return undefined;
+		}
+
+		if (options.os === OperatingSystem.Windows) {
+			return this._rewriteForPowerShell(options);
+		}
+
+		return this._rewriteForPosix(options);
+	}
+
+	private _rewriteForPosix(options: ICommandLineRewriterOptions): ICommandLineRewriterResult {
+		return {
+			rewritten: `nohup ${options.commandLine} &`,
+			reasoning: 'Wrapped background command with nohup to survive terminal shutdown',
+			forDisplay: options.commandLine,
+		};
+	}
+
+	private _rewriteForPowerShell(options: ICommandLineRewriterOptions): ICommandLineRewriterResult | undefined {
+		if (!isPowerShell(options.shell, options.os)) {
+			return undefined;
+		}
+
+		// Escape double quotes for PowerShell string
+		const escapedCommand = options.commandLine.replace(/"/g, '\\"');
+
+		return {
+			rewritten: `Start-Process -WindowStyle Hidden -FilePath "${options.shell}" -ArgumentList "-NoProfile", "-Command", "${escapedCommand}"`,
+			reasoning: 'Wrapped background command with Start-Process to survive terminal shutdown',
+			forDisplay: options.commandLine,
+		};
+	}
+}
diff --git a/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/commandLineRewriter/commandLineRewriter.ts b/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/commandLineRewriter/commandLineRewriter.ts
index fd91cf08e4314..9eb0f4c8a30e3 100644
--- a/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/commandLineRewriter/commandLineRewriter.ts
+++ b/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/commandLineRewriter/commandLineRewriter.ts
@@ -17,6 +17,7 @@ export interface ICommandLineRewriterOptions {
 	cwd: URI | undefined;
 	shell: string;
 	os: OperatingSystem;
+	isBackground?: boolean;
 	requestUnsandboxedExecution?: boolean;
 }

diff --git a/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts b/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts
index dda5992a57624..7e68d2f9753fa 100644
--- a/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts
+++ b/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts
@@ -60,6 +60,7 @@ import type { ICommandLineRewriter } from './commandLineRewriter/commandLineRewr
 import { CommandLineCdPrefixRewriter } from './commandLineRewriter/commandLineCdPrefixRewriter.js';
 import { CommandLinePreventHistoryRewriter } from './commandLineRewriter/commandLinePreventHistoryRewriter.js';
 import { CommandLinePwshChainOperatorRewriter } from './commandLineRewriter/commandLinePwshChainOperatorRewriter.js';
+import { CommandLineBackgroundDetachRewriter } from './commandLineRewriter/commandLineBackgroundDetachRewriter.js';
 import { CommandLineSandboxRewriter } from './commandLineRewriter/commandLineSandboxRewriter.js';
 import { IWorkspaceContextService } from '../../../../../../platform/workspace/common/workspace.js';
 import { IHistoryService } from '../../../../../services/history/common/history.js';
@@ -476,6 +477,10 @@ export class RunInTerminalTool extends Disposable implements IToolImpl {
 		if (this._enableCommandLineSandboxRewriting) {
 			this._commandLineRewriters.push(this._register(this._instantiationService.createInstance(CommandLineSandboxRewriter)));
 		}
+		// BackgroundDetachRewriter must come after SandboxRewriter so that nohup/Start-Process
+		// wraps the entire sandbox runtime, keeping both the sandbox and the child process alive
+		// through VS Code shutdown.
+		this._commandLineRewriters.push(this._register(this._instantiationService.createInstance(CommandLineBackgroundDetachRewriter)));
 		// PreventHistoryRewriter must be last so the leading space is applied to the final
 		// command, including any sandbox wrapping.
 		this._commandLineRewriters.push(this._register(this._instantiationService.createInstance(CommandLinePreventHistoryRewriter)));
@@ -584,6 +589,7 @@ export class RunInTerminalTool extends Disposable implements IToolImpl {
 				cwd,
 				shell,
 				os,
+				isBackground: args.isBackground,
 				requestUnsandboxedExecution: requiresUnsandboxConfirmation,
 			});
 			if (rewriteResult) {
diff --git a/src/vs/workbench/contrib/terminalContrib/chatAgentTools/common/terminalChatAgentToolsConfiguration.ts b/src/vs/workbench/contrib/terminalContrib/chatAgentTools/common/terminalChatAgentToolsConfiguration.ts
index a03e262423053..fa5dfda060f7a 100644
--- a/src/vs/workbench/contrib/terminalContrib/chatAgentTools/common/terminalChatAgentToolsConfiguration.ts
+++ b/src/vs/workbench/contrib/terminalContrib/chatAgentTools/common/terminalChatAgentToolsConfiguration.ts
@@ -27,6 +27,7 @@ export const enum TerminalChatAgentToolsSettingId {
 	AgentSandboxMacFileSystem = 'chat.agent.sandboxFileSystem.mac',
 	PreventShellHistory = 'chat.tools.terminal.preventShellHistory',
 	EnforceTimeoutFromModel = 'chat.tools.terminal.enforceTimeoutFromModel',
+	DetachBackgroundProcesses = 'chat.tools.terminal.detachBackgroundProcesses',
 	IdlePollInterval = 'chat.tools.terminal.idlePollInterval',

 	TerminalProfileLinux = 'chat.tools.terminal.terminalProfile.linux',
@@ -636,6 +637,14 @@ export const terminalChatAgentToolsConfiguration: IStringDictionary<IConfigurat
 			mode: 'auto'
 		},
 		markdownDescription: localize('enforceTimeoutFromModel.description', "Whether to enforce the timeout value provided by the model in the run in terminal tool. When enabled, if the model provides a timeout parameter, the tool will stop tracking the command after that duration and return the output collected so far."),
+	},
+	[TerminalChatAgentToolsSettingId.DetachBackgroundProcesses]: {
+		included: false,
+		restricted: true,
+		type: 'boolean',
+		default: false,
+		tags: ['experimental'],
+		markdownDescription: localize('detachBackgroundProcesses.description', "Whether to detach background terminal processes so they survive when VS Code exits. When enabled, commands started with `isBackground: true` are wrapped with `nohup` (POSIX) or `Start-Process` (Windows) so the process continues running after the terminal is disposed."),
 	}
 };

diff --git a/src/vs/workbench/contrib/terminalContrib/chatAgentTools/test/electron-browser/commandLineBackgroundDetachRewriter.test.ts b/src/vs/workbench/contrib/terminalContrib/chatAgentTools/test/electron-browser/commandLineBackgroundDetachRewriter.test.ts
new file mode 100644
index 0000000000000..b092b64f33d47
--- /dev/null
+++ b/src/vs/workbench/contrib/terminalContrib/chatAgentTools/test/electron-browser/commandLineBackgroundDetachRewriter.test.ts
@@ -0,0 +1,122 @@
+/*---------------------------------------------------------------------------------------------
+ *  Copyright (c) Microsoft Corporation. All rights reserved.
+ *  Licensed under the MIT License. See License.txt in the project root for license information.
+ *--------------------------------------------------------------------------------------------*/
+
+import { deepStrictEqual, strictEqual } from 'assert';
+import { OperatingSystem } from '../../../../../../base/common/platform.js';
+import { ensureNoDisposablesAreLeakedInTestSuite } from '../../../../../../base/test/common/utils.js';
+import type { TestInstantiationService } from '../../../../../../platform/instantiation/test/common/instantiationServiceMock.js';
+import { TestConfigurationService } from '../../../../../../platform/configuration/test/common/testConfigurationService.js';
+import { workbenchInstantiationService } from '../../../../../test/browser/workbenchTestServices.js';
+import { CommandLineBackgroundDetachRewriter } from '../../browser/tools/commandLineRewriter/commandLineBackgroundDetachRewriter.js';
+import type { ICommandLineRewriterOptions } from '../../browser/tools/commandLineRewriter/commandLineRewriter.js';
+import { TerminalChatAgentToolsSettingId } from '../../common/terminalChatAgentToolsConfiguration.js';
+
+suite('CommandLineBackgroundDetachRewriter', () => {
+	const store = ensureNoDisposablesAreLeakedInTestSuite();
+
+	let instantiationService: TestInstantiationService;
+	let configurationService: TestConfigurationService;
+	let rewriter: CommandLineBackgroundDetachRewriter;
+
+	function createOptions(command: string, shell: string, os: OperatingSystem, isBackground?: boolean): ICommandLineRewriterOptions {
+		return {
+			commandLine: command,
+			cwd: undefined,
+			shell,
+			os,
+			isBackground,
+		};
+	}
+
+	setup(() => {
+		configurationService = new TestConfigurationService();
+		configurationService.setUserConfiguration(TerminalChatAgentToolsSettingId.DetachBackgroundProcesses, true);
+		instantiationService = workbenchInstantiationService({
+			configurationService: () => configurationService
+		}, store);
+		rewriter = store.add(instantiationService.createInstance(CommandLineBackgroundDetachRewriter));
+	});
+
+	test('should return undefined for foreground commands', () => {
+		strictEqual(rewriter.rewrite(createOptions('echo hello', '/bin/bash', OperatingSystem.Linux, false)), undefined);
+	});
+
+	test('should return undefined when isBackground is not set', () => {
+		strictEqual(rewriter.rewrite(createOptions('echo hello', '/bin/bash', OperatingSystem.Linux)), undefined);
+	});
+
+	test('should return undefined when setting is disabled', () => {
+		configurationService.setUserConfiguration(TerminalChatAgentToolsSettingId.DetachBackgroundProcesses, false);
+		strictEqual(rewriter.rewrite(createOptions('python3 app.py', '/bin/bash', OperatingSystem.Linux, true)), undefined);
+	});
+
+	suite('POSIX (bash)', () => {
+		test('should wrap with nohup on Linux', () => {
+			deepStrictEqual(rewriter.rewrite(createOptions('python3 app.py', '/bin/bash', OperatingSystem.Linux, true)), {
+				rewritten: 'nohup python3 app.py &',
+				reasoning: 'Wrapped background command with nohup to survive terminal shutdown',
+				forDisplay: 'python3 app.py',
+			});
+		});
+
+		test('should wrap with nohup on macOS', () => {
+			deepStrictEqual(rewriter.rewrite(createOptions('flask run', '/bin/bash', OperatingSystem.Macintosh, true)), {
+				rewritten: 'nohup flask run &',
+				reasoning: 'Wrapped background command with nohup to survive terminal shutdown',
+				forDisplay: 'flask run',
+			});
+		});
+	});
+
+	suite('POSIX (zsh)', () => {
+		test('should wrap with nohup', () => {
+			deepStrictEqual(rewriter.rewrite(createOptions('node server.js', '/bin/zsh', OperatingSystem.Linux, true)), {
+				rewritten: 'nohup node server.js &',
+				reasoning: 'Wrapped background command with nohup to survive terminal shutdown',
+				forDisplay: 'node server.js',
+			});
+		});
+	});
+
+	suite('POSIX (fish)', () => {
+		test('should wrap with nohup', () => {
+			deepStrictEqual(rewriter.rewrite(createOptions('ruby app.rb', '/usr/bin/fish', OperatingSystem.Linux, true)), {
+				rewritten: 'nohup ruby app.rb &',
+				reasoning: 'Wrapped background command with nohup to survive terminal shutdown',
+				forDisplay: 'ruby app.rb',
+			});
+		});
+	});
+
+	suite('Windows (PowerShell)', () => {
+		test('should wrap with Start-Process for pwsh', () => {
+			deepStrictEqual(rewriter.rewrite(createOptions('python app.py', 'C:\\Program Files\\PowerShell\\7\\pwsh.exe', OperatingSystem.Windows, true)), {
+				rewritten: 'Start-Process -WindowStyle Hidden -FilePath "C:\\Program Files\\PowerShell\\7\\pwsh.exe" -ArgumentList "-NoProfile", "-Command", "python app.py"',
+				reasoning: 'Wrapped background command with Start-Process to survive terminal shutdown',
+				forDisplay: 'python app.py',
+			});
+		});
+
+		test('should wrap with Start-Process for Windows PowerShell', () => {
+			deepStrictEqual(rewriter.rewrite(createOptions('node server.js', 'C:\\WINDOWS\\System32\\WindowsPowerShell\\v1.0\\powershell.exe', OperatingSystem.Windows, true)), {
+				rewritten: 'Start-Process -WindowStyle Hidden -FilePath "C:\\WINDOWS\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -ArgumentList "-NoProfile", "-Command", "node server.js"',
+				reasoning: 'Wrapped background command with Start-Process to survive terminal shutdown',
+				forDisplay: 'node server.js',
+			});
+		});
+
+		test('should escape double quotes in PowerShell commands', () => {
+			deepStrictEqual(rewriter.rewrite(createOptions('echo "hello world"', 'C:\\Program Files\\PowerShell\\7\\pwsh.exe', OperatingSystem.Windows, true)), {
+				rewritten: 'Start-Process -WindowStyle Hidden -FilePath "C:\\Program Files\\PowerShell\\7\\pwsh.exe" -ArgumentList "-NoProfile", "-Command", "echo \\"hello world\\""',
+				reasoning: 'Wrapped background command with Start-Process to survive terminal shutdown',
+				forDisplay: 'echo "hello world"',
+			});
+		});
+
+		test('should return undefined for non-PowerShell Windows shell', () => {
+			strictEqual(rewriter.rewrite(createOptions('echo hello', 'cmd.exe', OperatingSystem.Windows, true)), undefined);
+		});
+	});
+});
PATCH

echo "Patch applied successfully"
