const fs = require("fs");
const path = require("path");

const REPO = "/workspace/playwright";

// Check that the modified TypeScript files are parseable
const files = [
  "packages/playwright/src/mcp/terminal/commands.ts",
  "packages/playwright/src/mcp/browser/tools/evaluate.ts",
  "packages/playwright/src/mcp/browser/tab.ts",
  "packages/playwright/src/mcp/browser/tools/tool.ts",
  "packages/playwright/src/mcp/program.ts"
];

let hasError = false;

for (const file of files) {
  const fullPath = path.join(REPO, file);
  const content = fs.readFileSync(fullPath, "utf8");

  // Check for balanced braces (skip braces in strings/comments approx)
  const open = content.split("{").length - 1;
  const close = content.split("}").length - 1;
  if (open !== close) {
    console.error(`FAIL: Unbalanced braces in ${file}: ${open} vs ${close}`);
    hasError = true;
    continue;
  }

  // Check for balanced parentheses
  const openP = content.split("(").length - 1;
  const closeP = content.split(")").length - 1;
  if (openP !== closeP) {
    console.error(`FAIL: Unbalanced parentheses in ${file}: ${openP} vs ${closeP}`);
    hasError = true;
    continue;
  }

  console.log(`OK: ${file}`);
}

if (hasError) {
  process.exit(1);
}

console.log("All files pass basic syntax checks");
process.exit(0);
