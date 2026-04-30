#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q "rawSections" packages/playwright-core/src/tools/backend/response.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Fix 1: response.ts using sed
sed -i "s/private _imageResults: { data: Buffer, imageType: \x27png\x27 | \x27jpeg\x27 }\[\] = \[\];/private _imageResults: { data: Buffer, imageType: \x27png\x27 | \x27jpeg\x27 }[] = [];\n  private _raw: boolean;/" packages/playwright-core/src/tools/backend/response.ts

sed -i "s/constructor(context: Context, toolName: string, toolArgs: Record<string, any>, relativeTo?: string) {/constructor(context: Context, toolName: string, toolArgs: Record<string, any>, options?: { relativeTo?: string, raw?: boolean }) {/" packages/playwright-core/src/tools/backend/response.ts

sed -i "s/this._clientWorkspace = relativeTo ?? context.options.cwd;/this._clientWorkspace = options?.relativeTo ?? context.options.cwd;\n    this._raw = options?.raw ?? false;/" packages/playwright-core/src/tools/backend/response.ts

# Fix serialize method - replace the sections variable declaration
sed -i "s/const sections = await this._build();/const allSections = await this._build();\n    const rawSections = [\x27Error\x27, \x27Result\x27, \x27Snapshot\x27] as const;\n    const sections = this._raw ? allSections.filter(section => rawSections.includes(section.title as typeof rawSections[number])) : allSections;/" packages/playwright-core/src/tools/backend/response.ts

# For the loop body, we need a Python script to handle the multi-line replacement
cat > /tmp/fix_serialize.py << PYEND
src = open("packages/playwright-core/src/tools/backend/response.ts").read()

# The old loop body pattern (using \x60 for backtick)
old_pattern = """      text.push(\x60### \${section.title}\x60);
      if (section.codeframe)
        text.push(\x60\x60\x60\${section.codeframe}\x60);
      text.push(...section.content);
      if (section.codeframe)
        text.push("\x60\x60\x60");"""

new_pattern = """      if (!this._raw) {
        text.push(\x60### \${section.title}\x60);
        if (section.codeframe)
          text.push(\x60\x60\x60\${section.codeframe}\x60);
        text.push(...section.content);
        if (section.codeframe)
          text.push("\x60\x60\x60");
      } else {
        text.push(...section.content);
      }"""

src = src.replace(old_pattern, new_pattern)
open("packages/playwright-core/src/tools/backend/response.ts", "w").write(src)
print("response.ts serialize fixed")
PYEND
python3 /tmp/fix_serialize.py

# Fix 2: browserBackend.ts
sed -i "s/const cwd = rawArguments._meta?.cwd;/const cwd = rawArguments._meta?.cwd;\n    const raw = !!rawArguments._meta?.raw;/" packages/playwright-core/src/tools/backend/browserBackend.ts
sed -i "s/const response = new Response(context, name, parsedArguments, cwd);/const response = new Response(context, name, parsedArguments, { relativeTo: cwd, raw });/" packages/playwright-core/src/tools/backend/browserBackend.ts

# Fix 3: evaluate.ts
cat > /tmp/fix_eval.py << PYEND
src = open("packages/playwright-core/src/tools/backend/evaluate.ts").read()
old = """      const text = JSON.stringify(evalResult.result, null, 2) ?? \x27undefined\x27;
      await response.addResult(\x27Evaluation result\x27, text, { prefix: \x27result\x27, ext: \x27json\x27, suggestedFilename: params.filename });
    });"""
new = """      const text = JSON.stringify(evalResult.result, null, 2) ?? \x27undefined\x27;
      await response.addResult(\x27Evaluation result\x27, text, { prefix: \x27result\x27, ext: \x27json\x27, suggestedFilename: params.filename });
    }).catch(e => {
      response.addError(e instanceof Error ? e.message : String(e));
    });"""
src = src.replace(old, new)
open("packages/playwright-core/src/tools/backend/evaluate.ts", "w").write(src)
PYEND
python3 /tmp/fix_eval.py

