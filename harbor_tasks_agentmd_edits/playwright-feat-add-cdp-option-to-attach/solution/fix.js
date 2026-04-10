const fs = require("fs");

// Fix 1: program.ts
let src = fs.readFileSync("/workspace/playwright/packages/playwright-core/src/tools/cli-client/program.ts", "utf-8");

// Replace OpenOptions with AttachOptions + OpenOptions
src = src.replace(
  /type OpenOptions = \{\n  endpoint\?: string;\n  browser\?: string;\n  config\?: string;\n  extension\?: boolean;\n  headed\?: boolean;\n  persistent\?: boolean;\n  profile\?: string;\n\};/,
  `type AttachOptions = {
  config?: string;
  cdp?: string;
  endpoint?: string;
  extension?: boolean | string;
};

type OpenOptions = {
  browser?: string;
  config?: string;
  headed?: boolean;
  persistent?: boolean;
  profile?: string;
};`
);

// Update globalOptions
src = src.replace(
  /const globalOptions: \(keyof \(GlobalOptions & OpenOptions\)\)\[\] = \[/,
  `const globalOptions: (keyof (GlobalOptions & OpenOptions & AttachOptions))[] = [
  'cdp',`
);

// Update booleanOptions
src = src.replace(
  /const booleanOptions: \(keyof \(GlobalOptions & OpenOptions & \{ all\?: boolean \}\)\)\[\] = \[/,
  `const booleanOptions: (keyof (GlobalOptions & OpenOptions & AttachOptions & { all?: boolean }))[] = [`
);

// Update attach case
src = src.replace(
  /const attachTarget = args\.\_\[1\];\n      const attachSessionName = explicitSessionName\(args\.session as string\) \?\? attachTarget;\n      args\.endpoint = attachTarget;/,
  `const attachTarget = args._[1] as string | undefined;
      if (attachTarget && (args.cdp || args.endpoint || args.extension)) {
        console.error("Error: cannot use target name with --cdp, --endpoint, or --extension");
        process.exit(1);
      }
      if (attachTarget)
        args.endpoint = attachTarget;
      if (typeof args.extension === "string") {
        args.browser = args.extension;
        args.extension = true;
      }
      const attachSessionName = explicitSessionName(args.session as string) ?? attachTarget ?? sessionName;`
);

fs.writeFileSync("/workspace/playwright/packages/playwright-core/src/tools/cli-client/program.ts", src);
console.log("program.ts updated");

// Fix 2: registry.ts
src = fs.readFileSync("/workspace/playwright/packages/playwright-core/src/tools/cli-client/registry.ts", "utf-8");
src = src.replace(
  /export function resolveSessionName\(sessionName\?: string\): string \{\n  if \(sessionName\)\n    return sessionName;\n  if \(process\.env\.PLAYWRIGHT_CLI_SESSION\)\n    return process\.env\.PLAYWRIGHT_CLI_SESSION;\n  return 'default';\n\}/,
  `export function resolveSessionName(sessionName?: string): string {
  return explicitSessionName(sessionName) || 'default';
}`
);
fs.writeFileSync("/workspace/playwright/packages/playwright-core/src/tools/cli-client/registry.ts", src);
console.log("registry.ts updated");

// Fix 3: session.ts
src = fs.readFileSync("/workspace/playwright/packages/playwright-core/src/tools/cli-client/session.ts", "utf-8");
src = src.replace(
  /if \(cliArgs\.config\)\n      args\.push\(\`--config=\$\{cliArgs\.config\}\`\);\n    if \(cliArgs\.endpoint \|\| process\.env\.PLAYWRIGHT_CLI_SESSION\)/,
  `if (cliArgs.config)
      args.push("--config=" + cliArgs.config);
    if (cliArgs.cdp)
      args.push("--cdp=" + cliArgs.cdp);
    if (cliArgs.endpoint || process.env.PLAYWRIGHT_CLI_SESSION)`
);
fs.writeFileSync("/workspace/playwright/packages/playwright-core/src/tools/cli-client/session.ts", src);
console.log("session.ts updated");

// Fix 4: SKILL.md
src = fs.readFileSync("/workspace/playwright/packages/playwright-core/src/tools/cli-client/skill/SKILL.md", "utf-8");
src = src.replace("# Connect to browser via extension\nplaywright-cli open --extension", "");
src = src.replace(
  "# Use persistent profile (by default profile is in-memory)\nplaywright-cli open --persistent\n# Use persistent profile with custom directory\nplaywright-cli open --profile=/path/to/profile",
  `# Use persistent profile (by default profile is in-memory)
playwright-cli open --persistent
# Use persistent profile with custom directory
playwright-cli open --profile=/path/to/profile

# Connect to browser via extension
playwright-cli attach --extension`
);
fs.writeFileSync("/workspace/playwright/packages/playwright-core/src/tools/cli-client/skill/SKILL.md", src);
console.log("SKILL.md updated");

// Fix 5: daemon commands.ts
src = fs.readFileSync("/workspace/playwright/packages/playwright-core/src/tools/cli-daemon/commands.ts", "utf-8");
src = src.replace(
  /extension: z\.boolean\(\)\.optional\(\)\.describe\('Connect to browser extension'\),\n    headed/,
  `headed`
);
src = src.replace(
  /const attach = declareCommand\(\{\n  name: 'attach',\n  description: 'Attach to a running Playwright browser',\n  category: 'core',\n  args: z\.object\(\{\n    name: z\.string\(\)\.describe\('Name or endpoint of the browser to attach to'\),\n  }\),\n  options: z\.object\(\{\n    config: z\.string\(\)\.optional\(\)\.describe\('Path to the configuration file, defaults to .playwright\/cli\.config\.json'\),\n    session: z\.string\(\)\.optional\(\)\.describe\('Session name alias \(defaults to the attach target name\)'\),\n  }\),/,
  `const attach = declareCommand({
  name: 'attach',
  description: 'Attach to a running Playwright browser',
  category: 'core',
  args: z.object({
    name: z.string().optional().describe('Bound browser name to attach to'),
  }),
  options: z.object({
    cdp: z.string().optional().describe('Connect to an existing browser via CDP endpoint URL.'),
    endpoint: z.string().optional().describe('Playwright browser server endpoint to attach to.'),
    extension: z.union([z.boolean(), z.string()]).optional().describe('Connect to browser extension, optionally specify browser name (e.g. --extension=chrome)'),
    config: z.string().optional().describe('Path to the configuration file, defaults to .playwright/cli.config.json'),
    session: z.string().optional().describe('Session name (defaults to bound browser name or "default")'),
  }),`
);
fs.writeFileSync("/workspace/playwright/packages/playwright-core/src/tools/cli-daemon/commands.ts", src);
console.log("commands.ts updated");

// Fix 6: daemon program.ts
src = fs.readFileSync("/workspace/playwright/packages/playwright-core/src/tools/cli-daemon/program.ts", "utf-8");
src = src.replace(
  /\.option\('--config <path>', 'path to the config file; by default uses \.playwright\/cli\.config\.json in the project directory and ~\/\.playwright\/cli\.config\.json as global config'\)\n    \.option\('--endpoint <endpoint>'/,
  `.option('--config <path>', 'path to the config file; by default uses .playwright/cli.config.json in the project directory and ~/.playwright/cli.config.json as global config')
    .option('--cdp <url>', 'connect to an existing browser via CDP endpoint URL')
    .option('--endpoint <endpoint>'`
);
fs.writeFileSync("/workspace/playwright/packages/playwright-core/src/tools/cli-daemon/program.ts", src);
console.log("daemon program.ts updated");

// Fix 7: mcp/config.ts
src = fs.readFileSync("/workspace/playwright/packages/playwright-core/src/tools/mcp/config.ts", "utf-8");
src = src.replace(
  /const daemonOverrides = configFromCLIOptions\(\{\n    endpoint: options\.endpoint,\n    config: options\.config,/,
  `const daemonOverrides = configFromCLIOptions({
    endpoint: options.endpoint,
    cdpEndpoint: options.cdp,
    config: options.config,`
);
src = src.replace(
  /result\.browser\.isolated = !options\.profile && !options\.persistent && !result\.browser\.userDataDir && !result\.browser\.remoteEndpoint && !result\.extension;/,
  `result.browser.isolated = !options.profile && !options.persistent && !result.browser.userDataDir && !result.browser.remoteEndpoint && !result.browser.cdpEndpoint && !result.extension;`
);
fs.writeFileSync("/workspace/playwright/packages/playwright-core/src/tools/mcp/config.ts", src);
console.log("config.ts updated");
