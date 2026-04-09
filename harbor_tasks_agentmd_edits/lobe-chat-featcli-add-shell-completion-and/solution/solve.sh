#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lobe-chat

# Idempotent: skip if already applied
if [ -f "apps/cli/src/commands/completion.ts" ]; then
    echo "Patch already applied (completion.ts exists)."
    exit 0
fi

# Apply the PR patch
git apply - <<'PATCH'
diff --git a/apps/cli/README.md b/apps/cli/README.md
new file mode 100644
index 000000000..2243c402a
--- /dev/null
+++ b/apps/cli/README.md
@@ -0,0 +1,44 @@
+# @lobehub/cli
+
+LobeHub command-line interface.
+
+## Local Development
+
+| Task                                       | Command                    |
+| ------------------------------------------ | -------------------------- |
+| Run in dev mode                            | `bun run dev -- <command>` |
+| Build the CLI                              | `bun run build`            |
+| Link `lh`/`lobe`/`lobehub` into your shell | `bun run cli:link`         |
+| Remove the global link                     | `bun run cli:unlink`       |
+
+- `bun run build` only generates `dist/index.js`.
+- To make `lh` available in your shell, run `bun run cli:link`.
+- After linking, if your shell still cannot find `lh`, run `rehash` in `zsh`.
+
+## Shell Completion
+
+### Install completion for a linked CLI
+
+| Shell  | Command                        |
+| ------ | ------------------------------ |
+| `zsh`  | `source <(lh completion zsh)`  |
+| `bash` | `source <(lh completion bash)` |
+
+### Use completion during local development
+
+| Shell  | Command                                      |
+| ------ | -------------------------------------------- |
+| `zsh`  | `source <(bun src/index.ts completion zsh)`  |
+| `bash` | `source <(bun src/index.ts completion bash)` |
+
+- Completion is context-aware. For example, `lh agent <Tab>` shows agent subcommands instead of top-level commands.
+- If you update completion logic locally, re-run the corresponding `source <(...)` command to reload it in the current shell session.
+- Completion only registers shell functions. It does not install the `lh` binary by itself.
+
+## Quick Check
+
+```bash
+which lh
+lh --help
+lh agent <TAB>
+```
diff --git a/apps/cli/package.json b/apps/cli/package.json
index 65a27f1bc..6e3fad7b2 100644
--- a/apps/cli/package.json
+++ b/apps/cli/package.json
@@ -11,7 +11,7 @@
     "dist"
   ],
   "scripts": {
-    "build": "npx tsup",
+    "build": "tsdown",
     "cli:link": "bun link",
     "cli:unlink": "bun unlink",
     "dev": "LOBEHUB_CLI_HOME=.lobehub-dev bun src/index.ts",
@@ -20,24 +20,22 @@
     "test:coverage": "bunx vitest run --config vitest.config.mts --coverage",
     "type-check": "tsc --noEmit"
   },
-  "dependencies": {
+  "devDependencies": {
+    "@lobechat/device-gateway-client": "workspace:*",
+    "@lobechat/local-file-shell": "workspace:*",
     "@trpc/client": "^11.8.1",
+    "@types/node": "^22.13.5",
+    "@types/ws": "^8.18.1",
     "commander": "^13.1.0",
     "debug": "^4.4.0",
     "diff": "^8.0.3",
     "fast-glob": "^3.3.3",
     "picocolors": "^1.1.1",
     "superjson": "^2.2.6",
+    "tsdown": "^0.21.4",
+    "typescript": "^5.9.3",
     "ws": "^8.18.1"
   },
-  "devDependencies": {
-    "@lobechat/device-gateway-client": "workspace:*",
-    "@lobechat/local-file-shell": "workspace:*",
-    "@types/node": "^22.13.5",
-    "@types/ws": "^8.18.1",
-    "tsup": "^8.4.0",
-    "typescript": "^5.9.3"
-  },
   "publishConfig": {
     "access": "public",
     "registry": "https://registry.npmjs.org"
   }
 }
