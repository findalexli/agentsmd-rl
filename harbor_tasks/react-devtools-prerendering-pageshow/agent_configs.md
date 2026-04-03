# Agent Config Files for react-devtools-prerendering-pageshow

Repo: facebook/react
Commit: 4b568a8dbb4cb84b0067f353b9c0bec1ddb61d8e
Files found: 9


---
## CLAUDE.md

```
   1 | # React
   2 | 
   3 | React is a JavaScript library for building user interfaces.
   4 | 
   5 | ## Monorepo Overview
   6 | 
   7 | - **React**: All files outside `/compiler/`
   8 | - **React Compiler**: `/compiler/` directory (has its own instructions)
```


---
## compiler/CLAUDE.md

```
   1 | # React Compiler Knowledge Base
   2 | 
   3 | This document contains knowledge about the React Compiler gathered during development sessions. It serves as a reference for understanding the codebase architecture and key concepts.
   4 | 
   5 | ## Project Structure
   6 | 
   7 | When modifying the compiler, you MUST read the documentation about that pass in `compiler/packages/babel-plugin-react-compiler/docs/passes/` to learn more about the role of that pass within the compiler.
   8 | 
   9 | - `packages/babel-plugin-react-compiler/` - Main compiler package
  10 |   - `src/HIR/` - High-level Intermediate Representation types and utilities
  11 |   - `src/Inference/` - Effect inference passes (aliasing, mutation, etc.)
  12 |   - `src/Validation/` - Validation passes that check for errors
  13 |   - `src/Entrypoint/Pipeline.ts` - Main compilation pipeline with pass ordering
  14 |   - `src/__tests__/fixtures/compiler/` - Test fixtures
  15 |     - `error.todo-*.js` - Unsupported feature, correctly throws Todo error (graceful bailout)
  16 |     - `error.bug-*.js` - Known bug, throws wrong error type or incorrect behavior
  17 |     - `*.expect.md` - Expected output for each fixture
  18 | 
  19 | ## Running Tests
  20 | 
  21 | ```bash
  22 | # Run all tests
  23 | yarn snap
  24 | 
  25 | # Run tests matching a pattern
  26 | # Example: yarn snap -p 'error.*'
  27 | yarn snap -p <pattern>
  28 | 
  29 | # Run a single fixture in debug mode. Use the path relative to the __tests__/fixtures/compiler directory
  30 | # For each step of compilation, outputs the step name and state of the compiled program
  31 | # Example: yarn snap -p simple.js -d
  32 | yarn snap -p <file-basename> -d
  33 | 
  34 | # Update fixture outputs (also works with -p)
  35 | yarn snap -u
  36 | ```
  37 | 
  38 | ## Linting
  39 | 
  40 | ```bash
  41 | # Run lint on the compiler source
  42 | yarn workspace babel-plugin-react-compiler lint
  43 | ```
  44 | 
  45 | ## Formatting
  46 | 
  47 | ```bash
  48 | # Run prettier on all files (from the react root directory, not compiler/)
  49 | yarn prettier-all
  50 | ```
  51 | 
  52 | ## Compiling Arbitrary Files
  53 | 
  54 | Use `yarn snap compile` to compile any file (not just fixtures) with the React Compiler:
  55 | 
  56 | ```bash
  57 | # Compile a file and see the output
  58 | yarn snap compile <path>
  59 | 
  60 | # Compile with debug logging to see the state after each compiler pass
  61 | # This is an alternative to `yarn snap -d -p <pattern>` when you don't have a fixture file yet
  62 | yarn snap compile --debug <path>
  63 | ```
  64 | 
  65 | ## Minimizing Test Cases
  66 | 
  67 | Use `yarn snap minimize` to automatically reduce a failing test case to its minimal reproduction:
  68 | 
  69 | ```bash
  70 | # Minimize a file that causes a compiler error
  71 | yarn snap minimize <path>
  72 | 
  73 | # Minimize and update the file in-place with the minimized version
  74 | yarn snap minimize --update <path>
  75 | ```
  76 | 
  77 | ## Version Control
  78 | 
  79 | This repository uses Sapling (`sl`) for version control. Sapling is similar to Mercurial: there is not staging area, but new/deleted files must be explicitlyu added/removed.
  80 | 
  81 | ```bash
  82 | # Check status
  83 | sl status
  84 | 
  85 | # Add new files, remove deleted files
  86 | sl addremove
  87 | 
  88 | # Commit all changes
  89 | sl commit -m "Your commit message"
  90 | 
  91 | # Commit with multi-line message using heredoc
  92 | sl commit -m "$(cat <<'EOF'
  93 | Summary line
  94 | 
  95 | Detailed description here
  96 | EOF
  97 | )"
  98 | ```
  99 | 
 100 | ## Key Concepts
 101 | 
 102 | ### HIR (High-level Intermediate Representation)
 103 | 
 104 | The compiler converts source code to HIR for analysis. Key types in `src/HIR/HIR.ts`:
 105 | 
 106 | - **HIRFunction** - A function being compiled
 107 |   - `body.blocks` - Map of BasicBlocks
 108 |   - `context` - Captured variables from outer scope
 109 |   - `params` - Function parameters
 110 |   - `returns` - The function's return place
 111 |   - `aliasingEffects` - Effects that describe the function's behavior when called
 112 | 
 113 | - **Instruction** - A single operation
 114 |   - `lvalue` - The place being assigned to
 115 |   - `value` - The instruction kind (CallExpression, FunctionExpression, LoadLocal, etc.)
 116 |   - `effects` - Array of AliasingEffects for this instruction
 117 | 
 118 | - **Terminal** - Block terminators (return, branch, etc.)
 119 |   - `effects` - Array of AliasingEffects
 120 | 
 121 | - **Place** - A reference to a value
 122 |   - `identifier.id` - Unique IdentifierId
 123 | 
 124 | - **Phi nodes** - Join points for values from different control flow paths
 125 |   - Located at `block.phis`
 126 |   - `phi.place` - The result place
 127 |   - `phi.operands` - Map of predecessor block to source place
 128 | 
 129 | ### AliasingEffects System
 130 | 
 131 | Effects describe data flow and operations. Defined in `src/Inference/AliasingEffects.ts`:
 132 | 
 133 | **Data Flow Effects:**
 134 | - `Impure` - Marks a place as containing an impure value (e.g., Date.now() result, ref.current)
 135 | - `Capture a -> b` - Value from `a` is captured into `b` (mutable capture)
 136 | - `Alias a -> b` - `b` aliases `a`
 137 | - `ImmutableCapture a -> b` - Immutable capture (like Capture but read-only)
 138 | - `Assign a -> b` - Direct assignment
 139 | - `MaybeAlias a -> b` - Possible aliasing
 140 | - `CreateFrom a -> b` - Created from source
 141 | 
 142 | **Mutation Effects:**
 143 | - `Mutate value` - Value is mutated
 144 | - `MutateTransitive value` - Value and transitive captures are mutated
 145 | - `MutateConditionally value` - May mutate
 146 | - `MutateTransitiveConditionally value` - May mutate transitively
 147 | 
 148 | **Other Effects:**
 149 | - `Render place` - Place is used in render context (JSX props, component return)
 150 | - `Freeze place` - Place is frozen (made immutable)
 151 | - `Create place` - New value created
 152 | - `CreateFunction` - Function expression created, includes `captures` array
 153 | - `Apply` - Function application with receiver, function, args, and result
 154 | 
 155 | ### Hook Aliasing Signatures
 156 | 
 157 | Located in `src/HIR/Globals.ts`, hooks can define custom aliasing signatures to control how data flows through them.
 158 | 
 159 | **Structure:**
 160 | ```typescript
 161 | aliasing: {
 162 |   receiver: '@receiver',    // The hook function itself
 163 |   params: ['@param0'],      // Named positional parameters
 164 |   rest: '@rest',            // Rest parameters (or null)
 165 |   returns: '@returns',      // Return value
 166 |   temporaries: [],          // Temporary values during execution
 167 |   effects: [                // Array of effects to apply when hook is called
 168 |     {kind: 'Freeze', value: '@param0', reason: ValueReason.HookCaptured},
 169 |     {kind: 'Assign', from: '@param0', into: '@returns'},
 170 |   ],
 171 | }
 172 | ```
 173 | 
 174 | **Common patterns:**
 175 | 
 176 | 1. **RenderHookAliasing** (useState, useContext, useMemo, useCallback):
 177 |    - Freezes arguments (`Freeze @rest`)
 178 |    - Marks arguments as render-time (`Render @rest`)
 179 |    - Creates frozen return value
 180 |    - Aliases arguments to return
 181 | 
 182 | 2. **EffectHookAliasing** (useEffect, useLayoutEffect, useInsertionEffect):
 183 |    - Freezes function and deps
 184 |    - Creates internal effect object
 185 |    - Captures function and deps into effect
 186 |    - Returns undefined
 187 | 
 188 | 3. **Event handler hooks** (useEffectEvent):
 189 |    - Freezes callback (`Freeze @fn`)
 190 |    - Aliases input to return (`Assign @fn -> @returns`)
 191 |    - NO Render effect (callback not called during render)
 192 | 
 193 | **Example: useEffectEvent**
 194 | ```typescript
 195 | const UseEffectEventHook = addHook(
 196 |   DEFAULT_SHAPES,
 197 |   {
 198 |     positionalParams: [Effect.Freeze],  // Takes one positional param
 199 |     restParam: null,
 200 |     returnType: {kind: 'Function', ...},
 201 |     calleeEffect: Effect.Read,
 202 |     hookKind: 'useEffectEvent',
 203 |     returnValueKind: ValueKind.Frozen,
 204 |     aliasing: {
 205 |       receiver: '@receiver',
 206 |       params: ['@fn'],              // Name for the callback parameter
 207 |       rest: null,
 208 |       returns: '@returns',
 209 |       temporaries: [],
 210 |       effects: [
 211 |         {kind: 'Freeze', value: '@fn', reason: ValueReason.HookCaptured},
 212 |         {kind: 'Assign', from: '@fn', into: '@returns'},
 213 |         // Note: NO Render effect - callback is not called during render
 214 |       ],
 215 |     },
 216 |   },
 217 |   BuiltInUseEffectEventId,
 218 | );
 219 | 
 220 | // Add as both names for compatibility
 221 | ['useEffectEvent', UseEffectEventHook],
 222 | ['experimental_useEffectEvent', UseEffectEventHook],
 223 | ```
 224 | 
 225 | **Key insight:** If a hook is missing an `aliasing` config, it falls back to `DefaultNonmutatingHook` which includes a `Render` effect on all arguments. This can cause false positives for hooks like `useEffectEvent` whose callbacks are not called during render.
 226 | 
 227 | ## Feature Flags
 228 | 
 229 | Feature flags are configured in `src/HIR/Environment.ts`, for example `enableJsxOutlining`. Test fixtures can override the active feature flags used for that fixture via a comment pragma on the first line of the fixture input, for example:
 230 | 
 231 | ```javascript
 232 | // enableJsxOutlining @enableNameAnonymousFunctions:false
 233 | 
 234 | ...code...
 235 | ```
 236 | 
 237 | Would enable the `enableJsxOutlining` feature and disable the `enableNameAnonymousFunctions` feature.
 238 | 
 239 | ## Debugging Tips
 240 | 
 241 | 1. Run `yarn snap -p <fixture>` to see full HIR output with effects
 242 | 2. Look for `@aliasingEffects=` on FunctionExpressions
 243 | 3. Look for `Impure`, `Render`, `Capture` effects on instructions
 244 | 4. Check the pass ordering in Pipeline.ts to understand when effects are populated vs validated
 245 | 
 246 | ## Error Handling and Fault Tolerance
 247 | 
 248 | The compiler is fault-tolerant: it runs all passes and accumulates errors on the `Environment` rather than throwing on the first error. This lets users see all compilation errors at once.
 249 | 
 250 | **Recording errors** — Passes record errors via `env.recordError(diagnostic)`. Errors are accumulated on `Environment.#errors` and checked at the end of the pipeline via `env.hasErrors()` / `env.aggregateErrors()`.
 251 | 
 252 | **`tryRecord()` wrapper** — In Pipeline.ts, validation passes are wrapped in `env.tryRecord(() => pass(hir))` which catches thrown `CompilerError`s (non-invariant) and records them. Infrastructure/transformation passes are NOT wrapped in `tryRecord()` because later passes depend on their output being structurally valid.
 253 | 
 254 | **Error categories:**
 255 | - `CompilerError.throwTodo()` — Unsupported but known pattern. Graceful bailout. Can be caught by `tryRecord()`.
 256 | - `CompilerError.invariant()` — Truly unexpected/invalid state. Always throws immediately, never caught by `tryRecord()`.
 257 | - Non-`CompilerError` exceptions — Always re-thrown.
 258 | 
 259 | **Key files:** `Environment.ts` (`recordError`, `tryRecord`, `hasErrors`, `aggregateErrors`), `Pipeline.ts` (pass orchestration), `Program.ts` (`tryCompileFunction` handles the `Result`).
 260 | 
 261 | **Test fixtures:** `__tests__/fixtures/compiler/fault-tolerance/` contains multi-error fixtures verifying all errors are reported.