# Fix 4: program.ts
sed -i "s/type GlobalOptions = {/type GlobalOptions = {\n  raw?: boolean;/" packages/playwright-core/src/tools/cli-client/program.ts
sed -i "s/\x27profile\x27,$/\x27profile\x27,\n  \x27raw\x27,/" packages/playwright-core/src/tools/cli-client/program.ts
sed -i "s/\x27help\x27,$/\x27help\x27,\n  \x27raw\x27,/g" packages/playwright-core/src/tools/cli-client/program.ts

cat > /tmp/fix_program.py << PYEND
src = open("packages/playwright-core/src/tools/cli-client/program.ts").read()
old = """async function runInSession(entry: SessionFile, clientInfo: ClientInfo, args: MinimistArgs) {
  for (const globalOption of globalOptions)
    delete args[globalOption];
  const session = new Session(entry);
  const result = await session.run(clientInfo, args);
  console.log(result.text);
}"""
new = """async function runInSession(entry: SessionFile, clientInfo: ClientInfo, args: MinimistArgs) {
  const raw = !!args.raw;
  for (const globalOption of globalOptions)
    delete args[globalOption];
  const session = new Session(entry);
  const result = await session.run(clientInfo, args, { raw });
  console.log(result.text);
}"""
src = src.replace(old, new)
open("packages/playwright-core/src/tools/cli-client/program.ts", "w").write(src)
PYEND
python3 /tmp/fix_program.py

# Fix 5: session.ts
sed -i "s/async run(clientInfo: ClientInfo, args: MinimistArgs): Promise<{ text: string }> {/async run(clientInfo: ClientInfo, args: MinimistArgs, options?: { raw?: boolean }): Promise<{ text: string }> {/" packages/playwright-core/src/tools/cli-client/session.ts
sed -i "s/{ args, cwd: process.cwd() }/{ args, cwd: process.cwd(), raw: options?.raw }/" packages/playwright-core/src/tools/cli-client/session.ts

# Fix 6: daemon.ts
cat > /tmp/fix_daemon.py << PYEND
src = open("packages/playwright-core/src/tools/cli-daemon/daemon.ts").read()
old = """          if (params.cwd)
            toolParams._meta = { cwd: params.cwd };"""
new = """          toolParams._meta = { cwd: params.cwd, raw: params.raw };"""
src = src.replace(old, new)
open("packages/playwright-core/src/tools/cli-daemon/daemon.ts", "w").write(src)
PYEND
python3 /tmp/fix_daemon.py

# Fix 7: helpGenerator.ts
sed -i "s/lines.push(formatWithGap(\x27  --help \[command\]\x27, \x27print help\x27));/lines.push(formatWithGap(\x27  --help [command]\x27, \x27print help\x27));\n  lines.push(formatWithGap(\x27  --raw\x27, \x27output only the result value, without status and code\x27));/" packages/playwright-core/src/tools/cli-daemon/helpGenerator.ts

# Fix 8: SKILL.md
cat > /tmp/fix_skill.py << PYEND
src = open("packages/playwright-core/src/tools/cli-client/skill/SKILL.md").read()
old = """playwright-cli video-stop
\x60\x60\x60

## Open parameters"""
new = """playwright-cli video-stop
\x60\x60\x60

## Raw output

The global \x60--raw\x60 option strips page status, generated code, and snapshot sections from the output, returning only the result value. Use it to pipe command output into other tools. Commands that do not produce output return nothing.

\x60\x60\x60bash
playwright-cli --raw eval "JSON.stringify(performance.timing)" | jq \x27.loadEventEnd - .navigationStart\x27
playwright-cli --raw eval "JSON.stringify([...document.querySelectorAll(\x27a\x27)].map(a => a.href))" > links.json
playwright-cli --raw snapshot > before.yml
playwright-cli click e5
playwright-cli --raw snapshot > after.yml
diff before.yml after.yml
TOKEN=\$$(playwright-cli --raw cookie-get session_id)
playwright-cli --raw localstorage-get theme
\x60\x60\x60

## Open parameters"""
src = src.replace(old, new)
open("packages/playwright-core/src/tools/cli-client/skill/SKILL.md", "w").write(src)
PYEND
python3 /tmp/fix_skill.py

echo "All fixes applied successfully."