diff --git a/apps/cli/src/commands/completion.test.ts b/apps/cli/src/commands/completion.test.ts
new file mode 100644
index 000000000..a34a5ac7b
--- /dev/null
+++ b/apps/cli/src/commands/completion.test.ts
@@ -0,0 +1,102 @@
+import { Command } from 'commander';
+import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
+
+import { registerCompletionCommand } from './completion';
+
+describe('completion command', () => {
+  let consoleSpy: ReturnType<typeof vi.spyOn>;
+  const originalShell = process.env.SHELL;
+
+  beforeEach(() => {
+    consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
+  });
+
+  afterEach(() => {
+    consoleSpy.mockRestore();
+    delete process.env.LOBEHUB_COMP_CWORD;
+    process.env.SHELL = originalShell;
+  });
+
+  function createProgram() {
+    const program = new Command();
+    program.exitOverride();
+
+    program
+      .command('agent')
+      .description('Agent commands')
+      .command('list')
+      .description('List agents');
+    program.command('generate').alias('gen').description('Generate content');
+    program.command('usage').description('Usage').option('--month <YYYY-MM>', 'Month to query');
+    program.command('internal', { hidden: true });
+
+    registerCompletionCommand(program);
+
+    return program;
+  }
+
+  it('should output zsh completion script by default', async () => {
+    process.env.SHELL = '/bin/zsh';
+
+    const program = createProgram();
+    await program.parseAsync(['node', 'test', 'completion']);
+
+    expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('compdef _lobehub_completion'));
+    expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('lh lobe lobehub'));
+    expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('"${(@)words[@]:1}"'));
+  });
+
+  it('should output bash completion script when requested', async () => {
+    const program = createProgram();
+    await program.parseAsync(['node', 'test', 'completion', 'bash']);
+
+    expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('complete -o nosort'));
+    expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('__complete'));
+  });
+
+  it('should suggest root commands and aliases', async () => {
+    process.env.LOBEHUB_COMP_CWORD = '0';
+
+    const program = createProgram();
+    await program.parseAsync(['node', 'test', '__complete', 'g']);
+
+    expect(consoleSpy.mock.calls.map(([value]) => value)).toEqual(['gen', 'generate']);
+  });
+
+  it('should suggest nested subcommands in the current command context', async () => {
+    process.env.LOBEHUB_COMP_CWORD = '1';
+
+    const program = createProgram();
+    await program.parseAsync(['node', 'test', '__complete', 'agent']);
+
+    expect(consoleSpy).toHaveBeenCalledWith('list');
+  });
+
+  it('should suggest command options after leaf commands', async () => {
+    process.env.LOBEHUB_COMP_CWORD = '1';
+
+    const program = createProgram();
+    await program.parseAsync(['node', 'test', '__complete', 'usage']);
+
+    expect(consoleSpy).toHaveBeenCalledWith('--month');
+  });
+
+  it('should not suggest commands while completing an option value', async () => {
+    process.env.LOBEHUB_COMP_CWORD = '2';
+
+    const program = createProgram();
+    await program.parseAsync(['node', 'test', '__complete', 'usage', '--month']);
+
+    expect(consoleSpy).not.toHaveBeenCalled();
+  });
+
+  it('should not expose hidden commands', async () => {
+    process.env.LOBEHUB_COMP_CWORD = '0';
+
+    const program = createProgram();
+    await program.parseAsync(['node', 'test', '__complete']);
+
+    expect(consoleSpy.mock.calls.map(([value]) => value)).not.toContain('internal');
+    expect(consoleSpy.mock.calls.map(([value]) => value)).not.toContain('__complete');
+  });
+});
diff --git a/apps/cli/src/commands/completion.ts b/apps/cli/src/commands/completion.ts
new file mode 100644
index 000000000..a4c095ca1
--- /dev/null
+++ b/apps/cli/src/commands/completion.ts
@@ -0,0 +1,30 @@
+import type { Command } from 'commander';
+
+import {
+  getCompletionCandidates,
+  parseCompletionWordIndex,
+  renderCompletionScript,
+  resolveCompletionShell,
+} from '../utils/completion';
+
+export function registerCompletionCommand(program: Command) {
+  program
+    .command('completion [shell]')
+    .description('Output shell completion script')
+    .action((shell?: string) => {
+      console.log(renderCompletionScript(resolveCompletionShell(shell)));
+    });
+
+  program
+    .command('__complete', { hidden: true })
+    .allowUnknownOption()
+    .argument('[words...]')
+    .action((words: string[] = []) => {
+      const currentWordIndex = parseCompletionWordIndex(process.env.LOBEHUB_COMP_CWORD, words);
+      const candidates = getCompletionCandidates(program, words, currentWordIndex);
+
+      for (const candidate of candidates) {
+        console.log(candidate);
+      }
+    });
+}
diff --git a/apps/cli/src/index.ts b/apps/cli/src/index.ts
index 6cd09beb2..1b9de4d24 100644
--- a/apps/cli/src/index.ts
+++ b/apps/cli/src/index.ts
@@ -5,6 +5,7 @@ import { Command } from 'commander';
 import { registerAgentCommand } from './commands/agent';
 import { registerAgentGroupCommand } from './commands/agent-group';
 import { registerBotCommand } from './commands/bot';