```


---
## .claude/skills/extract-errors/SKILL.md

```
   1 | ---
   2 | name: extract-errors
   3 | description: Use when adding new error messages to React, or seeing "unknown error code" warnings.
   4 | ---
   5 | 
   6 | # Extract Error Codes
   7 | 
   8 | ## Instructions
   9 | 
  10 | 1. Run `yarn extract-errors`
  11 | 2. Report if any new errors need codes assigned
  12 | 3. Check if error codes are up to date
```


---
## .claude/skills/feature-flags/SKILL.md

```
   1 | ---
   2 | name: feature-flags
   3 | description: Use when feature flag tests fail, flags need updating, understanding @gate pragmas, debugging channel-specific test failures, or adding new flags to React.
   4 | ---
   5 | 
   6 | # React Feature Flags
   7 | 
   8 | ## Flag Files
   9 | 
  10 | | File | Purpose |
  11 | |------|---------|
  12 | | `packages/shared/ReactFeatureFlags.js` | Default flags (canary), `__EXPERIMENTAL__` overrides |
  13 | | `packages/shared/forks/ReactFeatureFlags.www.js` | www channel, `__VARIANT__` overrides |
  14 | | `packages/shared/forks/ReactFeatureFlags.native-fb.js` | React Native, `__VARIANT__` overrides |
  15 | | `packages/shared/forks/ReactFeatureFlags.test-renderer.js` | Test renderer |
  16 | 
  17 | ## Gating Tests
  18 | 
  19 | ### `@gate` pragma (test-level)
  20 | 
  21 | Use when the feature is completely unavailable without the flag:
  22 | 
  23 | ```javascript
  24 | // @gate enableViewTransition
  25 | it('supports view transitions', () => {
  26 |   // This test only runs when enableViewTransition is true
  27 |   // and is SKIPPED (not failed) when false
  28 | });
  29 | ```
  30 | 
  31 | ### `gate()` inline (assertion-level)
  32 | 
  33 | Use when the feature exists but behavior differs based on flag:
  34 | 
  35 | ```javascript
  36 | it('renders component', async () => {
  37 |   await act(() => root.render(<App />));
  38 | 
  39 |   if (gate(flags => flags.enableNewBehavior)) {
  40 |     expect(container.textContent).toBe('new output');
  41 |   } else {
  42 |     expect(container.textContent).toBe('legacy output');
  43 |   }
  44 | });
  45 | ```
  46 | 
  47 | ## Adding a New Flag
  48 | 
  49 | 1. Add to `ReactFeatureFlags.js` with default value
  50 | 2. Add to each fork file (`*.www.js`, `*.native-fb.js`, etc.)
  51 | 3. If it should vary in www/RN, set to `__VARIANT__` in the fork file
  52 | 4. Gate tests with `@gate flagName` or inline `gate()`
  53 | 
  54 | ## Checking Flag States
  55 | 
  56 | Use `/flags` to view states across channels. See the `flags` skill for full command options.
  57 | 
  58 | ## `__VARIANT__` Flags (GKs)
  59 | 
  60 | Flags set to `__VARIANT__` simulate gatekeepers - tested twice (true and false):
  61 | 
  62 | ```bash
  63 | /test www <pattern>              # __VARIANT__ = true
  64 | /test www variant false <pattern> # __VARIANT__ = false
  65 | ```
  66 | 
  67 | ## Debugging Channel-Specific Failures
  68 | 
  69 | 1. Run `/flags --diff <channel1> <channel2>` to compare values
  70 | 2. Check `@gate` conditions - test may be gated to specific channels
  71 | 3. Run `/test <channel> <pattern>` to isolate the failure
  72 | 4. Verify flag exists in all fork files if newly added
  73 | 
  74 | ## Common Mistakes
  75 | 
  76 | - **Forgetting both variants** - Always test `www` AND `www variant false` for `__VARIANT__` flags
  77 | - **Using @gate for behavior differences** - Use inline `gate()` if both paths should run
  78 | - **Missing fork files** - New flags must be added to ALL fork files, not just the main one
  79 | - **Wrong gate syntax** - It's `gate(flags => flags.name)`, not `gate('name')`
