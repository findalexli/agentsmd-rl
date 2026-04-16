#!/bin/bash
set -e

cd /workspace/repo

# Check if already applied (idempotency)
if grep -q 'Never add "Generated with" in commit message' CLAUDE.md 2>/dev/null; then
    echo "Gold patch already applied. Skipping."
    exit 0
fi

# Apply the gold patch using git apply
cat <<'PATCH_EOF' | git apply --whitespace=nowarn
diff --git a/CLAUDE.md b/CLAUDE.md
index d5bdcd3a62372..15e5d82a420e5 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -125,6 +125,7 @@ EOF
 ```

 Never add Co-Authored-By agents in commit message.
+Never add "Generated with" in commit message.
 Branch naming for issue fixes: `fix-<issue-number>`

 ## Development Guides
diff --git a/package-lock.json b/package-lock.json
index 94f09f6995ab9..79c1b9fda82ca 100644
--- a/package-lock.json
+++ b/package-lock.json
@@ -24,7 +24,6 @@
         "@types/codemirror": "^5.60.7",
         "@types/formidable": "^2.0.4",
         "@types/mdast": "^4.0.4",
-        "@types/minimist": "^1.2.5",
         "@types/node": "18.19.76",
         "@types/react": "^19.2.1",
         "@types/react-dom": "^19.2.1",
@@ -1853,13 +1852,6 @@
         "@types/unist": "*"
       }
     },
-    "node_modules/@types/minimist": {
-      "version": "1.2.5",
-      "resolved": "https://registry.npmjs.org/@types/minimist/-/minimist-1.2.5.tgz",
-      "integrity": "sha512-hov8bUuiLiyFPGyFPE1lwWhmzYbirOXQNNo40+y3zow8aFVTeyn3VWL0VFFfdNddA8S4Vf0Tc062rzyNr7Paag==",
-      "dev": true,
-      "license": "MIT"
-    },
     "node_modules/@types/node": {
       "version": "18.19.76",
       "resolved": "https://registry.npmjs.org/@types/node/-/minimist-1.2.5.tgz",
diff --git a/package.json b/package.json
index df5fe7fe4af65..e209868709e1f 100644
--- a/package.json
+++ b/package.json
@@ -64,7 +64,6 @@
     "@types/codemirror": "^5.60.7",
     "@types/formidable": "^2.0.4",
     "@types/mdast": "^4.0.4",
-    "@types/minimist": "^1.2.5",
     "@types/node": "18.19.76",
     "@types/react": "^19.2.1",
     "@types/react-dom": "^19.2.1",
diff --git a/packages/playwright-core/src/tools/cli-client/DEPS.list b/packages/playwright-core/src/tools/cli-client/DEPS.list
index a780566006ba7..7901dac1293e6 100644
--- a/packages/playwright-core/src/tools/cli-client/DEPS.list
+++ b/packages/playwright-core/src/tools/cli-client/DEPS.list
@@ -1,11 +1,13 @@
 [program.ts]
 "strict"
+./minimist.ts
 ./session.ts
 ./registry.ts
 ../../serverRegistry.ts

 [session.ts]
 "strict"
+./minimist.ts
 ../utils/socketConnection.ts
 ./registry.ts

@@ -14,3 +16,6 @@

 [registry.ts]
 "strict"
+
+[minimist.ts]
+"strict"
diff --git a/packages/playwright-core/src/tools/cli-client/minimist.ts b/packages/playwright-core/src/tools/cli-client/minimist.ts
new file mode 100644
index 0000000000000..28e6f75257b22
--- /dev/null
+++ b/packages/playwright-core/src/tools/cli-client/minimist.ts
@@ -0,0 +1,164 @@
+/**
+ * MIT License
+ *
+ * Copyright (c) 2013 James Halliday and contributors
+ * Modifications copyright (c) Microsoft Corporation.
+ *
+ * Permission is hereby granted, free of charge, to any person obtaining a copy
+ * of this software and associated documentation files (the "Software"), to deal
+ * in the Software without restriction, including without limitation the rights
+ * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
+ * copies of the Software, and to permit persons to whom the Software is
+ * furnished to do so, subject to the following conditions:
+ *
+ * The above copyright notice and this permission notice shall be included in all
+ * copies or substantial portions of the Software.
+ *
+ * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
+ * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
+ * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
+ * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
+ * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
+ * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
+ * SOFTWARE.
+ */
+
+export interface MinimistOptions {
+  string?: string | string[];
+  boolean?: string | string[];
+}
+
+export interface MinimistArgs {
+  _: string[];
+  [key: string]: string | boolean | string[] | undefined;
+}
+
+export function minimist(args: string[], opts?: MinimistOptions): MinimistArgs {
+  if (!opts)
+    opts = {};
+
+  const bools: Record<string, boolean> = {};
+  const strings: Record<string, boolean> = {};
+
+  for (const key of toArray(opts.boolean))
+    bools[key] = true;
+
+  for (const key of toArray(opts.string))
+    strings[key] = true;
+
+  const argv: MinimistArgs = { _: [] };
+
+  function setArg(key: string, val: string | boolean): void {
+    if (argv[key] === undefined || bools[key] || typeof argv[key] === 'boolean')
+      argv[key] = val;
+    else if (Array.isArray(argv[key]))
+      (argv[key] as string[]).push(val as string);
+    else
+      argv[key] = [argv[key] as string, val as string];
+  }
+
+  let notFlags: string[] = [];
+  const doubleDashIndex = args.indexOf('--');
+  if (doubleDashIndex !== -1) {
+    notFlags = args.slice(doubleDashIndex + 1);
+    args = args.slice(0, doubleDashIndex);
+  }
+
+  for (let i = 0; i < args.length; i++) {
+    const arg = args[i];
+    let key: string;
+    let next: string;
+
+    if ((/^--.+=/).test(arg)) {
+      const m = arg.match(/^--([^=]+)=([\s\S]*)$/)!;
+      key = m[1];
+      if (bools[key])
+        throw new Error(`boolean option '--${key}' should not be passed with '=value', use '--${key}' or '--no-${key}' instead`);
+      setArg(key, m[2]);
+    } else if ((/^--no-.+/).test(arg)) {
+      key = arg.match(/^--no-(.+)/)![1];
+      setArg(key, false);
+    } else if ((/^--.+/).test(arg)) {
+      key = arg.match(/^--(.+)/)![1];
+      next = args[i + 1];
+      if (
+        next !== undefined
+        && !(/^(-|--)[^-]/).test(next)
+        && !bools[key]
+      ) {
+        setArg(key, next);
+        i += 1;
+      } else if ((/^(true|false)$/).test(next)) {
+        setArg(key, next === 'true');
+        i += 1;
+      } else {
+        setArg(key, strings[key] ? '' : true);
+      }
+    } else if ((/^-[^-]+/).test(arg)) {
+      const letters = arg.slice(1, -1).split('');
+
+      let broken = false;
+      for (let j = 0; j < letters.length; j++) {
+        next = arg.slice(j + 2);
+
+        if (next === '-') {
+          setArg(letters[j], next);
+          continue;
+        }
+
+        if ((/[A-Za-z]/).test(letters[j]) && next[0] === '=') {
+          setArg(letters[j], next.slice(1));
+          broken = true;
+          break;
+        }
+
+        if (
+          (/[A-Za-z]/).test(letters[j])
+          && (/-?\d+(\.\d*)?(e-?\d+)?$/).test(next)
+        ) {
+          setArg(letters[j], next);
+          broken = true;
+          break;
+        }
+
+        if (letters[j + 1] && letters[j + 1].match(/\W/)) {
+          setArg(letters[j], arg.slice(j + 2));
+          broken = true;
+          break;
+        } else {
+          setArg(letters[j], strings[letters[j]] ? '' : true);
+        }
+      }
+
+      key = arg.slice(-1)[0];
+      if (!broken && key !== '-') {
+        if (
+          args[i + 1]
+          && !(/^(-|--)[^-]/).test(args[i + 1])
+          && !bools[key]
+        ) {
+          setArg(key, args[i + 1]);
+          i += 1;
+        } else if (args[i + 1] && (/^(true|false)$/).test(args[i + 1])) {
+          setArg(key, args[i + 1] === 'true');
+          i += 1;
+        } else {
+          setArg(key, strings[key] ? '' : true);
+        }
+      }
+    } else {
+      argv._.push(arg);
+    }
+  }
+
+  for (const k of notFlags)
+    argv._.push(k);
+
+  return argv;
+}
+
+function toArray(value: string | string[] | undefined): string[] {
+  if (!value)
+    return [];
+  return Array.isArray(value) ? value : [value];
+}
diff --git a/packages/playwright-core/src/tools/cli-client/program.ts b/packages/playwright-core/src/tools/cli-client/program.ts
index cba03b08ee44d..7996c5b48b0d6 100644
--- a/packages/playwright-core/src/tools/cli-client/program.ts
+++ b/packages/playwright-core/src/tools/cli-client/program.ts
@@ -26,15 +26,12 @@ import path from 'path';
 import { createClientInfo, explicitSessionName, Registry, resolveSessionName } from './registry';
 import { Session, renderResolvedConfig } from './session';
 import { serverRegistry } from '../../serverRegistry';
+import { minimist } from './minimist';

 import type { Config } from '../mcp/config.d';
 import type { ClientInfo, SessionFile } from './registry';
 import type { BrowserDescriptor } from '../../serverRegistry';
-
-type MinimistArgs = {
-  _: string[];
-  [key: string]: any;
-};
+import type { MinimistArgs } from './minimist';

 type GlobalOptions = {
   help?: boolean;
@@ -77,21 +74,7 @@ export async function program(options?: { embedderVersion?: string}) {

   const argv = process.argv.slice(2);
   const boolean = [...help.booleanOptions, ...booleanOptions];
-  const args: MinimistArgs = require('minimist')(argv, { boolean, string: ['_'] });
-  for (const [key, value] of Object.entries(args)) {
-    if (key !== '_' && typeof value !== 'boolean')
-      args[key] = String(value);
-  }
-  for (let index = 0; index < args._.length; index++)
-    args._[index] = String(args._[index]);
-  for (const option of boolean) {
-    if (!argv.includes(`--${option}`) && !argv.includes(`--no-${option}`))
-      delete args[option];
-    if (argv.some(arg => arg.startsWith(`--${option}=`) || arg.startsWith(`--no-${option}=`))) {
-      console.error(`boolean option '--${option}' should not be passed with '=value', use '--${option}' or '--no-${option}' instead`);
-      process.exit(1);
-    }
-  }
+  const args: MinimistArgs = minimist(argv, { boolean, string: ['_'] });
   // Normalize -s alias to --session
   if (args.s) {
     args.session = args.s;
@@ -123,11 +106,11 @@ export async function program(options?: { embedderVersion?: string}) {
   }

   const registry = await Registry.load();
-  const sessionName = resolveSessionName(args.session);
+  const sessionName = resolveSessionName(args.session as string);

   switch (commandName) {
     case 'list': {
-      await listSessions(registry, clientInfo, args.all);
+      await listSessions(registry, clientInfo, !!args.all);
       return;
     }
     case 'close-all': {
@@ -155,7 +138,7 @@ export async function program(options?: { embedderVersion?: string}) {
     }
     case 'attach': {
       const attachTarget = args._[1];
-      const attachSessionName = explicitSessionName(args.session) ?? attachTarget;
+      const attachSessionName = explicitSessionName(args.session as string) ?? attachTarget;
       args.attach = attachTarget;
       args.session = attachSessionName;
       await startSession(attachSessionName, registry, clientInfo, args);
diff --git a/packages/playwright-core/src/tools/cli-client/session.ts b/packages/playwright-core/src/tools/cli-client/session.ts
index 2702c346efd17..577b665a61245 100644
--- a/packages/playwright-core/src/tools/cli-client/session.ts
+++ b/packages/playwright-core/src/tools/cli-client/session.ts
@@ -26,11 +26,7 @@ import { compareSemver, SocketConnection } from '../utils/socketConnection';
 import { resolveSessionName } from './registry';

 import type { SessionConfig, ClientInfo, SessionFile } from './registry';
-
-type MinimistArgs = {
-  _: string[];
-  [key: string]: any;
-};
+import type { MinimistArgs } from './minimist';

 export class Session {
   readonly name: string;
@@ -47,7 +43,7 @@ export class Session {
     return compareSemver(clientInfo.version, this.config.version) >= 0;
   }

-  async run(clientInfo: ClientInfo, args: MinimistArgs, cwd?: string): Promise<{ text: string }> {
+  async run(clientInfo: ClientInfo, args: MinimistArgs): Promise<{ text: string }> {
     if (!this.isCompatible(clientInfo))
       throw new Error(`Client is v${clientInfo.version}, session '${this.name}' is v${this.config.version}. Run\n\n  playwright-cli${this.name !== 'default' ? ` -s=${this.name}` : ''} open\n\nto restart the browser session.`);

@@ -127,7 +123,7 @@ export class Session {
     await fs.promises.mkdir(clientInfo.daemonProfilesDir, { recursive: true });

     const cliPath = require.resolve('../cli-daemon/program.js');
-    const sessionName = resolveSessionName(cliArgs.session);
+    const sessionName = resolveSessionName(cliArgs.session as string);
     const errLog = path.join(clientInfo.daemonProfilesDir, sessionName + '.err');
     const err = fs.openSync(errLog, 'w');
 PATCH_EOF

echo "Gold patch applied successfully!"
