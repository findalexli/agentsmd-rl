#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'JSON5.parse' compiler/apps/playground/lib/compilation.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

###############################################################################
# 1. compilation.ts — replace new Function() with JSON5.parse
###############################################################################
# Add JSON5 import after the @babel/core import
sed -i "/import {transformFromAstSync} from '@babel\/core';/a import JSON5 from 'json5';" \
    compiler/apps/playground/lib/compilation.ts

# Insert the parseConfigOverrides function before parseOptions
sed -i '/^function parseOptions(/i \
export function parseConfigOverrides(configOverrides: string): any {\
  const trimmed = configOverrides.trim();\
  if (!trimmed) {\
    return {};\
  }\
  return JSON5.parse(trimmed);\
}\
' compiler/apps/playground/lib/compilation.ts

# Replace the old config parsing block with the new one-liner
python3 -c "
import re
path = 'compiler/apps/playground/lib/compilation.ts'
src = open(path).read()
old_block = re.search(
    r'  // Parse config overrides from config editor\n'
    r'  let configOverrideOptions: any = \{\};\n'
    r'  const configMatch = configOverrides\.match\(.+?\n'
    r'  if \(configOverrides\.trim\(\)\) \{\n'
    r'.*?'
    r'  \}\n  \}',
    src, re.DOTALL
)
assert old_block, 'Could not find old config parsing block'
new_block = '  // Parse config overrides from config editor\n  const configOverrideOptions = parseConfigOverrides(configOverrides);'
src = src[:old_block.start()] + new_block + src[old_block.end():]
open(path, 'w').write(src)
"

###############################################################################
# 2. defaultStore.ts — switch to JSON5 config format
###############################################################################
python3 << 'PYEOF'
import re
path = 'compiler/apps/playground/lib/defaultStore.ts'
src = open(path).read()
# Replace the entire defaultConfig template literal
src = re.sub(
    r"export const defaultConfig = `.*?`;",
    "export const defaultConfig = `\\\\\n{\n  //compilationMode: \"all\"\n}`;",
    src,
    flags=re.DOTALL,
)
open(path, 'w').write(src)
PYEOF

###############################################################################
# 3. package.json — add json5 dependency
###############################################################################
python3 -c "
import json
path = 'compiler/apps/playground/package.json'
pkg = json.loads(open(path).read())
deps = pkg.get('dependencies', {})
if 'json5' not in deps:
    # Insert json5 in alphabetical order
    deps['json5'] = '^2.2.3'
    pkg['dependencies'] = dict(sorted(deps.items()))
    open(path, 'w').write(json.dumps(pkg, indent=2) + '\n')
"

###############################################################################
# 4. ConfigEditor.tsx — switch from TypeScript to JSON language
###############################################################################
python3 -c "
path = 'compiler/apps/playground/components/Editor/ConfigEditor.tsx'
src = open(path).read()
# Remove the compilerTypeDefs import
src = src.replace(
    \"\"\"// @ts-expect-error - webpack asset/source loader handles .d.ts files as strings
import compilerTypeDefs from 'babel-plugin-react-compiler/dist/index.d.ts';

\"\"\", '')
# Replace TypeScript Monaco config with JSON5 config
import re
old_mount = re.search(
    r'    // Add the babel-plugin-react-compiler type definitions to Monaco\n'
    r'    monaco\.languages\.typescript\.typescriptDefaults\.addExtraLib\(\n'
    r'.*?'
    r'      jsx: monaco\.languages\.typescript\.JsxEmit\.React,\n'
    r'    \}\);',
    src, re.DOTALL
)
if old_mount:
    new_mount = '''    // Enable comments in JSON for JSON5-style config
    monaco.languages.json.jsonDefaults.setDiagnosticsOptions({
      allowComments: true,
      trailingCommas: 'ignore',
    });'''
    src = src[:old_mount.start()] + new_mount + src[old_mount.end():]
# Switch Monaco editor language
src = src.replace(\"path={'config.ts'}\", \"path={'config.json5'}\")
src = src.replace(\"language={'typescript'}\", \"language={'json'}\")
open(path, 'w').write(src)
"

echo "Patch applied successfully."
