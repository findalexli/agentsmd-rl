# Agent Config Files for microsoft/vscode @ 8c61afa3677cb13ce3071eac5326312fc4d2193a

## .github/copilot-instructions.md

```
     1	# VS Code Copilot Instructions
     2	
     3	## Project Overview
     4	
     5	Visual Studio Code is built with a layered architecture using TypeScript, web APIs and Electron, combining web technologies with native app capabilities. The codebase is organized into key architectural layers:
     6	
     7	### Root Folders
     8	- `src/`: Main TypeScript source code with unit tests in `src/vs/*/test/` folders
     9	- `build/`: Build scripts and CI/CD tools
    10	- `extensions/`: Built-in extensions that ship with VS Code
    11	- `test/`: Integration tests and test infrastructure
    12	- `scripts/`: Development and build scripts
    13	- `resources/`: Static resources (icons, themes, etc.)
    14	- `out/`: Compiled JavaScript output (generated during build)
    15	
    16	### Core Architecture (`src/` folder)
    17	- `src/vs/base/` - Foundation utilities and cross-platform abstractions
    18	- `src/vs/platform/` - Platform services and dependency injection infrastructure
    19	- `src/vs/editor/` - Text editor implementation with language services, syntax highlighting, and editing features
    20	- `src/vs/workbench/` - Main application workbench for web and desktop
    21	  - `workbench/browser/` - Core workbench UI components (parts, layout, actions)
    22	  - `workbench/services/` - Service implementations
    23	  - `workbench/contrib/` - Feature contributions (git, debug, search, terminal, etc.)
    24	  - `workbench/api/` - Extension host and VS Code API implementation
    25	- `src/vs/code/` - Electron main process specific implementation
    26	- `src/vs/server/` - Server specific implementation
    27	- `src/vs/sessions/` - Agent sessions window, a dedicated workbench layer for agentic workflows (sits alongside `vs/workbench`, may import from it but not vice versa)
    28	
    29	The core architecture follows these principles:
    30	- **Layered architecture** - from `base`, `platform`, `editor`, to `workbench`
    31	- **Dependency injection** - Services are injected through constructor parameters
    32	    - If non-service parameters are needed, they need to come after the service parameters
    33	- **Contribution model** - Features contribute to registries and extension points
    34	- **Cross-platform compatibility** - Abstractions separate platform-specific code
    35	
    36	### Built-in Extensions (`extensions/` folder)
    37	The `extensions/` directory contains first-party extensions that ship with VS Code:
    38	- **Language support** - `typescript-language-features/`, `html-language-features/`, `css-language-features/`, etc.
    39	- **Core features** - `git/`, `debug-auto-launch/`, `emmet/`, `markdown-language-features/`
    40	- **Themes** - `theme-*` folders for default color themes
    41	- **Development tools** - `extension-editing/`, `vscode-api-tests/`
    42	
    43	Each extension follows the standard VS Code extension structure with `package.json`, TypeScript sources, and contribution points to extend the workbench through the Extension API.
    44	
    45	### Finding Related Code
    46	1. **Semantic search first**: Use file search for general concepts
    47	2. **Grep for exact strings**: Use grep for error messages or specific function names
    48	3. **Follow imports**: Check what files import the problematic module
    49	4. **Check test files**: Often reveal usage patterns and expected behavior
    50	
    51	## Validating TypeScript changes
    52	
    53	MANDATORY: Always check for compilation errors before running any tests or validation scripts, or declaring work complete, then fix all compilation errors before moving forward.
    54	
    55	- NEVER run tests if there are compilation errors
    56	- NEVER use `npm run compile` to compile TypeScript files
    57	
    58	### TypeScript compilation steps
    59	- If the `#runTasks/getTaskOutput` tool is available, check the `VS Code - Build` watch task output for compilation errors. This task runs `Core - Build` and `Ext - Build` to incrementally compile VS Code TypeScript sources and built-in extensions. Start the task if it's not already running in the background.
    60	- If the tool is not available (e.g. in CLI environments) and you only changed code under `src/`, run `npm run compile-check-ts-native` after making changes to type-check the main VS Code sources (it validates `./src/tsconfig.json`).
    61	- If you changed built-in extensions under `extensions/` and the tool is not available, run the corresponding gulp task `npm run gulp compile-extensions` instead so that TypeScript errors in extensions are also reported.
    62	- For TypeScript changes in the `build` folder, you can simply run `npm run typecheck` in the `build` folder.
    63	
    64	### TypeScript validation steps
    65	- Use the run test tool if you need to run tests. If that tool is not available, then you can use `scripts/test.sh` (or `scripts\test.bat` on Windows) for unit tests (add `--grep <pattern>` to filter tests) or `scripts/test-integration.sh` (or `scripts\test-integration.bat` on Windows) for integration tests (integration tests end with .integrationTest.ts or are in /extensions/).
    66	- Use `npm run valid-layers-check` to check for layering issues
    67	
    68	## Coding Guidelines
    69	
    70	### Indentation
    71	
    72	We use tabs, not spaces.
    73	
    74	### Naming Conventions
    75	
    76	- Use PascalCase for `type` names
    77	- Use PascalCase for `enum` values
    78	- Use camelCase for `function` and `method` names
    79	- Use camelCase for `property` names and `local variables`
    80	- Use whole words in names when possible
    81	
    82	### Types
    83	
    84	- Do not export `types` or `functions` unless you need to share it across multiple components
    85	- Do not introduce new `types` or `values` to the global namespace
    86	
    87	### Comments
    88	
    89	- Use JSDoc style comments for `functions`, `interfaces`, `enums`, and `classes`
    90	
    91	### Strings
    92	
    93	- Use "double quotes" for strings shown to the user that need to be externalized (localized)
    94	- Use 'single quotes' otherwise
    95	- All strings visible to the user need to be externalized using the `vs/nls` module
    96	- Externalized strings must not use string concatenation. Use placeholders instead (`{0}`).
    97	
    98	### UI labels
    99	- Use title-style capitalization for command labels, buttons and menu items (each word is capitalized).
   100	- Don't capitalize prepositions of four or fewer letters unless it's the first or last word (e.g. "in", "with", "for").
   101	
   102	### Style
   103	
   104	- Use arrow functions `=>` over anonymous function expressions
   105	- Only surround arrow function parameters when necessary. For example, `(x) => x + x` is wrong but the following are correct:
   106	
   107	```typescript
   108	x => x + x
   109	(x, y) => x + y
   110	<T>(x: T, y: T) => x === y
   111	```
   112	
   113	- Always surround loop and conditional bodies with curly braces
   114	- Open curly braces always go on the same line as whatever necessitates them
   115	- Parenthesized constructs should have no surrounding whitespace. A single space follows commas, colons, and semicolons in those constructs. For example:
   116	
   117	```typescript
   118	for (let i = 0, n = str.length; i < 10; i++) {
   119	    if (x < 10) {
   120	        foo();
   121	    }
   122	}
   123	function f(x: number, y: string): void { }
   124	```
   125	
   126	- Whenever possible, use in top-level scopes `export function x(…) {…}` instead of `export const x = (…) => {…}`. One advantage of using the `function` keyword is that the stack-trace shows a good name when debugging.
   127	
   128	### Code Quality
   129	
   130	- All files must include Microsoft copyright header
   131	- Prefer `async` and `await` over `Promise` and `then` calls
   132	- All user facing messages must be localized using the applicable localization framework (for example `nls.localize()` method)
   133	- Don't add tests to the wrong test suite (e.g., adding to end of file instead of inside relevant suite)
   134	- Look for existing test patterns before creating new structures
   135	- Use `describe` and `test` consistently with existing patterns
   136	- Prefer regex capture groups with names over numbered capture groups.
   137	- If you create any temporary new files, scripts, or helper files for iteration, clean up these files by removing them at the end of the task
   138	- Never duplicate imports. Always reuse existing imports if they are present.
   139	- When removing an import, do not leave behind blank lines where the import was. Ensure the surrounding code remains compact.
   140	- Do not use `any` or `unknown` as the type for variables, parameters, or return values unless absolutely necessary. If they need type annotations, they should have proper types or interfaces defined.
   141	- When adding file watching, prefer correlated file watchers (via fileService.createWatcher) to shared ones.
   142	- When adding tooltips to UI elements, prefer the use of IHoverService service.
   143	- Do not duplicate code. Always look for existing utility functions, helpers, or patterns in the codebase before implementing new functionality. Reuse and extend existing code whenever possible.
   144	- You MUST deal with disposables by registering them immediately after creation for later disposal. Use helpers such as `DisposableStore`, `MutableDisposable` or `DisposableMap`. Do NOT register a disposable to the containing class if the object is created within a method that is called repeadedly to avoid leaks. Instead, return a `IDisposable` from such method and let the caller register it.
   145	- You MUST NOT use storage keys of another component only to make changes to that component. You MUST come up with proper API to change another component.
   146	- Use `IEditorService` to open editors instead of `IEditorGroupsService.activeGroup.openEditor` to ensure that the editor opening logic is properly followed and to avoid bypassing important features such as `revealIfOpened` or `preserveFocus`.
   147	- Avoid using `bind()`, `call()` and `apply()` solely to control `this` or partially apply arguments; prefer arrow functions or closures to capture the necessary context, and use these methods only when required by an API or interoperability.
   148	- Avoid using events to drive control flow between components. Instead, prefer direct method calls or service interactions to ensure clearer dependencies and easier traceability of logic. Events should be reserved for broadcasting state changes or notifications rather than orchestrating behavior across components.
   149	- Service dependencies MUST be declared in constructors and MUST NOT be accessed through the `IInstantiationService` at any other point in time.
   150	
   151	## Learnings
   152	- Minimize the amount of assertions in tests. Prefer one snapshot-style `assert.deepStrictEqual` over multiple precise assertions, as they are much more difficult to understand and to update.
```

## AGENTS.md (root)

```
     1	# VS Code Agents Instructions
     2	
     3	This file provides instructions for AI coding agents working with the VS Code codebase.
     4	
     5	For detailed project overview, architecture, coding guidelines, and validation steps, see the [Copilot Instructions](.github/copilot-instructions.md).
```

## CONTRIBUTING.md (root)

```
     1	# How to Contribute
     2	
     3	Welcome, and thank you for your interest in contributing to VS Code!
     4	
     5	There are many ways in which you can contribute, beyond writing code. The goal of this document is to provide a high-level overview of how you can get involved.
     6	
     7	## Asking Questions
     8	
     9	Have a question? Instead of opening an issue, please ask on [Stack Overflow](https://stackoverflow.com/questions/tagged/vscode) using the tag `vscode`.
    10	
    11	The active community will be eager to assist you. Your well-worded question will serve as a resource to others searching for help.
    12	
    13	## Providing Feedback
    14	
    15	Your comments and feedback are welcome, and the development team is available via a handful of different channels.
    16	
    17	See the [Feedback Channels](https://github.com/microsoft/vscode/wiki/Feedback-Channels) wiki page for details on how to share your thoughts.
    18	
    19	## Reporting Issues
    20	
    21	Have you identified a reproducible problem in VS Code? Do you have a feature request? We want to hear about it! Here's how you can report your issue as effectively as possible.
    22	
    23	### Identify Where to Report
    24	
    25	The VS Code project is distributed across multiple repositories. Try to file the issue against the correct repository. Check the list of [Related Projects](https://github.com/microsoft/vscode/wiki/Related-Projects) to find out which is the right repo. If you can't figure it out, file it on the [main VS Code repo](https://github.com/microsoft/vscode) and we'll try to redirect you.
    26	
    27	### Look For an Existing Issue
    28	
    29	Before you create a new issue, please do a search in [open issues](https://github.com/microsoft/vscode/issues) to see if the issue or feature request has already been filed.
    30	
    31	Be sure to scan through the [most popular feature requests](https://github.com/microsoft/vscode/issues?q=is%3Aopen+is%3Aissue+label%3Afeature-request+sort%3Areactions-%2B1-desc).
    32	
    33	If you find your issue already exists, make relevant comments and add your [reaction](https://github.com/blog/2119-add-reactions-to-pull-requests-issues-and-comments). Use a reaction in place of a "+1" comment:
    34	
    35	* 👍 - upvote
    36	* 👎 - downvote
    37	
    38	If you cannot find an existing issue that describes your bug or feature, create a new issue using the guidelines below.
    39	
    40	### Writing Good Bug Reports and Feature Requests
    41	
    42	File a single issue per problem and feature request. Do not enumerate multiple bugs or feature requests in the same issue.
    43	
    44	Do not add your issue as a comment to an existing issue unless it's for the identical input. Many issues look similar, but have different causes.
    45	
    46	The more information you can provide, the more likely someone will be successful at reproducing the issue and finding a fix.
    47	
    48	The built-in tool for reporting an issue, which you can access by using `Report Issue` in VS Code's Help menu, can help streamline this process by automatically providing the version of VS Code, all your installed extensions, and your OS. Additionally, the tool will search among existing issues to see if a similar issue already exists.
    49	
    50	Please include the following with each issue:
    51	
    52	* Version of VS Code
    53	
    54	* Your operating system
    55	
    56	* List of extensions that you have installed
    57	
    58	* Reproducible steps (1... 2... 3...) that cause the issue
    59	
    60	* What you expected to see, versus what you actually saw
    61	
    62	* Images, animations, or a link to a video showing the issue occurring
    63	
    64	* A code snippet that demonstrates the issue or a link to a code repository the developers can easily pull down to recreate the issue locally
    65	
    66	  * **Note:** Because the developers need to copy and paste the code snippet, including a code snippet as a media file (i.e. .gif) is not sufficient.
    67	
    68	* Errors from the Dev Tools Console (open from the menu: Help > Toggle Developer Tools)
    69	
    70	### Creating Pull Requests
    71	
    72	* Please refer to the article on [creating pull requests](https://github.com/microsoft/vscode/wiki/How-to-Contribute#pull-requests) and contributing to this project.
    73	
    74	### Final Checklist
    75	
    76	Please remember to do the following:
    77	
    78	* [ ] Search the issue repository to ensure your report is a new issue
    79	
    80	* [ ] Recreate the issue after disabling all extensions
    81	
    82	* [ ] Simplify your code around the issue to better isolate the problem
    83	
    84	Don't feel bad if the developers can't reproduce the issue right away. They will simply ask for more information!
    85	
    86	### Follow Your Issue
    87	
    88	Once submitted, your report will go into the [issue tracking](https://github.com/microsoft/vscode/wiki/Issues-Triaging) workflow. Be sure to understand what will happen next, so you know what to expect, and how to continue to assist throughout the process.
    89	
    90	## Automated Issue Management
    91	
    92	We use GitHub Actions to help us manage issues. These Actions and their descriptions can be [viewed here](https://github.com/microsoft/vscode-github-triage-actions). Some examples of what these Actions do are:
    93	
    94	* Automatically closes any issue marked `needs-more-info` if there has been no response in the past 7 days.
    95	* Automatically locks issues 45 days after they are closed.
    96	* Automatically implements the VS Code [feature request pipeline](https://github.com/microsoft/vscode/wiki/Issues-Triaging#managing-feature-requests).
    97	
    98	If you believe there is an issue with any of these, please reach out on any one of our [feedback channels](https://github.com/microsoft/vscode/wiki/Feedback-Channels).
    99	
```

## Subdirectory configs (not relevant to this task)

The following config files exist but are NOT relevant to the `src/vs/workbench/contrib/localHistory/` directory:

- `src/vs/platform/agentHost/common/state/AGENTS.md` (81 lines) - protocol versioning for agent sessions
- `src/vs/workbench/contrib/imageCarousel/AGENTS.md` (68 lines) - image carousel component
- `.agents/skills/launch/SKILL.md` (369 lines) - VS Code automation via CDP
- `.github/skills/accessibility/SKILL.md` (303 lines) - accessibility requirements
- `.github/skills/add-policy/SKILL.md` (139 lines) - configuration policy lifecycle
- `.github/skills/agent-sessions-layout/SKILL.md` (82 lines) - agent sessions layout
- `.github/skills/author-contributions/SKILL.md` (186 lines) - authorship tracing
- `.github/skills/azure-pipelines/SKILL.md` (321 lines) - Azure DevOps CI
- `.github/skills/chat-customizations-editor/SKILL.md` (197 lines) - chat customizations UI
- `.github/skills/component-fixtures/SKILL.md` (342 lines) - component screenshot testing
- `.github/skills/fix-ci-failures/SKILL.md` (269 lines) - CI failure investigation
- `.github/skills/fix-errors/SKILL.md` (99 lines) - error telemetry triage
- `.github/skills/hygiene/SKILL.md` (38 lines) - pre-commit hygiene
- `.github/skills/integration-tests/SKILL.md` (122 lines) - integration tests
- `.github/skills/memory-leak-audit/SKILL.md` (147 lines) - memory leak audit
- `.github/skills/sessions/SKILL.md` (309 lines) - agent sessions window
- `.github/skills/tool-rename-deprecation/SKILL.md` (149 lines) - tool rename compat
- `.github/skills/unit-tests/SKILL.md` (105 lines) - unit tests
- `.github/skills/update-screenshots/SKILL.md` (96 lines) - screenshot updates
- `src/vs/sessions/skills/*/SKILL.md` (various) - session-specific skills
- `extensions/CONTRIBUTING.md` (30 lines) - built-in extension structure
- `extensions/css-language-features/CONTRIBUTING.md` (42 lines) - CSS extension dev
- `extensions/emmet/CONTRIBUTING.md` (14 lines) - Emmet extension dev
- `extensions/html-language-features/CONTRIBUTING.md` (40 lines) - HTML extension dev
- `extensions/json-language-features/CONTRIBUTING.md` (40 lines) - JSON extension dev
- `extensions/theme-seti/CONTRIBUTING.md` (33 lines) - Seti icon theme
- `cli/CONTRIBUTING.md` (20 lines) - CLI (Rust) build/debug