```


---
## .claude/skills/fix/SKILL.md

```
   1 | ---
   2 | name: fix
   3 | description: Use when you have lint errors, formatting issues, or before committing code to ensure it passes CI.
   4 | ---
   5 | 
   6 | # Fix Lint and Formatting
   7 | 
   8 | ## Instructions
   9 | 
  10 | 1. Run `yarn prettier` to fix formatting
  11 | 2. Run `yarn linc` to check for remaining lint issues
  12 | 3. Report any remaining manual fixes needed
  13 | 
  14 | ## Common Mistakes
  15 | 
  16 | - **Running prettier on wrong files** - `yarn prettier` only formats changed files
  17 | - **Ignoring linc errors** - These will fail CI, fix them before committing
```


---
## .claude/skills/flags/SKILL.md

```
   1 | ---
   2 | name: flags
   3 | description: Use when you need to check feature flag states, compare channels, or debug why a feature behaves differently across release channels.
   4 | ---
   5 | 
   6 | # Feature Flags
   7 | 
   8 | Arguments:
   9 | - $ARGUMENTS: Optional flags
  10 | 
  11 | ## Options
  12 | 
  13 | | Option | Purpose |
  14 | |--------|---------|
  15 | | (none) | Show all flags across all channels |
  16 | | `--diff <ch1> <ch2>` | Compare flags between channels |
  17 | | `--cleanup` | Show flags grouped by cleanup status |
  18 | | `--csv` | Output in CSV format |
  19 | 
  20 | ## Channels
  21 | 
  22 | - `www`, `www-modern` - Meta internal
  23 | - `canary`, `next`, `experimental` - OSS channels
  24 | - `rn`, `rn-fb`, `rn-next` - React Native
  25 | 
  26 | ## Legend
  27 | 
  28 | ✅ enabled, ❌ disabled, 🧪 `__VARIANT__`, 📊 profiling-only
  29 | 
  30 | ## Instructions
  31 | 
  32 | 1. Run `yarn flags $ARGUMENTS`
  33 | 2. Explain the output to the user
  34 | 3. For --diff, highlight meaningful differences
  35 | 
  36 | ## Common Mistakes
  37 | 
  38 | - **Forgetting `__VARIANT__` flags** - These are tested both ways in www; check both variants
  39 | - **Comparing wrong channels** - Use `--diff` to see exact differences
