#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ai-setup

# Idempotency guard
if grep -qF "- Command file MUST be in `src/commands/{commandName}.ts` and export a **named**" ".cursor/skills/adding-a-command/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/skills/adding-a-command/SKILL.md b/.cursor/skills/adding-a-command/SKILL.md
@@ -7,43 +7,39 @@ description: Create a new CLI command following Commander.js pattern. Handles co
 ## Critical
 
 - Commands MUST be registered in `src/cli.ts` using `.command()` and `.action()` with the `tracked()` wrapper for telemetry.
-- Command file MUST be in `src/commands/{commandName}.ts` and export a default async function with signature: `async (options: CommandOptions, ctx: CLIContext) => Promise<void>`.
-- Always use `tracked(commandName, async () => { ... })` wrapper in `src/cli.ts` to enable telemetry tracking.
+- Command file MUST be in `src/commands/{commandName}.ts` and export a **named** async function: `export async function {commandName}Command(options?: OptionType)`. Never use default exports — `src/cli.ts` imports commands by name.
+- Always use `tracked('{kebab-name}', {commandName}Command)` wrapper in `src/cli.ts` to enable telemetry tracking.
 - Test file MUST be in `src/commands/__tests__/{commandName}.test.ts` with at least one happy-path test.
 
 ## Instructions
 
 1. **Create command file** in `src/commands/{commandName}.ts`
-   - Export default async function: `export default async (options: any, ctx: CLIContext) => { ... }`
-   - Import `CLIContext` from `src/cli.ts`
-   - Use `ctx.log()` for output (respects quiet mode via `--quiet`)
-   - Use `ctx.spinner()` for async operations
+   - Export named async function: `export async function {commandName}Command(options?: { optionName?: type }) { ... }`
+   - Return `void`; handle all output via `console.log` or chalk
+   - Define a TypeScript interface for options if the command takes any
    - Verify function signature matches existing commands like `src/commands/score.ts`
 
 2. **Register in src/cli.ts**
-   - Import the command: `import addCommand from './commands/mycommand.js'`
+   - Import the command by name: `import { {commandName}Command } from './commands/{commandName}.js'`
    - Add command definition:
      ```ts
      program
-       .command('mycommand')
+       .command('{kebab-name}')
        .description('One-line description')
        .option('--option', 'Option description')
-       .action(tracked('mycommand', addCommand))
+       .action(tracked('{kebab-name}', {commandName}Command))
      ```
    - Verify imports are `.js` (ESM)
    - Verify `tracked()` wrapper is applied to `.action()`
 
-3. **Add telemetry event** in `src/telemetry/events.ts`
-   - Add event type: `export type MyCommandEvent = { type: 'mycommand:start' | 'mycommand:success' | 'mycommand:error'; ... }`
-   - Include `duration?: number` field for timed events
-   - Update `export type AllEvents = ... | MyCommandEvent`
-   - Verify event matches pattern in existing events
+3. **Handle errors consistently**: Wrap error-prone operations in try/catch:
+   - User error (bad input): `console.error(chalk.red('message')); throw new Error('__exit__');`
+   - System error: `throw new Error('Detailed error message');`
 
 4. **Create test file** in `src/commands/__tests__/{commandName}.test.ts`
    - Import `describe`, `it`, `expect`, `vi` from `vitest`
-   - Import command from parent: `import addCommand from '../mycommand.js'`
-   - Create mock `CLIContext`: `{ log: vi.fn(), spinner: vi.fn().mockReturnValue({ start: vi.fn(), stop: vi.fn() }) }`
-   - Test happy path: `await addCommand({}, ctx); expect(ctx.log).toHaveBeenCalled()`
+   - Import command by name: `import { {commandName}Command } from '../{commandName}.js'`
+   - Test happy path and error paths
    - Verify test runs: `npx vitest run src/commands/__tests__/{commandName}.test.ts`
 
 5. **Build and validate**
@@ -59,47 +55,40 @@ User says: "Add a new `verify` command that checks if config files exist"
 **Actions:**
 1. Create `src/commands/verify.ts`:
    ```ts
-   import { CLIContext } from '../cli.js';
-   export default async (options: any, ctx: CLIContext) => {
-     const spinner = ctx.spinner('Verifying config files...');
-     spinner.start();
+   import chalk from 'chalk';
+   import { checkFilesExist } from '../lib/config.js';
+
+   export async function verifyCommand(options?: { json?: boolean }) {
      const exists = await checkFilesExist();
-     spinner.stop();
-     ctx.log(`✓ Config files ${exists ? 'found' : 'missing'}`);
-   };
+     console.log(chalk.bold('Verify'));
+     console.log(`  Config files: ${exists ? chalk.green('found') : chalk.red('missing')}`);
+   }
    ```
 2. Register in `src/cli.ts`:
    ```ts
-   import verifyCommand from './commands/verify.js';
+   import { verifyCommand } from './commands/verify.js';
    program
      .command('verify')
      .description('Verify configuration files exist')
      .action(tracked('verify', verifyCommand))
    ```
-3. Add to `src/telemetry/events.ts`:
-   ```ts
-   export type VerifyEvent = {
-     type: 'verify:start' | 'verify:success' | 'verify:error';
-     duration?: number;
-   };
-   ```
-4. Create `src/commands/__tests__/verify.test.ts` with happy-path test
-5. Run `npm run build && npm run test && npm run lint`
+3. Create `src/commands/__tests__/verify.test.ts` with happy-path test
+4. Run `npm run build && npm run test`
 
 ## Common Issues
 
-**"Cannot find module './commands/mycommand.js'"**
-- Verify file is at `src/commands/mycommand.ts` (TypeScript)
-- Verify import in `src/cli.ts` uses `.js` extension: `from './commands/mycommand.js'`
+**"SyntaxError: The requested module does not provide an export named '{commandName}Command'"**
+- Use `export async function {commandName}Command(...)` — named export, not `export default`
+- Import in `src/cli.ts` using named import: `import { {commandName}Command } from './commands/{commandName}.js'`
 - Rebuild: `npm run build`
 
 **"tracked is not exported from src/cli.ts"**
-- Verify `tracked()` function exists in `src/cli.ts` (it should; check existing commands)
-- Verify you're using it as `.action(tracked('commandName', commandFunction))`
+- `tracked()` is defined in `src/cli.ts` itself; it takes two args: `tracked('kebab-name', handlerFn)`
+- Verify you're using it as `.action(tracked('{kebab-name}', {commandName}Command))`
 
-**Test fails with "CLIContext is not a constructor"**
-- Create mock object manually: `const ctx = { log: vi.fn(), spinner: vi.fn().mockReturnValue({ start: vi.fn(), stop: vi.fn() }) }`
-- Do NOT try to instantiate CLIContext; it's an interface
+**Command crashes when run but appears in --help**
+- Verify import name matches function export in the command file
+- Wrap handler with `tracked('command-name', handler)` and ensure the import is correct
 
 **"--option not recognized" when testing**
 - Verify `.option()` is chained in `src/cli.ts` BEFORE `.action()`
PATCH

echo "Gold patch applied."