+import { registerCompletionCommand } from './commands/completion';
 import { registerConfigCommand } from './commands/config';
 import { registerConnectCommand } from './commands/connect';
 import { registerCronCommand } from './commands/cron';
@@ -41,6 +42,7 @@ program

 registerLoginCommand(program);
 registerLogoutCommand(program);
+registerCompletionCommand(program);
 registerConnectCommand(program);
 registerDeviceCommand(program);
 registerStatusCommand(program);
diff --git a/apps/cli/src/utils/completion.ts b/apps/cli/src/utils/completion.ts
new file mode 100644
index 000000000..551442d7f
--- /dev/null
+++ b/apps/cli/src/utils/completion.ts
@@ -0,0 +1,157 @@
+import type { Command, Option } from 'commander';
+import { InvalidArgumentError } from 'commander';
+
+const CLI_BIN_NAMES = ['lh', 'lobe', 'lobehub'] as const;
+const SUPPORTED_SHELLS = ['bash', 'zsh'] as const;
+
+type SupportedShell = (typeof SUPPORTED_SHELLS)[number];
+
+interface HiddenCommand extends Command {
+  _hidden?: boolean;
+}
+
+interface HiddenOption extends Option {
+  hidden: boolean;
+}
+
+function isVisibleCommand(command: Command) {
+  return !(command as HiddenCommand)._hidden;
+}
+
+function isVisibleOption(option: Option) {
+  return !(option as HiddenOption).hidden;
+}
+
+function listCommandTokens(command: Command) {
+  return [command.name(), ...command.aliases()].filter(Boolean);
+}
+
+function listOptionTokens(command: Command) {
+  return command.options
+    .filter(isVisibleOption)
+    .flatMap((option) => [option.short, option.long].filter(Boolean) as string[]);
+}
+
+function findSubcommand(command: Command, token: string) {
+  return command.commands.find(
+    (subcommand) => isVisibleCommand(subcommand) && listCommandTokens(subcommand).includes(token),
+  );
+}
+
+function findOption(command: Command, token: string) {
+  return command.options.find(
+    (option) =>
+      isVisibleOption(option) && (option.short === token || option.long === token || false),
+  );
+}
+
+function filterCandidates(candidates: string[], currentWord: string) {
+  const unique = [...new Set(candidates)];
+
+  if (!currentWord) return unique.sort();
+
+  return unique.filter((candidate) => candidate.startsWith(currentWord)).sort();
+}
+
+function resolveCommandContext(program: Command, completedWords: string[]) {
+  let command = program;
+  let expectsOptionValue = false;
+
+  for (const token of completedWords) {
+    if (expectsOptionValue) {
+      expectsOptionValue = false;
+      continue;
+    }
+
+    if (!token) continue;
+
+    if (token.startsWith('-')) {
+      const option = findOption(command, token);
+
+      expectsOptionValue = Boolean(
+        option && (option.required || option.optional || option.variadic),
+      );
+      continue;
+    }
+
+    const subcommand = findSubcommand(command, token);
+    if (subcommand) {
+      command = subcommand;
+    }
+  }
+
+  return { command, expectsOptionValue };
+}
+
+export function getCompletionCandidates(
+  program: Command,
+  words: string[],
+  currentWordIndex = words.length,
+) {
+  const safeCurrentWordIndex = Math.min(Math.max(currentWordIndex, 0), words.length);
+  const completedWords = words.slice(0, safeCurrentWordIndex);
+  const currentWord = safeCurrentWordIndex < words.length ? words[safeCurrentWordIndex] || '' : '';
+  const { command, expectsOptionValue } = resolveCommandContext(program, completedWords);
+
+  if (expectsOptionValue) return [];
+
+  const commandCandidates = currentWord.startsWith('-')
+    ? []
+    : command.commands
+        .filter(isVisibleCommand)
+        .flatMap((subcommand) => listCommandTokens(subcommand));
+
+  if (commandCandidates.length > 0) {
+    return filterCandidates(commandCandidates, currentWord);
+  }
+
+  return filterCandidates(listOptionTokens(command), currentWord);
+}
+
+export function parseCompletionWordIndex(rawValue: string | undefined, words: string[]) {
+  const parsedValue = rawValue ? Number.parseInt(rawValue, 10) : Number.NaN;
+
+  if (Number.isNaN(parsedValue)) return words.length;
+
+  return Math.min(Math.max(parsedValue, 0), words.length);
+}
+
+export function resolveCompletionShell(shell?: string): SupportedShell {
+  const fallbackShell = process.env.SHELL?.split('/').pop() || 'zsh';
+  const resolvedShell = (shell || fallbackShell).toLowerCase();
+
+  if ((SUPPORTED_SHELLS as readonly string[]).includes(resolvedShell)) {
+    return resolvedShell as SupportedShell;
+  }
+
+  throw new InvalidArgumentError(
+    `Unsupported shell "${resolvedShell}". Supported shells: ${SUPPORTED_SHELLS.join(', ')}`,
+  );
+}
+
+export function renderCompletionScript(shell: SupportedShell) {
+  if (shell === 'bash') {
+    return [
+      '# shellcheck shell=bash',
+      '_lobehub_completion() {',
+      "  local IFS=$'\\n'",
+      '  local current_index=$((COMP_CWORD - 1))',
+      '  local completions',
+      '  completions=$(LOBEHUB_COMP_CWORD="$current_index" "${COMP_WORDS[0]}" __complete "${COMP_WORDS[@]:1}")',
+      '  COMPREPLY=($(printf \'%s\\n\' "$completions"))',
+      '}',
+      `complete -o nosort -F _lobehub_completion ${CLI_BIN_NAMES.join(' ')}`,
+    ].join('\n');
+  }
+
+  return [
+    `#compdef ${CLI_BIN_NAMES.join(' ')}`,
+    '_lobehub_completion() {',
+    '  local -a completions',
+    '  local current_index=$((CURRENT - 2))',
+    '  completions=("${(@f)$(LOBEHUB_COMP_CWORD="$current_index" "$words[1]" __complete "${(@)words[@]:1}")}")',
+    "  _describe 'values' completions",
+    '}',
+    `compdef _lobehub_completion ${CLI_BIN_NAMES.join(' ')}`,
+  ].join('\n');
+}
diff --git a/apps/cli/tsdown.config.ts b/apps/cli/tsdown.config.ts
new file mode 100644
index 000000000..0ee73abdd
--- /dev/null
+++ b/apps/cli/tsdown.config.ts
@@ -0,0 +1,14 @@
+import { defineConfig } from 'tsdown';
+
+export default defineConfig({
+  banner: { js: '#!/usr/bin/env node' },
+  clean: true,
+  deps: {
+    neverBundle: ['@napi-rs/canvas'],
+  },
+  entry: ['src/index.ts'],
+  fixedExtension: false,
+  format: ['esm'],
+  platform: 'node',
+  target: 'node18',
+});
diff --git a/apps/cli/tsup.config.ts b/apps/cli/tsup.config.ts
deleted file mode 100644
index b8dd11844..000000000
--- a/apps/cli/tsup.config.ts
+++ /dev/null
@@ -1,18 +0,0 @@
-import { defineConfig } from 'tsup';
-
-export default defineConfig({
-  banner: { js: '#!/usr/bin/env node' },
-  clean: true,
-  entry: ['src/index.ts'],
-  external: ['@napi-rs/canvas', 'fast-glob', 'diff', 'debug'],
-  format: ['esm'],
-  noExternal: [
-    '@lobechat/device-gateway-client',
-    '@lobechat/local-file-shell',
-    '@lobechat/file-loaders',
-    '@trpc/client',
-    'superjson',
-  ],
-  platform: 'node',
-  target: 'node18',
-});
PATCH

echo "Patch applied successfully."