```


---
## .claude/skills/flow/SKILL.md

```
   1 | ---
   2 | name: flow
   3 | description: Use when you need to run Flow type checking, or when seeing Flow type errors in React code.
   4 | ---
   5 | 
   6 | # Flow Type Checking
   7 | 
   8 | Arguments:
   9 | - $ARGUMENTS: Renderer to check (default: dom-node)
  10 | 
  11 | ## Renderers
  12 | 
  13 | | Renderer | When to Use |
  14 | |----------|-------------|
  15 | | `dom-node` | Default, recommended for most changes |
  16 | | `dom-browser` | Browser-specific DOM code |
  17 | | `native` | React Native |
  18 | | `fabric` | React Native Fabric |
  19 | 
  20 | ## Instructions
  21 | 
  22 | 1. Run `yarn flow $ARGUMENTS` (use `dom-node` if no argument)
  23 | 2. Report type errors with file locations
  24 | 3. For comprehensive checking (slow), use `yarn flow-ci`
  25 | 
  26 | ## Common Mistakes
  27 | 
  28 | - **Running without a renderer** - Always specify or use default `dom-node`
  29 | - **Ignoring suppressions** - Check if `$FlowFixMe` comments are masking real issues
  30 | - **Missing type imports** - Ensure types are imported from the correct package
```


---
## .claude/skills/test/SKILL.md

```
   1 | ---
   2 | name: test
   3 | description: Use when you need to run tests for React core. Supports source, www, stable, and experimental channels.
   4 | ---
   5 | 
   6 | Run tests for the React codebase.
   7 | 
   8 | Arguments:
   9 | - $ARGUMENTS: Channel, flags, and test pattern
  10 | 
  11 | Usage Examples:
  12 | - `/test ReactFiberHooks` - Run with source channel (default)
  13 | - `/test experimental ReactFiberHooks` - Run with experimental channel
  14 | - `/test www ReactFiberHooks` - Run with www-modern channel
  15 | - `/test www variant false ReactFiberHooks` - Test __VARIANT__=false
  16 | - `/test stable ReactFiberHooks` - Run with stable channel
  17 | - `/test classic ReactFiberHooks` - Run with www-classic channel
  18 | - `/test watch ReactFiberHooks` - Run in watch mode (TDD)
  19 | 
  20 | Release Channels:
  21 | - `(default)` - Source/canary channel, uses ReactFeatureFlags.js defaults
  22 | - `experimental` - Source/experimental channel with __EXPERIMENTAL__ flags = true
  23 | - `www` - www-modern channel with __VARIANT__ flags = true
  24 | - `www variant false` - www channel with __VARIANT__ flags = false
  25 | - `stable` - What ships to npm
  26 | - `classic` - Legacy www-classic (rarely needed)
  27 | 
  28 | Instructions:
  29 | 1. Parse channel from arguments (default: source)
  30 | 2. Map to yarn command:
  31 |    - (default) → `yarn test --silent --no-watchman <pattern>`
  32 |    - experimental → `yarn test -r=experimental --silent --no-watchman <pattern>`
  33 |    - stable → `yarn test-stable --silent --no-watchman <pattern>`
  34 |    - classic → `yarn test-classic --silent --no-watchman <pattern>`
  35 |    - www → `yarn test-www --silent --no-watchman <pattern>`
  36 |    - www variant false → `yarn test-www --variant=false --silent --no-watchman <pattern>`
  37 | 3. Report test results and any failures
  38 | 
  39 | Hard Rules:
  40 | 1. **Use --silent to see failures** - This limits the test output to only failures.
  41 | 2. **Use --no-watchman** - This is a common failure in sandboxing.
  42 | 
  43 | Common Mistakes:
  44 | - **Running without a pattern** - Runs ALL tests, very slow. Always specify a pattern.
  45 | - **Forgetting both www variants** - Test `www` AND `www variant false` for `__VARIANT__` flags.
  46 | - **Test skipped unexpectedly** - Check for `@gate` pragma; see `feature-flags` skill.
```


---
## .claude/skills/verify/SKILL.md

```
   1 | ---
   2 | name: verify
   3 | description: Use when you want to validate changes before committing, or when you need to check all React contribution requirements.
   4 | ---
   5 | 
   6 | # Verification
   7 | 
   8 | Run all verification steps.
   9 | 
  10 | Arguments:
  11 | - $ARGUMENTS: Test pattern for the test step
  12 | 
  13 | ## Instructions
  14 | 
  15 | Run these first in sequence:
  16 | 1. Run `yarn prettier` - format code (stop if fails)
  17 | 2. Run `yarn linc` - lint changed files (stop if fails)
  18 | 
  19 | Then run these with subagents in parallel:
  20 | 1. Use `/flow` to type check (stop if fails)
  21 | 2. Use `/test` to test changes in source (stop if fails)
  22 | 3. Use `/test www` to test changes in www (stop if fails)
  23 | 
  24 | If all pass, show success summary. On failure, stop immediately and report the issue with suggested fixes.
```
